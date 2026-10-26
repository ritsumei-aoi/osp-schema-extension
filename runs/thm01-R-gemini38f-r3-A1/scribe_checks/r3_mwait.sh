#!/bin/bash
# wait for Manager memo written and pane idle
M=<home>/notebook/git/thm01-R-managers/thm01-R-gemini38f-r3-A1; n=0
until { ! git -C $M diff --quiet && herdr pane read w2:p13 | tail -3 | grep -q "? for shortcuts"; } || [ $n -gt 57 ]; do sleep 10; n=$((n+1)); done; date -u +%H:%M:%S
