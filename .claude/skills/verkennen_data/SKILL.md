---
name: verkennen_data
description: Gebruik wanneer iemand de workshopdata wil verkennen voor er een dashboard komt — twee keuzevragen (welke vraag, waarop uitsplitsen), dan maakt één script het dataprofiel data-profiel.html in de hoofdmap (kolommen, definities en privacy, datakwaliteit, ideeën) en krijgt de gebruiker een link om het met één klik te openen. Alles wat over de data gaat, staat in het casusbestand naast de data. LET OP — de views schetsen hoort bij `schets_dashboard` en het dashboard bouwen bij `bouwen_dashboard`.
disable-model-invocation: true
allowed-tools: Read Bash AskUserQuestion
metadata:
  versie: "0.7.0"
---

# Data verkennen

Deze skill hoort bij een workshop. Het doel is dat de gebruiker enthousiast raakt over werken met skills,
dus **alles moet in één keer goed gaan**, voor beginners en ervaren programmeurs. De route ligt vast: volg
hem precies, sla niets over en voeg niets toe. Lees geen andere bestanden en schrijf geen eigen code.

Toon: kort, warm en in gewone taal. Hooguit drie zinnen per bericht.

## 1. Twee vragen

Lees `data/demodata_1cho.casus.json` (noemt de gebruiker een ander bestand `data/x.csv`, lees dan
`data/x.casus.json`). Zeg niets over dat bestand; stel meteen de eerste vraag met de AskUserQuestion-tool:

**Wat wil je weten?** Opties: de drie `vragen` uit de casus, in de volgorde A, B, C. Label: het veld
`label`, met "(Aanbevolen)" achter A. Uitleg: het veld `uitleg`. Vierde optie: *Leg dit eerst uit*. Kiest de
gebruiker die, leg dan in drie zinnen uit dat Claude met de data een dashboard gaat bouwen dat één vraag
beantwoordt, en stel de vraag opnieuw zonder die optie.

Daarna de tweede vraag, ook met de tool: **Waarop wil je het vergelijken?** Opties: de drie
`uitsplitsingen` bij de gekozen vraag, in die volgorde, met het `label` uit `uitsplitsingen` en
"(Aanbevolen)" achter de eerste.

Typt de gebruiker een eigen antwoord, kies dan de optie die er het dichtst bij ligt, zeg dat in één zin
en ga door. Is de tool niet beschikbaar, neem dan de aanbevolen opties en zeg welke.

## 2. Profiel maken

Draai, vanuit de hoofdmap, met de gekozen letter en uitsplitsing (zoals `A` en `sector`):

```bash
uv run --no-project --with duckdb==1.5.6 python .claude/skills/verkennen_data/assets/verken.py data/demodata_1cho.csv --vraag A --uitsplitsing sector
python3 .claude/skills/verkennen_data/assets/toon.py data-profiel.html
```

Het eerste commando schrijft `data-profiel.html` en drukt vier regels af, één per stap. Het tweede drukt
de link af.

## 3. Afsluiten

Eindig met precies dit, met de vier stappen in je eigen woorden (één korte zin per stap, zonder getallen
uit de data) en de afgedrukte link:

> **Je dataprofiel staat klaar.** [Open het profiel](<link>) of klik in de verkenner links op `data-profiel.html`.
>
> 1. **Kolommen**: …
> 2. **Definities en privacy**: …
> 3. **Datakwaliteit**: …
> 4. **Ideeën**: …
>
> Volgende stap: typ `/schets_dashboard`.

## Als er iets misgaat

- Geeft een commando een fout, draai het één keer opnieuw. Gaat het weer mis, toon dan de melding en zeg:
  *"Roep een begeleider erbij."* Probeer geen eigen oplossing.
- Is er geen casusbestand naast de data, zeg dan dat deze skill bij de workshop hoort en een casusbestand
  nodig heeft, en stop.
