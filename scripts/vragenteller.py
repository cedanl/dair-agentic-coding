#!/usr/bin/env python3
"""Telt AskUserQuestion-rondes per fase en zet bij het maximum het spiegelmoment in het gesprek.

Skills draaien `vragenteller.py fase N` bij de start van een fase. De PostToolUse-hook in
.claude/settings.json draait het script zonder argumenten na elke AskUserQuestion.
"""
import json
import sys
import tempfile
from pathlib import Path

MAX_RONDES = 3
STATE = Path(tempfile.gettempdir()) / "dair-vragenteller.json"

if sys.argv[1:2] == ["fase"]:
    STATE.write_text(json.dumps({"fase": int(sys.argv[2]), "rondes": 0}))
    sys.exit(0)

if not STATE.exists():
    sys.exit(0)

state = json.loads(STATE.read_text())
state["rondes"] += 1
if state["rondes"] >= MAX_RONDES:
    state["rondes"] = 0
    print(json.dumps({"hookSpecificOutput": {
        "hookEventName": "PostToolUse",
        "additionalContext": (
            f"Je hebt in fase {state['fase']} {MAX_RONDES} keer gevraagd. "
            "Stel geen vragen en gebruik geen tools meer. Toon nu precies dit bericht, in gewoon Nederlands "
            "en zonder extra uitleg:\n\n"
            "**Even pauze: kijk op van je scherm.**\n\n"
            "Dit heb je tot nu toe gekozen:\n"
            "- (maximaal drie korte punten, in jouw woorden en met het waarom)\n\n"
            "De speaker pakt nu het woord. Typ **door** zodra de speaker zegt dat je verder mag.\n\n"
            "Doe daarna niets tot de gebruiker 'door' typt."
        ),
    }}))
STATE.write_text(json.dumps(state))
