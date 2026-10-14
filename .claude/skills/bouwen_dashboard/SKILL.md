---
name: bouwen_dashboard
description: >-
  Gebruik wanneer iemand na de schets (schets.html) het dashboard wil laten bouwen — zonder vragen vooraf maakt één script uit de keuzes in de schets het dashboard dashboard.html in de hoofdmap (kerncijfers, grafieken, filter, privacydrempel en uitleg, in de Npuls-huisstijl, zonder server), met een link om het met één klik te openen. Daarna kan de gebruiker het dashboard aanpassen met vaste keuzes, en het alleen op verzoek bewaren in GitHub. LET OP — de data verkennen hoort bij `verkennen_data` en de views schetsen bij `schets_dashboard`.
disable-model-invocation: true
allowed-tools: Read Edit Bash AskUserQuestion
metadata:
  versie: "0.7.0"
---

# Dashboard bouwen

Deze skill hoort bij een workshop. Het doel is dat de gebruiker enthousiast raakt over werken met skills,
dus **het dashboard moet in één keer een 10 zijn**. Het script in deze skill is getest: het rekent, past de
privacydrempels toe, tekent de grafieken in de Npuls-huisstijl en werkt op telefoon en laptop. Volg de route
precies. Lees geen andere bestanden, schrijf geen eigen code en verander het script niet. Alleen bij een
kleine wens van de gebruiker mag je `dashboard.html` zelf aanpassen (zie *Aanpassen*).

**Toon.** Je bent een agent die meedenkt: kort, warm, in gewone taal en in de ik-vorm. Reageer op wat de
gebruiker kiest of typt, in je eigen woorden. Hooguit drie zinnen per bericht. Noem geen bestandsnamen of
commando's, tenzij de gebruiker erom vraagt.

Is de AskUserQuestion-tool niet beschikbaar, stel een keuzevraag dan in het gesprek: de opties als A, B, C
(met *(aanbevolen)* achter de aanbevolen optie), en stop je bericht daar. Ga pas verder als de gebruiker
antwoordt.

Staat `schets.html` niet in de hoofdmap, zeg dan: *"Typ eerst `/schets_dashboard`."* en stop.

Alle commando's draai je vanuit de hoofdmap, precies zoals ze hier staan.

## 1. Bouwen

Zeg in één zin: *"Ik bouw nu je dashboard: ik tel de eerstejaars, verberg groepen die te klein zijn en zet
alles in de Npuls-huisstijl."* Draai dan:

```bash
uv run --no-project --with polars==1.44.2 python .claude/skills/bouwen_dashboard/assets/maak_dashboard.py --vanaf schets.html
python3 .claude/skills/verkennen_data/assets/toon.py dashboard.html
```

Het eerste commando drukt af wat het dashboard laat zien (hoogst, laagst, over de jaren) en welke
aanpassingen kunnen. Het tweede drukt de link af.

## 2. Laten zien

Geef de link meteen, met deze opbouw in je eigen woorden:

> **Je dashboard staat klaar.** [Open het dashboard](<link>) of klik in de verkenner links op `dashboard.html`.
>
> <Eén zin over wat er bovenaan staat en één over de jaren, uit de afgedrukte regels, zonder oordeel.> Dit
> is demodata: het laat zien wat het dashboard kan, niet hoe het echt zit.
>
> Probeer het filter bovenaan. Groepen met te weinig studenten verdwijnen vanzelf: zo beschermt het
> dashboard de privacy.

## 3. Aanpassen

Vraag met de AskUserQuestion-tool: **Wil je nog iets anders zien?** Opties, in deze volgorde: de eerste twee
aanpassingen uit de laatste uitvoer (de regels die met `- ` beginnen na *Aanpassen*, het deel vóór `=>` als
label, de eerste met "(Aanbevolen)"), *Iets anders aanpassen* en *Het is goed zo*. Stop na *Het is goed zo*
of na drie aanpassingen of wensen samen.

**Een vaste aanpassing:**

1. Zeg in één zin wat je verandert (*"Ik vergelijk nu per opleiding."*).
2. Draai `uv run --no-project --with polars==1.44.2 python .claude/skills/bouwen_dashboard/assets/maak_dashboard.py --vanaf dashboard.html` met het deel na `=>` erachter (bijvoorbeeld `--uitsplitsing opleiding`),
   en daarna opnieuw `python3 .claude/skills/verkennen_data/assets/toon.py dashboard.html`.
3. Vertel in één of twee zinnen wat er nu bovenaan staat, met de nieuwe link, en stel de vraag opnieuw.

Een vaste aanpassing maakt het dashboard opnieuw: kleine wensen van eerder verdwijnen dan. Zeg dat als er al
een kleine wens was doorgevoerd.

**Iets anders aanpassen, of een eigen wens in eigen woorden:** vraag in het gesprek wat de gebruiker wil
veranderen, herhaal het in één zin, en kijk of het een kleine of een grote wens is.

- **Klein: tekst, kleur of volgorde in het dashboard.** Een andere titel of uitleg, een kortere ondertitel,
  een andere kleur uit de Npuls-huisstijl (`--npuls-oranje`, `--npuls-groen`, `--npuls-blauw`, `--npuls-geel`;
  nooit rood), de views in een andere volgorde, een zin erbij in *Zo lees je dit*. Dit doe je zelf:
  1. Zeg wat je gaat veranderen en pas `dashboard.html` aan met de Edit-tool. Alleen dat bestand; nooit het
     script, de schets, het casusbestand of de data.
  2. Laat elk getal, elk percentage, elke verborgen groep, het filter, het label *Dit is demodata* en de
     privacyuitleg staan zoals ze zijn, en voeg geen getallen of scripts toe.
  3. Draai `uv run --no-project --with polars==1.44.2 python .claude/skills/bouwen_dashboard/assets/maak_dashboard.py --vanaf dashboard.html --controleer`. Bij *Goed* geef je opnieuw de link (`toon.py
     dashboard.html`) en zeg je eerlijk: *"Dit heb ik in je dashboard aangepast. Bouw je het later opnieuw op
     je eigen data, dan zit deze wijziging er niet in; daarvoor passen we na de workshop het script aan."*
  4. Bij *Niet goed* draai je `uv run --no-project --with polars==1.44.2 python .claude/skills/bouwen_dashboard/assets/maak_dashboard.py --vanaf dashboard.html` om het dashboard te herstellen, en zeg je dat deze
     wens net te veel raakt, met een kleinere variant als voorstel. Probeer het niet een tweede keer.
- **Groot: een nieuwe maat, een ander soort grafiek, andere of extra data, een andere vraag, een
  voorspelling of een oorzaak.** Neem de wens serieus en zeg in twee zinnen waarom het een mooi idee is en
  dat het een vervolgstap is: *"Dat is precies het soort vraag waar je na de workshop het script voor
  uitbreidt; het rekenwerk moet dan eerst goed getest worden. Wat ik nu wel kan: …"* en bied de passende
  vaste aanpassing aan.
- Twijfel je of het klein of groot is, behandel het dan als groot.

## 4. Bewaren

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
