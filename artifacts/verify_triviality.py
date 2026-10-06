"""Triviality of the inhomogeneous (gb) deformation of C(n+1) = osp(2|2n).

Model
-----
V = span{a+, a-, b_j+, b_j-};  A = V + C K + C kappa  (K even central, kappa odd central).
g = quadratic elements of U(A) modulo constants, basis = ordered words x*y.
gamma_gb(X,Y) = kappa-linear part of [X,Y] in U(A) (K = 1), identified with an element of g.
Triviality: exists an odd linear f: g -> g with gamma_gb = delta f, delta f as in
docs/math/C_coboundary_definition.md.  Everything is linear in gb, so the set of trivial gb
is a linear subspace S, computed exactly over Q (sympy).
"""
import json
import numpy as np
import sympy as sp


def build(n):
    V = [('a', '+'), ('a', '-')] + [('b', j, s) for j in range(1, n + 1) for s in '+-']
    idx = {v: i for i, v in enumerate(V)}
    par = [1 if v[0] == 'a' else 0 for v in V]
    gbkeys = [(sg, j, s) for sg in '+-' for j in range(1, n + 1) for s in '+-']
    gbidx = {k: i for i, k in enumerate(gbkeys)}
    m, N = len(gbkeys), len(V)
    Kc = np.zeros((N, N))
    kap = np.zeros((N, N, m))
    for j in range(1, n + 1):
        Kc[idx[('b', j, '-')], idx[('b', j, '+')]] = 1
        Kc[idx[('b', j, '+')], idx[('b', j, '-')]] = -1
    Kc[idx[('a', '-')], idx[('a', '+')]] = 1      # {a-,a+} = 1
    Kc[idx[('a', '+')], idx[('a', '-')]] = 1
    for (sg, j, s), g in gbidx.items():
        ib, ia = idx[('b', j, s)], idx[('a', sg)]
        kap[ib, ia, g] += -1                       # [b_j^s, a^sigma] = -gb kappa
        kap[ia, ib, g] += +1
    basis = [(i, k) for i in range(N) for k in range(i, N) if not (par[i] == 1 and i == k)]
    bidx = {w: t for t, w in enumerate(basis)}
    bpar = [(par[i] + par[k]) % 2 for i, k in basis]
    return dict(n=n, V=V, par=par, Kc=Kc, kap=kap, m=m, N=N, basis=basis,
                bidx=bidx, bpar=bpar, gbkeys=gbkeys)


def canon(M, x, y):
    """word x*y -> (sign, basis index) modulo constants, or None if zero."""
    par = M['par']
    if par[x] == 1 and x == y:
        return None
    if x <= y:
        return 1, M['bidx'][(x, y)]
    return (-1) ** (par[x] * par[y]), M['bidx'][(y, x)]


def bracket_words(M, X, Y, which):
    par = M['par']
    C = M['Kc'] if which == 'K' else M['kap']
    out = {}

    def add(c, a, b, sign):
        r = canon(M, a, b)
        if r is None:
            return
        s, t = r
        out[t] = out.get(t, 0) + sign * s * c

    x1, x2 = X
    y1, y2 = Y
    pY = (par[y1] + par[y2]) % 2
    # [x1x2,Y] = x1[x2,Y] + (-1)^{p(x2)p(Y)} [x1,Y] x2
    add(C[x2, y1], x1, y2, 1)
    add(C[x2, y2], x1, y1, (-1) ** (par[x2] * par[y1]))
    sg = (-1) ** (par[x2] * pY)
    add(C[x1, y1], y2, x2, sg)
    add(C[x1, y2], y1, x2, sg * (-1) ** (par[x1] * par[y1]))
    return out


def structure(M):
    B, m = M['basis'], M['m']
    d = len(B)
    br0 = np.zeros((d, d, d))
    gam = np.zeros((d, d, d, m))
    for p, X in enumerate(B):
        for q, Y in enumerate(B):
            for t, c in bracket_words(M, X, Y, 'K').items():
                br0[p, q, t] += c
            for t, c in bracket_words(M, X, Y, 'kap').items():
                gam[p, q, t] += c
    return br0, gam


def run(n, out):
    M = build(n)
    br0, gam = structure(M)
    d, m, bp = len(M['basis']), M['m'], M['bpar']
    ev, od = bp.count(0), bp.count(1)
    assert (ev, od) == (2 * n * n + n + 1, 4 * n), (ev, od)
    L = br0
    for p in range(d):
        for q in range(d):
            s = -(-1) ** (bp[p] * bp[q])
            assert np.allclose(L[p, q], s * L[q, p]) and np.allclose(gam[p, q], s * gam[q, p])
    # super-Jacobi: [p,[q,r]] = [[p,q],r] + (-1)^{pq} [q,[p,r]]
    T1 = np.einsum('qrt,ptu->pqru', L, L)
    T2 = np.einsum('pqt,tru->pqru', L, L)
    T3 = np.einsum('prt,qtu->pqru', L, L)
    sgn = np.array([[(-1) ** (bp[p] * bp[q]) for q in range(d)] for p in range(d)])
    assert np.allclose(T1, T2 + sgn[:, :, None, None] * T3), "Jacobi fails"

    sx = np.array([(-1) ** bp[p] for p in range(d)])[:, None, None]
    sy = np.array([[(-1) ** ((bp[p] + 1) * bp[q]) for q in range(d)] for p in range(d)])[:, :, None]
    unk = [(i, j) for j in range(d) for i in range(d) if bp[i] != bp[j]]   # f(Z_j) += phi_ij Z_i
    cols = []
    for (i, j) in unk:
        f = np.zeros((d, d))
        f[i, j] = 1                                  # f[target, source]
        A1 = np.einsum('sq,pst->pqt', f, L)          # [X, f(Y)]
        A2 = np.einsum('sp,qst->pqt', f, L)          # [Y, f(X)]
        A3 = np.einsum('pqs,ts->pqt', L, f)          # f([X,Y])
        cols.append((sx * A1 - sy * A2 - A3).reshape(-1))
    Dn = np.array(cols).T
    assert np.allclose(Dn, np.round(Dn))
    D = sp.Matrix(np.round(Dn).astype(int).tolist())
    Gn = np.array([gam[..., g].reshape(-1) for g in range(m)]).T
    assert np.allclose(Gn, np.round(Gn))
    G = sp.Matrix(np.round(Gn).astype(int).tolist())
    rD, rG = D.rank(), G.rank()
    DG = D.row_join(G)
    rDG = DG.rank()
    ns = DG.nullspace()
    nu = len(unk)
    Sgb = sp.Matrix.hstack(*[v[nu:, :] for v in ns]) if ns else sp.zeros(m, 0)
    Sbasis = Sgb.columnspace() if Sgb.shape[1] else []
    res = dict(n=n, dim_g=d, even=ev, odd=od, num_gb_params=m, num_f_unknowns=nu,
               rank_delta=rD, rank_gamma_map=rG, rank_joint=rDG,
               dim_trivial_gb_subspace=len(Sbasis),
               trivial_gb_basis=[[str(x) for x in v] for v in Sbasis],
               gb_keys=["gb_%s_%d_%s" % k for k in M['gbkeys']],
               only_zero_gb_is_trivial=(len(Sbasis) == 0),
               basis_words=[[str(M['V'][i]) for i in w] for w in M['basis']],
               basis_parity=bp,
               gamma_nonzero=[dict(X=p, Y=q, Z=t,
                                   coeff_in_gb={"gb_%s_%d_%s" % M['gbkeys'][g]: float(gam[p, q, t, g])
                                                for g in range(m) if gam[p, q, t, g] != 0})
                              for p in range(d) for q in range(d) for t in range(d)
                              if np.any(gam[p, q, t])],
               bracket0_nonzero=[dict(X=p, Y=q, Z=t, c=float(br0[p, q, t]))
                                 for p in range(d) for q in range(d) for t in range(d)
                                 if br0[p, q, t] != 0])
    out[str(n)] = res
    print(f"n={n}: dim g={d} ({ev}|{od}), gb params={m}, rank delta={rD}, rank gamma-map={rG}, "
          f"rank[delta|gamma]={rDG}, dim trivial gb-subspace={len(Sbasis)}", flush=True)


if __name__ == '__main__':
    out = {}
    for n in (1, 2, 3):
        run(n, out)
    with open('artifacts/verification_data.json', 'w') as fh:
        json.dump(out, fh, indent=1)
