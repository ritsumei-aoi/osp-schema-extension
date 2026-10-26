import sys, os
from fractions import Fraction
from collections import defaultdict
import sympy as sp

# Let's test the formula for Theta(gb):
# Theta(gb) = 1/2 sum_{j=1}^n (
#   gb_{a1+, bj+} * E_{-, -}
# - gb_{a1+, bj-} * E_{-, +}
# + gb_{a1-, bj+} * E_{+, -}
# - gb_{a1-, bj-} * E_{+, +}
# )

# Oscillators relations:
# {a_1^m, a_1^p} = 1, {a_1^p, a_1^m} = 1
# [b_j^m, b_k^p] = delta_{jk}, [b_j^p, b_k^m] = -delta_{jk}

def test_Theta_bracket(theta_dict):
    # theta_dict: (sigma, j, s) -> Fraction coeff of a_1^sigma b_j^s
    # Computes [(b_k^t)', (a_1^r)'] to order 1 in kappa
    res = {}
    for r in ['p', 'm']:
        for t in ['p', 'm']:
            # We want coeff of kappa in [(b_1^t)', (a_1^r)']
            total = 0
            for (sigma_T, j_T, s_T), coeff in theta_dict.items():
                if j_T != 1: continue
                # Commutator coeff from Theta_1 = a_1^{sigma_T} b_1^{s_T}
                anticomm_a = 1 if {sigma_T, r} == {'p', 'm'} else 0
                comm_b = 0
                if s_T == 'm' and t == 'p': comm_b = 1
                elif s_T == 'p' and t == 'm': comm_b = -1

                term1 = 0
                if t == 'm' and s_T == 'p': term1 = anticomm_a * 1
                elif t == 'p' and s_T == 'm': term1 = anticomm_a * (-1)
                term2 = - comm_b * anticomm_a

                total += coeff * (term1 + term2)
            res[(r, t)] = total
    return res

params = ['gb_a1p_b1p', 'gb_a1p_b1m', 'gb_a1m_b1p', 'gb_a1m_b1m']

for p in params:
    # Set one parameter to 1, others to 0
    theta_dict = {}
    if p == 'gb_a1p_b1p':
        theta_dict[('m', 1, 'm')] = Fraction(1, 2)
    elif p == 'gb_a1p_b1m':
        theta_dict[('m', 1, 'p')] = Fraction(-1, 2)
    elif p == 'gb_a1m_b1p':
        theta_dict[('p', 1, 'm')] = Fraction(1, 2)
    elif p == 'gb_a1m_b1m':
        theta_dict[('p', 1, 'p')] = Fraction(-1, 2)

    res = test_Theta_bracket(theta_dict)
    print(f"\nParameter {p} = 1:")
    for (r, t), val in res.items():
        # [b_1^t, a_1^r] = - gb_{r, 1, t} * kappa
        # So expected is -1 if this is the target (r, t), else 0
        if val != 0:
            print(f"  [(b_1^{t})', (a_1^{r})'] = {val} * kappa (expected: - gb_{r, 1, t})")
