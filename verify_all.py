import sympy as sp
import json
import os
from algebra_helper import build_algebra
from reduction import get_osc_parity, deformed_bracket_osc, reduce_pair_to_basis
from bracket_solver import compute_bracket

def run_comprehensive_verification():
    all_artifacts = {}
    
    for n in [1, 2, 3]:
        algebra_name = f"C({n+1})"
        superalgebra_name = f"osp(2|{2*n})"
        print(f"\n=======================================================")
        print(f"  RIGOROUS VERIFICATION: {algebra_name} = {superalgebra_name}")
        print(f"=======================================================")
        
        basis = build_algebra(n)
        dim = len(basis)
        basis_map = {b[0]: i for i, b in enumerate(basis)}
        
        even_indices = [i for i, b in enumerate(basis) if b[1] == 0]
        odd_indices = [i for i, b in enumerate(basis) if b[1] == 1]
        dim_even = len(even_indices)
        dim_odd = len(odd_indices)
        
        # 1. Structure constants C^k_{ij}
        gb_keys = []
        for sigma in ['+', '-']:
            for j in range(1, n + 1):
                for s in ['+', '-']:
                    gb_keys.append((sigma, j, s))
                    
        gb_zero = {k: sp.Rational(0) for k in gb_keys}
        
        C = [[[sp.Rational(0) for _ in range(dim)] for _ in range(dim)] for _ in range(dim)]
        for i in range(dim):
            for j in range(dim):
                v0, _ = compute_bracket(basis[i], basis[j], n, basis, basis_map, gb_zero)
                for k in range(dim):
                    C[i][j][k] = v0[k]
                    
        # 2. Odd map f parametrization
        f_map_indices = []
        for j in range(dim):
            pj = basis[j][1]
            for i in range(dim):
                pi = basis[i][1]
                if pi != pj: # parity reversing
                    f_map_indices.append((i, j))
        f_idx_lookup = {pair: idx for idx, pair in enumerate(f_map_indices)}
        num_f_vars = len(f_map_indices)
        
        # Independent pairs (i, j)
        pair_list = []
        for i in range(dim):
            for j in range(dim):
                if i < j or (i == j and basis[i][1] == 1):
                    pair_list.append((i, j))
                    
        # 3. Build Coboundary Matrix delta_matrix
        # delta_matrix maps f_vars (size num_f_vars) -> 2-cochain components (size len(pair_list)*dim)
        delta_rows = []
        row_descriptors = []
        for (i, j) in pair_list:
            pX = basis[i][1]
            pY = basis[j][1]
            sign1 = (-1)**pX
            sign2 = - ((-1)**((pX + 1) * pY))
            
            for l in range(dim):
                row = [sp.Rational(0)] * num_f_vars
                # Term 1: (-1)^{pX} [X, f(Y)]_l
                for k in range(dim):
                    if (k, j) in f_idx_lookup and C[i][k][l] != 0:
                        row[f_idx_lookup[(k, j)]] += sign1 * C[i][k][l]
                        
                # Term 2: - (-1)^{(pX+1)pY} [Y, f(X)]_l
                for k in range(dim):
                    if (k, i) in f_idx_lookup and C[j][k][l] != 0:
                        row[f_idx_lookup[(k, i)]] += sign2 * C[j][k][l]
                        
                # Term 3: - f([X, Y])_l
                for k in range(dim):
                    if (l, k) in f_idx_lookup and C[i][j][k] != 0:
                        row[f_idx_lookup[(l, k)]] -= C[i][j][k]
                        
                delta_rows.append(row)
                row_descriptors.append((i, j, l))
                
        M_delta = sp.Matrix(delta_rows)
        print(f"Coboundary matrix dimensions: {M_delta.shape}")
        
        # 4. For each gb parameter, compute gamma and solve delta f = gamma
        solutions_by_gb = {}
        all_solved = True
        
        for p_idx, gb_key in enumerate(gb_keys):
            gb_str = f"gb_{gb_key[0]}_{gb_key[1]}_{gb_key[2]}"
            gb_dict = dict(gb_zero)
            gb_dict[gb_key] = sp.Rational(1)
            
            # Compute gamma for this gb_key
            b_vec = []
            for (i, j, l) in row_descriptors:
                _, vg = compute_bracket(basis[i], basis[j], n, basis, basis_map, gb_dict)
                b_vec.append(vg[l])
                
            b_mat = sp.Matrix(b_vec)
            
            # Solve M_delta * f = b_mat
            try:
                sol = M_delta.gauss_jordan_solve(b_mat)
                f_particular = sol[0]
                
                # Verify residual exactly: ||M_delta * f_particular - b_mat|| == 0
                residual = M_delta * f_particular - b_mat
                res_norm = sum(abs(x) for x in residual)
                assert res_norm == 0, f"Non-zero residual {res_norm} for {gb_str}"
                
                # Extract non-zero matrix elements of f:
                f_nonzero_entries = {}
                for f_var_idx, (out_idx, in_idx) in enumerate(f_map_indices):
                    val = f_particular[f_var_idx]
                    # Evaluate free parameters tau to 0 for a canonical particular solution
                    if hasattr(val, 'free_symbols'):
                        for sym in val.free_symbols:
                            val = val.subs(sym, 0)
                    if val != 0:
                        f_nonzero_entries[f"f({basis[in_idx][0]}) -> {basis[out_idx][0]}"] = str(val)
                        
                solutions_by_gb[gb_str] = {
                    "parameter": gb_str,
                    "is_coboundary": True,
                    "exact_residual": 0,
                    "f_canonical_matrix_entries": f_nonzero_entries
                }
                print(f"  [PASSED] Parameter {gb_str}: Exact Coboundary verified (Residual = 0).")
            except Exception as e:
                print(f"  [FAILED] Parameter {gb_str}: {e}")
                solutions_by_gb[gb_str] = {
                    "parameter": gb_str,
                    "is_coboundary": False,
                    "error": str(e)
                }
                all_solved = False
                
        # Rank of delta
        # Since rref of large matrix might take time, let's compute rank
        rref_M, pivots = M_delta.rref()
        rank_delta = len(pivots)
        dim_ker_delta = num_f_vars - rank_delta
        
        artifact_n = {
            "algebra": algebra_name,
            "superalgebra": superalgebra_name,
            "n": n,
            "dimensions": {
                "total": dim,
                "even": dim_even,
                "odd": dim_odd
            },
            "basis": [
                {"name": b[0], "parity": b[1], "type": "even" if b[1] == 0 else "odd"}
                for b in basis
            ],
            "num_gb_parameters": len(gb_keys),
            "gb_parameters": [f"gb_{k[0]}_{k[1]}_{k[2]}" for k in gb_keys],
            "coboundary_operator": {
                "f_dimension": num_f_vars,
                "rank": rank_delta,
                "kernel_dimension (1-cocycles)": dim_ker_delta
            },
            "all_gb_are_coboundaries": all_solved,
            "solutions": solutions_by_gb
        }
        
        all_artifacts[algebra_name] = artifact_n
        
    # Write structured JSON artifact
    os.makedirs("artifacts", exist_ok=True)
    artifact_path = "artifacts/triviality_verification_data.json"
    with open(artifact_path, "w") as f:
        json.dump(all_artifacts, f, indent=2)
    print(f"\nSuccessfully written structured artifact to {artifact_path}")
    return all_artifacts

if __name__ == '__main__':
    run_comprehensive_verification()
