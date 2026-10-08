"""
C(n+1) = osp(2|2n) inside U(A_gb):  basis, structure constants, the
inhomogeneous 2-cochain gamma_gb, the explicit odd map f_gb, and the
coboundary operator delta.

All arithmetic is exact (Fractions / polynomials in the gb parameters).
"""
from __future__ import annotations

from fractions import Fraction
from itertools import combinations

import sympy as sp

from osc_algebra import (
    ONE,
    OscillatorAlgebra,
    c_add,
    c_const,
    c_gb,
    c_mul,
    c_scale,
    e_add,
    e_scale_coef,
    split_kappa,
)


class CN1:
    def __init__(self, n: int):
        self.n = n
        self.A = OscillatorAlgebra(n)
        self._build_basis()
        self._build_decomposer()
        self._build_structure()

    # ------------------------------------------------------------------ basis
    def _build_basis(self):
        A, n = self.A, self.n
        labels, elems = [], []

        def add(label, elem):
            labels.append(label)
            elems.append(elem)

        # Cartan
        add("H1", e_add(A.word(1, 2), A.word(A.bp(1), A.bm(1))))
        for k in range(2, n + 1):
            add(f"H{k}", e_add(A.word(A.bp(k - 1), A.bm(k - 1)),
                               A.word(A.bp(k), A.bm(k), coef=-1)))
        add(f"H{n + 1}", e_add(A.word(A.bp(n), A.bm(n), coef=-1),
                               {(): c_const(Fraction(-1, 2))}))
        # even roots
        for k in range(1, n + 1):
            for l in range(1, n + 1):
                if k != l:
                    add(f"E[d{k}-d{l}]", A.word(A.bp(k), A.bm(l)))
        for k, l in combinations(range(1, n + 1), 2):
            add(f"E[d{k}+d{l}]", A.word(A.bp(k), A.bp(l)))
            add(f"E[-d{k}-d{l}]", A.word(A.bm(k), A.bm(l)))
        for k in range(1, n + 1):
            add(f"E[2d{k}]", A.word(A.bp(k), A.bp(k), coef=Fraction(1, 2)))
            add(f"E[-2d{k}]", A.word(A.bm(k), A.bm(k), coef=Fraction(1, 2)))
        # odd roots
        for l in range(1, n + 1):
            add(f"E[e+d{l}]", A.word(1, A.bp(l)))
            add(f"E[e-d{l}]", A.word(1, A.bm(l)))
            add(f"E[-e+d{l}]", A.word(2, A.bp(l)))
            add(f"E[-e-d{l}]", A.word(2, A.bm(l)))

        self.labels = labels
        self.basis = elems
        self.dim = len(elems)
        self.parity = [A.elem_parity(e) for e in elems]
        assert self.dim == 2 * n * n + 5 * n + 1
        assert sum(self.parity) == 4 * n

    # ---------------------------------------------------------- decomposition
    def _build_decomposer(self):
        """Invert the map  (coeffs on Z_1..Z_dim, 1)  ->  monomial coefficients."""
        monos = sorted({m for e in self.basis for m in e} | {()})
        self.monos = monos
        idx = {m: i for i, m in enumerate(monos)}
        N = len(monos)
        assert N == self.dim + 1, (N, self.dim)
        M = sp.zeros(N, N)
        cols = self.basis + [{(): c_const(1)}]
        for j, e in enumerate(cols):
            for m, c in e.items():
                assert set(c) <= {ONE}
                M[idx[m], j] = sp.Rational(c[ONE].numerator, c[ONE].denominator)
        self._Minv = M.inv()
        self._mono_idx = idx

    def decompose(self, elem: dict):
        """elem (kappa-free, degree <= 2) -> (vector over basis, scalar part),
        entries are polynomials in gb (dict gbkey -> Fraction)."""
        keys = set()
        for c in elem.values():
            keys |= set(c)
        vec = [dict() for _ in range(self.dim)]
        scal: dict = {}
        for key in keys:
            rhs = [Fraction(0)] * len(self.monos)
            for m, c in elem.items():
                if key in c:
                    if m not in self._mono_idx:
                        raise ValueError(f"monomial {m} outside g (+) C")
                    rhs[self._mono_idx[m]] = c[key]
            sol = self._Minv * sp.Matrix([sp.Rational(q.numerator, q.denominator) for q in rhs])
            for i in range(self.dim):
                q = Fraction(int(sol[i].p), int(sol[i].q))
                if q != 0:
                    vec[i] = c_add(vec[i], {key: q})
            q = Fraction(int(sol[self.dim].p), int(sol[self.dim].q))
            if q != 0:
                scal = c_add(scal, {key: q})
        return vec, scal

    # ------------------------------------------------------------ structure
    def _build_structure(self):
        """C[a][b] : dict c -> Fraction        (undeformed structure constants)
           G[a][b] : dict c -> {gbkey: Fraction}  (gamma_gb, g-part)
           G0[a][b]: {gbkey: Fraction}            (gamma_gb, scalar part)"""
        d = self.dim
        self.C = [[{} for _ in range(d)] for _ in range(d)]
        self.G = [[{} for _ in range(d)] for _ in range(d)]
        self.G0 = [[{} for _ in range(d)] for _ in range(d)]
        self.C0 = [[Fraction(0)] * d for _ in range(d)]
        for a in range(d):
            for b in range(d):
                br = self.A.bracket(self.basis[a], self.basis[b])
                B0, B1 = split_kappa(br)
                v0, s0 = self.decompose(B0)
                v1, s1 = self.decompose(B1)
                for c in range(d):
                    if v0[c]:
                        assert set(v0[c]) <= {ONE}, "gb appears without kappa?!"
                        self.C[a][b][c] = v0[c][ONE]
                    if v1[c]:
                        assert ONE not in v1[c], "kappa term without gb?!"
                        assert all(len(k) == 1 for k in v1[c]), "gamma not linear in gb"
                        self.G[a][b][c] = v1[c]
                if s0:
                    self.C0[a][b] = s0[ONE]
                if s1:
                    self.G0[a][b] = s1

    # ---------------------------------------------------- bracket on g (undeformed)
    def ad_bracket(self, u: list, v: list) -> list:
        """[u, v]_0 for coefficient vectors over the basis (entries Q[gb])."""
        out = [dict() for _ in range(self.dim)]
        for a, ua in enumerate(u):
            if not ua:
                continue
            for b, vb in enumerate(v):
                if not vb:
                    continue
                coef = c_mul(ua, vb)
                for c, q in self.C[a][b].items():
                    out[c] = c_add(out[c], c_scale(coef, q))
        return out

    # ------------------------------------------------------- explicit f_gb
    def explicit_f(self):
        """The odd map f_gb : g -> g (+) C  obtained from the change of variables
            a~^sig :=  a^sig + kappa * C^sig      (so that [b_j^s, a~^sig] = 0),
            C^sig   =  sum_j ( gb[a^sig,b_j^-] b_j^+  -  gb[a^sig,b_j^+] b_j^- ),
        i.e.  a^sig = a~^sig - kappa C^sig, and
        f(Z) := coefficient of kappa in Z(a -> a~ - kappa C).
        Returns (phi, phi0): phi[i][j] = coefficient of Z_i in f(Z_j), phi0[j] scalar part."""
        A = self.A
        Cp, Cm = {}, {}
        for j in range(1, self.n + 1):
            for sig in "+-":
                t1 = e_scale_coef(A.word(A.bm(j)), c_gb(A.gb_flat(sig, j, "+"), -1))
                t2 = e_scale_coef(A.word(A.bp(j)), c_gb(A.gb_flat(sig, j, "-"), 1))
                if sig == "+":
                    Cp = e_add(Cp, e_add(t1, t2))
                else:
                    Cm = e_add(Cm, e_add(t1, t2))
        Csub = {1: Cp, 2: Cm}
        kappa = A.word(0)
        phi = [[{} for _ in range(self.dim)] for _ in range(self.dim)]
        phi0 = [{} for _ in range(self.dim)]
        for j, Z in enumerate(self.basis):
            # substitute a^sig -> a^sig - kappa C^sig in every monomial of Z
            total = {}
            for m, c in Z.items():
                factors = []
                for g in m:
                    if g in Csub:
                        factors.append(e_add(A.word(g), e_scale_coef(A.mul(kappa, Csub[g]), c_const(-1))))
                    else:
                        factors.append(A.word(g))
                prod = {(): c_const(1)}
                for F in factors:
                    prod = A.mul(prod, F)
                total = e_add(total, e_scale_coef(prod, c))
            Z0, Z1 = split_kappa(total)
            # Z0 must be Z itself (expressed in the tilde variables)
            assert e_add(Z0, e_scale_coef(Z, c_const(-1))) == {}
            vec, scal = self.decompose(Z1)
            for i in range(self.dim):
                phi[i][j] = vec[i]
            phi0[j] = scal
        return phi, phi0

    # ------------------------------------------------------- coboundary
    def delta(self, phi, phi0=None):
        """(delta f)(Z_a, Z_b) = (-1)^{p_a}[Z_a, f Z_b] - (-1)^{(p_a+1)p_b}[Z_b, f Z_a] - f([Z_a, Z_b]).
        f(Z_j) = sum_i phi[i][j] Z_i + phi0[j]*1.  Returns (D, D0): g-part and scalar part."""
        d = self.dim
        fcol = [[phi[i][j] for i in range(d)] for j in range(d)]
        D = [[None] * d for _ in range(d)]
        D0 = [[{} for _ in range(d)] for _ in range(d)]
        unit = [dict() for _ in range(d)]
        for a in range(d):
            ea = [dict() for _ in range(d)]
            ea[a] = c_const(1)
            for b in range(d):
                eb = [dict() for _ in range(d)]
                eb[b] = c_const(1)
                pa, pb = self.parity[a], self.parity[b]
                t1 = self.ad_bracket(ea, fcol[b])
                s1 = -1 if pa else 1
                t2 = self.ad_bracket(eb, fcol[a])
                s2 = -(-1 if ((pa + 1) * pb) % 2 else 1)
                # f([Z_a, Z_b]) = sum_c C^c_ab f(Z_c)
                t3 = [dict() for _ in range(d)]
                s3 = {}
                for c, q in self.C[a][b].items():
                    for i in range(d):
                        if fcol[c][i]:
                            t3[i] = c_add(t3[i], c_scale(fcol[c][i], -q))
                    if phi0 is not None and phi0[c]:
                        s3 = c_add(s3, c_scale(phi0[c], -q))
                row = [dict() for _ in range(d)]
                for i in range(d):
                    row[i] = c_add(c_add(c_scale(t1[i], s1), c_scale(t2[i], s2)), t3[i])
                D[a][b] = row
                D0[a][b] = s3
        return D, D0


def coef_to_str(c: dict, gb_names) -> str:
    """Pretty print a polynomial in gb."""
    if not c:
        return "0"
    parts = []
    for k, v in sorted(c.items()):
        mon = "*".join(gb_names[i] for i in k) if k else "1"
        parts.append(f"({v})*{mon}" if k else f"({v})")
    return " + ".join(parts)
