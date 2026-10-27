#!/usr/bin/env python3
"""Aladin – Jen firma: doplněk k bráně, samotná aplikace se nemění.

Pravidla serveru, která se drží sama (pouští se po každém novém účtu
a pro jistotu každé dvě minuty, viz systemd/):

  * každý aktivní účet je ve firmě — firemní Obsidian se zápisem
    (admin je kapitánem firmy vždycky, tak to má brána sama),
  * majitel serveru je admin a do prostoru každého má plný přístup
    (gateway/pristup.py, role `plny`) — i u lidí přidaných později,
  * každému domovu se nainstaluje a zapne plugin appky `jen-firma`
    (plugin/jen-firma), který okno drží ve firemním prostoru a osobní
    prostor schová.

Nic z aplikace se nepřepisuje: skript jen volá stejné funkce brány, jaké
volá `claude-hub-admin` (gateway.accounts, gateway.firmy, gateway.workspace),
a do domovů zapisuje přes gateway.safefs (odkazy nenásleduje). Pouští se
jako uživatel `hub` se stejným prostředím jako claude-hub-admin.

Nastavení: /etc/aladin-jen-firma.json
    {"majitel": "jmeno@firma.cz", "nazev_firmy": "Firma s.r.o."}
"""
import json
import os
import sys

REPO = os.environ.get("HUB_GW_REPO", "/opt/claude-code-hub")
sys.path.insert(0, REPO)

from gateway import config, firmy, safefs, shared, workspace  # noqa: E402
from gateway.accounts import Accounts  # noqa: E402

CONF = os.environ.get("JEN_FIRMA_CONF", "/etc/aladin-jen-firma.json")
PLUGIN_ID = "jen-firma"
PLUGIN_SRC = os.path.join(os.path.dirname(os.path.abspath(__file__)), "plugin", PLUGIN_ID)
FIRMA_LEVEL = "write"
SPACE_ROLE = "plny"


def log(msg):
    print(msg, flush=True)


def load_conf():
    with open(CONF, encoding="utf-8") as fh:
        conf = json.load(fh)
    majitel = str(conf.get("majitel") or "").strip().lower()
    if not majitel:
        raise SystemExit(f"{CONF}: chybí „majitel“.")
    return majitel, str(conf.get("nazev_firmy") or "").strip()


def ensure_owner(accounts, email):
    owner = accounts.get(email)
    if not owner or owner.get("disabled"):
        log(f"majitel {email}: účet na bráně není (nebo je zablokovaný) — nic nedělám")
        return None
    if owner["role"] != "admin":
        accounts.set_role(email, "admin")
        owner = accounts.get(email)
        log(f"majitel {email}: povýšen na admina")
    return owner


def ensure_company_name(owner, name):
    if not name or firmy.LEGACY not in firmy.slugs():
        return
    if firmy.nazev(firmy.LEGACY) != name:
        firmy.prejmenovat_firmu(owner, firmy.LEGACY, name)
        log(f"firma přejmenována na „{name}“")


def ensure_member(accounts, owner, user):
    """Každý ve firmě se zápisem. Vrací True, když se něco změnilo."""
    if user["role"] == "admin" or accounts.company_level(user) == FIRMA_LEVEL:
        return False
    accounts.set_company_level(owner, user["id"], FIRMA_LEVEL)
    log(f"{user['email']}: do firmy (zápis)")
    return True


def ensure_owner_access(accounts, owner, user):
    """Majitel má do prostoru každého plný přístup."""
    if user["id"] == owner["id"] or accounts.access_row(user["id"], owner["id"]) == SPACE_ROLE:
        return
    accounts.access_set(user, owner["email"], SPACE_ROLE)
    log(f"{user['email']}: majitel {owner['email']} má plný přístup do prostoru")


def ensure_plugin(user):
    """Plugin appky do domova a zapnutý v jeho hub-config.json."""
    home = workspace.home_for(user)
    if not os.path.isdir(home):
        return
    rel = os.path.join(".claude", "hub-plugins", PLUGIN_ID)
    safefs.makedirs(home, rel)
    changed = False
    for name in sorted(os.listdir(PLUGIN_SRC)):
        with open(os.path.join(PLUGIN_SRC, name), encoding="utf-8") as fh:
            text = fh.read()
        if safefs.read_text(home, os.path.join(rel, name)) != text:
            safefs.write_text(home, os.path.join(rel, name), text)
            changed = True

    cfg_rel = os.path.join(".claude", "hub-config.json")
    try:
        cfg = json.loads(safefs.read_text(home, cfg_rel) or "{}")
    except ValueError:
        cfg = None
    if isinstance(cfg, dict):
        on = [p for p in cfg.get("hub_plugins_enabled") or [] if isinstance(p, str)]
        if PLUGIN_ID not in on:
            cfg["hub_plugins_enabled"] = on + [PLUGIN_ID]
            safefs.write_text(home, cfg_rel, json.dumps(cfg, ensure_ascii=False, indent=2))
            changed = True
    if changed:
        log(f"{user['email']}: plugin {PLUGIN_ID} nainstalován a zapnut")


def main():
    majitel, nazev_firmy = load_conf()
    accounts = Accounts(config.DB_PATH)
    shared.ACCOUNTS = accounts
    owner = ensure_owner(accounts, majitel)
    if not owner:
        return 0
    ensure_company_name(owner, nazev_firmy)
    errors = 0
    for user in accounts.list():
        if user["disabled"]:
            continue
        try:
            refresh = ensure_member(accounts, owner, user)
            ensure_owner_access(accounts, owner, user)
            if refresh:
                # Firmy v hub-config.json se počítají při přihlášení; tohle je
                # totéž, co brána dělá při každém startu prostoru.
                workspace.ensure(user)
            ensure_plugin(user)
        except Exception as exc:  # jeden rozbitý účet nesmí zastavit ostatní
            errors += 1
            log(f"{user['email']}: {type(exc).__name__}: {exc}")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
