import json,sys
from fractions import Fraction as F
sys.path.insert(0,'<home>/notebook/git/ai-workflow-evaluation/case_studies/osp-schema-extension/t1-schema-extension/revision-ipsj-r1/judging/gcheck')
from refmodel import WorkerBasisRef
D=sys.argv[1]
for n in (1,2,3):
    s1=json.load(open(f'{D}/C_{n}_structure.json')); c=json.load(open(f'{D}/C_{n}_coboundary.json'))
    basis=s1['basis']['even']+s1['basis']['odd']
    real={x:[(F(t['coeff']),t['words']) for t in s1['generator_realization']['realizations'][x]['standard_form']] for x in basis}
    R=WorkerBasisRef(n,basis,s1['parity'],real)
    cols={}
    pairs=set()
    for e in c['coboundary_structure']:
        pairs.add((e['X'],e['Y']))
        for t in e['delta_f_terms']:
            cols.setdefault(t['phi_label'],{})[(e['X'],e['Y'],t['Z'])]=cols.get(t['phi_label'],{}).get((e['X'],e['Y'],t['Z']),0)+F(t['coeff'])
    ref=R.coboundary_columns()
    refpairs={(k[0],k[1]) for col in ref.values() for k in col}
    # restrict ref to pairs W records
    A=[{k:v for k,v in col.items() if (k[0],k[1]) in pairs} for col in ref.values()]
    Wc=list(cols.values())
    # also map labels: phi_oe__T__S ? compare columns directly
    rW,rA,rB=R.rank(Wc),R.rank(A),R.rank(Wc+A)
    missing=[p for p in refpairs if p not in pairs and (p[1],p[0]) not in pairs]
    print(n,'params',len(cols),'pairsW',len(pairs),'refpairs',len(refpairs),'rank W',rW,'rank ref(restricted)',rA,'rank both',rB,'missing nonrev pairs',len(missing))
