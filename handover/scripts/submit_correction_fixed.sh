#!/usr/bin/env bash
# submit_correction.sh — Finalize a correction cycle and archive results (Final Fixed Version)

set -euo pipefail

info()  { echo -e "\033[0;36m[INFO]\033[0m  $*"; }
ok()    { echo -e "\033[0;32m[OK]\033[0m    $*"; }
warn()  { echo -e "\033[0;33m[WARN]\033[0m  $*"; }
error() { echo -e "\033[0;31m[ERROR]\033[0m $*" >&2; exit 1; }

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
cd "$REPO_ROOT"

CORRECTION_FILE="docs/issues/issue_correction.md"
DONE_DIR="docs/issues/done"
HANDOVER_MEMO="handover/handover_memo_latest.md"
CURRENT_BRANCH="$(git branch --show-current)"

if [ ! -f "$CORRECTION_FILE" ]; then
  error "Correction file not found: $CORRECTION_FILE"
fi

# Robust issue number extraction (no complex regex operators)
TARGET_ISSUE=$(grep -i "Target Issue:" "$CORRECTION_FILE" | grep -o "I[0-9][0-9]" | head -n 1 | sed 's/I//') || ""

if [ -n "$TARGET_ISSUE" ]; then
  ARCHIVE_FILE=$(ls -t "${DONE_DIR}/issue_"*"_${TARGET_ISSUE}.md" 2>/dev/null | head -n 1) || ""
  if [ -n "$ARCHIVE_FILE" ] && [ -f "$ARCHIVE_FILE" ]; then
    info "Appending correction to archive: $ARCHIVE_FILE"
    printf "\n\n---\n## Correction Cycle\n\n" >> "$ARCHIVE_FILE"
    cat "$CORRECTION_FILE" >> "$ARCHIVE_FILE"
    git add "$ARCHIVE_FILE"
  fi
fi

info "Finalizing correction"
git add "$HANDOVER_MEMO"
mv "$CORRECTION_FILE" "${CORRECTION_FILE}.completed"
git add "${CORRECTION_FILE}.completed"

if ! git diff --staged --quiet; then
  git commit -m "fix: execute corrections for Issue I${TARGET_ISSUE:-XX}"
fi

git push origin "$CURRENT_BRANCH"
git commit --allow-empty -m "MARKER: [AI-CLAIM] Correction I${TARGET_ISSUE:-XX} completed"
git push origin "$CURRENT_BRANCH"

echo ""
ok "Correction submitted and archived successfully."
