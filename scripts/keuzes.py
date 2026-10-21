#!/usr/bin/env python3
"""Het ene bestand met alle keuzes van de deelnemer: mijn-keuzes.json in de hoofdmap.

    python3 scripts/keuzes.py nieuw                              begin opnieuw (bij de start van /1-verkennen)
    python3 scripts/keuzes.py zet doelgroep "Studieadviseur"     een keuze vastleggen of vervangen
    python3 scripts/keuzes.py zet vergelijken "sector,opleiding"
    python3 scripts/keuzes.py wens "filter op geslacht" --voor 2-schetsen   een wens voor later
    python3 scripts/keuzes.py wens-klaar 1                       een wens is verwerkt
    python3 scripts/keuzes.py toon                               alles wat er staat

Dit bestand is de waarheid: het profiel, de schets en het dashboard lezen hun keuzes hier en schrijven terug
wat ze echt deden. Een keuze mag als code of als label ("C" of "Hangt stoppen samen met je vooropleiding?",
"sector" of "Sector"); het script zet hem om naar de code uit het casusbestand. Alleen de standaardbibliotheek.
"""
import argparse
import json
import sys
from pathlib import Path

BESTAND = Path("mijn-keuzes.json")
CSV = "data/demodata_1cho.csv"
SLEUTELS = ["doelgroep", "vraag", "vergelijken", "filter", "bovenaan", "titel"]
STAPPEN = ["1-verkennen", "2-schetsen", "3-bouwen", "later"]


def lees() -> dict:
    if BESTAND.is_file():
        return json.loads(BESTAND.read_text(encoding="utf-8"))
    return {"csv": CSV, "keuzes": {}, "gezien": [], "wensen": []}


def schrijf(stand: dict) -> None:
    BESTAND.write_text(json.dumps(stand, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def lees_casus(stand: dict) -> dict:
    return json.loads(Path(stand["csv"]).with_suffix(".casus.json").read_text(encoding="utf-8"))


def zoek(waarde: str, opties: dict, veld: str = "label") -> str:
    """Een code (A, sector) of een label naar de code; anders een melding met wat wel kan."""
    w = waarde.strip().lower()
    for code, inhoud in opties.items():
        if w in (code.lower(), str(inhoud.get(veld, "")).lower(), str(inhoud.get("vraag", "")).lower()):
            return code
    sys.exit(f"Onbekend: '{waarde}'. Kies uit: " + ", ".join(f"{c} ({o.get(veld, c)})" for c, o in opties.items()))


def normaliseer(sleutel: str, waarde: str, casus: dict) -> str:
    if sleutel == "doelgroep":
        return zoek(waarde, casus["doelgroepen"])
    if sleutel == "vraag":
        return zoek(waarde, casus["vragen"])
    if sleutel in ("vergelijken", "filter"):
        if sleutel == "filter" and waarde.strip().lower() in ("geen", "geen filter", ""):
            return "geen"
        # Instroomjaar is alleen een filter: de lijn over de jaren laat het al als vergelijking zien
        opties = {n: u for n, u in casus["uitsplitsingen"].items() if sleutel == "filter" or not u.get("alleen_filter")}
        return ",".join(dict.fromkeys(zoek(w, opties) for w in waarde.replace(" en ", ",").split(",") if w.strip()))
    if sleutel == "bovenaan":
        return "jaar" if "jaar" in waarde.lower() else "groep"
    return "" if waarde.strip().lower() == "standaard" else waarde.strip()


def toon(stand: dict) -> None:
    casus, k = lees_casus(stand), stand["keuzes"]
    label = lambda n: casus["uitsplitsingen"][n]["label"]  # noqa: E731
    leesbaar = {
        "doelgroep": casus["doelgroepen"][k["doelgroep"]]["label"] if k.get("doelgroep") else None,
        "vraag": f"{k['vraag']}: {casus['vragen'][k['vraag']]['vraag']}" if k.get("vraag") else None,
        "vergelijken": ", ".join(label(n) for n in k["vergelijken"].split(",")) if k.get("vergelijken") else None,
        "filter": ("geen" if k["filter"] == "geen" else ", ".join(label(n) for n in k["filter"].split(",")))
                  if k.get("filter") else None,
        "bovenaan": {"groep": "de vergelijking tussen groepen", "jaar": "de ontwikkeling over de jaren"}.get(k.get("bovenaan")),
        "titel": k.get("titel") or ("(de vraag)" if k.get("vraag") else None),
    }
    print("Keuzes:")
    for sleutel in SLEUTELS:
        print(f"- {sleutel}: {leesbaar[sleutel] or '(nog niet gekozen)'}")
    open_ = [(i, w) for i, w in enumerate(stand["wensen"], 1) if not w["klaar"]]
    print("Open wensen:" if open_ else "Open wensen: geen")
    for i, w in open_:
        print(f"{i}. {w['tekst']} (voor {w['voor']})")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Het ene bestand met alle keuzes: mijn-keuzes.json.")
    sub = parser.add_subparsers(dest="actie", required=True)
    nieuw = sub.add_parser("nieuw")
    nieuw.add_argument("--csv", default=CSV)
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

    stand = {"csv": args.csv, "keuzes": {}, "gezien": [], "wensen": []} if args.actie == "nieuw" else lees()
    if args.actie == "zet":
        stand["keuzes"][args.sleutel] = normaliseer(args.sleutel, args.waarde, lees_casus(stand))
    elif args.actie == "wens":
        stand["wensen"].append({"tekst": args.tekst, "voor": args.voor, "klaar": False})
    elif args.actie == "wens-klaar":
        if not 1 <= args.nummer <= len(stand["wensen"]):
            sys.exit(f"Wens {args.nummer} bestaat niet.")
        stand["wensen"][args.nummer - 1]["klaar"] = True
    schrijf(stand)
    toon(stand)
