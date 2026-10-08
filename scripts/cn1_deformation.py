#!/usr/bin/env python3
"""
cn1_deformation.py
==================

Verification artifacts for the triviality of the inhomogeneous (``gb``)
deformation of the Lie superalgebra C(n+1) = osp(2|2n).

Everything is computed from first principles, starting from the oscillator
realisation given in ``docs/math/Cn1_definition.md``:

* fermionic pair  a+, a-           with {a-, a+} = 1,
* bosonic pairs   b_k+, b_k-       with [b_k-, b_l+] = delta_kl,
* the odd central element kappa (kappa^2 = 0) and the deformed relations
      [b_j^s, a^sigma] = - gb_{sigma, j, s} * kappa
  (``docs/math/C_inhomogeneous_definition.md``).

The script

1. builds the Weyl-Clifford algebra W_gb = (oscillators) (x) C[kappa]/(kappa^2)
   with the deformed relations, with the 4n parameters gb kept SYMBOLIC;
2. builds the canonical basis of g = C(n+1) inside W_gb as super-symmetrised
   quadratic elements;
3. computes the undeformed structure constants c_{ij}^k and the deformation
   cocycle  gamma_{ij}^k(gb)  (plus the scalar parts s_{ij}(gb) that are
   dropped "up to scalar");
4. constructs the odd map f_gb : g -> g predicted by the theorem and checks
   gamma_gb = delta f_gb  EXACTLY (symbolically in gb), using the coboundary
   formula of ``docs/math/C_coboundary_definition.md``;
5. independently solves the linear system  delta f = gamma_{e_i}  for every
   coordinate direction e_i of gb, with exact rational arithmetic and WITHOUT
   using the explicit f, to confirm solvability;
6. computes dim H^1(g, Pi g) and dim H^2(g, Pi g) (odd cohomology with values
   in the adjoint module) via the weight-zero sub-complex, which decides the
   triviality question for *every* odd deformation, not only the gb family;
7. writes structured JSON artifacts.

Run:  python3 scripts/cn1_deformation.py --n 1 2 3 --out artifacts
"""

from __future__ import annotations

import argparse
import itertools
import json
import os
import sys
import time
from fractions import Fraction

import sympy as sp

# ---------------------------------------------------------------------------
# 1. The deformed Weyl-Clifford algebra
# ---------------------------------------------------------------------------


class Osc:
    """Weyl-Clifford algebra of the C(n+1) oscillators, tensored with
    C[kappa]/(kappa^2) where kappa is ODD and central, with the deformed mixed
    relations  [b_j^s, a^sigma] = -gb_{sigma,j,s} kappa.

    Elements are dicts  {(kflag, mono): coeff}  meaning
        sum  coeff * kappa^kflag * mono
    with kappa always written on the LEFT, and ``mono`` a normal-ordered tuple
    of generator indices.  Generator indices:
        0 = a+ , 1 = a- , 2+2(k-1) = b_k+ , 3+2(k-1) = b_k-   (k = 1..n).
    Normal order = non-decreasing index (all fermions to the left).
    """

    def __init__(self, n: int):
        self.n = n
        self.ngen = 2 + 2 * n
        self.par = [1, 1] + [0] * (2 * n)
        self.names = ["a+", "a-"] + [f"b{k}{s}" for k in range(1, n + 1) for s in "+-"]
        self.gb_syms: dict[tuple[str, int, str], sp.Symbol] = {}
        self.gb_labels: dict[tuple[str, int, str], str] = {}
        for sigma in "+-":
            for j in range(1, n + 1):
                for s in "+-":
                    sym = sp.Symbol(f"gb_a{'p' if sigma == '+' else 'm'}_b{j}{'p' if s == '+' else 'm'}")
                    self.gb_syms[(sigma, j, s)] = sym
                    self.gb_labels[(sigma, j, s)] = f"gb[a{sigma},b{j}{s}]"
        self.gb_list = list(self.gb_syms.keys())
        self.memo: dict = {}

    # -- bookkeeping ---------------------------------------------------------
    def boson_of(self, idx: int) -> int:
        return (idx - 2) // 2  # 0-based boson label

    def gb_of(self, b_idx: int, a_idx: int) -> sp.Symbol:
        sigma = "+" if a_idx == 0 else "-"
        j = (b_idx - 2) // 2 + 1
        s = "+" if (b_idx - 2) % 2 == 0 else "-"
        return self.gb_syms[(sigma, j, s)]

    def mono_parity(self, seq) -> int:
        return sum(self.par[x] for x in seq) % 2

    # -- normal ordering -------------------------------------------------------
    def normal(self, seq: tuple, k: int) -> dict:
        """Normal-order the word ``kappa^k * seq``.  Returns {(k', seq'): coeff}."""
        key = (seq, k)
        if key in self.memo:
            return self.memo[key]
        res: dict = {}
        for i in range(len(seq) - 1):
            x, y = seq[i], seq[i + 1]
            if x == y:
                if self.par[x] == 1:  # (a+)^2 = (a-)^2 = 0
                    res = {}
                    break
                continue
            if x > y:  # descent: rewrite  x y  =  (-1)^{p_x p_y} y x + [x, y]
                sign = -1 if (self.par[x] == 1 and self.par[y] == 1) else 1
                swapped = seq[:i] + (y, x) + seq[i + 2 :]
                res = {kk: sign * v for kk, v in self.normal(swapped, k).items()}
                rest = seq[:i] + seq[i + 2 :]
                if self.par[x] == 1 and self.par[y] == 1:
                    # x = a-, y = a+ :  a- a+ = -a+ a- + {a-, a+} = -a+ a- + 1
                    c, is_kappa = sp.Integer(1), False
                elif self.par[x] == 0 and self.par[y] == 0:
                    # same boson:  b- b+ = b+ b- + 1 ; different bosons commute
                    c = sp.Integer(1) if self.boson_of(x) == self.boson_of(y) else sp.Integer(0)
                    is_kappa = False
                else:
                    # x = b (even) > y = a (odd):  b a = a b + [b, a] = a b - gb kappa
                    c, is_kappa = -self.gb_of(x, y), True
                if c != 0:
                    if is_kappa:
                        if k == 1:
                            pass  # kappa^2 = 0
                        else:
                            # move kappa (odd) to the far left past seq[:i]
                            sgn = -1 if self.mono_parity(seq[:i]) == 1 else 1
                            for kk, v in self.normal(rest, 1).items():
                                res[kk] = res.get(kk, 0) + sgn * c * v
                    else:
                        for kk, v in self.normal(rest, k).items():
                            res[kk] = res.get(kk, 0) + c * v
                break
        else:
            res = {(k, seq): sp.Integer(1)}
        res = {kk: sp.expand(v) for kk, v in res.items()}
        res = {kk: v for kk, v in res.items() if v != 0}
        self.memo[key] = res
        return res

    # -- algebra operations ------------------------------------------------------
    @staticmethod
    def add(A: dict, B: dict, cb=1) -> dict:
        out = dict(A)
        for kk, v in B.items():
            out[kk] = out.get(kk, 0) + cb * v
        return {kk: sp.expand(v) for kk, v in out.items() if sp.expand(v) != 0}

    @staticmethod
    def scale(A: dict, c) -> dict:
        return {kk: sp.expand(c * v) for kk, v in A.items() if sp.expand(c * v) != 0}

    def mul(self, A: dict, B: dict) -> dict:
        out: dict = {}
        for (k1, s1), c1 in A.items():
            p1 = self.mono_parity(s1)
            for (k2, s2), c2 in B.items():
                if k1 and k2:
                    continue  # kappa^2 = 0
                sign = -1 if (k2 and p1) else 1  # s1 * kappa = (-1)^{p(s1)} kappa * s1
                for kk, v in self.normal(s1 + s2, k1 | k2).items():
                    out[kk] = out.get(kk, 0) + sign * c1 * c2 * v
        out = {kk: sp.expand(v) for kk, v in out.items()}
        return {kk: v for kk, v in out.items() if v != 0}

    def elem_parity(self, A: dict) -> int:
        ps = {(k + self.mono_parity(s)) % 2 for (k, s) in A}
        assert len(ps) <= 1, "inhomogeneous element"
        return ps.pop() if ps else 0

    def bracket(self, A: dict, B: dict) -> dict:
        """Super-commutator  [A, B] = A B - (-1)^{p(A) p(B)} B A."""
        pa, pb = self.elem_parity(A), self.elem_parity(B)
        sign = -1 if (pa and pb) else 1
        return self.add(self.mul(A, B), self.mul(B, A), -sign)

    def gen(self, idx: int) -> dict:
        return {(0, (idx,)): sp.Integer(1)}

    @staticmethod
    def one():
        return {(0, ()): sp.Integer(1)}

    def kappa_times(self, A: dict) -> dict:
        """kappa * A  (kappa on the left, no sign)."""
        return {(1, s): v for (k, s), v in A.items() if k == 0}

    def fmt(self, A: dict) -> str:
        parts = []
        for (k, s), v in sorted(A.items()):
            mono = ("kappa*" if k else "") + ("*".join(self.names[x] for x in s) if s else "1")
            parts.append(f"({v})*{mono}")
        return " + ".join(parts) if parts else "0"


# ---------------------------------------------------------------------------
# 2. The basis of g = C(n+1) inside W
# ---------------------------------------------------------------------------


class Cn1:
    """Canonical basis of g = osp(2|2n) = span of super-symmetrised quadratics."""

    def __init__(self, n: int):
        self.n = n
        self.W = Osc(n)
        W = self.W
        self.basis: list[dict] = []
        self.names: list[str] = []
        self.parity: list[int] = []
        self.weights: list[tuple] = []
        self.pair_index: dict[tuple, int] = {}
        self.shift: list[sp.Rational] = []
        self.gen_weight = self._gen_weights()
        for x in range(W.ngen):
            for y in range(x, W.ngen):
                if x == y and W.par[x] == 1:
                    continue
                mono = {(0, (x, y)): sp.Integer(1)}
                if (x, y) == (0, 1):  # N_a = a+ a- - 1/2 = sym(a+, a-)
                    shift, name = sp.Rational(-1, 2), "N_a"
                elif W.par[x] == 0 and W.par[y] == 0 and W.boson_of(x) == W.boson_of(y) and x != y:
                    shift, name = sp.Rational(1, 2), f"N_{W.boson_of(x) + 1}"  # N_k = b+ b- + 1/2
                else:
                    shift, name = sp.Integer(0), None
                wt = tuple(a + b for a, b in zip(self.gen_weight[x], self.gen_weight[y]))
                if name is None:
                    name = "E[" + self._root_name(wt) + "]"
                elem = W.add(mono, W.one(), shift)
                self.pair_index[(x, y)] = len(self.basis)
                self.basis.append(elem)
                self.names.append(name)
                self.parity.append((W.par[x] + W.par[y]) % 2)
                self.weights.append(wt)
                self.shift.append(shift)
        self.dim = len(self.basis)
        self.even_dim = sum(1 for p in self.parity if p == 0)
        self.odd_dim = self.dim - self.even_dim

    def _gen_weights(self):
        n = self.n
        wts = []
        for idx in range(self.W.ngen):
            v = [0] * (n + 1)
            if idx == 0:
                v[0] = 1
            elif idx == 1:
                v[0] = -1
            else:
                v[self.W.boson_of(idx) + 1] = 1 if (idx - 2) % 2 == 0 else -1
            wts.append(tuple(v))
        return wts

    def _root_name(self, wt):
        labels = ["e"] + [f"d{k}" for k in range(1, self.n + 1)]
        s = ""
        for lab, c in zip(labels, wt):
            if c == 0:
                continue
            sgn = "+" if c > 0 else "-"
            mag = "" if abs(c) == 1 else str(abs(c))
            s += sgn + mag + lab
        return s.lstrip("+") if s else "0"

    def oscillator_expression(self, i: int) -> str:
        return self.W.fmt(self.basis[i])

    # -- decomposition of an element of W into  g (+) C 1 (+) kappa g (+) kappa C 1 --
    def decompose(self, A: dict):
        vec = [[sp.Integer(0)] * self.dim for _ in range(2)]
        scal = [sp.Integer(0), sp.Integer(0)]
        for (k, s), v in A.items():
            if len(s) == 0:
                scal[k] += v
            elif len(s) == 2:
                idx = self.pair_index[s]
                vec[k][idx] += v
                scal[k] -= v * self.shift[idx]  # mono = Z - shift
            else:
                raise ValueError("element not in g (+) C: " + self.W.fmt(A))
        vec = [[sp.expand(c) for c in row] for row in vec]
        scal = [sp.expand(c) for c in scal]
        return vec[0], scal[0], vec[1], scal[1]

    def from_vec(self, vec) -> dict:
        out: dict = {}
        for i, c in enumerate(vec):
            if c != 0:
                out = self.W.add(out, self.basis[i], c)
        return out


# ---------------------------------------------------------------------------
# 3. Exact sparse linear algebra over Q
# ---------------------------------------------------------------------------


class SparseEchelon:
    """Incremental row-echelon form over Fractions (rows are dicts col->Fraction)."""

    def __init__(self):
        self.pivots: dict[int, dict] = {}  # pivot column -> normalised row

    def reduce(self, row: dict) -> dict:
        row = {c: Fraction(v) for c, v in row.items() if v != 0}
        while row:
            # reduce by pivots present in the row, smallest pivot column first
            cols = sorted(c for c in row if c in self.pivots)
            if not cols:
                break
            c = cols[0]
            factor = row[c]
            prow = self.pivots[c]
            for cc, vv in prow.items():
                nv = row.get(cc, Fraction(0)) - factor * vv
                if nv == 0:
                    row.pop(cc, None)
                else:
                    row[cc] = nv
        return row

    def add_row(self, row: dict) -> bool:
        row = self.reduce(row)
        if not row:
            return False
        c = min(row)
        inv = 1 / row[c]
        row = {cc: vv * inv for cc, vv in row.items()}
        # keep fully reduced form: eliminate c from existing pivot rows
        for pc, prow in self.pivots.items():
            if c in prow:
                f = prow[c]
                for cc, vv in row.items():
                    nv = prow.get(cc, Fraction(0)) - f * vv
                    if nv == 0:
                        prow.pop(cc, None)
                    else:
                        prow[cc] = nv
        self.pivots[c] = row
        return True

    @property
    def rank(self) -> int:
        return len(self.pivots)


def solve_exact(rows: list[dict], rhs_list: list[dict], ncols: int):
    """Solve  A phi = b  for each b in rhs_list (rows: dict col->Fraction).
    Returns (rank, [solution dict or None]).  RHS columns are appended with
    indices ncols + r so that inconsistency shows up as a pivot in an RHS column."""
    ech = SparseEchelon()
    for r_idx, row in enumerate(rows):
        aug = dict(row)
        for r, b in enumerate(rhs_list):
            v = b.get(r_idx, 0)
            if v != 0:
                aug[ncols + r] = -Fraction(v)  # row encodes  A phi - b = 0
        ech.add_row(aug)
    rank = sum(1 for c in ech.pivots if c < ncols)
    sols = []
    for r in range(len(rhs_list)):
        # inconsistent iff some pivot row has no unknown-columns but has RHS r ... in the
        # reduced system that is a pivot in an RHS column.  We solve per RHS by setting the
        # other RHS columns to zero: solution exists iff no pivot column equals ncols + r
        # with that pivot row having only RHS entries.  Because RHS columns were added as
        # ordinary columns, a pivot in column ncols+r means there is a row  (0 ... 0 | 1 ...)
        # => inconsistent for that RHS.
        if (ncols + r) in ech.pivots:
            sols.append(None)
            continue
        sol: dict = {}
        for pc, prow in ech.pivots.items():
            if pc >= ncols:
                continue
            # prow: phi_pc + sum_{free} ... - sum_r' coeff * b_{r'} = 0 ; set free vars = 0,
            # b_{r} = 1, other b = 0  ->  phi_pc = -coeff(ncols + r)
            v = -prow.get(ncols + r, Fraction(0))
            if v != 0:
                sol[pc] = v
        sols.append(sol)
    return rank, sols


# ---------------------------------------------------------------------------
# 4. Cochain calculus on g with values in Pi g
# ---------------------------------------------------------------------------


class LinForm(dict):
    """Linear form in unknowns: {var_index: Fraction}."""

    def plus(self, other, c=1):
        out = LinForm(self)
        for k, v in other.items():
            nv = out.get(k, Fraction(0)) + c * v
            if nv == 0:
                out.pop(k, None)
            else:
                out[k] = nv
        return out

    def times(self, c):
        if c == 0:
            return LinForm()
        return LinForm({k: v * c for k, v in self.items()})


def frac(x) -> Fraction:
    x = sp.nsimplify(x)
    return Fraction(int(x.p), int(x.q))


class Deformation:
    """Structure constants, the gb-cocycle, the explicit f and all checks."""

    def __init__(self, n: int, verbose=True):
        self.n = n
        self.g = Cn1(n)
        self.W = self.g.W
        self.log = (lambda *a: print(*a, flush=True)) if verbose else (lambda *a: None)
        g, W = self.g, self.W
        d = g.dim
        self.c = [[None] * d for _ in range(d)]  # c[i][j] = vector (sympy) of [Z_i, Z_j]_0
        self.gamma = [[None] * d for _ in range(d)]  # kappa-part, projected to g (symbolic in gb)
        self.s0 = [[None] * d for _ in range(d)]  # scalar part (kappa^0)  -- must vanish
        self.s1 = [[None] * d for _ in range(d)]  # scalar part of the kappa-term ("up to scalar")
        t = time.time()
        for i in range(d):
            for j in range(d):
                br = W.bracket(g.basis[i], g.basis[j])
                v0, sc0, v1, sc1 = g.decompose(br)
                self.c[i][j], self.s0[i][j], self.gamma[i][j], self.s1[i][j] = v0, sc0, v1, sc1
        self.log(f"[n={n}] dim g = {d} = {g.even_dim}|{g.odd_dim}; brackets computed in {time.time()-t:.1f}s")
        # exact rational structure constants
        self.cF = [[[frac(x) for x in self.c[i][j]] for j in range(d)] for i in range(d)]

    # -- helpers on g ----------------------------------------------------------------
    def ad_vec(self, i: int, vec):
        """[Z_i, v] for v a vector of coefficients (any ring supporting * and +)."""
        d = self.g.dim
        out = [0] * d
        for m, vm in enumerate(vec):
            if vm == 0:
                continue
            for k in range(d):
                ck = self.cF[i][m][k]
                if ck != 0:
                    out[k] = out[k] + vm * ck
        return out

    def bracket_vec(self, u, v):
        """[u, v]_0 for coefficient vectors u, v (bilinear extension)."""
        d = self.g.dim
        out = [0] * d
        for i, ui in enumerate(u):
            if ui == 0:
                continue
            for m, vm in enumerate(v):
                if vm == 0:
                    continue
                for k in range(d):
                    ck = self.cF[i][m][k]
                    if ck != 0:
                        out[k] = out[k] + ui * vm * ck
        return out

    # -- sanity checks on the undeformed algebra --------------------------------------
    def check_algebra(self) -> dict:
        g, d = self.g, self.g.dim
        res = {}
        res["closed_no_scalar"] = all(self.s0[i][j] == 0 for i in range(d) for j in range(d))
        res["structure_constants_gb_free"] = all(
            not sp.sympify(x).free_symbols for i in range(d) for j in range(d) for x in self.c[i][j]
        )
        # super-skew-symmetry
        ok = True
        for i in range(d):
            for j in range(d):
                sgn = -1 if (g.parity[i] and g.parity[j]) else 1
                ok &= all(sp.expand(self.c[i][j][k] + sgn * self.c[j][i][k]) == 0 for k in range(d))
        res["super_skew_symmetric"] = ok
        # super Jacobi
        ok = True
        for i in range(d):
            for j in range(d):
                for k in range(d):
                    a = self.ad_vec(i, self.cF[j][k])
                    b = self.bracket_vec(self.cF[i][j], [Fraction(1) if m == k else 0 for m in range(d)])
                    cc = self.ad_vec(j, self.cF[i][k])
                    sgn = -1 if (g.parity[i] and g.parity[j]) else 1
                    if any(a[m] - b[m] - sgn * cc[m] != 0 for m in range(d)):
                        ok = False
        res["super_jacobi"] = ok
        # weights: ad(N_a), ad(N_k) diagonal with the assigned weights
        cartan = [g.names.index("N_a")] + [g.names.index(f"N_{k}") for k in range(1, self.n + 1)]
        ok = True
        for ci, h in enumerate(cartan):
            for j in range(d):
                vec = self.cF[h][j]
                expect = [Fraction(g.weights[j][ci]) if m == j else 0 for m in range(d)]
                ok &= all(vec[m] == expect[m] for m in range(d))
        res["weights_consistent"] = ok
        # the so(2)-grading: epsilon-weight (eigenvalue of ad N_a) == parity mod 2 for every basis element
        res["parity_equals_epsilon_weight_mod_2"] = all(g.weights[j][0] % 2 == g.parity[j] for j in range(d))
        res["epsilon_weights_present"] = sorted({g.weights[j][0] for j in range(d)})
        res["cartan_indices"] = cartan
        res["center_trivial"] = self._center_dim() == 0
        return res

    def _center_dim(self) -> int:
        d = self.g.dim
        rows = []
        for i in range(d):
            for k in range(d):
                rows.append({m: self.cF[i][m][k] for m in range(d) if self.cF[i][m][k] != 0})
        ech = SparseEchelon()
        for r in rows:
            ech.add_row(r)
        return d - ech.rank

    # -- the cocycle gamma_gb ------------------------------------------------------
    def gamma_linear(self):
        """gamma_{ij}^k as dict gb_key -> Fraction (checks linearity in gb)."""
        d = self.g.dim
        out = {}
        for i in range(d):
            for j in range(d):
                for k in range(d):
                    e = sp.expand(self.gamma[i][j][k])
                    if e == 0:
                        continue
                    poly = sp.Poly(e, *self.W.gb_syms.values())
                    assert poly.total_degree() <= 1 and poly.coeff_monomial(1) == 0, "gamma not linear in gb"
                    coeffs = {}
                    for key, sym in self.W.gb_syms.items():
                        cval = e.coeff(sym)
                        if cval != 0:
                            coeffs[key] = frac(cval)
                    out[(i, j, k)] = coeffs
        return out

    def gamma_direction(self, gb_key) -> dict:
        """gamma for gb = e_{gb_key} as a dict (i,j,k) -> Fraction."""
        lin = self._gamma_lin
        return {ijk: cf[gb_key] for ijk, cf in lin.items() if gb_key in cf}

    def check_cocycle_symbolic(self) -> bool:
        """Super-Jacobi identity of the deformed bracket at first order in kappa,
        with gb symbolic.  Uses the bracket on L = g (+) kappa g:
            [X, Y]      = [X,Y]_0 + kappa gamma(X,Y)
            [X, kappa Y] = (-1)^{p(X)} kappa [X,Y]_0 ,  [kappa X, Y] = kappa [X,Y]_0 ."""
        g, d = self.g, self.g.dim
        ok = True
        for i in range(d):
            for j in range(d):
                for k in range(d):
                    # [Z_i, [Z_j, Z_k]]  first order
                    t1 = [sp.Integer(0)] * d
                    for m in range(d):
                        if self.c[j][k][m] != 0:
                            for l in range(d):
                                t1[l] += self.c[j][k][m] * self.gamma[i][m][l]
                    s = -1 if g.parity[i] else 1
                    for m in range(d):
                        if self.gamma[j][k][m] != 0:
                            for l in range(d):
                                t1[l] += s * self.gamma[j][k][m] * self.c[i][m][l]
                    # [[Z_i, Z_j], Z_k]
                    t2 = [sp.Integer(0)] * d
                    for m in range(d):
                        if self.c[i][j][m] != 0:
                            for l in range(d):
                                t2[l] += self.c[i][j][m] * self.gamma[m][k][l]
                    for m in range(d):
                        if self.gamma[i][j][m] != 0:
                            for l in range(d):
                                t2[l] += self.gamma[i][j][m] * self.c[m][k][l]
                    # (-1)^{p_i p_j} [Z_j, [Z_i, Z_k]]
                    t3 = [sp.Integer(0)] * d
                    for m in range(d):
                        if self.c[i][k][m] != 0:
                            for l in range(d):
                                t3[l] += self.c[i][k][m] * self.gamma[j][m][l]
                    s = -1 if g.parity[j] else 1
                    for m in range(d):
                        if self.gamma[i][k][m] != 0:
                            for l in range(d):
                                t3[l] += s * self.gamma[i][k][m] * self.c[j][m][l]
                    sgn = -1 if (g.parity[i] and g.parity[j]) else 1
                    for l in range(d):
                        if sp.expand(t1[l] - t2[l] - sgn * t3[l]) != 0:
                            ok = False
        return ok

    # -- the explicit f of the theorem ---------------------------------------------
    def d_sigma(self, sigma: str) -> dict:
        """d_sigma = sum_j ( gb_{sigma,j,-} b_j^+  -  gb_{sigma,j,+} b_j^- )  in W (kappa-free)."""
        W = self.W
        out: dict = {}
        for j in range(1, self.n + 1):
            bp, bm = 2 + 2 * (j - 1), 3 + 2 * (j - 1)
            out = W.add(out, W.gen(bp), W.gb_syms[(sigma, j, "-")])
            out = W.add(out, W.gen(bm), -W.gb_syms[(sigma, j, "+")])
        return out

    def primed_generator(self, idx: int) -> dict:
        """phi(x) = x + kappa d_x  (d_x = d_sigma for x = a^sigma, 0 for bosons)."""
        W = self.W
        x = W.gen(idx)
        if idx in (0, 1):
            x = W.add(x, W.kappa_times(self.d_sigma("+" if idx == 0 else "-")))
        return x

    def check_primed_oscillators(self) -> bool:
        """phi preserves ALL oscillator relations: [phi(x), phi(y)] = phi([x,y]_0) (undeformed)."""
        W = self.W
        ok = True
        prim = [self.primed_generator(i) for i in range(W.ngen)]
        for x in range(W.ngen):
            for y in range(W.ngen):
                lhs = W.bracket(prim[x], prim[y])
                # undeformed value of [x, y]
                if W.par[x] == 1 and W.par[y] == 1:
                    rhs = W.one() if x != y else {}
                elif W.par[x] == 0 and W.par[y] == 0 and W.boson_of(x) == W.boson_of(y) and x != y:
                    rhs = W.scale(W.one(), 1 if (x - 2) % 2 == 1 else -1)  # [b-,b+]=1, [b+,b-]=-1
                else:
                    rhs = {}
                if W.add(lhs, rhs, -1):
                    ok = False
        return ok

    def phi_of_basis(self, i: int) -> dict:
        """phi(Z_i): substitute primed oscillators into the defining expression of Z_i."""
        W = self.W
        out: dict = {}
        for (k, s), v in self.g.basis[i].items():
            assert k == 0
            term = W.one()
            for x in s:
                term = W.mul(term, self.primed_generator(x))
            out = W.add(out, term, v)
        return out

    def build_f(self):
        """F_i := kappa-part of phi(Z_i) in Q = g (+) C ;  f := -pi(F) : g -> g  (odd)."""
        g, d = self.g, self.g.dim
        self.F = []  # (vector in g, scalar) for each basis element
        self.f = [[sp.Integer(0)] * d for _ in range(d)]  # phi_{m j}: f(Z_j) = sum_m phi_{mj} Z_m
        self.lam = [sp.Integer(0)] * d
        self.Zprime = []
        for j in range(d):
            Zp = self.phi_of_basis(j)
            self.Zprime.append(Zp)
            v0, sc0, v1, sc1 = g.decompose(Zp)
            assert all(sp.expand(v0[m] - (1 if m == j else 0)) == 0 for m in range(d)) and sc0 == 0
            self.F.append((v1, sc1))
            for m in range(d):
                self.f[m][j] = sp.expand(-v1[m])
            self.lam[j] = sp.expand(-sc1)
        # parity check: f is odd
        ok = all(self.f[m][j] == 0 or g.parity[m] != g.parity[j] for m in range(d) for j in range(d))
        return ok

    def check_homomorphism_on_g(self) -> bool:
        """[phi(Z_i), phi(Z_j)]_gb  ==  sum_k c_{ij}^k phi(Z_k)   exactly in W_gb (incl. scalars)."""
        W, d = self.W, self.g.dim
        ok = True
        for i in range(d):
            for j in range(d):
                lhs = W.bracket(self.Zprime[i], self.Zprime[j])
                rhs: dict = {}
                for k in range(d):
                    if self.c[i][j][k] != 0:
                        rhs = W.add(rhs, self.Zprime[k], self.c[i][j][k])
                if W.add(lhs, rhs, -1):
                    ok = False
        return ok

    def delta_f(self, fmat, lam=None):
        """(delta f)(Z_i, Z_j) with the formula of C_coboundary_definition.md,
        for f(Z_j) = sum_m fmat[m][j] Z_m  (+ lam[j] * 1 if lam is given: Q-valued f).
        Returns (vectors, scalars)."""
        g, d = self.g, self.g.dim
        out = [[None] * d for _ in range(d)]
        outs = [[sp.Integer(0)] * d for _ in range(d)]
        for i in range(d):
            for j in range(d):
                vec = [sp.Integer(0)] * d
                # (-1)^{p_i} [Z_i, f(Z_j)]
                s = -1 if g.parity[i] else 1
                for m in range(d):
                    if fmat[m][j] != 0:
                        for k in range(d):
                            if self.c[i][m][k] != 0:
                                vec[k] += s * fmat[m][j] * self.c[i][m][k]
                # - (-1)^{(p_i+1) p_j} [Z_j, f(Z_i)]
                s = -1 if ((g.parity[i] + 1) * g.parity[j]) % 2 else 1
                for m in range(d):
                    if fmat[m][i] != 0:
                        for k in range(d):
                            if self.c[j][m][k] != 0:
                                vec[k] -= s * fmat[m][i] * self.c[j][m][k]
                # - f([Z_i, Z_j])
                for l in range(d):
                    if self.c[i][j][l] != 0:
                        for m in range(d):
                            if fmat[m][l] != 0:
                                vec[m] -= self.c[i][j][l] * fmat[m][l]
                        if lam is not None:
                            outs[i][j] -= self.c[i][j][l] * lam[l]
                out[i][j] = [sp.expand(x) for x in vec]
                outs[i][j] = sp.expand(outs[i][j])
        return out, outs

    def check_coboundary_exact(self):
        """gamma_gb == delta f_gb (in g) and  Gamma_gb == delta(-F) (in Q, incl. scalars)."""
        d = self.g.dim
        df, dfs = self.delta_f(self.f, self.lam)
        ok_g = all(sp.expand(df[i][j][k] - self.gamma[i][j][k]) == 0 for i in range(d) for j in range(d) for k in range(d))
        ok_scalar = all(sp.expand(dfs[i][j] - self.s1[i][j]) == 0 for i in range(d) for j in range(d))
        gamma_nonzero = any(self.gamma[i][j][k] != 0 for i in range(d) for j in range(d) for k in range(d))
        return ok_g, ok_scalar, gamma_nonzero

    # -- independent linear-algebra solution of delta f = gamma ---------------------
    def coboundary_matrix(self, weight_zero=False):
        """Rows: (i, j, k) with i <= j ; columns: (m, j) odd entries (p_m != p_j).
        Returns (rows as dict col->Fraction, row_index list, col list)."""
        g, d = self.g, self.g.dim
        cols = [(m, j) for m in range(d) for j in range(d) if g.parity[m] != g.parity[j]
                and (not weight_zero or g.weights[m] == g.weights[j])]
        col_id = {c: idx for idx, c in enumerate(cols)}
        rows, row_index = [], []
        for i in range(d):
            for j in range(i, d):
                for k in range(d):
                    row: dict = {}
                    s = Fraction(-1 if g.parity[i] else 1)
                    for m in range(d):
                        if (m, j) in col_id and self.cF[i][m][k] != 0:
                            row[col_id[(m, j)]] = row.get(col_id[(m, j)], Fraction(0)) + s * self.cF[i][m][k]
                    s = Fraction(-1 if ((g.parity[i] + 1) * g.parity[j]) % 2 else 1)
                    for m in range(d):
                        if (m, i) in col_id and self.cF[j][m][k] != 0:
                            row[col_id[(m, i)]] = row.get(col_id[(m, i)], Fraction(0)) - s * self.cF[j][m][k]
                    for l in range(d):
                        if self.cF[i][j][l] != 0 and (k, l) in col_id:
                            row[col_id[(k, l)]] = row.get(col_id[(k, l)], Fraction(0)) - self.cF[i][j][l]
                    row = {c: v for c, v in row.items() if v != 0}
                    rows.append(row)
                    row_index.append((i, j, k))
        return rows, row_index, cols

    def solve_for_f(self):
        """For each gb direction, solve delta f = gamma_{e} exactly (no use of the theorem's f)."""
        rows, row_index, cols = self.coboundary_matrix()
        rid = {ijk: r for r, ijk in enumerate(row_index)}
        rhs_list = []
        for key in self.W.gb_list:
            gdir = self.gamma_direction(key)
            rhs = {}
            for (i, j, k), v in gdir.items():
                if i <= j:
                    rhs[rid[(i, j, k)]] = v
            rhs_list.append(rhs)
        rank, sols = solve_exact(rows, rhs_list, len(cols))
        # verify each solution by direct substitution (full i, j including i > j)
        verified = []
        for key, sol in zip(self.W.gb_list, sols):
            if sol is None:
                verified.append(False)
                continue
            fmat = [[sp.Integer(0)] * self.g.dim for _ in range(self.g.dim)]
            for cidx, v in sol.items():
                m, j = cols[cidx]
                fmat[m][j] = sp.Rational(v.numerator, v.denominator)
            df, _ = self.delta_f(fmat)
            gdir = self.gamma_direction(key)
            ok = True
            for i in range(self.g.dim):
                for j in range(self.g.dim):
                    for k in range(self.g.dim):
                        if sp.expand(df[i][j][k]) != sp.Rational(gdir.get((i, j, k), 0)):
                            ok = False
            verified.append(ok)
        return {
            "n_unknowns_phi": len(cols),
            "rank_delta1": rank,
            "dim_ker_delta1_odd": len(cols) - rank,
            "solvable_per_gb_direction": {self.W.gb_labels[k]: (s is not None) for k, s in zip(self.W.gb_list, sols)},
            "solution_verified_per_gb_direction": {self.W.gb_labels[k]: v for k, v in zip(self.W.gb_list, verified)},
            "particular_solutions": {
                self.W.gb_labels[k]: ({f"{self.g.names[cols[c][0]]}<-{self.g.names[cols[c][1]]}": str(v) for c, v in s.items()} if s else None)
                for k, s in zip(self.W.gb_list, sols)
            },
        }

    def gamma_rank(self) -> int:
        """Rank of the linear map  gb -> gamma_gb  (injectivity => gamma_gb != 0 for gb != 0)."""
        ech = SparseEchelon()
        for key in self.W.gb_list:
            gdir = self.gamma_direction(key)
            ech.add_row({(i * self.g.dim + j) * self.g.dim + k: v for (i, j, k), v in gdir.items()})
        return ech.rank

    # -- cohomology H^1, H^2 (odd part) ------------------------------------------------
    def cohomology(self, weight_zero=True):
        """dim H^1(g, Pi g) and dim H^2(g, Pi g) from the (weight-zero) sub-complex.

        C^1_odd : odd linear maps f ; C^2_odd : gamma with gamma(X,Y) = -(-1)^{p_X p_Y} gamma(Y,X),
        p(gamma(X,Y)) = p_X + p_Y + 1 ;  d2 gamma = first-order super-Jacobi defect."""
        g, d = self.g, self.g.dim
        P = g.parity
        # --- C^2 variables
        var2 = []
        for i in range(d):
            for j in range(i, d):
                if i == j and P[i] == 0:
                    continue
                for k in range(d):
                    if (P[i] + P[j] + 1) % 2 != P[k]:
                        continue
                    if weight_zero and tuple(a + b for a, b in zip(g.weights[i], g.weights[j])) != g.weights[k]:
                        continue
                    var2.append((i, j, k))
        v2id = {v: idx for idx, v in enumerate(var2)}

        def gamma_form(i, j):
            """gamma(Z_i, Z_j) as a vector of LinForms."""
            out = [LinForm() for _ in range(d)]
            if i <= j:
                sgn = 1
            else:
                i, j = j, i
                sgn = -1 if (P[i] and P[j]) else 1
                sgn = -sgn  # gamma(Y,X) = -(-1)^{p p} gamma(X,Y)
            for k in range(d):
                if (i, j, k) in v2id:
                    out[k] = LinForm({v2id[(i, j, k)]: Fraction(sgn)})
            return out

        def gamma_vec(i, vec):
            """gamma(Z_i, v) for numeric vector v."""
            out = [LinForm() for _ in range(d)]
            for m, vm in enumerate(vec):
                if vm == 0:
                    continue
                gf = gamma_form(i, m)
                for k in range(d):
                    if gf[k]:
                        out[k] = out[k].plus(gf[k], vm)
            return out

        def ad_lin(i, lvec, sign=1):
            """sign * [Z_i, w] for w a vector of LinForms."""
            out = [LinForm() for _ in range(d)]
            for m, lm in enumerate(lvec):
                if not lm:
                    continue
                for k in range(d):
                    ck = self.cF[i][m][k]
                    if ck != 0:
                        out[k] = out[k].plus(lm, sign * ck)
            return out

        def br_first_order(i, vec0, lvec1):
            """kappa-part of [Z_i, (vec0 + kappa lvec1)] = gamma(Z_i, vec0) + (-1)^{p_i}[Z_i, lvec1]."""
            a = gamma_vec(i, vec0)
            b = ad_lin(i, lvec1, -1 if P[i] else 1)
            return [a[k].plus(b[k]) for k in range(d)]

        def br_first_order_right(lvec1, k):
            """kappa-part of [(vec0 + kappa lvec1), Z_k] from the kappa-part only: [kappa w, Z_k] = kappa [w, Z_k]."""
            out = [LinForm() for _ in range(d)]
            for m, lm in enumerate(lvec1):
                if not lm:
                    continue
                for l in range(d):
                    cl = self.cF[m][k][l]
                    if cl != 0:
                        out[l] = out[l].plus(lm, cl)
            return out

        rows2 = []
        t = time.time()
        for i in range(d):
            for j in range(i, d):
                for k in range(j, d):
                    # J = [Z_i,[Z_j,Z_k]] - [[Z_i,Z_j],Z_k] - (-1)^{p_i p_j} [Z_j,[Z_i,Z_k]]   (kappa-part)
                    t1 = br_first_order(i, self.cF[j][k], gamma_form(j, k))
                    # [[Z_i,Z_j], Z_k]: ([Z_i,Z_j]_0 + kappa gamma_ij , Z_k)
                    t2a = [LinForm() for _ in range(d)]
                    for m, cm in enumerate(self.cF[i][j]):
                        if cm == 0:
                            continue
                        gf = gamma_form(m, k)
                        for l in range(d):
                            if gf[l]:
                                t2a[l] = t2a[l].plus(gf[l], cm)
                    t2b = br_first_order_right(gamma_form(i, j), k)
                    t3 = br_first_order(j, self.cF[i][k], gamma_form(i, k))
                    sgn = -1 if (P[i] and P[j]) else 1
                    for l in range(d):
                        row = t1[l].plus(t2a[l], -1).plus(t2b[l], -1).plus(t3[l], -sgn)
                        if row:
                            rows2.append(row)
        ech2 = SparseEchelon()
        for r in rows2:
            ech2.add_row(r)
        rank_d2 = ech2.rank
        dimZ2 = len(var2) - rank_d2
        # --- image of delta on C^1 (weight-zero odd maps), expressed in C^2 coordinates
        cols1 = [(m, j) for m in range(d) for j in range(d) if P[m] != P[j]
                 and (not weight_zero or g.weights[m] == g.weights[j])]
        rows1, row_index1, _ = self.coboundary_matrix(weight_zero=weight_zero)
        # rows1 are indexed by (i,j,k) with i<=j; build the matrix delta: C^1 -> C^2 as columns
        # (we need rank of delta restricted to the weight-zero C^1) -> transpose: rows = C^1 basis
        rid = {ijk: r for r, ijk in enumerate(row_index1)}
        # build column vectors of delta e_{(m,j)}
        mat_T: list[dict] = [dict() for _ in range(len(cols1))]
        for r, row in enumerate(rows1):
            ijk = row_index1[r]
            if ijk not in v2id:
                # components outside the (weight-zero, parity-correct, i<=j) coordinates must vanish
                assert not row, f"delta f has a component outside C^2 coordinates: {ijk}"
                continue
            for cidx, v in row.items():
                mat_T[cidx][v2id[ijk]] = v
        ech1 = SparseEchelon()
        for col in mat_T:
            ech1.add_row(col)
        dimB2 = ech1.rank
        dimZ1 = len(cols1) - dimB2
        # inner odd derivations ad(X), X odd, of weight zero: X must have weight 0 => none for weight-zero? No:
        # ad(X) has weight wt(X); weight-zero C^1 contains ad(X) only if wt(X)=0, and no odd root is 0.
        # So in the weight-zero complex B^1 = 0 and H^1 = Z^1 directly (correct by the weight lemma).
        dimH1 = dimZ1 if weight_zero else dimZ1 - g.odd_dim
        # sanity: d2 o delta = 0
        ok_dd = True
        for col in mat_T:
            # check col is in ker d2: evaluate each row of d2 on col
            for row in rows2:
                s = sum(v * col.get(c, Fraction(0)) for c, v in row.items())
                if s != 0:
                    ok_dd = False
                    break
            if not ok_dd:
                break
        self.log(f"[n={self.n}] cohomology ({'weight-0' if weight_zero else 'full'}): "
                 f"C1={len(cols1)} C2={len(var2)} rows(d2)={len(rows2)} rank(d2)={rank_d2} "
                 f"Z2={dimZ2} B2={dimB2} H2={dimZ2 - dimB2} H1={dimH1}  ({time.time()-t:.1f}s)")
        return {
            "weight_zero_subcomplex": weight_zero,
            "dim_C1_odd": len(cols1),
            "dim_C2_odd": len(var2),
            "rank_d2": rank_d2,
            "dim_Z2_odd": dimZ2,
            "dim_B2_odd": dimB2,
            "dim_H2_odd": dimZ2 - dimB2,
            "dim_Z1_odd": dimZ1,
            "dim_H1_odd": dimH1,
            "d2_after_delta_is_zero": ok_dd,
        }

    # -- JSON export ------------------------------------------------------------------
    def export(self, extra: dict) -> dict:
        g, W, d = self.g, self.W, self.g.dim

        def lin_to_json(expr):
            expr = sp.expand(expr)
            out = {}
            for key, sym in W.gb_syms.items():
                cval = expr.coeff(sym)
                if cval != 0:
                    out[W.gb_labels[key]] = str(cval)
            const = expr.subs({s: 0 for s in W.gb_syms.values()})
            if const != 0:
                out["1"] = str(const)
            return out

        data = {
            "algebra": f"C({self.n + 1}) = osp(2|{2 * self.n})",
            "n": self.n,
            "dim": {"even": g.even_dim, "odd": g.odd_dim, "total": d},
            "conventions": {
                "oscillators": W.names,
                "oscillator_parity": W.par,
                "relations": "{a-,a+}=1, [b_k-,b_l+]=delta_kl, [b_j^s, a^sigma] = -gb[a sigma, b j s] * kappa, kappa odd central, kappa^2=0",
                "basis": "super-symmetrised quadratics: N_a = a+a- - 1/2, N_k = b_k+ b_k- + 1/2, E[root] = normal-ordered monomial",
                "weights": "coordinates (epsilon, delta_1, ..., delta_n)",
                "deformed_bracket": "[Z_i, Z_j]_gb = sum_k c[i][j][k] Z_k + s0[i][j]*1 + kappa*( sum_k gamma[i][j][k] Z_k + s1[i][j]*1 ), kappa on the LEFT",
                "coboundary": "(delta f)(X,Y) = (-1)^{p(X)}[X,f(Y)] - (-1)^{(p(X)+1)p(Y)}[Y,f(X)] - f([X,Y]); f(Z_j) = sum_m phi[m][j] Z_m",
                "gb_parameters": [W.gb_labels[k] for k in W.gb_list],
            },
            "basis": [
                {"index": i, "name": g.names[i], "parity": g.parity[i], "weight": list(g.weights[i]),
                 "oscillator_expression": g.oscillator_expression(i)}
                for i in range(d)
            ],
            "structure_constants": [
                {"i": i, "j": j, "k": k, "value": str(self.c[i][j][k])}
                for i in range(d) for j in range(d) for k in range(d) if self.c[i][j][k] != 0
            ],
            "gamma_gb": [
                {"i": i, "j": j, "k": k, "value": lin_to_json(self.gamma[i][j][k])}
                for i in range(d) for j in range(d) for k in range(d) if self.gamma[i][j][k] != 0
            ],
            "scalar_part_s1": [
                {"i": i, "j": j, "value": lin_to_json(self.s1[i][j])}
                for i in range(d) for j in range(d) if self.s1[i][j] != 0
            ],
            "f_gb": [
                {"m": m, "j": j, "phi_mj": lin_to_json(self.f[m][j])}
                for m in range(d) for j in range(d) if self.f[m][j] != 0
            ],
            "lambda_gb": [
                {"j": j, "value": lin_to_json(self.lam[j])} for j in range(d) if self.lam[j] != 0
            ],
            "d_sigma": {sigma: W.fmt(self.d_sigma(sigma)) for sigma in "+-"},
        }
        data.update(extra)
        return data


def run(n: int, outdir: str, do_cohomology=True, full_complex=False) -> dict:
    t0 = time.time()
    D = Deformation(n)
    alg = D.check_algebra()
    print(f"[n={n}] algebra checks: {alg}")
    D._gamma_lin = D.gamma_linear()
    cocycle = D.check_cocycle_symbolic()
    print(f"[n={n}] gamma_gb is a 2-cocycle (symbolic gb): {cocycle}")
    prim = D.check_primed_oscillators()
    print(f"[n={n}] primed oscillators satisfy undeformed relations: {prim}")
    f_odd = D.build_f()
    hom = D.check_homomorphism_on_g()
    print(f"[n={n}] [phi(Z_i),phi(Z_j)] = sum c phi(Z_k) exactly: {hom}")
    cob_g, cob_scalar, gamma_nonzero = D.check_coboundary_exact()
    print(f"[n={n}] gamma_gb == delta f_gb in g: {cob_g};  scalar parts == delta(-F) scalars: {cob_scalar}; gamma nonzero: {gamma_nonzero}")
    grank = D.gamma_rank()
    print(f"[n={n}] rank of gb -> gamma_gb: {grank} (4n = {4*n})")
    lin = D.solve_for_f()
    print(f"[n={n}] independent linear solve: rank(delta1)={lin['rank_delta1']}, unknowns={lin['n_unknowns_phi']}, "
          f"ker={lin['dim_ker_delta1_odd']}, solvable={all(lin['solvable_per_gb_direction'].values())}, "
          f"verified={all(lin['solution_verified_per_gb_direction'].values())}")
    coh = D.cohomology(weight_zero=True) if do_cohomology else None
    coh_full = D.cohomology(weight_zero=False) if full_complex else None
    results = {
        "verification": {
            "algebra": alg,
            "gamma_is_cocycle": cocycle,
            "gamma_linear_in_gb": True,
            "primed_oscillators_undeformed": prim,
            "f_is_odd": f_odd,
            "phi_is_homomorphism_on_g": hom,
            "gamma_equals_delta_f_in_g": cob_g,
            "scalar_parts_equal_delta_minusF_scalars": cob_scalar,
            "gamma_nonzero_for_generic_gb": gamma_nonzero,
            "rank_gb_to_gamma": grank,
            "gb_to_gamma_injective": grank == 4 * n,
            "linear_solve": lin,
            "cohomology_weight_zero": coh,
            "cohomology_full_complex": coh_full,
        },
        "conclusion": (
            "Every inhomogeneous deformation gamma_gb of C(n+1) is trivial: gamma_gb = delta f_gb for the explicit odd map f_gb; "
            "no condition on gb is needed.  gamma_gb is a NONZERO coboundary whenever gb != 0."
        ),
        "runtime_seconds": round(time.time() - t0, 1),
    }
    data = D.export(results)
    os.makedirs(outdir, exist_ok=True)
    path = os.path.join(outdir, f"cn1_n{n}.json")
    with open(path, "w") as fh:
        json.dump(data, fh, indent=1)
    print(f"[n={n}] wrote {path}  ({time.time()-t0:.1f}s)")
    return results


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, nargs="+", default=[1, 2, 3])
    ap.add_argument("--out", default="artifacts")
    ap.add_argument("--no-cohomology", action="store_true")
    ap.add_argument("--full-complex", action="store_true", help="also compute H^* on the full (non weight-zero) complex")
    args = ap.parse_args()
    summary = {}
    for n in args.n:
        summary[n] = run(n, args.out, do_cohomology=not args.no_cohomology, full_complex=args.full_complex)
    with open(os.path.join(args.out, "summary.json"), "w") as fh:
        json.dump(summary, fh, indent=1)
