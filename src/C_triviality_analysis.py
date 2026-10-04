import json
import numpy as np

def analyze_triviality(n):
    print(f"\n==================================================")
    print(f"Analyzing Triviality for C({n+1}) (n={n})")
    print(f"==================================================")
    
    # Load files
    with open(f"data/C_{n}_gamma.json") as f:
        data_gamma = json.load(f)
    with open(f"data/C_{n}_evaluated.json") as f:
        data_eval = json.load(f)
    with open(f"data/C_{n}_coboundary.json") as f:
        data_coboundary = json.load(f)
        
    basis_even = data_gamma["basis"]["even"]
    basis_odd = data_gamma["basis"]["odd"]
    basis = basis_odd + basis_even # PBW ordering: odd < even
    parity = data_gamma["parity"]
    dim_g = len(basis)
    
    phi_params = data_coboundary["odd_linear_map_space"]["parameters"]
    phi_to_idx = {p: i for i, p in enumerate(phi_params)}
    dim_phi = len(phi_params)
    
    # Independent 2-cochain pairs:
    # X < Y for all, or X == Y if parity[X] == 1
    independent_pairs = []
    for i, X in enumerate(basis):
        for j in range(i, dim_g):
            Y = basis[j]
            if i == j:
                if parity[X] == 1:
                    independent_pairs.append((X, Y))
            else:
                independent_pairs.append((X, Y))
                
    # Identify all possible 2-cochain components: (X, Y, Z) with (X, Y) independent
    # and parity constraint: p(Z) = (p(X) + p(Y) + 1) % 2
    cochain_components = []
    cochain_to_idx = {}
    for (X, Y) in independent_pairs:
        px, py = parity[X], parity[Y]
        for Z in basis:
            pz = parity[Z]
            if pz == (px + py + 1) % 2:
                cochain_components.append((X, Y, Z))
                cochain_to_idx[(X, Y, Z)] = len(cochain_components) - 1
                    
    num_components = len(cochain_components)
    print(f"Dimension of odd linear maps (dim Hom_1(g, g)): {dim_phi}")
    print(f"Dimension of odd 2-cochains Alt^2(g, g)_1: {num_components}")
    
    # Build Coboundary Matrix A
    # (delta phi)(X, Y)^Z
    A = np.zeros((num_components, dim_phi), dtype=int)
    for term in data_coboundary["coboundary_operator"]["coboundary_coefficients"]:
        X, Y, Z = term["X"], term["Y"], term["Z"]
        idx_X, idx_Y = basis.index(X), basis.index(Y)
        if (X, Y, Z) in cochain_to_idx:
            row = cochain_to_idx[(X, Y, Z)]
            col = phi_to_idx[term["phi"]]
            A[row, col] = int(term["coeff"])
            
    rank_A = np.linalg.matrix_rank(A)
    print(f"Rank of Coboundary Operator delta: {rank_A} / {min(num_components, dim_phi)}")
    
    # Build RHS for evaluated deformation (profile: all_ones)
    gamma_eval_vec = np.zeros(num_components, dtype=int)
    for term in data_eval["evaluated_deformation"]["evaluated_coefficients"]:
        X, Y, Z = term["X"], term["Y"], term["Z"]
        if (X, Y, Z) in cochain_to_idx:
            row = cochain_to_idx[(X, Y, Z)]
            gamma_eval_vec[row] = int(term["coeff"])
                    
    # Check consistency of A phi = gamma_eval_vec
    aug_eval = np.column_stack([A, gamma_eval_vec])
    rank_aug_eval = np.linalg.matrix_rank(aug_eval)
    is_eval_coboundary = (rank_A == rank_aug_eval)
    print(f"Rank of augmented matrix [A | gamma_eval]: {rank_aug_eval}")
    print(f"Is canonical evaluated deformation a coboundary? {is_eval_coboundary}")
    
    # Symbolic deformation analysis:
    # Build matrix B_gb representing gamma(gb) in basis of cochain components
    # The parameters are gb_sigma_j_s
    gb_symbols = []
    for sigma in ["p", "m"]:
        for j in range(1, n + 1):
            for s in ["p", "m"]:
                gb_symbols.append(f"gb_a1_{sigma}_b{j}_{s}")
    dim_gb = len(gb_symbols)
    gb_to_idx = {g: i for i, g in enumerate(gb_symbols)}
    
    B_gb = np.zeros((num_components, dim_gb), dtype=int)
    for term in data_gamma["inhomogeneous_deformation"]["gamma_coefficients"]:
        X, Y, Z = term["X"], term["Y"], term["Z"]
        if (X, Y, Z) in cochain_to_idx:
            row = cochain_to_idx[(X, Y, Z)]
            gb_name = term["gb"]
            B_gb[row, gb_to_idx[gb_name]] += int(term["coeff"])
                        
    # Obstruction calculation:
    # An element gamma(gb) is a coboundary iff for all w in ker(A^T), w^T gamma(gb) = 0.
    # We find an orthonormal basis of ker(A^T) via SVD of A
    U, S, Vt = np.linalg.svd(A)
    tol = 1e-10
    coker_U = []
    for col_idx in range(len(S)):
        if S[col_idx] < tol:
            coker_U.append(U[:, col_idx])
    for col_idx in range(len(S), num_components):
        coker_U.append(U[:, col_idx])
        
    coker_U = np.array(coker_U) # shape: (dim_coker, num_components)
    dim_coker = coker_U.shape[0]
    print(f"Dimension of cokernel (ker A^T): {dim_coker}")
    
    # Project B_gb onto cokernel:
    obs_matrix = coker_U @ B_gb # shape: (dim_coker, dim_gb)
    rank_obs = np.linalg.matrix_rank(obs_matrix, tol=1e-7)
    print(f"Number of gb parameters: {dim_gb}")
    print(f"Rank of obstruction matrix (coker(A)^T * B_gb): {rank_obs}")
    print(f"Are all gb parameters obstructed? {rank_obs == dim_gb}")
    
    # Explicit discrepancies / obstruction generator pairs:
    # Project gamma_eval onto cokernel:
    proj_eval = coker_U @ gamma_eval_vec
    norm_proj = np.linalg.norm(proj_eval)
    print(f"Norm of projection of gamma_eval onto coker(A^T): {norm_proj:.4f}")
    
    # Least squares residual:
    phi_least_sq, residuals, rank, s = np.linalg.lstsq(A.astype(float), gamma_eval_vec.astype(float), rcond=None)
    reconstructed_gamma = A.astype(float) @ phi_least_sq
    discrepancy = gamma_eval_vec - reconstructed_gamma
    
    print("\nSample discrepancies for evaluated deformation (all_ones):")
    disc_count = 0
    disc_pairs = set()
    for row_idx, diff in enumerate(discrepancy):
        if abs(diff) > 1e-5:
            X, Y, Z = cochain_components[row_idx]
            disc_pairs.add((X, Y))
            if disc_count < 10:
                print(f"  Pair ({X}, {Y}) -> Z={Z}: gamma={gamma_eval_vec[row_idx]}, delta_f={reconstructed_gamma[row_idx]:.2f}, diff={diff:.2f}")
                disc_count += 1
    print(f"Total number of cochain components with non-zero discrepancy: {len([d for d in discrepancy if abs(d) > 1e-5])}")
    print(f"Total generator pairs exhibiting discrepancies: {len(disc_pairs)}")
    print(f"Sample generator pairs exhibiting discrepancies:")
    for p in sorted(list(disc_pairs))[:10]:
        print(f"  {p}")

if __name__ == "__main__":
    for n in [1, 2, 3]:
        analyze_triviality(n)
