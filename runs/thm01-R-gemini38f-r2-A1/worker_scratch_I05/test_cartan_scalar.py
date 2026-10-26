"""
Test derivation of [X, Y]_gamma in U(A) where:
[b_j^s, a_1^sigma] = - gb_{sigma, j, s} * kappa, or + gb_{sigma, j, s} * kappa.
Let's see what happens if:
For any monomial u v and x y in U(A):
Let's compute the commutator directly in the associative algebra U(A):
[u v, x y] = (u v) (x y) - (-1)^{p(u v) p(x y)} (x y) (u v).
"""
from collections import defaultdict
from fractions import Fraction
import sympy as sp
from src.C_generators import build_c_basis, order_key, normal_order_word

# In associative algebra:
# [u, v] = u v - (-1)^{pu pv} v u.
# If u, v in V:
# [b_j^-, b_j^+] = 1 (K=1)
# {a_1^-, a_1^+} = 1
# And the cross commutator:
# [b_j^s, a_1^sigma] = c * gb_{sigma, j, s} * kappa
# What is [a_1^sigma, b_j^s]?
# In Lie superalgebra: [a, b} = - (-1)^{p(a) p(b)} [b, a} = - [b, a} (since p(a)=1, p(b)=0).
# So if [b, a] = - gb * kappa, then [a, b] = + gb * kappa!
# In associative algebra:
# a b - b a = + gb * kappa => a b = b a + gb * kappa.
# b a - a b = - gb * kappa => b a = a b - gb * kappa.
# These two equations are completely identical: b a = a b - gb * kappa!

# Now let's calculate the commutator [u v, x y} between two quadratic elements!
# Using associative algebra identity:
# For any associative superalgebra:
# [u v, w} = u [v, w} + (-1)^{p(v) p(w)} [u, w} v.
# And [w, x y} = [w, x} y + (-1)^{p(w) p(x)} x [w, y}.
# Therefore, for quadratic monomials:
# [u v, x y} = u [v, x y} + (-1)^{pv p(xy)} [u, x y} v
# = u ( [v, x} y + (-1)^{pv px} x [v, y} ) + (-1)^{pv p(xy)} ( [u, x} y + (-1)^{pu px} x [u, y} ) v
# = [v, x} u y + (-1)^{pv px} [v, y} u x + (-1)^{pv p(xy)} [u, x} y v + (-1)^{pv p(xy) + pu px} [u, y} x v.

# Wait! Earlier we noticed that [v, y} was central, but did we check if:
# u x and y v are in the Lie superalgebra?!
# Let's check which (X, Y) gave non-basis elements earlier!
# Earlier, non-basis elements occurred when:
# [H_1, E_eps_del1_pp] gave {('a_1_p', 'a_1_m'): 1, ('b_1_p', 'b_1_m'): -1}
# Wait! ('a_1_p', 'a_1_m') - ('b_1_p', 'b_1_m')
# Look at that: a_1_p a_1_m - b_1_p b_1_m !
# Is a_1_p a_1_m - b_1_p b_1_m in C(n+1)?
# In C(n+1):
# H_1 = a_1_p a_1_m + b_1_p b_1_m
# H_2 = - b_1_p b_1_m - 1/2.
# So H_1 + 2 H_2 + 1 = a_1_p a_1_m + b_1_p b_1_m - 2 b_1_p b_1_m = a_1_p a_1_m - b_1_p b_1_m !
# YES! a_1_p a_1_m - b_1_p b_1_m = H_1 + 2 H_2 (plus scalar 1)!
# It IS in the span of the Cartan generators modulo scalar 1!
# Wait! In Lie superalgebra, is the scalar 1 in the algebra, or is K = 1 central?!
# Remember B0n_schema_v5.md:
# "Note on K: The even central element K is identified with the scalar 1 in all current applications.
# It does not appear as an independent basis element and is excluded from PBW ordering and basis lists."
