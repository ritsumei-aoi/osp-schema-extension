from fractions import Fraction
from collections import defaultdict
import sys
sys.path.append('.')
from src.C_generators import Monomial, Poly

# We can define a general word normalizer in U(A):
# An oscillator string: e.g. ("a_1_p", "b_1_p", ...)
# Returns:
# - undeformed_poly: Poly
# - deformed_poly_by_param: dict of {param: Poly}

# Precedence for normal ordering:
# a_1_p < a_1_m < b_1_p < b_1_m < b_2_p < ...
def osc_rank(name, n):
    if name == "a_1_p": return 0
    if name == "a_1_m": return 1
    parts = name.split("_")
    k = int(parts[1]) - 1
    s = 0 if parts[2] == "p" else 1
    return 2 + 2 * k + s

def normal_order_word(word, n, sign_choice=1):
    # word is a tuple of osc names
    # We do bubble sort with relations!
    # State: list of (word_tuple, coeff, is_kappa, param)
    # is_kappa = False -> undeformed
    # is_kappa = True -> coefficient of kappa * param
    
    current_terms = [(word, Fraction(1), False, None)]
    
    while True:
        next_terms = []
        all_sorted = True
        for w, coeff, is_kap, par in current_terms:
            # Find first out-of-order pair
            pair_found = False
            for i in range(len(w) - 1):
                x, y = w[i], w[i+1]
                rx, ry = osc_rank(x, n), osc_rank(y, n)
                if rx > ry:
                    pair_found = True
                    all_sorted = False
                    # Rewrite w[i], w[i+1]:
                    # Prefix and suffix
                    pre = w[:i]
                    suf = w[i+2:]
                    
                    # What is the exchange relation between x and y?
                    # Case 1: x=a_1_m, y=a_1_p: a_m a_p = 1 - a_p a_m
                    if x == "a_1_m" and y == "a_1_p":
                        # term 1: - a_p a_m
                        next_terms.append((pre + ("a_1_p", "a_1_m") + suf, -coeff, is_kap, par))
                        # term 2: 1
                        next_terms.append((pre + suf, coeff, is_kap, par))
                    # Case 2: x=b_k_m, y=b_k_p: b_m b_p = b_p b_m + 1
                    elif x.startswith("b_") and y.startswith("b_"):
                        px, py = x.split("_"), y.split("_")
                        if px[1] == py[1] and px[2] == "m" and py[2] == "p":
                            next_terms.append((pre + (y, x) + suf, coeff, is_kap, par))
                            next_terms.append((pre + suf, coeff, is_kap, par))
                        else:
                            # They commute!
                            next_terms.append((pre + (y, x) + suf, coeff, is_kap, par))
                    # Case 3: x is boson, y is fermion: b_j^s a_1^sigma = a_1^sigma b_j^s - gb * kappa
                    elif x.startswith("b_") and y.startswith("a_"):
                        # term 1: a_1^sigma b_j^s (same coeff)
                        next_terms.append((pre + (y, x) + suf, coeff, is_kap, par))
                        # term 2: - gb * kappa
                        if not is_kap:
                            sigma = "p" if "p" in y else "m"
                            px = x.split("_")
                            j, s = px[1], px[2]
                            gb_param = f"gb_a1{sigma}_b{j}{s}"
                            next_terms.append((pre + suf, -coeff * sign_choice, True, gb_param))
                    else:
                        # Should not happen because rx > ry
                        next_terms.append((pre + (y, x) + suf, coeff, is_kap, par))
                    
                    # Add the rest of current_terms unchanged for this step
                    break
            if not pair_found:
                next_terms.append((w, coeff, is_kap, par))
                
        current_terms = next_terms
        if all_sorted:
            break
            
    # Convert sorted words to Poly
    # Filter nilpotent fermions: (a_1_p)^2 = 0, (a_1_m)^2 = 0
    undeff_poly = Poly(n=n)
    def_poly_by_param = defaultdict(lambda: Poly(n=n))
    
    for w, coeff, is_kap, par in current_terms:
        # Check if any a_1_p or a_1_m appears more than once
        if w.count("a_1_p") > 1 or w.count("a_1_m") > 1:
            continue
        p_single = Poly.const(coeff, n=n)
        for osc in w:
            p_single = p_single * Poly.from_osc(osc, n)
            
        if not is_kap:
            undeff_poly = undeff_poly + p_single
        else:
            def_poly_by_param[par] = def_poly_by_param[par] + p_single
            
    return undeff_poly, def_poly_by_param

print("normal_order_word implemented successfully.")
