import fractions
import json

def rank(op):
    if op == "a_1_p": return 0
    if op == "a_1_m": return 1
    if op.startswith("b_") and op.endswith("_p"): return 2 * int(op.split("_")[1])
    if op.startswith("b_") and op.endswith("_m"): return 2 * int(op.split("_")[1]) + 1
    return 99

def is_odd(op):
    return op.startswith("a_")

def normal_order_gb(word, start_gb=None):
    poly = {(word, start_gb): fractions.Fraction(1)}
    changed = True
    while changed:
        changed = False
        new_poly = {}
        for (w, gb), coeff in poly.items():
            if coeff == 0: continue
            
            ordered = True
            for i in range(len(w) - 1):
                if rank(w[i]) > rank(w[i+1]):
                    ordered = False
                    x, y = w[i], w[i+1]
                    
                    if is_odd(x) and is_odd(y):
                        new_w = w[:i] + (y, x) + w[i+2:]
                        new_poly[(new_w, gb)] = new_poly.get((new_w, gb), fractions.Fraction(0)) - coeff
                        if x == "a_1_m" and y == "a_1_p":
                            rest = w[:i] + w[i+2:]
                            new_poly[(rest, gb)] = new_poly.get((rest, gb), fractions.Fraction(0)) + coeff
                    elif not is_odd(x) and not is_odd(y):
                        new_w = w[:i] + (y, x) + w[i+2:]
                        new_poly[(new_w, gb)] = new_poly.get((new_w, gb), fractions.Fraction(0)) + coeff
                        if x.endswith("_m") and y.endswith("_p") and x[2:-2] == y[2:-2]:
                            rest = w[:i] + w[i+2:]
                            new_poly[(rest, gb)] = new_poly.get((rest, gb), fractions.Fraction(0)) + coeff
                    else:
                        new_w = w[:i] + (y, x) + w[i+2:]
                        new_poly[(new_w, gb)] = new_poly.get((new_w, gb), fractions.Fraction(0)) + coeff
                        
                        if gb is None:
                            rest = w[:i] + w[i+2:]
                            gb_label = f"gb_{y}_{x}"
                            new_poly[(rest, gb_label)] = new_poly.get((rest, gb_label), fractions.Fraction(0)) - coeff
                    break
            
            if ordered:
                has_sq = any(w[i] == w[i+1] and is_odd(w[i]) for i in range(len(w)-1))
                if not has_sq:
                    new_poly[(w, gb)] = new_poly.get((w, gb), fractions.Fraction(0)) + coeff
            else:
                changed = True
        
        poly = {k: v for k, v in new_poly.items() if v != 0}
        if changed: continue
        
    return poly

def mul_polys_gb(p1, p2):
    res = {}
    for w1, c1 in p1.items():
        for w2, c2 in p2.items():
            poly = normal_order_gb(w1 + w2, None)
            for (w_no, gb_no), c_no in poly.items():
                k = (w_no, gb_no)
                res[k] = res.get(k, fractions.Fraction(0)) + c1 * c2 * c_no
    return {k: v for k, v in res.items() if v != 0}

from C_generators import build_basis, decompose, mul_scalar

def compute_gamma(n):
    basis = build_basis(n)
    gamma_constants = []
    
    for i in range(len(basis)):
        name_x, poly_x, parity_x = basis[i]
        if name_x == "K": continue
        for j in range(i, len(basis)):
            name_y, poly_y, parity_y = basis[j]
            if name_y == "K": continue
            
            xy = mul_polys_gb(poly_x, poly_y)
            yx = mul_polys_gb(poly_y, poly_x)
            
            sign = -1 if (parity_x == 1 and parity_y == 1) else 1
            
            bracket = dict(xy)
            for k, v in yx.items():
                bracket[k] = bracket.get(k, fractions.Fraction(0)) - sign * v
                if bracket[k] == 0: del bracket[k]
                
            gb_groups = {}
            for (w, gb), c in bracket.items():
                if gb is not None:
                    if gb not in gb_groups: gb_groups[gb] = {}
                    gb_groups[gb][w] = gb_groups[gb].get(w, fractions.Fraction(0)) + c
                    
            for gb, poly in gb_groups.items():
                poly = {w: c for w, c in poly.items() if c != 0}
                if not poly: continue
                
                decomp = decompose(poly, basis)
                for term in decomp:
                    gamma_constants.append({
                        "X": name_x,
                        "Y": name_y,
                        "Z": term["Z"],
                        "gb_parameter": gb,
                        "coeff": term["coeff"],
                        "sign_rule": "graded"
                    })
                    
    return gamma_constants

def build_schema2(n):
    gamma = compute_gamma(n)
    
    with open(f"data/C_{n}_structure.json", "r") as f:
        schema1 = json.load(f)
        
    schema2 = {
        "schema_version": "5.0",
        "algebra": schema1["algebra"],
        "oscillator_generators": schema1["oscillator_generators"],
        "inhomogeneous_deformation": gamma
    }
    return schema2

if __name__ == "__main__":
    for n in [1, 2, 3]:
        s2 = build_schema2(n)
        with open(f"data/C_{n}_gamma.json", "w") as f:
            json.dump(s2, f, indent=2)
        print(f"n={n}: Generated {len(s2['inhomogeneous_deformation'])} gamma terms.")
