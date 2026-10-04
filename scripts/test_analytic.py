import sympy as sp
from collections import defaultdict
from scripts.test_normal_order import normal_order_monomial

kappa = sp.Symbol('kappa')

def run_test():
    # Let's test the C(2) sub-system for an arbitrary index k
    # We will express everything in terms of J0 and hk
    gb_pp = sp.Symbol('gb_pp')
    gb_pm = sp.Symbol('gb_pm')
    gb_mp = sp.Symbol('gb_mp')
    gb_mm = sp.Symbol('gb_mm')
    
    gb_params = {
        ('+', 1, '+'): gb_pp,
        ('+', 1, '-'): gb_pm,
        ('-', 1, '+'): gb_mp,
        ('-', 1, '-'): gb_mm,
    }
    
    ap = ('a', 1, 1)
    am = ('a', 1, -1)
    bp = ('b', 1, 1)
    bm = ('b', 1, -1)
    
    def multiply(A, B):
        res = defaultdict(lambda: sp.Integer(0))
        for m1, c1 in A.items():
            for m2, c2 in B.items():
                m = m1 + m2
                norm = normal_order_monomial(m, gb_params)
                for mn, cn in norm.items():
                    res[mn] += c1 * c2 * cn
        final = {}
        for m, c in res.items():
            c_lin = sp.expand(c)
            c_deg = sp.collect(c_lin, kappa)
            final[m] = c_deg
        return {m: c for m, c in final.items() if c != 0}

    def supercommutator(A, pA, B, pB):
        sign = (-1)**(pA * pB)
        AB = multiply(A, B)
        BA = multiply(B, A)
        res = defaultdict(lambda: sp.Integer(0))
        for m, c in AB.items():
            res[m] += c
        for m, c in BA.items():
            res[m] -= sign * c
        return {m: sp.expand(c) for m, c in res.items() if sp.expand(c) != 0}

    # Generators in J0, h1 basis:
    J0 = {(ap, am): 1, (): sp.Rational(-1, 2)}
    h1 = {(bp, bm): 1, (): sp.Rational(1, 2)}
    Ep = {(bp, bp): sp.Rational(1, 2)}
    Em = {(bm, bm): sp.Rational(1, 2)}
    
    F_pp = {(ap, bp): 1}
    F_pm = {(ap, bm): 1}
    F_mp = {(am, bp): 1}
    F_mm = {(am, bm): 1}
    
    basis = ['J0', 'h1', 'Ep', 'Em', 'F_pp', 'F_pm', 'F_mp', 'F_mm']
    parity = {'J0': 0, 'h1': 0, 'Ep': 0, 'Em': 0, 'F_pp': 1, 'F_pm': 1, 'F_mp': 1, 'F_mm': 1}
    
    gen_dict = {
        'J0': J0, 'h1': h1, 'Ep': Ep, 'Em': Em,
        'F_pp': F_pp, 'F_pm': F_pm, 'F_mp': F_mp, 'F_mm': F_mm
    }
    
    def project(d):
        vec = {b: sp.Integer(0) for b in basis}
        for m, c in d.items():
            if m == ():
                continue # central scalar
            elif m == (ap, am):
                # ap am = J0 + 1/2 -> J0
                vec['J0'] += c
            elif m == (bp, bm):
                # bp bm = h1 - 1/2 -> h1
                vec['h1'] += c
            elif m == (bp, bp):
                vec['Ep'] += 2 * c
            elif m == (bm, bm):
                vec['Em'] += 2 * c
            elif m == (ap, bp):
                vec['F_pp'] += c
            elif m == (ap, bm):
                vec['F_pm'] += c
            elif m == (am, bp):
                vec['F_mp'] += c
            elif m == (am, bm):
                vec['F_mm'] += c
            elif m == (bm, bp):
                vec['h1'] += c
            elif m == (am, ap):
                vec['J0'] += -c
            else:
                print('UNKNOWN:', m)
        return {b: sp.expand(v) for b, v in vec.items()}

    bracket_0 = {}
    gamma_map = {}
    for n1 in basis:
        for n2 in basis:
            comm = supercommutator(gen_dict[n1], parity[n1], gen_dict[n2], parity[n2])
            comm_0 = {m: c.subs(kappa, 0) for m, c in comm.items() if c.subs(kappa, 0) != 0}
            comm_gamma = {m: c.coeff(kappa, 1) for m, c in comm.items() if c.coeff(kappa, 1) != 0}
            bracket_0[(n1, n2)] = project(comm_0)
            gamma_map[(n1, n2)] = project(comm_gamma)
            
    print('Testing [J0, h1] undeformed:', bracket_0[('J0', 'h1')])
    print('Testing gamma(J0, h1):', gamma_map[('J0', 'h1')])
    print('Testing gamma(J0, F_pp):', gamma_map[('J0', 'F_pp')])
    print('Testing gamma(h1, F_pp):', gamma_map[('h1', 'F_pp')])

run_test()
