# Paluba Market

Katalog rozšíření pro appku **Paluba** (dřív Claude Code Hub). Appka ho čte
v *Nastavení → Napojení a pluginy → Paluba Market* a odtud se položky
instalují jedním klikem.

V katalogu jsou dva druhy položek:

- **Pluginy appky** — JS/CSS, které se načtou do okna Paluby a dostanou její
  API (tlačítka v Rychlých akcích, události, toast, úložiště, volání hubu).
  Běží se stejnými právy jako appka, proto jsou po instalaci **vypnuté**
  a zapnout je jde jen vědomě.
- **Motivy** — vzhled appky: paleta barev (okno i terminál) a volitelně CSS
  (písmo, zaoblení, šířky panelů). Motiv nespouští žádný skript.

Skilly Paluby (slash příkazy) a MCP napojení v katalogu nejsou — skilly
appka přibaluje sama, napojení bere z oficiálního registru MCP.

## Jak to appka čte

1. Stáhne `katalog.json` z větve `main`
   (`https://raw.githubusercontent.com/<repo>/main/katalog.json`).
2. Při instalaci stáhne tarball větve `main` a rozbalí z něj **jen složku
   položky** (`path`). Brány jsou jen běžné soubory a složky — symlinky,
   hardlinky, zařízení, absolutní cesty a `..` instalaci zruší. Položka
   smí mít nejvýš 500 souborů a 20 MB.
3. Plugin skončí v `~/.claude/hub-plugins/<id>/`, motiv
   v `~/.claude/hub-motivy/<id>/`.

Jiné repo katalogu jde nastavit klíčem `market_repo` v `~/.claude/hub-config.json`
(`"market_repo": "owner/repo"`).

## Jak přidat položku

1. Založ složku `pluginy/<id>/` nebo `motivy/<id>/`. `id` je malými písmeny:
   `a-z`, `0-9`, `.`, `_`, `-`, nejvýš 64 znaků, začíná písmenem nebo číslicí.
2. Do složky dej manifest a soubory (viz formáty níže).
3. Přidej záznam do `katalog.json` (do pole `pluginy` nebo `motivy`).
4. Commit a push do `main` — appka si katalog načte nejpozději do 10 minut
   (nebo hned tlačítkem „Obnovit").

## Formát `katalog.json`

```json
{
  "verze": 1,
  "pluginy": [
    {"id": "hodiny", "name": "Hodiny v liště", "description": "…",
     "author": "…", "version": "1.0.0", "path": "pluginy/hodiny"}
  ],
  "motivy": [
    {"id": "les", "name": "Les", "description": "…", "author": "…",
     "version": "1.0.0", "nahled": ["#0f1a14", "#16241c", "#8fc46a"],
     "path": "motivy/les"}
  ]
}
```

- `path` je relativní cesta ke složce položky v tomhle repu (bez `..`).
- `nahled` (jen motivy) jsou 3–5 barev `#rrggbb` pro náhled v katalogu.

## Plugin appky — `plugin.json`

```json
{"name": "Hodiny v liště", "version": "1.0.0", "description": "…",
 "author": "…", "main": "plugin.js", "style": "plugin.css"}
```

`plugin.js` se registruje přes `HubPluginy.registruj('<id>', (api) => { … })`.
API popisuje hlavička `hub/static/pluginy.js` v repu Paluby; ukázka je
v `pluginy/hodiny/`.

## Motiv — `motiv.json`

```json
{"name": "Les", "version": "1.0.0", "description": "…", "author": "…",
 "nahled": ["#0f1a14", "#16241c", "#8fc46a"],
 "barvy": {"dark": {"BG": "#0f1a14", "AMBER": "#8fc46a", "TERM_PALETTE": ["…16 barev…"]},
           "light": {"BG": "#f4f8f3"}},
 "style": "motiv.css"}
```

- `barvy` přepisují paletu Paluby (klíče jako v `hub/core.py`, DARK / LIGHT):
  `AMBER` (akcent), `BG`, `BG_SIDEBAR`, `BG_CARD`, `FG`, `FG_BRIGHT`, `DIM`,
  `GREEN`, `RED`, `CARD_HOVER`, `BORDER`, `SECTION`, `CLOUD`, `FIRMA`,
  `CHART`, `CHART_CLOUD` a volitelně `TERM_PALETTE` (přesně 16 barev pro
  terminál). Jen `#rrggbb`; co chybí, zůstane výchozí.
- `style` (volitelné) je CSS načtené za styl appky. Užitečné proměnné:
  `--radius`, `--radius-lg`, `--sidebar-w`, `--bar-w`, `--font-serif`.
  Vedle smí být i obrázky a fonty (`.svg`, `.png`, `.jpg`, `.webp`,
  `.woff2`, `.woff`) — odkazuj na ně relativně.

---


## Skilly (Claude Brain)

**571 skillů ve 22 kategoriích** pro Claude Code. Každý skill je složka
se souborem `SKILL.md` (popis, kdy ho použít, postup) a případnými
`references/` s detaily, které se čtou až když jsou potřeba.

Patří k [Palubě](https://github.com/jurapascal/claude-code-hub),
ale fungují i samostatně — stačí je mít v Obsidian vaultu, ze kterého
Claude Code čte paměť.

## Instalace

Nejjednodušší cestou je instalačka hubu — nabídne je sama:

```bash
curl -fsSL https://raw.githubusercontent.com/jurapascal/claude-code-hub/main/get.sh | bash
```

Ručně do existujícího vaultu:

```bash
git clone https://github.com/jurapascal/claude-brain-skills.git \
    ~/Obsidian/Claude-Brain/skills
```

## Kategorie

| Kategorie | Čemu se věnuje |
|---|---|
| Ads & Paid Media | reklamní kampaně, copy, rozpočty, affiliate |
| AI & Technology | zásady používání AI, automatizace workflow |
| Analytics & Data | měření, reporty, dashboardy |
| Branding & Design | vizuální identita, brand manuál |
| Client & Consulting | nabídky, onboarding, komunikace s klientem |
| Content & Copywriting | texty, redakční plán, storytelling |
| Courses & Education | kurzy, osnovy, výukové materiály |
| Dev & Engineering | vývoj, review, testy, převod návrhu do kódu |
| E-commerce & Products | produkty, ceny, e-shop |
| Email Marketing & Automation | sekvence, newslettery, automatizace |
| Events & Speaking | akce, prezentace, přednášky |
| Finance & Pricing | ceny, rozpočty, kalkulace |
| HR & Team | nábor, onboarding, procesy v týmu |
| Industry-Specific | oborové postupy |
| Launch & Growth | uvedení produktu, růst |
| Legal & Compliance | podmínky, ochrana údajů, smlouvy |
| Nonprofit & Community | neziskovky, komunita |
| Operations & Systems | provoz, procesy, systémy |
| Sales & Funnels | prodej, trychtýře, nabídky |
| SEO & Search | vyhledávače, obsah, technické SEO |
| Social Media | sociální sítě, kalendáře, formáty |

Úplný seznam s popisy je v [SKILLS-INDEX.md](SKILLS-INDEX.md).

## Jak to Claude používá

Hub při startu session pošle Claudovi jen **seznam kategorií**, ne všech 571
skillů — jinak by menu snědlo celý kontext. Claude si pak sám otevře ten
`SKILL.md`, který se hodí k zadání, a `references/` teprve když potřebuje
detail.
