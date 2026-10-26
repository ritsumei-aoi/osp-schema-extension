#!/usr/bin/env bash
# manager.sh — Prepare and start Manager AI sessions (condition A and F− runs).
#
# Usage:
#   scripts/manager.sh init  <MANAGER_DIR>
#       Create the Manager directory (must not exist): MANAGER_BRIEF.md,
#       reference/ (what the Worker receives in A / F−), memos/.
#       Nothing about the study design, other runs, or judgments is copied.
#   scripts/manager.sh update-brief <MANAGER_DIR>
#       Copy the current kit MANAGER_BRIEF.md into MANAGER_DIR (logged).
#   scripts/manager.sh run   <MANAGER_DIR> <WORKSPACE_DIR> <A|F>
#       Create memos/<run>/manager_memo.md for one run.
#   scripts/manager.sh review <MANAGER_DIR> <WORKSPACE_DIR> <N> ["<stop>"]
#       Print the fixed review request for issue N (condition F: step N; the
#       human pastes the Worker reply into the marked place). The Manager memo number
#       is the next one after those already in the memo. <stop> defaults to
#       "stopped for approval".
#   scripts/manager.sh close <MANAGER_DIR> <WORKSPACE_DIR> <N>
#       Print the fixed issue-closed message for issue N, with the Worker's
#       commits for that issue taken from git.
#   scripts/manager.sh start <MANAGER_DIR> <WORKSPACE_DIR> <N>
#       Copy the filled-in Manager session-start prompt for issue N to the
#       clipboard (start a NEW Manager session per issue).
#
# Keep MANAGER_DIR outside the evaluation repository and outside the
# directory that holds the Worker workspaces, e.g. <home>/notebook/git/thm01-R-manager.

set -euo pipefail
if [ $# -lt 2 ]; then sed -n '2,27p' "$0"; exit 1; fi
CMD="$1"; MGR="$2"
HERE="$(cd "$(dirname "$0")/.." && pwd)"
KIT="$HERE/kit"
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


case "$CMD" in
  init)
    [ -e "$MGR" ] && { echo "ERROR: $MGR already exists" >&2; exit 1; }
    mkdir -p "$MGR/reference/docs/math" "$MGR/reference/issues" "$MGR/reference/handover" \
             "$MGR/reference/prompts/A_start" "$MGR/reference/prompts/F_messages" "$MGR/memos"
    cp "$HERE/manager_kit/MANAGER_BRIEF.md" "$MGR/"
    for f in Cn1_definition.md C_inhomogeneous_definition.md C_coboundary_definition.md; do
      cp "$KIT/math_core/$f" "$MGR/reference/docs/math/$f"; done
    for f in B0n_definition.md B0n_schema_v5.md README.md; do
      cp "$KIT/workflow_docs/$f" "$MGR/reference/docs/math/$f"; done
    for f in "$KIT"/issues_A/I0*_issue_open.md; do cp "$f" "$MGR/reference/issues/"; done
    for f in README.md workflow.md ai_trust_policy.md notation.md; do
      cp "$KIT/handover/$f" "$MGR/reference/handover/$f"; done
    for f in "$HERE"/prompts/A_start/I0*.txt; do cp "$f" "$MGR/reference/prompts/A_start/"; done
    for f in "$HERE"/prompts/F_messages/step*.md; do cp "$f" "$MGR/reference/prompts/F_messages/"; done
    cp "$HERE/prompts/F_opening.txt" "$HERE/prompts/F_final_reflection.txt" "$MGR/reference/prompts/"
    MAN="${MANIFEST_DIR:-$HERE/manifests}/manager_reference.txt"
    {
      echo "# manager dir: $MGR"
      echo "# built: $(now)"
      echo "# kit commit: $(git -C "$HERE" rev-parse --short HEAD 2>/dev/null || echo unknown)"
      (cd "$MGR" && find . -type f | sort | xargs shasum -a 256)
    } > "$MAN"
    echo "Built $MGR"; echo "Manifest: $MAN"
    ;;
  update-brief)
    cp "$HERE/manager_kit/MANAGER_BRIEF.md" "$MGR/MANAGER_BRIEF.md"
    echo "# $(now) updated MANAGER_BRIEF.md: $(shasum -a 256 "$MGR/MANAGER_BRIEF.md" | awk '{print $1}') (kit commit $(git -C "$HERE" rev-parse --short HEAD))" >> "${MANIFEST_DIR:-$HERE/manifests}/manager_reference.txt"
    echo "Updated $MGR/MANAGER_BRIEF.md (start a new Manager session to use it)"
    ;;
  run)
    WS="$(cd "$3" && pwd)"; COND="$4"; RUN="$(basename "$WS")"
    case "$COND" in A|F) ;; *) echo "ERROR: condition must be A or F" >&2; exit 1;; esac
    MODEL="$(sed -n 's/^# model: //p' "${MANIFEST_DIR:-$HERE/manifests}/${RUN}.txt")"
    D="$MGR/memos/$RUN"; [ -e "$D/manager_memo.md" ] && { echo "ERROR: memo exists: $D/manager_memo.md" >&2; exit 1; }
    mkdir -p "$D"
    cat > "$D/manager_memo.md" <<EOF
# Manager memo: $RUN

- Run ID: $RUN
- Condition: $COND
- Worker model: $MODEL
- Worker workspace: $WS
- Created: $(now)

(Manager memos and Human memos are appended below, in order.)
EOF
    echo "Created $D/manager_memo.md"
    ;;
  review)
    WS="$(cd "$3" && pwd)"; N="$4"; STOP="${5:-stopped for approval}"; RUN="$(basename "$WS")"
    MEMO="$MGR/memos/$RUN/manager_memo.md"
    [ -f "$MEMO" ] || { echo "ERROR: run memo not found" >&2; exit 1; }
    # Highest Manager memo number mentioned anywhere (headers or references in Human memos)
    LAST=$({ grep -o 'Manager memo [0-9][0-9]*' "$MEMO" || true; } | awk '{print $3}' | sort -n | tail -1)
    MM=$(printf '%02d' $(( 10#${LAST:-0} + 1 )))
    COND="$(sed -n 's/^- Condition: //p' "$MEMO")"
    TPL="$HERE/manager_kit/review_request.txt"; if [ "$COND" = F ]; then TPL="$HERE/manager_kit/review_request_F.txt"; fi
    sed -e "s#{RUN}#$RUN#g" -e "s#{N}#$N#g" -e "s#{MM}#$MM#g" -e "s#{STOP}#$STOP#g" "$TPL" | emit
    echo "$(now)  MANAGER  I0${N}-review-request  memo=${MM}" >> "${MANIFEST_DIR:-$HERE/manifests}/${RUN}.deliveries.txt"
    echo "Printed the review request (next Manager memo: ${MM}). Paste it into the CURRENT Manager session."
    ;;
  close)
    WS="$(cd "$3" && pwd)"; N="$4"; RUN="$(basename "$WS")"
    if [ "$(sed -n 's/^- Condition: //p' "$MGR/memos/$RUN/manager_memo.md")" = F ]; then
      sed -e "s#{RUN}#$RUN#g" -e "s#{N}#$N#g" "$HERE/manager_kit/issue_closed_F.txt" | emit
      echo "$(now)  MANAGER  step${N}-closed" >> "${MANIFEST_DIR:-$HERE/manifests}/${RUN}.deliveries.txt"
      echo "Printed the step-closed message. Paste it into the CURRENT Manager session; end the session after \"Done\"."
      exit 0
    fi
    COMMITS=$(git -C "$WS" log --format='%h %s' | awk -v n="I0$N" '$0 ~ ("^[0-9a-f]+ " n "-1:") || $0 ~ ("AI-CLAIM\\] Issue " n " ") {print $1}' | tac 2>/dev/null || true)
    [ -n "$COMMITS" ] || COMMITS=$(git -C "$WS" log --format='%h %s' | awk -v n="I0$N" '$0 ~ ("^[0-9a-f]+ " n "-1:") || $0 ~ ("AI-CLAIM\\] Issue " n " ") {print $1}' | tail -r)
    [ -n "$COMMITS" ] || { echo "ERROR: no commits for I0$N found; has the Worker run close_issue.sh?" >&2; exit 1; }
    LIST=$(echo "$COMMITS" | paste -sd' ' - | sed 's/ / and /g')
    sed -e "s#{RUN}#$RUN#g" -e "s#{N}#$N#g" -e "s#{COMMITS}#$LIST#g" \
      "$HERE/manager_kit/issue_closed.txt" | emit
    echo "$(now)  MANAGER  I0${N}-closed  ${LIST}" >> "${MANIFEST_DIR:-$HERE/manifests}/${RUN}.deliveries.txt"
    echo "Printed the issue-closed message. Paste it into the CURRENT Manager session; end the session after \"Done\"."
    ;;
  start)
    WS="$(cd "$3" && pwd)"; N="$4"; RUN="$(basename "$WS")"
    MEMO="$MGR/memos/$RUN/manager_memo.md"
    [ -f "$MEMO" ] || { echo "ERROR: run memo not found; run 'manager.sh run' first" >&2; exit 1; }
    COND="$(sed -n 's/^- Condition: //p' "$MEMO")"
    sed -e "s#{RUN}#$RUN#g" -e "s#{COND}#$COND#g" -e "s#{WS}#$WS#g" -e "s#{N}#$N#g" \
      "$HERE/manager_kit/manager_session_start.txt" | emit
    echo "$(now)  MANAGER  I0${N}-session-start  (clipboard)" >> "${MANIFEST_DIR:-$HERE/manifests}/${RUN}.deliveries.txt"
    echo "Printed the Manager session-start prompt for I0${N} above (also copied to the Mac clipboard)."
    echo "Start a NEW Manager session (Antigravity CLI) in $MGR and paste it."
    ;;
  *) echo "ERROR: unknown command $CMD" >&2; exit 1;;
esac
