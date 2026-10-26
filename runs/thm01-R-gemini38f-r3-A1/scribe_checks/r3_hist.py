# usage: r2f_hist.py worker|manager FILE [offset_from_end] -> compare history entry with file
import json,sys,os,datetime
who,f=sys.argv[1:3]; k=int(sys.argv[3]) if len(sys.argv)>3 else 1
h=os.path.expanduser(f'<home>/notebook/git/thm01-R-agy-home/{who}-thm01-R-gemini38f-r3-A1/.gemini/antigravity-cli/history.jsonl')
L=[json.loads(l) for l in open(h).read().splitlines()]; d=L[-k]
t=d.get('display') or d.get('text') or d.get('prompt')
print(who, len(L), t.strip()==open(f).read().strip(), datetime.datetime.utcfromtimestamp(d['timestamp']/1000).strftime('%H:%M:%S'))
