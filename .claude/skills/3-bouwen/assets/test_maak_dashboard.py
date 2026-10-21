"""Onderhoudstests voor maak_dashboard.py. Niet voor de workshop: draai ze na een wijziging aan de motor.

    uv run --no-project --with polars==1.44.2 --with pytest==9.1.1 python -m pytest .claude/skills/3-bouwen/assets

Ze rekenen de uitkomsten op de demodata onafhankelijk na en controleren dat dezelfde keuzes twee keer
hetzelfde dashboard geven.
"""

import re
import subprocess
import sys
from pathlib import Path

import polars as pl
import pytest

REPO = Path(__file__).resolve().parents[4]
SCRIPT = Path(__file__).resolve().parent / "maak_dashboard.py"
DATA = REPO / "data" / "demodata_1cho.csv"


def maak(tmp_path: Path, *args: str) -> tuple[subprocess.CompletedProcess, str]:
    uit = tmp_path / "dashboard.html"
    resultaat = subprocess.run([sys.executable, str(SCRIPT), *args, "--uit", str(uit)], capture_output=True,
                               text=True, cwd=REPO)
    return resultaat, uit.read_text(encoding="utf-8") if uit.is_file() else ""


def lees_eerstejaars() -> pl.DataFrame:
    d = pl.read_csv(DATA, separator=";", infer_schema=False).with_columns(pl.col("inschrijvingsjaar").cast(pl.Int32))
    return d, d.filter(pl.col("verblijfsjaar_actuele_instelling") == "1")


def test_stoppen_per_sector_klopt(tmp_path: Path) -> None:
    resultaat, pagina = maak(tmp_path, "data/demodata_1cho.csv", "--vraag", "A", "--uitsplitsing", "sector")
    assert resultaat.returncode == 0, resultaat.stderr
    d, eerst = lees_eerstejaars()
    laatste = d["inschrijvingsjaar"].max()
    volgend = set(zip(d["persoonsgebonden_nummer"], d["inschrijvingsjaar"].to_list(), strict=True))
    eerst = eerst.filter(pl.col("inschrijvingsjaar") < laatste)
    gestopt = [(p, j + 1) not in volgend for p, j in zip(eerst["persoonsgebonden_nummer"], eerst["inschrijvingsjaar"], strict=True)]
    totaal = round(100 * sum(gestopt) / len(gestopt))
    alles = pagina.split('data-filter="alle"')[1]
    assert re.search(rf"<strong>{totaal}%</strong><span>Stopt na het eerste jaar", alles)
    techniek = eerst.with_columns(pl.Series("gestopt", gestopt)).filter(pl.col("croho_onderdeel_actuele_opleiding") == "techniek")
    assert f"Techniek</span><span><strong>{round(100 * techniek['gestopt'].mean())}%" in alles


def test_diploma_telt_alleen_waarneembare_jaren(tmp_path: Path) -> None:
    resultaat, pagina = maak(tmp_path, "data/demodata_1cho.csv", "--vraag", "B")
    assert resultaat.returncode == 0, resultaat.stderr
    d, eerst = lees_eerstejaars()
    meetellend = eerst.filter(pl.col("inschrijvingsjaar") + 4 <= d["inschrijvingsjaar"].max()).height
    assert f"<strong>{meetellend:,}</strong>".replace(",", ".") in pagina.split('data-filter="alle"')[1]


@pytest.mark.parametrize("vraag", ["A", "B", "C"])
def test_zelfde_keuzes_geven_hetzelfde_dashboard(tmp_path: Path, vraag: str) -> None:
    _, eerste = maak(tmp_path, "data/demodata_1cho.csv", "--vraag", vraag)
    _, tweede = maak(tmp_path, "data/demodata_1cho.csv", "--vraag", vraag)
    assert eerste == tweede


def test_geen_rijen_in_het_dashboard(tmp_path: Path) -> None:
    _, pagina = maak(tmp_path, "data/demodata_1cho.csv", "--vraag", "A")
    eerste_nummer = pl.read_csv(DATA, separator=";", infer_schema=False, n_rows=1)["persoonsgebonden_nummer"][0]
    assert eerste_nummer not in pagina


def test_onbekend_bestand_geeft_een_melding(tmp_path: Path) -> None:
    resultaat, _ = maak(tmp_path, "data/bestaat_niet.csv")
    assert resultaat.returncode == 1 and "Traceback" not in resultaat.stderr


def test_aanpassingen_zijn_uitvoerbaar(tmp_path: Path) -> None:
    resultaat, _ = maak(tmp_path, "data/demodata_1cho.csv", "--vraag", "A")
    for regel in resultaat.stdout.splitlines():
        if regel.startswith("- ") and "=>" in regel:
            extra = regel.split("=>")[1].split()
            opnieuw, pagina = maak(tmp_path, "--vanaf", str(tmp_path / "dashboard.html"), *extra)
            assert opnieuw.returncode == 0, opnieuw.stderr
            assert "<h2>" in pagina


def test_controle_staat_tekst_toe_maar_geen_cijfers(tmp_path: Path) -> None:
    maak(tmp_path, "data/demodata_1cho.csv", "--vraag", "A")
    pad = tmp_path / "dashboard.html"
    controle = [sys.executable, str(SCRIPT), "--vanaf", str(pad), "--controleer"]
    pagina = pad.read_text(encoding="utf-8")
    pad.write_text(pagina.replace("Verschilt het stoppen per sector?", "Waar stoppen de meeste eerstejaars?")
                   .replace("var(--npuls-blauw); border-radius: 9999px; }", "var(--npuls-oranje); border-radius: 9999px; }"),
                   encoding="utf-8")
    assert subprocess.run(controle, capture_output=True, cwd=REPO).returncode == 0
    pad.write_text(pagina.replace("<strong>23%</strong>", "<strong>25%</strong>", 1), encoding="utf-8")
    assert subprocess.run(controle, capture_output=True, cwd=REPO).returncode == 1


def test_een_aanpassing_komt_niet_terug(tmp_path: Path) -> None:
    resultaat, _ = maak(tmp_path, "data/demodata_1cho.csv", "--vraag", "A", "--uitsplitsing", "sector")
    assert "--uitsplitsing sector,opleiding" in resultaat.stdout
    maak(tmp_path, "--vanaf", str(tmp_path / "dashboard.html"), "--volgorde", "jaar")
    terug, _ = maak(tmp_path, "--vanaf", str(tmp_path / "dashboard.html"), "--volgorde", "groep")
    aanbod = [r for r in terug.stdout.splitlines() if r.startswith("- ")]
    assert aanbod and not any("--volgorde" in r for r in aanbod)


def test_meer_vergelijkingen_worden_een_wissel(tmp_path: Path) -> None:
    resultaat, pagina = maak(tmp_path, "data/demodata_1cho.csv", "--vraag", "A", "--uitsplitsing", "sector,opleiding")
    assert resultaat.returncode == 0, resultaat.stderr
    assert '<select id="uitsplitsing" data-wissel>' in pagina
    alles = pagina.split('data-filter="alle"')[1].split('data-filter="')[0]
    assert 'data-uitsplitsing="sector"' in alles and 'data-uitsplitsing="opleiding"' in alles


def test_twee_filters_geven_elke_combinatie(tmp_path: Path) -> None:
    resultaat, pagina = maak(tmp_path, "data/demodata_1cho.csv", "--vraag", "A", "--uitsplitsing", "sector",
                             "--filter", "vestiging,geslacht")
    assert resultaat.returncode == 0, resultaat.stderr
    d = pl.read_csv(DATA, separator=";", infer_schema=False)
    vestigingen = d["vestigingsnummer_gemeentenaam_volgens_rio"].drop_nulls().n_unique()
    geslachten = d["geslacht"].drop_nulls().n_unique()
    assert len(re.findall(r'<div data-filter="[^"]*\|[^"]*">', pagina)) == (vestigingen + 1) * (geslachten + 1)
    assert '<select id="filter2" data-filterkeuze>' in pagina


def test_te_veel_keuzes_geeft_een_melding(tmp_path: Path) -> None:
    resultaat, _ = maak(tmp_path, "data/demodata_1cho.csv", "--vraag", "A",
                        "--uitsplitsing", "sector,opleiding,geslacht,vooropleiding")
    assert resultaat.returncode == 1 and "hooguit 3 vergelijkingen" in resultaat.stderr


def test_dashboard_blijft_klein_bij_de_meeste_keuzes(tmp_path: Path) -> None:
    resultaat, pagina = maak(tmp_path, "data/demodata_1cho.csv", "--vraag", "B",
                             "--uitsplitsing", "opleiding,vooropleiding,sector", "--filter", "vestiging,geslacht")
    assert resultaat.returncode == 0, resultaat.stderr
    assert len(pagina.encode("utf-8")) < 1_000_000


def test_de_kern_van_de_vraag_staat_er_altijd_bij(tmp_path: Path) -> None:
    resultaat, pagina = maak(tmp_path, "data/demodata_1cho.csv", "--vraag", "C", "--uitsplitsing", "sector,geslacht",
                             "--filter", "vestiging")
    assert resultaat.returncode == 0, resultaat.stderr
    wissel = re.search(r'<select id="uitsplitsing" data-wissel>(.*?)</select>', pagina).group(1)
    assert re.findall(r'value="([^"]*)"', wissel) == ["vooropleiding", "sector", "geslacht"]
