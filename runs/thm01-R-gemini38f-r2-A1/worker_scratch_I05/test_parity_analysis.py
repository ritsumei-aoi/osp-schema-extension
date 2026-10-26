"""
Let's test normal_order_word with the commutator relation:
Let's see what happens to [X, Y] in U(A) if we use:
XY - (-1)^{pX pY} YX.
Wait, why did normal_order_deformed produce non-basis words?
Let's check the non-basis words:
[H_1, E_eps_del1_pp] gave:
b_1_p^2, b_1_p b_1_m, 1, a_1_p a_1_m.
Wait! Why did [H_1, E_eps_del1_pp] produce those words?
Let's trace:
H_1 = a_1_p a_1_m + b_1_p b_1_m (even)
E_eps_del1_pp = a_1_p b_1_p (odd).
[H_1, E_eps_del1_pp]:
p(H_1) = 0, p(E) = 1.
Bracket: H_1 E - E H_1.
Let's calculate:
H_1 E = (a_1_p a_1_m + b_1_p b_1_m) (a_1_p b_1_p)
= a_1_p a_1_m a_1_p b_1_p + b_1_p b_1_m a_1_p b_1_p.
And E H_1 = (a_1_p b_1_p) (a_1_p a_1_m + b_1_p b_1_m)
= a_1_p b_1_p a_1_p a_1_m + a_1_p b_1_p b_1_p b_1_m.
Let's do this by hand!
"""
# 1) a_1_p a_1_m a_1_p b_1_p:
# a_1_m a_1_p = 1 - a_1_p a_1_m.
# So a_1_p (1 - a_1_p a_1_m) b_1_p = a_1_p b_1_p - a_1_p^2 a_1_m b_1_p = a_1_p b_1_p.
# (purely unperturbed, no b adjacent to a with b on left!).

# 2) b_1_p b_1_m a_1_p b_1_p:
# Here b_1_m a_1_p = a_1_p b_1_m - gb_{p, 1, m} kappa !
# So b_1_p (a_1_p b_1_m - gb_{p, 1, m} kappa) b_1_p
# = b_1_p a_1_p b_1_m b_1_p - gb_{p, 1, m} kappa b_1_p b_1_p.
# And b_1_p a_1_p = a_1_p b_1_p - gb_{p, 1, p} kappa !
# So (a_1_p b_1_p - gb_{p, 1, p} kappa) b_1_m b_1_p - gb_{p, 1, m} kappa b_1_p^2
# = a_1_p b_1_p b_1_m b_1_p - gb_{p, 1, p} kappa b_1_p b_1_m b_1_p - gb_{p, 1, m} kappa b_1_p^2.
# Notice the kappa terms here are CUBIC in oscillators: b_1_p b_1_m b_1_p and b_1_p^2 !
# Wait! Why are there cubic terms?!
# Because H_1 has DEGREE 2, and E has DEGREE 2, so the product H_1 E has DEGREE 4!
# The commutator [H_1, E] in the associative algebra U has degree:
# In degree 0 (unperturbed), [H_1, E]_0 = 2 E (degree 2). The degree 4 terms cancel!
# But in degree 1 (kappa term), does it have degree 2 or degree 3?!
# A single swap of b and a replaces degree 4 by degree 2! (b a -> a b - kappa).
# So the kappa term has degree (4 - 2) = 2!
# BUT a_1_p b_1_p is degree 2 (linear in a, linear in b).
# And b_1_p^2 is degree 2 (purely bosonic, even parity)!
# But wait! If kappa has parity 1, and [H_1, E] has parity 1 (since p(H_1)=0, p(E)=1),
# then [H_1, E] = [H_1, E]_0 + kappa * gamma(H_1, E).
# If kappa has parity 1, what must the parity of gamma(H_1, E) be?!
# Total parity of [H_1, E] must be 1.
# p(kappa * gamma) = p(kappa) + p(gamma) = 1 + p(gamma) = 1 (mod 2).
# Therefore, p(gamma(H_1, E)) MUST BE 0 (EVEN)!
# And b_1_p^2 is EVEN!
