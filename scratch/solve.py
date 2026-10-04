import numpy as np
import sys

# Basis for C(2)
# Even:
# H1 = a+ a- + b+ b-
# H2 = -b+ b- - 1/2
# E+2 = 1/2 b+ b+
# E-2 = 1/2 b- b-
#
# Odd:
# F++ = a+ b+
# F+- = a+ b-
# F-+ = a- b+
# F-- = a- b-

# Oscillators commutation:
# [b-, b+] = 1 => b- b+ = b+ b- + 1
# {a-, a+} = 1 => a- a+ = -a+ a- + 1
# a+ a+ = 0, a- a- = 0

# We can represent any quadratic element in normal order:
# c0 + c1 a+a- + c2 b+b+ + c3 b+b- + c4 b-b-  (Even)
# c5 a+b+ + c6 a+b- + c7 a-b+ + c8 a-b-       (Odd)

# Let's map this to a vector space of dimension 9 (including constants).
# But C(2) doesn't contain constants except as part of H2.
# Wait, H1 = a+a- + b+b-.
# H2 = -b+b- - 1/2
# So constant 1 is -2 H2 - 2 b+b-. This is not in the algebra. 
# Wait, if 1 is not in the algebra, how is H2 in the algebra?
# The enveloping algebra contains constants. 
# The Lie superalgebra is defined as span of H1, H2, E+2, E-2, F++, F+-, F-+, F--.
# That is 4 even and 4 odd generators. Total 8.

basis = ['H1', 'H2', 'E+2', 'E-2', 'F++', 'F+-', 'F-+', 'F--']

def p(name):
    if name.startswith('F'): return 1
    return 0

# Let's write a function to multiply two basis elements in the oscillator algebra
# and return it as a normal-ordered polynomial.
def normal_order(ops):
    # ops is a list of strings: 'a+', 'a-', 'b+', 'b-'
    # We want to bubble a+ to the left of a-, b+ to the left of b-.
    # Also a's to the left of b's.
    pass

