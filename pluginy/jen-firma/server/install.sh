#!/bin/bash
# Aladin – Jen firma: instalace doplňku na server s bránou Aladina.
#
#   sudo bash install.sh --majitel jmeno@firma.cz [--nazev "Firma s.r.o."]
#
# Zkopíruje doplněk do /opt/aladin-jen-firma, zapíše nastavení
# /etc/aladin-jen-firma.json (jen když ho předáš nebo ještě není), zapne
# systemd jednotky a jednou ho pustí. Jde pouštět znovu (aktualizace).
set -euo pipefail

DEST=/opt/aladin-jen-firma
CONF=/etc/aladin-jen-firma.json
SRC="$(cd "$(dirname "$0")" && pwd)"
MAJITEL=""
NAZEV=""

while [ $# -gt 0 ]; do
    case "$1" in
        --majitel) MAJITEL="$2"; shift 2 ;;
        --nazev)   NAZEV="$2"; shift 2 ;;
        *) echo "Neznámý přepínač: $1" >&2; exit 1 ;;
    esac
done

[ "$(id -u)" -eq 0 ] || { echo "Pusť jako root." >&2; exit 1; }
[ -d /opt/claude-code-hub/gateway ] || { echo "Brána Aladina tu není (/opt/claude-code-hub)." >&2; exit 1; }

if [ -n "$MAJITEL" ]; then
    python3 - "$CONF" "$MAJITEL" "$NAZEV" <<'EOF'
import json, sys
path, majitel, nazev = sys.argv[1:]
json.dump({"majitel": majitel.strip().lower(), "nazev_firmy": nazev.strip()},
          open(path, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
EOF
fi
[ -f "$CONF" ] || { echo "Chybí $CONF — pusť s --majitel." >&2; exit 1; }
chmod 644 "$CONF"

install -d -m 755 "$DEST" "$DEST/plugin/jen-firma"
install -m 755 "$SRC/jen_firma.py" "$DEST/"
install -m 644 "$SRC"/../plugin.js "$SRC"/../plugin.json "$DEST/plugin/jen-firma/"
install -m 644 "$SRC"/systemd/aladin-jen-firma.{service,path,timer} /etc/systemd/system/
systemctl daemon-reload
systemctl enable --now aladin-jen-firma.path aladin-jen-firma.timer >/dev/null
systemctl start aladin-jen-firma.service
journalctl -u aladin-jen-firma.service -n 30 --no-pager -o cat
echo "Hotovo: $(cat "$CONF" | tr -d '\n ')"
