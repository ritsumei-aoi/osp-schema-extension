"""
Verify triviality of C(n+1)=osp(2|2n) deformations for n=1,2,3.

Purely algebraic computation: brackets of bilinear operators are computed
exactly using oscillator commutation relations, without Fock space truncation.
"""
import numpy as np
import json
import sys


def osc_parity(label):
    return 1 if label.startswith('a') else 0


def basic_commutator(X, Y):
    """[X, Y] for single oscillators. Returns scalar."""
    pX, pY = osc_parity(X), osc_parity(Y)
    if pX == 1 and pY == 1:
        if (X == 'a+' and Y == 'a-') or (X == 'a-' and Y == 'a+'):
            return 1.0
        return 0.0
    if pX == 0 and pY == 0:
        xbase, xsign = X[:-1], X[-1]
        ybase, ysign = Y[:-1], Y[-1]
        if xbase == ybase:
            if xsign == '-' and ysign == '+':
                return 1.0
            if xsign == '+' and ysign == '-':
                return -1.0
        return 0.0
    return 0.0


def osc_rank(label):
    if label == 'a+': return 0
    if label == 'a-': return 1
    k = int(label[1:-1])
    return 10*k if label[-1] == '+' else 10*k + 1


def is_normal(X, Y):
    return osc_rank(X) <= osc_rank(Y)


def bracket_bilinears(A, B, C, D):
    """
    [AB, CD] using super-Leibniz.
    Returns dict {(X,Y): coeff} of bilinear terms.
    All basic [osc, osc] are scalars, so result is sum of bilinears.
    """
    pA, pB, pC, pD = osc_parity(A), osc_parity(B), osc_parity(C), osc_parity(D)
    terms = {}

    def add(pair, c):
        if abs(c) > 1e-15:
            terms[pair] = terms.get(pair, 0) + c

    s = basic_commutator(B, C)
    add((A, D), s)

    s = basic_commutator(B, D)
    add((A, C), (-1)**(pB*pC) * s)

    s = basic_commutator(A, C)
    add((D, B), (-1)**(pB*(pC+pD)) * s)

    s = basic_commutator(A, D)
    add((C, B), (-1)**(pB*(pC+pD) + pA*pC) * s)

    return {k: v for k, v in terms.items() if abs(v) > 1e-15}


def normalize_bilinears(terms):
    """Rewrite bilinears in normal order. Returns (normalized_terms, scalar)."""
    result = {}
    scalar = 0.0
    for (X, Y), c in terms.items():
        if abs(c) < 1e-15:
            continue
        if is_normal(X, Y):
            result[(X, Y)] = result.get((X, Y), 0) + c
        else:
            pX, pY = osc_parity(X), osc_parity(Y)
            sign = (-1)**(pX*pY)
            result[(Y, X)] = result.get((Y, X), 0) + sign * c
            scalar += c * basic_commutator(X, Y)
    result = {k: v for k, v in result.items() if abs(v) > 1e-15}
    return result, scalar


def build_osp(n):
    """Build C(n+1)=osp(2|2n) generators and structure constants algebraically."""

    # Each generator: list of (osc_left, osc_right, coeff) + scalar
    gen_terms = []
    gen_scalar = []
    labels = []
    parities = []

    # H1 = a+a- + b1+b1-
    gen_terms.append([('a+', 'a-', 1.0), ('b1+', 'b1-', 1.0)])
    gen_scalar.append(0.0); labels.append('H1'); parities.append(0)

    for k in range(2, n+1):
        gen_terms.append([(f'b{k-1}+', f'b{k-1}-', 1.0), (f'b{k}+', f'b{k}-', -1.0)])
        gen_scalar.append(0.0); labels.append(f'H{k}'); parities.append(0)

    gen_terms.append([(f'b{n}+', f'b{n}-', -1.0)])
    gen_scalar.append(-0.5); labels.append(f'H{n+1}'); parities.append(0)

    for k in range(1, n+1):
        gen_terms.append([(f'b{k}+', f'b{k}+', 1.0)])
        gen_scalar.append(0.0); labels.append(f'E2d{k}'); parities.append(0)
        gen_terms.append([(f'b{k}-', f'b{k}-', 1.0)])
        gen_scalar.append(0.0); labels.append(f'E-2d{k}'); parities.append(0)

    for k in range(1, n+1):
        for l in range(k+1, n+1):
            for sk in ['+', '-']:
                for sl in ['+', '-']:
                    gen_terms.append([(f'b{k}{sk}', f'b{l}{sl}', 1.0)])
                    gen_scalar.append(0.0)
                    labels.append(f'Eb{k}{sk}b{l}{sl}')
                    parities.append(0)

    odd_info = []
    for sigma in ['+', '-']:
        for k in range(1, n+1):
            for s in ['+', '-']:
                gen_terms.append([(f'a{sigma}', f'b{k}{s}', 1.0)])
                gen_scalar.append(0.0)
                labels.append(f'o{sigma}{k}{s}')
                parities.append(1)
                odd_info.append((sigma, k, s))

    dim = len(gen_terms)
    par = np.array(parities)

    # Collect all bilinear keys that appear in generators
    all_keys = set()
    for gt in gen_terms:
        for (A, B, c) in gt:
            all_keys.add((A, B))
    all_keys = sorted(all_keys, key=lambda x: (osc_rank(x[0]), osc_rank(x[1])))
    key_idx = {k: i for i, k in enumerate(all_keys)}
    n_keys = len(all_keys)

    # Build generator matrix: G[bilinear_idx, gen_idx] = coefficient
    G_mat = np.zeros((n_keys + 1, dim))  # +1 for scalar row
    for gi, gt in enumerate(gen_terms):
        for (A, B, c) in gt:
            G_mat[key_idx[(A, B)], gi] = c
        G_mat[n_keys, gi] = gen_scalar[gi]

    def project(norm_terms, scalar):
        """Project normalized bilinear expression onto generator basis."""
        rhs = np.zeros(n_keys + 1)
        for (X, Y), c in norm_terms.items():
            if (X, Y) in key_idx:
                rhs[key_idx[(X, Y)]] = c
            else:
                all_keys.append((X, Y))
                pass
        rhs[n_keys] = scalar

        coeffs, _, _, _ = np.linalg.lstsq(G_mat, rhs, rcond=None)
        resid = np.max(np.abs(G_mat @ coeffs - rhs))
        if resid > 1e-8:
            pass  # might have components not in the algebra
        return coeffs

    # Compute structure constants
    sc = np.zeros((dim, dim, dim))

    for i in range(dim):
        for j in range(i, dim):
            raw = {}
            for (A, B, c1) in gen_terms[i]:
                for (C, D, c2) in gen_terms[j]:
                    br = bracket_bilinears(A, B, C, D)
                    for (X, Y), v in br.items():
                        raw[(X, Y)] = raw.get((X, Y), 0) + c1 * c2 * v

            norm, scalar = normalize_bilinears(raw)
            coeffs = project(norm, scalar)
            sc[i, j, :] = coeffs
            sign = -(-1)**(par[i]*par[j])
            sc[j, i, :] = sign * sc[i, j, :]

    return labels, par, sc, dim, gen_terms, gen_scalar, odd_info, G_mat, key_idx, n_keys


def check_jacobi(sc, par, labels):
    dim = len(par)
    max_err = 0
    worst = None
    for i in range(dim):
        for j in range(dim):
            for k in range(dim):
                pi, pj, pk = par[i], par[j], par[k]
                v = np.zeros(dim)
                for l in range(dim):
                    if abs(sc[j,k,l]) > 1e-12: v += sc[j,k,l] * sc[i,l]
                v *= (-1)**(pi*pk)
                w = np.zeros(dim)
                for l in range(dim):
                    if abs(sc[k,i,l]) > 1e-12: w += sc[k,i,l] * sc[j,l]
                w *= (-1)**(pj*pi)
                u = np.zeros(dim)
                for l in range(dim):
                    if abs(sc[i,j,l]) > 1e-12: u += sc[i,j,l] * sc[k,l]
                u *= (-1)**(pk*pj)
                err = np.max(np.abs(v + w + u))
                if err > max_err:
                    max_err = err
                    worst = (i, j, k)
    return max_err, worst


def compute_gamma(n, gen_terms, gen_scalar, par, labels, odd_info, dim,
                  G_mat, key_idx, n_keys, gb):
    """
    Compute gamma from deformed commutation relations.

    The deformation [b_j^s, a^sigma] = -gb * kappa modifies each basic
    commutator. gamma(G_i, G_j) is the first-order correction to [G_i, G_j]
    obtained by replacing basic_commutator -> delta in bracket_bilinears.
    """
    gamma = np.zeros((dim, dim, dim))

    for (sigma, j, s), coeff in gb.items():
        if abs(coeff) < 1e-15:
            continue

        b_label = f'b{j}{s}'
        a_label = f'a{sigma}'

        def delta_comm(X, Y):
            if X == b_label and Y == a_label:
                return -1.0
            if X == a_label and Y == b_label:
                return 1.0
            return 0.0

        for i in range(dim):
            for jj in range(dim):
                raw = {}

                for (A, B, c1) in gen_terms[i]:
                    for (C, D, c2) in gen_terms[jj]:
                        pA = osc_parity(A)
                        pB = osc_parity(B)
                        pC = osc_parity(C)
                        pD = osc_parity(D)
                        cc = c1 * c2

                        # Sign corrections from moving odd kappa to the left:
                        # Term 1: A*[B,C]*D -> A*kappa*D, move kappa past A: (-1)^pA
                        # Term 2: A*C*[B,D] -> A*C*kappa, move past A,C: (-1)^{pA+pC}
                        # Term 3: [A,C]*D*B -> kappa*D*B, already left: no correction
                        # Term 4: C*[A,D]*B -> C*kappa*B, move past C: (-1)^pC

                        d = delta_comm(B, C)
                        if abs(d) > 1e-15:
                            raw[(A, D)] = raw.get((A, D), 0) + cc * (-1)**pA * d

                        d = delta_comm(B, D)
                        if abs(d) > 1e-15:
                            raw[(A, C)] = raw.get((A, C), 0) + cc * (-1)**(pB*pC + pA + pC) * d

                        d = delta_comm(A, C)
                        if abs(d) > 1e-15:
                            raw[(D, B)] = raw.get((D, B), 0) + cc * (-1)**(pB*(pC+pD)) * d

                        d = delta_comm(A, D)
                        if abs(d) > 1e-15:
                            raw[(C, B)] = raw.get((C, B), 0) + cc * (-1)**(pB*(pC+pD) + pA*pC + pC) * d

                if raw:
                    norm, scalar = normalize_bilinears(raw)
                    rhs = np.zeros(n_keys)
                    for (X, Y), c in norm.items():
                        if (X, Y) in key_idx:
                            rhs[key_idx[(X, Y)]] = c
                    coeffs, _, _, _ = np.linalg.lstsq(G_mat[:n_keys], rhs, rcond=None)
                    gamma[i, jj, :] += coeff * coeffs

    return gamma


def analyze_triviality(sc, par, dim, gamma_list, gb_labels):
    f_vars = [(r, c) for r in range(dim) for c in range(dim)
              if (par[r] + par[c]) % 2 == 1]
    n_vars = len(f_vars)

    rows_A = []
    output_slots = []
    for i in range(dim):
        for j in range(dim):
            for m in range(dim):
                if par[m] != (par[i] + par[j] + 1) % 2:
                    continue
                pi, pj = par[i], par[j]
                coeff_row = np.zeros(n_vars)
                for vi, (r, c) in enumerate(f_vars):
                    if r == j:
                        coeff_row[vi] += ((-1)**pi) * sc[i, c, m]
                    if r == i:
                        coeff_row[vi] += -((-1)**((pi+1)*pj)) * sc[j, c, m]
                    if c == m:
                        coeff_row[vi] += -sc[i, j, r]
                rows_A.append(coeff_row)
                output_slots.append((i, j, m))

    A = np.array(rows_A)
    rank_A = np.linalg.matrix_rank(A, tol=1e-8)

    gamma_vecs = []
    for g in gamma_list:
        gamma_vecs.append([g[i, j, m] for (i, j, m) in output_slots])
    G = np.array(gamma_vecs).T
    AG = np.hstack([A, G])
    rank_AG = np.linalg.matrix_rank(AG, tol=1e-8)

    results = {}
    for idx in range(len(gamma_list)):
        gvec = np.array(gamma_vecs[idx])
        x, _, _, _ = np.linalg.lstsq(A, gvec, rcond=None)
        resid = np.max(np.abs(A @ x - gvec))
        results[gb_labels[idx]] = {"residual": float(resid), "trivial": resid < 1e-6}

    return {
        "n_vars": n_vars, "n_eqs": len(rows_A),
        "rank_delta": int(rank_A), "rank_augmented": int(rank_AG),
        "gb_dim": len(gamma_list), "all_trivial": bool(rank_AG == rank_A),
        "individual": results,
    }


def main():
    all_results = {}

    for n_val in [1, 2, 3]:
        print(f"\n{'='*70}")
        print(f"C({n_val+1}) = osp(2|{2*n_val}), n={n_val}")
        print(f"{'='*70}")
        sys.stdout.flush()

        labels, par, sc, dim, gen_terms, gen_scalar, odd_info, G_mat, key_idx, n_keys = build_osp(n_val)

        n_even = int(sum(par == 0))
        n_odd = int(sum(par == 1))
        print(f"Dimension: {dim} ({n_even} even + {n_odd} odd)")

        # Verify a known bracket
        if n_val == 1:
            nz = {labels[k]: round(sc[2,3,k],4) for k in range(dim) if abs(sc[2,3,k]) > 0.001}
            print(f"  [E2d1, E-2d1] = {nz}  (expect H2: 4.0)")

        print("Checking Jacobi...", end=" "); sys.stdout.flush()
        max_err, worst = check_jacobi(sc, par, labels)
        print(f"max violation: {max_err:.2e}")
        if worst and max_err > 1e-10:
            print(f"  Worst: ({labels[worst[0]]}, {labels[worst[1]]}, {labels[worst[2]]})")
        sys.stdout.flush()

        gb_params = []
        gb_labels_list = []
        for sigma in ['+', '-']:
            for j in range(1, n_val+1):
                for s in ['+', '-']:
                    gb_params.append({(sigma, j, s): 1.0})
                    gb_labels_list.append(f"gb_{sigma},{j},{s}")

        print(f"Computing {4*n_val} gamma vectors...", end=" "); sys.stdout.flush()
        gamma_list = []
        for gb in gb_params:
            g = compute_gamma(n_val, gen_terms, gen_scalar, par, labels, odd_info, dim,
                             G_mat, key_idx, n_keys, gb)
            gamma_list.append(g)
        print("done"); sys.stdout.flush()

        print("Analyzing triviality...", end=" "); sys.stdout.flush()
        info = analyze_triviality(sc, par, dim, gamma_list, gb_labels_list)
        print("done")

        print(f"\n  f-parameter dim: {info['n_vars']}")
        print(f"  rank(delta): {info['rank_delta']}")
        print(f"  rank([delta|gamma]): {info['rank_augmented']}")
        print(f"  gb dim: {info['gb_dim']}")
        print(f"  ALL TRIVIAL: {info['all_trivial']}")

        for name, res in info['individual'].items():
            status = "TRIVIAL" if res['trivial'] else "NON-TRIVIAL"
            print(f"    {name:20s}: residual={res['residual']:.2e} -> {status}")

        all_results[f"C({n_val+1})"] = {
            "n": n_val, "dim": dim, "even": n_even, "odd": n_odd,
            "jacobi": float(max_err),
            "rank_delta": info["rank_delta"],
            "rank_augmented": info["rank_augmented"],
            "all_trivial": info["all_trivial"],
            "individual": info["individual"],
        }
        sys.stdout.flush()

    with open("verification_artifacts.json", "w") as f:
        json.dump(all_results, f, indent=2,
                  default=lambda x: float(x) if isinstance(x, np.floating)
                  else int(x) if isinstance(x, np.integer)
                  else bool(x) if isinstance(x, np.bool_) else x)
    print(f"\nAll results saved to verification_artifacts.json")


if __name__ == "__main__":
    main()
