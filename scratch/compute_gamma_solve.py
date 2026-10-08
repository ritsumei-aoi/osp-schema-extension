import sympy as sp
from collections import defaultdict
import sys

def epsilon(s1, s2):
    if s1 == '+' and s2 == '-': return -1
    if s1 == '-' and s2 == '+': return 1
    return 0

def get_S(k, l, s1, s2):
    if (k, s1) > (l, s2):
        return ('S', l, k, s2, s1)
    return ('S', k, l, s1, s2)

def bracket(X, Y):
    # Returns a list of (coeff, element)
    typeX = X[0]
    typeY = Y[0]

    if typeX == 'C' and typeY == 'C':
        return []
    
    if typeX == 'C' and typeY == 'S':
        return []
    
    if typeX == 'S' and typeY == 'C':
        return []

    if typeX == 'S' and typeY == 'S':
        _, k, l, s1, s2 = X
        _, m, n, s3, s4 = Y
        res = defaultdict(int)
        
        def add(coeff, elem):
            if coeff != 0:
                res[elem] += coeff
        
        add(epsilon(s2, s4) * (1 if l==n else 0), get_S(k, m, s1, s3))
        add(epsilon(s2, s3) * (1 if l==m else 0), get_S(k, n, s1, s4))
        add(epsilon(s1, s4) * (1 if k==n else 0), get_S(m, l, s3, s2))
        add(epsilon(s1, s3) * (1 if k==m else 0), get_S(n, l, s4, s2))
        
        return [(c, e) for e, c in res.items() if c != 0]

    if typeX == 'C' and typeY == 'F':
        _, k, sigma, s = Y
        sig_val = 1 if sigma == '+' else -1
        return [(sig_val, Y)]

    if typeX == 'F' and typeY == 'C':
        # [F, C] = - [C, F] since both are not odd (C is even)
        _, k, sigma, s = X
        sig_val = 1 if sigma == '+' else -1
        return [(-sig_val, X)]

    if typeX == 'S' and typeY == 'F':
        _, k, l, s1, s2 = X
        _, m, sigma, s = Y
        res = defaultdict(int)
        if l == m:
            res[('F', k, sigma, s1)] += epsilon(s2, s)
        if k == m:
            res[('F', l, sigma, s2)] += epsilon(s1, s)
        return [(c, e) for e, c in res.items() if c != 0]

    if typeX == 'F' and typeY == 'S':
        # [F, S] = - [S, F]
        res = bracket(Y, X)
        return [(-c, e) for c, e in res]

    if typeX == 'F' and typeY == 'F':
        # {F, F}
        _, k, sigma1, s1 = X
        _, l, sigma2, s2 = Y
        if sigma1 == sigma2:
            return []
        
        res = defaultdict(int)
        res[get_S(k, l, s1, s2)] += 1
        sig_val = 1 if sigma1 == '+' else -1
        if k == l:
            res[('C',)] += sig_val * epsilon(s1, s2)
            
        return [(c, e) for e, c in res.items() if c != 0]

def p(X):
    if X[0] == 'F': return 1
    return 0

def get_gamma(X, Y, gb):
    typeX = X[0]
    typeY = Y[0]
    
    if typeX == 'C' and typeY == 'C': return []
    if typeX == 'S' and typeY == 'S': return []
    if typeX == 'C' and typeY == 'S': return []
    if typeX == 'S' and typeY == 'C': return []
    
    if typeX == 'C' and typeY == 'F':
        _, k, sigma, s = Y
        return [(-gb[(sigma, k, s)], ('C',))]
    
    if typeX == 'F' and typeY == 'C':
        # gamma(F, C) = (-1)^{p(F)p(C)}? Wait, gamma is a cocycle for the bracket.
        # [X, Y]_gamma = ...
        # gamma(X, Y) = - (-1)^{p(X)p(Y)} gamma(Y, X)
        # So gamma(F, C) = - gamma(C, F)
        _, k, sigma, s = X
        return [(gb[(sigma, k, s)], ('C',))]

    if typeX == 'S' and typeY == 'F':
        _, k, l, s1, s2 = X
        _, m, sigma, s = Y
        res = defaultdict(int)
        # gamma(S^{s1,s2}_{k,l}, F_m^{sigma, s}) = - gb_{sigma, k, s1} S^{s2, s}_{l, m} - gb_{sigma, l, s2} S^{s1, s}_{k, m}
        res[get_S(l, m, s2, s)] += - gb[(sigma, k, s1)]
        res[get_S(k, m, s1, s)] += - gb[(sigma, l, s2)]
        return [(c, e) for e, c in res.items() if c != 0]

    if typeX == 'F' and typeY == 'S':
        # gamma(F, S) = - gamma(S, F)
        res = get_gamma(Y, X, gb)
        return [(-c, e) for c, e in res]

    if typeX == 'F' and typeY == 'F':
        _, k, sigma1, s1 = X
        _, l, sigma2, s2 = Y
        res = defaultdict(int)
        # gamma(F_k^{sigma, s}, F_l^{sigma', s'}) = gb_{sigma', k, s} F_l^{sigma, s'} + gb_{sigma, l, s'} F_k^{sigma', s}
        res[('F', l, sigma1, s2)] += gb[(sigma2, k, s1)]
        res[('F', k, sigma2, s1)] += gb[(sigma1, l, s2)]
        return [(c, e) for e, c in res.items() if c != 0]

def main():
    n = 1
    if len(sys.argv) > 1:
        n = int(sys.argv[1])
        
    print(f"Solving for n={n}")
    
    basis = []
    basis.append(('C',))
    for k in range(1, n+1):
        for l in range(k, n+1):
            for s1 in ['+', '-']:
                for s2 in ['+', '-']:
                    if k == l and s1 == '-' and s2 == '+':
                        continue # symmetric, handled by get_S
                    basis.append(get_S(k, l, s1, s2))
    
    basis = list(set(basis))
    
    for k in range(1, n+1):
        for sigma in ['+', '-']:
            for s in ['+', '-']:
                basis.append(('F', k, sigma, s))

    # create gb symbols
    gb = {}
    for sigma in ['+', '-']:
        for k in range(1, n+1):
            for s in ['+', '-']:
                gb[(sigma, k, s)] = sp.Symbol(f"gb_{sigma}_{k}_{s}")
                
    # create f symbols
    f_syms = {}
    # f maps even to odd, odd to even
    for b in basis:
        f_syms[b] = {}
        if p(b) == 0:
            for b_out in basis:
                if p(b_out) == 1:
                    f_syms[b][b_out] = sp.Symbol(f"f_{b}_{b_out}")
        else:
            for b_out in basis:
                if p(b_out) == 0:
                    f_syms[b][b_out] = sp.Symbol(f"f_{b}_{b_out}")
                    
    def apply_f(X):
        return [(f_syms[X][b_out], b_out) for b_out in f_syms[X]]

    # build equations
    # delta f(X, Y) = (-1)^{p(X)} [X, f(Y)] - (-1)^{(p(X)+1)p(Y)} [Y, f(X)] - f([X, Y])
    
    eqs = []
    
    for i, X in enumerate(basis):
        for j, Y in enumerate(basis):
            if i > j: continue # graded symmetric, so we only need i <= j
            # compute gamma
            gamma_terms = get_gamma(X, Y, gb)
            
            # compute delta f
            delta_f_terms = defaultdict(int)
            
            # 1: (-1)^{p(X)} [X, f(Y)]
            sign1 = -1 if p(X) == 1 else 1
            for c_fY, b_fY in apply_f(Y):
                for c_br, b_br in bracket(X, b_fY):
                    delta_f_terms[b_br] += sign1 * c_fY * c_br
                    
            # 2: - (-1)^{(p(X)+1)p(Y)} [Y, f(X)]
            sign2 = -1 if ((p(X)+1)*p(Y)) % 2 == 1 else 1
            for c_fX, b_fX in apply_f(X):
                for c_br, b_br in bracket(Y, b_fX):
                    delta_f_terms[b_br] -= sign2 * c_fX * c_br
                    
            # 3: - f([X, Y])
            for c_br, b_br in bracket(X, Y):
                for c_f, b_f in apply_f(b_br):
                    delta_f_terms[b_f] -= c_br * c_f
                    
            # equation: gamma_terms = delta_f_terms
            gamma_dict = defaultdict(int)
            for c, b in gamma_terms:
                gamma_dict[b] += c
                
            all_b = set(gamma_dict.keys()).union(set(delta_f_terms.keys()))
            for b in all_b:
                eq = gamma_dict[b] - delta_f_terms[b]
                if eq != 0:
                    eqs.append(eq)

    print(f"Generated {len(eqs)} equations.")
    
    # solve for f_syms in terms of gb
    f_vars = []
    for b in f_syms:
        for b_out in f_syms[b]:
            f_vars.append(f_syms[b][b_out])
            
    # equations are linear in f_vars AND gb.
    # We want to see if for ANY gb, there exists f.
    # If the system can be solved for f, we will get the conditions on gb (if any)
    # The conditions on gb are the zero rows of the row-reduced matrix for f_vars.
    # We can do this by treating f_vars as the variables, and gb as parameters.
    # We construct the matrix A (coeffs of f_vars) and vector B (coeffs of gb).
    
    A_rows = []
    B_rows = []
    
    gb_vars = list(gb.values())
    
    for eq in eqs:
        # eq is of the form: expr_f + expr_gb = 0
        # we want expr_f = -expr_gb
        row_A = [eq.coeff(v) for v in f_vars]
        row_B = [-eq.subs({v: 0 for v in f_vars}).coeff(v) for v in gb_vars]
        A_rows.append(row_A)
        B_rows.append(row_B)
        
    M = sp.Matrix(A_rows)
    B_mat = sp.Matrix(B_rows)
    
    print("Matrix A shape:", M.shape)
    
    # Let's augment and rref
    aug = M.row_join(B_mat)
    print("Computing RREF...")
    rref_aug, pivots = aug.rref()
    
    # Conditions on gb are those rows where A is all zeros but B is not
    conditions = []
    for i in range(rref_aug.shape[0]):
        # Check if the A part is zero
        is_A_zero = True
        for j in range(len(f_vars)):
            if rref_aug[i, j] != 0:
                is_A_zero = False
                break
        
        if is_A_zero:
            # The B part must be zero for the system to be consistent
            cond = sum(rref_aug[i, len(f_vars) + j] * gb_vars[j] for j in range(len(gb_vars)))
            if cond != 0:
                conditions.append(cond)

    if not conditions:
        print("No conditions on gb! All deformations are trivial.")
    else:
        print(f"Found {len(conditions)} conditions on gb for the deformation to be trivial:")
        for c in conditions:
            print(c, "== 0")

if __name__ == "__main__":
    main()
