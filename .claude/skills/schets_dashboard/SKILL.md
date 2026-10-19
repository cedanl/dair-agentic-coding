---
name: 2-schetsen
description: Gebruik wanneer iemand na het dataprofiel (data-profiel.html) het dashboard wil schetsen — één vraagronde (filter en volgorde), dan maakt één script schets.html in de hoofdmap met de twee views op papier, zonder data en zonder getallen, en krijgt de gebruiker een link om het met één klik te openen. LET OP — de data verkennen hoort bij `1-verkennen` en het dashboard bouwen bij `3-bouwen`.
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

**Vragen.** Stel elke vraag met de AskUserQuestion-tool, niet als losse tekst, zodat de gebruiker op de route
blijft. Gebruik de mogelijkheden van de tool waar ze helpen en beslis per vraag zelf welke past: een korte
`header`, bij elke optie een uitleg, de aanbevolen optie eerst met *(Aanbevolen)*, `multiSelect` als meer dan
één antwoord tegelijk kan, `preview` als het vergelijken van opties daardoor duidelijker wordt, en tot vier
samenhangende vragen in één aanroep. Wil de gebruiker iets anders, dan kiest die *Other* en typt zelf.
Standaard is één vraag met drie opties en één aanbeveling: een richtlijn, geen regel. Welke vragen je stelt en
in welke volgorde ligt vast.

Staat `data-profiel.html` niet in de hoofdmap, zeg dan: *"Typ eerst `/1-verkennen`."* en stop.

**Start.** Draai daarna, zonder het te noemen: `uv run scripts/vragenteller.py fase 2`.

## 1. Eén vraagronde

Lees de keuzes uit de regel `<meta name="keuzes" ...>` bovenaan `data-profiel.html` (de vraag en de
uitsplitsing) en de `filters` en `uitsplitsingen` uit het casusbestand naast de data. Zeg in één zin wat je
meeneemt (*"Je wilt weten welk deel van de eerstejaars stopt, per sector. Ik zet twee grafieken op papier."*)
en stel dan in **één** aanroep van de AskUserQuestion-tool twee vragen:

1. **Waarop wil je kunnen filteren?** Opties: de `filters` uit de casus behalve de gekozen uitsplitsing, met
   hun `label` en "(Aanbevolen)" achter de eerste, en *Geen filter*.
2. **Wat wil je bovenaan zien?** Opties: *De vergelijking tussen groepen* (aanbevolen) en *De ontwikkeling over
   de jaren*.

Typt de gebruiker iets eigens, herhaal dan in één zin wat je hoort en kies de optie die er het dichtst bij
ligt (*"Je wilt per stad kunnen kijken: dat is het filter op vestiging."*). Past geen optie, zoals een ander
soort grafiek (sankey, kaart) of een filter dat er niet bij staat, kies dan de **aanbevolen** optie en zeg in
twee zinnen dat het een mooi idee is voor na de workshop, als het script wordt uitgebreid. Verwijs niet naar
een begeleider. Is de AskUserQuestion-tool niet beschikbaar, stel de vraag dan in het gesprek: de opties als A, B, C (met
*(aanbevolen)* achter de aanbevolen optie), en stop je bericht daar. Ga pas verder als de gebruiker antwoordt.

## 2. Schets maken

Zeg in één zin wat je doet (*"Ik schets nu de twee grafieken, nog zonder getallen: eerst kijken of de opzet
klopt, dan pas bouwen."*). Draai dan, vanuit de hoofdmap, met de gekozen filter (`vestiging`, `geslacht` of `geen`) en volgorde (`groep` of
`jaar`):

```bash
python3 .claude/skills/schets_dashboard/assets/maak_schets.py --filter vestiging --volgorde groep
python3 .claude/skills/verkennen_data/assets/toon.py schets.html
```

## 3. Afsluiten

Eindig met precies dit, met de twee views en het filter uit de uitvoer van het eerste commando en de link
uit het tweede:

> **Je schets staat klaar.** [Open de schets](<link>) of klik in de verkenner links op `schets.html`.
>
> Bovenaan komt *<view 1>*, daaronder *<view 2>*, met een filter op <filter>. Nog zonder getallen: die
> komen pas in het dashboard.
>
> Volgende stap: typ `/3-bouwen`.

## Als er iets misgaat

Geeft een commando een fout, draai het één keer opnieuw. Gaat het weer mis, toon dan de melding en zeg:
*"Roep een begeleider erbij."* Probeer geen eigen oplossing.
