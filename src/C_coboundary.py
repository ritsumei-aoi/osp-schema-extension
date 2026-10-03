"""
C_coboundary.py — Schema 4: coboundary structure for C(n+1).

Computes the coboundary (delta f)(X,Y) for an odd linear map f: g -> g.
The map f is parametrized by phi_{ij}: f(Z_j) = sum_i phi_{ij} * Z_i.

Formula (docs/math/C_coboundary_definition.md):
  (delta f)(X, Y) = (-1)^{p(X)} [X, f(Y)] - (-1)^{(p(X)+1)*p(Y)} [Y, f(X)] - f([X,Y])

Reference: docs/math/C_coboundary_definition.md
"""

import json
import os
import sys
from fractions import Fraction
from datetime import date

DATA_DIR = os.path.join(os.path.dirname(__file__), '..', 'data')


def load_schema1(n):
    path = os.path.join(DATA_DIR, f'C_{n}_structure.json')
    with open(path) as f:
        return json.load(f)


def build_bracket_table(schema):
    """Build full bracket table from Schema 1 structure constants."""
    parity = dict(schema['parity'])
    parity['K'] = 0
    basis = schema['basis']['odd'] + schema['basis']['even']
    table = {(X, Y): {} for X in basis for Y in basis}

    for sc in schema['structure_constants']:
        X, Y, Z = sc['X'], sc['Y'], sc['Z']
        if Z == 'K':
            continue
        c = Fraction(sc['coeff'])
        table[(X, Y)][Z] = table[(X, Y)].get(Z, Fraction(0)) + c

    original = {key: dict(val) for key, val in table.items()}
    for X in basis:
        for Y in basis:
            if X == Y:
                continue
            pX, pY = parity[X], parity[Y]
            sign = -(-1) ** (pX * pY)
            for Z, c in original[(X, Y)].items():
                table[(Y, X)][Z] = table[(Y, X)].get(Z, Fraction(0)) + sign * c

    for key in table:
        table[key] = {k: v for k, v in table[key].items() if v != 0}
    return table, parity, basis


def apply_f(phi, Z_label, basis):
    """
    Apply the odd linear map f to generator Z_label.
    phi[i][j] = phi_{ij} coefficient.
    f(Z_j) = sum_i phi_{ij} * Z_i.
    Returns dict: generator_label -> Fraction.
    """
    j = basis.index(Z_label)
    result = {}
    for i, Z_i in enumerate(basis):
        c = phi.get((i, j), Fraction(0))
        if c != 0:
            result[Z_i] = result.get(Z_i, Fraction(0)) + c
    return {k: v for k, v in result.items() if v != 0}


def apply_bracket_linear(table, X, element_dict):
    """Apply [X, -] linearly: [X, sum_Z c_Z Z] = sum_Z c_Z [X,Z]."""
    out = {}
    for Z, cz in element_dict.items():
        for W, c in table[(X, Z)].items():
            out[W] = out.get(W, Fraction(0)) + cz * c
    return {k: v for k, v in out.items() if v != 0}


def apply_f_linear(phi, element_dict, basis):
    """Apply f linearly: f(sum_Z c_Z Z) = sum_Z c_Z f(Z)."""
    out = {}
    for Z, cz in element_dict.items():
        fZ = apply_f(phi, Z, basis)
        for W, c in fZ.items():
            out[W] = out.get(W, Fraction(0)) + cz * c
    return {k: v for k, v in out.items() if v != 0}


def compute_coboundary(n, phi, basis, parity, table):
    """
    Compute (delta f)(X, Y) for all pairs (X,Y) with X<=Y (basis index).
    Returns list of {X, Y, Z, phi_labels, coeff}.

    Formula: (delta f)(X,Y) = (-1)^{p(X)} [X, f(Y)] - (-1)^{(p(X)+1)*p(Y)} [Y, f(X)] - f([X,Y])
    """
    entries = []
    for i, X in enumerate(basis):
        for j, Y in enumerate(basis):
            if i > j:
                continue
            pX, pY = parity[X], parity[Y]

            # f(Y): odd map, so f maps even -> odd and odd -> even
            fY = apply_f(phi, Y, basis)
            fX = apply_f(phi, X, basis)

            # Term 1: (-1)^{p(X)} [X, f(Y)]
            XfY = apply_bracket_linear(table, X, fY)
            s1 = (-1) ** pX

            # Term 2: -(-1)^{(p(X)+1)*p(Y)} [Y, f(X)]
            YfX = apply_bracket_linear(table, Y, fX)
            s2 = -(-1) ** ((pX + 1) * pY)

            # Term 3: -f([X,Y])
            XY_bracket = table[(X, Y)]
            fXY = apply_f_linear(phi, XY_bracket, basis)

            # Sum
            total = {}
            for W, c in XfY.items():
                total[W] = total.get(W, Fraction(0)) + s1 * c
            for W, c in YfX.items():
                total[W] = total.get(W, Fraction(0)) + s2 * c
            for W, c in fXY.items():
                total[W] = total.get(W, Fraction(0)) - c

            total = {k: v for k, v in total.items() if v != 0}
            for Z, c in total.items():
                entries.append({"X": X, "Y": Y, "Z": Z, "coeff": str(c)})

    return entries


def symbolic_phi(n, basis, parity):
    """
    Build a symbolic phi matrix: phi_{ij} is a symbolic variable phi_i_j
    when f(Z_j) can have a Z_i component (parity constraint: p(f(Z))=1-p(Z)).
    Returns phi dict (i,j)->phi_label_str and list of phi labels.
    """
    phi = {}
    phi_labels = {}
    for j, Zj in enumerate(basis):
        pZj = parity[Zj]
        target_parity = 1 - pZj  # f reverses parity
        for i, Zi in enumerate(basis):
            if parity[Zi] == target_parity:
                lbl = f"phi_{i}_{j}"
                phi[(i, j)] = lbl
                phi_labels[lbl] = (i, j, Zi, Zj)
    return phi, phi_labels


def compute_coboundary_symbolic(n, basis, parity, table):
    """
    Compute (delta f)(X,Y) symbolically, treating phi_{ij} as symbols.
    Returns list of {X, Y, Z, phi_label, coeff}.
    """
    phi_sym, phi_labels = symbolic_phi(n, basis, parity)

    # For each phi_{i,j} independently, compute its contribution to coboundary
    entries = []

    for phi_lbl, (i, j, Zi, Zj) in phi_labels.items():
        # phi = {(i,j): Fraction(1)}, all others zero
        phi = {(i, j): Fraction(1)}

        coboundary = compute_coboundary(n, phi, basis, parity, table)
        for entry in coboundary:
            entries.append({
                "X": entry["X"], "Y": entry["Y"], "Z": entry["Z"],
                "phi_label": phi_lbl,
                "phi_meaning": f"f({Zj}) has {Zi} component",
                "coeff": entry["coeff"]
            })

    return entries


def build_schema4(n):
    s1 = load_schema1(n)
    table, parity, basis = build_bracket_table(s1)

    # Build symbolic phi and coboundary
    phi_sym, phi_labels = symbolic_phi(n, basis, parity)

    coboundary_entries = compute_coboundary_symbolic(n, basis, parity, table)

    # Build phi_matrix description
    phi_desc = {}
    for lbl, (i, j, Zi, Zj) in phi_labels.items():
        phi_desc[lbl] = {
            "i": i, "j": j,
            "target_generator": Zi,
            "source_generator": Zj,
            "meaning": f"f({Zj}) includes phi_{i}_{j} * {Zi}"
        }

    return {
        "schema_version": "5.0",
        "algebra": s1['algebra'],
        "phi_matrix": {
            "description": "Odd linear map f: g->g, f(Z_j)=sum_i phi_{ij}*Z_i",
            "parity_constraint": "p(f(Z)) = 1 - p(Z) (f reverses parity)",
            "count": len(phi_labels),
            "parameters": phi_desc
        },
        "coboundary_coefficients": coboundary_entries,
        "metadata": {
            "generated_by": "src/C_coboundary.py",
            "generation_date": str(date.today()),
            "formula": "(delta f)(X,Y) = (-1)^{p(X)}[X,f(Y)] - (-1)^{(p(X)+1)p(Y)}[Y,f(X)] - f([X,Y])"
        }
    }


def main():
    os.makedirs(DATA_DIR, exist_ok=True)
    for n in [1, 2, 3]:
        print(f"Generating C_{n}_coboundary.json (n={n})...")
        schema = build_schema4(n)
        path = os.path.join(DATA_DIR, f'C_{n}_coboundary.json')
        with open(path, 'w') as f:
            json.dump(schema, f, indent=2)
        n_phi = schema['phi_matrix']['count']
        n_cob = len(schema['coboundary_coefficients'])
        print(f"  phi parameters: {n_phi}")
        print(f"  coboundary entries: {n_cob}")
    print("Done.")


if __name__ == "__main__":
    main()
