import sympy as sp
import json

def get_triviality_conditions(n):
    even_basis = []
    odd_basis = []
    
    # Even: bi+ bj+ (i<=j), bi- bj- (i<=j), bi+ bj- (any i,j)
    for i in range(1, n+1):
        for j in range(i, n+1):
            even_basis.append((f'b{i}+', f'b{j}+'))
            even_basis.append((f'b{i}-', f'b{j}-'))
    for i in range(1, n+1):
        for j in range(1, n+1):
            even_basis.append((f'b{i}+', f'b{j}-'))
            
    even_basis.append(('a1+', 'a1-'))
    
    # Odd: a1+ bi+, a1+ bi-, a1- bi+, a1- bi-
    for i in range(1, n+1):
        odd_basis.append(('a1+', f'b{i}+'))
        odd_basis.append(('a1+', f'b{i}-'))
        odd_basis.append(('a1-', f'b{i}+'))
        odd_basis.append(('a1-', f'b{i}-'))
        
    basis = even_basis + odd_basis
    
    def p(osc):
        return 1 if osc.startswith('a') else 0

    def pg(gen):
        return (p(gen[0]) + p(gen[1])) % 2

    def commutator_base(A, B):
        if p(A) == 0 and p(B) == 0:
            if A[0] == 'b' and B[0] == 'b':
                if A[1:-1] == B[1:-1] and A[-1] != B[-1]:
                    return [(1 if A[-1] == '-' else -1, "K")]
        elif p(A) == 1 and p(B) == 1:
            if A[0] == 'a' and B[0] == 'a':
                if A[-1] != B[-1]:
                    return [(1, "K")] # {a-, a+} = 1
        return []

    def commutator_def(A, B):
        if p(A) != p(B):
            if p(A) == 0:
                j, s, sigma = A[1:-1], A[-1], B[-1]
                return [(sp.Symbol(f"gb_{sigma}_{j}_{s}"), "kappa", -1)]
            else:
                sigma, j, s = A[-1], B[1:-1], B[-1]
                return [(sp.Symbol(f"gb_{sigma}_{j}_{s}"), "kappa", 1)]
        return []

    def bracket(X, Y, comm_func):
        A, B = X
        C, D = Y
        terms = []
        
        def add_term(comm_res, left, right, sign_pow):
            sign = 1 if sign_pow % 2 == 0 else -1
            for res in comm_res:
                if len(res) == 2:
                    coeff, _ = res
                    total_sign = sign
                else:
                    coeff, _, csign = res
                    swaps = sum(p(o) for o in left)
                    total_sign = sign * csign * (1 if swaps % 2 == 0 else -1)
                
                oscs = tuple(left + right)
                terms.append((coeff * total_sign, oscs))
                    
        add_term(comm_func(B, C), [A], [D], 0)
        add_term(comm_func(B, D), [A, C], [], p(B)*p(C))
        add_term(comm_func(A, C), [], [D, B], p(B)*(p(C)+p(D)))
        add_term(comm_func(A, D), [C], [B], p(B)*(p(C)+p(D)) + p(A)*p(C))
        
        return terms

    def standardize(coeff, oscs):
        if p(oscs[0]) == 0 and p(oscs[1]) == 0:
            if oscs[0].startswith('a'):
                if oscs[0][-1] == '+': return [(coeff, basis.index(('a1+', 'a1-')))]
                else: return [(-coeff, basis.index(('a1+', 'a1-')))]
            else:
                i = int(oscs[0][1:-1])
                j = int(oscs[1][1:-1])
                s = oscs[0][-1]
                t = oscs[1][-1]
                
                if s == '-' and t == '+':
                    return [(coeff, basis.index((f'b{j}+', f'b{i}-')))]
                elif oscs[0] == oscs[1]:
                    return [(coeff, basis.index(oscs))]
                elif s == '+' and t == '+':
                    if i <= j: return [(coeff, basis.index((f'b{i}+', f'b{j}+')))]
                    else: return [(coeff, basis.index((f'b{j}+', f'b{i}+')))]
                elif s == '-' and t == '-':
                    if i <= j: return [(coeff, basis.index((f'b{i}-', f'b{j}-')))]
                    else: return [(coeff, basis.index((f'b{j}-', f'b{i}-')))]
                else:
                    if s == '+' and t == '-':
                        return [(coeff, basis.index((f'b{i}+', f'b{j}-')))]
                    else:
                        return [(coeff, basis.index((f'b{j}+', f'b{i}-')))]
        elif p(oscs[0]) == 1 and p(oscs[1]) == 0:
            return [(coeff, basis.index((oscs[0], oscs[1])))]
        elif p(oscs[0]) == 0 and p(oscs[1]) == 1:
            return [(coeff, basis.index((oscs[1], oscs[0])))]
        else:
            if oscs[0][-1] == '+': return [(coeff, basis.index(('a1+', 'a1-')))]
            else: return [(-coeff, basis.index(('a1+', 'a1-')))]

    def get_gamma(X, Y):
        terms = bracket(X, Y, commutator_def)
        res = [0] * len(basis)
        for c, o in terms:
            for c_std, idx in standardize(c, o):
                res[idx] += c_std
        return res

    def get_bracket_0(X, Y):
        terms = bracket(X, Y, commutator_base)
        res = [0] * len(basis)
        for c, o in terms:
            for c_std, idx in standardize(c, o):
                res[idx] += c_std
        return res

    gb_vars = [sp.Symbol(f"gb_{sigma}_{j}_{s}") for sigma in ['+', '-'] for j in range(1, n+1) for s in ['+', '-']]
    
    dim = len(basis)
    f_vars = [sp.Symbol(f"f_{i}_{j}") for i in range(dim) for j in range(dim) if pg(basis[i]) != pg(basis[j])]
    
    def apply_f(idx):
        res = [0] * dim
        for i in range(dim):
            if pg(basis[idx]) != pg(basis[i]):
                res[i] = sp.Symbol(f"f_{idx}_{i}")
        return res

    equations = []
    for i in range(dim):
        for j in range(i, dim):
            X = basis[i]
            Y = basis[j]
            gamma_XY = get_gamma(X, Y)
            
            df_XY = [0] * dim
            fY = apply_f(j)
            for k in range(dim):
                if fY[k] != 0:
                    b_X_fk = get_bracket_0(X, basis[k])
                    for m in range(dim):
                        df_XY[m] += ((-1)**pg(X)) * fY[k] * b_X_fk[m]
                        
            fX = apply_f(i)
            for k in range(dim):
                if fX[k] != 0:
                    b_Y_fk = get_bracket_0(Y, basis[k])
                    for m in range(dim):
                        df_XY[m] -= ((-1)**((pg(X)+1)*pg(Y))) * fX[k] * b_Y_fk[m]
                        
            b_XY = get_bracket_0(X, Y)
            for k in range(dim):
                if b_XY[k] != 0:
                    f_bXY = apply_f(k)
                    for m in range(dim):
                        df_XY[m] -= b_XY[k] * f_bXY[m]
                        
            for m in range(dim):
                eq = gamma_XY[m] - df_XY[m]
                if eq != 0:
                    equations.append(eq)

    matrix, _ = sp.linear_eq_to_matrix(equations, f_vars)
    matrix_gb, _ = sp.linear_eq_to_matrix(equations, gb_vars)

    left_null = matrix.T.nullspace()
    constraints = []
    for vec in left_null:
        constraint = vec.T * matrix_gb
        constraints.append(constraint)

    eqs_to_solve = []
    for c in constraints:
        expr = sum(c[0, idx] * gb_vars[idx] for idx in range(len(gb_vars)))
        if expr != 0: eqs_to_solve.append(expr)
        
    sol = sp.solve(eqs_to_solve, gb_vars)
    print(f"n={n} solution: {sol}")
    return sol

get_triviality_conditions(1)
get_triviality_conditions(2)
get_triviality_conditions(3)
