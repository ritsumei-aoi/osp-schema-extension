"""
C(n+1) = osp(2|2n) coboundary structure (Schema 4) generator.

Parameterizes the most general odd linear map f: g -> g as

    f(Z_j) = sum_i phi_{i,j} Z_i   (p(Z_i) != p(Z_j))

and computes the coboundary

    (delta f)(X, Y) = (-1)^{p(X)} [X, f(Y)]
                    - (-1)^{(p(X)+1)*p(Y)} [Y, f(X)]
                    - f([X, Y])

as a linear combination of phi parameters for each basis pair (X <= Y in PBW order).

Produces Schema 4 JSON files C_{n}_coboundary.json for n=1, 2, 3.

Usage:
    python src/build_C_coboundary.py
"""

import json
import os
from fractions import Fraction
from collections import defaultdict
from datetime import date

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")


def load_schema1(n):
    path = os.path.join(DATA_DIR, f"C_{n}_structure.json")
    with open(path) as f:
        return json.load(f)


def build_sc_map(structure_constants):
    """Build {(X, Y): {Z: Fraction(coeff)}} from the stored structure constants (X <= Y in PBW)."""
    sc = defaultdict(lambda: defaultdict(Fraction))
    for entry in structure_constants:
        X, Y, Z = entry["X"], entry["Y"], entry["Z"]
        sc[(X, Y)][Z] += Fraction(entry["coeff"])
    return {k: dict(v) for k, v in sc.items()}


def get_bracket(sc_map, parity, pbw_index, X, Y):
    """Return [X, Y] as {Z: Fraction coeff}. Applies graded antisymmetry for reversed pairs."""
    iX, iY = pbw_index[X], pbw_index[Y]
    if iX <= iY:
        return dict(sc_map.get((X, Y), {}))
    # [X, Y] = -(-1)^{p(X)p(Y)} [Y, X]
    stored = sc_map.get((Y, X), {})
    sign = Fraction(-1) * Fraction((-1) ** (parity[X] * parity[Y]))
    return {Z: sign * c for Z, c in stored.items()}


def param_name(target, source):
    """Return the phi parameter name: phi_{target, source} means f(source) has target component."""
    return f"phi__{target}__{source}"


def compute_coboundary_entries(schema1):
    """
    Compute (delta f)(X, Y) for all X <= Y in PBW order.

    Returns a list of dicts with keys X, Y, Z, phi_terms where phi_terms
    is a list of {phi: name, coeff: str(Fraction)} for all non-zero contributions.
    """
    parity = schema1["parity"]
    basis_all = schema1["basis"]["odd"] + schema1["basis"]["even"]
    pbw_index = {g: i for i, g in enumerate(basis_all)}
    sc_map = build_sc_map(schema1["structure_constants"])

    results = []

    for xi, X in enumerate(basis_all):
        for Y in basis_all[xi:]:
            pX = parity[X]
            pY = parity[Y]

            # acc[Z][param_name] = Fraction coefficient
            acc = {}

            def add(Z, param, val):
                if val == 0:
                    return
                if Z not in acc:
                    acc[Z] = {}
                acc[Z][param] = acc[Z].get(param, Fraction(0)) + val

            # TERM 1: (-1)^{p(X)} * [X, f(Y)]
            # f(Y) = sum_{Zi: p(Zi) != p(Y)} phi_{Zi, Y} Zi
            sign1 = Fraction((-1) ** pX)
            for Zi in basis_all:
                if parity[Zi] == pY:
                    continue
                p = param_name(Zi, Y)
                for Zm, c in get_bracket(sc_map, parity, pbw_index, X, Zi).items():
                    add(Zm, p, sign1 * c)

            # TERM 2: -(-1)^{(p(X)+1)*p(Y)} * [Y, f(X)]
            # f(X) = sum_{Zi: p(Zi) != p(X)} phi_{Zi, X} Zi
            sign2 = Fraction(-1) * Fraction((-1) ** ((pX + 1) * pY))
            for Zi in basis_all:
                if parity[Zi] == pX:
                    continue
                p = param_name(Zi, X)
                for Zm, c in get_bracket(sc_map, parity, pbw_index, Y, Zi).items():
                    add(Zm, p, sign2 * c)

            # TERM 3: -f([X, Y])
            # [X, Y] = sum_Ztmp c^{Ztmp}_{XY} Ztmp
            # f(Ztmp) = sum_{Zi: p(Zi) != p(Ztmp)} phi_{Zi, Ztmp} Zi
            for Ztmp, c_XY in get_bracket(sc_map, parity, pbw_index, X, Y).items():
                pZtmp = parity[Ztmp]
                for Zi in basis_all:
                    if parity[Zi] == pZtmp:
                        continue
                    p = param_name(Zi, Ztmp)
                    add(Zi, p, -c_XY)

            # Collect non-zero (Z, phi_terms) entries
            for Zm in basis_all:
                if Zm not in acc:
                    continue
                term_dict = {p: v for p, v in acc[Zm].items() if v != 0}
                if not term_dict:
                    continue
                results.append({
                    "X": X,
                    "Y": Y,
                    "Z": Zm,
                    "phi_terms": [
                        {"phi": p, "coeff": str(v)}
                        for p, v in sorted(term_dict.items())
                    ],
                })

    return results


def enumerate_f_parameters(schema1):
    """Return the list of all phi_{target, source} parameters for the general odd linear map."""
    parity = schema1["parity"]
    basis_all = schema1["basis"]["odd"] + schema1["basis"]["even"]
    params = []
    for source in basis_all:
        for target in basis_all:
            if parity[target] != parity[source]:
                params.append({
                    "name": param_name(target, source),
                    "from_generator": source,
                    "from_parity": parity[source],
                    "to_generator": target,
                    "to_parity": parity[target],
                })
    return params


def verify_parity(schema4, schema1):
    """
    Check that each (delta f)(X, Y)|_Z has the expected parity:
    p(Z) == p(X) + p(Y) + 1  (mod 2).
    """
    parity = schema1["parity"]
    for entry in schema4["coboundary"]["delta_f_entries"]:
        X, Y, Z = entry["X"], entry["Y"], entry["Z"]
        expected = (parity[X] + parity[Y] + 1) % 2
        if parity[Z] != expected:
            raise ValueError(
                f"Parity mismatch at ({X}, {Y}) -> {Z}: "
                f"expected p(Z)={expected}, got {parity[Z]}"
            )


def build_schema4(n):
    schema1 = load_schema1(n)
    f_params = enumerate_f_parameters(schema1)
    coboundary_entries = compute_coboundary_entries(schema1)

    schema4 = {
        "schema_version": "5.0",
        "layer": 4,
        "algebra": schema1["algebra"],
        "coboundary": {
            "description": (
                "Coboundary operator delta_f for the general odd linear map "
                "f: g -> g. f(Z_j) = sum_i phi_{i,j} Z_i with p(Z_i) != p(Z_j). "
                "(delta f)(X,Y) = (-1)^{p(X)} [X, f(Y)] "
                "- (-1)^{(p(X)+1)*p(Y)} [Y, f(X)] - f([X,Y]). "
                "Entries stored for X <= Y in PBW order. "
                "Coefficients are linear in phi parameters (Scale A: natural). "
                "Graded antisymmetry: (delta f)(Y,X) = -(-1)^{p(X)p(Y)} (delta f)(X,Y)."
            ),
            "f_parameterization": "general_odd",
            "scaling_convention": "Scale_A_natural",
            "phi_parameter_count": len(f_params),
            "f_parameters": f_params,
            "delta_f_entry_count": len(coboundary_entries),
            "delta_f_entries": coboundary_entries,
        },
        "metadata": {
            "generated_by": "build_C_coboundary.py",
            "generation_date": str(date.today()),
            "source_schema1": f"C_{n}_structure.json",
            "references": [
                "Frappat et al. (2000), Dictionary on Lie Algebras and Superalgebras",
                "C_coboundary_definition.md",
            ],
        },
    }
    return schema4


def main():
    for n in [1, 2, 3]:
        print(f"Building Schema 4 for n={n} (C({n+1}) = osp(2|{2*n}))...")
        schema1 = load_schema1(n)
        schema4 = build_schema4(n)

        verify_parity(schema4, schema1)
        print(f"  Parity check passed.")

        n_params = schema4["coboundary"]["phi_parameter_count"]
        n_entries = schema4["coboundary"]["delta_f_entry_count"]
        print(f"  phi parameters: {n_params}")
        print(f"  delta_f (X, Y, Z) entries: {n_entries}")

        out_path = os.path.join(DATA_DIR, f"C_{n}_coboundary.json")
        with open(out_path, "w") as f:
            json.dump(schema4, f, indent=2)
        print(f"  Written: {out_path}")

    print("Done.")


if __name__ == "__main__":
    main()
