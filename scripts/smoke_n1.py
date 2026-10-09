import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from osp_deformation import *

cn = Cn1(1)
print(cn.dim, cn.labels)
print(cn.parity, cn.weight)
c, gamma, gamma0 = cn.structure()
nz = {k: v for k, v in c.items() if v}
print('nonzero structure consts', len(nz))
i, j = cn.index['E_{2d1}'], cn.index['E_{-2d1}']
print('[E2d,E-2d] =', c[(i, j)])
for k in gamma:
    if gamma[k] or not gamma0[k].is_zero():
        print(cn.labels[k[0]], cn.labels[k[1]], {cn.labels[m]: str(v) for m, v in gamma[k].items()}, 'scalar:', gamma0[k])
print('gb labels', cn.A.gb_label)
