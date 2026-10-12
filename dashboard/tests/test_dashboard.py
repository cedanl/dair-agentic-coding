"""Tests voor het dashboard: berekeningen, privacyregels en de schermen.

Draai vanuit de map `dashboard`:
    uv run --no-project --with-requirements requirements.txt --with pytest pytest tests
"""

import io
import sys
from pathlib import Path

import polars as pl
import pytest
from streamlit.testing.v1 import AppTest

sys.path.insert(0, str(Path(__file__).parent.parent))

import berekeningen as ber  # noqa: E402
import configuratie as cfg  # noqa: E402

DEMODATA = Path(__file__).parent.parent.parent / "data" / "demodata_1cho.csv"
APP = str(Path(__file__).parent.parent / "app.py")


@pytest.fixture(scope="module")
def verbinding():
    with open(DEMODATA, "rb") as bestand:
        return ber.maak_verbinding(ber.lees_csv(bestand))


@pytest.fixture(scope="module")
def verwacht():
    """Onafhankelijke telling per sector en instroomjaar, rechtstreeks uit de CSV met Polars."""
    df = pl.read_csv(DEMODATA, separator=";", infer_schema=False).select(cfg.VERPLICHT)
    df = df.with_columns(
        pl.col(cfg.JAAR).cast(pl.Int64),
        pl.col(cfg.VERBLIJFSJAAR).cast(pl.Int64),
    )
    laatste = df[cfg.JAAR].max()
    heeft_diploma = (
        df.group_by(cfg.PERSOON)
        .agg(pl.col(cfg.DIPLOMAJAAR).is_not_null().any().alias("diploma"))
        .to_dict(as_series=False)
    )
    diploma = dict(zip(heeft_diploma[cfg.PERSOON], heeft_diploma["diploma"], strict=True))
    aanwezig = set(zip(df[cfg.PERSOON], df[cfg.JAAR], strict=True))
    instromers = (
        df.filter((pl.col(cfg.VERBLIJFSJAAR) == 1) & (pl.col(cfg.JAAR) < laatste))
        .select(cfg.PERSOON, cfg.JAAR, cfg.SECTOR)
        .unique()
    )
    uitval = [
        (persoon, jaar + 1) not in aanwezig and not diploma[persoon]
        for persoon, jaar in zip(instromers[cfg.PERSOON], instromers[cfg.JAAR], strict=True)
    ]
    return (
        instromers.with_columns(pl.Series("uitval", uitval))
        .group_by(cfg.SECTOR, cfg.JAAR)
        .agg(pl.len().alias("n"), pl.col("uitval").sum().alias("uitval"))
    )


def test_laatste_jaar_is_geen_instroomjaar(verbinding):
    jaren, laatste = ber.bepaal_waarneembare_jaren(verbinding)
    assert jaren
    assert max(jaren) < laatste


def test_aantallen_per_sector_en_jaar_komen_overeen_met_onafhankelijke_telling(
    verbinding, verwacht
):
    jaren, _ = ber.bepaal_waarneembare_jaren(verbinding)
    sectoren = ber.haal_sectoren_op(verbinding)
    per_sector = ber.bereken_uitval_per_sector_en_jaar(verbinding, jaren, sectoren)
    verwacht_dict = {
        (rij[cfg.SECTOR], rij[cfg.JAAR]): (rij["n"], rij["uitval"])
        for rij in verwacht.iter_rows(named=True)
    }
    assert verwacht_dict
    for sector, groepen in per_sector.items():
        for groep in groepen:
            assert verwacht_dict[(sector, int(groep.naam))] == (groep.n, groep.uitval)


def test_groepen_onder_de_drempel_krijgen_geen_percentage(verbinding):
    jaren, _ = ber.bepaal_waarneembare_jaren(verbinding)
    per_sector = ber.bereken_uitval_per_sector_en_jaar(
        verbinding, jaren, ber.haal_sectoren_op(verbinding)
    )
    for groepen in per_sector.values():
        for groep in groepen:
            if groep.n < cfg.DREMPEL_GROEP:
                assert groep.aandeel is None
                assert not ber.mag_aantal_tonen(groep)
            if groep.aandeel is not None:
                assert groep.uitval >= cfg.DREMPEL_CEL
                assert groep.n - groep.uitval >= cfg.DREMPEL_CEL


def test_een_onderdrukte_groep_onderdrukt_ook_de_kleinste_zichtbare():
    groepen = [
        ber.Groep("a", 10, 3, None, None),
        ber.Groep("b", 100, 20, None, None),
        ber.Groep("c", 300, 60, None, None),
    ]
    resultaat = ber.pas_privacy_toe(groepen)
    assert [g.reden is None for g in resultaat] == [False, False, True]
    assert resultaat[1].reden == ber.REDEN_EXTRA


def test_ontbrekende_kolommen_worden_gemeld():
    with pytest.raises(ber.OntbrekendeKolommenError) as fout:
        ber.lees_csv(io.BytesIO(b"a;b\n1;2\n"))
    assert set(fout.value.ontbrekend) == set(cfg.VERPLICHT)


def test_uploadscherm_is_het_eerste_scherm():
    at = AppTest.from_file(APP, default_timeout=90).run()
    assert not at.exception
    assert any("Stap 1 van 2" in m.value for m in at.markdown)


def test_dashboard_toont_drie_views_en_het_demodata_label(verbinding):
    at = AppTest.from_file(APP, default_timeout=90)
    at.session_state["upload_teller"] = 0
    at.session_state["verbinding"] = verbinding
    at.session_state["bestandsnaam"] = "demodata_1cho.csv"
    at.session_state["demo"] = True
    at.run()
    assert not at.exception
    koppen = [s.value for s in at.subheader]
    assert [k[:2] for k in koppen[:3]] == ["1.", "2.", "3."]
    assert any("Dit is demodata" in m.value for m in at.markdown)


def test_filter_naar_een_kleine_groep_geeft_te_weinig_personen(verbinding):
    jaren, _ = ber.bepaal_waarneembare_jaren(verbinding)
    sectoren = ber.haal_sectoren_op(verbinding)
    kleinste = min(
        sectoren,
        key=lambda s: ber.bereken_uitval_per_sector(verbinding, jaren[:1], [s])[0].n,
    )
    groep = ber.bereken_uitval_per_sector(verbinding, jaren[:1], [kleinste])[0]
    assert groep.n < cfg.DREMPEL_GROEP
    assert groep.reden == ber.REDEN_GROEP
