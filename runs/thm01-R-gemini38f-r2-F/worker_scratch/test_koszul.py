import json
import sympy as sp
from collections import defaultdict
from fractions import Fraction

# Let's check the Koszul sign in normal_order_word_ua:
# When b_j^s and a_1^\sigma are exchanged:
# pre + (b_j^s, a_1^\sigma) + suf
# The kappa is produced at the position between pre and suf:
# pre * kappa * suf
# To move kappa to the front:
# kappa * (-1)^{sum_{osc in pre} p(osc)} * pre * suf
# What is sum_{osc in pre} p(osc)?
# It is the number of fermionic oscillators in pre!
# If pre contains an a_1^+ or a_1^-, then (-1)^1 = -1!

print("Testing Koszul sign correction...")
