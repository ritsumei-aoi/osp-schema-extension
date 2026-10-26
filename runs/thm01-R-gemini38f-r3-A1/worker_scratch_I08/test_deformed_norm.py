import sys, os
from fractions import Fraction
from collections import defaultdict
import sympy as sp

REPO_ROOT = "<home>/notebook/git/thm01-R/thm01-R-gemini38f-r3-A1"
sys.path.insert(0, REPO_ROOT)
from src.C_generators import get_generators, parity_of

def osc_key(osc: str):
    if osc == 'a_1_p': return (0, 0, 0)
    if osc == 'a_1_m': return (0, 1, 0)
    parts = osc.split('_')
    return (1, int(parts[1]), 0 if parts[2] == 'p' else 1)

# In U(A) to first order in kappa:
# An element is represented as a dict:
# (word, param) -> Fraction
# where param is None (order 0) or "gb_a1{sigma}_b{j}{s}" (order 1 in kappa).
# Note: word is a tuple of oscillators, e.g. ('a_1_p', 'b_1_p').
# (word, param) represents:
#   if param is None: coeff * word
#   if param is str:  coeff * param * kappa * word   (or kappa * word)

def normal_order_deformed_word(word: tuple):
    # Returns dict of {(ordered_word, param): Fraction}
    # where param is None for order 0, or symbol name for order 1 (gb * kappa).
    # Since gb * kappa is central and even, it can sit at the front: (gb * kappa) * ordered_word.
    # But wait! The definition has [X, Y]_gamma = [X, Y]_0 + kappa * gamma(X, Y).
    # If we factor kappa to the left, since kappa * a_1^sigma = - a_1^sigma * kappa,
    # what is kappa * ordered_word vs (gb * kappa) * ordered_word?
    # (gb * kappa) * word = - kappa * gb * word = kappa * (- gb * word) if gb is odd!
    # Let's track (ordered_word, param_str) carefully.

    current = {(word, None): Fraction(1, 1)}

    while True:
        next_dict = defaultdict(Fraction)
        all_sorted = True
        for (w, param), coeff in current.items():
            if coeff == 0:
                continue
            found = False
            for i in range(len(w) - 1):
                o1, o2 = w[i], w[i+1]
                if o1 == o2 and parity_of(o1) == 1:
                    found = True
                    all_sorted = False
                    break # a^2 = 0
                elif osc_key(o1) > osc_key(o2):
                    found = True
                    all_sorted = False
                    # Reordering o1 o2:
                    if o1 == 'a_1_m' and o2 == 'a_1_p':
                        # a_1^- a_1^+ = - a_1^+ a_1^- + 1
                        next_dict[(w[:i] + (o2, o1) + w[i+2:], param)] += -coeff
                        next_dict[(w[:i] + w[i+2:], param)] += coeff
                    elif o1.startswith('b_') and o2.startswith('b_'):
                        p1, p2 = o1.split('_'), o2.split('_')
                        j, s1 = int(p1[1]), p1[2]
                        k, s2 = int(p2[1]), p2[2]
                        if s1 == 'm' and s2 == 'p' and j == k:
                            # b^- b^+ = b^+ b^- + 1
                            next_dict[(w[:i] + (o2, o1) + w[i+2:], param)] += coeff
                            next_dict[(w[:i] + w[i+2:], param)] += coeff
                        else:
                            next_dict[(w[:i] + (o2, o1) + w[i+2:], param)] += coeff
                    elif o1.startswith('b_') and o2.startswith('a_'):
                        # b_j^s a_1^sigma = a_1^sigma b_j^s - gb_{sigma, j, s} * kappa
                        # Reordered term: a_1^sigma b_j^s
                        next_dict[(w[:i] + (o2, o1) + w[i+2:], param)] += coeff
                        # Commutator term: - gb_{sigma, j, s} * kappa * w[:i] + w[i+2:]
                        # Only keep if param is None (first order in kappa, kappa^2 = 0)
                        if param is None:
                            parts_b = o1.split('_')
                            j, s = int(parts_b[1]), parts_b[2]
                            sigma = o2.split('_')[2]
                            p_name = f"gb_a1{sigma}_b{j}{s}"
                            rem_word = w[:i] + w[i+2:]
                            next_dict[(rem_word, p_name)] += -coeff
                    else:
                        raise ValueError(f"Unhandled pair: {o1}, {o2}")
                    break
            if not found:
                next_dict[(w, param)] += coeff
        if all_sorted:
            return {k: v for k, v in current.items() if v != 0}
        current = next_dict

print("Testing normal ordering on b_1_p a_1_p:")
print(normal_order_deformed_word(('b_1_p', 'a_1_p')))
print("\nTesting normal ordering on b_1_p b_1_m a_1_p a_1_m:")
res = normal_order_deformed_word(('b_1_p', 'b_1_m', 'a_1_p', 'a_1_m'))
for k, v in res.items():
    print(k, v)
