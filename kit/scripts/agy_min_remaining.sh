#!/usr/bin/env bash
# agy_min_remaining.sh — Exit 0 only if the agy Gemini weekly limit remaining is at
# least <PERCENT> (used as GUARD_CMD of batch_window.sh, so automatic Gemini runs
# leave enough of the shared weekly quota for the Managers of human-gated runs).
#
# Usage: scripts/agy_min_remaining.sh <PERCENT>
set -u
MIN="$1"
line=$(HOME="$HOME/notebook/git/thm01-R-agy-home/base" timeout 60 agy -p "/usage" 2>/dev/null \
  | grep -E 'Gemini Models.*Weekly Limit Remaining' | head -1)
pct=$(echo "$line" | grep -oE '[0-9]+%' | head -1 | tr -d '%')
echo "agy Gemini weekly remaining: ${pct:-unknown}% (minimum $MIN%)"
[ -n "$pct" ] && [ "$pct" -ge "$MIN" ]
