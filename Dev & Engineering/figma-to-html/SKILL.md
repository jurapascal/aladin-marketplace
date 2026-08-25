---
name: figma-to-html
description: Převod dodaného Figma návrhu jednostránkového webu do jednoho standalone produkčního HTML souboru (vložený CSS+JS, vanilla, bez frameworků). Čte design přímo z Figma Dev Mode MCP serveru. Použij vždy, když má uživatel „předělat Figmu na HTML/CSS/JS 1:1".
---

# Figma → HTML (jednostránkový web)

Destilát postupu, který už jednou prošel celým procesem. Drž se ho — šetří kola dokola.
**Plný referenční dokument: [reference.md](reference.md) — přečti si ho na začátku práce.**
**Poučení z reálné realizace (co fungovalo / 14 chyb, které stály revize): [lessons-figma-realizace.md](lessons-figma-realizace.md) — povinné čtení, hlavně mobil-first reflow, přesná SVG loga, jednotné okraje.**

## Definition of done

- Jeden standalone `index.html` (vložený `<style>` i `<script>`), otevře se dvojklikem a vypadá jako Figma.
- Pixel-přesné — design **neinterpretovat ani „nevylepšovat"**.
- Responsivní: breakpointy 1024px (tablet) a 768px (mobil) + hamburger.
- Přístupnost: `alt`, `aria-label`, spárované `<label>`.
- **Žádný framework** (zákaz React/Vue/Angular/Tailwind/Bootstrap/NPM). Jen HTML5 + CSS3 + Vanilla JS.
- Veden průběžný `LOG.md` (povinné) + finální předávací `.md` souhrn.

## Absolutní pravidla do promptu

- Výstup = jeden standalone `.html` (vložený `<style>` + `<script>`).
- CSS: design tokeny v `:root`, BEM, Flexbox/Grid (NE `position:absolute` pro layout — výjimka: full-bleed pozadí).
- Sémantické HTML5: `<header> <main> <section> <article> <nav> <footer>`.
- Font vlastnosti (`font-family/weight/size/line-height`) psát **explicitně na každý textový element** (nespoléhat na dědičnost z `body`).

## Workflow

1. `whoami` → ověř Figma připojení (placený účet, Figma desktop běží, Dev Mode MCP zapnutý).
2. `use_figma` (Plugin API) → zjisti stránky a hlavní frame. `node-id=0:1` je jen root stránky, ne frame.
3. `get_metadata` / `use_figma` → rozeber frame na sekce.
4. `get_design_context` (fileKey, nodeId, clientLanguages="html,css") → referenční React+Tailwind kód (převést na vanilla), screenshot, **URL assetů (platné 7 dní)**.
5. `get_variable_defs` → tokeny (pokud prázdné, odvoď barvy/typografii z kódu).
6. Stáhni assety **ihned** (`curl` / `download_assets`) do `assets/`.
7. Postav HTML sekci po sekci, průběžně cross-check `get_screenshot`.

## Top gotchas (viz reference.md sekce 5)

- `get_design_context` „nothing selected" → použit ID konkrétního framu, ne `0:1`.
- Asset URL expirují po **7 dnech** → stáhnout hned lokálně.
- Model sype React/Tailwind → explicitně zakázat.
- Font vypadá jinak → CSS dědičnost, piš font vlastnosti explicitně na každý element.
- Celostránkové pozadí přes víc sekcí: ve Figmě je to `RECTANGLE` na root framu → v HTML patří na úroveň `<main>`, ne do `<section overflow:hidden>`. Pozor na `fills[].opacity` vs `node.opacity`.

## Povinný log + předání

- `LOG.md` vedle HTML: každý krok = číslovaná sekce s datem (nejnovější nahoře); vždy **co / proč / jak / problémy+řešení / placeholdery**. Konkrétně (názvy tříd, ID framů, hodnoty tokenů).
- Na konci finální předávací `.md` pro klienta: co je hotové, jak to funguje, čím uděláno, jak dlouho trvalo, co je placeholder.

## Co NEřešit v této fázi

Hosting/doména/nasazení a CMS/Directus/formuláře = pozdější fáze, údaje dostaneš zvlášť. Hesla/API klíče NIKDY do kódu ani logu.
