"""
C_coboundary.py
Layer 4: Compute coboundary (delta f) for an odd linear map f: g -> g.

(delta f)(X, Y) = (-1)^{p(X)} [X, f(Y)] - (-1)^{(p(X)+1)*p(Y)} [Y, f(X)] - f([X,Y])

f is parametrized by coefficients phi_{ij}: f(Z_j) = sum_i phi_{ij} Z_i,
with parity constraint: f maps even <-> odd (reverses parity).

The coboundary coefficients are linear in phi parameters.
"""

import json
import os
from fractions import Fraction
from collections import defaultdict

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")


def rational_str(f):
    if f.denominator == 1:
        return str(f.numerator)
    return f"{f.numerator}/{f.denominator}"


def build_bracket_table(sc_list, basis_all, parity):
    """Build {(X,Y): {Z: Fraction}} from structure constants list, with anti-symmetry."""
    table = defaultdict(lambda: defaultdict(Fraction))
    for entry in sc_list:
        X, Y = entry["X"], entry["Y"]
        for term in entry["result"]:
            table[(X, Y)][term["Z"]] += Fraction(term["coeff"])

    # Expand anti-symmetry
    for (X, Y) in list(table.keys()):
        px, py = parity[X], parity[Y]
        sign = Fraction((-1) ** (px * py + 1))
        for Z, c in table[(X, Y)].items():
            table[(Y, X)][Z] += sign * c

    return {k: dict(v) for k, v in table.items()}


def bracket_result(table, X, Y):
    return table.get((X, Y), {})


def compute_coboundary(n):
    """
    Compute (delta f)(X, Y) for all basis pairs (X, Y) with X <= Y.

    f is parametrized by phi_{ij}: phi_label = 'phi_{j_idx}_{i_idx}'
    meaning f(Z_j) contributes phi_{j,i} * Z_i to f(Z_j).

    Parity constraint: p(Z_i) = 1 - p(Z_j) (f reverses parity).

    Returns list of {X, Y, Z, coeff_expr} entries.
    """
    struct_path = os.path.join(DATA_DIR, f"C_{n}_structure.json")
    with open(struct_path) as f:
        s1 = json.load(f)

    basis_even = s1["basis"]["even"]
    basis_odd = s1["basis"]["odd"]
    basis_all = basis_even + basis_odd
    parity = {g: s1["parity"][g] for g in basis_all}

    sc_list = s1["structure_constants"]
    table = build_bracket_table(sc_list, basis_all, parity)

    # Define phi parameters:
    # For each generator Z_j, f(Z_j) = sum_{Z_i: p(Z_i) != p(Z_j)} phi_{j,i} Z_i
    # Param label: 'phi_{jlabel}_{ilabel}'  (using basis indices)
    # We build a map: phi_label -> contribution to (delta f)(X,Y)[Z]

    # (delta f)(X,Y) = (-1)^{pX} [X, f(Y)] - (-1)^{(pX+1)*pY} [Y, f(X)] - f([X,Y])

    # For each target pair (X,Y), we accumulate:
    # {Z: {phi_label: Fraction}}

    phi_target_parity = {}  # phi_{j,i}: parity reversal means p(Z_i) = 1 - p(Z_j)
    for j, Zj in enumerate(basis_all):
        pZj = parity[Zj]
        for i, Zi in enumerate(basis_all):
            pZi = parity[Zi]
            if pZi != pZj:  # parity constraint
                phi_label = f"phi_{j}_{i}"
                phi_target_parity[phi_label] = (Zj, Zi)

    # For each pair (X, Y) with Xi <= Yi in basis_all index
    entries = []
    basis_idx = {g: i for i, g in enumerate(basis_all)}

    for Xi, X in enumerate(basis_all):
        pX = parity[X]
        for Yi in range(Xi, len(basis_all)):
            Y = basis_all[Yi]
            pY = parity[Y]

            # Accumulate: {Z: {phi_label: Fraction}}
            contrib = defaultdict(lambda: defaultdict(Fraction))

            sign1 = Fraction((-1) ** pX)          # for [X, f(Y)]
            sign2 = Fraction((-1) ** ((pX + 1) * pY))  # for [Y, f(X)]

            # Term 1: (-1)^{pX} [X, f(Y)]
            # f(Y) = sum_{i: p(Zi)!=pY} phi_{Yi,i} Zi
            # [X, f(Y)] = sum_i phi_{Yi,i} [X, Zi]
            for i, Zi in enumerate(basis_all):
                pZi = parity[Zi]
                if pZi == pY:
                    continue  # parity constraint violated
                phi_lbl = f"phi_{Yi}_{i}"
                br = bracket_result(table, X, Zi)
                for Z, c in br.items():
                    if Z != "K":  # K is central, [X,K]=0
                        contrib[Z][phi_lbl] += sign1 * c

            # Term 2: -(-1)^{(pX+1)*pY} [Y, f(X)]
            # = -sign2 * sum_i phi_{Xi,i} [Y, Zi]
            for i, Zi in enumerate(basis_all):
                pZi = parity[Zi]
                if pZi == pX:
                    continue
                phi_lbl = f"phi_{Xi}_{i}"
                br = bracket_result(table, Y, Zi)
                for Z, c in br.items():
                    if Z != "K":
                        contrib[Z][phi_lbl] -= sign2 * c

            # Term 3: -f([X,Y])
            # f([X,Y]) = sum_{W in [X,Y]} c_W sum_{i: p(Zi)!=p(W)} phi_{W_idx,i} Zi
            xy_br = bracket_result(table, X, Y)
            for W, c_W in xy_br.items():
                if W == "K":
                    continue  # K is central, not in basis for f
                pW = parity[W]
                Widx = basis_idx[W]
                for i, Zi in enumerate(basis_all):
                    pZi = parity[Zi]
                    if pZi == pW:
                        continue
                    phi_lbl = f"phi_{Widx}_{i}"
                    contrib[Zi][phi_lbl] -= c_W

            # Collect non-zero entries
            for Z, phi_d in contrib.items():
                phi_d = {pl: pv for pl, pv in phi_d.items() if pv != 0}
                if not phi_d:
                    continue
                # Build coeff_expr
                terms = []
                for pl, pv in sorted(phi_d.items()):
                    Zj_lbl, Zi_lbl = phi_target_parity[pl]
                    param_name = f"phi_{{{Zj_lbl},{Zi_lbl}}}"
                    if pv == Fraction(1):
                        terms.append(param_name)
                    elif pv == Fraction(-1):
                        terms.append(f"-{param_name}")
                    else:
                        terms.append(f"{rational_str(pv)}*{param_name}")
                expr = " + ".join(terms).replace("+ -", "- ")
                entries.append({"X": X, "Y": Y, "Z": Z, "coeff_expr": expr})

    return entries


def build_coboundary(n):
    struct_path = os.path.join(DATA_DIR, f"C_{n}_structure.json")
    with open(struct_path) as f:
        s1 = json.load(f)

    entries = compute_coboundary(n)

    return {
        "schema_version": "5.0",
        "algebra": s1["algebra"],
        "basis": s1["basis"],
        "parity": s1["parity"],
        "coboundary": {
            "definition": "(delta f)(X,Y) = (-1)^{p(X)}[X,f(Y)] - (-1)^{(p(X)+1)p(Y)}[Y,f(X)] - f([X,Y])",
            "f_parametrization": "f(Z_j) = sum_{i: p(Z_i)=1-p(Z_j)} phi_{Z_j,Z_i} Z_i",
            "parity_constraint": "f reverses parity: maps even -> odd, odd -> even",
            "coefficients": entries
        },
        "metadata": {
            "generated_by": "C_coboundary.py",
            "generation_date": "2026-10-09"
        }
    }


def main():
    os.makedirs(DATA_DIR, exist_ok=True)
    for n in [1, 2, 3]:
        print(f"Computing coboundary for C({n+1})...", end=" ", flush=True)
        schema = build_coboundary(n)
        path = os.path.join(DATA_DIR, f"C_{n}_coboundary.json")
        with open(path, "w") as f:
            json.dump(schema, f, indent=2)
        nc = len(schema["coboundary"]["coefficients"])
        print(f"done. coboundary entries={nc}")


if __name__ == "__main__":
    main()
