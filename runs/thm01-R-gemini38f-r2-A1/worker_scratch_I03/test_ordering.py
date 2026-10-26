"""
Scratch script to compute and verify C(n+1) structure constants and algebra closure.
"""
from fractions import Fraction
from collections import defaultdict
import json

def multiply_monomials(w1, c1, w2, c2):
    # w1, w2: list of oscillator names, e.g. ["a_1_p", "b_1_m"]
    # c1, c2: Fraction
    # Returns dictionary of {tuple(words): Fraction}
    pass

# Let's write the normal ordering / reduction rule for oscillator words
# PBW order of oscillators:
# a_1_p, a_1_m, b_1_p, b_1_m, ..., b_n_p, b_n_m
# Relations:
# a_1_m a_1_p = 1 - a_1_p a_1_m
# a_1_p a_1_p = 0
# a_1_m a_1_m = 0
# b_k_m b_k_p = 1 + b_k_p b_k_m
# All other pairs commute (or fermions anticommute, but there is only 1 fermion pair)
# For cross pairs [b, a] = 0.

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
    # word: list of str
    # returns list of (word, coeff)
    # Recursively or iteratively reduce adjacent out-of-order pairs
    current = {tuple(word): coeff}
    
    changed = True
    while changed:
        changed = False
        new_current = defaultdict(Fraction)
        for w, c in current.items():
            if c == 0:
                continue
            # find first inversion
            inversion_idx = -1
            for i in range(len(w) - 1):
                if order_key(w[i]) > order_key(w[i+1]):
                    inversion_idx = i
                    break
                elif w[i] == w[i+1]:
                    if w[i] in ("a_1_p", "a_1_m"):
                        # nilpotent!
                        inversion_idx = -2
                        break
            
            if inversion_idx == -2:
                # vanishes
                changed = True
                continue
            elif inversion_idx == -1:
                # fully ordered, check nilpotency just in case
                new_current[w] += c
            else:
                changed = True
                i = inversion_idx
                x, y = w[i], w[i+1]
                prefix = w[:i]
                suffix = w[i+2:]
                
                # Check relation between x and y
                if x == "a_1_m" and y == "a_1_p":
                    # a_1_m a_1_p = 1 - a_1_p a_1_m
                    # term 1: - a_1_p a_1_m
                    new_current[prefix + ("a_1_p", "a_1_m") + suffix] += -c
                    # term 2: 1
                    new_current[prefix + suffix] += c
                elif x.startswith("b_") and y.startswith("b_"):
                    # Check if conjugate pair
                    px = x.split("_")
                    py = y.split("_")
                    if px[1] == py[1] and px[2] == "m" and py[2] == "p":
                        # b_k_m b_k_p = 1 + b_k_p b_k_m
                        new_current[prefix + (f"b_{px[1]}_p", f"b_{px[1]}_m") + suffix] += c
                        new_current[prefix + suffix] += c
                    else:
                        # different k, or same sign -> they commute!
                        new_current[prefix + (y, x) + suffix] += c
                else:
                    # mixed boson and fermion: [b, a] = 0 -> commute
                    new_current[prefix + (y, x) + suffix] += c
        current = new_current
    return {w: c for w, c in current.items() if c != 0}

print("Testing normal ordering:")
print("a_1_m * a_1_p:", normal_order_word(["a_1_m", "a_1_p"], Fraction(1)))
print("b_1_m * b_1_p:", normal_order_word(["b_1_m", "b_1_p"], Fraction(1)))
print("b_1_m * a_1_p:", normal_order_word(["b_1_m", "a_1_p"], Fraction(1)))
