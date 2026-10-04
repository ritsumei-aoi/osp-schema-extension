"""
Symbolic Algebra Engine for C(n+1) = osp(2|2n) and its Inhomogeneous Deformations
"""

import sympy as sp
from itertools import product

def create_symbols(n):
    """
    Creates symbolic gb parameters gb_{sigma, k, s} for sigma in {+, -}, k in 1..n, s in {+, -}.
    Total 4n parameters.
    """
    gb = {}
    for sigma in ['+', '-']:
        for k in range(1, n + 1):
            for s in ['+', '-']:
                # Label like gb_{sigma, k, s}
                sig_str = 'p' if sigma == '+' else 'm'
                s_str = 'p' if s == '+' else 'm'
                sym_name = f"gb_{sig_str}_{k}_{s_str}"
                gb[(sigma, k, s)] = sp.Symbol(sym_name)
    return gb

class Generator:
    """
    Represents a generator of C(n+1) in terms of oscillator bilinear basis:
    Even generators:
      - Z0 = a+ a- - 1/2
      - h_k = b_k+ b_k- + 1/2 (k=1..n)
      - E_{(k,s1),(l,s2)} for (k,s1) != (l,s2):
          if (k,s1) == (l,s2): 1/2 (b_k^s1)^2
          else: b_k^s1 b_l^s2
    Odd generators:
      - F_{(sigma, k, s)} = a^sigma b_k^s
    """
    pass

# Let's write normal ordering and commutator functions for arbitrary quadratic oscillator expressions.

def normal_order_monomial(factors):
    """
    factors is a list of tuples representing operators:
    ('a', '+') or ('a', '-')
    ('b', k, '+') or ('b', k, '-')
    ('kappa',)
    ('scalar', val)

    Returns a list of (coeff, list_of_ordered_factors) to first order in kappa.
    Ordering rule:
    1. 'kappa' scalar
    2. 'a' operators: '+' before '-'
    3. 'b' operators: sorted by k, then '+' before '-'
    """
    pass
