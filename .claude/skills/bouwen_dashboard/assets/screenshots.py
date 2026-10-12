"""Maakt screenshots van een dashboard uit bouwen_dashboard, op 1280 en 390 pixels breed.

Schermen: het schijn-uploadscherm, het dashboard na Doorgaan, en de foutmelding bij een bestand
zonder de verplichte kolommen (dat bestand maakt dit script zelf). Elke screenshot is de hele
pagina. Meldt per scherm het lettertype van de kop en of Streamlit een fout toonde.

Gebruik, vanuit de werkmap:

    uv run --no-project --with-requirements dashboard/requirements.txt \
        --with-requirements .devcontainer/test-requirements.txt \
        python .claude/skills/bouwen_dashboard/assets/screenshots.py \
        --app dashboard/app.py --data <pad-naar-csv> --uit uitvoer/screenshots

Verwacht de afspraken uit de skill: het pad komt na `--` in het startcommando, het eerste scherm
toont "Stap 1 van 2", de knop heet "Doorgaan" en het dashboard toont "Stap 2 van 2".
Exitcode 1 als een scherm een fout van Streamlit toont of het lettertype niet klopt.
"""

import argparse
import socket
import subprocess
import sys
import tempfile
import time
import urllib.request
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path
from typing import IO

from playwright.sync_api import Page, sync_playwright

BREEDTES = [1280, 390]
LETTERTYPE = '"General Sans", "Plus Jakarta Sans"'
WACHTTIJD_MS = 60_000


def zoek_vrije_poort() -> int:
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


@contextmanager
def start_dashboard(app: Path, data: Path) -> Iterator[str]:
    """Start Streamlit met het databestand als pad en geeft de URL terug."""
    poort = zoek_vrije_poort()
    log = tempfile.TemporaryFile()  # een pipe kan vollopen en Streamlit laten hangen
    proces = subprocess.Popen(
        [
            sys.executable,
            "-m",
            "streamlit",
            "run",
            app.name,
            "--server.headless",
            "true",
            "--server.port",
            str(poort),
            "--browser.gatherUsageStats",
            "false",
            "--",
            str(data),
        ],
        cwd=app.parent,
        stdout=subprocess.DEVNULL,
        stderr=log,
    )
    url = f"http://localhost:{poort}"
    try:
        wacht_op_server(url, proces, log)
        yield url
    finally:
        proces.terminate()
        proces.wait(timeout=10)
        log.close()


def wacht_op_server(url: str, proces: subprocess.Popen, log: IO[bytes]) -> None:
    eind = time.monotonic() + WACHTTIJD_MS / 1000
    while time.monotonic() < eind:
        if proces.poll() is not None:
            log.seek(0)
            raise SystemExit(f"Streamlit stopte meteen:\n{log.read().decode()}")
        try:
            with urllib.request.urlopen(f"{url}/_stcore/health", timeout=2) as antwoord:
                if antwoord.status == 200:
                    return
        except OSError:
            time.sleep(0.5)
    raise SystemExit(f"Streamlit startte niet binnen {WACHTTIJD_MS // 1000} seconden")


def maak_screenshot(page: Page, naam: str, breedte: int, uit: Path) -> list[str]:
    """Maakt de viewport zo hoog als de pagina, bewaart de screenshot en geeft de problemen."""
    # Streamlit scrolt binnen stMain, dus de viewport moet de hele hoogte krijgen. Na het vergroten
    # tekent Plotly opnieuw en kan de pagina langer worden: meet opnieuw tot de hoogte vaststaat.
    hoogte = 0
    for _ in range(5):
        nieuw = page.evaluate(
            "() => document.querySelector('[data-testid=\"stMain\"]')?.scrollHeight ?? 900"
        )
        if nieuw == hoogte:
            break
        hoogte = nieuw
        page.set_viewport_size({"width": breedte, "height": max(hoogte, 600)})
        page.wait_for_timeout(500)
    page.evaluate("async () => { await document.fonts.ready; }")
    page.wait_for_timeout(300)  # tekst opnieuw tekenen in het geladen lettertype
    bestand = uit / f"{naam}-{breedte}.png"
    page.screenshot(path=bestand, full_page=True)

    problemen = []
    if page.locator('[data-testid="stException"]').count():
        problemen.append(f"{bestand.name}: Streamlit toont een fout (traceback)")
    lettertype = page.evaluate(
        "() => { const h = document.querySelector('h1');"
        " return h ? getComputedStyle(h).fontFamily : ''; }"
    )
    if not lettertype.startswith(LETTERTYPE):
        problemen.append(f"{bestand.name}: lettertype van h1 is {lettertype!r}")
    print(f"  {bestand}  (h1: {lettertype})")
    return problemen


def fotografeer_flow(
    url: str, breedte: int, uit: Path, naam_na_doorgaan: str, wacht_na: str
) -> list[str]:
    """Opent het eerste scherm, klikt op Doorgaan en fotografeert beide toestanden."""
    problemen = []
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={"width": breedte, "height": 900})
        page.set_default_timeout(WACHTTIJD_MS)
        page.goto(url)
        page.get_by_text("Stap 1 van 2").first.wait_for()
        if naam_na_doorgaan == "dashboard":
            problemen += maak_screenshot(page, "upload", breedte, uit)
        page.get_by_role("button", name="Doorgaan").click()
        page.locator(wacht_na).first.wait_for()
        page.wait_for_load_state("networkidle")
        problemen += maak_screenshot(page, naam_na_doorgaan, breedte, uit)
        browser.close()
    return problemen


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--app", type=Path, required=True, help="pad naar app.py")
    parser.add_argument("--data", type=Path, required=True, help="databestand voor het dashboard")
    parser.add_argument("--uit", type=Path, default=Path("uitvoer/screenshots"))
    args = parser.parse_args()

    app, data, uit = args.app.resolve(), args.data.resolve(), args.uit.resolve()
    uit.mkdir(parents=True, exist_ok=True)
    problemen: list[str] = []

    with start_dashboard(app, data) as url:
        for breedte in BREEDTES:
            problemen += fotografeer_flow(url, breedte, uit, "dashboard", "text=Stap 2 van 2")

    with tempfile.TemporaryDirectory() as tijdelijk:
        fout = Path(tijdelijk) / "zonder_kolommen.csv"
        fout.write_text("onbekend\n1\n", encoding="utf-8")
        with start_dashboard(app, fout) as url:
            for breedte in BREEDTES:
                problemen += fotografeer_flow(
                    url, breedte, uit, "foutmelding", '[data-testid="stAlertContentError"]'
                )

    if problemen:
        print("\nProblemen:\n- " + "\n- ".join(problemen))
        sys.exit(1)
    print("\nGeen fouten van Streamlit, lettertype klopt. Bekijk de screenshots zelf.")


if __name__ == "__main__":
    main()
