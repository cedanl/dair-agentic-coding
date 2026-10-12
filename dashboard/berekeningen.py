"""Berekeningen voor het dashboard: inlezen, waarneembaarheid, uitval per sector en privacyregels."""
from dataclasses import dataclass

import duckdb
import pandas as pd

import configuratie as cfg


class KolommenOntbreken(Exception):
    """De upload mist kolommen die de berekening nodig heeft."""

    def __init__(self, ontbrekend):
        super().__init__(", ".join(ontbrekend))
        self.ontbrekend = ontbrekend


REDEN_GROEP = "te weinig personen"
REDEN_CEL = "te weinig personen voor een percentage"
REDEN_EXTRA = "onderdrukt zodat een verborgen groep niet terug te rekenen is"


@dataclass
class Groep:
    naam: str
    n: int
    uitval: int
    aandeel: float | None
    reden: str | None  # None als de groep getoond mag worden


def lees_csv(bestand):
    """Leest alleen de verplichte kolommen uit de upload, zonder kopie in het geheugen."""
    kop = pd.read_csv(bestand, sep=cfg.SCHEIDINGSTEKEN, nrows=0, dtype=str).columns
    ontbrekend = [k for k in cfg.VERPLICHT if k not in kop]
    if ontbrekend:
        raise KolommenOntbreken(ontbrekend)
    bestand.seek(0)
    return pd.read_csv(bestand, sep=cfg.SCHEIDINGSTEKEN, usecols=cfg.VERPLICHT, dtype=str)


def maak_verbinding(ruw):
    """Zet de ingelezen kolommen om in één tabel `data` met getypeerde kolommen."""
    con = duckdb.connect()
    con.register("ruw", ruw)
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


def aantal_rijen(con):
    return con.execute("select count(*) from data").fetchone()[0]


def laatste_jaar(con):
    return con.execute("select max(jaar) from data").fetchone()[0]


def waarneembare_jaren(con):
    """Instroomjaren waarvan het volgende jaar in de data zit, met het laatste jaar uit de data."""
    laatste = laatste_jaar(con)
    rijen = con.execute(
        "select distinct jaar from data where verblijfsjaar = ? and jaar < ? order by jaar",
        [cfg.INSTROOM_VERBLIJFSJAAR, laatste],
    ).fetchall()
    return [r[0] for r in rijen], laatste


def sectoren(con):
    return [r[0] for r in con.execute("select distinct sector from data order by sector").fetchall()]


def _tel_uitval(con, jaren, gekozen_sectoren, per_jaar):
    """Per sector (en eventueel per instroomjaar) instromers en uitvallers.

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


def uitval_per_sector(con, jaren, gekozen_sectoren):
    """Per sector het aantal instromers en uitvallers, met de privacyregels toegepast."""
    rijen = _tel_uitval(con, jaren, gekozen_sectoren, per_jaar=False)
    return pas_privacy_toe([Groep(s, n, u, None, None) for s, n, u in rijen])


def uitval_per_sector_en_jaar(con, jaren, gekozen_sectoren):
    """Per sector een lijst groepen, een per instroomjaar, met de privacyregels per sector toegepast.

    De secundaire onderdrukking geldt per sector: het totaal van een sector staat zichtbaar in de
    vergelijking tussen sectoren, dus een enkel onderdrukt jaar zou daaruit terug te rekenen zijn.
    """
    per_sector = {}
    for sector, jaar, n, uitval in _tel_uitval(con, jaren, gekozen_sectoren, per_jaar=True):
        per_sector.setdefault(sector, []).append(Groep(str(jaar), n, uitval, None, None))
    return {s: pas_privacy_toe(groepen) for s, groepen in per_sector.items()}


def toon_aantal(groep):
    """Mag het aantal instromers getoond worden? Niet bij een kleine of extra onderdrukte groep."""
    return groep.reden is None or groep.reden == REDEN_CEL


def pas_privacy_toe(groepen):
    """Onderdrukt kleine groepen en kleine percentagecellen, met secundaire onderdrukking.

    Het totaal van de selectie staat zichtbaar op het dashboard. Is er precies één groep onderdrukt,
    dan zou die uit het totaal terug te rekenen zijn: dan onderdrukken we ook de kleinste zichtbare groep.
    """
    for g in groepen:
        if g.n < cfg.DREMPEL_GROEP:
            g.reden = REDEN_GROEP
        elif g.uitval < cfg.DREMPEL_CEL or g.n - g.uitval < cfg.DREMPEL_CEL:
            g.reden = REDEN_CEL
        else:
            g.aandeel = g.uitval / g.n

    onderdrukt = [g for g in groepen if g.reden]
    zichtbaar = [g for g in groepen if not g.reden]
    if len(onderdrukt) == 1 and zichtbaar:
        kleinste = min(zichtbaar, key=lambda g: g.n)
        kleinste.reden = REDEN_EXTRA
        kleinste.aandeel = None
    return groepen
