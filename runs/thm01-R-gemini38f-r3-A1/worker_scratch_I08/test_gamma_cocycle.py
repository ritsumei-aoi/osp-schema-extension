import sys
sys.path.insert(0, '<home>/notebook/git/thm01-R/thm01-R-gemini38f-r3-A1')
from fractions import Fraction
from collections import defaultdict
import sympy as sp
import time

from src.C_generators import get_generators

def compute_gamma_via_rep(n: int, sign_convention: int = 1):
    even_basis, odd_basis, realizations, ff, notes, parity = get_generators(n)
    all_basis = even_basis + odd_basis
    dim_g = len(all_basis)

    V_basis = ['a_1_p', 'a_1_m']
    for k in range(1, n + 1):
        V_basis.extend([f"b_{k}_p", f"b_{k}_m"])
    dim_V = len(V_basis)

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

    # comm_1(u, v): coefficient of kappa
    # [b_j^s, a_1^sigma] = - sign_convention * gb_{sigma, j, s} * kappa
    # [a_1^sigma, b_j^s] = + sign_convention * gb_{sigma, j, s} * kappa
    def comm_1(u: str, v: str):
        if u.startswith('b_') and v.startswith('a_'):
            parts_b = u.split('_')
            j, s = int(parts_b[1]), parts_b[2]
            sigma = v.split('_')[2]
            return -sign_convention * sp.Symbol(f"gb_a1{sigma}_b{j}_{s}")
        elif u.startswith('a_') and v.startswith('b_'):
            sigma = u.split('_')[2]
            parts_b = v.split('_')
            j, s = int(parts_b[1]), parts_b[2]
            return sign_convention * sp.Symbol(f"gb_a1{sigma}_b{j}_{s}")
        return sp.Integer(0)

    # Action ad_0(X)(v)
    def ad_0(poly, v: str):
        pv = V_parity(v)
        res = defaultdict(Fraction)
        for w, c in poly.items():
            if len(w) != 2: continue
            u1, u2 = w[0], w[1]
            pu2 = V_parity(u2)
            c1 = comm_0(u2, v)
            if c1 != 0: res[u1] += c * c1
            c2 = comm_0(u1, v)
            if c2 != 0:
                s = -1 if (pu2 * pv) % 2 == 1 else 1
                res[u2] += c * s * c2
        return res

    # Action ad_1(X)(v): coefficient of kappa in [X, v]
    def ad_1(poly, v: str):
        pv = V_parity(v)
        res = defaultdict(lambda: sp.Integer(0))
        for w, c in poly.items():
            if len(w) != 2: continue
            u1, u2 = w[0], w[1]
            pu2 = V_parity(u2)
            c1 = comm_1(u2, v)
            if c1 != 0:
                res[u1] += c * c1
            c2 = comm_1(u1, v)
            if c2 != 0:
                s = -1 if (pu2 * pv) % 2 == 1 else 1
                res[u2] += c * s * c2
        return res

    # Precompute ad_0 matrix to invert: g -> Mat(V)
    # Mat(V) is flattened to vector of length dim_V * dim_V
    ad_matrix_rows = []
    for X in all_basis:
        row = []
        for v in V_basis:
            ad_X_v = ad_0(realizations[X], v)
            for w in V_basis:
                row.append(Fraction(ad_X_v.get(w, Fraction(0, 1))))
        ad_matrix_rows.append(row)

    sp_A = sp.Matrix(ad_matrix_rows) # size (dim_g, dim_V^2)
    # Pseudo-inverse or solve
    # Since rank is dim_g, sp_A has full row rank!
    # sp_A * Z = target_vector => Z
    # We can precompute the left inverse: (A A^T)^(-1) A ... wait, rows are generators!
    # So A^T * x = target? No, target is a row vector in Mat(V).
    # target = sum_Z c_Z * row_Z = c * A
    # So c * A = target => c = target * A^T * (A A^T)^(-1)!
    AAT = sp_A * sp_A.T
    AAT_inv = AAT.inv()
    proj = sp_A.T * AAT_inv # shape (dim_V^2, dim_g)
    # Then for any target row vector T: c = T * proj!

    # Now compute gamma(X, Y) for all pairs X, Y
    # The action of gamma(X, Y) on v is:
    # ad_gamma(X, Y)(v) = ad_0(X)(ad_1(Y)(v)) + ad_1(X)(ad_0(Y)(v))
    #                    - (-1)^{pX pY} [ ad_0(Y)(ad_1(X)(v)) + ad_1(Y)(ad_0(X)(v)) ]
    
    gamma_dict = defaultdict(dict)
    t0 = time.time()
    
    for X in all_basis:
        pX = parity[X]
        poly_X = realizations[X]
        for Y in all_basis:
            pY = parity[Y]
            poly_Y = realizations[Y]
            sign_XY = -1 if (pX * pY) % 2 == 1 else 1

            # Compute target vector for gamma(X, Y)
            target = []
            has_nonzero = False
            for v in V_basis:
                # ad_1(Y)(v)
                ad1_Y_v = ad_1(poly_Y, v)
                # ad_0(Y)(v)
                ad0_Y_v = ad_0(poly_Y, v)
                # ad_1(X)(v)
                ad1_X_v = ad_1(poly_X, v)
                # ad_0(X)(v)
                ad0_X_v = ad_0(poly_X, v)

                # Term A: ad_0(X)(ad1_Y_v)
                termA = defaultdict(lambda: sp.Integer(0))
                for w, cw in ad1_Y_v.items():
                    for u, cu in ad_0(poly_X, w).items():
                        termA[u] += cw * cu

                # Term B: ad_1(X)(ad0_Y_v)
                termB = defaultdict(lambda: sp.Integer(0))
                for w, cw in ad0_Y_v.items():
                    for u, cu in ad_1(poly_X, w).items():
                        termB[u] += cw * cu

                # Term C: ad_0(Y)(ad1_X_v)
                termC = defaultdict(lambda: sp.Integer(0))
                for w, cw in ad1_X_v.items():
                    for u, cu in ad_0(poly_Y, w).items():
                        termC[u] += cw * cu

                # Term D: ad_1(Y)(ad0_X_v)
                termD = defaultdict(lambda: sp.Integer(0))
                for w, cw in ad0_X_v.items():
                    for u, cu in ad_1(poly_Y, w).items():
                        termD[u] += cw * cu

                for u in V_basis:
                    val = sp.simplify((termA[u] + termB[u]) - sign_XY * (termC[u] + termD[u]))
                    if val != 0:
                        has_nonzero = True
                    target.append(val)

            if has_nonzero:
                # c = target * proj
                T_mat = sp.Matrix([target]) # 1 x dim_V^2
                c_mat = T_mat * proj # 1 x dim_g
                for idx, Z in enumerate(all_basis):
                    coeff = sp.simplify(c_mat[0, idx])
                    if coeff != 0:
                        gamma_dict[(X, Y)][Z] = coeff

    t1 = time.time()
    num_entries = sum(len(v) for v in gamma_dict.values())
    print(f"n={n}: computed gamma via representation in {t1 - t0:.2f}s, non-zero entries = {num_entries}")

    # Check graded skew-symmetry of gamma:
    # gamma(Y, X) = -(-1)^{pX pY} gamma(X, Y)
    skew_errs = 0
    for X in all_basis:
        pX = parity[X]
        for Y in all_basis:
            pY = parity[Y]
            s = -1 if (pX * pY) % 2 == 1 else 1
            g_XY = gamma_dict.get((X, Y), {})
            g_YX = gamma_dict.get((Y, X), {})
            for Z in set(g_XY) | set(g_YX):
                if sp.simplify(g_YX.get(Z, 0) - (-s * g_XY.get(Z, 0))) != 0:
                    skew_errs += 1
    print(f"n={n}: gamma graded skew-symmetry errors = {skew_errs}")

    return gamma_dict

for n in [1, 2]:
    compute_gamma_via_rep(n)
