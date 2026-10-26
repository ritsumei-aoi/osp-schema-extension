import sys
sys.path.append('.')
from src.C_generators import build_c_generators, Poly
from fractions import Fraction
import sympy as sp

# Test for n=1: C(2) = osp(2|2)
# Dimension of V: 2 (fermionic) + 2n (bosonic) = 4.
# Basis of V:
# v_0 = a_1_p, v_1 = a_1_m, v_2 = b_1_p, v_3 = b_1_m
v_names = ["a_1_p", "a_1_m", "b_1_p", "b_1_m"]
data = build_c_generators(1)
full_basis = data["odd_basis"] + data["even_basis"]
generators = data["generators"]
parities = data["parities"]

# Compute matrix of ad(X) on V for each generator X
# [X, v] in undeformed algebra
print(f"Basis size of g: {len(full_basis)}")
ad_matrices = {}
for name in full_basis:
    poly_X = generators[name]
    p_X = parities[name]
    # Matrix of ad(X) on V: 4x4
    mat = sp.zeros(4, 4)
    for col, v_name in enumerate(v_names):
        poly_v = Poly.from_osc(v_name, 1)
        p_v = 1 if v_name.startswith("a_") else 0
        # [X, v} = X v - (-1)^{p_X p_v} v X
        sign = -1 if (p_X * p_v) % 2 == 1 else 1
        comm = poly_X * poly_v - poly_v * poly_X * sign
        for row, target_v in enumerate(v_names):
            # Check coefficient of target_v in comm
            # comm should be a linear combination of v_names
            # A monomial for target_v has 1 in target_v and 0 elsewhere
            for m, coeff in comm.terms.items():
                if m.to_words() == [target_v]:
                    mat[row, col] += sp.Rational(coeff.numerator, coeff.denominator)
    ad_matrices[name] = mat

# Check linear independence of ad_matrices
# Flatten each 4x4 matrix into a 16-element vector
vecs = [sp.Matrix(ad_matrices[name]).reshape(16, 1) for name in full_basis]
M = sp.Matrix.hstack(*vecs)
rank = M.rank()
print(f"Rank of ad matrices on V: {rank} out of {len(full_basis)}")
