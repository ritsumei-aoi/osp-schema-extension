import sympy as sp

# Let's define the basis for C(2) = osp(2|2)
# Bosonic basis: E0, E1, E2, E3
# E0 = a1+ a1-
# E1 = 1/2 (b1+)^2
# E2 = 1/2 (b1-)^2
# E3 = b1+ b1- + 1/2

# Odd basis: F1, F2, F3, F4
# F1 = a1+ b1+
# F2 = a1+ b1-
# F3 = a1- b1+
# F4 = a1- b1-

# Parities:
# E_i: parity 0
# F_i: parity 1

basis_even = ["E0", "E1", "E2", "E3"]
basis_odd  = ["F1", "F2", "F3", "F4"]
basis_all  = basis_even + basis_odd

dim_even = 4
dim_odd  = 4
dim_total = 8

def parity(name):
    return 0 if name in basis_even else 1

# Let's compute standard Lie superalgebra brackets [X, Y]_0
# Using oscillator commutators:
# [b1-, b1+] = 1 => b1- b1+ - b1+ b1- = 1 => b1- b1+ = 1 + b1+ b1-
# {a1-, a1+} = 1 => a1- a1+ + a1+ a1- = 1 => a1- a1+ = 1 - a1+ a1-
# (a1+)^2 = (a1-)^2 = 0

# We represent quadratic forms in (a1+, a1-, b1+, b1-)
# Let's compute supercommutator [X, Y] for any quadratic forms in oscillators.

# Let's define a helper to simplify product of oscillators to standard basis + scalar.
# Oscillators: a+, a-, b+, b-
# Normal ordering: a+ before a-, b+ before b-

# Basis elements in terms of (a+, a-, b+, b-):
# E0: a+ a-
# E1: 1/2 b+ b+
# E2: 1/2 b- b-
# E3: b+ b- + 1/2

# F1: a+ b+
# F2: a+ b-
# F3: a- b+
# F4: a- b-

print("Testing basis set up")
