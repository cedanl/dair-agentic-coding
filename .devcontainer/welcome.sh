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
echo ""
echo -e "  Je hebt twee manieren om te werken:\n"
echo -e "  1. ${BOLD}VSCode Claude Code extension${RESET} (aanbevolen)"
echo -e "     Open het Claude paneel in de linker balk"
echo -e "     De extension is al geïnstalleerd in deze workspace\n"
echo -e "  2. ${BOLD}Terminal CLI${RESET}"
echo -e "     Open een terminal en typ: ${CYAN}claude${RESET}\n"
echo -e "  Typ ${CYAN}/help${RESET} voor alle beschikbare commands."
echo ""
