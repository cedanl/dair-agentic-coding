---
name: bouwen_dashboard
description: Gebruik wanneer iemand uit een eerder profiel en schets (data-profiel.md en schets.md) een dashboard wil bouwen over studiesucces in 1CHO-data, zoals in ronde 2 van de CEDA-workshop "Agentic data science in het onderwijs" — met grafiek, vergelijking en filter, privacy-drempel, eerlijke framing, bron en toegankelijkheid. LET OP — de data eerst verkennen hoort bij `verkennen_data`.
allowed-tools: Read Grep Glob Write Edit Bash
metadata:
  workshop: ceda-rad-dair
  ronde: "2"
  versie: "0.1.0"
---

# Dashboard bouwen

Bouwt uit `schets.md` een werkend én verantwoord dashboard dat de casusvraag beantwoordt. Het
verantwoorden zit er **in verweven**: er is geen aparte stap achteraf.

## Invoer

- `data-profiel.md` en `schets.md` uit `verkennen_data`. Ontbreken ze, draai dan eerst die skill.
- `data/demodata_1cho.csv`.
- De casusvraag (staat bovenaan het profiel).

## Stack

Python, DuckDB voor de berekening en Streamlit voor het dashboard (de dashboard-tool kan voor de
workshop nog wijzigen; volg dan de keuze van de workshopleiding). Installeer wat nodig is met uv in een virtuele omgeving
(`uv venv` en `uv pip install duckdb streamlit plotly`). Zet de berekeningen in
`berekeningen.py` naast `app.py`, zodat ze los te testen zijn; `app.py` bevat alleen de weergave.
Start met `streamlit run app.py`. Gebruik `width="stretch"` in plaats van `use_container_width`.

## Wat het dashboard minimaal heeft

1. **Een grafiek** die de casusvraag beantwoordt, met de **conclusie als titel** ("Uitval is het
   hoogst in techniek"), niet "Uitval per sector".
2. **Een vergelijking** tussen groepen of cohorten, met één gemeenschappelijke nul-as.
3. **Een filter** (sector, opleiding, cohort), waarbij de privacy-drempel opnieuw wordt toegepast
   op de gefilterde groep.
4. **Een zijbalk of kader "Zo lees je dit"** met definities (uit `data-profiel.md`), bron en de
   zin *Wat dit dashboard niet kan zeggen*.

## Responsible, verweven

| Check | Wat jij doet |
|---|---|
| Privacy | Toon geen groep onder de drempel (standaard 30 studenten per groep, 5 per percentage-cel; zie `data-profiel.md`). Toon in plaats daarvan "te weinig studenten" en pas secundaire onderdrukking toe. Bouw de drempel als parameter, niet hardcoded in elke grafiek. |
| Waarneembaarheid | Sluit cohorten uit waarvan de observatietermijn niet volledig is en zeg dat op het dashboard. |
| Eerlijke framing | Geen woorden als "slechter" of "risicogroep" over groepen mensen; benoem opleidingen, geen kenmerken van personen als oorzaak. Een verband is geen oorzaak. |
| Toegankelijkheid | Kleurenblind-veilig palet (niet alleen rood/groen), contrast minimaal 4,5:1, elke grafiek met een tekstuele samenvatting als alt-tekst, labels direct op de staven waar het past. |
| Bron en uitleg | Bronvermelding (1CHO-demodata, de definities), peildatum en n per groep zichtbaar. De data heeft geen peildatum: gebruik het laatste `inschrijvingsjaar` in de data, tenzij anders opgegeven. |

## Werkwijze

1. Lees `schets.md`, kies met de deelnemer welke view het eerst komt, bouw die.
2. Test headless met `streamlit.testing.v1.AppTest`: geen exception, de cohortkeuze stopt bij het
   laatste waarneembare cohort, en een filter naar een kleine groep geeft "te weinig studenten".
   Dat zegt meer dan alleen kijken of de server start. Meld eerlijk wat je niet kon controleren,
   bijvoorbeeld hoe het er in de browser uitziet of de alt-tekst bij een schermlezer aankomt
   (Plotly in Streamlit heeft geen echte alt-tekst: zet de samenvatting in een `st.caption`).
3. Vat samen: welke keuzes zijn gemaakt, welke checks zijn toegepast, wat blijft open.

## Let op

- Onderdrukte groepen laat je weg uit de grafiek en noem je in de tekstuele samenvatting. Controleer
  het kleurcontrast echt (4,5:1) en neem niet aan dat een palet voldoet.
- Geen interactie of extra tab "voor de zekerheid": houd het bij wat de casus nodig heeft.
- Vermeld op het dashboard dat het demodata is.
- Gebruik in elke tekst, ook de samenvatting onder een grafiek, dezelfde leesbare labels als in de grafiek
  zelf (dus niet de ruwe waarde "B Bedrijfskunde" als de grafiek "Bedrijfskunde" toont).
- Volg de huisstijl van het eigen team of Npuls als de deelnemer die opgeeft; zo niet, kies een rustig
  standaardthema met voldoende contrast.
