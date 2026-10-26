import json,sys,re
from fractions import Fraction as F
from collections import Counter
sys.path.insert(0,'<home>/notebook/git/ai-workflow-evaluation/case_studies/osp-schema-extension/t1-schema-extension/revision-ipsj-r1/judging/gcheck')
from refmodel import WorkerBasisRef
D=sys.argv[1]; sg={'p':'+','m':'-'}
for n in (1,2):
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
    ref={}
    for prm in R.gb_params:
        for (x,y,z),c in R.gamma(prm,False).items():
            if c and z!='K': ref[(prm,x,y,z)]=c
    bad=[k for k in set(W)|set(ref) if (k[1],k[2]) in pairsW and W.get(k)!=ref.get(k)]
    print('n',n,'bad pair types',Counter((k[1].split('_')[0]+k[1].split('_')[1][:3], k[2][:6]) for k in bad).most_common(8))
    for k in sorted(bad)[:8]: print('  ',k,'W',W.get(k),'ref',ref.get(k))
    miss={(k[1],k[2]) for k in ref}-pairsW
    nonrev=[q for q in miss if (q[1],q[0]) not in pairsW]
    print('  missing nonrev',nonrev[:8])
    for q in nonrev[:3]: print('   ',q,{k[0]+(k[3],):v for k,v in ref.items() if (k[1],k[2])==q})
