"""Maakt schets.html: de views van het dashboard op papier, zonder data en zonder getallen.

Gebruik, vanuit de hoofdmap van de repo:

    python .claude/skills/schets_dashboard/assets/maak_schets.py --filter vestiging --volgorde groep

Neemt de vraag en de uitsplitsing over uit data-profiel.html en de teksten uit het casusbestand naast de data.
Alleen de standaardbibliotheek: draait zonder installatie.
"""

import argparse
import html
import json
import re
import string
import sys
from pathlib import Path

HIER = Path(__file__).resolve().parent
e = html.escape

# Plaatjes met vormen van gelijke lengte: een verschil in lengte zou lezen als een uitkomst
STAAF = ('<svg viewBox="0 0 300 120" role="img" aria-label="Schets van een horizontaal staafdiagram">'
         + "".join(f'<text x="0" y="{12 + i * 28}">{e(label)}</text><rect class="vorm" x="0" y="{16 + i * 28}" width="260" height="8" rx="4"/>'
                   for i, label in enumerate(["groep", "groep", "groep", "groep"]))
         + "</svg>")
LIJN = ('<svg viewBox="0 0 300 120" role="img" aria-label="Schets van een lijndiagram">'
        '<line class="as" x1="20" x2="296" y1="100" y2="100"/><line class="as" x1="20" x2="20" y1="8" y2="100"/>'
        '<polyline class="lijn" points="30,54 90,54 150,54 210,54 290,54"/>'
        '<text x="24" y="116">eerste jaar</text><text x="230" y="116">laatste jaar</text></svg>')


def lees_keuzes(pad: Path) -> dict:
    if not pad.is_file():
        sys.exit(f"{pad} niet gevonden. Draai eerst /1-verkennen.")
    gevonden = re.search(r'<meta name="keuzes" content="([^"]*)"', pad.read_text(encoding="utf-8"))
    if not gevonden:
        sys.exit(f"{pad} bevat geen keuzes. Draai /1-verkennen opnieuw.")
    return json.loads(html.unescape(gevonden.group(1)))


def main() -> None:
    parser = argparse.ArgumentParser(description="Maakt schets.html uit de keuzes in data-profiel.html.")
    parser.add_argument("--vanaf", type=Path, default=Path("data-profiel.html"))
    parser.add_argument("--filter", default="standaard", help="bijvoorbeeld vestiging, geslacht of geen")
    parser.add_argument("--volgorde", choices=["groep", "jaar"], default="groep", help="welke view bovenaan staat")
    parser.add_argument("--uit", type=Path, default=Path("schets.html"))
    args = parser.parse_args()

    keuzes = lees_keuzes(args.vanaf)
    casus = json.loads(Path(keuzes["csv"]).with_suffix(".casus.json").read_text(encoding="utf-8"))
    vraag = casus["vragen"][keuzes["vraag"]]
    naam = keuzes["uitsplitsing"]
    label = casus["uitsplitsingen"][naam]["label"]
    filter_naam = args.filter
    if filter_naam not in casus["uitsplitsingen"] and filter_naam != "geen" or filter_naam == naam:
        filter_naam = next(f for f in casus["filters"] if f != naam)
    maat = casus["maten"][vraag["maat"]]
    keuzes.update(filter=filter_naam, volgorde=args.volgorde)

    groep = (vraag["titel_groep"].format(uitsplitsing=label), vraag["uitleg_groep"].format(uitsplitsing=label),
             f"Horizontaal staafdiagram, van hoog naar laag (vergelijken, lange labels)", STAAF,
             f"Groepen met minder dan {casus['drempels']['groep']} {casus['eenheid']}.")
    jaar = (vraag["titel_jaar"], vraag["uitleg_jaar"], "Lijn (ontwikkeling in de tijd)", LIJN,
            maat["definities"][-1][1])
    views = [jaar, groep] if args.volgorde == "jaar" else [groep, jaar]
    views_html = "".join(
        f'<section class="view"><h3><span class="nr">{i}</span>{e(titel)}</h3>'
        f"<figure>{plaatje}<figcaption>Schets, geen data</figcaption></figure>"
        f"<dl><dt>Wat je ziet</dt><dd>{e(uitleg)}</dd><dt>Grafiek</dt><dd>{e(soort)}</dd>"
        f"<dt>Valt weg</dt><dd>{e(weg)}</dd></dl></section>"
        for i, (titel, uitleg, soort, plaatje, weg) in enumerate(views, 1))
    filter_label = casus["uitsplitsingen"][filter_naam]["label"] if filter_naam != "geen" else "geen"
    rijen = [("Vraag", vraag["vraag"]), ("Uitgesplitst naar", label), ("Filter", filter_label),
             ("Bovenaan", "vergelijken tussen groepen" if args.volgorde == "groep" else "ontwikkeling over de jaren"),
             (maat["definities"][0][0], maat["definities"][0][1]),
             ("Kerncijfer", vraag["kerncijfer"])]
    niet = [*maat["niet_zeggen"], "Waarom groepen verschillen: een verschil is geen oorzaak."]
    if casus.get("demo"):
        niet.append("Iets over de werkelijkheid: dit is demodata.")

    sjabloon = string.Template((HIER / "schets-sjabloon.html").read_text(encoding="utf-8"))
    args.uit.write_text(sjabloon.substitute(
        keuzes=e(json.dumps(keuzes, ensure_ascii=False)), vraag=e(vraag["vraag"]), ondertitel=e(casus["ondertitel"]),
        demo='<p class="demo">Dit is demodata</p>' if casus.get("demo") else "", views=views_html,
        keuzes_tabel="".join(f"<tr><td>{e(a)}</td><td>{e(b)}</td></tr>" for a, b in rijen),
        niet="".join(f"<li>{e(n)}</li>" for n in niet),
    ), encoding="utf-8")
    print(f"Geschreven: {args.uit}")
    print(f"View 1: {views[0][0]}  View 2: {views[1][0]}  Filter: {filter_label}")


if __name__ == "__main__":
    main()
