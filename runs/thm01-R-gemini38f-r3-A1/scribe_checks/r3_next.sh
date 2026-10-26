#!/bin/bash
# usage: r2f_next.sh PREV NEXT  (after Manager "Done" for step PREV)
set -uo pipefail
P=$1; N=$2
REV=<home>/notebook/git/ai-workflow-evaluation/case_studies/osp-schema-extension/t1-schema-extension/revision-ipsj-r1
RD=$REV/runs/thm01-R-gemini38f-r3-A1; WS=<home>/notebook/git/thm01-R/thm01-R-gemini38f-r3-A1; M=<home>/notebook/git/thm01-R-managers/thm01-R-gemini38f-r3-A1
S=/private/tmp/claude-501/-<home>-notebook-git-ai-workflow-evaluation/d74c40ef-b90f-41a3-a34d-48a5f62af0d8/scratchpad
if git -C $M diff | grep '^-' | grep -v '^---' | grep -q .; then echo "STOP: memo has removed lines"; exit 1; fi
git -C $M -c user.name=scribe -c user.email=scribe@localhost commit -qam "Carry-over after I0$P" && git -C $M log --oneline -1
python3 $S/r3_hist.py manager $RD/relay/M_I0${P}_close.txt 2>/dev/null
$REV/experiment/scripts/quota.sh $RD/quota_log.tsv 2>/dev/null | grep -E "agy\s+Gemini (Models|4 Argon)"
herdr pane send-text w2:p13 "/exit"; herdr pane send-keys w2:p13 Enter; echo "exit $(date -u +%H:%M:%S)"
sleep 5
if ! herdr pane read w2:p13 | tail -2 | grep -q "thm01-R-gemini38f-r3-A1 %"; then echo "STOP: no shell prompt"; herdr pane read w2:p13 | tail -6; exit 1; fi
herdr pane read w2:p13 | grep -o "agy --conversation=[0-9a-f-]*" | tail -1
herdr pane send-text w2:p13 "$(cat $RD/relay/M_launch.txt)"; herdr pane send-keys w2:p13 Enter; echo "launch $(date -u +%H:%M:%S)"
sleep 9
if ! herdr pane read w2:p13 | tail -3 | grep -q "Gemini 4 Argon · low"; then echo "STOP: input screen not seen"; herdr pane read w2:p13 | tail -10; exit 1; fi
L=$(ls -t <home>/notebook/git/thm01-R-agy-home/manager-thm01-R-gemini38f-r3-A1/.gemini/antigravity-cli/log/cli-*.log | head -1)
grep -o "Language server version: .*" $L; grep -ci alias $L
herdr pane read w2:p13 | tail -10 | grep -E "┃" | head -3
cd $REV
experiment/scripts/manager.sh start $M $WS $N | sed -n '/^----- BEGIN TEXT/,/^----- END TEXT/p' | sed '1d;$d' > $RD/relay/M_I0${N}_start.txt
experiment/scripts/deliver_issue.sh A $WS $N | sed -n "/^----- BEGIN TEXT/,/^----- END TEXT/p" | sed "1d;\$d" > $RD/relay/W_I0${N}_start.txt; tail -3 $REV/experiment/manifests/thm01-R-gemini38f-r3-A1.deliveries.txt; git -C $WS status --short
perl -pi -e "chomp if eof" $RD/relay/M_I0${N}_start.txt; cmp -s $RD/relay/W_I0${N}_start.txt $REV/runs/thm01-R-gemini38f-r2-A1/relay/W_I0${N}_start.txt && echo "W same as r2-A1" || echo "W DIFFERS from r2-A1"
diff $RD/relay/M_I01_start.txt $RD/relay/M_I0${N}_start.txt | grep '^[<>]' | grep -v Reply
shasum -a 256 $RD/relay/M_I0${N}_start.txt $RD/relay/W_I0${N}_start.txt | cut -c1-8
herdr pane send-text w2:p13 "$(cat $RD/relay/M_I0${N}_start.txt)"; herdr pane send-text w2:p14 "$(cat $RD/relay/W_I0${N}_start.txt)"; echo "typed $(date -u +%H:%M:%S)"
