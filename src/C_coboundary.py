"""Schema 4 generator: coboundary structure for C(n+1).  Issue I07.

Following ``docs/math/C_coboundary_definition.md``, an odd linear map
``f : g -> g~`` (parity reversing) has coboundary

    (df)(X, Y) = (-1)^{p(X)} [X, f(Y)]
               - (-1)^{(p(X)+1) p(Y)} [Y, f(X)]
               - f([X, Y]) .

``f`` is parameterised by ``phi``: ``f(Z_j) = sum_i phi[i][j] Z_i``.

**Target of f.** I05 established that gamma takes values in the central
extension ``g~ = g + C*K`` (it has non-zero K-components on (odd, even) pairs),
while brackets of g never produce K.  So f is allowed to take values in ``g~``;
K occurs in ``df`` only through the ``- f([X,Y])`` term.  See the I07 Response.

This module provides
  * :func:`delta_f` -- the coboundary of an arbitrary phi,
  * :func:`canonical_f` -- the explicit f induced by the oscillator
    substitution ``a_1^sigma -> a_1^sigma + kappa * u_sigma``,
and writes ``data/C_{n}_coboundary.json``.

Usage::

    python src/C_coboundary.py        # n = 1, 2, 3
"""

from __future__ import annotations

import json
import os
import sys
from typing import Dict, List, Tuple

import sympy as sp

try:
    from .osc_algebra import (CAlgebra, Element, OscAlgebra, add_into, boson,
                              elt_add, elt_scale, gb_symbols, FERM, KAPPA)
    from .C_gamma import build_gamma, gamma_table, gb_matrix_field
    from .C_generators import algebra_field, GENERATION_DATE, REFERENCES
except ImportError:
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from osc_algebra import (CAlgebra, Element, OscAlgebra, add_into, boson,  # type: ignore
                             elt_add, elt_scale, gb_symbols, FERM, KAPPA)
    from C_gamma import build_gamma, gamma_table, gb_matrix_field  # type: ignore
    from C_generators import algebra_field, GENERATION_DATE, REFERENCES  # type: ignore

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(REPO, "data")

Vec = Dict[str, sp.Expr]
PhiMap = Dict[str, Vec]  # f(Z_j) = PhiMap[j]


# --------------------------------------------------------------------------
def vadd(a: Vec, b: Vec, scale=1) -> Vec:
    out = dict(a)
    for k, v in b.items():
        nv = sp.expand(out.get(k, 0) + scale * v)
        if nv == 0:
            out.pop(k, None)
        else:
            out[k] = nv
    return out


class Coboundary:
    """Coboundary calculus on C(n+1) using the Schema 1 bracket table."""

    def __init__(self, n: int):
        self.n = n
        self.alg = CAlgebra(n)  # undeformed: delta f uses the Schema 1 bracket
        self.order = self.alg.pbw_order
        self.par = dict(self.alg.parity)
        self.par["K"] = 0
        self.br: Dict[Tuple[str, str], Vec] = {}
        for x in self.order:
            for y in self.order:
                self.br[(x, y)] = self.alg.bracket_coeffs(x, y)

    # -- building blocks ----------------------------------------------------
    def bracket_gen_vec(self, x: str, v: Vec) -> Vec:
        """[x, v] extended linearly; K is central so it drops out."""
        out: Vec = {}
        for z, c in v.items():
            if z == "K":
                continue
            out = vadd(out, self.br[(x, z)], c)
        return out

    def apply_f(self, phi: PhiMap, v: Vec) -> Vec:
        """f(v) extended linearly; f(K) := 0."""
        out: Vec = {}
        for z, c in v.items():
            if z == "K":
                continue
            out = vadd(out, phi.get(z, {}), c)
        return out

    def delta_f(self, phi: PhiMap, x: str, y: str) -> Vec:
        px, py = self.par[x], self.par[y]
        s1 = sp.Integer(-1) ** px
        s2 = sp.Integer(-1) ** ((px + 1) * py)
        out = self.bracket_gen_vec(x, phi.get(y, {}))
        out = elt_like_scale(out, s1)
        out = vadd(out, elt_like_scale(self.bracket_gen_vec(y, phi.get(x, {})), s2), -1)
        out = vadd(out, self.apply_f(phi, self.br[(x, y)]), -1)
        return out

    def check_f_is_odd(self, phi: PhiMap) -> List[str]:
        errs = []
        for src, image in phi.items():
            for tgt, c in image.items():
                if c == 0:
                    continue
                if self.par[tgt] != (self.par[src] + 1) % 2:
                    errs.append(f"f({src}) has component {tgt} of wrong parity")
        return errs


def elt_like_scale(v: Vec, factor) -> Vec:
    return {k: sp.expand(factor * c) for k, c in v.items() if sp.expand(factor * c) != 0}


# --------------------------------------------------------------------------
# the canonical f, derived from the oscillator substitution
# --------------------------------------------------------------------------
def canonical_f(n: int, gb) -> PhiMap:
    r"""The odd map f induced by ``a_1^sigma -> a_1^sigma + kappa * u_sigma``.

    Choosing

        u_sigma = sum_j ( -gb[sigma, j, m] b_j^+  +  gb[sigma, j, p] b_j^- )

    reproduces the deformed relation ``[b_k^s, a_1^sigma] = -gb[sigma,k,s] kappa``
    exactly, because ``[b_k^+, b_k^-] = -1`` and ``[b_k^-, b_k^+] = +1``.

    Writing ``X~`` for the image of a generator under the substitution,
    ``X~ = X + kappa * f_nat(X)``, and ``gamma = delta f`` holds with
    ``f = f_nat`` exactly (sign fixed empirically and explained in the I07
    Response).
    """
    plain = OscAlgebra(n)          # normalise the kappa-linear part undeformed
    alg = CAlgebra(n)

    u: Dict[str, Element] = {}
    for sigma in ("p", "m"):
        e: Element = {}
        for j in range(1, n + 1):
            add_into(e, (KAPPA, boson(j, "p")), -gb[(sigma, j, "m")])
            add_into(e, (KAPPA, boson(j, "m")), gb[(sigma, j, "p")])
        u[sigma] = e  # this is kappa * u_sigma

    phi: PhiMap = {}
    for lab in alg.pbw_order:
        total: Element = {}
        for word, coeff in alg.realization[lab].items():
            for i, letter in enumerate(word):
                if letter not in FERM:
                    continue
                sigma = "p" if letter == "a_1_p" else "m"
                for rep_word, rep_c in u[sigma].items():
                    new = word[:i] + rep_word + word[i + 1:]
                    for w, c in plain.normalize(new).items():
                        add_into(total, w, coeff * rep_c * c)
        if not total:
            phi[lab] = {}
            continue
        f_nat = alg.decompose_kappa(total)
        phi[lab] = {k: sp.expand(v) for k, v in f_nat.items() if sp.expand(v) != 0}
    return phi


# --------------------------------------------------------------------------
def build_schema4(n: int) -> dict:
    gb, labels = gb_symbols(n)
    cob = Coboundary(n)
    alg_def = CAlgebra(n, gb)
    _a, _p, gamma_entries, _c, _l = build_gamma(n)
    gam = gamma_table(alg_def, gamma_entries)

    phi = canonical_f(n, gb)
    parity_errs = cob.check_f_is_odd(phi)

    # delta f on the stored half, and comparison against gamma
    entries: List[dict] = []
    diffs: List[str] = []
    k_entries = 0
    for i, x in enumerate(cob.order):
        for y in cob.order[i:]:
            d = cob.delta_f(phi, x, y)
            g = gam[(x, y)]
            if vadd(d, g, -1):
                diffs.append(f"({x}, {y}): delta_f - gamma = {vadd(d, g, -1)}")
            for z in cob.order + ["K"]:
                c = d.get(z)
                if c is None or sp.expand(c) == 0:
                    continue
                if z == "K":
                    k_entries += 1
                entries.append({
                    "X": x, "Y": y, "Z": z, "coeff": str(sp.expand(c)),
                    "parity_X": cob.par[x], "parity_Y": cob.par[y],
                })

    # is the K-target actually needed?
    phi_no_k = {src: {t: c for t, c in img.items() if t != "K"}
                for src, img in phi.items()}
    diffs_no_k = sum(
        1 for i, x in enumerate(cob.order) for y in cob.order[i:]
        if vadd(cob.delta_f(phi_no_k, x, y), gam[(x, y)], -1)
    )

    f_map = {
        src: {t: str(c) for t, c in img.items()}
        for src, img in phi.items() if img
    }

    return {
        "schema_version": "5.0",
        "layer": 4,
        "algebra": algebra_field(n),
        "basis": {
            "even": cob.alg.even,
            "odd": cob.alg.odd,
            "pbw_order": cob.order,
            "source": f"data/C_{n}_structure.json",
        },
        "parity": {lab: cob.par[lab] for lab in cob.order},
        "gb_matrix": gb_matrix_field(n, labels),
        "f_map": {
            "description": (
                "Odd linear map f: g -> g~ = g + C*K, f(Z_j) = sum_i phi[i][j] Z_i. "
                "Entries are keyed by source generator; coefficients are linear in gb."
            ),
            "parity_rule": "p(f(X)) = p(X) + 1",
            "target": "g + C*K (see I07 Response: gamma has K-components, so f must too)",
            "construction": (
                "Induced by the oscillator substitution a_1^sigma -> a_1^sigma "
                "+ kappa * u_sigma with u_sigma = sum_j ( -gb[sigma,j,m] b_j^+ "
                "+ gb[sigma,j,p] b_j^- ); f = f_nat where X~ = X + kappa*f_nat(X)."
            ),
            "phi": f_map,
            "nonzero_sources": len(f_map),
        },
        "coboundary": {
            "description": (
                "(df)(X,Y) = (-1)^{p(X)}[X,f(Y)] - (-1)^{(p(X)+1)p(Y)}[Y,f(X)] - f([X,Y])"
            ),
            "convention": (
                "entries stored for pbw_index(X) <= pbw_index(Y); "
                "delta f inherits graded antisymmetry from gamma"
            ),
            "entries": entries,
            "nonzero_entries_total": len(entries),
            "nonzero_pairs_total": len({(e["X"], e["Y"]) for e in entries}),
            "K_component_entries": k_entries,
        },
        "consistency": {
            "f_is_parity_reversing": not parity_errs,
            "f_parity_errors": parity_errs,
            "delta_f_equals_gamma": not diffs,
            "mismatches": diffs[:20],
            "pairs_compared": len(cob.order) * (len(cob.order) + 1) // 2,
            "K_target_is_necessary": diffs_no_k > 0,
            "mismatches_if_K_target_removed": diffs_no_k,
        },
        "metadata": {
            "generated_by": "src/C_coboundary.py",
            "generation_date": GENERATION_DATE,
            "references": REFERENCES + ["docs/math/C_coboundary_definition.md"],
        },
    }


def write_schema4(n: int) -> str:
    os.makedirs(DATA, exist_ok=True)
    path = os.path.join(DATA, f"C_{n}_coboundary.json")
    with open(path, "w") as fh:
        json.dump(build_schema4(n), fh, indent=2)
        fh.write("\n")
    return path


def main(argv: List[str]) -> int:
    ns = [int(a) for a in argv[1:]] or [1, 2, 3]
    ok = True
    for n in ns:
        path = write_schema4(n)
        with open(path) as fh:
            doc = json.load(fh)
        c, cb = doc["consistency"], doc["coboundary"]
        ok &= c["f_is_parity_reversing"] and c["delta_f_equals_gamma"]
        print(f"n={n}  f sources={doc['f_map']['nonzero_sources']}  "
              f"delta_f entries={cb['nonzero_entries_total']} "
              f"(K-components {cb['K_component_entries']})")
        print(f"      f odd={c['f_is_parity_reversing']}  "
              f"delta_f==gamma={c['delta_f_equals_gamma']} "
              f"over {c['pairs_compared']} pairs  "
              f"K-target needed={c['K_target_is_necessary']} "
              f"({c['mismatches_if_K_target_removed']} pairs would fail)  "
              f"-> {os.path.relpath(path, REPO)}")
        for m in c["mismatches"][:5]:
            print("      !", m)
    print("SUMMARY:", "PASS" if ok else "FAIL")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
