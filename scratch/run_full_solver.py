import sympy as sp
from collections import defaultdict
from itertools import combinations_with_replacement, product
import sys

from normal_order import Monomial, multiply_monomials
from vec_helper import get_basis_and_algebra, monomial_to_vec

def elem_to_monomial(elem):
    """
    Converts a basis element representation tuple into a Monomial.
    """
    if elem == ('Z',):
        return Monomial(1, 1, (), 0, 1)
    elif elem[0] == 'O':
        sigma, k, s = elem[1], elem[2], elem[3]
        u_p = 1 if sigma == '+' else 0
        u_m = 1 if sigma == '-' else 0
        return Monomial(u_p, u_m, ((k, s),), 0, 1)
    elif len(elem) == 2 and elem[0][0] == 'b':
        # sp(2n) element: ( ('b', k, s1), ('b', l, s2) )
        k, s1 = elem[0][1], elem[0][2]
        l, s2 = elem[1][1], elem[1][2]
        return Monomial(0, 0, ((k, s1), (l, s2)), 0, 1)
    else:
        raise ValueError(f"Unknown elem: {elem}")

def solve_cn_system(n):
    print(f"\n==================================================")
    print(f"   RUNNING TRIVIALITY SOLVER FOR C({n+1}) = osp(2|2{n})")
    print(f"==================================================")
    
    even_basis, odd_basis = get_basis_and_algebra(n)
    all_basis = even_basis + odd_basis
    
    dim_even = len(even_basis)
    dim_odd = len(odd_basis)
    print(f"Dimension: even = {dim_even}, odd = {dim_odd}, total = {dim_even + dim_odd}")
    
    # Define gb parameters: gb_{sigma, k, s}
    gb_params = {}
    gb_vars = []
    for sigma in ['+', '-']:
        for k in range(1, n+1):
            for s in ['+', '-']:
                var = sp.Symbol(f"gb_{sigma}_{k}_{s}")
                gb_params[(sigma, k, s)] = var
                gb_vars.append(var)
                
    print(f"Deformation parameters ({len(gb_vars)} total): {gb_vars}")
    
    # Define f parameters (phi_E_O and phi_O_E)
    f_vars = []
    phi_map = {}
    for E in even_basis:
        for O in odd_basis:
            # E string name
            E_str = "Z" if E == ('Z',) else f"B_{E[0][1]}{E[0][2]}_{E[1][1]}{E[1][2]}"
            O_str = f"O_{O[1]}_{O[2]}{O[3]}"
            v = sp.Symbol(f"phi_{E_str}_{O_str}")
            phi_map[(E, O)] = v
            f_vars.append(v)
            
    for O in odd_basis:
        for E in even_basis:
            E_str = "Z" if E == ('Z',) else f"B_{E[0][1]}{E[0][2]}_{E[1][1]}{E[1][2]}"
            O_str = f"O_{O[1]}_{O[2]}{O[3]}"
            v = sp.Symbol(f"phi_{O_str}_{E_str}")
            phi_map[(O, E)] = v
            f_vars.append(v)
            
    print(f"Linear map f parameters ({len(f_vars)} total)")
    
    # 1. Precompute [X, Y]_0 and gamma_gb(X, Y) for all basis pairs (X, Y)
    # To reduce redundant pairs, we consider X <= Y by index in all_basis.
    
    brackets_0 = {} # (X, Y) -> vec_0
    gamma_gb = {}   # (X, Y) -> vec_1
    
    for i, X in enumerate(all_basis):
        pX = 0 if X in even_basis else 1
        mX = elem_to_monomial(X)
        for j, Y in enumerate(all_basis):
            if i > j:
                continue # use anti-symmetry / super-symmetry
            pY = 0 if Y in even_basis else 1
            mY = elem_to_monomial(Y)
            
            # Superbracket: XY - (-1)^{pX pY} YX
            sign_YX = 1 if (pX * pY == 1) else -1
            
            XY_dict = multiply_monomials(mX, mY, n, gb_params)
            YX_dict = multiply_monomials(mY, mX, n, gb_params)
            
            super_bracket_dict = defaultdict(lambda: sp.sympify(0))
            for k, c in XY_dict.items():
                super_bracket_dict[k] += c
            for k, c in YX_dict.items():
                super_bracket_dict[k] += sign_YX * c
                
            vec_0, vec_1 = monomial_to_vec(super_bracket_dict, even_basis, odd_basis, n)
            brackets_0[(X, Y)] = vec_0
            gamma_gb[(X, Y)] = vec_1
            
    print("Precomputed all Lie superbrackets and gamma_gb deformations.")
    
    # Helper for bracket [X, Y]_0 with arbitrary order
    def get_bracket_0(X, Y):
        if (X, Y) in brackets_0:
            return brackets_0[(X, Y)]
        # Use super-symmetry: [Y, X]_0 = (-1)^{pX pY + 1} [X, Y]_0
        pX = 0 if X in even_basis else 1
        pY = 0 if Y in even_basis else 1
        sign = 1 if (pX * pY == 1) else -1
        raw = brackets_0[(Y, X)]
        return {b: sign * c for b, c in raw.items()}
        
    # 2. Form coboundary delta f(X, Y) and linear equations
    # delta f(X, Y) = (-1)^{pX} [X, f(Y)]_0 - (-1)^{(pX+1)pY} [Y, f(X)]_0 - f([X, Y]_0)
    
    equations = []
    
    for i, X in enumerate(all_basis):
        pX = 0 if X in even_basis else 1
        for j, Y in enumerate(all_basis):
            if i > j:
                continue
            pY = 0 if Y in even_basis else 1
            
            # Target gamma_gb vector
            gamma_vec = gamma_gb[(X, Y)]
            
            # Compute delta f(X, Y):
            # Term 1: (-1)^{pX} [X, f(Y)]_0
            # f(Y) = sum_{W} phi_{(Y, W)} W
            t1_sign = -1 if pX == 1 else 1
            t1_vec = {b: sp.sympify(0) for b in all_basis}
            
            target_space_Y = odd_basis if pY == 0 else even_basis
            for W in target_space_Y:
                phi_YW = phi_map[(Y, W)]
                br = get_bracket_0(X, W)
                for b, c in br.items():
                    t1_vec[b] += t1_sign * phi_YW * c
                    
            # Term 2: - (-1)^{(pX+1)pY} [Y, f(X)]_0
            t2_sign = - (-1)**((pX + 1) * pY)
            t2_vec = {b: sp.sympify(0) for b in all_basis}
            
            target_space_X = odd_basis if pX == 0 else even_basis
            for W in target_space_X:
                phi_XW = phi_map[(X, W)]
                br = get_bracket_0(Y, W)
                for b, c in br.items():
                    t2_vec[b] += t2_sign * phi_XW * c
                    
            # Term 3: - f([X, Y]_0)
            # [X, Y]_0 = sum_W c_W W
            t3_vec = {b: sp.sympify(0) for b in all_basis}
            br_XY = brackets_0[(X, Y)]
            for W, c_W in br_XY.items():
                if c_W == 0:
                    continue
                target_space_W = odd_basis if (W in even_basis) else even_basis
                for V in target_space_W:
                    phi_WV = phi_map[(W, V)]
                    t3_vec[V] -= c_W * phi_WV
                    
            # Combine delta f(X, Y)
            delta_f_vec = {b: t1_vec[b] + t2_vec[b] + t3_vec[b] for b in all_basis}
            
            # Equate gamma_gb(X, Y)[b] == delta_f_vec[b] for all b in all_basis
            for b in all_basis:
                eq = sp.simplify(gamma_vec[b] - delta_f_vec[b])
                if eq != 0:
                    equations.append(eq)
                    
    print(f"Generated {len(equations)} linear equations for C({n+1}).")
    
    # 3. Solve the system of linear equations for (gb_vars, f_vars)
    all_vars = gb_vars + f_vars
    sol = sp.solve(equations, all_vars, dict=True)
    
    print(f"\n--- SOLUTION RESULT FOR C({n+1}) ---")
    if not sol:
        print("No solution exists! (System is inconsistent)")
        return False
        
    print(f"Number of solution branches / parameter sets: {len(sol)}")
    for idx, s in enumerate(sol):
        print(f"\nSolution set #{idx+1}:")
        gb_sols = {v: s.get(v, v) for v in gb_vars}
        print("gb parameters in solution:")
        for v, val in gb_sols.items():
            print(f"  {v} = {val}")
            
    # Check if all gb_vars are forced to be 0
    all_gb_zero = True
    for s in sol:
        for v in gb_vars:
            val = s.get(v, v)
            if val != 0:
                all_gb_zero = False
                break
                
    if all_gb_zero:
        print(f"\n>>> CONCLUSION FOR C({n+1}): TRIVIALITY REQUIRES gb = 0!")
        print(f">>> No non-zero gb configuration can be trivial!")
    else:
        print(f"\n>>> CONCLUSION FOR C({n+1}): NON-TRIVIAL gb EXIST!")
        
    return all_gb_zero

if __name__ == "__main__":
    for n in [1, 2, 3]:
        solve_cn_system(n)
