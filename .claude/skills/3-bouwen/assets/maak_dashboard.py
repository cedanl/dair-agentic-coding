"""Maakt het dashboard als één HTML-bestand. Draait zonder AI, ook op andere data.

Gebruik, vanuit de hoofdmap van de repo:

    python .claude/skills/3-bouwen/assets/maak_dashboard.py --vanaf schets.html
    python .claude/skills/3-bouwen/assets/maak_dashboard.py data/eigen.csv --vraag A \\
        --uitsplitsing sector --filter vestiging

De vraag, de definities en de teksten komen uit het casusbestand naast de data (data/x.csv -> data/x.casus.json).
De berekeningen staan in berekeningen.py, naast dit script, en zijn getest: tel eerstejaars, en per eerstejaars of
die het jaar erna gestopt is of binnen een termijn een diploma haalde. Het dashboard krijgt een kopie mee als
dashboard-berekeningen.py, zodat de deelnemer ziet wat er is gerekend. De privacydrempels worden toegepast voordat er iets in het bestand
komt: in het dashboard staan alleen uitkomsten per groep, nooit rijen.
"""

from __future__ import annotations

import argparse
import base64
import datetime
import html
import itertools
import json
import math
import re
import shutil
import string
import sys
import time
from pathlib import Path

import polars as pl

from berekeningen import bereken_eerstejaars, pas_drempels_toe, tel

HIER = Path(__file__).resolve().parent
e = html.escape
MAX_VERGELIJKINGEN, MAX_FILTERS = 3, 2
MAANDEN = ["januari", "februari", "maart", "april", "mei", "juni", "juli", "augustus", "september",
           "oktober", "november", "december"]


class Melding(Exception):
    """Een fout die de gebruiker kan oplossen: één zin, geen traceback."""


# ── Keuzes en casus ─────────────────────────────────────────────────────────


def lees_keuzes(pad: Path) -> dict:
    """Leest de keuzes die schets.html of data-profiel.html in een meta-tag meedraagt."""
    if not pad.is_file():
        raise Melding(f"{pad} niet gevonden. Maak het eerst met de vorige skill.")
    gevonden = re.search(r'<meta name="keuzes" content="([^"]*)"', pad.read_text(encoding="utf-8"))
    if not gevonden:
        raise Melding(f"{pad.name} bevat geen keuzes. Maak het opnieuw met de skill.")
    return json.loads(html.unescape(gevonden.group(1)))


def lees_mijn_keuzes(pad: Path) -> dict:
    """mijn-keuzes.json is de waarheid. De schets moet precies hetzelfde zeggen, anders bouwen we niet."""
    mijn = json.loads(pad.read_text(encoding="utf-8"))
    k = mijn["keuzes"]
    keuzes = {"csv": mijn["csv"], "vraag": k.get("vraag"), "uitsplitsing": k.get("vergelijken"),
              "filter": k.get("filter"), "volgorde": k.get("bovenaan"), "titel": k.get("titel", "")}
    schets = pad.with_name("schets.html")
    if schets.is_file():
        getekend = lees_keuzes(schets)
        anders = [veld for veld in ("vraag", "uitsplitsing", "filter", "volgorde", "titel")
                  if (getekend.get(veld) or "") != (keuzes.get(veld) or "")]
        if anders:
            raise Melding(f"je schets en je keuzes zijn niet meer gelijk ({', '.join(anders)}). "
                          "Typ /2-schetsen om de schets bij te werken, dan bouw ik daarna precies die schets.")
    return keuzes


def bepaal_keuzes(args: argparse.Namespace) -> dict:
    keuzes: dict = {}
    mijn = Path("mijn-keuzes.json")
    vanaf = args.vanaf or (mijn if not args.csv and mijn.is_file() else
                           Path("schets.html") if not args.csv and Path("schets.html").is_file() else None)
    if vanaf and Path(vanaf).suffix == ".json":
        keuzes = lees_mijn_keuzes(Path(vanaf))
    elif vanaf:
        keuzes = lees_keuzes(Path(vanaf))
    for naam in ("csv", "vraag", "uitsplitsing", "filter", "volgorde", "titel"):
        if getattr(args, naam):
            keuzes[naam] = str(getattr(args, naam))
    if not keuzes.get("csv"):
        raise Melding("Geef het databestand of --vanaf schets.html.\n"
                      "Gebruik: python maak_dashboard.py <pad-naar-csv> --vraag A --uitsplitsing sector")
    return keuzes


def lees_casus(csv: Path) -> dict:
    pad = csv.with_suffix(".casus.json")
    if not pad.is_file():
        raise Melding(f"Geen casusbestand gevonden naast de data: {pad}")
    return json.loads(pad.read_text(encoding="utf-8"))


def bepaal_stand(keuzes: dict) -> str:
    """Welke vergelijking en welke volgorde het dashboard toont; zo bieden we nooit een eerdere stand opnieuw aan."""
    return f"{keuzes['uitsplitsing']}|{keuzes.get('volgorde') or 'groep'}"


def stel_in(keuzes: dict, casus: dict) -> dict:
    """Zet de keuzes en de casus om in één instelling voor de rest van het script."""
    vraag = casus["vragen"].get(keuzes.get("vraag", "A"))
    if vraag is None:
        raise Melding(f"Onbekende vraag '{keuzes.get('vraag')}'. Kies uit: {', '.join(casus['vragen'])}")
    # Meer vergelijkingen en filters mogen, met komma's: "sector,opleiding". De eerste vergelijking staat vooraan.
    namen = list(dict.fromkeys(n.strip() for n in str(keuzes.get("uitsplitsing") or vraag["uitsplitsingen"][0]).split(",")
                               if n.strip()))
    # Gaat de vraag over één vergelijking (zoals vooropleiding bij C), dan staat die er altijd bij, vooraan
    if vraag.get("kern"):
        namen = [vraag["kern"], *(n for n in namen if n != vraag["kern"])]
    onbekend = [n for n in namen if n not in casus["uitsplitsingen"]]
    if onbekend:
        raise Melding(f"Onbekende uitsplitsing '{', '.join(onbekend)}'. Kies uit: {', '.join(casus['uitsplitsingen'])}")
    if len(namen) > MAX_VERGELIJKINGEN:
        bij = f" ({vraag['kern']} hoort altijd bij deze vraag)" if vraag.get("kern") else ""
        raise Melding(f"Kies hooguit {MAX_VERGELIJKINGEN} vergelijkingen{bij}; meer past niet overzichtelijk in één dashboard.")
    gevraagd = str(keuzes.get("filter") or "standaard")
    filter_namen = [] if gevraagd == "geen" else [
        f for f in dict.fromkeys(gevraagd.split(",")) if f in casus["uitsplitsingen"] and f not in namen]
    if not filter_namen and gevraagd != "geen":
        filter_namen = [f for f in casus["filters"] if f not in namen][:1]
    if len(filter_namen) > MAX_FILTERS:
        raise Melding(f"Kies hooguit {MAX_FILTERS} filters; meer past niet overzichtelijk in één dashboard.")
    uitsplitsingen = [(n, casus["uitsplitsingen"][n]) for n in namen]
    filters = [casus["uitsplitsingen"][f] for f in filter_namen]
    maat = casus["maten"][vraag["maat"]]
    k = casus["kolommen"]
    kolommen = [k["persoon"], k["jaar"], k["start"], *(u["kolom"] for _, u in uitsplitsingen)]
    if maat["soort"] == "diploma":
        kolommen.append(k["diplomajaar"])
    kolommen += [f["kolom"] for f in filters]
    groep_views = {n: {"soort": "staaf", "per": "groep",
                       "titel": vraag["titel_groep"].format(uitsplitsing=u["label"]),
                       "uitleg": vraag["uitleg_groep"].format(uitsplitsing=u["label"])} for n, u in uitsplitsingen}
    jaar_view = {"soort": "lijn", "per": "periode", "titel": vraag["titel_jaar"], "uitleg": vraag["uitleg_jaar"]}
    views = ["jaar", "groep"] if keuzes.get("volgorde") == "jaar" else ["groep", "jaar"]
    keuzes = {**keuzes, "uitsplitsing": ",".join(namen), "filter": ",".join(filter_namen) or "geen"}
    keuzes["gezien"] = list(dict.fromkeys([*keuzes.get("gezien", []), bepaal_stand(keuzes)]))
    return {
        "keuzes": keuzes,
        "vraag": vraag, "maat": maat, "uitsplitsing": uitsplitsingen[0][1], "uitsplitsingen": uitsplitsingen,
        "filters": filters, "views": views, "groep_views": groep_views, "jaar_view": jaar_view,
        "kolommen": list(dict.fromkeys(kolommen)), "k": k, "eenheid": casus["eenheid"],
        "ondertitel": casus["ondertitel"], "demo": casus.get("demo", False),
        "scheidingsteken": casus.get("scheidingsteken", ";"),
        "groep": casus["drempels"]["groep"], "cel": casus["drempels"]["cel"],
        "alle_uitsplitsingen": casus["uitsplitsingen"],
    }


def lees_data(pad: Path, ins: dict) -> pl.DataFrame:
    """Leest alleen de kolommen die nodig zijn, als tekst. Controleert eerst de kopregel."""
    if not pad.is_file():
        raise Melding(f"Databestand niet gevonden: {pad}")
    kop = pl.read_csv(pad, separator=ins["scheidingsteken"], n_rows=0).columns
    ontbreekt = [k for k in ins["kolommen"] if k not in kop]
    if ontbreekt:
        raise Melding(f"In {pad.name} ontbreken de kolommen: {', '.join(ontbreekt)}. "
                      f"Controleer het bestand en het scheidingsteken ('{ins['scheidingsteken']}').")
    try:
        return pl.read_csv(pad, separator=ins["scheidingsteken"], columns=ins["kolommen"], infer_schema=False)
    except MemoryError as fout:
        raise Melding(f"{pad.name} is te groot om in te lezen. Sla alleen de kolommen "
                      f"{', '.join(ins['kolommen'])} op in een kleiner bestand.") from fout


# ── Tekst ───────────────────────────────────────────────────────────────────


def maak_getal(n: float) -> str:
    return f"{round(n):,}".replace(",", ".")


def maak_procent(w: float) -> str:
    return "<1%" if 0 < w < 0.005 else f"{round(100 * w)}%"


def maak_label(tekst: str) -> str:
    return tekst[:1].upper() + tekst[1:]


def maak_telwoord(n: int) -> str:
    woorden = ["nul", "één", "twee", "drie", "vier", "vijf", "zes", "zeven", "acht", "negen", "tien"]
    return woorden[n] if n < len(woorden) else str(n)


def maak_schaal(hoogste: float) -> float:
    """Een rond percentage net boven de hoogste waarde; de as begint altijd bij nul."""
    stap = 0.05 if hoogste <= 0.3 else 0.1
    return min(1.0, max(stap, math.ceil(hoogste / stap - 1e-9) * stap))


# ── HTML per grafiek ────────────────────────────────────────────────────────


def toon_staaf(rijen: list[dict], ins: dict) -> tuple[str, str]:
    te_weinig = f"te weinig {ins['eenheid']}"
    zichtbaar = sorted((r for r in rijen if not r["verborgen"]), key=lambda r: -r["waarde"])
    verborgen = sorted((r for r in rijen if r["verborgen"]), key=lambda r: r["groep"])
    top = maak_schaal(max((r["waarde"] for r in zichtbaar), default=0))
    items = "".join(
        f'<li><div class="npuls-staaf-kop"><span>{e(maak_label(r["groep"]))}</span>'
        f'<span><strong>{maak_procent(r["waarde"])}</strong> <small>(n&nbsp;=&nbsp;{maak_getal(r["n"])})</small></span></div>'
        f'<div class="npuls-staaf-spoor"><div class="npuls-staaf" style="width:{100 * r["waarde"] / top:.1f}%"></div></div></li>'
        for r in zichtbaar)
    items += "".join(
        f'<li class="npuls-staaf-verborgen"><div class="npuls-staaf-kop"><span>{e(maak_label(r["groep"]))}</span>'
        f"<span>{te_weinig}</span></div></li>" for r in verborgen)
    grafiek = (f'<ul class="npuls-staven">{items}</ul>'
               f'<div class="npuls-schaal" aria-hidden="true"><span>0%</span><span>{maak_procent(top)}</span></div>')
    if len(zichtbaar) >= 2:
        hoog, laag = zichtbaar[0], zichtbaar[-1]
        zin = (f"Het hoogst bij {maak_label(hoog['groep'])} ({maak_procent(hoog['waarde'])}), "
               f"het laagst bij {maak_label(laag['groep'])} ({maak_procent(laag['waarde'])}).")
    elif zichtbaar:
        zin = f"{maak_label(zichtbaar[0]['groep'])}: {maak_procent(zichtbaar[0]['waarde'])}."
    else:
        zin = f"Alle groepen hebben {te_weinig} om te tonen."
    if verborgen and zichtbaar:
        zin += (f" {maak_label(maak_telwoord(len(verborgen)))} {'groep is' if len(verborgen) == 1 else 'groepen zijn'} "
                f"niet getoond omdat er {te_weinig} in zitten.")
    return grafiek, zin


def toon_lijn(rijen: list[dict], ins: dict) -> tuple[str, str]:
    """Lijn in een SVG die meerekt met de breedte; punten, labels en assen zijn HTML, zodat tekst scherp blijft."""
    perioden = [r["periode"] for r in rijen]
    zichtbaar = [r for r in rijen if not r["verborgen"]]
    top = maak_schaal(max((r["waarde"] for r in zichtbaar), default=0))

    def x(i: int) -> float:
        return 50.0 if len(perioden) == 1 else 4 + 92 * i / (len(perioden) - 1)

    def y(w: float) -> float:
        return 100 - 100 * w / top

    stukken, stuk, punten = [], [], ""
    for i, r in enumerate(rijen):
        if r["verborgen"]:
            stukken.append(stuk)
            stuk = []
            continue
        stuk.append(f"{x(i):.2f},{y(r['waarde']):.2f}")
        punten += (f'<span class="npuls-punt" style="left:{x(i):.2f}%;top:{y(r["waarde"]):.2f}%" '
                   f'title="{r["periode"]}: {maak_procent(r["waarde"])} (n = {maak_getal(r["n"])})"></span>')
    stukken.append(stuk)
    lijnen = "".join(f'<polyline points="{" ".join(s)}" vector-effect="non-scaling-stroke"/>' for s in stukken if len(s) > 1)
    labels = ""
    if zichtbaar:  # waarde bij het hoogste, het laagste en het laatste punt
        hoog = max(zichtbaar, key=lambda r: r["waarde"])
        laag = min(zichtbaar, key=lambda r: r["waarde"])
        for i, r in enumerate(rijen):
            if r is hoog or r is laag or r is zichtbaar[-1]:
                kant = " rechts" if x(i) > 80 else (" links" if x(i) < 12 else "")
                # het laagste punt en een punt tegen de bovenrand krijgen hun label eronder
                onder = " onder" if (r is laag and laag is not hoog) or y(r["waarde"]) < 15 else ""
                labels += (f'<span class="npuls-punt-label{kant}{onder}" style="left:{x(i):.2f}%;top:{y(r["waarde"]):.2f}%">'
                           f"{maak_procent(r['waarde'])}</span>")
    rasters = "".join(f'<line x1="0" x2="100" y1="{v}" y2="{v}" vector-effect="non-scaling-stroke"/>' for v in (0, 50, 100))
    y_labels = "".join(f'<span style="top:{100 - f * 100:.0f}%">{maak_procent(top * f)}</span>' for f in (0, 0.5, 1))
    x_labels = "".join(f'<span style="left:{x(i):.2f}%"><b class="lang">{p}</b><b class="kort">&#8217;{str(p)[-2:]}</b></span>'
                       for i, p in enumerate(perioden))
    grafiek = (f'<div class="npuls-lijn" aria-hidden="true"><div class="npuls-lijn-y">{y_labels}</div>'
               f'<div class="npuls-lijn-vlak"><svg viewBox="0 0 100 100" preserveAspectRatio="none">'
               f'<g class="raster">{rasters}</g><g class="lijn">{lijnen}</g></svg>{punten}{labels}</div>'
               f'<div class="npuls-lijn-x">{x_labels}</div></div>')
    if len(zichtbaar) >= 2:
        hoog, laag = max(zichtbaar, key=lambda r: r["waarde"]), min(zichtbaar, key=lambda r: r["waarde"])
        zin = (f"Van {maak_procent(zichtbaar[0]['waarde'])} in {zichtbaar[0]['periode']} naar "
               f"{maak_procent(zichtbaar[-1]['waarde'])} in {zichtbaar[-1]['periode']}. Het hoogst in {hoog['periode']} "
               f"({maak_procent(hoog['waarde'])}), het laagst in {laag['periode']} ({maak_procent(laag['waarde'])}).")
    elif zichtbaar:
        zin = f"In {zichtbaar[0]['periode']}: {maak_procent(zichtbaar[0]['waarde'])}."
    else:
        zin = f"Elk jaar heeft te weinig {ins['eenheid']} om te tonen."
    weg = [str(r["periode"]) for r in rijen if r["verborgen"]]
    if weg and zichtbaar:
        zin += f" Niet getoond omdat er te weinig {ins['eenheid']} zijn: {', '.join(weg)}."
    return grafiek, zin


def toon_cijfers(view: dict, rijen: list[dict], ins: dict) -> str:
    """De getallen achter de grafiek als tabel, voor wie ze wil nalezen of een schermlezer gebruikt."""
    kop = "Groep" if view["per"] == "groep" else "Instroomjaar"
    regels = ""
    for r in rijen:
        cellen = f"<td>{e(maak_label(str(r[view['per']])))}</td>"
        if r["verborgen"]:
            cellen += f'<td colspan="2">te weinig {ins["eenheid"]}</td>'
        else:
            cellen += f"<td>{maak_procent(r['waarde'])}</td><td>{maak_getal(r['n'])}</td>"
        regels += f"<tr>{cellen}</tr>"
    return (f'<details class="npuls-cijfers"><summary>Toon de cijfers</summary><div class="npuls-tabel">'
            f"<table><caption>{e(view['titel'])}</caption><thead><tr><th scope=\"col\">{kop}</th>"
            f'<th scope="col">Aandeel</th><th scope="col">Aantal eerstejaars</th></tr></thead>'
            f"<tbody>{regels}</tbody></table></div></details>")


def toon_view(view: dict, eerstejaars: pl.DataFrame, ins: dict, wissel: str = "") -> str:
    rijen = pas_drempels_toe(tel(eerstejaars, view["per"]), ins)
    grafiek, zin = (toon_staaf if view["soort"] == "staaf" else toon_lijn)(rijen, ins)
    return (f'<section class="npuls-view"{wissel}><h2>{e(view["titel"])}</h2><p class="npuls-uitleg">{e(view["uitleg"])}</p>'
            f'{grafiek}<p class="npuls-samenvatting">{e(zin)}</p>{toon_cijfers(view, rijen, ins)}</section>')


def toon_blok(data: pl.DataFrame, ins: dict) -> str:
    """Kerncijfers en de views voor één filterkeuze. Bij meer vergelijkingen één groepsview per vergelijking."""
    if data.is_empty():  # een combinatie van filters zonder één student
        return f'<div class="npuls-melding">In deze selectie zitten geen {ins["eenheid"]}. Kies een andere waarde.</div>'
    eerstejaars = bereken_eerstejaars(data, ins)
    teller, noemer = int(eerstejaars["telt"].sum()), eerstejaars.height
    if noemer < ins["groep"]:
        return (f'<div class="npuls-melding">In deze selectie zitten te weinig {ins["eenheid"]} om iets te tonen. '
                "Kies een andere waarde.</div>")
    perioden = eerstejaars["periode"].unique().sort().to_list()
    verborgen_totaal = teller < ins["cel"] or noemer - teller < ins["cel"]
    tegels = (f'<div class="npuls-tegel hoofd"><strong>{"–" if verborgen_totaal else maak_procent(teller / noemer)}</strong>'
              f"<span>{e(ins['vraag']['kerncijfer'])}</span></div>"
              f'<div class="npuls-tegel"><strong>{maak_getal(noemer)}</strong><span>Eerstejaars die meetellen</span></div>'
              f'<div class="npuls-tegel"><strong>{perioden[0]}–{perioden[-1]}</strong><span>Instroomjaren</span></div>')
    views = ""
    for soort in ins["views"]:
        if soort == "jaar":
            views += toon_view(ins["jaar_view"], eerstejaars, ins)
        elif len(ins["uitsplitsingen"]) == 1:
            views += toon_view(ins["groep_views"][ins["uitsplitsingen"][0][0]], eerstejaars, ins)
        else:
            for naam, uitsplitsing in ins["uitsplitsingen"]:
                per = bereken_eerstejaars(data, {**ins, "uitsplitsing": uitsplitsing})
                views += toon_view(ins["groep_views"][naam], per, {**ins, "uitsplitsing": uitsplitsing},
                                   f' data-uitsplitsing="{e(naam)}"')
    return f'<div class="npuls-tegels">{tegels}</div>{views}'


def toon_zo_lees_je_dit(ins: dict) -> str:
    definities = "".join(f"<dt>{e(n)}</dt><dd>{e(t)}</dd>" for n, t in ins["maat"]["definities"])
    niet = [*ins["maat"]["niet_zeggen"], "Waarom groepen verschillen: een verschil is geen oorzaak."]
    if ins["demo"]:
        niet.append("Iets over de werkelijkheid: dit is demodata.")
    kaarten = [
        ("Definities", f"<dl>{definities}</dl>"),
        ("Privacy", f"<p>Groepen met minder dan {ins['groep']} {e(ins['eenheid'])} tonen we niet, en ook geen percentage "
                    f"met minder dan {ins['cel']} {e(ins['eenheid'])} in de teller of in de rest. Is in een grafiek één groep "
                    "verborgen, dan verbergen we ook de kleinste andere groep, zodat niemand de verborgen waarde kan "
                    "terugrekenen. In dit bestand staan alleen uitkomsten per groep, geen gegevens van personen.</p>"),
        ("Aannames", "<ul>" + "".join(f"<li>{e(a)}</li>" for a in ins["maat"]["aannames"]) + "</ul>"),
        ("Wat dit dashboard niet kan zeggen", "<ul>" + "".join(f"<li>{e(n)}</li>" for n in niet) + "</ul>"),
    ]
    return "".join(f'<div class="npuls-uitlegkaart"><h3>{t}</h3>{inhoud}</div>' for t, inhoud in kaarten)


def bepaal_ranglijst(data: pl.DataFrame, ins: dict) -> list[dict]:
    """De zichtbare groepen over alle data, van hoog naar laag."""
    rijen = pas_drempels_toe(tel(bereken_eerstejaars(data, ins), "groep"), ins)
    return sorted((r for r in rijen if not r["verborgen"]), key=lambda r: -r["waarde"])


def toon_uitkomst(data: pl.DataFrame, ins: dict) -> None:
    """Wat het dashboard laat zien, en wat de gebruiker daarna kan aanpassen. Voor het gesprek."""
    lijst = bepaal_ranglijst(data, ins)
    eerstejaars = bereken_eerstejaars(data, ins)
    jaren = [r for r in pas_drempels_toe(tel(eerstejaars, "periode"), ins) if not r["verborgen"]]
    print(f"Hoogst: {maak_label(lijst[0]['groep'])} ({maak_procent(lijst[0]['waarde'])}). "
          f"Laagst: {maak_label(lijst[-1]['groep'])} ({maak_procent(lijst[-1]['waarde'])}). "
          f"Alle eerstejaars samen: {maak_procent(eerstejaars['telt'].mean())}.")
    if jaren:
        hoog, laag = max(jaren, key=lambda r: r["waarde"]), min(jaren, key=lambda r: r["waarde"])
        print(f"Over de jaren: het hoogst in {hoog['periode']} ({maak_procent(hoog['waarde'])}), "
              f"het laagst in {laag['periode']} ({maak_procent(laag['waarde'])}).")
    toon_aanpassingen(ins)


def toon_aanpassingen(ins: dict) -> None:
    """Alleen aanpassingen naar een stand die de gebruiker nog niet heeft gezien, zodat geen keuze terugkomt."""
    k = ins["keuzes"]
    volgorde = k.get("volgorde") or "groep"
    namen = k["uitsplitsing"].split(",")
    mogelijk = []
    if len(namen) < MAX_VERGELIJKINGEN:
        for naam in ins["vraag"]["uitsplitsingen"]:
            if naam not in namen and naam not in k["filter"].split(","):
                erbij = ",".join([*namen, naam])
                mogelijk.append((f"Vergelijk ook per {ins['alle_uitsplitsingen'][naam]['label']}",
                                 f"--uitsplitsing {erbij}", {**k, "uitsplitsing": erbij}))
    if volgorde == "jaar":
        mogelijk.append(("Zet de vergelijking tussen groepen bovenaan", "--volgorde groep", {**k, "volgorde": "groep"}))
    else:
        mogelijk.append(("Zet de ontwikkeling over de jaren bovenaan", "--volgorde jaar", {**k, "volgorde": "jaar"}))
    nieuw = [(label, extra) for label, extra, stand in mogelijk if bepaal_stand(stand) not in k["gezien"]]
    print("Aanpassen (label => extra argumenten bij --vanaf dashboard.html):")
    for label, extra in nieuw:
        print(f"- {label} => {extra}")
    if not nieuw:
        print("Geen nieuwe vaste aanpassingen meer: alles is al eens getoond.")


def bepaal_vingerafdruk(pagina: str) -> dict:
    """Wat er na een handmatige aanpassing hetzelfde moet blijven: de cijfers, wat verborgen is, het filter en het label."""
    tekst = re.sub(r"<style>.*?</style>|style=\"[^\"]*\"", "", pagina, flags=re.S)  # opmaak mag veranderen
    return {
        "procenten": sorted(re.findall(r"\d+%", tekst)),
        "cijfers": sorted(re.findall(r"<strong>([^<]*)</strong>", pagina)),
        "n": sorted(re.findall(r"n&nbsp;=&nbsp;([0-9.]+)", pagina)),
        "punten": sorted(re.findall(r'title="([^"]*)"', pagina)),
        "verborgen": pagina.count("npuls-staaf-verborgen"),
        "filterwaarden": re.findall(r'data-filter="([^"]*)"', pagina),
        "cijfertabellen": sorted(re.findall(r"<td>([^<]*%)</td><td>([0-9.]+)</td>", pagina)),
        "demo": "Dit is demodata" in pagina,
        "privacy": "terugrekenen" in pagina,
    }


def controleer(pad: Path, ins: dict, data: pl.DataFrame, csv: Path) -> None:
    """Vergelijkt een met de hand aangepast dashboard met een nieuw gemaakt dashboard op dezelfde keuzes."""
    aangepast = bepaal_vingerafdruk(pad.read_text(encoding="utf-8"))
    nieuw = bepaal_vingerafdruk(maak_html(data, csv, ins))
    fouten = [naam for naam in nieuw if aangepast[naam] != nieuw[naam]]
    if fouten:
        sys.exit("Niet goed: de aanpassing raakt " + ", ".join(fouten)
                 + ". Maak het dashboard opnieuw met --vanaf " + pad.name + " en probeer een kleinere aanpassing.")
    print("Goed: alle cijfers, verborgen groepen, het filter en de privacyuitleg zijn ongewijzigd.")
    toon_aanpassingen(ins)


def maak_commando(ins: dict, csv: Path) -> str:
    k = ins["keuzes"]
    return (f"uv run --no-project --with polars python .claude/skills/3-bouwen/assets/maak_dashboard.py {csv.as_posix()} --vraag {k.get('vraag', 'A')} "
            f"--uitsplitsing {k['uitsplitsing']} --filter {k['filter']}"
            + (f" --volgorde {k['volgorde']}" if k.get("volgorde") else "")
            + (f" --titel {json.dumps(k['titel'], ensure_ascii=False)}" if k.get("titel") else ""))


def maak_keuzelijst(id_: str, label: str, opties: list[tuple[str, str]], rol: str) -> str:
    return (f'<label for="{id_}">{e(label)}</label><select id="{id_}" {rol}>'
            + "".join(f'<option value="{e(w)}">{e(t)}</option>' for w, t in opties) + "</select>")


def maak_html(data: pl.DataFrame, csv: Path, ins: dict) -> str:
    """Eén blok per combinatie van filterwaarden, vooraf berekend; de keuzelijsten tonen alleen het gekozen blok."""
    waarden_per_filter = [["alle", *sorted(w for w in data[f["kolom"]].unique().to_list() if w is not None)]
                          for f in ins["filters"]]
    blokken = []
    for combinatie in itertools.product(*waarden_per_filter):
        deel = data
        for f, w in zip(ins["filters"], combinatie, strict=True):
            if w != "alle":
                deel = deel.filter(pl.col(f["kolom"]) == w)
        sleutel = "|".join(combinatie) or "alle"
        blokken.append(f'<div data-filter="{e(sleutel)}">{toon_blok(deel, ins)}</div>')
    keuzelijsten = []
    if len(ins["uitsplitsingen"]) > 1:
        keuzelijsten.append(maak_keuzelijst("uitsplitsing", "Vergelijk per", [
            (n, maak_label(u["label"])) for n, u in ins["uitsplitsingen"]], "data-wissel"))
    for i, (f, waarden) in enumerate(zip(ins["filters"], waarden_per_filter, strict=True)):
        keuzelijsten.append(maak_keuzelijst("filter" if i == 0 else f"filter{i + 1}", maak_label(f["label"]), [
            (w, "Alles" if w == "alle" else maak_label(w)) for w in waarden], "data-filterkeuze"))
    filter_html = "".join(keuzelijsten)
    vandaag = datetime.date.today()
    personen = data[ins["k"]["persoon"]].n_unique()
    bron = (f"Bron: {e(csv.name)}, {maak_getal(data.height)} rijen, {maak_getal(personen)} {e(ins['eenheid'])}. "
            f"Gemaakt op {vandaag.day} {MAANDEN[vandaag.month - 1]} {vandaag.year}.")
    logo = "data:image/jpeg;base64," + base64.b64encode(
        (HIER.parents[1] / "vormgever-npuls-huisstijl/assets/logos/npuls_logo.jpg").read_bytes()).decode()
    # Een eigen titel komt uit de schets; de vraag zelf blijft dan in de ondertitel staan
    titel = ins["keuzes"].get("titel") or ins["vraag"]["vraag"]
    ondertitel = ins["ondertitel"] if titel == ins["vraag"]["vraag"] else f"{ins['vraag']['vraag']} {ins['ondertitel']}"
    sjabloon = string.Template((HIER / "dashboard-sjabloon.html").read_text(encoding="utf-8"))
    return sjabloon.substitute(
        keuzes=e(json.dumps(ins["keuzes"], ensure_ascii=False)), titel=e(titel), logo=logo,
        css=(HIER / "npuls/npuls-dashboard.css").read_text(encoding="utf-8"),
        vraag=e(titel), ondertitel=e(ondertitel),
        demo='<p class="npuls-demo">Dit is demodata</p>' if ins["demo"] else "",
        filter=filter_html, blokken="".join(blokken), zo_lees_je_dit=toon_zo_lees_je_dit(ins), bron=bron,
        commando=e(maak_commando(ins, csv)),
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Maakt het dashboard als één HTML-bestand.")
    parser.add_argument("csv", nargs="?", type=Path, help="pad naar het databestand")
    parser.add_argument("--vanaf", type=Path, help="neem de keuzes over uit mijn-keuzes.json (standaard), schets.html of dashboard.html")
    parser.add_argument("--vraag", help="A, B of C uit het casusbestand")
    parser.add_argument("--uitsplitsing", help="bijvoorbeeld sector")
    parser.add_argument("--filter", help="bijvoorbeeld vestiging, of geen")
    parser.add_argument("--volgorde", choices=["groep", "jaar"], help="welke view bovenaan staat")
    parser.add_argument("--titel", help="een eigen titel boven het dashboard (standaard: de vraag)")
    parser.add_argument("--uit", type=Path, default=Path("dashboard.html"))
    parser.add_argument("--controleer", action="store_true",
                        help="controleer een met de hand aangepast dashboard (--vanaf) tegen een nieuw gemaakt dashboard")
    args = parser.parse_args()
    start = time.perf_counter()
    try:
        keuzes = bepaal_keuzes(args)
        csv = Path(keuzes["csv"])
        ins = stel_in(keuzes, lees_casus(csv))
        ins["keuzes"]["csv"] = csv.as_posix()
        data = lees_data(csv, ins)
        if args.controleer:
            controleer(Path(args.vanaf or "dashboard.html"), ins, data, csv)
            return
        pagina = maak_html(data, csv, ins)
    except Melding as melding:
        sys.exit(f"Niet gelukt: {melding}")
    args.uit.write_text(pagina, encoding="utf-8")
    shutil.copyfile(HIER / "berekeningen.py", args.uit.with_name("dashboard-berekeningen.py"))
    print(f"Klaar in {time.perf_counter() - start:.1f} s: {args.uit} ({maak_getal(data.height)} rijen gelezen)")
    toon_uitkomst(data, ins)


if __name__ == "__main__":
    main()
