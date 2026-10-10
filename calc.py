import sympy as sp
import json

def get_basis(n):
    even_basis = ['H']
    for j in range(1, n+1):
        for k in range(j, n+1):
            for s in [1, -1]:
                for t in [1, -1]:
                    if j == k and s > t:
                        continue
                    even_basis.append(f"B_{j}_{k}_{s}_{t}")
    
    odd_basis = []
    for k in range(1, n+1):
        for sigma in [1, -1]:
            for s in [1, -1]:
                odd_basis.append(f"F_{k}_{sigma}_{s}")
                
    return even_basis, odd_basis

def parse_B(name):
    if name == 'H': return None
    _, j, k, s, t = name.split('_')
    return int(j), int(k), int(s), int(t)

def parse_F(name):
    _, k, sigma, s = name.split('_')
    return int(k), int(sigma), int(s)

def b_comm(j, s, k, t):
    if j == k and s == -t:
        return s
    return 0

def make_B(j, k, s, t):
    if j > k:
        j, k = k, j
        s, t = t, s
    if j == k and s > t:
        s, t = t, s
    return f"B_{j}_{k}_{s}_{t}"

def bracket(X, Y, n):
    res = {}
    def add(term, coeff):
        if coeff != 0:
            res[term] = res.get(term, 0) + coeff

    # Even-Even
    if X.startswith('B') and Y.startswith('B'):
        j1, k1, s1, t1 = parse_B(X)
        j2, k2, s2, t2 = parse_B(Y)
        
        # [b_j1^s1 b_k1^t1, b_j2^s2 b_k2^t2]
        # = b_j1^s1 [b_k1^t1, b_j2^s2 b_k2^t2] + [b_j1^s1, b_j2^s2 b_k2^t2] b_k1^t1
        # = b_j1^s1 ( b_j2^s2 [b_k1^t1, b_k2^t2] + [b_k1^t1, b_j2^s2] b_k2^t2 ) + ( b_j2^s2 [b_j1^s1, b_k2^t2] + [b_j1^s1, b_j2^s2] b_k2^t2 ) b_k1^t1
        
        c1 = b_comm(k1, t1, k2, t2)
        if c1 != 0: add(make_B(j1, j2, s1, s2), c1)
        
        c2 = b_comm(k1, t1, j2, s2)
        if c2 != 0: add(make_B(j1, k2, s1, t2), c2)
        
        c3 = b_comm(j1, s1, k2, t2)
        if c3 != 0: add(make_B(k1, j2, t1, s2), c3)
        
        c4 = b_comm(j1, s1, j2, s2)
        if c4 != 0: add(make_B(k1, k2, t1, t2), c4)
        
        return res

    if X == 'H' and Y.startswith('B') or X.startswith('B') and Y == 'H' or (X == 'H' and Y == 'H'):
        return {}

    # Even-Odd
    if X.startswith('B') and Y.startswith('F'):
        # [b_j^s b_k^t, a_1^\sigma b_l^u] = a_1^\sigma [b_j^s b_k^t, b_l^u]
        j, k, s, t = parse_B(X)
        l, sigma, u = parse_F(Y)
        
        # [b_j^s b_k^t, b_l^u] = b_j^s [b_k^t, b_l^u] + [b_j^s, b_l^u] b_k^t
        c1 = b_comm(k, t, l, u)
        if c1 != 0: add(f"F_{j}_{sigma}_{s}", c1)
        
        c2 = b_comm(j, s, l, u)
        if c2 != 0: add(f"F_{k}_{sigma}_{t}", c2)
        
        return res
        
    if X.startswith('F') and Y.startswith('B'):
        # Odd-Even: [F, B] = - [B, F]
        br = bracket(Y, X, n)
        for k, v in br.items():
            res[k] = -v
        return res

    if X == 'H' and Y.startswith('F'):
        # [a_1^+ a_1^-, a_1^\sigma b_l^u] = [a_1^+ a_1^-, a_1^\sigma] b_l^u
        # = \sigma a_1^\sigma b_l^u
        l, sigma, u = parse_F(Y)
        add(f"F_{l}_{sigma}_{u}", sigma)
        return res
        
    if X.startswith('F') and Y == 'H':
        br = bracket(Y, X, n)
        for k, v in br.items():
            res[k] = -v
        return res

    # Odd-Odd
    if X.startswith('F') and Y.startswith('F'):
        # [a_1^\sigma b_j^s, a_1^\tau b_k^t] = [a_1^\sigma, a_1^\tau] b_j^s b_k^t - a_1^\tau a_1^\sigma [b_j^s, b_k^t]
        # = \delta_{\sigma, -\tau} b_j^s b_k^t - s \delta_{j,k} \delta_{s, -t} a_1^\tau a_1^\sigma
        j, sigma, s = parse_F(X)
        k, tau, t = parse_F(Y)
        
        if sigma == -tau:
            add(make_B(j, k, s, t), 1)
        
        c = b_comm(j, s, k, t)
        if c != 0:
            # - c a_1^\tau a_1^\sigma
            if tau == 1 and sigma == -1: # a_1^+ a_1^- = H
                add('H', -c)
            elif tau == -1 and sigma == 1: # a_1^- a_1^+ = 1 - H  (we drop the 1 because we work modulo scalars)
                add('H', c)  # -c * (-H)
                
        return res

    return {}

def gamma(X, Y, n, gb):
    res = {}
    def add(term, coeff):
        if coeff != 0:
            res[term] = res.get(term, 0) + coeff

    # Even-Even
    if X.startswith('B') and Y.startswith('B'):
        return res
        
    if X == 'H' and Y.startswith('B'):
        l, v = parse_B(Y)[0:2], parse_B(Y)[2:4] # wait, it's j, k, s, t
        j, k, s, t = parse_B(Y)
        # \gamma(H_a, B_{lm}^{vw}) = - gb_{-, l, v} F_m^{+, w} - gb_{-, m, w} F_l^{+, v} + gb_{+, l, v} F_m^{-, w} + gb_{+, m, w} F_l^{-, v}
        add(f"F_{k}_{1}_{t}", -gb[-1, j, s])
        add(f"F_{j}_{1}_{s}", -gb[-1, k, t])
        add(f"F_{k}_{-1}_{t}", gb[1, j, s])
        add(f"F_{j}_{-1}_{s}", gb[1, k, t])
        return res
        
    if X.startswith('B') and Y == 'H':
        g = gamma(Y, X, n, gb)
        for k, v in g.items(): res[k] = -v
        return res
        
    if X == 'H' and Y == 'H':
        return res

    # Even-Odd
    if X.startswith('B') and Y.startswith('F'):
        # \gamma(B_{jk}^{st}, F_l^{\tau u}) = - gb_{\tau, k, t} B_{jl}^{su} - gb_{\tau, j, s} B_{kl}^{tu}
        j, k, s, t = parse_B(X)
        l, tau, u = parse_F(Y)
        
        add(make_B(j, l, s, u), -gb[tau, k, t])
        add(make_B(k, l, t, u), -gb[tau, j, s])
        return res
        
    if X.startswith('F') and Y.startswith('B'):
        g = gamma(Y, X, n, gb)
        for k, v in g.items(): res[k] = -v
        return res

    if X == 'H' and Y.startswith('F'):
        # \gamma(H_a, F_l^{\tau u}) \equiv - gb_{\tau, l, u} H_a
        l, tau, u = parse_F(Y)
        add('H', -gb[tau, l, u])
        return res
        
    if X.startswith('F') and Y == 'H':
        g = gamma(Y, X, n, gb)
        for k, v in g.items(): res[k] = -v
        return res

    # Odd-Odd
    if X.startswith('F') and Y.startswith('F'):
        # \gamma(F_j^{\sigma s}, F_k^{\tau t}) = gb_{\tau, j, s} F_k^{\sigma t} + gb_{\sigma, k, t} F_j^{\tau s}
        j, sigma, s = parse_F(X)
        k, tau, t = parse_F(Y)
        
        add(f"F_{k}_{sigma}_{t}", gb[tau, j, s])
        add(f"F_{j}_{tau}_{s}", gb[sigma, k, t])
        return res

    return res

def run():
    n = 1
    even, odd = get_basis(n)
    basis = even + odd
    
    # Create variables for gb
    gb = {}
    for sigma in [1, -1]:
        for k in range(1, n+1):
            for s in [1, -1]:
                gb[sigma, k, s] = sp.Symbol(f"gb_{sigma}_{k}_{s}")
                
    # Create variables for f
    f_vars = {}
    # f maps even to odd, odd to even
    for e in even:
        for o in odd:
            f_vars[(e, o)] = sp.Symbol(f"f_{e}_{o}")
            f_vars[(o, e)] = sp.Symbol(f"f_{o}_{e}")
            
    def f_map(X):
        res = {}
        if X in even:
            for o in odd:
                res[o] = f_vars[(X, o)]
        else:
            for e in even:
                res[e] = f_vars[(X, e)]
        return res
        
    def parity(X):
        return 0 if X in even else 1

    equations = []
    
    # \gamma(X, Y) = (-1)^{p(X)}[X, f(Y)] - (-1)^{(p(X)+1)p(Y)}[Y, f(X)] - f([X, Y])
    for i, X in enumerate(basis):
        for j in range(i, len(basis)):
            Y = basis[j]
            
            pX = parity(X)
            pY = parity(Y)
            
            gam = gamma(X, Y, n, gb)
            
            # coboundary
            # term 1: (-1)^{pX} [X, f(Y)]
            term1 = {}
            for k, coeff in f_map(Y).items():
                br = bracket(X, k, n)
                for res_k, res_coeff in br.items():
                    term1[res_k] = term1.get(res_k, 0) + (1 if pX == 0 else -1) * coeff * res_coeff
                    
            # term 2: - (-1)^{(pX+1)*pY} [Y, f(X)]
            term2 = {}
            sign2 = -1 * (1 if ((pX+1)*pY) % 2 == 0 else -1)
            for k, coeff in f_map(X).items():
                br = bracket(Y, k, n)
                for res_k, res_coeff in br.items():
                    term2[res_k] = term2.get(res_k, 0) + sign2 * coeff * res_coeff
                    
            # term 3: - f([X, Y])
            term3 = {}
            br_XY = bracket(X, Y, n)
            for k, coeff in br_XY.items():
                f_k = f_map(k)
                for res_k, res_coeff in f_k.items():
                    term3[res_k] = term3.get(res_k, 0) - coeff * res_coeff
                    
            # Sum up terms
            coboundary = {}
            for t in [term1, term2, term3]:
                for k, v in t.items():
                    coboundary[k] = coboundary.get(k, 0) + v
                    
            # Equation: gam = coboundary
            for k in basis:
                lhs = gam.get(k, 0)
                rhs = coboundary.get(k, 0)
                eq = lhs - rhs
                if eq != 0:
                    equations.append(sp.simplify(eq))

    print(f"Total equations: {len(equations)}")
    # The unknowns are the f_vars. We want to know if for ANY gb, there exists an f.
    # So we treat f_vars as variables and gb as constants (in the matrix),
    # or just collect the matrix of the linear system A * f = B(gb)
    
    f_list = list(f_vars.values())
    A, b = sp.linear_eq_to_matrix(equations, f_list)
    
    # We want A * f = b to have a solution.
    # The condition is that b is in the column space of A.
    # Let's find the left null space of A, or just do row reduction on [A | b]
    
    # Instead of full row reduction which might be slow, let's substitute some random values for gb and see if it's consistent.
    # Actually, sympy can do rref.
    print("Computing RREF...")
    M = A.row_join(b)
    # RREF might be slow, let's just find the nullspace of A.T
    null_A_T = A.T.nullspace()
    print(f"Left null space dimension: {len(null_A_T)}")
    
    conditions = []
    for vec in null_A_T:
        cond = (vec.dot(b)).simplify()
        if cond != 0:
            conditions.append(cond)
            
    print("Triviality conditions on gb:")
    for c in conditions:
        print(c, "= 0")
        
    if len(conditions) == 0:
        print("All deformations are trivial!")
        
    # Generate structured data
    out_data = {
        "n": n,
        "conditions_str": [str(c) for c in conditions],
    }
    with open("artifacts.json", "w") as f:
        json.dump(out_data, f, indent=2)

if __name__ == "__main__":
    run()
