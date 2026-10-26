import json,sys
from fractions import Fraction as Fr
from collections import defaultdict
WS=sys.argv[1]
for n in (1,2,3):
    s=json.load(open(f"{WS}/data/C_{n}_structure.json")); c=json.load(open(f"{WS}/data/C_{n}_coboundary.json"))
    p=s['parity']; gens=list(p)
    br=defaultdict(dict)  # br[X][Y]={Z:coeff}
    for e in s['structure_constants']:
        X,Y,Z=e['X'],e['Y'],e['Z']; k=Fr(e['coeff'])
        br[X].setdefault(Y,{}); br[X][Y][Z]=br[X][Y].get(Z,0)+k
        if (X,Y)!=(Y,X):
            sg=-(-1)**(p[X]*p[Y]); br[Y].setdefault(X,{}); br[Y][X][Z]=br[Y][X].get(Z,0)+sg*k
    def bracket(X,Y): return br.get(X,{}).get(Y,{})
    phis=c['f_map']['phi_labels']
    # f(Zj)= sum_i phi_i_j Zi ; label phi_<image>_<domain>; resolve by generator list
    def split(l):
        r=l[4:]
        for a in gens:
            if r.startswith(a+'_') and r[len(a)+1:] in p: return a,r[len(a)+1:]
        raise Exception(l)
    fmap=defaultdict(dict)  # fmap[dom][img]=label
    for l in phis:
        i,j=split(l); assert p[i]!=p[j]; fmap[j][i]=l
    def fimg(Z): return fmap.get(Z,{})   # {img: label}
    # delta f (X,Y)->{Z:{label:coef}}
    def df(X,Y):
        out=defaultdict(lambda:defaultdict(Fr))
        s1=(-1)**p[X]; s2=-(-1)**((p[X]+1)*p[Y])
        for i,l in fimg(Y).items():
            for Z,k in bracket(X,i).items(): out[Z][l]+=s1*k
        for i,l in fimg(X).items():
            for Z,k in bracket(Y,i).items(): out[Z][l]+=s2*k
        for W,k in bracket(X,Y).items():
            for i,l in fimg(W).items(): out[i][l]+=-k
        return {Z:{l:v for l,v in d.items() if v} for Z,d in out.items() if any(d.values())}
    rec=defaultdict(dict)
    for e in c['coboundary']:
        rec[(e['X'],e['Y'])][e['Z']]={l:Fr(v) for l,v in e['coeff_phi'].items()}
    bad=0;miss=0;pairs=set(rec)
    for (X,Y) in pairs:
        if df(X,Y)!=dict(rec[(X,Y)]): bad+=1
    # pairs not recorded where df nonzero
    for X in gens:
        for Y in gens:
            if (X,Y) not in pairs and (Y,X) not in pairs and df(X,Y): miss+=1
    # recorded both directions?
    both=sum(1 for (X,Y) in pairs if (Y,X) in pairs and X!=Y)
    print(n,'phi',len(phis),'entries',len(c['coboundary']),'pairs',len(pairs),'mismatch',bad,'missing',miss,'both-dir',both)
