#!/usr/bin/env bash
# submit_correction.sh — Finalize a correction cycle and archive results
#
# Usage:
#   ./handover/scripts/submit_correction.sh
#
# Description:
#   This script automates the completion of a correction cycle. It:
#   1. Appends the correction details to the original archived issue in docs/issues/done/
#   2. Updates the handover memo
#   3. Commits and pushes changes
#   4. Creates an [AI-CLAIM] marker commit

set -euo pipefail

# Colors
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

# 1. Pre-checks
if [ ! -f "$CORRECTION_FILE" ]; then
  error "Correction file not found: $CORRECTION_FILE"
fi

# 2. Extract Target Issue Number
# Expected format in issue_correction.md: **Target Issue**: I{NN}-{n}
TARGET_ISSUE=$(grep -i "Target Issue" "$CORRECTION_FILE" | grep -oE "I[0-9]{2}" | sed 's/I//' || true)
if [ -z "$TARGET_ISSUE" ]; then
  warn "Could not determine target issue number from $CORRECTION_FILE. Archiving may be incomplete."
fi

# 3. Integrated Archiving
if [ -n "$TARGET_ISSUE" ]; then
  # Find the most recent done file for this issue number
  ARCHIVE_FILE=$(ls -t "${DONE_DIR}/issue_"*"_${TARGET_ISSUE}.md" 2>/dev/null | head -n 1) || ""
  
  if [ -n "$ARCHIVE_FILE" ] && [ -f "$ARCHIVE_FILE" ]; then
    info "Appending correction to archive: $ARCHIVE_FILE"
    printf "\n\n---\n## Correction Cycle\n\n" >> "$ARCHIVE_FILE"
    cat "$CORRECTION_FILE" >> "$ARCHIVE_FILE"
    git add "$ARCHIVE_FILE"
  else
    warn "Archive file for issue $TARGET_ISSUE not found in $DONE_DIR. Skipping append."
  fi
fi

# 4. Cleanup and Staging
info "Finalizing correction"
git add "$HANDOVER_MEMO"
# We don't remove the file yet to allow the AI to 'git add' it if they want, 
# but the standard procedure is that the human deletes it after review.
# HOWEVER, for this automated study, we will move it to a backup or delete it to signal completion.
mv "$CORRECTION_FILE" "${CORRECTION_FILE}.completed"
git add "${CORRECTION_FILE}.completed"

# 5. Commit and Push
COMMIT_MSG="fix: execute corrections for Issue I${TARGET_ISSUE:-XX}"
if ! git diff --staged --quiet; then
  info "Committing changes"
  git commit -m "$COMMIT_MSG"
fi

info "Pushing to $CURRENT_BRANCH"
git push origin "$CURRENT_BRANCH"

# 6. Create AI-CLAIM marker
info "Creating [AI-CLAIM] marker commit"
git commit --allow-empty -m "MARKER: [AI-CLAIM] Correction I${TARGET_ISSUE:-XX} completed"
git push origin "$CURRENT_BRANCH"

echo ""
ok "Correction submitted and archived successfully."
info "The file $CORRECTION_FILE has been moved to ${CORRECTION_FILE}.completed"
