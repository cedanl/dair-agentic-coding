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
    echo -e "  $cli niet gevonden — neem contact op met de begeleider."
  fi
done

echo ""
echo -e "  ${BOLD}Aan de slag:${RESET}"
echo -e "  Open een terminal en typ:  ${BOLD}${CYAN}claude${RESET}"
echo ""
