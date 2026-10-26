import sys
sys.path.append('.')
from src.C_generators import build_c_generators, Monomial, Poly
from src.C_gamma import osc_rank, decompose_mod_K
from collections import defaultdict
from fractions import Fraction
import sympy as sp

def normal_order_word_ua_corrected(word, n, sign_choice=1):
    current_terms = [(word, Fraction(1), False, None)]

    while True:
        next_terms = []
        all_sorted = True
        for w, coeff, is_kap, par in current_terms:
            pair_found = False
            for i in range(len(w) - 1):
                x, y = w[i], w[i + 1]
                rx, ry = osc_rank(x, n), osc_rank(y, n)
                if rx > ry:
                    pair_found = True
                    all_sorted = False
                    pre = w[:i]
                    suf = w[i + 2:]

                    if x == "a_1_m" and y == "a_1_p":
                        next_terms.append((pre + ("a_1_p", "a_1_m") + suf, -coeff, is_kap, par))
                        next_terms.append((pre + suf, coeff, is_kap, par))
                    elif x.startswith("b_") and y.startswith("b_"):
                        px, py = x.split("_"), y.split("_")
                        if px[1] == py[1] and px[2] == "m" and py[2] == "p":
                            next_terms.append((pre + (y, x) + suf, coeff, is_kap, par))
                            next_terms.append((pre + suf, coeff, is_kap, par))
                        else:
                            next_terms.append((pre + (y, x) + suf, coeff, is_kap, par))
                    elif x.startswith("b_") and y.startswith("a_"):
                        next_terms.append((pre + (y, x) + suf, coeff, is_kap, par))
                        if not is_kap:
                            sigma = "p" if "p" in y else "m"
                            px = x.split("_")
                            j, s = px[1], px[2]
                            gb_param = f"gb_a1{sigma}_b{j}{s}"
                            # Koszul sign: move kappa (p=1) to the front past all odd oscillators in pre
                            num_fermions_pre = sum(1 for osc in pre if osc.startswith("a_"))
                            koszul_sign = (-1) ** (num_fermions_pre % 2)
                            next_terms.append((pre + suf, -coeff * sign_choice * koszul_sign, True, gb_param))
                    else:
                        next_terms.append((pre + (y, x) + suf, coeff, is_kap, par))
                    break

            if not pair_found:
                next_terms.append((w, coeff, is_kap, par))

        current_terms = next_terms
        if all_sorted:
            break

    undeff_poly = Poly(n=n)
    def_poly_by_param = defaultdict(lambda: Poly(n=n))

    for w, coeff, is_kap, par in current_terms:
        if w.count("a_1_p") > 1 or w.count("a_1_m") > 1:
            continue
        p_single = Poly.const(coeff, n=n)
        for osc in w:
            p_single = p_single * Poly.from_osc(osc, n)

        if not is_kap:
            undeff_poly = undeff_poly + p_single
        else:
            def_poly_by_param[par] = def_poly_by_param[par] + p_single

    return undeff_poly, def_poly_by_param

def test_corrected_triviality(n):
    data = build_c_generators(n)
    full_basis = data["odd_basis"] + data["even_basis"]
    generators = data["generators"]
    parities = data["parities"]
    dim = len(full_basis)
    name_to_idx = {name: i for i, name in enumerate(full_basis)}
    
    # Structure constants of g
    from src.C_generators import compute_structure_constants
    c_0_list = compute_structure_constants(n, data)
    c_0 = defaultdict(Fraction)
    for e in c_0_list:
        c_0[(name_to_idx[e["X"]], name_to_idx[e["Y"]], name_to_idx[e["Z"]])] = Fraction(e["coeff"])
        
    # Compute gamma structure constants with corrected Koszul sign
    gamma_table = defaultdict(dict)
    param_set = set()
    for X in full_basis:
        poly_X = generators[X]
        pX = parities[X]
        for Y in full_basis:
            poly_Y = generators[Y]
            pY = parities[Y]
            sign_XY = -1 if (pX * pY) % 2 == 1 else 1

            def_res = defaultdict(lambda: Poly(n=n))
            for mX, cX in poly_X.terms.items():
                wX = mX.to_words()
                for mY, cY in poly_Y.terms.items():
                    wY = mY.to_words()
                    c_prod = cX * cY

                    _, d_XY = normal_order_word_ua_corrected(tuple(wX + wY), n)
                    for par, poly in d_XY.items():
                        def_res[par] = def_res[par] + poly * c_prod

                    _, d_YX = normal_order_word_ua_corrected(tuple(wY + wX), n)
                    for par, poly in d_YX.items():
                        def_res[par] = def_res[par] - poly * (c_prod * sign_XY)

            for par, poly in def_res.items():
                param_set.add(par)
                if poly.terms:
                    decomp = decompose_mod_K(poly, full_basis, generators, n)
                    if decomp is None:
                        raise ValueError(f"Decomposition failed for [{X}, {Y}] {par}")
                    for Z, coeff in decomp.items():
                        gamma_table[(name_to_idx[X], name_to_idx[Y], name_to_idx[Z])][par] = coeff

    param_names = sorted(list(param_set))
    param_to_idx = {p: i for i, p in enumerate(param_names)}
    num_params = len(param_names)
    print(f"\n==================== C({n+1}) Corrected Test ====================")
    print(f"num_params = {num_params}")

    # Check 2-cocycle condition: (delta gamma)(X, Y, Z) = 0 for each parameter
    # For a fixed parameter, gamma is an odd 2-cochain.
    # The coboundary of an odd 2-cochain gamma is:
    # (delta gamma)(X, Y, Z) =
    # (-1)^{pX} [X, gamma(Y, Z)] - (-1)^{(pX+1)pY} [Y, gamma(X, Z)] + (-1)^{(pX+pY)pZ + pZ} [Z, gamma(X, Y)]
    # - gamma([X, Y], Z) - (-1)^{pX(pY+pZ)} gamma(Y, [X, Z]) ...
    # Or simply: check if [X, Y]_gamma satisfies super-Jacobi identity to first order in kappa!
    # [X, [Y, Z]_gamma]_gamma + cycl = 0 mod kappa^2
    # The order kappa term is:
    # [X, gamma(Y, Z)]_0 + gamma(X, [Y, Z]_0) with appropriate Koszul signs!
    
    # Let's directly check coboundary solvability: delta(f) = gamma(param)
    f_vars = []
    for j in range(dim):
        for i in range(dim):
            if parities[full_basis[i]] != parities[full_basis[j]]:
                f_vars.append((i, j))
    num_f_vars = len(f_vars)
    f_var_to_col = {v: c for c, v in enumerate(f_vars)}

    eq_rows_coboundary = []
    eq_rows_gamma = []

    for j in range(dim):
        pX = parities[full_basis[j]]
        for k in range(j, dim):
            pY = parities[full_basis[k]]
            for m in range(dim):
                if parities[full_basis[m]] != (pX + pY + 1) % 2:
                    continue

                row_f = [Fraction(0)] * num_f_vars
                row_g = [Fraction(0)] * num_params

                sign1 = -1 if pX == 1 else 1
                for i in range(dim):
                    if (i, k) in f_var_to_col:
                        c_ji_m = c_0.get((j, i, m), 0)
                        if c_ji_m != 0:
                            row_f[f_var_to_col[(i, k)]] += sign1 * c_ji_m

                sign2 = -1 if ((pX + 1) * pY) % 2 == 1 else 1
                for i in range(dim):
                    if (i, j) in f_var_to_col:
                        c_ki_m = c_0.get((k, i, m), 0)
                        if c_ki_m != 0:
                            row_f[f_var_to_col[(i, j)]] -= sign2 * c_ki_m

                for l in range(dim):
                    if (m, l) in f_var_to_col:
                        c_jk_l = c_0.get((j, k, l), 0)
                        if c_jk_l != 0:
                            row_f[f_var_to_col[(m, l)]] -= c_jk_l

                if (j, k, m) in gamma_table:
                    for p_name, c_val in gamma_table[(j, k, m)].items():
                        row_g[param_to_idx[p_name]] = c_val

                if any(x != 0 for x in row_f) or any(x != 0 for x in row_g):
                    eq_rows_coboundary.append(row_f)
                    eq_rows_gamma.append(row_g)

    M_cob = sp.Matrix([[sp.Rational(x.numerator, x.denominator) for x in row] for row in eq_rows_coboundary])
    M_gam = sp.Matrix([[sp.Rational(x.numerator, x.denominator) for x in row] for row in eq_rows_gamma])

    rank_cob = M_cob.rank()
    M_aug = sp.Matrix.hstack(M_cob, M_gam)
    rank_aug = M_aug.rank()
    diff = rank_aug - rank_cob

    print(f"Rank(delta) = {rank_cob}")
    print(f"Rank([delta | gamma]) = {rank_aug}")
    print(f"Difference = {diff}")
    if diff == 0:
        print(">>> ALL GAMMA ARE COBOUNDARIES! THE DEFORMATION IS TRIVIAL! <<<")
        # Solve for the exact map f for each parameter!
        for p_idx, p_name in enumerate(param_names):
            b_col = M_gam[:, p_idx]
            sol, _ = M_cob.gauss_jordan_solve(b_col)
            # Display non-zero components of f
            print(f"\nMap f for {p_name}:")
            for (i, j), col in f_var_to_col.items():
                val = sol[col]
                if val != 0:
                    print(f"  f({full_basis[j]}) = {val} * {full_basis[i]}")

test_corrected_triviality(1)
test_corrected_triviality(2)
