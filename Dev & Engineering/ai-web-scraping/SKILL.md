---
name: ai-web-scraping
description: "Scraping webu přes lokální CLI `scrape` (ScrapeGraphAI). Umí buď vyrenderovat stránku do markdownu zdarma (--dump), nebo extrahovat data autonomně s automatickou volbou modelu (Ollama → Haiku → Sonnet → Opus). Použij při tahání strukturovaných dat ze stránek — ceny, kontakty, produktová pole, výpisy — hlavně u JS stránek, které WebFetch nepřečte."
allowed-tools: Bash Read Write
metadata:
  author: pascaljura
  version: "2.0"
---

# AI scraping webu (`scrape`)

## Kdy tenhle skill použít

Sáhni po `scrape` místo `WebFetch`, když:

- Stránka je **JS-rendered** (React/Vue SPA, lazy-loaded výpisy) — WebFetch vidí prázdnou slupku, `scrape` pouští skutečné Chromium
- Potřebuješ **strukturovaný výstup** — JSON s pojmenovanými poli, ne prózu
- Taháš **stejná pole napříč mnoha stránkami** (produktové mřížky, katalogy konkurence, kontakty)

Na běžné články a dokumentaci zůstaň u `WebFetch` — je zdarma a okamžitý.

**NEPOUŽÍVEJ** na stránky za přihlášením ani na hromadné procházení celého webu — tohle je extrakce z jedné stránky.

---

## Dva režimy — vyber správný

### `--dump` — render zdarma, zpracování v session

```bash
scrape <url> --dump
```

Vyrenderuje stránku Chromiem a vypíše čistý markdown. **Nevolá žádné LLM**, takže nestojí nic. Výstup pak zpracuje Claude Code přímo v konverzaci, tedy v rámci předplatného.

**Tohle je výchozí volba, když uživatel sedí u konverzace.** Ušetří tokeny i čekání a extrakci si odvedeš sám.

### Autonomní extrakce — pro dávky

```bash
scrape <url> "<co vytáhnout>" [--model auto|ollama|haiku|sonnet|opus] [--explain] [--raw-prompt]
```

Zvolí model sám a vrátí JSON. Použij, když běží dávka přes desítky URL a nikdo u toho nesedí — třeba ve smyčce nad seznamem produktů.

Skript k zadání sám připojuje instrukci „vrať platný JSON, chybějící údaj jako null" — bez ní každý model volí jiný tvar výstupu (Haiku vrátí objekt, Sonnet prózu) a dávka se pak nedá strojově zpracovat. Vypni to přes `--raw-prompt`, když chceš souvislý text.

### Příklady

```bash
# Render pro zpracování v session (zdarma)
scrape https://eshop.cz/produkt/123 --dump

# Jednoduchá extrakce → lokální qwen2.5, zdarma
scrape https://eshop.cz/produkt/123 "vytáhni název a cenu"

# Hodně polí → Sonnet
scrape https://firma.cz/kontakt "vytáhni jméno, adresu, IČO, DIČ, telefon a email"

# Vyžaduje úsudek → Opus
scrape https://konkurence.cz "analyzuj jejich cenovou strategii a doporuč postup"

# Vynucený model + kolik to stálo
scrape https://example.com "seznam produktů" --model haiku --explain
```

---

## Volba modelu

Routing je deterministická heuristika v `~/.local/share/scrapegraphai/scrape.py` (funkce `choose_model`) — žádné LLM volání navíc, takže je zdarma a vysvětlitelný.

| Signál v zadání | Model | Proč |
|---|---|---|
| `analyzuj`, `porovnej`, `vyhodnoť`, `doporuč`, `shrň`, `proč` | **Opus 5** | Potřebuje úsudek, ne jen vytažení |
| ≥6 polí, nebo zadání delší než 180 znaků | **Sonnet 5** | Víc polí = větší riziko záměny |
| `vytáhni`, `najdi`, `seznam`, `cena`, `kontakt` … | **Haiku 4.5** | Přímá extrakce, ~půl centu za stránku |
| Cokoli nejednoznačného | **Sonnet 5** | Bezpečný střed |

**Ollama v automatické cestě záměrně není.** Naměřeno na tomhle stroji (4 jádra, bez dedikované GPU): **~10 tok/s** při čtení promptu, takže běžná stránka (~2 tis. tokenů) stojí 3+ minuty jen na načtení, u qwen2.5:7b dvojnásob — testy na reálné stránce spolehlivě padaly na timeout. Haiku odvede totéž za ~$0,005. Lokální model zůstává dostupný přes `--model ollama` (když data nesmí ven) a jako záchrana, když klíč nefunguje.

Pozor na klamavý test: na `example.com` (pár desítek tokenů) lokální model doběhne za sekundy a vypadá použitelně. Měř na reálné stránce, ne na `example.com`.

Přepiš přes `--model`, kdykoli routing hádá špatně. Když ti nějaký tier soustavně sedí špatně, uprav tabulky `SIMPLE_HINTS` / `COMPLEX_HINTS` přímo ve skriptu.

### Automatické fallbacky

- Ollama nedostupná → spadne na Haiku
- `ANTHROPIC_API_KEY` chybí → spadne na Ollamu
- Klíč odmítnut při běhu (401) → přepne na Ollamu a doběhne

Fallback se **nespustí u ručně zvoleného** `--model` — tam dostaneš chybu, aby dávková úloha tiše nezměnila model v polovině běhu.

---

## Náklady

Do LLM jde celý obsah stránky, takže cena roste s velikostí stránky, ne s počtem polí.

**Naměřeno** na reálné podstránce firemního webu (7,3 kB markdownu ≈ 5–6 tis. vstupních tokenů):

| Model | Cena za stránku | Poznámka |
|---|---|---|
| `--dump` + zpracování v session | **$0** | Nejlevnější cesta, když sedíš u konverzace |
| Haiku 4.5 | ~$0,0053 | ≈ 190 stránek za dolar |
| Sonnet 5 | ~$0,025 | ≈ 40 stránek za dolar |
| Opus 5 | neměřeno (≈ 5× Haiku) | |
| qwen2.5:7b lokálně | $0, ale prakticky nepoužitelné | Viz měření výše — na reálné stránce timeoutuje |

Na novém webu si první běh pusť s `--explain`, ať máš reálné číslo, než to nasadíš do smyčky nad stovkami URL.

**Předplatné Max nepokrývá API volání** — Claude tiery potřebují samostatně nabitý kredit na Anthropic Console. Proto je `--dump` + zpracování v session často nejlevnější cesta.

---

## Kde co leží

| Položka | Cesta |
|---|---|
| Skript | `~/.local/share/scrapegraphai/scrape.py` |
| venv | `~/.local/share/scrapegraphai/venv` |
| Spouštěč | `~/.local/bin/scrape` |
| Auth | `ANTHROPIC_API_KEY` z prostředí (`~/.bashrc`), Ollama na `localhost:11434` |

Aktualizace:

```bash
~/.local/share/scrapegraphai/venv/bin/pip install -U scrapegraphai langchain-anthropic
~/.local/share/scrapegraphai/venv/bin/playwright install chromium
```

---

## Pasti

- **`langchain-anthropic` není závislost scrapegraphai** — instaluje se zvlášť, jinak provider `anthropic/` spadne až za běhu.
- **Tabulka tokenů ve scrapegraphai nezná Claude 5** — skript proto posílá `model_tokens` explicitně. Bez toho knihovna jen zaloguje warning a použije výchozí okno.
- **Ollama má výchozí kontext 2048 tokenů** bez ohledu na to, co model umí — stránka by se tiše uřízla. Skript nastavuje `num_ctx` napevno.
- **Playwright si drží vlastní Chromium** (~400 MB v `~/.cache/ms-playwright/`), nezávisle na systémovém prohlížeči. Na tomhle stroji je to jediný použitelný headless prohlížeč — viz [[learning_headless-screenshoty-bez-chrome]], Opera GX z flatpaku maluje jen výřez.
