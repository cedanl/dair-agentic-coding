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
            f"Je hebt in fase {state['fase']} {MAX_RONDES} keer gevraagd. Stel geen nieuwe vraag meer. "
            "Start nu het spiegelmoment: vat in twee of drie zinnen samen wat de gebruiker tot nu toe "
            "koos en waarom, en vraag of dat klopt met hun eigen inzicht. Zeg daarna dat ze hun "
            "resultaat kort live presenteren aan de groep en dat we daarna door gaan naar de volgende "
            "fase. Ga pas verder als de gebruiker aangeeft dat het zover is."
        ),
    }}))
STATE.write_text(json.dumps(state))
