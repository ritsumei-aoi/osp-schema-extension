import sympy as sp
from itertools import product

# Let's test the commutator of any two quadratic monomials in the oscillator algebra.
# Let oscillators be ordered:
# For n=1:
# 0: a+ (p=1)
# 1: a- (p=1)
# 2: b+ (p=0)
# 3: b- (p=0)

# Parities:
parity = {'a+': 1, 'a-': 1, 'b+': 0, 'b-': 0}

# Undeformed commutators: [u, v] = C0(u, v)
# [b-, b+] = 1, [b+, b-] = -1
# [a-, a+] = 1, [a+, a-] = 1
# all other C0 = 0
def C0(u, v):
    if u == 'b-' and v == 'b+': return 1
    if u == 'b+' and v == 'b-': return -1
    if (u == 'a-' and v == 'a+') or (u == 'a+' and v == 'a-'): return 1
    return 0

# Deformed commutators: [u, v] = C0(u, v) + kappa * C1(u, v)
# [b_j^s, a_1^sigma] = - gb_{sigma, j, s} * kappa
# [a_1^sigma, b_j^s] = gb_{sigma, j, s} * kappa

# Let's test:
# For X = u v and Y = w z:
# [X, Y] = X Y - (-1)^{p(X) p(Y)} Y X
# Let's compute this algebraically in the free algebra modulo relations!

print("Setting up algebraic verification...")
