#!/bin/bash
# r3_close.sh N DRAFTFILE : verify draft history, mark draft row, manager close N, type, log row
set -euo pipefail
N=$1; DR=$2
REV=<home>/notebook/git/ai-workflow-evaluation/case_studies/osp-schema-extension/t1-schema-extension/revision-ipsj-r1; RUN=thm01-R-gemini38f-r3-A1
RD=$REV/runs/$RUN; WS=<home>/notebook/git/thm01-R/$RUN; MG=<home>/notebook/git/thm01-R-managers/$RUN
S=/private/tmp/claude-501/-<home>-notebook-git-ai-workflow-evaluation/d74c40ef-b90f-41a3-a34d-48a5f62af0d8/scratchpad
H=$(python3 $S/r3_hist.py worker $DR 2>/dev/null); echo "$H"
cd $REV; experiment/scripts/manager.sh close $MG $WS $N | sed -n '/^----- BEGIN TEXT/,/^----- END TEXT/p' | sed '1d;$d' > $RD/relay/M_I0${N}_close.txt
perl -pi -e 'chomp if eof' $RD/relay/M_I0${N}_close.txt
herdr pane send-text w2:p13 "$(cat $RD/relay/M_I0${N}_close.txt)"; T=$(date -u +%H:%M:%S); sha=$(shasum -a 256 $RD/relay/M_I0${N}_close.txt | cut -c1-8)
echo "| $T | Manager p13 | M_I0${N}_close.txt | $sha | 著者 | |" >> $RD/run_log.md
echo "$T $sha"; cat $RD/relay/M_I0${N}_close.txt; echo
