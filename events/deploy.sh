#!/bin/bash
# One-time deploy. Needs: CLOUDFLARE_API_TOKEN (Workers + D1 edit) and CLOUDFLARE_ACCOUNT_ID in the environment.
set -e
cd "$(dirname "$0")"
command -v npx >/dev/null || { echo "node/npx required"; exit 1; }
if grep -q REPLACE_AFTER_D1_CREATE wrangler.toml; then
  OUT=$(npx -y wrangler@latest d1 create rz-events 2>&1 || true)
  ID=$(echo "$OUT" | grep -oE '[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}' | head -1)
  if [ -z "$ID" ]; then ID=$(npx -y wrangler@latest d1 list --json | python3 -c "import json,sys;print([d['uuid'] for d in json.load(sys.stdin) if d['name']=='rz-events'][0])"); fi
  sed -i "s/REPLACE_AFTER_D1_CREATE/$ID/" wrangler.toml
  echo "D1 database id: $ID"
fi
npx -y wrangler@latest d1 execute rz-events --remote --file=schema.sql
npx -y wrangler@latest deploy
echo "Now put the printed workers.dev URL into gen_web.py EVENTS_URL and run python3 gen_web.py"
