# Poučení z jedné realizace Figma → HTML

Destilát z 33 revizí jednoho jednostránkového webu (LOG.md projektu) — co fungovalo napoprvé a co stálo kola oprav. **Přečti před každým dalším Figma → HTML projektem.**

## ✅ Co fungovalo (opakovat)

- **Workflow MCP:** `whoami` → `use_figma` (najít hlavní frame, `node-id` z URL bývá stránka, ne frame!) → `get_design_context` po sekcích → assety stáhnout **ihned** (URL expirují za 7 dní).
- **Design tokeny v `:root`** + BEM + standalone HTML — drží konzistenci.
- **Headless Chrome kontrola po každé sekci** proti Figma screenshotu — chyby se chytí hned.
- **LOG.md průběžně** — každá revize s co/proč/jak; nová session naváže bez ztráty.
- **Velký frame extrahovat po pod-sekcích** — 5707px frame naráz = timeout.
- Dekorace (rámečky, kruhy, oddělovače) kreslit jako CSS/inline SVG, ne stahovat PNG.

## ❌ Chyby, které stály nejvíc kol (NEOPAKOVAT)

1. **Mobil odbytý = největší přepracování.** Desktop 1440 zmenšený přes zoom byl na mobilu „vůbec nedělaný". → **Mobil stavět jako plnohodnotný reflow layout od začátku**, podle mobilního Figma framu, pokud existuje. Vzor, který se osvědčil: desktop ≥1025px = fixní 1440px canvas škálovaný CSS `zoom` (NE `transform:scale` — zoom škáluje i layout box); ≤1024px = čistý jednosloupcový reflow. Žádný mezistupeň tablet-media-query pod zoomem (korekce se aplikují dvakrát).
2. **Loga/ikony překreslované „od oka".** Pyramida se 3× předělávala (5 vs 6 trojúhelníků). → **Vždy stáhnout přesné SVG z Figmy (paths verbatim)**, `fill=currentColor`. Mezera v logu může být záměr designu.
3. **Ořez fotek:** Figma má fotky ořezané (object-cover s konkrétním crop). Když zobrazíš celý zdroj, overlay prvky (detekční čtverce, popisky) nesedí. → Přenést **přesný crop** (width/height % + posun) z Figmy.
4. **`download_assets` vrací někdy špatnou vrstvu** (spodní dekorativní místo fotky). → Ověřit vizuálně; skutečná fotka bývá horní vrstva (`imgRectangle…`).
5. **Mezery mezi sekcemi:** první verze byla stěsnaná (7426 vs 7752 px). → **Srovnat celkovou výšku stránky s návrhem** (±1 %), měřit po sekcích.
6. **Nejednotné okraje.** Na desktopu jeden `--content` token pro VŠECHNY sekce (např. 1330px = 55px guttery stejné jako u hero fotky). Na mobilu jednotná levá hrana textu (24px) napříč tagy/kartami/panely — jinak klient pozná 5px rozdíl.
7. **Hover stavy vs podklad sekce:** oranžový hover na tlačítku ležícím na oranžové sekci = neviditelný; bílý hover na světlém headeru zanikal. → **U každého hoveru zvážit barvu podkladu.** Jednotný systém stavů pro všechna tlačítka od začátku.
8. **Sticky navbar + kotvy:** (a) skok na kotvu ≠ scroll — `|dy| > 400` ignorovat, jinak se navbar schová „sám"; (b) `scroll-padding-top` ať kotva neskončí pod fixním headerem; (c) reload s `#hash` + zoom škálování = stránka „ujede" → re-anchor po přeškálování.
9. **Štítky `display:inline-block`** mají mezeru z leadingu → `display:block; width:fit-content` když má štítek sedět těsně na kartě.
10. **Reveal animace `transform:none`** rušila centrující `translateX(-50%)` → reveal jen přes opacity/blur u centrovaných prvků.
11. **Scratch skripty (Python apod.): VŽDY absolutní cesty** — relativní cesta jednou přepsala index.html mimo Edit tracking.
12. **Favicon/asset změny verzovat** (`?v=N` v href) — jinak „nefunguje" kvůli browser cache.
13. **Placeholdery ponechat 1:1** (texty „Menu", překlep v návrhu) a vypsat je do předávacího souhrnu — nevymýšlet obsah bez ptaní.
14. **Ptát se klienta místo hádání** — každá interpretace designu = revize navíc.

## Proces s klientem

- Klient dělá review po nasazení a posílá připomínky po dávkách — počítat s iteracemi, držet kód čitelný pro chirurgické změny.
- Fáze 1 = jen design (žádné CMS/formuláře/hosting — údaje klient pošle zvlášť, neptat se dopředu).
- Po každé změně: nasadit/uložit + ověřit (curl marker / render) + zapsat do LOG.md.
