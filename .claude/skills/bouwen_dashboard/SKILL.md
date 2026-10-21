---
name: 3-bouwen
description: >-
  Gebruik wanneer iemand na de schets (schets.html) het dashboard wil laten bouwen — zonder vragen vooraf maakt één script uit de keuzes in de schets het dashboard dashboard.html in de hoofdmap (kerncijfers, grafieken, filter, privacydrempel en uitleg, in de Npuls-huisstijl, zonder server), met een link om het met één klik te openen. Daarna kan de gebruiker het dashboard aanpassen met vaste keuzes, en uitleggen hoe hij het meeneemt. LET OP — de data verkennen hoort bij `1-verkennen` en de views schetsen bij `2-schetsen`.
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

**Vragen.** Stel elke vraag met de AskUserQuestion-tool, niet als losse tekst, zodat de gebruiker op de route
blijft. Gebruik de mogelijkheden van de tool waar ze helpen en beslis per vraag zelf welke past: een korte
`header`, bij elke optie een uitleg, de aanbevolen optie eerst met *(Aanbevolen)*, `multiSelect` als meer dan
één antwoord tegelijk kan, `preview` als het vergelijken van opties daardoor duidelijker wordt, en tot vier
samenhangende vragen in één aanroep. Wil de gebruiker iets anders, dan kiest die *Other* en typt zelf.
Standaard is één vraag met drie opties en één aanbeveling: een richtlijn, geen regel. Welke vragen je stelt en
in welke volgorde ligt vast.

Is de AskUserQuestion-tool niet beschikbaar, stel een keuzevraag dan in het gesprek: de opties als A, B, C
(met *(aanbevolen)* achter de aanbevolen optie), en stop je bericht daar. Ga pas verder als de gebruiker
antwoordt.

Staat `schets.html` niet in de hoofdmap, zeg dan: *"Typ eerst `/2-schetsen`."* en stop.

Alle commando's draai je vanuit de hoofdmap, precies zoals ze hier staan.

**Start.** Draai eerst, zonder het te noemen: `uv run scripts/vragenteller.py fase 3`.

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

> **Je dashboard staat klaar.** Klik op de link om het te openen:
>
> ### 👉 [Open je dashboard](<link>)
>
> <Eén zin over wat er bovenaan staat en één over de jaren, uit de afgedrukte regels, zonder oordeel.> Dit
> is demodata: het laat zien wat het dashboard kan, niet hoe het echt zit.
>
> <Alleen als het dashboard een filter heeft: "Probeer het filter bovenaan."> Groepen met te weinig studenten
> verdwijnen vanzelf: zo beschermt het dashboard de privacy.

## 3. Aanpassen

Vraag met de AskUserQuestion-tool: **Wil je nog iets anders zien?** Opties, in deze volgorde: de eerste twee
aanpassingen uit de laatste uitvoer (de regels die met `- ` beginnen na *Aanpassen*, het deel vóór `=>` als
label, de eerste met "(Aanbevolen)") en *Het is goed zo*. Een eigen wens typt de gebruiker via *Other*. Stop na *Het is goed zo*
of na vijf aanpassingen of wensen samen.

**Een vaste aanpassing:**

1. Zeg in één zin wat je verandert (*"Ik vergelijk nu per opleiding."*).
2. Draai `uv run --no-project --with polars==1.44.2 python .claude/skills/bouwen_dashboard/assets/maak_dashboard.py --vanaf dashboard.html` met het deel na `=>` erachter (bijvoorbeeld `--uitsplitsing opleiding`),
   en daarna opnieuw `python3 .claude/skills/verkennen_data/assets/toon.py dashboard.html`.
3. Vertel in één of twee zinnen wat er nu bovenaan staat, met de nieuwe link, en stel de vraag opnieuw.

Een vaste aanpassing maakt het dashboard opnieuw: kleine wensen van eerder verdwijnen dan. Zeg dat als er al
een kleine wens was doorgevoerd.

**Een eigen wens (via *Other*, of in het gesprek getypt):** lees wat de gebruiker wil veranderen, herhaal het
in één zin, en kijk of het een kleine of een grote wens is.

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

## 4. Meenemen en afsluiten

Draai eerst opnieuw `python3 .claude/skills/verkennen_data/assets/toon.py dashboard.html` voor de link. Eindig
dan, zonder vraag, met precies dit als **laatste bericht**, in één bericht. Zet er niets meer onder:

> Wil je weten wat er is gerekend? In `dashboard-berekeningen.py` staat precies hoe de cijfers zijn berekend.
> Deze Codespace is tijdelijk: wil je je dashboard houden, klik dan in de verkenner met de rechtermuisknop op
> `dashboard.html` (en het rekenbestand erbij) en kies **Download**. Er gaat niets naar GitHub. Onderaan het
> dashboard staat het commando waarmee het opnieuw draait op je eigen data, zonder AI.
>
> **Je dashboard is af.** Klik op de link om het te openen:
>
> ### 👉 [Open je dashboard](<link>)
>
> Typ `/4-review` als je de sessie wilt beoordelen. Dat is anoniem.

## Als er iets misgaat

Geeft een commando een fout, draai het één keer opnieuw. Gaat het weer mis, toon dan de melding en zeg:
*"Roep een begeleider erbij."* Probeer geen eigen oplossing.

## Na de workshop

Het script draait zonder AI op eigen data met het commando onderaan het dashboard. De onderhoudstests staan
in `assets/test_maak_dashboard.py`; ze horen niet bij de workshop.
