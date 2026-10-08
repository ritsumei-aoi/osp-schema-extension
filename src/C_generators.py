import fractions
import itertools
import json
import os

def rank(op):
    if op == "a_1_p": return 0
    if op == "a_1_m": return 1
    if op.startswith("b_") and op.endswith("_p"):
        k = int(op.split("_")[1])
        return 2*k
    if op.startswith("b_") and op.endswith("_m"):
        k = int(op.split("_")[1])
        return 2*k + 1
    return 99

def is_odd(op):
    return op.startswith("a_")

def add_term(poly, word, coeff):
    if word in poly:
        poly[word] += coeff
    else:
        poly[word] = coeff
    if poly[word] == 0:
        del poly[word]

def normal_order(word):
    poly = {word: fractions.Fraction(1)}
    changed = True
    while changed:
        changed = False
        new_poly = {}
        for w, coeff in poly.items():
            if coeff == 0: continue
            
            ordered = True
            for i in range(len(w) - 1):
                if rank(w[i]) > rank(w[i+1]):
                    ordered = False
                    x, y = w[i], w[i+1]
                    
                    if is_odd(x) and is_odd(y):
                        w_swapped = w[:i] + (y, x) + w[i+2:]
                        add_term(new_poly, w_swapped, -coeff)
                        if x == "a_1_m" and y == "a_1_p":
                            w_rest = w[:i] + w[i+2:]
                            add_term(new_poly, w_rest, coeff)
                    elif not is_odd(x) and not is_odd(y):
                        w_swapped = w[:i] + (y, x) + w[i+2:]
                        add_term(new_poly, w_swapped, coeff)
                        if x.endswith("_m") and y.endswith("_p") and x[2:-2] == y[2:-2]:
                            w_rest = w[:i] + w[i+2:]
                            add_term(new_poly, w_rest, coeff)
                    else:
                        w_swapped = w[:i] + (y, x) + w[i+2:]
                        add_term(new_poly, w_swapped, coeff)
                    break
            
            if ordered:
                has_square = False
                for i in range(len(w)-1):
                    if w[i] == w[i+1] and is_odd(w[i]):
                        has_square = True
                if not has_square:
                    add_term(new_poly, w, coeff)
            else:
                changed = True
        
        if changed:
            poly = new_poly
            
    return {w: c for w, c in poly.items() if c != 0}

def mul_polys(p1, p2):
    res = {}
    for w1, c1 in p1.items():
        for w2, c2 in p2.items():
            add_term(res, w1 + w2, c1 * c2)
    
    no_res = {}
    for w, c in res.items():
        w_poly = normal_order(w)
        for w_no, c_no in w_poly.items():
            add_term(no_res, w_no, c * c_no)
    return no_res

def add_polys(p1, p2):
    res = dict(p1)
    for w, c in p2.items():
        add_term(res, w, c)
    return res

def mul_scalar(p, s):
    return {w: c * fractions.Fraction(s) for w, c in p.items() if c * s != 0}

def build_basis(n):
    basis = []
    basis.append(("K", {(): fractions.Fraction(1)}, 0))
    h1 = {("a_1_p", "a_1_m"): fractions.Fraction(1), ("b_1_p", "b_1_m"): fractions.Fraction(1)}
    basis.append(("H_1", h1, 0))
    for k in range(2, n + 1):
        hk = {
            (f"b_{k-1}_p", f"b_{k-1}_m"): fractions.Fraction(1),
            (f"b_{k}_p", f"b_{k}_m"): fractions.Fraction(-1)
        }
        basis.append((f"H_{k}", hk, 0))
    hn1 = {
        (f"b_{n}_p", f"b_{n}_m"): fractions.Fraction(-1),
        (): fractions.Fraction(-1, 2)
    }
    basis.append((f"H_{n+1}", hn1, 0))
    
    for k in range(1, n + 1):
        basis.append((f"E_2del{k}_p", {(f"b_{k}_p", f"b_{k}_p"): fractions.Fraction(1)}, 0))
        basis.append((f"E_2del{k}_m", {(f"b_{k}_m", f"b_{k}_m"): fractions.Fraction(1)}, 0))
    for k in range(1, n + 1):
        for l in range(k + 1, n + 1):
            basis.append((f"E_del{k}_del{l}_pp", {(f"b_{k}_p", f"b_{l}_p"): fractions.Fraction(1)}, 0))
            basis.append((f"E_del{k}_del{l}_pm", {(f"b_{k}_p", f"b_{l}_m"): fractions.Fraction(1)}, 0))
            basis.append((f"E_del{k}_del{l}_mp", {(f"b_{k}_m", f"b_{l}_p"): fractions.Fraction(1)}, 0))
            basis.append((f"E_del{k}_del{l}_mm", {(f"b_{k}_m", f"b_{l}_m"): fractions.Fraction(1)}, 0))
            
    for k in range(1, n + 1):
        basis.append((f"E_eps1_del{k}_pp", {("a_1_p", f"b_{k}_p"): fractions.Fraction(1)}, 1))
        basis.append((f"E_eps1_del{k}_pm", {("a_1_p", f"b_{k}_m"): fractions.Fraction(1)}, 1))
        basis.append((f"E_eps1_del{k}_mp", {("a_1_m", f"b_{k}_p"): fractions.Fraction(1)}, 1))
        basis.append((f"E_eps1_del{k}_mm", {("a_1_m", f"b_{k}_m"): fractions.Fraction(1)}, 1))
        
    return basis

def solve_linear(matrix, target):
    rows = len(matrix)
    cols = len(matrix[0])
    for i in range(cols):
        pivot = -1
        for j in range(i, rows):
            if matrix[j][i] != 0:
                pivot = j
                break
        if pivot == -1: continue
        matrix[i], matrix[pivot] = matrix[pivot], matrix[i]
        target[i], target[pivot] = target[pivot], target[i]
        
        inv = fractions.Fraction(1) / matrix[i][i]
        for j in range(cols): matrix[i][j] *= inv
        target[i] *= inv
        
        for j in range(rows):
            if i != j and matrix[j][i] != 0:
                factor = matrix[j][i]
                for k in range(cols): matrix[j][k] -= factor * matrix[i][k]
                target[j] -= factor * target[i]
    return target

def decompose(poly, basis):
    words = list(set(word for name, p, parity in basis for word in p.keys()) | set(poly.keys()))
    matrix = []
    for name, p, parity in basis:
        row = [p.get(w, fractions.Fraction(0)) for w in words]
        matrix.append(row)
    
    matrix_t = [[matrix[j][i] for j in range(len(basis))] for i in range(len(words))]
    target = [poly.get(w, fractions.Fraction(0)) for w in words]
    
    coeffs = solve_linear(matrix_t, target)
    
    res = []
    for i, (name, p, parity) in enumerate(basis):
        if coeffs[i] != 0:
            res.append({"Z": name, "coeff": str(coeffs[i])})
    return res

def build_schema(n):
    basis = build_basis(n)
    constants = []
    for i in range(len(basis)):
        name_x, poly_x, parity_x = basis[i]
        if name_x == "K": continue
        for j in range(i, len(basis)):
            name_y, poly_y, parity_y = basis[j]
            if name_y == "K": continue
            
            xy = mul_polys(poly_x, poly_y)
            yx = mul_polys(poly_y, poly_x)
            
            sign = -1 if (parity_x == 1 and parity_y == 1) else 1
            bracket = add_polys(xy, mul_scalar(yx, -sign))
            
            if not bracket: continue
            
            decomp = decompose(bracket, basis)
            if decomp:
                for term in decomp:
                    constants.append({
                        "X": name_x,
                        "Y": name_y,
                        "Z": term["Z"],
                        "coeff": term["coeff"],
                        "sign_rule": "graded"
                    })
                    
    # Build complete JSON schema
    schema = {
        "schema_version": "5.0",
        "algebra": {
            "family": "C",
            "m": 1,
            "n": n,
            "cartan_type": f"C({n+1})",
            "alternative_notation": {
                "osp": f"osp(2|{2*n})",
                "dimension_formula": "osp(2m|2n) with m=1"
            },
            "dimension": {
                "total": 2*n**2 + 5*n + 1,
                "even": 2*n**2 + n + 1,
                "odd": 4*n
            }
        },
        "oscillator_generators": {
            "fermions": {
                "m": 1,
                "labels": ["a_1_p", "a_1_m"],
                "description": "Standard fermionic pair"
            },
            "bosons": {
                "count": 2*n,
                "n": n,
                "labels": [f"b_{k}_{s}" for k in range(1, n+1) for s in ("p", "m")],
                "description": "Bosonic oscillators b_k^± with k=1,...,n"
            }
        },
        "oscillator_relations": {
            "standard_fermion_anticommutators": {
                "description": "Canonical anticommutation relations for fermions",
                "relations": {
                    "conjugate_pair": "{a_1_m, a_1_p} = 1",
                    "same_type": "{a_1_p, a_1_p} = 0, {a_1_m, a_1_m} = 0"
                }
            },
            "bosonic_commutators": {
                "description": "Canonical commutation relations for bosonic oscillators",
                "relations": {
                    "same_type": "[b_i^±, b_j^±] = 0",
                    "conjugate_pair": "[b_i^m, b_j^p] = δ_{ij}"
                }
            },
            "mixed_commutators": {
                "boson_fermion": "[b_i^±, a_1^±] = 0"
            }
        },
        "central_elements": {
            "kappa": {
                "parity": 1,
                "description": "Odd central extension element"
            },
            "K": {
                "parity": 0,
                "description": "Even central element (identified with scalar 1)"
            }
        },
        "basis": {
            "even": [b[0] for b in basis if b[2] == 0 and b[0] != "K"],
            "odd": [b[0] for b in basis if b[2] == 1],
            "ordering_convention": "PBW: Negative Roots < Cartan < Positive Roots"
        },
        "parity": {b[0]: b[2] for b in basis if b[0] != "K"},
        "structure_constants": constants
    }
    return schema

if __name__ == "__main__":
    for n in [1, 2, 3]:
        schema = build_schema(n)
        with open(f"data/C_{n}_structure.json", "w") as f:
            json.dump(schema, f, indent=2)
        print(f"n={n}: Generated {len(schema['structure_constants'])} non-zero brackets.")
