#!/usr/bin/env python3
"""
osp_deformation.py
==================

Realisation of g = C(n+1) = osp(2|2n) inside the (deformed) Weyl--Clifford
algebra, extraction of the inhomogeneous 2-cocycle gamma_gb, and the
triviality analysis gamma_gb = c . delta f.

Basis of g (super-symmetrised quadratics)
-----------------------------------------
    Z_{ij} = v_i o v_j := 1/2 ( v_i v_j + (-1)^{p_i p_j} v_j v_i ),   i <= j,
    omitting i = j with p_i = 1  (since (a^sigma)^2 = 0).

Counts:  even block  n(2n+1) = dim sp(2n),  odd-odd block 1 = dim so(2),
         mixed block 4n = odd part.  Total 2n^2 + 5n + 1 = dim C(n+1).  OK.

Two sections of g inside W_kappa are compared:

    SYM : Z_{ij} = v_i v_j - 1/2 (omega_ij + mu_ij kappa)   (true super-symmetrisation
                                                             IN the deformed algebra)
    NAIVE: Z^0_{ij} = v_i v_j - 1/2 omega_ij                (undeformed normal ordering)

They differ by the odd scalar cochain  Z_{ij} - Z^0_{ij} = -1/2 mu_ij kappa.
"""

from fractions import Fraction
import itertools
import json

from osp_algebra import (OscAlgebra, Lin, const, sym, ZERO, ONE,
                         add_into, prune, scale, sub, mul_lin)


# --------------------------------------------------------------------------


class Deformation:
    def __init__(self, n, gb=None, section="SYM"):
        self.n = n
        self.A = OscAlgebra(n, gb)
        self.section = section
        self.pairs = []
        N = self.A.N
        for i in range(N):
            for j in range(i, N):
                if i == j and self.A.par[i] == 1:
                    continue
                self.pairs.append((i, j))
        self.dim = len(self.pairs)
        self.labels = [f"{self.A.names[i]}o{self.A.names[j]}" for i, j in self.pairs]
        self.Z = [self._make_Z(i, j) for i, j in self.pairs]
        self.zpar = [(self.A.par[i] + self.A.par[j]) % 2 for i, j in self.pairs]
        # position of leading word (i,j) inside the basis, for decomposition
        self.pos = {(i, j): a for a, (i, j) in enumerate(self.pairs)}

    def _make_Z(self, i, j):
        A = self.A
        w = {((i, j), 0): ONE}
        out = dict(w)
        add_into(out, {((), 0): ONE}, const(A.omega[i][j]) * Fraction(-1, 2))
        if self.section == "SYM":
            add_into(out, {((), 1): ONE}, A.mu[i][j] * Fraction(-1, 2))
        return prune(out)

    # ---------------------------------------------------------------- decompose
    def decompose(self, X):
        """
        Write X = sum_c C_c Z_c + kappa.(sum_c G_c Z_c) + tau + sigma.kappa.

        Returns (C, G, tau, sigma) with C, G lists of Lin and tau, sigma Lin.
        """
        A = self.A
        rem = dict(X)
        C = [ZERO] * self.dim
        G = [ZERO] * self.dim
        # kappa-free quadratic part
        for a, (i, j) in enumerate(self.pairs):
            c = rem.get(((i, j), 0), ZERO)
            if not c.is_zero():
                C[a] = c
                add_into(rem, self.Z[a], -c)
        # kappa quadratic part
        for a, (i, j) in enumerate(self.pairs):
            c = rem.get(((i, j), 1), ZERO)
            if not c.is_zero():
                G[a] = c
                add_into(rem, A.kappa_times(self.Z[a]), -c)
        rem = prune(rem)
        tau = rem.pop(((), 0), ZERO)
        sigma = rem.pop(((), 1), ZERO)
        if prune(rem):
            raise ValueError(f"undecomposable remainder: {prune(rem)}")
        return C, G, tau, sigma

    # ---------------------------------------------------------------- brackets
    def compute(self):
        """Structure constants C, cocycle Gamma, anomalies tau (even) / sigma (odd)."""
        d = self.dim
        self.C = [[None] * d for _ in range(d)]
        self.G = [[None] * d for _ in range(d)]
        self.tau = [[ZERO] * d for _ in range(d)]
        self.sigma = [[ZERO] * d for _ in range(d)]
        for a in range(d):
            for b in range(d):
                br = self.A.bracket(self.Z[a], self.Z[b])
                C, G, tau, sg = self.decompose(br)
                self.C[a][b] = C
                self.G[a][b] = G
                self.tau[a][b] = tau
                self.sigma[a][b] = sg
        return self

    # ---------------------------------------------------------------- twist
    def twist_T(self):
        """
        Odd map T : V -> V with  T(b) = 0,
            T(a^sigma) = sum_j ( gb[sigma,j,-] b_j^+  -  gb[sigma,j,+] b_j^- ).
        The twisted generators are  vt_i = v_i + kappa T(v_i).
        """
        A = self.A
        T = {i: {} for i in range(A.N)}
        for sigma in "+-":
            ai = A.index[f"a{sigma}"]
            acc = {}
            for j in range(1, self.n + 1):
                bp, bm = A.index[f"b{j}+"], A.index[f"b{j}-"]
                add_into(acc, {((bp,), 0): ONE}, A.gb[(sigma, j, "-")])
                add_into(acc, {((bm,), 0): ONE}, -A.gb[(sigma, j, "+")])
            T[ai] = prune(acc)
        return T

    def twisted_gens(self):
        A = self.A
        T = self.twist_T()
        vt = []
        for i in range(A.N):
            e = {((i,), 0): ONE}
            if T[i]:
                add_into(e, A.kappa_times(T[i]), 1)
            vt.append(prune(e))
        return vt

    def twisted_Z(self):
        """Zt_a = vt_i o vt_j  (super-symmetrised with UNDEFORMED signs)."""
        A = self.A
        vt = self.twisted_gens()
        out = []
        for (i, j) in self.pairs:
            s = (-1) ** (A.par[i] * A.par[j])
            e = A.mul(vt[i], vt[j])
            add_into(e, A.mul(vt[j], vt[i]), Fraction(s))
            e = scale(e, Fraction(1, 2))
            out.append(prune(e))
        return out


# --------------------------------------------------------------------------
# delta f  (definition of docs/math/C_coboundary_definition.md)
# --------------------------------------------------------------------------


def delta_f(D, phi):
    """
    phi[i][j] = coefficient of Z_i in f(Z_j)  (odd: nonzero only if p_i != p_j).
    Uses the UNDEFORMED structure constants D.C0 (gb = 0).
    Returns dict (a,b) -> list of Lin, the components of (delta f)(Z_a, Z_b).
    """
    d = D.dim
    out = {}
    for a in range(d):
        pa = D.zpar[a]
        for b in range(d):
            pb = D.zpar[b]
            comp = [ZERO] * d
            # (-1)^{p(X)} [X, f(Y)]
            s1 = Fraction(-1) ** pa
            for i in range(d):
                if phi[i][b].is_zero():
                    continue
                for c in range(d):
                    if D.C0[a][i][c].is_zero():
                        continue
                    comp[c] = comp[c] + mul_lin(phi[i][b], D.C0[a][i][c]) * s1
            # -(-1)^{(p(X)+1) p(Y)} [Y, f(X)]
            s2 = -(Fraction(-1) ** (((pa + 1) * pb) % 2))
            for i in range(d):
                if phi[i][a].is_zero():
                    continue
                for c in range(d):
                    if D.C0[b][i][c].is_zero():
                        continue
                    comp[c] = comp[c] + mul_lin(phi[i][a], D.C0[b][i][c]) * s2
            # - f([X,Y])
            for i in range(d):
                cc = D.C0[a][b][i]
                if cc.is_zero():
                    continue
                for c in range(d):
                    if phi[c][i].is_zero():
                        continue
                    comp[c] = comp[c] + mul_lin(cc, phi[c][i]) * Fraction(-1)
            out[(a, b)] = comp
    return out
