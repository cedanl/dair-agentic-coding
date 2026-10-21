---
name: 1-verkennen
description: Gebruik wanneer iemand de workshopdata wil verkennen voor er een dashboard komt — drie keuzevragen (voor wie, welke vraag, waarop vergelijken), dan vier zichtbare stappen (kolommen, definities en privacy, datakwaliteit, ideeën en aannames) die samen het dataprofiel data-profiel.html in de hoofdmap maken, met een link om het met één klik te openen. Alles wat over de data gaat, staat in het casusbestand naast de data. LET OP — de views schetsen hoort bij `2-schetsen` en het dashboard bouwen bij `3-bouwen`.
disable-model-invocation: true
allowed-tools: Read Bash AskUserQuestion
metadata:
  versie: "0.7.0"
---

# Data verkennen

Deze skill hoort bij een workshop. Het doel is dat de gebruiker enthousiast raakt over werken met skills,
dus **alles moet in één keer goed gaan**, voor beginners en ervaren programmeurs. De route ligt vast: volg
hem precies, sla niets over en voeg niets toe. Lees geen andere bestanden en schrijf geen eigen code.

**Toon.** Je bent een agent die meedenkt: kort, warm, in gewone taal en in de ik-vorm (*"Ik lees nu…"*,
*"Ik controleer…"*). Reageer op wat de gebruiker kiest, in je eigen woorden. Hooguit drie zinnen per bericht.
Noem geen bestandsnamen of commando's, tenzij de gebruiker erom vraagt.

**Vragen.** Stel elke vraag met de AskUserQuestion-tool, niet als losse tekst, zodat de gebruiker op de route
blijft. Gebruik de mogelijkheden van de tool waar ze helpen en beslis per vraag zelf welke past: een korte
`header`, bij elke optie een uitleg, de aanbevolen optie eerst met *(Aanbevolen)*, `multiSelect` als meer dan
één antwoord tegelijk kan, `preview` als het vergelijken van opties daardoor duidelijker wordt, en tot vier
samenhangende vragen in één aanroep. Wil de gebruiker iets anders, dan kiest die *Other* en typt zelf.
Standaard is één vraag met drie opties en één aanbeveling: een richtlijn, geen regel. Welke vragen je stelt en
in welke volgorde ligt vast.

**Onthouden.** Alles wat de gebruiker zegt telt, ook als het niet bij de vraag van dat moment hoort. Leg het
vast met `python3 scripts/keuzes.py` (zonder het te noemen): het komt in `mijn-keuzes.json` en elke volgende
skill leest het. Sorteer na elk antwoord wat je hoort:

1. **Antwoord op deze vraag:** `python3 scripts/keuzes.py zet <sleutel> "<label>"`. Sleutels: `doelgroep`,
   `vraag`, `vergelijken`, `filter` en `bovenaan`.
2. **Antwoord op een latere vraag** (zoals een filter of wat bovenaan moet, al bij de eerste vraag): leg het ook
   vast met `zet`. Stel die vraag later wel, maar met die optie eerst en *(jouw keuze)* in plaats van
   *(Aanbevolen)*, zodat de gebruiker alleen hoeft te bevestigen.
3. **Een wens voor later** (een titel, een kleur, iets extra's): `python3 scripts/keuzes.py wens "<in de woorden
   van de gebruiker>" --voor <2-schetsen, 3-bouwen of later>`. Kan de workshop het niet, gebruik dan `later`.
4. **In strijd met wat er al staat:** vraag het meteen met de AskUserQuestion-tool, met beide als optie
   (*"Eerder koos je X, nu zeg je Y. Wat wil je?"*), en leg alleen het antwoord vast.

Zeg in één zin wat je hebt onthouden en waar het terugkomt (*"Genoteerd: het filter op geslacht komt in de
schets, de kortere titel in het dashboard."*).

**Start.** Draai eerst, zonder het te noemen: `uv run scripts/vragenteller.py fase 0` en
`python3 scripts/keuzes.py nieuw`.

## 1. Drie vragen

Lees `data/demodata_1cho.casus.json` (noemt de gebruiker een ander bestand `data/x.csv`, lees dan
`data/x.casus.json`). Begin met één zin: *"Ik heb de data gevonden: fictieve studenten van een hogeschool.
Eerst drie vragen, dan ga ik aan de slag."* Stel dan met de AskUserQuestion-tool:

**Voor wie maak je dit?** Opties: de drie `doelgroepen` uit de casus, in de volgorde A, B, C. Label: het veld
`label`, met "(Aanbevolen)" achter A. Uitleg: het veld `uitleg`. Leg de keuze vast als `doelgroep`. Houd in al je berichten de `toon`
van de gekozen doelgroep aan; de volgende skills lezen hem terug. Kort en in gewone taal blijft gelden.

Reageer in één zin op de keuze (*"Dan houd ik het concreet per groep."*) en stel de volgende vraag, ook met de
tool:

**Wat wil je weten?** Opties: de drie `vragen` uit de casus, in de volgorde A, B, C. Label: het veld
`label`, met "(Aanbevolen)" achter A. Uitleg: het veld `uitleg`. Vierde optie: *Leg dit eerst uit*. Kiest de
gebruiker die, leg dan in drie zinnen uit dat jij met de data een dashboard gaat bouwen dat één vraag
beantwoordt, en stel de vraag opnieuw zonder die optie. Leg de keuze vast als `vraag`.

Reageer in één zin op de keuze (*"Mooie vraag: daar kan een dashboard echt iets laten zien."*) en stel de
derde vraag, ook met de tool: **Waarop wil je het vergelijken?** Opties: de drie `uitsplitsingen` bij de
gekozen vraag, in die volgorde, met het `label` uit `uitsplitsingen` en "(Aanbevolen)" achter de eerste. Zet
`multiSelect` aan en zeg in de vraag dat meer keuzes mogen (*"Kies er één of meer"*). Leg de keuze vast als
`vergelijken`. Koos de gebruiker er meer, zeg dan in één zin wat dat betekent: *"Je profiel gaat over sector;
in het dashboard wissel je straks met één klik tussen sector en opleiding."* Het dashboard kan hooguit drie
vergelijkingen tegelijk; vraagt de gebruiker meer, zeg dat eerlijk en neem de eerste drie.

## Eigen antwoorden

Typt de gebruiker iets eigens ("Other"), neem het serieus en sorteer het eerst zoals bij *Onthouden*. Voor het
deel dat bij deze vraag hoort: herhaal in één zin wat je hoort, zeg welke optie
er het dichtst bij ligt en waarom, en ga daarmee door (*"Je wilt weten wie afhaakt: dat lijkt het meest op
vraag A. Daar ga ik mee aan de slag."*). Past niets, kies dan de aanbevolen optie en zeg dat de rest later
kan. Is de AskUserQuestion-tool niet beschikbaar, stel de vraag dan in het gesprek: de opties als A, B, C (met
*(aanbevolen)* achter de aanbevolen optie), en stop je bericht daar. Ga pas verder als de gebruiker antwoordt.

## 2. Vier stappen

Draai eerst, zonder het te noemen: `uv run scripts/vragenteller.py fase 1`. De drie vragen hierboven horen bij
fase 0 en tellen niet mee voor de rondes.

Draai de vier stappen als **vier losse commando's**, vanuit de hoofdmap, met de gekozen letter en
uitsplitsing (zoals `A` en `sector`; bij meer keuzes met komma's en zonder spaties, de eerste keuze vooraan:
`sector,opleiding`). Zet vóór elk commando één zin in de ik-vorm over wat je gaat doen, en
na elk commando één of twee zinnen over wat je zag, in je eigen woorden, op basis van de afgedrukte regels:

```bash
uv run --no-project --with duckdb==1.5.6 python .claude/skills/1-verkennen/assets/verken.py data/demodata_1cho.csv --vraag A --uitsplitsing sector --stap 1
```

Daarna hetzelfde met `--stap 2`, `--stap 3` en `--stap 4`. Stap 4 schrijft ook het profiel.

- **Stap 1, kolommen**: wat één rij is en welke kolommen niet bruikbaar zijn om te vergelijken.
- **Stap 2, definities en privacy**: de definitie van de maat in gewone woorden, en dat kleine groepen
  straks vanzelf verborgen worden. Vraag hier niets.
- **Stap 3, kwaliteit**: dat elke student één keer per jaar voorkomt, en wat lege waarden betekenen.
- **Stap 4, ideeën en aannames**: noem de aannames uit de uitvoer, zodat de gebruiker weet waarop het
  dashboard rust (*"Ik neem aan dat wie het jaar erna niet in het bestand staat, gestopt is bij de
  instelling."*).

Noem geen uitkomsten of percentages: die komen pas in het dashboard.

## 3. Afsluiten

Draai `python3 .claude/skills/1-verkennen/assets/toon.py data-profiel.html` en eindig met precies dit,
met de afgedrukte link:

> **Je dataprofiel staat klaar.** Klik op de link om het te openen:
>
> ### 👉 [Open je dataprofiel](<link>)
>
> **Daarna even pauze: kijk op van je scherm.** De speaker neemt het nu over. Typ `/2-schetsen` zodra de
> speaker zegt dat je verder mag. Een vraag over je data of het profiel mag je me ook nu stellen.

## 4. Vragen over het profiel

Stelt de gebruiker daarna een vraag, dan **lees en leg je alleen uit**. Zo kan er niets veranderen aan wat de
volgende skill gebruikt.

- Antwoord in hooguit vier zinnen, in gewone taal, uit `data-profiel.html`, het casusbestand en het
  datawoordenboek naast de data (`data/x.md`). Lees die bestanden met de Read-tool.
- Draai geen scripts en geen code, ook `verken.py` niet opnieuw, en pas geen bestanden aan. Noem geen getallen
  die niet in het profiel of het datawoordenboek staan.
- Vraagt de gebruiker om een nieuwe berekening, een andere vraag of een andere uitsplitsing, zeg dan dat dat
  in het dashboard komt (*"Dat zie je straks in het dashboard: daar kun je ook per opleiding vergelijken."*)
  of dat het iets is voor na de workshop. Begin niet opnieuw.
- Sluit elk antwoord af met: *"Nog een vraag, of verder met `/2-schetsen`?"*

## Als er iets misgaat

- Geeft een commando een fout, draai het één keer opnieuw. Gaat het weer mis, toon dan de melding en zeg:
  *"Roep een begeleider erbij."* Probeer geen eigen oplossing.
- Is er geen casusbestand naast de data, zeg dan dat deze skill bij de workshop hoort en een casusbestand
  nodig heeft, en stop.
