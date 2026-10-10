import sympy as sp
import json
from calc import get_basis, bracket, gamma

def parity(X):
    return 0 if X.startswith('B') or X == 'H' else 1

def run_n(n):
    even, odd = get_basis(n)
    basis = even + odd
    
    gb = {}
    for sigma in [1, -1]:
        for k in range(1, n+1):
            for s in [1, -1]:
                gb[sigma, k, s] = sp.Symbol(f"gb_{sigma}_{k}_{s}")
                
    f_vars = {}
    for e in even:
        for o in odd:
            f_vars[(e, o)] = sp.Symbol(f"f_{e}_{o}")
            f_vars[(o, e)] = sp.Symbol(f"f_{o}_{e}")
            
    def f_map(X):
        res = {}
        if X in even:
            for o in odd: res[o] = f_vars[(X, o)]
        else:
            for e in even: res[e] = f_vars[(X, e)]
        return res

    equations = []
    
    for i, X in enumerate(basis):
        for j in range(i, len(basis)):
            Y = basis[j]
            pX = parity(X)
            pY = parity(Y)
            gam = gamma(X, Y, n, gb)
            
            term1 = {}
            for k, coeff in f_map(Y).items():
                br = bracket(X, k, n)
                for res_k, res_coeff in br.items():
                    term1[res_k] = term1.get(res_k, 0) + (1 if pX == 0 else -1) * coeff * res_coeff
                    
            term2 = {}
            sign2 = -1 * (1 if ((pX+1)*pY) % 2 == 0 else -1)
            for k, coeff in f_map(X).items():
                br = bracket(Y, k, n)
                for res_k, res_coeff in br.items():
                    term2[res_k] = term2.get(res_k, 0) + sign2 * coeff * res_coeff
                    
            term3 = {}
            br_XY = bracket(X, Y, n)
            for k, coeff in br_XY.items():
                f_k = f_map(k)
                for res_k, res_coeff in f_k.items():
                    term3[res_k] = term3.get(res_k, 0) - coeff * res_coeff
                    
            coboundary = {}
            for t in [term1, term2, term3]:
                for k, v in t.items():
                    coboundary[k] = coboundary.get(k, 0) + v
                    
            for k in basis:
                lhs = gam.get(k, 0)
                rhs = coboundary.get(k, 0)
                eq = lhs - rhs
                if eq != 0:
                    equations.append(sp.simplify(eq))

    print(f"n={n}, Total equations: {len(equations)}")
    f_list = list(f_vars.values())
    A, b = sp.linear_eq_to_matrix(equations, f_list)
    
    null_A_T = A.T.nullspace()
    print(f"Left null space dimension: {len(null_A_T)}")
    
    conditions = []
    for vec in null_A_T:
        cond = (vec.dot(b)).simplify()
        if cond != 0:
            conditions.append(cond)
            
    print(f"Triviality conditions on gb for n={n}:")
    for c in conditions:
        print(c, "= 0")
        
    if len(conditions) == 0:
        print("All deformations are trivial!")
        
    out_data = {
        "n": n,
        "conditions_str": [str(c) for c in conditions],
    }
    with open(f"artifacts_n{n}.json", "w") as f:
        json.dump(out_data, f, indent=2)

if __name__ == "__main__":
    run_n(2)
    # run_n(3) # Might be slow, let's just do 2 first
