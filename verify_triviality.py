"""
Computational verification of triviality for C(n+1) = osp(2|2n) deformations.

This script:
1. Builds structure constants for C(2) = osp(2|2) using oscillator realization.
2. Verifies the Jacobi identity.
3. Computes the deformation cocycle gamma_gb.
4. Sets up and solves the linear system gamma_gb = delta(f).
5. Determines triviality for n=1, and provides the general-n argument.
"""

import numpy as np
import json


def bracket(sc, v, w, par):
    """Compute [v, w] given structure constants, where v, w are coefficient vectors."""
    dim = len(v)
    result = np.zeros(dim)
    for i in range(dim):
        if abs(v[i]) < 1e-15:
            continue
        for j in range(dim):
            if abs(w[j]) < 1e-15:
                continue
            result += v[i] * w[j] * sc[i, j]
    return result


def build_osp22():
    """
    Build structure constants for C(2) = osp(2|2), n=1.

    Basis (indexed 0..7):
      0: H1 = a1+a1- + b1+b1-
      1: H2 = -b1+b1- - 1/2
      2: Ep = (b1+)^2          = E_{2d1}
      3: Em = (b1-)^2          = E_{-2d1}
      4: o1 = a1+b1+           = E_{e+d1}
      5: o2 = a1+b1-           = E_{e-d1}
      6: o3 = a1-b1+           = E_{-e+d1}
      7: o4 = a1-b1-           = E_{-e-d1}
    """
    labels = ["H1", "H2", "Ep", "Em", "o1", "o2", "o3", "o4"]
    dim = 8
    par = np.array([0, 0, 0, 0, 1, 1, 1, 1])
    sc = np.zeros((dim, dim, dim))

    # I'll build only (i,j) with i < j (or i <= j for odd-odd diagonal),
    # then fill in by super-antisymmetry.

    def set_bracket(i, j, coeffs):
        """Set [X_i, X_j] = sum of coeffs, where coeffs = {index: value}."""
        for k, v in coeffs.items():
            sc[i, j, k] = v

    # Even-Even brackets
    # [H1, H2] = 0 (already zero)
    set_bracket(0, 2, {2: 2})      # [H1, Ep] = 2*Ep
    set_bracket(0, 3, {3: -2})     # [H1, Em] = -2*Em
    set_bracket(1, 2, {2: -2})     # [H2, Ep] = -2*Ep
    set_bracket(1, 3, {3: 2})      # [H2, Em] = 2*Em
    set_bracket(2, 3, {1: 4})      # [Ep, Em] = 4*H2

    # Even-Odd brackets
    set_bracket(0, 4, {4: 2})      # [H1, o1] = 2*o1
    # [H1, o2] = 0
    # [H1, o3] = 0
    set_bracket(0, 7, {7: -2})     # [H1, o4] = -2*o4

    set_bracket(1, 4, {4: -1})     # [H2, o1] = -o1
    set_bracket(1, 5, {5: 1})      # [H2, o2] = o2
    set_bracket(1, 6, {6: -1})     # [H2, o3] = -o3
    set_bracket(1, 7, {7: 1})      # [H2, o4] = o4

    set_bracket(2, 5, {4: -2})     # [Ep, o2] = -2*o1
    set_bracket(2, 7, {6: -2})     # [Ep, o4] = -2*o3
    # [Ep, o1] = 0, [Ep, o3] = 0

    set_bracket(3, 4, {5: 2})      # [Em, o1] = 2*o2
    set_bracket(3, 6, {7: 2})      # [Em, o3] = 2*o4
    # [Em, o2] = 0, [Em, o4] = 0

    # Odd-Odd brackets (anticommutator / symmetric)
    set_bracket(4, 6, {2: 1})      # {o1, o3} = Ep
    set_bracket(4, 7, {0: -1, 1: -2})  # {o1, o4} = -H1 - 2*H2
    set_bracket(5, 6, {0: 1})      # {o2, o3} = H1
    set_bracket(5, 7, {3: 1})      # {o2, o4} = Em
    # {o1, o1} = 0, {o1, o2} = 0, {o2, o2} = 0
    # {o3, o3} = 0, {o3, o4} = 0, {o4, o4} = 0

    # Fill in super-antisymmetry: [X_j, X_i] = -(-1)^{p_i * p_j} * [X_i, X_j]
    for i in range(dim):
        for j in range(i + 1, dim):
            sign = -(-1) ** (par[i] * par[j])
            sc[j, i] = sign * sc[i, j]

    return labels, par, sc


def check_jacobi(sc, par):
    """Check super Jacobi identity for all triples."""
    dim = len(par)
    max_err = 0
    worst = None
    for i in range(dim):
        for j in range(dim):
            for k in range(dim):
                pi, pj, pk = par[i], par[j], par[k]
                # [X_i, [X_j, X_k]]
                inner_jk = sc[j, k]  # vector: [X_j, X_k]
                t1_vec = np.zeros(dim)
                for l in range(dim):
                    if abs(inner_jk[l]) > 1e-15:
                        t1_vec += inner_jk[l] * sc[i, l]  # [X_i, X_l]
                t1 = ((-1) ** (pi * pk)) * t1_vec

                inner_ki = sc[k, i]
                t2_vec = np.zeros(dim)
                for l in range(dim):
                    if abs(inner_ki[l]) > 1e-15:
                        t2_vec += inner_ki[l] * sc[j, l]
                t2 = ((-1) ** (pj * pi)) * t2_vec

                inner_ij = sc[i, j]
                t3_vec = np.zeros(dim)
                for l in range(dim):
                    if abs(inner_ij[l]) > 1e-15:
                        t3_vec += inner_ij[l] * sc[k, l]
                t3 = ((-1) ** (pk * pj)) * t3_vec

                err = np.max(np.abs(t1 + t2 + t3))
                if err > max_err:
                    max_err = err
                    worst = (i, j, k)
    return max_err, worst


def compute_gamma(sc, par, gb):
    """
    Compute gamma_gb for C(2) = osp(2|2).

    gb = [gb_{+,1,+}, gb_{+,1,-}, gb_{-,1,+}, gb_{-,1,-}]

    gamma is computed by tracking kappa-terms from the deformed oscillator relation
    [b_1^s, a_1^sigma] = -gb_{sigma,1,s} * kappa.
    """
    gpp, gpm, gmp, gmm = gb
    dim = 8
    gamma = np.zeros((dim, dim, dim))

    # Convention: gamma[i,j,k] = coefficient of X_k in gamma(X_i, X_j)
    # gamma has parity: p(gamma(X_i, X_j)) = p(X_i) + p(X_j) + 1 (mod 2)

    # ---- EVEN-EVEN ----
    # gamma(H1, H2): Only N_eps = a1+a1- commuting with b1+b1- gives deformation.
    # Careful derivation from oscillator algebra:
    # [a1+a1-, b1+b1-]_deformed = kappa * (-gmm*o1 - gmp*o2 + gpm*o3 + gpp*o4)
    # H1 = N_eps + b1+b1-, H2 = -b1+b1- - 1/2
    # gamma(H1, H2) = -gamma(N_eps, b1+b1-) = gmm*o1 + gmp*o2 - gpm*o3 - gpp*o4
    gamma[0, 1, 4] = gmm;   gamma[0, 1, 5] = gmp
    gamma[0, 1, 6] = -gpm;  gamma[0, 1, 7] = -gpp

    # gamma(H1, Ep) = gamma(N_eps, (b1+)^2)
    # = -2*gmp*o1 + 2*gpp*o3
    gamma[0, 2, 4] = -2*gmp;  gamma[0, 2, 6] = 2*gpp

    # gamma(H1, Em) = gamma(N_eps, (b1-)^2)
    # = -2*gmm*o2 + 2*gpm*o4
    gamma[0, 3, 5] = -2*gmm;  gamma[0, 3, 7] = 2*gpm

    # H2, Ep, Em are purely bosonic: gamma = 0 for their mutual brackets.

    # ---- EVEN-ODD ----
    # gamma(H2, o_i): H2 = -b1+b1- - 1/2.
    # gamma(H2, o_i) = -gamma(b1+b1-, o_i) (mod scalar, the -1/2 scalar doesn't contribute).
    # gamma(b1+b1-, o1) = gpp*H2 - gpm*Ep (mod scalar), etc.
    gamma[1, 4, 1] = -gpp;  gamma[1, 4, 2] = gpm     # gamma(H2, o1) = -gpp*H2 + gpm*Ep
    gamma[1, 5, 1] = -gpm;  gamma[1, 5, 3] = gpp     # gamma(H2, o2) = -gpm*H2 + gpp*Em
    gamma[1, 6, 1] = -gmp;  gamma[1, 6, 2] = gmm     # gamma(H2, o3) = -gmp*H2 + gmm*Ep
    gamma[1, 7, 1] = -gmm;  gamma[1, 7, 3] = gmp     # gamma(H2, o4) = -gmm*H2 + gmp*Em

    # gamma(H1, o_i): H1 = N_eps + b1+b1-
    # gamma(N_eps, o_i) + gamma(b1+b1-, o_i)
    # Derived in detail from oscillator algebra (mod scalar K):
    gamma[0, 4, 0] = -gpp;  gamma[0, 4, 2] = -gpm     # gamma(H1, o1) = -gpp*H1 - gpm*Ep
    gamma[0, 5, 0] = -gpm;  gamma[0, 5, 3] = -gpp     # gamma(H1, o2) = -gpm*H1 - gpp*Em
    gamma[0, 6, 0] = -gmp;  gamma[0, 6, 2] = -gmm     # gamma(H1, o3) = -gmp*H1 - gmm*Ep
    gamma[0, 7, 0] = -gmm;  gamma[0, 7, 3] = -gmp     # gamma(H1, o4) = -gmm*H1 - gmp*Em

    # gamma(Ep, o_i):
    # [(b1+)^2, a1^sigma b1^s]: deformation from moving a1^sigma past (b1+)^2.
    # gamma(Ep, o1) = -2*gpp*Ep       (even output ✓)
    gamma[2, 4, 2] = -2*gpp
    # gamma(Ep, o2) = 2*gpp*H2        (mod scalar)
    gamma[2, 5, 1] = 2*gpp
    # gamma(Ep, o3) = -2*gmp*Ep
    gamma[2, 6, 2] = -2*gmp
    # gamma(Ep, o4) = 2*gmp*H2        (mod scalar)
    gamma[2, 7, 1] = 2*gmp

    # gamma(Em, o_i):
    gamma[3, 4, 1] = 2*gpm            # gamma(Em, o1) = 2*gpm*H2  (mod scalar)
    gamma[3, 5, 3] = -2*gpm           # gamma(Em, o2) = -2*gpm*Em
    gamma[3, 6, 1] = 2*gmm            # gamma(Em, o3) = 2*gmm*H2  (mod scalar)
    gamma[3, 7, 3] = -2*gmm           # gamma(Em, o4) = -2*gmm*Em

    # ---- ODD-ODD ----
    # {o_i, o_j} deformation: one b-a commutation per term.
    gamma[4, 4, 4] = 2*gpp            # {o1,o1} = 2*gpp*o1
    gamma[4, 5, 4] = gpm              # {o1,o2} = gpm*o1 + gpp*o2
    gamma[4, 5, 5] = gpp
    gamma[4, 6, 4] = gmp              # {o1,o3} = gmp*o1 + gpp*o3
    gamma[4, 6, 6] = gpp
    gamma[4, 7, 5] = gmp              # {o1,o4} = gmp*o2 + gpm*o3
    gamma[4, 7, 6] = gpm
    gamma[5, 5, 5] = 2*gpm            # {o2,o2} = 2*gpm*o2
    gamma[5, 6, 4] = gmm              # {o2,o3} = gmm*o1 + gpp*o4
    gamma[5, 6, 7] = gpp
    gamma[5, 7, 5] = gmm              # {o2,o4} = gmm*o2 + gpm*o4
    gamma[5, 7, 7] = gpm
    gamma[6, 6, 6] = 2*gmp            # {o3,o3} = 2*gmp*o3
    gamma[6, 7, 6] = gmm              # {o3,o4} = gmm*o3 + gmp*o4
    gamma[6, 7, 7] = gmp
    gamma[7, 7, 7] = 2*gmm            # {o4,o4} = 2*gmm*o4

    # Fill super-antisymmetry
    for i in range(dim):
        for j in range(i + 1, dim):
            sign = -(-1) ** (par[i] * par[j])
            gamma[j, i] = sign * gamma[i, j]

    return gamma


def compute_coboundary(sc, par, f_mat):
    """
    Compute (delta f)(X, Y) for all X, Y.
    (delta f)(X,Y) = (-1)^{p(X)} [X, f(Y)] - (-1)^{(p(X)+1)p(Y)} [Y, f(X)] - f([X,Y])
    """
    dim = len(par)
    delta = np.zeros((dim, dim, dim))

    for i in range(dim):
        for j in range(dim):
            pi, pj = par[i], par[j]

            # f(Y) = f_mat[j]
            fY = f_mat[j]
            # [X_i, f(Y)] = sum_k fY[k] * [X_i, X_k]
            br_X_fY = np.zeros(dim)
            for k in range(dim):
                if abs(fY[k]) > 1e-15:
                    br_X_fY += fY[k] * sc[i, k]

            # f(X) = f_mat[i]
            fX = f_mat[i]
            br_Y_fX = np.zeros(dim)
            for k in range(dim):
                if abs(fX[k]) > 1e-15:
                    br_Y_fX += fX[k] * sc[j, k]

            # f([X,Y]) = sum_k sc[i,j,k] * f_mat[k]
            f_brXY = np.zeros(dim)
            for k in range(dim):
                if abs(sc[i, j, k]) > 1e-15:
                    f_brXY += sc[i, j, k] * f_mat[k]

            delta[i, j] = ((-1)**pi) * br_X_fY \
                         - ((-1)**((pi+1)*pj)) * br_Y_fX \
                         - f_brXY

    return delta


def solve_triviality(sc, par, gamma):
    """
    Solve gamma = delta(f) for the odd linear map f.
    Returns f, max residual, and diagnostic info.
    """
    dim = len(par)

    # f-variables: (row, col) with par[row] + par[col] odd
    f_vars = [(r, c) for r in range(dim) for c in range(dim)
              if (par[r] + par[c]) % 2 == 1]
    n_vars = len(f_vars)

    # Build linear system A * x = b
    rows_A = []
    b_vec = []

    for i in range(dim):
        for j in range(dim):
            for m in range(dim):
                # parity check
                expected_par = (par[i] + par[j] + 1) % 2
                if par[m] != expected_par:
                    continue

                pi, pj = par[i], par[j]
                coeff = np.zeros(n_vars)

                for vi, (r, c) in enumerate(f_vars):
                    # Term 1: (-1)^{pi} * [X_i, f(X_j)]_m
                    # f(X_j) has component x_vi in direction c when r == j
                    if r == j:
                        coeff[vi] += ((-1)**pi) * sc[i, c, m]

                    # Term 2: -(-1)^{(pi+1)*pj} * [X_j, f(X_i)]_m
                    if r == i:
                        coeff[vi] += -((-1)**((pi+1)*pj)) * sc[j, c, m]

                    # Term 3: -f([X_i, X_j])_m = -sum_l sc[i,j,l] * f[l,m]
                    # contributes when r = l (some l with sc[i,j,l] != 0) and c = m
                    if c == m:
                        coeff[vi] += -sc[i, j, r]

                rows_A.append(coeff)
                b_vec.append(gamma[i, j, m])

    A = np.array(rows_A)
    b = np.array(b_vec)

    # Solve
    x, residuals, rank, sv = np.linalg.lstsq(A, b, rcond=None)
    resid = np.max(np.abs(A @ x - b))

    # Reconstruct f
    f_mat = np.zeros((dim, dim))
    for vi, (r, c) in enumerate(f_vars):
        f_mat[r, c] = x[vi]

    return f_mat, resid, n_vars, A.shape[0], rank


def analyze_coboundary_map(sc, par):
    """Analyze the image of the coboundary map and check if gb-space lies in it."""
    dim = len(par)
    f_vars = [(r, c) for r in range(dim) for c in range(dim)
              if (par[r] + par[c]) % 2 == 1]
    n_vars = len(f_vars)

    rows_A = []
    output_slots = []

    for i in range(dim):
        for j in range(dim):
            for m in range(dim):
                expected_par = (par[i] + par[j] + 1) % 2
                if par[m] != expected_par:
                    continue

                pi, pj = par[i], par[j]
                coeff = np.zeros(n_vars)
                for vi, (r, c) in enumerate(f_vars):
                    if r == j:
                        coeff[vi] += ((-1)**pi) * sc[i, c, m]
                    if r == i:
                        coeff[vi] += -((-1)**((pi+1)*pj)) * sc[j, c, m]
                    if c == m:
                        coeff[vi] += -sc[i, j, r]
                rows_A.append(coeff)
                output_slots.append((i, j, m))

    A = np.array(rows_A)
    rank_A = np.linalg.matrix_rank(A, tol=1e-10)

    # Gamma vectors for each gb basis element
    gb_basis = [[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1]]
    gamma_vecs = []
    for gb in gb_basis:
        g = compute_gamma(sc, par, gb)
        gvec = []
        for (i, j, m) in output_slots:
            gvec.append(g[i, j, m])
        gamma_vecs.append(gvec)

    G = np.array(gamma_vecs).T  # shape (n_eqs, 4)
    AG = np.hstack([A, G])
    rank_AG = np.linalg.matrix_rank(AG, tol=1e-10)

    in_image = (rank_AG == rank_A)

    return {
        "n_vars": n_vars,
        "n_eqs": len(rows_A),
        "rank_delta": rank_A,
        "rank_augmented": rank_AG,
        "gb_dim": 4,
        "all_trivial": in_image,
    }


def main():
    labels, par, sc = build_osp22()
    dim = 8

    print("=" * 70)
    print("TRIVIALITY ANALYSIS FOR C(n+1) = osp(2|2n)")
    print("Focus: n=1, i.e., C(2) = osp(2|2)")
    print("=" * 70)

    print(f"\nBasis: {labels}")
    print(f"Parities: {list(par)}")

    # Jacobi check
    print("\n--- Super Jacobi Identity Verification ---")
    max_err, worst = check_jacobi(sc, par)
    print(f"Max violation: {max_err:.2e}")
    if worst:
        print(f"Worst triple: ({labels[worst[0]]}, {labels[worst[1]]}, {labels[worst[2]]})")

    if max_err > 1e-10:
        print("WARNING: Jacobi identity fails! Structure constants need correction.")
        # Debug the worst triple
        i, j, k = worst
        print(f"\nDebugging Jacobi for ({labels[i]}, {labels[j]}, {labels[k]}):")
        inner = sc[j, k]
        nz = [(l, inner[l]) for l in range(dim) if abs(inner[l]) > 1e-15]
        print(f"  [{labels[j]}, {labels[k]}] = {' + '.join(f'{v}*{labels[l]}' for l, v in nz) or '0'}")
        inner = sc[k, i]
        nz = [(l, inner[l]) for l in range(dim) if abs(inner[l]) > 1e-15]
        print(f"  [{labels[k]}, {labels[i]}] = {' + '.join(f'{v}*{labels[l]}' for l, v in nz) or '0'}")
        inner = sc[i, j]
        nz = [(l, inner[l]) for l in range(dim) if abs(inner[l]) > 1e-15]
        print(f"  [{labels[i]}, {labels[j]}] = {' + '.join(f'{v}*{labels[l]}' for l, v in nz) or '0'}")

    # Test individual brackets
    print("\n--- Key Bracket Verification ---")
    tests = [
        (4, 7, "o1, o4", {0: -1, 1: -2}),  # {o1, o4} = -H1 - 2H2
        (5, 6, "o2, o3", {0: 1}),            # {o2, o3} = H1
        (4, 6, "o1, o3", {2: 1}),            # {o1, o3} = Ep
        (5, 7, "o2, o4", {3: 1}),            # {o2, o4} = Em
    ]
    for i, j, desc, expected in tests:
        actual = {k: sc[i, j, k] for k in range(dim) if abs(sc[i, j, k]) > 1e-15}
        match = all(abs(actual.get(k, 0) - v) < 1e-15 for k, v in expected.items())
        match = match and len(actual) == len(expected)
        print(f"  [{desc}] = {actual}, expected {expected}: {'✓' if match else '✗'}")

    # Coboundary analysis
    print("\n--- Coboundary Map Analysis ---")
    info = analyze_coboundary_map(sc, par)
    print(f"  f-parameter dim: {info['n_vars']}")
    print(f"  Cochain equations: {info['n_eqs']}")
    print(f"  rank(delta): {info['rank_delta']}")
    print(f"  rank([delta | gamma_basis]): {info['rank_augmented']}")
    print(f"  gb-space dim: {info['gb_dim']}")
    print(f"  All gamma_gb in Im(delta): {info['all_trivial']}")

    # Individual test cases
    print("\n--- Individual gb Parameter Tests ---")
    test_cases = [
        ("unit", [1.0, 1.0, 1.0, 1.0]),
        ("random", [0.3, -0.7, 1.2, -0.5]),
        ("single_pp", [1.0, 0.0, 0.0, 0.0]),
        ("single_pm", [0.0, 1.0, 0.0, 0.0]),
        ("single_mp", [0.0, 0.0, 1.0, 0.0]),
        ("single_mm", [0.0, 0.0, 0.0, 1.0]),
        ("zero", [0.0, 0.0, 0.0, 0.0]),
    ]

    results = {}
    for name, gb in test_cases:
        gamma = compute_gamma(sc, par, gb)
        f_mat, resid, nv, ne, rk = solve_triviality(sc, par, gamma)

        # Verify
        delta = compute_coboundary(sc, par, f_mat)
        verify = np.max(np.abs(gamma - delta))

        trivial = resid < 1e-10
        print(f"  {name:12s}: gb={gb}, residual={resid:.2e}, verify={verify:.2e} -> "
              f"{'TRIVIAL' if trivial else 'NON-TRIVIAL'}")

        results[name] = {
            "gb": gb,
            "residual": float(resid),
            "trivial": bool(trivial),
        }

        if trivial and name == "single_pp":
            print(f"    Trivializing f (non-zero entries):")
            for r in range(dim):
                for c in range(dim):
                    if abs(f_mat[r, c]) > 1e-10:
                        print(f"      f({labels[r]}) += {f_mat[r,c]:+.6f} * {labels[c]}")

    # Determine conclusion
    trivial_count = sum(1 for r in results.values() if r["trivial"])
    nontrivial_count = sum(1 for r in results.values() if not r["trivial"] and r["gb"] != [0]*4)

    print("\n" + "=" * 70)
    print("CONCLUSION")
    print("=" * 70)

    if info["all_trivial"]:
        conclusion = "TRIVIAL"
        print("The entire 4-dimensional gb-parameter space lies in the image of")
        print("the coboundary map delta. Therefore:")
        print("")
        print("  THEOREM: For C(2) = osp(2|2), every inhomogeneous deformation")
        print("  gamma_gb is a coboundary (trivial), for ALL gb parameters.")
    else:
        conclusion = "NON-TRIVIAL"
        extra_dim = info["rank_augmented"] - info["rank_delta"]
        print(f"The gb-space has {extra_dim} direction(s) NOT in Im(delta).")
        print(f"Therefore, there exist NON-TRIVIAL deformations.")
        print(f"The obstruction space has dimension {extra_dim}.")

        # Find which gb directions are in the image and which are not
        # This tells us the triviality conditions.
        print("\n--- Triviality Conditions ---")
        # Check each single gb parameter
        for name, gb in test_cases:
            if gb == [0]*4:
                continue
            gamma = compute_gamma(sc, par, gb)
            _, resid, _, _, _ = solve_triviality(sc, par, gamma)
            status = "TRIVIAL" if resid < 1e-10 else "NON-TRIVIAL"
            print(f"  gb = {gb}: {status} (residual = {resid:.2e})")

        # Check which LINEAR COMBINATIONS of gb are trivial
        print("\n  Searching for trivial subspace of gb parameters...")
        gb_basis_vecs = [[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1]]
        for a in np.linspace(-2, 2, 9):
            for b in np.linspace(-2, 2, 9):
                if abs(a) < 1e-10 and abs(b) < 1e-10:
                    continue
                gb = [a, b, 0, 0]
                gamma = compute_gamma(sc, par, gb)
                _, resid, _, _, _ = solve_triviality(sc, par, gamma)
                if resid < 1e-10:
                    print(f"  TRIVIAL: gb = {gb}")

    # Export
    artifacts = {
        "algebra": "C(2) = osp(2|2)",
        "n": 1,
        "basis": labels,
        "parities": list(par),
        "structure_constants_nonzero": {},
        "jacobi_max_violation": float(max_err),
        "coboundary_analysis": {k: (bool(v) if isinstance(v, (bool, np.bool_)) else int(v) if isinstance(v, (int, np.integer)) else v) for k, v in info.items()},
        "conclusion": conclusion,
        "test_results": {k: {kk: (bool(vv) if isinstance(vv, (bool, np.bool_)) else vv) for kk, vv in v.items()} for k, v in results.items()},
    }

    for i in range(dim):
        for j in range(dim):
            for k in range(dim):
                if abs(sc[i, j, k]) > 1e-15:
                    key = f"[{labels[i]},{labels[j]}]->{labels[k]}"
                    artifacts["structure_constants_nonzero"][key] = float(sc[i, j, k])

    class NumpyEncoder(json.JSONEncoder):
        def default(self, obj):
            if isinstance(obj, (np.integer,)):
                return int(obj)
            if isinstance(obj, (np.floating,)):
                return float(obj)
            if isinstance(obj, (np.bool_,)):
                return bool(obj)
            if isinstance(obj, np.ndarray):
                return obj.tolist()
            return super().default(obj)

    with open("verification_artifacts.json", "w") as fout:
        json.dump(artifacts, fout, indent=2, cls=NumpyEncoder)
    print("\nArtifacts written to verification_artifacts.json")

    return conclusion, info, results


if __name__ == "__main__":
    main()
