---
name: verkennen_data
description: Gebruik wanneer iemand een 1CHO-inschrijvingenbestand (CSV met puntkomma) wil verkennen voor er een dashboard komt, zoals in ronde 1 van de CEDA-workshop "Agentic data science in het onderwijs" — profileren van data en codebook, kleine groepen signaleren, definities vastleggen en twee of drie views schetsen. LET OP — het dashboard zelf bouwen hoort bij `bouwen_dashboard`.
allowed-tools: Read Grep Glob Write Bash
metadata:
  workshop: ceda-rad-dair
  ronde: "1"
  versie: "0.1.0"
---

# Data verkennen

Maakt van een ruw 1CHO-bestand **begrip**: wat zit erin, wat mag je ermee zeggen en wat mag je
niet laten zien. De uitkomst is twee bestanden die ronde 2 als invoer gebruikt, zodat elke stap na
te lopen is. Je schrijft geen dashboard en trekt nog geen conclusie.

De deelnemer stuurt, jij programmeert. Leg kort uit wat je gaat doen voor je het doet, en laat de
code zien (of zet 'm in een bestand) zodat de navigator mee kan lezen.

## Invoer

- `data/demodata_1cho.csv` — puntkomma-gescheiden, één rij per student per inschrijvingsjaar.
  Heeft de deelnemer een ander pad opgegeven, gebruik dat.
- De casusvraag (A, B of C). Weet je die niet: vraag hem, en herhaal 'm in `data-profiel.md`.

Kolommen: **sector** = `croho_onderdeel_actuele_opleiding` (techniek, economie, gezondheidszorg);
**opleiding** = `opleidingscode_naam_opleiding` (de leesbare naam, niet de code in
`opleiding_actueel_equivalent`).

Lees het bestand met DuckDB (`read_csv('...', delim=';', header=true, all_varchar=true)`) en cast
zelf. Zo gaat niets stilletjes mis door een gegokt type.

## Stappen

### 1. Profileer

Rapporteer in **gewone taal** (de deelnemer hoeft geen code te lezen):

- aantal rijen, aantal unieke studenten (`persoonsgebonden_nummer`), jaren in de data
  (`inschrijvingsjaar` min/max)
- per relevante kolom: aantal ontbrekende waarden en de waarden zelf als er weinig zijn (sector,
  geslacht, vooropleiding, opleiding)
- instroom per jaar: student met `verblijfsjaar_actuele_instelling = 1`
- per uitsplitsingskolom: heeft die meer dan één waarde? Heeft de casusvraag een uitsplitsing waarvoor
  de data maar één waarde heeft (in de standaarddata is `opleidingsvorm` altijd voltijd), meld dat
  expliciet in `data-profiel.md` en laat die uitsplitsing weg.

### 2. Leg de definities vast

Gebruik de definities van het package `staat1cho`, tenzij de deelnemer expliciet iets anders
kiest. Schrijf ze letterlijk in `data-profiel.md` onder het kopje *Definities*:

| Begrip | Definitie |
|---|---|
| Instroom | hoofdinschrijving en `verblijfsjaar_actuele_instelling = 1`; een student telt eenmaal |
| Uitval binnen 1 jaar | voor een instromer met instroomjaar j: geen rij voor dezelfde student met `inschrijvingsjaar = j+1` en geen rij met ingevuld `diplomajaar`. Op instellingsniveau: wisselen van opleiding binnen de instelling is geen uitval |
| Studiewissel | de opleiding in verblijfsjaar 2 verschilt van die in verblijfsjaar 1 |
| Rendement binnen n jaar | diploma met `diplomajaar - instroomjaar + 1 <= n` (n = 3, 5 of 8) |
| Nog niet waarneembaar | cohorten waarvoor de observatietermijn nog niet in de data zit (uitval 1 jr: `instroomjaar + 1` ontbreekt) — tellen niet mee in het percentage |

Dat laatste is de klassieke valkuil: het **laatste cohort geeft een vertekend percentage** (met de
definitie hierboven zelfs 100% uitval, want er is nog geen vervolgjaar) omdat het nog niet afgelopen is. Controleer welke cohorten volledig waarneembaar zijn en noteer dat.

### 3. Signaleer kleine groepen

Tel de groepsgroottes voor de uitsplitsingen die de casus nodig heeft (bijvoorbeeld opleiding ×
cohort × geslacht). Rapporteer de aantallen **apart**: groepen met n < 30, en groepen waarvan de
teller (uitvallers) of de rest (blijvers) kleiner is dan 5. Zeg erbij welke cohorten je meetelt.

- **Standaarddrempel:** groepen met minder dan **30** studenten worden niet getoond; een percentage
  waarvan teller of rest kleiner is dan **5** ook niet. Dit zijn de waarden van staat1cho, een eigen
  keuze van het project die nog niet is getoetst door een privacy officer.
- Is één groep in een jaar onderdrukt, onderdruk dan ook de kleinste zichtbare groep, anders is de
  verborgen waarde terug te rekenen uit het totaal (secundaire onderdrukking). Dat is alleen nodig
  als het totaal van die uitsplitsing zichtbaar blijft, en je past het toe per uitsplitsing, niet over
  de hele pagina. Leg dit uit aan de deelnemer, het is niet vanzelfsprekend.

### 4. Schets twee of drie views

Schrijf `schets.md`: per view een titel die de **conclusie** bevat (alsof je 'm al weet, als
hypothese), de uitsplitsing, het type grafiek en waarom dat type past. Kies bij vergelijkingen tussen
groepen staafdiagrammen met een gemeenschappelijke nul-as; gebruik lijnen alleen voor tijd.

Eindig met één regel *Wat dit dashboard niet kan zeggen* (bijvoorbeeld: geen oorzaak, alleen
verband; alleen demodata).

## Uitvoer

Twee bestanden in de werkmap:

- `data-profiel.md` — profiel, definities, waarneembare cohorten, kleine groepen
- `schets.md` — de twee of drie views

Eindig met een korte samenvatting in het gesprek: drie dingen die de deelnemer nu weet, en één
vraag die de data nog open laat.

## Let op

- Verzin geen kolomnamen: lees ze uit de header.
- Noem een verschil tussen groepen geen "effect" of "oorzaak".
- Het is demodata: zeg dat in `data-profiel.md`.
