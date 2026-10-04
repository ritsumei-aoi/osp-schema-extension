import json
import numpy as np

def check_triviality(n):
    with open(f"data/C_{n}_gamma.json", "r") as f:
        schema2 = json.load(f)
    with open(f"data/C_{n}_coboundary.json", "r") as f:
        schema4 = json.load(f)
        
    gb_params = schema2['inhomogeneous_deformation']['gb_parameters']
    phi_params = schema4['coboundary_structure']['phi_parameters']
    
    gb_idx = {p: i for i, p in enumerate(gb_params)}
    phi_idx = {p: i for i, p in enumerate(phi_params)}
    
    equations = {} # (X, Y, Z) -> (row_gamma, row_M)
    
    # Fill Gamma (from Schema 2)
    for entry in schema2['inhomogeneous_deformation']['gamma_structure_constants']:
        key = (entry['X'], entry['Y'], entry['Z'])
        gb_param = entry['gb_param']
        coeff = float(eval(entry['coeff']))
        if key not in equations:
            equations[key] = (np.zeros(len(gb_params)), np.zeros(len(phi_params)))
        equations[key][0][gb_idx[gb_param]] += coeff
        
    # Fill M (from Schema 4)
    for entry in schema4['coboundary_structure']['coboundary_constants']:
        key = (entry['X'], entry['Y'], entry['Z'])
        phi_param = entry['phi_param']
        coeff = float(eval(entry['coeff']))
        if key not in equations:
            equations[key] = (np.zeros(len(gb_params)), np.zeros(len(phi_params)))
        equations[key][1][phi_idx[phi_param]] += coeff
        
    keys = list(equations.keys())
    Gamma_matrix = np.array([equations[k][0] for k in keys]) # shape (num_eqs, num_gb)
    M_matrix = np.array([equations[k][1] for k in keys]) # shape (num_eqs, num_phi)
    
    # We want to know if for every column in Gamma, it is in the column space of M.
    rank_M = np.linalg.matrix_rank(M_matrix)
    
    trivial_gb_conditions = []
    
    # To find conditions, we can find the left null space of M.
    # U, S, Vh = svd(M)
    U, S, Vh = np.linalg.svd(M_matrix)
    # The columns of U corresponding to singular values = 0 form the left null space.
    tol = 1e-10
    null_space_dim = sum(S < tol) + (M_matrix.shape[0] - len(S))
    if null_space_dim > 0:
        left_null_space = U[:, np.abs(S) < tol] if len(S) == M_matrix.shape[0] else U[:, len(S):]
        # Any vector v in column space of Gamma must satisfy left_null_space.T @ v = 0
        constraints = left_null_space.T @ Gamma_matrix # shape (null_dim, num_gb)
        
        # We find a basis for the row space of constraints to see which linear combinations of gb must be 0
        U_c, S_c, Vh_c = np.linalg.svd(constraints)
        rank_c = np.linalg.matrix_rank(constraints, tol=tol)
        
        if rank_c == 0:
            print(f"n={n}: ALWAYS TRIVIAL. All Gamma vectors are in the span of M.")
        else:
            print(f"n={n}: NON-TRIVIAL. There are {rank_c} independent constraints on gb.")
            for i in range(rank_c):
                row = Vh_c[i]
                cond = []
                for j, p in enumerate(gb_params):
                    if abs(row[j]) > 1e-5:
                        cond.append(f"{row[j]:.3f} * {p}")
                print("  Constraint:", " + ".join(cond), "= 0")
    else:
        print(f"n={n}: ALWAYS TRIVIAL. M has full row rank (which is unlikely but mathematically possible).")
        
    print(f"  Equations: {M_matrix.shape[0]}, phi vars: {M_matrix.shape[1]}, rank(M): {rank_M}")

if __name__ == '__main__':
    for n in [1, 2, 3]:
        check_triviality(n)
