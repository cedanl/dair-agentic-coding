"""Geeft een link waarmee de gebruiker een uitkomst met één klik in de browser opent.

Gebruik, vanuit de hoofdmap van de repo:

    python .claude/skills/verkennen_data/assets/toon.py dashboard.html

Een browser kan een bestand in een Codespace alleen via een webadres openen. Daarom start dit script (als dat
nog niet draait) een kleine webserver op poort 8765 die uitsluitend data-profiel.html, schets.html en
dashboard.html uit de hoofdmap serveert, en drukt het de link af: in Codespaces het doorgestuurde adres
(https://<codespace>-8765.app.github.dev/...), op een eigen computer http://localhost:8765/... De poort is
privé: alleen wie in de Codespace is ingelogd, kan de pagina zien. Alleen de standaardbibliotheek.
"""

import http.server
import os
import socket
import subprocess
import sys
import time
from pathlib import Path

POORT = 8765
BESTANDEN = {"data-profiel.html", "schets.html", "dashboard.html"}


class Alleen(http.server.SimpleHTTPRequestHandler):
    """Serveert alleen de drie uitkomsten, nooit de data of de rest van de repo."""

    def do_GET(self) -> None:
        naam = self.path.split("?")[0].lstrip("/")
        if naam not in BESTANDEN:
            self.send_error(404)
            return
        self.path = "/" + naam
        super().do_GET()

    def end_headers(self) -> None:
        self.send_header("Cache-Control", "no-store")  # altijd de nieuwste versie
        super().end_headers()

    def log_message(self, *args) -> None:
        pass


def poort_bezet() -> bool:
    with socket.socket() as s:
        return s.connect_ex(("127.0.0.1", POORT)) == 0


def start_server() -> None:
    """Start dit script als server, los van dit proces, zodat hij blijft draaien."""
    opties = {"cwd": Path.cwd(), "stdout": subprocess.DEVNULL, "stderr": subprocess.DEVNULL,
              "stdin": subprocess.DEVNULL}
    if os.name == "nt":
        opties["creationflags"] = subprocess.DETACHED_PROCESS | subprocess.CREATE_NEW_PROCESS_GROUP
    else:
        opties["start_new_session"] = True
    subprocess.Popen([sys.executable, __file__, "--server"], **opties)
    for _ in range(50):
        if poort_bezet():
            return
        time.sleep(0.1)
    sys.exit(f"De webserver op poort {POORT} startte niet.")


def maak_link(naam: str) -> str:
    codespace = os.environ.get("CODESPACE_NAME")
    domein = os.environ.get("GITHUB_CODESPACES_PORT_FORWARDING_DOMAIN", "app.github.dev")
    if codespace:
        return f"https://{codespace}-{POORT}.{domein}/{naam}"
    return f"http://localhost:{POORT}/{naam}"


def main() -> None:
    if sys.argv[1:] == ["--server"]:
        http.server.ThreadingHTTPServer(("127.0.0.1", POORT), Alleen).serve_forever()
        return
    if len(sys.argv) != 2 or Path(sys.argv[1]).name not in BESTANDEN:
        sys.exit(f"Gebruik: python toon.py <{' | '.join(sorted(BESTANDEN))}>")
    naam = Path(sys.argv[1]).name
    if not Path(naam).is_file():
        sys.exit(f"{naam} staat niet in de hoofdmap. Draai eerst de skill die het maakt.")
    if not poort_bezet():
        start_server()
    print(maak_link(naam))


if __name__ == "__main__":
    main()
