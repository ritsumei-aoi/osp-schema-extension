#!/usr/bin/env bash
# shadow.sh — Record snapshots of a condition-F workspace without putting Git
# inside it. The repository lives outside the workspace, so the Worker cannot
# see it.
#
# Usage:
#   scripts/shadow.sh init <WORKSPACE_DIR>
#   scripts/shadow.sh snap <WORKSPACE_DIR> "<message>"
#   scripts/shadow.sh status <WORKSPACE_DIR>
# Shadow repositories: <home>/notebook/git/thm01-R-shadow/<run>.git
set -euo pipefail
CMD="$1"; WS="$(cd "$2" && pwd)"; RUN="$(basename "$WS")"
G="$HOME/notebook/git/thm01-R-shadow/$RUN.git"
g() { git --git-dir="$G" --work-tree="$WS" "$@"; }
case "$CMD" in
  init) mkdir -p "$(dirname "$G")"; git init -q --bare "$G"; git --git-dir="$G" config core.bare false
        g add -A; g -c user.name=scribe -c user.email=scribe@local commit -q -m "init: distributed files"; echo "Shadow repo: $G";;
  snap) g add -A; g -c user.name=scribe -c user.email=scribe@local commit -q -m "${3:-snapshot}" || echo "(no changes)"; g log --oneline -1;;
  status) g status --short;;
  *) echo "unknown command" >&2; exit 1;;
esac
