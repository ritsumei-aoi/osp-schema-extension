"""
Triviality analysis of the inhomogeneous deformation gamma_gb of C(n+1) = osp(2|2n).

For n = 1, 2, 3 this script
  1. realises ghat = g + C*1 (g = C(n+1), spanned by super-symmetrised quadratics)
     inside the deformed oscillator algebra U(A_gb)/(K-1)  (scripts/osc_algebra.py);
  2. extracts the undeformed structure constants  [Z_i, Z_j]_0 = sum_k C[i][j][k] Z_k
     and the kappa-coefficient  gamma_gb(Z_i, Z_j) = sum_p gb_p * sum_k G[p][i][j][k] Z_k
     (k = m means the scalar 1, where m = dim g);
  3. checks: super-Jacobi for C, the 2-cocycle identity for gamma (Jacobi of the
     deformed bracket), ad-weights of the basis;
  4. verifies the closed-form odd map f_gb (Theorem in docs/issues/mathematical_proof.md):
         gamma_gb(X, Y) = (delta f_gb)(X, Y) + lambda_gb([X, Y]_0) * 1
     with lambda_gb(a^sigma b_j^s) = -gb_{sigma,j,s}/2, lambda_gb = 0 on g_0;
  5. certifies ker(delta : C^1_odd(g,g) -> C^2) = {ad_Z : Z in g_1}  (dimension 4n),
     so f_gb is unique up to inner odd derivations;
  6. shows that the scalar residual lambda_gb o [.,.]_0 vanishes iff gb = 0
     (rank of the residual map gb -> scalar part of gamma_gb equals 4n);
  7. writes artifacts/cn1_n{n}.json and artifacts/summary.json.

Run:  python3 scripts/verify_triviality.py
"""
import sys, os, json, time, random
from fractions import Fraction as F
sys.path.insert(0, os.path.dirname(__file__))
from osc_algebra import OscAlgebra, ONE, p_add

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ART = os.path.join(ROOT, "artifacts")


# ============================================================================
# 1. basis of ghat = C(n+1) + C*1 in the oscillator realisation
# ============================================================================
def build_basis(A):
    """Return list of dicts {label, parity, weight, poly} and the scalar index."""
    n = A.n
    P = lambda w: {w: dict(ONE)}
    half = F(1, 2)
    basis = []

    def weight(eps, deltas):
        return [eps] + list(deltas)

    # so(2) generator N = a+ a- - 1/2  (antisymmetrised Clifford bilinear)
    basis.append(dict(label="N", parity=0, weight=weight(0, [0] * n),
                      poly=p_add(P((1, 2)), {(): dict(ONE)}, -half),
                      oscillator="a+ a- - 1/2"))
    # sp(2n) Cartan: Hs_j = b_j^+ b_j^- + 1/2 = (b_j^+ b_j^- + b_j^- b_j^+)/2
    for j in range(1, n + 1):
        basis.append(dict(label=f"Hs{j}", parity=0, weight=weight(0, [0] * n),
                          poly=p_add(P((A.b(j, '+'), A.b(j, '-'))), {(): dict(ONE)}, half),
                          oscillator=f"b{j}+ b{j}- + 1/2"))
    # sp(2n) root vectors: b_j^s b_k^t  (normal ordered, excluding b_j^+ b_j^-)
    bgens = [(j, s) for j in range(1, n + 1) for s in ("+", "-")]
    for x in range(len(bgens)):
        for y in range(x, len(bgens)):
            (j, s), (k, t) = bgens[x], bgens[y]
            if j == k and s != t:
                continue
            wt = [0] * n
            wt[j - 1] += 1 if s == "+" else -1
            wt[k - 1] += 1 if t == "+" else -1
            lab = "E(" + "".join(("+" if v > 0 else "-") + (f"{abs(v)}" if abs(v) != 1 else "") + f"d{i+1}"
                                 for i, v in enumerate(wt) if v != 0) + ")"
            basis.append(dict(label=lab, parity=0, weight=weight(0, wt),
                              poly=P((A.b(j, s), A.b(k, t))),
                              oscillator=f"b{j}{s} b{k}{t}"))
    # odd root vectors: a^sigma b_j^s
    for sigma in ("+", "-"):
        for j in range(1, n + 1):
            for s in ("+", "-"):
                wt = [0] * n
                wt[j - 1] = 1 if s == "+" else -1
                lab = f"E({'+' if sigma == '+' else '-'}e{'+' if s == '+' else '-'}d{j})"
                basis.append(dict(label=lab, parity=1,
                                  weight=weight(1 if sigma == "+" else -1, wt),
                                  poly=P((A.a(sigma), A.b(j, s))),
                                  oscillator=f"a{sigma} b{j}{s}"))
    m = len(basis)
    assert m == 2 * n * n + 5 * n + 1, (m, n)
    return basis


def decompose(A, basis, poly):
    """Decompose a kappa-free normal-ordered polynomial of degree <= 2 as
    sum_k v[k] Z_k + v[m]*1.   Returns sparse dict k -> coefficient (coeff ring)."""
    m = len(basis)
    word_to_idx = {}
    for idx, Z in enumerate(basis):
        for w in Z["poly"]:
            if len(w) == 2:
                word_to_idx[w] = idx
    out = {}

    def add(k, c, scale=F(1)):
        nc = {}
        for key, v in c.items():
            nc[key] = v * scale
        cur = out.get(k, {})
        for key, v in nc.items():
            nv = cur.get(key, F(0)) + v
            if nv == 0:
                cur.pop(key, None)
            else:
                cur[key] = nv
        if cur:
            out[k] = cur
        else:
            out.pop(k, None)

    for w, c in poly.items():
        if len(w) == 0:
            add(m, c)
        elif len(w) == 2 and w in word_to_idx:
            idx = word_to_idx[w]
            add(idx, c)
            # correct for the scalar shift in N and Hs_j
            sc = basis[idx]["poly"].get((), {})
            if sc:
                add(m, c, -sc[()])
        else:
            raise ValueError("unexpected word in bracket: %r" % (w,))
    return out


# ============================================================================
# 2. structure constants and gamma
# ============================================================================
def extract(A, basis):
    """C[(i,j)] = {k: Fraction}  (undeformed bracket),
       G[p][(i,j)] = {k: Fraction} (coefficient of gb_p in the kappa-part)."""
    m = len(basis)
    np_ = len(A.gb_labels)
    C = {}
    G = [dict() for _ in range(np_)]
    for i in range(m):
        for j in range(m):
            br = A.supercomm(basis[i]["poly"], basis[j]["poly"])
            k0 = {w: c for w, c in br.items() if not (w and w[0] == 0)}
            k1 = {w[1:]: c for w, c in br.items() if (w and w[0] == 0)}
            d0 = decompose(A, basis, k0)
            d1 = decompose(A, basis, k1)
            row = {}
            for k, c in d0.items():
                assert set(c.keys()) <= {()}, "gb appears without kappa"
                row[k] = c[()]
            assert m not in row, f"scalar in undeformed bracket [{basis[i]['label']},{basis[j]['label']}]"
            if row:
                C[(i, j)] = row
            for k, c in d1.items():
                for key, v in c.items():
                    assert len(key) == 1, "gb-degree != 1 in kappa part"
                    G[key[0]].setdefault((i, j), {})[k] = v
    return C, G


# ============================================================================
# helpers for sparse vectors / brackets on ghat
# ============================================================================
def vadd(u, v, s=F(1)):
    out = dict(u)
    for k, x in v.items():
        nv = out.get(k, F(0)) + s * x
        if nv == 0:
            out.pop(k, None)
        else:
            out[k] = nv
    return out


def bracket0(C, m, u, v):
    """undeformed bracket of sparse vectors over ghat (scalar index m is central)."""
    out = {}
    for i, x in u.items():
        if i == m:
            continue
        for j, y in v.items():
            if j == m:
                continue
            row = C.get((i, j))
            if row:
                out = vadd(out, row, x * y)
    return out


def vec_parity(basis, u):
    m = len(basis)
    ps = {basis[i]["parity"] if i < m else 0 for i in u}
    assert len(ps) <= 1
    return ps.pop() if ps else None


# ============================================================================
# 3. checks: Jacobi, cocycle, weights
# ============================================================================
def check_jacobi(C, basis):
    m = len(basis)
    par = [Z["parity"] for Z in basis]
    bad = 0
    for i in range(m):
        for j in range(m):
            cij = C.get((i, j), {})
            for k in range(m):
                # [Z_i,[Z_j,Z_k]] - [[Z_i,Z_j],Z_k] - (-1)^{p_i p_j}[Z_j,[Z_i,Z_k]]
                t1 = bracket0(C, m, {i: F(1)}, C.get((j, k), {}))
                t2 = bracket0(C, m, cij, {k: F(1)})
                t3 = bracket0(C, m, {j: F(1)}, C.get((i, k), {}))
                s = F(-1) if (par[i] and par[j]) else F(1)   # (-1)^{p_i p_j}
                r = vadd(vadd(t1, t2, F(-1)), t3, -s)
                if r:
                    bad += 1
    return bad == 0


def deformed_bracket(C, Gp, m, par, u, v):
    """bracket on L = ghat + kappa*ghat for gb = e_p.  u = (u0, u1) means u0 + kappa u1."""
    u0, u1 = u
    v0, v1 = v
    p0 = vec_parity_simple(par, m, u0)
    out0 = bracket0(C, m, u0, v0)
    out1 = {}
    for i, x in u0.items():
        for j, y in v0.items():
            g = Gp.get((i, j))
            if g:
                out1 = vadd(out1, g, x * y)
    out1 = vadd(out1, bracket0(C, m, u1, v0))
    out1 = vadd(out1, bracket0(C, m, u0, v1), F(-1) if p0 == 1 else F(1))
    return out0, out1


def vec_parity_simple(par, m, u):
    ps = {par[i] if i < m else 0 for i in u}
    assert len(ps) <= 1, ps
    return ps.pop() if ps else 0


def check_cocycle(C, G, basis):
    """Jacobi identity for the deformed bracket on L (kappa^1 part), for every gb direction."""
    m = len(basis)
    par = [Z["parity"] for Z in basis]
    for Gp in G:
        for i in range(m):
            for j in range(m):
                for k in range(m):
                    Zi, Zj, Zk = ({i: F(1)}, {}), ({j: F(1)}, {}), ({k: F(1)}, {})
                    t1 = deformed_bracket(C, Gp, m, par, Zi, deformed_bracket(C, Gp, m, par, Zj, Zk))
                    t2 = deformed_bracket(C, Gp, m, par, deformed_bracket(C, Gp, m, par, Zi, Zj), Zk)
                    t3 = deformed_bracket(C, Gp, m, par, Zj, deformed_bracket(C, Gp, m, par, Zi, Zk))
                    s = F(-1) if (par[i] and par[j]) else F(1)
                    r1 = vadd(vadd(t1[1], t2[1], F(-1)), t3[1], -s)
                    r0 = vadd(vadd(t1[0], t2[0], F(-1)), t3[0], -s)
                    if r0 or r1:
                        return False
    return True


def check_weights(C, basis):
    """ad N and ad Hs_j are diagonal with eigenvalues = stored weights."""
    m = len(basis)
    n = (len(basis[0]["weight"]) - 1)
    cartan = [0] + [1 + j for j in range(n)]  # indices of N, Hs_1..Hs_n
    for k in range(m):
        for c_idx, h in enumerate(cartan):
            row = C.get((h, k), {})
            expect = {k: F(basis[k]["weight"][c_idx])} if basis[k]["weight"][c_idx] != 0 else {}
            if row != expect:
                return False
    return True


# ============================================================================
# 4. coboundary operator and the closed-form f
# ============================================================================
def delta(C, basis, f):
    """f: dict j -> sparse vector (f(Z_j)), odd map g -> ghat. Returns dict (i,j) -> sparse vec."""
    m = len(basis)
    par = [Z["parity"] for Z in basis]
    out = {}
    for i in range(m):
        for j in range(m):
            fi, fj = f.get(i, {}), f.get(j, {})
            t = bracket0(C, m, {i: F(1)}, fj)
            t = {k: (-1 if par[i] else 1) * v for k, v in t.items()}
            s = F(-1) * (-1 if ((par[i] + 1) * par[j]) % 2 else 1)
            t = vadd(t, bracket0(C, m, {j: F(1)}, fi), s)
            # - f([Z_i, Z_j])
            for k, c in C.get((i, j), {}).items():
                t = vadd(t, f.get(k, {}), -c)
            if t:
                out[(i, j)] = t
    return out


def closed_form_f(A, basis, p):
    """f_{e_p}:  Theorem.  c_j^s = gb(-,j,s) a+ + gb(+,j,s) a-  (only the e_p component).
       f(N) = 0;  f(sym(b_j^s b_k^t)) = -(c_k^t b_j^s + c_j^s b_k^t);
       f(a+ b_j^s) = gb(+,j,s) N;  f(a- b_j^s) = -gb(-,j,s) N."""
    sigma, jp, sp = A.gb_labels[p]
    m = len(basis)
    idx = {Z["label"]: i for i, Z in enumerate(basis)}
    n = A.n

    def odd_idx(sig, j, s):
        return idx[f"E({'+' if sig == '+' else '-'}e{'+' if s == '+' else '-'}d{j})"]

    f = {}
    # c_j^s (for gb = e_p): nonzero only for (j,s) = (jp,sp): c = a^{-sigma}  (a+ if sigma='-', a- if sigma='+')
    c_sign = "-" if sigma == "+" else "+"   # c_{jp}^{sp} = a^{c_sign}

    for i, Z in enumerate(basis):
        if Z["parity"] == 0 and Z["label"] not in ("N",) and not Z["label"].startswith("Hs"):
            # E = b_j^s b_k^t : find the two b's from the oscillator string
            toks = Z["oscillator"].split()
            (j, s), (k, t) = [(int(tk[1:-1]), tk[-1]) for tk in toks]
            v = {}
            # -(c_k^t b_j^s + c_j^s b_k^t)
            if (k, t) == (jp, sp):
                v = vadd(v, {odd_idx(c_sign, j, s): F(1)}, F(-1))
            if (j, s) == (jp, sp):
                v = vadd(v, {odd_idx(c_sign, k, t): F(1)}, F(-1))
            if v:
                f[i] = v
        elif Z["label"].startswith("Hs"):
            j = int(Z["label"][2:])
            # Hs_j = sym(b_j^+ b_j^-): f = -(c_j^- b_j^+ + c_j^+ b_j^-)
            v = {}
            if (j, "-") == (jp, sp):
                v = vadd(v, {odd_idx(c_sign, j, "+"): F(1)}, F(-1))
            if (j, "+") == (jp, sp):
                v = vadd(v, {odd_idx(c_sign, j, "-"): F(1)}, F(-1))
            if v:
                f[i] = v
        elif Z["parity"] == 1:
            toks = Z["oscillator"].split()
            sig = toks[0][1]
            j, s = int(toks[1][1:-1]), toks[1][-1]
            if (sig, j, s) == (sigma, jp, sp):
                f[i] = {idx["N"]: F(1) if sig == "+" else F(-1)}
    return f


def closed_form_lambda(A, basis, p):
    """lambda_{e_p}(Z_k): -1/2 on the odd generator a^sigma b_j^s with (sigma,j,s) = label p."""
    sigma, j, s = A.gb_labels[p]
    lab = f"E({'+' if sigma == '+' else '-'}e{'+' if s == '+' else '-'}d{j})"
    idx = {Z["label"]: i for i, Z in enumerate(basis)}
    return {idx[lab]: F(-1, 2)}


# ============================================================================
# 5. kernel of delta on odd 1-cochains  (rank certification)
# ============================================================================
def odd_unknowns(basis):
    m = len(basis)
    par = [Z["parity"] for Z in basis]
    return [(i, j) for j in range(m) for i in range(m) if par[i] != par[j]]  # phi_{ij}: coeff of Z_i in f(Z_j)


def delta_matrix_rows(C, basis):
    """Rows of the matrix of delta: C^1_odd -> C^2 as sparse dicts over unknown index."""
    m = len(basis)
    par = [Z["parity"] for Z in basis]
    unk = odd_unknowns(basis)
    uidx = {u: a for a, u in enumerate(unk)}
    rows = []
    for i in range(m):
        for j in range(i, m):
            # delta f (Z_i, Z_j) component k, as linear form in phi
            comps = {}

            def addterm(k, u, val):
                if u not in uidx or val == 0:
                    return
                d = comps.setdefault(k, {})
                nv = d.get(uidx[u], F(0)) + val
                if nv == 0:
                    d.pop(uidx[u], None)
                else:
                    d[uidx[u]] = nv

            s1 = F(-1) if par[i] else F(1)
            s2 = F(-1) * (-1 if ((par[i] + 1) * par[j]) % 2 else 1)
            # (-1)^{p_i} [Z_i, f(Z_j)] = s1 * sum_l phi_{l j} [Z_i, Z_l]
            for l in range(m):
                if par[l] == par[j]:
                    continue
                for k, c in C.get((i, l), {}).items():
                    addterm(k, (l, j), s1 * c)
            # s2 [Z_j, f(Z_i)]
            for l in range(m):
                if par[l] == par[i]:
                    continue
                for k, c in C.get((j, l), {}).items():
                    addterm(k, (l, i), s2 * c)
            # - f([Z_i,Z_j]) = - sum_k c_k f(Z_k) = - sum_k c_k sum_l phi_{l k} Z_l
            for k, c in C.get((i, j), {}).items():
                for l in range(m):
                    if par[l] != par[k]:
                        addterm(l, (l, k), -c)
            for k, d in comps.items():
                if d:
                    rows.append(d)
    return rows, unk


def rank_mod_p(rows, ncols, prime):
    """Rank of a sparse rational matrix reduced mod prime (lower bound on the Q-rank)."""
    import numpy as np
    M = np.zeros((len(rows), ncols), dtype=np.int64)
    for r, d in enumerate(rows):
        for c, v in d.items():
            num = v.numerator % prime
            den = pow(v.denominator % prime, prime - 2, prime)
            M[r, c] = (num * den) % prime
    rank = 0
    rowpos = 0
    for col in range(ncols):
        if rowpos >= M.shape[0]:
            break
        nz = np.nonzero(M[rowpos:, col])[0]
        if len(nz) == 0:
            continue
        piv = rowpos + nz[0]
        M[[rowpos, piv]] = M[[piv, rowpos]]
        inv = pow(int(M[rowpos, col]), prime - 2, prime)
        M[rowpos] = (M[rowpos] * inv) % prime
        others = np.nonzero(M[:, col])[0]
        others = others[others != rowpos]
        if len(others):
            M[others] = (M[others] - np.outer(M[others, col], M[rowpos])) % prime
        rowpos += 1
        rank += 1
    return rank


def rank_exact_small(vectors, ncols):
    """Exact rank of a small list of sparse rational vectors (Gaussian elimination)."""
    piv = {}
    rank = 0
    for v in vectors:
        v = dict(v)
        while v:
            c = min(v)
            if c in piv:
                pv = piv[c]
                s = v[c] / pv[c]
                v = vadd(v, pv, -s)
            else:
                piv[c] = v
                rank += 1
                break
    return rank


def inner_odd_derivations(C, basis):
    """ad_Z for odd basis Z, as maps j -> f(Z_j) = [Z, Z_j]."""
    m = len(basis)
    out = []
    for z in range(m):
        if basis[z]["parity"] != 1:
            continue
        f = {j: C[(z, j)] for j in range(m) if (z, j) in C}
        out.append((basis[z]["label"], f))
    return out


# ============================================================================
# main
# ============================================================================
def fr(x):
    return str(x)


def run(n):
    t0 = time.time()
    A = OscAlgebra(n)
    basis = build_basis(A)
    m = len(basis)
    par = [Z["parity"] for Z in basis]
    print(f"\n=== n = {n}: C({n+1}) = osp(2|{2*n}), dim = ({sum(1 for p in par if p == 0)}|{sum(par)}) ===")
    C, G = extract(A, basis)
    print(f"  brackets extracted ({time.time()-t0:.1f}s); nonzero undeformed brackets: {len(C)}")

    res = {}
    res["jacobi_undeformed"] = check_jacobi(C, basis)
    res["weights_consistent"] = check_weights(C, basis)
    res["cocycle_deformed_jacobi"] = check_cocycle(C, G, basis)
    print(f"  Jacobi(C) = {res['jacobi_undeformed']}, weights = {res['weights_consistent']}, "
          f"deformed Jacobi / cocycle = {res['cocycle_deformed_jacobi']}  ({time.time()-t0:.1f}s)")

    # gamma at gb=0 vanishes; each gb direction nonzero
    res["gamma_vanishes_at_gb_zero"] = True  # by construction (G only holds gb-linear terms)
    res["gamma_nonzero_each_direction"] = all(len(Gp) > 0 for Gp in G)

    # closed form f and lambda
    f_all, lam_all = {}, {}
    ok_g, ok_scalar = True, True
    max_resid = 0
    for p in range(len(A.gb_labels)):
        f = closed_form_f(A, basis, p)
        lam = closed_form_lambda(A, basis, p)
        f_all[p], lam_all[p] = f, lam
        df = delta(C, basis, f)
        for i in range(m):
            for j in range(m):
                g = G[p].get((i, j), {})
                g_part = {k: v for k, v in g.items() if k != m}
                g_scalar = g.get(m, F(0))
                d = df.get((i, j), {})
                if vadd(g_part, d, F(-1)):
                    ok_g = False
                    max_resid += 1
                # scalar residual must equal lambda([Z_i,Z_j]_0)
                lam_br = sum((lam.get(k, F(0)) * c for k, c in C.get((i, j), {}).items()), F(0))
                if g_scalar != lam_br:
                    ok_scalar = False
    res["gamma_g_part_equals_delta_f"] = ok_g
    res["gamma_scalar_part_equals_lambda_of_bracket"] = ok_scalar
    print(f"  gamma|_g == delta f_gb : {ok_g};   scalar part == lambda([.,.]) : {ok_scalar}")

    # kernel of delta on odd 1-cochains
    rows, unk = delta_matrix_rows(C, basis)
    nunk = len(unk)
    primes = [1000000007, 998244353, 999999937]
    ranks = [rank_mod_p(rows, nunk, pr) for pr in primes]
    inner = inner_odd_derivations(C, basis)
    # verify delta(ad_Z) = 0 exactly and independence
    inner_ok = all(not delta(C, basis, f) for _, f in inner)
    uidx = {u: a for a, u in enumerate(unk)}
    inner_vecs = [{uidx[(i, j)]: v for j, fv in f.items() for i, v in fv.items()} for _, f in inner]
    inner_rank = rank_exact_small(inner_vecs, nunk)
    res["delta_odd1_unknowns"] = nunk
    res["delta_odd1_rank_mod_p"] = dict(zip(map(str, primes), ranks))
    res["inner_odd_derivations_in_kernel"] = inner_ok
    res["inner_odd_derivations_rank"] = inner_rank
    res["kernel_dim_certified"] = (max(ranks) + inner_rank == nunk) and inner_ok
    res["kernel_dim"] = nunk - max(ranks)
    print(f"  delta on odd 1-cochains: unknowns {nunk}, rank(mod p) {ranks}, "
          f"inner odd derivations in kernel: {inner_ok} (rank {inner_rank}); "
          f"ker dim = 4n = {4*n}: {res['kernel_dim_certified']}  ({time.time()-t0:.1f}s)")

    # strict reading: scalar residual map gb -> (scalar part of gamma) has full rank 4n
    S = []
    for p in range(len(A.gb_labels)):
        S.append({(i * m + j): g[m] for (i, j), g in G[p].items() if m in g})
    s_rank = rank_exact_small(S, m * m)
    res["scalar_residual_rank"] = s_rank
    res["strict_triviality_iff_gb_zero"] = (s_rank == len(A.gb_labels))
    # explicit witnesses: gamma(a^sigma b_j^+, (b_j^-)^2) and gamma(a^sigma b_j^-, (b_j^+)^2)
    idx = {Z["label"]: i for i, Z in enumerate(basis)}
    witnesses = []
    for p, (sigma, j, s) in enumerate(A.gb_labels):
        X = idx[f"E({'+' if sigma=='+' else '-'}e{'-' if s=='+' else '+'}d{j})"]  # a^sigma b_j^{-s}
        Y = idx[f"E({'+' if s=='+' else '-'}2d{j})"]                                # (b_j^{s})^2
        sc = G[p].get((X, Y), {}).get(m, F(0))
        witnesses.append(dict(gb=f"gb({sigma},{j},{s})", X=basis[X]["label"], Y=basis[Y]["label"],
                              scalar_part_of_gamma=fr(sc)))
    print(f"  scalar-residual rank = {s_rank} (= 4n: {res['strict_triviality_iff_gb_zero']})")

    # ---------------- artifact ----------------
    art = dict(
        n=n, algebra=f"C({n+1}) = osp(2|{2*n})", dim_even=sum(1 for p in par if p == 0), dim_odd=sum(par),
        conventions=dict(
            generators="0:kappa(odd,central,kappa^2=0) 1:a+ 2:a- ; b_j^+ = 3+2(j-1), b_j^- = 4+2(j-1)",
            relations="{a-,a+}=1, [b_j^-,b_j^+]=1, [b_j^s,a^sigma] = -gb(sigma,j,s)*kappa",
            basis="ghat = g + C*1; index m = dim g denotes the scalar 1; g = span of super-symmetrised quadratics",
            bracket="[Z_i,Z_j]_gb = sum_k C[i][j][k] Z_k + kappa * sum_p gb_p sum_k G[p][i][j][k] Z_k",
            coboundary="(delta f)(X,Y) = (-1)^{p(X)}[X,f(Y)] - (-1)^{(p(X)+1)p(Y)}[Y,f(X)] - f([X,Y])",
            f_matrix="f[p][j] = sparse vector of f_{e_p}(Z_j) in the basis (phi_{ij} = f[p][j][i])",
            weights="[eps-coefficient, delta_1, ..., delta_n]; a+ has weight +eps, b_j^+ has weight +delta_j",
            cartan_relation="doc's H_1 = N + Hs_1, H_k = Hs_{k-1} - Hs_k (2<=k<=n), H_{n+1} = -Hs_n",
            numbers="all rationals given as strings",
        ),
        basis=[dict(index=i, label=Z["label"], parity=Z["parity"], weight=Z["weight"],
                    oscillator=Z["oscillator"],
                    normal_ordered=[[fr(c[()]), [A.gen_label(g) for g in w]] for w, c in Z["poly"].items()])
               for i, Z in enumerate(basis)] + [dict(index=m, label="1", parity=0, weight=[0] * (n + 1),
                                                     oscillator="1", normal_ordered=[["1", []]])],
        gb_parameters=[dict(index=p, label=f"gb({s},{j},{t})", sigma=s, j=j, s=t)
                       for p, (s, j, t) in enumerate(A.gb_labels)],
        structure_constants=dict(format="[i, j, k, value] : [Z_i, Z_j]_0 = sum_k value Z_k",
                                 data=[[i, j, k, fr(v)] for (i, j), row in sorted(C.items()) for k, v in sorted(row.items())]),
        gamma=dict(format="[p, i, j, k, value] : coefficient of gb_p in gamma(Z_i,Z_j) along Z_k (k = m is the scalar 1)",
                   data=[[p, i, j, k, fr(v)] for p, Gp in enumerate(G) for (i, j), row in sorted(Gp.items())
                         for k, v in sorted(row.items())]),
        f=dict(format="[p, i, j, value] : f_{e_p}(Z_j) = sum_i value Z_i  (odd map g -> g)",
               data=[[p, i, j, fr(v)] for p, f in f_all.items() for j, fv in sorted(f.items()) for i, v in sorted(fv.items())]),
        lambda_=dict(format="[p, k, value] : lambda_{e_p}(Z_k) = value;  gamma(X,Y) - (delta f)(X,Y) = lambda([X,Y]_0) * 1",
                     data=[[p, k, fr(v)] for p, lam in lam_all.items() for k, v in sorted(lam.items())]),
        inner_odd_derivations=dict(format="label Z, [i, j, value]: ad_Z(Z_j) = sum_i value Z_i; these span ker(delta) on odd 1-cochains",
                                   data=[dict(Z=lab, map=[[i, j, fr(v)] for j, fv in sorted(f.items()) for i, v in sorted(fv.items())])
                                         for lab, f in inner]),
        strict_witnesses=witnesses,
        verification=res,
        elapsed_seconds=round(time.time() - t0, 2),
    )
    os.makedirs(ART, exist_ok=True)
    with open(os.path.join(ART, f"cn1_n{n}.json"), "w") as fh:
        json.dump(art, fh, indent=1)
    return res


if __name__ == "__main__":
    summary = {}
    for n in (1, 2, 3):
        summary[f"n={n}"] = run(n)
    summary["conclusion"] = (
        "For n = 1,2,3 and every gb in C^{4n}: gamma_gb = delta f_gb + lambda_gb([.,.]_0)*1 with the explicit "
        "odd map f_gb : g -> g and the odd functional lambda_gb (= -gb/2 on odd generators).  Modulo scalars "
        "(adjoint representation) gamma_gb is therefore a coboundary for ALL gb; f_gb is unique up to inner odd "
        "derivations ad_Z, Z in g_1.  The scalar residual vanishes iff gb = 0, so exact equality in U(A) with "
        "f confined to g holds only for gb = 0."
    )
    with open(os.path.join(ART, "summary.json"), "w") as fh:
        json.dump(summary, fh, indent=1)
    print("\nSUMMARY:")
    for k, v in summary.items():
        print(" ", k, ":", v if isinstance(v, str) else {kk: vv for kk, vv in v.items()})
