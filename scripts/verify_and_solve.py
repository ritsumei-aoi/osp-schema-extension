"""
Verify structure constants via Jacobi identity and compute explicit
coboundary solutions f for given gb parameters.
"""

import numpy as np
import json
import os

def compute_full_analysis(n, verbose=False):
    num_osc = 2 + 2 * n

    def parity(i):
        return 1 if i < 2 else 0

    def bracket1(i, j):
        if i == 0 and j == 1: return 1
        if i == 1 and j == 0: return 1
        if i >= 2 and j >= 2:
            ki, si = divmod(i - 2, 2)
            kj, sj = divmod(j - 2, 2)
            if ki == kj:
                if si == 1 and sj == 0: return 1
                if si == 0 and sj == 1: return -1
        return 0

    def deformation_info(i, j):
        if i >= 2 and j < 2:
            k, s = divmod(i - 2, 2)
            sigma = j
            gb_idx = sigma * (2 * n) + k * 2 + s
            return (gb_idx, -1)
        if i < 2 and j >= 2:
            sigma = i
            k, s = divmod(j - 2, 2)
            gb_idx = sigma * (2 * n) + k * 2 + s
            return (gb_idx, +1)
        return None

    generators = []
    gen_names = []
    gen_parity = []
    gen_scalar = []

    generators.append([(1.0, 0, 1), (1.0, 2, 3)])
    gen_names.append('H_1')
    gen_parity.append(0)
    gen_scalar.append(0.0)

    for k in range(2, n + 1):
        generators.append([(1.0, 2*(k-1), 2*(k-1)+1), (-1.0, 2*k, 2*k+1)])
        gen_names.append(f'H_{k}')
        gen_parity.append(0)
        gen_scalar.append(0.0)

    generators.append([(-1.0, 2*n, 2*n+1)])
    gen_names.append(f'H_{n+1}')
    gen_parity.append(0)
    gen_scalar.append(-0.5)

    for k in range(1, n+1):
        for l in range(1, n+1):
            if k != l:
                generators.append([(1.0, 2*k, 2*l+1)])
                gen_names.append(f'E_{{d{k}-d{l}}}')
                gen_parity.append(0)
                gen_scalar.append(0.0)

    for k in range(1, n+1):
        for l in range(k+1, n+1):
            generators.append([(1.0, 2*k, 2*l)])
            gen_names.append(f'E_{{d{k}+d{l}}}')
            gen_parity.append(0)
            gen_scalar.append(0.0)

    for k in range(1, n+1):
        for l in range(k+1, n+1):
            generators.append([(1.0, 2*k+1, 2*l+1)])
            gen_names.append(f'E_{{-d{k}-d{l}}}')
            gen_parity.append(0)
            gen_scalar.append(0.0)

    for k in range(1, n+1):
        generators.append([(0.5, 2*k, 2*k)])
        gen_names.append(f'E_{{2d{k}}}')
        gen_parity.append(0)
        gen_scalar.append(0.0)

    for k in range(1, n+1):
        generators.append([(0.5, 2*k+1, 2*k+1)])
        gen_names.append(f'E_{{-2d{k}}}')
        gen_parity.append(0)
        gen_scalar.append(0.0)

    for k in range(1, n+1):
        generators.append([(1.0, 0, 2*k)])
        gen_names.append(f'E_{{e+d{k}}}')
        gen_parity.append(1)
        gen_scalar.append(0.0)

    for k in range(1, n+1):
        generators.append([(1.0, 0, 2*k+1)])
        gen_names.append(f'E_{{e-d{k}}}')
        gen_parity.append(1)
        gen_scalar.append(0.0)

    for k in range(1, n+1):
        generators.append([(1.0, 1, 2*k)])
        gen_names.append(f'E_{{-e+d{k}}}')
        gen_parity.append(1)
        gen_scalar.append(0.0)

    for k in range(1, n+1):
        generators.append([(1.0, 1, 2*k+1)])
        gen_names.append(f'E_{{-e-d{k}}}')
        gen_parity.append(1)
        gen_scalar.append(0.0)

    dim_g = len(generators)

    monomial_list = []
    monomial_index = {}
    for i in range(num_osc):
        for j in range(i, num_osc):
            if i == j and parity(i) == 1:
                continue
            monomial_list.append((i, j))
            monomial_index[(i, j)] = len(monomial_list) - 1

    num_mono = len(monomial_list)
    assert num_mono == dim_g

    gen_mono = np.zeros((dim_g, num_mono))
    actual_scalar = list(gen_scalar)  # copy

    for alpha in range(dim_g):
        for coeff, i, j in generators[alpha]:
            if i > j:
                sign = (-1) ** (parity(i) * parity(j))
                idx = monomial_index.get((j, i))
                if idx is not None:
                    gen_mono[alpha, idx] += coeff * sign
                actual_scalar[alpha] += coeff * bracket1(i, j)
            elif i == j:
                idx = monomial_index.get((i, j))
                if idx is not None:
                    gen_mono[alpha, idx] += coeff
            else:
                idx = monomial_index.get((i, j))
                if idx is not None:
                    gen_mono[alpha, idx] += coeff

    gen_mono_inv = np.linalg.inv(gen_mono)

    def monomial_to_gen(i, j):
        gen_coeffs = np.zeros(dim_g)
        scalar = 0.0
        if i == j and parity(i) == 1:
            return gen_coeffs, 0.0
        if i <= j:
            idx = monomial_index.get((i, j))
            if idx is not None:
                gen_coeffs = gen_mono_inv[idx, :].copy()
        else:
            sign = (-1) ** (parity(i) * parity(j))
            scalar = bracket1(i, j)
            idx = monomial_index.get((j, i))
            if idx is not None:
                gen_coeffs = sign * gen_mono_inv[idx, :].copy()
        return gen_coeffs, scalar

    # Structure constants
    struct_const = np.zeros((dim_g, dim_g, dim_g))

    for i_gen in range(dim_g):
        for j_gen in range(dim_g):
            total_gen = np.zeros(dim_g)
            for coeff_i, Ai, Bi in generators[i_gen]:
                for coeff_j, Cj, Dj in generators[j_gen]:
                    pA, pB, pC, pD = parity(Ai), parity(Bi), parity(Cj), parity(Dj)
                    terms = []
                    bc = bracket1(Bi, Cj)
                    if bc != 0:
                        g, s = monomial_to_gen(Ai, Dj)
                        terms.append((bc, g, s))
                    bd = bracket1(Bi, Dj)
                    if bd != 0:
                        sign2 = (-1) ** (pB * pC)
                        g, s = monomial_to_gen(Ai, Cj)
                        terms.append((bd * sign2, g, s))
                    ac = bracket1(Ai, Cj)
                    if ac != 0:
                        sign3 = (-1) ** (pB * (pC + pD))
                        g, s = monomial_to_gen(Dj, Bi)
                        terms.append((ac * sign3, g, s))
                    ad = bracket1(Ai, Dj)
                    if ad != 0:
                        sign4 = (-1) ** (pB * (pC + pD) + pA * pC)
                        g, s = monomial_to_gen(Cj, Bi)
                        terms.append((ad * sign4, g, s))
                    for val, g, s in terms:
                        total_gen += coeff_i * coeff_j * val * g
            struct_const[i_gen, j_gen, :] = total_gen

    # Corrected Jacobi check
    jacobi_violations = 0
    max_jacobi_error = 0.0
    for i_gen in range(dim_g):
        for j_gen in range(dim_g):
            for k_gen in range(dim_g):
                pi, pj, pk = gen_parity[i_gen], gen_parity[j_gen], gen_parity[k_gen]
                # [e_i, [e_j, e_k]]_m = sum_l c_{jk}^l c_{il}^m
                jk = struct_const[j_gen, k_gen]  # vector of c_{jk}^l
                term1_vec = np.zeros(dim_g)
                for l in range(dim_g):
                    if abs(jk[l]) > 1e-12:
                        term1_vec += jk[l] * struct_const[i_gen, l]
                term1 = (-1) ** (pi * pk) * term1_vec

                ki = struct_const[k_gen, i_gen]
                term2_vec = np.zeros(dim_g)
                for l in range(dim_g):
                    if abs(ki[l]) > 1e-12:
                        term2_vec += ki[l] * struct_const[j_gen, l]
                term2 = (-1) ** (pj * pi) * term2_vec

                ij = struct_const[i_gen, j_gen]
                term3_vec = np.zeros(dim_g)
                for l in range(dim_g):
                    if abs(ij[l]) > 1e-12:
                        term3_vec += ij[l] * struct_const[k_gen, l]
                term3 = (-1) ** (pk * pj) * term3_vec

                jacobi = term1 + term2 + term3
                err = np.max(np.abs(jacobi))
                max_jacobi_error = max(max_jacobi_error, err)
                if err > 1e-8:
                    jacobi_violations += 1
                    if verbose and jacobi_violations <= 3:
                        print(f"Jacobi violation: ({gen_names[i_gen]},{gen_names[j_gen]},{gen_names[k_gen]})")
                        print(f"  error = {err}")

    print(f"\n=== C({n+1}) = osp(2|{2*n}) ===")
    print(f"dim(g) = {dim_g}")
    print(f"Jacobi violations: {jacobi_violations}, max error: {max_jacobi_error:.2e}")

    # Gamma_gb computation
    num_gb = 4 * n
    gamma_gb = np.zeros((dim_g, dim_g, dim_g, num_gb))

    for i_gen in range(dim_g):
        for j_gen in range(dim_g):
            for coeff_i, Ai, Bi in generators[i_gen]:
                for coeff_j, Cj, Dj in generators[j_gen]:
                    pA, pB, pC, pD = parity(Ai), parity(Bi), parity(Cj), parity(Dj)

                    info = deformation_info(Bi, Cj)
                    if info is not None:
                        gb_idx, def_sign = info
                        kappa_sign = (-1) ** pA
                        g, s = monomial_to_gen(Ai, Dj)
                        gamma_gb[i_gen, j_gen, :, gb_idx] += coeff_i * coeff_j * def_sign * kappa_sign * g

                    info = deformation_info(Bi, Dj)
                    if info is not None:
                        gb_idx, def_sign = info
                        total_sign = (-1) ** (pB * pC) * def_sign * (-1) ** (pA + pC)
                        g, s = monomial_to_gen(Ai, Cj)
                        gamma_gb[i_gen, j_gen, :, gb_idx] += coeff_i * coeff_j * total_sign * g

                    info = deformation_info(Ai, Cj)
                    if info is not None:
                        gb_idx, def_sign = info
                        total_sign = (-1) ** (pB * (pC + pD)) * def_sign
                        g, s = monomial_to_gen(Dj, Bi)
                        gamma_gb[i_gen, j_gen, :, gb_idx] += coeff_i * coeff_j * total_sign * g

                    info = deformation_info(Ai, Dj)
                    if info is not None:
                        gb_idx, def_sign = info
                        total_sign = (-1) ** (pB * (pC + pD) + pA * pC + pC) * def_sign
                        g, s = monomial_to_gen(Cj, Bi)
                        gamma_gb[i_gen, j_gen, :, gb_idx] += coeff_i * coeff_j * total_sign * g

    # Build coboundary and gamma matrices
    f_params = []
    f_param_index = {}
    for l in range(dim_g):
        for k in range(dim_g):
            if gen_parity[k] != gen_parity[l]:
                f_param_index[(k, l)] = len(f_params)
                f_params.append((k, l))
    num_f = len(f_params)

    equations = []
    for i_gen in range(dim_g):
        for j_gen in range(i_gen, dim_g):
            if i_gen == j_gen and gen_parity[i_gen] == 0:
                continue
            for m in range(dim_g):
                equations.append((i_gen, j_gen, m))
    num_eq = len(equations)

    A_mat = np.zeros((num_eq, num_f))
    B_mat = np.zeros((num_eq, num_gb))

    for eq_idx, (i_gen, j_gen, m) in enumerate(equations):
        pi, pj = gen_parity[i_gen], gen_parity[j_gen]

        for k in range(dim_g):
            if (k, j_gen) in f_param_index:
                phi_idx = f_param_index[(k, j_gen)]
                A_mat[eq_idx, phi_idx] += (-1) ** pi * struct_const[i_gen, k, m]

        for k in range(dim_g):
            if (k, i_gen) in f_param_index:
                phi_idx = f_param_index[(k, i_gen)]
                A_mat[eq_idx, phi_idx] -= (-1) ** ((pi + 1) * pj) * struct_const[j_gen, k, m]

        for l in range(dim_g):
            if (m, l) in f_param_index:
                phi_idx = f_param_index[(m, l)]
                A_mat[eq_idx, phi_idx] -= struct_const[i_gen, j_gen, l]

        for p in range(num_gb):
            B_mat[eq_idx, p] = gamma_gb[i_gen, j_gen, m, p]

    rank_A = np.linalg.matrix_rank(A_mat, tol=1e-8)
    rank_B = np.linalg.matrix_rank(B_mat, tol=1e-8)
    AB = np.hstack([A_mat, B_mat])
    rank_AB = np.linalg.matrix_rank(AB, tol=1e-8)

    print(f"rank(A) = {rank_A}, rank(B) = {rank_B}, rank([A|B]) = {rank_AB}")
    trivial = (rank_AB == rank_A)
    print(f"All trivial: {trivial}")

    # For each gb parameter, find a specific f solution
    solutions = {}
    for p in range(num_gb):
        rhs = B_mat[:, p]
        if np.max(np.abs(rhs)) < 1e-12:
            solutions[p] = "zero_cocycle"
            continue
        sol, residuals, rank_used, sv = np.linalg.lstsq(A_mat, rhs, rcond=None)
        residual = np.max(np.abs(A_mat @ sol - rhs))
        if residual < 1e-8:
            nonzero = np.nonzero(np.abs(sol) > 1e-10)[0]
            sol_dict = {}
            for idx in nonzero:
                k, l = f_params[idx]
                sol_dict[f"f({gen_names[l]})_coeff_{gen_names[k]}"] = round(float(sol[idx]), 10)
            solutions[p] = {"residual": float(residual), "f_map": sol_dict}
        else:
            solutions[p] = {"residual": float(residual), "status": "no_solution"}

    print(f"\nExplicit solutions for individual gb parameters:")
    for p in range(num_gb):
        sigma = p // (2 * n)
        rem = p % (2 * n)
        k = rem // 2
        s = rem % 2
        sigma_str = '+' if sigma == 0 else '-'
        s_str = '+' if s == 0 else '-'
        gb_name = f"gb(a{sigma_str}, b_{k+1}{s_str})"
        if solutions[p] == "zero_cocycle":
            print(f"  {gb_name}: zero cocycle")
        elif "f_map" in solutions[p]:
            print(f"  {gb_name}: solution found (residual={solutions[p]['residual']:.2e})")
            for key, val in solutions[p]["f_map"].items():
                if abs(val) > 1e-10:
                    print(f"    {key} = {val}")
        else:
            print(f"  {gb_name}: NO SOLUTION (residual={solutions[p]['residual']:.2e})")

    return {
        "n": n,
        "dim_g": dim_g,
        "jacobi_violations": jacobi_violations,
        "max_jacobi_error": float(max_jacobi_error),
        "rank_A": int(rank_A),
        "rank_B": int(rank_B),
        "rank_AB": int(rank_AB),
        "all_trivial": trivial,
        "num_gb": num_gb,
        "num_f": num_f,
        "solutions": {str(k): v for k, v in solutions.items()},
        "gen_names": gen_names,
        "gen_parities": gen_parity,
    }


if __name__ == "__main__":
    all_results = {}
    for n_val in [1, 2, 3]:
        result = compute_full_analysis(n_val, verbose=(n_val == 1))
        all_results[f"C({n_val+1})"] = result

    os.makedirs("data", exist_ok=True)
    with open("data/full_verification.json", "w") as f:
        json.dump(all_results, f, indent=2, default=str)
    print(f"\nFull verification data saved to data/full_verification.json")

    print("\n" + "=" * 60)
    print("FINAL SUMMARY")
    print("=" * 60)
    for key, r in all_results.items():
        jac = "PASS" if r["jacobi_violations"] == 0 else f"FAIL({r['jacobi_violations']})"
        triv = "ALL TRIVIAL" if r["all_trivial"] else "NON-TRIVIAL"
        print(f"{key}: {triv} | Jacobi: {jac} (max err: {r['max_jacobi_error']:.2e})")
        print(f"  dim={r['dim_g']}, #gb={r['num_gb']}, #f={r['num_f']}")
        print(f"  rank(delta)={r['rank_A']}, rank(gamma)={r['rank_B']}, rank(combined)={r['rank_AB']}")
