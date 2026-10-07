#!/usr/bin/env python3
"""Stuur de workshop-review naar voxpop (PostgreSQL op het SURF Developer Platform).

  feedback.py questions                 vragenlijst (JSON) van de server
  feedback.py submit '{"nuttig":"5"}'   antwoorden versturen (of JSON via stdin)
  feedback.py form                      invulformulier in de terminal, zonder Claude

Configuratie (omgevingsvariabelen):
  VOXPOP_FEEDBACK_TOKEN   workshop-token van de begeleider (of in ~/.config/dair/feedback-token)
  VOXPOP_URL              default https://voxpop.playground.sdp.surf.nl
  VOXPOP_WORKSHOP         workshop-id, default dair

De deelnemer is anoniem: er wordt een willekeurig id gebruikt dat in
~/.config/dair/participant-id blijft staan. Alleen stdlib, geen installatie nodig.
"""
import json
import os
import secrets
import sys
import urllib.error
import urllib.request
from pathlib import Path

CONFIG_DIR = Path.home() / ".config" / "dair"
URL = os.environ.get("VOXPOP_URL", "https://voxpop.playground.sdp.surf.nl").rstrip("/")
WORKSHOP = os.environ.get("VOXPOP_WORKSHOP", "dair")


def fail(message: str, code: int = 1) -> None:
    print(f"Fout: {message}", file=sys.stderr)
    sys.exit(code)


def token() -> str:
    value = os.environ.get("VOXPOP_FEEDBACK_TOKEN", "").strip()
    path = CONFIG_DIR / "feedback-token"
    if not value and path.exists():
        value = path.read_text().strip()
    if not value:
        fail("geen workshop-token. Vraag de begeleider om het token en zet het met:\n"
             "  mkdir -p ~/.config/dair && read -rs t && echo \"$t\" > ~/.config/dair/feedback-token")
    return value


def participant_id() -> str:
    path = CONFIG_DIR / "participant-id"
    if path.exists():
        return path.read_text().strip()
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    value = "p_" + secrets.token_hex(8)
    path.write_text(value + "\n")
    return value


def request(method: str, path: str, body: dict | None = None, headers: dict | None = None) -> tuple[int, dict]:
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(URL + path, data=data, method=method,
                                 headers={"Content-Type": "application/json", **(headers or {})})
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            return resp.status, json.loads(resp.read() or b"{}")
    except urllib.error.HTTPError as exc:
        try:
            return exc.code, json.loads(exc.read() or b"{}")
        except ValueError:
            return exc.code, {}
    except (urllib.error.URLError, TimeoutError) as exc:
        fail(f"{URL} niet bereikbaar ({exc})")
    raise AssertionError("unreachable")


def send(answers: dict) -> bool:
    status, out = request("POST", "/feedback/api/submit",
                          {"workshop": WORKSHOP, "participant": participant_id(), "answers": answers},
                          {"X-Workshop-Token": token()})
    if status == 201:
        print(f"Verstuurd (id {out.get('id')}). Bedankt!")
        return True
    messages = {
        401: "token ongeldig. Vraag de begeleider om het juiste token.",
        429: "je hebt net al feedback gestuurd; probeer het over een paar minuten opnieuw.",
        503: "feedback staat op de server (nog) uit of de database is niet bereikbaar.",
    }
    fail(messages.get(status) or f"HTTP {status}: {out.get('error', 'onbekende fout')}")
    return False


def ask(question: dict) -> str:
    """Eén vraag stellen; leeg antwoord = overslaan. Herhaalt bij een ongeldige keuze."""
    print(f"\n{question['text']}")
    options = question.get("options")
    if question["type"] == "scale":
        low, high = question["labels"]
        print(f"  {question['options'][0]} = {low}, {question['options'][-1]} = {high}")
    elif options:
        for i, option in enumerate(options, 1):
            print(f"  {i}) {option}")
    while True:
        raw = input("> ").strip()
        if not raw:
            return ""
        if question["type"] == "text":
            return raw
        if question["type"] == "scale" and raw in options:
            return raw
        if question["type"] == "choice" and raw.isdigit() and 1 <= int(raw) <= len(options):
            return options[int(raw) - 1]
        if raw in options:
            return raw
        print("  Ongeldige keuze, probeer opnieuw (Enter = overslaan).")


def form() -> None:
    token()  # eerst controleren, zodat een ontbrekend token niet pas na het invullen blijkt
    status, questions = request("GET", "/feedback/api/questions")
    if status != 200:
        fail(f"vragen ophalen mislukt (HTTP {status})")
    print("Review van de sessie. Enter slaat een vraag over; je review is anoniem.")
    try:
        answers = {q["id"]: v for q in questions if (v := ask(q))}
        if not answers:
            fail("geen enkele vraag beantwoord; er is niets verstuurd.")
        print("\nJe review:")
        for q in questions:
            if q["id"] in answers:
                print(f"  - {q['text']} {answers[q['id']]}")
        if input("\nVersturen? [j/N] ").strip().lower() not in ("j", "ja", "y", "yes"):
            fail("niet verstuurd.")
    except (EOFError, KeyboardInterrupt):
        print()
        fail("afgebroken; er is niets verstuurd.")
    send(answers)


def main(argv: list[str]) -> None:
    if len(argv) < 2 or argv[1] not in ("questions", "submit", "form"):
        fail("Gebruik: feedback.py questions | submit [JSON] | form", 2)
    if argv[1] == "form":
        form()
        return
    if argv[1] == "questions":
        status, out = request("GET", "/feedback/api/questions")
        if status != 200:
            fail(f"vragen ophalen mislukt (HTTP {status})")
        print(json.dumps(out, ensure_ascii=False, indent=2))
        return

    raw = argv[2] if len(argv) > 2 else sys.stdin.read()
    try:
        answers = json.loads(raw)
    except ValueError:
        fail("antwoorden zijn geen geldige JSON")
    send(answers)


if __name__ == "__main__":
    main(sys.argv)
