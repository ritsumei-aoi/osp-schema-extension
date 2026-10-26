#!/bin/bash
# r3_wait.sh : wait until Worker pane idle (or dialog), then show tail, workspace status, histories
n=0; until { [ $n -gt 3 ] && herdr pane read w2:p14 | tail -3 | grep -q "? for shortcuts" && ! herdr pane read w2:p14 | tail -3 | grep -q "task(s)"; } || [ $n -gt 57 ]; do sleep 10; n=$((n+1)); herdr pane read w2:p14 | tail -16 | grep -qE "Run this command|Enter to select|↑/↓ Navigate" && { echo "*** DIALOG"; break; }; done
date -u +%H:%M:%S; herdr pane read w2:p14 | tail -${1:-14}
WS=<home>/notebook/git/thm01-R/thm01-R-gemini38f-r3-A1; echo "--- ws"; git -C $WS status --short; git -C $WS diff --stat | tail -1; git -C $WS log --oneline | head -3
