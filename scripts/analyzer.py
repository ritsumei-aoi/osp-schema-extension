import sympy as sp
from collections import defaultdict
import json

def run_analysis(n):
    print(f"\n==========================================")
    print(f"       ANALYZING C({n+1}) = osp(2|{2*n})")
    print(f"==========================================")
    
    # Oscillators:
    osc_list = ['a+', 'a-']
    for k in range(1, n + 1):
        osc_list.extend([f'b+{k}', f'b-{k}'])
    
    osc_order = {name: i for i, name in enumerate(osc_list)}
    parity = {name: (1 if name.startswith('a') else 0) for name in osc_list}
    
    # Deformation parameters gb_{sigma, j, s}
    gb_syms = {}
    for sigma in ['+', '-']:
        for j in range(1, n + 1):
            for s in ['+', '-']:
                sym_name = f"gb_{sigma}_{j}_{s}"
                gb_syms[(sigma, j, s)] = sp.Symbol(sym_name)
                
    # Commutators of oscillators:
    def C0(u, v):
        if u.startswith('b-') and v.startswith('b+'):
            if u[2:] == v[2:]: return sp.Integer(1)
        if u.startswith('b+') and v.startswith('b-'):
            if u[2:] == v[2:]: return sp.Integer(-1)
        if (u == 'a-' and v == 'a+') or (u == 'a+' and v == 'a-'):
            return sp.Integer(1)
        return sp.Integer(0)
    
    def C1(u, v):
        if u.startswith('b') and v.startswith('a'):
            s = u[1]
            j = int(u[2:])
            sigma = v[1]
            return -gb_syms[(sigma, j, s)]
        if u.startswith('a') and v.startswith('b'):
            sigma = u[1]
            s = v[1]
            j = int(v[2:])
            return gb_syms[(sigma, j, s)]
        return sp.Integer(0)
    
    # Reduction of word to normal order
    def reduce_word(word, has_kappa=False):
        for i in range(len(word) - 1):
            if word[i] == word[i+1] and parity[word[i]] == 1:
                return {}
                
        for i in range(len(word) - 1):
            u, v = word[i], word[i+1]
            if osc_order[u] > osc_order[v]:
                sign = -1 if (parity[u] == 1 and parity[v] == 1) else 1
                c0 = C0(u, v)
                c1 = C1(u, v) if not has_kappa else sp.Integer(0)
                
                # Term 1: swap u and v
                w_swap = word[:i] + (v, u) + word[i+2:]
                res_swap = reduce_word(w_swap, has_kappa=has_kappa)
                
                total = defaultdict(lambda: [sp.Integer(0), sp.Integer(0)])
                for w, (val0, val1) in res_swap.items():
                    total[w][0] += sign * val0
                    total[w][1] += sign * val1
                    
                # Term 2: contraction with c0
                if c0 != 0:
                    w_c0 = word[:i] + word[i+2:]
                    res_c0 = reduce_word(w_c0, has_kappa=has_kappa)
                    for w, (val0, val1) in res_c0.items():
                        total[w][0] += c0 * val0
                        total[w][1] += c0 * val1
                        
                # Term 3: contraction with c1 (only if not has_kappa)
                if c1 != 0 and not has_kappa:
                    w_c1 = word[:i] + word[i+2:]
                    res_c1 = reduce_word(w_c1, has_kappa=False)
                    for w, (val0, _) in res_c1.items():
                        total[w][1] += c1 * val0
                        
                return {w: (sp.simplify(vals[0]), sp.simplify(vals[1])) 
                        for w, vals in total.items() if vals[0] != 0 or vals[1] != 0}
                
        for i in range(len(word) - 1):
            if word[i] == word[i+1] and parity[word[i]] == 1:
                return {}
        return {word: (sp.Integer(0) if has_kappa else sp.Integer(1), 
                       sp.Integer(1) if has_kappa else sp.Integer(0))}

    # Build basis of g = C(n+1)
    basis = {}
    basis_parity = {}
    
    basis['H1'] = {('a+', 'a-'): sp.Integer(1), (f'b+1', f'b-1'): sp.Integer(1)}
    basis_parity['H1'] = 0
    for k in range(2, n + 1):
        basis[f'H{k}'] = {(f'b+{k-1}', f'b-{k-1}'): sp.Integer(1), (f'b+{k}', f'b-{k}'): sp.Integer(-1)}
        basis_parity[f'H{k}'] = 0
    basis[f'H{n+1}'] = {(f'b+{n}', f'b-{n}'): sp.Integer(-1), (): -sp.Rational(1, 2)}
    basis_parity[f'H{n+1}'] = 0
    
    for k in range(1, n + 1):
        basis[f'E_2d{k}'] = {(f'b+{k}', f'b+{k}'): sp.Rational(1, 2)}
        basis_parity[f'E_2d{k}'] = 0
        basis[f'E_-2d{k}'] = {(f'b-{k}', f'b-{k}'): sp.Rational(1, 2)}
        basis_parity[f'E_-2d{k}'] = 0
        
    for k in range(1, n + 1):
        for l in range(1, n + 1):
            if k != l:
                if osc_order[f'b+{k}'] < osc_order[f'b-{l}']:
                    basis[f'E_d{k}-d{l}'] = {(f'b+{k}', f'b-{l}'): sp.Integer(1)}
                else:
                    basis[f'E_d{k}-d{l}'] = {(f'b-{l}', f'b+{k}'): sp.Integer(1)}
                basis_parity[f'E_d{k}-d{l}'] = 0
                
    for k in range(1, n + 1):
        for l in range(k + 1, n + 1):
            basis[f'E_d{k}+d{l}'] = {(f'b+{k}', f'b+{l}'): sp.Integer(1)}
            basis_parity[f'E_d{k}+d{l}'] = 0
            basis[f'E_-d{k}-d{l}'] = {(f'b-{k}', f'b-{l}'): sp.Integer(1)}
            basis_parity[f'E_-d{k}-d{l}'] = 0
            
    for k in range(1, n + 1):
        basis[f'E_eps+d{k}'] = {('a+', f'b+{k}'): sp.Integer(1)}
        basis_parity[f'E_eps+d{k}'] = 1
        basis[f'E_eps-d{k}'] = {('a+', f'b-{k}'): sp.Integer(1)}
        basis_parity[f'E_eps-d{k}'] = 1
        basis[f'E_-eps+d{k}'] = {('a-', f'b+{k}'): sp.Integer(1)}
        basis_parity[f'E_-eps+d{k}'] = 1
        basis[f'E_-eps-d{k}'] = {('a-', f'b-{k}'): sp.Integer(1)}
        basis_parity[f'E_-eps-d{k}'] = 1
        
    basis_names = list(basis.keys())
    dim_total = len(basis_names)
    dim_even = sum(1 for name in basis_names if basis_parity[name] == 0)
    dim_odd = sum(1 for name in basis_names if basis_parity[name] == 1)
    print(f"Dimension check: Total = {dim_total}, Even = {dim_even}, Odd = {dim_odd}")
    
    # Quadratic monomials list
    quad_monomials = set()
    for b_dict in basis.values():
        for m in b_dict.keys():
            if len(m) == 2:
                quad_monomials.add(m)
    quad_list = sorted(list(quad_monomials), key=lambda m: [osc_order[x] for x in m])
    
    # Matrix M_quad
    M_quad = sp.zeros(len(quad_list), len(basis_names))
    for j, name in enumerate(basis_names):
        for m, c in basis[name].items():
            if len(m) == 2:
                i = quad_list.index(m)
                M_quad[i, j] = c
                
    # Invert M_quad once
    M_quad_inv = M_quad.inv()
    
    # Function to express any element in basis modulo scalars (up to scalar)
    def express_in_basis(elem_dict):
        v = sp.zeros(len(quad_list), 1)
        for w, c in elem_dict.items():
            if len(w) == 2:
                if w in quad_list:
                    v[quad_list.index(w), 0] = c
                else:
                    raise ValueError(f"Quadratic monomial {w} not recognized!")
        # Solution x = M_quad_inv * v
        x = M_quad_inv * v
        return {basis_names[j]: sp.simplify(x[j, 0]) for j in range(len(basis_names)) if sp.simplify(x[j, 0]) != 0}

    # Compute associative bracket [X, Y]
    def compute_bracket(name_X, name_Y):
        pX = basis_parity[name_X]
        pY = basis_parity[name_Y]
        sign_super = -1 if (pX == 1 and pY == 1) else 1
        
        dict_X = basis[name_X]
        dict_Y = basis[name_Y]
        
        res0 = defaultdict(lambda: sp.Integer(0))
        res1 = defaultdict(lambda: sp.Integer(0))
        
        # XY
        for wX, cX in dict_X.items():
            for wY, cY in dict_Y.items():
                c_prod = cX * cY
                red = reduce_word(wX + wY, has_kappa=False)
                for w, (v0, v1) in red.items():
                    res0[w] += c_prod * v0
                    res1[w] += c_prod * v1
                    
        # - (-1)^{pX pY} YX
        for wY, cY in dict_Y.items():
            for wX, cX in dict_X.items():
                c_prod = -sign_super * cY * cX
                red = reduce_word(wY + wX, has_kappa=False)
                for w, (v0, v1) in red.items():
                    res0[w] += c_prod * v0
                    res1[w] += c_prod * v1
                    
        elem0 = {w: sp.simplify(c) for w, c in res0.items() if c != 0}
        elem1 = {w: sp.simplify(c) for w, c in res1.items() if c != 0}
        
        basis_coeff0 = express_in_basis(elem0)
        basis_coeff1 = express_in_basis(elem1)
        return basis_coeff0, basis_coeff1

    print("Computing brackets for all pairs of basis elements...")
    bracket_0 = {}
    gamma_gb = {}
    
    for i, name_X in enumerate(basis_names):
        for j in range(i, len(basis_names)):
            name_Y = basis_names[j]
            b0, b1 = compute_bracket(name_X, name_Y)
            bracket_0[(name_X, name_Y)] = b0
            gamma_gb[(name_X, name_Y)] = b1
                
    print("Brackets computed successfully! Verified closure in g up to scalar.")
    
    # Verify Lie superalgebra Jacobi identity for [ , ]_0
    def eval_b0(name_X, name_Y):
        if (name_X, name_Y) in bracket_0:
            return bracket_0[(name_X, name_Y)]
        else:
            pX = basis_parity[name_X]
            pY = basis_parity[name_Y]
            sign = -1 if (pX == 1 and pY == 1) else 1
            inv = bracket_0[(name_Y, name_X)]
            return {k: -sign * v for k, v in inv.items()}
            
    jacobi_errors = 0
    triples_to_test = []
    for i in range(len(basis_names)):
        for j in range(i, len(basis_names)):
            for k in range(j, len(basis_names)):
                triples_to_test.append((basis_names[i], basis_names[j], basis_names[k]))
                
    print(f"Testing Jacobi on {len(triples_to_test)} triples...")
    for X, Y, Z in triples_to_test:
        pX, pY, pZ = basis_parity[X], basis_parity[Y], basis_parity[Z]
        def bracket_gen_dict(name_W, b_dict):
            res = defaultdict(lambda: sp.Integer(0))
            for k, c in b_dict.items():
                bw = eval_b0(name_W, k)
                for gen, val in bw.items():
                    res[gen] += c * val
            return {k: sp.simplify(v) for k, v in res.items() if v != 0}
            
        t1 = bracket_gen_dict(X, eval_b0(Y, Z))
        t2 = bracket_gen_dict(Y, eval_b0(Z, X))
        t3 = bracket_gen_dict(Z, eval_b0(X, Y))
        
        s1 = -1 if (pX * pZ) % 2 == 1 else 1
        s2 = -1 if (pY * pX) % 2 == 1 else 1
        s3 = -1 if (pZ * pY) % 2 == 1 else 1
        
        jac = defaultdict(lambda: sp.Integer(0))
        for g, c in t1.items(): jac[g] += s1 * c
        for g, c in t2.items(): jac[g] += s2 * c
        for g, c in t3.items(): jac[g] += s3 * c
        for g, c in jac.items():
            if sp.simplify(c) != 0:
                jacobi_errors += 1
                break
                
    if jacobi_errors == 0:
        print("Undeformed Jacobi identity holds EXACTLY for all triples!")
    else:
        print(f"Jacobi failed in {jacobi_errors} triples.")
        
    return basis_names, basis_parity, bracket_0, gamma_gb, gb_syms

if __name__ == '__main__':
    run_analysis(1)
