import sys, os
from fractions import Fraction
from collections import defaultdict
import sympy as sp

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../thm01-R-gemini38f-r3-A1")))
from src.C_generators import get_generators

def test_corrected_ad(n=1):
    even_basis, odd_basis, realizations, _, _, parity = get_generators(n)
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

    def comm_1(u: str, v: str):
        # [b_j^s, a_1^sigma] = - gb * kappa
        # [a_1^sigma, b_j^s] = + gb * kappa
        if u.startswith('b_') and v.startswith('a_'):
            parts_b = u.split('_')
            j, s = int(parts_b[1]), parts_b[2]
            sigma = v.split('_')[2]
            return -sp.Symbol(f"gb_a1{sigma}_b{j}{s}")
        elif u.startswith('a_') and v.startswith('b_'):
            sigma = u.split('_')[2]
            parts_b = v.split('_')
            j, s = int(parts_b[1]), parts_b[2]
            return sp.Symbol(f"gb_a1{sigma}_b{j}{s}")
        return sp.Integer(0)

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

    def ad_1_corrected(poly, v: str):
        pv = V_parity(v)
        res = defaultdict(lambda: sp.Integer(0))
        for w, c in poly.items():
            if len(w) != 2: continue
            u1, u2 = w[0], w[1]
            pu1, pu2 = V_parity(u1), V_parity(u2)
            
            # [u1 u2, v] = u1 [u2, v] + (-1)^{p(u2)p(v)} [u1, v] u2
            # [u2, v] = c1 * kappa. u1 * (c1 kappa) = kappa * (-1)^{p(u1)} c1 u1
            c1 = comm_1(u2, v)
            if c1 != 0:
                s1 = -1 if pu1 == 1 else 1
                res[u1] += c * s1 * c1
                
            # [u1, v] = c2 * kappa. (-1)^{p(u2)p(v)} (c2 kappa) u2 = kappa * (-1)^{p(u2)p(v)} c2 u2
            c2 = comm_1(u1, v)
            if c2 != 0:
                s2 = -1 if (pu2 * pv) % 2 == 1 else 1
                res[u2] += c * s2 * c2
        return res

    print("Checking ad_1 of H_1 on all v in V:")
    for v in V_basis:
        res = ad_1_corrected(realizations['H_1'], v)
        print(f"ad_1(H_1)({v}) =", dict(res))

    print("\nChecking ad_1 of H_2 on all v in V:")
    for v in V_basis:
        res = ad_1_corrected(realizations['H_2'], v)
        print(f"ad_1(H_2)({v}) =", dict(res))

    # Now let's check [ad(H_1), ad(H_2)] on V
    pX = parity['H_1'] # 0
    pY = parity['H_2'] # 0
    sign_XY = 1

    print("\nChecking [ad(H_1), ad(H_2)] on all v in V:")
    for v in V_basis:
        ad1_Y_v = ad_1_corrected(realizations['H_2'], v)
        ad0_Y_v = ad_0(realizations['H_2'], v)
        ad1_X_v = ad_1_corrected(realizations['H_1'], v)
        ad0_X_v = ad_0(realizations['H_1'], v)

        # termA: (-1)^pX * ad_0(X, ad_1(Y, v))
        termA = defaultdict(lambda: sp.Integer(0))
        for w, cw in ad1_Y_v.items():
            for u, cu in ad_0(realizations['H_1'], w).items():
                termA[u] += (-1)**pX * cw * cu

        # termB: ad_1(X, ad_0(Y, v))
        termB = defaultdict(lambda: sp.Integer(0))
        for w, cw in ad0_Y_v.items():
            for u, cu in ad_1_corrected(realizations['H_1'], w).items():
                termB[u] += cw * cu

        # termC: (-1)^pY * ad_0(Y, ad_1(X, v))
        termC = defaultdict(lambda: sp.Integer(0))
        for w, cw in ad1_X_v.items():
            for u, cu in ad_0(realizations['H_2'], w).items():
                termC[u] += (-1)**pY * cw * cu

        # termD: ad_1(Y, ad_0(X, v))
        termD = defaultdict(lambda: sp.Integer(0))
        for w, cw in ad0_X_v.items():
            for u, cu in ad_1_corrected(realizations['H_2'], w).items():
                termD[u] += cw * cu

        for u in V_basis:
            val = sp.simplify((termA[u] + termB[u]) - sign_XY * (termC[u] + termD[u]))
            if val != 0:
                print(f"NON-ZERO on v={v}, u={u}: {val}")

test_corrected_ad()
