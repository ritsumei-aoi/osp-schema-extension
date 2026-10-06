"""Schema 2: inhomogeneous (gb) deformation of C(n+1) = osp(2|2n).

Deformed oscillator relation (docs/math/C_inhomogeneous_definition.md):
    [b_j^s, a_1^sigma] = b a - a b = -gb_{sigma,j,s} kappa.
Generators are Weyl-symmetrised quadratics in the deformed algebra, so that
    [X,Y}_gamma = [X,Y}_0 + kappa * gamma(X,Y)   with gamma(X,Y) in g
(no kappa*K central residual).  For the odd generators this means
    E = (a b + b a)/2 = a b - (1/2) gb_{sigma,k,tau} kappa     (normal-ordered a b).
gamma is linear in gb (kappa^2 = 0), so it is computed per unit parameter.

usage: python src/gamma.py     # writes data/C_{n}_gamma.json
"""
import json
import os
import sys
from fractions import Fraction

sys.path.insert(0, os.path.dirname(__file__))
from C_generators import CAlgebra, schema1  # noqa: E402
from oscalg import KAPPA, OscAlgebra, make_decomposer  # noqa: E402

PM = ("p", "m")


def param_keys(n):
    """gb index (sigma, j, s) in a fixed order: row a_1_p then a_1_m; columns b_1_p, b_1_m, ..."""
    return [(sg, j, s) for sg in PM for j in range(1, n + 1) for s in PM]


def param_name(key):
    sg, j, s = key
    return f"gb_a_1_{sg}_b_{j}_{s}"


class DeformedC:
    """C(n+1) realized in the oscillator algebra deformed by gb (dict key -> number)."""

    def __init__(self, n, gb=None, symmetrize=True):
        """symmetrize=False keeps the normal-ordered product a b as the odd generator (used only in I08 to
        exhibit the central kappa*K residual); the default Weyl-symmetrised choice is the one of Schema 2."""
        self.n = n
        base = CAlgebra(n)
        self.labels, self.parity = base.labels, base.parity
        self.even, self.odd = base.even, base.odd
        self.gb = {k: Fraction(v) for k, v in (gb or {}).items() if v}
        self.osc = OscAlgebra(self.gb)
        self.real = {}
        for l in self.labels:
            r = dict(base.real[l])
            if l in self.odd and symmetrize:
                (aw, bw), = r.keys()
                key = ("p" if aw == 1 else "m", (bw - 3) // 2 + 1, "p" if (bw - 3) % 2 == 0 else "m")
                g = self.gb.get(key, 0)
                if g:
                    r[(KAPPA,)] = -g / 2
            self.real[l] = r
        N = len(self.labels)
        vecs = [self.real[l] for l in self.labels]
        kvecs = []
        for l in self.labels:
            kv = {}
            for w, c in self.real[l].items():
                OscAlgebra._add(kv, self.osc.normal((KAPPA,) + w), c)
            kvecs.append(kv)
        self.N = N
        self.decompose = make_decomposer(vecs + kvecs + [{(KAPPA,): Fraction(1)}])

    def bracket(self, X, Y):
        """Return (g0, gamma): dicts label -> coeff with [X,Y} = g0 + kappa*gamma (+ last_central * kappa*K)."""
        v = self.osc.bracket(self.real[X], self.parity[X], self.real[Y], self.parity[Y])
        co, resid = self.decompose(v)
        if resid:
            raise ValueError(f"[{X},{Y}] not in g + kappa g: residual {resid}")
        g0 = {self.labels[i]: c for i, c in co.items() if i < self.N}
        gam = {self.labels[i - self.N]: c for i, c in co.items() if self.N <= i < 2 * self.N}
        self.last_central = co.get(2 * self.N, Fraction(0))  # coefficient of kappa*K (zero if symmetrised)
        return g0, gam


def gamma_table(n):
    """{(X,Y): {param_key: {Z: coeff}}} for non-zero gamma, one unit parameter at a time."""
    labels = CAlgebra(n).labels
    table = {}
    for key in param_keys(n):
        alg = DeformedC(n, {key: 1})
        for X in labels:
            for Y in labels:
                g0, gam = alg.bracket(X, Y)
                if gam:
                    table.setdefault((X, Y), {})[key] = gam
    return table


def schema2(n):
    s1 = schema1(n)
    keys = param_keys(n)
    table = gamma_table(n)
    entries = []
    for (X, Y), per in table.items():
        zs = {}
        for key, gam in per.items():
            for Z, c in gam.items():
                zs.setdefault(Z, []).append({"param": param_name(key), "coeff": str(c)})
        for Z, terms in zs.items():
            entries.append({"X": X, "Y": Y, "Z": Z, "gamma": terms})
    return {
        "schema_version": "5.0",
        "layer": 2,
        "algebra": s1["algebra"],
        "basis": s1["basis"],
        "parity": s1["parity"],
        "central_elements": s1["central_elements"],
        "inhomogeneous_deformation": {
            "description": "[b_j^s, a_1^sigma] = -gb_{sigma,j,s} kappa; [X,Y}_gamma = [X,Y}_0 + kappa*gamma(X,Y); "
                           "gamma linear in gb; odd generators Weyl-symmetrised",
            "gb_matrix": {
                "rows": ["a_1_p", "a_1_m"],
                "cols": [f"b_{j}_{s}" for j in range(1, n + 1) for s in PM],
                "shape": [2, 2 * n],
                "parity": 1,
                "parameters": [param_name(k) for k in keys],
            },
            "gamma_convention": "kappa placed to the left: kappa*Z; gamma(X,Y) has parity p(X)+p(Y)+1",
            "gamma_structure": entries,
        },
        "metadata": {"generated_by": "src/gamma.py", "generation_date": "2026-10-06", "n": n,
                     "base_file": f"C_{n}_structure.json"},
    }


def main():
    out = os.path.join(os.path.dirname(__file__), "..", "data")
    for n in (1, 2, 3):
        d = schema2(n)
        with open(os.path.join(out, f"C_{n}_gamma.json"), "w") as f:
            json.dump(d, f, indent=1, ensure_ascii=False)
        print(n, len(d["inhomogeneous_deformation"]["gamma_structure"]), "non-zero gamma entries")


if __name__ == "__main__":
    main()
