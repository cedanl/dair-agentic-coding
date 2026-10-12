# Aantekeningen: skills uit cedanl/.github in de workshop

Doel: aan deelnemers laten zien dat we de CEDA-skills zelf gebruiken. Nog niet in de presentatie
opgenomen; hier staat wat we later kunnen tonen.

Bron: `cedanl/.github`, map `.claude/skills/` (69 skills, peildatum commit `da22569`, 2026-10-06).

## Verweven in de workshopskills

| CEDA-skill | Waar verweven | Wat er is gedaan |
|---|---|---|
| `grafiekkeuze` (TRIPS-beslisboom) | `schets_dashboard` stap 3 (grafiektype kiezen) en `bouwen_dashboard` (sectie *Grafiekkeuze*) | Grafiektype kiezen via verhaal, publiek, doel en datastructuur, met het pad in één regel. Vuistregels overgenomen: horizontaal bij lange labels, cirkel alleen één periode en max. 5-7 delen, extra groepering als facet. |
| `streamlit`, `init-repo` (alleen de huisregels) | `bouwen_dashboard` (sectie *Stack*) | Regel "de app bevat geen businesslogica" (`berekeningen.py` naast `app.py`), `st.set_page_config` en het thema in `.streamlit/config.toml`. Niet de projectstructuur zelf. |
| `vormgever-npuls-huisstijl` | `bouwen_dashboard` (sectie *Huisstijl*) | Npuls is de standaard: thema, hero met het officiële logo, kleuren en lettertype uit `design-tokens.json`, plus een contrastcheck die wij zelf deden (zie hieronder). |

De essentie staat in de skills zelf, dus deelnemers hoeven de CEDA-skills niet te hebben geïnstalleerd.

## Opvallend bij het verweven (goed verhaal voor de presentatie)

Npuls-kleuren op wit, contrast berekend:

| Kleur | Contrast op wit | Tekst (4,5:1) |
|---|---|---|
| Zwart #000000 | 21,0 | ja |
| Blauw #3D68EC | 4,78 | ja |
| Oranje #DD784B | 3,06 | nee |
| Groen #00AF81 | 2,82 | nee |
| Geel #F4D74B | 1,43 | nee |
| Roze #F4D9DC | 1,33 | nee |

De huisstijl is dus niet vanzelf toegankelijk. Alleen blauw en zwart zijn geschikt voor tekst; oranje en
groen alleen voor staven. Dat sluit aan op de toegankelijkheidscheck in `bouwen_dashboard`, die zegt
niet aan te nemen dat een palet voldoet.

## Bewust niet verweven

| CEDA-skill | Reden |
|---|---|
| `sessie-terugblik` | Lijkt op onze `review-reflect`, maar schrijft naar `cedanl/repo-context-as-data` en vraagt schrijfrechten. Voor deelnemers niet bruikbaar. Wel een goed voorbeeld van dezelfde vorm: vaste vragenset, antwoorden in de woorden van de deelnemer. |
| `brainstorm`, `sparren` | Passen bij het schetsen van views, maar `verkennen_data` doet dat al stap voor stap. Zou de workshop uitbreiden. |
| `clidev`, `clanna`, `powerclaude`, `build-marp-deck`, `npuls-huisstijl` (presentatiedeel) | Voor de presentatie zelf, niet voor de deelnemersopdracht. Kandidaat om de presentatie mee te maken. |
| `streamlit` (volledige opzet), `init-repo` (scaffolding) | `streamlit` wil een `src/`-layout met multipage-navigatie en `init-repo` bouwt een compleet nieuw repo met devcontainer, `pyproject.toml`, `ty` en CLAUDE.md. Te zwaar voor één dashboard in een workshopronde van een uur, en de deelnemers werken al in een kant-en-klare omgeving. Ook zegt `streamlit` dat de UI niet headless te testen is; wij doen dat wel met `AppTest`. |
| `branch-pr`, `ship`, `check-style`, `simplify-ceda`, `actions-ci`, `docker` | Ontwikkel- en deploywerk, buiten de scope van de workshopronde. |
| `voorspellen-*`, `ceda-*analyse`, `centrale-inzichten-*`, `hoe-kunnen-we`, `ideeen-ontwikkelen`, `mindmapping` | Andere workshops of vakgebieden. |
| `surf-*`, `sdp-*`, `objectstore-*`, `sram-oidc`, `surfdrive`, `etl-pipeline`, `gitlab-ci` | Infrastructuur, niet relevant voor deelnemers. |

## Later toe te voegen aan de presentatie

- Eén dia: "Deze workshop is gebouwd met onze eigen skills", met de twee gebruikte skills hierboven.
- De contrasttabel als voorbeeld dat een huisstijl niet automatisch toegankelijk is.
- Eventueel `review-reflect` naast `sessie-terugblik` zetten als voorbeeld van hergebruik.

## Wijziging: verkennen_data opgesplitst (2026-10-08)

- `verkennen_data` is nu generiek (profiel, definities, kleine groepen); 1CHO-kolommen en -definities staan in `references/1cho.md`.
- Het schetsen is een eigen skill: `schets_dashboard`.
- Uitkomsten zijn HTML in `uitvoer/` (staat in `.gitignore`): `data-profiel.html` en `schets.html`. `verken.py` maakt het profiel en is later zonder AI op echte data te draaien.
- Principe in alle drie de skills: tijdens de ontwikkeling alleen demodata, nooit echte data opsturen, en geen conclusies uit demodata (titels zijn vragen of worden uit de data berekend).
- `sparren` als eerste stap vóór `verkennen_data` is besproken maar nog niet toegevoegd.
- Kopie in `workshop-dair-begeleider/skills/` is niet bijgewerkt.

## Voor de presentatie: het dashboard in Npuls-huisstijl (2026-10-08)

Nog niet in de presentatie opgenomen; dit gaan we op termijn wel laten zien.

- **Wat te tonen:** het uploadscherm als eerste scherm (roze hero met het officiële Npuls-logo, gele pill-knop) en daarna het dashboard met roze zijbalk en grafieken in witte kaarten. Screenshots staan in `uitvoer/testrun/` (`11-` t/m `14-`).
- **Verhaal:** de workshop gebruikt onze eigen CEDA-skills. Het dashboard is gestyled met `vormgever-npuls-huisstijl`, de grafiekkeuze volgt `grafiekkeuze`.
- **Opvallend (zelf nagerekend):** een huisstijl is niet automatisch toegankelijk. Blauw op roze haalt maar 3,6:1, dus de zijbalk heeft zwarte tekst in plaats van de blauwe tekst uit de gids. Oranje en groen halen geen 3:1 bij kleine tekst, dus ze zijn er alleen voor vlakken en staven.
- **Bijvangst:** de oude Streamlit-asset van `npuls-huisstijl` gebruikt Inter, terwijl `vormgever-npuls-huisstijl` zegt "nooit Inter". We volgen de vormgever (Plus Jakarta Sans). Dat is een inconsistentie in de CEDA-collectie om te melden.
- **Beperking:** Cooper Light is een projectasset en wordt niet geladen; de intro valt terug op Georgia. Op deze computer werd 'Cooper Light' vervangen door een veel zwaardere letter, dus we noemen hem niet meer in de lettertypestack.
- **Eigen aandachtspunt:** de uploadknop en de bestandsgrootte-tekst van Streamlit blijven Engels ("Upload", "200MB per file").

## Demodata v2 en grote bestanden (2026-10-08)

- `data/demodata_1cho.csv` is vervangen door een versie met 7 sectoren en 28 opleidingen (6322 studenten, 21.220 rijen, 5,5 MB), gevalideerd tegen `variable_metadata.json` en `Croho.asc` van 1cijferho: 51 van 51 controles, de oude data haalde er 34. Details, generator en antwoordsleutel staan in `workshop-dair-begeleider/docs/demodata-v2.md`.
- Voor de presentatie: de validatie vond echte fouten in onze eigen demodata (opleidingscodes die niet bij CROHO pasten, "Nederlandse student" als EER-waarde). Goed voorbeeld dat je een agent zijn eigen werk moet laten controleren tegen een bron.
- Een echt 1CHO-bestand is veel groter dan de demodata. Gemeten met een testbestand van 227 MB: alles lezen 28 s en 459 MB; alleen de nodige kolommen lezen 2 s en 27 MB. De skill `bouwen_dashboard` vraagt de deelnemer nu naar de grootte van het echte bestand en bouwt daarop.

## Skills generiek gemaakt (2026-10-08)

Doel: de drie skills (`verkennen_data`, `schets_dashboard`, `bouwen_dashboard`) moeten ook thuis bruikbaar zijn, op andere data dan de workshop.

- De skills bevatten geen domeinkennis meer. Kolommen, definities, drempels en wat een kolom betekent komen van de gebruiker (metainfo). De 1CHO-informatie staat nu in `data/metadata_1cho.md`, buiten de skills. Dat bestand is alleen lokaal en wordt niet gepusht (staat in `.gitignore`).
- Datagebruik is een gesprek met drie keuzes (demo/openbaar, eigen data die gedeeld mag worden, gevoelig: Claude leest dan alleen kolomnamen en de gebruiker draait `verken.py` zelf). In de workshop is de standaard demodata.
- `verkennen_data` levert nu `assets/verken.py` mee: getest op 1CHO, op echte data (geen label en geen waarden in het profiel) en op een gewone CSV met komma's.
- De Npuls-stijl is de standaard (zie *Huisstijl: Npuls als standaard* hieronder). Een andere stijl kiezen kan later.
- Voor de presentatie: de skills zijn zo gebouwd dat ze door een ander team kunnen worden hergebruikt. Dat is een sterk punt om te laten zien.

## Huisstijl: Npuls als standaard (2026-10-12)

- `bouwen_dashboard` gebruikt de Npuls-huisstijl en roept daarvoor de skill `vormgever-npuls-huisstijl` aan. Dat is een bewuste keuze voor nu, omdat de workshop van CEDA en Npuls is.
- **Later aan te passen:** wie een andere stijl wil, kan dat zeggen. Dan volgt de skill een eigen stijl (kleuren, lettertype, logo) of een rustig standaardthema. Willen we dat als vaste keuze in de workshop, dan is dat een aanpassing in de sectie *Huisstijl* van `bouwen_dashboard`.
- Het officiële logo komt uit `clidev-presentaties/public/npuls/npuls_logo.jpg`. Het is een JPG met roze achtergrond, dus het hoort op npuls-roze (de hero). Er is geen vector of transparante versie. Dit logo staat op één plek: `vormgever-npuls-huisstijl/assets/logos/` (PR cedanl/.github#100 zet het ook in de centrale skill). `bouwen_dashboard` kopieert het naar `dashboard/npuls/`.
- De gekleurde ringen en de pulse-curve worden niet meer gebruikt als decoratie: het logo is het enige beeld in de hero.
- De dashboardcode staat in `dashboard/` (niet in `uitvoer/`, dat staat in `.gitignore`).
