#!/usr/bin/env bash
# manager_home.sh — Give one A / F− run its own Manager directory and its own
# Antigravity HOME, so the Manager sees no other run (memos, conversations,
# conversation summaries, brain/knowledge).
#
# Usage:
#   scripts/manager_home.sh <RUN>        e.g. thm01-R-sonnet46-A
# Creates (both must not exist):
#   <home>/notebook/git/thm01-R-managers/<RUN>/        Manager directory (manager.sh init)
#   <home>/notebook/git/thm01-R-agy-home/manager-<RUN>/ HOME for agy: only the login token
#       from the author's base login and a copy of the author's agy settings.json
#       (the same Manager settings as in luna-A / luna-F; model Gemini 3.1 Pro (Low)).
# Then prints the command that starts the Manager.
set -euo pipefail
[ $# -eq 1 ] || { sed -n '2,14p' "$0"; exit 1; }
RUN="$1"
HERE="$(cd "$(dirname "$0")" && pwd)"
MGR="$HOME/notebook/git/thm01-R-managers/$RUN"
H="$HOME/notebook/git/thm01-R-agy-home/manager-$RUN"
[ -e "$MGR" ] && { echo "ERROR: $MGR exists" >&2; exit 1; }
[ -e "$H" ] && { echo "ERROR: $H exists" >&2; exit 1; }
mkdir -p "$(dirname "$MGR")"
"$HERE/manager.sh" init "$MGR"
mkdir -p "$H/.gemini/antigravity-cli"
cp "$HOME/notebook/git/thm01-R-agy-home/base/.gemini/antigravity-cli/antigravity-oauth-token" "$H/.gemini/antigravity-cli/"
cp "$HOME/.gemini/antigravity-cli/settings.json" "$H/.gemini/antigravity-cli/settings.json"
echo
echo "Manager directory: $MGR"
echo "Manager HOME:      $H"
echo "Start the Manager (one new session per issue) with:"
echo "  cd $MGR && HOME=$H GIT_CONFIG_GLOBAL=$HOME/.gitconfig agy"
echo "Use $MGR as <MANAGER_DIR> for scripts/manager.sh."
