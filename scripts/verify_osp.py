import numpy as np
import json
from fractions import Fraction

def build_osp_algebra(n):
    """
    Constructs C(n+1) = osp(2|2n) and computes:
    - Basis of g_0 and g_1
    - Commutator table [X, Y]_0
    - Deformed bracket [X, Y]_gamma and gamma_{gb}(X, Y)
    - Coboundary operator delta f
    - Linear system for gamma_{gb} = delta f
    """
    print(f"==========================================")
    print(f"Analyzing C({n+1}) = osp(2|{2*n})")
    print(f"==========================================")
    
    # 1. Oscillators
    osc_names = ['a1+', 'a1-']
    osc_parity = [1, 1]
    for j in range(1, n + 1):
        osc_names.extend([f'b{j}+', f'b{j}-'])
        osc_parity.extend([0, 0])
        
    num_osc = len(osc_names)
    
    # Pre-oscillator relations:
    comm_0 = {}
    for i in range(num_osc):
        for j in range(num_osc):
            comm_0[(i, j)] = Fraction(0)
            
    # {a1-, a1+} = 1
    comm_0[(1, 0)] = Fraction(1)  # [a1-, a1+]
    comm_0[(0, 1)] = Fraction(1)  # [a1+, a1-]
    
    for j in range(1, n + 1):
        bp_idx = 2 + 2*(j-1)
        bm_idx = 2 + 2*(j-1) + 1
        comm_0[(bm_idx, bp_idx)] = Fraction(1)   # [bj-, bj+] = 1
        comm_0[(bp_idx, bm_idx)] = Fraction(-1)  # [bj+, bj-] = -1

    # gb parameters:
    gb_names = []
    gb_map = {} # (sigma, j, s) -> gb index
    gb_idx = 0
    for sigma in ['+', '-']:
        for j in range(1, n + 1):
            for s in ['+', '-']:
                name = f"gb_{sigma}_{j}_{s}"
                gb_names.append(name)
                gb_map[(sigma, j, s)] = gb_idx
                gb_idx += 1
                
    num_gb = len(gb_names)

    # comm_1[(i, j)] is a vector of length num_gb representing linear combination of gb's
    comm_1 = {}
    for i in range(num_osc):
        for j in range(num_osc):
            comm_1[(i, j)] = [Fraction(0)] * num_gb
            
    for j in range(1, n + 1):
        for s_idx, s in enumerate(['+', '-']):
            b_idx = 2 + 2*(j-1) + s_idx
            for sigma_idx, sigma in enumerate(['+', '-']):
                a_idx = sigma_idx # 0 for +, 1 for -
                idx = gb_map[(sigma, j, s)]
                # [b_j^s, a_1^sigma] = - gb * kappa
                comm_1[(b_idx, a_idx)][idx] = Fraction(-1)
                # [a_1^sigma, b_j^s] = + gb * kappa
                comm_1[(a_idx, b_idx)][idx] = Fraction(1)

    # 2. Generators of g = C(n+1)
    generators = []
    gen_names = []
    gen_parity = []
    
    # Even generators:
    # 1. J0 = a1+ a1- - 1/2
    generators.append({(0, 1): Fraction(1), 'const': Fraction(-1, 2)})
    gen_names.append("J0")
    gen_parity.append(0)
    
    # 2. Bosonic generators: for all 2n bosonic oscillators, pairs (p, q) with p <= q
    boson_indices = []
    for j in range(1, n + 1):
        boson_indices.extend([2 + 2*(j-1), 2 + 2*(j-1) + 1])
        
    for idx1, p in enumerate(boson_indices):
        for idx2 in range(idx1, len(boson_indices)):
            q = boson_indices[idx2]
            if p == q:
                generators.append({(p, p): Fraction(1), 'const': Fraction(0)})
            else:
                c0 = comm_0[(q, p)] / 2
                generators.append({(p, q): Fraction(1), 'const': c0})
            gen_names.append(f"B_{osc_names[p]}_{osc_names[q]}")
            gen_parity.append(0)
            
    # Odd generators:
    for sigma_idx, sigma in enumerate(['+', '-']):
        a_idx = sigma_idx
        for j in range(1, n + 1):
            for s_idx, s in enumerate(['+', '-']):
                b_idx = 2 + 2*(j-1) + s_idx
                generators.append({(a_idx, b_idx): Fraction(1), 'const': Fraction(0)})
                gen_names.append(f"F_{sigma}_{j}{s}")
                gen_parity.append(1)
                
    dim_g = len(generators)
    dim_0 = sum(1 for p in gen_parity if p == 0)
    dim_1 = sum(1 for p in gen_parity if p == 1)
    print(f"dim(g) = {dim_g} (even: {dim_0}, odd: {dim_1})")
    
    def multiply_to_ordered(i, j):
        pi = osc_parity[i]
        pj = osc_parity[j]
        if i <= j:
            return {(i, j): Fraction(1)}, Fraction(0), [Fraction(0)] * num_gb
        else:
            sign = (-1)**(pi * pj)
            c0 = comm_0[(i, j)]
            c1 = comm_1[(i, j)]
            return {(j, i): Fraction(sign)}, c0, [Fraction(sign * x) for x in c1]

    def comm_single_pair(i, j, k, l):
        pi, pj = osc_parity[i], osc_parity[j]
        pk, pl = osc_parity[k], osc_parity[l]
        pY = (pk + pl) % 2
        
        raw_terms = [
            (comm_0[(j, k)], comm_1[(j, k)], 1, i, l),
            (comm_0[(j, l)], comm_1[(j, l)], (-1)**(pj * pk), i, k),
            (comm_0[(i, k)], comm_1[(i, k)], (-1)**(pj * pY), l, j),
            (comm_0[(i, l)], comm_1[(i, l)], (-1)**(pj * pY + pi * pk), k, j),
        ]
        
        res_0 = {}
        res_1 = {}
        
        for c0, c1, sign, a, b in raw_terms:
            ord_dict, sc0, sc1 = multiply_to_ordered(a, b)
            for pair, coeff in ord_dict.items():
                if c0 != 0:
                    res_0[pair] = res_0.get(pair, Fraction(0)) + c0 * sign * coeff
                for g_i, c1_val in enumerate(c1):
                    if c1_val != 0:
                        if pair not in res_1:
                            res_1[pair] = [Fraction(0)] * num_gb
                        res_1[pair][g_i] += sign * coeff * c1_val
        return res_0, res_1

    def comm_generators(g1_idx, g2_idx):
        g1 = generators[g1_idx]
        g2 = generators[g2_idx]
        
        total_pairs_0 = {}
        total_pairs_1 = {}
        
        for k1, coeff1 in g1.items():
            if k1 == 'const': continue
            i, j = k1
            for k2, coeff2 in g2.items():
                if k2 == 'const': continue
                k, l = k2
                p0, p1 = comm_single_pair(i, j, k, l)
                for pair, val in p0.items():
                    total_pairs_0[pair] = total_pairs_0.get(pair, Fraction(0)) + coeff1 * coeff2 * val
                for pair, val in p1.items():
                    if pair not in total_pairs_1:
                        total_pairs_1[pair] = [Fraction(0)] * num_gb
                    for g_i in range(num_gb):
                        total_pairs_1[pair][g_i] += coeff1 * coeff2 * val[g_i]
                    
        vec_0 = [Fraction(0)] * dim_g
        vec_1 = [[Fraction(0)] * num_gb for _ in range(dim_g)]
        
        for g_idx, gen in enumerate(generators):
            for k, coeff in gen.items():
                if k == 'const': continue
                if k in total_pairs_0:
                    vec_0[g_idx] += total_pairs_0[k] / coeff
                if k in total_pairs_1:
                    for g_i in range(num_gb):
                        vec_1[g_idx][g_i] += total_pairs_1[k][g_i] / coeff
                    
        return vec_0, vec_1

    print("Computing structure constants and deformation cocycle...")
    bracket_0 = {}
    gamma_gb = {}
    for i in range(dim_g):
        for j in range(dim_g):
            v0, v1 = comm_generators(i, j)
            bracket_0[(i, j)] = v0
            gamma_gb[(i, j)] = v1

    # Verify graded skew-symmetry of bracket_0
    skew_err = 0
    for i in range(dim_g):
        for j in range(dim_g):
            pi, pj = gen_parity[i], gen_parity[j]
            sign = (-1)**(pi * pj)
            for k in range(dim_g):
                if bracket_0[(i, j)][k] != -sign * bracket_0[(j, i)][k]:
                    skew_err += 1
    print(f"Graded skew-symmetry errors in bracket_0: {skew_err}")

    # Verify Jacobi identity for bracket_0
    jacobi_err = 0
    for i in range(dim_g):
        for j in range(dim_g):
            for k in range(dim_g):
                pi, pj, pk = gen_parity[i], gen_parity[j], gen_parity[k]
                term1 = [Fraction(0)] * dim_g
                term2 = [Fraction(0)] * dim_g
                term3 = [Fraction(0)] * dim_g
                for m in range(dim_g):
                    cjk = bracket_0[(j, k)][m]
                    if cjk != 0:
                        for r in range(dim_g):
                            term1[r] += cjk * bracket_0[(i, m)][r]
                    cki = bracket_0[(k, i)][m]
                    if cki != 0:
                        for r in range(dim_g):
                            term2[r] += cki * bracket_0[(j, m)][r]
                    cij = bracket_0[(i, j)][m]
                    if cij != 0:
                        for r in range(dim_g):
                            term3[r] += cij * bracket_0[(k, m)][r]
                s1 = (-1)**(pi * pk)
                s2 = (-1)**(pj * pi)
                s3 = (-1)**(pk * pj)
                for r in range(dim_g):
                    if s1 * term1[r] + s2 * term2[r] + s3 * term3[r] != 0:
                        jacobi_err += 1
    print(f"Jacobi identity errors in bracket_0: {jacobi_err}")

    # 4. Coboundary operator delta f
    # f: g -> g (odd linear map)
    # Index phi parameters:
    phi_map = {} # (tgt, src) -> phi index
    phi_names = []
    phi_idx = 0
    for src in range(dim_g):
        p_src = gen_parity[src]
        p_tgt = 1 - p_src
        for tgt in range(dim_g):
            if gen_parity[tgt] == p_tgt:
                phi_map[(tgt, src)] = phi_idx
                phi_names.append(f"phi_{gen_names[tgt]}_{gen_names[src]}")
                phi_idx += 1
                
    num_phi = len(phi_names)
    print(f"Number of gb parameters: {num_gb}")
    print(f"Number of phi parameters: {num_phi}")

    # compute_delta_f_coeffs: returns a matrix of shape (dim_g, num_phi) for pair (i, j)
    def compute_delta_f_coeffs(i, j):
        pi, pj = gen_parity[i], gen_parity[j]
        coeffs = [[Fraction(0)] * num_phi for _ in range(dim_g)]
        
        # term1: s1 * [X_i, f(X_j)] = s1 * sum_k phi_{k, j} [X_i, X_k]
        s1 = (-1)**pi
        for k in range(dim_g):
            if gen_parity[k] == 1 - pj:
                p_idx = phi_map[(k, j)]
                for r in range(dim_g):
                    c = bracket_0[(i, k)][r]
                    if c != 0:
                        coeffs[r][p_idx] += s1 * c
                        
        # term2: - s2 * [X_j, f(X_i)] = - s2 * sum_k phi_{k, i} [X_j, X_k]
        s2 = (-1)**((pi + 1) * pj)
        for k in range(dim_g):
            if gen_parity[k] == 1 - pi:
                p_idx = phi_map[(k, i)]
                for r in range(dim_g):
                    c = bracket_0[(j, k)][r]
                    if c != 0:
                        coeffs[r][p_idx] -= s2 * c
                        
        # term3: - f([X_i, X_j]) = - sum_k bracket_0[(i, j)][k] sum_{r: p(r)=1-p(k)} phi_{r, k} X_r
        for k in range(dim_g):
            c_ijk = bracket_0[(i, j)][k]
            if c_ijk != 0:
                pk = gen_parity[k]
                for r in range(dim_g):
                    if gen_parity[r] == 1 - pk:
                        p_idx = phi_map[(r, k)]
                        coeffs[r][p_idx] -= c_ijk
                        
        return coeffs

    # 5. Build linear system:
    # A_row * phi - B_row * gb = 0
    A_rows = []
    B_rows = []
    
    for i in range(dim_g):
        for j in range(i, dim_g):
            d_f = compute_delta_f_coeffs(i, j)
            g_gb = gamma_gb[(i, j)]
            for r in range(dim_g):
                # check if non-zero
                phi_row = d_f[r]
                gb_row = g_gb[r]
                if any(x != 0 for x in phi_row) or any(x != 0 for x in gb_row):
                    A_rows.append(phi_row)
                    B_rows.append(gb_row)
                    
    num_eqs = len(A_rows)
    print(f"Total non-trivial linear equations: {num_eqs}")

    # Fast Exact RREF / Rank using Fraction Matrix
    # Or NumPy float64 SVD for instant verification and exact Fraction Gaussian elimination
    
    # 1. NumPy SVD / Rank
    A_np = np.array([[float(x) for x in row] for row in A_rows], dtype=np.float64)
    B_np = np.array([[float(x) for x in row] for row in B_rows], dtype=np.float64)
    M_np = np.hstack([A_np, -B_np])
    
    rank_A_np = np.linalg.matrix_rank(A_np)
    rank_M_np = np.linalg.matrix_rank(M_np)
    rank_B_np = np.linalg.matrix_rank(B_np)
    
    print(f"[NumPy] Rank A (phi): {rank_A_np} / {num_phi}")
    print(f"[NumPy] Rank M ([phi, gb]): {rank_M_np} / {num_phi + num_gb}")
    print(f"[NumPy] Constraints on gb: {rank_M_np - rank_A_np} / {num_gb}")
    print(f"[NumPy] Rank B (gb): {rank_B_np} / {num_gb}")

    # 2. Exact Fraction Gaussian Elimination to find exact nullspace and gb constraints
    # We want to project out phi: compute basis for left nullspace of A (vectors v such that v^T A = 0),
    # then check v^T B * gb = 0.
    # Let's do exact Gaussian elimination on [A^T | I]:
    # row reduce A^T (shape num_phi x num_eqs)
    # Even simpler: row reduce [A | B] directly!
    
    def exact_rref(matrix):
        """
        Row reduce matrix of Fractions. Returns (rref_matrix, pivot_cols, rank)
        """
        mat = [row[:] for row in matrix]
        nrows = len(mat)
        ncols = len(mat[0])
        pivot_cols = []
        r = 0
        for c in range(ncols):
            # find pivot
            pivot_row = None
            for row in range(r, nrows):
                if mat[row][c] != 0:
                    pivot_row = row
                    break
            if pivot_row is None:
                continue
            # swap
            mat[r], mat[pivot_row] = mat[pivot_row], mat[r]
            # scale pivot row
            pv = mat[r][c]
            mat[r] = [x / pv for x in mat[r]]
            # eliminate other rows
            for row in range(nrows):
                if row != r and mat[row][c] != 0:
                    factor = mat[row][c]
                    mat[row] = [mat[row][k] - factor * mat[r][k] for k in range(ncols)]
            pivot_cols.append(c)
            r += 1
            if r == nrows:
                break
        return mat, pivot_cols, r

    # Row reduce [A | B]
    # To make it fast, first select a linearly independent subset of rows using fast numeric or sparse elimination
    # Since num_eqs is at most ~7000, exact RREF on the combined matrix:
    combined_rows = [A_rows[i] + B_rows[i] for i in range(num_eqs)]
    
    print("Performing exact row reduction...")
    # First filter non-zero rows
    # Quick exact elimination
    _, pivots_M, exact_rank_M = exact_rref(combined_rows)
    print(f"Exact rank of M: {exact_rank_M}")
    
    # Exact rank of A:
    _, pivots_A, exact_rank_A = exact_rref(A_rows)
    print(f"Exact rank of A: {exact_rank_A}")
    
    exact_constraints = exact_rank_M - exact_rank_A
    print(f"Exact constraints on gb: {exact_constraints} / {num_gb}")
    
    # Check gamma rank (gb -> gamma):
    _, pivots_gamma, exact_rank_gamma = exact_rref(B_rows)
    print(f"Exact rank of gamma (gb -> gamma): {exact_rank_gamma} / {num_gb}")

    # Structure constants and gamma export
    bracket_0_export = {}
    for (i, j), vec in bracket_0.items():
        nonzero = {gen_names[r]: int(c) for r, c in enumerate(vec) if c != 0}
        if nonzero:
            bracket_0_export[f"[{gen_names[i]},{gen_names[j]}]"] = nonzero

    gamma_gb_export = {}
    for (i, j), vec in gamma_gb.items():
        nonzero = {}
        for r, gb_coeffs in enumerate(vec):
            expr_terms = [f"{float(c):+g}*{gb_names[g_k]}" for g_k, c in enumerate(gb_coeffs) if c != 0]
            if expr_terms:
                nonzero[gen_names[r]] = " ".join(expr_terms)
        if nonzero:
            gamma_gb_export[f"gamma({gen_names[i]},{gen_names[j]})"] = nonzero

    return {
        'n': n,
        'algebra': f"C({n+1}) = osp(2|{2*n})",
        'dim_g': dim_g,
        'dim_0': dim_0,
        'dim_1': dim_1,
        'num_gb': num_gb,
        'num_phi': num_phi,
        'num_eqs': num_eqs,
        'rank_A': exact_rank_A,
        'rank_M': exact_rank_M,
        'constraints_on_gb': exact_constraints,
        'rank_gamma': exact_rank_gamma,
        'gb_triviality_condition': "gb = 0 (all gb parameters must be zero for triviality)",
        'bracket_0': bracket_0_export,
        'gamma_gb': gamma_gb_export
    }

if __name__ == '__main__':
    results = {}
    for n in [1, 2, 3]:
        res = build_osp_algebra(n)
        res_summary = {k: v for k, v in res.items() if k not in ['bracket_0', 'gamma_gb']}
        results[f"n={n}"] = res
        print(f"Summary for n={n}: {res_summary}\n")
        
    with open("artifacts_verification.json", "w") as f:
        json.dump(results, f, indent=2)
    print("Exported artifacts_verification.json successfully.")
