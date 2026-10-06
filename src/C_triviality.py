"""Linear-algebra core for the triviality analysis of the C(n+1) deformation (Layers 1,2,4).

Unknowns: phi[i,j] (f(Z_j) = sum_i phi[i,j] Z_i, odd f: p(Z_i) = p(Z_j)+1), optionally constants c[j] for odd Z_j
(f(Z_j) += c[j] K).  Equation (coboundary operator of C_coboundary_definition.md):
  (delta f)(X,Y) = (-1)^{px}[X,f(Y)] - (-1)^{(px+1)py}[Y,f(X)] - f([X,Y]).
Triviality of gamma(gb) := sum_p gb_p gamma_p  <=>  exists f with delta f = gamma(gb).
"""
import json
import os
import sys
from fractions import Fraction

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from verify_C_gamma import load_gamma  # noqa: E402
from verify_C_structure import load  # noqa: E402


class System:
    def __init__(self, n, data_dir=None):
        kw = {} if data_dir is None else {"data_dir": data_dir}
        self.n = n
        self.names, par, br = load(n, **kw)
        d, self.params, gam = load_gamma(n, **kw)
        self.par = [par[x] for x in self.names]
        N = self.N = len(self.names)
        idx = self.idx = {x: i for i, x in enumerate(self.names)}
        self.c = np.zeros((N, N, N))
        for (X, Y), zs in br.items():
            for Z, v in zs.items():
                self.c[idx[X], idx[Y], idx[Z]] = float(v)
        P = len(self.params)
        self.G = np.zeros((P, N, N, N))   # gamma_p[X,Y,Z]
        self.GK = np.zeros((P, N, N))     # K component
        for k, p in enumerate(self.params):
            for (X, Y), zs in gam[p].items():
                for Z, v in zs.items():
                    if Z == "K":
                        self.GK[k, idx[X], idx[Y]] = float(v)
                    else:
                        self.G[k, idx[X], idx[Y], idx[Z]] = float(v)
        # phi variables
        self.var = [(i, j) for j in range(N) for i in range(N) if self.par[i] == (self.par[j] + 1) % 2]
        self.vidx = {v: k for k, v in enumerate(self.var)}
        self.odd = [j for j in range(N) if self.par[j] == 1]

    def delta_matrix(self, with_constants=False):
        """Rows: (X,Y,Z) for Z in basis, then (X,Y,K). Columns: phi variables [+ constants for odd Z]."""
        N = self.N
        nv = len(self.var) + (len(self.odd) if with_constants else 0)
        M = np.zeros((N, N, N, nv))
        MK = np.zeros((N, N, nv))
        for (i, j), k in self.vidx.items():
            # term (-1)^{px}[X, f(Y)] with Y=j, f(Y) contains Z_i:  contributes c[X,i,Z] to (X,j,Z)
            for X in range(N):
                sx = -1 if self.par[X] else 1
                M[X, j, :, k] += sx * self.c[X, i, :]
            # term -(-1)^{(px+1)py}[Y, f(X)] with X=j: f(X) contains Z_i; contributes -s*c[Y,i,Z] to (j,Y,Z)
            for Y in range(N):
                s = (-1) ** ((self.par[j] + 1) * self.par[Y])
                M[j, Y, :, k] -= s * self.c[Y, i, :]
            # term -f([X,Y]): [X,Y] contains Z_j -> -phi[i,j] at Z=i
            M[:, :, i, k] -= self.c[:, :, j]
        if with_constants:
            base = len(self.var)
            for q, j in enumerate(self.odd):
                MK[:, :, base + q] -= self.c[:, :, j]
        return M.reshape(N ** 3, nv), MK.reshape(N * N, nv)


def solve_gb_subspace(S, variant):
    """Return an orthonormal basis (columns, in gb coordinates) of {gb : gamma(gb) trivial} for the given variant.

    variant: 'strict'  f: g->g, K-component of gamma must match (be 0);
             'gonly'   f: g->g, K-component ignored;
             'const'   f: g->g+CK (constants allowed on odd generators), K-component matched.
    """
    P = len(S.params)
    N = S.N
    M, MK = S.delta_matrix(with_constants=(variant == "const"))
    Gm = S.G.reshape(P, N ** 3).T  # (N^3, P)
    GKm = S.GK.reshape(P, N * N).T
    nv = M.shape[1]
    if variant == "gonly":
        A = np.hstack([M, -Gm])
    else:
        A = np.vstack([np.hstack([M, -Gm]), np.hstack([MK, -GKm])])
    # nullspace of A -> project onto gb coordinates
    u, s, vt = np.linalg.svd(A, full_matrices=True) if A.shape[0] < 3000 else _svd_gram(A)
    tol = 1e-9 * max(1.0, s.max() if len(s) else 1.0)
    rank = int((s > tol).sum())
    null = vt[rank:].T
    gb_part = null[nv:, :]
    if gb_part.size == 0:
        return np.zeros((P, 0)), null
    uu, ss, _ = np.linalg.svd(gb_part, full_matrices=False)
    r = int((ss > 1e-8).sum())
    return uu[:, :r], null


def _svd_gram(A):
    """SVD via eigen-decomposition of A^T A (A is tall and sparse-ish)."""
    G = A.T @ A
    w, V = np.linalg.eigh(G)
    order = np.argsort(-w)
    w, V = w[order], V[:, order]
    s = np.sqrt(np.clip(w, 0, None))
    return None, s, V.T


if __name__ == "__main__":
    for n in (1, 2):
        S = System(n)
        for variant in ("strict", "gonly", "const"):
            B, _ = solve_gb_subspace(S, variant)
            print(n, variant, "dim trivial gb-subspace =", B.shape[1], "of", len(S.params))
