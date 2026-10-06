"""Check the FULL U(A) graded Jacobiator (every monomial component, incl.
scalars and kappa-scalars) vanishes for the deformed quadratic generators."""
import itertools
from sympy import simplify
from osp_engine import make_gb_symbols, super_bracket
from basis import build_basis, monomial_to_index

n = 1
gb = make_gb_symbols(n)
basis, parity, names = build_basis(n)
D = len(basis)


def dbl(x, y, z):
    inner = super_bracket(basis[y], basis[z], parity[y], parity[z], gb)
    pyz = (parity[y] + parity[z]) % 2
    return super_bracket(basis[x], inner, parity[x], pyz, gb)


def jac_full(a, b, c):
    pa, pb, pc = parity[a], parity[b], parity[c]
    terms = ((dbl(a, b, c), (-1) ** (pa * pc)),
             (dbl(b, c, a), (-1) ** (pb * pa)),
             (dbl(c, a, b), (-1) ** (pc * pb)))
    acc = {}
    for t, s in terms:
        for k, v in t.items():
            acc[k] = acc.get(k, 0) + s * v
    return {k: simplify(v) for k, v in acc.items() if simplify(v) != 0}


bad = 0
examples = []
for (a, b, c) in itertools.permutations(range(D), 3):
    j = jac_full(a, b, c)
    if j:
        bad += 1
        if len(examples) < 3:
            examples.append((names[a], names[b], names[c],
                             {(kp, t): str(v) for (kp, t), v in j.items()}))
print(f"full U(A) Jacobiator: nonzero on {bad}/{D*(D-1)*(D-2)} triples")
for e in examples:
    print("  ", e)
