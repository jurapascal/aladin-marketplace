# Předání: jednostránkový web z Figmy → HTML

> **Pro koho:** vlož celý tento soubor svému Claudovi (Claude Code) jako kontext na začátku práce.
> Je to destilát postupu, který už jednou prošel celým procesem — obsahuje konkrétní chyby, na které model sám naráží, a jak se jim vyhnout. Drž se ho, ušetří to spoustu kol dokola.

---

## 1. Co se staví a co je „hotovo"

**Cíl této fáze:** převést dodaný **Figma design** do **jednoho samostatného `.html` souboru** — čisté, produkční HTML/CSS/JS. Nic víc.

**Fáze 1 = jenom „naprogramovat design".** Nasazení (hosting), CMS (Directus), formuláře, automatizace — to se řeší **až potom** a přihlašovací údaje k tomu dostaneš zvlášť. **Teď je neřeš a neptej se na ně.**

**Kritéria „hotovo" (definition of done):**
- Jeden standalone `.html` soubor (vložený `<style>` i `<script>`), otevře se dvojklikem a vypadá jako Figma.
- Pixel-přesné vůči návrhu — design **neinterpretovat ani „nevylepšovat"**.
- Responsivní: breakpointy 1024px (tablet) a 768px (mobil).
- Přístupnost: `alt` u obrázků, `aria-label`, spárované `<label>` u formulářů.
- Žádný framework (viz pravidla níže).
- Veden průběžný **log** (viz sekce 7) — povinné.

---

## 2. Prerekvizity (Figma MCP)

Design se nečte z obrázku, ale přímo z Figmy přes **Dev Mode MCP server**. Postup:

- **Figma desktop aplikace** musí běžet (web verze MCP nepodporuje).
- Přihlášený **placený účet** (Pro/Org/Enterprise) — ten ti klient předá **zvlášť**. Free plán Dev Mode MCP nemá.
- V Figmě zapnuto: `Preferences → Enable Dev Mode MCP Server`.
- V Claude připojený Figma MCP konektor (sekce Connectors), případně CLI:
  `claude mcp add --transport sse figma-dev-mode-mcp-server http://127.0.0.1:3845/sse`

**Ověření spojení:** nástroj `whoami` → vrátí přihlášeného uživatele a plán. Když selže → Figma desktop neběží nebo MCP server není aktivní.

---

## 3. Absolutní pravidla (vlož to do promptu)

```
Na základě Figma design contextu vygeneruj produkční HTML soubor.

PRAVIDLA:
- Výstup = jeden standalone .html soubor (vložený <style> a <script>)
- Absolutní zákaz: React, Vue, Angular, Tailwind, Bootstrap, jakékoliv NPM balíčky
- Použij výhradně: HTML5, CSS3, Vanilla JS
- CSS: design tokeny v :root, BEM metodologie, Flexbox/Grid (NE position:absolute pro layout)
- Sémantické HTML5 tagy: <header>, <main>, <section>, <article>, <nav>, <footer>
- Responsivita: breakpointy 1024px (tablet) a 768px (mobil) přes CSS Media Queries
- Přístupnost: alt atributy, aria-label, správné <label> u formulářů
- Pixel-přesná implementace – neinterpretuj ani nevylepšuj design
```

> ⚠️ **Model má vrozenou tendenci sypat React + Tailwind** (Figma MCP ho tak i vrací). Tohle pravidlo musí být explicitní, jinak ti to udělá.

---

## 4. Workflow krok za krokem

### Krok 1 — Ověř spojení
`whoami` → přihlášený uživatel + plán.

### Krok 2 — Zjisti strukturu souboru
Nástrojem `use_figma` (JavaScript přes Plugin API):
```javascript
const topFrames = figma.currentPage.children.map(n => ({
  id: n.id, name: n.name, type: n.type, w: n.width, h: n.height
}));
return { pages: figma.root.children.map(p => ({ id: p.id, name: p.name })), topFrames };
```
→ Identifikuj hlavní frame (obvykle největší, „Index"/„Home").

> ⚠️ `node-id=0:1` v URL je jen **root stránky** — nelze na něm volat `get_design_context`. Potřebuješ konkrétní ID framu (např. `1:2`).

### Krok 3 — Extrahuj design context
Nástroj `get_design_context`, parametry:
```
fileKey:          [z URL: /design/TADY/...]
nodeId:           [konkrétní frame, např. "1:2"]
clientLanguages:  "html,css"
clientFrameworks: "unknown"
```
Vrátí: referenční React+Tailwind kód (převést na vanilla), screenshot framu, **URL adresy assetů (platné jen 7 dní)**.

### Krok 4 — Design tokeny do `:root`
Z kódu / přes `get_variable_defs` vytáhni barvy, typografii, spacing, radius, shadow → CSS Custom Properties:
```css
:root {
  --color-bg:      #xxxxxx;
  --color-primary: #xxxxxx;
  --color-accent:  #xxxxxx;
  --font-display:  'Font', serif;
  --font-body:     'Font', sans-serif;
  --size-body:     16px;
  --sp-lg:         64px;
  --radius-card:   12px;
  --max-content:   1140px;
}
```

### Krok 5 — Konverze
- **Auto Layout (horizontal/vertical)** → `display: flex; flex-direction: row/column`. Grid → `display: grid`. `gap`, `justify-content`, `align-items` se mapují 1:1.
- **Tailwind → čisté CSS:** `bg-[#0f1024]`→`background-color`, `text-[40px]`→`font-size`, `rounded-[12px]`→`border-radius`, `font-['Aboreto']`→`font-family`, `opacity-15`→`opacity:0.15`.
- **JSX → sémantické HTML5:** nav→`<nav>`, header→`<header>`, sekce→`<section aria-labelledby>`, karta→`<article>`, footer→`<footer>`, tlačítko→`<button>`/`<a class="btn">`.
- **BEM:** `.block`, `.block__element`, `.block--modifier`.

> ⛔ **Nikdy `position: absolute` pro layout** — rozbije se při změně obsahu. (Výjimka: celostránkový background, viz gotcha níže.)

### Krok 6 — Assety
URL z `get_design_context` fungují **7 dní**. Stáhni je hned lokálně:
```bash
curl -o assets/hero-bg.jpg "https://www.figma.com/api/mcp/asset/XXXXXXXX"
```

---

## 5. Gotchas — chyby, na které se naráží (čti POZORNĚ)

Tohle je jádro celého předání. Tyhle věci už stály hodiny — nemusíš je objevovat znovu.

| Problém | Příčina | Řešení |
|---------|---------|--------|
| `get_design_context` → „nothing selected" | `node-id=0:1` je root stránky | Zjisti ID konkrétního framu přes `use_figma` |
| `get_metadata` timeout | Velký soubor | Jdi rovnou na `get_design_context` |
| Figma MCP se nepřipojí | Desktop app neběží / MCP server vypnutý | `Preferences → Enable Dev Mode MCP Server` |
| Asset URL po týdnu nefunguje | Figma MCP assety **expirují po 7 dnech** | Stáhni assety lokálně **ihned** |
| Model sype React/Tailwind | Výchozí tendence modelu | Explicitně zakázat v promptu (sekce 3) |
| Font vypadá jinak než ve Figmě | CSS **dědičnost** — element spoléhá na `body` | Piš `font-family`, `font-weight`, `font-size`, `line-height` **explicitně na každý textový element** |

### 5a. Font dědičnost (nejčastější vizuální nepřesnost)
Na každý textový element piš **všechny** font vlastnosti explicitně. Nikdy nespoléhej na dědičnost z `body` — jiná třída, pořadí stylů nebo media query ji můžou přebít a font pak vypadá jinak, přestože „technicky správně" nastavený výš v kaskádě.
```css
/* ✅ Správně */
.newsletter__description {
  font-family: var(--font-body);
  font-weight: 300;
  font-size:   var(--size-body);
  line-height: 1.5;
}
/* ❌ Špatně – spoléhá na body */
.newsletter__description { font-weight: 300; }
```

### 5b. Celostránkový background přes víc sekcí (multi-section background)
**Nejzákeřnější chyba:** ve Figmě bývá pozadí jako jeden velký element na **root framu**, který překrývá víc sekcí. Když ho v HTML zavřeš do jedné `<section>` s `overflow: hidden`, **nikdy** nebude sedět.

**Jak to poznat** — spusť na hlavním framu:
```javascript
const mainFrame = page.children.find(n => n.id === '1:2'); // ID hlavního framu
return JSON.stringify(mainFrame.children.map(n => ({
  id: n.id, name: n.name, type: n.type,
  y: Math.round(n.y), height: Math.round(n.height), bottom: Math.round(n.y + n.height),
})), null, 2);
```
**Signály celostránkového elementu:** je to `RECTANGLE` (ne frame) na top-level; `height` výrazně větší než jedna sekce; `x` == šířka framu (1366px) → leží mimo frame → ve Figmě je to zrcadlený přes `scaleX(-1)`; přesahuje y-rozsah víc sekcí.

**Pozor na dvě opacity:** Figma má `fills[].opacity` (průhlednost výplně) ≠ `node.opacity` (celková). V CSS mapuj **fill opacity** na `img { opacity }`.

**Správná implementace** — bg patří na úroveň `<main>`, ne do sekce:
```css
main { position: relative; }                 /* offset parent pro absolutní bg */
.page-bg { position: absolute; top: [Figma node.y]px; left: 0; width: 100%;
           height: [Figma node.height]px; z-index: 0; overflow: hidden; pointer-events: none; }
.page-bg img { position: absolute; inset: 0; width: 100%; height: 100%;
               object-fit: cover; object-position: center;
               opacity: [FILL opacity]; transform: scaleX(-1); /* jen když node.x == šířka framu */ }
/* VŠECHNY sekce nad bg musí mít: */
.hero, .services, .cards, .newsletter { position: relative; z-index: 1; }
```

---

## 6. Struktura výstupního souboru
```
<!DOCTYPE html>
<html lang="cs">
<head>
  meta, title, Google Fonts link
  <style>
    :root { design tokeny }
    reset & base
    utility třídy
    sekce po sekcích (BEM)
    @media (max-width:1024px) { ... }   /* tablet */
    @media (max-width:768px)  { ... }   /* mobil + hamburger */
  </style>
</head>
<body>
  <header>navigace</header>
  <main>
    <section class="hero">...</section>
    ...
  </main>
  <footer>kontakt</footer>
  <script>vanilla JS</script>
</body>
</html>
```
**Hamburger menu (vzor):**
```javascript
const toggle = document.getElementById('menu-toggle');
const nav    = document.getElementById('main-nav');
toggle.addEventListener('click', () => {
  const isOpen = nav.classList.toggle('nav--open');
  toggle.setAttribute('aria-expanded', String(isOpen));
});
```

---

## 7. POVINNÉ: veď si log o průběhu práce

Cíl: kdyby na webu pokračoval někdo jiný (nebo nová session bez paměti), musí z logu **přesně** pochopit, co a proč je hotové. Zakládej soubor `LOG.md` vedle HTML a piš do něj průběžně.

**Pravidla logu:**
- Každý větší krok = **vlastní číslovaná sekce s datem**. Nové nahoru (nejnovější první).
- Vždy: **co** se udělalo, **proč** (rozhodnutí), **jak** (konkrétní technické řešení), a **problémy + jak se vyřešily**.
- Zaznamenej i **co je placeholder / čeká na dodání** (texty, fotky).
- Konkrétně: názvy tříd, ID framů, hodnoty tokenů, breakpointy — ne obecné fráze.

**Šablona (zkopíruj na začátek `LOG.md`):**
```markdown
# [Název webu] – log realizace

**Figma soubor:** [odkaz]
**Výstup:** index.html
**Datum zahájení:** RRRR-MM-DD
**Status:** rozpracováno / ✅ design hotový

---

### N. [Název kroku] (RRRR-MM-DD)

**Co:** …
**Proč (rozhodnutí):** …
**Jak (řešení):** …
**Problémy:** … → vyřešeno tím, že …
**Placeholder / čeká na dodání:** …

---
```

**Mini příklad zápisu (jak má vypadat):**
```markdown
### 3. Hero sekce + celostránkové pozadí (2026-06-23)

**Co:** Hero s fotkou na pozadí, claim, CTA „Více".
**Proč:** Pozadí ve Figmě (node 1:88, RECTANGLE) přesahuje hero i služby → dáno na úroveň <main>, ne do sekce.
**Jak:** .page-bg position:absolute, top:1018px, height:1498px; img scaleX(-1) (node.x = 1366 = šířka framu); fill opacity 0.15.
**Problémy:** Nejdřív v <section overflow:hidden> → ořezané. Přesun na <main> to vyřešil.
**Placeholder:** Texty CTA finální, fotka z Figmy stažená do assets/.
```

---

## 8. Na co se teď NEptat / co neřešit
- **Hosting, doména, nasazení** — později, údaje dostaneš zvlášť.
- **CMS / Directus, formuláře, automatizace** — pozdější fáze.
- **Žádné přihlašovací údaje, API klíče ani hesla nedávej do kódu ani do logu.** Když je budeš potřebovat, vyžádej si je — neukládej je do souborů projektu.

---

*Když něco z workflow nesedí (jiná struktura Figmy, neznámý prvek), radši se zeptej klienta, než budeš hádat. Jednoduchost první, chirurgické změny, cíl předem.*
