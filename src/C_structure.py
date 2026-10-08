"""Structure constants of C(n+1) = osp(2|2n) in the Weyl-symmetric basis.

Usage:  python src/C_structure.py N [N ...]   -> writes data/C_{N}_structure.json
"""
from fractions import Fraction
import json
import os
import sys

import sympy

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from C_generators import OscAlgebra, ONE  # noqa: E402

SCHEMA_VERSION = "1.0-C"


def frac_str(x):
    return str(x.numerator) if x.denominator == 1 else f"{x.numerator}/{x.denominator}"


class Expander:
    """Exact coordinates of operators in the basis {W(i,j)} + {1}."""

    def __init__(self, alg, pairs):
        self.alg = alg
        self.pairs = pairs
        d = alg.dim_osc
        self.rows = [(i, j) for i in range(d) for j in range(i, d)] + [()]
        self.row_index = {w: r for r, w in enumerate(self.rows)}
        cols = [alg.sym(i, j) for (i, j) in pairs] + [{(): ONE}]
        M = sympy.zeros(len(self.rows), len(cols))
        for c, op in enumerate(cols):
            for w, v in op.items():
                assert v[1] == 0
                M[self.row_index[w], c] = sympy.Rational(v[0].numerator, v[0].denominator)
        self.M = M
        self.L = (M.T * M).inv() * M.T

    def coords(self, op):
        """Return (coeffs_c0, coeffs_ck) as lists over basis + identity."""
        v0 = sympy.zeros(len(self.rows), 1)
        vk = sympy.zeros(len(self.rows), 1)
        for w, v in op.items():
            v0[self.row_index[w], 0] = sympy.Rational(v[0].numerator, v[0].denominator)
            vk[self.row_index[w], 0] = sympy.Rational(v[1].numerator, v[1].denominator)
        x0 = self.L * v0
        xk = self.L * vk
        if self.M * x0 != v0 or self.M * xk != vk:
            raise ValueError("operator is not in the span of the basis")
        return list(x0), list(xk)


def to_frac(s):
    return Fraction(int(sympy.fraction(s)[0]), int(sympy.fraction(s)[1]))


def build(n, gb=None):
    alg = OscAlgebra(n, gb=gb)
    pairs = alg.basis_pairs()
    labels = [alg.pair_label(i, j) for (i, j) in pairs]
    parity = [(alg.par[i] + alg.par[j]) % 2 for (i, j) in pairs]
    ex = Expander(alg, pairs)
    N = len(pairs)
    basis_ops = [alg.sym(i, j) for (i, j) in pairs]
    brackets = []
    constants = []
    for a in range(N):
        for b in range(N):
            op = alg.supercommutator(basis_ops[a], parity[a], basis_ops[b], parity[b])
            if not op:
                continue
            x0, xk = ex.coords(op)
            for c in range(N + 1):
                c0, ck = sympy.nsimplify(x0[c]), sympy.nsimplify(xk[c])
                if c0 == 0 and ck == 0:
                    continue
                entry = {"X": labels[a], "Y": labels[b]}
                if c == N:
                    entry.update({"Z": "K", "coeff": frac_str(to_frac(c0)),
                                  "kappa_coeff": frac_str(to_frac(ck))})
                    constants.append(entry)
                    continue
                entry.update({"Z": labels[c], "coeff": frac_str(to_frac(c0)),
                              "kappa_coeff": frac_str(to_frac(ck))})
                brackets.append(entry)
    return {
        "schema_version": SCHEMA_VERSION,
        "algebra": {
            "family": "C",
            "m": 1,
            "n": n,
            "cartan_type": f"C({n + 1})",
            "osp": f"osp(2|{2 * n})",
            "dimension": {"even": 2 * n * n + n + 1, "odd": 4 * n,
                          "total": 2 * n * n + 5 * n + 1},
        },
        "oscillator_generators": {
            "fermions": {"m": 1, "labels": ["a_1_p", "a_1_m"], "parity": 1},
            "bosons": {"rank": n,
                       "labels": [f"b_{k}_{s}" for k in range(1, n + 1) for s in ("p", "m")],
                       "parity": 0},
        },
        "central_elements": {
            "kappa": {"parity": 1, "relation": "kappa^2 = 0"},
            "K": {"parity": 0, "identified_with": 1},
        },
        "basis": {
            "ordering": "odd first, then even; within each parity by (i,j) index order",
            "odd": [l for l, p in zip(labels, parity) if p == 1],
            "even": [l for l, p in zip(labels, parity) if p == 0],
        },
        "parity": {l: p for l, p in zip(labels, parity)},
        "generator_realization": {
            l: {"standard_form": [{"words": [alg.labels[i], alg.labels[j]], "coeff": "1/2"}],
                "parity": p,
                "note": "Weyl-symmetrized quadratic; see notation.md"}
            for l, (i, j), p in zip(labels, pairs, parity)
        },
        "structure_constants": {"brackets": brackets, "constant_terms": constants},
        "metadata": {"generated_by": "src/C_structure.py",
                     "gb_provided": gb is not None,
                     "references": ["Frappat et al. (2000), arXiv:hep-th/9607161"]},
    }


def main(argv):
    out_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data")
    for arg in argv:
        n = int(arg)
        data = build(n)
        path = os.path.join(out_dir, f"C_{n}_structure.json")
        with open(path, "w") as fh:
            json.dump(data, fh, indent=2)
        print(f"n={n}: basis={len(data['basis']['odd']) + len(data['basis']['even'])} "
              f"brackets={len(data['structure_constants']['brackets'])} "
              f"constants={len(data['structure_constants']['constant_terms'])} -> {path}")


if __name__ == "__main__":
    main(sys.argv[1:] or ["1", "2", "3"])
