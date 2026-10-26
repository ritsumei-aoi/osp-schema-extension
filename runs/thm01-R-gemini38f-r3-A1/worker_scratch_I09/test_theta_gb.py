import sys, os
from fractions import Fraction
from collections import defaultdict
import sympy as sp

REPO_ROOT = "<home>/notebook/git/thm01-R/thm01-R-gemini38f-r3-A1"
sys.path.insert(0, REPO_ROOT)
from src.C_generators import get_generators

# Let's determine the exact Theta for any given gb matrix!
# Let Theta = sum_{sigma in {+, -}, j in {1..n}, s in {+, -}} theta_{sigma, j, s} E_{eps1, del_j, sigma, s}
# where E_{eps1, del_j, sigma, s} = a_1^sigma b_j^s.

# Undeformed oscillator commutators:
# {a_1^m, a_1^p} = 1, {a_1^p, a_1^m} = 1, {a_1^+, a_1^+} = 0, {a_1^-, a_1^-} = 0.
# [b_j^m, b_k^p] = delta_{jk}, [b_j^p, b_k^m] = -delta_{jk}.

# Let's check for a general Theta:
# [Theta, a_1^r] = sum_{sigma, j, s} theta_{sigma, j, s} [a_1^sigma b_j^s, a_1^r]
# Since p(a_1^sigma) = 1, p(b_j^s) = 0:
# [a_1^sigma b_j^s, a_1^r] = {a_1^sigma, a_1^r} b_j^s.

# [Theta, b_k^t] = sum_{sigma, j, s} theta_{sigma, j, s} [a_1^sigma b_j^s, b_k^t]
# [a_1^sigma b_j^s, b_k^t] = - a_1^sigma [b_j^s, b_k^t].

# Now, under the transformation v -> v + kappa [Theta, v]:
# [(b_k^t)', (a_1^r)'] = [b_k^t + kappa [Theta, b_k^t], a_1^r + kappa [Theta, a_1^r]]
# = [b_k^t, a_1^r] + [b_k^t, kappa [Theta, a_1^r]] + [kappa [Theta, b_k^t], a_1^r]
# Since [b_k^t, a_1^r] = 0:
# = kappa ( [b_k^t, [Theta, a_1^r]] - [[Theta, b_k^t], a_1^r] )   (using kappa * v = (-1)^p(v) v * kappa)
# Let's compute this bracket carefully!

for sigma_T in ['p', 'm']:
    for s_T in ['p', 'm']:
        # Theta = a_1^{sigma_T} b_1^{s_T}
        print(f"\n--- Theta = a_1^{sigma_T} b_1^{s_T} ---")
        for r in ['p', 'm']:
            # [Theta, a_1^r]
            # {a_1^{sigma_T}, a_1^r}
            anticomm_a = 1 if {sigma_T, r} == {'p', 'm'} else 0
            # result is anticomm_a * b_1^{s_T}
            for t in ['p', 'm']:
                # [Theta, b_1^t] = - a_1^{sigma_T} [b_1^{s_T}, b_1^t]
                comm_b = 0
                if s_T == 'm' and t == 'p': comm_b = 1
                elif s_T == 'p' and t == 'm': comm_b = -1
                # [Theta, b_1^t] = - comm_b * a_1^{sigma_T}

                # Now in U(A):
                # (b_1^t)' (a_1^r)' - (a_1^r)' (b_1^t)'
                # = (b_1^t + kappa [Theta, b_1^t])(a_1^r + kappa [Theta, a_1^r]) - (a_1^r + kappa [Theta, a_1^r])(b_1^t + kappa [Theta, b_1^t])
                # Order 1 in kappa:
                # b_1^t * kappa [Theta, a_1^r] + kappa [Theta, b_1^t] * a_1^r - a_1^r * kappa [Theta, b_1^t] - kappa [Theta, a_1^r] * b_1^t
                # Note: b_1^t * kappa = kappa * b_1^t
                # a_1^r * kappa = - kappa * a_1^r
                # So:
                # = kappa * ( b_1^t [Theta, a_1^r] + [Theta, b_1^t] a_1^r + a_1^r [Theta, b_1^t] - [Theta, a_1^r] b_1^t )
                # = kappa * ( [b_1^t, [Theta, a_1^r]] + {a_1^r, [Theta, b_1^t]} )
                # Substitute [Theta, a_1^r] = anticomm_a * b_1^{s_T}:
                # [b_1^t, anticomm_a * b_1^{s_T}] = anticomm_a * [b_1^t, b_1^{s_T}]
                # Substitute [Theta, b_1^t] = - comm_b * a_1^{sigma_T}:
                # {a_1^r, - comm_b * a_1^{sigma_T}} = - comm_b * {a_1^r, a_1^{sigma_T}}

                term1 = 0
                if t == 'm' and s_T == 'p': term1 = anticomm_a * 1
                elif t == 'p' and s_T == 'm': term1 = anticomm_a * (-1)

                term2 = - comm_b * anticomm_a

                total = term1 + term2
                # We want [(b_1^t)', (a_1^r)'] = - gb_{r, 1, t} * kappa
                # So total * kappa = - gb_{r, 1, t} * kappa
                if total != 0:
                    print(f"  Affects [(b_1^{t})', (a_1^{r})']: coeff of kappa = {total}")
