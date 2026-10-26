#!/usr/bin/env bash
# claude_quota_wait.sh — GUARD_CMD for batch_window.sh: before each Claude run, wait
# until the Claude Code 5-hour window ("Current session") is at most <SESSION_MAX>%
# used (checking every 5 minutes, so the series sleeps through a full window instead
# of failing mid-run), and stop the series (exit 1) if a weekly limit is too high.
#
# Usage: scripts/claude_quota_wait.sh <SESSION_MAX> <WEEK_MAX> [<FABLE_MAX>]
#   e.g. scripts/claude_quota_wait.sh 65 95 90
# Reads the limits with `claude -p "/usage"` (slash command; no model turn), as quota.sh.
set -u
SMAX="$1"; WMAX="$2"; FMAX="${3:-100}"
usage() {
  CLAUDE_CONFIG_DIR="$HOME/notebook/git/thm01-R-claude-config/batch" DISABLE_AUTOUPDATER=1 \
    timeout 90 "$HOME/.local/share/claude/versions/2.1.288" -p "/usage" 2>/dev/null
}
pct() { echo "$1" | grep -E "^$2" | head -1 | grep -oE '[0-9]+%' | head -1 | tr -d '%'; }
fails=0
while :; do
  out=$(cd /tmp && usage)
  s=$(pct "$out" "Current session"); w=$(pct "$out" "Current week \(all models\)"); f=$(pct "$out" "Current week \(Fable\)")
  echo "$(date '+%Y-%m-%d %H:%M:%S') claude session ${s:-?}% (max $SMAX), week ${w:-?}% (max $WMAX), fable ${f:-?}% (max $FMAX)"
  if [ -z "$s" ] || [ -z "$w" ]; then
    fails=$((fails + 1)); [ "$fails" -ge 6 ] && { echo "usage unreadable 6 times"; exit 1; }
    sleep 300; continue
  fi
  [ "$w" -gt "$WMAX" ] && { echo "weekly limit above $WMAX%"; exit 1; }
  [ -n "$f" ] && [ "$f" -gt "$FMAX" ] && { echo "Fable weekly limit above $FMAX%"; exit 1; }
  [ "$s" -le "$SMAX" ] && exit 0
  sleep 300
done
