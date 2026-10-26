from fractions import Fraction
import math

def reduce_single_boson(m1, p2):
    res = {}
    for k in range(min(m1, p2) + 1):
        coeff = math.factorial(k) * math.comb(m1, k) * math.comb(p2, k)
        res[(p2 - k, m1 - k)] = Fraction(coeff)
    return res

# (b^-)^1 * (b^+)^2
print("b^- * (b^+)^2:", reduce_single_boson(1, 2))
# For k=0: coeff = 1, (2, 1) -> (b^+)^2 b^-
# For k=1: coeff = 1! * 1 * 2 = 2, (1, 0) -> 2 b^+
