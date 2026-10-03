#!/usr/bin/env bash
# Creates the GitHub repo under your account, pushes, and publishes the first release.
# Usage: ./publish.sh [repo-name]     (default: the-interstice)
# Needs the GitHub CLI (brew install gh). You log in yourself; no tokens are stored here.
set -euo pipefail
cd "$(dirname "$0")"
REPO="${1:-the-interstice}"

command -v gh >/dev/null || { echo "GitHub CLI not found. Install it with: brew install gh"; exit 1; }
gh auth status >/dev/null 2>&1 || gh auth login --web
OWNER="$(gh api user --jq .login)"
echo "Publishing as $OWNER/$REPO"

# Point the manifest, download and README URLs at your account.
for f in README.md module.json tools/build.py; do
  sed -i.bak "s#github.com/OWNER/the-interstice#github.com/$OWNER/$REPO#g" "$f" && rm -f "$f.bak"
done
git add -A
git -c user.name="$OWNER" -c user.email="$OWNER@users.noreply.github.com" commit -qm "Point URLs at $OWNER/$REPO" || true

gh repo create "$OWNER/$REPO" --public --source . --remote origin --push

VERSION="$(node -p "require('./module.json').version" 2>/dev/null || python3 -c "import json;print(json.load(open('module.json'))['version'])")"
gh release create "v$VERSION" --title "The Interstice v$VERSION" \
  --notes "Liminal-horror adventure for D&D 5e (2024), levels 5–8. Requires Monk's Active Tile Triggers."

echo "Waiting for the Release Module workflow to build and attach module.zip..."
sleep 5
gh run watch "$(gh run list --workflow release.yml --limit 1 --json databaseId --jq '.[0].databaseId')" --exit-status

echo
echo "Done. Install in Foundry with this manifest URL:"
echo "  https://github.com/$OWNER/$REPO/releases/latest/download/module.json"
