---
name: 4-review
description: Geeft de link naar het review-formulier van de DAIR agentic-coding sessie (voxpop). Gebruik aan het einde van de sessie, of wanneer iemand "review", "feedback geven", "reflectie" of "afronden" zegt.
disable-model-invocation: true
---

# Review-link

Draai eerst, zonder het te noemen: `uv run scripts/vragenteller.py fase 4`.

Draai dit en geef de deelnemer de URL die het commando teruggeeft:

```bash
uv run scripts/feedback.py link
```

Zeg erbij dat de review anoniem is en in de eigen browser ingevuld wordt.

Bij `geen workshop-token`: de deelnemer vraagt het token aan de begeleider en zet het met het commando
uit de foutmelding. Vraag het token niet in de chat.
