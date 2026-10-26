import sys, os
from fractions import Fraction
from collections import defaultdict
import sympy as sp

# Let's compute [[Theta, b_k^t], a_1^r] + [b_k^t, [Theta, a_1^r]]
# where Theta = sum_{sigma, j, s} theta_{sigma, j, s} a_1^sigma b_j^s
# Oscillators relations:
# {a_1^sigma, a_1^{sigma'}} = 1 if {sigma, sigma'} = {+, -} else 0
# [b_j^s, b_k^{s'}] = s * delta_{jk} delta_{s, -s'}
# Specifically: [b_j^-, b_j^+] = 1, [b_j^+, b_j^-] = -1

# For a given (sigma, j, s):
# Let Theta_1 = a_1^sigma b_j^s. (p = 1)
# [Theta_1, a_1^r] = {a_1^sigma, a_1^r} b_j^s.
# [Theta_1, b_k^t] = - a_1^sigma [b_j^s, b_k^t].

# Now:
# Term 1: [Theta_1, a_1^r] is a scalar * b_j^s.
# Then [b_k^t, [Theta_1, a_1^r]] = {a_1^sigma, a_1^r} [b_k^t, b_j^s].
# This is a SCALAR!

# Term 2: [Theta_1, b_k^t] is - [b_j^s, b_k^t] a_1^sigma.
# Then [[Theta_1, b_k^t], a_1^r] = - [b_j^s, b_k^t] {a_1^sigma, a_1^r}.
# This is also a SCALAR!

# Sum:
# [[Theta_1, b_k^t], a_1^r] + [b_k^t, [Theta_1, a_1^r]]
# = - [b_j^s, b_k^t] {a_1^sigma, a_1^r} + [b_k^t, b_j^s] {a_1^sigma, a_1^r}
# Since [b_k^t, b_j^s] = - [b_j^s, b_k^t]:
# = - 2 [b_j^s, b_k^t] {a_1^sigma, a_1^r} !

print("The commutator is EXACTLY proportional to a SCALAR times kappa!")
print("Namely: -2 * [b_j^s, b_k^t] * {a_1^sigma, a_1^r} * kappa!")
