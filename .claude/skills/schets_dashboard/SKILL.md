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
regisseur ook al doe jij het werk.

Houd het ritme hoog. **Stel alle vragen die je nodig hebt in één bericht**, genummerd, en geef bij elke
vraag een **standaardantwoord** ("Ik ga uit van X, tenzij je iets anders zegt"). Antwoordt de gebruiker
"ok", dan gelden de standaarden. Vraag niets wat al in het gesprek staat, en vraag niet naar ervaring:
pas je uitleg aan op hoe de gebruiker praat. Stel alleen een vraag als het antwoord het werk echt verandert
en je het niet kunt aannemen. Alles wat je aanneemt, zeg je hardop en leg je vast, zodat het zichtbaar is
en de gebruiker het kan corrigeren.

Lees voor wie het dashboard is en welke beslissing het helpt nemen uit het gesprek of het profiel; vraag
het alleen als het daar niet staat. Doe daarna in **één bericht** een voorstel: twee of drie views met
grafiektype en volgorde als standaard, plus alle open punten, elk met een standaardantwoord. Wat de
gebruiker als eerste wil zien, wordt een view, ook als jij een andere had gekozen: zeg een bezwaar
kort en laat de gebruiker beslissen. Zet in de schets een kopje *Keuzes van de gebruiker* met wat de
gebruiker besloot en wat een aanname is.

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

Zet in de schets een kopje *Nog open vragen* met alles wat nog bevestigd moet worden: vragen uit het
profiel die openstaan, maten die je zelf nieuw voorstelt, en keuzes die je als aanname deed. Laat niets
onuitgesproken: wat daar niet staat, denkt de gebruiker dat al beslist is.

Eindig met een korte samenvatting in het gesprek. Zeg met welke view je begint en geef daar een
stellige standaard voor, bijvoorbeeld *"Ik begin met view 1, tenzij je iets anders wilt."* Kies
standaard de view die de vraag het meest direct beantwoordt, tenzij de gebruiker al een volgorde noemde.
De gebruiker houdt de keuze maar hoeft niets te beantwoorden. Vraag dus niet *"welke view eerst?"*
als je al een aanbeveling hebt. Noem de open vragen apart, zodat ze niet in de samenvatting
verdwijnen.

## Let op

- Geen conclusie, geen getal uit voorbeelddata als uitkomst.
- Noem een verschil tussen groepen geen "effect" of "oorzaak".
- Houd het bij twee of drie views: meer is geen verbetering.
