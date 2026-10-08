---
name: bouwen_dashboard
description: Gebruik wanneer iemand uit een profiel en een schets (uitvoer/data-profiel.html en uitvoer/schets.html) een dashboard wil bouwen dat draait op data die de gebruiker zelf uploadt — eerst sparren over ervaring, gebruikers, bestandsgrootte en huisstijl, dan een uploadscherm als eerste scherm en daarna grafiek, vergelijking en filter, met privacy-drempel, eerlijke framing, bron en toegankelijkheid. LET OP — de data eerst verkennen hoort bij `verkennen_data` en de views schetsen bij `schets_dashboard`.
allowed-tools: Read Grep Glob Write Edit Bash
metadata:
  versie: "0.3.0"
---

# Dashboard bouwen

Bouwt uit `uitvoer/schets.html` een werkend én verantwoord dashboard dat de vraag van de gebruiker
beantwoordt. Het verantwoorden zit er **in verweven**: er is geen aparte stap achteraf.

Deze skill kent **geen domein**. Welke kolommen er zijn, wat de maten betekenen en welke definities
gelden, komt uit het profiel en van de gebruiker. Staat iets daarvan niet in het profiel, vraag het dan.

## Eerst sparren

De gebruiker bepaalt wat er gebouwd wordt, ook al schrijf jij de code. Stel **één vraag per
bericht** en wacht op het antwoord:

1. *Wat is je ervaring met dashboards of Python?* Pas daar je uitleg op aan: meer uitleg en
   kleinere stappen bij iemand die het nieuw vindt, kort en technisch bij een ervaren gebruiker.
2. *Wie gebruikt het dashboard straks met de echte data, en wat moet diegene er zelf mee kunnen
   doen?* Dit bepaalt filters en de uploadflow.
3. *Hoe groot is het echte bestand waar dit dashboard straks mee draait?* Een echt bestand kan
   honderden MB en ruim 100 kolommen hebben, terwijl de voorbeelddata maar enkele MB is. Vraag naar
   rijen of MB, en of het dashboard lokaal of in een gedeelde omgeving draait. Vang het op in het
   ontwerp (zie *Grote bestanden*) en zeg het eerlijk als de grootte een grens raakt. Neem de grootte
   van de voorbeelddata niet over: die hoeft niet groot te zijn.
4. *Welke huisstijl wil je gebruiken?* Een eigen stijl, de bijgeleverde voorbeeldstijl (Npuls), of
   een rustig standaardthema. Zie *Huisstijl*.

Geef bij elke ontwerpkeuze (volgorde van de views, filters, titels, kleuren) **twee of drie opties
met één aanbeveling** en laat de gebruiker kiezen. Bouw een view eerst, laat de gebruiker kijken
en vraag *wat zou je anders willen?* voor je de volgende bouwt. Vraag de gebruiker ook om zelf
de privacy-drempel en de definities in het dashboard te controleren: die beoordeling is van
de gebruiker, niet van jou. Vat aan het eind samen wat de gebruiker besloot.

## Datagebruik

Volg de keuze onder *Datagebruik* in het profiel (zie `verkennen_data`). Is die er niet, vraag dan:
is de data die je bij het bouwen nodig hebt demo, synthetisch of openbaar, of mag de gebruiker die
bewust delen, of is het gevoelig? Bij gevoelige data lees je nooit rijen en test je alleen op synthetische
data die jij of de gebruiker maakt.

Echte data gaat pas door de tool als die af is en er geen AI meer bij betrokken is. Bouw het
dashboard daarom zo dat het zonder jou op andere data te draaien is:

- Het dashboard **laadt zelf geen data**. Het **eerste scherm is het uploadscherm** (zie hieronder) en
  het dashboard opent pas na een geslaagde upload. Geen pad naar voorbeelddata in de code, geen
  terugval op een bestand.
- Geen waarden, kolomwaarden of groepsnamen uit de voorbeelddata in de code. Groepen, perioden en
  waarneembaarheid komen uit de data zelf.
- Het label *Dit is demodata* volgt een vinkje op het uploadscherm (standaard aan, de gebruiker
  zet het uit bij echte data) en is geen vaste tekst.
- Een uitspraak over de werkelijkheid doe je nooit op demodata, ook niet in de samenvatting.

## Invoer

- `uitvoer/data-profiel.html` uit `verkennen_data` en `uitvoer/schets.html` uit `schets_dashboard`.
  Ontbreken ze, draai dan eerst die skills, of vraag de gebruiker om de kolommen, de maten en de
  definities.
- Voorbeelddata om te testen. Het dashboard leest die niet zelf, je uploadt hem. In een cloudomgeving
  zoals GitHub Codespaces kiest de bestandsdialoog van de browser een bestand van de eigen computer,
  niet uit de omgeving. Laat de gebruiker het bestand dan eerst downloaden en dan uploaden.
- De vraag die het dashboard beantwoordt (staat bovenaan de schets).

## Stack

Python, DuckDB voor de berekening en Streamlit voor het dashboard. Gebruikt de gebruiker iets anders,
volg dan die keuze. Installeer wat nodig is met uv in een virtuele omgeving
(`uv venv` en `uv pip install duckdb streamlit plotly`). Zet de berekeningen in
`berekeningen.py` naast `app.py`, zodat ze los te testen zijn; `app.py` bevat alleen de weergave. Zet de
kolomnamen per rol, de lijst met verplichte kolommen, het scheidingsteken en de drempels in één
configuratie (`configuratie.py`), afgeleid van het profiel, niet verspreid door de code. Begin `app.py`
met `st.set_page_config(page_title=..., layout="wide")` en zet het thema in `.streamlit/config.toml`.
Start met `streamlit run app.py`. Gebruik `width="stretch"` in plaats van `use_container_width`.

## Wat het dashboard minimaal heeft

1. **Een grafiek** die de vraag beantwoordt. De titel wordt **uit de data berekend** bij het
   laden ("X is het hoogst bij <groep>") of is de vraag zelf ("Verschilt X per Y?").
   Nooit een vaste conclusie in de code: die zou op echte data verkeerd kunnen zijn.
2. **Een vergelijking** tussen groepen of perioden, met één gemeenschappelijke nul-as.
3. **Een filter** op de uitsplitsingen uit de schets, waarbij de privacy-drempel opnieuw wordt
   toegepast op de gefilterde groep.
4. **Een uploadscherm als eerste scherm** (zie hieronder).
5. **Een zijbalk of kader "Zo lees je dit"** met definities (uit `uitvoer/data-profiel.html`), bron en de
   zin *Wat dit dashboard niet kan zeggen*.

## Eerste scherm: data uploaden

Het dashboard is gemaakt op voorbeelddata maar draait straks op echte data, door iemand zonder AI. Het
eerste scherm is daarom het uploadscherm: geen tabbladen, alleen dit scherm tot er geldige data is.
Daarna toont de app het dashboard, met in de zijbalk een knop *Andere data uploaden* die terugkeert
naar het eerste scherm. Schrijf er twee functies voor (`scherm_upload()` en `scherm_dashboard()`) en
kies in `app.py` op basis van `st.session_state`. Geef het uploadscherm de stap als label ("Stap 1
van 2") en het dashboard "Stap 2 van 2".

Het uploadscherm heeft:

- `st.file_uploader` voor een CSV, met uitleg welke kolommen nodig zijn en wat de verwachte opmaak is.
  Het scheidingsteken komt uit de configuratie.
- **Controle op de kolommen**: ontbreken er kolommen die de berekening nodig heeft, toon dan één
  heldere melding met de ontbrekende kolomnamen en gebruik de upload niet. Geen traceback.
- Een geslaagde upload opent meteen het dashboard (`st.rerun()`). Toon op het dashboard de
  bestandsnaam als bron; toon nergens rijen uit de data.
- Een vinkje *Dit bestand is demodata* (standaard aan) dat bepaalt of het demodata-label getoond wordt.
  Zet de keuze bij een geslaagde upload over naar een eigen sleutel in `st.session_state`: een
  widget dat niet meer getoond wordt, verliest zijn waarde.
- Een knop *Andere data uploaden* in de zijbalk van het dashboard. Geef de uploader een `key` met een
  teller en verhoog die bij het terugkeren: anders blijft het bestand in de uploader staan en wordt
  het meteen opnieuw ingelezen.
- Een korte privacy-tekst: de data wordt alleen in het geheugen van deze sessie gebruikt, niet
  opgeslagen en nergens naartoe gestuurd. Zorg dat dat klopt: lees de upload in het geheugen
  (geen schrijfactie naar schijf) en doe geen externe aanroepen.

### Grote bestanden

De grootte van het echte bestand bepaalt hoe je de upload bouwt. Gemeten met een testbestand van 227 MB
(169.760 rijen, 186 kolommen): het hele bestand lezen kostte 28 seconden en 459 MB, alleen de
verplichte kolommen lezen kostte 2 seconden en 27 MB. Bouw het daarom zo:

- **Lees alleen de kolommen die je nodig hebt.** Lees eerst de kopregel (`nrows=0`), controleer de
  verplichte kolommen, en lees dan met `usecols`. Geef de upload zelf door aan `pandas.read_csv` (met
  `seek(0)` ertussen) en niet `getvalue()`: dat maakt een kopie in het geheugen.
- **Zet de grens bewust.** Streamlit weigert standaard bestanden boven 200 MB. Zet in
  `.streamlit/config.toml` onder `[server]` een `maxUploadSize` (in MB) die bij het bestand past en
  toon die grens op het uploadscherm (`st.get_option("server.maxUploadSize")`). Een upload staat in het
  geheugen van de server: reken ruim, en zeg de gebruiker dat dit geheugen kost.
- **Toon voortgang.** Een `st.spinner` met de bestandsnaam en grootte tijdens het lezen, en daarna
  alleen het aantal rijen als bron, nooit rijen uit de data.
- **Maak de verbinding één keer.** Bouw de DuckDB-verbinding bij de upload en bewaar die in
  `st.session_state`, niet bij elke herberekening. Gooi hem weg bij *Andere data uploaden*.
- **Vang een geheugenfout op** (`MemoryError`) met een melding die zegt dat het bestand te groot is en
  dat de gebruiker alleen de verplichte kolommen in een kleiner bestand kan opslaan.
- **Past het nog niet?** Bespreek met de gebruiker: een kleiner bestand met alleen de nodige kolommen,
  een ander formaat zoals parquet, of het dashboard lokaal laten draaien en een pad laten opgeven in
  plaats van uploaden. Dat laatste leest van schijf; leg dan uit dat de data dan niet via de browser
  binnenkomt.

Test met een groot testbestand dat je zelf maakt **buiten de repo** (bijvoorbeeld in een tijdelijke
map), op basis van de voorbeelddata met extra kolommen en herhaalde rijen. Meet de tijd en het geheugen,
en verwijder het bestand daarna. Zet geen groot bestand in de repo.

Na een upload berekent het dashboard alles uit die data: groepen, perioden, drempels en
waarneembaarheid. De bron toont de bestandsnaam.

Test de upload alleen met voorbeelddata waar de gebruiker mee akkoord is, bijvoorbeeld met Playwright
(`set_input_files`), en test ook een bestand met ontbrekende kolommen.

## Responsible, verweven

| Check | Wat jij doet |
|---|---|
| Privacy | Toon geen groep onder de drempel (voorbeeldwaarden: 30 personen per groep, 5 per percentage-cel; de echte waarden staan in `uitvoer/data-profiel.html`). Toon in plaats daarvan "te weinig personen" en pas secundaire onderdrukking toe. Bouw de drempel als parameter in `configuratie.py`, niet hardcoded in elke grafiek. |
| Waarneembaarheid | Sluit perioden uit waarvan de observatietermijn niet volledig is (zie de regel in het profiel) en zeg dat op het dashboard. |
| Eerlijke framing | Geen woorden als "slechter" of "risicogroep" over groepen mensen; benoem de groep of eenheid, geen kenmerken van personen als oorzaak. Een verband is geen oorzaak. |
| Toegankelijkheid | Kleurenblind-veilig palet (niet alleen rood/groen), contrast minimaal 4,5:1, elke grafiek met een tekstuele samenvatting als alt-tekst, labels direct op de staven waar het past. |
| Bron en uitleg | Bronvermelding (bestandsnaam, de definities), peildatum en n per groep zichtbaar. Heeft de data geen peildatum, gebruik dan de laatste periode in de data en zeg dat, tenzij de gebruiker iets anders opgeeft. |

## Grafiekkeuze

Kies de grafiek in een vaste volgorde: eerst verhaal, publiek en doel, dan de datastructuur (de
TRIPS-beslisboom). Noem het pad kort bij je keuze (*"vergelijken tussen groepen, lange labels
-> horizontaal staafdiagram"*).

- Vergelijken tussen groepen: staafdiagram, horizontaal bij lange labels. Over tijd: lijn of kolommen.
- Cirkeldiagram alleen voor deel-van-geheel in één periode, en niet bij meer dan 5-7 delen.
- Een extra groepering wordt een facet, geen derde dimensie in één grafiek.
- Plotly in Streamlit: `st.plotly_chart(fig, width="stretch", theme=None)`. Streamlit zet anders zijn
  eigen kleuren over die van de huisstijl heen. Zonder het Streamlit-thema ontbreken de automatische
  marges: zet `automargin=True` op beide assen en `ticklabelstandoff` op de y-as, anders overlappen de
  labels de staven.

## Huisstijl

Vraag welke huisstijl de gebruiker wil (zie *Eerst sparren*) en volg die. Opties:

- **Een eigen stijl**: de gebruiker geeft kleuren, lettertype en eventueel een logo.
- **De bijgeleverde voorbeeldstijl (Npuls)**, in `assets/npuls/`. Zie hieronder.
- **Een rustig standaardthema**: licht, een accentkleur, zwarte tekst op wit, contrast minimaal 4,5:1.

Voor elke stijl geldt: zet het Streamlit-thema in `.streamlit/config.toml`, controleer elk kleurpaar op
contrast (kleine tekst 4,5:1, tekst vanaf 24px of vet vanaf 18,7px 3:1), en gebruik kleur nooit als enig
onderscheid.

### Voorbeeldstijl: Npuls

Deze stijl volgt de tokens van de Npuls-huisstijl: kleur is de persoonlijkheid, dus minstens drie
primaire kleuren zichtbaar, alleen toegestane kleurparen, Plus Jakarta Sans als lettertype (nooit
Inter) en royale afronding. Gebruik hem alleen als de gebruiker bij Npuls hoort of er uitdrukkelijk om
vraagt. De bestanden in `assets/npuls/`:

- `npuls-dashboard.css`: lettertype, hero, kaarten, pill-knoppen, uploadvak, zijbalk, meldingen en
  grafiekkaarten. Laad het met `st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)`.
- `concentrische-ringen.svg` en `pulse-curve.svg`: kernvormen als decoratie, zoals ze zijn. Wijzig ze
  niet; ze vallen onder CC BY-SA 4.0 en de naamsvermelding hoort bij het gebruik.

Thema:

```toml
[theme]
base = "light"
primaryColor = "#3D68EC"
backgroundColor = "#FFFFFF"
secondaryBackgroundColor = "#FAEAEA"
textColor = "#000000"

[client]
toolbarMode = "minimal"
```

Opmaak van het scherm: roze hero met een grote blauwe kop en een vorm, een kaart "Zo werkt het" op
licht-blauw, privacy op licht-geel, het uploadvak met een gele pill-knop, de zijbalk roze, en de
grafieken in een witte kaart. Staven zijn blauw en oranje, met zwarte labels, gridlijnen in grijs-200
en een witte achtergrond.

Contrast van deze kleuren, zelf berekend:

| Paar | Contrast | Gebruik |
|---|---|---|
| zwart op wit | 21,0 | alle tekst |
| blauw op wit | 4,78 | links en kleine tekst |
| zwart op geel | 14,7 | knoppen en label |
| zwart op roze | 15,8 | zijbalk |
| blauw op roze | 3,6 | alleen de grote hero-kop, niet in de zijbalk |
| oranje op wit | 3,06 | alleen vlakken en staven, nooit tekst |
| groen op wit | 2,82 | alleen vlakken, nooit tekst |

De zijbalk heeft daarom zwarte tekst op roze. Cooper Light is een projectasset en wordt niet geladen;
de intro valt terug op Georgia.

## Werkwijze

1. Lees `uitvoer/schets.html`, kies met de gebruiker welke view het eerst komt, bouw die.
2. Test headless met `streamlit.testing.v1.AppTest`: geen exception, de periodekeuze stopt bij de
   laatste waarneembare periode, en een filter naar een kleine groep geeft "te weinig personen".
   Dat zegt meer dan alleen kijken of de server start. `AppTest` kan geen bestand uploaden: test het
   uploadscherm en de flow naar het dashboard in een echte browser (Playwright), en bekijk de
   screenshots zelf voor je zegt dat het er goed uitziet. Meld eerlijk wat je niet kon controleren,
   bijvoorbeeld hoe het er in de browser uitziet of de alt-tekst bij een schermlezer aankomt
   (Plotly in Streamlit heeft geen echte alt-tekst: zet de samenvatting in een `st.caption`).
3. Vat samen: welke keuzes zijn gemaakt, welke checks zijn toegepast, wat blijft open.

## Let op

- Onderdrukte groepen laat je weg uit de grafiek en noem je in de tekstuele samenvatting. Controleer
  het kleurcontrast echt (4,5:1) en neem niet aan dat een palet voldoet.
- Geen interactie of extra scherm "voor de zekerheid": houd het bij wat de vraag nodig heeft.
- Vermeld op het dashboard dat het demodata is, via het vinkje uit *Datagebruik*.
- Gebruik in elke tekst, ook de samenvatting onder een grafiek, dezelfde leesbare labels als in de grafiek
  zelf (dus niet de ruwe waarde "B Bedrijfskunde" als de grafiek "Bedrijfskunde" toont).
