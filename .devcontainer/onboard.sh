#!/usr/bin/env bash
# Writes the workshop key to ~/.claude/settings.json so both the CLI and the VS Code extension pick it up.
set -euo pipefail

settings="$HOME/.claude/settings.json"

has_key() {
  [[ -f "$settings" ]] &&
    node -e 'process.exit(require(process.argv[1]).env?.ANTHROPIC_FOUNDRY_API_KEY ? 0 : 1)' "$settings"
}

if [[ "${1:-}" == "--if-needed" ]] && { [[ -n "${ANTHROPIC_FOUNDRY_API_KEY:-}" ]] || has_key; }; then
  exit 0
fi

echo ""
echo "DAIR — Claude koppelen"
read -rsp "Plak de workshop-key van de begeleider (Enter = overslaan): " key
echo ""
if [[ -z "$key" ]]; then
  echo "Overgeslagen. Later instellen kan met: dair-onboard"
  exit 0
fi

resource="${ANTHROPIC_FOUNDRY_RESOURCE:-}"
if [[ -z "$resource" ]]; then
  read -rp "Foundry resource-naam: " resource
fi

mkdir -p "$HOME/.claude"
KEY="$key" RESOURCE="$resource" node -e '
const fs = require("fs");
const f = process.argv[1];
const s = fs.existsSync(f) ? JSON.parse(fs.readFileSync(f, "utf8")) : {};
s.env = { ...s.env, ANTHROPIC_FOUNDRY_API_KEY: process.env.KEY, ANTHROPIC_FOUNDRY_RESOURCE: process.env.RESOURCE };
fs.writeFileSync(f, JSON.stringify(s, null, 2) + "\n");
' "$settings"
chmod 600 "$settings"

echo "✔ Klaar. Start Claude met: claude (of open het Claude-paneel)"
