import sympy as sp
from algebra_helper import build_algebra
from bracket_solver import compute_bracket

def test_algebra(n):
    print(f"\n==================== Testing C({n+1}) ====================")
    basis = build_algebra(n)
    dim = len(basis)
    basis_map = {b[0]: i for i, b in enumerate(basis)}
    
    even_count = sum(1 for b in basis if b[1] == 0)
    odd_count = sum(1 for b in basis if b[1] == 1)
    print(f"Dimension: total={dim}, even={even_count}, odd={odd_count}")
    print("Basis elements:", [b[0] for b in basis])
    
    # 0 gb_dict
    gb_zero = {}
    for sigma in ['+', '-']:
        for j in range(1, n + 1):
            for s in ['+', '-']:
                gb_zero[(sigma, j, s)] = sp.Rational(0)
                
    # Check skew-supersymmetry
    skew_ok = True
    for i in range(dim):
        for j in range(dim):
            X = basis[i]
            Y = basis[j]
            v0_xy, _ = compute_bracket(X, Y, n, basis, basis_map, gb_zero)
            v0_yx, _ = compute_bracket(Y, X, n, basis, basis_map, gb_zero)
            
            pX, pY = X[1], Y[1]
            sign = (-1)**(pX * pY)
            for k in range(dim):
                if v0_xy[k] != - sign * v0_yx[k]:
                    print(f"Skew-supersymmetry failed for [{X[0]}, {Y[0]}]: index {basis[k][0]} xy={v0_xy[k]} yx={v0_yx[k]}")
                    skew_ok = False
                    break
            if not skew_ok:
                break
        if not skew_ok:
            break
    print("Skew-supersymmetry check:", "PASSED" if skew_ok else "FAILED")
    
    # Check Jacobi identity
    # [X, [Y, Z]] = [[X, Y], Z] + (-1)^{pX pY} [Y, [X, Z]]
    # or (-1)^{pZ pX} [X, [Y, Z]] + (-1)^{pX pY} [Y, [Z, X]] + (-1)^{pY pZ} [Z, [X, Y]] = 0
    jacobi_ok = True
    # Let's compute structure constants C^k_{ij}
    C = [[[sp.Rational(0) for _ in range(dim)] for _ in range(dim)] for _ in range(dim)]
    for i in range(dim):
        for j in range(dim):
            v0, _ = compute_bracket(basis[i], basis[j], n, basis, basis_map, gb_zero)
            for k in range(dim):
                C[i][j][k] = v0[k]
                
    # Jacobi:
    for i in range(dim):
        for j in range(dim):
            for k in range(dim):
                pX, pY, pZ = basis[i][1], basis[j][1], basis[k][1]
                # term1: (-1)^{pZ pX} [X, [Y, Z]]
                # [Y, Z] = sum_m C[j][k][m] basis[m]
                # [X, [Y, Z]] = sum_m C[j][k][m] [X, basis[m]] = sum_{m, l} C[j][k][m] C[i][m][l] basis[l]
                
                # Check each component l
                for l in range(dim):
                    t1 = sum(C[j][k][m] * C[i][m][l] for m in range(dim)) * ((-1)**(pZ * pX))
                    t2 = sum(C[k][i][m] * C[j][m][l] for m in range(dim)) * ((-1)**(pX * pY))
                    t3 = sum(C[i][j][m] * C[k][m][l] for m in range(dim)) * ((-1)**(pY * pZ))
                    if t1 + t2 + t3 != 0:
                        print(f"Jacobi failed for ({basis[i][0]}, {basis[j][0]}, {basis[k][0]}) at {basis[l][0]}: {t1+t2+t3}")
                        jacobi_ok = False
                        break
                if not jacobi_ok:
                    break
            if not jacobi_ok:
                break
        if not jacobi_ok:
            break
    print("Jacobi identity check:", "PASSED" if jacobi_ok else "FAILED")

if __name__ == '__main__':
    for n in [1, 2, 3]:
        test_algebra(n)
