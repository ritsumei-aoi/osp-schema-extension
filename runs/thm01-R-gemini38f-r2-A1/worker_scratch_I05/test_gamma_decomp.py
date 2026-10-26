"""
Append bracket computation and basis decomposition for gamma to derive_gamma.py.
"""
from derive_gamma import normal_order_deformed, get_gb_label
from src.C_generators import build_c_basis
from collections import defaultdict
from fractions import Fraction
import sympy as sp

def multiply_deformed(poly1, poly2):
    # poly1, poly2 are dict {word: Fraction} in U(A)_0
    res_0 = defaultdict(Fraction)
    res_kappa = defaultdict(Fraction)
    for w1, c1 in poly1.items():
        for w2, c2 in poly2.items():
            w = list(w1) + list(w2)
            c = c1 * c2
            p0, pk = normal_order_deformed(w, c)
            for nw, nc in p0.items():
                res_0[nw] += nc
            for nk, nc in pk.items():
                res_kappa[nk] += nc
    return res_0, res_kappa

def deformed_superbracket(poly1, p1, poly2, p2):
    # [X, Y}_\gamma = X Y - (-1)^{p1 p2} Y X
    # Returns (br_0, br_kappa)
    # br_0: {word: Fraction}
    # br_kappa: {(word, gb_name): Fraction}
    s = Fraction(-1) if (p1 * p2) % 2 == 1 else Fraction(1)
    xy_0, xy_k = multiply_deformed(poly1, poly2)
    yx_0, yx_k = multiply_deformed(poly2, poly1)
    
    br_0 = defaultdict(Fraction, xy_0)
    for w, c in yx_0.items():
        br_0[w] -= s * c
        
    br_k = defaultdict(Fraction, xy_k)
    for k, c in yx_k.items():
        br_k[k] -= s * c
        
    return {w: c for w, c in br_0.items() if c != 0}, {k: c for k, c in br_k.items() if c != 0}

def test_gamma(n):
    even_basis, odd_basis, generators = build_c_basis(n)
    full_basis = even_basis + odd_basis
    print(f"\n=== Testing Gamma for n={n} (dim={len(full_basis)}) ===")
    
    all_words = set()
    for g in generators.values():
        all_words.update(g["poly"].keys())
    word_list = sorted(list(all_words))
    M_sp = sp.Matrix(
        [[generators[name]["poly"].get(w, Fraction(0)) for name in full_basis] for w in word_list]
    )
    
    # Let's compute all deformed brackets
    gamma_entries = [] # (X, Y, gb_name, Z, coeff)
    unmatched = []
    
    for i, X in enumerate(full_basis):
        pX = generators[X]["parity"]
        for j, Y in enumerate(full_basis):
            pY = generators[Y]["parity"]
            br_0, br_k = deformed_superbracket(generators[X]["poly"], pX, generators[Y]["poly"], pY)
            
            # Group br_k by gb_name
            by_gb = defaultdict(lambda: defaultdict(Fraction))
            for (w, gb), c in br_k.items():
                by_gb[gb][w] += c
                
            for gb, w_dict in by_gb.items():
                # Check if all words are in word_list
                for w in w_dict:
                    if w not in word_list:
                        unmatched.append((X, Y, gb, w, w_dict[w]))
                # Decompose into basis
                vec = sp.Matrix([w_dict.get(w, Fraction(0)) for w in word_list])
                sol, _ = M_sp.gauss_jordan_solve(vec)
                for k, Z in enumerate(full_basis):
                    c = sol[k]
                    if c != 0:
                        gamma_entries.append((X, Y, gb, Z, c))
                        
    print(f"Total gamma entries (X, Y, gb -> Z): {len(gamma_entries)}")
    print(f"Unmatched words: {len(unmatched)}")
    if unmatched:
        print("First unmatched:", unmatched[0])
    else:
        print("ALL gamma terms perfectly decompose into the Lie superalgebra basis!")
        
    # Sample gamma entries
    print("Sample non-zero gamma entries:")
    for entry in gamma_entries[:10]:
        print(f"  [{entry[0]}, {entry[1]}]_gamma ({entry[2]}) -> {entry[4]} * {entry[3]}")
        
    return gamma_entries

if __name__ == "__main__":
    test_gamma(1)
