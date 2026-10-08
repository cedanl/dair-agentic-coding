---
name: schets_dashboard
description: Gebruik wanneer iemand uit een dataprofiel (uitvoer/data-profiel.html) twee of drie views voor een dashboard wil schetsen — eerst sparren over wie het dashboard gebruikt en wat de gebruiker als eerste wil zien, dan per view de vraag, de uitsplitsing, het grafiektype en wat het niet kan zeggen, als HTML-schets zonder code. LET OP — de data verkennen hoort bij `verkennen_data` en het dashboard bouwen bij `bouwen_dashboard`.
allowed-tools: Read Grep Glob Write
metadata:
  versie: "0.2.0"
---

# Dashboard schetsen

Zet de vraag van de gebruiker en het profiel om in twee of drie views, op papier, nog zonder code.
De schets is een **voorstel dat de gebruiker beoordeelt**. Je bouwt niets en rekent niets uit.

Deze skill kent **geen domein**. De vraag, de maten en de definities komen uit het profiel en van
de gebruiker.

## Geen conclusies

Dit is een ontwerp. Je leest alleen het profiel, niet de data. Volg de keuze onder *Datagebruik* in
het profiel: was dat gevoelige of echte data, lees dan nergens rijen. Je trekt **geen conclusie**
uit voorbeelddata of demodata: de conclusie hoort bij de echte data, als de tool af is.

- Formuleer elke view als **vraag of hypothese**, niet als bevinding: *"Verschilt X per Y?"*, niet
  *"X is het hoogst bij Y"*.
- Noem geen getallen of ranglijsten uit de voorbeelddata als uitkomst.

## Invoer

- `uitvoer/data-profiel.html` uit `verkennen_data`. Ontbreekt het, draai dan eerst die skill, of
  vraag de gebruiker om de kolommen, de maten en hun definities.
- De vraag die het dashboard moet beantwoorden. Vraag de gebruiker die in eigen woorden als hij niet
  gegeven is, en noteer hem bovenaan de schets. Verzin hem niet.

## Eerst sparren

De gebruiker kent de lezers van het dashboard en het domein beter dan jij, en blijft de
regisseur ook al doe jij het werk. Stel **één vraag per bericht** en wacht op het antwoord:

1. *Voor wie is dit dashboard en welke beslissing moet het helpen nemen?*
2. *Wat zou jij als eerste willen zien?* Wat de gebruiker noemt, wordt een view, ook als jij een
   andere had gekozen. Zeg het kort als je een bezwaar hebt en laat de gebruiker beslissen.

Geef bij elke keuze (welke views, welke volgorde, welk grafiektype) **twee of drie opties met één
aanbeveling**. Zet in de schets een kopje *Keuzes van de gebruiker* met wat de gebruiker besloot en
waarom, zodat zichtbaar is wie wat bepaalde.

## Stappen

1. **Lees het profiel**: welke uitsplitsingen kunnen (meer dan één waarde), welke maten hebben een
   definitie, welke regels gelden voor waarneembaarheid en privacy, en welke aanpakken
   `verkennen_data` voor de vraag voorstelde. Begin bij *Jouw aanpak* van de gebruiker, daarna de
   aanpakken van `verkennen_data`.
2. **Kies twee of drie views** die samen de vraag beantwoorden. Laat uitsplitsingen weg die het
   profiel niet draagt.
3. **Kies het grafiektype** met een vaste volgorde: eerst verhaal, publiek en doel, dan de
   datastructuur (de TRIPS-beslisboom). Noem het pad in één regel (*"vergelijken, lange labels ->
   horizontaal staafdiagram"*). Vergelijkingen tussen groepen krijgen staafdiagrammen met een
   gemeenschappelijke nul-as; lijnen zijn alleen voor tijd; een cirkeldiagram alleen voor deel-van-geheel
   in één periode en bij hooguit 5-7 delen; een extra groepering wordt een facet, geen derde dimensie in
   één grafiek.
4. **Schrijf per view**: de vraag of hypothese, de maat (met verwijzing naar de definitie in het
   profiel), de uitsplitsing, het grafiektype met waarom, en welke groepen of perioden wegvallen
   door de privacydrempel of omdat ze nog niet waarneembaar zijn.
5. **Eindig met *Wat dit dashboard niet kan zeggen***: geen oorzaak maar hooguit verband, alleen de
   groepen boven de drempel, en niets over de werkelijkheid zolang het voorbeelddata is.

## Uitvoer

Eén bestand: `uitvoer/schets.html` (maak de map `uitvoer/` aan als die ontbreekt; alle gegenereerde HTML
hoort daar). Eén bestand zonder externe afhankelijkheden, met bovenaan de vraag en de keuze onder
*Datagebruik*, en daarna één blok per view. Staat in het profiel dat het demodata is, zet dat er
dan ook bij. De gebruiker opent het in de browser.

HTML-opmaak: semantische kopjes, per view een `<section>` met een kleine definitielijst
(`<dl>`: vraag, maat, uitsplitsing, grafiektype, valt weg), contrast minimaal 4,5:1, geen kleur als
enige onderscheid, leesbaar op een smal scherm. Eén inline `<style>`, geen scripts. Teken geen
nagebootste grafieken met verzonnen waarden: een leeg kader met een tekstbeschrijving is genoeg.

Eindig met een korte samenvatting in het gesprek en vraag welke view als eerste gebouwd wordt: dat
is de keuze van de gebruiker.

## Let op

- Geen conclusie, geen getal uit voorbeelddata als uitkomst.
- Noem een verschil tussen groepen geen "effect" of "oorzaak".
- Houd het bij twee of drie views: meer is geen verbetering.
