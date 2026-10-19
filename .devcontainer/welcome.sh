#!/usr/bin/env bash
set -euo pipefail

BOLD='\033[1m'
CYAN='\033[0;36m'
GREEN='\033[0;32m'
RESET='\033[0m'

echo ""
echo -e "${BOLD}${CYAN}╔══════════════════════════════════════════════╗${RESET}"
echo -e "${BOLD}${CYAN}║        DAIR — Agentic Coding Sessie          ║${RESET}"
echo -e "${BOLD}${CYAN}╚══════════════════════════════════════════════╝${RESET}"
echo ""
echo -e "  Welkom! Je werkomgeving is klaar."
echo ""

for cli in claude entire; do
  if command -v "$cli" &>/dev/null; then
    echo -e "  ${GREEN}✔${RESET}  $cli beschikbaar"
  else
    echo -e "  $cli niet gevonden. Roep de begeleider."
  fi
done

if [[ -n "${ANTHROPIC_FOUNDRY_API_KEY:-}" ]]; then
  echo -e "  ${GREEN}✔${RESET}  Workshop-key staat klaar"
else
  echo -e "  Geen workshop-key gevonden. Roep de begeleider."
fi

echo ""
echo -e "  ${BOLD}Aan de slag:${RESET}"
echo ""
echo -e "  1. Klik op het ${BOLD}oranje Claude-icoon${RESET} rechtsboven in de editor."
echo -e "  2. Typ ${CYAN}/1-verkennen${RESET} in het vak onderaan het paneel en druk op Enter."
echo ""
echo -e "  Met ${CYAN}/${RESET} zie je alle beschikbare skills."
echo ""
