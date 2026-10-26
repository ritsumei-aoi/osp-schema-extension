#!/bin/bash
# usage: r2f_hm.sh N(step) HMNUM MMNUM DRAFTFILE "STOP" KIND
set -euo pipefail
N=$1; HM=$2; MM=$3; DR=$4; STOP=$5; KIND=$6
M=<home>/notebook/git/thm01-R-managers/thm01-R-gemini38f-r2-F; RD=<home>/notebook/git/ai-workflow-evaluation/case_studies/osp-schema-extension/t1-schema-extension/revision-ipsj-r1/runs/thm01-R-gemini38f-r2-F
F=$M/memos/thm01-R-gemini38f-r2-F/manager_memo.md
python3 <home>/notebook/git/thm01-R-judging-work/2026-10-10/scratchpad_6e76e7ab/hm.py $F "$DR" "$HM" "$STOP" "$KIND" "$MM"
if git -C $M diff | grep '^-' | grep -v '^---' | grep -q .; then echo STOP removed; exit 1; fi
git -C $M -c user.name=scribe -c user.email=scribe@localhost commit -qam "Human memo $HM (step $N)"; H=$(git -C $M log --format=%h -1)
herdr pane send-text w2:p14 "$(cat $DR)"; T=$(date -u +%H:%M:%S); sha=$(shasum -a 256 $DR | cut -c1-8)
echo "$H $T $sha"
cd $RD; python3 - "$H" "$T" "$sha" "$DR" "$HM" "$N" <<'PY'
import sys,os
H,T,sha,DR,HM,N=sys.argv[1:]
p='run_log.md'; s=open(p).read()
lines=s.split('\n')
# insert relay row after last table row
idx=max(i for i,l in enumerate(lines) if l.startswith('| ') and l.count('|')>=7)
lines.insert(idx+1,f"| {T} | Worker p14 | pending/{os.path.basename(DR)} (Human memo {HM}) | {sha} | 著者 | |")
s='\n'.join(lines)
anchor='\n\n## 中継の記録'
s=s.replace(anchor,f"\n- step {N}: 著者の選択 1 (k)。Human memo {HM} を追記 (Manager git {H}、追加のみ) してから Worker に入力 ({T}Z)。\n\n## 中継の記録",1)
open(p,'w').write(s)
PY
