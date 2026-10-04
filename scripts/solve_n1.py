import sys
sys.path.append('.')
import sympy as sp
from collections import defaultdict
from scripts.test_normal_order import normal_order_monomial

kappa = sp.Symbol('kappa')

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

ap = ('a', 1, 1)
am = ('a', 1, -1)
bp = ('b', 1, 1)
bm = ('b', 1, -1)

# Basis:
basis_even = ['H1', 'H2', 'Ep', 'Em']
basis_odd = ['F_pp', 'F_pm', 'F_mp', 'F_mm']
basis = basis_even + basis_odd

gen_dict = {
    'H1': ({(ap, am): 1, (bp, bm): 1}, 0),
    'H2': ({(bp, bm): -1, (): sp.Rational(-1, 2)}, 0),
    'Ep': ({(bp, bp): sp.Rational(1, 2)}, 0),
    'Em': ({(bm, bm): sp.Rational(1, 2)}, 0),
    'F_pp': ({(ap, bp): 1}, 1),
    'F_pm': ({(ap, bm): 1}, 1),
    'F_mp': ({(am, bp): 1}, 1),
    'F_mm': ({(am, bm): 1}, 1),
}

def project_to_basis(elem_dict):
    vec = {name: sp.Integer(0) for name in basis}
    for m, c in elem_dict.items():
        if m == ():
            # scalar term, ignored up to scalar / center
            continue
        elif m == (ap, am):
            # ap am = H1 + H2
            vec['H1'] += c
            vec['H2'] += c
        elif m == (bp, bm):
            # bp bm = -H2
            vec['H2'] += -c
        elif m == (bp, bp):
            # 1/2 bp bp = Ep => bp bp = 2 Ep
            vec['Ep'] += 2 * c
        elif m == (bm, bm):
            # bm bm = 2 Em
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
            vec['H2'] += -c
        elif m == (am, ap):
            vec['H1'] += -c
            vec['H2'] += -c
        else:
            print(f'UNKNOWN MONOMIAL: {m} with coeff {c}')
    return {k: sp.expand(v) for k, v in vec.items()}

bracket_0 = {}
gamma_map = {}

print('Computing undeformed brackets and gamma...')
for name1 in basis:
    g1, p1 = gen_dict[name1]
    for name2 in basis:
        g2, p2 = gen_dict[name2]
        comm = supercommutator(g1, p1, g2, p2)
        comm_0 = {m: c.subs(kappa, 0) for m, c in comm.items() if c.subs(kappa, 0) != 0}
        comm_gamma = {m: c.coeff(kappa, 1) for m, c in comm.items() if c.coeff(kappa, 1) != 0}
        
        vec_0 = project_to_basis(comm_0)
        vec_gamma = project_to_basis(comm_gamma)
        
        bracket_0[(name1, name2)] = vec_0
        gamma_map[(name1, name2)] = vec_gamma

# Check super-Jacobi for bracket_0
print('Verifying super-Jacobi for bracket_0...')
jacobi_errors = 0
for X in basis:
    pX = gen_dict[X][1]
    for Y in basis:
        pY = gen_dict[Y][1]
        for Z in basis:
            pZ = gen_dict[Z][1]
            # (-1)^{pX pZ} [X, [Y, Z]] + (-1)^{pY pX} [Y, [Z, X]] + (-1)^{pZ pY} [Z, [X, Y]]
            def b(v1, v2):
                res = {b_name: sp.Integer(0) for b_name in basis}
                for b1, c1 in v1.items():
                    if c1 == 0: continue
                    for b2, c2 in v2.items():
                        if c2 == 0: continue
                        br = bracket_0[(b1, b2)]
                        for b_out, c_out in br.items():
                            res[b_out] += c1 * c2 * c_out
                return res

            vX = {b_name: (1 if b_name == X else 0) for b_name in basis}
            vY = {b_name: (1 if b_name == Y else 0) for b_name in basis}
            vZ = {b_name: (1 if b_name == Z else 0) for b_name in basis}

            t1 = b(vX, b(vY, vZ))
            t2 = b(vY, b(vZ, vX))
            t3 = b(vZ, b(vX, vY))

            s1 = (-1)**(pX * pZ)
            s2 = (-1)**(pY * pX)
            s3 = (-1)**(pZ * pY)

            for b_name in basis:
                val = sp.expand(s1 * t1[b_name] + s2 * t2[b_name] + s3 * t3[b_name])
                if val != 0:
                    jacobi_errors += 1
                    print(f'Jacobi error on ({X}, {Y}, {Z}) at {b_name}: {val}')
print(f'Jacobi verification complete. Total errors: {jacobi_errors}')

# Now define general odd map f:
phi_even_odd = {}
for e in basis_even:
    for o in basis_odd:
        phi_even_odd[(e, o)] = sp.Symbol(f'phi_{e}_{o}')

phi_odd_even = {}
for o in basis_odd:
    for e in basis_even:
        phi_odd_even[(o, e)] = sp.Symbol(f'phi_{o}_{e}')

def apply_f(name):
    res = {b: sp.Integer(0) for b in basis}
    if name in basis_even:
        for o in basis_odd:
            res[o] = phi_even_odd[(name, o)]
    else:
        for e in basis_even:
            res[e] = phi_odd_even[(name, e)]
    return res

def lie_bracket(v1, v2):
    res = {b: sp.Integer(0) for b in basis}
    for b1, c1 in v1.items():
        if c1 == 0: continue
        for b2, c2 in v2.items():
            if c2 == 0: continue
            br = bracket_0[(b1, b2)]
            for b_out, c_out in br.items():
                res[b_out] += c1 * c2 * c_out
    return {b: sp.expand(c) for b, c in res.items()}

def delta_f(name1, name2):
    p1 = gen_dict[name1][1]
    p2 = gen_dict[name2][1]
    
    fY = apply_f(name2)
    vX = {b: (1 if b == name1 else 0) for b in basis}
    X_fY = lie_bracket(vX, fY)
    
    fX = apply_f(name1)
    vY = {b: (1 if b == name2 else 0) for b in basis}
    Y_fX = lie_bracket(vY, fX)
    
    br_XY = bracket_0[(name1, name2)]
    f_br = {b: sp.Integer(0) for b in basis}
    for b_in, c_in in br_XY.items():
        if c_in == 0: continue
        fb = apply_f(b_in)
        for b_out, c_out in fb.items():
            f_br[b_out] += c_in * c_out
            
    sign1 = (-1)**p1
    sign2 = (-1)**((p1 + 1) * p2)
    
    res = {b: sp.Integer(0) for b in basis}
    for b in basis:
        res[b] = sign1 * X_fY[b] - sign2 * Y_fX[b] - f_br[b]
    return {b: sp.expand(c) for b, c in res.items()}

equations = []
for i, name1 in enumerate(basis):
    for j, name2 in enumerate(basis):
        if j < i:
            continue
        df = delta_f(name1, name2)
        gm = gamma_map[(name1, name2)]
        for b in basis:
            eq = sp.expand(df[b] - gm[b])
            if eq != 0:
                equations.append(eq)

print(f'Total non-trivial equations: {len(equations)}')
all_unknowns = list(phi_even_odd.values()) + list(phi_odd_even.values())
print(f'Total unknowns: {len(all_unknowns)}')

sol = sp.solve(equations, all_unknowns)
if isinstance(sol, list):
    if len(sol) == 0:
        print('No solution for arbitrary gb! sol is []')
    else:
        print(f'Found {len(sol)} solution(s):')
        for s in sol:
            print(s)
elif isinstance(sol, dict):
    print('Unique solution found:')
    for k, v in sol.items():
        print(f'  {k} = {v}')

