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
                            next_dict[(w[:i] + w[i+2:], p_name)] += -coeff
                    else:
                        raise ValueError(f"Unhandled pair: {o1}, {o2}")
                    break
            if not found:
                next_dict[(w, param)] += coeff
        if all_sorted:
            return {k: v for k, v in current.items() if v != 0}
        current = next_dict

def test_gamma_from_normal_ordering(n=1):
    even_basis, odd_basis, realizations, _, _, parity = get_generators(n)
    all_basis = even_basis + odd_basis

    # Invert basis realizations: map normalized word -> linear combination of basis elements
    # Every basis element except Cartans is a single word!
    # For Cartans:
    # H_1: a_1^+ a_1^- + b_1^+ b_1^-
    # H_2: -b_1^+ b_1^- - 1/2
    # So b_1^+ b_1^- = - H_2 - 1/2
    # a_1^+ a_1^- = H_1 - b_1^+ b_1^- = H_1 + H_2 + 1/2
    
    # Let's build exact linear solver: poly -> basis coords
    # Words in realizations:
    all_words = set()
    for b in all_basis:
        for w in realizations[b].keys():
            all_words.add(w)
    
    # We can form a matrix word x basis
    word_list = sorted(list(all_words))
    mat = []
    for w in word_list:
        row = []
        for b in all_basis:
            row.append(realizations[b].get(w, Fraction(0)))
        mat.append(row)
    
    M = sp.Matrix(mat) # shape (len(word_list), len(all_basis))
    
    # Compute brackets
    # gamma_dict[(X, Y, Z)] = expr in gb
    gamma_dict = defaultdict(lambda: defaultdict(Fraction))
    
    for idx_X, X in enumerate(all_basis):
        pX = parity[X]
        polyX = realizations[X]
        for idx_Y, Y in enumerate(all_basis):
            pY = parity[Y]
            polyY = realizations[Y]

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

            bracket = defaultdict(Fraction)
            for k, v in XY.items():
                bracket[k] += v
            for k, v in YX.items():
                bracket[k] -= sign_XY * v

            # Collect terms by param
            by_param = defaultdict(lambda: defaultdict(Fraction))
            for (w, param), coeff in bracket.items():
                if coeff == 0 or param is None: continue
                by_param[param][w] += coeff

            for param, poly in by_param.items():
                # poly is {w: coeff}. Solve poly = sum c_Z Z
                # Check if poly is in span(basis)
                rhs = sp.Matrix([poly.get(w, Fraction(0)) for w in word_list])
                # M * coords = rhs
                sol, params = M.gauss_jordan_solve(rhs)
                for idx_Z, Z in enumerate(all_basis):
                    val = sol[idx_Z]
                    if val != 0:
                        gamma_dict[(X, Y, Z)][param] += Fraction(val)

    print(f"Generated gamma entries: {len(gamma_dict)}")
    print("Sample entries:")
    for (X, Y, Z), pdict in sorted(list(gamma_dict.items()))[:10]:
        print(f"gamma({X}, {Y})^{Z} = {dict(pdict)}")

    # Now verify Super-Jacobi identity on this gamma!
    # Load c_base
    c_base = defaultdict(Fraction)
    with open(f"{REPO_ROOT}/data/C_{n}_structure.json") as f: s1 = json.load(f)
    for e in s1["structure_constants"]:
        c_base[(e["X"], e["Y"], e["Z"])] = Fraction(e["coeff"])

    # Notice: In [X, Y]_gamma = [X, Y]_0 + kappa * gamma(X, Y)
    # What is the relation between kappa and gamma?
    # In U(A), [X, Y]~ = [X, Y]_0 + sum_p (p * kappa) * gamma_p(X, Y)
    # Since p is odd and kappa is odd, (p * kappa) = - kappa * p.
    # If [X, Y]_gamma = [X, Y]_0 + kappa * sum_p p * gamma_p(X, Y),
    # there might be a minus sign!
    # Let's check Jacobi with both signs!

    for sign_factor in [1, -1]:
        print(f"\n--- Checking Jacobi with sign_factor={sign_factor} ---")
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

                    res_W = defaultdict(lambda: defaultdict(Fraction))
                    for A, pA, B, pB, C, pC, sign_cyc in triples:
                        # [A, gamma(B, C)]_0
                        # Note: kappa has parity 1. When A moves past kappa: (-1)^pA
                        sign_kappa = (-1)**pA
                        for W in all_basis:
                            for param, coeff in gamma_dict.get((B, C, W), {}).items():
                                for target in all_basis:
                                    c = c_base.get((A, W, target), Fraction(0))
                                    if c != 0:
                                        res_W[target][param] += sign_cyc * sign_kappa * (sign_factor * coeff) * c

                        # gamma(A, [B, C]_0)
                        for W in all_basis:
                            c_BC_W = c_base.get((B, C, W), Fraction(0))
                            if c_BC_W != 0:
                                for target in all_basis:
                                    for param, coeff in gamma_dict.get((A, W, target), {}).items():
                                        res_W[target][param] += sign_cyc * c_BC_W * (sign_factor * coeff)

                    for target, pdict in res_W.items():
                        for param, val in pdict.items():
                            if val != 0:
                                violations += 1
                                if violations <= 5:
                                    print(f"Violation ({X}, {Y}, {Z}) -> {target}, {param}: {val}")
                                break

        print(f"Total triples: {total_triples}, Violations: {violations}")

test_gamma_from_normal_ordering(1)
