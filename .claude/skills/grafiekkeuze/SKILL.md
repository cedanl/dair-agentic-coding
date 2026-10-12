---
name: grafiekkeuze
description: Use when choosing/recommending a chart or graph type to present data, or generating chart code. Triggers like "welke grafiek/diagram", "hoe visualiseer/presenteer ik deze data", "maak een grafiek/visualisatie voor", "is dit de juiste grafiek", "what chart should I use", "how to visualize this data". NL + EN.
---

# Grafiekkeuze (TRIPS-beslisboom)

## Overzicht

Kies precies één grafieksoort via de TRIPS-beslisboom en lever werkende **Plotly**-code.
Kernprincipe: de juiste grafiek volgt uit **verhaal + publiek + doel + datastructuur** — niet uit gewoonte.

Bron van het beslismodel: TRIPS. Vermeld dat kort bij het advies.

## Werkwijze

1. **Kader (TRIPS 1–3):** weeg kort mee — welk *verhaal* vertel je, aan *wie*, met welk *doel*.
2. **Afleiden:** bepaal zoveel mogelijk uit de datastructuur en het verzoek (zie `beslisboom.md`).
3. **Gericht doorvragen:** stel alléén de 1–2 vragen die nú nog beslissend zijn. Loop de boom niet volledig met de gebruiker door.
4. **Kies + verantwoord:** noem de grafieksoort + het pad door de boom in één regel
   (bv. *"geen enkel getal → deel van geheel → over tijd → procentueel aandeel → 100% gestapelde kolomdiagram"*).
5. **Code:** detecteer de stack en lever Plotly:
   - frontend (HTML/CSS/JS) → `plotly.js`-snippet — zie `templates/plotly-js.md`
   - Python (notebook / Streamlit / FastAPI) → `plotly.py` — zie `templates/plotly-py.md`
   - Vul de échte data in waar bekend; anders duidelijk gemarkeerde placeholders.
   - Standaard een snippet in de chat; schrijf alléén naar een bestand als de gebruiker daarom vraagt.
   - Noem Chart.js/andere libraries alleen als de gebruiker er expliciet om vraagt.

## Beslisboom — uitkomsten in één oogopslag

| Uitkomst | Wanneer | Plotly-type |
|---|---|---|
| Enkel getal | één getal, géén norm/maximum-context | `indicator` (number) |
| Enkel getal geschaald | één getal t.o.v. norm/maximum | `indicator` (gauge/bullet) |
| Cirkeldiagram | deel-van-geheel, **één** periode | `pie` |
| Lijndiagram | trend in de tijd | `scatter` mode lines |
| Kolomdiagram (verticaal) | vergelijken, ordening op tijd-/getalas | `bar` |
| Staafdiagram (horizontaal) | vergelijken, veel/lange categorielabels | `bar` `orientation:'h'` |
| Gestapelde staafdiagram | deel-van-geheel over **categorieën**, absoluut | `bar` h + `barmode:'stack'` |
| 100% gestapelde staafdiagram | deel-van-geheel over **categorieën**, % aandeel | h + `barmode:'stack'`, genormaliseerd |
| Gestapelde kolomdiagram | deel-van-geheel over **tijd**, absoluut | `bar` v + `barmode:'stack'` |
| 100% gestapelde kolomdiagram | deel-van-geheel over **tijd**, % aandeel | v + `barmode:'stack'`, genormaliseerd |
| Correlatie-analyse | samenhang tussen variabelen | `scatter` mode markers |
| Lijst/tabel | exacte waarden opzoeken, geen visueel patroon | `table` |

Volledige boom met alle ja/nee-paden: zie `beslisboom.md`.

## Veelgemaakte fouten

- **Tijd vs. categorie door elkaar bij gestapeld/vergelijken:** over **tijd** → **kolom**diagram (verticaal, tijd op x-as); over **categorieën** → **staaf**diagram (horizontaal). Een generieke keuze pakt vaak ten onrechte een staaf voor een tijdreeks.
- **Hele boom uitvragen** i.p.v. afleiden uit de data en alleen het beslissende restant vragen.
- **Cirkeldiagram voor meerdere periodes** — cirkel is alléén voor deel-van-geheel in één periode.
- **Te veel categorieën in cirkel/gestapeld** — bij >5–7 delen wordt het onleesbaar; overweeg staaf of tabel.
- **Een derde dimensie in één grafiek persen** — een (gestapelde) grafiek toont twee dimensies (bv. cohort × vooropleiding). Komt er een extra groepering bij (bv. per opleiding), maak dan een **facet**: één grafiek per groep, niet alles in één.
- **Default naar Chart.js** terwijl de rode draad Plotly is.
