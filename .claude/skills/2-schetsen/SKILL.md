---
name: 2-schetsen
description: Gebruik wanneer iemand na het dataprofiel (data-profiel.html) het dashboard wil schetsen — één vraagronde (filter en volgorde), dan maakt één script schets.html in de hoofdmap: het dashboard in grijs, met de echte groepen en jaren maar zonder getallen, en krijgt de gebruiker een link om het met één klik te openen. Daarna past de gebruiker de schets aan (vergelijkingen, filters, wat bovenaan staat, titel) tot hij goed is: het dashboard volgt de schets. LET OP — de data verkennen hoort bij `1-verkennen` en het dashboard bouwen bij `3-bouwen`.
disable-model-invocation: true
allowed-tools: Read Bash AskUserQuestion
metadata:
  versie: "0.5.0"
---

# Dashboard schetsen

Deze skill hoort bij een workshop. Het doel is dat de gebruiker enthousiast raakt over werken met skills,
dus **alles moet in één keer goed gaan**. De route ligt vast: volg hem precies. Lees geen andere bestanden en
schrijf geen eigen code.

**Toon.** Je bent een agent die meedenkt: kort, warm, in gewone taal en in de ik-vorm. Reageer op wat de
gebruiker kiest, in je eigen woorden. Hooguit drie zinnen per bericht. Noem geen bestandsnamen of commando's,
tenzij de gebruiker erom vraagt.

**Stap voor stap.** Veel deelnemers werken voor het eerst met een AI-agent. Wees helder en zonder vakjargon, en
behandel de gebruiker als een collega die de inhoud kent maar de werkwijze nog niet. Zeg steeds drie dingen: wat je nu gaat doen, waarom, en wat er daarna komt (*"Ik maak nu
een schets van je dashboard. Dat doe ik eerst, zodat je kunt zien of het klopt voordat ik ga rekenen. Daarna
mag jij zeggen wat je anders wilt."*). Leg een woord als *filter* of *vergelijken* de eerste keer in een paar
woorden uit. Zeg erbij waar je klikt of wat je typt.

**Bevestigen.** Ga nooit stil verder. Zeg na **elk** antwoord in één zin wat je ermee doet, vóór je de volgende
vraag stelt of iets draait. Dat geldt vooral als het antwoord niet precies één optie is: meer opties tegelijk,
"alles", "weet ik niet", "?", een eigen tekst of iets wat de workshop niet kan. Zeg dan welke keuze je maakt en
waarom (*"Je koos alle drie: ik maak het voor de studieadviseur, want één doelgroep houdt het dashboard
helder."*), en wat niet kan (*"Een kaart kan het dashboard niet maken; ik noteer het als idee voor later."*).
Kiest de gebruiker *Leg dit eerst uit*, leg dan eerst uit en stel pas daarna de vraag opnieuw.
Stel je direct daarna een nieuwe vraag met de tool, zet de bevestiging dan **ook vooraan in de vraagtekst**, zodat
hij nooit wegvalt: *"Je koos alle drie; ik neem de studieadviseur. Wat wil je weten?"*

**Vragen.** Stel elke vraag met de AskUserQuestion-tool, niet als losse tekst, zodat de gebruiker op de route
blijft. Gebruik de mogelijkheden van de tool waar ze helpen en beslis per vraag zelf welke past: een korte
`header`, bij elke optie een uitleg, de aanbevolen optie eerst met *(Aanbevolen)*, `multiSelect` als meer dan
één antwoord tegelijk kan, `preview` als het vergelijken van opties daardoor duidelijker wordt. Stel **één vraag per
aanroep**: meer vragen in één aanroep worden tabbladen die deelnemers niet zien. Mag de gebruiker meer kiezen
(`multiSelect`), zet dan in de vraag zelf hoe je verder gaat: *"Kies er één of meer en klik dan op Submit."*
Wil de gebruiker iets anders, dan kiest die *Other* en typt zelf.
Standaard is één vraag met drie opties en één aanbeveling: een richtlijn, geen regel. Welke vragen je stelt en
in welke volgorde ligt vast.

**Onthouden.** Alles wat de gebruiker zegt telt, ook als het niet bij de vraag van dat moment hoort. Leg het
vast met `python3 scripts/keuzes.py` (zonder het te noemen): het komt in `mijn-keuzes.json` en elke volgende
skill leest het. Sorteer na elk antwoord wat je hoort:

1. **Antwoord op deze vraag:** `python3 scripts/keuzes.py zet <sleutel> "<label>"`. Sleutels: `doelgroep`,
   `vraag`, `vergelijken`, `filter`, `bovenaan` en `titel`; een label of een code mag allebei. `mijn-keuzes.json`
   is de waarheid: het profiel, de schets en het dashboard lezen hun keuzes daar en schrijven terug wat ze
   echt deden. Lees na het draaien van een script dus opnieuw met `keuzes.py toon` wat er nu staat.
2. **Antwoord op een latere vraag** (zoals een filter of wat bovenaan moet, al bij de eerste vraag): leg het ook
   vast met `zet`. Stel die vraag later wel, maar met die optie eerst en *(jouw keuze)* in plaats van
   *(Aanbevolen)*, zodat de gebruiker alleen hoeft te bevestigen.
3. **Een wens voor later** (een titel, een kleur, iets extra's): `python3 scripts/keuzes.py wens "<in de woorden
   van de gebruiker>" --voor <2-schetsen, 3-bouwen of later>`. Kan de workshop het niet, gebruik dan `later`.
4. **In strijd met wat er al staat:** vraag het meteen met de AskUserQuestion-tool, met beide als optie
   (*"Eerder koos je X, nu zeg je Y. Wat wil je?"*), en leg alleen het antwoord vast.

Zeg na elke keer vastleggen, ook als de gebruiker in één bericht zijn hele verhaal vertelt, in één zin wat je hebt
onthouden en waar het terugkomt (*"Genoteerd: het filter op geslacht komt in de schets, de kortere titel in
het dashboard."*). Zeg nooit dat je iets hebt genoteerd zonder het met `keuzes.py` vast te leggen, en zet een
wens pas op klaar als hij echt in de schets of het dashboard zit.

**Eerder gezegd.** Draai bij de start `python3 scripts/keuzes.py toon` en lees wat er al staat. Houd de `toon`
van de gekozen doelgroep uit de casus aan. Staan er een filter, wat bovenaan moet of open wensen voor
`2-schetsen`, neem ze mee volgens punt 2 hierboven, zeg in één zin dat je ze meeneemt (*"Je noemde al een
filter op geslacht: dat zet ik als eerste."*) en zet een verwerkte wens op klaar met `python3 scripts/keuzes.py
wens-klaar <nummer>`.

Staat `data-profiel.html` niet in de hoofdmap, zeg dan: *"Typ eerst `/1-verkennen`."* en stop.

**Start.** Draai daarna, zonder het te noemen: `uv run scripts/vragenteller.py fase 2`.

**Is er al een schets?** Staat `schets.html` al in de hoofdmap (de gebruiker komt terug, bijvoorbeeld vanuit
`/3-bouwen`), stel dan de vragen uit *Eén vraagronde* **niet** opnieuw. Zeg: *"Je schets van net staat er
nog, met je keuzes en je titel. Ik zet hem opnieuw klaar."* Draai `uv run --no-project --with polars==1.44.2 python
.claude/skills/2-schetsen/assets/maak_schets.py` zonder extra's (hij tekent precies wat in `mijn-keuzes.json`
staat), pas daarna de open wensen voor `2-schetsen` één voor één toe met de vaste aanpassingen uit *Schets
aanpassen*, en ga verder bij *Laten zien*.

## 1. Eén vraagronde

Lees de keuzes met `python3 scripts/keuzes.py toon` (de vraag en de vergelijkingen) en de `filters` en
`uitsplitsingen` uit het casusbestand naast de data. Zeg in één zin wat je
meeneemt (*"Je wilt weten welk deel van de eerstejaars stopt, per sector. Ik zet twee grafieken op papier."*)
en stel dan twee vragen met de AskUserQuestion-tool, **elk in een eigen aanroep**: eerst de
eerste, en pas na het antwoord de tweede.

1. **Waarop wil je kunnen filteren?** Opties: de eerste vier `filters` uit de casus die geen gekozen vergelijking
   zijn, in die volgorde, met hun `label` en "(Aanbevolen)" achter de eerste (meestal instroomjaar). Elke andere
   kolom uit `uitsplitsingen` mag ook een filter zijn, zolang je er niet al op vergelijkt: noemt de gebruiker die
   via *Other*, gebruik hem dan gewoon. Zeg er bij veel waarden bij dat het keuzemenu lang wordt. Zet
   `multiSelect` aan: hooguit twee filters samen. Zet in de vraag: *"Kies er één of twee en klik dan op Submit.
   Geen filter of een ander filter? Typ het bij Other."* Kiest de gebruiker meer dan twee, vraag dan in één zin
   welke twee. Het filter op instroomjaar geldt voor de kerncijfers en de groepen; de lijn over de jaren laat
   altijd alle jaren zien.
2. **Wat wil je bovenaan zien?** Opties: *De vergelijking tussen groepen* (aanbevolen) en *De ontwikkeling over
   de jaren*.

Het schetsscript hieronder legt de antwoorden zelf vast in `mijn-keuzes.json`.

Typt de gebruiker iets eigens, herhaal dan in één zin wat je hoort en kies de optie die er het dichtst bij
ligt (*"Je wilt per stad kunnen kijken: dat is het filter op vestiging."*). Past geen optie, zoals een ander
soort grafiek (sankey, kaart) of een filter dat er niet bij staat, kies dan de **aanbevolen** optie en zeg in
twee zinnen dat het een mooi idee is voor na de workshop, als het script wordt uitgebreid. Verwijs niet naar
een begeleider. Is de AskUserQuestion-tool niet beschikbaar, stel de vraag dan in het gesprek: de opties als A, B, C (met
*(aanbevolen)* achter de aanbevolen optie), en stop je bericht daar. Ga pas verder als de gebruiker antwoordt.

**Past het bij de vraag?** Kijk vóór je de schets maakt of de keuzes de vraag beantwoorden. Gaat de vraag over
één ding (de `kern` in de casus) en staat dat niet vooraan, zeg dan dat het script het erbij zet en waarom.

## 2. Schets maken

Zeg in één zin wat je doet (*"Ik schets nu de twee grafieken, nog zonder getallen: eerst kijken of de opzet
klopt, dan pas bouwen."*). Draai dan, vanuit de hoofdmap, met de gekozen filters (bijvoorbeeld `instroomjaar`, twee als `instroomjaar,vestiging`, of `geen`) en volgorde (`groep` of
`jaar`):

```bash
uv run --no-project --with polars==1.44.2 python .claude/skills/2-schetsen/assets/maak_schets.py --filter instroomjaar --volgorde groep
python3 .claude/skills/1-verkennen/assets/toon.py schets.html
```

## 3. Laten zien

Geef de schets meteen, met de twee views, de titel en het filter uit de uitvoer van het eerste commando en de
link uit het tweede:

> **Je schets staat klaar.** Klik op de link om hem te openen:
>
> ### 👉 [Open je schets](<link>)
>
> Bovenaan komt *<view 1>*, daaronder *<view 2>*, met een filter op <filter>. <Alleen bij meer
> vergelijkingen: "In het dashboard wissel je met één klik tussen <vergelijkingen>."> Het ziet eruit als je dashboard, met de echte groepen en jaren, alleen nog zonder getallen: die
> komen pas in het dashboard.

## 4. Schets aanpassen

**Eerst de link, dan de vraag.** Stel de vraag hieronder pas als de gebruiker de schets heeft kunnen zien: de
regel `### 👉 [Open je schets](<link>)` uit *Laten zien* (na een aanpassing met de nieuwe link) staat altijd
letterlijk in je bericht vlak boven de vraag. Zonder die regel geen vraag. Zet de link **nooit** in de vraagtekst:
daar is hij niet aan te klikken. De vraagtekst verwijst naar boven: *"Bekijk je schets via de link hierboven. Wil
je iets veranderen?"*

Dit is hét moment om te veranderen: het dashboard wordt straks precies zoals deze schets. Vraag met de
AskUserQuestion-tool: **Wil je iets veranderen aan de schets?** Opties, in deze volgorde: *De schets is goed
(Aanbevolen)*; open wensen voor `2-schetsen` of `3-bouwen` die over de opzet of de titel gaan, met *(jouw wens)*;
dan de eerste twee regels uit de **laatste** uitvoer na *Aanpassen* (het deel vóór `=>` **letterlijk** als label,
ook wat tussen haakjes staat, zonder "(Aanbevolen)"). Een eigen wens typt de gebruiker via *Other*.

- **Een vaste aanpassing:** zeg in één zin wat je verandert, draai `uv run --no-project --with polars==1.44.2 python
  .claude/skills/2-schetsen/assets/maak_schets.py` met het deel na `=>` erachter, en daarna
  opnieuw `toon.py schets.html`. Het script past de schets én `mijn-keuzes.json` aan.
- **Een andere titel:** draai `maak_schets.py --titel "<titel>"` (met `--titel standaard`
  komt de vraag terug als titel). De titel blijft ook in het dashboard staan.
- **Een andere wens:** kies de vaste aanpassing die er het dichtst bij ligt en zeg welke. Kan de schets het niet
  (een ander soort grafiek, een kaart, een voorspelling), zeg dat in twee zinnen en noteer het als wens voor
  `later`.

Na elke aanpassing: *"Gedaan: …"* in één zin, **alleen over wat de uitvoer van het script laat zien** (staat er een
regel *Let op*, zeg dan eerlijk wat er niet is gelukt en waarom), de regel `### 👉 [Open je schets](<link>)` met de
nieuwe link, en dan **Nog iets veranderen aan de schets?** met
de opties uit de nieuwe uitvoer. Stel nooit twee keer dezelfde vraag met dezelfde opties. Stop na *De schets is
goed*, na *Geen nieuwe vaste aanpassingen meer* of na vijf aanpassingen.

## 5. Afsluiten

Eindig met precies dit:

> **Je schets is klaar.** Straks bouw ik het dashboard precies zoals deze schets.
>
> **Even pauze: kijk op van je scherm.** De speaker neemt het nu over. Typ `/3-bouwen` zodra de speaker
> zegt dat je verder mag.

## Als er iets misgaat

Geeft een commando een fout, draai het één keer opnieuw. Gaat het weer mis, toon dan de melding en zeg:
*"Roep een begeleider erbij."* Probeer geen eigen oplossing.
