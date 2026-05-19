import json
import os
from fractions import Fraction
from collections import defaultdict
import numpy as np

def solve_with_formula(n, formula_type="project"):
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

    gamma_target = defaultdict(dict)
    for entry in layer3['evaluated_gamma_structure']:
        gamma_target[(entry['X'], entry['Y'])][entry['Z']] = Fraction(entry['coeff'])

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

    vars = []
    for j, Zj in enumerate(all_basis):
        for i, Zi in enumerate(all_basis):
            if (parity[Zi] + parity[Zj]) % 2 == 1:
                vars.append((i, j))
    
    var_to_idx = {v: k for k, v in enumerate(vars)}
    num_vars = len(vars)
    
    equations = []
    targets = []

    for idx_X, X in enumerate(all_basis):
        for idx_Y, Y in enumerate(all_basis):
            if idx_X > idx_Y: continue
            
            pX, pY = parity[X], parity[Y]
            target_dict = gamma_target[(X, Y)]
            
            for idx_Zres, Z_res in enumerate(all_basis):
                row = [Fraction(0)] * num_vars
                
                if formula_type == "project":
                    # (-1)^pX [X, f(Y)] - (-1)^{(pX+1)pY} [Y, f(X)] - f([X, Y])
                    s1_val = -1 if pX == 1 else 1
                    s2_val = - (-1 if ((pX + 1) == 1 and pY == 1) else 1)
                else:
                    # [X, f(Y)] + [f(X), Y] - f([X, Y]) (naive derivation)
                    s1_val = 1
                    s2_val = 1 # [f(X), Y] = -(-1)^{p(fX)pY} [Y, f(X)] = -(-1)^{(pX+1)pY} [Y, f(X)]
                    # Wait, let's use [X, f(Y)] - (-1)^pX [f(X), Y] ... no.
                    # Let's just test if ANY linear combination works.
                    pass

                # Term 1: [X, f(Y)]
                for i, Zi in enumerate(all_basis):
                    if (parity[Zi] + pY) % 2 == 1:
                        v_idx = var_to_idx.get((i, idx_Y))
                        if v_idx is not None:
                            br = get_bracket(X, Zi)
                            coeff = br.get(Z_res, Fraction(0))
                            row[v_idx] += s1_val * coeff

                # Term 2: [f(X), Y] = -(-1)^{(pX+1)pY} [Y, f(X)]
                for i, Zi in enumerate(all_basis):
                    if (parity[Zi] + pX) % 2 == 1:
                        v_idx = var_to_idx.get((i, idx_X))
                        if v_idx is not None:
                            br = get_bracket(Y, Zi)
                            coeff = br.get(Z_res, Fraction(0))
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

    A = np.zeros((len(equations), num_vars))
    for i, row in enumerate(equations):
        for j, val in enumerate(row):
            A[i, j] = float(val)
    B = np.array([float(t) for t in targets])
    sol, residuals, rank, s = np.linalg.lstsq(A, B, rcond=None)
    max_diff = np.max(np.abs(A @ sol - B))
    print(f"Formula {formula_type}: Max Diff {max_diff}")

if __name__ == "__main__":
    solve_with_formula(1, "project")
