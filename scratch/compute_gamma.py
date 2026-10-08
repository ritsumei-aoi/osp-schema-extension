import sys
import numpy as np
from collections import defaultdict

def print_err(*args):
    print(*args, file=sys.stderr)

# We want to represent elements of the enveloping algebra and compute brackets.
# Instead of a full enveloping algebra, we can just track the rules.
# Generators of g:
# C = a^+ a^- - 1/2
# S^{s1, s2}_{k, l} = b_k^{s1} b_l^{s2} + (1/2 if s1!=s2 and k==l else 0) (note: S^{s1, s2}_{k,l} = S^{s2, s1}_{l,k})
# F^{sigma, s}_{k} = a^{sigma} b_k^s
#
# Let's write down the gamma directly by doing the contraction on the oscillators.
# gamma(X, Y) is defined by taking X * Y - (-1)^{p(X)p(Y)} Y * X
# In each product X * Y, we move oscillators to standard order or just apply the deformation relation:
# b_k^s a_1^sigma = a_1^sigma b_k^s - gb_{sigma, k, s} kappa
# 
# For example, let's compute gamma(F^{sigma, s}_k, F^{sigma', s'}_l).
# F_1 = a^{sigma} b_k^s, F_2 = a^{sigma'} b_l^{s'}
# F_1 F_2 + F_2 F_1 = a^{sigma} b_k^s a^{sigma'} b_l^{s'} + a^{sigma'} b_l^{s'} a^{sigma} b_k^s
# = a^{sigma} (a^{sigma'} b_k^s - gb_{sigma', k, s} kappa) b_l^{s'} + a^{sigma'} (a^{sigma} b_l^{s'} - gb_{sigma, l, s'} kappa) b_k^s
# = a^{sigma} a^{sigma'} b_k^s b_l^{s'} - gb_{sigma', k, s} a^{sigma} kappa b_l^{s'} + a^{sigma'} a^{sigma} b_l^{s'} b_k^s - gb_{sigma, l, s'} a^{sigma'} kappa b_k^s
# Since kappa is odd central: a^{sigma} kappa = - kappa a^{sigma}.
# So - gb_{sigma', k, s} a^{sigma} kappa b_l^{s'} = + gb_{sigma', k, s} kappa a^{sigma} b_l^{s'} = kappa ( gb_{sigma', k, s} F^{sigma, s'}_l )
# Similarly, - gb_{sigma, l, s'} a^{sigma'} kappa b_k^s = kappa ( gb_{sigma, l, s'} F^{sigma', s}_k )
# Thus, gamma( F^{sigma, s}_k, F^{sigma', s'}_l ) = gb_{sigma', k, s} F^{sigma, s'}_l + gb_{sigma, l, s'} F^{sigma', s}_k
#
# Let's check parity: p(gamma(F, F)) = p(F) = 1. Matches!
#
# What about gamma(C, F^{sigma, s}_k)?
# C = a^+ a^- - 1/2
# [C, F] = (a^+ a^- - 1/2) a^{sigma} b_k^s - a^{sigma} b_k^s (a^+ a^- - 1/2)
# = a^+ a^- a^{sigma} b_k^s - a^{sigma} b_k^s a^+ a^-
# = a^+ a^- a^{sigma} b_k^s - a^{sigma} (a^+ b_k^s - gb_{+, k, s} kappa) a^-
# = a^+ a^- a^{sigma} b_k^s - a^{sigma} a^+ b_k^s a^- + a^{sigma} gb_{+, k, s} kappa a^-
# And b_k^s a^- = a^- b_k^s - gb_{-, k, s} kappa
# So = a^+ a^- a^{sigma} b_k^s - a^{sigma} a^+ (a^- b_k^s - gb_{-, k, s} kappa) + a^{sigma} gb_{+, k, s} (- kappa a^-)
# = a^+ a^- a^{sigma} b_k^s - a^{sigma} a^+ a^- b_k^s + a^{sigma} a^+ gb_{-, k, s} kappa - gb_{+, k, s} a^{sigma} kappa a^-
# = (a^+ a^- a^{sigma} - a^{sigma} a^+ a^-) b_k^s + gb_{-, k, s} a^{sigma} a^+ kappa - gb_{+, k, s} a^{sigma} (-kappa) a^-
# The first part is the 0-th order bracket. The gamma part is:
# kappa [ gb_{-, k, s} a^{sigma} a^+ + gb_{+, k, s} a^{sigma} a^- ]
# Wait, a^{sigma} a^+ kappa = - kappa a^{sigma} a^+ ?
# No, p(a a) = 0, so a a kappa = kappa a a.
# And a^{sigma} kappa a^- = - kappa a^{sigma} a^- = - kappa a^{sigma} a^-.
# So gamma term = kappa ( gb_{-, k, s} a^{sigma} a^+ - gb_{+, k, s} a^{sigma} a^- )
# But this is an even element! Is it in g?
# If sigma = +, gb_{-, k, s} a^+ a^+ - gb_{+, k, s} a^+ a^- = - gb_{+, k, s} a^+ a^- = - gb_{+, k, s} (C + 1/2).
# If sigma = -, gb_{-, k, s} a^- a^+ - gb_{+, k, s} a^- a^- = gb_{-, k, s} (1 - a^+ a^-) = gb_{-, k, s} (1/2 - C).
# But gamma values must be in g.
# The constant term (like -1/2 * gb) must vanish, or else it is not a deformation of g!
# Let's check this carefully:
# gamma(C, F^{+, s}_k) = - gb_{+, k, s} C - 1/2 gb_{+, k, s} * I
# For this to be in g, the coefficient of the identity must be 0, which means gb_{+, k, s} = 0?
# Wait! This is a super important point. "gamma(X, Y) = (delta f)(X, Y) for all X,Y in g up to scalar"
# Ah! "up to scalar" means modulo the identity element!
# Let me reread `C_coboundary_definition.md`.
# "gamma(X, Y) = (delta f)(X, Y) for all X, Y in \mathfrak{g} up to scalar."
# Yes, it means the equality holds in the Lie superalgebra, where we might ignore the central extension part, or perhaps gamma itself produces central terms (scalars) which we quotient out.
# So we can project onto g by dropping the constant terms.
# So gamma(C, F^{+, s}_k) = - gb_{+, k, s} C
# gamma(C, F^{-, s}_k) = - gb_{-, k, s} C

# Let's write the rules for all pairs.
# g has basis:
# C
# S_{kl}^{s1,s2} = b_k^{s1} b_l^{s2} + (1/2 if s1!=s2 and k==l else 0)
# F_k^{sigma, s} = a^{sigma} b_k^s

n = 1

def p_F(): return 1
def p_S(): return 0
def p_C(): return 0

# We'll represent elements of g as dicts: { basis_name : coefficient }
# basis names: 'C', ('S', k, l, s1, s2), ('F', k, sigma, s)
# Note: S is symmetric. We'll canonicalize ('S', k, l, s1, s2) so that (k, s1) <= (l, s2).

def make_S(k, l, s1, s2):
    if (k, s1) > (l, s2):
        k, l, s1, s2 = l, k, s2, s1
    return ('S', k, l, s1, s2)

# Un-deformed brackets
def bracket_0(X, Y):
    # Returns a dict of basis : coeff
    res = defaultdict(int)
    
    # We can just implement the oscillator commutator manually
    # or hardcode the Lie superalgebra brackets.
    # [C, C] = 0
    # [C, S] = 0
    # [S, S] = standard sp(2n) bracket
    # [C, F_k^{sigma, s}] = sigma * F_k^{sigma, s}
    # [S_{kl}^{s1,s2}, F_m^{sigma, s}] = ...
    # {F_k^{sigma, s}, F_l^{sigma', s'}} = ...
    return res

# Let's build a full oscillator multiplier that computes normal-ordered expressions.
# oscillators: a+, a-, b_1+, b_1-, ...
# normal order: b+ left of b-, a+ left of a-.
# Actually, since max degree is 4, we can just use strings or tuples.

# Let's formalize words as tuples of (type, index, sign).
# type: 'a' or 'b'
# index: 1..n (for b), 1 (for a)
# sign: '+' or '-'

def multiply_words(w1, w2, use_gamma=False):
    # Returns a list of (word, coeff, gamma_coeff)
    # word is a tuple of letters.
    # gamma_coeff is the coefficient of kappa * word.
    # Since we only care about O(gamma) terms, gamma_coeff is linear in gb.
    # Actually, let's represent terms as (word, coeff, dict_of_gamma_coeffs)
    pass

