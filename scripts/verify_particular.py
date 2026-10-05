import sympy as sp
from test_triviality import run_analysis
from collections import defaultdict

basis_names, basis_parity, bracket_0, gamma_gb, gb_syms = run_analysis(1)

even_indices = [name for name in basis_names if basis_parity[name] == 0]
odd_indices = [name for name in basis_names if basis_parity[name] == 1]

phi_syms = {}
for j in even_indices:
    for k in odd_indices:
        phi_syms[(k, j)] = sp.Symbol(f"phi_{k}_{j}")
for j in odd_indices:
    for k in even_indices:
        phi_syms[(k, j)] = sp.Symbol(f"phi_{k}_{j}")

def eval_b0(name_X, name_Y):
    if (name_X, name_Y) in bracket_0:
        return bracket_0[(name_X, name_Y)]
    else:
        pX = basis_parity[name_X]
        pY = basis_parity[name_Y]
        sign = -1 if (pX == 1 and pY == 1) else 1
        inv = bracket_0[(name_Y, name_X)]
        return {k: -sign * v for k, v in inv.items()}

def apply_f(elem_dict):
    res = defaultdict(lambda: sp.Integer(0))
    for name, c in elem_dict.items():
        if basis_parity[name] == 0:
            for k in odd_indices:
                res[k] += c * phi_syms[(k, name)]
        else:
            for k in even_indices:
                res[k] += c * phi_syms[(k, name)]
    return {k: sp.simplify(v) for k, v in res.items() if v != 0}

def bracket_name_dict(name_X, elem_dict):
    res = defaultdict(lambda: sp.Integer(0))
    for name_Y, c in elem_dict.items():
        b = eval_b0(name_X, name_Y)
        for k, v in b.items():
            res[k] += c * v
    return {k: sp.simplify(v) for k, v in res.items() if v != 0}

def compute_delta_f(name_X, name_Y):
    pX = basis_parity[name_X]
    pY = basis_parity[name_Y]
    s1 = -1 if pX == 1 else 1
    fY = apply_f({name_Y: sp.Integer(1)})
    t1 = bracket_name_dict(name_X, fY)
    s2 = - (-1 if ((pX + 1) * pY) % 2 == 1 else 1)
    fX = apply_f({name_X: sp.Integer(1)})
    t2 = bracket_name_dict(name_Y, fX)
    bXY = eval_b0(name_X, name_Y)
    t3 = apply_f(bXY)
    res = defaultdict(lambda: sp.Integer(0))
    for k, v in t1.items(): res[k] += s1 * v
    for k, v in t2.items(): res[k] += s2 * v
    for k, v in t3.items(): res[k] -= v
    return {k: sp.simplify(v) for k, v in res.items() if v != 0}

all_equations = []
for i, name_X in enumerate(basis_names):
    for j in range(i, len(basis_names)):
        name_Y = basis_names[j]
        df = compute_delta_f(name_X, name_Y)
        gam = gamma_gb[(name_X, name_Y)]
        all_gens = set(df.keys()).union(set(gam.keys()))
        for g in all_gens:
            val_df = df.get(g, sp.Integer(0))
            val_gam = gam.get(g, sp.Integer(0))
            eq = sp.simplify(val_df - val_gam)
            if eq != 0:
                all_equations.append(eq)

phi_vars = list(phi_syms.values())
# Solve for phi in terms of gb
sol_phi = sp.solve(all_equations, phi_vars)
print("Solution for phi in terms of gb found?")
print("Is dict?", isinstance(sol_phi, dict))
for k, v in sol_phi.items():
    # If expression contains gb, print it!
    gb_in_v = [s for s in gb_syms.values() if s in v.free_symbols]
    if gb_in_v:
        print(f"{k} = {v}")

# Now let's pick a particular solution by setting all other free phi parameters to 0
# and substitute back into delta f to verify that delta f == gamma_gb EXACTLY!
subs_dict = {}
for var in phi_vars:
    if var in sol_phi:
        subs_dict[var] = sol_phi[var]
    else:
        subs_dict[var] = 0

# Set remaining free phi to 0
free_in_sol = set()
for v in subs_dict.values():
    if hasattr(v, 'free_symbols'):
        free_in_sol.update([s for s in v.free_symbols if s not in gb_syms.values()])

for s in free_in_sol:
    for k in subs_dict:
        if hasattr(subs_dict[k], 'subs'):
            subs_dict[k] = subs_dict[k].subs(s, 0)

print("\n--- Testing verification of delta_f == gamma_gb with particular phi(gb) ---")
mismatches = 0
for i, name_X in enumerate(basis_names):
    for j in range(i, len(basis_names)):
        name_Y = basis_names[j]
        df = compute_delta_f(name_X, name_Y)
        gam = gamma_gb[(name_X, name_Y)]
        all_gens = set(df.keys()).union(set(gam.keys()))
        for g in all_gens:
            v_df = df.get(g, sp.Integer(0)).subs(subs_dict)
            v_gam = gam.get(g, sp.Integer(0))
            diff = sp.simplify(v_df - v_gam)
            if diff != 0:
                mismatches += 1
                print(f"Mismatch at ({name_X}, {name_Y}) component {g}: df={v_df}, gam={v_gam}")

if mismatches == 0:
    print("SUCCESS: delta_f == gamma_gb IDENTICALLY for ALL values of gb!")
else:
    print(f"FAILED: {mismatches} mismatches.")
