import json,sys,re
from fractions import Fraction as F
sys.path.insert(0,'<home>/notebook/git/ai-workflow-evaluation/case_studies/osp-schema-extension/t1-schema-extension/revision-ipsj-r1/judging/gcheck')
from refmodel import WorkerBasisRef
D=sys.argv[1]; sg={'p':'+','m':'-'}
for n in (1,2,3):
    s1=json.load(open(f'{D}/C_{n}_structure.json')); c=json.load(open(f'{D}/C_{n}_coboundary.json')); g=json.load(open(f'{D}/C_{n}_gamma.json'))
    basis=s1['basis']['even']+s1['basis']['odd']
    real={x:[(F(t['coeff']),t['words']) for t in s1['generator_realization']['realizations'][x]['standard_form']] for x in basis}
    R=WorkerBasisRef(n,basis,s1['parity'],real)
    cols={}; pairs=set()
    for e in c['coboundary_structure']:
        pairs.add((e['X'],e['Y']))
        for t in e['delta_f_terms']:
            k=(e['X'],e['Y'],t['Z']); d=cols.setdefault(t['phi_label'],{}); d[k]=d.get(k,0)+F(t['coeff'])
    A=list(cols.values())
    G={}
    for e in g['gamma_structure']:
        for t in e['gamma_terms']:
            m=re.fullmatch(r'gb_a_1_([pm])_b_(\d+)_([pm])',t['gb_label']); prm=(sg[m.group(1)],int(m.group(2)),sg[m.group(3)])
            d=G.setdefault(prm,{}); k=(e['X'],e['Y'],t['Z']); d[k]=d.get(k,0)+F(t['coeff'])
    Gl=list(G.values())
    rA=R.rank(A)
    out=[n,'W: rank A',rA,'rank[A|G_W]',R.rank(A+Gl)]
    # ref gamma restricted to pairs, comm/super, with/without K
    for sign in (False,True):
        for keepK in (False,True):
            Gr=[]
            for prm in R.gb_params:
                col={k:v for k,v in R.gamma(prm,sign).items() if v and (k[0],k[1]) in pairs and (keepK or k[2]!='K')}
                Gr.append(col)
            out+=[('super' if sign else 'comm')+('+K' if keepK else ''),R.rank(A+Gr)]
    print(*out)
