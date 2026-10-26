import json,sys,re
from fractions import Fraction as F
sys.path.insert(0,'<home>/notebook/git/ai-workflow-evaluation/case_studies/osp-schema-extension/t1-schema-extension/revision-ipsj-r1/judging/gcheck')
from refmodel import WorkerBasisRef
D=sys.argv[1]; sg={'p':'+','m':'-'}
for n in (1,2,3):
    s1=json.load(open(f'{D}/C_{n}_structure.json')); g=json.load(open(f'{D}/C_{n}_gamma.json'))
    basis=s1['basis']['even']+s1['basis']['odd']; p=s1['parity']
    real={x:[(F(t['coeff']),t['words']) for t in s1['generator_realization']['realizations'][x]['standard_form']] for x in basis}
    R=WorkerBasisRef(n,basis,p,real)
    W={}
    for e in g['gamma_structure']:
        for t in e['gamma_terms']:
            m=re.fullmatch(r'gb_a_1_([pm])_b_(\d+)_([pm])',t['gb_label']); prm=(sg[m.group(1)],int(m.group(2)),sg[m.group(3)])
            k=(prm,e['X'],e['Y'],t['Z']); W[k]=W.get(k,0)+F(t['coeff'])
    W={k:v for k,v in W.items() if v}
    pairsW={(k[1],k[2]) for k in W}
    for sign in (False,True):
        ref={}
        for prm in R.gb_params:
            for (x,y,z),c in R.gamma(prm,sign).items():
                if c: ref[(prm,x,y,z)]=c
        # compare only on pairs W stores
        refW={k:v for k,v in ref.items() if (k[1],k[2]) in pairsW}
        bad=[k for k in set(W)|set(refW) if W.get(k)!=refW.get(k)]
        refpairs={(k[1],k[2]) for k in ref}
        miss=refpairs-pairsW; missrev=[q for q in miss if (q[1],q[0]) in pairsW]
        print(n,'super' if sign else 'comm ','Wterms',len(W),'pairsW',len(pairsW),'refpairs',len(refpairs),'mismatch_on_W_pairs',len(bad),'missing',len(miss),'of which reverse',len(missrev),'K',sum(1 for k in W if k[3]=='K'),'refK',sum(1 for k in ref if k[3]=='K'))
