#!/usr/bin/env bash
# Start het dashboard uit dashboard/ met de demodata, of met een eigen csv als eerste argument.
set -euo pipefail

root="$(git rev-parse --show-toplevel)"
csv="$(realpath "${1:-$root/data/demodata_1cho.csv}")"

if [[ ! -f "$root/dashboard/app.py" ]]; then
  echo "✘ Geen dashboard gevonden in dashboard/. Bouw het eerst met /bouwen_dashboard."
  exit 1
fi
if [[ ! -f "$csv" ]]; then
  echo "✘ Databestand niet gevonden: $csv"
  exit 1
fi

echo "Dashboard start met $csv"
echo "Open poort 8501 via de melding rechtsonder, of via het tabblad Poorten (wereldbolletje, nieuw tabblad). Stoppen: Ctrl+C"
cd "$root/dashboard"
exec uv run --no-project --with-requirements requirements.txt streamlit run app.py -- "$csv"
