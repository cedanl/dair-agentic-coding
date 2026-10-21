"""Maakt schets.html: het dashboard in grijs, met de echte groepen en jaren maar zonder getallen.

Gebruik, vanuit de hoofdmap van de repo:

    uv run --no-project --with polars==1.44.2 python .claude/skills/2-schetsen/assets/maak_schets.py \
        --filter vestiging --volgorde groep

Neemt de keuzes over uit mijn-keuzes.json (of uit data-profiel.html) en de teksten uit het casusbestand naast de
data. De pagina komt uit maak_dashboard.py, zodat schets en dashboard er hetzelfde uitzien. Drukt af welke
aanpassingen nog iets nieuws laten zien.
"""

import argparse
import html
import json
import re
import sys
from pathlib import Path

HIER = Path(__file__).resolve().parent
sys.path.insert(0, str(HIER.parents[1] / "3-bouwen/assets"))
import maak_dashboard as dashboard  # noqa: E402


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
        mogelijk += [(f"Vergelijk ook per {label(n)}" + (" (in plaats van het filter erop)" if n in filters else ""),
                      f"--uitsplitsing {','.join([*namen, n])}"
                      + (f" --filter {','.join(f for f in filters if f != n) or 'geen'}" if n in filters else ""),
                      {"uitsplitsing": ",".join([*namen, n]), "filter": ",".join(f for f in filters if f != n) or "geen"})
                     for n in vraag["uitsplitsingen"] if n not in namen]
    mogelijk += [(f"Vergelijk niet meer per {label(n)}", f"--uitsplitsing {','.join(m for m in namen if m != n)}",
                  {"uitsplitsing": ",".join(m for m in namen if m != n)})
                 for n in namen if len(namen) > 1 and n != vraag.get("kern")]
    if len(filters) < MAX_FILTERS:
        mogelijk += [(f"Filter ook op {label(f)}", f"--filter {','.join([*filters, f])}", {"filter": ",".join([*filters, f])})
                     for f in dict.fromkeys([*casus["filters"], *casus["uitsplitsingen"]])
                     if f not in filters and f not in namen]
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
    if not filters and gevraagd == "standaard":  # alleen als er nog nooit een filter is gekozen
        filters = [f for f in casus["filters"] if f not in namen][:1]
    filter_naam = ",".join(filters) or "geen"
    keuzes.update(uitsplitsing=",".join(namen), filter=filter_naam, volgorde=volgorde, titel=titel)
    keuzes["gezien"] = list(dict.fromkeys([*keuzes.get("gezien", []), bepaal_stand(keuzes)]))

    # Dezelfde pagina als het dashboard, met de echte groepen en jaren maar zonder getallen
    csv = Path(keuzes["csv"])
    try:
        ins = dashboard.stel_in(keuzes, casus)
        pagina = dashboard.maak_html(dashboard.lees_data(csv, ins), csv, {**ins, "schets": True}, meta=keuzes)
    except dashboard.Melding as melding:
        sys.exit(f"Niet gelukt: {melding}")
    args.uit.write_text(pagina, encoding="utf-8")
    views = [vraag["titel_jaar"], vraag["titel_groep"].format(uitsplitsing=label)]
    if volgorde == "groep":
        views.reverse()
    filter_label = " en ".join(casus["uitsplitsingen"][f]["label"] for f in filters) or "geen"
    vergelijken = " of ".join(casus["uitsplitsingen"][n]["label"] for n in namen)
    if len(namen) > 1:
        vergelijken += " (wissel met één klik in het dashboard)"
    if args.keuzes.is_file():
        schrijf_mijn_keuzes(args.keuzes, keuzes)
    print(f"Geschreven: {args.uit}")
    print(f"Titel: {titel or vraag['vraag']}  View 1: {views[0]}  View 2: {views[1]}  "
          f"Vergelijken: {vergelijken}  Filter: {filter_label}")
    for regel in let_op:
        print(f"Let op: {regel}")
    toon_aanpassingen(keuzes, casus, vraag)


if __name__ == "__main__":
    main()
