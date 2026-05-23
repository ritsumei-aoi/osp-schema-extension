
import numpy as np

class Term:
    def __init__(self, oscillators, coeff=1.0, kappa=0):
        self.oscillators = list(oscillators)
        self.coeff = coeff
        self.kappa = kappa

    def copy(self):
        return Term(self.oscillators, self.coeff, self.kappa)

def simplify_expression(terms):
    combined = {}
    for t in terms:
        if abs(t.coeff) < 1e-10: continue
        key = (tuple(t.oscillators), t.kappa)
        combined[key] = combined.get(key, 0) + t.coeff
    res = []
    for key, coeff in combined.items():
        if abs(coeff) > 1e-10:
            res.append(Term(key[0], coeff, key[1]))
    return res

def get_parity(name):
    if name.startswith('a'): return 1
    if name.startswith('b'): return 0
    return 0

def get_parity_expr(term):
    p = term.kappa % 2
    for o in term.oscillators:
        p = (p + get_parity(o)) % 2
    return p

def get_order(name, n):
    if name == 'a+': return 0
    if name == 'a-': return 1
    if name.startswith('b'):
        idx = int(name[1:-1])
        sign = 0 if name.endswith('+') else 1
        return 2 + (idx - 1) * 2 + sign
    return 999

def normal_order(term, g, n):
    current_terms = [term]
    changed = True
    while changed:
        changed = False
        new_terms = []
        for t in current_terms:
            if t.kappa > 1: continue
            idx = -1
            for i in range(len(t.oscillators) - 1):
                if get_order(t.oscillators[i], n) > get_order(t.oscillators[i+1], n):
                    idx = i
                    break
            if idx == -1:
                new_terms.append(t)
                continue
            changed = True
            o1, o2 = t.oscillators[idx], t.oscillators[idx+1]
            p1, p2 = get_parity(o1), get_parity(o2)
            prefix, suffix = t.oscillators[:idx], t.oscillators[idx+2:]
            sign = -1 if (p1 == 1 and p2 == 1) else 1
            new_terms.append(Term(prefix + [o2, o1] + suffix, t.coeff * sign, t.kappa))
            
            bracket_val = 0
            bracket_kappa = 0
            if (o1 == 'a-' and o2 == 'a+') or (o1 == 'a+' and o2 == 'a-'):
                bracket_val = 1
            elif o1.startswith('b') and o2.startswith('b'):
                idx1 = int(o1[1:-1])
                idx2 = int(o2[1:-1])
                if idx1 == idx2:
                    if o1.endswith('-') and o2.endswith('+'): bracket_val = 1
                    elif o1.endswith('+') and o2.endswith('-'): bracket_val = -1
            elif o1.startswith('b') and o2.startswith('a'):
                bracket_kappa = 1
                bracket_val = -g.get((o2, o1), 0)
            elif o1.startswith('a') and o2.startswith('b'):
                bracket_kappa = 1
                bracket_val = g.get((o1, o2), 0)
            
            if bracket_val != 0:
                new_terms.append(Term(prefix + suffix, t.coeff * bracket_val, t.kappa + bracket_kappa))
        current_terms = simplify_expression(new_terms)
    return current_terms

def bracket(expr1, expr2, g, n):
    res = []
    for t1 in expr1:
        p1 = get_parity_expr(t1)
        for t2 in expr2:
            p2 = get_parity_expr(t2)
            res.append(Term(t1.oscillators + t2.oscillators, t1.coeff * t2.coeff, t1.kappa + t2.kappa))
            sign = -1 if (p1 == 1 and p2 == 1) else 1
            res.append(Term(t2.oscillators + t1.oscillators, -t1.coeff * t2.coeff * sign, t1.kappa + t2.kappa))
    simplified = simplify_expression(res)
    final = []
    for t in simplified:
        final.extend(normal_order(t, g, n))
    return simplify_expression(final)

def get_basis(n):
    basis = {}
    # Even part
    basis['Ja'] = [Term(['a+', 'a-'], 1.0), Term([], -0.5)] # so(2) generator
    for i in range(1, n + 1):
        for j in range(i, n + 1):
            if i == j:
                basis[f'H_b{i}'] = [Term([f'b{i}+', f'b{i}-'], 1.0), Term([], 0.5)]
                basis[f'E_2d{i}'] = [Term([f'b{i}+', f'b{i}+'], 0.5)]
                basis[f'F_2d{i}'] = [Term([f'b{i}-', f'b{i}-'], 0.5)]
            else:
                basis[f'E_dp{i}{j}'] = [Term([f'b{i}+', f'b{j}+'], 1.0)]
                basis[f'E_dm{i}{j}'] = [Term([f'b{i}-', f'b{j}-'], 1.0)]
                basis[f'E_dpm{i}{j}'] = [Term([f'b{i}+', f'b{j}-'], 1.0)]
                basis[f'E_dmp{i}{j}'] = [Term([f'b{i}-', f'b{j}+'], 1.0)]
    # Odd part
    for i in range(1, n + 1):
        basis[f'O_pp{i}'] = [Term(['a+', f'b{i}+'], 1.0)]
        basis[f'O_pm{i}'] = [Term(['a+', f'b{i}-'], 1.0)]
        basis[f'O_mp{i}'] = [Term(['a-', f'b{i}+'], 1.0)]
        basis[f'O_mm{i}'] = [Term(['a-', f'b{i}-'], 1.0)]
    return basis

def analyze_triviality(n):
    print(f"\nAnalyzing C({n+1})...")
    basis = get_basis(n)
    all_names = list(basis.keys())
    even_names = [name for name in all_names if get_parity_expr(basis[name][0]) == 0]
    odd_names = [name for name in all_names if get_parity_expr(basis[name][0]) == 1]
    
    # Pre-normalize basis
    g0 = {}
    norm_basis = {name: simplify_expression([t2 for t1 in exprs for t2 in normal_order(t1, g0, n)]) 
                  for name, exprs in basis.items()}
    
    def expr_to_vec(expr):
        remaining = simplify_expression(expr)
        terms_in_expr = set()
        for t in remaining: terms_in_expr.add((tuple(t.oscillators), t.kappa))
        for name in all_names:
            for t in norm_basis[name]: terms_in_expr.add((tuple(t.oscillators), t.kappa))
        term_to_idx = {term: i for i, term in enumerate(sorted(list(terms_in_expr)))}
        matrix = np.zeros((len(term_to_idx), len(all_names)))
        for j, name in enumerate(all_names):
            for t in norm_basis[name]: matrix[term_to_idx[(tuple(t.oscillators), t.kappa)], j] = t.coeff
        target = np.zeros(len(term_to_idx))
        for t in remaining: target[term_to_idx[(tuple(t.oscillators), t.kappa)]] = t.coeff
        sol, residuals, rank, s = np.linalg.lstsq(matrix, target, rcond=None)
        return sol

    # Deformations
    g_vars = []
    for i in range(1, n + 1):
        for sigma in ['+', '-']:
            for s in ['+', '-']:
                g_vars.append((sigma, i, s))
    
    # f parameters (odd map)
    f_vars = []
    for en in even_names:
        for on in odd_names: f_vars.append((en, on))
    for on in odd_names:
        for en in even_names: f_vars.append((on, en))
    
    num_f = len(f_vars)
    num_g = len(g_vars)
    
    pairs = []
    for i in range(len(all_names)):
        for j in range(i + 1, len(all_names)): pairs.append((all_names[i], all_names[j]))
    
    # Matrix for delta f
    # df_matrix[pair_idx * num_basis + comp_idx, f_idx]
    num_eqs = len(pairs) * len(all_names)
    df_matrix = np.zeros((num_eqs, num_f))
    
    print(f"Building delta f matrix ({num_eqs} x {num_f})...")
    for f_idx, (src, dst) in enumerate(f_vars):
        f_params = {name: np.zeros(len(all_names)) for name in all_names}
        f_params[src][all_names.index(dst)] = 1.0
        
        # We need a function to compute delta f(X, Y)
        # To speed up, we pre-calculate brackets
        pass 

    # Re-implementing get_delta_f locally for speed
    def get_df_vec(X_name, Y_name, f_params):
        X, Y = basis[X_name], basis[Y_name]
        pX = 0 if X_name in even_names else 1
        pY = 0 if Y_name in even_names else 1
        fX_vec = f_params[X_name]
        fY_vec = f_params[Y_name]
        fX = []
        for i, c in enumerate(fX_vec):
            if abs(c) > 1e-10:
                for t in basis[all_names[i]]:
                    t2 = t.copy(); t2.coeff *= c; fX.append(t2)
        fY = []
        for i, c in enumerate(fY_vec):
            if abs(c) > 1e-10:
                for t in basis[all_names[i]]:
                    t2 = t.copy(); t2.coeff *= c; fY.append(t2)
        term1 = bracket(X, fY, {}, n)
        term2 = bracket(Y, fX, {}, n)
        XY = bracket(X, Y, {}, n)
        XY_vec = expr_to_vec(XY)
        fXY = np.zeros(len(all_names))
        for i, c in enumerate(XY_vec):
            if abs(c) > 1e-10: fXY += c * f_params[all_names[i]]
        res_expr = []
        s1 = -1 if pX == 1 else 1
        for t in term1: t2 = t.copy(); t2.coeff *= s1; res_expr.append(t2)
        s2 = -1 if (pX + 1) * pY % 2 == 1 else 1
        for t in term2: t2 = t.copy(); t2.coeff *= -s2; res_expr.append(t2)
        return expr_to_vec(res_expr) - fXY

    for f_idx, (src, dst) in enumerate(f_vars):
        f_params = {name: np.zeros(len(all_names)) for name in all_names}
        f_params[src][all_names.index(dst)] = 1.0
        for p_idx, (X_name, Y_name) in enumerate(pairs):
            df_vec = get_df_vec(X_name, Y_name, f_params)
            for comp in range(len(all_names)):
                df_matrix[p_idx * len(all_names) + comp, f_idx] = df_vec[comp]
                
    # Matrix for gamma
    gamma_matrix = np.zeros((num_eqs, num_g))
    print(f"Building gamma matrix ({num_eqs} x {num_g})...")
    for g_idx, (sigma, i_idx, s) in enumerate(g_vars):
        g_params = {(f'a{sigma}', f'b{i_idx}{s}'): 1.0}
        for p_idx, (X_name, Y_name) in enumerate(pairs):
            # get_gamma logic
            res = bracket(basis[X_name], basis[Y_name], g_params, n)
            gamma_terms = [t for t in res if t.kappa == 1]
            for t in gamma_terms: t.kappa = 0
            gamma_vec = expr_to_vec(gamma_terms)
            for comp in range(len(all_names)):
                gamma_matrix[p_idx * len(all_names) + comp, g_idx] = gamma_vec[comp]
                
    # Find subspace of gamma that is in colspace of df_matrix
    # Projection matrix P onto orthogonal complement of colspace(df_matrix)
    print("Computing SVD...")
    U, S, Vh = np.linalg.svd(df_matrix, full_matrices=False)
    rank_df = np.sum(S > 1e-10)
    U_perp = np.eye(num_eqs) - U[:, :rank_df] @ U[:, :rank_df].T
    
    projected_gamma = U_perp @ gamma_matrix
    # Null space of projected_gamma gives trivial combinations
    print("Computing null space of projected gamma...")
    Ug, Sg, Vhg = np.linalg.svd(projected_gamma)
    
    # rank of projected_gamma
    rank_pg = np.sum(Sg > 1e-10)
    print(f"Rank of df_matrix: {rank_df}")
    print(f"Rank of projected_gamma: {rank_pg}")
    print(f"Number of g parameters: {num_g}")
    
    num_trivial = num_g - rank_pg
    print(f"Number of trivial combinations: {num_trivial}")
    
    if num_trivial > 0:
        print("Trivial combinations found:")
        for i in range(rank_pg, num_g):
            vec = Vhg[i]
            print(vec)
    else:
        print("No trivial combinations found (except 0).")

def output_structured_data(n):
    basis = get_basis(n)
    all_names = list(basis.keys())
    g0 = {}
    norm_basis = {name: simplify_expression([t2 for t1 in exprs for t2 in normal_order(t1, g0, n)]) 
                  for name, exprs in basis.items()}
    
    # We'll just output n=1 for brevity
    if n != 1: return
    
    print("\nSTRUCTURED DATA (n=1)")
    print("BASIS_GENERATORS = {")
    for name, terms in norm_basis.items():
        terms_str = [(t.oscillators, t.coeff) for t in terms]
        print(f"    '{name}': {terms_str},")
    print("}")
    
    g_vars = [('+', 1, '+'), ('+', 1, '-'), ('-', 1, '+'), ('-', 1, '-')]
    pairs = []
    for i in range(len(all_names)):
        for j in range(i + 1, len(all_names)): pairs.append((all_names[i], all_names[j]))
        
    print("\nGAMMA_STRUCTURES = {")
    for g_var in g_vars:
        g_params = {(f'a{g_var[0]}', f'b{g_var[1]}{g_var[2]}'): 1.0}
        print(f"    'g_{g_var}': {{")
        for X_name, Y_name in pairs:
            res = bracket(basis[X_name], basis[Y_name], g_params, n)
            gamma_terms = [t for t in res if t.kappa == 1]
            if not gamma_terms: continue
            for t in gamma_terms: t.kappa = 0
            # Simplify gamma_terms
            gamma_terms = simplify_expression(gamma_terms)
            gamma_str = [(t.oscillators, t.coeff) for t in gamma_terms]
            print(f"        ('{X_name}', '{Y_name}'): {gamma_str},")
        print("    },")
    print("}")

if __name__ == "__main__":
    analyze_triviality(1)
    analyze_triviality(2)
    analyze_triviality(3)
    output_structured_data(1)
