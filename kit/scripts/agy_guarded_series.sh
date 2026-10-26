#!/usr/bin/env bash
# agy_guarded_series.sh — Run Gemini batch runs one after another, but before each
# run read the Antigravity weekly quota from a herdr pane that shows agy's /usage
# (read-only: `herdr pane read`), and stop when it is below a threshold, so that
# quota stays for the Manager of the A / F− runs (Gemini 3.1 Pro on agy).
#
# Usage:
#   scripts/agy_guarded_series.sh <PANE_ID> <MIN_WEEKLY_PCT> <LOG> <COND>:<TAG>:<MODEL>:<MODEL NAME> ...
set -u
PANE="$1"; MIN="$2"; LOG="$3"; shift 3
HERE="$(cd "$(dirname "$0")" && pwd)"
weekly() {  # Gemini weekly limit remaining, read live with `agy -p /usage`
  # (PANE is kept for compatibility and no longer used: the /usage panel of an
  # open session keeps the value from when it was opened)
  (cd /tmp && HOME="$HOME/notebook/git/thm01-R-agy-home/base" timeout 60 agy -p "/usage" 2>/dev/null) \
    | awk -F'\t' '$1=="Gemini Models" && $2=="Weekly Limit Remaining"{gsub("%","",$3); print $3; exit}'
}
for spec in "$@"; do
  w="$(weekly)"
  echo "quota $(date '+%Y-%m-%d %H:%M:%S') weekly_remaining=${w:-unreadable}" >> "$LOG"
  if [ -z "$w" ] || awk -v w="$w" -v m="$MIN" 'BEGIN{exit !(w < m)}'; then
    echo "stop: weekly quota ${w:-unreadable}% < $MIN% (or unreadable) before $spec" >> "$LOG"; break
  fi
  "$HERE/batch_window.sh" "$(date '+%Y-%m-%d %H:%M:%S')" "$LOG" "$spec"
  tail -1 "$LOG" | grep -q '^stop:' && break
done
echo "series end $(date '+%Y-%m-%d %H:%M:%S')" >> "$LOG"
