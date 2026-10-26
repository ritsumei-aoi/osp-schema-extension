import json,glob,os,re
B=glob.glob(os.path.expanduser('<home>/notebook/git/thm01-R-agy-home/worker-thm01-R-gemini38f-r3-A1/.gemini/antigravity-cli/brain/*/.system_generated/logs/transcript_full.jsonl'))[0]
L=[json.loads(l) for l in open(B)]
lu=max(i for i,d in enumerate(L) if d['type']=='USER_INPUT')
n=0
for i,d in enumerate(L[lu:],lu):
    for t in (d.get('tool_calls') or []):
        n+=1; s=json.dumps(t.get('args',{}))
        hits=set(re.findall(r'(\.\./[\w./-]*|thm01-R-(?!gemini38f-r3-A1|agy-home)[\w-]+|<home>/notebook/git/(?!thm01-R/thm01-R-gemini38f-r3-A1|thm01-R-agy-home/worker-thm01-R-gemini38f-r3-A1)[\w/.-]*)',s))
        if hits: print('*** OUTSIDE?',i,t['name'],hits)
print('tool calls since step',lu,':',n)
