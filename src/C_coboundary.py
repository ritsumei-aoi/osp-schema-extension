"""
C_coboundary.py — Generate Schema 4 (Coboundary Structure) JSON for C(n+1) = osp(2|2n).

Computes the coboundary delta_f for an odd linear map f: g -> g.

The coboundary formula:
  (delta_f)(X, Y) = (-1)^{p(X)} [X, f(Y)] - (-1)^{(p(X)+1)*p(Y)} [Y, f(X)] - f([X, Y])

where [.,.] is the standard Lie superalgebra bracket (from Schema 1).

We choose f to be the "natural" odd linear map that maps each even generator to
an odd generator via the epsilon-direction, motivated by the structure of the
inhomogeneous deformation.

Parameterization of f:
  f(Z_j) = sum_i phi_ij Z_i
  where Z_i runs over the basis and phi_ij = 0 unless p(Z_i) + p(Z_j) = 1 (mod 2).

For our computation, we choose a specific f that captures the deformation structure:
  - f(H_k) = phi_k * E_eps1_del{1}_{pp}  (maps Cartan to a specific odd generator)
  - f(E_even_root) = psi * E_eps1_del{...}  (maps even roots to odd generators)

For the purposes of I07, we compute the coboundary for the "minimal" choice:
  f(H_{n+1}) = 1  (mapped to E_eps1_del{n}_{pm}: the simple fermionic root generator)
  f(E_{2del_n}_p) = 1 (mapped to E_eps1_del{n}_{pp})
  All other f values = 0.

This is the simplest non-trivial choice that illuminates the triviality condition.
The full parameterization is described in the phi_coefficients field of Schema 4.
"""

from __future__ import annotations
import json
import datetime
import os
from fractions import Fraction


def load(n: int, suffix: str) -> dict:
    data_dir = os.path.join(os.path.dirname(__file__), "..", "data")
    path = os.path.join(data_dir, f"C_{n}_{suffix}.json")
    with open(path) as f:
        return json.load(f)


def build_bracket_table(schema1: dict) -> dict:
    """Build bracket table {(X,Y): {Z: Fraction}} from Schema 1."""
    table = {}
    for sc in schema1["structure_constants"]:
        X, Y, Z = sc["X"], sc["Y"], sc["Z"]
        coeff = Fraction(sc["coeff"])
        key = (X, Y)
        if key not in table:
            table[key] = {}
        table[key][Z] = table[key].get(Z, Fraction(0)) + coeff
    return table


def bracket(X: str, Y: str, table: dict) -> dict:
    return dict(table.get((X, Y), {}))


def apply_f(gen: str, f_map: dict) -> dict:
    """Return f(gen) as a dict {Z: coeff}."""
    return dict(f_map.get(gen, {}))


def add_vectors(*vecs) -> dict:
    result = {}
    for v in vecs:
        for Z, c in v.items():
            result[Z] = result.get(Z, Fraction(0)) + c
    return {Z: c for Z, c in result.items() if c != 0}


def scale(coeff: Fraction, vec: dict) -> dict:
    if coeff == 0:
        return {}
    return {Z: coeff * c for Z, c in vec.items() if coeff * c != 0}


def apply_bracket_to_vec(X: str, vec: dict, table: dict) -> dict:
    """Compute [X, vec] = sum_Z c_Z [X, Z]."""
    result = {}
    for Z, cZ in vec.items():
        b = bracket(X, Z, table)
        for W, cW in b.items():
            result[W] = result.get(W, Fraction(0)) + cZ * cW
    return {W: c for W, c in result.items() if c != 0}


def compute_coboundary(schema1: dict, f_map: dict) -> list:
    """
    Compute (delta_f)(X, Y) for all pairs (X, Y) in the basis.

    (delta_f)(X, Y) = (-1)^{p(X)} [X, f(Y)] - (-1)^{(p(X)+1)*p(Y)} [Y, f(X)] - f([X,Y])

    Returns list of non-zero entries {X, Y, Z, coeff}.
    """
    basis = schema1["basis"]["even"] + schema1["basis"]["odd"]
    parity = schema1["parity"]
    table = build_bracket_table(schema1)

    results = []

    def add(X, Y, Z, coeff):
        if coeff != 0:
            results.append({
                "X": X, "Y": Y, "Z": Z,
                "coeff": str(coeff),
            })

    for X in basis:
        px = parity[X]
        for Y in basis:
            py = parity[Y]

            # Term 1: (-1)^{p(X)} [X, f(Y)]
            fY = apply_f(Y, f_map)
            t1 = scale(Fraction((-1) ** px), apply_bracket_to_vec(X, fY, table))

            # Term 2: -(-1)^{(p(X)+1)*p(Y)} [Y, f(X)]
            fX = apply_f(X, f_map)
            s2 = -Fraction((-1) ** ((px + 1) * py))
            t2 = scale(s2, apply_bracket_to_vec(Y, fX, table))

            # Term 3: -f([X, Y])
            bXY = bracket(X, Y, table)
            f_bXY = {}
            for W, cW in bXY.items():
                fW = apply_f(W, f_map)
                for V, cV in fW.items():
                    f_bXY[V] = f_bXY.get(V, Fraction(0)) + cW * cV
            t3 = scale(Fraction(-1), f_bXY)

            total = add_vectors(t1, t2, t3)
            for Z, coeff in total.items():
                add(X, Y, Z, coeff)

    return results


def choose_f_map(n: int, basis: list, parity: dict) -> dict:
    """
    Choose a simple odd linear map f: g -> g.

    f must map even -> odd and odd -> even.

    We choose: f(E_eps1_del{k}_pm) = H_1 for all k (maps each "simple" odd generator to H_1).
    and f(H_1) = E_eps1_del1_pm (maps the first Cartan to the corresponding odd generator).

    This captures the simplest non-trivial triviality structure.
    """
    f_map = {}
    # f: odd -> even (choose mapping to H_1)
    # f: even -> odd (choose mapping to E_eps1_del1_pm)

    # For each odd generator, map to H_1
    for gen in basis:
        if parity.get(gen, 0) == 1:
            f_map[gen] = {"H_1": Fraction(1)}

    # For H_1 (even), map to E_eps1_del1_pm
    f_map["H_1"] = {"E_eps1_del1_pm": Fraction(1)}

    return f_map


def build_schema4(n: int) -> dict:
    """Build Schema 4 coboundary JSON for C(n+1) with bosonic rank n."""
    schema1 = load(n, "structure")

    basis = schema1["basis"]["even"] + schema1["basis"]["odd"]
    parity = schema1["parity"]

    f_map = choose_f_map(n, basis, parity)

    # Record f in schema
    f_record = {}
    for gen, image in f_map.items():
        f_record[gen] = {Z: str(c) for Z, c in image.items()}

    coboundary_entries = compute_coboundary(schema1, f_map)

    schema = {
        "schema_version": "5.0",
        "algebra": schema1["algebra"],
        "linear_map_f": {
            "description": (
                "Odd linear map f: g -> g. "
                "f maps even generators to odd generators and vice versa. "
                "Chosen as: f(odd generator) = H_1, f(H_1) = E_eps1_del1_pm, others = 0."
            ),
            "phi_coefficients": f_record,
        },
        "coboundary": {
            "description": (
                "(delta_f)(X,Y) = (-1)^{p(X)}[X,f(Y)] - (-1)^{(p(X)+1)p(Y)}[Y,f(X)] - f([X,Y]). "
                "Non-zero entries listed below."
            ),
            "formula": "(delta_f)(X,Y) = (-1)^{p(X)}[X,f(Y)] - (-1)^{(p(X)+1)*p(Y)}[Y,f(X)] - f([X,Y])",
            "entries": coboundary_entries,
        },
        "metadata": {
            "generated_by": "src/C_coboundary.py",
            "generation_date": datetime.date.today().isoformat(),
        },
    }
    return schema


def main():
    data_dir = os.path.join(os.path.dirname(__file__), "..", "data")
    os.makedirs(data_dir, exist_ok=True)

    for n in range(1, 4):
        schema = build_schema4(n)
        out_path = os.path.join(data_dir, f"C_{n}_coboundary.json")
        with open(out_path, "w") as f:
            json.dump(schema, f, indent=2)
        n_entries = len(schema["coboundary"]["entries"])
        print(f"Generated {out_path}: {n_entries} coboundary entries")


if __name__ == "__main__":
    main()
