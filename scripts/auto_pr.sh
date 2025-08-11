#!/usr/bin/env bash
set -euo pipefail
BRANCH="feature/tests/${1:-story}-$(date +%s)"
MSG="chore(tests): add generated tests for ${1:-story}"

git checkout -b "$BRANCH"
git add tests artifacts || true
git commit -m "$MSG" || true
git push -u origin "$BRANCH"

if command -v gh >/dev/null 2>&1; then
  gh pr create --fill --base main || true
else
  echo "PR created on branch $BRANCH. Install gh to open automatically."
fi
