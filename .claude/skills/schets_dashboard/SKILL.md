---
name: schets_dashboard
description: Gebruik wanneer iemand uit een dataprofiel (uitvoer/data-profiel.html) twee of drie views voor een dashboard wil schetsen — eerst een voorstel waar de gebruiker op reageert, dan per view de vraag, de uitsplitsing, het grafiektype en wat het niet kan zeggen, als HTML-schets zonder code. LET OP — de data verkennen hoort bij `verkennen_data` en het dashboard bouwen bij `bouwen_dashboard`.
allowed-tools: Read Grep Glob Write Skill
metadata:
  versie: "0.3.0"
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

## Eerst een voorstel

De gebruiker kent de lezers van het dashboard en het domein beter dan jij, en blijft de
regisseur ook al doe jij het werk.

Begin zonder vragenronde. Lees voor wie het dashboard is en welke beslissing het helpt nemen uit het
gesprek of het profiel; staat het daar niet, neem dan iets aan en zeg dat. Doe in **één bericht** een
voorstel: twee of drie views met grafiektype en volgorde, en daaronder je aannames, één regel per
aanname. Het voorstel is de vraag: antwoordt de gebruiker "ok", dan schrijf je de schets, en anders pas
je het voorstel aan. Vraag niets wat al in het gesprek of het profiel staat, en vraag niet naar ervaring:
pas je uitleg aan op hoe de gebruiker praat.

Stel **hooguit drie vragen**, en alleen als het antwoord een view verandert en je het niet kunt aannemen.
Stel ze na het voorstel, één voor één: één vraag per bericht, met een standaardantwoord ("Ik ga uit van
X, tenzij je iets anders zegt"). Al het andere is een aanname die je hardop zegt en vastlegt.

Wat de gebruiker als eerste wil zien, wordt een view, ook als jij een andere had gekozen: zeg een bezwaar
kort en laat de gebruiker beslissen. Zet in de schets een kopje *Keuzes van de gebruiker* met wat de
gebruiker besloot en wat een aanname is.

## Stappen

1. **Lees het profiel**: welke uitsplitsingen kunnen (meer dan één waarde), welke maten hebben een
   definitie, wat één rij is en of de sleutel uniek is (dat bepaalt of een view rijen of eenheden telt),
   welke kolommen per groep ongelijk ontbreken, welke regels gelden voor waarneembaarheid en privacy, en
   welke aanpakken `verkennen_data` voor de vraag voorstelde. Begin bij *Jouw aanpak* van de gebruiker, daarna de
   aanpakken van `verkennen_data`.
2. **Kies twee of drie views** die samen de vraag beantwoorden. Laat uitsplitsingen weg die het
   profiel niet draagt.
3. **Kies het grafiektype** met de skill `grafiekkeuze` (de TRIPS-beslisboom). Neem daaruit alleen de
   keuze en het pad in één regel (*"vergelijken, lange labels -> horizontaal staafdiagram"*), geen code:
   de schets blijft zonder code. Ontbreekt de skill, houd dan aan: groepen vergelijken met staven op een
   gemeenschappelijke nul-as, tijd met een lijn.
4. **Schrijf per view**: de vraag of hypothese, de maat (met verwijzing naar de definitie in het
   profiel), de uitsplitsing, het grafiektype met waarom, en welke groepen of perioden wegvallen
   door de privacydrempel of omdat ze nog niet waarneembaar zijn.
5. **Eindig met *Wat dit dashboard niet kan zeggen***: geen oorzaak maar hooguit verband, alleen de
   groepen boven de drempel, en niets over de werkelijkheid zolang het voorbeelddata is.

## Uitvoer

Eén bestand: `uitvoer/schets.html` (maak de map `uitvoer/` aan als die ontbreekt; alle gegenereerde HTML
hoort daar). Eén bestand zonder externe afhankelijkheden, met bovenaan de vraag en de keuze onder
*Datagebruik*, en daarna één blok per view. Staat in het profiel dat het demodata is, zet dat er
dan ook bij.

Geef geen commando om het bestand te openen: `open` en `xdg-open` werken niet in een container of
cloudomgeving. Noem het pad en de klikroute: in VS Code of Codespaces rechtsklik op het bestand en
*Show Preview*, of als die keuze er niet is *Download* en het gedownloade bestand openen; op een eigen
computer dubbelklikken op het bestand.

HTML-opmaak: semantische kopjes, per view een `<section>` met een kleine definitielijst
(`<dl>`: vraag, maat, uitsplitsing, grafiektype, valt weg), contrast minimaal 4,5:1, geen kleur als
enige onderscheid, leesbaar op een smal scherm. Eén inline `<style>`, geen scripts. Teken geen
nagebootste grafieken met verzonnen waarden: een leeg kader met een tekstbeschrijving is genoeg.

Zet in de schets een kopje *Nog open vragen* met hooguit drie punten: alleen wat een view verandert en
wat de gebruiker nog niet beantwoordde. Al het andere dat niet bevestigd is (open punten uit het profiel,
maten die je zelf nieuw voorstelt, keuzes die je zelf deed) staat als aanname met de gekozen waarde onder
*Keuzes van de gebruiker*, zodat de gebruiker het kan corrigeren. Laat niets onuitgesproken: wat nergens
staat, denkt de gebruiker dat al beslist is.

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
