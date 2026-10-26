#!/usr/bin/env bash
# deliver_issue.sh — Deliver the next task to a running A or F− workspace.
#
# Usage:
#   scripts/deliver_issue.sh A <WORKSPACE_DIR> <N>     # N = 1..9
#   scripts/deliver_issue.sh F <WORKSPACE_DIR> <N>     # N = open, 1..8, or "final"
#
# A: places kit/issues_A/I0N_issue_open.md as docs/issues/issue_open.md,
#    filling {Model Name} and the branch name. It refuses to overwrite an
#    issue that is still open (i.e. issue_open.md is not the reset template),
#    and for N >= 2 it requires the previous issue to be archived in
#    docs/issues/done/. Nothing is committed: close_issue.sh archives and
#    commits the issue when the Worker finishes it. The issue's fixed start
#    prompt (prompts/A_start/I0N.txt) is then copied to the clipboard.
#    Use N=1 only to copy the I01 start prompt (I01 is placed at build time).
# F: copies prompts/F_messages/stepN.md (or F_final_reflection.txt) to the
#    terminal (and clipboard), so that it can be pasted into the chat unchanged.
#
# Every delivery is appended, with its sha256 and UTC time, to
# manifests/<run>.deliveries.txt (outside the workspace).

set -euo pipefail

if [ $# -lt 3 ]; then sed -n '2,18p' "$0"; exit 1; fi
COND="$1"; WS="$(cd "$2" && pwd)"; N="$3"
HERE="$(cd "$(dirname "$0")/.." && pwd)"
RUN="$(basename "$WS")"
MANIFEST="${MANIFEST_DIR:-$HERE/manifests}/${RUN}.txt"
LOG="${MANIFEST_DIR:-$HERE/manifests}/${RUN}.deliveries.txt"

[ -f "$MANIFEST" ] || { echo "ERROR: manifest not found: $MANIFEST" >&2; exit 1; }
MODEL="$(sed -n 's/^# model: //p' "$MANIFEST")"
now() { date -u +%Y-%m-%dT%H:%M:%SZ; }
# emit: show the text to paste. It is always printed between markers (so it can
# be copied from any terminal, including remote ones). It is also put on the
# local macOS clipboard with pbcopy when available, and, if OSC52=1, sent to the
# terminal client's clipboard with an OSC 52 escape sequence.
emit() {
  local text; text="$(cat)"
  echo "----- BEGIN TEXT TO PASTE -----"
  printf '%s\n' "$text"
  echo "----- END TEXT TO PASTE -----"
  if command -v pbcopy >/dev/null 2>&1; then printf '%s\n' "$text" | pbcopy 2>/dev/null || true; fi
  if [ "${OSC52:-0}" = 1 ]; then printf '\033]52;c;%s\a' "$(printf '%s\n' "$text" | base64 | tr -d '\n')"; fi
}


case "$COND" in
  A)
    case "$N" in [1-9]) ;; *) echo "ERROR: N must be 1..9 for A" >&2; exit 1;; esac
    PROMPT="$HERE/prompts/A_start/I0${N}.txt"
    if [ "$N" = 1 ]; then
      emit < "$PROMPT"
      echo "$(now)  A  I01-start-prompt  $(shasum -a 256 "$PROMPT" | awk '{print $1}')  (clipboard)" >> "$LOG"
      echo "I01 was placed at build time. Printed prompts/A_start/I01.txt above (also copied to the Mac clipboard)."
      echo "Logged: $LOG"; exit 0
    fi
    SRC="$HERE/kit/issues_A/I0${N}_issue_open.md"
    DEST="$WS/docs/issues/issue_open.md"
    BRANCH="$(git -C "$WS" branch --show-current)"
    # The current issue_open.md must be the reset template, not an open issue.
    if [ -f "$DEST" ] && grep -q '^\*\*Status\*\*: open' "$DEST"; then
      echo "ERROR: $DEST still holds an open issue. Has the Worker run close_issue.sh?" >&2
      exit 1
    fi
    if [ "$N" -ge 2 ]; then
      PREV=$(printf '%02d' $((N - 1)))
      if ! ls "$WS/docs/issues/done/"issue_*_"${PREV}".md >/dev/null 2>&1; then
        echo "ERROR: issue I${PREV} is not archived in docs/issues/done/ yet." >&2
        exit 1
      fi
    fi
    sed -e "s/{Model Name}/${MODEL}/g" -e "s#study/thm{XX}-{YY}#${BRANCH}#g" "$SRC" > "$DEST"
    SHA="$(shasum -a 256 "$DEST" | awk '{print $1}')"
    echo "$(now)  A  I0${N}  ${SHA}  docs/issues/issue_open.md" >> "$LOG"
    emit < "$PROMPT"
    echo "$(now)  A  I0${N}-start-prompt  $(shasum -a 256 "$PROMPT" | awk '{print $1}')  (clipboard)" >> "$LOG"
    echo "Delivered I0${N} to $DEST"
    echo "Printed prompts/A_start/I0${N}.txt above (also copied to the Mac clipboard). Start a new Worker session and paste it unchanged."
    ;;
  F)
    if [ "$N" = "final" ]; then SRC="$HERE/prompts/F_final_reflection.txt"; TAG="final"
    elif [ "$N" = "open" ]; then SRC="$HERE/prompts/F_opening.txt"; TAG="opening"
    else
      case "$N" in [1-8]) ;; *) echo "ERROR: N must be 1..8 or final for F" >&2; exit 1;; esac
      SRC="$HERE/prompts/F_messages/step${N}.md"; TAG="step${N}"
    fi
    emit < "$SRC"
    SHA="$(shasum -a 256 "$SRC" | awk '{print $1}')"
    echo "$(now)  F  ${TAG}  ${SHA}  (clipboard)" >> "$LOG"
    echo "Printed ${TAG} above (also copied to the Mac clipboard). Paste it into the Worker chat unchanged."
    ;;
  *) echo "ERROR: COND must be A or F" >&2; exit 1;;
esac
echo "Logged: $LOG"
