"""Maakt een HTML-dataprofiel uit een CSV. Draait zonder AI, ook op andere data.

Gebruik:
    python verken.py data/bestand.csv --begrip begrip.json --uit uitvoer/data-profiel.html
    python verken.py data/demo.csv --demo               # demodata: label en de waarden bij weinig verschillende waarden
    python verken.py data/echt.csv                      # elke andere data: geen label en geen waarden in het profiel

Het script bevat geen waarden uit de data en geen conclusies. Het rekent de structuur uit (rijen,
kolommen, unieke en ontbrekende waarden, groepsgroottes) en zet de tekst uit begrip.json erbij. Alles wat
iets over het domein zegt (betekenis van kolommen, definities, aanpakken) komt uit begrip.json.

Installeren: uv pip install duckdb
"""
import argparse
import html
import json
from pathlib import Path

import duckdb

p = argparse.ArgumentParser()
p.add_argument("csv")
p.add_argument("--begrip", help="JSON met de tekst van de gebruiker: datagebruik, jouw_aanpak, keuzes, kolommen, definities, casus_ideeen, casus_aanpak")
p.add_argument("--uit", default="uitvoer/data-profiel.html")
p.add_argument("--sep", default=";", help="scheidingsteken van de CSV")
p.add_argument("--demo", action="store_true", help="de data is demodata: toon het demodata-label en de waarden bij weinig verschillende waarden")
p.add_argument("--uitsplitsing", action="append", default=[], help="kolom om mee uit te splitsen (herhaalbaar)")
p.add_argument("--drempel", type=int, default=30, help="minimale groepsgrootte")
p.add_argument("--drempel-cel", type=int, default=5, help="minimale teller of rest bij een percentage")
p.add_argument("--max-waarden", type=int, default=6, help="toon de waarden zelf bij hooguit zoveel verschillende")
a = p.parse_args()

e = html.escape
con = duckdb.connect()
bron = f"read_csv('{a.csv}', delim='{a.sep}', header=true, all_varchar=true)"
q = lambda sql: con.sql(sql).fetchall()
begrip = json.loads(Path(a.begrip).read_text(encoding="utf-8")) if a.begrip else {}

kolommen = [r[0] for r in q(f"describe select * from {bron}")]
n_rijen = q(f"select count(*) from {bron}")[0][0]
structuur = []
for k in kolommen:
    # een lege waarde telt mee als waarde: een kolom met alleen "ingevuld" en "leeg" heeft twee toestanden
    uniek, leeg = q(f'select count(distinct coalesce(trim("{k}"), \'\')), count(*) filter (where "{k}" is null or trim("{k}") = \'\') from {bron}')[0]
    waarden = ""
    if uniek <= a.max_waarden and a.demo:
        waarden = ", ".join(f"{w} ({n})" for w, n in q(
            f"select coalesce(nullif(trim(\"{k}\"), ''), '(leeg)'), count(*) from {bron} group by 1 order by 2 desc"))
    structuur.append((k, uniek, leeg, waarden))
een_waarde = [k for k, u, _, _ in structuur if u == 1]


def tabel(caption, kop, rijen):
    t = f"<table><caption>{e(caption)}</caption><thead><tr>" + "".join(f'<th scope="col">{e(c)}</th>' for c in kop) + "</tr></thead><tbody>"
    for r in rijen:
        t += "<tr>" + "".join(f"<td>{e(str(c))}</td>" for c in r) + "</tr>"
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

kolom_begrip = begrip.get("kolommen", {})
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
