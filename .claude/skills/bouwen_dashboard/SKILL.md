---
name: bouwen_dashboard
description: >-
  Gebruik wanneer iemand na de schets (schets.html) het dashboard wil laten bouwen — eerst een raadvraag, dan maakt één script uit de keuzes in de schets het dashboard dashboard.html in de hoofdmap (kerncijfers, grafieken, filter, privacydrempel en uitleg, in de Npuls-huisstijl, zonder server), met een link om het met één klik te openen. Daarna kan de gebruiker het dashboard aanpassen met vaste keuzes, en het alleen op verzoek bewaren in GitHub. LET OP — de data verkennen hoort bij `verkennen_data` en de views schetsen bij `schets_dashboard`.
disable-model-invocation: true
allowed-tools: Read Bash AskUserQuestion
metadata:
  versie: "0.7.0"
---

# Dashboard bouwen

Deze skill hoort bij een workshop. Het doel is dat de gebruiker enthousiast raakt over werken met skills,
dus **het dashboard moet in één keer een 10 zijn**. Het script in deze skill is getest: het rekent, past de
privacydrempels toe, tekent de grafieken in de Npuls-huisstijl en werkt op telefoon en laptop. Volg de route
precies. Lees geen andere bestanden, schrijf geen eigen code en verander het script niet.

**Toon.** Je bent een agent die meedenkt: kort, warm, in gewone taal en in de ik-vorm. Reageer op wat de
gebruiker kiest of typt, in je eigen woorden. Hooguit drie zinnen per bericht. Noem geen bestandsnamen of
commando's, tenzij de gebruiker erom vraagt.

Staat `schets.html` niet in de hoofdmap, zeg dan: *"Typ eerst `/schets_dashboard`."* en stop.

Alle commando's draai je vanuit de hoofdmap, precies zoals ze hier staan.

## 1. Eerst raden

Draai:

```bash
uv run --no-project --with polars==1.44.2 python .claude/skills/bouwen_dashboard/assets/maak_dashboard.py --vanaf schets.html --gok
```

Dat drukt een vraag en drie opties af. Zeg: *"Voor ik het dashboard
bouw: wat verwacht jij?"* en stel de vraag met de AskUserQuestion-tool, met de drie opties in de afgedrukte
volgorde en als vierde *Geen idee*. Geen optie is aanbevolen. Onthoud het antwoord.

## 2. Bouwen

Zeg in één zin: *"Ik bouw nu je dashboard: ik tel de eerstejaars, verberg groepen die te klein zijn en zet
alles in de Npuls-huisstijl."* Draai dan:

```bash
uv run --no-project --with polars==1.44.2 python .claude/skills/bouwen_dashboard/assets/maak_dashboard.py --vanaf schets.html
python3 .claude/skills/verkennen_data/assets/toon.py dashboard.html
```

Het eerste commando drukt af wat het dashboard laat zien (hoogst, laagst, over de jaren) en welke
aanpassingen kunnen. Het tweede drukt de link af.

## 3. De onthulling

Eindig met dit, in je eigen woorden maar met deze opbouw en de afgedrukte link:

> **Je dashboard staat klaar.** [Open het dashboard](<link>) of klik in de verkenner links op `dashboard.html`.
>
> <Reageer op de gok: goed geraden, of *"Je gokte X; het blijkt Y te zijn (Z%)."* Bij *Geen idee*: noem
> gewoon de hoogste.> <Eén zin over de jaren, uit de afgedrukte regel.> Dit is demodata: het laat zien wat
> het dashboard kan, niet hoe het echt zit.
>
> Probeer het filter bovenaan. Groepen met te weinig studenten verdwijnen vanzelf: zo beschermt het
> dashboard de privacy.

## 4. Aanpassen

Vraag met de AskUserQuestion-tool: **Wil je nog iets anders zien?** Opties: de aanpassingen uit de laatste
uitvoer (elke regel na *Aanpassen*, het deel vóór `=>` als label, de eerste met "(Aanbevolen)"), en als
laatste *Het is goed zo*. Bij een aanpassing:

1. Zeg in één zin wat je verandert (*"Ik vergelijk nu per opleiding."*).
2. Draai `uv run --no-project --with polars==1.44.2 python .claude/skills/bouwen_dashboard/assets/maak_dashboard.py --vanaf dashboard.html` met het deel na `=>` erachter (bijvoorbeeld `--uitsplitsing opleiding`),
   en daarna opnieuw `python3 .claude/skills/verkennen_data/assets/toon.py dashboard.html`.
3. Vertel in één of twee zinnen wat er nu bovenaan staat, met de nieuwe link, en stel de vraag opnieuw met
   de nieuwe aanpassingen.

Stop na *Het is goed zo* of na drie aanpassingen. Typt de gebruiker een eigen wens, herhaal dan in één zin
wat je hoort en kies de aanpassing die er het dichtst bij ligt (*"Je wilt zien hoe het per opleiding zit:
dat kan ik nu meteen bouwen."*). Past niets, zeg dan eerlijk wat er nu kan, en dat het script later op eigen
data en met eigen vragen verder te bouwen is.

## 5. Bewaren

Vraag tot slot met de AskUserQuestion-tool: **Wil je dit bewaren in je eigen GitHub?** met de opties *Nog
niet* (aanbevolen) en *Nu bewaren*. Kiest de gebruiker *Nu bewaren* of typt de gebruiker 'bewaar', volg dan
*Bewaren, alleen op verzoek*. Sluit af met: *"Onderaan het dashboard staat het commando waarmee het opnieuw
draait op je eigen data, zonder AI."*

## Als er iets misgaat

Geeft een commando een fout, draai het één keer opnieuw. Gaat het weer mis, toon dan de melding en zeg:
*"Roep een begeleider erbij."* Probeer geen eigen oplossing.

## Bewaren, alleen op verzoek

Commit en push alleen als de gebruiker erom vraagt, en nooit zonder bevestiging.

1. **Laat zien wat er gebeurt.** De uitkomsten (`data-profiel.html`, `schets.html`, `dashboard.html`) staan
   bewust in `.gitignore`: ze kunnen op echte data gedraaid zijn. Wil de gebruiker ze toch bewaren, noem dan
   de bestanden en de repo waar ze heen gaan. Heeft de gebruiker geen schrijfrechten op die repo, zeg dan dat
   GitHub een kopie (fork) in het eigen account van de gebruiker maakt, en dat die kopie **openbaar** is als
   de oorspronkelijke repo openbaar is. Vraag om akkoord met de AskUserQuestion-tool (*Doorgaan* of
   *Annuleren*).
2. **Na akkoord:** lees `.claude/skills/ship/SKILL.md` en volg die om te committen en te pushen. In een
   Codespace regelt `GITHUB_TOKEN` de toegang tot de repo: laat die staan, ook waar `ship` aanraadt hem te
   unsetten.
3. **Weigert de push:** omzeil dat niet en vraag geen token. Zeg dat het werk lokaal gecommit is en geef de
   klikroute om de bestanden te downloaden: rechtsklik op het bestand in de verkenner en *Download*.

## Na de workshop

Het script draait zonder AI op eigen data met het commando onderaan het dashboard. De onderhoudstests staan
in `assets/test_maak_dashboard.py`; ze horen niet bij de workshop.
