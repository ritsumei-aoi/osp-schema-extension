"""
Scratch script to test all generators and their commutators for C(2), C(3), C(4).
"""
from fractions import Fraction
from collections import defaultdict
import json

def order_key(osc):
    if osc == "a_1_p": return (0, 0)
    if osc == "a_1_m": return (0, 1)
    if osc.startswith("b_"):
        parts = osc.split("_")
        k = int(parts[1])
        s = 0 if parts[2] == "p" else 1
        return (k, s)
    raise ValueError(f"Unknown osc: {osc}")

def normal_order_word(word, coeff):
    current = {tuple(word): coeff}
    changed = True
    while changed:
        changed = False
        new_current = defaultdict(Fraction)
        for w, c in current.items():
            if c == 0:
                continue
            inversion_idx = -1
            for i in range(len(w) - 1):
                if order_key(w[i]) > order_key(w[i+1]):
                    inversion_idx = i
                    break
                elif w[i] == w[i+1]:
                    if w[i] in ("a_1_p", "a_1_m"):
                        inversion_idx = -2
                        break
            
            if inversion_idx == -2:
                changed = True
                continue
            elif inversion_idx == -1:
                new_current[w] += c
            else:
                changed = True
                i = inversion_idx
                x, y = w[i], w[i+1]
                prefix = w[:i]
                suffix = w[i+2:]
                
                if x == "a_1_m" and y == "a_1_p":
                    new_current[prefix + ("a_1_p", "a_1_m") + suffix] += -c
                    new_current[prefix + suffix] += c
                elif x.startswith("b_") and y.startswith("b_"):
                    px = x.split("_")
                    py = y.split("_")
                    if px[1] == py[1] and px[2] == "m" and py[2] == "p":
                        new_current[prefix + (f"b_{px[1]}_p", f"b_{px[1]}_m") + suffix] += c
                        new_current[prefix + suffix] += c
                    else:
                        new_current[prefix + (y, x) + suffix] += c
                else:
                    new_current[prefix + (y, x) + suffix] += c
        current = new_current
    return {w: c for w, c in current.items() if c != 0}

def multiply_elements(poly1, poly2):
    # poly: dict of {tuple(word): Fraction}
    res = defaultdict(Fraction)
    for w1, c1 in poly1.items():
        for w2, c2 in poly2.items():
            combined_w = list(w1) + list(w2)
            c = c1 * c2
            no = normal_order_word(combined_w, c)
            for w, cw in no.items():
                res[w] += cw
    return {w: c for w, c in res.items() if c != 0}

def add_elements(poly1, poly2, scale2=Fraction(1)):
    res = defaultdict(Fraction, poly1)
    for w, c in poly2.items():
        res[w] += c * scale2
    return {w: c for w, c in res.items() if c != 0}

def superbracket(poly1, p1, poly2, p2):
    # [X, Y} = X Y - (-1)^{p1 p2} Y X
    sign = Fraction(-1) if (p1 * p2) % 2 == 1 else Fraction(1)
    xy = multiply_elements(poly1, poly2)
    yx = multiply_elements(poly2, poly1)
    return add_elements(xy, yx, -sign)

def get_c_generators(n):
    # Returns basis_dict: {name: {"poly": dict, "parity": int, "label": str}}
    # and basis_list: list of names in PBW order
    generators = {}
    
    # Cartan
    # H_1 = a_1^+ a_1^- + b_1^+ b_1^-
    generators["H_1"] = {
        "poly": {("a_1_p", "a_1_m"): Fraction(1), ("b_1_p", "b_1_m"): Fraction(1)},
        "parity": 0
    }
    for k in range(2, n + 1):
        # H_k = b_{k-1}^+ b_{k-1}^- - b_k^+ b_k^-
        generators[f"H_{k}"] = {
            "poly": {(f"b_{k-1}_p", f"b_{k-1}_m"): Fraction(1), (f"b_{k}_p", f"b_{k}_m"): Fraction(-1)},
            "parity": 0
        }
    # H_{n+1} = -b_n^+ b_n^- - 1/2
    generators[f"H_{n+1}"] = {
        "poly": {(f"b_{n}_p", f"b_{n}_m"): Fraction(-1), (): Fraction(-1, 2)},
        "parity": 0
    }
    
    # 2del_k
    for k in range(1, n + 1):
        generators[f"E_2del{k}_p"] = {
            "poly": {(f"b_{k}_p", f"b_{k}_p"): Fraction(1)},
            "parity": 0
        }
        generators[f"E_2del{k}_m"] = {
            "poly": {(f"b_{k}_m", f"b_{k}_m"): Fraction(1)},
            "parity": 0
        }
        
    # del_i_del_j
    for i in range(1, n + 1):
        for j in range(i + 1, n + 1):
            generators[f"E_del{i}_del{j}_pp"] = {
                "poly": {(f"b_{i}_p", f"b_{j}_p"): Fraction(1)},
                "parity": 0
            }
            generators[f"E_del{i}_del{j}_mm"] = {
                "poly": {(f"b_{i}_m", f"b_{j}_m"): Fraction(1)},
                "parity": 0
            }
            generators[f"E_del{i}_del{j}_pm"] = {
                "poly": {(f"b_{i}_p", f"b_{j}_m"): Fraction(1)},
                "parity": 0
            }
            generators[f"E_del{i}_del{j}_mp"] = {
                "poly": {(f"b_{i}_m", f"b_{j}_p"): Fraction(1)},
                "parity": 0
            }
            
    # Odd generators: E_eps_del{k}_{sign_eps}{sign_del}
    for k in range(1, n + 1):
        generators[f"E_eps_del{k}_pp"] = {
            "poly": {("a_1_p", f"b_{k}_p"): Fraction(1)},
            "parity": 1
        }
        generators[f"E_eps_del{k}_pm"] = {
            "poly": {("a_1_p", f"b_{k}_m"): Fraction(1)},
            "parity": 1
        }
        generators[f"E_eps_del{k}_mp"] = {
            "poly": {("a_1_m", f"b_{k}_p"): Fraction(1)},
            "parity": 1
        }
        generators[f"E_eps_del{k}_mm"] = {
            "poly": {("a_1_m", f"b_{k}_m"): Fraction(1)},
            "parity": 1
        }
        
    return generators

# Let's test closure for n=1:
gen1 = get_c_generators(1)
print(f"n=1 generator count: {len(gen1)}")
basis_names = list(gen1.keys())

# Check all brackets
def decompose_into_basis(poly, basis_dict):
    # Returns {basis_name: coeff} if poly is in span, else None
    rem = dict(poly)
    decomp = {}
    for name, data in basis_dict.items():
        b_poly = data["poly"]
        # Find if there is a word in b_poly not in scalar
        # Usually each b_poly has a unique leading word
        pass

# Let's test by comparing each bracket against the basis
for n in [1, 2]:
    gens = get_c_generators(n)
    print(f"\n--- Testing closure for n={n} (dim = {len(gens)}) ---")
    all_closed = True
    bracket_count = 0
    non_zero_count = 0
    names = list(gens.keys())
    
    # Map from canonical tuple to generator name
    # Notice each root generator has a unique word!
    # Cartan generators have words:
    # H_1: a_1_p a_1_m + b_1_p b_1_m
    # H_k: b_{k-1}_p b_{k-1}_m - b_k_p b_k_m
    # H_{n+1}: -b_n_p b_n_m - 1/2
    # So we can set up a linear system to express any element in the basis.
    
    # Collect all words appearing in basis or brackets
    basis_matrix = {} # word -> vector of coeffs for each basis elt
    all_basis_words = set()
    for name, data in gens.items():
        for w in data["poly"]:
            all_basis_words.add(w)
            
    word_list = sorted(list(all_basis_words))
    # Check linear independence of basis
    # Construct matrix
    import numpy as np
    M = np.zeros((len(word_list), len(names)))
    for j, name in enumerate(names):
        for i, w in enumerate(word_list):
            M[i, j] = float(gens[name]["poly"].get(w, 0))
    rank = np.linalg.matrix_rank(M)
    print(f"Basis rank: {rank} / {len(names)} (words: {len(word_list)})")
    assert rank == len(names), "Basis is not linearly independent!"
    
    # Now check all brackets [X, Y}
    # Using exact rational Gaussian elimination / pseudo-inverse with sympy
    import sympy as sp
    M_sp = sp.Matrix([[gens[name]["poly"].get(w, Fraction(0)) for name in names] for w in word_list])
    
    # Test brackets
    for i in range(len(names)):
        for j in range(len(names)):
            name1, name2 = names[i], names[j]
            p1, p2 = gens[name1]["parity"], gens[name2]["parity"]
            br = superbracket(gens[name1]["poly"], p1, gens[name2]["poly"], p2)
            bracket_count += 1
            if not br:
                continue
            non_zero_count += 1
            # Check if br has any words not in word_list
            for w in br:
                if w not in word_list:
                    print(f"UNKNOWN WORD {w} in [{name1}, {name2}]")
                    all_closed = False
            # Check if vector is in column space
            br_vec = sp.Matrix([br.get(w, Fraction(0)) for w in word_list])
            sol = M_sp.gauss_jordan_solve(br_vec)
            # check if solution is exact
            recon = M_sp * sol[0]
            if recon != br_vec:
                print(f"FAILED TO DECOMPOSE [{name1}, {name2}]")
                all_closed = False
                
    print(f"Closure for n={n}: {all_closed}! Total non-zero brackets: {non_zero_count}/{bracket_count}")
