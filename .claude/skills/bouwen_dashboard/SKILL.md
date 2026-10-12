---
name: bouwen_dashboard
description: Gebruik wanneer iemand uit een profiel en een schets (uitvoer/data-profiel.html en uitvoer/schets.html) een dashboard wil bouwen dat draait op data die de gebruiker zelf uploadt — zonder vragenronde vooraf: de keuzes komen uit de schets. Eerst een uploadscherm als eerste scherm en daarna grafiek, vergelijking en filter, met privacy-drempel, eerlijke framing, bron en toegankelijkheid, en een afronding met tests en waardencheck; bewaren in git alleen als de gebruiker erom vraagt. LET OP — de data eerst verkennen hoort bij `verkennen_data` en de views schetsen bij `schets_dashboard`.
disable-model-invocation: true
allowed-tools: Read Grep Glob Write Edit Bash
metadata:
  versie: "0.4.0"
---

# Dashboard bouwen

Bouwt uit `uitvoer/schets.html` een werkend én verantwoord dashboard dat de vraag van de gebruiker
beantwoordt. Het verantwoorden zit er **in verweven**: er is geen aparte stap achteraf.

Deze skill kent **geen domein**. Welke kolommen er zijn, wat de maten betekenen en welke definities
gelden, komt uit het profiel en van de gebruiker. Staat iets daarvan niet in het profiel, vraag het dan.

## Eerst sparren

De gebruiker bepaalt wat er gebouwd wordt, ook al schrijf jij de code.

Begin zonder vragenronde. Wat in het profiel en in de schets onder *Keuzes van de gebruiker* staat, is
beslist: vraag het niet opnieuw. Vraag niet naar ervaring: pas je uitleg aan op hoe de gebruiker praat,
met meer uitleg en kleinere stappen bij iemand die het nieuw vindt en kort en technisch bij een ervaren
gebruiker.

Noem je eigen aannames samen in **één regel** en begin daarna met bouwen, bijvoorbeeld *"Ik bouw voor
een groot bestand, in de Npuls-huisstijl, tenzij je iets anders zegt."* Dit neem je aan:

- **Wie het dashboard gebruikt:** afgeleid uit de vraag en de schets (een lezer zonder tijd krijgt weinig
  knoppen en duidelijke titels).
- **Bestandsgrootte:** een groot bestand (honderden MB, ruim 100 kolommen), tenzij het gesprek iets anders
  zegt. Bouw daarop (zie *Grote bestanden*) en zeg het eerlijk als de grootte een grens raakt. De
  voorbeelddata hoeft niet groot te zijn.
- **Huisstijl:** de Npuls-huisstijl, via de skill `vormgever-npuls-huisstijl`. Een eigen stijl of een
  rustig standaardthema alleen als de gebruiker dat zegt. Zie *Huisstijl*.

Stel **hooguit drie vragen**, en alleen over iets dat het bouwen van een view blokkeert. Stel ze één voor
één: één vraag per bericht, met een standaardantwoord ("Ik ga uit van X, tenzij je iets anders zegt").
Alles wat je aanneemt, zeg je hardop en leg je vast, zodat de gebruiker het kan corrigeren.

Bouw alle views uit de schets in één keer. Wat de gebruiker niet goed vindt aan een view had in de
schets al zichtbaar moeten zijn: de schets is het moment om te sturen, het bouwen voert die keuzes uit.
Vraag pas als alle views staan *wat zou je anders willen?*, en vraag de gebruiker zelf de
privacy-drempel en de definities in het dashboard te controleren: die beoordeling is van de gebruiker,
niet van jou. Vat aan het eind samen wat de gebruiker besloot en wat een aanname was.

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
- De kopjes *Keuzes van de gebruiker* en *Nog open vragen* in de schets (zie *Werkwijze*).

## Stack

Python, DuckDB voor de berekening en Streamlit voor het dashboard. Gebruikt de gebruiker iets anders,
volg dan die keuze. Installeer wat nodig is met uv in een virtuele omgeving
(`uv venv` en `uv pip install duckdb streamlit plotly polars pyarrow`). Volg de CEDA-standaard:
Polars voor DataFrames, `ruff` voor stijl, `pytest` voor tests. Zet de berekeningen in
`berekeningen.py` naast `app.py`, zodat ze los te testen zijn; `app.py` bevat alleen de weergave. Zet de
kolomnamen per rol, de lijst met verplichte kolommen, het scheidingsteken en de drempels in één
configuratie (`configuratie.py`), afgeleid van het profiel, niet verspreid door de code. Begin `app.py`
met `st.set_page_config(page_title=..., layout="wide")` en zet het thema in `.streamlit/config.toml`.
Start tijdens het bouwen met `streamlit run app.py` in de venv; hoe de gebruiker het opent staat onder
*Hoe de gebruiker het opent*. Gebruik `width="stretch"` in plaats van `use_container_width`.

Zet de code in een map `dashboard/` in de werkmap, niet in `uitvoer/` (dat staat in `.gitignore` en is
voor gegenereerde HTML). Die map bevat `app.py`, `berekeningen.py`, `configuratie.py`,
`requirements.txt`, `README.md`, `ruff.toml`, `tests/`, `.streamlit/config.toml` en `npuls/`
(stijlblad en logo).

Deze platte opzet (drie bestanden naast elkaar, geen pakket) is een bewuste keuze: het dashboard moet
klein en leesbaar blijven. Bouw er geen `src/`-indeling of `pyproject.toml` omheen, tenzij de gebruiker
daarom vraagt. Twee bestanden komen er wel bij: `requirements.txt` (de pakketten) en `README.md` (hoe de
gebruiker het dashboard opent, zie *Hoe de gebruiker het opent*).

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
naar het eerste scherm. Schrijf er twee functies voor (`toon_scherm_upload()` en `toon_scherm_dashboard()`, functienamen
beginnen met een werkwoord) en kies in `app.py` op basis van `st.session_state`. Geef het uploadscherm de stap als label ("Stap 1
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
  (geen schrijfactie naar schijf) en stuur de data nergens heen. De huisstijl laadt het lettertype van
  Google Fonts: dat is een aanroep van de browser zonder data, maar zeg het wel in de privacy-tekst
  ("alleen het lettertype wordt van Google Fonts geladen"), of lever het lettertype lokaal mee.

### Grote bestanden

De grootte van het echte bestand bepaalt hoe je de upload bouwt. Gemeten met een testbestand van 227 MB
(169.760 rijen, 186 kolommen): het hele bestand lezen kostte 28 seconden en 459 MB, alleen de
verplichte kolommen lezen kostte 2 seconden en 27 MB. Bouw het daarom zo:

- **Lees alleen de kolommen die je nodig hebt.** Lees eerst de kopregel (`nrows=0`), controleer de
  verplichte kolommen, en lees dan met `columns=` en `infer_schema=False`. Geef de upload zelf door
  aan `polars.read_csv` (met `seek(0)` ertussen) en niet `getvalue()`: dat maakt een kopie in het
  geheugen.
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
| Eenheid | Tel wat het profiel als eenheid van de rij noemt. Is de sleutel niet uniek, tel dan unieke sleutels en geen rijen, en zeg op het dashboard wat er geteld wordt. |
| Waarneembaarheid | Sluit perioden uit waarvan de observatietermijn niet volledig is (zie de regel in het profiel) en zeg dat op het dashboard. |
| Eerlijke framing | Geen woorden als "slechter" of "risicogroep" over groepen mensen; benoem de groep of eenheid, geen kenmerken van personen als oorzaak. Een verband is geen oorzaak. |
| Toegankelijkheid | Kleurenblind-veilig palet (niet alleen rood/groen), contrast minimaal 4,5:1, elke grafiek met een tekstuele samenvatting als alt-tekst, labels direct op de staven waar het past. |
| Bron en uitleg | Bronvermelding (bestandsnaam, de definities), peildatum en n per groep zichtbaar. Heeft de data geen peildatum, gebruik dan de laatste periode in de data en zeg dat, tenzij de gebruiker iets anders opgeeft. |

## Grafiekkeuze

Kies elke grafiek met `.claude/skills/grafiekkeuze/SKILL.md` (de TRIPS-beslisboom) en noem het pad kort bij je keuze
(*"vergelijken tussen groepen, lange labels -> horizontaal staafdiagram"*). De schets noemt per view al
een grafiektype: volg dat, tenzij de data het niet draagt. Ontbreekt de skill, houd dan aan: groepen
vergelijken met staven op een gemeenschappelijke nul-as, tijd met een lijn of kolommen.

In Streamlit teken je de grafiek met `st.plotly_chart(fig, width="stretch", theme=None)`, ook waar een
sjabloon uit `grafiekkeuze` `use_container_width` gebruikt. Streamlit zet anders zijn eigen kleuren over
die van de huisstijl heen. Zonder het Streamlit-thema ontbreken de automatische marges: zet
`automargin=True` op beide assen en `ticklabelstandoff` op de y-as, anders overlappen de labels de staven.

## Huisstijl

**De standaard is de Npuls-huisstijl.** Lees `.claude/skills/vormgever-npuls-huisstijl/SKILL.md` en volg
die voor je het scherm opmaakt (zie *Hulpskills lees je zelf*), en lees
`.claude/skills/vormgever-npuls-huisstijl/references/design-tokens.json`: kleuren, toegestane
kleurparen, typografie en grafiekkleuren staan daar. Pas de stijl toe met de bestanden hieronder. Alleen als de
gebruiker iets anders zegt:

- **Een eigen stijl**: de gebruiker geeft kleuren, lettertype en eventueel een logo.
- **Een rustig standaardthema**: licht, een accentkleur, zwarte tekst op wit, contrast minimaal 4,5:1.

Voor elke stijl geldt: zet het Streamlit-thema in `.streamlit/config.toml`, controleer elk kleurpaar op
contrast (kleine tekst 4,5:1, tekst vanaf 24px of vet vanaf 18,7px 3:1), en gebruik kleur nooit als enig
onderscheid.

### Npuls-huisstijl

De bron van deze stijl is de skill `vormgever-npuls-huisstijl`. Het lettertype is Plus Jakarta Sans, de
digitale vervanger van General Sans; gebruik nooit Inter of een ander vervangend lettertype. De regels
daaruit die je altijd controleert: minstens drie primaire kleuren zichtbaar, `npuls-zwart` alleen voor
tekst, alleen kleurparen uit `allowed_combinations`, fouten oranje en nooit rood. Het stijlblad in
`assets/npuls/` is de uitwerking voor dit dashboard (uploadscherm, hero, kaarten):

- `npuls-dashboard.css`: lettertype, hero, kaarten, pill-knoppen, uploadvak, zijbalk, meldingen en
  grafiekkaarten. Laad het met `st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)`.
- Het logo: `vormgever-npuls-huisstijl/assets/logos/npuls_logo.jpg`, het officiële beeldmerk. Kopieer het
  naar `dashboard/npuls/`; er staat bewust geen kopie in deze skill, zodat er één bron is. Zet het in de
  hero en gebruik het als favicon (`st.set_page_config(page_icon=...)`). De achtergrond van het bestand is
  `#F3D9DC`, vrijwel gelijk aan Npuls-roze, dus het hoort op roze (de hero) en niet op wit. Wijzig het
  logo niet: het valt buiten de CC BY-SA-licentie. Laat ruimte rondom ter grootte van de letter N en zet
  de payoff *Onderwijs bewegen.* (als je die toont) los van het logo. Lees
  `vormgever-npuls-huisstijl/references/merkcontext.md` voor de logo-regels.
- Gebruik **geen** kernvormen (ringen, pulse-curve) als decoratie in het dashboard. Het officiële logo is
  het enige beeld in de hero; de losse tekeningen in andere kleuren leiden af en zijn geen merk.

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

Opmaak van het scherm: roze hero met een grote blauwe kop en het officiële logo, een kaart "Zo werkt het" op
licht-blauw, privacy op licht-geel, het uploadvak met een gele pill-knop, de zijbalk roze, en de
grafieken op een witte achtergrond. Staven en lijnen zijn blauw (een tweede reeks oranje), met zwarte
labels en gridlijnen in grijs-200. Het demodata-label is een gele pill met zwarte tekst
(`.npuls-demo`). Zet de hero (`.npuls-hero`) op beide schermen bovenaan, met de stap als label
(*Stap 1 van 2*) en de vraag als kop.

Wat uit de praktijk volgt:

- De CSS richt zich op `data-testid` van Streamlit. De status van een melding zit in de inhoud
  (`stAlertContentError`, `...Info`, `...Success`, `...Warning`); Streamlit maakt fouten zelf rood, dus
  zonder deze CSS breek je de Npuls-regel. Controleer in een screenshot dat een fout oranje is.
- Op een smal scherm is de hero te groot: kleinere kop en een kleiner logo, boven de kop (staat in de CSS).
- Zet het lettertype ook in de Plotly-grafieken (`font.family`), en breek lange labels af met vaste
  spaties in `(n = 12)`, zodat ze op een telefoon niet worden afgekapt.
- Zet het logo als `<img>` met een base64-`data:`-URI in `st.markdown(..., unsafe_allow_html=True)`, met
  `alt="Npuls"`. Dan hoef je geen statische bestanden te serveren.

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

0. **Lees de keuzes en de open punten.** Lees *Keuzes van de gebruiker* en *Nog open vragen* in
   `uitvoer/schets.html`, en let op maten die de schets nieuw voorstelt en nog niet in het profiel staan.
   Wat bij de keuzes staat, vraag je niet opnieuw. Vraag alleen een open punt dat het bouwen van een
   view blokkeert, één vraag per bericht met een standaardantwoord, en leg het antwoord vast bij *Keuzes
   van de gebruiker* in de schets. Elk ander open punt wordt een aanname: zeg die hardop, leg haar vast
   en toon haar op het dashboard onder *Zo lees je dit*.
1. Lees `uitvoer/schets.html` en bouw alle views in de volgorde van de schets, in één keer. Zeg in
   één zin wat je gaat bouwen ("Ik bouw de drie views uit de schets") en vraag het niet als open vraag.
   De view die de vraag het meest direct beantwoordt staat bovenaan.
2. Test headless met `streamlit.testing.v1.AppTest`: geen exception, de periodekeuze stopt bij de
   laatste waarneembare periode, en een filter naar een kleine groep geeft "te weinig personen".
   Dat zegt meer dan alleen kijken of de server start. `AppTest` kan geen bestand uploaden: test het
   uploadscherm en de flow naar het dashboard in een echte browser (Playwright), en bekijk de
   screenshots zelf voor je zegt dat het er goed uitziet. Meld eerlijk wat je niet kon controleren,
   bijvoorbeeld hoe het er in de browser uitziet of de alt-tekst bij een schermlezer aankomt
   (Plotly in Streamlit heeft geen echte alt-tekst: zet de samenvatting in een `st.caption`).
3. **Bekijk het uiterlijk zelf, op de hele pagina.** De gebruiker moet bij de eerste blik tevreden zijn.
   Maak met Playwright screenshots van het uploadscherm, de foutmelding bij een bestand met ontbrekende
   kolommen en het dashboard, op 1280 en op 390 pixels breed, en kijk niet alleen naar het eerste scherm:
   maak de viewport zo hoog als de pagina (`scrollHeight` van `stMain`). Wacht op een tekst in de
   pagina, niet op een vaste tijd, anders fotografeer je een half gerenderd scherm. Kijk naar:
   - afgekapte labels, tekst of waarden (op smal scherm valt vaak tekst rechts van een staaf af: zet n
     dan bij het label);
   - filters die niet passen, zoals een rij chips in een klein vak (gebruik een schuif of vinkjes met de
     volledige naam);
   - een lange pagina met veel kleine grijze tekst (zet uitleg in een uitklapper en houd bovenaan één
     zin die uit de data is berekend);
   - getalnotatie in het Nederlands (punt voor duizendtallen, geen "5,811");
   - de huisstijl: het officiële logo staat in de hero en als favicon, minstens drie primaire kleuren zichtbaar, een foutmelding is oranje en niet rood
     (open daarvoor een bestand met ontbrekende kolommen), het lettertype is Plus Jakarta Sans, en de
     kleurparen komen uit `allowed_combinations`. Heb je `vormgever-npuls-huisstijl/SKILL.md` niet
     gelezen, doe dat dan nu.
   Pas aan en maak de screenshots opnieuw. Zeg niet "ziet er goed uit" voor je ze zelf bekeken hebt.
4. **Controleer of het inhoudelijk logisch is op de data.** Reken de maat onafhankelijk na, bijvoorbeeld
   met Polars, en vergelijk de aantallen met het dashboard. Controleer dat de totalen kloppen (aantal
   instromers is het aantal personen min het niet-waarneembare jaar) en controleer de aannames waarop de
   definitie rust: heeft elke persoon één instroomjaar, zijn er gaten, staat een diploma op de laatste
   rij, wisselen mensen van groep. Zet wat je vindt als beperking onder *Zo lees je dit*. Trek geen
   conclusie over de werkelijkheid uit demodata, ook niet in de samenvatting.
5. **Test een groot bestand** zoals bij *Grote bestanden* staat, en meld de gemeten tijd en het geheugen.
   Maak het bestand buiten de repo en verwijder het daarna. Meet in een schoon proces: een bestand dat je
   in hetzelfde proces maakt, vertekent het geheugen.
6. **Leg uit hoe de gebruiker het opent** (zie *Hoe de gebruiker het opent*) en test dat het commando
   werkt.
7. **Rond af (zie *Afronden*).** Dit hoort bij het bouwen: bewaar de tests, doe de waardencheck en de
   snelle stijlcheck en test opnieuw. Vraag er geen toestemming voor en zeg niet dat het dashboard
   klaar is voor het is gedaan. `check-style` en `simplify-ceda` draai je niet zelf (zie *Afronden*).
8. Vat samen: welke keuzes zijn gemaakt, welke checks zijn toegepast, wat blijft open, en hoe de
   gebruiker het dashboard opent.

## Hoe de gebruiker het opent

De gebruiker kent `streamlit run` niet en weet niet waar het dashboard opent. Leg dat uit, zowel in een
`README.md` naast `app.py` als in de samenvatting in het gesprek.

- **Eén startcommando zonder voorinstallatie**, in de map van het dashboard:
  `uv run --no-project --with-requirements requirements.txt streamlit run app.py`. Test dat het werkt
  (`... streamlit --version`). Zet de pakketten in `requirements.txt`.
- **Waar het opent:** op een eigen computer opent de browser vanzelf, anders `http://localhost:8501`. In
  GitHub Codespaces verschijnt rechtsonder een melding over poort 8501 (*Open in Browser*), en anders
  staat het wereldbolletje bij poort 8501 in het tabblad *Poorten*.
- **Wat de gebruiker daarna doet:** welk bestand te uploaden (in Codespaces eerst downloaden), wat stap 2
  laat zien, hoe je stopt (`Ctrl+C`) en wat je doet als het niet lukt (melding over kolommen, te groot
  bestand, poort bezet).
- Noem alleen wat je getest hebt. Heb je iets niet kunnen testen, zoals een 403 bij uploaden in
  Codespaces, zeg dat dan erbij.

## Afronden

Afronden is onderdeel van bouwen: het dashboard is af als de tests zijn bewaard en slagen en de
waardencheck is gedaan. Doe deze stappen achter elkaar als alle views staan, zonder per stap
toestemming te vragen. Meld per stap in één regel wat eruit kwam.

1. **Tests bewaren.** Zet de tests uit *Werkwijze* in `dashboard/tests/test_dashboard.py` (pytest), zodat
   ze later opnieuw te draaien zijn:
   `uv run --no-project --with-requirements requirements.txt --with pytest pytest tests`. De tests
   rekenen de aantallen onafhankelijk na, controleren de drempels en de secundaire onderdrukking,
   meten dat het uploadscherm eerst komt en dat het dashboard alle views toont.
2. **Waarden uit de voorbeelddata.** Zoek in de code naar waarden uit de voorbeelddata die er letterlijk
   in staan (groepsnamen, codes, jaartallen). Die horen uit de data of uit de configuratie te komen,
   zodat het dashboard op andere data draait. Haal elke treffer uit de code, of leg uit waarom het
   geen datawaarde is. Toon bij gevoelige data de gevonden waarden niet.
3. **Snelle stijlcheck.** Draai `uvx ruff check .` en `uvx ruff format .` met `dashboard/ruff.toml`
   (regelbreedte 100, regels E, F, I, N, W, UP). Dat kost seconden. Houd je aan de CEDA-regels bij
   het schrijven: functienamen met een werkwoord, type hints, Polars in plaats van pandas, en geen kale
   `except Exception`.
4. **Opnieuw testen.** Draai de tests opnieuw, en kijk de schermen opnieuw in de browser als de
   vorige stappen de weergave of het inlezen hebben veranderd.
5. **Bewaren aanbieden.** Commit en push niets uit jezelf. Sluit af met één regel: *"Wil je dit bewaren in
   je eigen GitHub? Zeg dan 'bewaar'."*

**Optioneel, niet standaard.** `check-style` en `simplify-ceda` kosten veel tijd (drie review-agents,
een plugin en opnieuw testen) en horen niet bij de workshopronde. Draai ze niet zelf. Noem ze alleen aan
het eind in één zin: *"Wil je dat ik de code nakijk? Typ dan `/check-style` of `/simplify-ceda`."*

Ontbreekt een van de skillbestanden die je leest, sla die stap dan over en meld het.

## Hulpskills lees je zelf

Alle skills in deze repo starten alleen als de gebruiker ze zelf typt (`/naam`): ze hebben
`disable-model-invocation: true`, zodat ze niet vanzelf aanspringen tijdens gewoon chatten. Daardoor
kun je ze ook niet met de Skill-tool aanroepen. De hulpskills `grafiekkeuze`,
`vormgever-npuls-huisstijl` en `ship` lees je daarom als bestand
(`.claude/skills/<naam>/SKILL.md`) en je volgt wat daarin staat, als onderdeel van deze skill. De
gebruiker heeft `bouwen_dashboard` zelf gestart; dat is de toestemming.

## Bewaren, alleen op verzoek

Commit en push alleen als de gebruiker erom vraagt, en nooit zonder bevestiging.

1. **Laat zien wat er gebeurt.** Noem de bestanden die meegaan (de code van het dashboard; geen
   `uitvoer/`, geen `.venv/` en geen databestanden die nog niet in de repo stonden) en de repo waar ze
   heen gaan. Heeft de gebruiker geen schrijfrechten op die repo, zeg dan dat GitHub een kopie (fork) in
   het eigen account van de gebruiker maakt, en dat die kopie **openbaar** is als de oorspronkelijke repo
   openbaar is. Vraag om akkoord.
2. **Na akkoord:** lees `.claude/skills/ship/SKILL.md` en volg die om te committen en te pushen. In een Codespace regelt
   `GITHUB_TOKEN` de toegang tot de repo: laat die staan, ook waar `ship` aanraadt hem te unsetten.
3. **Weigert de push:** omzeil dat niet en vraag geen token. Zeg dat het werk lokaal gecommit is en geef
   de klikroute om de bestanden te downloaden: rechtsklik op het bestand in de verkenner en *Download*.

## Let op

- Onderdrukte groepen laat je weg uit de grafiek en noem je in de tekstuele samenvatting. Controleer
  het kleurcontrast echt (4,5:1) en neem niet aan dat een palet voldoet.
- Geen interactie of extra scherm "voor de zekerheid": houd het bij wat de vraag nodig heeft.
- Vermeld op het dashboard dat het demodata is, via het vinkje uit *Datagebruik*.
- Gebruik in elke tekst, ook de samenvatting onder een grafiek, dezelfde leesbare labels als in de grafiek
  zelf (dus niet de ruwe waarde "B Bedrijfskunde" als de grafiek "Bedrijfskunde" toont).
