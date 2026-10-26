import json,sys
from fractions import Fraction as F
from collections import defaultdict
d=json.load(open(sys.argv[1]))
B=d['basis']['even']+d['basis']['odd']; p={b:d['parity'][b] for b in B}
br=defaultdict(lambda: defaultdict(F))
for e in d['structure_constants']: br[(e['X'],e['Y'])][e['Z']]+=F(e['coeff'])
pairs=set(br)
# fill skew if only one orientation listed
both=sum(1 for (x,y) in pairs if (y,x) in pairs)
for (x,y) in list(pairs):
    if (y,x) not in pairs:
        s=-(-1)**(p[x]*p[y])
        for z,c in br[(x,y)].items(): br[(y,x)][z]=s*c
skew=0
for x in B:
    for y in B:
        a=br.get((x,y),{}); b=br.get((y,x),{}); s=-(-1)**(p[x]*p[y])
        for z in set(a)|set(b):
            if a.get(z,0)-s*b.get(z,0)!=0: skew+=1
def bv(x,v):
    out=defaultdict(F)
    for y,c in v.items():
        for z,cc in br.get((x,y),{}).items(): out[z]+=c*cc
    return out
bad=0
for x in B:
    for y in B:
        for z in B:
            t=defaultdict(F)
            for (a,b,c) in ((x,y,z),(y,z,x),(z,x,y)):
                s=(-1)**(p[a]*p[c])
                for k,v in bv(a,br.get((b,c),{})).items(): t[k]+=s*v
            if any(v!=0 for v in t.values()): bad+=1
print(sys.argv[1].split('/')[-1], 'entries',len(d['structure_constants']),'both-orient',both,'skewfail',skew,'jacobifail',bad)
