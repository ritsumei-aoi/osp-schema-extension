#!/bin/bash
# r3_review.sh N [STOP] [SUFFIX]: save issue diff, make review request, type into Manager, log row
set -euo pipefail
N=$1; STOP=${2:-}; SUF=${3:-}
REV=<home>/notebook/git/ai-workflow-evaluation/case_studies/osp-schema-extension/t1-schema-extension/revision-ipsj-r1; RUN=thm01-R-gemini38f-r3-A1
RD=$REV/runs/$RUN; WS=<home>/notebook/git/thm01-R/$RUN; MG=<home>/notebook/git/thm01-R-managers/$RUN
git -C $WS diff > $RD/pending/I0${N}_issue_open_diff${SUF}.txt
cd $REV
if [ -n "$STOP" ]; then experiment/scripts/manager.sh review $MG $WS $N "$STOP"; else experiment/scripts/manager.sh review $MG $WS $N; fi | sed -n '/^----- BEGIN TEXT/,/^----- END TEXT/p' | sed '1d;$d' > $RD/relay/M_I0${N}_review${SUF}.txt
perl -pi -e 'chomp if eof' $RD/relay/M_I0${N}_review${SUF}.txt
herdr pane send-text w2:p13 "$(cat $RD/relay/M_I0${N}_review${SUF}.txt)"; T=$(date -u +%H:%M:%S); sha=$(shasum -a 256 $RD/relay/M_I0${N}_review${SUF}.txt | cut -c1-8)
echo "| $T | Manager p13 | M_I0${N}_review${SUF}.txt | $sha | 著者 | |" >> $RD/run_log.md
echo "$T $sha"; cat $RD/relay/M_I0${N}_review${SUF}.txt; echo
