#!/usr/bin/env bash
# submit_correction.sh — Mark a Git-based human intervention as fixed by AI
#
# Usage:
#   ./handover/scripts/submit_correction.sh
#
# Description:
#   This script is used by the AI Agent after completing the fixes requested in
#   docs/issues/issue_correction.md. It updates the handover memo and creates
#   a standard [AI-CLAIM] marker commit to signal that the correction is ready
#   for human review.

set -euo pipefail

# Utility functions
info()  { echo -e "\033[0;36m[INFO]\033[0m  $*"; }
ok()    { echo -e "\033[0;32m[OK]\033[0m    $*"; }
error() { echo -e "\033[0;31m[ERROR]\033[0m $*" >&2; exit 1; }

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
cd "$REPO_ROOT"

CORRECTION_FILE="docs/issues/issue_correction.md"
HANDOVER_MEMO="handover/handover_memo_latest.md"
CURRENT_BRANCH="$(git branch --show-current)"

# Pre-checks
if [ ! -f "$CORRECTION_FILE" ]; then
  error "Correction file not found: $CORRECTION_FILE. Are you currently in a correction cycle?"
fi

# Stage files
info "Staging handover memo"
git add "$HANDOVER_MEMO"

# Commit changes if any exist
if ! git diff --staged --quiet; then
  info "Committing handover memo updates"
  git commit -m "docs: update handover memo after executing corrections"
fi

# Push changes
info "Pushing code changes"
git push origin "$CURRENT_BRANCH"

# Create AI-CLAIM marker
info "Creating [AI-CLAIM] marker commit for Correction"
git commit --allow-empty -m "MARKER: [AI-CLAIM] Correction completed"
git push origin "$CURRENT_BRANCH"

echo ""
ok "Correction submitted successfully. Awaiting human review."
echo "Please instruct the human to delete $CORRECTION_FILE if they approve the fix."
