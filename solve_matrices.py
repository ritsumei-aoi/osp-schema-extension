import sympy as sp

# Let's define the basis and the action of the bracket.
# We will represent generators as abstract vectors.
# To do this exactly, we can just use sympy symbols for the matrix elements of f.

# basis:
# Even (4):
# B1 = (b+)^2
# B2 = (b-)^2
# B3 = b+ b- + 1/2
# B4 = a+ a- - 1/2
# Odd (4):
# F1 = a+ b+
# F2 = a+ b-
# F3 = a- b+
# F4 = a- b-

# Let's use the explicit brackets for C(2):
# We need [X, Y] for all pairs.
# Instead of recalculating, I will hardcode the known brackets of C(2).
# Or better, we can write a tiny correct commutator function.
def comm_b(b1, b2):
    # [b^s, b^t] = \delta_{s,-} \delta_{t,+} - \delta_{s,+} \delta_{t,-}
    # But wait, [b-, b+] = 1, [b+, b-] = -1
    if b1 == '-' and b2 == '+': return 1
    if b1 == '+' and b2 == '-': return -1
    return 0

# Commutators of B = b^t b^u
# [b^t b^u, b^v b^w] = b^t [b^u, b^v] b^w + b^t b^v [b^u, b^w] + [b^t, b^v] b^u b^w + b^v [b^t, b^w] b^u
# This is getting tedious. Let's use sympy's quantum physics module, or just matrices!
# C(n+1) has a defining matrix representation!
# osp(2|2) is 4x4 supermatrices.
# The supercommutator of supermatrices is EXACTLY the Lie superbracket!
# M1, M2 -> M1 M2 - (-1)^{p(M1)p(M2)} M2 M1.
# Let's build the 4x4 supermatrices for osp(2|2).

# osp(2|2) matrices:
# Parity: first 2 rows/cols are EVEN (bosonic? No, standard is m|n, so 2 even, 2 odd).
# Wait, osp(2|2) means 2 even, 2 odd variables?
# Orthosymplectic group OSp(2|2n) leaves invariant a super-symmetric form.
# The form is (x, y) = x^T J y.
# For osp(2|2), J = diag(J_ortho, J_symp).
# J_ortho = [[0, 1], [1, 0]]
# J_symp = [[0, 1], [-1, 0]]
# Supertranspose: M^{sT}.
# Let's just define the matrices.

def supercomm(A, B, pA, pB):
    return A * B - (-1)**(pA * pB) * B * A

# Let's just use the explicit algebraic relations.
# I will write a simple string replacer that evaluates brackets.
# It's faster.
def term_comm(t1, t2, sign):
    # t1, t2 are lists of strings like ['a+', 'b+']
    # sign is -1 for commutator, 1 for anticommutator
    # return list of (coeff, term)
    pass
