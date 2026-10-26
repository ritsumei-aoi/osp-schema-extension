import sys
from fractions import Fraction
from collections import defaultdict
import itertools

# Let's define monomials with kappa:
# (kappa)^k_deg * (a_1^+)^fp (a_1^-)^fm * prod (b^+)^u (b^-)^v
# kappa has parity 1, kappa^2 = 0, kappa is central.
# Exchange relation:
# b_j^s * a_1^\sigma = a_1^\sigma * b_j^s - gb_{\sigma, j, s} * kappa
# a_1^\sigma * b_j^s = b_j^s * a_1^\sigma + gb_{\sigma, j, s} * kappa

# Let's test a simple generator bracket:
# X = E_{eps1, del1, pp} = a_1^+ b_1^+
# Y = H_2 = - b_1^+ b_1^- - 1/2
# Let's compute [X, Y] directly!
# Since X is odd (p=1) and H_2 is even (p=0):
# [X, Y] = X Y - Y X = (a_1^+ b_1^+) (-b_1^+ b_1^- - 1/2) - (-b_1^+ b_1^- - 1/2) (a_1^+ b_1^+)
# Let's evaluate term by term:
# Term 1: X * (-1/2) - (-1/2) * X = -1/2 X + 1/2 X = 0! (Constants cancel!)
# So:
# [X, Y] = (a_1^+ b_1^+) (-b_1^+ b_1^-) - (-b_1^+ b_1^-) (a_1^+ b_1^+)
# = - a_1^+ (b_1^+)^2 b_1^- + b_1^+ b_1^- a_1^+ b_1^+
# Now let's move a_1^+ past b_1^+ b_1^- using:
# b_1^- a_1^+ = a_1^+ b_1^- - gb_{a1_p, b1_m} kappa
# b_1^+ a_1^+ = a_1^+ b_1^+ - gb_{a1_p, b1_p} kappa
# Let's see:
# b_1^+ b_1^- a_1^+ b_1^+ = b_1^+ (a_1^+ b_1^- - gb_{a1_p, b1_m} kappa) b_1^+
# = (b_1^+ a_1^+) b_1^- b_1^+ - b_1^+ gb_{a1_p, b1_m} kappa b_1^+
# = (a_1^+ b_1^+ - gb_{a1_p, b1_p} kappa) b_1^- b_1^+ - gb_{a1_p, b1_m} kappa (b_1^+)^2
# = a_1^+ b_1^+ b_1^- b_1^+ - gb_{a1_p, b1_p} kappa b_1^- b_1^+ - gb_{a1_p, b1_m} kappa (b_1^+)^2
# Now use b_1^- b_1^+ = b_1^+ b_1^- + 1:
# = a_1^+ b_1^+ (b_1^+ b_1^- + 1) - gb_{a1_p, b1_p} kappa (b_1^+ b_1^- + 1) - gb_{a1_p, b1_m} kappa (b_1^+)^2
# = a_1^+ (b_1^+)^2 b_1^- + a_1^+ b_1^+ - gb_{a1_p, b1_p} kappa (b_1^+ b_1^- + 1) - gb_{a1_p, b1_m} kappa (b_1^+)^2
# Now subtract Term 1: - a_1^+ (b_1^+)^2 b_1^- + ...
# The a_1^+ (b_1^+)^2 b_1^- cancels!
# Result of [X, Y]:
# = a_1^+ b_1^+  -  kappa * [ gb_{a1_p, b1_p} (b_1^+ b_1^- + 1) + gb_{a1_p, b1_m} (b_1^+)^2 ]
# Look at that:
# Undeformed part: a_1^+ b_1^+ = E_{eps1, del1, pp} (standard root bracket!)
# Deformed part (coefficient of kappa):
# - gb_{a1_p, b1_p} (b_1^+ b_1^- + 1) - gb_{a1_p, b1_m} (b_1^+)^2

print("Direct computation complete:")
print("Undeformed:", "a_1^+ b_1^+")
print("Deformed:", "- gb_{a1p, b1p} * (b_1^+ b_1^- + 1) - gb_{a1p, b1m} * (b_1^+)^2")
