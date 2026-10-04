import sympy as sp
from test_monomials import superbracket_monomials, parities
from test_osp22 import normal_order, generators, gen_list

# We have 8 generators:
# Even: J, H, E, F (parities = 0)
# Odd: F1, F2, F3, F4 (parities = 1)

# Let's compute all undeformed brackets [X, Y]_0 and gamma(X, Y)
# For each pair (X, Y) with X, Y in gen_list:
def get_brackets():
    br_0 = {}
    gamma = {}
    for g1 in gen_list:
        for g2 in gen_list:
            t1, _, _ = generators[g1]
            t2, _, _ = generators[g2]
            tot0, tot1 = {}, {}
            for u1, u2, co1 in t1:
                for w1, w2, co2 in t2:
                    r0, r1 = superbracket_monomials(u1, u2, w1, w2)
                    for p, v in r0.items():
                        tot0[p] = tot0.get(p, 0) + co1 * co2 * v
                    for p, v in r1.items():
                        tot1[p] = tot1.get(p, 0) + co1 * co2 * v
            dec0, _ = normal_order(tot0)
            dec1, _ = normal_order(tot1)
            br_0[(g1, g2)] = dec0
            gamma[(g1, g2)] = dec1
    return br_0, gamma

br_0, gamma = get_brackets()

# An odd linear map f: g -> g.
# Since f is odd:
# For even X in {J, H, E, F}: f(X) must be odd, so f(X) in span{F1, F2, F3, F4}.
# For odd Y in {F1, F2, F3, F4}: f(Y) must be even, so f(Y) in span{J, H, E, F}.

even_gens = ['J', 'H', 'E', 'F']
odd_gens = ['F1', 'F2', 'F3', 'F4']

# Parameterize f:
phi = {}
for g in even_gens:
    for target in odd_gens:
        phi[(g, target)] = sp.Symbol(f"phi_{g}_{target}")

for g in odd_gens:
    for target in even_gens:
        phi[(g, target)] = sp.Symbol(f"phi_{g}_{target}")

# Total 16 + 16 = 32 parameters in f.
all_phi_vars = list(phi.values())

def f_map(Z):
    # returns dict of {gen: expr}
    pz = generators[Z][2]
    res = {g: 0 for g in gen_list}
    if pz == 0:
        for target in odd_gens:
            res[target] = phi[(Z, target)]
    else:
        for target in even_gens:
            res[target] = phi[(Z, target)]
    return res

# Coboundary formula:
# (delta f)(X, Y) = (-1)^{p(X)} [X, f(Y)] - (-1)^{(p(X)+1)p(Y)} [Y, f(X)] - f([X, Y])
# Here [., .] is the undeformed bracket [., .]_0 on g!

def compute_bracket_linear(Z_dict1, Z_dict2):
    # bracket between two linear combinations
    res = {g: 0 for g in gen_list}
    for g1, c1 in Z_dict1.items():
        if c1 == 0: continue
        for g2, c2 in Z_dict2.items():
            if c2 == 0: continue
            for out_g, out_c in br_0[(g1, g2)].items():
                if out_c != 0:
                    res[out_g] += c1 * c2 * out_c
    return res

def compute_delta_f(X, Y):
    pX = generators[X][2]
    pY = generators[Y][2]
    
    fY = f_map(Y)
    fX = f_map(X)
    
    # [X, f(Y)]:
    X_dict = {g: (1 if g == X else 0) for g in gen_list}
    Y_dict = {g: (1 if g == Y else 0) for g in gen_list}
    
    term1 = compute_bracket_linear(X_dict, fY)
    term2 = compute_bracket_linear(Y_dict, fX)
    
    # [X, Y]_0:
    XY_0 = br_0[(X, Y)]
    f_XY = {g: 0 for g in gen_list}
    for z, cz in XY_0.items():
        if cz != 0:
            fz = f_map(z)
            for g, cfg in fz.items():
                f_XY[g] += cz * cfg
                
    sign1 = (-1)**pX
    sign2 = (-1)**((pX + 1) * pY)
    
    res = {g: 0 for g in gen_list}
    for g in gen_list:
        res[g] = sign1 * term1[g] - sign2 * term2[g] - f_XY[g]
    return res

# Now let's set up the system:
# gamma(X, Y) == delta f(X, Y) for all X, Y in gen_list
equations = []
for g1 in gen_list:
    for g2 in gen_list:
        df = compute_delta_f(g1, g2)
        gam = gamma[(g1, g2)]
        for g in gen_list:
            eq = sp.simplify(df[g] - gam[g])
            if eq != 0:
                equations.append(eq)

print(f"Total equations: {len(equations)}")

# Let's solve for phi in terms of gb parameters!
sol = sp.solve(equations, all_phi_vars)
print("Solution for f:")
print(sol)

# What are the remaining conditions on gb?
# Let's substitute sol back into equations:
remaining = []
for eq in equations:
    rem = sp.simplify(eq.subs(sol))
    if rem != 0:
        remaining.append(rem)

remaining = list(set(remaining))
print(f"Number of remaining constraints on gb: {len(remaining)}")
for r in remaining:
    print("Constraint:", r)
