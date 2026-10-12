# Dashboard: uitval in het eerste jaar per sector

Een dashboard dat de vraag beantwoordt: *verschilt het aandeel uitval in het eerste jaar tussen de sectoren?*
Je uploadt zelf een CSV. De data blijft in het geheugen van je sessie en wordt nergens opgeslagen of verstuurd.

## Starten

Open een terminal in de map `dashboard` en draai:

```
uv run --no-project --with-requirements requirements.txt streamlit run app.py
```

De eerste keer duurt het even, omdat de pakketten worden gehaald. Je hoeft niets zelf te installeren.

Je ziet daarna in de terminal een regel zoals `Local URL: http://localhost:8501`.

## Openen

| Waar draai je het? | Wat doe je? |
|---|---|
| **Op je eigen computer** | De browser opent vanzelf. Gebeurt dat niet, ga dan naar `http://localhost:8501`. |
| **In GitHub Codespaces** | Rechtsonder verschijnt een melding over poort 8501: klik op *Open in Browser*. Zie je die melding niet, open dan het tabblad *Poorten* naast de terminal en klik op het wereldbolletje bij poort 8501. |

## Gebruiken

1. **Stap 1 van 2:** kies een CSV met `;` als scheidingsteken. Wil je het uitproberen, neem dan `data/demodata_1cho.csv`.
   Laat het vinkje *Dit bestand is demodata* aan bij demodata en zet het uit bij echte data.
2. **Stap 2 van 2:** je ziet drie views onder elkaar: de sectoren naast elkaar, de ontwikkeling per instroomjaar en een tabel met de groepsgroottes. Met het filter links kies je instroomjaren en sectoren.
   Onder de grafiek staat *Zo lees je dit*, met de definities, de privacyregels en wat het dashboard niet kan zeggen.
3. **Andere data?** Klik links op *Andere data uploaden*.

In Codespaces kiest de bestandsdialoog een bestand van je eigen computer. Download het bestand dus eerst
(rechtsklik in de verkenner, *Downloaden*) en upload het daarna.

## Stoppen

Druk in de terminal op `Ctrl+C`.

## Als het niet lukt

- **Er staat een rode melding over ontbrekende kolommen.** Het bestand mist kolommen die het dashboard nodig heeft.
  De melding noemt ze. Controleer ook of het scheidingsteken een puntkomma is.
- **Het uploaden geeft in Codespaces een foutmelding (403).** Start dan met deze extra opties:
  `uv run --no-project --with-requirements requirements.txt streamlit run app.py --server.enableCORS false --server.enableXsrfProtection false`
  (dit is in deze omgeving niet getest).
- **Het bestand is te groot.** Sla een kleiner bestand op met alleen de verplichte kolommen. De grens staat op het uploadscherm.
- **Poort 8501 is bezet.** Voeg `--server.port 8502` toe aan het commando.

## Waar staat wat

| Bestand | Inhoud |
|---|---|
| `app.py` | De schermen: uploaden en het dashboard |
| `berekeningen.py` | Inlezen, uitval, waarneembaarheid en privacyregels |
| `configuratie.py` | Kolomnamen, scheidingsteken en drempels |
| `.streamlit/config.toml` | Thema en uploadgrens |
| `npuls/` | Npuls-huisstijl: stijlblad en het officiële Npuls-logo |
| `requirements.txt` | De pakketten die nodig zijn |

De drempels (30 en 5) zijn voorbeeldwaarden. Stem de echte waarden af met je organisatie.
