"""Maakt het dashboard als één HTML-bestand. Draait zonder AI, ook op andere data.

Gebruik, vanuit de hoofdmap van de repo:

    python .claude/skills/bouwen_dashboard/assets/maak_dashboard.py --vanaf schets.html
    python .claude/skills/bouwen_dashboard/assets/maak_dashboard.py data/eigen.csv --vraag A \\
        --uitsplitsing sector --filter vestiging

De vraag, de definities en de teksten komen uit het casusbestand naast de data (data/x.csv -> data/x.casus.json).
De berekeningen staan hieronder en zijn getest: tel eerstejaars, en per eerstejaars of die het jaar erna gestopt
is of binnen een termijn een diploma haalde. De privacydrempels worden toegepast voordat er iets in het bestand
komt: in het dashboard staan alleen uitkomsten per groep, nooit rijen.
"""

from __future__ import annotations

import argparse
import base64
import datetime
import html
import json
import math
import re
import string
import sys
import time
from pathlib import Path

import polars as pl

HIER = Path(__file__).resolve().parent
e = html.escape
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


def bepaal_keuzes(args: argparse.Namespace) -> dict:
    keuzes: dict = {}
    vanaf = args.vanaf or (Path("schets.html") if not args.csv and Path("schets.html").is_file() else None)
    if vanaf:
        keuzes = lees_keuzes(Path(vanaf))
    for naam in ("csv", "vraag", "uitsplitsing", "filter", "volgorde"):
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


def stel_in(keuzes: dict, casus: dict) -> dict:
    """Zet de keuzes en de casus om in één instelling voor de rest van het script."""
    vraag = casus["vragen"].get(keuzes.get("vraag", "A"))
    if vraag is None:
        raise Melding(f"Onbekende vraag '{keuzes.get('vraag')}'. Kies uit: {', '.join(casus['vragen'])}")
    naam = keuzes.get("uitsplitsing") or vraag["uitsplitsingen"][0]
    if naam not in casus["uitsplitsingen"]:
        raise Melding(f"Onbekende uitsplitsing '{naam}'. Kies uit: {', '.join(casus['uitsplitsingen'])}")
    uitsplitsing = casus["uitsplitsingen"][naam]
    filter_naam = keuzes.get("filter") or "standaard"
    if filter_naam not in casus["uitsplitsingen"] and filter_naam != "geen" or filter_naam == naam:
        filter_naam = next(f for f in casus["filters"] if f != naam)
    filter_ = casus["uitsplitsingen"].get(filter_naam) if filter_naam != "geen" else None
    maat = casus["maten"][vraag["maat"]]
    k = casus["kolommen"]
    kolommen = [k["persoon"], k["jaar"], k["start"], uitsplitsing["kolom"]]
    if maat["soort"] == "diploma":
        kolommen.append(k["diplomajaar"])
    if filter_:
        kolommen.append(filter_["kolom"])
    groep_view = {"soort": "staaf", "per": "groep",
                  "titel": vraag["titel_groep"].format(uitsplitsing=uitsplitsing["label"]),
                  "uitleg": vraag["uitleg_groep"].format(uitsplitsing=uitsplitsing["label"])}
    jaar_view = {"soort": "lijn", "per": "periode", "titel": vraag["titel_jaar"], "uitleg": vraag["uitleg_jaar"]}
    views = [jaar_view, groep_view] if keuzes.get("volgorde") == "jaar" else [groep_view, jaar_view]
    return {
        "keuzes": {**keuzes, "uitsplitsing": naam, "filter": filter_naam},
        "vraag": vraag, "maat": maat, "uitsplitsing": uitsplitsing, "filter": filter_, "views": views,
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


# ── Berekeningen ────────────────────────────────────────────────────────────


def bereken_eerstejaars(data: pl.DataFrame, ins: dict) -> pl.DataFrame:
    """Per eerstejaars één rij: persoon, instroomjaar (periode), groep en of die meetelt in de teller."""
    k = ins["k"]
    d = data.with_columns(pl.col(k["jaar"]).cast(pl.Int32, strict=False).alias("_jaar"))
    laatste = d["_jaar"].max()
    groep = pl.col(ins["uitsplitsing"]["kolom"]).fill_null("onbekend").str.strip_chars()
    if ins["uitsplitsing"].get("opschonen"):
        groep = groep.str.replace(ins["uitsplitsing"]["opschonen"], "")
    instroom = (d.filter(pl.col(k["start"]).str.strip_chars() == k["start_waarde"])
                .select(pl.col(k["persoon"]).alias("persoon"), pl.col("_jaar").alias("periode"), groep.alias("groep"))
                .unique(subset="persoon", keep="first"))
    if ins["maat"]["soort"] == "uitval":
        terug = (d.select(pl.col(k["persoon"]).alias("persoon"), (pl.col("_jaar") - 1).alias("periode"))
                 .unique().with_columns(pl.lit(True).alias("terug")))
        return (instroom.filter(pl.col("periode") + 1 <= laatste)
                .join(terug, on=["persoon", "periode"], how="left")
                .with_columns(pl.col("terug").is_null().alias("telt")).drop("terug"))
    termijn = ins["maat"]["termijn"]
    diploma = (d.select(pl.col(k["persoon"]).alias("persoon"),
                        pl.col(k["diplomajaar"]).cast(pl.Int32, strict=False).alias("diplomajaar"))
               .group_by("persoon").agg(pl.col("diplomajaar").min()))
    return (instroom.filter(pl.col("periode") + termijn - 1 <= laatste)
            .join(diploma, on="persoon", how="left")
            .with_columns(((pl.col("diplomajaar") - pl.col("periode")) <= termijn - 1).fill_null(False).alias("telt"))
            .drop("diplomajaar"))


def tel(eerstejaars: pl.DataFrame, per: str) -> list[dict]:
    return (eerstejaars.group_by(per).agg(pl.col("telt").sum().alias("teller"), pl.len().alias("noemer"))
            .sort(per).to_dicts())


def pas_drempels_toe(rijen: list[dict], ins: dict) -> list[dict]:
    """Verbergt kleine groepen, en ook de kleinste zichtbare als er precies één verborgen is."""
    for r in rijen:
        r["n"] = r["noemer"]
        r["verborgen"] = r["noemer"] < ins["groep"] or r["teller"] < ins["cel"] or r["noemer"] - r["teller"] < ins["cel"]
        r["waarde"] = r["teller"] / r["noemer"] if r["noemer"] else 0.0
    zichtbaar = [r for r in rijen if not r["verborgen"]]
    if len(rijen) - len(zichtbaar) == 1 and zichtbaar:
        min(zichtbaar, key=lambda r: r["n"])["verborgen"] = True
    for r in rijen:
        if r["verborgen"]:
            r["waarde"] = None  # een verborgen waarde komt niet in het bestand
    return rijen


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


def toon_blok(data: pl.DataFrame, ins: dict) -> str:
    """Kerncijfers en de views voor één filterwaarde."""
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
    for view in ins["views"]:
        rijen = pas_drempels_toe(tel(eerstejaars, view["per"]), ins)
        grafiek, zin = (toon_staaf if view["soort"] == "staaf" else toon_lijn)(rijen, ins)
        views += (f'<section class="npuls-view"><h2>{e(view["titel"])}</h2><p class="npuls-uitleg">{e(view["uitleg"])}</p>'
                  f'{grafiek}<p class="npuls-samenvatting">{e(zin)}</p>{toon_cijfers(view, rijen, ins)}</section>')
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


def toon_gok(data: pl.DataFrame, ins: dict) -> None:
    """Een raadvraag voor de gebruiker: de hoogste, de laagste en een middelste groep, op alfabet."""
    lijst = bepaal_ranglijst(data, ins)
    keuze = {id(lijst[0]): lijst[0], id(lijst[-1]): lijst[-1], id(lijst[len(lijst) // 2]): lijst[len(lijst) // 2]}
    print("Vraag: " + ins["vraag"]["gok"].format(uitsplitsing=ins["uitsplitsing"]["label"]))
    print("Opties: " + " | ".join(sorted(maak_label(r["groep"]) for r in keuze.values())))


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
    print("Aanpassen (label => extra argumenten bij --vanaf dashboard.html):")
    k = ins["keuzes"]
    for naam in ins["vraag"]["uitsplitsingen"]:
        if naam != k["uitsplitsing"]:
            print(f"- Vergelijk per {ins['alle_uitsplitsingen'][naam]['label']} => --uitsplitsing {naam}")
    if k.get("volgorde") == "jaar":
        print("- Zet de vergelijking tussen groepen bovenaan => --volgorde groep")
    else:
        print("- Zet de ontwikkeling over de jaren bovenaan => --volgorde jaar")


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


def maak_commando(ins: dict, csv: Path) -> str:
    k = ins["keuzes"]
    return (f"uv run --no-project --with polars python .claude/skills/bouwen_dashboard/assets/maak_dashboard.py {csv.as_posix()} --vraag {k.get('vraag', 'A')} "
            f"--uitsplitsing {k['uitsplitsing']} --filter {k['filter']}"
            + (f" --volgorde {k['volgorde']}" if k.get("volgorde") else ""))


def maak_html(data: pl.DataFrame, csv: Path, ins: dict) -> str:
    blokken, opties = [], []
    waarden = ["alle"]
    if ins["filter"]:
        waarden += sorted(w for w in data[ins["filter"]["kolom"]].unique().to_list() if w is not None)
    for w in waarden:
        deel = data if w == "alle" else data.filter(pl.col(ins["filter"]["kolom"]) == w)
        label = "Alles" if w == "alle" else maak_label(w)
        opties.append(f'<option value="{e(w)}">{e(label)}</option>')
        blokken.append(f'<div data-filter="{e(w)}">{toon_blok(deel, ins)}</div>')
    filter_html = (f'<label for="filter">{e(maak_label(ins["filter"]["label"]))}</label>'
                   f'<select id="filter">{"".join(opties)}</select>') if ins["filter"] else ""
    vandaag = datetime.date.today()
    personen = data[ins["k"]["persoon"]].n_unique()
    bron = (f"Bron: {e(csv.name)}, {maak_getal(data.height)} rijen, {maak_getal(personen)} {e(ins['eenheid'])}. "
            f"Gemaakt op {vandaag.day} {MAANDEN[vandaag.month - 1]} {vandaag.year}.")
    logo = "data:image/jpeg;base64," + base64.b64encode(
        (HIER.parents[1] / "vormgever-npuls-huisstijl/assets/logos/npuls_logo.jpg").read_bytes()).decode()
    sjabloon = string.Template((HIER / "dashboard-sjabloon.html").read_text(encoding="utf-8"))
    return sjabloon.substitute(
        keuzes=e(json.dumps(ins["keuzes"], ensure_ascii=False)), titel=e(ins["vraag"]["vraag"]), logo=logo,
        css=(HIER / "npuls/npuls-dashboard.css").read_text(encoding="utf-8"),
        vraag=e(ins["vraag"]["vraag"]), ondertitel=e(ins["ondertitel"]),
        demo='<p class="npuls-demo">Dit is demodata</p>' if ins["demo"] else "",
        filter=filter_html, blokken="".join(blokken), zo_lees_je_dit=toon_zo_lees_je_dit(ins), bron=bron,
        commando=e(maak_commando(ins, csv)),
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Maakt het dashboard als één HTML-bestand.")
    parser.add_argument("csv", nargs="?", type=Path, help="pad naar het databestand")
    parser.add_argument("--vanaf", type=Path, help="neem de keuzes over uit schets.html")
    parser.add_argument("--vraag", help="A, B of C uit het casusbestand")
    parser.add_argument("--uitsplitsing", help="bijvoorbeeld sector")
    parser.add_argument("--filter", help="bijvoorbeeld vestiging, of geen")
    parser.add_argument("--volgorde", choices=["groep", "jaar"], help="welke view bovenaan staat")
    parser.add_argument("--uit", type=Path, default=Path("dashboard.html"))
    parser.add_argument("--gok", action="store_true", help="druk alleen een raadvraag af; maakt geen dashboard")
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
        if args.gok:
            toon_gok(data, ins)
            return
        pagina = maak_html(data, csv, ins)
    except Melding as melding:
        sys.exit(f"Niet gelukt: {melding}")
    args.uit.write_text(pagina, encoding="utf-8")
    print(f"Klaar in {time.perf_counter() - start:.1f} s: {args.uit} ({maak_getal(data.height)} rijen gelezen)")
    toon_uitkomst(data, ins)


if __name__ == "__main__":
    main()
