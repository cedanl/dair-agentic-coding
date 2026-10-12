"""Dashboard: uitval in het eerste jaar per sector. Start met: streamlit run app.py"""
import base64
import math
from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
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
LETTERTYPE = "Plus Jakarta Sans, system-ui, sans-serif"


def label(naam):
    return naam[:1].upper() + naam[1:]


def procent(x):
    return f"{round(100 * x)}%"


def getal(n):
    return f"{n:,}".replace(",", ".")


def laad_stijl():
    css = (STIJL / "npuls-dashboard.css").read_text(encoding="utf-8")
    st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)


def hero(stap, titel, intro=None):
    """Roze vlak met een grote blauwe kop en het officiële Npuls-beeldmerk."""
    logo = base64.b64encode((STIJL / "npuls_logo.jpg").read_bytes()).decode()
    intro_html = f'<p class="npuls-intro">{intro}</p>' if intro else ""
    st.markdown(
        f'<div class="npuls-hero"><div><p class="npuls-label">{stap}</p><h1>{titel}</h1>{intro_html}</div>'
        f'<img class="npuls-logo" src="data:image/jpeg;base64,{logo}" alt="Npuls"></div>',
        unsafe_allow_html=True,
    )


def scherm_upload():
    hero("Stap 1 van 2", cfg.TITEL, cfg.VRAAG)

    st.markdown(
        '<div class="npuls-kaart blauw"><h3>Zo werkt het</h3><ol>'
        "<li>Kies een CSV-bestand en laat het vinkje over demodata staan of zet het uit.</li>"
        "<li>Je ziet drie views onder elkaar: de sectoren naast elkaar, de ontwikkeling per instroomjaar "
        "en een tabel met de groepsgroottes.</li>"
        "<li>Met het filter links kies je instroomjaren en sectoren.</li>"
        "</ol></div>",
        unsafe_allow_html=True,
    )
    st.subheader("Upload je bestand")
    st.markdown(
        f"Een CSV-bestand, scheidingsteken: `{cfg.SCHEIDINGSTEKEN}`. Deze kolommen zijn nodig: "
        + ", ".join(f"`{k}`" for k in cfg.VERPLICHT)
        + ". Andere kolommen worden niet gelezen."
    )
    st.checkbox("Dit bestand is demodata", value=True, key="demo_keuze")
    bestand = st.file_uploader(
        "Kies een CSV-bestand", type="csv", key=f"upload_{st.session_state['upload_teller']}"
    )
    grens = st.get_option("server.maxUploadSize")
    st.caption(
        f"Maximale grootte: {grens} MB. Een upload staat in het geheugen van de server: "
        "een groot bestand kost geheugen."
    )
    st.markdown(
        '<div class="npuls-kaart geel"><h3>Privacy</h3>'
        "<p>De data wordt alleen in het geheugen van deze sessie gebruikt. Er wordt niets opgeslagen en je "
        "data wordt nergens naartoe gestuurd. Alleen het lettertype wordt van Google Fonts geladen.</p></div>",
        unsafe_allow_html=True,
    )
    if bestand is None:
        return

    try:
        with st.spinner(f"{bestand.name} wordt gelezen ({bestand.size / 1e6:.1f} MB)"):
            ruw = ber.lees_csv(bestand)
            con = ber.maak_verbinding(ruw)
            del ruw
    except ber.KolommenOntbreken as fout:
        st.error(
            "Dit bestand mist kolommen die het dashboard nodig heeft: "
            + ", ".join(f"`{k}`" for k in fout.ontbrekend)
            + f". Controleer ook of het scheidingsteken `{cfg.SCHEIDINGSTEKEN}` is."
        )
        return
    except MemoryError:
        st.error(
            "Dit bestand is te groot voor het geheugen. Sla een kleiner bestand op met alleen "
            "de verplichte kolommen en probeer het opnieuw."
        )
        return
    except Exception as fout:  # onleesbaar bestand: één melding, geen traceback
        st.error(f"Het bestand kon niet gelezen worden ({type(fout).__name__}). Is het een CSV?")
        return

    st.session_state.update(
        verbinding=con, bestandsnaam=bestand.name, demo=st.session_state["demo_keuze"]
    )
    st.rerun()


def terug_naar_upload():
    con = st.session_state.pop("verbinding", None)
    if con is not None:
        con.close()
    st.session_state.pop("bestandsnaam", None)
    st.session_state.pop("demo", None)
    st.session_state["upload_teller"] += 1


def grafiek_sectoren(groepen):
    getoond = sorted((g for g in groepen if g.reden is None), key=lambda g: g.aandeel)
    fig = go.Figure(
        go.Bar(
            x=[g.aandeel for g in getoond],
            y=[regelafbreking(f"{label(g.naam)} (n = {g.n})", 24) for g in getoond],
            orientation="h",
            marker_color=BLAUW,
            text=[procent(g.aandeel) for g in getoond],
            textposition="outside",
            textfont=dict(color="#000000"),
            cliponaxis=False,
            hovertemplate="%{y}: %{x:.0%}<extra></extra>",
        )
    )
    fig.update_xaxes(
        range=[0, max([g.aandeel for g in getoond], default=0) * 1.25 or 1],
        tickformat=".0%",
        title="Aandeel uitval van instromers",
        automargin=True,
        gridcolor=GRID,
        zeroline=True,
        zerolinecolor="#000000",
    )
    fig.update_yaxes(automargin=True, ticklabelstandoff=8)
    fig.update_layout(
        height=max(260, 64 * len(getoond) + 120),
        margin=dict(l=10, r=48, t=10, b=10),
        plot_bgcolor="#FFFFFF",
        paper_bgcolor="#FFFFFF",
        font=dict(color="#000000", size=14, family=LETTERTYPE),
    )
    return fig


def samenvatting(groepen):
    getoond = [g for g in groepen if g.reden is None]
    weg = [g for g in groepen if g.reden]
    if not getoond:
        return "Geen enkele sector heeft genoeg instromers om te tonen."
    delen = [f"{label(g.naam)}: {procent(g.aandeel)} van {g.n} instromers" for g in getoond]
    tekst = "Aandeel uitval per sector. " + "; ".join(delen) + "."
    if weg:
        tekst += f" {len(weg)} sector(en) zijn niet getoond: te weinig personen."
    return tekst


def view_sectoren(groepen, jaren, totaal):
    st.subheader("1. Sectoren naast elkaar")
    getoond = [g for g in groepen if g.reden is None]
    if len(getoond) >= 2:
        hoog = max(getoond, key=lambda g: g.aandeel)
        laag = min(getoond, key=lambda g: g.aandeel)
        st.markdown(
            f"**In deze selectie is het aandeel uitval het hoogst bij {label(hoog.naam)} "
            f"({procent(hoog.aandeel)}) en het laagst bij {label(laag.naam)} ({procent(laag.aandeel)}).**"
        )
    st.plotly_chart(
        grafiek_sectoren(groepen), width="stretch", theme=None, config={"displayModeBar": False}
    )
    st.caption(
        f"Instroomjaren {jaren[0]} tot en met {jaren[-1]}, {getal(totaal)} instromers. "
        "n is het aantal instromers per sector."
    )
    weg = [g for g in groepen if g.reden]
    if weg:
        st.caption(
            "Niet getoond, te weinig personen of extra onderdrukt: "
            + ", ".join(label(g.naam) for g in weg) + "."
        )
    with st.expander("Grafiek als tekst (sectoren naast elkaar)"):
        st.write(samenvatting(groepen))  # tekstuele samenvatting voor wie de grafiek niet kan zien


def regelafbreking(tekst, breedte=20):
    """Breekt een lange paneeltitel af, zodat die niet buiten het paneel valt."""
    regels, regel = [], ""
    for woord in tekst.split(" "):
        if regel and len(regel) + 1 + len(woord) > breedte:
            regels.append(regel)
            regel = woord
        else:
            regel = f"{regel} {woord}".strip()
    regels.append(regel)
    return "<br>".join(regels)


def grafiek_cohorten(per_sector, jaren):
    namen = list(per_sector)
    kolommen = min(4, len(namen))
    rijen = math.ceil(len(namen) / kolommen)
    fig = make_subplots(
        rows=rijen, cols=kolommen, shared_yaxes=True,
        subplot_titles=[regelafbreking(label(s)) for s in namen],
        horizontal_spacing=0.04, vertical_spacing=0.28,
    )
    hoogste = max((g.aandeel for gs in per_sector.values() for g in gs if g.aandeel is not None), default=0)
    for i, naam in enumerate(namen):
        r, c = divmod(i, kolommen)
        groepen = per_sector[naam]
        fig.add_trace(
            go.Scatter(
                x=[int(g.naam) for g in groepen], y=[g.aandeel for g in groepen],
                mode="lines+markers", connectgaps=False,
                line=dict(color=BLAUW, width=3), marker=dict(size=7, color=BLAUW),
                hovertemplate="%{x}: %{y:.0%}<extra></extra>", showlegend=False,
            ),
            row=r + 1, col=c + 1,
        )
        if all(g.aandeel is None for g in groepen):
            ax = "" if i == 0 else str(i + 1)
            fig.add_annotation(
                text="te weinig personen", xref=f"x{ax} domain", yref=f"y{ax} domain",
                x=0.5, y=0.5, showarrow=False, font=dict(color=GRIJS, size=13),
            )
    fig.update_yaxes(range=[0, hoogste * 1.3 or 1], tickformat=".0%", gridcolor=GRID,
                     zeroline=True, zerolinecolor="#000000", automargin=True)
    fig.update_xaxes(range=[jaren[0] - 0.5, jaren[-1] + 0.5], tickmode="array",
                     tickvals=[jaren[0], jaren[-1]], automargin=True, ticklabelstandoff=8)
    fig.update_annotations(font=dict(size=14, color="#000000"))
    fig.update_layout(
        height=300 * rijen + 40, margin=dict(l=10, r=10, t=50, b=10),
        plot_bgcolor="#FFFFFF", paper_bgcolor="#FFFFFF", font=dict(color="#000000", size=13, family=LETTERTYPE),
    )
    return fig


def tekst_cohorten(per_sector):
    delen = []
    for naam, groepen in per_sector.items():
        punten = [f"{g.naam} {procent(g.aandeel)}" for g in groepen if g.aandeel is not None]
        delen.append(f"{label(naam)}: " + (", ".join(punten) if punten else "te weinig personen"))
    return "Aandeel uitval per instroomjaar. " + "; ".join(delen) + ". Jaren zonder percentage zijn onderdrukt."


def view_cohorten(per_sector, jaren):
    st.subheader("2. Over de instroomjaren")
    if len(jaren) < 2:
        st.info("Kies minstens twee instroomjaren in het filter om de ontwikkeling te zien.")
        return
    st.markdown("Per sector het aandeel uitval per instroomjaar, op dezelfde schaal. Een gat in de lijn betekent: te weinig personen.")
    st.plotly_chart(
        grafiek_cohorten(per_sector, jaren), width="stretch", theme=None, config={"displayModeBar": False}
    )
    with st.expander("Grafiek als tekst (over de instroomjaren)"):
        st.write(tekst_cohorten(per_sector))


def view_groepsgrootte(per_sector):
    st.subheader("3. Groepsgrootte")
    st.markdown("Hoeveel instromers staan er achter elk percentage, en welke groepen zijn te klein om te tonen?")
    rijen = []
    for naam, groepen in per_sector.items():
        for g in groepen:
            rijen.append({
                "Sector": label(naam),
                "Instroomjaar": g.naam,
                "Instromers": getal(g.n) if ber.toon_aantal(g) else "onderdrukt",
                "Uitvallers": getal(g.uitval) if g.reden is None else "onderdrukt",
                "Aandeel uitval": procent(g.aandeel) if g.reden is None else "onderdrukt",
            })
    if not rijen:
        st.info("Er zijn geen instromers in deze selectie.")
        return
    st.dataframe(pd.DataFrame(rijen), hide_index=True, width="stretch", height=min(40 * len(rijen) + 40, 420))
    st.caption(
        "Onderdrukt: te weinig personen om te tonen, of extra onderdrukt zodat een verborgen groep "
        "niet uit het totaal terug te rekenen is."
    )


def kies_sectoren(opties):
    """Vinkjes met de volledige naam; bij veel sectoren een keuzelijst."""
    if len(opties) > 12:
        return st.multiselect("Sectoren", opties, default=opties, format_func=label)
    st.write("Sectoren")
    return [s for s in opties if st.checkbox(label(s), value=True, key=f"sector_{s}")]


def scherm_dashboard():
    con = st.session_state["verbinding"]
    jaren_waarneembaar, laatste = ber.waarneembare_jaren(con)
    alle_sectoren = ber.sectoren(con)

    hero("Stap 2 van 2", cfg.VRAAG)
    if st.session_state.get("demo"):
        st.markdown(
            '<div class="npuls-demo">Dit is demodata. Dit dashboard zegt niets over de werkelijkheid.</div>',
            unsafe_allow_html=True,
        )

    if not jaren_waarneembaar:
        st.warning("Er is geen instroomjaar waarvan het volgende jaar in de data zit. Zonder vervolgjaar is uitval niet te bepalen.")
        st.button("Andere data uploaden", on_click=terug_naar_upload)
        return

    with st.sidebar:
        st.header("Filter")
        if len(jaren_waarneembaar) > 1:
            van, tot = st.select_slider(
                "Instroomjaren", options=jaren_waarneembaar,
                value=(jaren_waarneembaar[0], jaren_waarneembaar[-1]),
                help="Alleen jaren waarvan het volgende jaar in de data zit.",
            )
            jaren = [j for j in jaren_waarneembaar if van <= j <= tot]
        else:
            jaren = jaren_waarneembaar
            st.write(f"Instroomjaar: {jaren[0]}")
        gekozen = kies_sectoren(alle_sectoren)
        st.button("Andere data uploaden", on_click=terug_naar_upload)

    if not gekozen:
        st.warning("Kies minstens één sector in het filter.")
        return

    groepen = ber.uitval_per_sector(con, jaren, gekozen)
    totaal = sum(g.n for g in groepen)
    per_sector = ber.uitval_per_sector_en_jaar(con, jaren, gekozen)

    view_sectoren(groepen, jaren, totaal)
    view_cohorten(per_sector, jaren)
    view_groepsgrootte(per_sector)
    st.caption("Definities en beperkingen staan onder *Zo lees je dit*.")

    with st.expander("Zo lees je dit"):
        st.markdown(
            f"""
**Bron:** {st.session_state['bestandsnaam']} ({getal(ber.aantal_rijen(con))} rijen, laatste jaar in de data: {laatste}).
Er is geen aparte peildatum; het laatste jaar in de data geldt als laatste periode.

**Wat er geteld wordt:** instromers, dus studenten met verblijfsjaar {cfg.INSTROOM_VERBLIJFSJAAR} bij de instelling
in een instroomjaar. Een student telt eenmaal per instroomjaar. In de selectie zijn dat {getal(totaal)} instromers.

**Uitval in het eerste jaar:** een instromer uit jaar j valt uit als er geen rij voor dezelfde student is met
inschrijvingsjaar j + 1 en er geen ingevuld diplomajaar is.

**Aandeel uitval:** uitvallers gedeeld door instromers, per sector.

**Waarneembaar:** een instroomjaar telt pas mee als het volgende jaar in de data zit. Het jaar {laatste}
doet daarom niet mee als instroomjaar.

**Privacy:** groepen met minder dan {cfg.DREMPEL_GROEP} instromers worden niet getoond, en een percentage
waarvan de teller of de rest kleiner is dan {cfg.DREMPEL_CEL} ook niet. Dit zijn voorbeeldwaarden. Is er één
groep onderdrukt, dan wordt ook de kleinste zichtbare groep onderdrukt, zodat de verborgen groep niet uit het
totaal terug te rekenen is.

**Wat dit dashboard niet kan zeggen:**
- Een verschil tussen sectoren is geen oorzaak; de samenstelling van de groepen kan meespelen.
- Wie naar een andere instelling gaat, telt als uitvaller. Het dashboard ziet niet waar een student heen gaat.
- Een wissel van opleiding of van sector binnen de instelling telt niet als uitval.
- De redenen voor uitval staan niet in de data.
- Een student die in één jaar in meer sectoren staat, telt in elke sector mee.
"""
        )


laad_stijl()
st.session_state.setdefault("upload_teller", 0)
if "verbinding" in st.session_state:
    scherm_dashboard()
else:
    scherm_upload()
