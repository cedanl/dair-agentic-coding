"""Onderhoudstests voor maak_dashboard.py. Niet voor de workshop: draai ze na een wijziging aan de motor.

    uv run --no-project --with polars==1.44.2 --with pytest==9.1.1 python -m pytest .claude/skills/bouwen_dashboard/assets

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


def test_gok_bevat_het_goede_antwoord(tmp_path: Path) -> None:
    gok = subprocess.run([sys.executable, str(SCRIPT), "data/demodata_1cho.csv", "--vraag", "A", "--gok"],
                         capture_output=True, text=True, cwd=REPO)
    resultaat, _ = maak(tmp_path, "data/demodata_1cho.csv", "--vraag", "A")
    hoogst = re.search(r"Hoogst: (.+?) \(", resultaat.stdout).group(1)
    assert gok.returncode == 0 and hoogst in gok.stdout.splitlines()[1]
    assert not (tmp_path / "x").exists()


def test_aanpassingen_zijn_uitvoerbaar(tmp_path: Path) -> None:
    resultaat, _ = maak(tmp_path, "data/demodata_1cho.csv", "--vraag", "A")
    for regel in resultaat.stdout.splitlines():
        if regel.startswith("- ") and "=>" in regel:
            extra = regel.split("=>")[1].split()
            opnieuw, pagina = maak(tmp_path, "--vanaf", str(tmp_path / "dashboard.html"), *extra)
            assert opnieuw.returncode == 0, opnieuw.stderr
            assert "<h2>" in pagina
