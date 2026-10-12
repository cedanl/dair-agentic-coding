"""Berekeningen voor het dashboard: inlezen, waarneembaarheid, uitval en privacyregels."""

from dataclasses import dataclass
from typing import BinaryIO

import duckdb
import polars as pl

import configuratie as cfg

REDEN_GROEP = "te weinig personen"
REDEN_CEL = "te weinig personen voor een percentage"
REDEN_EXTRA = "onderdrukt zodat een verborgen groep niet terug te rekenen is"


class OntbrekendeKolommenError(Exception):
    """De upload mist kolommen die de berekening nodig heeft."""

    def __init__(self, ontbrekend: list[str]) -> None:
        super().__init__(", ".join(ontbrekend))
        self.ontbrekend = ontbrekend


@dataclass
class Groep:
    """Een groep instromers met het aantal uitvallers en de privacystatus."""

    naam: str
    n: int
    uitval: int
    aandeel: float | None
    reden: str | None  # None als de groep getoond mag worden


def lees_csv(bestand: BinaryIO) -> pl.DataFrame:
    """Leest alleen de verplichte kolommen uit de upload, als tekst.

    Args:
        bestand: Geopend bestand of upload, in bytes. Moet terugspoelbaar zijn.

    Returns:
        Tabel met de verplichte kolommen, alle waarden als tekst.

    Raises:
        OntbrekendeKolommenError: Als een verplichte kolom niet in de kopregel staat.
    """
    kop = pl.read_csv(bestand, separator=cfg.SCHEIDINGSTEKEN, n_rows=0, infer_schema=False).columns
    ontbrekend = [kolom for kolom in cfg.VERPLICHT if kolom not in kop]
    if ontbrekend:
        raise OntbrekendeKolommenError(ontbrekend)
    bestand.seek(0)
    return pl.read_csv(
        bestand,
        separator=cfg.SCHEIDINGSTEKEN,
        columns=cfg.VERPLICHT,
        infer_schema=False,
    )


def maak_verbinding(ruw: pl.DataFrame) -> duckdb.DuckDBPyConnection:
    """Zet de ingelezen kolommen om in één tabel `data` met getypeerde kolommen.

    Args:
        ruw: Tabel uit `lees_csv`.

    Returns:
        DuckDB-verbinding met de tabel `data` (persoon, jaar, verblijfsjaar, diplomajaar, sector).
    """
    con = duckdb.connect()
    con.register("ruw", ruw.to_arrow())
    con.execute(
        f"""
        create table data as
        select
            "{cfg.PERSOON}" as persoon,
            try_cast("{cfg.JAAR}" as integer) as jaar,
            try_cast("{cfg.VERBLIJFSJAAR}" as integer) as verblijfsjaar,
            try_cast("{cfg.DIPLOMAJAAR}" as integer) as diplomajaar,
            coalesce(nullif(trim("{cfg.SECTOR}"), ''), '{cfg.ONBEKEND}') as sector
        from ruw
        """
    )
    con.unregister("ruw")
    return con


def tel_rijen(con: duckdb.DuckDBPyConnection) -> int:
    """Geeft het aantal rijen in de ingelezen data."""
    return con.execute("select count(*) from data").fetchone()[0]


def bepaal_laatste_jaar(con: duckdb.DuckDBPyConnection) -> int:
    """Geeft het laatste inschrijvingsjaar in de data."""
    return con.execute("select max(jaar) from data").fetchone()[0]


def bepaal_waarneembare_jaren(con: duckdb.DuckDBPyConnection) -> tuple[list[int], int]:
    """Bepaalt de instroomjaren waarvan het volgende jaar in de data zit.

    Args:
        con: Verbinding uit `maak_verbinding`.

    Returns:
        De waarneembare instroomjaren, oplopend, en het laatste jaar in de data.
    """
    laatste = bepaal_laatste_jaar(con)
    rijen = con.execute(
        "select distinct jaar from data where verblijfsjaar = ? and jaar < ? order by jaar",
        [cfg.INSTROOM_VERBLIJFSJAAR, laatste],
    ).fetchall()
    return [rij[0] for rij in rijen], laatste


def haal_sectoren_op(con: duckdb.DuckDBPyConnection) -> list[str]:
    """Geeft de sectoren in de data, alfabetisch."""
    rijen = con.execute("select distinct sector from data order by sector").fetchall()
    return [rij[0] for rij in rijen]


def _tel_uitval(
    con: duckdb.DuckDBPyConnection,
    jaren: list[int],
    gekozen_sectoren: list[str],
    per_jaar: bool,
) -> list[tuple]:
    """Telt per sector (en eventueel per instroomjaar) instromers en uitvallers.

    Uitval: geen rij in het jaar erna en geen diploma. Een student telt eenmaal per instroomjaar.
    """
    jaar_kolom = ", i.jaar" if per_jaar else ""
    return con.execute(
        f"""
        with instromers as (
            select distinct persoon, jaar, sector
            from data
            where verblijfsjaar = ? and list_contains(?, jaar) and list_contains(?, sector)
        ),
        heeft_diploma as (
            select persoon, bool_or(diplomajaar is not null) as diploma from data group by persoon
        ),
        aanwezig as (select distinct persoon, jaar from data)
        select
            i.sector{jaar_kolom},
            count(*) as n,
            count(*) filter (where a.persoon is null and not coalesce(d.diploma, false)) as uitval
        from instromers i
        left join aanwezig a on a.persoon = i.persoon and a.jaar = i.jaar + 1
        left join heeft_diploma d on d.persoon = i.persoon
        group by i.sector{jaar_kolom}
        order by i.sector{jaar_kolom}
        """,
        [cfg.INSTROOM_VERBLIJFSJAAR, list(jaren), list(gekozen_sectoren)],
    ).fetchall()


def bereken_uitval_per_sector(
    con: duckdb.DuckDBPyConnection, jaren: list[int], gekozen_sectoren: list[str]
) -> list[Groep]:
    """Berekent per sector het aantal instromers en uitvallers.

    Args:
        con: Verbinding uit `maak_verbinding`.
        jaren: Instroomjaren die meetellen.
        gekozen_sectoren: Sectoren die meetellen.

    Returns:
        Een groep per sector, met de privacyregels toegepast.
    """
    rijen = _tel_uitval(con, jaren, gekozen_sectoren, per_jaar=False)
    return pas_privacy_toe([Groep(s, n, u, None, None) for s, n, u in rijen])


def bereken_uitval_per_sector_en_jaar(
    con: duckdb.DuckDBPyConnection, jaren: list[int], gekozen_sectoren: list[str]
) -> dict[str, list[Groep]]:
    """Berekent per sector en instroomjaar het aantal instromers en uitvallers.

    De secundaire onderdrukking geldt per sector: het totaal van een sector staat zichtbaar in de
    vergelijking tussen sectoren, dus een enkel onderdrukt jaar zou daaruit terug te rekenen zijn.

    Args:
        con: Verbinding uit `maak_verbinding`.
        jaren: Instroomjaren die meetellen.
        gekozen_sectoren: Sectoren die meetellen.

    Returns:
        Per sector een lijst groepen, een per instroomjaar, met de privacyregels toegepast.
    """
    per_sector: dict[str, list[Groep]] = {}
    for sector, jaar, n, uitval in _tel_uitval(con, jaren, gekozen_sectoren, per_jaar=True):
        per_sector.setdefault(sector, []).append(Groep(str(jaar), n, uitval, None, None))
    return {sector: pas_privacy_toe(groepen) for sector, groepen in per_sector.items()}


def mag_aantal_tonen(groep: Groep) -> bool:
    """Bepaalt of het aantal instromers getoond mag worden.

    Niet bij een kleine of extra onderdrukte groep.
    """
    return groep.reden is None or groep.reden == REDEN_CEL


def pas_privacy_toe(groepen: list[Groep]) -> list[Groep]:
    """Onderdrukt kleine groepen en kleine percentagecellen, met secundaire onderdrukking.

    Het totaal van de selectie staat zichtbaar op het dashboard. Is er precies één groep
    onderdrukt, dan zou die uit het totaal terug te rekenen zijn: dan onderdrukken we ook de
    kleinste zichtbare groep.

    Args:
        groepen: Groepen met aantallen; wordt aangepast en teruggegeven.

    Returns:
        Dezelfde groepen, met `reden` en `aandeel` ingevuld.
    """
    for groep in groepen:
        if groep.n < cfg.DREMPEL_GROEP:
            groep.reden = REDEN_GROEP
        elif groep.uitval < cfg.DREMPEL_CEL or groep.n - groep.uitval < cfg.DREMPEL_CEL:
            groep.reden = REDEN_CEL
        else:
            groep.aandeel = groep.uitval / groep.n

    onderdrukt = [groep for groep in groepen if groep.reden]
    zichtbaar = [groep for groep in groepen if not groep.reden]
    if len(onderdrukt) == 1 and zichtbaar:
        kleinste = min(zichtbaar, key=lambda groep: groep.n)
        kleinste.reden = REDEN_EXTRA
        kleinste.aandeel = None
    return groepen
