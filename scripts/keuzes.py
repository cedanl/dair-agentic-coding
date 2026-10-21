#!/usr/bin/env python3
"""Onthoudt de keuzes en wensen van de deelnemer over alle skills heen, in mijn-keuzes.json in de hoofdmap.

    python3 scripts/keuzes.py nieuw                                  begin opnieuw (bij de start van /1-verkennen)
    python3 scripts/keuzes.py zet doelgroep "Studieadviseur"         een keuze vastleggen of vervangen
    python3 scripts/keuzes.py wens "filter op geslacht" --voor 2-schetsen   een wens voor later
    python3 scripts/keuzes.py wens-klaar 1                           een wens is verwerkt
    python3 scripts/keuzes.py toon                                   alles wat er staat

Zo weet elke skill wat de deelnemer eerder zei, ook als dat bij een andere vraag hoorde. Alleen de
standaardbibliotheek.
"""
import argparse
import json
from pathlib import Path

BESTAND = Path("mijn-keuzes.json")
SLEUTELS = ["doelgroep", "vraag", "vergelijken", "filter", "bovenaan"]
STAPPEN = ["1-verkennen", "2-schetsen", "3-bouwen", "later"]


def lees() -> dict:
    if BESTAND.is_file():
        return json.loads(BESTAND.read_text(encoding="utf-8"))
    return {"keuzes": {}, "wensen": []}


def schrijf(stand: dict) -> None:
    BESTAND.write_text(json.dumps(stand, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def toon(stand: dict) -> None:
    print("Keuzes:")
    for sleutel in SLEUTELS:
        print(f"- {sleutel}: {stand['keuzes'].get(sleutel, '(nog niet gekozen)')}")
    open_ = [(i, w) for i, w in enumerate(stand["wensen"], 1) if not w["klaar"]]
    print("Open wensen:" if open_ else "Open wensen: geen")
    for i, w in open_:
        print(f"{i}. {w['tekst']} (voor {w['voor']})")


parser = argparse.ArgumentParser(description="Onthoudt keuzes en wensen in mijn-keuzes.json.")
sub = parser.add_subparsers(dest="actie", required=True)
sub.add_parser("nieuw")
zet = sub.add_parser("zet")
zet.add_argument("sleutel", choices=SLEUTELS)
zet.add_argument("waarde")
wens = sub.add_parser("wens")
wens.add_argument("tekst")
wens.add_argument("--voor", choices=STAPPEN, default="later")
klaar = sub.add_parser("wens-klaar")
klaar.add_argument("nummer", type=int)
sub.add_parser("toon")
args = parser.parse_args()

stand = {"keuzes": {}, "wensen": []} if args.actie == "nieuw" else lees()
if args.actie == "zet":
    stand["keuzes"][args.sleutel] = args.waarde
elif args.actie == "wens":
    stand["wensen"].append({"tekst": args.tekst, "voor": args.voor, "klaar": False})
elif args.actie == "wens-klaar":
    if not 1 <= args.nummer <= len(stand["wensen"]):
        raise SystemExit(f"Wens {args.nummer} bestaat niet.")
    stand["wensen"][args.nummer - 1]["klaar"] = True
schrijf(stand)
toon(stand)
