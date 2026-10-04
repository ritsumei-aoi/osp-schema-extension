import sympy as sp
from test_monomials import superbracket_monomials, names, parities

# Basis of osp(2|2):
# 0: b_p, 1: b_m, 2: a_p, 3: a_m

# Generators:
# Even:
# J = a_p a_m - 1/2  -> pair (2, 3): 1, const -1/2
# H = b_p b_m + 1/2  -> pair (0, 1): 1, const +1/2
# E = 1/2 b_p^2      -> pair (0, 0): 1/2
# F = 1/2 b_m^2      -> pair (1, 1): 1/2
# Odd:
# F1 = a_p b_p       -> pair (2, 0): 1
# F2 = a_p b_m       -> pair (2, 1): 1
# F3 = a_m b_p       -> pair (3, 0): 1
# F4 = a_m b_m       -> pair (3, 1): 1

generators = {
    'J':  ([(2, 3, 1)], -sp.Rational(1, 2), 0),
    'H':  ([(0, 1, 1)],  sp.Rational(1, 2), 0),
    'E':  ([(0, 0, sp.Rational(1, 2))], 0, 0),
    'F':  ([(1, 1, sp.Rational(1, 2))], 0, 0),
    'F1': ([(2, 0, 1)], 0, 1),
    'F2': ([(2, 1, 1)], 0, 1),
    'F3': ([(3, 0, 1)], 0, 1),
    'F4': ([(3, 1, 1)], 0, 1),
}

def normal_order(pair_dict):
    res = {g: 0 for g in generators}
    const = 0
    for (i, j), coeff in pair_dict.items():
        if coeff == 0: continue
        if (i, j) == (0, 0):
            res['E'] += coeff * 2
        elif (i, j) == (1, 1):
            res['F'] += coeff * 2
        elif (i, j) == (0, 1):
            res['H'] += coeff
            const -= coeff * sp.Rational(1, 2)
        elif (i, j) == (1, 0):
            res['H'] += coeff
            const += coeff * sp.Rational(1, 2)
        elif (i, j) == (2, 3):
            res['J'] += coeff
            const += coeff * sp.Rational(1, 2)
        elif (i, j) == (3, 2):
            res['J'] -= coeff
            const += coeff * sp.Rational(1, 2)
        elif (i, j) in [(2, 0), (0, 2)]:
            res['F1'] += coeff
        elif (i, j) in [(2, 1), (1, 2)]:
            res['F2'] += coeff
        elif (i, j) in [(3, 0), (0, 3)]:
            res['F3'] += coeff
        elif (i, j) in [(3, 1), (1, 3)]:
            res['F4'] += coeff
        elif (i, j) in [(2, 2), (3, 3)]:
            pass
        else:
            raise ValueError(f"Unknown pair: {i}, {j}")
    return res, const

def bracket_generators(g1, g2):
    t1, c1, p1 = generators[g1]
    t2, c2, p2 = generators[g2]
    total_0 = {}
    total_1 = {}
    for u1, u2, co1 in t1:
        for w1, w2, co2 in t2:
            r0, r1 = superbracket_monomials(u1, u2, w1, w2)
            for pair, v in r0.items():
                total_0[pair] = total_0.get(pair, 0) + co1 * co2 * v
            for pair, v in r1.items():
                total_1[pair] = total_1.get(pair, 0) + co1 * co2 * v
                
    dec0, const0 = normal_order(total_0)
    dec1, const1 = normal_order(total_1)
    return dec0, const0, dec1, const1

gen_list = ['J', 'H', 'E', 'F', 'F1', 'F2', 'F3', 'F4']

print("Checking undeformed brackets and constants:")
has_const0 = False
has_const1 = False
for g1 in gen_list:
    for g2 in gen_list:
        dec0, const0, dec1, const1 = bracket_generators(g1, g2)
        if sp.simplify(const0) != 0:
            print(f"Non-zero const0 in [{g1}, {g2}]: {const0}")
            has_const0 = True
        if sp.simplify(const1) != 0:
            print(f"Non-zero const1 in [{g1}, {g2}]: {const1}")
            has_const1 = True

if not has_const0:
    print("ALL const0 are ZERO! [g1, g2]_0 lies strictly in g!")
if not has_const1:
    print("ALL const1 are ZERO! gamma(g1, g2) lies strictly in g!")

print("\n--- Non-zero undeformed brackets [g1, g2]_0 ---")
for i, g1 in enumerate(gen_list):
    for j, g2 in enumerate(gen_list):
        if j < i and generators[g1][2] == generators[g2][2] and generators[g1][2] == 0:
            continue
        dec0, _, dec1, _ = bracket_generators(g1, g2)
        nz0 = {k: v for k, v in dec0.items() if sp.simplify(v) != 0}
        if nz0:
            print(f"[{g1}, {g2}]_0 = {nz0}")

print("\n--- Deformed brackets gamma(g1, g2) ---")
for i, g1 in enumerate(gen_list):
    for j, g2 in enumerate(gen_list):
        dec0, _, dec1, _ = bracket_generators(g1, g2)
        nz1 = {k: v for k, v in dec1.items() if sp.simplify(v) != 0}
        if nz1:
            print(f"gamma({g1}, {g2}) = {nz1}")
