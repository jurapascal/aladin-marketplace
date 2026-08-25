<p align="center">
  <img src="https://raw.githubusercontent.com/jurapascal/claude-code-hub/main/assets/hub-wordmark.svg" alt="Claude Code Hub" width="360"/>
</p>

# Claude Brain — skilly

**571 skillů ve 22 kategoriích** pro Claude Code. Každý skill je složka
se souborem `SKILL.md` (popis, kdy ho použít, postup) a případnými
`references/` s detaily, které se čtou až když jsou potřeba.

Patří k [Claude Code Hubu](https://github.com/jurapascal/claude-code-hub),
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
