# print Worker tool calls after last USER_INPUT, flag outside-workspace refs
import json,glob,os,re,sys
B=glob.glob(os.path.expanduser('<home>/notebook/git/thm01-R-agy-home/worker-thm01-R-gemini38f-r3-A1/.gemini/antigravity-cli/brain/*/.system_generated/logs/transcript_full.jsonl'))[0]
L=[json.loads(l) for l in open(B)]
start=int(sys.argv[1]) if len(sys.argv)>1 else max(i for i,d in enumerate(L) if d['type']=='USER_INPUT')
WS='<home>/notebook/git/thm01-R/thm01-R-gemini38f-r3-A1'
for i,d in enumerate(L[start:],start):
    for t in (d.get('tool_calls') or []):
        a=t.get('args',{}); s=str(a.get('CommandLine') or a.get('AbsolutePath') or a.get('TargetFile') or '')
        flag=''
        if '..' in s or re.search(r'<home>/(?!notebook/git/thm01-R/thm01-R-gemini38f-r3-A1)',s): flag=' <<< OUTSIDE?'
        print(i,t['name'],s[:150].replace('\n',' '),flag)
print('steps',len(L))
