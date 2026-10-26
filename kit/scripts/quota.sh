#!/usr/bin/env bash
# quota.sh — Print the current usage limits of Claude Code and Antigravity
# without opening an interactive session, and append them to a log.
#   Claude Code: `claude -p "/usage"` (slash command; no model turn)
#   agy:         `agy -p "/usage"`   (slash command; no model turn)
#   Copilot:     `gh api /copilot_internal/user` (monthly credits; `copilot -p "/usage"`
#                is sent to the model instead, so it is not used)
# Both read the account's limits at the time of the call (unlike the /usage
# panel of an open session, which keeps the value from when it was opened).
#
# Usage: scripts/quota.sh [LOG]      (default LOG: experiment/quota_log.tsv)
set -u
HERE="$(cd "$(dirname "$0")/.." && pwd)"
LOG="${1:-$HERE/quota_log.tsv}"
TMP="$(mktemp -d)"; cd "$TMP"
now="$(date '+%Y-%m-%d %H:%M:%S')"
CLAUDE_CONFIG_DIR="$HOME/notebook/git/thm01-R-claude-config/batch" DISABLE_AUTOUPDATER=1 \
  timeout 90 "$HOME/.local/share/claude/versions/2.1.288" -p "/usage" 2>/dev/null \
  | grep -E '^Current' | sed "s/^/$now\tclaude\t/" | tee -a "$LOG"
HOME="$HOME/notebook/git/thm01-R-agy-home/base" timeout 60 agy -p "/usage" 2>/dev/null \
  | sed "s/^/$now\tagy\t/" | tee -a "$LOG"
# Copilot: monthly credits via the (undocumented) endpoint used by the editors
gh api /copilot_internal/user 2>/dev/null | python3 -c '
import json,sys
d=json.load(sys.stdin); p=d["quota_snapshots"]["premium_interactions"]
print("premium_interactions\tremaining\t%s/%s\t%.1f%%\treset %s" % (p["remaining"],p["entitlement"],p["percent_remaining"],d.get("quota_reset_date")))' \
  | sed "s/^/$now\tcopilot\t/" | tee -a "$LOG"
cd /; rm -rf "$TMP"
