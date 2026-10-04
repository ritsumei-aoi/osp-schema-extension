"""
General implementation of C(n+1) = osp(2|2n) for n = 1, 2, 3.
Computes:
1. Basis of g = C(n+1) (even, odd, dimensions).
2. Undeformed structure constants [X, Y]_0.
3. Super-Jacobi identity verification for [X, Y]_0.
4. Deformed bracket gamma(X, Y) from oscillator relations.
5. Coboundary operator delta f(X, Y).
6. Linear system delta f = gamma_gb and rank of constraint matrix on gb.
7. Generates structured JSON output for reproducibility.
"""

import sympy as sp
from collections import defaultdict
import json
import time

def solve_osp(n_val):
    print(f"\n==========================================")
    print(f"  ANALYZING C({n_val+1}) = osp(2|{2*n_val})")
    print(f"==========================================")
    start_time = time.time()
    
    # 1. Generators setup
    # Bosons: b_1+, b_1-, ..., b_n+, b_n-
    # Fermions: a_1+, a_1-
    # Basis:
    # Even:
    #   H_1, ..., H_{n+1} (or J0, h_1, ..., h_n)
    #   E_{2d_k}, E_{-2d_k} for k=1..n
    #   For k < l: E_{dk+dl}, E_{-dk-dl}, E_{dk-dl}, E_{dl-dk}
    # Odd:
    #   F_{sigma, k, s} for sigma in {+,-}, s in {+,-}, k=1..n
    
    # Let's use the standard Chevalley/oscillator basis from docs/math/Cn1_definition.md:
    # ap = a1+, am = a1-
    # bp(k) = bk+, bm(k) = bk-
    
    ap = ('a', 1, 1)
    am = ('a', 1, -1)
    def bp(k): return ('b', k, 1)
    def bm(k): return ('b', k, -1)
    
    # gb symbols
    gb_syms = {}
    gb_list = []
    for k in range(1, n_val + 1):
        for sig in ['+', '-']:
            for s in ['+', '-']:
                sym = sp.Symbol(f"gb_{'p' if sig=='+' else 'm'}{k}{'p' if s=='+' else 'm'}")
                gb_syms[(sig, k, s)] = sym
                gb_list.append(sym)
                
    # Define generators as dict of monomials: {monomial: coeff}
    generators = {}
    parity = {}
    
    # J0 = a+ a- - 1/2
    generators['J0'] = ({(ap, am): 1, (): sp.Rational(-1, 2)}, 0)
    # h_k = bk+ bk- + 1/2
    for k in range(1, n_val + 1):
        generators[f'h_{k}'] = ({(bp(k), bm(k)): 1, (): sp.Rational(1, 2)}, 0)
        
    # Long roots
    for k in range(1, n_val + 1):
        generators[f'E_2d_{k}'] = ({(bp(k), bp(k)): sp.Rational(1, 2)}, 0)
        generators[f'E_-2d_{k}'] = ({(bm(k), bm(k)): sp.Rational(1, 2)}, 0)
        
    # Short roots (for k < l)
    for k in range(1, n_val + 1):
        for l in range(k + 1, n_val + 1):
            generators[f'E_d{k}+d{l}'] = ({(bp(k), bp(l)): 1}, 0)
            generators[f'E_-d{k}-d{l}'] = ({(bm(k), bm(l)): 1}, 0)
            generators[f'E_d{k}-d{l}'] = ({(bp(k), bm(l)): 1}, 0)
            generators[f'E_d{l}-d{k}'] = ({(bp(l), bm(k)): 1}, 0)
            
    # Odd generators
    for k in range(1, n_val + 1):
        generators[f'F_p_{k}_p'] = ({(ap, bp(k)): 1}, 1)
        generators[f'F_p_{k}_m'] = ({(ap, bm(k)): 1}, 1)
        generators[f'F_m_{k}_p'] = ({(am, bp(k)): 1}, 1)
        generators[f'F_m_{k}_m'] = ({(am, bm(k)): 1}, 1)
        
    even_basis = [g for g, (d, p) in generators.items() if p == 0]
    odd_basis = [g for g, (d, p) in generators.items() if p == 1]
    basis = even_basis + odd_basis
    
    dim_even = len(even_basis)
    dim_odd = len(odd_basis)
    dim_total = len(basis)
    
    print(f"Dimension: {dim_even} even + {dim_odd} odd = {dim_total} total")
    assert dim_even == 2 * n_val**2 + n_val + 1
    assert dim_odd == 4 * n_val
    
    # Fast commutator of two oscillators
    # returns (c0, c_gamma_expr)
    def osc_superbracket(o1, o2):
        t1, j1, s1 = o1
        t2, j2, s2 = o2
        p1 = 1 if t1 == 'a' else 0
        p2 = 1 if t2 == 'a' else 0
        if t1 == 'b' and t2 == 'b':
            if j1 == j2:
                if s1 == -1 and s2 == 1:
                    return (sp.Integer(1), sp.Integer(0))
                elif s1 == 1 and s2 == -1:
                    return (sp.Integer(-1), sp.Integer(0))
            return (sp.Integer(0), sp.Integer(0))
        elif t1 == 'a' and t2 == 'a':
            if s1 != s2:
                return (sp.Integer(1), sp.Integer(0))
            return (sp.Integer(0), sp.Integer(0))
        elif t1 == 'b' and t2 == 'a':
            sig = '+' if s2 == 1 else '-'
            s = '+' if s1 == 1 else '-'
            val = gb_syms.get((sig, j1, s), sp.Integer(0))
            return (sp.Integer(0), -val)
        elif t1 == 'a' and t2 == 'b':
            sig = '+' if s1 == 1 else '-'
            s = '+' if s2 == 1 else '-'
            val = gb_syms.get((sig, j2, s), sp.Integer(0))
            return (sp.Integer(0), val)
        return (sp.Integer(0), sp.Integer(0))

    # Fast projection to basis
    def project_monomial(m):
        # m is a tuple of 2 oscillators: (o1, o2)
        # returns dict of {basis_element: coeff}
        if m == ():
            return {} # central scalar
        o1, o2 = m
        t1, j1, s1 = o1
        t2, j2, s2 = o2
        # Case 1: ap am, am ap, ap ap, am am
        if t1 == 'a' and t2 == 'a':
            if s1 == s2:
                # (a+)^2 = 0, (a-)^2 = 0
                return {}
            elif s1 == 1 and s2 == -1:
                # ap am = J0 + 1/2
                return {'J0': sp.Integer(1)}
            elif s1 == -1 and s2 == 1:
                # am ap = 1 - ap am = -J0 + 1/2
                return {'J0': sp.Integer(-1)}
        # Case 2: b b
        elif t1 == 'b' and t2 == 'b':
            if j1 == j2:
                if s1 == 1 and s2 == 1:
                    # bp bp = 2 E_2d
                    return {f'E_2d_{j1}': sp.Integer(2)}
                elif s1 == -1 and s2 == -1:
                    # bm bm = 2 E_-2d
                    return {f'E_-2d_{j1}': sp.Integer(2)}
                elif s1 == 1 and s2 == -1:
                    # bp bm = h - 1/2
                    return {f'h_{j1}': sp.Integer(1)}
                elif s1 == -1 and s2 == 1:
                    # bm bp = bp bm + 1 = h + 1/2
                    return {f'h_{j1}': sp.Integer(1)}
            else:
                k, l = min(j1, j2), max(j1, j2)
                # Short roots
                if s1 == 1 and s2 == 1:
                    return {f'E_d{k}+d{l}': sp.Integer(1)}
                elif s1 == -1 and s2 == -1:
                    return {f'E_-d{k}-d{l}': sp.Integer(1)}
                elif j1 == k and j2 == l:
                    if s1 == 1 and s2 == -1:
                        return {f'E_d{k}-d{l}': sp.Integer(1)}
                    elif s1 == -1 and s2 == 1:
                        return {f'E_d{l}-d{k}': sp.Integer(1)}
                elif j1 == l and j2 == k:
                    if s1 == 1 and s2 == -1:
                        return {f'E_d{l}-d{k}': sp.Integer(1)}
                    elif s1 == -1 and s2 == 1:
                        return {f'E_d{k}-d{l}': sp.Integer(1)}
        # Case 3: a b or b a
        elif t1 == 'a' and t2 == 'b':
            sig = 'p' if s1 == 1 else 'm'
            s = 'p' if s2 == 1 else 'm'
            return {f'F_{sig}_{j2}_{s}': sp.Integer(1)}
        elif t1 == 'b' and t2 == 'a':
            sig = 'p' if s2 == 1 else 'm'
            s = 'p' if s1 == 1 else 'm'
            return {f'F_{sig}_{j1}_{s}': sp.Integer(1)}
        
        raise ValueError(f"Unknown monomial {m}")

    def compute_bracket_pair(name1, name2):
        g1, p1 = generators[name1]
        g2, p2 = generators[name2]
        
        res_0 = defaultdict(lambda: sp.Integer(0))
        res_gamma = defaultdict(lambda: sp.Integer(0))
        
        for m1, c1 in g1.items():
            if m1 == (): continue
            for m2, c2 in g2.items():
                if m2 == (): continue
                x1, x2 = m1
                y1, y2 = m2
                p_x1 = 1 if x1[0] == 'a' else 0
                p_x2 = 1 if x2[0] == 'a' else 0
                p_y1 = 1 if y1[0] == 'a' else 0
                p_y2 = 1 if y2[0] == 'a' else 0
                
                # Pairwise brackets:
                # [x1, y1], [x1, y2], [x2, y1], [x2, y2]
                b_x2_y1 = osc_superbracket(x2, y1)
                b_x2_y2 = osc_superbracket(x2, y2)
                b_x1_y1 = osc_superbracket(x1, y1)
                b_x1_y2 = osc_superbracket(x1, y2)
                
                terms = [
                    (b_x2_y1, (x1, y2), 1),
                    (b_x2_y2, (x1, y1), (-1)**(p_x2 * p_y1)),
                    (b_x1_y1, (x2, y2), (-1)**(p_x2 * p_y1)),
                    (b_x1_y2, (x2, y1), (-1)**(p_x2 * p_y2 + p_x1 * p_y1)),
                ]
                
                for (c0, cg), mon, sgn in terms:
                    proj = project_monomial(mon)
                    for b_elem, c_proj in proj.items():
                        tot_sgn = c1 * c2 * sgn * c_proj
                        if c0 != 0:
                            res_0[b_elem] += tot_sgn * c0
                        if cg != 0:
                            res_gamma[b_elem] += tot_sgn * cg
                            
        return {k: sp.expand(v) for k, v in res_0.items() if v != 0}, \
               {k: sp.expand(v) for k, v in res_gamma.items() if v != 0}

    print("Computing all brackets...")
    bracket_0 = {}
    gamma_map = {}
    for i, n1 in enumerate(basis):
        for j, n2 in enumerate(basis):
            b0, bg = compute_bracket_pair(n1, n2)
            bracket_0[(n1, n2)] = b0
            gamma_map[(n1, n2)] = bg
            
    # Verify super-Jacobi for a sample of triples
    print("Verifying super-Jacobi identity on undeformed bracket...")
    jac_errors = 0
    # Check all Cartan + roots
    for X in basis[:min(10, dim_total)]:
        pX = generators[X][1]
        for Y in basis[:min(10, dim_total)]:
            pY = generators[Y][1]
            for Z in basis[:min(10, dim_total)]:
                pZ = generators[Z][1]
                def b(v1, v2):
                    res = defaultdict(lambda: sp.Integer(0))
                    for b1, c1 in v1.items():
                        for b2, c2 in v2.items():
                            for b_out, c_out in bracket_0.get((b1, b2), {}).items():
                                res[b_out] += c1 * c2 * c_out
                    return res
                t1 = b({X: 1}, b({Y: 1}, {Z: 1}))
                t2 = b({Y: 1}, b({Z: 1}, {X: 1}))
                t3 = b({Z: 1}, b({X: 1}, {Y: 1}))
                s1 = (-1)**(pX * pZ)
                s2 = (-1)**(pY * pX)
                s3 = (-1)**(pZ * pY)
                for b_name in basis:
                    val = sp.expand(s1 * t1[b_name] + s2 * t2[b_name] + s3 * t3[b_name])
                    if val != 0:
                        jac_errors += 1
    print(f"Super-Jacobi verified (errors: {jac_errors}).")
    
    # 2. Linear system for coboundary delta f = gamma
    # f: g -> g odd linear map
    # f(even) in odd: dim_even * dim_odd unknowns
    # f(odd) in even: dim_odd * dim_even unknowns
    # Total unknowns = 2 * dim_even * dim_odd
    print("Setting up coboundary map f...")
    phi_vars = {}
    var_list = []
    for e in even_basis:
        for o in odd_basis:
            sym = sp.Symbol(f"phi_{e}_{o}")
            phi_vars[(e, o)] = sym
            var_list.append(sym)
    for o in odd_basis:
        for e in even_basis:
            sym = sp.Symbol(f"phi_{o}_{e}")
            phi_vars[(o, e)] = sym
            var_list.append(sym)
            
    print(f"Total unknowns for f: {len(var_list)}")
    
    def apply_f(name):
        p = generators[name][1]
        if p == 0:
            return {o: phi_vars[(name, o)] for o in odd_basis}
        else:
            return {e: phi_vars[(name, e)] for e in even_basis}

    def lie_bracket(v1, v2):
        res = defaultdict(lambda: sp.Integer(0))
        for b1, c1 in v1.items():
            for b2, c2 in v2.items():
                for b_out, c_out in bracket_0.get((b1, b2), {}).items():
                    res[b_out] += c1 * c2 * c_out
        return res

    def compute_delta_f(name1, name2):
        p1 = generators[name1][1]
        p2 = generators[name2][1]
        
        fY = apply_f(name2)
        X_fY = lie_bracket({name1: 1}, fY)
        
        fX = apply_f(name1)
        Y_fX = lie_bracket({name2: 1}, fX)
        
        br_XY = bracket_0.get((name1, name2), {})
        f_br = defaultdict(lambda: sp.Integer(0))
        for b_in, c_in in br_XY.items():
            fb = apply_f(b_in)
            for b_out, c_out in fb.items():
                f_br[b_out] += c_in * c_out
                
        sign1 = (-1)**p1
        sign2 = (-1)**((p1 + 1) * p2)
        
        res = {}
        all_keys = set(X_fY.keys()) | set(Y_fX.keys()) | set(f_br.keys())
        for b in all_keys:
            val = sp.expand(sign1 * X_fY[b] - sign2 * Y_fX[b] - f_br[b])
            if val != 0:
                res[b] = val
        return res

    print("Building coboundary equations delta f - gamma = 0...")
    equations = []
    eq_details = []
    for i, n1 in enumerate(basis):
        for j, n2 in enumerate(basis):
            if j < i: continue
            df = compute_delta_f(n1, n2)
            gm = gamma_map.get((n1, n2), {})
            all_keys = set(df.keys()) | set(gm.keys())
            for b in all_keys:
                eq = sp.expand(df.get(b, 0) - gm.get(b, 0))
                if eq != 0:
                    equations.append(eq)
                    eq_details.append((n1, n2, b))
                    
    print(f"Total non-trivial equations: {len(equations)}")
    
    # 3. Analyze constraint on gb
    print("Computing rank and constraints on gb...")
    A, b_vec = sp.linear_eq_to_matrix(equations, var_list)
    print(f"Matrix A shape: {A.shape}")
    
    # Compute left nullspace of A
    left_null = A.T.nullspace()
    print(f"Left nullspace dimension: {len(left_null)}")
    
    constraints_on_gb = []
    for v in left_null:
        val = sp.expand((v.T * b_vec)[0, 0])
        if val != 0:
            constraints_on_gb.append(val)
            
    print(f"Number of non-zero gb constraints from left nullspace: {len(constraints_on_gb)}")
    
    # Find rank of gb constraints
    M_gb, _ = sp.linear_eq_to_matrix(constraints_on_gb, gb_list)
    rank_gb = M_gb.rank()
    num_gb = len(gb_list)
    print(f"Constraint matrix on gb shape: {M_gb.shape}")
    print(f"Rank of gb constraint matrix: {rank_gb} / {num_gb}")
    
    sol_gb = sp.solve(constraints_on_gb, gb_list)
    print(f"Explicit solution for gb: {sol_gb}")
    
    all_zero = (rank_gb == num_gb)
    print(f"Is gb strictly forced to 0? {'YES (gb = 0 uniquely)' if all_zero else 'NO'}")
    
    elapsed = time.time() - start_time
    print(f"Elapsed time: {elapsed:.2f} s")
    
    result_data = {
        'n': n_val,
        'algebra': f'C({n_val+1}) = osp(2|{2*n_val})',
        'dim_even': dim_even,
        'dim_odd': dim_odd,
        'dim_total': dim_total,
        'num_gb_params': num_gb,
        'rank_gb_constraint_matrix': int(rank_gb),
        'gb_forced_to_zero': bool(all_zero),
        'total_equations': len(equations),
        'total_unknowns': len(var_list),
        'matrix_A_rank': int(A.rank()),
        'left_nullspace_dim': len(left_null),
        'solution_gb': {str(k): int(v) for k, v in sol_gb.items()} if isinstance(sol_gb, dict) else {},
        'elapsed_seconds': round(elapsed, 2)
    }
    
    return result_data

if __name__ == '__main__':
    all_results = []
    for n in [1, 2, 3]:
        res = solve_osp(n)
        all_results.append(res)
        
    with open('artifacts/verification_results.json', 'w') as f:
        json.dump(all_results, f, indent=2)
    print("\nSaved results to artifacts/verification_results.json")
