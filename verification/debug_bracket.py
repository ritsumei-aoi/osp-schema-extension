#!/usr/bin/env python3
import sys; sys.path.insert(0, '.')
from fractions import Fraction as F
from verification.operator_algebra import DeformedOscillator, DeformedOscillatorUndeformed

alg_def = DeformedOscillator(1, 2, 3, 4)
alg_undef = DeformedOscillatorUndeformed()

labels = {(1,0,1,0): 'o1', (1,0,0,1): 'o2', (0,1,1,0): 'o3', (0,1,0,1): 'o4',
          (0,0,2,0): 'bp2', (0,0,0,2): 'bm2', (1,1,0,0): 'Na', (0,0,1,1): 'Nb',
          (0,0,0,0): '1'}

def show(terms, name):
    print(f'{name}:')
    for k, v in sorted(terms.items()):
        osc = k[:4]
        nm = labels.get(osc, str(osc))
        kstr = '_K' if k[4] else ''
        print(f'  {nm}{kstr}: {v}')
    print()

t = alg_def.build_product(['a+','b+','a-'])
show(t, 'a+b+a- (def)')

t2 = alg_def.build_product(['a+','b+','a-','b+'])
show(t2, 'a+b+a-b+ (def)')

t3 = alg_def.build_product(['a-','b+','a+','b+'])
show(t3, 'a-b+a+b+ (def)')

brk = alg_def.add_terms(t2, t3)
show(brk, '{o1,o3}_def = t2+t3')

u2 = alg_undef.build_product(['a+','b+','a-','b+'])
u3 = alg_undef.build_product(['a-','b+','a+','b+'])
brk_u = alg_undef.add_terms(u2, u3)
show(brk_u, '{o1,o3}_undef')

diff = alg_def.sub_terms(brk, brk_u)
show(diff, 'difference')
