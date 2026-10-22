# Onderzoek: puntjes op de i voor een professionele workshop

Onderzocht op 2026-10-19 aan de hand van primaire bronnen. Toegepast op `.devcontainer/devcontainer.json` zoals die nu in de repo staat.

## Conclusie

- Professionaliteit zit vooral in wat de deelnemer niet hoeft te doen: geen welkomstpagina's, geen tips, geen meldingen, direct het juiste bestand en de juiste layout.
- Veel van de inrichting staat al goed (startEditor, tips, meldingen, extensies). Wat nog ontbreekt: een bewust gekozen thema, layout (Claude rechts), `openFiles`, `hostRequirements`, benoemde poort en een prebuild.
- Didactisch: begeleide oefening werkt beter dan vrij ontdekken, zeker voor beginners; houd ervaren deelnemers bezig met verdiepingsvragen.
- Een spiegelmoment is bruikbaar als vast ritme (voor en na elke bouwfase), met anonieme feedback aan het eind van een blok.
- Wachttijd en storingen: ontwerp ze vooraf (fallback, helpers, wat te doen tijdens het wachten). Foutmeldingen zijn leermomenten, geen falen.
- Behoud: laat deelnemers het resultaat meenemen; de Codespace verdwijnt. In deze workshop kan dat alleen via download, er gaat niets naar GitHub.

## 1. Workshop-opzet

**Leerdoelen vooraf, achterwaarts ontworpen.** Wat: formuleer wat een deelnemer na afloop kan, en bouw de oefeningen daarvan af. Waarom: de Carpentries-training maakt van leerdoelen het startpunt per episode (elke episode opent met Questions en Objectives). Toepassing: drie zinnen bovenaan de README en op de eerste slide ("Na afloop kun je ...") en dezelfde zinnen terug in het spiegelmoment aan het eind. Bron: https://carpentries.github.io/instructor-training/17-live.html (structuur Overview/Objectives zichtbaar op elke episodepagina).

**Begeleide oefening in plaats van vrij ontdekken.** Wat: geef beginners een duidelijke route. Waarom: minimale begeleiding mislukt vaak bij novices omdat ze inhoud en zoekstrategie tegelijk moeten leren; bij gevorderden werkt het wel. Toepassing: een vaste route met de skills (bouwen_dashboard), plus een "ga-verder"-opdracht voor ervaren deelnemers. Bron: https://carpentries.github.io/instructor-training/05-memory.html (sectie "Is Guided Practice Hand Holding?").

**Tempo: langzamer dan je denkt, hardop benoemen.** Wat: zeg wat je gaat doen, doe het, leg daarna uit wat er gebeurde. Waarom: luisteren en tegelijk typen kost werkgeheugen (split-attention). Toepassing: de speaker laat dezelfde route zien in dezelfde omgeving als de deelnemers (geen eigen sneltoetsen of andere layout). Bron: https://carpentries.github.io/instructor-training/17-live.html ("Top Ten Tips", tip 2 en 3).

**Spiegelmoment als vast ritme.** Wat: na elke fase een korte pauze van de computer, speaker weer aan het woord. Waarom: de Carpentries gebruiken kort feedbackmomenten voor elke lange pauze en benoemen expliciet wat ze met de feedback doen. Toepassing: één vraag per spiegelmoment ("Wat besliste jij, wat Claude?"), antwoord anoniem of mondeling, en een volgend blok dat er zichtbaar op reageert. Bron: https://carpentries.github.io/instructor-training/06-feedback.html (Minute Cards, "Be Explicit About Using Feedback").
Let op: het concept spiegelmoment zelf (computer dicht) is eigen aan deze workshop; de bron onderbouwt alleen het feedbackritme.

**Anonieme feedback op het eind.** Wat: korte vragenlijst met één positieve en één kritische prompt. Waarom: privé en anoniem geeft bruikbaarder feedback dan een publiek bord. Toepassing: QR-code op de laatste slide naar een formulier met "Wat nam je mee?" en "Wat was onduidelijk?". Bron: zelfde pagina, "Minute Cards" en "Surveys".

**Wachttijd en fouten inplannen.** Wat: reken tijd voor storingen mee en kader fouten positief. Waarom: de Carpentries waarschuwen dat installatieproblemen de eerste minuten tot frustratie maken en dat schattingen rekening moeten houden met hoe vaak dingen fout gaan. Toepassing: Codespace vooraf laten starten (prebuild, zie deel 2), een "als het niet werkt"-pad op papier, en de wachttijd van Claude benutten voor een voorspelvraag aan de zaal ("wat verwacht je dat er verschijnt?"). Bron: https://carpentries.github.io/instructor-training/08-motivation.html ("Actual Time", "Helping Learners Learn From Mistakes").

**Fouten van de instructeur zijn een kenmerk.** Wat: toon dat je een mislukte stap herstelt. Waarom: leert het diagnosticeren, wat in leerboeken ontbreekt. Toepassing: de speaker mag een foutieve Claude-uitvoer laten zien en samen beoordelen (past bij "extensie van je eigen inzicht"). Bron: https://carpentries.github.io/instructor-training/17-live.html (voordelen participatory live coding).

**Terugdraaien kan, maar niet alles.** Wat: leg uit dat Claude Code checkpoints bijhoudt van bestandswijzigingen. Waarom: geeft veiligheid om te experimenteren; beperking: wijzigingen via Bash-commando's (rm, mv, cp) worden niet teruggedraaid. Toepassing: één minuut demo van rewind; noem de beperking eerlijk. Bron: https://code.claude.com/docs/en/checkpointing (sectie Limitations).

**Deelnemers houden het resultaat.** Wat: een expliciete laatste stap waarin het dashboard buiten de Codespace komt. Waarom: een Codespace is tijdelijke cloudomgeving (bron beschrijft hem als cloud-development-environment); zonder stap verdwijnt het werk uit beeld. Toepassing: afsluiting met "download je dashboard en het rekenbestand" en dit in de README (zo staat het nu in `bouwen_dashboard` en de README; bewust zonder commit en push, omdat een fork openbaar kan zijn). Bron: https://docs.github.com/en/codespaces/about-codespaces/what-are-codespaces (zie Onzeker voor bewaartermijn).

## 2. Uitstraling en branding

**Eerste indruk: stil openen.** Wat: geen welkomstpagina, tips of release notes. Waarom: niets concurreert met de speaker. Toepassing: staat al goed (`workbench.startupEditor: none`, tips uit, walkthroughs uit, `update.showReleaseNotes: false`). Bron: https://code.visualstudio.com/docs/configure/settings (instellingen zelf te raadplegen in de Settings-editor).

**Gekozen bestanden openen.** Wat: `customizations.codespaces.openFiles` opent bestanden in de webclient, het eerste bestand zichtbaar. Waarom: nu opent niets, de deelnemer ziet een lege editor. Toepassing: `"openFiles": ["README.md"]` of de eerste werkinstructie. Merk op: relatief pad vanaf repo-root, alleen in de VS Code-webclient. Bron: https://docs.github.com/en/codespaces/setting-up-your-project-for-codespaces/configuring-dev-containers/automatically-opening-files-in-the-codespaces-for-a-repository

**Thema bewust kiezen.** Wat: stel `workbench.colorTheme` expliciet in via `settings`. Waarom: geen thema ingesteld laat het gedrag afhangen van het gebruikersprofiel of de OS-voorkeur (`window.autoDetectColorScheme`). Toepassing: kies één thema met voldoende contrast voor beamer; de Carpentries adviseren een grote letter en bij projecteren zwart op wit boven licht op donker. Eigen kleuren: `workbench.colorCustomizations` (per thema of met wildcard). Bronnen: https://code.visualstudio.com/docs/configure/themes ; https://carpentries.github.io/instructor-training/17-live.html (tip 4).

**Instellingsscope begrijpen.** Wat: waarden in `devcontainer.json` `settings` zijn Remote [Codespaces]-scope, `.vscode/settings.json` is Workspace-scope en wint. Waarom: wie een thema wil afdwingen moet de juiste plek kiezen; gebruikersinstellingen (Settings Sync, dotfiles) kunnen een deelnemer eigen voorkeuren geven. Toepassing: zet huisstijlinstellingen in `devcontainer.json`; wil je ze hard afdwingen, in `.vscode/settings.json`. Bronnen: https://docs.github.com/en/codespaces/setting-up-your-project-for-codespaces/adding-a-dev-container-configuration/introduction-to-dev-containers ; https://docs.github.com/en/codespaces/setting-your-user-preferences/personalizing-github-codespaces-for-your-account

**Layout: Claude naast je werk.** Wat: Claude-paneel in de secundaire zijbalk (rechts) of als editor-tab. Waarom: de documentatie noemt de secundaire zijbalk als plek die Claude zichtbaar houdt tijdens het werken; Claude onthoudt de gekozen locatie. Toepassing: kies één layout, test hem in de webclient en leg uit in de README. Het precieze instellingsnaam voor de startlocatie is niet bevestigd (zie Onzeker). Bron: https://code.claude.com/docs/en/vs-code

**Rustige zichtbare UI.** Wat: tuig de UI af met de opties die VS Code documenteert: Zen Mode (`zenMode.*`: verberg activity bar, statusbalk, regelnummers), Customize Layout-knop, positie van meldingen (`workbench.notifications.position`, experimenteel), standaard zichtbaarheid secundaire zijbalk (`workbench.secondarySideBar.defaultVisibility`). Waarom: minder ruis, minder cognitieve belasting. Toepassing: Zen Mode alleen als speaker-demo; voor deelnemers liever een vaste, rustige standaard. Bronnen: https://code.visualstudio.com/docs/configure/custom-layout ; https://code.visualstudio.com/docs/getstarted/userinterface

**Extensies minimaal en bewust.** Wat: alleen wat nodig is (nu `anthropic.claude-code` en `ms-vscode.live-server`). Waarom: elke extensie is een bron van meldingen en verschillen in de web. Let op: sommige extensies werken niet in de webclient (bijvoorbeeld language packs, extensies die een UI/desktop-extension-host nodig hebben). Toepassing: test elke toevoeging in de browser; een Nederlands taalpakket kan dus niet in web-Codespaces. Bron: https://code.visualstudio.com/docs/remote/codespaces (Known limitations)

**Vooraf waarschuwen voor te kleine machine.** Wat: `hostRequirements` (cpus, memory, storage). Waarom: voorkomt dat een deelnemer een te kleine machine kiest. Toepassing: zet een bescheiden minimum; GitHub toont dan alleen passende machinetypes. Bronnen: https://docs.github.com/en/codespaces/setting-up-your-project-for-codespaces/configuring-dev-containers/setting-a-minimum-specification-for-codespace-machines ; https://containers.dev/implementors/json_reference/

**Poort benoemen en stil houden.** Wat: `portsAttributes` met `label` en `onAutoForward`. Waarom: een herkenbare poortnaam in het Ports-paneel in plaats van een kaal nummer; `otherPortsAttributes: silent` staat al. Toepassing: label "Dashboard" op de dashboardpoort; kies `openBrowser` of `openPreview` als de preview direct moet verschijnen. Bronnen: https://containers.dev/implementors/json_reference/ (Port attributes) ; https://docs.github.com/en/codespaces/developing-in-a-codespace/forwarding-ports-in-your-codespace

**Secrets netjes vragen.** Wat: `secrets` in `devcontainer.json` laat Codespaces om specifieke geheimen vragen, met beschrijving en documentatielink. Waarom: de API-sleutel (`ANTHROPIC_FOUNDRY_API_KEY`) wordt nu via `localEnv` doorgegeven; een duidelijke prompt voorkomt een onbegrijpelijke fout. Toepassing: beschrijf in `description` waar de sleutel vandaan komt. Bron: https://docs.github.com/en/codespaces/setting-up-your-project-for-codespaces/configuring-dev-containers/specifying-recommended-secrets-for-a-repository
Let op: of `localEnv` in een Codespace dezelfde waarde oplevert als een Codespaces-secret is niet in deze bronnen bevestigd.

**Snelle start via prebuild.** Wat: GitHub verwijst voor "Prebuilding your codespaces" als aparte pagina. Waarom: kortere wachttijd bij 30 gelijktijdige deelnemers. Toepassing: onderzoeken en voor de workshop vooraf instellen. Bron: https://docs.github.com/en/codespaces/prebuilding-your-codespaces (alleen de verwijzing vanuit de intro is gelezen; inhoud niet geverifieerd).

**Claude Code zelf: eigen touch via instellingen.** Wat: statusregel met model, context en kosten (`statusLine`), output styles, en managed settings die persoonlijke instellingen overrulen (organisatie > project > gebruiker). Waarom: de statusregel maakt context en kosten zichtbaar (transparantie); managed settings zorgen voor identieke gedrag. Toepassing: staat deels al in `managed-settings.json`; overweeg een simpele statusregel. Bronnen: https://code.claude.com/docs/en/statusline ; https://code.claude.com/docs/en/settings ; https://code.claude.com/docs/en/output-styles

**README en huisstijl: één pagina, één pad.** Wat: bovenaan wat je bouwt, wat je nodig hebt, hoe je start, en wat je meeneemt. Waarom: eerste indruk voor wie de repo opent zonder workshop. Toepassing: gebruik dezelfde zinnen als de leerdoelen, één beeld uit `docs/images`, en consistente schrijfwijze (woorden, naam van de workshop). Bron: geen primaire bron gevonden voor een README-norm; dit is eigen oordeel.

**Afsluiting.** Wat: spiegelmoment, wat nemen ze mee, volgende stap, feedbackformulier. Waarom: sluit het leerdoel en de feedbacklus. Toepassing: laatste slide met drie dingen (meenemen, proberen, vragen). Bron: https://carpentries.github.io/instructor-training/06-feedback.html (post-workshop survey).

## Niet gevonden of onzeker

- Of een gebruikersinstelling (Settings Sync, dotfiles) de instellingen uit `devcontainer.json` kan overschrijven, is niet bevestigd; de bron voor de scope-uitleg hierboven noemt dit niet eenduidig. Controleer in een echte Codespace dat het thema en `chat.disableAIFeatures` gelden.
- Instellingsnaam en standaardwaarde voor de startlocatie van het Claude-paneel in de extensie: de pagina beschrijft alleen dat Claude de voorkeurslocatie onthoudt. Niet bevestigd in welke settings-key dat staat.
- Of `window.commandCenter`, `workbench.activityBar.location` en `workbench.layoutControl.enabled` documentatie hebben en werken in de webclient: niet teruggevonden in de opgehaalde pagina's; niet geverifieerd.
- Of Codespaces-secrets via `remoteEnv` `${localEnv:...}` beschikbaar zijn: niet bevestigd.
- Bewaartermijn van een inactieve Codespace en kostenlimiet voor 30 deelnemers: niet gelezen.
- Inhoud van de prebuild-documentatie: alleen de verwijzing gezien.
- Carpentries: het rode/groene stickersysteem voor "ik zit vast" stond niet in de gelezen pagina's. Leerdoelen als ontwerpprincipe is afgeleid uit de episodestructuur, niet uit een gelezen aparte "backward design"-pagina (pagina niet gevonden onder de geprobeerde URL's).
- Wat de Carpentries zeggen over wachttijd bij tools is een afleiding uit "Actual Time"; geen bron over wachten op AI-uitvoer.
- Spiegelmoment (computer dicht) als vorm: geen primaire bron, eigen ontwerp van deze workshop.
- Geen versienummers gecontroleerd, behalve dat Lock Editor Groups een recente Claude Code-versie vereist (de pagina noemt een versie; hier niet overgenomen).
