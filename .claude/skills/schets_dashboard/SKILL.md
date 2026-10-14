---
name: schets_dashboard
description: Gebruik wanneer iemand na het dataprofiel (data-profiel.html) het dashboard wil schetsen — één vraagronde (filter en volgorde), dan maakt één script schets.html in de hoofdmap met de twee views op papier, zonder data en zonder getallen, en krijgt de gebruiker een link om het met één klik te openen. LET OP — de data verkennen hoort bij `verkennen_data` en het dashboard bouwen bij `bouwen_dashboard`.
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

Staat `data-profiel.html` niet in de hoofdmap, zeg dan: *"Typ eerst `/verkennen_data`."* en stop.

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
ligt (*"Je wilt per stad kunnen kijken: dat is het filter op vestiging."*). Is de AskUserQuestion-tool niet beschikbaar, stel de vraag dan in het gesprek: de opties als A, B, C (met
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
> Volgende stap: typ `/bouwen_dashboard`.

## Als er iets misgaat

Geeft een commando een fout, draai het één keer opnieuw. Gaat het weer mis, toon dan de melding en zeg:
*"Roep een begeleider erbij."* Probeer geen eigen oplossing.
