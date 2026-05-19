import json
import os
from fractions import Fraction
from collections import defaultdict
import numpy as np

def solve_for_f(n):
    eval_path = f"data/C_{n}_evaluated_pos.json"
    struct_path = f"data/C_{n}_structure.json"
    
    with open(eval_path, 'r') as f:
        layer3 = json.load(f)
    with open(struct_path, 'r') as f:
        s1 = json.load(f)

    basis_even = s1['basis']['even']
    basis_odd = s1['basis']['odd']
    all_basis = basis_odd + basis_even + ["K"]
    parity = s1['parity']
    if "K" not in parity: parity["K"] = 0

    # Map: (X, Y) -> {Z: coeff}
    gamma_target = defaultdict(dict)
    for entry in layer3['evaluated_gamma_structure']:
        gamma_target[(entry['X'], entry['Y'])][entry['Z']] = Fraction(entry['coeff'])

    # Structure constants
    sc = defaultdict(dict)
    for entry in s1['structure_constants']:
        X, Y, Z = entry['X'], entry['Y'], entry['Z']
        sc[(X, Y)][Fraction(1)] = {Z: Fraction(entry['coeff'])} # Wait, this is wrong format
    
    # Let's rebuild SC map
    sc_map = defaultdict(dict)
    for entry in s1['structure_constants']:
        sc_map[(entry['X'], entry['Y'])][entry['Z']] = Fraction(entry['coeff'])

    def get_bracket(X, Y):
        if (X, Y) in sc_map: return sc_map[(X, Y)]
        pX, pY = parity[X], parity[Y]
        sign = -1 if (pX == 1 and pY == 1) else 1
        if (Y, X) in sc_map:
            return {Z: -val * sign for Z, val in sc_map[(Y, X)].items()}
        return {}

    # We want to find f: g -> g such that delta f = gamma
    # f is odd.
    # f(Z_j) = sum_i phi_{ij} Z_i
    # where p(Z_i) = p(Z_j) + 1 (mod 2)
    
    # Variables: phi_{ij} where p_i + p_j = 1
    vars = []
    for j, Zj in enumerate(all_basis):
        for i, Zi in enumerate(all_basis):
            if (parity[Zi] + parity[Zj]) % 2 == 1:
                vars.append((i, j)) # f(Zj) has component Zi
    
    var_to_idx = {v: k for k, v in enumerate(vars)}
    num_vars = len(vars)
    
    # Equations: for each (X, Y) pair and each result Z_res
    # (delta f)(X, Y)_Zres = gamma(X, Y)_Zres
    
    # (delta f)(X, Y) = (-1)^pX [X, f(Y)] - (-1)^{(pX+1)pY} [Y, f(X)] - f([X, Y])
    
    equations = []
    targets = []
    
    # To keep it manageable, let's only use a subset of pairs or check if it's solvable
    # Actually, let's try to build the matrix for n=1
    if n > 1:
        print(f"Skipping solver for n={n} (too many variables)")
        return

    eq_info = []
    for idx_X, X in enumerate(all_basis):
        for idx_Y, Y in enumerate(all_basis):
            if idx_X > idx_Y: continue
            
            pX, pY = parity[X], parity[Y]
            target_dict = gamma_target[(X, Y)]
            
            for idx_Zres, Z_res in enumerate(all_basis):
                row = [Fraction(0)] * num_vars
                
                # Term 1: (-1)^pX [X, f(Y)]
                s1_val = -1 if pX == 1 else 1
                for i, Zi in enumerate(all_basis):
                    if (parity[Zi] + pY) % 2 == 1:
                        v_idx = var_to_idx.get((i, idx_Y))
                        if v_idx is not None:
                            br = get_bracket(X, Zi)
                            coeff = br.get(Z_res, Fraction(0))
                            if coeff != 0:
                                row[v_idx] += s1_val * coeff

                # Term 2: - (-1)^{(pX+1)pY} [Y, f(X)]
                s2_val = - (-1 if ((pX + 1) == 1 and pY == 1) else 1)
                for i, Zi in enumerate(all_basis):
                    if (parity[Zi] + pX) % 2 == 1:
                        v_idx = var_to_idx.get((i, idx_X))
                        if v_idx is not None:
                            br = get_bracket(Y, Zi)
                            coeff = br.get(Z_res, Fraction(0))
                            if coeff != 0:
                                row[v_idx] += s2_val * coeff

                # Term 3: - f([X, Y])
                brXY = get_bracket(X, Y)
                for k_name, c_k in brXY.items():
                    idx_k = all_basis.index(k_name)
                    v_idx = var_to_idx.get((idx_Zres, idx_k))
                    if v_idx is not None:
                        row[v_idx] -= c_k

                target_val = target_dict.get(Z_res, Fraction(0))
                
                if any(val != 0 for val in row) or target_val != 0:
                    equations.append(row)
                    targets.append(target_val)
                    eq_info.append((X, Y, Z_res))

    # Solve using numpy
    A = np.zeros((len(equations), num_vars))
    for i, row in enumerate(equations):
        for j, val in enumerate(row):
            A[i, j] = float(val)
    
    B = np.array([float(t) for t in targets])
    
    # Check rank of A (Image of delta)
    rank_delta = np.linalg.matrix_rank(A)
    print(f"Rank of Image(delta): {rank_delta}")

    # Check rank of [A | B] (Image of delta + specific deformation)
    A_ext = np.column_stack([A, B])
    rank_ext = np.linalg.matrix_rank(A_ext)
    print(f"Rank of [Image(delta) | gamma]: {rank_ext}")
    
    if rank_ext > rank_delta:
        print("The deformation gamma is LINEARLY INDEPENDENT of coboundaries.")
        print("Conclusion: NON-TRIVIAL.")
    else:
        print("The deformation gamma is in the Image(delta).")
        print("Conclusion: TRIVIAL.")

if __name__ == "__main__":
    solve_for_f(1)
