# TRIPS-beslisboom — volledig

Bron: TRIPS-beslismodel "Welke grafiek wanneer". Letterlijk getranscribeerd uit het originele
schema en bevestigd tegen de bron (incl. de twee eerder dubbelzinnige pijlen, zie onderaan).

## Kadervragen (altijd eerst, kort)

1. **Welk verhaal wil je vertellen?**
2. **Aan wie vertel je het?**
3. **Met welk doel?**

Deze drie sturen de toon en detaillering, niet direct de grafieksoort. Neem ze mee in de afweging.

## De boom

```
4. Wil je één enkel getal inzien?
├─ JA → 4.a Wil je dit zien in de context van maxima en normen?
│        ├─ JA  → ENKEL GETAL GESCHAALD (gauge/bullet)
│        └─ NEE → ENKEL GETAL (groot kengetal, bv. "72%")
│
└─ NEE → 5. Wil je weten hoe data deel zijn van een geheel?
         ├─ JA → 5.a Wil je data uit slechts één periode bekijken?
         │        ├─ JA  → CIRKELDIAGRAM
         │        └─ NEE → 5.b Gaat het over tijd of categorieën?
         │                 ├─ CATEGORIEËN → 5.c Wil je het procentuele aandeel van elk deel weten?
         │                 │                 ├─ JA  → 100% GESTAPELDE STAAFDIAGRAM (horizontaal)
         │                 │                 └─ NEE → GESTAPELDE STAAFDIAGRAM (horizontaal)
         │                 └─ TIJD        → 5.c Wil je het procentuele aandeel van elk deel weten?
         │                                   ├─ JA  → 100% GESTAPELDE KOLOMDIAGRAM (verticaal)
         │                                   └─ NEE → GESTAPELDE KOLOMDIAGRAM (verticaal)
         │
         └─ NEE → 6. Ben je op zoek naar een trend in tijd?
                  ├─ JA  → LIJNDIAGRAM
                  └─ NEE → 7. Wil je meerdere databronnen vergelijken?
                           ├─ JA  → KOLOMDIAGRAM / STAAFDIAGRAM   (zie ⚠ hieronder)
                           └─ NEE → 8. Wil je weten in hoeverre data aan elkaar gerelateerd zijn?
                                    ├─ JA  → CORRELATIE-ANALYSE (scatter)
                                    └─ NEE → LIJST / TABEL WEERGAVE
```

## Conventie kolom vs. staaf

Door de hele boom geldt:
- **Kolomdiagram = verticaal** — gebruikt waar de x-as een **tijd**- of natuurlijke volgorde heeft.
- **Staafdiagram = horizontaal** — gebruikt voor **categorieën**, zeker bij veel of lange labels.

Bij vraag 7 (vergelijken): kies **kolom** als er een tijd-/ordeningsas is, anders **staaf**
(horizontaal leest prettiger bij veel of lange categorienamen).

## Bevestigd tegen de bron

1. **Vraag 6 "Ja"** → **Lijndiagram** (trend in tijd → lijn).
2. **Vraag 7 "Ja"** → **Kolomdiagram óf Staafdiagram** als twee gelijkwaardige opties; kies via de
   kolom/staaf-conventie hierboven (tijd/ordening → kolom, anders → staaf) en benoem de keuze.
