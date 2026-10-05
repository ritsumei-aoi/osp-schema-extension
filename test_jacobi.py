import sympy as sp

# Let's test the brackets of osp(2|2) in detail:
# Generators:
# 0: J = a_+ a_- - 1/2
# 1: E = 1/2 (b_+)^2
# 2: F = 1/2 (b_-)^2
# 3: H = 1/2 (b_+ b_- + b_- b_+)
# 4: F_{++} = a_+ b_+
# 5: F_{+-} = a_+ b_-
# 6: F_{-+} = a_- b_+
# 7: F_{--} = a_- b_-

names = ['J', 'E', 'F', 'H', 'F++', 'F+-', 'F-+', 'F--']
parities = [0, 0, 0, 0, 1, 1, 1, 1]
dim = 8

C = { (i, j): [0]*dim for i in range(dim) for j in range(dim) }

# [H, E] = 2 E, [E, H] = -2 E
C[(3, 1)][1] = 2; C[(1, 3)][1] = -2
# [H, F] = -2 F, [F, H] = 2 F
C[(3, 2)][2] = -2; C[(2, 3)][2] = 2
# [E, F] = -H, [F, E] = H   (Wait! [b_-, b_+] = 1 => [b_+^2, b_-^2] = -4 H, so [1/2 b_+^2, 1/2 b_-^2] = -H)
C[(1, 2)][3] = -1; C[(2, 1)][3] = 1

# [J, F++] = F++, [J, F+-] = F+-
C[(0, 4)][4] = 1; C[(4, 0)][4] = -1
C[(0, 5)][5] = 1; C[(5, 0)][5] = -1
# [J, F-+] = -F-+, [J, F--] = -F--
C[(0, 6)][6] = -1; C[(6, 0)][6] = 1
C[(0, 7)][7] = -1; C[(7, 0)][7] = 1

# [E, F_{sigma, -}] = - F_{sigma, +}
# [E, F+-] = - F++, [F+-, E] = F++
C[(1, 5)][4] = -1; C[(5, 1)][4] = 1
# [E, F--] = - F-+, [F--, E] = F-+
C[(1, 7)][6] = -1; C[(7, 1)][6] = 1

# [F, F_{sigma, +}] = + F_{sigma, -}
# [F, F++] = F+-, [F++, F] = -F+-
C[(2, 4)][5] = 1; C[(4, 2)][5] = -1
# [F, F-+] = F--, [F-+, F] = -F--
C[(2, 6)][7] = 1; C[(6, 2)][7] = -1

# [H, F_{sigma, +}] = F_{sigma, +}
C[(3, 4)][4] = 1; C[(4, 3)][4] = -1
C[(3, 6)][6] = 1; C[(6, 3)][6] = -1

# [H, F_{sigma, -}] = -F_{sigma, -}
C[(3, 5)][5] = -1; C[(5, 3)][5] = 1
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

# Check Jacobi:
jac_err = 0
for i in range(dim):
    for j in range(dim):
        for k in range(dim):
            pi, pj, pk = parities[i], parities[j], parities[k]
            t1 = [sum(C[(j,k)][m] * C[(i,m)][r] for m in range(dim)) for r in range(dim)]
            t2 = [sum(C[(k,i)][m] * C[(j,m)][r] for m in range(dim)) for r in range(dim)]
            t3 = [sum(C[(i,j)][m] * C[(k,m)][r] for m in range(dim)) for r in range(dim)]
            s1, s2, s3 = (-1)**(pi * pk), (-1)**(pj * pi), (-1)**(pk * pj)
            tot = [s1 * t1[r] + s2 * t2[r] + s3 * t3[r] for r in range(dim)]
            if any(x != 0 for x in tot):
                print(f"Jacobi error for {names[i]}, {names[j]}, {names[k]}: {tot}")
                jac_err += 1

print(f"Total Jacobi errors: {jac_err}")
