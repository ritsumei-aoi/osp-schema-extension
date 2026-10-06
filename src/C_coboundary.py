"""
C(n+1) Schema-4: coboundary structure delta f.  Issue I07.

Given an *odd* linear map f: g -> g (parity reversing), the coboundary is
(docs/math/C_coboundary_definition.md):

    (delta f)(X,Y) = (-1)^{p(X)} [X, f(Y)]
                     - (-1)^{(p(X)+1) p(Y)} [Y, f(X)]
                     - f([X,Y])

with [.,.] the undeformed C(n+1) bracket.  A deformation gamma is trivial iff gamma = delta f for
some such f (I08).

We parameterize f by coefficients phi_{src->tgt} (tgt ranges over the opposite-parity basis, plus
the central K for odd sources):  f(Z_src) = sum_tgt phi_{src->tgt} Z_tgt,  and f(K)=0.

delta f is then linear in the phi parameters.  This module emits, per (X<=Y) basis pair, the nonzero
delta f coefficients (phi-linear).

Run:  python3 src/C_coboundary.py     # writes data/C_{1,2,3}_coboundary.json
"""

from __future__ import annotations
import json
import os
import sys
from datetime import date
import sympy as sp

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import osc_algebra as oa
import C_generators as cg

DATA_DIR = cg.DATA_DIR


# --- base bracket cache ---------------------------------------------------

class Base:
    def __init__(self, n):
        self.n = n
        self.R = cg.realizations(n)
        self.P = cg.parity_map(n)
        self.even = cg.even_labels(n)
        self.odd = cg.odd_labels(n)
        self.basis = self.odd + self.even          # PBW order
        self.par = dict(self.P)
        self.par["K"] = 0
        self._bracket = {}

    def parity(self, X):
        return self.par[X]

    def bracket(self, X, Y):
        """Undeformed [X,Y} as dict{Z: sympy}, Z in basis or 'K'. K is central."""
        if X == "K" or Y == "K":
            return {}
        key = (X, Y)
        if key not in self._bracket:
            self._bracket[key] = cg.decompose(
                oa.graded_commutator(self.R[X], self.P[X], self.R[Y], self.P[Y]), self.n)
        return self._bracket[key]


# --- the odd map f --------------------------------------------------------

def phi_name(src, tgt):
    return f"phi__{src}__{tgt}"


def f_targets(base, src):
    """Opposite-parity targets for source generator `src` (plus K for odd sources)."""
    if base.parity(src) == 0:       # even source -> odd targets
        return list(base.odd)
    else:                           # odd source -> even targets (+ central K)
        return list(base.even) + ["K"]


def f_of(base, src):
    """f(src) as dict{tgt: phi_symbol}."""
    if src == "K":
        return {}
    return {tgt: sp.Symbol(phi_name(src, tgt)) for tgt in f_targets(base, src)}


def phi_symbols(base):
    syms = []
    for src in base.basis:
        for tgt in f_targets(base, src):
            syms.append(phi_name(src, tgt))
    return syms


# --- linear helpers -------------------------------------------------------

def _add(dst, Z, c):
    if c == 0:
        return
    v = dst.get(Z, sp.Integer(0)) + c
    if v == 0:
        dst.pop(Z, None)
    else:
        dst[Z] = v


def bracket_lin(base, X, vec):
    """[X, sum c_i Z_i } = sum c_i [X, Z_i}."""
    out = {}
    for Z, c in vec.items():
        for W, cc in base.bracket(X, Z).items():
            _add(out, W, c * cc)
    return out


def f_apply(base, vec):
    """f(sum c_i Z_i) = sum c_i f(Z_i)."""
    out = {}
    for Z, c in vec.items():
        for tgt, phi in f_of(base, Z).items():
            _add(out, tgt, c * phi)
    return out


def delta_f(base, X, Y):
    pX, pY = base.parity(X), base.parity(Y)
    s1 = -1 if pX % 2 else 1
    s2 = -1 if ((pX + 1) * pY) % 2 else 1
    t1 = bracket_lin(base, X, f_of(base, Y))
    t2 = bracket_lin(base, Y, f_of(base, X))
    t3 = f_apply(base, base.bracket(X, Y))
    out = {}
    for Z, c in t1.items():
        _add(out, Z, s1 * c)
    for Z, c in t2.items():
        _add(out, Z, -s2 * c)
    for Z, c in t3.items():
        _add(out, Z, -c)
    return {Z: sp.expand(c) for Z, c in out.items() if sp.expand(c) != 0}


# --- schema 4 assembly ----------------------------------------------------

def build_schema4(n):
    base = Base(n)
    order = base.basis
    pos = {lab: i for i, lab in enumerate(order)}
    records = []
    for a in range(len(order)):
        for b in range(a, len(order)):
            X, Y = order[a], order[b]
            df = delta_f(base, X, Y)
            for Z, c in sorted(df.items(), key=lambda kv: pos.get(kv[0], 10 ** 9)):
                records.append({"X": X, "Y": Y, "Z": Z, "coeff": str(c)})
    syms = phi_symbols(base)
    return {
        "schema_version": "5.0",
        "layer": 4,
        "algebra": {"family": "C", "m": 1, "n": n, "cartan_type": f"C({n + 1})"},
        "description": "Coboundary delta f of an odd linear map f: g -> g; see "
                       "docs/math/C_coboundary_definition.md.",
        "f_map": {
            "parity": "odd",
            "parameterization": "f(Z_src) = sum_tgt phi__src__tgt * Z_tgt  (tgt opposite parity; "
                                "K allowed for odd sources); f(K)=0",
            "num_parameters": len(syms),
            "parameters": syms,
        },
        "coboundary_formula": "(delta f)(X,Y) = (-1)^{pX}[X,f(Y)] - (-1)^{(pX+1)pY}[Y,f(X)] - f([X,Y])",
        "delta_f": records,
        "metadata": {
            "generated_by": "src/C_coboundary.py",
            "generation_date": date.today().isoformat(),
            "references": ["docs/math/C_coboundary_definition.md"],
        },
    }


def generate_all():
    os.makedirs(DATA_DIR, exist_ok=True)
    for n in (1, 2, 3):
        data = build_schema4(n)
        path = os.path.join(DATA_DIR, f"C_{n}_coboundary.json")
        with open(path, "w") as f:
            json.dump(data, f, indent=2)
        print(f"wrote {path}  (#phi={data['f_map']['num_parameters']}, "
              f"#delta_f_records={len(data['delta_f'])})")


if __name__ == "__main__":
    generate_all()
