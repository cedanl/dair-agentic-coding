# Datawoordenboek demodata_1cho.csv

Fictieve studentgegevens in de opzet van 1CijferHO 2025 (v1.0). 1CijferHO (één cijfer hoger onderwijs) is het bestand van DUO met de inschrijvingen en diploma's van alle studenten in het hoger onderwijs; instellingen krijgen elk jaar het deel over hun eigen studenten. De omschrijvingen komen uit `Bestandsbeschrijving_1cyferho_2025_v1.0.txt`; de waarden en eigenaardigheden zijn gecontroleerd in dit bestand.

- Formaat: CSV, scheidingsteken `;`, 21.220 rijen, 22 kolommen.
- Eén rij per student per inschrijvingsjaar (6.322 studenten, inschrijvingsjaren 2012 t/m 2023, geen dubbele student-jaar-combinaties).
- Waarden zijn al gedecodeerd naar labels (bijvoorbeeld `man`, `voltijd`); in het originele 1CijferHO-bestand staan codes (`M`, `1`).
- Lees `leeftijd_per_peildatum_1_oktober`, `postcodecijfers_*` en `opleiding_actueel_equivalent` als tekst, anders verdwijnen de voorloopnullen.

## Kolommen

| Kolom | Omschrijving | Type | Waarden in de demo | Opmerking | Bronveld 1CijferHO |
|---|---|---|---|---|---|
| `persoonsgebonden_nummer` | Nummer waarmee een student uniek te onderscheiden is. | tekst (9 cijfers) | 6.322 unieke waarden | Sleutel samen met `inschrijvingsjaar`. | Persoonsgebonden nummer |
| `inschrijvingsjaar` | Kalenderjaar waarin het studiejaar begint. 2023 is dus studiejaar 2023/2024. | geheel getal | 2012 t/m 2023 | Aantal rijen groeit van 520 (2012) naar circa 2.100 per jaar vanaf 2016. | Inschrijvingsjaar |
| `verblijfsjaar_actuele_instelling` | Hoeveelste jaar de student actief ingeschreven is bij de actuele instelling. | geheel getal | 1 t/m 7 | Elke student heeft precies één rij met waarde 1. Origineel: 00 bij neveninschrijving, komt in de demo niet voor. | Verblijfsjaar actuele instelling |
| `verblijfsjaar_actuele_opleiding_instelling` | Hoeveelste jaar de student actief ingeschreven is in dezelfde opleiding bij de actuele instelling. | geheel getal | 1 t/m 6 | Waarde 1 komt vaker voor (6.810) dan er studenten zijn (6.322): wie van opleiding wisselt begint weer bij 1. | Verblijfsjaar actuele opleiding-instelling |
| `diplomajaar` | Jaar waarin het diploma is behaald. Een diplomajaar T loopt van oktober T t/m september T+1. | geheel getal | 2015 t/m 2023 | **Leeg = geen diploma** (18.087 rijen). Origineel: `0000`. Gevuld precies als `soort_diploma_instelling` gevuld is (3.133 rijen). | Diplomajaar |
| `soort_hoger_onderwijs` | Soort hoger onderwijs van de inschrijving. | categorie | `hoger beroepsonderwijs` | Constant: alleen hbo. Origineel: `hbo`. | Soort hoger onderwijs |
| `soort_inschrijving_actuele_instelling` | Of de rij de hoofdinschrijving is binnen de actuele instelling. | categorie | `hoofdinschrijving binnen het domein actuele instelling` | Constant: alleen hoofdinschrijvingen, daarom één rij per student per jaar. Origineel: `1`. | Soort inschrijving actuele instelling |
| `geslacht` | Geslacht van de student. | categorie | `man` (9.599), `vrouw` (11.621) | Origineel ook `O` (onbekend), komt in de demo niet voor. | Geslacht |
| `opleidingsvorm` | Studievorm van de inschrijving. | categorie | `voltijd` | Constant: alleen voltijd. Origineel: `1`. | Opleidingsvorm |
| `indicatie_internationale_student` | Of de student volgens de afgesproken definitie als internationale student telt, op basis van de actuele eerste nationaliteit. | categorie | `geen internationale student` (19.823), `internationale student` (1.397) | Niet hetzelfde als `indicatie_eer_actueel`: 1.397 internationale studenten tegenover 531 niet-EER-rijen. Origineel: `J`/`N`. | Indicatie internationale student |
| `indicatie_eer_actueel` | Of een van de actuele nationaliteiten tot de EER behoort (lijst per 1 oktober 2025, aangevuld met Zwitserland en Suriname). | categorie | `EER-student` (20.689), `niet-EER-student` (531) | EER is inclusief Nederland. Origineel: `J`/`N`. | Indicatie EER actueel |
| `croho_onderdeel_actuele_opleiding` | CROHO-onderdeel (sector) van de actuele opleiding. | categorie | `economie`, `techniek`, `gezondheidszorg`, `gedrag en maatschappij`, `onderwijs`, `taal en cultuur`, `landbouw en natuurlijke omgeving` | 7 van de 11 mogelijke waarden. `natuur`, `recht` en `sectoroverstijgend` komen niet voor. | Croho-onderdeel actuele opleiding |
| `soort_diploma_instelling` | Soort diploma binnen de actuele instelling (hoofd- of nevendiploma, propedeuse, bachelor, master). | categorie | `Hoofd-bachelor-diploma binnen de actuele instelling` | **Leeg = geen diploma.** Alleen deze ene waarde in de demo. Origineel: `03`. | Soort diploma instelling |
| `opleiding_actueel_equivalent` | Opleidingscode (ISAT) van de actuele variant van de opleiding. | tekst (5 cijfers) | 28 codes | Hoort 1-op-1 bij `opleidingscode_naam_opleiding`. | Opleiding actueel equivalent |
| `type_hoger_onderwijs_binnen_soort_hoger_onderwijs` | Type opleiding binnen het soort hoger onderwijs. | categorie | `bachelor` | Constant: alleen bachelor. Origineel: `ba`. | Type hoger onderwijs binnen soort hoger onderwijs |
| `leeftijd_per_peildatum_1_oktober` | Leeftijd van de student aan het begin van het inschrijvingsjaar. | tekst (3 cijfers) | `017` t/m `028` | Voorloopnullen. Volgens de bestandsbeschrijving is de peildatum feitelijk 30 september. | Leeftijd per peildatum 1 oktober |
| `postcodecijfers_student_op_1_oktober` | Eerste vier cijfers van de postcode van het woonadres op 1 oktober. | tekst (4 cijfers) | 96 waarden | `0010` = België, `0020` = Duitsland, `0030` = elders in het buitenland; anders een Nederlandse postcode (1000 t/m 9999). Origineel leeg = onbekend en `0040` = geen vaste woonplaats, komen niet voor. | Postcodecijfers student op 1 oktober |
| `postcodecijfers_van_de_hoogste_vooropl_voor_het_ho` | Postcodecijfers van het woonadres op 1 oktober van het diplomajaar van de hoogste vooropleiding vóór het HO. | tekst (4 cijfers) | 96 waarden | Zelfde codering als hierboven. Alleen gevuld voor diplomajaren vanaf 2003. | Postcodecijfers van de hoogste vooropl. vóór het HO |
| `opleidingscode_naam_opleiding` | Naam van de opleiding bij `opleiding_actueel_equivalent`. | tekst | 28 namen, bijvoorbeeld `B Werktuigbouwkunde` | Prefix `B` = bachelor. Gedecodeerd uit `Dec_isat.asc`. | Opleidingscode (decodering Dec_isat) |
| `vestigingsnummer_gemeentenaam_volgens_rio` | Vestigingsplaats van de opleiding, als gemeentenaam volgens RIO. | categorie | `Den Bosch` (7.574), `Tilburg` (7.370), `Breda` (6.276) | In 1CijferHO staat een tweecijferig vestigingsnummer; hier is dat vertaald naar een gemeentenaam. | Vestigingsnummer (actueel) |
| `hoogste_vooropleiding_voor_het_ho_omschrijving_vooropleiding` | Hoogste vooropleiding die vóór het hoger onderwijs is behaald, als omschrijving. | categorie | 15 waarden, bijvoorbeeld `havo profiel economie & maatschappij`, `mbo zorg en welzijn niveau 4`, `vooropleiding onbekend` (668) | Gedecodeerd uit `Dec_vopl.asc`. Vwo/havo staan per profiel apart; mbo per sector op niveau 4. | Hoogste vooropleiding vóór het HO |
| `eerste_jaar_in_het_hoger_onderwijs` | Eerste inschrijvingsjaar van de student in het hoger onderwijs. | geheel getal | 2010 t/m 2023 | Nooit later dan `inschrijvingsjaar`. Kan eerder liggen dan het eerste jaar in dit bestand (2010 en 2011: studenten die elders begonnen). Is niet gelijk aan het eerstejaarsjaar. | Eerste jaar in het hoger onderwijs |

## Voorbeeldvragen

De workshopskills bieden drie vragen aan. De uitwerking (definities, uitsplitsingen, filters, teksten) staat in `demodata_1cho.casus.json`; de berekening zit in `.claude/skills/bouwen_dashboard/assets/maak_dashboard.py`. Ze zijn zo gekozen dat de demodata een zichtbaar verschil laat zien. Wat de demodata erop antwoordt, zegt niets over de werkelijkheid: de data is bruikbaar om code mee te bouwen, niet betrouwbaar als uitkomst.

| | Vraag | Uitsplitsing (aanbevolen) | Andere uitsplitsingen |
|---|---|---|---|
| A | Welk deel van de eerstejaars stopt na het eerste jaar? | sector | opleiding, geslacht |
| B | Welk deel van de eerstejaars haalt binnen vijf jaar een diploma? | opleiding | vooropleiding, sector |
| C | Stoppen eerstejaars vaker na het eerste jaar bij de ene vooropleiding dan bij de andere? | vooropleiding | sector, geslacht |

- **Eerstejaars**: de rij van een student met `verblijfsjaar_actuele_instelling` = 1 (elke student heeft er precies één). Het instroomjaar en de groep komen uit die rij. Er wordt in studenten geteld, niet in rijen.
- **Stopt na het eerste jaar**: geen rij in instroomjaar + 1. Telt alleen voor instroomjaren waarvan het jaar erna in de data zit.
- **Diploma binnen vijf jaar**: `diplomajaar` − instroomjaar ≤ 4. Telt alleen voor instroomjaren waarvan alle vijf jaren in de data zitten.
- **Privacy**: groepen onder 30 studenten niet tonen, een percentage met minder dan 5 studenten in de teller of de rest ook niet, en secundaire onderdrukking.

## Let op bij gebruik

- **Lege diplomavelden zijn geen ontbrekende data**: ze betekenen dat in die rij geen diploma is behaald. Alleen `diplomajaar` en `soort_diploma_instelling` hebben lege waarden (18.087 rijen).
- **Constante kolommen**: `soort_hoger_onderwijs`, `soort_inschrijving_actuele_instelling`, `opleidingsvorm` en `type_hoger_onderwijs_binnen_soort_hoger_onderwijs` hebben één waarde en dragen niets bij aan een analyse of filter.
- **Internationaal is niet hetzelfde als niet-EER**: een internationale student kan een EER-nationaliteit hebben.
- **Voorloopnullen**: lees leeftijd, postcodecijfers en opleidingscode als tekst.
- **Verblijfsjaar is geen leeftijd van de opleiding**: wie van opleiding wisselt, krijgt bij `verblijfsjaar_actuele_opleiding_instelling` opnieuw 1, bij `verblijfsjaar_actuele_instelling` niet.
- **Trendbreuk nationaliteit**: voor 1CijferHO 2025 zijn nationaliteiten en geboortelanden opnieuw bepaald, dat kan een trendbreuk geven in `indicatie_internationale_student` en `indicatie_eer_actueel`.
- **Weggelaten uit 1CijferHO**: migratieachtergrond en generatie zijn op besluit van OCW niet meer opgenomen.
