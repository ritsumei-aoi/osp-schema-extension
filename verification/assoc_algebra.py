"""
Exact computation of [X, Y] in U(A) to order kappa.
"""
import sympy as sp
from collections import defaultdict

# Let's define the oscillators:
# For n=1:
# Fermions: a+, a-
# Bosons: b+, b-

# A monomial in U(A) can be written as a product of single oscillators and kappa.
# We work to first order in kappa: kappa**2 = 0.
# kappa is central, p(kappa) = 1.
# gb parameters: gb(sigma, j, s)

# Let's implement an explicit associative multiplication / reduction to normal order!
