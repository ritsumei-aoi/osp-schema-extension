import pytest
import json
import numpy as np

@pytest.mark.parametrize("n,expected_gb_dim,expected_map_dim,expected_delta_rank", [
    (1, 4, 32, 28),
    (2, 8, 176, 168),
    (3, 12, 528, 516),
])
def test_triviality_obstruction_and_non_triviality(n, expected_gb_dim, expected_map_dim, expected_delta_rank):
    with open(f"data/C_{n}_gamma.json") as f:
        data_gamma = json.load(f)
    with open(f"data/C_{n}_evaluated.json") as f:
        data_eval = json.load(f)
    with open(f"data/C_{n}_coboundary.json") as f:
        data_coboundary = json.load(f)
        
    basis = data_gamma["basis"]["odd"] + data_gamma["basis"]["even"]
    parity = data_gamma["parity"]
    dim_g = len(basis)
    
    phi_params = data_coboundary["odd_linear_map_space"]["parameters"]
    phi_to_idx = {p: i for i, p in enumerate(phi_params)}
    dim_phi = len(phi_params)
    assert dim_phi == expected_map_dim
    
    # Independent cochain pairs
    independent_pairs = []
    for i, X in enumerate(basis):
        for j in range(i, dim_g):
            if i == j:
                if parity[X] == 1:
                    independent_pairs.append((X, basis[j]))
            else:
                independent_pairs.append((X, basis[j]))
                
    cochain_components = []
    cochain_to_idx = {}
    for (X, Y) in independent_pairs:
        px, py = parity[X], parity[Y]
        for Z in basis:
            if parity[Z] == (px + py + 1) % 2:
                cochain_components.append((X, Y, Z))
                cochain_to_idx[(X, Y, Z)] = len(cochain_components) - 1
                
    num_components = len(cochain_components)
    
    # Coboundary matrix A
    A = np.zeros((num_components, dim_phi), dtype=int)
    for term in data_coboundary["coboundary_operator"]["coboundary_coefficients"]:
        X, Y, Z = term["X"], term["Y"], term["Z"]
        if (X, Y, Z) in cochain_to_idx:
            row = cochain_to_idx[(X, Y, Z)]
            col = phi_to_idx[term["phi"]]
            A[row, col] = int(term["coeff"])
            
    rank_A = np.linalg.matrix_rank(A)
    assert rank_A == expected_delta_rank
    
    # Evaluated deformation vector
    gamma_eval_vec = np.zeros(num_components, dtype=int)
    for term in data_eval["evaluated_deformation"]["evaluated_coefficients"]:
        X, Y, Z = term["X"], term["Y"], term["Z"]
        if (X, Y, Z) in cochain_to_idx:
            row = cochain_to_idx[(X, Y, Z)]
            gamma_eval_vec[row] = int(term["coeff"])
            
    aug_eval = np.column_stack([A, gamma_eval_vec])
    rank_aug_eval = np.linalg.matrix_rank(aug_eval)
    # Proves canonical deformation is NOT a coboundary
    assert rank_aug_eval == rank_A + 1
    
    # Symbolic deformation matrix B_gb
    gb_symbols = []
    for sigma in ["p", "m"]:
        for j in range(1, n + 1):
            for s in ["p", "m"]:
                gb_symbols.append(f"gb_a1_{sigma}_b{j}_{s}")
    assert len(gb_symbols) == expected_gb_dim
    gb_to_idx = {g: i for i, g in enumerate(gb_symbols)}
    
    B_gb = np.zeros((num_components, expected_gb_dim), dtype=int)
    for term in data_gamma["inhomogeneous_deformation"]["gamma_coefficients"]:
        X, Y, Z = term["X"], term["Y"], term["Z"]
        if (X, Y, Z) in cochain_to_idx:
            row = cochain_to_idx[(X, Y, Z)]
            B_gb[row, gb_to_idx[term["gb"]]] += int(term["coeff"])
            
    # Obstruction rank via SVD
    U, S, Vt = np.linalg.svd(A)
    tol = 1e-10
    coker_U = []
    for col_idx in range(len(S)):
        if S[col_idx] < tol:
            coker_U.append(U[:, col_idx])
    for col_idx in range(len(S), num_components):
        coker_U.append(U[:, col_idx])
    coker_U = np.array(coker_U)
    
    obs_matrix = coker_U @ B_gb
    rank_obs = np.linalg.matrix_rank(obs_matrix, tol=1e-7)
    # Proves all gb parameters are obstructed
    assert rank_obs == expected_gb_dim
