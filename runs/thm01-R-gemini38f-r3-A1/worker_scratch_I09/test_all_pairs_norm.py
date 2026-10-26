import sys, os
from fractions import Fraction
from collections import defaultdict
import sympy as sp

REPO_ROOT = "<home>/notebook/git/thm01-R/thm01-R-gemini38f-r3-A1"
sys.path.insert(0, REPO_ROOT)
from src.C_generators import get_generators, parity_of

def osc_key(osc: str):
    if osc == 'a_1_p': return (0, 0, 0)
    if osc == 'a_1_m': return (0, 1, 0)
    parts = osc.split('_')
    return (1, int(parts[1]), 0 if parts[2] == 'p' else 1)

def normal_order_deformed_word(word: tuple):
    current = {(word, None): Fraction(1, 1)}
    while True:
        next_dict = defaultdict(Fraction)
        all_sorted = True
        for (w, param), coeff in current.items():
            if coeff == 0:
                continue
            found = False
            for i in range(len(w) - 1):
                o1, o2 = w[i], w[i+1]
                if o1 == o2 and parity_of(o1) == 1:
                    found = True
                    all_sorted = False
                    break
                elif osc_key(o1) > osc_key(o2):
                    found = True
                    all_sorted = False
                    if o1 == 'a_1_m' and o2 == 'a_1_p':
                        next_dict[(w[:i] + (o2, o1) + w[i+2:], param)] += -coeff
                        next_dict[(w[:i] + w[i+2:], param)] += coeff
                    elif o1.startswith('b_') and o2.startswith('b_'):
                        p1, p2 = o1.split('_'), o2.split('_')
                        j, s1 = int(p1[1]), p1[2]
                        k, s2 = int(p2[1]), p2[2]
                        if s1 == 'm' and s2 == 'p' and j == k:
                            next_dict[(w[:i] + (o2, o1) + w[i+2:], param)] += coeff
                            next_dict[(w[:i] + w[i+2:], param)] += coeff
                        else:
                            next_dict[(w[:i] + (o2, o1) + w[i+2:], param)] += coeff
                    elif o1.startswith('b_') and o2.startswith('a_'):
                        next_dict[(w[:i] + (o2, o1) + w[i+2:], param)] += coeff
                        if param is None:
                            parts_b = o1.split('_')
                            j, s = int(parts_b[1]), parts_b[2]
                            sigma = o2.split('_')[2]
                            p_name = f"gb_a1{sigma}_b{j}{s}"
                            # In [b_j^s, a_1^sigma] = - gb * kappa.
                            # b_j^s a_1^sigma = a_1^sigma b_j^s - gb * kappa.
                            # The remaining word is w[:i] + w[i+2:].
                            # But wait! Does the remaining word need to be normal-ordered?
                            # Yes! So we just add (w[:i] + w[i+2:], p_name) with coefficient -coeff!
                            next_dict[(w[:i] + w[i+2:], p_name)] += -coeff
                    else:
                        raise ValueError(f"Unhandled pair: {o1}, {o2}")
                    break
            if not found:
                next_dict[(w, param)] += coeff
        if all_sorted:
            return {k: v for k, v in current.items() if v != 0}
        current = next_dict

def test_n(n=1):
    even_basis, odd_basis, realizations, _, _, parity = get_generators(n)
    all_basis = even_basis + odd_basis

    # Precompute basis poly dictionary
    # In C_generators, each basis element X has realization {word: coeff}
    # Let's map normalized word -> basis element
    # For Cartans, realizations have:
    # H_1: {('a_1_p', 'a_1_m'): 1, ('b_1_p', 'b_1_m'): 1}
    # H_2: {('b_1_p', 'b_1_m'): -1, (): -1/2}

    print(f"Testing n={n}...")
    # Multiply X and Y:
    # XY = sum cX * cY * normal_order_deformed_word(wX + wY)
    # [X, Y]~ = XY - (-1)^{pX pY} YX
    
    # Let's check non-quadratic terms in [X, Y]~
    non_quad_terms = 0
    total_pairs = 0
    
    for idx_X, X in enumerate(all_basis):
        pX = parity[X]
        polyX = realizations[X]
        for idx_Y, Y in enumerate(all_basis):
            if idx_X > idx_Y: continue
            pY = parity[Y]
            polyY = realizations[Y]
            total_pairs += 1

            # Compute XY
            XY = defaultdict(Fraction)
            for wX, cX in polyX.items():
                for wY, cY in polyY.items():
                    res = normal_order_deformed_word(wX + wY)
                    for k, v in res.items():
                        XY[k] += cX * cY * v

            # Compute YX
            YX = defaultdict(Fraction)
            for wY, cY in polyY.items():
                for wX, cX in polyX.items():
                    res = normal_order_deformed_word(wY + wX)
                    for k, v in res.items():
                        YX[k] += cY * cX * v

            sign_XY = -1 if (pX * pY) % 2 == 1 else 1

            # [X, Y]~ = XY - sign_XY * YX
            bracket = defaultdict(Fraction)
            for k, v in XY.items():
                bracket[k] += v
            for k, v in YX.items():
                bracket[k] -= sign_XY * v

            for (w, param), coeff in bracket.items():
                if coeff == 0: continue
                if param is not None:
                    # Order 1 in kappa
                    if len(w) > 2:
                        print(f"Non-quadratic order 1 term for ({X}, {Y}): {w}, param={param}, coeff={coeff}")
                        non_quad_terms += 1

    print(f"Finished n={n}: Total pairs={total_pairs}, Non-quadratic order 1 terms={non_quad_terms}")

test_n(1)
