#!/bin/bash
# usage: r2f_review.sh N REPLYFILE OUTNAME [STOP]
set -euo pipefail
REV=<home>/notebook/git/ai-workflow-evaluation/case_studies/osp-schema-extension/t1-schema-extension/revision-ipsj-r1
RD=$REV/runs/thm01-R-gemini38f-r2-F
cd $REV
experiment/scripts/manager.sh review <home>/notebook/git/thm01-R-managers/thm01-R-gemini38f-r2-F <home>/notebook/git/thm01-R/thm01-R-gemini38f-r2-F "$1" ${4:+"$4"} | sed -n '/^----- BEGIN TEXT/,/^----- END TEXT/p' | sed '1d;$d' > $RD/.tpl
python3 - $RD/.tpl "$2" "$RD/reviews/$3" <<'PY'
import sys
t=open(sys.argv[1]).read(); r=open(sys.argv[2]).read().rstrip('\n')
k="<<< paste the Worker's latest reply here >>>"; assert t.count(k)==1
open(sys.argv[3],'w').write(t.replace(k,r))
PY
rm $RD/.tpl; shasum -a 256 "$RD/reviews/$3"; tail -1 experiment/manifests/thm01-R-gemini38f-r2-F.deliveries.txt; head -c 200 "$RD/reviews/$3"; echo
