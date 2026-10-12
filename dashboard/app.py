"""Dashboard: uitval in het eerste jaar per sector. Start met: streamlit run app.py"""

import base64
import math
from pathlib import Path

import plotly.graph_objects as go
import polars as pl
import streamlit as st
from plotly.subplots import make_subplots

import berekeningen as ber
import configuratie as cfg

STIJL = Path(__file__).parent / "npuls"

st.set_page_config(page_title=cfg.TITEL, page_icon=str(STIJL / "npuls_logo.jpg"), layout="wide")

# Npuls-huisstijl: kleuren uit vormgever-npuls-huisstijl/references/design-tokens.json
BLAUW = "#3D68EC"
GRIJS = "#5C5C66"
GRID = "#DCDCE0"
ZWART = "#000000"
WIT = "#FFFFFF"
LETTERTYPE = "Plus Jakarta Sans, system-ui, sans-serif"


def maak_label(naam: str) -> str:
    """Zet de eerste letter van een naam om in een hoofdletter."""
    return naam[:1].upper() + naam[1:]


def formatteer_procent(aandeel: float) -> str:
    """Geeft een aandeel als afgerond percentage, bijvoorbeeld 0,23 als '23%'."""
    return f"{round(100 * aandeel)}%"


def formatteer_getal(n: int) -> str:
    """Geeft een geheel getal met een punt als duizendtalscheiding."""
    return f"{n:,}".replace(",", ".")


def breek_regel_af(tekst: str, breedte: int = 20) -> str:
    """Breekt een lange titel of label af, zodat die niet buiten beeld valt.

    Args:
        tekst: De tekst die wordt afgebroken, bij spaties.
        breedte: Maximaal aantal tekens per regel.

    Returns:
        De tekst met `<br>` tussen de regels.
    """
    regels, regel = [], ""
    for woord in tekst.split(" "):
        if regel and len(regel) + 1 + len(woord) > breedte:
            regels.append(regel)
            regel = woord
        else:
            regel = f"{regel} {woord}".strip()
    regels.append(regel)
    return "<br>".join(regels)


@st.cache_data
def lees_stijlblad() -> str:
    """Leest het Npuls-stijlblad van schijf, eenmaal per sessie."""
    return (STIJL / "npuls-dashboard.css").read_text(encoding="utf-8")


@st.cache_data
def lees_logo() -> str:
    """Geeft het Npuls-logo als base64-tekst voor in een `<img>`, eenmaal per sessie."""
    return base64.b64encode((STIJL / "npuls_logo.jpg").read_bytes()).decode()


def laad_stijl() -> None:
    """Zet het Npuls-stijlblad op de pagina."""
    st.markdown(f"<style>{lees_stijlblad()}</style>", unsafe_allow_html=True)


def toon_hero(stap: str, titel: str, intro: str | None = None) -> None:
    """Toont het roze vlak met een grote blauwe kop en het officiële Npuls-beeldmerk."""
    intro_html = f'<p class="npuls-intro">{intro}</p>' if intro else ""
    st.markdown(
        f'<div class="npuls-hero"><div><p class="npuls-label">{stap}</p>'
        f"<h1>{titel}</h1>{intro_html}</div>"
        f'<img class="npuls-logo" src="data:image/jpeg;base64,{lees_logo()}" alt="Npuls"></div>',
        unsafe_allow_html=True,
    )


def toon_scherm_upload() -> None:
    """Toont stap 1: het uploadscherm. Een geldige upload opent het dashboard."""
    toon_hero("Stap 1 van 2", cfg.TITEL, cfg.VRAAG)

    st.markdown(
        '<div class="npuls-kaart blauw"><h3>Zo werkt het</h3><ol>'
        "<li>Kies een CSV-bestand en laat het vinkje over demodata staan of zet het uit.</li>"
        "<li>Je ziet drie views onder elkaar: de sectoren naast elkaar, de ontwikkeling per "
        "instroomjaar en een tabel met de groepsgroottes.</li>"
        "<li>Met het filter links kies je instroomjaren en sectoren.</li>"
        "</ol></div>",
        unsafe_allow_html=True,
    )
    st.subheader("Upload je bestand")
    st.markdown(
        f"Een CSV-bestand, scheidingsteken: `{cfg.SCHEIDINGSTEKEN}`. Deze kolommen zijn nodig: "
        + ", ".join(f"`{kolom}`" for kolom in cfg.VERPLICHT)
        + ". Andere kolommen worden niet gelezen."
    )
    st.checkbox("Dit bestand is demodata", value=True, key="demo_keuze")
    bestand = st.file_uploader(
        "Kies een CSV-bestand", type="csv", key=f"upload_{st.session_state['upload_teller']}"
    )
    st.caption(
        f"Maximale grootte: {st.get_option('server.maxUploadSize')} MB. Een upload staat in het "
        "geheugen van de server: een groot bestand kost geheugen."
    )
    st.markdown(
        '<div class="npuls-kaart geel"><h3>Privacy</h3>'
        "<p>De data wordt alleen in het geheugen van deze sessie gebruikt. Er wordt niets "
        "opgeslagen en je data wordt nergens naartoe gestuurd. Alleen het lettertype wordt van "
        "Google Fonts geladen.</p></div>",
        unsafe_allow_html=True,
    )
    if bestand is None:
        return

    try:
        with st.spinner(f"{bestand.name} wordt gelezen ({bestand.size / 1e6:.1f} MB)"):
            con = ber.maak_verbinding(ber.lees_csv(bestand))
    except ber.OntbrekendeKolommenError as fout:
        st.error(
            "Dit bestand mist kolommen die het dashboard nodig heeft: "
            + ", ".join(f"`{kolom}`" for kolom in fout.ontbrekend)
            + f". Controleer ook of het scheidingsteken `{cfg.SCHEIDINGSTEKEN}` is."
        )
        return
    except MemoryError:
        st.error(
            "Dit bestand is te groot voor het geheugen. Sla een kleiner bestand op met alleen "
            "de verplichte kolommen en probeer het opnieuw."
        )
        return
    except (pl.exceptions.PolarsError, UnicodeDecodeError, ValueError) as fout:
        st.error(f"Het bestand kon niet gelezen worden ({type(fout).__name__}). Is het een CSV?")
        return

    st.session_state.update(
        verbinding=con, bestandsnaam=bestand.name, demo=st.session_state["demo_keuze"]
    )
    st.rerun()


def ga_terug_naar_upload() -> None:
    """Sluit de verbinding en keert terug naar het uploadscherm."""
    con = st.session_state.pop("verbinding", None)
    if con is not None:
        con.close()
    st.session_state.pop("bestandsnaam", None)
    st.session_state.pop("demo", None)
    st.session_state["upload_teller"] += 1


def maak_basislayout(hoogte: int, marge: dict, tekstgrootte: int) -> dict:
    """Geeft de gedeelde opmaak van de grafieken: wit, zwarte tekst, huislettertype."""
    return {
        "height": hoogte,
        "margin": marge,
        "plot_bgcolor": WIT,
        "paper_bgcolor": WIT,
        "font": {"color": ZWART, "size": tekstgrootte, "family": LETTERTYPE},
    }


def teken_grafiek_sectoren(groepen: list[ber.Groep]) -> go.Figure:
    """Tekent een horizontaal staafdiagram met het aandeel uitval per sector.

    Args:
        groepen: Groepen uit `bereken_uitval_per_sector`. Onderdrukte groepen worden niet getekend.

    Returns:
        De figuur, met een gemeenschappelijke nul-as.
    """
    getoond = sorted((g for g in groepen if g.reden is None), key=lambda g: g.aandeel)
    fig = go.Figure(
        go.Bar(
            x=[g.aandeel for g in getoond],
            y=[breek_regel_af(f"{maak_label(g.naam)} (n = {g.n})", 24) for g in getoond],
            orientation="h",
            marker_color=BLAUW,
            text=[formatteer_procent(g.aandeel) for g in getoond],
            textposition="outside",
            textfont={"color": ZWART},
            cliponaxis=False,
            hovertemplate="%{y}: %{x:.0%}<extra></extra>",
        )
    )
    fig.update_xaxes(
        range=[0, max((g.aandeel for g in getoond), default=0) * 1.25 or 1],
        tickformat=".0%",
        title="Aandeel uitval van instromers",
        automargin=True,
        gridcolor=GRID,
        zeroline=True,
        zerolinecolor=ZWART,
    )
    fig.update_yaxes(automargin=True, ticklabelstandoff=8)
    fig.update_layout(
        **maak_basislayout(
            max(260, 64 * len(getoond) + 120), {"l": 10, "r": 48, "t": 10, "b": 10}, 14
        )
    )
    return fig


def beschrijf_sectoren(groepen: list[ber.Groep]) -> str:
    """Beschrijft de sectorgrafiek in tekst, voor wie de grafiek niet kan zien."""
    getoond = [g for g in groepen if g.reden is None]
    weg = [g for g in groepen if g.reden]
    if not getoond:
        return "Geen enkele sector heeft genoeg instromers om te tonen."
    delen = [
        f"{maak_label(g.naam)}: {formatteer_procent(g.aandeel)} van {g.n} instromers"
        for g in getoond
    ]
    tekst = "Aandeel uitval per sector. " + "; ".join(delen) + "."
    if weg:
        tekst += f" {len(weg)} sector(en) zijn niet getoond: te weinig personen."
    return tekst


def toon_view_sectoren(groepen: list[ber.Groep], jaren: list[int], totaal: int) -> None:
    """Toont view 1: de sectoren naast elkaar."""
    st.subheader("1. Sectoren naast elkaar")
    getoond = [g for g in groepen if g.reden is None]
    if len(getoond) >= 2:
        hoog = max(getoond, key=lambda g: g.aandeel)
        laag = min(getoond, key=lambda g: g.aandeel)
        st.markdown(
            f"**In deze selectie is het aandeel uitval het hoogst bij {maak_label(hoog.naam)} "
            f"({formatteer_procent(hoog.aandeel)}) en het laagst bij {maak_label(laag.naam)} "
            f"({formatteer_procent(laag.aandeel)}).**"
        )
    st.plotly_chart(
        teken_grafiek_sectoren(groepen),
        width="stretch",
        theme=None,
        config={"displayModeBar": False},
    )
    st.caption(
        f"Instroomjaren {jaren[0]} tot en met {jaren[-1]}, {formatteer_getal(totaal)} instromers. "
        "n is het aantal instromers per sector."
    )
    weg = [g for g in groepen if g.reden]
    if weg:
        st.caption(
            "Niet getoond, te weinig personen of extra onderdrukt: "
            + ", ".join(maak_label(g.naam) for g in weg)
            + "."
        )
    with st.expander("Grafiek als tekst (sectoren naast elkaar)"):
        st.write(beschrijf_sectoren(groepen))


def teken_grafiek_cohorten(per_sector: dict[str, list[ber.Groep]], jaren: list[int]) -> go.Figure:
    """Tekent een klein lijnpaneel per sector met het aandeel uitval per instroomjaar.

    Args:
        per_sector: Groepen uit `bereken_uitval_per_sector_en_jaar`.
        jaren: De gekozen instroomjaren, voor het bereik van de x-as.

    Returns:
        De figuur, met op alle panelen dezelfde schaal. Een onderdrukt jaar is een gat in de lijn.
    """
    namen = list(per_sector)
    kolommen = min(4, len(namen))
    rijen = math.ceil(len(namen) / kolommen)
    fig = make_subplots(
        rows=rijen,
        cols=kolommen,
        shared_yaxes=True,
        subplot_titles=[breek_regel_af(maak_label(naam)) for naam in namen],
        horizontal_spacing=0.04,
        vertical_spacing=0.28,
    )
    hoogste = max(
        (g.aandeel for groepen in per_sector.values() for g in groepen if g.aandeel is not None),
        default=0,
    )
    for i, naam in enumerate(namen):
        rij, kolom = divmod(i, kolommen)
        groepen = per_sector[naam]
        fig.add_trace(
            go.Scatter(
                x=[int(g.naam) for g in groepen],
                y=[g.aandeel for g in groepen],
                mode="lines+markers",
                connectgaps=False,
                line={"color": BLAUW, "width": 3},
                marker={"size": 7, "color": BLAUW},
                hovertemplate="%{x}: %{y:.0%}<extra></extra>",
                showlegend=False,
            ),
            row=rij + 1,
            col=kolom + 1,
        )
        if all(g.aandeel is None for g in groepen):
            as_nummer = "" if i == 0 else str(i + 1)
            fig.add_annotation(
                text="te weinig personen",
                xref=f"x{as_nummer} domain",
                yref=f"y{as_nummer} domain",
                x=0.5,
                y=0.5,
                showarrow=False,
                font={"color": GRIJS, "size": 13},
            )
    fig.update_yaxes(
        range=[0, hoogste * 1.3 or 1],
        tickformat=".0%",
        gridcolor=GRID,
        zeroline=True,
        zerolinecolor=ZWART,
        automargin=True,
    )
    fig.update_xaxes(
        range=[jaren[0] - 0.5, jaren[-1] + 0.5],
        tickmode="array",
        tickvals=[jaren[0], jaren[-1]],
        automargin=True,
        ticklabelstandoff=8,
    )
    fig.update_annotations(font={"size": 14, "color": ZWART})
    fig.update_layout(
        **maak_basislayout(300 * rijen + 40, {"l": 10, "r": 10, "t": 50, "b": 10}, 13)
    )
    return fig


def beschrijf_cohorten(per_sector: dict[str, list[ber.Groep]]) -> str:
    """Beschrijft de cohortgrafiek in tekst, voor wie de grafiek niet kan zien."""
    delen = []
    for naam, groepen in per_sector.items():
        punten = [
            f"{g.naam} {formatteer_procent(g.aandeel)}" for g in groepen if g.aandeel is not None
        ]
        delen.append(f"{maak_label(naam)}: " + (", ".join(punten) if punten else ber.REDEN_GROEP))
    return (
        "Aandeel uitval per instroomjaar. "
        + "; ".join(delen)
        + ". Jaren zonder percentage zijn onderdrukt."
    )


def toon_view_cohorten(per_sector: dict[str, list[ber.Groep]], jaren: list[int]) -> None:
    """Toont view 2: het aandeel uitval per instroomjaar, een paneel per sector."""
    st.subheader("2. Over de instroomjaren")
    if len(jaren) < 2:
        st.info("Kies minstens twee instroomjaren in het filter om de ontwikkeling te zien.")
        return
    st.markdown(
        "Per sector het aandeel uitval per instroomjaar, op dezelfde schaal. "
        "Een gat in de lijn betekent: te weinig personen."
    )
    st.plotly_chart(
        teken_grafiek_cohorten(per_sector, jaren),
        width="stretch",
        theme=None,
        config={"displayModeBar": False},
    )
    with st.expander("Grafiek als tekst (over de instroomjaren)"):
        st.write(beschrijf_cohorten(per_sector))


def toon_view_groepsgrootte(per_sector: dict[str, list[ber.Groep]]) -> None:
    """Toont view 3: een tabel met de groepsgroottes en de onderdrukte groepen."""
    st.subheader("3. Groepsgrootte")
    st.markdown(
        "Hoeveel instromers staan er achter elk percentage, en welke groepen zijn te klein "
        "om te tonen?"
    )
    rijen = [
        {
            "Sector": maak_label(naam),
            "Instroomjaar": g.naam,
            "Instromers": formatteer_getal(g.n) if ber.mag_aantal_tonen(g) else "onderdrukt",
            "Uitvallers": formatteer_getal(g.uitval) if g.reden is None else "onderdrukt",
            "Aandeel uitval": formatteer_procent(g.aandeel) if g.reden is None else "onderdrukt",
        }
        for naam, groepen in per_sector.items()
        for g in groepen
    ]
    if not rijen:
        st.info("Er zijn geen instromers in deze selectie.")
        return
    st.dataframe(
        pl.DataFrame(rijen), hide_index=True, width="stretch", height=min(40 * len(rijen) + 40, 420)
    )
    st.caption(
        "Onderdrukt: te weinig personen om te tonen, of extra onderdrukt zodat een verborgen "
        "groep niet uit het totaal terug te rekenen is."
    )


def kies_sectoren(opties: list[str]) -> list[str]:
    """Laat de gebruiker sectoren kiezen: vinkjes, of bij veel sectoren een keuzelijst."""
    if len(opties) > 12:
        return st.multiselect("Sectoren", opties, default=opties, format_func=maak_label)
    st.write("Sectoren")
    return [s for s in opties if st.checkbox(maak_label(s), value=True, key=f"sector_{s}")]


def toon_uitleg(totaal: int, laatste: int) -> None:
    """Toont de uitklapper 'Zo lees je dit': bron, definities, privacy en beperkingen."""
    con = st.session_state["verbinding"]
    with st.expander("Zo lees je dit"):
        st.markdown(
            f"""
**Bron:** {st.session_state["bestandsnaam"]} ({formatteer_getal(ber.tel_rijen(con))} rijen,
laatste jaar in de data: {laatste}). Er is geen aparte peildatum; het laatste jaar in de data
geldt als laatste periode.

**Wat er geteld wordt:** instromers, dus studenten met verblijfsjaar
{cfg.INSTROOM_VERBLIJFSJAAR} bij de instelling in een instroomjaar. Een student telt eenmaal
per instroomjaar. In de selectie zijn dat {formatteer_getal(totaal)} instromers.

**Uitval in het eerste jaar:** een instromer uit jaar j valt uit als er geen rij voor dezelfde
student is met inschrijvingsjaar j + 1 en er geen ingevuld diplomajaar is.

**Aandeel uitval:** uitvallers gedeeld door instromers, per sector.

**Waarneembaar:** een instroomjaar telt pas mee als het volgende jaar in de data zit. Het jaar
{laatste} doet daarom niet mee als instroomjaar.

**Privacy:** groepen met minder dan {cfg.DREMPEL_GROEP} instromers worden niet getoond, en een
percentage waarvan de teller of de rest kleiner is dan {cfg.DREMPEL_CEL} ook niet. Dit zijn
voorbeeldwaarden. Is er één groep onderdrukt, dan wordt ook de kleinste zichtbare groep
onderdrukt, zodat de verborgen groep niet uit het totaal terug te rekenen is.

**Wat dit dashboard niet kan zeggen:**
- Een verschil tussen sectoren is geen oorzaak; de samenstelling van de groepen kan meespelen.
- Wie naar een andere instelling gaat, telt als uitvaller. Het dashboard ziet niet waar een
  student heen gaat.
- Een wissel van opleiding of van sector binnen de instelling telt niet als uitval.
- De redenen voor uitval staan niet in de data.
- Een student die in één jaar in meer sectoren staat, telt in elke sector mee.
"""
        )


def toon_scherm_dashboard() -> None:
    """Toont stap 2: het dashboard met filter, drie views en uitleg."""
    con = st.session_state["verbinding"]
    jaren_waarneembaar, laatste = ber.bepaal_waarneembare_jaren(con)

    toon_hero("Stap 2 van 2", cfg.VRAAG)
    if st.session_state.get("demo"):
        st.markdown(
            '<div class="npuls-demo">Dit is demodata. Dit dashboard zegt niets over de '
            "werkelijkheid.</div>",
            unsafe_allow_html=True,
        )

    if not jaren_waarneembaar:
        st.warning(
            "Er is geen instroomjaar waarvan het volgende jaar in de data zit. "
            "Zonder vervolgjaar is uitval niet te bepalen."
        )
        st.button("Andere data uploaden", on_click=ga_terug_naar_upload)
        return

    with st.sidebar:
        st.header("Filter")
        if len(jaren_waarneembaar) > 1:
            van, tot = st.select_slider(
                "Instroomjaren",
                options=jaren_waarneembaar,
                value=(jaren_waarneembaar[0], jaren_waarneembaar[-1]),
                help="Alleen jaren waarvan het volgende jaar in de data zit.",
            )
            jaren = [jaar for jaar in jaren_waarneembaar if van <= jaar <= tot]
        else:
            jaren = jaren_waarneembaar
            st.write(f"Instroomjaar: {jaren[0]}")
        gekozen = kies_sectoren(ber.haal_sectoren_op(con))
        st.button("Andere data uploaden", on_click=ga_terug_naar_upload)

    if not gekozen:
        st.warning("Kies minstens één sector in het filter.")
        return

    groepen = ber.bereken_uitval_per_sector(con, jaren, gekozen)
    totaal = sum(g.n for g in groepen)
    per_sector = ber.bereken_uitval_per_sector_en_jaar(con, jaren, gekozen)

    toon_view_sectoren(groepen, jaren, totaal)
    toon_view_cohorten(per_sector, jaren)
    toon_view_groepsgrootte(per_sector)
    st.caption("Definities en beperkingen staan onder *Zo lees je dit*.")
    toon_uitleg(totaal, laatste)


laad_stijl()
st.session_state.setdefault("upload_teller", 0)
if "verbinding" in st.session_state:
    toon_scherm_dashboard()
else:
    toon_scherm_upload()
