"""
C(n+1) = osp(2|2n) coboundary structure (Schema 4) generator.

Computes the coboundary (δf)(X,Y) for an odd linear map f: g -> g,
parameterized by coefficients φ_{ij}.

(δf)(X,Y) = (-1)^{p(X)} [X, f(Y)] - (-1)^{(p(X)+1)p(Y)} [Y, f(X)] - f([X,Y])
"""

import json
import os
from fractions import Fraction
from datetime import date
from C_generators import (
    build_basis, build_parity_map, gen_realization,
    compute_graded_bracket_gen, decompose_in_basis,
)


def build_phi_params(all_basis, parity):
    """Build the φ parameters for the odd linear map f.
    f reverses parity: f(even) = odd, f(odd) = even.
    φ_{ij} is the coefficient of Z_i in f(Z_j), where p(Z_i) != p(Z_j).
    """
    params = []
    for j, Zj in enumerate(all_basis):
        pj = parity[Zj]
        for i, Zi in enumerate(all_basis):
            pi = parity[Zi]
            if (pi + pj) % 2 == 1:
                params.append({
                    "label": f"phi_{Zi}_{Zj}",
                    "source": Zj,
                    "target": Zi,
                    "source_parity": pj,
                    "target_parity": pi,
                })
    return params


def compute_coboundary_symbolic(n):
    """Compute (δf)(X,Y) symbolically in terms of φ parameters.

    For each pair (X,Y), (δf)(X,Y) is a linear combination of generators
    with coefficients that are linear in φ.

    Returns list of dicts with keys: X, Y, Z, phi_param, coeff.
    """
    even, odd = build_basis(n)
    all_basis = odd + even
    parity = build_parity_map(even, odd)
    reals = gen_realization(n)

    # Precompute structure constants as a dict: (X, Y) -> {Z: coeff}
    sc_table = {}
    for i, X in enumerate(all_basis):
        for j in range(i + 1, len(all_basis)):
            Y = all_basis[j]
            pX, pY = parity[X], parity[Y]
            bracket = compute_graded_bracket_gen(reals[X], reals[Y], pX, pY)
            if bracket:
                decomp = decompose_in_basis(bracket, reals, all_basis, parity)
                d = {Z: c for Z, c in decomp}
                sc_table[(X, Y)] = d

    def get_bracket(A, B):
        """Get [A, B} as {Z: coeff}."""
        if (A, B) in sc_table:
            return dict(sc_table[(A, B)])
        elif (B, A) in sc_table:
            pA, pB = parity[A], parity[B]
            sign = Fraction(-1) ** (pA * pB) * Fraction(-1)
            return {Z: sign * c for Z, c in sc_table[(B, A)].items()}
        return {}

    coboundary_entries = []

    for i, X in enumerate(all_basis):
        for j in range(i + 1, len(all_basis)):
            Y = all_basis[j]
            pX, pY = parity[X], parity[Y]

            # For each φ parameter, compute its contribution to (δf)(X,Y)
            # f(Y) = Σ_k φ_{Zk,Y} Zk where p(Zk) = 1-pY
            # f(X) = Σ_k φ_{Zk,X} Zk where p(Zk) = 1-pX

            # Term 1: (-1)^{pX} [X, f(Y)] = (-1)^{pX} Σ_k φ_{Zk,Y} [X, Zk]
            sign1 = Fraction(-1) ** pX
            for k, Zk in enumerate(all_basis):
                if (parity[Zk] + pY) % 2 != 1:
                    continue
                phi_label = f"phi_{Zk}_{Y}"
                bracket_XZk = get_bracket(X, Zk)
                for Z, c in bracket_XZk.items():
                    coboundary_entries.append({
                        "X": X, "Y": Y, "Z": Z,
                        "phi_param": phi_label,
                        "coeff": str(sign1 * c),
                        "term": "term1",
                    })

            # Term 2: -(-1)^{(pX+1)pY} [Y, f(X)] = -(-1)^{(pX+1)pY} Σ_k φ_{Zk,X} [Y, Zk]
            sign2 = -Fraction(-1) ** ((pX + 1) * pY)
            for k, Zk in enumerate(all_basis):
                if (parity[Zk] + pX) % 2 != 1:
                    continue
                phi_label = f"phi_{Zk}_{X}"
                bracket_YZk = get_bracket(Y, Zk)
                for Z, c in bracket_YZk.items():
                    coboundary_entries.append({
                        "X": X, "Y": Y, "Z": Z,
                        "phi_param": phi_label,
                        "coeff": str(sign2 * c),
                        "term": "term2",
                    })

            # Term 3: -f([X,Y]) = -Σ_W c_W^{XY} f(W) = -Σ_W c_W^{XY} Σ_k φ_{Zk,W} Zk
            bracket_XY = get_bracket(X, Y)
            for W, c_W in bracket_XY.items():
                pW = parity[W]
                for k, Zk in enumerate(all_basis):
                    if (parity[Zk] + pW) % 2 != 1:
                        continue
                    phi_label = f"phi_{Zk}_{W}"
                    coboundary_entries.append({
                        "X": X, "Y": Y, "Z": Zk,
                        "phi_param": phi_label,
                        "coeff": str(-c_W),
                        "term": "term3",
                    })

    # Consolidate: group by (X, Y, Z, phi_param)
    consolidated = {}
    for entry in coboundary_entries:
        key = (entry["X"], entry["Y"], entry["Z"], entry["phi_param"])
        consolidated[key] = consolidated.get(key, Fraction(0)) + Fraction(entry["coeff"])

    result = []
    for (X, Y, Z, phi), coeff in consolidated.items():
        if coeff != 0:
            result.append({
                "X": X, "Y": Y, "Z": Z,
                "phi_param": phi,
                "coeff": str(coeff),
            })

    return result


def build_schema4_json(n):
    """Build Schema 4 JSON for C(n+1)."""
    even, odd = build_basis(n)
    all_basis = odd + even
    parity = build_parity_map(even, odd)

    phi_params = build_phi_params(all_basis, parity)
    coboundary = compute_coboundary_symbolic(n)

    schema = {
        "schema_version": "5.0",
        "schema_layer": 4,
        "algebra": {
            "family": "C",
            "m": 1,
            "n": n,
            "cartan_type": f"C({n + 1})",
        },
        "odd_linear_map": {
            "description": "Odd linear map f: g -> g reversing parity",
            "parameter_count": len(phi_params),
            "parameters_sample": phi_params[:10],
        },
        "coboundary_formula": {
            "description": "(δf)(X,Y) = (-1)^{p(X)} [X, f(Y)] - (-1)^{(p(X)+1)p(Y)} [Y, f(X)] - f([X,Y])",
        },
        "coboundary_coefficients": coboundary,
        "metadata": {
            "generated_by": "C_coboundary.py",
            "generation_date": str(date.today()),
            "references": [
                "C_coboundary_definition.md",
            ],
        },
    }
    return schema


def generate_all(output_dir="data"):
    os.makedirs(output_dir, exist_ok=True)
    for n in [1, 2, 3]:
        schema = build_schema4_json(n)
        path = os.path.join(output_dir, f"C_{n}_coboundary.json")
        with open(path, "w") as f:
            json.dump(schema, f, indent=2)
        print(f"Generated {path}: {len(schema['coboundary_coefficients'])} coboundary entries, "
              f"{schema['odd_linear_map']['parameter_count']} phi params")


def verify_consistency(n, data_dir="data"):
    """Verify Schema 4 consistency with Layer 1 basis."""
    with open(os.path.join(data_dir, f"C_{n}_structure.json")) as f:
        s1 = json.load(f)
    with open(os.path.join(data_dir, f"C_{n}_coboundary.json")) as f:
        s4 = json.load(f)

    basis = set(s1["basis"]["even"] + s1["basis"]["odd"])
    errors = []

    for entry in s4["coboundary_coefficients"]:
        for key in ["X", "Y", "Z"]:
            if entry[key] not in basis:
                errors.append(f"Generator {entry[key]} not in basis")

    if errors:
        print(f"  Consistency FAILURES for n={n}: {len(errors)}")
        for e in errors[:5]:
            print(f"    {e}")
    else:
        print(f"  Consistency check for n={n}: PASS")
    return len(errors) == 0


if __name__ == "__main__":
    generate_all()
    print("\nConsistency checks:")
    for n in [1, 2, 3]:
        verify_consistency(n)
