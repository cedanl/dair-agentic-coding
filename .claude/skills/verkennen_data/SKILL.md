---
name: verkennen_data
description: Gebruik wanneer iemand een tabelbestand (CSV) wil verkennen voor er een dashboard of analyse komt — eerst afspreken welke data er gebruikt mag worden en sparren over de expertise en aanpak van de gebruiker, dan begrijpen wat de kolommen kunnen betekenen, definities vastleggen en casusgerichte ideeën en aanpakken bedenken voor de vraag van de gebruiker, met een HTML-profiel als uitkomst. De metainfo (codebook, definities, uitleg) komt van de gebruiker. LET OP — de views schetsen hoort bij `schets_dashboard` en het dashboard bouwen bij `bouwen_dashboard`.
allowed-tools: Read Grep Glob Write Bash
metadata:
  versie: "0.4.0"
---

# Data verkennen

Maakt van een ruw tabelbestand **begrip**: wat zou elke kolom kunnen betekenen, wat mag je ermee
zeggen, wat mag je niet laten zien en hoe kun je de vraag aanvliegen. De uitkomst is een
HTML-profiel dat vooral **conceptueel** is. Je schrijft geen dashboard, schetst geen views en
trekt geen conclusie.

Deze skill kent **geen domein**. Alles wat iets over de data zegt, komt van de gebruiker: een
codebook, uitleg bij de kolommen, definities van maten, drempels voor kleine groepen. Heeft de
gebruiker dat niet, dan stel je iets voor en laat je het bevestigen.

Het dashboard wordt vaak gemaakt op demodata of een voorbeeld, maar draait uiteindelijk op echte data
die de gebruiker zelf uploadt, zonder AI. Daarom beschrijft dit profiel wat voor soort kolommen er zijn en
hoe je ze kunt gebruiken, en niet wat de voorbeelddata toevallig laat zien.

De gebruiker stuurt, jij programmeert. Leg kort uit wat je gaat doen voor je het doet, en laat de
code zien (of zet 'm in een bestand) zodat de gebruiker mee kan lezen.

## Eerst afspreken en sparren

De gebruiker heeft kennis die jij niet hebt en blijft de regisseur, ook al doe jij het werk. Begin
met een korte ronde, **één vraag per bericht**, en wacht op het antwoord:

1. **Welke data is dit, en mag ik die lezen?** Dit bepaalt hoe je werkt (zie *Datagebruik*).
2. **Welke metainfo heb je?** Een codebook, kolomomschrijvingen, definities van maten, drempels. Vraag
   om een pad of laat de gebruiker het plakken. Zonder metainfo leid je betekenissen af uit de
   kolomnamen en markeer je ze als aanname.
3. **Wat weet je al van deze data of van dit onderwerp?** Pas daar je uitleg op aan: korter en
   technischer bij een expert, meer uitleg bij iemand die het nieuw vindt.
4. **Wat wil je weten, en hoe zou jij het aanvliegen? Wat denk je dat erachter zit?** Wat de gebruiker
   zegt, komt **eerst** in het profiel, onder *Jouw aanpak*, in de eigen woorden van de gebruiker.
   Jouw ideeën komen daarna.

Geef bij elke keuze waar het profiel van afhangt (definitie, uitsplitsing, drempel) **twee of drie
opties met één aanbeveling**, en laat de gebruiker kiezen. Beslis zelf niets wat inhoudelijk is.
Leg de keuzes vast in een kopje *Keuzes van de gebruiker*, zodat zichtbaar is wie wat besloot.

## Datagebruik

Data kan gevoelig zijn. Laat de gebruiker kiezen, en leg de keuze vast in het profiel onder
*Datagebruik*:

| Keuze | Wat jij doet |
|---|---|
| **Demo, synthetisch of openbaar** | Je mag de data lezen en het profiel vult zich met de structuur ervan. |
| **Eigen data die de gebruiker bewust mag delen** | Je mag de data lezen, maar toont nooit rijen of persoonsgegevens in je antwoord of in het profiel. Vraag één keer om bevestiging. |
| **Gevoelige of echte data** | Je leest **alleen de kolomnamen** en de metainfo, nooit rijen. De gebruiker draait `verken.py` zelf. Test later op synthetische data. |

Is de keuze niet duidelijk, kies dan de voorzichtigste. Een organisatie of werkgever kan eigen regels
hebben: vraag ernaar en volg die.

Altijd: baseer het begrip op **kolomnamen en metainfo**, niet op waarden of patronen in de voorbeelddata
(op echte data kunnen die anders zijn), en schrijf geen waarden uit de data in de skilltekst of in het script.

## Invoer

- Een CSV. Vraag naar het pad en het scheidingsteken. Zeg bij een groot bestand dat het script het niet
  in zijn geheel in het geheugen laadt.
- De metainfo van de gebruiker (zie hierboven), de vraag of casus in de woorden van de gebruiker, en de
  uitsplitsingen die de gebruiker wil gebruiken. Zonder vraag sla je het deel *Hoe de vraag aan te
  vliegen* over.

Lees het bestand met DuckDB (`read_csv('...', delim=';', header=true, all_varchar=true)`) en cast
zelf. Zo gaat niets stilletjes mis door een gegokt type. Laad het nooit in zijn geheel in pandas:
een echt bestand kan veel groter zijn dan de voorbeelddata, en het script moet daar later zonder
aanpassing op kunnen draaien. Lees kolomnamen uit de header en verzin ze niet.

## Stappen

### 1. Begrijp de kolommen

Loop de kolommen langs en geef per kolom, in **gewone taal**:

- **Rol**: identificatie, tijd, categorie (kan uitsplitsen), maat (getal) of vrije tekst
- **Wat het zou kunnen betekenen**, als aanname ("waarschijnlijk het jaar waarin...") en wat je
  nog niet zeker weet. Gebruik de metainfo als die er is; vraag bij twijfel de gebruiker, die kent het
  domein vaak beter.
- **Waar je op moet letten**: ontbrekende waarden die iets betekenen (leeg kan "niet van toepassing"
  zijn), codes die een leesbare naam hebben, kolommen die elkaar dupliceren of die persoonsgegevens
  bevatten (nooit tonen).

Schrijf dit weg als `begrip.json` (zie *Uitvoer*), niet als vaste tekst in het script. Het script
rekent alleen de structuur uit: aantal rijen en kolommen, unieke en ontbrekende waarden per kolom,
de kolommen met één waarde (die kunnen niet uitsplitsen) en de groepsgroottes.

### 2. Leg de definities vast

Schrijf de definities van de maten die de gebruiker wil gebruiken **letterlijk** in het profiel
onder het kopje *Definities*, met de kolommen waarop ze rusten. Neem ze uit de metainfo van de
gebruiker. Heeft de gebruiker ze niet, doe dan een voorstel en markeer het als *voorstel, bevestigd
door de gebruiker* zodra die akkoord is. Een maat zonder definitie komt het dashboard niet in.

Beschrijf per maat welke groepen of perioden **nog niet waarneembaar** kunnen zijn: de
observatietermijn zit dan nog niet in de data. Zeg dat als **regel** ("een periode telt pas mee als
de volgende periode in de data zit"), zodat het dashboard het zelf kan toepassen op elke data.

### 3. Bedenk casusgerichte ideeën en aanpakken

Alleen als er een vraag is. Denk mee over **deze vraag**, niet over data in het algemeen. Begin met
*Jouw aanpak* en voeg daarna jouw eigen ideeën toe, als ideeën en niet als bevindingen. Baseer ze op
de vraag, de kolommen en de metainfo, niet op waarden in de voorbeelddata. Bedenk:

- **Relevante kolommen**: welke kolommen de vraag direct raken, welke context geven en welke je juist
  buiten beschouwing laat, elk met een zin waarom.
- **Afgeleide maten en groepen**: wat je uit de kolommen kunt maken dat de vraag beter beantwoordt
  (een verhouding, een periode, een indeling in groepen), met de definitie erbij.
- **Hypotheses om te verkennen**: wat er achter de vraag kan zitten, als vraag geformuleerd ("Hangt X
  samen met Y?"), met bij elke hypothese een **alternatieve verklaring** of storende factor die je
  eerst moet uitsluiten.
- **Vergelijkingen**: welke groepen of perioden je naast elkaar zet en wat een eerlijke vergelijking
  nodig heeft (gelijke observatietermijn, voldoende groepsgrootte).
- **Valkuilen voor deze vraag**: wie of wat ontbreekt in de data, waar een verschil door de samenstelling
  van groepen kan komen, en waar een percentage vertekend kan zijn.
- **Ontbrekende data**: wat je zou willen weten maar niet in dit bestand zit, en of de gebruiker dat
  elders kan krijgen.
- **Vragen aan de gebruiker**: wat jij niet kunt weten maar de gebruiker wel.

Werk daarna twee of drie **mogelijke aanpakken** uit. Per aanpak:

- welke maat de vraag beantwoordt (met verwijzing naar de definitie)
- welke uitsplitsingen daarbij passen en welke niet kunnen (kolommen met één waarde, of te veel
  kleine groepen)
- wat de aanpak niet kan zeggen (verband is geen oorzaak, wie ontbreekt in de data)
- wat je nog zou willen weten van de gebruiker of uit de metainfo

Dit is een voorzet voor `schets_dashboard`, dat er de views van maakt. Laat de gebruiker kiezen welke
ideeën de moeite waard zijn en schrap wat niet past. Noem geen uitkomst.

### 4. Leg de privacyregels vast

Beschrijf de regels, niet de aantallen. Vraag de gebruiker welke drempels gelden, en stel anders
deze gangbare voorbeeldwaarden voor:

- Groepen met minder dan **30** personen worden niet getoond; een percentage waarvan teller of rest
  kleiner is dan **5** ook niet. Dit zijn voorbeeldwaarden, geen getoetste regel: een privacy officer
  of de eigen organisatie beslist.
- Is één groep onderdrukt, onderdruk dan ook de kleinste zichtbare groep, anders is de verborgen
  waarde terug te rekenen uit het totaal (secundaire onderdrukking). Dat is alleen nodig als het
  totaal van die uitsplitsing zichtbaar blijft, en je past het toe per uitsplitsing, niet over de
  hele pagina. Leg dit uit aan de gebruiker, het is niet vanzelfsprekend.
- Noem welke uitsplitsingen de kans op kleine groepen groot maken (veel kolommen tegelijk, kleine
  categorieën).

## Uitvoer

Drie bestanden:

- `uitvoer/data-profiel.html`: eerst *Datagebruik*, *Jouw aanpak* en *Keuzes van de gebruiker*, dan het
  begrip per kolom, de definities, de casusideeën en aanpakken voor de vraag en de privacyregels, en als bijlage de
  structuur van de data. Eén bestand zonder externe afhankelijkheden.
- `begrip.json`: je eigen tekst, met de velden `datagebruik`, `jouw_aanpak`, `keuzes`, `kolommen`
  (`{naam: {"rol", "betekenis", "let_op"}}`), `definities` (`[{"naam", "definitie"}]`) en
  `casus_ideeen` (`{"relevante_kolommen": [{"kolom", "waarom"}], "afgeleide_maten": [{"naam", "definitie"}],
  "hypotheses": [{"vraag", "alternatieve_verklaring"}], "vergelijkingen": [], "valkuilen": [],
  "ontbrekende_data": [], "vragen": []}`) en `casus_aanpak` (`[{"idee", "maat", "uitsplitsing", "kan_niet"}]`).
- `verken.py`: staat in `assets/` van deze skill. Kopieer het naar de werkmap en draai het:
  `python verken.py bestand.csv --begrip begrip.json`. Het leest het bestand en `begrip.json` en schrijft
  het profiel. Gebruik `--demo` alleen bij demodata. Het script bevat geen waarden uit de data en geen
  conclusies, zodat de gebruiker het later zonder AI op andere data kan draaien.

Alle gegenereerde HTML hoort in `uitvoer/` (maak de map aan als die ontbreekt), nooit naast de invoer.
Zet `uitvoer/` in `.gitignore`: een profiel dat later op echte data is gedraaid mag niet per ongeluk in
git belanden. Zeg erbij dat de gebruiker het bestand opent in de browser.

HTML-opmaak: semantische kopjes en `<table>` met `<caption>` en `<th scope>`, contrast minimaal
4,5:1, geen kleur als enige onderscheid, leesbaar op een smal scherm. Eén inline `<style>`, geen
scripts.

Eindig met een korte samenvatting in het gesprek: drie dingen die de gebruiker nu weet, en één
vraag die de data nog open laat. Noem hierin geen waarden uit de data.

## Let op

- Noem een verschil tussen groepen geen "effect" of "oorzaak".
- Het profiel zegt wat kolommen kunnen betekenen, niet wat er in de werkelijkheid geldt.
- Formuleer betekenissen als aanname zolang er geen metainfo is.
- De gebruiker beslist over de inhoud; jij legt uit, stelt voor en voert uit.
- Het volgende stuk, de views schetsen, doet `schets_dashboard`.
