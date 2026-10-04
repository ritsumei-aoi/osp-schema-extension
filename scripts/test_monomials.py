import sympy as sp

# Let's verify the commutator of quadratic generators for n=1
# Generators of C(2) = osp(2|2):
# Fermionic: a_p = a_1^+, a_m = a_1^-  (p = +, m = -)
# Bosonic: b_p = b_1^+, b_m = b_1^-

# Oscillators and their parities:
# p(b_p) = 0, p(b_m) = 0
# p(a_p) = 1, p(a_m) = 1

# Basis of oscillators:
# 0: b_p, 1: b_m, 2: a_p, 3: a_m
names = ['b_p', 'b_m', 'a_p', 'a_m']
parities = [0, 0, 1, 1]

# Commutators [v_i, v_j] = c0[i][j] + c1[i][j] * kappa
# Undeformed c0:
# [b_m, b_p] = 1, [b_p, b_m] = -1
# [a_m, a_p] = 1, [a_p, a_m] = 1 (supercommutator: {a, b} for odd)
# Deformed c1:
# [b_j^s, a_1^sigma] = - gb_{sigma, j, s} * kappa
# [a_1^sigma, b_j^s] = gb_{sigma, j, s} * kappa

gb_pp = sp.Symbol('gb_pp') # gb_{a_1^+, b_1^+}
gb_pm = sp.Symbol('gb_pm') # gb_{a_1^+, b_1^-}
gb_mp = sp.Symbol('gb_mp') # gb_{a_1^-, b_1^+}
gb_mm = sp.Symbol('gb_mm') # gb_{a_1^-, b_1^-}

# Let's map (sigma, s) -> gb symbol:
# sigma in {+, -}, s in {+, -}
# [b_s, a_sigma] = - gb_{sigma, s}
# [a_sigma, b_s] = gb_{sigma, s}

c0 = { (i, j): 0 for i in range(4) for j in range(4) }
c0[(1, 0)] = 1   # [b_m, b_p] = 1
c0[(0, 1)] = -1  # [b_p, b_m] = -1
c0[(3, 2)] = 1   # [a_m, a_p] = 1
c0[(2, 3)] = 1   # [a_p, a_m] = 1

c1 = { (i, j): 0 for i in range(4) for j in range(4) }
# b_p is 0, b_m is 1, a_p is 2, a_m is 3
# [b_p, a_p] = -gb_pp
c1[(0, 2)] = -gb_pp
c1[(2, 0)] = gb_pp

# [b_p, a_m] = -gb_mp
c1[(0, 3)] = -gb_mp
c1[(3, 0)] = gb_mp

# [b_m, a_p] = -gb_pm
c1[(1, 2)] = -gb_pm
c1[(2, 1)] = gb_pm

# [b_m, a_m] = -gb_mm
c1[(1, 3)] = -gb_mm
c1[(3, 1)] = gb_mm

def bracket_oscillators(i, j):
    return c0[(i, j)], c1[(i, j)]

# Let a quadratic expression be represented as a dict of pairs (i, j) -> coefficient
# u_i u_j.
# Let's compute [u1 u2, w1 w2] in U(A):
# Formula:
# [u1 u2, w1 w2] = u1 [u2, w1 w2] + (-1)^{p(u2)(p(w1)+p(w2))} [u1, w1 w2] u2
# where [v, w1 w2] = [v, w1] w2 + (-1)^{p(v) p(w1)} w1 [v, w2].

def superbracket_monomials(u1, u2, w1, w2):
    # returns two dicts: part_0 (coeffs of pairs (i, j) for undeformed)
    # and part_1 (coeffs of pairs (i, j) for kappa * pair)
    pu1, pu2 = parities[u1], parities[u2]
    pw1, pw2 = parities[w1], parities[w2]
    pY = pw1 + pw2
    
    # [u2, w1] and [u2, w2]
    c0_u2_w1, c1_u2_w1 = bracket_oscillators(u2, w1)
    c0_u2_w2, c1_u2_w2 = bracket_oscillators(u2, w2)
    
    c0_u1_w1, c1_u1_w1 = bracket_oscillators(u1, w1)
    c0_u1_w2, c1_u1_w2 = bracket_oscillators(u1, w2)
    
    res0 = {}
    res1 = {}
    def add0(pair, val):
        res0[pair] = res0.get(pair, 0) + val
    def add1(pair, val):
        res1[pair] = res1.get(pair, 0) + val
        
    # Term 1: u1 [u2, w1] w2
    # [u2, w1] = c0 + c1 * kappa
    # u1 c0 w2 = c0 (u1 w2)
    if c0_u2_w1 != 0:
        add0((u1, w2), c0_u2_w1)
    # u1 (c1 kappa) w2 = c1 (-1)^{pu1} kappa (u1 w2)
    if c1_u2_w1 != 0:
        add1((u1, w2), c1_u2_w1 * (-1)**pu1)
        
    # Term 2: (-1)^{pu2 * pw1} u1 w1 [u2, w2]
    # [u2, w2] = c0 + c1 * kappa
    # u1 w1 (c0) = c0 (u1 w1)
    # u1 w1 (c1 kappa) = c1 (-1)^{pu1 + pw1} kappa (u1 w1)
    sign2 = (-1)**(pu2 * pw1)
    if c0_u2_w2 != 0:
        add0((u1, w1), sign2 * c0_u2_w2)
    if c1_u2_w2 != 0:
        add1((u1, w1), sign2 * c1_u2_w2 * (-1)**(pu1 + pw1))
        
    # Term 3: (-1)^{pu2 * pY} [u1, w1] w2 u2
    # [u1, w1] = c0 + c1 * kappa
    # (c0) w2 u2
    # (c1 kappa) w2 u2 = c1 kappa (w2 u2)
    sign3 = (-1)**(pu2 * pY)
    if c0_u1_w1 != 0:
        add0((w2, u2), sign3 * c0_u1_w1)
    if c1_u1_w1 != 0:
        add1((w2, u2), sign3 * c1_u1_w1)
        
    # Term 4: (-1)^{pu2 * pY + pu1 * pw1} w1 [u1, w2] u2
    # [u1, w2] = c0 + c1 * kappa
    # w1 (c0) u2 = c0 (w1 u2)
    # w1 (c1 kappa) u2 = c1 (-1)^{pw1} kappa (w1 u2)
    sign4 = (-1)**(pu2 * pY + pu1 * pw1)
    if c0_u1_w2 != 0:
        add0((w1, u2), sign4 * c0_u1_w2)
    if c1_u1_w2 != 0:
        add1((w1, u2), sign4 * c1_u1_w2 * (-1)**pw1)
        
    return res0, res1

print("Defined superbracket_monomials successfully.")
