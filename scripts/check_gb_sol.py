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

# Check what constraints exist on gb
# Solve for all variables
res = sp.linsolve(all_equations, list(gb_syms.values()) + list(phi_syms.values()))
print("Number of free parameters in full solution:", len(res.args[0]) - len([x for x in res.args[0] if x.is_Symbol]))

# Let's print the expressions for gb:
for k, sym in enumerate(gb_syms.values()):
    print(f"{sym} = {res.args[0][k]}")
