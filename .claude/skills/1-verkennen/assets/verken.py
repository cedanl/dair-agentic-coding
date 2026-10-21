"""Maakt een HTML-dataprofiel uit een CSV. Draait zonder AI, ook op andere data.

Gebruik, vanuit de hoofdmap van de repo:
    python .claude/skills/1-verkennen/assets/verken.py data/demodata_1cho.csv --vraag A --uitsplitsing sector
        # met een casusbestand naast de data (data/x.casus.json): schrijft data-profiel.html
    python verken.py data/bestand.csv --overzicht --demo  # alleen de structuur per kolom, in de terminal
    python verken.py data/bestand.csv --begrip begrip.json  # zonder casus: de tekst uit begrip.json
    python verken.py data/demo.csv --demo               # demodata: label en de namen van waarden
    python verken.py data/echt.csv                      # elke andere data: geen label en geen namen van waarden
    python verken.py data/bestand.csv --sleutel persoon --sleutel jaar --uitsplitsing-kolom groep

Het script bevat geen waarden uit de data en geen conclusies. Het rekent de structuur uit (rijen,
kolommen, unieke en ontbrekende waarden, groepsgroottes), controleert de kwaliteit (sleutel, dubbele rijen,
typen, ontbrekende waarden per kolom en per groep) en tekent de verdelingen (histogram per getalkolom,
aandelen per categorie, samenhang tussen getalkolommen). De tekst uit begrip.json komt erbij. Alles wat
iets over het domein zegt (betekenis van kolommen, definities, aanpakken) komt uit begrip.json.

Installeren: uv pip install duckdb
"""
import argparse
import html
import json
import math
import sys
from pathlib import Path

import duckdb


def maak_hoofdletter(tekst):
    return tekst[:1].upper() + tekst[1:]

p = argparse.ArgumentParser()
p.add_argument("csv")
p.add_argument("--begrip", help="JSON met de tekst van de gebruiker: datagebruik, jouw_aanpak, keuzes, eenheid_rij, sleutel, kolommen, definities, casus_ideeen, casus_aanpak")
p.add_argument("--uit", default="data-profiel.html")
p.add_argument("--keuzes", default="mijn-keuzes.json", help="het bestand met de keuzes van de deelnemer: vraag en vergelijken komen hieruit, en het profiel schrijft terug wat het deed")
p.add_argument("--vraag", help="A, B of C uit het casusbestand naast de data")
p.add_argument("--stap", type=int, choices=[1, 2, 3, 4], help="druk alleen de samenvatting van deze stap af; stap 4 schrijft ook het profiel")
p.add_argument("--uitsplitsing", dest="uitsplitsing_naam", help="naam van de uitsplitsing uit het casusbestand, bijvoorbeeld sector, of meer met komma's: sector,opleiding")
p.add_argument("--overzicht", action="store_true", help="druk alleen de structuur per kolom af en schrijf geen profiel")
p.add_argument("--sep", default=";", help="scheidingsteken van de CSV")
p.add_argument("--demo", action="store_true", help="de data is demodata: toon het demodata-label en de namen van waarden")
p.add_argument("--uitsplitsing-kolom", dest="uitsplitsing", action="append", default=[], help="kolom om mee uit te splitsen, zonder casus (herhaalbaar)")
p.add_argument("--sleutel", action="append", default=[], help="kolom die samen met de andere sleutelkolommen één rij uniek maakt (herhaalbaar)")
p.add_argument("--drempel", type=int, default=30, help="minimale groepsgrootte")
p.add_argument("--drempel-cel", type=int, default=5, help="minimale teller of rest bij een percentage")
p.add_argument("--max-waarden", type=int, default=6, help="toon de waarden zelf bij hooguit zoveel verschillende")
a = p.parse_args()

TYPE_AANDEEL = 0.9  # een kolom krijgt een type als minstens dit deel van de ingevulde waarden erin past
ID_AANDEEL = 0.9  # vrijwel alleen unieke waarden: de kolom lijkt een identificatie
ONGELIJK = 0.2  # verschil in aandeel ontbrekend tussen groepen dat als ongelijk telt
CATEGORIE_MAX = 12  # teken de aandelen per waarde bij hooguit zoveel verschillende waarden
BAKKEN = 20  # aantal staven in een histogram
SAMENHANG_MAX = 10  # hooguit zoveel getalkolommen in de tabel met samenhang
GETAL = "try_cast(replace(v, ',', '.') as double)"  # een decimale komma telt als getal

e = html.escape
con = duckdb.connect()
# één keer inlezen in het geheugen van DuckDB; elke controle hieronder leest dan die tabel en niet opnieuw het bestand
con.sql(f"create table data as select * from read_csv('{a.csv}', delim='{a.sep}', header=true, all_varchar=true)")
bron = "data"
q = lambda sql: con.sql(sql).fetchall()
begrip = json.loads(Path(a.begrip).read_text(encoding="utf-8")) if a.begrip else {}
keuzes = {"csv": Path(a.csv).as_posix()}
casus_pad = Path(a.csv).with_suffix(".casus.json")
if casus_pad.is_file() and not a.begrip:
    # De casus bepaalt de tekst: kolommen, definities en ideeën liggen vast, de keuzes komen uit het commando
    casus = json.loads(casus_pad.read_text(encoding="utf-8"))
    mijn = json.loads(Path(a.keuzes).read_text(encoding="utf-8")) if Path(a.keuzes).is_file() else None
    if mijn:  # de keuzes van de deelnemer zijn de waarheid; een argument op de opdrachtregel gaat voor
        a.vraag = a.vraag or mijn["keuzes"].get("vraag")
        a.uitsplitsing_naam = a.uitsplitsing_naam or mijn["keuzes"].get("vergelijken")
    vraag_letter = a.vraag or "A"
    vraag = casus["vragen"][vraag_letter]
    # Meer vergelijkingen mogen ("sector,opleiding"): het profiel gaat over de eerste, het dashboard krijgt ze allemaal
    namen = list(dict.fromkeys(n.strip() for n in (a.uitsplitsing_naam or vraag["uitsplitsingen"][0]).split(",") if n.strip()))
    # Gaat de vraag over één vergelijking (zoals vooropleiding bij C), dan staat die er altijd bij, vooraan
    if vraag.get("kern"):
        namen = [vraag["kern"], *(n for n in namen if n != vraag["kern"])]
    onbekend_naam = [n for n in namen if casus["uitsplitsingen"].get(n, {"alleen_filter": True}).get("alleen_filter")]
    if onbekend_naam:
        sys.exit(f"Onbekende uitsplitsing: {', '.join(onbekend_naam)}. Kies uit: {', '.join(casus['uitsplitsingen'])}")
    naam = namen[0]
    uitsplitsing = casus["uitsplitsingen"][naam]
    maat = casus["maten"][vraag["maat"]]
    label = uitsplitsing["label"]
    a.demo = a.demo or casus.get("demo", False)
    a.uitsplitsing = [uitsplitsing["kolom"], *a.uitsplitsing]
    a.drempel, a.drempel_cel = casus["drempels"]["groep"], casus["drempels"]["cel"]
    keuzes.update(vraag=vraag_letter, uitsplitsing=",".join(namen))
    if mijn:
        mijn["keuzes"].update(vraag=vraag_letter, vergelijken=",".join(namen))
        Path(a.keuzes).write_text(json.dumps(mijn, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    begrip = {
        **casus["begrip"],
        "jouw_aanpak": f"{vraag['vraag']} Uitgesplitst naar {label}.",
        "keuzes": [
            {"onderwerp": "Vraag", "keuze": vraag["vraag"], "status": "bevestigd"},
            {"onderwerp": "Uitsplitsing", "keuze": label, "status": "bevestigd"},
            {"onderwerp": "Kernmaat", "keuze": maat["definities"][0][0], "status": "bevestigd", "hoofdstuk": "definities"},
            {"onderwerp": "Privacy", "keuze": f"groepen vanaf {a.drempel}, cellen vanaf {a.drempel_cel}, secundaire onderdrukking",
             "status": "bevestigd", "hoofdstuk": "privacy"},
        ],
        "definities": [{"naam": n, "definitie": t} for n, t in maat["definities"]],
        "aannames": maat["aannames"],
        "casus_ideeen": {
            "hypotheses": [{k: v.format(uitsplitsing=label) for k, v in h.items()} for h in vraag["ideeen"]["hypotheses"]],
            "valkuilen": vraag["ideeen"]["valkuilen"],
        },
        "casus_aanpak": [
            {"idee": f"{maak_hoofdletter(maat['definities'][0][0])} per {label}",
             "maat": maat["definities"][0][0], "uitsplitsing": label, "kan_niet": "Waarom groepen verschillen: een verschil is geen oorzaak."},
            {"idee": f"{maak_hoofdletter(maat['definities'][0][0])} per instroomjaar",
             "maat": maat["definities"][0][0], "uitsplitsing": "instroomjaar", "kan_niet": "Of een verandering doorzet in de jaren die nog niet in de data zitten."},
        ],
    }

kolommen = [r[0] for r in q(f"describe select * from {bron}")]
kolom_begrip = begrip.get("kolommen", {})
# Kolommen waar leeg een betekenis heeft (zoals diplomajaar: leeg = geen diploma) tellen niet als ontbrekend
leeg_is = {k: v["leeg_is"] for k, v in kolom_begrip.items() if v.get("leeg_is")}
sleutel = a.sleutel or begrip.get("sleutel", [])
onbekend = [k for k in a.uitsplitsing + sleutel if k not in kolommen]
if onbekend:
    sys.exit(f"Kolom niet gevonden in {Path(a.csv).name}: {', '.join(onbekend)}")


def waarde(k):
    return f"nullif(trim(\"{k}\"), '')"


def duizend(n):
    return f"{n:,}".replace(",", ".")


def getal(x):
    return str(int(x)) if float(x).is_integer() else f"{x:.2f}".replace(".", ",")


def procent(x):
    return "<1%" if 0 < x < 0.005 else f"{round(100 * x)}%"


def tabel(caption, kop, rijen, html_kolommen=()):
    t = f"<table><caption>{e(caption)}</caption><thead><tr>" + "".join(f'<th scope="col">{e(c)}</th>' for c in kop) + "</tr></thead><tbody>"
    for r in rijen:
        t += "<tr>" + "".join(f"<td>{c if i in html_kolommen else e(str(c))}</td>" for i, c in enumerate(r)) + "</tr>"
    return '<div class="wrap">' + t + "</tbody></table></div>"


def balk(aandeel):
    return f'<span class="balk"><span style="width:{round(100 * aandeel, 1)}%"></span></span>'


def lijst(items):
    return "<ul>" + "".join(f"<li>{i}</li>" for i in items) + "</ul>" if items else ""


# Structuur en typen per kolom
n_rijen = q(f"select count(*) from {bron}")[0][0]
structuur = []
typen = {}
for k in kolommen:
    # een lege waarde telt mee als waarde: een kolom met alleen "ingevuld" en "leeg" heeft twee toestanden
    uniek, leeg, n_getal, n_datum = q(f"select count(distinct coalesce(v, '')), count(*) filter (where v is null), "
                                      f"count({GETAL}), count(try_cast(v as date)) from (select {waarde(k)} v from {bron})")[0]
    ingevuld = n_rijen - leeg
    passend = {"getal": n_getal, "datum": n_datum}
    soort = kolom_begrip.get(k, {}).get("type")
    if soort not in ("getal", "datum", "tekst"):
        soort = next((t for t, n in passend.items() if ingevuld and n >= TYPE_AANDEEL * ingevuld), "tekst")
    typen[k] = (soort, ingevuld - passend.get(soort, ingevuld), uniek, ingevuld)
    waarden = ""
    if uniek <= a.max_waarden and a.demo:
        waarden = ", ".join(f"{w} ({n})" for w, n in q(
            f"select coalesce(nullif(trim(\"{k}\"), ''), '(leeg)'), count(*) from {bron} group by 1 order by 2 desc, 1"))
    structuur.append((k, uniek, leeg, waarden))
een_waarde = [k for k, u, _, _ in structuur if u == 1]
n_leeg = sum(leeg for k, _, leeg, _ in structuur if k not in leeg_is)

if a.overzicht:
    print(f"{Path(a.csv).name}: {duizend(n_rijen)} rijen, {len(kolommen)} kolommen")
    print("kolom | unieke waarden | leeg | voorgesteld type | waarden" + ("" if a.demo else " (alleen bij --demo)"))
    for k, u, leeg, w in structuur:
        print(f"{k} | {duizend(u)} | {duizend(leeg)} | {typen[k][0]} | {w}")
    sys.exit()

# Groepsgroottes per uitsplitsing: alleen aantallen, geen namen van groepen
groepen_html = ""
if a.uitsplitsing:
    cols = ", ".join(f'"{c}"' for c in a.uitsplitsing)
    groottes = [r[0] for r in q(f"select count(*) from {bron} group by {cols}")]
    klein = sum(1 for n in groottes if n < a.drempel)
    groepen_html = (f"<p>Uitsplitsing {e(' × '.join(a.uitsplitsing))}: {len(groottes)} groepen, waarvan {klein} met minder dan "
                    f"{a.drempel} rijen. Een indicatie van de structuur; op andere data zijn de aantallen anders. "
                    "Let op: dit telt rijen, geen personen.</p>")

# Datakwaliteit: wat één rij is, of de sleutel uniek is, dubbele rijen, typen en ontbrekende waarden
kwaliteit = [f"Eén rij is: {e(begrip['eenheid_rij'])}"] if begrip.get("eenheid_rij") else []
sleutel_tegel = "niet opgegeven"
if sleutel:
    cols = ", ".join(f'"{c}"' for c in sleutel)
    n_sleutels = q(f"select count(*) from (select distinct {cols} from {bron})")[0][0]
    naam = e(" × ".join(sleutel))
    sleutel_tegel = "uniek" if n_sleutels == n_rijen else "niet uniek"
    kwaliteit.append(f"De sleutel {naam} is uniek: elke rij heeft een eigen combinatie." if n_sleutels == n_rijen else
                     f"De sleutel {naam} is <strong>niet uniek</strong>: {n_rijen - n_sleutels} rijen delen hun sleutel met een eerdere rij. "
                     "Een telling van rijen telt dan iets anders dan een telling van sleutels.")
else:
    kwaliteit.append("Er is geen sleutel opgegeven, dus het is niet gecontroleerd wat één rij voorstelt. Geef de kolommen op met <code>--sleutel</code>.")
n_dubbel = n_rijen - q(f"select count(*) from (select distinct * from {bron})")[0][0]
kwaliteit.append(f"{n_dubbel} rijen zijn een exacte kopie van een eerdere rij." if n_dubbel else "Er zijn geen exact dubbele rijen.")
if een_waarde:
    kwaliteit.append("Kolommen met één waarde (kunnen niet uitsplitsen): " + e(", ".join(een_waarde)))

ontbrekend_kolom = [(k, f"{duizend(leeg)} ({procent(leeg / n_rijen)})", balk(leeg / n_rijen))
                    for k, _, leeg, _ in sorted(structuur, key=lambda r: -r[2]) if leeg and k not in leeg_is]
verwacht_leeg = [(k, f"{duizend(leeg)} ({procent(leeg / n_rijen)})", leeg_is[k])
                 for k, _, leeg, _ in structuur if leeg and k in leeg_is]
n_getypeerd = sum(1 for soort, _, _, _ in typen.values() if soort != "tekst")
type_rijen = [(k, soort, past_niet) for k, (soort, past_niet, _, _) in typen.items() if soort != "tekst" and past_niet]
kwaliteit.append(f"{n_getypeerd} kolommen bevatten een getal of datum. " + (f"In {len(type_rijen)} daarvan passen niet alle waarden (zie de tabel)." if type_rijen else "Alle ingevulde waarden passen in dat type."))

ontbrekend_groep = []
if a.uitsplitsing:
    cols = ", ".join(f'"{c}"' for c in a.uitsplitsing)
    for k, _, leeg, _ in structuur:
        if not leeg or k in a.uitsplitsing or k in leeg_is:
            continue
        laagste, hoogste, n_groepen = q(f"select min(aandeel), max(aandeel), count(*) from (select count(*) filter (where {waarde(k)} is null) / count(*) aandeel "
                                        f"from {bron} group by {cols} having count(*) >= {a.drempel})")[0]
        if n_groepen:
            ontbrekend_groep.append((hoogste - laagste, k, procent(laagste), procent(hoogste), "ongelijk" if hoogste - laagste >= ONGELIJK else ""))
    ontbrekend_groep = [r[1:] for r in sorted(ontbrekend_groep, reverse=True)]


def histogram(k, laagste, hoogste, kw, n_laagste):
    """Staven tussen de grenzen voor uitschieters. Een staaf onder de celdrempel wordt niet getekend."""
    afstand = kw[3] - kw[1]
    onder, boven = (max(laagste, kw[1] - 1.5 * afstand), min(hoogste, kw[3] + 1.5 * afstand)) if afstand else (laagste, hoogste)
    x = f"(select {GETAL} x from (select {waarde(k)} v from {bron}))"
    geheel = q(f"select count(*) from {x} where x != floor(x)")[0][0] == 0
    if geheel and boven - onder < 2 * BAKKEN:
        onder, boven = math.floor(onder), math.ceil(boven)
        breedte, n_bakken = 1, boven - onder + 1
    else:
        breedte, n_bakken = (boven - onder) / BAKKEN, BAKKEN
    if not breedte:
        return ""
    tellingen = dict(q(f"select least(floor((x - {onder}) / {breedte}), {n_bakken - 1})::int, count(*) from {x} where x between {onder} and {boven} group by 1"))
    hoogste_staaf = max(tellingen.values())
    stap = 252 / n_bakken
    staven, weggelaten = "", 0
    for i in range(n_bakken):
        n = tellingen.get(i, 0)
        if 0 < n < a.drempel_cel:
            weggelaten += 1
        elif n:
            hoogte = max(2, 70 * n / hoogste_staaf)
            bereik = getal(onder + i) if breedte == 1 else f"{getal(onder + i * breedte)} tot {getal(onder + (i + 1) * breedte)}"
            staven += (f'<rect x="{round(4 + i * stap + 1, 1)}" y="{round(74 - hoogte, 1)}" width="{round(stap - 2, 1)}" height="{round(hoogte, 1)}" rx="2">'
                       f"<title>{bereik}: {duizend(n)} rijen</title></rect>")
    # de laagste waarde staat alleen op de as als ze geen losse rij aanwijst
    links = getal(onder) if onder > laagste or n_laagste >= a.drempel_cel else ""
    as_tekst = f'<text x="4" y="90">{links}</text><text x="256" y="90" text-anchor="end">{getal(boven)}</text>'
    noot = f" {weggelaten} staven met minder dan {a.drempel_cel} rijen zijn weggelaten." if weggelaten else ""
    return (f'<svg viewBox="0 0 260 94" role="img" aria-label="Histogram van {e(k)}"><line x1="4" x2="256" y1="74.5" y2="74.5"/>{staven}{as_tekst}</svg>', noot)


# Verdelingen: alleen getalkolommen die geen identificatie of categorie zijn
onderdrukt = f"onderdrukt (minder dan {a.drempel_cel} rijen)"
verdeling_rijen, kaarten, maten = [], "", []
for k, (soort, past_niet, uniek, ingevuld) in typen.items():
    rol = kolom_begrip.get(k, {}).get("rol", "").lower()
    n = ingevuld - past_niet
    if soort != "getal" or k in sleutel or uniek <= a.max_waarden or rol.startswith(("identificatie", "categorie")):
        continue
    if not rol and uniek >= ID_AANDEEL * ingevuld:
        continue
    if n < a.drempel:
        verdeling_rijen.append((k, n, *["te weinig waarden"] * 6))
        continue
    laagste, hoogste, kw, n_laagste, n_hoogste, n_uitschieters = q(
        f"with g as (select {GETAL} x from (select {waarde(k)} v from {bron})), "
        "s as (select min(x) mn, max(x) mx, quantile_cont(x, [0.05, 0.25, 0.5, 0.75, 0.95]) kw from g) "
        "select mn, mx, kw, (select count(*) from g where x = mn), (select count(*) from g where x = mx), "
        "(select count(*) from g where x < kw[2] - 1.5 * (kw[4] - kw[2]) or x > kw[4] + 1.5 * (kw[4] - kw[2])) from s")[0]
    uitschieters = n_uitschieters if n_uitschieters == 0 or n_uitschieters >= a.drempel_cel else f"minder dan {a.drempel_cel}"
    verdeling_rijen.append((
        k, duizend(n),
        getal(laagste) if n_laagste >= a.drempel_cel else onderdrukt,
        getal(kw[1]), getal(kw[2]), getal(kw[3]),
        getal(hoogste) if n_hoogste >= a.drempel_cel else onderdrukt,
        uitschieters))
    maten.append(k)
    plaatje = histogram(k, laagste, hoogste, kw, n_laagste)
    if plaatje:
        kaarten += (f"<figure><figcaption>{e(k)}</figcaption>{plaatje[0]}<p class='muted'>mediaan {getal(kw[2])}, helft tussen {getal(kw[1])} en {getal(kw[3])}, "
                    f"{duizend(n)} waarden, uitschieters buiten beeld: {uitschieters}.{plaatje[1]}</p></figure>")

# Aandelen per waarde bij kolommen met weinig verschillende waarden; namen alleen bij demodata
categorie_kaarten = ""
for k, uniek, _, _ in structuur:
    if not 2 <= uniek <= CATEGORIE_MAX:
        continue
    rijen = []
    for i, (w, n) in enumerate(q(f"select coalesce({waarde(k)}, '(leeg)'), count(*) from {bron} group by 1 order by 2 desc, 1"), 1):
        naam = w if a.demo or w == "(leeg)" else f"waarde {i}"
        rijen.append((naam, procent(n / n_rijen), balk(n / n_rijen)) if n >= a.drempel_cel else (naam, f"minder dan {a.drempel_cel} rijen", ""))
    categorie_kaarten += "<figure>" + tabel(k, ["Waarde", "Aandeel", ""], rijen, html_kolommen={2}) + "</figure>"

# Samenhang tussen getalkolommen: correlatie over de rijen waarin beide kolommen een getal hebben
samenhang_html = ""
maten = maten[:SAMENHANG_MAX]
if len(maten) > 1:
    paren = [(i, j) for i in range(len(maten)) for j in range(i)]
    gekozen = ", ".join(f"try_cast(replace({waarde(k)}, ',', '.') as double) c{i}" for i, k in enumerate(maten))
    r = dict(zip(paren, q(f"select {', '.join(f'corr(c{i}, c{j})' for i, j in paren)} from (select {gekozen} from {bron})")[0]))
    rijen = ""
    for i, k in enumerate(maten):
        cellen = ""
        for j in range(len(maten)):
            c = r.get((i, j))
            if j >= i or c is None or math.isnan(c):
                cellen += "<td></td>" if j >= i else "<td>–</td>"
            else:
                kleur = "61,104,236" if c > 0 else "208,59,59"
                cellen += f'<td style="background:rgba({kleur},{round(abs(c) * 0.55, 2)})">{f"{c:.2f}".replace(".", ",")}</td>'
        rijen += f'<tr><th scope="row">{i + 1}. {e(k)}</th>{cellen}</tr>'
    samenhang_html = ('<div class="wrap"><table class="samenhang"><caption>Samenhang tussen getalkolommen (correlatie van -1 tot 1)</caption><thead><tr><td></td>'
                      + "".join(f'<th scope="col">{i + 1}</th>' for i in range(len(maten))) + f"</tr></thead><tbody>{rijen}</tbody></table></div>"
                      "<p class='muted'>Dicht bij 1 (blauw): de kolommen gaan samen omhoog. Dicht bij -1 (rood): de ene gaat omhoog als de andere daalt. "
                      "Rond 0: geen rechtlijnig verband. Een samenhang is geen oorzaak.</p>")

# Tekst uit begrip.json
begrip_rijen = [(k, v.get("rol", ""), v.get("betekenis", ""), v.get("let_op", "")) for k, v in kolom_begrip.items()]
definities = begrip.get("definities", [])
ideeen = begrip.get("casus_ideeen", {})


def ideeen_html():
    delen = []
    kol = [f"<strong>{e(x.get('kolom', ''))}</strong>: {e(x.get('waarom', ''))}" for x in ideeen.get("relevante_kolommen", [])]
    maten = [f"<strong>{e(x.get('naam', ''))}</strong>: {e(x.get('definitie', ''))}" for x in ideeen.get("afgeleide_maten", [])]
    hyp = [f"{e(x.get('vraag', ''))}<br><span class='muted'>Alternatieve verklaring: {e(x.get('alternatieve_verklaring', ''))}</span>" for x in ideeen.get("hypotheses", [])]
    for titel, items in [("Relevante kolommen", kol), ("Afgeleide maten en groepen", maten), ("Hypotheses om te verkennen", hyp),
                         ("Eerlijke vergelijkingen", [e(x) for x in ideeen.get("vergelijkingen", [])]),
                         ("Valkuilen voor deze vraag", [e(x) for x in ideeen.get("valkuilen", [])]),
                         ("Ontbrekende data", [e(x) for x in ideeen.get("ontbrekende_data", [])]),
                         ("Vragen aan de gebruiker", [e(x) for x in ideeen.get("vragen", [])])]:
        if items:
            delen.append(f"<h3>{titel}</h3>{lijst(items)}")
    aanpak = "".join(
        f"<li><strong>{e(x.get('idee', ''))}</strong><br>Maat: {e(x.get('maat', ''))}. Uitsplitsing: {e(x.get('uitsplitsing', ''))}."
        f"<br><span class='muted'>Kan niet zeggen: {e(x.get('kan_niet', ''))}</span></li>" for x in begrip.get("casus_aanpak", []))
    if aanpak:
        delen.append(f"<h3>Hoe de vraag aan te vliegen</h3><ol>{aanpak}</ol>")
    return "".join(delen)


# In het kort: elke keuze één keer, met de status en een verwijzing naar het hoofdstuk met de uitleg
HOOFDSTUKKEN = [("kort", "In het kort"), ("kolommen", "Kolommen"), ("definities", "Definities"), ("kwaliteit", "Datakwaliteit"),
                ("verdelingen", "Verdelingen"), ("ideeen", "Ideeën en aanpak"), ("privacy", "Privacy"), ("bijlage", "Bijlage")]
titels = dict(HOOFDSTUKKEN)
keuze_rijen = [(naam, e(begrip[veld]), "") for naam, veld in [("Datagebruik", "datagebruik"), ("Jouw aanpak", "jouw_aanpak")] if begrip.get(veld)]
for x in begrip.get("keuzes", []):
    x = x if isinstance(x, dict) else {"keuze": x}
    verwijzing = f' <a href="#{x["hoofdstuk"]}">Zie {titels[x["hoofdstuk"]]}</a>' if x.get("hoofdstuk") in titels else ""
    keuze_rijen.append((x.get("onderwerp", ""), e(x.get("keuze", "")) + verwijzing, x.get("status", "")))

tegels = "".join(f"<div><strong>{e(str(w))}</strong><span>{e(n)}</span></div>" for w, n in [
    (duizend(n_rijen), "rijen"), (len(kolommen), "kolommen"), (procent(n_leeg / (n_rijen * len(kolommen))) if n_rijen else "0%", "van de cellen ontbreekt"),
    (duizend(n_dubbel), "dubbele rijen"), (sleutel_tegel, "sleutel")])
demo = '<p class="demo"><strong>Dit is demodata.</strong> Het profiel beschrijft wat er in het bestand zit, niet wat er in de werkelijkheid geldt.</p>' if a.demo else ""

inhoud = {
    "kort": f'<p class="muted">Bestand: {e(Path(a.csv).name)}</p>{demo}<div class="tegels">{tegels}</div>'
            + (tabel("Keuzes en aannames", ["Onderwerp", "Keuze", "Status"], keuze_rijen, html_kolommen={1}) if keuze_rijen else ""),
    "kolommen": tabel("Rol, betekenis (aanname) en aandachtspunt per kolom", ["Kolom", "Rol", "Betekenis", "Let op"], begrip_rijen) if begrip_rijen else "",
    "definities": "<dl>" + "".join(f"<dt>{e(d.get('naam', ''))}</dt><dd>{e(d.get('definitie', ''))}</dd>" for d in definities) + "</dl>" if definities else "",
    "kwaliteit": lijst(kwaliteit)
                 + (tabel("Ontbrekende waarden per kolom", ["Kolom", "Ontbrekend", ""], ontbrekend_kolom, html_kolommen={2}) if ontbrekend_kolom else "<p>Geen enkele kolom heeft ontbrekende waarden.</p>")
                 + (tabel("Leeg met een betekenis (geen ontbrekende waarde)", ["Kolom", "Leeg", "Leeg betekent"], verwacht_leeg) if verwacht_leeg else "")
                 + (tabel(f"Aandeel ontbrekend per groep van {' × '.join(a.uitsplitsing)} (alleen groepen vanaf {a.drempel} rijen)", ["Kolom", "Laagste aandeel", "Hoogste aandeel", "Verschil"], ontbrekend_groep)
                    + "<p class='muted'>Ongelijk betekent: in de ene groep ontbreekt veel meer dan in de andere. Een vergelijking tussen groepen op die kolom is dan scheef.</p>" if ontbrekend_groep else "")
                 + (tabel("Kolommen waarin niet alle ingevulde waarden in het voorgestelde type passen", ["Kolom", "Voorgesteld type", "Past niet"], type_rijen) if type_rijen else ""),
    "verdelingen": (f"<h3>Getalkolommen</h3><div class='kaarten'>{kaarten}</div>" if kaarten else "")
                   + (f"<details><summary>Toon de getallen als tabel</summary>{tabel('Verdeling per getalkolom', ['Kolom', 'Aantal', 'Laagste', 'Kwartiel 1', 'Mediaan', 'Kwartiel 3', 'Hoogste', 'Uitschieters'], verdeling_rijen)}"
                      f"<p class='muted'>De laagste en hoogste waarde staan er alleen als minstens {a.drempel_cel} rijen die waarde hebben: anders wijst het getal één rij aan. "
                      "Uitschieters liggen meer dan anderhalf keer de afstand tussen kwartiel 1 en 3 buiten die kwartielen.</p></details>" if verdeling_rijen else "")
                   + (f"<h3>Kolommen met weinig verschillende waarden</h3><div class='kaarten'>{categorie_kaarten}</div>"
                      + ("" if a.demo else "<p class='muted'>De namen van de waarden staan er alleen bij demodata.</p>") if categorie_kaarten else "")
                   + (f"<h3>Samenhang</h3>{samenhang_html}" if samenhang_html else "")
                   + ("<p class='muted'>Deze cijfers beschrijven dit bestand; op andere data zijn ze anders.</p>" if kaarten or categorie_kaarten else ""),
    "ideeen": ideeen_html(),
    "privacy": f"{groepen_html}<ul><li>Groepen onder <strong>{a.drempel}</strong> personen worden niet getoond.</li><li>Een percentage waarvan teller of rest onder <strong>{a.drempel_cel}</strong> ligt, ook niet.</li>"
               "<li>Is één groep onderdrukt, onderdruk dan ook de kleinste zichtbare groep van die uitsplitsing (secundaire onderdrukking).</li></ul>",
    "bijlage": tabel("Kolommen met aantal unieke en ontbrekende waarden", ["Kolom", "Unieke waarden", "Ontbrekend", "Waarden (bij weinig verschillende)"], structuur),
}
aanwezig = [(i, t) for i, t in HOOFDSTUKKEN if inhoud[i]]
menu = "".join(f'<li><a href="#{i}">{e(t)}</a></li>' for i, t in aanwezig)
secties = "\n".join(f'<section id="{i}"><h2>{e(t)}</h2>\n{inhoud[i]}\n</section>' for i, t in aanwezig)

doc = f"""<!doctype html>
<html lang="nl"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="keuzes" content="{e(json.dumps(keuzes, ensure_ascii=False))}">
<title>Dataprofiel</title>
<style>
:root{{--bg:#fff;--fg:#000;--muted:#4b5563;--line:#d1d5db;--accent:#3d68ec;--warn-bg:#fdf3d0;--vlak:#f3f4f6}}
@media (prefers-color-scheme:dark){{:root{{--bg:#111827;--fg:#f9fafb;--muted:#d1d5db;--line:#4b5563;--accent:#9db4ff;--warn-bg:#4a3b00;--vlak:#1f2937}}}}
html{{scroll-behavior:smooth}}body{{background:var(--bg);color:var(--fg);font:16px/1.5 system-ui,sans-serif;margin:0;padding:0 16px 48px}}
.layout{{display:grid;grid-template-columns:200px minmax(0,1fr);gap:32px;max-width:1200px;margin:0 auto}}
nav{{position:sticky;top:0;align-self:start;max-height:100vh;overflow:auto;padding-top:24px}}nav ol{{list-style:none;margin:8px 0;padding:0}}
nav a{{display:block;padding:6px 8px;border-left:3px solid var(--line);color:var(--fg);text-decoration:none}}nav a:hover,nav a:focus{{border-color:var(--accent);background:var(--vlak)}}
@media (max-width:800px){{.layout{{display:block}}nav{{position:static;max-height:none}}}}
h1{{margin:24px 0 4px}}h2{{margin-top:40px;border-bottom:2px solid var(--accent);padding-bottom:4px}}h3{{margin:24px 0 4px}}section{{scroll-margin-top:8px}}
.demo{{background:var(--warn-bg);border-left:6px solid var(--accent);padding:8px 12px;margin:12px 0}}.muted{{color:var(--muted)}}a{{color:var(--accent)}}
.tegels{{display:grid;grid-template-columns:repeat(auto-fit,minmax(130px,1fr));gap:12px;margin:16px 0}}.tegels div{{background:var(--vlak);border-radius:8px;padding:12px}}
.tegels strong{{display:block;font-size:24px}}.tegels span{{color:var(--muted);font-size:14px}}
.wrap{{overflow-x:auto}}table{{border-collapse:collapse;width:100%;font-size:14px}}caption{{text-align:left;font-weight:600;padding:8px 0}}
th,td{{border:1px solid var(--line);padding:4px 8px;text-align:left;vertical-align:top}}th{{background:var(--vlak)}}
.balk{{display:block;min-width:60px;height:12px;background:var(--vlak);border-radius:3px}}.balk span{{display:block;height:100%;background:var(--accent);border-radius:3px}}
.kaarten{{display:grid;grid-template-columns:repeat(auto-fill,minmax(280px,1fr));gap:16px}}figure{{margin:0;border:1px solid var(--line);border-radius:8px;padding:12px}}
figcaption,figure caption,li,p,dd,dt{{overflow-wrap:anywhere}}figcaption{{font-weight:600}}figure td:last-child{{width:40%}}figure p{{margin:4px 0 0;font-size:14px}}figure table{{font-size:13px}}figure td,figure th{{border:0;border-top:1px solid var(--line)}}
svg{{width:100%;height:auto;display:block}}svg rect{{fill:var(--accent)}}svg line{{stroke:var(--line)}}svg text{{fill:var(--muted);font-size:11px}}
.samenhang{{width:auto}}.samenhang td{{text-align:right;color:var(--fg);min-width:48px}}details{{margin:16px 0}}summary{{cursor:pointer;color:var(--accent)}}
</style></head><body><div class="layout">
<nav aria-label="Hoofdstukken"><strong>Dataprofiel</strong><ol>{menu}</ol></nav>
<main>
<h1>Dataprofiel</h1>
{secties}
</main></div></body></html>
"""

# Per stap een korte samenvatting voor het gesprek. Alleen kolomnamen, regels en aantallen rijen: geen waarden
# uit de data. Zo ziet de gebruiker de agent vier stappen zetten, terwijl elke stap hetzelfde script is.
kolom_let_op = {k: v.get("let_op", "") for k, v in kolom_begrip.items()}
rollen = {}
for v in kolom_begrip.values():
    rol = v.get("rol", "").split()[0] if v.get("rol") else "onbekend"
    rollen[rol] = rollen.get(rol, 0) + 1
STAPPEN = {
    1: ("Kolommen begrijpen", [
        f"{len(kolommen)} kolommen en {duizend(n_rijen)} rijen gelezen.",
        "Soorten kolommen: " + ", ".join(f"{n} {r}" for r, n in sorted(rollen.items(), key=lambda x: -x[1])) + "." if rollen else "",
        f"Eén rij is: {begrip['eenheid_rij']}" if begrip.get("eenheid_rij") else "",
        ("Kan niet vergelijken (één waarde): " + ", ".join(een_waarde) + ".") if een_waarde else "",
    ]),
    2: ("Definities en privacy", [
        *[f"{d.get('naam', '')}: {d.get('definitie', '')}" for d in definities],
        f"Privacy: groepen onder {a.drempel} en percentages met minder dan {a.drempel_cel} in teller of rest tonen we niet, "
        "plus secundaire onderdrukking. Dat gebeurt straks vanzelf in het dashboard.",
    ]),
    3: ("Datakwaliteit controleren", [
        (f"Sleutel {' × '.join(sleutel)}: " + ("uniek, elke student staat één keer per jaar in het bestand." if sleutel_tegel == "uniek" else "niet uniek.")) if sleutel else "Geen sleutel opgegeven.",
        "Geen dubbele rijen." if not n_dubbel else f"{n_dubbel} dubbele rijen.",
        *[f"Lege waarden in {k}: {kolom_let_op.get(k) or 'controleer wat leeg betekent.'}" for k, _, _ in ontbrekend_kolom],
        *[f"Leeg in {k} is geen ontbrekende waarde: leeg betekent {betekenis}." for k, _, betekenis in verwacht_leeg],
    ]),
    4: ("Ideeën en aannames", [
        *[f"Hypothese: {h.get('vraag', '')} Andere verklaring: {h.get('alternatieve_verklaring', '')}" for h in ideeen.get("hypotheses", [])],
        *[f"Aanname: {x}" for x in begrip.get("aannames", [])],
    ]),
}


def toon_stap(nummer):
    titel, regels = STAPPEN[nummer]
    print(f"Stap {nummer} van 4: {titel}")
    for regel in regels:
        if regel:
            print(f"- {regel}")


if a.stap in (1, 2, 3):
    toon_stap(a.stap)
    sys.exit()

uit = Path(a.uit)
uit.parent.mkdir(parents=True, exist_ok=True)
uit.write_text(doc, encoding="utf-8")
if a.stap == 4:
    toon_stap(4)
else:
    for nummer in STAPPEN:
        toon_stap(nummer)
print(f"Geschreven: {uit}")
