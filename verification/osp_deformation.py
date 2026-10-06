"""Triviality of the inhomogeneous (gb) deformation of C(n+1) = osp(2|2n).

Everything here follows docs/math/*.md:

* A = V + C K + C kappa, V_0 = span{b_k^+, b_k^-}, V_1 = span{a^+, a^-}
  (a = a_1), K identified with 1, kappa odd central.
* Brackets of generators (super-commutators):
      [b_k^-, b_l^+] = delta_kl,  {a^-, a^+} = 1,  {a^s, a^s} = 0,
      [b_j^s, a^sigma] = -gb[sigma, j, s] * kappa.
* g = C(n+1) is the span of the quadratic monomials (normal-ordered words of
  length 2 in a, b) inside U(A); g acts on U(A)_{<=2} = g + C.1 by the
  adjoint representation, and C.1 is a trivial submodule, so "up to scalar"
  means: compare values in U(A)_{<=2} / C.1, which is isomorphic to the
  adjoint module g.
* gamma_gb(X, Y) is defined by [X, Y]_gb = [X, Y]_0 + kappa * gamma_gb(X, Y).
* (delta f)(X, Y) = (-1)^{p(X)} [X, f Y] - (-1)^{(p(X)+1) p(Y)} [Y, f X] - f([X, Y]).

Exact arithmetic (fractions.Fraction) is used for all claims; numpy is used
only for rank computations (independent confirmation / dimension counts).

Usage:  python3 verification/osp_deformation.py [n ...]      (default 1 2 3)
Writes verification/artifacts/C{n+1}_n{n}.json and a summary JSON.
"""

from __future__ import annotations

import json
import sys
from fractions import Fraction
from functools import lru_cache
from pathlib import Path

import numpy as np

KAPPA, AP, AM = 0, 1, 2  # generator indices; b_k^+ = 1 + 2k, b_k^- = 2 + 2k


def bp(k: int) -> int:
    return 1 + 2 * k


def bm(k: int) -> int:
    return 2 + 2 * k


def parity(i: int) -> int:
    return 1 if i <= AM else 0


def gen_name(i: int) -> str:
    if i == KAPPA:
        return "kappa"
    if i == AP:
        return "a+"
    if i == AM:
        return "a-"
    k = (i - 1) // 2
    return f"b{k}{'+' if i % 2 else '-'}"


def gen_root(i: int, n: int) -> list[int]:
    """Weight of a generator in the basis (epsilon, delta_1..delta_n)."""
    r = [0] * (n + 1)
    if i == AP:
        r[0] = 1
    elif i == AM:
        r[0] = -1
    elif i > AM:
        k = (i - 1) // 2
        r[k] = 1 if i % 2 else -1
    return r


def word_parity(w: tuple) -> int:
    return sum(parity(i) for i in w) % 2


def gb_params(n: int) -> list[tuple[str, int, str]]:
    """The 4n parameters gb_{sigma, j, s}."""
    return [(sg, j, s) for sg in "+-" for j in range(1, n + 1) for s in "+-"]


def gb_label(p) -> str:
    sg, j, s = p
    return f"gb[a{sg},b{j}{s}]"


# ---------------------------------------------------------------------------
# The algebra U(A) with deformation parameters gb
# ---------------------------------------------------------------------------
class UA:
    """Normal-ordered arithmetic in U(A).  Normal order: kappa < a+ < a- < b1+ < b1- < ..."""

    def __init__(self, n: int, gb: dict | None = None):
        self.n = n
        self.gb = {p: Fraction(0) for p in gb_params(n)}
        if gb:
            self.gb.update({p: Fraction(v) for p, v in gb.items()})
        self.normal = lru_cache(maxsize=None)(self._normal)

    def gen_bracket(self, i: int, j: int) -> dict:
        """Super-commutator [g_i, g_j] for i > j (always central)."""
        if j == KAPPA:
            return {}
        if (i, j) == (AM, AP):
            return {(): Fraction(1)}
        if i > AM and j in (AP, AM):  # [b_k^s, a^sigma] = -gb kappa
            k = (i - 1) // 2
            s = "+" if i % 2 else "-"
            sg = "+" if j == AP else "-"
            c = -self.gb[(sg, k, s)]
            return {(KAPPA,): c} if c else {}
        if i > AM and j > AM and i == j + 1 and j % 2 == 1:  # [b_k^-, b_k^+] = 1
            return {(): Fraction(1)}
        return {}

    def _normal(self, w: tuple) -> tuple:
        for p in range(len(w) - 1):
            x, y = w[p], w[p + 1]
            if x == y and parity(x):  # x x = (1/2)[x, x] = 0 for kappa, a+, a-
                return ()
            if x > y:
                out: dict = {}
                sign = -1 if parity(x) and parity(y) else 1
                for ww, c in self.normal(w[:p] + (y, x) + w[p + 2:]):
                    out[ww] = out.get(ww, 0) + sign * c
                for mid, c0 in self.gen_bracket(x, y).items():
                    for ww, c in self.normal(w[:p] + mid + w[p + 2:]):
                        out[ww] = out.get(ww, 0) + c0 * c
                return tuple((k, v) for k, v in out.items() if v)
        return ((w, Fraction(1)),)

    def mul(self, e1: dict, e2: dict) -> dict:
        out: dict = {}
        for w1, c1 in e1.items():
            for w2, c2 in e2.items():
                for w, c in self.normal(w1 + w2):
                    out[w] = out.get(w, 0) + c1 * c2 * c
        return {k: v for k, v in out.items() if v}

    def br(self, e1: dict, e2: dict) -> dict:
        """Super-commutator of homogeneous elements."""
        p1 = word_parity(next(iter(e1))) if e1 else 0
        p2 = word_parity(next(iter(e2))) if e2 else 0
        s = -1 if p1 and p2 else 1
        out = self.mul(e1, e2)
        for w, c in self.mul(e2, e1).items():
            out[w] = out.get(w, 0) - s * c
        return {k: v for k, v in out.items() if v}


def add(*terms) -> dict:
    out: dict = {}
    for coef, e in terms:
        for w, c in e.items():
            out[w] = out.get(w, 0) + coef * c
    return {k: v for k, v in out.items() if v}


def split_kappa(e: dict) -> tuple[dict, dict]:
    """e = plain + kappa * kpart."""
    plain, kpart = {}, {}
    for w, c in e.items():
        if w and w[0] == KAPPA:
            kpart[w[1:]] = c
        else:
            plain[w] = c
    return plain, kpart


def drop_scalars(e: dict) -> dict:
    return {w: c for w, c in e.items() if w != ()}


# ---------------------------------------------------------------------------
# Basis of g and the explicit trivialising map h_gb
# ---------------------------------------------------------------------------
def g_basis(n: int) -> list[tuple]:
    gens = [AP, AM] + [g for k in range(1, n + 1) for g in (bp(k), bm(k))]
    basis = []
    for x in gens:
        for y in gens:
            if x < y or (x == y and not parity(x)):
                basis.append((x, y))
    basis.sort(key=lambda w: (word_parity(w), w))
    return basis


def u_vector(n: int, gb: dict, sg: str) -> dict:
    """u^sigma = sum_j gb[sigma,j,-] b_j^+ - gb[sigma,j,+] b_j^-  (so that [b_j^s, u^sigma] = gb[sigma,j,s])."""
    u = {}
    for j in range(1, n + 1):
        if gb.get((sg, j, "-"), 0):
            u[(bp(j),)] = Fraction(gb[(sg, j, "-")])
        if gb.get((sg, j, "+"), 0):
            u[(bm(j),)] = -Fraction(gb[(sg, j, "+")])
    return u


def h_map(U0: UA, gb: dict):
    """Explicit odd map h: g -> U(A)_{<=2} with gamma_gb = delta h.

    Origin: a'^sigma := a^sigma + kappa u^sigma satisfies [b, a'] = 0, so in the
    primed variables the algebra is undeformed; a word X in (a, b) equals
    X' + kappa h(X') with h(a^s b) = -u^s b, h(a+ a-) = a+ u^- - a- u^+, h(b b) = 0.
    """
    n = U0.n
    u = {sg: u_vector(n, gb, sg) for sg in "+-"}

    def h_word(w: tuple) -> dict:
        if w == () or (w[0] > AM):
            return {}
        if w == (AP, AM):
            return add((1, U0.mul({(AP,): Fraction(1)}, u["-"])),
                       (-1, U0.mul({(AM,): Fraction(1)}, u["+"])))
        sg = "+" if w[0] == AP else "-"
        return add((-1, U0.mul(u[sg], {w[1:]: Fraction(1)})))

    def h(e: dict) -> dict:
        return add(*[(c, h_word(w)) for w, c in e.items()])

    return h


def delta(U0: UA, f, X: tuple, Y: tuple) -> dict:
    pX, pY = word_parity(X), word_parity(Y)
    eX, eY = {X: Fraction(1)}, {Y: Fraction(1)}
    return add(((-1) ** pX, U0.br(eX, f(eY))),
               (-((-1) ** ((pX + 1) * pY)), U0.br(eY, f(eX))),
               (-1, f(U0.br(eX, eY))))


# ---------------------------------------------------------------------------
# Main analysis for a given n
# ---------------------------------------------------------------------------
def frac_str(c: Fraction) -> str:
    return str(c.numerator) if c.denominator == 1 else f"{c.numerator}/{c.denominator}"


def coords(e: dict, index: dict) -> dict:
    """Sparse coordinates over basis of g; scalar component under key 'const'."""
    out = {}
    for w, c in e.items():
        out["const" if w == () else index[w]] = c
    return out


def analyse(n: int) -> dict:
    basis = g_basis(n)
    index = {w: i for i, w in enumerate(basis)}
    dim = len(basis)
    par = [word_parity(w) for w in basis]
    n_even = par.count(0)
    U0 = UA(n)

    # --- undeformed structure constants on g_hat = g + C.1 ----------------
    sc = {}
    for i, X in enumerate(basis):
        for j, Y in enumerate(basis):
            e = U0.br({X: Fraction(1)}, {Y: Fraction(1)})
            assert all(len(w) in (0, 2) for w in e), "bracket left U_{<=2}"
            assert all(w == () or w in index for w in e)
            if e:
                sc[(i, j)] = coords(e, index)

    params = gb_params(n)
    gamma = {}       # param -> {(i,j): coords}
    hmaps = {}       # param -> {j: coords}
    exact_mod_scalar = {}
    exact_full = {}
    for p in params:
        gb = {p: 1}
        Ug = UA(n, gb)
        h = h_map(U0, gb)
        gam = {}
        ok_mod, ok_full = True, True
        for i, X in enumerate(basis):
            for j, Y in enumerate(basis):
                e = Ug.br({X: Fraction(1)}, {Y: Fraction(1)})
                plain, kp = split_kappa(e)
                # zeroth order is unchanged; first order lies in U_{<=2}
                assert plain == U0.br({X: Fraction(1)}, {Y: Fraction(1)})
                assert all(len(w) in (0, 2) for w in kp)
                # gamma has parity p(X)+p(Y)+1
                assert all(word_parity(w) == (par[i] + par[j] + 1) % 2 for w in kp if w)
                if kp:
                    gam[(i, j)] = coords(kp, index)
                d = delta(U0, h, X, Y)
                if drop_scalars(d) != drop_scalars(kp):
                    ok_mod = False
                if d != kp:
                    ok_full = False
        gamma[p] = gam
        hmaps[p] = {j: coords(h({w: Fraction(1)}), index) for j, w in enumerate(basis)
                    if h({w: Fraction(1)})}
        # h is odd
        for j, w in enumerate(basis):
            for wv in h({w: Fraction(1)}):
                assert wv == () or word_parity(wv) != par[j]
        exact_mod_scalar[p] = ok_mod
        exact_full[p] = ok_full

    # --- independent numerical confirmation (no knowledge of h) ------------
    num = numeric_checks(n, dim, par, sc, gamma, params)

    def jsonify_sc(d):
        return {f"{i},{j}": {str(k): frac_str(v) for k, v in c.items()} for (i, j), c in d.items()}

    return {
        "algebra": f"C({n + 1}) = osp(2|{2 * n})",
        "n": n,
        "conventions": {
            "generators": "a+=a_1^+, a-=a_1^-, b{k}+=b_k^+, b{k}-=b_k^-; normal order a+ < a- < b1+ < b1- < ...",
            "relations": "[b_k^-,b_l^+]=delta_kl, {a^-,a^+}=1, {a^s,a^s}=0, [b_j^s,a^sigma]=-gb[sigma,j,s]*kappa",
            "gamma": "[X,Y]_gb = [X,Y]_0 + kappa*gamma(X,Y) (kappa on the left), computed in U(A)",
            "coboundary": "(df)(X,Y) = (-1)^p(X)[X,fY] - (-1)^((p(X)+1)p(Y))[Y,fX] - f([X,Y])",
            "coordinates": "sparse dict basis_index -> coefficient; key 'const' = multiple of 1 (scalar)",
        },
        "dimension": {"even": n_even, "odd": dim - n_even, "total": dim},
        "basis": [{"index": i, "word": [gen_name(g) for g in w], "parity": par[i],
                   "root": [a + b for a, b in zip(gen_root(w[0], n), gen_root(w[1], n))]}
                  for i, w in enumerate(basis)],
        "structure_constants": jsonify_sc(sc),
        "gb_parameters": [gb_label(p) for p in params],
        "gamma_per_unit_gb": {gb_label(p): jsonify_sc(gamma[p]) for p in params},
        "trivialising_map_h_per_unit_gb": {
            gb_label(p): {str(j): {str(k): frac_str(v) for k, v in c.items()} for j, c in hmaps[p].items()}
            for p in params},
        "exact_checks": {
            "gamma_equals_delta_h_mod_scalars": {gb_label(p): exact_mod_scalar[p] for p in params},
            "gamma_equals_delta_h_including_scalars": {gb_label(p): exact_full[p] for p in params},
        },
        "numerical_checks": num,
    }


def numeric_checks(n, dim, par, sc, gamma, params) -> dict:
    """Rank tests for gamma in Im(delta) on odd 1-cochains, in two module settings.

    mode 'mod_scalar': target module g = U_{<=2}/C.1 (adjoint), domain g.
    mode 'g_hat'     : target U_{<=2} = g + C.1, domain g_hat = g + C.1 (1 even, central).
    """
    results = {}
    for mode in ("mod_scalar", "g_hat"):
        D = dim if mode == "mod_scalar" else dim + 1
        P = par + ([] if mode == "mod_scalar" else [0])
        C = np.zeros((D, D, D))
        for (i, j), c in sc.items():
            for k, v in c.items():
                if k == "const":
                    if mode == "g_hat":
                        C[i, j, dim] = float(v)
                else:
                    C[i, j, k] = float(v)
        unk = [(k, j) for j in range(D) for k in range(D) if P[k] != P[j]]
        col = {kj: t for t, kj in enumerate(unk)}
        pairs = [(i, j) for i in range(D) for j in range(i, D)]
        M = np.zeros((len(pairs) * D, len(unk)))
        for r, (i, j) in enumerate(pairs):
            si = (-1) ** P[i]
            tij = (-1) ** ((P[i] + 1) * P[j])
            base = r * D
            for k in range(D):
                if (k, j) in col:  # si [Z_i, F_kj Z_k]
                    M[base:base + D, col[(k, j)]] += si * C[i, k]
                if (k, i) in col:  # -tij [Z_j, F_ki Z_k]
                    M[base:base + D, col[(k, i)]] -= tij * C[j, k]
            for l in range(D):  # -F([Z_i,Z_j])
                cl = C[i, j, l]
                if cl:
                    for m in range(D):
                        if (m, l) in col:
                            M[base + m, col[(m, l)]] -= cl
        rank_M = int(np.linalg.matrix_rank(M))
        G = np.zeros((len(pairs) * D, len(params)))
        for t, p in enumerate(params):
            for r, (i, j) in enumerate(pairs):
                for k, v in gamma[p].get((i, j), {}).items():
                    if k == "const":
                        if mode == "g_hat":
                            G[r * D + dim, t] = float(v)
                    else:
                        G[r * D + k, t] = float(v)
        rank_G = int(np.linalg.matrix_rank(G))
        rank_MG = int(np.linalg.matrix_rank(np.hstack([M, G])))
        rng = np.random.default_rng(n)
        g_rand = G @ rng.standard_normal(len(params))
        sol, *_ = np.linalg.lstsq(M, g_rand, rcond=None)
        # negative control: a random odd cochain (parity p(i)+p(j)+1) must NOT be a coboundary
        ctrl = np.zeros(len(pairs) * D)
        for r, (i, j) in enumerate(pairs):
            for m in range(D):
                if P[m] == (P[i] + P[j] + 1) % 2:
                    ctrl[r * D + m] = rng.standard_normal()
        rank_ctrl = int(np.linalg.matrix_rank(np.column_stack([M, ctrl])))
        # kernel identification: f_Q = ad(Q) for odd Q (first-order part of exp ad(kappa Q))
        ad_vecs = []
        for q in range(D):
            if P[q] != 1:
                continue
            vec = np.zeros(len(unk))
            for j in range(D):
                for k in range(D):
                    if C[q, j, k] and (k, j) in col:
                        vec[col[(k, j)]] = C[q, j, k]
            ad_vecs.append(vec)
        ad_vecs = np.array(ad_vecs).T
        ad_are_cocycles = bool(np.allclose(M @ ad_vecs, 0))
        ad_rank = int(np.linalg.matrix_rank(ad_vecs))
        # super-Jacobi sanity check: [Zi,[Zj,Zk]] = [[Zi,Zj],Zk] + (-1)^{p_i p_j} [Zj,[Zi,Zk]]
        jac = 0.0
        for i in range(D):
            for j in range(D):
                for k in range(D):
                    lhs = np.einsum("l,lm->m", C[j, k], C[i])
                    t1 = np.einsum("l,lm->m", C[i, j], C[:, k, :])
                    t2 = (-1) ** (P[i] * P[j]) * np.einsum("l,lm->m", C[i, k], C[j])
                    jac = max(jac, float(np.abs(lhs - t1 - t2).max()))
        results[mode] = {
            "super_jacobi_max_violation": jac,
            "negative_control_random_odd_cochain_rank_increases": rank_ctrl == rank_M + 1,
            "odd_inner_maps_ad(Q)_are_cocycles": ad_are_cocycles,
            "rank_of_odd_inner_maps": ad_rank,
            "num_unknowns_odd_f": len(unk),
            "rank_delta_on_odd_1_cochains": rank_M,
            "dim_odd_1_cocycles(kernel)": len(unk) - rank_M,
            "rank_of_gamma_family (injectivity of gb -> gamma)": rank_G,
            "rank_[delta|gamma_family]": rank_MG,
            "all_gamma_in_image_of_delta": rank_MG == rank_M,
            "random_gb_lstsq_residual": float(np.linalg.norm(M @ sol - g_rand)),
            "random_gb_gamma_norm": float(np.linalg.norm(g_rand)),
        }
    return results


def main(ns):
    out_dir = Path(__file__).resolve().parent / "artifacts"
    out_dir.mkdir(exist_ok=True)
    summary = {}
    for n in ns:
        res = analyse(n)
        (out_dir / f"C{n + 1}_n{n}.json").write_text(json.dumps(res, indent=1))
        summary[f"n={n}"] = {
            "algebra": res["algebra"],
            "dimension": res["dimension"],
            "exact_gamma_eq_delta_h_mod_scalars_all": all(res["exact_checks"]["gamma_equals_delta_h_mod_scalars"].values()),
            "exact_gamma_eq_delta_h_including_scalars_all": all(res["exact_checks"]["gamma_equals_delta_h_including_scalars"].values()),
            "numerical_checks": res["numerical_checks"],
        }
        print(json.dumps(summary[f"n={n}"], indent=1), flush=True)
    (out_dir / "summary.json").write_text(json.dumps(summary, indent=1))


if __name__ == "__main__":
    main([int(a) for a in sys.argv[1:]] or [1, 2, 3])
