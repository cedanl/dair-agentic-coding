---
name: workshop-reflectie
description: Gebruik aan het eind van de CEDA-workshop "Agentic data science in het onderwijs" (evaluatieblok), of bij "reflectie", "terugblik", "hoe ging dit", "wat neem je mee" — stelt vaste vragen over werkwijze, wat goed ging en wat je nu pas ziet, peilt interesse in een vervolgtraining en vraagt wat iemand wil leren. Antwoorden in de woorden van de deelnemer, lokaal opgeslagen. LET OP — voor reflectie op werk in een repo met commit-koppeling gebruik je `sessie-terugblik`; deze is bedoeld voor een groep deelnemers in een workshop.
allowed-tools: Read Write Glob
metadata:
  workshop: ceda-rad-dair
  blok: evaluatie
  versie: "0.1.0"
  afgeleid-van: sessie-terugblik 0.4.0 (cedanl)
---

# Workshop-reflectie

Legt vast hoe de workshop voor één deelnemer ging, in **de woorden van de deelnemer**, plus twee
peilingvragen over een vervolg. De waarde zit in de antwoorden, niet in jouw samenvatting: vul
niets voor iemand in. Duur: circa 8 minuten.

Afgeleid van de team-skill `sessie-terugblik` met drie verschillen: geen GitHub-koppeling of
tokenstatistiek (deelnemers zijn geen team), een kortere vragenreeks, en een vervolgpeiling. De
principes blijven gelijk: één vraag per keer, een dun antwoord is een antwoord, nooit
doorvragen of overhalen, parafraseren maakt het waardeloos.

## Voor je begint

Zeg in twee zinnen wat er gaat gebeuren en dat elke vraag mag worden overgeslagen. Vraag of de
antwoorden mogen worden gebruikt (anoniem) om te bepalen of CEDA een vervolg organiseert. Zonder
ja schrijf je niets weg en deel je niets.

## Vragen (altijd in deze volgorde, één voor één)

Lees `references/vragenset.md` voor de exacte formulering en de achtergrond.

1. **Werkwijze** — Hoe heb je dit aangepakt, en hoe werkte je samen met de agent?
2. **Ging goed** — Wat ging goed?
3. **Blinde vlekken** — Wat zie je nu wat je eerst niet zag?
4. **Interesse in een training** (meerkeuze) — Zou je een vervolg willen?
   - Nee, niet nodig
   - Een losse sessie van een paar uur
   - Een paar dagdelen verspreid over enkele weken
   - Een programma van 4 uur per week voor één semester
5. **Wat wil je leren** (open) — Alleen als het antwoord op 4 niet "nee" is: wat wil je precies leren
   in zo'n training?

## Uitvoer

Schrijf één bestand `reflectie-<voornaam of pseudoniem>.md` in de werkmap, in dit format:

```markdown
---
type: workshop-reflectie
workshop: agentic-data-science-in-het-onderwijs
datum: <YYYY-MM-DD>
toestemming-gebruik: ja
interesse-training: <een van de vier opties>
---

## Werkwijze
<woorden van de deelnemer>

## Ging goed
<woorden van de deelnemer>

## Blinde vlekken
<woorden van de deelnemer>

## Wat ik wil leren
<woorden van de deelnemer, of leeg>
```

Laat het concept zien en wacht op akkoord voor je wegschrijft. Bestaat het bestand al, hang er `-2` aan:
nooit overschrijven.

## Let op

- Geen persoonsgegevens, namen van collega's of oordelen over personen: herformuleer naar het proces.
- Meerkeuze en open vraag mogen ook via de peiling (QR-code) in plaats van in het gesprek met de agent;
  gebruik dan dezelfde formulering.
- Verander de vragen niet per sessie; verbeteringen horen in `references/vragenset.md`.
