import json
import sympy as sp

def analyze_triviality(n):
    with open(f"data/C_{n}_gamma.json") as f:
        gamma_data = json.load(f)
    with open(f"data/C_{n}_coboundary.json") as f:
        coboundary_data = json.load(f)
        
    gamma_eqs = {}
    for entry in gamma_data["gamma_structure"]:
        X, Y = entry["X"], entry["Y"]
        for term in entry["gamma_expansion"]:
            Z, gb, c = term["Z"], term["gb_param"], sp.Rational(term["coeff"])
            if (X, Y, Z) not in gamma_eqs:
                gamma_eqs[(X, Y, Z)] = 0
            gamma_eqs[(X, Y, Z)] += c * sp.Symbol(gb)
            
    cob_eqs = {}
    phi_symbols = set()
    for entry in coboundary_data["coboundary_structure"]:
        X, Y = entry["X"], entry["Y"]
        for term in entry["coboundary_expansion"]:
            Z, phi, c = term["Z"], term["phi_param"], sp.Rational(term["coeff"])
            if (X, Y, Z) not in cob_eqs:
                cob_eqs[(X, Y, Z)] = 0
            cob_eqs[(X, Y, Z)] += c * sp.Symbol(phi)
            phi_symbols.add(sp.Symbol(phi))
            
    equations = []
    all_keys = set(gamma_eqs.keys()) | set(cob_eqs.keys())
    for k in all_keys:
        rhs = gamma_eqs.get(k, 0)
        lhs = cob_eqs.get(k, 0)
        if lhs != 0 or rhs != 0:
            equations.append(lhs - rhs)
            
    print(f"n={n}: Solving {len(equations)} equations with {len(phi_symbols)} variables...")
    solution = sp.solve(equations, list(phi_symbols))
    if solution:
        print(f"n={n}: Deformation is TRIVIAL! Solution found.")
    else:
        print(f"n={n}: Deformation is NON-TRIVIAL! No solution exists.")
        
if __name__ == "__main__":
    for n in [1, 2]:
        analyze_triviality(n)
