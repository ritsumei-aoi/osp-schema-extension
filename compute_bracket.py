import sympy as sp
from sympy import symbols, Matrix, zeros, Eq, solve
import sys

def build_algebra(n):
    # Oscillators
    osc = []
    osc.append(('a', '+', 0))
    osc.append(('a', '-', 0))
    for k in range(1, n+1):
        osc.append(('b', '+', k))
        osc.append(('b', '-', k))
        
    def parity(u):
        return 1 if u[0] == 'a' else 0
        
    def order(u):
        if u[0] == 'a':
            return 1 if u[1] == '+' else 2
        else:
            base = 2 + 2 * (u[2] - 1)
            return base + 1 if u[1] == '+' else base + 2

    # gb parameters as sympy symbols
    gb_syms = {}
    for sigma in ['+', '-']:
        for k in range(1, n+1):
            for s in ['+', '-']:
                sym = sp.Symbol(f'gb_{sigma}_{k}_{s}')
                gb_syms[(sigma, k, s)] = sym

    def omega0(u, v): # Standard omega (scalar)
        if u[0] == 'b' and v[0] == 'b':
            if u[2] == v[2] and u[1] != v[1]:
                return 1 if u[1] == '-' else -1
            return 0
        if u[0] == 'a' and v[0] == 'a':
            if u[1] != v[1]:
                return 1
            return 0
        return 0

    def omega1(u, v): # Deformed omega (coefficient of kappa)
        if u[0] == 'b' and v[0] == 'a':
            return -gb_syms[(v[1], u[2], u[1])]
        if u[0] == 'a' and v[0] == 'b':
            return gb_syms[(u[1], v[2], v[1])]
        return 0

    def normal_order(u, v):
        # returns dict of { (u', v'): coeff_0, 'scalar': coeff_0, 'kappa': coeff_1 }
        # representing u*v
        if order(u) <= order(v):
            return { (u, v): 1 }
        else:
            sign = -1 if (parity(u) == 1 and parity(v) == 1) else 1
            res = { (v, u): sign }
            w0 = omega0(u, v)
            w1 = omega1(u, v)
            if w0 != 0:
                res['scalar'] = w0
            if w1 != 0:
                res['kappa'] = w1
            return res

    def multiply_scalar(term, scalar):
        res = {}
        for k, v in term.items():
            res[k] = v * scalar
        return res

    def add_terms(t1, t2):
        res = {}
        for k, v in t1.items():
            res[k] = res.get(k, 0) + v
        for k, v in t2.items():
            res[k] = res.get(k, 0) + v
        return {k: v for k, v in res.items() if v != 0}

    # [AB, CD] = w(B,C) AD + (-1)^{p(B)p(C)} w(B,D) AC + (-1)^{p(B)(p(C)+p(D))} w(A,C) DB + (-1)^{p(B)(p(C)+p(D)) + p(A)p(C)} w(A,D) CB
    def superbracket(AB, CD):
        A, B = AB
        C, D = CD
        res = {}
        
        def process_term(u, v, w0, w1, sign):
            nonlocal res
            if w0 != 0:
                ord_uv = normal_order(u, v)
                res = add_terms(res, multiply_scalar(ord_uv, w0 * sign))
            if w1 != 0:
                # w1 is coeff of kappa. kappa * u * v = kappa * (normal_order(u, v))
                # but we only keep up to linear in kappa, so normal order without kappa terms
                ord_uv = normal_order(u, v)
                # discard 'kappa' from ord_uv, and promote basis to kappa
                for k, val in ord_uv.items():
                    if k != 'kappa' and k != 'scalar':
                        res[('kappa', k)] = res.get(('kappa', k), 0) + val * w1 * sign
                    elif k == 'scalar':
                        res['kappa'] = res.get('kappa', 0) + val * w1 * sign
                        
        pA = parity(A); pB = parity(B); pC = parity(C); pD = parity(D)
        
        w0, w1 = omega0(B, C), omega1(B, C)
        process_term(A, D, w0, w1, 1)
        
        w0, w1 = omega0(B, D), omega1(B, D)
        process_term(A, C, w0, w1, (-1)**(pB*pC))
        
        w0, w1 = omega0(A, C), omega1(A, C)
        process_term(D, B, w0, w1, (-1)**(pB*(pC+pD)))
        
        w0, w1 = omega0(A, D), omega1(A, D)
        process_term(C, B, w0, w1, (-1)**(pB*(pC+pD) + pA*pC))
        
        return res

    basis = []
    basis.append((('a', '+', 0), ('a', '-', 0)))
    for k in range(1, n+1):
        for l in range(k, n+1):
            basis.append((('b', '+', k), ('b', '+', l)))
            basis.append((('b', '-', k), ('b', '-', l)))
    for k in range(1, n+1):
        for l in range(1, n+1):
            basis.append((('b', '+', k), ('b', '-', l)))
    for k in range(1, n+1):
        basis.append((('a', '+', 0), ('b', '+', k)))
        basis.append((('a', '+', 0), ('b', '-', k)))
        basis.append((('a', '-', 0), ('b', '+', k)))
        basis.append((('a', '-', 0), ('b', '-', k)))

    return basis, superbracket, parity, gb_syms

if __name__ == '__main__':
    basis, bracket, parity_fn, gb_syms = build_algebra(1)
    for k, v in bracket(basis[0], basis[1]).items():
        print(k, ":", v)
