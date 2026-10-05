import sympy as sp
from collections import defaultdict
from analyzer import run_analysis
import json

def test_triviality(n=1):
    basis_names, basis_parity, bracket_0, gamma_gb, gb_syms = run_analysis(n)
    
    # Let's define the linear map f: g -> g
    # f reverses parity:
    # If p(Z_j) = 0: f(Z_j) in g_1 (odd)
    # If p(Z_j) = 1: f(Z_j) in g_0 (even)
    
    even_indices = [name for name in basis_names if basis_parity[name] == 0]
    odd_indices = [name for name in basis_names if basis_parity[name] == 1]
    
    phi_syms = {}
    # f(Z_even) = sum_{k in odd} phi[k, j] Z_k
    for j in even_indices:
        for k in odd_indices:
            phi_syms[(k, j)] = sp.Symbol(f"phi_{k}_{j}")
            
    # f(Z_odd) = sum_{k in even} phi[k, j] Z_k
    for j in odd_indices:
        for k in even_indices:
            phi_syms[(k, j)] = sp.Symbol(f"phi_{k}_{j}")
            
    print(f"Total phi parameters: {len(phi_syms)}")
    print(f"Total gb parameters: {len(gb_syms)}")
    
    # Helper to evaluate undeformed bracket [X, Y]_0 for any two basis elements
    def eval_b0(name_X, name_Y):
        if (name_X, name_Y) in bracket_0:
            return bracket_0[(name_X, name_Y)]
        else:
            pX = basis_parity[name_X]
            pY = basis_parity[name_Y]
            sign = -1 if (pX == 1 and pY == 1) else 1
            inv = bracket_0[(name_Y, name_X)]
            return {k: -sign * v for k, v in inv.items()}
            
    # Helper to evaluate f(dict_element)
    def apply_f(elem_dict):
        # elem_dict is {basis_name: coeff}
        res = defaultdict(lambda: sp.Integer(0))
        for name, c in elem_dict.items():
            if basis_parity[name] == 0:
                for k in odd_indices:
                    res[k] += c * phi_syms[(k, name)]
            else:
                for k in even_indices:
                    res[k] += c * phi_syms[(k, name)]
        return {k: sp.simplify(v) for k, v in res.items() if v != 0}
        
    # Helper to evaluate [name_X, dict_element]
    def bracket_name_dict(name_X, elem_dict):
        res = defaultdict(lambda: sp.Integer(0))
        for name_Y, c in elem_dict.items():
            b = eval_b0(name_X, name_Y)
            for k, v in b.items():
                res[k] += c * v
        return {k: sp.simplify(v) for k, v in res.items() if v != 0}
        
    # Compute delta f(X, Y)
    # (\delta f)(X, Y) = (-1)^{p(X)}[X, f(Y)] - (-1)^{(p(X)+1)p(Y)}[Y, f(X)] - f([X, Y])
    def compute_delta_f(name_X, name_Y):
        pX = basis_parity[name_X]
        pY = basis_parity[name_Y]
        
        # Term 1: (-1)^{pX} [X, f(Y)]
        s1 = -1 if pX == 1 else 1
        fY = apply_f({name_Y: sp.Integer(1)})
        t1 = bracket_name_dict(name_X, fY)
        
        # Term 2: - (-1)^{(pX + 1) pY} [Y, f(X)]
        s2 = - (-1 if ((pX + 1) * pY) % 2 == 1 else 1)
        fX = apply_f({name_X: sp.Integer(1)})
        t2 = bracket_name_dict(name_Y, fX)
        
        # Term 3: - f([X, Y])
        bXY = eval_b0(name_X, name_Y)
        t3 = apply_f(bXY)
        
        res = defaultdict(lambda: sp.Integer(0))
        for k, v in t1.items(): res[k] += s1 * v
        for k, v in t2.items(): res[k] += s2 * v
        for k, v in t3.items(): res[k] -= v
        
        return {k: sp.simplify(v) for k, v in res.items() if v != 0}

    # Now we compare gamma_{gb}(X, Y) and delta_f(X, Y) for all pairs (X, Y) with i <= j
    print("Setting up linear system: gamma_gb(X, Y) = delta_f(X, Y)...")
    
    # Each equation is: (delta_f(X, Y))_k - (gamma_gb(X, Y))_k = 0
    all_equations = []
    
    for i, name_X in enumerate(basis_names):
        for j in range(i, len(basis_names)):
            name_Y = basis_names[j]
            df = compute_delta_f(name_X, name_Y)
            gam = gamma_gb[(name_X, name_Y)]
            
            # All basis components
            all_gens = set(df.keys()).union(set(gam.keys()))
            for g in all_gens:
                val_df = df.get(g, sp.Integer(0))
                val_gam = gam.get(g, sp.Integer(0))
                eq = sp.simplify(val_df - val_gam)
                if eq != 0:
                    all_equations.append(eq)
                    
    print(f"Total non-trivial component equations: {len(all_equations)}")
    
    # Solve linear system for phi and gb
    # We want to see what conditions on gb are required for a solution in phi to exist!
    all_vars = list(phi_syms.values()) + list(gb_syms.values())
    
    # Construct matrix A * vars = 0
    A, b = sp.linear_eq_to_matrix(all_equations, all_vars)
    print(f"Linear system matrix shape: {A.shape}")
    print(f"Matrix rank: {A.rank()}")
    
    # Now let's project out phi to find constraints on gb alone!
    # Or solve for all variables:
    sol = sp.solve(all_equations, all_vars, dict=True)
    print(f"Solution: {sol}")
    
    # Check if gb must be 0:
    sol_gb = sp.solve(all_equations, list(gb_syms.values()), dict=True)
    print(f"gb solutions: {sol_gb}")
    
    # Let's test whether gb = 0 is forced
    # Let's isolate the gb variables
    A_phi, _ = sp.linear_eq_to_matrix(all_equations, list(phi_syms.values()))
    print(f"A_phi shape: {A_phi.shape}, rank: {A_phi.rank()}")
    
    return sol

if __name__ == '__main__':
    test_triviality(1)
