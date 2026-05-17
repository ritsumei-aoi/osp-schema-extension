#!/usr/bin/env bash
# close_issue.sh — Phase 4 completion automation script (single-issue version)
#
# Overview:
#   Executes Phase 4 completion processing for a single issue.
#   For multiple issues, the caller (AI agent) splits issue_open.md
#   beforehand and provides individual files.
#
# Usage:
#   ./handover/scripts/close_issue.sh [OPTIONS] <YYMMDD> <NN> <issue_label> <next_issue_number>
#
# Options:
#   --issue-file <path>      Issue content file to archive (default: issue_open.md)
#   --remaining-file <path>  Content to place in issue_open.md after processing (default: template)
#   --dry-run                No writes or git operations; display plan only
#   --skip-git               Skip git operations (archive only)
#   --skip-taio-check        Skip '### Response' section existence check
#   --help                   Show help
#
# Examples:
#   # Normal (single issue, template reset)
#   ./handover/scripts/close_issue.sh 260413 13 "I13: Phase4 script fix" 14
#
#   # Split file + remaining file (multiple issues)
#   ./handover/scripts/close_issue.sh \
#     --issue-file /tmp/issue_i12.md \
#     --remaining-file /tmp/issue_i13.md \
#     260413 12 "I12: mathqform setup" 14
#
#   # dry-run to confirm plan
#   ./handover/scripts/close_issue.sh --dry-run 260413 13 "I13: script fix" 14
#
# Prerequisites:
#   - Issue completion criteria are marked [x], ### Response sections added
#   - handover_memo_latest.md is updated (or will be after script execution)
#   - Current directory is the repository root
#   - Working on study/workflow_issue branch
#
# Design principles:
#   - Process only 1 issue per execution (multi-issue handling is caller's responsibility)
#   - git add targets specific files only (no -A)
#   - --dry-run performs no file or git operations
#   - On error, stop immediately; completed operations are not rolled back

set -euo pipefail

# ========================================
# Utility functions
# ========================================

# Color output (terminal-aware)
if [ -t 1 ]; then
  RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[0;33m'
  CYAN='\033[0;36m'; NC='\033[0m'
else
  RED=''; GREEN=''; YELLOW=''; CYAN=''; NC=''
fi

info()  { echo -e "${CYAN}[INFO]${NC}  $*"; }
ok()    { echo -e "${GREEN}[OK]${NC}    $*"; }
warn()  { echo -e "${YELLOW}[WARN]${NC}  $*"; }
error() { echo -e "${RED}[ERROR]${NC} $*" >&2; }

# dry-run aware file operation wrappers
do_cp() {
  if [ "$DRY_RUN" = true ]; then
    info "(dry-run) cp $1 → $2"
  else
    cp "$1" "$2"
  fi
}

do_write() {
  # $1: destination, stdin: content
  if [ "$DRY_RUN" = true ]; then
    info "(dry-run) write → $1"
    cat > /dev/null  # consume stdin
  else
    cat > "$1"
  fi
}

do_git() {
  if [ "$DRY_RUN" = true ]; then
    info "(dry-run) git $*"
  elif [ "$SKIP_GIT" = true ]; then
    info "(skip-git) git $*"
  else
    git "$@"
  fi
}

# ========================================
# Argument parsing
# ========================================

DRY_RUN=false
SKIP_GIT=false
SKIP_TAIO_CHECK=false
ISSUE_FILE=""
REMAINING_FILE=""

show_help() {
  sed -n '2,/^$/{ s/^# //; s/^#$//; p; }' "$0"
  exit 0
}

# Parse option arguments
while [ $# -gt 0 ]; do
  case "$1" in
    --dry-run)       DRY_RUN=true; shift ;;
    --skip-git)      SKIP_GIT=true; shift ;;
    --skip-taio-check) SKIP_TAIO_CHECK=true; shift ;;
    --issue-file)    ISSUE_FILE="$2"; shift 2 ;;
    --remaining-file) REMAINING_FILE="$2"; shift 2 ;;
    --help|-h)       show_help ;;
    -*)              error "Unknown option: $1"; exit 1 ;;
    *)               break ;;  # Start of positional arguments
  esac
done

# Check positional arguments
if [ $# -lt 4 ]; then
  error "Usage: $0 [OPTIONS] <YYMMDD> <NN> <issue_label> <next_issue_number>"
  echo ""
  echo "  YYMMDD:            Date (e.g., 260413)"
  echo "  NN:                Sequential number (e.g., 13)"
  echo "  issue_label:       Commit message label (e.g., 'I13: Phase4 script fix')"
  echo "  next_issue_number: Next issue number (e.g., 14)"
  echo ""
  echo "Options: --issue-file <path>  --remaining-file <path>  --dry-run  --skip-git  --help"
  exit 1
fi

YYMMDD="$1"
NN="$2"
ISSUE_LABEL="$3"
NEXT_NN="$4"

# ========================================
# Path configuration
# ========================================

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
cd "$REPO_ROOT"

ISSUE_OPEN="docs/issues/issue_open.md"
DONE_DIR="docs/issues/done"
DONE_FILE="${DONE_DIR}/issue_${YYMMDD}_${NN}.md"
TEMPLATE="docs/issues/template_issue_open.md"
HISTORY="docs/issues/issue_history.md"
HANDOVER_MEMO="handover/handover_memo_latest.md"

# Use issue_open.md if --issue-file is not specified
if [ -z "$ISSUE_FILE" ]; then
  ISSUE_FILE="$ISSUE_OPEN"
fi

# ========================================
# Pre-checks (validate everything before writing)
# ========================================

echo ""
info "=== Pre-checks ==="

ERRORS=0

# 1. Branch check
CURRENT_BRANCH="$(git branch --show-current)"
if [[ ! "$CURRENT_BRANCH" =~ ^study/thm ]]; then
  error "Current branch is '$CURRENT_BRANCH', expected an 'ai/...' branch"
  ERRORS=$((ERRORS + 1))
fi

# 2. Working tree clean check (strict only when --issue-file is used)
if [ "$ISSUE_FILE" != "$ISSUE_OPEN" ]; then
  DIRTY="$(git status --porcelain)"
  if [ -n "$DIRTY" ]; then
    warn "Working tree has uncommitted changes:"
    echo "$DIRTY" | head -10
    # Warning only (not an error — AI agent may have intentional changes)
  fi
fi

# 3. Archive target duplicate check
if [ -f "$DONE_FILE" ]; then
  error "Archive target already exists: $DONE_FILE"
  ERRORS=$((ERRORS + 1))
fi

# 4. Issue file existence check
if [ ! -f "$ISSUE_FILE" ]; then
  error "Issue file not found: $ISSUE_FILE"
  ERRORS=$((ERRORS + 1))
fi

# 5. Template existence check (only if no remaining-file)
if [ -z "$REMAINING_FILE" ] && [ ! -f "$TEMPLATE" ]; then
  error "Template not found: $TEMPLATE (needed for issue_open.md reset)"
  ERRORS=$((ERRORS + 1))
fi

# 6. Remaining file existence check (if specified)
if [ -n "$REMAINING_FILE" ] && [ ! -f "$REMAINING_FILE" ]; then
  error "Remaining file not found: $REMAINING_FILE"
  ERRORS=$((ERRORS + 1))
fi

# 7. Done directory existence check
if [ ! -d "$DONE_DIR" ]; then
  error "Done directory not found: $DONE_DIR"
  ERRORS=$((ERRORS + 1))
fi

# 8. Response section existence check (R15)
if [ "$SKIP_TAIO_CHECK" = false ] && [ -f "$ISSUE_FILE" ]; then
  if ! grep -q '### Response' "$ISSUE_FILE"; then
    error "Issue file is missing '### Response' section: $ISSUE_FILE (use --skip-taio-check to override)"
    ERRORS=$((ERRORS + 1))
  fi
fi

# 9. Completion criteria checkbox [x] check
if [ -f "$ISSUE_FILE" ]; then
  UNCHECKED=$(grep -c '\- \[ \]' "$ISSUE_FILE" 2>/dev/null || true)
  if [ "$UNCHECKED" -gt 0 ]; then
    error "Issue file has $UNCHECKED unchecked checkbox(es) ('- [ ]'): $ISSUE_FILE"
    ERRORS=$((ERRORS + 1))
  fi
fi

if [ "$ERRORS" -gt 0 ]; then
  error "Pre-checks failed ($ERRORS error(s)). Aborting."
  exit 1
fi

ok "All pre-checks passed"

# ========================================
# Display execution plan
# ========================================

echo ""
info "=== Execution plan ==="
echo "  Source:       $ISSUE_FILE"
echo "  Archive to:  $DONE_FILE"
if [ -n "$REMAINING_FILE" ]; then
  echo "  Reset from:  $REMAINING_FILE"
else
  echo "  Reset from:  $TEMPLATE (next: I${NEXT_NN})"
fi
echo "  Commit msg:  $ISSUE_LABEL"
echo "  Dry-run:     $DRY_RUN"
echo "  Skip-git:    $SKIP_GIT"
echo ""

# ========================================
# Step 1: Archive
# ========================================

info "Step 1: Archiving → $DONE_FILE"
do_cp "$ISSUE_FILE" "$DONE_FILE"
ok "Step 1 done"

# ========================================
# Step 2: Reset issue_open.md
# ========================================

if [ -n "$REMAINING_FILE" ]; then
  # Replace with remaining file content
  info "Step 2: Replacing $ISSUE_OPEN with $REMAINING_FILE"
  do_cp "$REMAINING_FILE" "$ISSUE_OPEN"
else
  # Reset from template
  info "Step 2: Resetting $ISSUE_OPEN from template (next: I${NEXT_NN})"
  if [ "$DRY_RUN" = true ]; then
    info "(dry-run) sed 's/{NN}/${NEXT_NN}/g' $TEMPLATE > $ISSUE_OPEN"
  else
    sed "s/{NN}/${NEXT_NN}/g" "$TEMPLATE" > "$ISSUE_OPEN"
  fi
fi
ok "Step 2 done"

# ========================================
# Step 3: Stage specific files
# ========================================

info "Step 3: Staging specific files"
# Files that are always staged
STAGE_FILES=("$DONE_FILE" "$ISSUE_OPEN")

# Stage issue_history.md if changed
if git diff --name-only -- "$HISTORY" | grep -q .; then
  STAGE_FILES+=("$HISTORY")
fi
if git diff --name-only --cached -- "$HISTORY" | grep -q .; then
  : # already staged
fi

# Stage handover_memo_latest.md if changed
if git diff --name-only -- "$HANDOVER_MEMO" | grep -q .; then
  STAGE_FILES+=("$HANDOVER_MEMO")
fi

# Stage close_issue.sh itself if changed
SCRIPT_REL="handover/scripts/close_issue.sh"
if git diff --name-only -- "$SCRIPT_REL" | grep -q .; then
  STAGE_FILES+=("$SCRIPT_REL")
fi

for f in "${STAGE_FILES[@]}"; do
  do_git add "$f"
done
ok "Step 3 done (staged ${#STAGE_FILES[@]} file(s): ${STAGE_FILES[*]})"

# ========================================
# Step 4: Commit
# ========================================

COMMIT_MSG="${ISSUE_LABEL}

Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>"

info "Step 4: Committing"
do_git commit -m "$COMMIT_MSG"
ok "Step 4 done"

# ========================================
# Step 5: Push
# ========================================

info "Step 5: Pushing to origin $CURRENT_BRANCH"
do_git push origin $CURRENT_BRANCH
ok "Step 5 done"

# ========================================
# Step 6: Create AI-CLAIM Marker
# ========================================

info "Step 6: Creating [AI-CLAIM] marker commit"
do_git commit --allow-empty -m "MARKER: [AI-CLAIM] Issue I${NN} completed"
do_git push origin $CURRENT_BRANCH
ok "Step 6 done"

# ========================================
# Completion summary
# ========================================

echo ""
echo "==========================================="
if [ "$DRY_RUN" = true ]; then
  warn "DRY-RUN complete — no changes were made"
else
  ok "Phase 4 complete"
fi
echo "  Archived:  $DONE_FILE"
echo "  Next issue: I${NEXT_NN}-1"
echo "  Branch:    $CURRENT_BRANCH (retained independent status)"
echo "==========================================="
