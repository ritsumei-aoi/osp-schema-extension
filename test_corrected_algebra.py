import sympy as sp

def test_algebra(n):
    bosons = []
    for k in range(1, n + 1):
        bosons.append((k, '+'))
        bosons.append((k, '-'))
    num_b = 2 * n

    basis = []
    parities = []

    # J:
    basis.append(('J',))
    parities.append(0)

    # Sp(2n):
    for i in range(num_b):
        for j in range(i, num_b):
            b1, b2 = bosons[i], bosons[j]
            basis.append(('B', b1, b2))
            parities.append(0)

    # Odd:
    for sigma in ['+', '-']:
        for b in bosons:
            basis.append(('F', sigma, b))
            parities.append(1)

    dim_total = len(basis)
    dim_even = sum(1 for p in parities if p == 0)
    dim_odd = sum(1 for p in parities if p == 1)

    def get_B_idx(b1, b2):
        i1 = bosons.index(b1)
        i2 = bosons.index(b2)
        if i1 <= i2:
            return basis.index(('B', b1, b2))
        else:
            return basis.index(('B', b2, b1))

    def get_F_idx(sigma, b):
        return basis.index(('F', sigma, b))

    def omega(b1, b2):
        if b1[0] == b2[0]:
            if b1[1] == '-' and b2[1] == '+':
                return 1
            elif b1[1] == '+' and b2[1] == '-':
                return -1
        return 0

    C = { (i, j): [sp.Rational(0)]*dim_total for i in range(dim_total) for j in range(dim_total) }

    # [J, F(sigma, b)]:
    for b in bosons:
        idx_p = get_F_idx('+', b)
        idx_m = get_F_idx('-', b)
        C[(0, idx_p)][idx_p] = sp.Rational(1)
        C[(idx_p, 0)][idx_p] = sp.Rational(-1)
        C[(0, idx_m)][idx_m] = sp.Rational(-1)
        C[(idx_m, 0)][idx_m] = sp.Rational(1)

    # [B(b1, b2), B(b3, b4)]:
    for i in range(1, dim_even):
        _, b1, b2 = basis[i]
        for j in range(1, dim_even):
            _, b3, b4 = basis[j]
            # Bracket of B(b1, b2) with B(b3, b4)
            # Factor for Z:
            # If b1==b2 and b3==b4: [1/2 b1^2, 1/2 b3^2] = omega(b1, b3) Z_{b1, b3}
            # If b1==b2 and b3!=b4: [1/2 b1^2, Z_{b3, b4}] = omega(b1, b3) Z_{b1, b4} + omega(b1, b4) Z_{b1, b3}
            # If b1!=b2 and b3==b4: [Z_{b1, b2}, 1/2 b3^2] = omega(b2, b3) Z_{b1, b3} + omega(b1, b3) Z_{b2, b3}
            # If b1!=b2 and b3!=b4: [Z_{b1, b2}, Z_{b3, b4}] = w23 Z_{14} + w24 Z_{13} + w13 Z_{24} + w14 Z_{23}
            
            if b1 == b2 and b3 == b4:
                terms = [(omega(b1, b3), b1, b3)]
            elif b1 == b2 and b3 != b4:
                terms = [(omega(b1, b3), b1, b4), (omega(b1, b4), b1, b3)]
            elif b1 != b2 and b3 == b4:
                terms = [(omega(b2, b3), b1, b3), (omega(b1, b3), b2, b3)]
            else:
                terms = [
                    (omega(b2, b3), b1, b4),
                    (omega(b2, b4), b1, b3),
                    (omega(b1, b3), b2, b4),
                    (omega(b1, b4), b2, b3)
                ]
            for w, u, v in terms:
                if w != 0:
                    idx = get_B_idx(u, v)
                    mult = 2 if u == v else 1
                    C[(i, j)][idx] += sp.Rational(w * mult)

    # [B(b1, b2), F(sigma, b3)]:
    for i in range(1, dim_even):
        _, b1, b2 = basis[i]
        for j in range(dim_even, dim_total):
            _, sigma, b3 = basis[j]
            if b1 == b2:
                terms = [(omega(b1, b3), b1)]
            else:
                terms = [(omega(b2, b3), b1), (omega(b1, b3), b2)]
            for w, u in terms:
                if w != 0:
                    idx = get_F_idx(sigma, u)
                    C[(i, j)][idx] += sp.Rational(w)
                    C[(j, i)][idx] -= sp.Rational(w)

    # {F(sigma1, b1), F(sigma2, b2)}:
    for i in range(dim_even, dim_total):
        _, sig1, b1 = basis[i]
        for j in range(dim_even, dim_total):
            _, sig2, b2 = basis[j]
            if sig1 == '+' and sig2 == '-':
                idx = get_B_idx(b1, b2)
                mult = 2 if b1 == b2 else 1
                w12 = omega(b1, b2)
                C[(i, j)][idx] += sp.Rational(mult)
                C[(i, j)][0] += sp.Rational(w12)
            elif sig1 == '-' and sig2 == '+':
                idx = get_B_idx(b1, b2)
                mult = 2 if b1 == b2 else 1
                w12 = omega(b1, b2)
                C[(i, j)][idx] += sp.Rational(mult)
                C[(i, j)][0] -= sp.Rational(w12)

    # Verify Jacobi:
    jac_err = 0
    for i in range(dim_total):
        for j in range(dim_total):
            for k in range(dim_total):
                pi, pj, pk = parities[i], parities[j], parities[k]
                t1 = [sum(C[(j,k)][m] * C[(i,m)][r] for m in range(dim_total)) for r in range(dim_total)]
                t2 = [sum(C[(k,i)][m] * C[(j,m)][r] for m in range(dim_total)) for r in range(dim_total)]
                t3 = [sum(C[(i,j)][m] * C[(k,m)][r] for m in range(dim_total)) for r in range(dim_total)]
                s1, s2, s3 = (-1)**(pi * pk), (-1)**(pj * pi), (-1)**(pk * pj)
                tot = [s1 * t1[r] + s2 * t2[r] + s3 * t3[r] for r in range(dim_total)]
                if any(x != 0 for x in tot):
                    jac_err += 1
    print(f"n={n}: Jacobi errors = {jac_err}")
    return jac_err

for n in [1, 2, 3]:
    test_algebra(n)
