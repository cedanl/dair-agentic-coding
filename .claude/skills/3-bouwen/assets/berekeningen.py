"""De berekeningen achter je dashboard.

Dit is het deel van het script dat rekent. Al het andere (de pagina, de grafieken, de teksten) staat in
maak_dashboard.py. Je kunt dit bestand lezen zonder iets van de rest te weten. Er zijn drie stappen:

1. bereken_eerstejaars: per student die in zijn of haar eerste jaar begon, telt die student mee in de teller?
   Bij uitval telt de student mee als die zich het jaar erna niet opnieuw inschreef. Bij een diploma telt de
   student mee als die binnen de termijn een diploma haalde. Jaren waarin dit nog niet te zeggen is, vallen weg.
2. tel: per groep, of per jaar, het aantal studenten in de teller en in de noemer.
3. pas_drempels_toe: te kleine groepen en te kleine aantallen worden verborgen. Zo kan niemand uit het
   dashboard afleiden wat er met één bepaalde student is gebeurd.

De functies hebben een instelling (`ins`) nodig die maak_dashboard.py uit de casus en je keuzes samenstelt.
Daarom draai je dit bestand niet los: opnieuw bouwen kan met het commando onderaan dashboard.html.
"""

import polars as pl


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
