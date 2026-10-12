"""Zoekt waarden uit de voorbeelddata die letterlijk in de code staan. Draait zonder AI.

Gebruik:
    python controleer_voorbeeldwaarden.py data/voorbeeld.csv app.py berekeningen.py configuratie.py

Het dashboard moet op andere data draaien. Een groepsnaam of code uit de voorbeelddata in de code breekt dat.
Het script leest de waarden van kolommen met weinig verschillende waarden en meldt elke tekst tussen
aanhalingstekens in de code die gelijk is aan zo'n waarde. Draai het alleen op voorbeelddata: de melding
toont de gevonden waarde.

Installeren: uv pip install duckdb
"""
import argparse
import ast
import sys
from pathlib import Path

import duckdb

p = argparse.ArgumentParser()
p.add_argument("csv")
p.add_argument("code", nargs="+", help="de Python-bestanden van het dashboard")
p.add_argument("--sep", default=";", help="scheidingsteken van de CSV")
p.add_argument("--max-waarden", type=int, default=50, help="controleer kolommen met hooguit zoveel verschillende waarden")
a = p.parse_args()

con = duckdb.connect()
bron = f"read_csv('{a.csv}', delim='{a.sep}', header=true, all_varchar=true)"
q = lambda sql: con.sql(sql).fetchall()

# waarde -> kolommen waarin die voorkomt; één teken is te kort om iets te zeggen
waarden = {}
for k in [r[0] for r in q(f"describe select * from {bron}")]:
    gevonden = q(f'select distinct trim("{k}") from {bron} where length(trim("{k}")) > 1 limit {a.max_waarden + 1}')
    if len(gevonden) <= a.max_waarden:
        for (w,) in gevonden:
            waarden.setdefault(w, []).append(k)

treffers = []
for pad in a.code:
    for knoop in ast.walk(ast.parse(Path(pad).read_text(encoding="utf-8"))):
        if isinstance(knoop, ast.Constant) and isinstance(knoop.value, str) and knoop.value.strip() in waarden:
            treffers.append(f"{pad}:{knoop.lineno}: \"{knoop.value.strip()}\" is een waarde uit kolom {', '.join(waarden[knoop.value.strip()])}")

if treffers:
    print("\n".join(treffers))
    sys.exit(f"{len(treffers)} keer staat een waarde uit de voorbeelddata in de code. Haal die uit de data zelf, of leg uit waarom het geen datawaarde is.")
print("Geen waarden uit de voorbeelddata gevonden in de code.")
