#!/usr/bin/env bash
set -euo pipefail
BRANCH="feature/tests/${1:-story}-$(date +%s)"
MSG="chore(tests): add generated tests for ${1:-story}"

if ! git diff --quiet; then
  echo "Working tree has changes; committing";
fi

git checkout -b "$BRANCH"
git add tests artifacts || true
git commit -m "$MSG" || true
git push -u origin "$BRANCH"

echo "Opening PR via GitHub CLI (if available)..."
if command -v gh >/dev/null 2>&1; then
  gh pr create --fill --base main || true
else
  echo "gh not installed; create PR manually."
fi
