---
name: review-reflect
description: Sluit de DAIR agentic-coding sessie af met een korte review. Interviewt de deelnemer over de sessie (nut, tempo, wat geleerd, wat beter) en stuurt de antwoorden naar voxpop. Gebruik aan het einde van de sessie, of wanneer iemand "review", "feedback geven", "reflectie" of "afronden" zegt.
---

# Review & reflectie

Je helpt de deelnemer aan het einde van de sessie een korte review te geven. De antwoorden gaan anoniem
naar de voxpop-database van de begeleiders. Houd het kort: ongeveer twee minuten.

## Stappen

1. **Haal de vragen op** — de server is de bron, niet deze tekst:

   ```bash
   python3 scripts/feedback.py questions
   ```

   Elke vraag heeft `id`, `text`, `type` (`scale`, `choice` of `text`) en bij scale/choice `options`
   (bij `scale` ook `labels`: eerste = laagste, laatste = hoogste).

2. **Stel de vragen één voor één** in het Nederlands.
   - `scale` en `choice`: gebruik AskUserQuestion met de `options` als keuzes.
   - `text`: vraag in een gewone chatvraag om een of twee zinnen.
   - Alle vragen zijn optioneel; accepteer "sla over". Minstens één antwoord is nodig.
   - Vul nooit antwoorden in namens de deelnemer en suggereer geen antwoord.

3. **Toon een samenvatting en vraag bevestiging** voor je iets verstuurt. Zeg erbij dat de review anoniem
   is en naar de begeleiders gaat; laat de deelnemer zo nodig tekst aanpassen of weghalen (vrije tekst
   kan per ongeluk namen of persoonsgegevens bevatten).

4. **Verstuur** met een JSON-object `{vraag-id: antwoord}`, alleen de beantwoorde vragen. Geef de JSON via
   stdin zodat quotes in tekst niet stuk gaan:

   ```bash
   python3 scripts/feedback.py submit <<'JSON'
   {"nuttig": "4", "tempo": "Precies goed", "geleerd": "..."}
   JSON
   ```

5. **Meld het resultaat.** Bij "geen workshop-token" of een 401: laat de deelnemer de begeleider om het
   token vragen en toon het commando uit de foutmelding; vraag het token niet in de chat. Bij 429: dezelfde
   review is net al verstuurd. Probeer niet te omzeilen.
   **Niet bereikbaar** (time-out): vanuit Codespaces wordt SDP soms geblokkeerd. Draai dan
   `python3 scripts/feedback.py link` en laat de deelnemer die link in de eigen browser openen om het
   webformulier in te vullen. Toon de link aan de deelnemer; de antwoorden die al verzameld zijn kunnen
   daar opnieuw worden ingevuld.
