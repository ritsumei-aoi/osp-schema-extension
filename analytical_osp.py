import sympy as sp

# Let's verify brackets explicitly for n=1:
# Oscillators: a_+, a_-, b_+, b_-
# Parity: p(a_pm) = 1, p(b_pm) = 0
# CAR: {a_-, a_+} = a_- a_+ + a_+ a_- = 1, a_+^2 = a_-^2 = 0
# CCR: [b_-, b_+] = b_- b_+ - b_+ b_- = 1, [b_+, b_+] = [b_-, b_-] = 0

# Basis for C(2) = osp(2|2):
# Even:
# J = a_+ a_- - 1/2
# E = 1/2 (b_+)^2
# F = 1/2 (b_-)^2
# H = 1/2 (b_+ b_- + b_- b_+) = b_+ b_- + 1/2

# Odd:
# F_{++} = a_+ b_+
# F_{+-} = a_+ b_-
# F_{-+} = a_- b_+
# F_{--} = a_- b_-

# Let's compute all brackets analytically!
print("Analytical brackets for osp(2|2):")

# [J, E] = 0, [J, F] = 0, [J, H] = 0
# [H, E] = (b_+ b_- + 1/2) (1/2 b_+^2) - (1/2 b_+^2) (b_+ b_- + 1/2)
# = 1/2 ( b_+ b_- b_+^2 - b_+^2 b_+ b_- ) = 1/2 b_+ (b_- b_+ - b_+ b_-) b_+ = 1/2 b_+ (1) b_+ = 1/2 b_+^2 = E. Wait!
# Let's check: [b_+ b_-, b_+^2] = b_+ [b_-, b_+^2] = b_+ ( [b_-, b_+] b_+ + b_+ [b_-, b_+] ) = b_+ (2 b_+) = 2 b_+^2.
# So [H, E] = 1/2 (2 b_+^2) = b_+^2 = 2 E.
# Similarly [H, F] = -2 F.
# [E, F] = [1/2 b_+^2, 1/2 b_-^2] = 1/4 [b_+^2, b_-^2] = 1/4 (-4 H) = -H.

# [J, F_{sigma, s}] = [a_+ a_-, a_sigma b_s] = [a_+ a_-, a_sigma] b_s
# [a_+ a_-, a_+] = a_+, so [J, F_{+, s}] = + F_{+, s}
# [a_+ a_-, a_-] = -a_-, so [J, F_{-, s}] = - F_{-, s}

# Let's check [E, F_{sigma, s}]:
# [1/2 b_+^2, a_sigma b_s] = a_sigma [1/2 b_+^2, b_s]
# For s = +: [b_+^2, b_+] = 0 => [E, F_{sigma, +}] = 0
# For s = -: [1/2 b_+^2, b_-] = 1/2 (b_+ [b_+, b_-] + [b_+, b_-] b_+) = 1/2 (-2 b_+) = -b_+
# So [E, F_{sigma, -}] = - a_sigma b_+ = - F_{sigma, +}.

# Let's check [F, F_{sigma, s}]:
# For s = +: [1/2 b_-^2, a_sigma b_+] = a_sigma 1/2 [b_-^2, b_+] = a_sigma 1/2 (2 b_-) = + a_sigma b_- = + F_{sigma, -}.
# For s = -: [F, F_{sigma, -}] = 0.

# Let's check [H, F_{sigma, s}]:
# [b_+ b_- + 1/2, a_sigma b_+] = a_sigma [b_+ b_-, b_+] = a_sigma b_+ [b_-, b_+] = + a_sigma b_+ = + F_{sigma, +}.
# [b_+ b_- + 1/2, a_sigma b_-] = a_sigma [b_+ b_-, b_-] = a_sigma [b_+, b_-] b_- = - a_sigma b_- = - F_{sigma, -}.

# Let's check odd-odd anticommutators {F_{sigma1, s1}, F_{sigma2, s2}}:
# {a_sigma1 b_s1, a_sigma2 b_s2} = a_sigma1 b_s1 a_sigma2 b_s2 + a_sigma2 b_s2 a_sigma1 b_s1
# In undeformed algebra, [a, b] = 0:
# = a_sigma1 a_sigma2 b_s1 b_s2 + a_sigma2 a_sigma1 b_s2 b_s1
# Case 1: sigma1 = sigma2 = +:
# a_+ a_+ = 0, so {F_{+, s1}, F_{+, s2}} = 0.
# Case 2: sigma1 = sigma2 = -:
# a_- a_- = 0, so {F_{-, s1}, F_{-, s2}} = 0.
# Case 3: sigma1 = +, sigma2 = -:
# a_+ a_- b_s1 b_s2 + a_- a_+ b_s2 b_s1
# = a_+ a_- b_s1 b_s2 + (1 - a_+ a_-) b_s2 b_s1
# = b_s2 b_s1 + a_+ a_- (b_s1 b_s2 - b_s2 b_s1)
# = b_s2 b_s1 + a_+ a_- [b_s1, b_s2]
# = 1/2 (b_s1 b_s2 + b_s2 b_s1) + 1/2 [b_s2, b_s1] + a_+ a_- [b_s1, b_s2]
# = 1/2 (b_s1 b_s2 + b_s2 b_s1) + (a_+ a_- - 1/2) [b_s1, b_s2]
# = B(b_s1, b_s2) + [b_s1, b_s2] J !

# Look how clean that is!
# {F_{+, s1}, F_{-, s2}} = B(b_s1, b_s2) + [b_s1, b_s2] J:
# - For s1 = +, s2 = +: [b_+, b_+] = 0, B(b_+, b_+) = b_+^2 = 2 E. So {F_{+,+}, F_{-,+}} = 2 E.
# - For s1 = -, s2 = -: [b_-, b_-] = 0, B(b_-, b_-) = b_-^2 = 2 F. So {F_{+,-}, F_{-,-}} = 2 F.
# - For s1 = +, s2 = -: [b_+, b_-] = -1, B(b_+, b_-) = H. So {F_{+,+}, F_{-,-}} = H - J.
# - For s1 = -, s2 = +: [b_-, b_+] = +1, B(b_-, b_+) = H. So {F_{+,-}, F_{-,+}} = H + J.

print("All undeformed brackets derived exactly!")
