import sys, os
from fractions import Fraction
from collections import defaultdict
import sympy as sp

REPO_ROOT = "<home>/notebook/git/thm01-R/thm01-R-gemini38f-r3-A1"
sys.path.insert(0, REPO_ROOT)
from src.C_generators import get_generators

def compute_corrected_gamma(n: int, sign_convention: int = 1):
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
        if u.startswith('b_') and v.startswith('a_'):
            parts_b = u.split('_')
            j, s = int(parts_b[1]), parts_b[2]
            sigma = v.split('_')[2]
            return -sign_convention * sp.Symbol(f"gb_a1{sigma}_b{j}{s}")
        elif u.startswith('a_') and v.startswith('b_'):
            sigma = u.split('_')[2]
            parts_b = v.split('_')
            j, s = int(parts_b[1]), parts_b[2]
            return sign_convention * sp.Symbol(f"gb_a1{sigma}_b{j}{s}")
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

    def ad_1(poly, v: str):
        pv = V_parity(v)
        res = defaultdict(lambda: sp.Integer(0))
        for w, c in poly.items():
            if len(w) != 2: continue
            u1, u2 = w[0], w[1]
            pu1, pu2 = V_parity(u1), V_parity(u2)

            # [u1 u2, v] = u1 [u2, v] + (-1)^{p(u2)p(v)} [u1, v] u2
            # Moving kappa to left:
            # u1 (c1 kappa) = kappa * (-1)^{p(u1)} c1 u1
            c1 = comm_1(u2, v)
            if c1 != 0:
                s1 = -1 if pu1 == 1 else 1
                res[u1] += c * s1 * c1

            # (c2 kappa) u2 = kappa * c2 u2
            c2 = comm_1(u1, v)
            if c2 != 0:
                s2 = -1 if (pu2 * pv) % 2 == 1 else 1
                res[u2] += c * s2 * c2
        return res

    # Precompute ad_0 matrix to invert
    ad_matrix_rows = []
    for X in all_basis:
        row = []
        for v in V_basis:
            ad_X_v = ad_0(realizations[X], v)
            for w in V_basis:
                row.append(Fraction(ad_X_v.get(w, Fraction(0, 1))))
        ad_matrix_rows.append(row)

    sp_A = sp.Matrix(ad_matrix_rows)
    AAT = sp_A * sp_A.T
    AAT_inv = AAT.inv()
    proj = sp_A.T * AAT_inv

    gamma_dict = defaultdict(dict)
    for X in all_basis:
        pX = parity[X]
        poly_X = realizations[X]
        for Y in all_basis:
            pY = parity[Y]
            poly_Y = realizations[Y]
            sign_XY = -1 if (pX * pY) % 2 == 1 else 1

            target = []
            has_nonzero = False
            for v in V_basis:
                ad1_Y_v = ad_1(poly_Y, v)
                ad0_Y_v = ad_0(poly_Y, v)
                ad1_X_v = ad_1(poly_X, v)
                ad0_X_v = ad_0(poly_X, v)

                # Term A: (-1)^pX * ad_0(X)(ad_1(Y)(v))
                termA = defaultdict(lambda: sp.Integer(0))
                for w, cw in ad1_Y_v.items():
                    for u, cu in ad_0(poly_X, w).items():
                        termA[u] += ((-1)**pX) * cw * cu

                # Term B: ad_1(X)(ad_0(Y)(v))
                termB = defaultdict(lambda: sp.Integer(0))
                for w, cw in ad0_Y_v.items():
                    for u, cu in ad_1(poly_X, w).items():
                        termB[u] += cw * cu

                # Term C: (-1)^pY * ad_0(Y)(ad_1(X)(v))
                termC = defaultdict(lambda: sp.Integer(0))
                for w, cw in ad1_X_v.items():
                    for u, cu in ad_0(poly_Y, w).items():
                        termC[u] += ((-1)**pY) * cw * cu

                # Term D: ad_1(Y)(ad_0(X)(v))
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
                target_vec = sp.Matrix([target])
                coords = target_vec * proj
                for k, Z in enumerate(all_basis):
                    val = sp.simplify(coords[k])
                    if val != 0:
                        gamma_dict[(X, Y, Z)] = val

    return gamma_dict, all_basis, parity

gamma_dict, all_basis, parity = compute_corrected_gamma(1)
print(f"Corrected gamma computed: {len(gamma_dict)} entries")
for (X, Y, Z), val in sorted(list(gamma_dict.items()))[:10]:
    print(f"gamma({X}, {Y})^{Z} = {val}")

# Now let's check Jacobi on this corrected gamma!
import json
with open(f"{REPO_ROOT}/data/C_1_structure.json") as f: s1 = json.load(f)
c_base = defaultdict(Fraction)
for e in s1["structure_constants"]:
    c_base[(e["X"], e["Y"], e["Z"])] = Fraction(e["coeff"])

violations = 0
total_triples = 0
for idx_X, X in enumerate(all_basis):
    pX = parity[X]
    for idx_Y, Y in enumerate(all_basis):
        if idx_X > idx_Y: continue
        pY = parity[Y]
        for idx_Z, Z in enumerate(all_basis):
            if idx_Y > idx_Z: continue
            pZ = parity[Z]
            total_triples += 1

            triples = [
                (X, pX, Y, pY, Z, pZ, (-1)**(pX * pZ)),
                (Y, pY, Z, pZ, X, pX, (-1)**(pY * pX)),
                (Z, pZ, X, pX, Y, pY, (-1)**(pZ * pY)),
            ]

            res_W = defaultdict(lambda: sp.Integer(0))
            for A, pA, B, pB, C, pC, sign_cyc in triples:
                # [A, gamma(B, C)]_0
                # When A passes kappa (parity 1): (-1)^pA
                sign_kappa = (-1)**pA
                for W in all_basis:
                    g_BC_W = gamma_dict.get((B, C, W), sp.Integer(0))
                    if g_BC_W != 0:
                        for target in all_basis:
                            c = c_base.get((A, W, target), Fraction(0))
                            if c != 0:
                                res_W[target] += sign_cyc * sign_kappa * g_BC_W * c

                # gamma(A, [B, C]_0)
                for W in all_basis:
                    c_BC_W = c_base.get((B, C, W), Fraction(0))
                    if c_BC_W != 0:
                        for target in all_basis:
                            g_AW_target = gamma_dict.get((A, W, target), sp.Integer(0))
                            if g_AW_target != 0:
                                res_W[target] += sign_cyc * c_BC_W * g_AW_target

            for target, expr in res_W.items():
                if sp.simplify(expr) != 0:
                    violations += 1
                    if violations <= 5:
                        print(f"Violation on ({X}, {Y}, {Z}), target {target}: {sp.simplify(expr)}")
                    break

print(f"Super-Jacobi Check on Corrected Gamma: Total triples = {total_triples}, Violations = {violations}")
