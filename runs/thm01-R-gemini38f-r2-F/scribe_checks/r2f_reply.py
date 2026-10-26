# usage: r2f_reply.py OUT  -> writes Worker's latest reply (last PLANNER_RESPONSE content after last USER_INPUT)
import json,sys,glob,os
B=glob.glob(os.path.expanduser('<home>/notebook/git/thm01-R-agy-home/worker-thm01-R-gemini38f-r2-F/.gemini/antigravity-cli/brain/*/.system_generated/logs/transcript_full.jsonl'))
assert len(B)==1,B
L=[json.loads(l) for l in open(B[0])]
lu=max(i for i,d in enumerate(L) if d['type']=='USER_INPUT')
print('last user step',lu,L[lu]['created_at'])
rs=[(i,d) for i,d in enumerate(L[lu+1:],lu+1) if d['type']=='PLANNER_RESPONSE' and d.get('content')]
tools=[d.get('tool_calls') for d in L[lu+1:] if d['type']=='PLANNER_RESPONSE' and d.get('tool_calls')]
for i,d in rs: print(' content at',i,d['created_at'],len(d['content']),d.get('truncated_fields'))
for t in tools: print('  tool:',str(t)[:160])
i,d=rs[-1]
open(sys.argv[1],'w').write(d['content'].rstrip('\n')+'\n')
