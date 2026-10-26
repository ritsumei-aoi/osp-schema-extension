# agent computation: joint rank of the obstruction over all gb directions, using the run's own code and data
import sys, os
from fractions import Fraction
root=sys.argv[1]; os.chdir(root); sys.path.insert(0, os.path.join(root,"src"))
from C_triviality import build_coboundary_system, load_gamma_evaluated
from C_gamma import get_all_gb_labels
import sympy as sp
for n in [1,2,3]:
    sysm=build_coboundary_system(n); labels=get_all_gb_labels(n)
    keys=sysm["sorted_keys"]; keyset=set(keys); cols=[]; rowkeys={}
    for gbl in labels:
        g=load_gamma_evaluated(n,{x:(1 if x==gbl else 0) for x in labels})
        res={}
        for k,v in g.items():
            if k not in keyset and v!=0: res[("out",k)]=v
        b=[g.get(k,Fraction(0)) for k in keys]
        for op in sysm["ops"]:
            if op[0]=='swap': _,r1,r2=op; b[r1],b[r2]=b[r2],b[r1]
            elif op[0]=='scale': _,r,f=op; b[r]=b[r]*f
            elif op[0]=='elim': _,r,p,f=op; b[r]=b[r]-f*b[p]
        for r in sysm["free_rows"]:
            if b[r]!=0: res[("free",r)]=b[r]
        cols.append(res)
    allrows=sorted({k for c in cols for k in c}, key=str)
    M=sp.Matrix([[c.get(r,0) for c in cols] for r in allrows])
    print(f"n={n}: gb dims {len(labels)}, obstruction rows {len(allrows)}, joint rank {M.rank()}")
