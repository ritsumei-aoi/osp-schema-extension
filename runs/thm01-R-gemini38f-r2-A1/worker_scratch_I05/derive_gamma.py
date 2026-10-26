"""
Full derivation of gamma(X, Y) for C(n+1) inhomogeneous deformation.
"""
from src.C_generators import build_c_basis, order_key, normal_order_word
from collections import defaultdict
from fractions import Fraction
import sympy as sp

# Let's define deformation parameters:
# For each sigma in {p, m} and (j, s) in {1..n} x {p, m}:
# gb_{sigma, j, s}
# In notation: gb_a1p_b{j}p, gb_a1p_b{j}m, gb_a1m_b{j}p, gb_a1m_b{j}m.

def get_gb_label(sigma, j, s):
    sig_str = "a1p" if sigma == "p" else "a1m"
    s_str = f"b{j}p" if s == "p" else f"b{j}m"
    return f"gb_{sig_str}_{s_str}"

# Relations:
# In standard reduction, when we have adjacent oscillators:
# If x = b_j_s and y = a_1_sigma:
# b_j_s a_1_sigma = a_1_sigma b_j_s - gb_{sigma, j, s} * kappa
# Here x has key > y (because a_1 < b_j in our PBW order).
# So in normal ordering from left to right:
# word containing (... b_j_s, a_1_sigma ...) swaps to (... a_1_sigma, b_j_s ...)
# with an extra term: - gb_{sigma, j, s} * kappa * (... remaining word ...)
# Since kappa is central and kappa^2 = 0, this extra term has no further kappa deformation!
# The remaining word in the extra term can be normal-ordered using standard U(A)_0 rules!

def normal_order_deformed(word, coeff):
    # Returns (poly_0, poly_kappa)
    # poly_0: dict of {tuple(word): Fraction}
    # poly_kappa: dict of {(tuple(word), gb_param): Fraction}
    
    # We can perform the normal ordering step-by-step
    # State: list of (word, coeff, has_kappa, gb_param_or_None)
    # Initially: [(word, coeff, False, None)]
    
    current_0 = {tuple(word): coeff}
    current_kappa = defaultdict(Fraction) # (word, gb_param) -> coeff
    
    changed = True
    while changed:
        changed = False
        new_0 = defaultdict(Fraction)
        for w, c in current_0.items():
            if c == 0: continue
            inv_idx = -1
            for i in range(len(w) - 1):
                if order_key(w[i]) > order_key(w[i+1]):
                    inv_idx = i
                    break
                elif w[i] == w[i+1] and w[i] in ("a_1_p", "a_1_m"):
                    inv_idx = -2
                    break
            if inv_idx == -2:
                changed = True
                continue
            elif inv_idx == -1:
                new_0[w] += c
            else:
                changed = True
                i = inv_idx
                x, y = w[i], w[i+1]
                prefix = w[:i]
                suffix = w[i+2:]
                if x == "a_1_m" and y == "a_1_p":
                    new_0[prefix + ("a_1_p", "a_1_m") + suffix] += -c
                    new_0[prefix + suffix] += c
                elif x.startswith("b_") and y.startswith("b_"):
                    px, py = x.split("_"), y.split("_")
                    if px[1] == py[1] and px[2] == "m" and py[2] == "p":
                        new_0[prefix + (f"b_{px[1]}_p", f"b_{px[1]}_m") + suffix] += c
                        new_0[prefix + suffix] += c
                    else:
                        new_0[prefix + (y, x) + suffix] += c
                elif x.startswith("b_") and y.startswith("a_"):
                    # Here is the deformation!
                    # [b_j^s, a_1^sigma] = - gb_{sigma, j, s} * kappa
                    # b a = a b - gb * kappa
                    # term 1 (unperturbed): a b
                    new_0[prefix + (y, x) + suffix] += c
                    # term 2 (order kappa): - gb * c * (prefix + suffix)
                    # Notice: [b_j^s, a_1^sigma] = - gb_{sigma, j, s} kappa
                    px = x.split("_") # b, j, s
                    py = y.split("_") # a, 1, sigma
                    gb_name = get_gb_label(py[2], px[1], px[2])
                    current_kappa[(prefix + suffix, gb_name)] += -c
                else:
                    new_0[prefix + (y, x) + suffix] += c
        current_0 = new_0

    # Now reduce all words in current_kappa using normal_order_word in U(A)_0
    final_kappa = defaultdict(Fraction)
    for (w, gb_name), c in current_kappa.items():
        no = normal_order_word(list(w), c)
        for nw, nc in no.items():
            final_kappa[(nw, gb_name)] += nc

    return {w: c for w, c in current_0.items() if c != 0}, {k: c for k, c in final_kappa.items() if c != 0}

print("Normal order deformed function defined.")
