import sympy as sp
from collections import defaultdict
import sys

def p_F(): return 1
def p_S(): return 0
def p_C(): return 0

# We want to represent the elements of the algebra g and the cocycles.
# Because the relations are simple enough, we can compute gamma analytically
# and then construct the linear system for triviality.

# Let's derive gamma analytically for all basis elements.
#
# gamma( F^{sigma, s}_k, F^{sigma', s'}_l ) = gb_{sigma', k, s} F^{sigma, s'}_l + gb_{sigma, l, s'} F^{sigma', s}_k
#
# gamma( C, F^{sigma, s}_k ) = - sigma * gb_{sigma, k, s} C ?
# Wait, let's re-evaluate [C, F]:
# C = a^+ a^- - 1/2
# C F^{sigma, s}_k = (a^+ a^- - 1/2) a^sigma b_k^s
# F^{sigma, s}_k C = a^sigma b_k^s (a^+ a^- - 1/2) = a^sigma (a^+ b_k^s - gb_{+,k,s} kappa) a^- - 1/2 a^sigma b_k^s
#   = a^sigma a^+ (a^- b_k^s - gb_{-,k,s} kappa) - gb_{+,k,s} a^sigma kappa a^- - 1/2 a^sigma b_k^s
#   = a^sigma a^+ a^- b_k^s - gb_{-,k,s} a^sigma a^+ kappa - gb_{+,k,s} a^sigma kappa a^- - 1/2 a^sigma b_k^s
# So F C = a^sigma a^+ a^- b_k^s - kappa ( gb_{-,k,s} a^sigma a^+ - gb_{+,k,s} a^sigma a^- ) - 1/2 a^sigma b_k^s
#
# Thus C F - F C = (a^+ a^- a^sigma - a^sigma a^+ a^-) b_k^s + kappa ( gb_{-,k,s} a^sigma a^+ - gb_{+,k,s} a^sigma a^- )
# So gamma(C, F^{sigma, s}_k) = gb_{-,k,s} a^sigma a^+ - gb_{+,k,s} a^sigma a^-
# Let's evaluate this for sigma = +:
# gamma(C, F^{+, s}_k) = gb_{-,k,s} a^+ a^+ - gb_{+,k,s} a^+ a^- = - gb_{+,k,s} a^+ a^- = - gb_{+,k,s} (C + 1/2)
# For sigma = -:
# gamma(C, F^{-, s}_k) = gb_{-,k,s} a^- a^+ - gb_{+,k,s} a^- a^- = gb_{-,k,s} (1 - a^+ a^-) = gb_{-,k,s} (1/2 - C) = - gb_{-,k,s} (C - 1/2)
#
# Since gamma must take values in g, and g does NOT contain the central element (the identity), the coefficient of the identity must be 0?
# Wait! "gamma(X,Y) = (delta f)(X,Y) ... up to scalar".
# This means we only care about the projection of gamma onto g. The scalar part is ignored!
# The projection to g is:
# P(a^+ a^-) = C
# P(1) = 0
# So P( gamma(C, F^{+, s}_k) ) = - gb_{+,k,s} C
# P( gamma(C, F^{-, s}_k) ) = - gb_{-,k,s} C
# So gamma(C, F^{sigma, s}_k) = - gb_{sigma, k, s} C.
#
# Let's verify gamma( S^{s1,s2}_{k,l}, F^{sigma, s}_m ).
# S^{s1,s2}_{k,l} = b_k^{s1} b_l^{s2} + (1/2 if s1!=s2 and k==l else 0)
# Let's just look at the quadratic part B = b_k^{s1} b_l^{s2}.
# [B, F] = b_k^{s1} b_l^{s2} a^sigma b_m^s - a^sigma b_m^s b_k^{s1} b_l^{s2}
# = b_k^{s1} (a^sigma b_l^{s2} - gb_{sigma, l, s2} kappa) b_m^s - a^sigma b_m^s b_k^{s1} b_l^{s2}
# = (a^sigma b_k^{s1} - gb_{sigma, k, s1} kappa) b_l^{s2} b_m^s - gb_{sigma, l, s2} b_k^{s1} kappa b_m^s - a^sigma b_m^s b_k^{s1} b_l^{s2}
# = a^sigma b_k^{s1} b_l^{s2} b_m^s - kappa ( gb_{sigma, k, s1} b_l^{s2} b_m^s + gb_{sigma, l, s2} b_k^{s1} b_m^s ) - a^sigma b_m^s b_k^{s1} b_l^{s2}
# = a^sigma [ b_k^{s1} b_l^{s2}, b_m^s ] - kappa ( gb_{sigma, k, s1} b_l^{s2} b_m^s + gb_{sigma, l, s2} b_k^{s1} b_m^s )
# So gamma(B, F) = - ( gb_{sigma, k, s1} b_l^{s2} b_m^s + gb_{sigma, l, s2} b_k^{s1} b_m^s )
# Wait!
# The variables B are symmetric in (k, s1) and (l, s2), meaning B = b_k^{s1} b_l^{s2} = S^{s1,s2}_{k,l} + const.
# Projection of B * b_m^s onto g:
# Wait, b_l^{s2} b_m^s is exactly S^{s2, s}_{l, m} + const.
# So gamma( S^{s1,s2}_{k,l}, F^{sigma, s}_m ) = - gb_{sigma, k, s1} S^{s2, s}_{l, m} - gb_{sigma, l, s2} S^{s1, s}_{k, m}
#
# What about gamma(C, C)?
# Both are made of a's, which have no gb deformation with themselves. So gamma(C, C) = 0.
# What about gamma(S, S)?
# Both are made of b's, which have no gb deformation with themselves. So gamma(S, S) = 0.
#
# Let's summarize gamma:
# gamma(C, C) = 0
# gamma(S, S) = 0
# gamma(C, S) = 0
# gamma(F_k^{sigma, s}, F_l^{sigma', s'}) = gb_{sigma', k, s} F_l^{sigma, s'} + gb_{sigma, l, s'} F_k^{sigma', s}
# gamma(C, F_k^{sigma, s}) = - gb_{sigma, k, s} C
# gamma(S^{s1,s2}_{k,l}, F_m^{sigma, s}) = - gb_{sigma, k, s1} S^{s2, s}_{l, m} - gb_{sigma, l, s2} S^{s1, s}_{k, m}

# Now we need delta f.
# f is an odd linear map f: g -> g.
# g has even basis: C, S^{s1,s2}_{k,l}
# g has odd basis: F^{sigma, s}_k
#
# Since f is odd, it maps even elements to odd elements, and odd elements to even elements.
# Let f(C) = sum_{k, sigma, s} f_C^{sigma, s, k} F_k^{sigma, s}
# f(S^{s1,s2}_{k,l}) = sum_{m, sigma, s} f_S^{s1,s2,k,l; sigma,s,m} F_m^{sigma, s}
# f(F_k^{sigma, s}) = f_{F,C}^{sigma, s, k} C + sum_{l,m,s1,s2} f_{F,S}^{sigma, s, k; s1,s2,l,m} S^{s1,s2}_{l,m}
#
# delta f (X, Y) = (-1)^{p(X)} [X, f(Y)] - (-1)^{(p(X)+1)p(Y)} [Y, f(X)] - f([X, Y])
#
# We want to solve gamma(X, Y) = delta f (X, Y) for all X, Y.
#
# Let's write a program to build this linear system for the unknown f coefficients,
# in terms of the gb parameters. We can see if there's a solution for f for ANY gb.
# If the only solution requires gb = 0, then the deformation is non-trivial for any non-zero gb.
#
# First, we need the exact un-deformed Lie brackets [X, Y].
# [C, C] = 0
# [C, S] = 0
# [S, S] = ...
# [C, F_k^{sigma, s}] = sigma * F_k^{sigma, s}   (where sigma is +1 or -1)
# Let's verify [C, F]:
# C = a^+ a^- - 1/2.
# [C, a^+] = a^+ a^- a^+ - a^+ a^+ a^- = a^+ (1) - 0 = a^+. So sigma=+1 -> +F.
# [C, a^-] = a^+ a^- a^- - a^- a^+ a^- = 0 - (1 - a^+ a^-) a^- = - a^-. So sigma=-1 -> -F.
# Correct!
#
# What about [S, F]?
# S^{s1,s2}_{k,l} = b_k^{s1} b_l^{s2} + const
# [b_k^{s1} b_l^{s2}, a^sigma b_m^s] = a^sigma [b_k^{s1} b_l^{s2}, b_m^s]
# [b_k^{s1} b_l^{s2}, b_m^s] = b_k^{s1} [b_l^{s2}, b_m^s] + [b_k^{s1}, b_m^s] b_l^{s2}
# Commutators of b:
# [b_p^+, b_q^-] = - delta_{pq}   (since b_p^- b_q^+ = b_q^+ b_p^- + delta_pq -> [b_p^-, b_q^+] = delta_pq)
# Let's define epsilon(s, s') as the commutator [b^s, b^{s'}].
# epsilon(+, -) = -1
# epsilon(-, +) = 1
# epsilon(+, +) = 0
# epsilon(-, -) = 0
# So [b_p^s, b_q^{s'}] = epsilon(s, s') delta_{pq}.
#
# Thus [b_k^{s1} b_l^{s2}, b_m^s] = epsilon(s2, s) delta_{lm} b_k^{s1} + epsilon(s1, s) delta_{km} b_l^{s2}.
# So [S^{s1,s2}_{k,l}, F_m^{sigma, s}] = epsilon(s2, s) delta_{lm} F_k^{sigma, s1} + epsilon(s1, s) delta_{km} F_l^{sigma, s2}.
#
# What about {F_k^{sigma, s}, F_l^{sigma', s'}}?
# = {a^sigma b_k^s, a^{sigma'} b_l^{s'}}
# = a^sigma b_k^s a^{sigma'} b_l^{s'} + a^{sigma'} b_l^{s'} a^sigma b_k^s
# = a^sigma a^{sigma'} b_k^s b_l^{s'} + a^{sigma'} a^sigma b_l^{s'} b_k^s
# = a^sigma a^{sigma'} b_k^s b_l^{s'} + a^{sigma'} a^sigma (b_k^s b_l^{s'} - epsilon(s, s') delta_{kl})
# = {a^sigma, a^{sigma'}} b_k^s b_l^{s'} - a^{sigma'} a^sigma epsilon(s, s') delta_{kl}
# Note: {a^+, a^-} = 1, {a^+, a^+} = 0, {a^-, a^-} = 0.
# So {a^sigma, a^{sigma'}} = 1 if sigma != sigma', else 0.
# Also if sigma != sigma', say sigma=+, sigma'=-:
# a^- a^+ = 1 - a^+ a^- = 1/2 - C.
# a^+ a^- = 1/2 + C.
# Let's write this generally:
# If sigma == sigma', {a^sigma, a^sigma} = 0, and a^sigma a^sigma = 0, so the bracket is 0.
# If sigma != sigma':
#   {a^sigma, a^{sigma'}} = 1.
#   a^{sigma'} a^sigma = 1/2 - sigma * C. (For sigma=+, a^- a^+ = 1/2 - C, so sigma=+1 matches. For sigma=-, a^+ a^- = 1/2 + C, matches sigma=-1.)
#   So {F_k^{sigma, s}, F_l^{sigma', s'}} = S^{s, s'}_{k, l} - (1/2 - sigma * C) epsilon(s, s') delta_{kl}
# Let's check the constant:
# S^{s, s'}_{k, l} = b_k^s b_l^{s'} + (1/2 if s!=s' and k==l else 0)
# Wait, let's use the explicit formulas without constants, projecting onto g.
# {F_k^{sigma, s}, F_l^{sigma', s'}} = S^{s, s'}_{k, l} + sigma * epsilon(s, s') delta_{kl} C.
# Let's verify for k=l, s=+, s'=-, sigma=+, sigma'=-.
# {F_k^{+, +}, F_k^{-, -}} = S^{+, -}_{k, k} + 1 * (-1) * 1 * C = S^{+, -}_{k, k} - C.
# Let's compute directly: a^+ b_k^+ a^- b_k^- + a^- b_k^- a^+ b_k^+
# = a^+ a^- b_k^+ b_k^- + a^- a^+ b_k^- b_k^+
# = (C + 1/2) b_k^+ b_k^- + (1/2 - C) (b_k^+ b_k^- + 1)
# = C b_k^+ b_k^- + 1/2 b_k^+ b_k^- + 1/2 b_k^+ b_k^- - C b_k^+ b_k^- + 1/2 - C
# = b_k^+ b_k^- + 1/2 - C.
# Note that S^{+, -}_{k, k} = b_k^+ b_k^- + 1/2.
# So it equals S^{+, -}_{k, k} - C. Perfect!
# So the rule is:
# If sigma == sigma', 0.
# If sigma != sigma', S^{s, s'}_{k, l} + sigma * epsilon(s, s') delta_{kl} C.
# (Here sigma is +1 or -1)
#
# What about [S^{s1,s2}_{k,l}, S^{s3,s4}_{m,n}]?
# S = b_k^{s1} b_l^{s2} (ignoring central constants which commute with everything).
# [b_k^{s1} b_l^{s2}, b_m^{s3} b_n^{s4}] = b_k^{s1} [b_l^{s2}, b_m^{s3} b_n^{s4}] + [b_k^{s1}, b_m^{s3} b_n^{s4}] b_l^{s2}
# = b_k^{s1} ( b_m^{s3} [b_l^{s2}, b_n^{s4}] + [b_l^{s2}, b_m^{s3}] b_n^{s4} ) + ( b_m^{s3} [b_k^{s1}, b_n^{s4}] + [b_k^{s1}, b_m^{s3}] b_n^{s4} ) b_l^{s2}
# = epsilon(s2, s4) delta_{ln} b_k^{s1} b_m^{s3}
# + epsilon(s2, s3) delta_{lm} b_k^{s1} b_n^{s4}
# + epsilon(s1, s4) delta_{kn} b_m^{s3} b_l^{s2}
# + epsilon(s1, s3) delta_{km} b_m^{s3} b_n^{s4} ... wait, [b_k, b_m] is scalar, so it's epsilon(s1, s3) delta_{km} b_n^{s4} b_l^{s2}.
# We can map these back to S variables:
# = epsilon(s2, s4) delta_{ln} S^{s1, s3}_{k, m}
# + epsilon(s2, s3) delta_{lm} S^{s1, s4}_{k, n}
# + epsilon(s1, s4) delta_{kn} S^{s3, s2}_{m, l}
# + epsilon(s1, s3) delta_{km} S^{s4, s2}_{n, l}
# Let's check symmetry! b_m^{s3} b_l^{s2} = S^{s3, s2}_{m, l}. Yes!
# This gives the full bracket structure of g.

def main():
    pass

if __name__ == "__main__":
    main()
