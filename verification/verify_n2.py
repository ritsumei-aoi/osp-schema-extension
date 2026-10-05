"""
Explicit verification for C(3) = osp(2|4), n=2.
Uses trace-based structure constant computation to avoid scalar decomposition issues.
"""
import numpy as np
import json


def build_fock(n_bos, n_max):
    dim_bos = n_max ** n_bos
    dim = 2 * dim_bos

    def idx(nf, nb_tuple):
        bi = 0
        for k in range(n_bos):
            bi = bi * n_max + nb_tuple[k]
        return nf * dim_bos + bi

    def nb_from_bi(bi):
        t = []
        for k in range(n_bos - 1, -1, -1):
            t.append(bi % n_max)
            bi //= n_max
        return tuple(reversed(t))

    ap = np.zeros((dim, dim))
    am = np.zeros((dim, dim))
    for nf in [0, 1]:
        for bi in range(dim_bos):
            nb = nb_from_bi(bi)
            s = idx(nf, nb)
            if nf == 0:
                ap[idx(1, nb), s] = 1.0
            if nf == 1:
                am[idx(0, nb), s] = 1.0

    bp, bm = [], []
    for j in range(n_bos):
        bpj = np.zeros((dim, dim))
        bmj = np.zeros((dim, dim))
        for nf in [0, 1]:
            for bi in range(dim_bos):
                nb = list(nb_from_bi(bi))
                s = idx(nf, tuple(nb))
                if nb[j] + 1 < n_max:
                    nb2 = list(nb); nb2[j] += 1
                    bpj[idx(nf, tuple(nb2)), s] = np.sqrt(nb[j] + 1)
                if nb[j] > 0:
                    nb2 = list(nb); nb2[j] -= 1
                    bmj[idx(nf, tuple(nb2)), s] = np.sqrt(nb[j])
        bp.append(bpj)
        bm.append(bmj)

    return ap, am, bp, bm, np.eye(dim), dim


def sb(A, pA, B, pB):
    return A @ B - ((-1) ** (pA * pB)) * B @ A


def trace_decompose(M, basis_mats, I, dim):
    """Decompose M = sum c_k Z_k + scalar*I using trace inner product."""
    n = len(basis_mats)
    coeffs = np.zeros(n)
    norms = np.zeros(n)

    for k in range(n):
        norms[k] = np.trace(basis_mats[k].T @ basis_mats[k])

    aug = basis_mats + [I]
    aug_norms = [np.trace(z.T @ z) for z in aug]

    G = np.zeros((n + 1, n + 1))
    for i in range(n + 1):
        for j in range(n + 1):
            G[i, j] = np.trace(aug[i].T @ aug[j])

    rhs = np.array([np.trace(aug[k].T @ M) for k in range(n + 1)])

    c = np.linalg.solve(G, rhs)
    err = np.max(np.abs(M - sum(c[k] * aug[k] for k in range(n + 1))))
    return c[:n], c[n], err


def main():
    n = 2
    n_max = 6
    print(f"C({n+1}) = osp(2|{2*n}), n={n}, n_max={n_max}")

    ap, am, bp, bm, I, dim = build_fock(n, n_max)
    print(f"Fock dim: {dim}")

    # Build generators
    gens = []
    Nf = ap @ am

    H1 = Nf + bp[0] @ bm[0]
    gens.append(('H1', H1, 0))
    H2 = bp[0] @ bm[0] - bp[1] @ bm[1]
    gens.append(('H2', H2, 0))
    H3 = -bp[1] @ bm[1] - 0.5 * I
    gens.append(('H3', H3, 0))

    for k in range(n):
        gens.append((f'E2d{k+1}', 0.5 * bp[k] @ bp[k], 0))
        gens.append((f'E-2d{k+1}', 0.5 * bm[k] @ bm[k], 0))

    for k in range(n):
        for l in range(k + 1, n):
            gens.append((f'Ed{k+1}+d{l+1}', bp[k] @ bp[l], 0))
            gens.append((f'E-d{k+1}-d{l+1}', bm[k] @ bm[l], 0))
            gens.append((f'Ed{k+1}-d{l+1}', bp[k] @ bm[l], 0))
            gens.append((f'E-d{k+1}+d{l+1}', bp[l] @ bm[k], 0))

    for k in range(n):
        gens.append((f'o_e+d{k+1}', ap @ bp[k], 1))
        gens.append((f'o_e-d{k+1}', ap @ bm[k], 1))
        gens.append((f'o_-e+d{k+1}', am @ bp[k], 1))
        gens.append((f'o_-e-d{k+1}', am @ bm[k], 1))

    names = [g[0] for g in gens]
    mats = [g[1] for g in gens]
    pars = [g[2] for g in gens]
    ng = len(gens)
    print(f"Generators: {ng} ({sum(1 for p in pars if p==0)} even, {sum(1 for p in pars if p==1)} odd)")

    # Check independence
    V = np.column_stack([m.flatten() for m in mats])
    rank = np.linalg.matrix_rank(V, tol=1e-6)
    print(f"Rank: {rank}")

    if rank < ng:
        print(f"Dependent! Selecting {rank} independent generators...")
        sel = []
        cr = 0
        for idx in range(ng):
            test = V[:, sel + [idx]] if sel else V[:, [idx]]
            r = np.linalg.matrix_rank(test, tol=1e-6)
            if r > cr:
                sel.append(idx)
                cr = r
            if cr == rank:
                break
        gens = [gens[i] for i in sel]
        names = [g[0] for g in gens]
        mats = [g[1] for g in gens]
        pars = [g[2] for g in gens]
        ng = len(gens)
        print(f"Selected {ng}: {names}")

    exp = 2*n*n + n + 1 + 4*n
    print(f"Expected total: {exp}")
    assert ng == exp, f"Got {ng}, expected {exp}"

    # Compute structure constants using trace decomposition
    print("\nComputing structure constants...")
    sc = {}
    for i in range(ng):
        for j in range(ng):
            sc[(i, j)] = {}

    max_err = 0
    for i in range(ng):
        for j in range(i, ng):
            br = sb(mats[i], pars[i], mats[j], pars[j])
            c, s, err = trace_decompose(br, mats, I, dim)
            max_err = max(max_err, err)

            d = {}
            for k in range(ng):
                val = round(c[k] * 4) / 4
                if abs(val) > 1e-6:
                    d[k] = val
            sc[(i, j)] = d
            sign = -((-1) ** (pars[i] * pars[j]))
            sc[(j, i)] = {k: sign * v for k, v in d.items()}

    print(f"Max decomposition error: {max_err:.2e}")

    # Compute gamma using corrected finite-difference approach
    print("\nComputing gamma_gb...")

    # Use corrected approach: perturb the oscillator b -> b + eps * a^{-sigma},
    # but keep the ORIGINAL generators. Compute the deformed bracket of original
    # generators by using the deformed product rule.
    #
    # Key insight: instead of building deformed generators, we compute the
    # deformed bracket by using the formula:
    # [X, Y]_def = X_def Y_def +/- Y_def X_def
    # where X_def = original X computed with deformed oscillator products.
    #
    # But this is exactly what we get by using the deformed oscillator matrices
    # to build the generators and then computing brackets!
    #
    # The issue before was that the generators CHANGE when we deform oscillators.
    # So [X_def, Y_def] is NOT the deformed bracket of X, Y.
    # It's the bracket of X_def, Y_def in the standard algebra.
    #
    # To get the DEFORMED bracket of the ORIGINAL generators:
    # [X, Y]_def = deformed product X*Y - (+/-) deformed product Y*X
    # where the "deformed product" uses the deformed oscillator relations.
    #
    # CORRECT APPROACH: use the undeformed generators, but compute their bracket
    # using a "deformed super-commutator" that accounts for the changed [b,a] relation.
    #
    # Implementation: augment the Hilbert space with a "kappa" flag.
    # States: |nf, nb1, ..., nbn, kappa_flag>  where kappa_flag in {0,1}
    # Operators in the deformed algebra:
    #   a^sigma_def = a^sigma (same as before)
    #   b^s_def = b^s + kappa_flag * gb * a^{-sigma}  ... this is still problematic.
    #
    # SIMPLEST CORRECT APPROACH:
    # Represent the deformed algebra on V tensor C[kappa]/(kappa^2)
    # Each operator is a 2x2 block matrix: ((M, M'), (0, M)) where M' is the kappa-part.
    # Products: ((A,A'),(0,A)) @ ((B,B'),(0,B)) = ((AB, AB'+A'B), (0, AB))
    #
    # Standard oscillators: a = ((a_mat, 0), (0, a_mat)), b = ((b_mat, 0), (0, b_mat))
    # Deformation: for specific (sigma, j, s), add kappa correction.
    # b_j^s in deformed algebra: ((b_mat, -gb*I), (0, b_mat))
    # Wait, that would mean b_j^s = b_mat + kappa*(-gb*I).
    # Then [b_j^s, a^sigma] = b·a - a·b + kappa*(-gb·a - a*0) = 0 + kappa*(-gb·a)
    # That's not right either.
    #
    # Actually: the deformation says [b, a] = -gb*kappa*I in the abstract algebra.
    # In the dual-number representation:
    # b_def = ((b, delta_b), (0, b)) where delta_b is the kappa-correction to b.
    # [b_def, a_def] = b_def @ a_def - a_def @ b_def (matrix product in 2x2 block form)
    # = ((ba, b*0 + delta_b*a), (0, ba)) - ((ab, a*delta_b + 0*b), (0, ab))
    # (using a_def = ((a, 0), (0, a)))
    # = ((ba - ab, delta_b*a - a*delta_b), (0, ba - ab))
    # = ((0, [delta_b, a]), (0, 0))
    # For [b_def, a_def] = ((0, -gb*I), (0, 0)), we need [delta_b, a] = -gb*I.
    # i.e., delta_b*a - a*delta_b = -gb*I.
    #
    # For odd a (parity 1): [delta_b, a] = delta_b*a - (-1)^{p(delta_b)*1}*a*delta_b
    # If delta_b has parity 1 (odd): = delta_b*a + a*delta_b = {delta_b, a}
    # We need {delta_b, a^sigma} = -gb*I.
    # For a^sigma and a^{-sigma}: {a^{-sigma}, a^sigma} = 1, so delta_b = -gb*a^{-sigma} works!
    #
    # So delta_b = -gb * a^{-sigma} for deforming [b, a^sigma].
    # And in the dual number representation:
    # b_j^s_def = ((b_j^s_mat, -gb * a^{-sigma}_mat), (0, b_j^s_mat))
    # a^sigma_def = ((a^sigma_mat, 0), (0, a^sigma_mat))
    #
    # The GENERATORS of g are built from these deformed oscillators:
    # E.g., X = a^sigma @ b_j^s = ((a*b, a*(-gb*a^{-sigma})), (0, a*b))
    #                             = ((X_mat, -gb*a*a^{-sigma}), (0, X_mat))
    # a*a^{-sigma} = a^sigma * a^{-sigma} = N_f or (1-N_f)
    #
    # But this changes the generator! X_def has a kappa-component.
    # The kappa-component of the generator IS part of the deformation.
    #
    # The DEFORMED BRACKET of original generators X, Y:
    # [X, Y]_def is the bracket in the deformed algebra.
    # If X = sum of products of oscillators, then X_def = corresponding products in deformed algebra.
    # [X_def, Y_def] gives the deformed bracket.
    # The kappa-component of [X_def, Y_def] is the gamma correction.
    #
    # But X_def != X: the deformation changes the generators.
    # So [X_def, Y_def] is NOT [X, Y]_def. It's the bracket of the "deformed generators".
    #
    # THE RESOLUTION: The gamma cocycle is DEFINED as the correction to the bracket
    # of the ORIGINAL generators (elements of the abstract Lie superalgebra).
    # In the abelian extension L = g + kappa*g:
    # [X + kappa*0, Y + kappa*0]_L = [X,Y]_0 + kappa*gamma(X,Y)
    #
    # In the oscillator realization, X and Y are realized as specific operators.
    # The "deformed bracket" [X, Y]_def is computed using the deformed product
    # of these SAME operators. The kappa-component gives gamma.
    #
    # In the dual-number representation:
    # X_def = ((X_mat, X_kappa), (0, X_mat)) where X_kappa comes from the
    # kappa-components of the oscillators that make up X.
    # The bracket [X_def, Y_def] has kappa-component that includes BOTH
    # the "generator change" and the "bracket change".
    #
    # gamma(X, Y) is the kappa-component of [X_def, Y_def] MINUS the
    # "generator change" contributions.
    #
    # Actually, gamma(X, Y) = kappa-component of (X_0 Y_kappa + X_kappa Y_0 - ...)
    # where the "..." accounts for the super-commutator.
    #
    # Hmm, this is getting complicated. Let me just use the DUAL NUMBER approach
    # directly and extract the correct gamma.

    # DUAL NUMBER IMPLEMENTATION
    eps_val = 1e-7

    gb_names = []
    for sigma in ['+', '-']:
        for j in range(1, n + 1):
            for s in ['+', '-']:
                gb_names.append(f'gb_{sigma},{j},{s}')
    n_gb = len(gb_names)

    gamma_comp = {}

    for gi, gname in enumerate(gb_names):
        parts = gname.split('_')[1].split(',')
        sigma, j_str, s = parts
        j = int(j_str) - 1

        a_neg = am if sigma == '+' else ap

        # Build deformed oscillators in dual-number form
        # b_j^s_def = b_j^s + eps * (-a^{-sigma})
        # This gives [b_j^s_def, a^sigma] = eps * {a^{-sigma}, a^sigma} = eps * I
        bp_d = [m.copy() for m in bp]
        bm_d = [m.copy() for m in bm]
        if s == '+':
            bp_d[j] = bp[j] + eps_val * a_neg
        else:
            bm_d[j] = bm[j] + eps_val * a_neg

        # Build generators with deformed oscillators
        # These are the "deformed generator realizations"
        mats_d = []
        for gn, gm, gp in gens:
            if gn == 'H1':
                mats_d.append(ap @ am + bp_d[0] @ bm_d[0])
            elif gn == 'H2':
                mats_d.append(bp_d[0] @ bm_d[0] - bp_d[1] @ bm_d[1])
            elif gn == 'H3':
                mats_d.append(-bp_d[1] @ bm_d[1] - 0.5 * I)
            elif gn.startswith('E2d'):
                k = int(gn[3:]) - 1
                mats_d.append(0.5 * bp_d[k] @ bp_d[k])
            elif gn.startswith('E-2d'):
                k = int(gn[4:]) - 1
                mats_d.append(0.5 * bm_d[k] @ bm_d[k])
            elif gn.startswith('Ed') and '+' in gn:
                k_str, l_str = gn[2:].split('+d')
                k, l = int(k_str) - 1, int(l_str) - 1
                mats_d.append(bp_d[k] @ bp_d[l])
            elif gn.startswith('E-d') and '-d' in gn[3:]:
                rest = gn[3:]
                k_str, l_str = rest.split('-d')
                k, l = int(k_str) - 1, int(l_str) - 1
                mats_d.append(bm_d[k] @ bm_d[l])
            elif gn.startswith('Ed') and '-' in gn[2:]:
                k_str, l_str = gn[2:].split('-d')
                k, l = int(k_str) - 1, int(l_str) - 1
                mats_d.append(bp_d[k] @ bm_d[l])
            elif gn.startswith('E-d') and '+d' in gn:
                rest = gn[3:]
                k_str, l_str = rest.split('+d')
                k, l = int(k_str) - 1, int(l_str) - 1
                mats_d.append(bp_d[l] @ bm_d[k])
            elif gn.startswith('o_e+d'):
                k = int(gn[5:]) - 1
                mats_d.append(ap @ bp_d[k])
            elif gn.startswith('o_e-d'):
                k = int(gn[5:]) - 1
                mats_d.append(ap @ bm_d[k])
            elif gn.startswith('o_-e+d'):
                k = int(gn[6:]) - 1
                mats_d.append(am @ bp_d[k])
            elif gn.startswith('o_-e-d'):
                k = int(gn[6:]) - 1
                mats_d.append(am @ bm_d[k])
            else:
                raise ValueError(f"Unknown generator: {gn}")

        # The correction to the bracket of X_def, Y_def includes both
        # the gamma correction AND the "generator change" effect.
        # To isolate gamma, we need:
        # gamma(X, Y) = (correction to bracket) - (bracket of correction generators)
        #
        # correction_X = X_def - X (first order in eps)
        # [X_def, Y_def] = [X+dX, Y+dY] = [X,Y] + [dX,Y] + [X,dY] + O(eps^2)
        # So the first-order correction is [dX, Y] + [X, dY].
        #
        # But gamma(X, Y) is ONLY the part from the deformed commutation relation.
        # The [dX, Y] + [X, dY] part is the "total derivative" which includes
        # both the relation change and the generator change.
        #
        # In the abelian extension framework:
        # gamma(X, Y) = (total correction) - [dX, Y]_0 - [X, dY]_0
        # where dX = X_def - X.

        # But actually, I think the total correction IS gamma.
        # The reason: in the oscillator realization, the abstract generators of g
        # are DEFINED as specific bilinears. When the oscillator algebra is deformed,
        # the SAME bilinear expressions give DIFFERENT brackets. The gamma measures
        # this change in brackets.
        #
        # The "generator change" (X_def - X) is not meaningful in the abstract algebra
        # because X and X_def are both just "the generator associated with root alpha".
        # The deformation changes the BRACKET, not the generators.
        #
        # So gamma(X, Y) = kappa-component of [X_def, Y_def] - [X, Y]
        #                 = (first-order eps-component of [X_def, Y_def] - [X, Y]) / eps
        #
        # And the numerical "total correction" / eps IS gamma.
        #
        # Wait, but this contradicts what I found earlier for n=1, where the numerical
        # approach gave wrong results (like -9*H1 - 8.75*H2).
        #
        # The issue for n=1 was NOT the approach itself but possibly:
        # 1. The lstsq decomposition was wrong (confirmed: the scalar issue)
        # 2. Or the interpretation was wrong
        #
        # With the TRACE-based decomposition, the results should be correct.
        # Let me try it.

        gc = {}
        for i in range(ng):
            for j2 in range(ng):
                br_d = sb(mats_d[i], pars[i], mats_d[j2], pars[j2])
                br_o = sb(mats[i], pars[i], mats[j2], pars[j2])
                corr = (br_d - br_o) / eps_val

                c, s, err = trace_decompose(corr, mats, I, dim)

                d = {}
                for k in range(ng):
                    val = round(c[k] * 4) / 4
                    if abs(val) > 0.1:
                        d[k] = val
                if d:
                    gc[(i, j2)] = d

        gamma_comp[gname] = gc

    # Now build the linear system
    phi_idx = [(a, b) for a in range(ng) for b in range(ng) if pars[a] != pars[b]]
    eq_idx = [(i, j, k) for i in range(ng) for j in range(i + 1, ng) for k in range(ng)]
    n_phi = len(phi_idx)
    n_eq = len(eq_idx)

    def get_sc(i, j, k):
        return sc.get((i, j), {}).get(k, 0.0)

    A = np.zeros((n_eq, n_phi))
    for row, (i, j, k) in enumerate(eq_idx):
        pi, pj = pars[i], pars[j]
        for col, (a, b) in enumerate(phi_idx):
            val = 0.0
            if b == j: val += ((-1) ** pi) * get_sc(i, a, k)
            if b == i: val -= ((-1) ** ((pi + 1) * pj)) * get_sc(j, a, k)
            if a == k: val -= get_sc(i, j, b)
            A[row, col] = val

    B = np.zeros((n_eq, n_gb))
    for gi_idx, gname in enumerate(gb_names):
        gc = gamma_comp[gname]
        for row, (i, j, k) in enumerate(eq_idx):
            if (i, j) in gc:
                B[row, gi_idx] = gc[(i, j)].get(k, 0.0)

    rank_A = np.linalg.matrix_rank(A, tol=1e-4)
    rank_B = np.linalg.matrix_rank(B, tol=1e-4)
    print(f"\nCoboundary A: {A.shape}, rank={rank_A}")
    print(f"Gamma B: {B.shape}, rank={rank_B}")

    U, S, Vt = np.linalg.svd(A, full_matrices=True)
    P = U[:, :rank_A] @ U[:, :rank_A].T

    constraint = (np.eye(n_eq) - P) @ B
    U2, S2, Vt2 = np.linalg.svd(constraint, full_matrices=True)
    n_con = int(np.sum(np.abs(S2) > 1e-3))

    print(f"\nConstraints on gb: {n_con}")
    print(f"Trivial dim: {n_gb - n_con}")
    print(f"Singular values: {S2[:min(12, len(S2))]}")

    if n_con == n_gb:
        print("=> ONLY gb=0 is trivial")
    elif n_con == 0:
        print("=> ALL trivial")
    else:
        print(f"=> {n_gb - n_con}-dim trivial subspace")

    return n_con == n_gb


if __name__ == '__main__':
    main()
