---
name: bouwen_dashboard
description: >-
  Gebruik wanneer iemand na de schets (schets.html) het dashboard wil laten bouwen — zonder vragen vooraf: één script maakt uit de keuzes in de schets het dashboard dashboard.html in de hoofdmap (kerncijfers, grafieken, filter, privacydrempel en uitleg, in de Npuls-huisstijl, zonder server) en de gebruiker krijgt een link om het met één klik te openen. Daarna alleen op verzoek bewaren in GitHub. LET OP — de data verkennen hoort bij `verkennen_data` en de views schetsen bij `schets_dashboard`.
disable-model-invocation: true
allowed-tools: Read Bash AskUserQuestion
metadata:
  versie: "0.7.0"
---

# Dashboard bouwen

Deze skill hoort bij een workshop. Het doel is dat de gebruiker enthousiast raakt over werken met skills,
dus **het dashboard moet in één keer een 10 zijn**. Het script in deze skill is getest: het rekent, past de
privacydrempels toe, tekent de grafieken in de Npuls-huisstijl en werkt op telefoon en laptop. Volg de route
precies. Lees geen andere bestanden, schrijf geen eigen code en verander het script niet. Toon: kort, warm
en in gewone taal.

Staat `schets.html` niet in de hoofdmap, zeg dan: *"Typ eerst `/schets_dashboard`."* en stop.

## 1. Bouwen

Zeg in één zin: *"Ik bouw nu je dashboard uit de schets."* Draai dan, vanuit de hoofdmap:

```bash
uv run --no-project --with polars==1.44.2 python .claude/skills/bouwen_dashboard/assets/maak_dashboard.py --vanaf schets.html
python3 .claude/skills/verkennen_data/assets/toon.py dashboard.html
```

## 2. Afsluiten

Eindig met precies dit, met de link uit het tweede commando:

> **Je dashboard staat klaar.** [Open het dashboard](<link>) of klik in de verkenner links op `dashboard.html`.
>
> Probeer het filter bovenaan. Groepen met te weinig studenten verdwijnen vanzelf: zo beschermt het
> dashboard de privacy. Onderaan staat hoe je het leest, en met welk commando het opnieuw draait op je
> eigen data, zonder AI.

Vraag daarna met de AskUserQuestion-tool: **Wil je dit bewaren in je eigen GitHub?** met de opties *Nog niet*
(aanbevolen) en *Nu bewaren*. Kiest de gebruiker *Nu bewaren* of typt de gebruiker 'bewaar', volg dan
*Bewaren, alleen op verzoek*.

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

Wie verder wil: het script draait zonder AI op eigen data met het commando onderaan het dashboard. De
onderhoudstests van het script staan in `assets/test_maak_dashboard.py`; ze horen niet bij de workshop.
