#!/usr/bin/env bash
# batch_window.sh — Wait until a start time, then run automatic runs one after
# another (used to start 25 minutes before a usage-limit reset and run across it).
#
# Usage:
#   scripts/batch_window.sh "<YYYY-mm-dd HH:MM:SS>" <LOG> <COND>:<TAG>[:<MODEL>:<MODEL NAME>] ...
#   A MODEL starting with "gemini" runs with the Antigravity CLI harness (--harness agy),
#   one starting with "gpt" with the Copilot CLI harness (--harness copilot).
#   CLAUDE_VERSION=<version> in the environment is passed as --claude-version to Claude runs;
#   a fifth field (<COND>:<TAG>:<MODEL>:<MODEL NAME>:<VERSION>) sets it for one run.
# Optional environment (added 2026-10-08):
#   NO_START_AFTER="<YYYY-mm-dd HH:MM:SS>"  start no new run after that time.
#   STOP_FILE=<path>   start no new run once this file exists (the author is ready
#                      for a human-gated run: `touch` it; the current run finishes).
#   GUARD_CMD="<cmd>"  run before each run; a non-zero exit stops the series
#                      (e.g. a quota check).
#   WAIT_PID=<pid>     wait until that process has exited before the first run.
#   SKIP_EXISTING=1    skip (do not stop at) a run whose log directory already exists.
# Example:
#   scripts/batch_window.sh "2026-10-04 12:55:00" /tmp/w1.out C:sonnet46-b03 G:sonnet46-b04
#
# A run is started only if the previous one completed; if a run does not end
# with status "completed" (e.g. a usage-limit or output-limit error), the rest
# are skipped.
set -u
START="$1"; LOG="$2"; shift 2
HERE="$(cd "$(dirname "$0")" && pwd)"
T=$(date -j -f '%Y-%m-%d %H:%M:%S' "$START" +%s)
while [ "$(date +%s)" -lt "$T" ]; do sleep 60; done
if [ -n "${WAIT_PID:-}" ]; then while kill -0 "$WAIT_PID" 2>/dev/null; do sleep 30; done; fi
for spec in "$@"; do
  # NO_START_AFTER="<YYYY-mm-dd HH:MM:SS>": start no new run after that time (e.g. before a human-gated run).
  if [ -n "${NO_START_AFTER:-}" ] && [ "$(date +%s)" -ge "$(date -j -f '%Y-%m-%d %H:%M:%S' "$NO_START_AFTER" +%s)" ]; then
    echo "stop: not starting $spec after $NO_START_AFTER" >> "$LOG"; break
  fi
  if [ -n "${STOP_FILE:-}" ] && [ -e "$STOP_FILE" ]; then
    echo "stop: $STOP_FILE exists, not starting $spec $(date '+%Y-%m-%d %H:%M:%S')" >> "$LOG"; break
  fi
  if [ -n "${GUARD_CMD:-}" ] && ! bash -c "$GUARD_CMD" >> "$LOG" 2>&1; then
    echo "stop: guard failed, not starting $spec $(date '+%Y-%m-%d %H:%M:%S')" >> "$LOG"; break
  fi
  IFS=: read -r cond tag model name version <<< "$spec"
  if [ -n "${SKIP_EXISTING:-}" ] && [ -e "$HERE/../../runs/batch/thm01-R-$tag-$cond" ]; then
    echo "skip: thm01-R-$tag-$cond exists" >> "$LOG"; continue
  fi
  extra=()
  [ -n "${model:-}" ] && extra+=(--model "$model" --model-name "$name")
  case "${model:-}" in gemini*) extra+=(--harness agy);; gpt*) extra+=(--harness copilot);; esac
  # CLAUDE_VERSION=2.1.293 in the environment selects that Claude Code version (claude harness only).
  case "${model:-}" in gemini*|gpt*) ;; *) v="${version:-${CLAUDE_VERSION:-}}"; [ -n "$v" ] && extra+=(--claude-version "$v");; esac
  echo "start $cond $tag $(date '+%Y-%m-%d %H:%M:%S')" >> "$LOG"
  out=$(cd "$HERE/.." && python3 scripts/batch_run.py "$cond" "$tag" ${extra[@]+"${extra[@]}"} 2>&1)
  echo "$out" >> "$LOG"
  echo "end $cond $tag $(date '+%Y-%m-%d %H:%M:%S')" >> "$LOG"
  # "stopped" = the Worker ended without the completion file (e.g. agy denial of a
  # glob command): go on with the next run. Anything else (aborted: API error such
  # as a usage limit, or a crash) stops the series.
  echo "$out" | grep -qE '"status": "(completed|stopped)"' || { echo "stop: $tag did not complete" >> "$LOG"; break; }
done
