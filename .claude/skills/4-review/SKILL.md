---
name: 4-review
description: Geeft de link naar het review-formulier van de DAIR agentic-coding sessie (voxpop). Gebruik aan het einde van de sessie, of wanneer iemand "review", "feedback geven", "reflectie" of "afronden" zegt.
disable-model-invocation: true
---

# Review-link

Draai eerst, zonder het te noemen: `uv run scripts/vragenteller.py fase 4`.

Draai dit:

```bash
uv run scripts/feedback.py link
```

Het commando drukt de linkregel `### 👉 [Open je review](...)` af. Die uitvoer ziet de deelnemer niet: neem de
regel **letterlijk** over in je bericht, als eigen regel, en nooit in een bash-commando. Zeg erbij dat de review anoniem is en in de eigen browser ingevuld wordt.

Bij `geen workshop-token`: de deelnemer vraagt het token aan de begeleider en zet het met het commando
uit de foutmelding. Vraag het token niet in de chat.
