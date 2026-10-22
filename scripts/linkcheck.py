#!/usr/bin/env python3
"""Houdt Claude tegen zolang de deelnemer een link nog niet in het gesprek heeft gezien.

De scripts drukken een linkregel af (`### 👉 [Open je schets](...)`, ook voor het dashboard, het dataprofiel en de
review), maar die uitvoer ziet de deelnemer niet: alleen Claude leest hem. Dat geldt voor elke link, niet alleen de
laatste. Staat een afgedrukte link nog niet in een bericht van Claude, dan weigert de PreToolUse-hook een
keuzevraag, en laat de Stop-hook Claude niet stoppen, met de opdracht de regels eerst te tonen.

Bij een bash-commando werkt de hook ook: een link ín het commando (bijvoorbeeld met echo) weigert hij, want ook
die ziet de deelnemer niet; en drukt een commando linkregels af, dan krijgt Claude meteen de opdracht ze allemaal
in zijn volgende bericht te zetten, buiten elk commando. Alle hooks staan in .claude/settings.json.

Bij een keuzevraag over de schets of het dashboard moet de nieuwste link bovendien in Claudes bericht vlak boven
de vraag staan (na het laatste antwoord of de laatste uitvoer), ook als hij eerder al eens getoond is: anders is
hij bij een tussenvraag al weggescrold.
"""
import json
import re
import sys
import time
from pathlib import Path

WACHTTIJDEN = (0, 0.5, 1.0, 1.5)  # seconden vóór elke poging om het transcript te lezen
LINKREGEL = re.compile(r"### 👉 \[Open je [^\]]+\]\((https?://\S+?)\)")  # geen voorbeelden als (<link>) uit de skills


def teksten(inhoud) -> list[str]:
    if isinstance(inhoud, str):
        return [inhoud]
    if isinstance(inhoud, list):
        return [t for blok in inhoud if isinstance(blok, dict) for t in teksten(blok.get("text") or blok.get("content"))]
    return []


def alle_tekst(inhoud) -> list[str]:
    """Alle tekst in de uitvoer van een commando, hoe die ook genest is (stdout, stderr, blokken)."""
    if isinstance(inhoud, str):
        return [inhoud]
    if isinstance(inhoud, dict):
        inhoud = list(inhoud.values())
    if isinstance(inhoud, list):
        return [t for deel in inhoud for t in alle_tekst(deel)]
    return []


def linkregels(tekst: str) -> dict[str, str]:
    """De linkregels in een tekst, per url, in volgorde."""
    return {gevonden.group(1): gevonden.group(0) for gevonden in LINKREGEL.finditer(tekst)}


def toon_eerst(regels: list[str]) -> str:
    woorden = "deze regel letterlijk in je bericht, als" if len(regels) == 1 else \
        f"deze {len(regels)} regels letterlijk in je bericht, elk als"
    return ("De deelnemer ziet commando's en hun uitvoer niet, dus ook de link niet. Zet eerst, buiten elk commando, "
            f"{woorden} eigen regel:\n\n" + "\n\n".join(regels) + "\n\n")


def bash(invoer: dict) -> None:
    """Link nooit in een bash-commando; na een commando dat links afdrukt meteen de opdracht ze allemaal te tonen."""
    if invoer.get("hook_event_name") == "PreToolUse":
        if "👉" in str((invoer.get("tool_input") or {}).get("command", "")):
            print(json.dumps({"hookSpecificOutput": {"hookEventName": "PreToolUse", "permissionDecision": "deny",
                                                     "permissionDecisionReason": "Zet de link niet in een bash-commando: "
                                                     "de deelnemer ziet commando's en hun uitvoer niet. Zet de "
                                                     "linkregel letterlijk in je bericht, als eigen regel."}},
                             ensure_ascii=False))
        return
    regels = linkregels("\n".join(alle_tekst(invoer.get("tool_response"))))
    if regels:
        print(json.dumps({"hookSpecificOutput": {"hookEventName": "PostToolUse",
                                                 "additionalContext": toon_eerst(list(regels.values()))}},
                         ensure_ascii=False))


def main() -> None:
    invoer = json.load(sys.stdin)
    sys.stdout.reconfigure(encoding="utf-8")
    if invoer.get("tool_name") == "Bash":
        bash(invoer)
        return
    pad = Path(invoer.get("transcript_path") or "")
    if not pad.is_file() or invoer.get("stop_hook_active"):  # na één keer tegenhouden niet blijven herhalen
        return
    # De extensie schrijft Claudes laatste bericht soms pas net na het starten van de hook in het transcript.
    # Daarom pas tegenhouden als de link er na even wachten nog steeds niet staat.
    for wacht in WACHTTIJDEN:
        time.sleep(wacht)
        regels = ontbrekend(pad, invoer)
        if not regels:
            return
    if invoer.get("hook_event_name") == "Stop":
        print(json.dumps({"decision": "block", "reason": toon_eerst(regels) + "Sluit daarna af zoals de skill zegt."},
                         ensure_ascii=False))
    else:
        print(json.dumps({"hookSpecificOutput": {"hookEventName": "PreToolUse", "permissionDecision": "deny",
                                                 "permissionDecisionReason": toon_eerst(regels) + "Stel daarna dezelfde vraag opnieuw."}},
                         ensure_ascii=False))


def ontbrekend(pad: Path, invoer: dict) -> list[str]:
    """De linkregels die de deelnemer nog moet zien voordat Claude mag vragen of stoppen."""
    open_, laatste, vlak_boven = {}, None, False  # open_: afgedrukte links die nog niet in een bericht stonden
    for lijn in pad.read_text(encoding="utf-8").splitlines():
        try:
            rij = json.loads(lijn)
        except json.JSONDecodeError:
            continue
        # alleen het gesprek zelf: geen kopieën van eerdere verzoeken (api-request-blob) of subagents
        if rij.get("type") not in ("user", "assistant") or rij.get("isSidechain"):
            continue
        bericht = rij.get("message") or {}
        blokken = bericht.get("content") if isinstance(bericht.get("content"), list) else []
        if bericht.get("role") == "user":  # nieuw antwoord of nieuwe uitvoer: de link staat niet meer vlak boven
            vlak_boven = False
        for blok in blokken:
            if blok.get("type") == "tool_result":
                for tekst in teksten(blok.get("content")):
                    for url, regel in linkregels(tekst).items():
                        open_.pop(url, None)  # opnieuw afgedrukt: achteraan, als nieuwste
                        open_[url], laatste = regel, (url, regel)
            elif blok.get("type") == "text" and bericht.get("role") == "assistant":
                tekst = blok.get("text", "")
                for url in [url for url in open_ if url in tekst]:
                    del open_[url]
                if laatste and laatste[0] in tekst:
                    vlak_boven = True
    # Bij Stop geeft Claude Code het laatste bericht ook zelf mee: dat telt, ook als het nog niet in het transcript staat
    slot = invoer.get("last_assistant_message")
    if isinstance(slot, str):
        for url in [url for url in open_ if url in slot]:
            del open_[url]
    regels = list(open_.values())
    over_schets_of_dashboard = laatste and ("Open je schets" in laatste[1] or "Open je dashboard" in laatste[1])
    if (invoer.get("hook_event_name") != "Stop" and over_schets_of_dashboard and not vlak_boven
            and laatste[1] not in regels):
        regels.append(laatste[1])
    return regels


if __name__ == "__main__":
    main()
