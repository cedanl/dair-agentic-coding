---
name: 3-bouwen
description: >-
  Gebruik wanneer iemand na de schets (schets.html) het dashboard wil laten bouwen — zonder vragen vooraf maakt één script uit de keuzes in de schets het dashboard dashboard.html in de hoofdmap (kerncijfers, grafieken, filter, privacydrempel en uitleg, in de Npuls-huisstijl, zonder server), met een link om het met één klik te openen. Het dashboard volgt de schets precies; daarna één vraag (klopt het?), hooguit een kleine wens in tekst of kleur, en uitleg hoe je het meeneemt. Iets anders zien doe je in de schets. LET OP — de data verkennen hoort bij `1-verkennen` en de views schetsen bij `2-schetsen`.
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

**Bevestigen.** Ga nooit stil verder. Zeg na **elk** antwoord in één zin wat je ermee doet, vóór je de volgende
vraag stelt of iets draait. Dat geldt vooral als het antwoord niet precies één optie is: meer opties tegelijk,
"alles", "weet ik niet", "?", een eigen tekst of iets wat de workshop niet kan. Zeg dan welke keuze je maakt en
waarom (*"Je koos alle drie: ik maak het voor de studieadviseur, want één doelgroep houdt het dashboard
helder."*), en wat niet kan (*"Een kaart kan het dashboard niet maken; ik noteer het als idee voor later."*).
Kiest de gebruiker *Leg dit eerst uit*, leg dan eerst uit en stel pas daarna de vraag opnieuw.

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
   `vraag`, `vergelijken`, `filter` en `bovenaan`.
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
van de gekozen doelgroep uit de casus aan. Open wensen voor `3-bouwen` over tekst of kleur bied je bij *Klopt
je dashboard?* aan met *(jouw wens)*; zet een verwerkte wens op klaar met `python3 scripts/keuzes.py wens-klaar
<nummer>`.

Is de AskUserQuestion-tool niet beschikbaar, stel een keuzevraag dan in het gesprek: de opties als A, B, C
(met *(aanbevolen)* achter de aanbevolen optie), en stop je bericht daar. Ga pas verder als de gebruiker
antwoordt.

Staat `schets.html` niet in de hoofdmap, zeg dan: *"Typ eerst `/2-schetsen`."* en stop.

Alle commando's draai je vanuit de hoofdmap, precies zoals ze hier staan.

**Start.** Draai eerst, zonder het te noemen: `uv run scripts/vragenteller.py fase 3`.

## 1. Bouwen

Zeg in twee zinnen: *"Ik bouw je dashboard precies zoals je schets: dezelfde vergelijkingen, filters en titel.
Wil je straks iets anders zien, dan pas je de schets aan met `/2-schetsen`."* Draai dan:

```bash
uv run --no-project --with polars==1.44.2 python .claude/skills/3-bouwen/assets/maak_dashboard.py --vanaf schets.html
python3 .claude/skills/1-verkennen/assets/toon.py dashboard.html
```

Het eerste commando drukt af wat het dashboard laat zien (hoogst, laagst, over de jaren). Het tweede drukt de
link af. De regels onder *Aanpassen* gebruik je in deze skill niet: veranderen doe je in de schets.

## 2. Laten zien

Geef de link meteen, met deze opbouw in je eigen woorden:

> **Je dashboard staat klaar.** Klik op de link om het te openen:
>
> ### 👉 [Open je dashboard](<link>)
>
> <Eén zin over wat er bovenaan staat en één over de jaren, uit de afgedrukte regels, zonder oordeel.> Dit
> is demodata: het laat zien wat het dashboard kan, niet hoe het echt zit.
>
> <Alleen als het dashboard filters of meer vergelijkingen heeft: "Probeer de keuzelijsten bovenaan."> Groepen met te weinig studenten
> verdwijnen vanzelf: zo beschermt het dashboard de privacy.

## 3. Eén vraag

Vraag met de AskUserQuestion-tool: **Klopt je dashboard?** Opties: *Ja, het is goed* (aanbevolen), open
wensen voor `3-bouwen` over tekst of kleur met *(jouw wens)*, en *Ik wil iets anders zien*. Een kleine wens
typt de gebruiker via *Other*. Meer vragen stel je in deze skill niet.

- **Ja, het is goed:** ga naar *Meenemen en afsluiten*.
- **Iets anders zien (vergelijkingen, filters, wat bovenaan staat, de titel):** dat hoort in de schets. Zeg:
  *"Dat pas je aan in de schets: typ `/2-schetsen`, verander wat je wilt, en typ daarna weer `/3-bouwen`. Je
  keuzes blijven bewaard."* en stop.
- **Een kleine wens: tekst of kleur.** Een andere uitleg, een kortere ondertitel, een andere kleur uit de
  Npuls-huisstijl (`--npuls-oranje`, `--npuls-groen`, `--npuls-blauw`, `--npuls-geel`; nooit rood), een zin
  erbij in *Zo lees je dit*. Dit doe je zelf, hooguit twee keer:
  1. Zeg wat je gaat veranderen en pas `dashboard.html` aan met de Edit-tool. Alleen dat bestand; nooit het
     script, de schets, het casusbestand of de data.
  2. Laat elk getal, elk percentage, elke verborgen groep, het filter, het label *Dit is demodata* en de
     privacyuitleg staan zoals ze zijn, en voeg geen getallen of scripts toe.
  3. Draai `uv run --no-project --with polars==1.44.2 python .claude/skills/3-bouwen/assets/maak_dashboard.py
     --vanaf dashboard.html --controleer`. Bij *Goed* zeg je *"Gedaan: …"*, geef je opnieuw de link (`toon.py
     dashboard.html`) en zeg je eerlijk: *"Bouw je het later opnieuw, dan zit deze wijziging er niet in."*
     Vraag daarna nog één keer **Is het zo goed?** (*Ja, het is goed* of *Nog een kleine wens*).
  4. Bij *Niet goed* draai je `uv run --no-project --with polars==1.44.2 python
     .claude/skills/3-bouwen/assets/maak_dashboard.py --vanaf schets.html` om het dashboard te herstellen, en zeg
     je dat deze wens net te veel raakt. Probeer het niet een tweede keer.
- **Groot: een nieuwe maat, een ander soort grafiek, andere data, een voorspelling of een oorzaak.** Zeg in
  twee zinnen waarom het een mooi idee is en dat het een vervolgstap is voor na de workshop, noteer het als wens
  voor `later`, en ga naar *Meenemen en afsluiten*.

## 4. Meenemen en afsluiten

Draai eerst opnieuw `python3 .claude/skills/1-verkennen/assets/toon.py dashboard.html` voor de link. Eindig
dan, zonder vraag, met precies dit als **laatste bericht**, in één bericht. Zet er niets meer onder:

> Wil je weten wat er is gerekend? In `dashboard-berekeningen.py` staat precies hoe de cijfers zijn berekend.
> Deze Codespace is tijdelijk: wil je je dashboard houden, klik dan in de verkenner met de rechtermuisknop op
> `dashboard.html` (en het rekenbestand erbij) en kies **Download**. Er gaat niets naar GitHub. Onderaan het
> dashboard staat het commando waarmee het opnieuw draait op je eigen data, zonder AI.
>
> **Je dashboard is af. Even pauze: de speaker neemt het nu over.** Bekijk je dashboard via de link:
>
> ### 👉 [Open je dashboard](<link>)
>
> Typ `/4-review` als de speaker vraagt om de sessie te beoordelen. Dat is anoniem.

## Als er iets misgaat

Geeft een commando een fout, draai het één keer opnieuw. Gaat het weer mis, toon dan de melding en zeg:
*"Roep een begeleider erbij."* Probeer geen eigen oplossing.

## Na de workshop

Het script draait zonder AI op eigen data met het commando onderaan het dashboard. De onderhoudstests staan
in `assets/test_maak_dashboard.py`; ze horen niet bij de workshop.
