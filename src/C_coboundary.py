"""Layer 4: coboundary structure for C(n+1) (I07).

For an odd linear map f (parity-reversing on the basis), the coboundary is

    (delta f)(X, Y) = (-1)^{p(X)} [X, f(Y)] - (-1)^{(p(X)+1) p(Y)} [Y, f(X)] - f([X, Y]),

with [ , ] the undeformed Schema 1 bracket (docs/math/C_coboundary_definition.md).

Parameterization: an elementary odd map f_{ij} sends Z_j to Z_i and every other
basis element to 0, where p(Z_i) != p(Z_j). A general odd map is
f = sum_{ij} phi_{ij} f_{ij}, so delta is linear in phi and the coboundary space is
spanned by {delta f_{ij}}. Layer 4 stores these basis coboundaries.

The bracket is read from data/C_{n}_structure.json (Layer 1), not from the
generator code, so the coboundary uses the file as its data source.
"""

import json
from fractions import Fraction
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"


class Schema1:
    """Undeformed bracket read from the Schema 1 file (PBW orientation stored)."""

    def __init__(self, n):
        data = json.loads((DATA / f"C_{n}_structure.json").read_text())
        self.labels = data["basis"]["odd"] + data["basis"]["even"]  # PBW order (I01)
        self.parity = data["parity"]
        self.pbw = {l: i for i, l in enumerate(self.labels)}
        self.stored = {}
        for e in data["structure_constants"]:
            self.stored.setdefault((e["X"], e["Y"]), {})[e["Z"]] = Fraction(e["coeff"])

    def bracket(self, X, Y):
        """[X, Y} as {Z: Fraction}, using graded antisymmetry for the reversed orientation."""
        if self.pbw[X] <= self.pbw[Y]:
            return dict(self.stored.get((X, Y), {}))
        sign = -1 if (self.parity[X] * self.parity[Y]) % 2 else 1
        return {z: -sign * c for z, c in self.stored.get((Y, X), {}).items()}


def add(acc, terms, scale):
    for z, c in terms.items():
        acc[z] = acc.get(z, 0) + scale * c


def elementary_coboundary(alg, i, j):
    """delta f_{ij} with f_{ij}: Z_j -> Z_i, as {(X, Y): {Z: Fraction}} for X, Y basis."""
    p = alg.parity
    labels = alg.labels
    out = {}
    for X in labels:
        for Y in labels:
            acc = {}
            # term 1: (-1)^{p(X)} [X, f(Y)], nonzero only when Y == Z_j
            if Y == j:
                add(acc, alg.bracket(X, i), (-1) ** p[X])
            # term 2: -(-1)^{(p(X)+1) p(Y)} [Y, f(X)], nonzero only when X == Z_j
            if X == j:
                add(acc, alg.bracket(Y, i), -((-1) ** ((p[X] + 1) * p[Y])))
            # term 3: -f([X, Y]); f sends Z_j to Z_i and kills the rest
            bXY = alg.bracket(X, Y)
            if j in bXY:
                acc[i] = acc.get(i, 0) - bXY[j]
            acc = {z: c for z, c in acc.items() if c != 0}
            if acc:
                out[(X, Y)] = acc
    return out


def coboundary_basis(n):
    alg = Schema1(n)
    params = []
    for j in alg.labels:
        for i in alg.labels:
            if alg.parity[i] != alg.parity[j]:
                params.append((i, j))
    return alg, params


def to_json(n):
    alg, params = coboundary_basis(n)
    maps = []
    for i, j in params:
        delta = elementary_coboundary(alg, i, j)
        # Parity check: delta f has parity p(X) + p(Y) + 1 (same as gamma).
        for (X, Y), terms in delta.items():
            for Z in terms:
                assert alg.parity[Z] == (alg.parity[X] + alg.parity[Y] + 1) % 2, (i, j, X, Y, Z)
        entries = []
        for (X, Y), terms in delta.items():
            if alg.pbw[X] > alg.pbw[Y]:
                continue  # store the PBW orientation only, as in Schema 1
            for Z, c in terms.items():
                entries.append({"X": X, "Y": Y, "Z": Z, "coeff": str(c), "sign_rule": "graded"})
        maps.append(
            {
                "phi": f"phi_{i}_{j}",
                "map": f"{j} -> {i}",
                "parity_source": alg.parity[j],
                "parity_target": alg.parity[i],
                "coboundary_entries": entries,
            }
        )
    return {
        "schema_version": "5.0",
        "algebra": {"family": "C", "m": 1, "n": n, "cartan_type": f"C({n + 1})"},
        "layer": "coboundary",
        "odd_map_parameterization": "f = sum phi_{ij} f_{ij}, f_{ij}: Z_j -> Z_i, p(Z_i) != p(Z_j)",
        "bracket_source": f"data/C_{n}_structure.json",
        "number_of_parameters": len(maps),
        "coboundary_maps": maps,
    }


def main():
    for n in (1, 2, 3):
        doc = to_json(n)
        path = DATA / f"C_{n}_coboundary.json"
        path.write_text(json.dumps(doc, indent=2) + "\n")
        print(f"wrote {path.name}: parameters={doc['number_of_parameters']}")
    return 0


if __name__ == "__main__":
    main()
