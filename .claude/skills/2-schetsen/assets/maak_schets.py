"""Maakt schets.html: de views van het dashboard op papier, zonder data en zonder getallen.

Gebruik, vanuit de hoofdmap van de repo:

    python .claude/skills/2-schetsen/assets/maak_schets.py --filter vestiging --volgorde groep
    python .claude/skills/2-schetsen/assets/maak_schets.py --vanaf schets.html --filter geen   (schets aanpassen)

Neemt de vraag en de uitsplitsing over uit data-profiel.html (of uit een eerdere schets) en de teksten uit het
casusbestand naast de data. Drukt af welke aanpassingen nog iets nieuws laten zien.
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


MAX_VERGELIJKINGEN, MAX_FILTERS = 3, 2


def bepaal_stand(keuzes: dict) -> str:
    """Welke vergelijkingen, filters en volgorde de schets toont; zo bieden we nooit een eerdere stand opnieuw aan."""
    return f"{keuzes['uitsplitsing']}|{keuzes['filter']}|{keuzes['volgorde']}"


def toon_aanpassingen(keuzes: dict, casus: dict, vraag: dict) -> None:
    namen, filters = keuzes["uitsplitsing"].split(","), [f for f in keuzes["filter"].split(",") if f != "geen"]
    label = lambda n: casus["uitsplitsingen"][n]["label"]  # noqa: E731
    mogelijk = []
    if len(namen) < MAX_VERGELIJKINGEN:
        mogelijk += [(f"Vergelijk ook per {label(n)}", f"--uitsplitsing {','.join([*namen, n])}",
                      {"uitsplitsing": ",".join([*namen, n]), "filter": ",".join(f for f in filters if f != n) or "geen"})
                     for n in vraag["uitsplitsingen"] if n not in namen]
    mogelijk += [(f"Vergelijk niet meer per {label(n)}", f"--uitsplitsing {','.join(m for m in namen if m != n)}",
                  {"uitsplitsing": ",".join(m for m in namen if m != n)})
                 for n in namen if len(namen) > 1 and n != vraag.get("kern")]
    if len(filters) < MAX_FILTERS:
        mogelijk += [(f"Filter ook op {label(f)}", f"--filter {','.join([*filters, f])}", {"filter": ",".join([*filters, f])})
                     for f in casus["filters"] if f not in filters and f not in namen]
    mogelijk += [(f"Haal het filter op {label(f)} weg", f"--filter {','.join(g for g in filters if g != f) or 'geen'}",
                  {"filter": ",".join(g for g in filters if g != f) or "geen"}) for f in filters]
    andere = "jaar" if keuzes["volgorde"] == "groep" else "groep"
    mogelijk.append(("Zet de ontwikkeling over de jaren bovenaan" if andere == "jaar" else
                     "Zet de vergelijking tussen groepen bovenaan", f"--volgorde {andere}", {"volgorde": andere}))
    nieuw = [(t, x) for t, x, stand in mogelijk if bepaal_stand({**keuzes, **stand}) not in keuzes["gezien"]]
    print("Aanpassen (label => extra argumenten bij --vanaf schets.html; een eigen titel met --titel \"...\"):")
    for t, x in nieuw:
        print(f"- {t} => {x}")
    if not nieuw:
        print("Geen nieuwe vaste aanpassingen meer: alles is al eens getoond.")


def lees_mijn_keuzes(pad: Path) -> dict | None:
    """mijn-keuzes.json is de waarheid; zonder dat bestand nemen we de keuzes over uit het profiel (of --vanaf)."""
    if not pad.is_file():
        return None
    mijn = json.loads(pad.read_text(encoding="utf-8"))
    k = mijn["keuzes"]
    return {"csv": mijn["csv"], "vraag": k["vraag"], "uitsplitsing": k["vergelijken"], "filter": k.get("filter"),
            "volgorde": k.get("bovenaan"), "titel": k.get("titel", ""), "gezien": mijn.get("gezien", [])}


def schrijf_mijn_keuzes(pad: Path, keuzes: dict) -> None:
    """Schrijft terug wat de schets echt laat zien, zodat schets en mijn-keuzes.json altijd gelijk zijn."""
    mijn = json.loads(pad.read_text(encoding="utf-8"))
    mijn["keuzes"].update(vergelijken=keuzes["uitsplitsing"], filter=keuzes["filter"], bovenaan=keuzes["volgorde"],
                          titel=keuzes["titel"])
    mijn["gezien"] = keuzes["gezien"]
    pad.write_text(json.dumps(mijn, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Maakt schets.html uit mijn-keuzes.json (of uit data-profiel.html).")
    parser.add_argument("--keuzes", type=Path, default=Path("mijn-keuzes.json"),
                        help="het bestand met de keuzes; de schets schrijft hier terug wat hij laat zien")
    parser.add_argument("--vanaf", type=Path, default=Path("data-profiel.html"), help="alleen als er geen --keuzes is")
    parser.add_argument("--uitsplitsing", help="vergelijkingen, bijvoorbeeld sector of sector,opleiding")
    parser.add_argument("--filter", help="bijvoorbeeld vestiging, geslacht, vestiging,geslacht of geen")
    parser.add_argument("--volgorde", choices=["groep", "jaar"], help="welke view bovenaan staat")
    parser.add_argument("--titel", help="een eigen titel; 'standaard' zet de vraag terug als titel")
    parser.add_argument("--uit", type=Path, default=Path("schets.html"))
    args = parser.parse_args()

    keuzes = lees_mijn_keuzes(args.keuzes) or lees_keuzes(args.vanaf)
    casus = json.loads(Path(keuzes["csv"]).with_suffix(".casus.json").read_text(encoding="utf-8"))
    vraag = casus["vragen"][keuzes["vraag"]]
    namen = list(dict.fromkeys(n.strip() for n in (args.uitsplitsing or keuzes["uitsplitsing"]).split(",") if n.strip()))
    onbekend = [n for n in namen if n not in casus["uitsplitsingen"]]
    if onbekend:
        sys.exit(f"Onbekende uitsplitsing: {', '.join(onbekend)}. Kies uit: {', '.join(casus['uitsplitsingen'])}")
    # Gaat de vraag over één vergelijking (zoals vooropleiding bij C), dan staat die er altijd bij, vooraan
    let_op = []  # wat het script anders doet dan gevraagd; Claude zegt dit eerlijk tegen de deelnemer
    if vraag.get("kern"):
        if vraag["kern"] not in namen:
            let_op.append(f"{vraag['kern']} staat er altijd bij, want daar gaat de vraag over.")
        namen = [vraag["kern"], *(n for n in namen if n != vraag["kern"])]
    if len(namen) > MAX_VERGELIJKINGEN:
        sys.exit(f"Kies hooguit {MAX_VERGELIJKINGEN} vergelijkingen; meer past niet overzichtelijk in één dashboard.")
    label = casus["uitsplitsingen"][namen[0]]["label"]
    gevraagd = args.filter or keuzes.get("filter") or "standaard"
    volgorde = args.volgorde or keuzes.get("volgorde") or "groep"
    titel = keuzes.get("titel", "") if args.titel is None else ("" if args.titel == "standaard" else args.titel.strip())
    # Hooguit twee filters, nooit op iets waarop je al vergelijkt; geen geldig filter gekozen: het eerste uit de casus
    filters = []
    for f in [] if gevraagd == "geen" else [f.strip() for f in dict.fromkeys(gevraagd.split(",")) if f.strip()]:
        if f == "standaard":
            continue
        if f not in casus["uitsplitsingen"]:
            let_op.append(f"{f} bestaat niet als filter; het valt weg.")
        elif f in namen:
            let_op.append(f"{f} is al een vergelijking en kan niet ook een filter zijn; het filter valt weg.")
        elif len(filters) == MAX_FILTERS:
            let_op.append(f"Hooguit {MAX_FILTERS} filters; {f} valt weg.")
        else:
            filters.append(f)
    if not filters and gevraagd != "geen":
        filters = [f for f in casus["filters"] if f not in namen][:1]
    filter_naam = ",".join(filters) or "geen"
    maat = casus["maten"][vraag["maat"]]
    keuzes.update(uitsplitsing=",".join(namen), filter=filter_naam, volgorde=volgorde, titel=titel)
    keuzes["gezien"] = list(dict.fromkeys([*keuzes.get("gezien", []), bepaal_stand(keuzes)]))

    groep = (vraag["titel_groep"].format(uitsplitsing=label), vraag["uitleg_groep"].format(uitsplitsing=label),
             f"Horizontaal staafdiagram, van hoog naar laag (vergelijken, lange labels)", STAAF,
             f"Groepen met minder dan {casus['drempels']['groep']} {casus['eenheid']}.")
    jaar = (vraag["titel_jaar"], vraag["uitleg_jaar"], "Lijn (ontwikkeling in de tijd)", LIJN,
            maat["definities"][-1][1])
    views = [jaar, groep] if volgorde == "jaar" else [groep, jaar]
    views_html = "".join(
        f'<section class="view"><h3><span class="nr">{i}</span>{e(titel)}</h3>'
        f"<figure>{plaatje}<figcaption>Schets, geen data</figcaption></figure>"
        f"<dl><dt>Wat je ziet</dt><dd>{e(uitleg)}</dd><dt>Grafiek</dt><dd>{e(soort)}</dd>"
        f"<dt>Valt weg</dt><dd>{e(weg)}</dd></dl></section>"
        for i, (titel, uitleg, soort, plaatje, weg) in enumerate(views, 1))
    filter_label = " en ".join(casus["uitsplitsingen"][f]["label"] for f in filters) or "geen"
    vergelijken = " of ".join(casus["uitsplitsingen"][n]["label"] for n in namen)
    if len(namen) > 1:
        vergelijken += " (wissel met één klik in het dashboard)"
    rijen = [("Titel", titel or vraag["vraag"]), ("Vraag", vraag["vraag"]), ("Uitgesplitst naar", vergelijken),
             ("Filter", filter_label),
             ("Bovenaan", "vergelijken tussen groepen" if volgorde == "groep" else "ontwikkeling over de jaren"),
             (maat["definities"][0][0], maat["definities"][0][1]),
             ("Kerncijfer", vraag["kerncijfer"])]
    niet = [*maat["niet_zeggen"], "Waarom groepen verschillen: een verschil is geen oorzaak."]
    if casus.get("demo"):
        niet.append("Iets over de werkelijkheid: dit is demodata.")

    sjabloon = string.Template((HIER / "schets-sjabloon.html").read_text(encoding="utf-8"))
    args.uit.write_text(sjabloon.substitute(
        keuzes=e(json.dumps(keuzes, ensure_ascii=False)), vraag=e(titel or vraag["vraag"]), ondertitel=e(casus["ondertitel"]),
        demo='<p class="demo">Dit is demodata</p>' if casus.get("demo") else "", views=views_html,
        keuzes_tabel="".join(f"<tr><td>{e(a)}</td><td>{e(b)}</td></tr>" for a, b in rijen),
        niet="".join(f"<li>{e(n)}</li>" for n in niet),
    ), encoding="utf-8")
    if args.keuzes.is_file():
        schrijf_mijn_keuzes(args.keuzes, keuzes)
    print(f"Geschreven: {args.uit}")
    print(f"Titel: {titel or vraag['vraag']}  View 1: {views[0][0]}  View 2: {views[1][0]}  "
          f"Vergelijken: {vergelijken}  Filter: {filter_label}")
    for regel in let_op:
        print(f"Let op: {regel}")
    toon_aanpassingen(keuzes, casus, vraag)


if __name__ == "__main__":
    main()
