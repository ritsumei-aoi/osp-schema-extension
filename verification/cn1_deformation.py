"""Verification engine for the triviality of the inhomogeneous (gb) deformation
of C(n+1) = osp(2|2n), following docs/math/*.md.

Model
-----
* A = V + C K + C kappa, K = 1 (even central), kappa odd central, kappa^2 = 0.
* Oscillators: a+ , a- (odd, {a-,a+} = 1), b_j^+ , b_j^- (even, [b_j^-, b_l^+] = delta_jl).
* Deformation: [b_j^s, a^sigma] = -gb[sigma, j, s] * kappa.
* U(A) is modelled by normal-ordered words (order: kappa < a+ < a- < b1+ < b1- < ...),
  with exact rational coefficients.
* g = span of quadratic normal-ordered monomials (a+a-, a^sigma b_j^s, b b), taken
  modulo scalars ("up to scalar" = equality in the adjoint representation, where the
  centre C*1 acts trivially).

Run:  python3 verification/cn1_deformation.py   (writes verification/artifacts/*.json)
"""

from __future__ import annotations

import json
import random
import sys
from fractions import Fraction
from functools import lru_cache
from itertools import product
from pathlib import Path

import numpy as np

KAPPA = "k"
PRIME = 2_147_483_647  # for exact modular rank computations


# ---------------------------------------------------------------------------
# Super-oscillator algebra U(A) with gb deformation
# ---------------------------------------------------------------------------

def gb_labels(n):
    """All 4n deformation parameters (sigma, j, s)."""
    return [(sig, j, s) for sig in "+-" for j in range(1, n + 1) for s in "+-"]


def gb_key(lbl):
    sig, j, s = lbl
    return f"gb[a1{sig},b{j}{s}]"


class OscillatorAlgebra:
    def __init__(self, n, gb=None):
        self.n = n
        self.gb = {k: Fraction(v) for k, v in (gb or {}).items() if v != 0}
        self.gens = [KAPPA, "a+", "a-"] + [f"b{j}{s}" for j in range(1, n + 1) for s in "+-"]
        self.order = {g: i for i, g in enumerate(self.gens)}
        self._normal = lru_cache(maxsize=None)(self._normal_order)

    @staticmethod
    def parity(g):
        return 1 if g in (KAPPA, "a+", "a-") else 0

    def word_parity(self, w):
        return sum(self.parity(g) for g in w) % 2

    def gen_bracket(self, x, y):
        """Supercommutator [x, y] of two generators, as an element (dict)."""
        if x == KAPPA or y == KAPPA:
            return {}
        if x[0] == "b" and y[0] == "b":
            jx, sx, jy, sy = int(x[1:-1]), x[-1], int(y[1:-1]), y[-1]
            if jx != jy or sx == sy:
                return {}
            return {(): Fraction(1 if sx == "-" else -1)}
        if x[0] == "a" and y[0] == "a":
            return {(): Fraction(1)} if x != y else {}
        # mixed: [b_j^s, a^sigma] = -gb kappa ; [a^sigma, b_j^s] = +gb kappa
        if x[0] == "b":
            c = -self.gb.get((y[1], int(x[1:-1]), x[-1]), 0)
        else:
            c = self.gb.get((x[1], int(y[1:-1]), y[-1]), 0)
        return {(KAPPA,): Fraction(c)} if c else {}

    def _normal_order(self, word):
        for i in range(len(word) - 1):
            x, y = word[i], word[i + 1]
            ox, oy = self.order[x], self.order[y]
            if ox > oy or (ox == oy and self.parity(x) == 1):
                out = {}
                pre, post = word[:i], word[i + 2:]
                if ox > oy:  # x y = (-1)^{p(x)p(y)} y x + [x, y]
                    sign = -1 if self.parity(x) * self.parity(y) else 1
                    add_elem(out, self._normal(pre + (y, x) + post), sign)
                    br = self.gen_bracket(x, y)
                else:  # odd x: x x = [x, x] / 2
                    br = {m: c / 2 for m, c in self.gen_bracket(x, x).items()}
                for m, c in br.items():
                    add_elem(out, self._normal(pre + m + post), c)
                return out
        return {word: Fraction(1)}

    def mul(self, A, B):
        out = {}
        for wa, ca in A.items():
            for wb, cb in B.items():
                add_elem(out, self._normal(wa + wb), ca * cb)
        return out

    def elem_parity(self, A):
        ps = {self.word_parity(w) for w in A}
        assert len(ps) <= 1, "inhomogeneous element"
        return ps.pop() if ps else 0

    def bracket(self, A, B):
        pa, pb = self.elem_parity(A), self.elem_parity(B)
        out = self.mul(A, B)
        add_elem(out, self.mul(B, A), -1 if not (pa and pb) else 1)
        return clean(out)


def add(d, k, c):
    if c:
        v = d.get(k, 0) + c
        if v:
            d[k] = v
        else:
            d.pop(k, None)


def add_elem(d, e, s=1):
    for k, c in e.items():
        add(d, k, s * c)


def clean(d):
    return {k: v for k, v in d.items() if v != 0}


# ---------------------------------------------------------------------------
# The Lie superalgebra g = C(n+1) inside U(A), modulo scalars
# ---------------------------------------------------------------------------

def basis(n):
    """Basis of g (mod scalars): normal-ordered quadratic monomials."""
    bs = [f"b{j}{s}" for j in range(1, n + 1) for s in "+-"]
    even = [("a+", "a-")] + [(bs[i], bs[k]) for i in range(len(bs)) for k in range(i, len(bs))]
    odd = [(a, b) for a in ("a+", "a-") for b in bs]
    return even + odd


def name(w):
    return "*".join(w) if w else "1"


def split(alg, e, idx):
    """Split a U(A) element into (kappa-free part, kappa part) as coordinate dicts
    over the basis of g, plus their scalar parts. Asserts nothing else occurs."""
    out = {"g0": {}, "s0": Fraction(0), "g1": {}, "s1": Fraction(0)}
    for w, c in e.items():
        kap = bool(w) and w[0] == KAPPA
        rest = w[1:] if kap else w
        assert KAPPA not in rest
        if rest == ():
            out["s1" if kap else "s0"] += c
        else:
            assert rest in idx, f"element outside g: {w}"
            out["g1" if kap else "g0"][idx[rest]] = c
    return out


def structure(n, gb):
    """Return (basis, parities, undeformed constants c, gamma, gamma scalar parts)."""
    B = basis(n)
    idx = {w: i for i, w in enumerate(B)}
    alg = OscillatorAlgebra(n, gb)
    par = [alg.word_parity(w) for w in B]
    c, gamma, c0, gamma0 = {}, {}, {}, {}
    for i, j in product(range(len(B)), repeat=2):
        sp = split(alg, alg.bracket({B[i]: 1}, {B[j]: 1}), idx)
        if sp["g0"]:
            c[(i, j)] = sp["g0"]
        if sp["s0"]:
            c0[(i, j)] = sp["s0"]
        if sp["g1"]:
            gamma[(i, j)] = sp["g1"]
        if sp["s1"]:
            gamma0[(i, j)] = sp["s1"]
    return B, par, c, gamma, c0, gamma0


# ---------------------------------------------------------------------------
# Coboundary operator  (delta f)(X,Y) = (-1)^{pX}[X,fY] - (-1)^{(pX+1)pY}[Y,fX] - f([X,Y])
# ---------------------------------------------------------------------------

def odd_unknowns(par):
    """Unknowns phi_{ij} (f(Z_j) = sum_i phi_ij Z_i) with p(Z_i) != p(Z_j)."""
    N = len(par)
    return [(i, j) for j in range(N) for i in range(N) if par[i] != par[j]]


def delta_rows(par, c):
    """Sparse linear map phi -> delta f, rows indexed by (X, Y, k)."""
    N = len(par)
    unk = odd_unknowns(par)
    uidx = {u: t for t, u in enumerate(unk)}
    rows = {}

    def put(key, u, v):
        r = rows.setdefault(key, {})
        r[u] = r.get(u, 0) + v

    for X, Y in product(range(N), repeat=2):
        pX, pY = par[X], par[Y]
        s1 = -1 if pX else 1
        s2 = -1 if ((pX + 1) * pY) % 2 else 1
        for i in range(N):  # (-1)^pX [X, f(Y)] : f(Y) = sum_i phi_{iY} Z_i
            if par[i] != pY:
                for k, v in c.get((X, i), {}).items():
                    put((X, Y, k), uidx[(i, Y)], s1 * v)
        for i in range(N):  # -(-1)^{(pX+1)pY} [Y, f(X)]
            if par[i] != pX:
                for k, v in c.get((Y, i), {}).items():
                    put((X, Y, k), uidx[(i, X)], -s2 * v)
        for m, v in c.get((X, Y), {}).items():  # - f([X,Y])
            for k in range(N):
                if par[k] != par[m]:
                    put((X, Y, k), uidx[(k, m)], -v)
    rows = {key: {u: v for u, v in r.items() if v} for key, r in rows.items()}
    return unk, {key: r for key, r in rows.items() if r}


def apply_delta(par, c, f):
    """Evaluate delta f for f given as {j: {i: coef}} (mod scalars)."""
    N = len(par)
    out = {}
    for X, Y in product(range(N), repeat=2):
        pX, pY = par[X], par[Y]
        s1 = -1 if pX else 1
        s2 = -1 if ((pX + 1) * pY) % 2 else 1
        res = {}
        for i, v in f.get(Y, {}).items():
            for k, w in c.get((X, i), {}).items():
                add(res, k, s1 * v * w)
        for i, v in f.get(X, {}).items():
            for k, w in c.get((Y, i), {}).items():
                add(res, k, -s2 * v * w)
        for m, v in c.get((X, Y), {}).items():
            for k, w in f.get(m, {}).items():
                add(res, k, -v * w)
        if res:
            out[(X, Y)] = res
    return out


# ---------------------------------------------------------------------------
# Explicit trivialising map (oscillator redefinition b -> b + kappa * l(b))
# ---------------------------------------------------------------------------

def ell(gb, j, s):
    """l(b_j^s) = gb[-,j,s] a+ + gb[+,j,s] a-."""
    e = {}
    add(e, ("a+",), Fraction(gb.get(("-", j, s), 0)))
    add(e, ("a-",), Fraction(gb.get(("+", j, s), 0)))
    return e


def substituted_generator(n, gb, g):
    """Image of a generator under b -> b' = b + kappa l(b), a -> a."""
    e = {(g,): Fraction(1)}
    if g[0] == "b":
        for w, c in ell(gb, int(g[1:-1]), g[-1]).items():
            add(e, (KAPPA,) + w, c)
    return e


def phi_map(n, gb):
    """phi(X) := kappa-part of X(o'), computed in the deformed algebra.
    Returns (phi mod scalars, scalar parts, check that o' obey undeformed CCR/CAR)."""
    B = basis(n)
    idx = {w: i for i, w in enumerate(B)}
    alg = OscillatorAlgebra(n, gb)
    alg0 = OscillatorAlgebra(n, {})
    # 1) o' satisfy the undeformed relations
    gens = alg.gens[1:]
    ok = True
    for x, y in product(gens, repeat=2):
        lhs = alg.bracket(substituted_generator(n, gb, x), substituted_generator(n, gb, y))
        rhs = alg0.gen_bracket(x, y)
        ok &= clean(lhs) == clean(rhs)
    # 2) phi
    phi, phi0 = {}, {}
    for t, w in enumerate(B):
        e = {(): Fraction(1)}
        for g in w:
            e = alg.mul(e, substituted_generator(n, gb, g))
        sp = split(alg, e, idx)
        assert sp["g0"] == {t: 1}
        if sp["g1"]:
            phi[t] = sp["g1"]
        if sp["s1"]:
            phi0[t] = sp["s1"]
    return phi, phi0, ok


def exact_in_UA(n, gb):
    """Stronger check without quotienting by scalars: with phi_full(X) = full kappa-part
    of X(o') (scalars included) and phi_full(1) = 0, verify in U(A) that
    kappa-part of [X,Y]_gb  ==  -( (-1)^pX [X,phiY]_0 - (-1)^{(pX+1)pY} [Y,phiX]_0 - phi([X,Y]_0) )."""
    B = basis(n)
    alg, alg0 = OscillatorAlgebra(n, gb), OscillatorAlgebra(n, {})
    phi = {}
    for w in B:
        e = {(): Fraction(1)}
        for g in w:
            e = alg.mul(e, substituted_generator(n, gb, g))
        phi[w] = {m[1:]: c for m, c in e.items() if m and m[0] == KAPPA}
    for X, Y in product(B, repeat=2):
        full = alg.bracket({X: 1}, {Y: 1})
        gam = {m[1:]: c for m, c in full.items() if m and m[0] == KAPPA}
        pX, pY = alg.word_parity(X), alg.word_parity(Y)
        d = {}
        add_elem(d, alg0.bracket({X: 1}, phi[Y]) if phi[Y] else {}, -1 if pX else 1)
        add_elem(d, alg0.bracket({Y: 1}, phi[X]) if phi[X] else {}, 1 if ((pX + 1) * pY) % 2 else -1)
        for m, c in alg0.bracket({X: 1}, {Y: 1}).items():
            if m:  # phi(1) = 0
                add_elem(d, phi[m], -c)
        if clean(gam) != clean({m: -c for m, c in d.items()}):
            return False
    return True


def f_closed_form(n, gb):
    """Hand-derived f = -phi (mod scalars), see mathematical_proof.md, Thm 1."""
    B = basis(n)
    idx = {w: i for i, w in enumerate(B)}
    alg0 = OscillatorAlgebra(n, {})
    f = {}
    for t, w in enumerate(B):
        res = {}
        if w[0][0] == "b":  # f(b_j^s b_k^t) = -(l(b_j^s) b_k^t + l(b_k^t) b_j^s)
            for u, v in ((w[0], w[1]), (w[1], w[0])):
                for m, c in alg0.mul(ell(gb, int(u[1:-1]), u[-1]), {(v,): 1}).items():
                    add(res, m, -c)
        elif w[1][0] == "b":  # f(a^sig b_k^t) = a^sig l(b_k^t)
            for m, c in alg0.mul({(w[0],): 1}, ell(gb, int(w[1][1:-1]), w[1][-1])).items():
                add(res, m, c)
        res = {idx[m]: c for m, c in res.items() if m}  # drop scalars
        if res:
            f[t] = res
    return f


# ---------------------------------------------------------------------------
# Linear algebra helpers
# ---------------------------------------------------------------------------

def to_mod(x):
    x = Fraction(x)
    return (x.numerator % PRIME) * pow(x.denominator % PRIME, -1, PRIME) % PRIME


def rank_mod_p(M):
    """Exact rank over GF(p) of an integer matrix (numpy int64 entries in [0,p))."""
    M = M.copy() % PRIME
    M = M[np.any(M != 0, axis=1)]
    r = 0
    rows, cols = M.shape
    for col in range(cols):
        if r == rows:
            break
        nz = np.nonzero(M[r:, col])[0]
        if nz.size == 0:
            continue
        piv = r + nz[0]
        M[[r, piv]] = M[[piv, r]]
        inv = pow(int(M[r, col]), -1, PRIME)
        M[r] = (M[r] * inv) % PRIME
        others = np.nonzero(M[:, col])[0]
        others = others[others != r]
        if others.size:
            fac = M[others, col].reshape(-1, 1)
            M[others] = (M[others] - (fac * M[r]) % PRIME) % PRIME
        r += 1
        # drop rows that became zero to keep things small
        keep = np.ones(M.shape[0], bool)
        keep[r:] = np.any(M[r:] != 0, axis=1)
        M = M[keep]
        rows = M.shape[0]
    return r


def dense(rows, ncols, extra_cols=()):
    keys = set(rows)
    for e in extra_cols:
        keys |= set(e)
    keys = sorted(keys)
    kidx = {k: t for t, k in enumerate(keys)}
    M = np.zeros((len(keys), ncols + len(extra_cols)), dtype=np.int64)
    Mf = np.zeros(M.shape)
    for key, r in rows.items():
        for u, v in r.items():
            M[kidx[key], u] = to_mod(v)
            Mf[kidx[key], u] = float(v)
    for t, e in enumerate(extra_cols):
        for key, v in e.items():
            M[kidx[key], ncols + t] = to_mod(v)
            Mf[kidx[key], ncols + t] = float(v)
    return M, Mf


def flatten(gamma):
    return {(X, Y, k): v for (X, Y), comp in gamma.items() for k, v in comp.items()}


# ---------------------------------------------------------------------------
# Main driver
# ---------------------------------------------------------------------------

def frac_json(x):
    x = Fraction(x)
    return str(x) if x.denominator != 1 else int(x)


def sparse_json(B, d):
    return [
        {"X": name(B[X]), "Y": name(B[Y]),
         "value": {name(B[k]): frac_json(v) for k, v in sorted(comp.items())}}
        for (X, Y), comp in sorted(d.items())
    ]


def map_json(B, f):
    return {name(B[j]): {name(B[i]): frac_json(v) for i, v in sorted(comp.items())}
            for j, comp in sorted(f.items())}


def run(n, rng):
    labels = gb_labels(n)
    B, par, c, _, c0, _ = structure(n, {})
    N = len(B)
    neven = par.count(0)
    report = {
        "algebra": f"C({n + 1}) = osp(2|{2 * n})",
        "n": n,
        "conventions": {
            "kappa": "odd central, kappa^2 = 0, written on the LEFT: [X,Y]_gb = [X,Y]_0 + kappa*gamma(X,Y)",
            "deformation": "[b_j^s, a1^sigma] = -gb[sigma,j,s] kappa",
            "basis": "normal-ordered quadratic monomials (order a+ < a- < b1+ < b1- < ...); g taken modulo C*1",
            "coboundary": "(delta f)(X,Y) = (-1)^pX [X,fY] - (-1)^((pX+1)pY) [Y,fX] - f([X,Y])",
            "up_to_scalar": "equalities are in g = (quadratic span)/C*1, i.e. in the adjoint representation",
        },
        "basis": [{"index": t, "name": name(w), "parity": par[t]} for t, w in enumerate(B)],
        "superdimension": {"even": neven, "odd": N - neven, "total": N},
        "structure_constants": sparse_json(B, c),
        "structure_constants_scalar_part": [
            {"X": name(B[X]), "Y": name(B[Y]), "value": frac_json(v)} for (X, Y), v in sorted(c0.items())
        ],
    }
    assert (neven, N - neven) == (2 * n * n + n + 1, 4 * n)

    # gamma for each unit gb, verification of triviality
    unk, drows = delta_rows(par, c)
    gammas, per_gb = [], {}
    all_ok = True
    for lbl in labels:
        gb = {lbl: 1}
        _, _, _, gamma, _, gamma0 = structure(n, gb)
        phi, phi0, osc_ok = phi_map(n, gb)
        f = {j: {i: -v for i, v in comp.items()} for j, comp in phi.items()}
        f_cf = f_closed_form(n, gb)
        df = apply_delta(par, c, f)
        ok = clean(flatten(df)) == clean(flatten(gamma)) and f == f_cf and osc_ok
        all_ok &= ok
        gammas.append(flatten(gamma))
        per_gb[gb_key(lbl)] = {
            "gamma": sparse_json(B, gamma),
            "gamma_scalar_part_dropped_up_to_scalar": [
                {"X": name(B[X]), "Y": name(B[Y]), "value": frac_json(v)} for (X, Y), v in sorted(gamma0.items())
            ],
            "trivialising_f": map_json(B, f),
            "redefined_oscillators_satisfy_undeformed_relations": osc_ok,
            "f_matches_closed_form": f == f_cf,
            "gamma_equals_delta_f_exactly_mod_scalars": clean(flatten(df)) == clean(flatten(gamma)),
            "num_nonzero_gamma_pairs": len(gamma),
            "num_pairs_with_scalar_part": len(gamma0),
        }

    # random generic gb (all 4n parameters non-zero simultaneously)
    gb_rand = {lbl: Fraction(rng.randint(-9, 9) or 1, rng.randint(1, 5)) for lbl in labels}
    _, _, _, gamma_r, _, _ = structure(n, gb_rand)
    phi_r, _, osc_r = phi_map(n, gb_rand)
    f_r = {j: {i: -v for i, v in comp.items()} for j, comp in phi_r.items()}
    lin = {}
    for lbl, g in zip(labels, gammas):
        for k, v in g.items():
            add(lin, k, gb_rand[lbl] * v)
    exact_ok = exact_in_UA(n, gb_rand)
    rand_ok = (clean(flatten(apply_delta(par, c, f_r))) == clean(flatten(gamma_r))
               and clean(flatten(gamma_r)) == lin and osc_r and f_r == f_closed_form(n, gb_rand))
    all_ok &= rand_ok

    # negative control: a random odd 2-cochain (same support pattern size) must NOT be a coboundary
    control = {}
    for (X, Y), comp in structure(n, gb_rand)[3].items():
        for k in comp:
            control[(X, Y, k)] = Fraction(rng.randint(1, 9))
    Mc, Mcf = dense(drows, len(unk), [control])
    control_in_image = rank_mod_p(Mc) == rank_mod_p(Mc[:, :len(unk)])

    # ranks (exact mod p, plus floating-point cross-check)
    M, Mf = dense(drows, len(unk), gammas)
    nu = len(unk)
    r_delta = rank_mod_p(M[:, :nu])
    r_aug = rank_mod_p(M)
    r_gamma = rank_mod_p(M[:, nu:])
    rf_delta = int(np.linalg.matrix_rank(Mf[:, :nu]))
    rf_aug = int(np.linalg.matrix_rank(Mf))
    rf_gamma = int(np.linalg.matrix_rank(Mf[:, nu:]))

    report["checks"] = {
        "all_unit_gb_trivial_with_explicit_f": all_ok,
        "random_generic_gb": {"gb": {gb_key(k): frac_json(v) for k, v in gb_rand.items()},
                              "gamma_equals_delta_f": rand_ok,
                              "gamma_is_linear_in_gb": clean(flatten(gamma_r)) == lin,
                              "exact_identity_in_U(A)_including_scalars": exact_ok},
        "linear_algebra": {
            "num_odd_maps_f (unknowns phi_ij)": nu,
            "rank_delta_on_odd_maps (mod p / float)": [r_delta, rf_delta],
            "dim_ker_delta (odd 1-cocycles)": nu - r_delta,
            "rank_[delta | gamma_e for all 4n gb]": [r_aug, rf_aug],
            "rank_of_gb_to_gamma_map": [r_gamma, rf_gamma],
            "num_gb_parameters": 4 * n,
            "every_gamma_gb_in_image_of_delta": r_aug == r_delta and rf_aug == rf_delta,
            "gb_to_gamma_injective": r_gamma == 4 * n,
            "negative_control_random_cochain_in_image (expected false)": control_in_image,
        },
        "pairs_with_kappa_scalar_term_in_gamma (per unit gb)": sorted(
            {v["num_pairs_with_scalar_part"] for v in per_gb.values()}),
    }
    report["per_gb_parameter"] = per_gb
    return report


def main():
    rng = random.Random(20261006)
    out = Path(__file__).resolve().parent / "artifacts"
    out.mkdir(exist_ok=True)
    ns = [int(a) for a in sys.argv[1:]] or [1, 2, 3]
    summary = {}
    for n in ns:
        rep = run(n, rng)
        (out / f"cn1_n{n}.json").write_text(json.dumps(rep, indent=1))
        summary[f"n={n}"] = {"algebra": rep["algebra"], "superdimension": rep["superdimension"], **rep["checks"]}
        print(json.dumps(summary[f"n={n}"], indent=1))
    (out / "summary.json").write_text(json.dumps(summary, indent=1))


if __name__ == "__main__":
    main()
