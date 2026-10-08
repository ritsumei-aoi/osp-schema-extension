#!/usr/bin/env python3
"""
Worked example for docs/issues/mathematical_proof.md, section 1.3:
the bracket [b_k^+ b_k^-, E_{sigma eps + delta_k}] in U(A') for n = 1, k = 1,
printed in the three sections (representatives of the odd generators):
   normal-ordered  b a,   document  a b,   super-symmetrised  (ab + ba)/2.
Usage: python3 scripts/example_bracket.py
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from cn1_deformation import Osc, coef_scale, HALF  # noqa: E402

o = Osc(1)


def show(E):
    parts = []
    for w, c in sorted(E.items(), key=lambda t: (len(t[0]), t[0])):
        cs = ' + '.join(('%s' % v) if k is None else ('%s*gb[a%s,b%d%s]' % (v, k[0], k[1], k[2])) for k, v in c.items())
        parts.append('(%s) %s' % (cs, o.word_name(w)))
    return '  +  '.join(parts)


X = o.word(o.bp(1), o.bm(1))                       # b+ b-
for sigma, a_id in (('+', o.AP), ('-', o.AM)):
    E_no = o.word(o.bp(1), a_id)                   # b+ a^sigma  (normal ordered)
    E_doc = o.word(a_id, o.bp(1))                  # a^sigma b+  (document)
    E_sym = {w: coef_scale(c, HALF) for w, c in o.add(o.normal_order((a_id, o.bp(1))), o.normal_order((o.bp(1), a_id))).items()}
    print('sigma = %s' % sigma)
    print('  document word a%s b1+ normal-ordered = %s' % (sigma, show(o.normal_order((a_id, o.bp(1))))))
    print('  symmetrised element                = %s' % show(E_sym))
    for label, E in (('normal-ordered', E_no), ('document', E_doc), ('symmetrised', E_sym)):
        print('  [b1+ b1-, E] with E in %-15s section = %s' % (label, show(o.bracket(X, 0, E, 1))))
    print()
print('All three brackets coincide as elements of U(A\'); they differ only in how the result is')
print('re-expressed in terms of the chosen representative E (E_doc = E_no + gb*kappa, E_sym = E_no + gb*kappa/2),')
print('which moves a multiple of kappa*1 between the "E" term and the scalar part of gamma.')
