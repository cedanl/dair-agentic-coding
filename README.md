# DAIR — Agentic Coding Sessie

Welkom bij de agentic coding sessie. Je hebt geen lokale installatie nodig — alles draait in de browser via GitHub Codespaces.

---

## Aan de slag

### Stap 1 — Klik op de groene "Code" knop

Zoek de groene knop rechtsboven in deze pagina en klik erop.

![Stap 1 — Code knop](docs/images/01-repo-pagina.png)

---

### Stap 2 — Open de Codespaces tab en maak een Codespace aan

Klik op de tab **Codespaces** en daarna op de groene knop **Create codespace on main**.

![Stap 2 — Codespaces dropdown](docs/images/02-codespaces-dropdown.png)

---

### Stap 3 — Wacht tot de omgeving klaar is

De Codespace start automatisch op. Dit duurt ongeveer één minuut.

![Stap 3 — Codespace laadt](docs/images/03-codespace-laadt.png)

---

### Stap 4 — Voer de workshop-key in (via de terminal)

Klik in de menubalk op **Terminal → New Terminal**.

> Sneltoets: `Ctrl+`` ` (Windows/Linux) of `Ctrl+`` ` (Mac)

![Stap 4 — Terminal openen](docs/images/04-vscode-terminal.png)

De eerste keer vraagt de terminal om de **workshop-key**. Die krijg je van de begeleider. Plak hem en druk op **Enter** (je ziet tijdens het plakken niets verschijnen, dat is normaal). Opnieuw instellen kan altijd met `dair-onboard`.

---

### Stap 5 — Open het Claude-paneel

Klik op het **oranje Claude-icoon** rechtsboven in de editor. Het Claude-paneel opent aan de rechterkant. Je hoeft niets in de terminal te typen.

![Stap 5 — Claude-knop](docs/images/05-claude-knop.png)

---

### Stap 6 — Geef Claude een opdracht

Typ je opdracht in het vak onderaan het paneel en druk op **Enter**. Met `/` zie je alle beschikbare commando's en skills, zoals `/workshop-verkennen` en `/workshop-dashboard`.

![Stap 6 — Claude-paneel](docs/images/06-claude-paneel.png)

---

## Review geven

Aan het einde van de sessie, kies de route die voor jou werkt:

1. **Webformulier (aanbevolen).** Draai dit in de terminal en open de link in je browser:

   ```
   python3 scripts/feedback.py link
   ```

   Je kunt ook de link gebruiken die de begeleider deelt.
2. **In Claude:** typ `/review-reflect`.
3. **In de terminal, zonder Claude:** `python3 scripts/feedback.py form`

Routes 2 en 3 sturen vanuit je Codespace rechtstreeks naar voxpop. Dat lukt niet altijd (soms time-out); gebruik dan route 1.

De review is anoniem en gaat naar de begeleiders. Enter slaat een vraag over.

---

## Hulp nodig?

Spreek een begeleider aan of stel je vraag hardop, dat is precies waar deze sessie over gaat.
