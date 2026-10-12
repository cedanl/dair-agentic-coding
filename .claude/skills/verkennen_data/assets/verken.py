"""Maakt een HTML-dataprofiel uit een CSV. Draait zonder AI, ook op andere data.

Gebruik:
    python verken.py data/bestand.csv --begrip begrip.json --uit uitvoer/data-profiel.html
    python verken.py data/demo.csv --demo               # demodata: label en de waarden bij weinig verschillende waarden
    python verken.py data/echt.csv                      # elke andere data: geen label en geen waarden in het profiel
    python verken.py data/bestand.csv --sleutel persoon --sleutel jaar --uitsplitsing groep

Het script bevat geen waarden uit de data en geen conclusies. Het rekent de structuur uit (rijen,
kolommen, unieke en ontbrekende waarden, groepsgroottes), controleert de kwaliteit (sleutel, dubbele rijen,
typen, ontbrekende waarden per groep) en rekent de verdeling van getalkolommen uit. De tekst uit begrip.json
komt erbij. Alles wat iets over het domein zegt (betekenis van kolommen, definities, aanpakken) komt uit
begrip.json.

Installeren: uv pip install duckdb
"""
import argparse
import html
import json
import sys
from pathlib import Path

import duckdb

p = argparse.ArgumentParser()
p.add_argument("csv")
p.add_argument("--begrip", help="JSON met de tekst van de gebruiker: datagebruik, jouw_aanpak, keuzes, kolommen, definities, casus_ideeen, casus_aanpak")
p.add_argument("--uit", default="uitvoer/data-profiel.html")
p.add_argument("--sep", default=";", help="scheidingsteken van de CSV")
p.add_argument("--demo", action="store_true", help="de data is demodata: toon het demodata-label en de waarden bij weinig verschillende waarden")
p.add_argument("--uitsplitsing", action="append", default=[], help="kolom om mee uit te splitsen (herhaalbaar)")
p.add_argument("--sleutel", action="append", default=[], help="kolom die samen met de andere sleutelkolommen één rij uniek maakt (herhaalbaar)")
p.add_argument("--drempel", type=int, default=30, help="minimale groepsgrootte")
p.add_argument("--drempel-cel", type=int, default=5, help="minimale teller of rest bij een percentage")
p.add_argument("--max-waarden", type=int, default=6, help="toon de waarden zelf bij hooguit zoveel verschillende")
a = p.parse_args()

TYPE_AANDEEL = 0.9  # een kolom krijgt een type als minstens dit deel van de ingevulde waarden erin past
ID_AANDEEL = 0.9  # vrijwel alleen unieke waarden: de kolom lijkt een identificatie
ONGELIJK = 0.2  # verschil in aandeel ontbrekend tussen groepen dat als ongelijk telt
GETAL = "try_cast(replace(v, ',', '.') as double)"  # een decimale komma telt als getal

e = html.escape
con = duckdb.connect()
bron = f"read_csv('{a.csv}', delim='{a.sep}', header=true, all_varchar=true)"
q = lambda sql: con.sql(sql).fetchall()
begrip = json.loads(Path(a.begrip).read_text(encoding="utf-8")) if a.begrip else {}

kolommen = [r[0] for r in q(f"describe select * from {bron}")]
kolom_begrip = begrip.get("kolommen", {})
sleutel = a.sleutel or begrip.get("sleutel", [])
onbekend = [k for k in a.uitsplitsing + sleutel if k not in kolommen]
if onbekend:
    sys.exit(f"Kolom niet gevonden in {Path(a.csv).name}: {', '.join(onbekend)}")


def waarde(k):
    return f"nullif(trim(\"{k}\"), '')"


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
            f"select coalesce(nullif(trim(\"{k}\"), ''), '(leeg)'), count(*) from {bron} group by 1 order by 2 desc"))
    structuur.append((k, uniek, leeg, waarden))
een_waarde = [k for k, u, _, _ in structuur if u == 1]


def tabel(caption, kop, rijen, html_kolom=None):
    t = f"<table><caption>{e(caption)}</caption><thead><tr>" + "".join(f'<th scope="col">{e(c)}</th>' for c in kop) + "</tr></thead><tbody>"
    for r in rijen:
        t += "<tr>" + "".join(f"<td>{c if i == html_kolom else e(str(c))}</td>" for i, c in enumerate(r)) + "</tr>"
    return t + "</tbody></table>"


def sectie(titel, inhoud):
    return f"<h2>{e(titel)}</h2>\n{inhoud}\n" if inhoud else ""


# Groepsgroottes per uitsplitsing: alleen aantallen, geen namen van groepen
groepen_html = ""
if a.uitsplitsing:
    cols = ", ".join(f'"{c}"' for c in a.uitsplitsing)
    groottes = [r[0] for r in q(f"select count(*) from {bron} group by {cols}")]
    klein = sum(1 for n in groottes if n < a.drempel)
    groepen_html = (f"<p>Uitsplitsing {e(' × '.join(a.uitsplitsing))}: {len(groottes)} groepen, waarvan {klein} met minder dan "
                    f"{a.drempel} rijen. Een indicatie van de structuur; op andere data zijn de aantallen anders. "
                    "Let op: dit telt rijen, geen personen.</p>")


def getal(x):
    return str(int(x)) if float(x).is_integer() else f"{x:.2f}".replace(".", ",")


def procent(x):
    return f"{round(100 * x)}%"


def boxplot(p5, q1, mediaan, q3, p95):
    if p95 == p5:
        return ""
    x = lambda v: round(4 + 152 * (v - p5) / (p95 - p5), 1)
    return (f'<svg width="160" height="20" viewBox="0 0 160 20" aria-hidden="true"><line x1="4" x2="156" y1="10" y2="10" stroke="currentColor"/>'
            f'<rect x="{x(q1)}" y="3" width="{round(x(q3) - x(q1), 1)}" height="14" fill="var(--accent)"/>'
            f'<line x1="{x(mediaan)}" x2="{x(mediaan)}" y1="1" y2="19" stroke="var(--bg)" stroke-width="2"/></svg>')


# Datakwaliteit: wat één rij is, of de sleutel uniek is, dubbele rijen, typen en ontbrekende waarden per groep
kwaliteit = [f"Eén rij is: {e(begrip['eenheid_rij'])}"] if begrip.get("eenheid_rij") else []
if sleutel:
    cols = ", ".join(f'"{c}"' for c in sleutel)
    n_sleutels = q(f"select count(*) from (select distinct {cols} from {bron})")[0][0]
    naam = e(" × ".join(sleutel))
    kwaliteit.append(f"De sleutel {naam} is uniek: elke rij heeft een eigen combinatie." if n_sleutels == n_rijen else
                     f"De sleutel {naam} is <strong>niet uniek</strong>: {n_rijen - n_sleutels} rijen delen hun sleutel met een eerdere rij. "
                     "Een telling van rijen telt dan iets anders dan een telling van sleutels.")
else:
    kwaliteit.append("Er is geen sleutel opgegeven, dus het is niet gecontroleerd wat één rij voorstelt. Geef de kolommen op met <code>--sleutel</code>.")
n_dubbel = n_rijen - q(f"select count(*) from (select distinct * from {bron})")[0][0]
kwaliteit.append(f"{n_dubbel} rijen zijn een exacte kopie van een eerdere rij." if n_dubbel else "Er zijn geen exact dubbele rijen.")

type_rijen = [(k, soort, past_niet) for k, (soort, past_niet, _, _) in typen.items() if soort != "tekst"]

ontbrekend_rijen = []
if a.uitsplitsing:
    cols = ", ".join(f'"{c}"' for c in a.uitsplitsing)
    for k, _, leeg, _ in structuur:
        if not leeg or k in a.uitsplitsing:
            continue
        laagste, hoogste, n_groepen = q(f"select min(aandeel), max(aandeel), count(*) from (select count(*) filter (where {waarde(k)} is null) / count(*) aandeel "
                                        f"from {bron} group by {cols} having count(*) >= {a.drempel})")[0]
        if n_groepen:
            ontbrekend_rijen.append((hoogste - laagste, k, procent(laagste), procent(hoogste), "ongelijk" if hoogste - laagste >= ONGELIJK else ""))
    ontbrekend_rijen = [r[1:] for r in sorted(ontbrekend_rijen, reverse=True)]

# Verdelingen: alleen getalkolommen die geen identificatie of categorie zijn
onderdrukt = f"onderdrukt (minder dan {a.drempel_cel} rijen)"
verdeling_rijen = []
for k, (soort, past_niet, uniek, ingevuld) in typen.items():
    rol = kolom_begrip.get(k, {}).get("rol", "").lower()
    n = ingevuld - past_niet
    if soort != "getal" or k in sleutel or uniek <= a.max_waarden or rol.startswith(("identificatie", "categorie")):
        continue
    if not rol and uniek >= ID_AANDEEL * ingevuld:
        continue
    if n < a.drempel:
        verdeling_rijen.append((k, n, *["te weinig waarden"] * 6, ""))
        continue
    laagste, hoogste, kw, n_laagste, n_hoogste, n_uitschieters = q(
        f"with g as (select {GETAL} x from (select {waarde(k)} v from {bron})), "
        "s as (select min(x) mn, max(x) mx, quantile_cont(x, [0.05, 0.25, 0.5, 0.75, 0.95]) kw from g) "
        "select mn, mx, kw, (select count(*) from g where x = mn), (select count(*) from g where x = mx), "
        "(select count(*) from g where x < kw[2] - 1.5 * (kw[4] - kw[2]) or x > kw[4] + 1.5 * (kw[4] - kw[2])) from s")[0]
    verdeling_rijen.append((
        k, n,
        getal(laagste) if n_laagste >= a.drempel_cel else onderdrukt,
        getal(kw[1]), getal(kw[2]), getal(kw[3]),
        getal(hoogste) if n_hoogste >= a.drempel_cel else onderdrukt,
        n_uitschieters if n_uitschieters == 0 or n_uitschieters >= a.drempel_cel else f"minder dan {a.drempel_cel}",
        boxplot(*kw)))

kwaliteit_html = "<ul>" + "".join(f"<li>{x}</li>" for x in kwaliteit) + "</ul>"
if type_rijen:
    kwaliteit_html += '<div class="wrap">' + tabel("Kolommen met een getal of datum, en hoeveel ingevulde waarden daar niet in passen", ["Kolom", "Voorgesteld type", "Past niet"], type_rijen) + "</div>"
if ontbrekend_rijen:
    kwaliteit_html += ('<div class="wrap">' + tabel(f"Aandeel ontbrekend per groep van {' × '.join(a.uitsplitsing)} (alleen groepen vanaf {a.drempel} rijen)",
                                                   ["Kolom", "Laagste aandeel", "Hoogste aandeel", "Verschil"], ontbrekend_rijen) + "</div>"
                       "<p class='muted'>Ongelijk betekent: in de ene groep ontbreekt veel meer dan in de andere. Een vergelijking tussen groepen op die kolom is dan scheef.</p>")
verdeling_html = ""
if verdeling_rijen:
    verdeling_html = ('<div class="wrap">' + tabel("Verdeling per getalkolom", ["Kolom", "Aantal", "Laagste", "Kwartiel 1", "Mediaan", "Kwartiel 3", "Hoogste", "Uitschieters", "5% tot 95%"], verdeling_rijen, html_kolom=8) + "</div>"
                      f"<p class='muted'>De laagste en hoogste waarde staan er alleen als minstens {a.drempel_cel} rijen die waarde hebben: anders wijst het getal één rij aan. "
                      "Uitschieters liggen meer dan anderhalf keer de afstand tussen kwartiel 1 en 3 buiten die kwartielen. De balk loopt van 5% tot 95%, het blok van kwartiel 1 tot 3, de streep is de mediaan. "
                      "Deze cijfers beschrijven dit bestand; op andere data zijn ze anders.</p>")

begrip_rijen = [(k, v.get("rol", ""), v.get("betekenis", ""), v.get("let_op", "")) for k, v in kolom_begrip.items()]
definities = begrip.get("definities", [])
ideeen = begrip.get("casus_ideeen", {})


def lijst(items):
    return "<ul>" + "".join(f"<li>{i}</li>" for i in items) + "</ul>" if items else ""


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
    return "".join(delen)

aanpak = begrip.get("casus_aanpak", [])
aanpak_html = "".join(
    f"<li><strong>{e(x.get('idee', ''))}</strong><br>Maat: {e(x.get('maat', ''))}. Uitsplitsing: {e(x.get('uitsplitsing', ''))}."
    f"<br><span class='muted'>Kan niet zeggen: {e(x.get('kan_niet', ''))}</span></li>" for x in aanpak)

demo = '<p class="demo"><strong>Dit is demodata.</strong> Het profiel beschrijft wat er in het bestand zit, niet wat er in de werkelijkheid geldt.</p>' if a.demo else ""
doc = f"""<!doctype html>
<html lang="nl"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Dataprofiel</title>
<style>
:root{{--bg:#fff;--fg:#000;--muted:#4b5563;--line:#d1d5db;--accent:#3d68ec;--warn-bg:#fdf3d0}}
@media (prefers-color-scheme:dark){{:root{{--bg:#111827;--fg:#f9fafb;--muted:#d1d5db;--line:#4b5563;--accent:#9db4ff;--warn-bg:#4a3b00}}}}
body{{background:var(--bg);color:var(--fg);font:16px/1.5 system-ui,sans-serif;margin:0;padding:0 16px 48px}}
main{{max-width:960px;margin:0 auto}}h1{{margin:24px 0 4px}}h2{{margin-top:32px;border-bottom:2px solid var(--accent);padding-bottom:4px}}h3{{margin:20px 0 4px}}
.demo{{background:var(--warn-bg);border-left:6px solid var(--accent);padding:8px 12px;margin:12px 0}}
.wrap{{overflow-x:auto}}table{{border-collapse:collapse;width:100%;font-size:14px}}caption{{text-align:left;font-weight:600;padding:8px 0}}
th,td{{border:1px solid var(--line);padding:4px 8px;text-align:left;vertical-align:top}}th{{background:rgba(61,104,236,.12)}}.muted{{color:var(--muted)}}
</style></head><body><main>
<h1>Dataprofiel</h1>
<p class="muted">Bestand: {e(Path(a.csv).name)}</p>
{demo}
{sectie("Datagebruik", f"<p>{e(begrip['datagebruik'])}</p>" if begrip.get("datagebruik") else "")}
{sectie("Jouw aanpak", f"<p>{e(begrip['jouw_aanpak'])}</p>" if begrip.get("jouw_aanpak") else "")}
{sectie("Keuzes van de gebruiker", "<ul>" + "".join(f"<li>{e(k)}</li>" for k in begrip.get("keuzes", [])) + "</ul>" if begrip.get("keuzes") else "")}
{sectie("Wat de kolommen kunnen betekenen", '<div class="wrap">' + tabel("Rol, betekenis (aanname) en aandachtspunt per kolom", ["Kolom", "Rol", "Betekenis", "Let op"], begrip_rijen) + "</div>" if begrip_rijen else "")}
{sectie("Definities", "<dl>" + "".join(f"<dt>{e(d.get('naam', ''))}</dt><dd>{e(d.get('definitie', ''))}</dd>" for d in definities) + "</dl>" if definities else "")}
{sectie("Casusgerichte ideeën", ideeen_html())}
{sectie("Hoe de vraag aan te vliegen", f"<ol>{aanpak_html}</ol>" if aanpak_html else "")}
{sectie("Privacyregels", f"{groepen_html}<ul><li>Groepen onder <strong>{a.drempel}</strong> personen worden niet getoond.</li><li>Een percentage waarvan teller of rest onder <strong>{a.drempel_cel}</strong> ligt, ook niet.</li><li>Is één groep onderdrukt, onderdruk dan ook de kleinste zichtbare groep van die uitsplitsing (secundaire onderdrukking).</li></ul>")}
{sectie("Datakwaliteit", kwaliteit_html)}
{sectie("Verdelingen", verdeling_html)}
<h2>Bijlage: structuur van de data</h2>
<ul><li>{f"{n_rijen:,}".replace(",", ".")} rijen, {len(kolommen)} kolommen</li></ul>
{"<p><strong>Kolommen met één waarde</strong> (kunnen niet uitsplitsen): " + e(", ".join(een_waarde)) + "</p>" if een_waarde else ""}
<div class="wrap">{tabel("Kolommen met aantal unieke en ontbrekende waarden", ["Kolom", "Unieke waarden", "Ontbrekend", "Waarden (bij weinig verschillende)"], structuur)}</div>
</main></body></html>
"""

uit = Path(a.uit)
uit.parent.mkdir(parents=True, exist_ok=True)
uit.write_text(doc, encoding="utf-8")
print(f"Geschreven: {uit}")
