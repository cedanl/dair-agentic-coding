#!/usr/bin/env python3
"""Houdt Claude tegen zolang de deelnemer de nieuwste link nog niet in het gesprek heeft gezien.

De scripts drukken een linkregel af (`### 👉 [Open je schets](...)`, ook voor het dashboard en het dataprofiel),
maar die uitvoer ziet de deelnemer niet: alleen Claude leest hem. Staat de nieuwste link nog niet in een bericht
van Claude, dan weigert de PreToolUse-hook een keuzevraag, en laat de Stop-hook Claude niet stoppen, met de
opdracht de regel eerst te tonen. Beide hooks staan in .claude/settings.json.
"""
import json
import re
import sys
from pathlib import Path

LINKREGEL = re.compile(r"### 👉 \[Open je [^\]]+\]\((\S+?)\)")


def teksten(inhoud) -> list[str]:
    if isinstance(inhoud, str):
        return [inhoud]
    if isinstance(inhoud, list):
        return [t for blok in inhoud if isinstance(blok, dict) for t in teksten(blok.get("text") or blok.get("content"))]
    return []


def main() -> None:
    invoer = json.load(sys.stdin)
    pad = Path(invoer.get("transcript_path") or "")
    if not pad.is_file() or invoer.get("stop_hook_active"):  # na één keer tegenhouden niet blijven herhalen
        return
    regel, url, getoond = None, None, True
    for lijn in pad.read_text(encoding="utf-8").splitlines():
        try:
            bericht = json.loads(lijn).get("message") or {}
        except json.JSONDecodeError:
            continue
        blokken = bericht.get("content") if isinstance(bericht.get("content"), list) else []
        for blok in blokken:
            if blok.get("type") == "tool_result":
                for tekst in teksten(blok.get("content")):
                    for gevonden in LINKREGEL.finditer(tekst):
                        regel, url, getoond = gevonden.group(0), gevonden.group(1), False
            elif blok.get("type") == "text" and bericht.get("role") == "assistant" and url and url in blok.get("text", ""):
                getoond = True
    if not regel or getoond:
        return
    reden = ("De deelnemer ziet de uitvoer van het script niet, dus ook de link niet. Zet eerst deze regel "
             f"letterlijk in je bericht, als eigen regel:\n\n{regel}\n\n")
    sys.stdout.reconfigure(encoding="utf-8")
    if invoer.get("hook_event_name") == "Stop":
        print(json.dumps({"decision": "block", "reason": reden + "Sluit daarna af zoals de skill zegt."},
                         ensure_ascii=False))
    else:
        print(json.dumps({"hookSpecificOutput": {"hookEventName": "PreToolUse", "permissionDecision": "deny",
                                                 "permissionDecisionReason": reden + "Stel daarna dezelfde vraag opnieuw."}},
                         ensure_ascii=False))


if __name__ == "__main__":
    main()
