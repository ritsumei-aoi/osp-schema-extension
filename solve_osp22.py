import sympy as sp
import json

# Setup osp(2|2) exact system
names = ['J', 'E', 'F', 'H', 'F++', 'F+-', 'F-+', 'F--']
parities = [0, 0, 0, 0, 1, 1, 1, 1]
dim = 8

C = { (i, j): [0]*dim for i in range(dim) for j in range(dim) }

# [H, E] = 2 E, [E, H] = -2 E
C[(3, 1)][1] = 2; C[(1, 3)][1] = -2
# [H, F] = -2 F, [F, H] = 2 F
C[(3, 2)][2] = -2; C[(2, 3)][2] = 2
# [E, F] = -H, [F, E] = H
C[(1, 2)][3] = -1; C[(2, 1)][3] = 1

# [J, F++] = F++, [J, F+-] = F+-
C[(0, 4)][4] = 1; C[(4, 0)][4] = -1
C[(0, 5)][5] = 1; C[(5, 0)][5] = -1
# [J, F-+] = -F-+, [J, F--] = -F--
C[(0, 6)][6] = -1; C[(6, 0)][6] = 1
C[(0, 7)][7] = -1; C[(7, 0)][7] = 1

# [E, F+-] = - F++, [F+-, E] = F++
C[(1, 5)][4] = -1; C[(5, 1)][4] = 1
# [E, F--] = - F-+, [F--, E] = F-+
C[(1, 7)][6] = -1; C[(7, 1)][6] = 1

# [F, F++] = F+-, [F++, F] = -F+-
C[(2, 4)][5] = 1; C[(4, 2)][5] = -1
# [F, F-+] = F--, [F-+, F] = -F--
C[(2, 6)][7] = 1; C[(6, 2)][7] = -1

# [H, F++] = F++, [F++, H] = -F++
C[(3, 4)][4] = 1; C[(4, 3)][4] = -1
# [H, F-+] = F-+, [F-+, H] = -F-+
C[(3, 6)][6] = 1; C[(6, 3)][6] = -1

# [H, F+-] = -F+-, [F+-, H] = F+-
C[(3, 5)][5] = -1; C[(5, 3)][5] = 1
# [H, F--] = -F--, [F--, H] = F--
C[(3, 7)][7] = -1; C[(7, 3)][7] = 1

# Anticommutators:
# {F++, F-+} = 2 E
C[(4, 6)][1] = 2; C[(6, 4)][1] = 2
# {F+-, F--} = 2 F
C[(5, 7)][2] = 2; C[(7, 5)][2] = 2
# {F++, F--} = H - J
C[(4, 7)][3] = 1; C[(4, 7)][0] = -1
C[(7, 4)][3] = 1; C[(7, 4)][0] = -1
# {F+-, F-+} = H + J
C[(5, 6)][3] = 1; C[(5, 6)][0] = 1
C[(6, 5)][3] = 1; C[(6, 5)][0] = 1

# Deformation parameters:
# gb_p_p = gb(+, +), gb_p_m = gb(+, -), gb_m_p = gb(-, +), gb_m_m = gb(-, -)
gb_pp = sp.Symbol('gb_pp')
gb_pm = sp.Symbol('gb_pm')
gb_mp = sp.Symbol('gb_mp')
gb_mm = sp.Symbol('gb_mm')
gb_list = [gb_pp, gb_pm, gb_mp, gb_mm]

# Compute gamma_{ij}^k from oscillator algebra definitions:
gamma = { (i, j): [sp.Rational(0)]*dim for i in range(dim) for j in range(dim) }

# Recall:
# 1. Even-Even:
# gamma(J, E) = gb_m_p F++ + gb_p_p F-+
# Wait, let's verify gamma(J, E):
# [J, E] = [a_+ a_-, 1/2 b_+^2] = 1/2 ( [a_+ a_-, b_+] b_+ + b_+ [a_+ a_-, b_+] )
# [a_+ a_-, b_+] = kappa (gb_m_p a_+ + gb_p_p a_-)
# So [J, E] = kappa (gb_m_p a_+ b_+ + gb_p_p a_- b_+) = kappa (gb_m_p F++ + gb_p_p F-+)
gamma[(0, 1)][4] = gb_mp; gamma[(0, 1)][6] = gb_pp
gamma[(1, 0)][4] = -gb_mp; gamma[(1, 0)][6] = -gb_pp

# gamma(J, F):
# [J, F] = [a_+ a_-, 1/2 b_-^2] = kappa (gb_m_m a_+ b_- + gb_p_m a_- b_-) = kappa (gb_m_m F+- + gb_p_m F--)
gamma[(0, 2)][5] = gb_mm; gamma[(0, 2)][7] = gb_pm
gamma[(2, 0)][5] = -gb_mm; gamma[(2, 0)][7] = -gb_pm

# gamma(J, H):
# [J, H] = [a_+ a_-, 1/2 (b_+ b_- + b_- b_+)]
# = 1/2 [ (gb_m_p a_+ + gb_p_p a_-) b_- + b_+ (gb_m_m a_+ + gb_p_m a_-) + (gb_m_m a_+ + gb_p_m a_-) b_+ + b_- (gb_m_p a_+ + gb_p_p a_-) ]
# = 1/2 [ gb_m_p F+- + gb_p_p F-- + gb_m_m F++ + gb_p_m F-+ + gb_m_m F++ + gb_p_m F-+ + gb_m_p F+- + gb_p_p F-- ]
# = gb_m_m F++ + gb_p_m F-+ + gb_m_p F+- + gb_p_p F--
gamma[(0, 3)][4] = gb_mm; gamma[(0, 3)][6] = gb_pm; gamma[(0, 3)][5] = gb_mp; gamma[(0, 3)][7] = gb_pp
gamma[(3, 0)][4] = -gb_mm; gamma[(3, 0)][6] = -gb_pm; gamma[(3, 0)][5] = -gb_mp; gamma[(3, 0)][7] = -gb_pp

# 2. Even-Odd:
# gamma(J, F++) = gb_pp J
gamma[(0, 4)][0] = gb_pp; gamma[(4, 0)][0] = -gb_pp
# gamma(J, F+-) = gb_pm J
gamma[(0, 5)][0] = gb_pm; gamma[(5, 0)][0] = -gb_pm
# gamma(J, F-+) = -gb_mp J
gamma[(0, 6)][0] = -gb_mp; gamma[(6, 0)][0] = gb_mp
# gamma(J, F--) = -gb_mm J
gamma[(0, 7)][0] = -gb_mm; gamma[(7, 0)][0] = gb_mm

# gamma(E, F):
# [E, F_{sigma, s}]_gamma:
# [1/2 b_+^2, a_sigma b_s] = [1/2 b_+^2, a_sigma] b_s + a_sigma [1/2 b_+^2, b_s]
# [1/2 b_+^2, a_sigma] = - kappa gb_{sigma, +} b_+
# So [E, F_{sigma, s}]_kappa = - gb_{sigma, +} b_+ b_s = - gb_{sigma, +} ( 2 E if s=+ else H )
# For F++ (sigma=+, s=+): gamma(E, F++) = - 2 gb_pp E
gamma[(1, 4)][1] = -2 * gb_pp; gamma[(4, 1)][1] = 2 * gb_pp
# For F+- (sigma=+, s=-): gamma(E, F+-) = - gb_pp H
gamma[(1, 5)][3] = -gb_pp; gamma[(5, 1)][3] = gb_pp
# For F-+ (sigma=-, s=+): gamma(E, F-+) = - 2 gb_mp E
gamma[(1, 6)][1] = -2 * gb_mp; gamma[(6, 1)][1] = 2 * gb_mp
# For F-- (sigma=-, s=-): gamma(E, F--) = - gb_mp H
gamma[(1, 7)][3] = -gb_mp; gamma[(7, 1)][3] = gb_mp

# gamma(F, F_{sigma, s}):
# [1/2 b_-^2, a_sigma b_s] = - kappa gb_{sigma, -} b_- b_s = - gb_{sigma, -} ( 2 F if s=- else H )
# For F++: gamma(F, F++) = - gb_pm H
gamma[(2, 4)][3] = -gb_pm; gamma[(4, 2)][3] = gb_pm
# For F+-: gamma(F, F+-) = - 2 gb_pm F
gamma[(2, 5)][2] = -2 * gb_pm; gamma[(5, 2)][2] = 2 * gb_pm
# For F-+: gamma(F, F-+) = - gb_mm H
gamma[(2, 6)][3] = -gb_mm; gamma[(6, 2)][3] = gb_mm
# For F--: gamma(F, F--) = - 2 gb_mm F
gamma[(2, 7)][2] = -2 * gb_mm; gamma[(7, 2)][2] = 2 * gb_mm

# gamma(H, F_{sigma, s}):
# [1/2(b_+ b_- + b_- b_+), a_sigma b_s] = - 1/2 kappa ( gb_{sigma,-} b_+ + gb_{sigma,+} b_- ) b_s - 1/2 kappa b_s ( ... )
# = - kappa [ gb_{sigma, -} (b_+ b_s symmetrized) + gb_{sigma, +} (b_- b_s symmetrized) ]
# For F++ (sigma=+, s=+): - [ gb_pm (b_+^2 = 2E) + gb_pp (b_- b_+ = H) ] = - 2 gb_pm E - gb_pp H
gamma[(3, 4)][1] = -2 * gb_pm; gamma[(3, 4)][3] = -gb_pp
gamma[(4, 3)][1] = 2 * gb_pm; gamma[(4, 3)][3] = gb_pp
# For F+- (sigma=+, s=-): - [ gb_pm (b_+ b_- = H) + gb_pp (b_-^2 = 2F) ] = - gb_pm H - 2 gb_pp F
gamma[(3, 5)][3] = -gb_pm; gamma[(3, 5)][2] = -2 * gb_pp
gamma[(5, 3)][3] = gb_pm; gamma[(5, 3)][2] = 2 * gb_pp
# For F-+ (sigma=-, s=+): - [ gb_mm (b_+^2 = 2E) + gb_mp (b_- b_+ = H) ] = - 2 gb_mm E - gb_mp H
gamma[(3, 6)][1] = -2 * gb_mm; gamma[(3, 6)][3] = -gb_mp
gamma[(6, 3)][1] = 2 * gb_mm; gamma[(6, 3)][3] = gb_mp
# For F-- (sigma=-, s=-): - [ gb_mm (b_+ b_- = H) + gb_mp (b_-^2 = 2F) ] = - gb_mm H - 2 gb_mp F
gamma[(3, 7)][3] = -gb_mm; gamma[(3, 7)][2] = -2 * gb_mp
gamma[(7, 3)][3] = gb_mm; gamma[(7, 3)][2] = 2 * gb_mp

# 3. Odd-Odd:
# gamma(F_{s1, b1}, F_{s2, b2}) = - [ gb_{s2, b1} F_{s1, b2} + gb_{s1, b2} F_{s2, b1} ]
# Note: anticommutator gamma(X, Y) is symmetric for odd-odd!
odd_indices = [4, 5, 6, 7]
odd_info = [('+', '+'), ('+', '-'), ('-', '+'), ('-', '-')]
for i_idx, i in enumerate(odd_indices):
    s1, b1 = odd_info[i_idx]
    for j_idx, j in enumerate(odd_indices):
        s2, b2 = odd_info[j_idx]
        
        # term 1: - gb_{s2, b1} F_{s1, b2}
        gb_val1 = gb_pp if (s2, b1)==('+', '+') else (gb_pm if (s2, b1)==('+', '-') else (gb_mp if (s2, b1)==('-', '+') else gb_mm))
        target1 = odd_indices[odd_info.index((s1, b2))]
        
        # term 2: - gb_{s1, b2} F_{s2, b1}
        gb_val2 = gb_pp if (s1, b2)==('+', '+') else (gb_pm if (s1, b2)==('+', '-') else (gb_mp if (s1, b2)==('-', '+') else gb_mm))
        target2 = odd_indices[odd_info.index((s2, b1))]
        
        gamma[(i, j)][target1] -= gb_val1
        gamma[(i, j)][target2] -= gb_val2

print("Setup completed. Building coboundary linear system...")

# Coboundary setup:
phi = {}
phi_vars = []
for j in range(dim):
    for i in range(dim):
        if parities[i] != parities[j]:
            var = sp.Symbol(f"phi_{i}_{j}")
            phi[(i, j)] = var
            phi_vars.append(var)
        else:
            phi[(i, j)] = sp.Rational(0)

print(f"Number of phi variables: {len(phi_vars)}")

# Coboundary formula from doc:
# (\delta f)(X, Y) = (-1)^{p(X)} [X, f(Y)] - (-1)^{(p(X)+1)p(Y)} [Y, f(X)] - f([X, Y])
equations = []
for i in range(dim):
    for j in range(dim):
        pi = parities[i]
        pj = parities[j]
        for k in range(dim):
            delta_f_ijk = (
                (-1)**pi * sum(phi[(m, j)] * C[(i, m)][k] for m in range(dim))
                - (-1)**((pi + 1) * pj) * sum(phi[(m, i)] * C[(j, m)][k] for m in range(dim))
                - sum(C[(i, j)][m] * phi[(k, m)] for m in range(dim))
            )
            eq = delta_f_ijk - gamma[(i, j)][k]
            eq_simp = sp.simplify(eq)
            if eq_simp != 0:
                equations.append(eq_simp)

print(f"Number of independent equations: {len(equations)}")

sol = sp.solve(equations, phi_vars, dict=True)
print(f"Number of solution branches: {len(sol)}")
if len(sol) > 0:
    s = sol[0]
    print(f"Solution size: {len(s)}")
    # Check residuals
    residuals = []
    for eq in equations:
        r = sp.simplify(eq.subs(s))
        if r != 0:
            residuals.append(r)
    print(f"Residual equations: {len(residuals)}")
    if len(residuals) == 0:
        print("\n>>> PROVEN: Inhomogeneous deformation of osp(2|2) is TRIVIAL for all gb! <<<")
        print("Explicit solution for phi in terms of gb:")
        for k, v in s.items():
            if v != 0:
                print(f"  {k} = {v}")
    else:
        print("Residuals found:", residuals)
        gb_sol = sp.solve(residuals, gb_list)
        print("Constraints on gb:", gb_sol)
