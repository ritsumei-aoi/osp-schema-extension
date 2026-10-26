import json,sys,re
from fractions import Fraction as F
ws,gc=sys.argv[1],sys.argv[2]; sys.path.insert(0,gc)
from refmodel import WorkerBasisRef
n=int(sys.argv[3])
S=json.load(open(f'{ws}/data/C_{n}_structure.json')); basis=S['basis']['even']+S['basis']['odd']
par={x:0 for x in S['basis']['even']}|{x:1 for x in S['basis']['odd']}
R=S['generator_realization']['realizations']; real={g:[(F(t['coeff']),list(t['words'])) for t in R[g]['standard_form']] for g in basis}
ref=WorkerBasisRef(n,basis,par,real)
G=json.load(open(f'{ws}/data/C_{n}_gamma.json'))['inhomogeneous_deformation']['gamma_constants']
def key(l):
    m=re.fullmatch(r'gb_a1([pm])_b(\d+)([pm])',l); return ('+' if m[1]=='p' else '-',int(m[2]),'+' if m[3]=='p' else '-')
for p in ref.gb_params:
    w={(e['X'],e['Y']):F(e['coeff']) for e in G if e['Z']=='K' and key(e['param'])==p}
    for sign in (False,True):
        r={(k[0],k[1]):v for k,v in ref.gamma(p,sign).items() if k[2]=='K' and v}
        ratio={k:(w.get(k,0)/r[k] if r.get(k) else None) for k in set(w)|set(r)}
        print(p,'commuting' if not sign else 'super',len(w),len(r),sorted(set(str(v) for v in ratio.values())))
print('--- detail commuting')
tot=[0,0,0,0]
for p in ref.gb_params:
    w={(e['X'],e['Y']):F(e['coeff']) for e in G if e['Z']=='K' and key(e['param'])==p}
    r={(k[0],k[1]):v for k,v in ref.gamma(p,False).items() if k[2]=='K' and v}
    for k in sorted(set(w)|set(r)):
        a,b=w.get(k,0),r.get(k,0)
        tot[0]+=a==b; tot[1]+=(a==-b and a!=0); tot[2]+=(a==0); tot[3]+=(b==0)
        if a!=b and n==1: print(p,k,'worker',a,'ref',b)
print('n',n,'K pairs: equal',tot[0],'sign-flipped',tot[1],'missing in worker',tot[2],'extra in worker',tot[3])
