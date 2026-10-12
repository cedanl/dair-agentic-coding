# vormgever-npuls-huisstijl

Doe-skill die de Npuls huisstijl toepast op digitale uitingen (webapps, dashboards, componenten, landingspagina's, posters, social posts) en werkende HTML/CSS/React oplevert — of bestaande code restylet.

## Structuur

```
vormgever-npuls-huisstijl/
├── SKILL.md                        # Werkwijze + restricties
├── README.md                       # Dit bestand
├── references/
│   ├── design-tokens.json          # Bron van waarheid: kleuren, combinaties, typografie,
│   │                               #   iconen, vormen, spacing/radii/shadows, neutrals,
│   │                               #   feedback_colors, data_visualization, css_variables
│   └── merkcontext.md              # Logo, vormentaal, fotografie, licentie
└── assets/
    ├── shapes/                     # De vijf kernvormen als SVG
    ├── logos/                      # Indicatief beeldmerk (licht + donker)
    └── illustrations/              # Voorbeeld-illustraties in de vlakke Npuls-stijl
```

## Hoe Claude het gebruikt

1. Bepaal het type uiting → alleen `design-tokens.json` (functionele UI) of ook `merkcontext.md` (logo/vormentaal/fotografie prominent).
2. Kies ≥3 primaire kleuren; check elk achtergrond-voorgrond paar tegen `allowed_combinations`.
3. Typografie, iconen, vormentaal, fotografie volgens de tokens; hergebruik `assets/`.
4. Bouw vanaf het `css_variables`-blok; grafieken/status via `data_visualization` en `feedback_colors`.

## Verhouding tot andere skills

| Skill | Rol |
|-------|-----|
| **vormgever-npuls-huisstijl** (deze) | HTML/CSS/React-uitingen in Npuls-stijl; canonieke `design-tokens.json` |
| `npuls-huisstijl` | Framework-thema's (Slidev, Streamlit, R Shiny) + PowerPoint-template |
| `clidev` | Volledige Slidev-presentatieworkflow |
| `ontwerper-digitaal-product` / `ui-designer` | Product- en interactieontwerp (de "V" in ISGVO) |

Houd de tokens hier canoniek — niet dupliceren in andere skills.

## Bijwerken

1. Wijzig eerst `references/design-tokens.json` (bron van waarheid).
2. Pas `SKILL.md` aan als er nieuwe regels bij komen.
3. Nieuwe SVG's in `assets/<map>/`, met kleuren uit de tokens.
4. Commit + push naar `cedanl/.github`.

## Licentie

Npuls-materialen: CC BY-SA 4.0. Logo's en merkidentiteitselementen uitgezonderd — niet wijzigen zonder expliciete toestemming.
