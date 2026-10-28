#!/usr/bin/env bash
# Writes the workshop key to ~/.claude/settings.json so both the CLI and the VS Code extension pick it up.
set -euo pipefail

settings="$HOME/.claude/settings.json"

has_key() {
  [[ -f "$settings" ]] &&
    node -e 'process.exit(require(process.argv[1]).env?.ANTHROPIC_FOUNDRY_API_KEY ? 0 : 1)' "$settings"
}

# Schrijft de key uit de omgeving (Codespace-secret) weg naar settings.json,
# zodat ook de VS Code-extension hem oppikt. Maakt het bestand aan indien nodig.
sync_key() {
  [[ -n "${ANTHROPIC_FOUNDRY_API_KEY:-}" ]] || return 0
  mkdir -p "$(dirname "$settings")"
  KEY="$ANTHROPIC_FOUNDRY_API_KEY" node -e '
const fs = require("fs");
const f = process.argv[1];
const s = fs.existsSync(f) ? JSON.parse(fs.readFileSync(f, "utf8")) : {};
s.env = s.env || {};
if (s.env.ANTHROPIC_FOUNDRY_API_KEY !== process.env.KEY) {
  s.env.ANTHROPIC_FOUNDRY_API_KEY = process.env.KEY;
  fs.writeFileSync(f, JSON.stringify(s, null, 2) + "\n");
}
' "$settings"
  chmod 600 "$settings"
}

# De image-standaard wint van een oude of verkeerd getypte resource in settings.json.
# Alleen actief als de resource in de omgeving niet-leeg is, zodat een leeg
# ${localEnv:...} nooit de goede waarde wist.
sync_resource() {
  [[ -n "${ANTHROPIC_FOUNDRY_RESOURCE:-}" && -f "$settings" ]] || return 0
  node -e '
const fs = require("fs");
const f = process.argv[1];
const s = JSON.parse(fs.readFileSync(f, "utf8"));
if (!s.env?.ANTHROPIC_FOUNDRY_RESOURCE || s.env.ANTHROPIC_FOUNDRY_RESOURCE !== process.env.ANTHROPIC_FOUNDRY_RESOURCE) {
  s.env = s.env || {};
  s.env.ANTHROPIC_FOUNDRY_RESOURCE = process.env.ANTHROPIC_FOUNDRY_RESOURCE;
  fs.writeFileSync(f, JSON.stringify(s, null, 2) + "\n");
}
' "$settings"
}

if [[ "${1:-}" == "--if-needed" ]] && { [[ -n "${ANTHROPIC_FOUNDRY_API_KEY:-}" ]] || has_key; }; then
  sync_key
  sync_resource
  exit 0
fi

# Key via Codespace-secret aanwezig maar nog niet weggeschreven (bv. handmatige
# run): gebruik hem direct, zonder paste-prompt. Zonder secret volgt de prompt.
if [[ -n "${ANTHROPIC_FOUNDRY_API_KEY:-}" ]]; then
  sync_key
  sync_resource
  echo ""
  echo "✔ Foundry-key overgenomen uit het Codespace-secret."
  echo "✔ Resource: ${ANTHROPIC_FOUNDRY_RESOURCE:-onbekend}"
  echo "✔ Klaar. Start Claude met: claude (of open het Claude-paneel)"
  exit 0
fi

echo ""
echo "DAIR — Claude koppelen"

# De key staat versleuteld in de repo (key.enc); de workshopcode van de begeleider ontsleutelt hem.
# De code is bewust zichtbaar tijdens het typen, zodat typfouten meteen opvallen.
enc=(/workspaces/*/.devcontainer/key.enc)
key=""
if [[ -f "${enc[0]}" ]]; then
  read -rp "Workshopcode van de begeleider (Enter = key zelf plakken): " code
  code="$(printf '%s' "$code" | tr -d '[:space:]')"
  if [[ -n "$code" ]]; then
    if ! key="$(printf '%s' "$code" | openssl enc -d -aes-256-cbc -pbkdf2 -a -pass stdin -in "${enc[0]}" 2>/dev/null)" || [[ -z "$key" ]]; then
      echo "✘ Onjuiste workshopcode. Probeer opnieuw met: dair-onboard"
      exit 1
    fi
  fi
fi

if [[ -z "$key" ]]; then
  read -rsp "Plak de workshop-key van de begeleider (Enter = overslaan): " key
  echo ""
fi
key="$(printf '%s' "$key" | tr -d '[:space:]')"
if [[ -z "$key" ]]; then
  echo "Overgeslagen. Later instellen kan met: dair-onboard"
  exit 0
fi

resource="${ANTHROPIC_FOUNDRY_RESOURCE:-}"
if [[ -z "$resource" ]]; then
  read -rp "Foundry resource-naam: " resource
fi

# Accepteer ook een geplakte URL (https://naam.services.ai.azure.com/...) en pak de naam eruit
resource="${resource#*://}"
resource="${resource%%[./]*}"
resource="$(printf '%s' "$resource" | tr -d '[:space:]')"
if [[ -z "$resource" ]]; then
  echo "✘ Geen resource-naam opgegeven. Probeer opnieuw met: dair-onboard"
  exit 1
fi

# Laat zien dat het plakken gelukt is: alleen de laatste 4 tekens zichtbaar
if (( ${#key} > 4 )); then
  masked="$(printf '%*s' $(( ${#key} - 4 )) '' | tr ' ' '*')${key: -4}"
else
  masked="$(printf '%*s' "${#key}" '' | tr ' ' '*')"
fi
echo "✔ Key ontvangen (${#key} tekens): $masked"
echo "✔ Resource: $resource"

mkdir -p "$HOME/.claude"
KEY="$key" RESOURCE="$resource" node -e '
const fs = require("fs");
const f = process.argv[1];
const s = fs.existsSync(f) ? JSON.parse(fs.readFileSync(f, "utf8")) : {};
s.env = { ...s.env, ANTHROPIC_FOUNDRY_API_KEY: process.env.KEY, ANTHROPIC_FOUNDRY_RESOURCE: process.env.RESOURCE };
fs.writeFileSync(f, JSON.stringify(s, null, 2) + "\n");
' "$settings"
chmod 600 "$settings"

host="$resource.services.ai.azure.com"
if getent hosts "$host" >/dev/null 2>&1; then
  echo "✔ DNS ok: $host"
else
  echo "⚠ Kan $host niet vinden (DNS). Controleer de resource-naam of je netwerk."
fi

echo "✔ Klaar. Start Claude met: claude (of open het Claude-paneel)"
