from fractions import Fraction
from typing import Dict, List, Tuple
from collections import defaultdict
import sympy as sp
import time

# Basis generators from run_full_validation
from run_full_validation import get_generators, normal_order_word

# In universal enveloping algebra, each element is a linear combination of words.
# When computing [u1 u2, v1 v2], we can either:
# 1) Use the commutator of product formula directly
# 2) Or evaluate XY - (-1)^{pX pY} YX where the multiplication rule between
#    b_j^s and a_1^\sigma includes the O(kappa) term:
#    b_j^s a_1^\sigma = a_1^\sigma b_j^s - gb_{sigma, j, s} * kappa

# Let's verify both methods and check that they give identical results!

def get_gamma_brackets(n: int, sign_convention: int = 1):
    # sign_convention:
    # 1: [b_j^s, a_1^\sigma] = - gb * kappa  (as in C_inhomogeneous_definition.md line 22)
    # -1: [b_j^s, a_1^\sigma] = + gb * kappa
    
    even_basis, odd_basis, realizations, parity = get_generators(n)
    all_basis = even_basis + odd_basis

    # Precompute Cartan decomposition
    word_to_root = {}
    for g in all_basis:
        if not g.startswith('H_'):
            words = list(realizations[g].keys())
            word_to_root[words[0]] = g

    w_coeffs = [{} for _ in range(n + 1)]
    w_const = [Fraction(0, 1) for _ in range(n + 1)]
    w_coeffs[n][f"H_{n+1}"] = Fraction(-1, 1)
    w_const[n] = Fraction(-1, 2)
    for k in range(n - 1, 0, -1):
        w_coeffs[k] = dict(w_coeffs[k + 1])
        w_coeffs[k][f"H_{k+1}"] = w_coeffs[k].get(f"H_{k+1}", Fraction(0, 1)) + Fraction(1, 1)
        w_const[k] = w_const[k + 1]
    w_coeffs[0] = {h_name: -c for h_name, c in w_coeffs[1].items()}
    w_coeffs[0]['H_1'] = w_coeffs[0].get('H_1', Fraction(0, 1)) + Fraction(1, 1)
    w_const[0] = -w_const[1]

    cartan_word_to_idx = {('a_1_p', 'a_1_m'): 0}
    for k in range(1, n + 1):
        cartan_word_to_idx[(f"b_{k}_p", f"b_{k}_m")] = k

    def decompose(poly_dict):
        # poly_dict: dict of word -> sympy expression in gb
        res = defaultdict(lambda: sp.Integer(0))
        res_const = sp.Integer(0)
        for w, coeff in poly_dict.items():
            if w == ():
                res_const += coeff
                continue
            if w in word_to_root:
                res[word_to_root[w]] += coeff
            elif w in cartan_word_to_idx:
                idx = cartan_word_to_idx[w]
                for h_name, h_c in w_coeffs[idx].items():
                    res[h_name] += coeff * Fraction(h_c)
                res_const += coeff * Fraction(w_const[idx])
            else:
                raise ValueError(f"Unrecognized word: {w}")
        return {k: sp.simplify(v) for k, v in res.items() if sp.simplify(v) != 0}, sp.simplify(res_const)

    # Let's compute [u, v]_1 (the kappa coefficient of the bracket between single oscillators):
    # u and v are oscillator strings like 'a_1_p', 'b_1_p'
    def comm_1(u: str, v: str):
        # returns sympy expr
        # [b_j^s, a_1^sigma] = - sign_convention * gb_{sigma, j, s}
        # [a_1^sigma, b_j^s] = + sign_convention * gb_{sigma, j, s}
        if u.startswith('b_') and v.startswith('a_'):
            parts_b = u.split('_')
            j, s = int(parts_b[1]), parts_b[2]
            sigma = v.split('_')[2]
            sym = sp.Symbol(f"gb_a1{sigma}_b{j}_{s}")
            return -sign_convention * sym
        elif u.startswith('a_') and v.startswith('b_'):
            sigma = u.split('_')[2]
            parts_b = v.split('_')
            j, s = int(parts_b[1]), parts_b[2]
            sym = sp.Symbol(f"gb_a1{sigma}_b{j}_{s}")
            return sign_convention * sym
        return sp.Integer(0)

    # For X = sum c_w w, Y = sum d_w w
    # We want the O(kappa) term of [X, Y}:
    # For a pair of monomials X_w = u1 u2 and Y_w = v1 v2:
    # [u1 u2, v1 v2] =
    #   u1 [u2, v1] v2 + (-1)^{p(u2)p(v1)} [u1, v1] u2 v2
    # + (-1)^{p(X)p(v1)} v1 u1 [u2, v2] + (-1)^{p(X)p(v1)+p(u2)p(v2)} v1 [u1, v2] u2
    # In each term, the bracket [u, v] is replaced by comm_1(u, v).
    # Since comm_1(u, v) is a scalar (in gb), the remaining two operators are multiplied and normal-ordered!
    
    gamma_entries = []
    
    t0 = time.time()
    for X in all_basis:
        pX = parity[X]
        poly_X = realizations[X]
        for Y in all_basis:
            pY = parity[Y]
            poly_Y = realizations[Y]

            # Accumulator for gamma(X, Y) as a polynomial of normal-ordered words
            gamma_poly = defaultdict(lambda: sp.Integer(0))

            for wX, cX in poly_X.items():
                if len(wX) == 0:
                    continue
                if len(wX) == 1:
                    # should not happen since all generators are quadratic
                    continue
                u1, u2 = wX[0], wX[1]
                pu1 = 1 if u1.startswith('a_') else 0
                pu2 = 1 if u2.startswith('a_') else 0

                for wY, cY in poly_Y.items():
                    if len(wY) == 0:
                        continue
                    v1, v2 = wY[0], wY[1]
                    pv1 = 1 if v1.startswith('a_') else 0
                    pv2 = 1 if v2.startswith('a_') else 0

                    c_total = cX * cY

                    # Term 1: u1 [u2, v1] v2 -> comm_1(u2, v1) * (u1 v2)
                    c1 = comm_1(u2, v1)
                    if c1 != 0:
                        # normal order u1 v2
                        w_ord = normal_order_word((u1, v2))
                        for w, cw in w_ord.items():
                            gamma_poly[w] += c_total * c1 * cw

                    # Term 2: (-1)^{pu2 pv1} [u1, v1] u2 v2
                    c2 = comm_1(u1, v1)
                    if c2 != 0:
                        s = -1 if (pu2 * pv1) % 2 == 1 else 1
                        w_ord = normal_order_word((u2, v2))
                        for w, cw in w_ord.items():
                            gamma_poly[w] += c_total * s * c2 * cw

                    # Term 3: (-1)^{pX pv1} v1 u1 [u2, v2]
                    c3 = comm_1(u2, v2)
                    if c3 != 0:
                        s = -1 if (pX * pv1) % 2 == 1 else 1
                        w_ord = normal_order_word((v1, u1))
                        for w, cw in w_ord.items():
                            gamma_poly[w] += c_total * s * c3 * cw

                    # Term 4: (-1)^{pX pv1 + pu2 pv2} v1 [u1, v2] u2
                    c4 = comm_1(u1, v2)
                    if c4 != 0:
                        s = -1 if (pX * pv1 + pu2 * pv2) % 2 == 1 else 1
                        w_ord = normal_order_word((v1, u2))
                        for w, cw in w_ord.items():
                            gamma_poly[w] += c_total * s * c4 * cw

            decomp, res_const = decompose(gamma_poly)
            if res_const != 0:
                print(f"Residual const for ({X}, {Y}): {res_const}")
            for Z, expr in decomp.items():
                gamma_entries.append((X, Y, Z, expr))

    t1 = time.time()
    print(f"n={n}: total gamma entries = {len(gamma_entries)} (time: {t1 - t0:.2f}s)")
    return gamma_entries

for n in [1, 2, 3]:
    entries = get_gamma_brackets(n)
