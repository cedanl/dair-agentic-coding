# DAIR — Agentic Coding Sessie

Welkom bij de agentic coding sessie. Je hebt geen lokale installatie nodig — alles draait in de browser via GitHub Codespaces.

Na afloop kun je:

- een vraag over data omzetten in een dashboard, samen met Claude;
- uitleggen hoe de cijfers in je dashboard zijn berekend en welke privacyregels erin zitten;
- aangeven wat je zelf beslist en wat je aan Claude overlaat.

---

## Aan de slag

### Stap 1 — Log in op GitHub

Ga naar [github.com](https://github.com) en log in met je eigen account. Heb je er nog geen? Maak er dan gratis een aan met **Sign up**.

---

### Stap 2 — Maak een Codespace aan

Klik op de groene knop **Code**, dan op de tab **Codespaces** en daarna op **Create codespace on main**.

![Stap 2 — Code knop](docs/images/01-repo-pagina.png)

![Stap 2 — Codespaces dropdown](docs/images/02-codespaces-dropdown.png)

---

### Stap 3 — Wacht tot de omgeving klaar is

De Codespace start vanzelf op. Dit duurt twee tot drie minuten. De workshop-key staat al klaar, je hoeft niets in te stellen.

![Stap 3 — Codespace laadt](docs/images/03-codespace-laadt.png)

Verschijnt de vraag **Do you trust the authors of the files in this folder?**, klik dan op **Trust Folder & Continue**. Zonder dat vertrouwen start de terminal niet. De bestanden komen uit de workshop-repo van CEDA.

![Stap 3 — Map vertrouwen](docs/images/03b-vertrouw-map.png)

---

### Stap 4 — Open het Claude-paneel

Klik op het **oranje Claude-icoon** rechtsboven in de editor. Het Claude-paneel opent aan de rechterkant.

![Stap 4 — Claude-knop](docs/images/05-claude-knop.png)

---

### Stap 5 — Start met de eerste skill

Typ `/1-verkennen` in het vak onderaan het paneel en druk op **Enter**. Claude stelt je dan drie vragen en gaat daarna aan de slag. Met `/` zie je alle beschikbare skills. Hieronder staat wat elke skill doet.

![Stap 5 — Claude-paneel](docs/images/06-claude-paneel.png)

> Vraagt een terminal toch om een workshop-key? Roep de begeleider.

---

## De skills

Een skill is een werkwijze die Claude volgt. Je start er een met `/` en de naam. Skills starten alleen als je ze zelf typt; tijdens gewoon chatten springen ze niet vanzelf aan. In deze sessie gebruik je er drie, achter elkaar:

| Stap | Skill | Wat Claude doet | Wat je krijgt |
|---|---|---|---|
| 1 | `/1-verkennen` | Leert samen met jou de data kennen: wat de kolommen kunnen betekenen, hoe het staat met de datakwaliteit en de verdelingen, welke definities en privacyregels gelden, en welke ideeën er bij jouw vraag passen | `data-profiel.html` |
| 2 | `/2-schetsen` | Schetst twee of drie grafieken (views) op papier, nog zonder code | `schets.html` |
| 3 | `/3-bouwen` | Bouwt het dashboard, met een (schijn-)uploadscherm als eerste scherm, en test het daarna | Een dashboard dat je zelf opent |

**Hoe het werkt.** Claude stelt je vragen één voor één, elk met een standaardantwoord, of doet een voorstel. Antwoord "ok" of corrigeer wat niet klopt: jij beslist over de inhoud, Claude voert uit. De uitkomsten (HTML) komen in de hoofdmap, bovenaan in de verkenner. Zie hieronder hoe je ze opent.

**Een HTML-bestand openen in Codespaces.** Claude geeft je na elke stap een link: klik erop. Werkt de link niet, klik dan met de rechtermuisknop op het bestand in de verkenner en kies **Show Preview**. De pagina opent in een nieuw tabblad van je browser; vraagt GitHub om door te gaan, klik dan op *Continue*. Zie je in plaats daarvan *This content is blocked*, dan opent de preview nog binnen VS Code: druk op `Ctrl+Shift+P` (Mac: `Cmd+Shift+P`) en kies **Live Preview: Show Preview (External Browser)**. Staat *Show Preview* er niet tussen, installeer dan de extensie **Live Preview** van Microsoft (`ms-vscode.live-server`) via het Extensions-paneel (`Ctrl+Shift+X`).

**Andere skills.** De skills verwijzen naar `vormgever-npuls-huisstijl` (de Npuls-stijl), die CEDA ook in eigen projecten gebruikt en die in deze repo staat. Je hoeft hem niet zelf te starten.

**Meenemen.** Claude zet niets in GitHub. Je Codespace is tijdelijk: wil je je werk houden, klik dan met de rechtermuisknop op het bestand in de verkenner en kies *Download*. Naast `dashboard.html` staat `dashboard-berekeningen.py`: daarin kun je lezen hoe de cijfers zijn berekend. Download die er ook bij als je wilt kunnen terugkijken.

**De data.** De demodata (fictieve studenten) staat in `data/demodata_1cho.csv`. Heb je uitleg bij de data (een codebook, een omschrijving van de kolommen, een definitie), geef die dan aan Claude wanneer `/1-verkennen` daarom vraagt. Heb je dat niet, dan leidt Claude de betekenis af uit de kolomnamen en vraagt het jou om te bevestigen. De skills zelf kennen geen 1CHO en werken ook met andere data. Het dashboard begint met een uploadscherm, zoals in een echte toepassing. Voor de workshop staat het bestand daar al klaar: je hoeft niets te downloaden of te uploaden, alleen op *Doorgaan* te klikken. Welk bestand het dashboard gebruikt, staat in het startcommando dat Claude je geeft.

Aan het einde van de sessie sluit je af met `/4-review` (zie hieronder).

---

## Review geven

Aan het einde van de sessie geef je je review **in Claude**: typ `/4-review`. Er opent een vragenlijst die je invult.

De review is anoniem en gaat naar de begeleiders. Je kunt een vraag overslaan.

---

## Hulp nodig?

Spreek een begeleider aan of stel je vraag hardop, dat is precies waar deze sessie over gaat.
