"""
C_coboundary.py: Compute Schema 4 (coboundary structure) for C(n+1) = osp(2|2n).

The coboundary operator delta_f applied to an odd linear map f: g -> g is:
  (delta f)(X, Y) = (-1)^{p(X)} [X, f(Y)] - (-1)^{(p(X)+1)*p(Y)} [Y, f(X)] - f([X,Y])

The map f: g -> g is odd (reverses parity), parameterized by phi_{ij}:
  f(Z_j) = sum_i phi_{ij} * Z_i

where phi_{ij} has parity p(Z_i) + p(Z_j) + 1 mod 2 (must be non-zero only when
p(Z_i) != p(Z_j), i.e., one index is even and the other is odd).

(delta f)_{abc} = sum_k [ phi_{ak} * sc_{kbc} ] * sign1
                - sum_k [ phi_{bk} * sc_{kac} ] * sign2
                - sum_k [ phi_{ck} * sc_{ab->k} ]

where sc_{abc} is the structure constant [Z_a, Z_b] = sum_c sc_{abc} Z_c.

This produces the coboundary as a function of phi parameters.
"""

import json
import sys
import os
from fractions import Fraction
from datetime import date
sys.path.insert(0, os.path.dirname(__file__))
from C_generators import build_basis, parity_of, build_parity_dict


def load_sc_table(n):
    """Load Schema 1 and build SC lookup: sc[(X,Y)] = {Z: coeff}."""
    fname = f"data/C_{n}_structure.json"
    with open(fname) as f:
        schema = json.load(f)
    basis = schema["basis"]["even"] + schema["basis"]["odd"]
    parity = schema["parity"]
    sc = {}
    for entry in schema["structure_constants"]:
        X, Y, Z, c = entry["X"], entry["Y"], entry["Z"], Fraction(entry["coeff"])
        key = (X, Y)
        if key not in sc:
            sc[key] = {}
        sc[key][Z] = sc[key].get(Z, Fraction(0)) + c
    # Clean zeros
    for key in list(sc.keys()):
        sc[key] = {z: c for z, c in sc[key].items() if c != 0}
        if not sc[key]:
            del sc[key]
    return sc, basis, parity


def bracket_lookup(sc, parity, X, Y):
    """Return [X,Y} as {Z: coeff}, using anti-symmetry for reverse pairs."""
    px = parity.get(X, 0)
    py = parity.get(Y, 0)
    result = {}
    direct = sc.get((X, Y), {})
    for z, c in direct.items():
        result[z] = result.get(z, Fraction(0)) + c
    reverse = sc.get((Y, X), {})
    sign = (-1) ** (px * py)
    for z, c in reverse.items():
        result[z] = result.get(z, Fraction(0)) - sign * c
    return {z: c for z, c in result.items() if c != 0}


def compute_coboundary(n):
    """
    Compute (delta f)(X, Y) symbolically.

    Returns list of entries {X, Y, Z, phi_param, coeff} where
    (delta f)(X,Y) = sum_{Z,phi} coeff * phi_param * Z

    phi_param = phi_{i}{j} means f(basis[j]) has a basis[i] component.
    Since f is odd: f maps even -> odd and odd -> even.
    phi_{ij} is nonzero only when parity(i) != parity(j).
    """
    sc, basis, parity = load_sc_table(n)
    even_basis = [g for g in basis if parity.get(g, 0) == 0]
    odd_basis = [g for g in basis if parity.get(g, 0) == 1]

    # phi_ij: f(Z_j) has Z_i component. Valid only when p(Z_i) != p(Z_j).
    # f: even -> odd, odd -> even.
    # f(Z_j^even) = sum_{Z_i^odd} phi_{ij} * Z_i
    # f(Z_j^odd)  = sum_{Z_i^even} phi_{ij} * Z_i

    coboundary_entries = []

    def add_entry(X, Y, Z, phi_i, phi_j, coeff):
        """Record: (delta f)(X,Y) has Z-component = coeff * phi_{phi_i,phi_j}."""
        if coeff == 0:
            return
        phi_label = f"phi_{phi_i}_{phi_j}"
        coboundary_entries.append({
            "X": X, "Y": Y, "Z": Z,
            "phi_param": phi_label,
            "coeff": str(coeff)
        })

    def bracket_with_f_result(X, f_Y_idx, basis, coeff_fY, parity_fY):
        """Compute [X, f(Y)] = coeff_fY * [X, basis[f_Y_idx]]."""
        Z_gen = basis[f_Y_idx]
        return coeff_fY, bracket_lookup(sc, parity, X, Z_gen)

    # Iterate over all pairs (X, Y):
    for xi, X in enumerate(basis):
        px = parity.get(X, 0)
        for yi, Y in enumerate(basis):
            if yi < xi:
                continue  # anti-symmetry handles [Y,X]
            py = parity.get(Y, 0)

            # (delta f)(X,Y) = (-1)^{px}[X,f(Y)] - (-1)^{(px+1)*py}[Y,f(X)] - f([X,Y])

            # Term 1: (-1)^{px} * [X, f(Y)]
            # f(Y) = sum_{Z_i with p(Z_i)!=py} phi_{i,yi} * Z_i
            sign1 = Fraction((-1) ** px)
            for zi, Zi in enumerate(basis):
                pzi = parity.get(Zi, 0)
                if pzi == py:
                    continue  # f(Y) only maps to generators of opposite parity
                # f(Z_Y) = phi_{zi, yi} * Z_zi
                br = bracket_lookup(sc, parity, X, Zi)
                for W, c in br.items():
                    add_entry(X, Y, W, zi, yi, sign1 * c)

            # Term 2: -(-1)^{(px+1)*py} * [Y, f(X)]
            sign2 = Fraction(-(-1) ** ((px + 1) * py))
            for zi, Zi in enumerate(basis):
                pzi = parity.get(Zi, 0)
                if pzi == px:
                    continue  # f(X) maps to opposite parity
                br = bracket_lookup(sc, parity, Y, Zi)
                for W, c in br.items():
                    add_entry(X, Y, W, zi, xi, sign2 * c)

            # Term 3: -f([X,Y])
            # [X,Y] = sum_k coeff_k * Z_k; f([X,Y]) = sum_k coeff_k * f(Z_k)
            # = sum_k coeff_k * sum_{zi: p(zi)!=p(Zk)} phi_{zi,k} * Z_zi
            bXY = bracket_lookup(sc, parity, X, Y)
            for W, c_bxy in bXY.items():
                pw = parity.get(W, 0)
                k = basis.index(W)
                for zi, Zi in enumerate(basis):
                    pzi = parity.get(Zi, 0)
                    if pzi == pw:
                        continue  # f maps to opposite parity
                    add_entry(X, Y, Zi, zi, k, Fraction(-1) * c_bxy)

    return coboundary_entries


def consolidate_coboundary(entries):
    """Consolidate entries by (X,Y,Z,phi_param)."""
    accumulated = {}
    for entry in entries:
        key = (entry["X"], entry["Y"], entry["Z"], entry["phi_param"])
        c = Fraction(entry["coeff"])
        accumulated[key] = accumulated.get(key, Fraction(0)) + c
    result = []
    for (X, Y, Z, phi), c in accumulated.items():
        if c != 0:
            result.append({"X": X, "Y": Y, "Z": Z, "phi_param": phi, "coeff": str(c)})
    return result


def build_schema4(n):
    even, odd = build_basis(n)
    basis = odd + even
    parity_dict = build_parity_dict(even, odd)

    # Generate phi parameter labels
    phi_labels = []
    for zi, Zi in enumerate(basis):
        pzi = parity_dict[Zi]
        for yi, Yi in enumerate(basis):
            pyi = parity_dict[Yi]
            if pzi != pyi:
                phi_labels.append(f"phi_{zi}_{yi}")

    coboundary_raw = compute_coboundary(n)
    coboundary = consolidate_coboundary(coboundary_raw)

    schema = {
        "schema_version": "5.0",
        "algebra": {
            "family": "C", "m": 1, "n": n,
            "cartan_type": f"C({n+1})",
            "alternative_notation": {"osp": f"osp(2|{2*n})"}
        },
        "odd_map_f": {
            "description": "Odd linear map f: g -> g parameterized by phi_{i,j} coefficients",
            "convention": "f(Z_j) = sum_i phi_{i,j} * Z_i, where p(Z_i) != p(Z_j)",
            "basis_order": "odd generators first, then even (following PBW ordering)"
        },
        "coboundary_delta_f": {
            "description": "(delta f)(X,Y) = (-1)^{p(X)}[X,f(Y)] - (-1)^{(p(X)+1)p(Y)}[Y,f(X)] - f([X,Y])",
            "entries": coboundary
        },
        "metadata": {
            "generated_by": "src/C_coboundary.py",
            "generation_date": str(date.today()),
            "references": [
                "docs/math/C_coboundary_definition.md"
            ]
        }
    }
    return schema


def main():
    import os
    os.makedirs("data", exist_ok=True)
    for n in [1, 2, 3]:
        print(f"Computing coboundary for C_{n}...", end=" ")
        schema4 = build_schema4(n)
        fname = f"data/C_{n}_coboundary.json"
        with open(fname, "w") as f:
            json.dump(schema4, f, indent=2)
        entry_count = len(schema4["coboundary_delta_f"]["entries"])
        print(f"entries={entry_count} -> {fname}")


if __name__ == "__main__":
    main()
