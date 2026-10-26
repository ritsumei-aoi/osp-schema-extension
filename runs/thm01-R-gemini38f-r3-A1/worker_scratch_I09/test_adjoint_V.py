from fractions import Fraction
from typing import Dict, List, Tuple
from collections import defaultdict
import sympy as sp
from src.C_generators import get_generators

def test_adjoint(n: int):
    even_basis, odd_basis, realizations, ff, notes, parity = get_generators(n)
    all_basis = even_basis + odd_basis

    V_basis = ['a_1_p', 'a_1_m']
    for k in range(1, n + 1):
        V_basis.extend([f"b_{k}_p", f"b_{k}_m"])

    def V_parity(v: str) -> int:
        return 1 if v.startswith('a_') else 0

    def comm_0(u: str, v: str) -> Fraction:
        pu, pv = V_parity(u), V_parity(v)
        if pu == 1 and pv == 1:
            if (u, v) in [('a_1_m', 'a_1_p'), ('a_1_p', 'a_1_m')]:
                return Fraction(1, 1)
            return Fraction(0, 1)
        elif pu == 0 and pv == 0:
            if u.startswith('b_') and v.startswith('b_'):
                p1, p2 = u.split('_'), v.split('_')
                if int(p1[1]) == int(p2[1]):
                    if p1[2] == 'm' and p2[2] == 'p': return Fraction(1, 1)
                    if p1[2] == 'p' and p2[2] == 'm': return Fraction(-1, 1)
            return Fraction(0, 1)
        return Fraction(0, 1)

    def ad_0(X_name: str, v: str) -> Dict[str, Fraction]:
        poly = realizations[X_name]
        pv = V_parity(v)
        res = defaultdict(Fraction)
        for w, c in poly.items():
            if len(w) != 2:
                continue
            u1, u2 = w[0], w[1]
            pu1, pu2 = V_parity(u1), V_parity(u2)
            c1 = comm_0(u2, v)
            if c1 != 0:
                res[u1] += c * c1
            c2 = comm_0(u1, v)
            if c2 != 0:
                s = -1 if (pu2 * pv) % 2 == 1 else 1
                res[u2] += c * s * c2
        return {k: v for k, v in res.items() if v != 0}

    matrix_rows = []
    for X in all_basis:
        row = []
        for v in V_basis:
            ad_X_v = ad_0(X, v)
            for w in V_basis:
                row.append(ad_X_v.get(w, Fraction(0, 1)))
        matrix_rows.append(row)

    sp_mat = sp.Matrix(matrix_rows)
    rank = sp_mat.rank()
    print(f"n={n}: dim(g)={len(all_basis)}, ad_0 matrix rank={rank}")
    assert rank == len(all_basis), f"Rank mismatch: {rank} != {len(all_basis)}"

test_adjoint(1)
test_adjoint(2)
test_adjoint(3)
