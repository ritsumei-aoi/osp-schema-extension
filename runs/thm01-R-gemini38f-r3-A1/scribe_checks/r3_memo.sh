#!/bin/bash
# r3_memo.sh MM : after Manager wrote memo MM: show diff, tools, commit, extract draft to pending/W_draft_MM.txt
set -uo pipefail
MM=$1; RUN=thm01-R-gemini38f-r3-A1
M=<home>/notebook/git/thm01-R-managers/$RUN; RD=<home>/notebook/git/ai-workflow-evaluation/case_studies/osp-schema-extension/t1-schema-extension/revision-ipsj-r1/runs/$RUN
git -C $M diff | grep '^-' | grep -v '^---'; echo "--removed above"
git -C $M diff | grep '^+' | grep -v '^+++' | sed 's/^+//'
python3 - <<'PY'
import json,glob,os
fs=sorted(glob.glob(os.path.expanduser('<home>/notebook/git/thm01-R-agy-home/manager-thm01-R-gemini38f-r3-A1/.gemini/antigravity-cli/brain/*/.system_generated/logs/transcript_full.jsonl')),key=os.path.getmtime)
L=[json.loads(l) for l in open(fs[-1])]
lu=max(i for i,d in enumerate(L) if d['type']=='USER_INPUT')
for d in L[lu+1:]:
    for t in (d.get('tool_calls') or []):
        a=t.get('args',{}); print('TOOL',t['name'], str(a.get('CommandLine') or a.get('AbsolutePath') or a.get('TargetFile') or '')[:200])
PY
git -C $M -c user.name=scribe -c user.email=scribe@localhost commit -qam "Manager memo $MM"; echo "GIT $(git -C $M log --format=%h -1)"
python3 - $M/memos/$RUN/manager_memo.md $RD/pending/W_draft_$MM.txt $MM <<'PY'
import sys,re
s=open(sys.argv[1]).read()
blk=s.split('## Manager memo '+sys.argv[3])[1]
d=re.search(r'```text\n(.*?)\n```',blk,re.S).group(1)
lines=d.split('\n'); print('TYPE LINE:',lines[0]); assert lines[0].startswith('TYPE:')
open(sys.argv[2],'w').write('\n'.join(lines[1:]).strip('\n')+'\n')
PY
echo "SHA $(shasum -a 256 $RD/pending/W_draft_$MM.txt | cut -c1-8)"
git -C <home>/notebook/git/thm01-R/$RUN status --short
