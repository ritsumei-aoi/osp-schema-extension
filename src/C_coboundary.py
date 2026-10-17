"""
C_coboundary.py: Computes the coboundary structure (Layer 4)
for C(n+1) = osp(2|2n) Lie superalgebras.
"""

import json
import os
import sys
from datetime import datetime
from fractions import Fraction
from collections import defaultdict
import sympy as sp

# Ensure workspace root is in sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.C_generators import build_c_generators, generate_schema_1_dict


def build_mode_paired_exchange_map(n, data=None, scaling=1):
    """
    Builds the Option 1: Canonical Mode-Paired Exchange Map f: g -> g.
    - f(H_k) = scaling * E_eps1_del{k}_pp (for k=1..n)
    - f(E_eps1_del{k}_pp) = scaling * H_k (for k=1..n)
    - f(H_{n+1}) = scaling * E_eps1_del{n}_mm
    - f(E_eps1_del{n}_mm) = scaling * H_{n+1}
    - 0 for all other basis elements.
    """
    scale_frac = Fraction(scaling)
    mapping_list = []
    f_dict = defaultdict(dict)  # f_dict[source][target] = coeff

    # Mode pairs for k=1..n
    for k in range(1, n + 1):
        hk = f"H_{k}"
        odd_pp = f"E_eps1_del{k}_pp"
        f_dict[hk][odd_pp] = scale_frac
        f_dict[odd_pp][hk] = scale_frac
        c_str = str(scale_frac.numerator) if scale_frac.denominator == 1 else f"{scale_frac.numerator}/{scale_frac.denominator}"
        mapping_list.append({"source": hk, "target": odd_pp, "coeff": c_str})
        mapping_list.append({"source": odd_pp, "target": hk, "coeff": c_str})

    # Terminal Cartan H_{n+1} paired with E_eps1_del{n}_mm
    h_term = f"H_{n+1}"
    odd_mm = f"E_eps1_del{n}_mm"
    f_dict[h_term][odd_mm] = scale_frac
    f_dict[odd_mm][h_term] = scale_frac
    c_str = str(scale_frac.numerator) if scale_frac.denominator == 1 else f"{scale_frac.numerator}/{scale_frac.denominator}"
    mapping_list.append({"source": h_term, "target": odd_mm, "coeff": c_str})
    mapping_list.append({"source": odd_mm, "target": h_term, "coeff": c_str})

    scale_str = str(scale_frac.numerator) if scale_frac.denominator == 1 else f"{scale_frac.numerator}/{scale_frac.denominator}"

    map_info = {
        "configuration": "mode_paired_exchange",
        "scaling": scale_str,
        "description": "Odd linear map f: g -> g reversing parity (p(f(X)) = p(X) + 1 mod 2)",
        "mapping": mapping_list
    }
    return f_dict, map_info


def compute_coboundary(struct_consts, basis, parity, f_dict):
    """
    Computes delta f for an arbitrary odd linear map f given by f_dict[X][Z] = coeff.
    Formula:
    (delta f)(X, Y) = (-1)^{p(X)} [X, f(Y)] - (-1)^{(p(X)+1)p(Y)} [Y, f(X)] - f([X, Y])
    Returns list of non-zero entries: {X, Y, Z, coeff, sign_rule}.
    """
    # Build bracket table c_{XY}^W
    bracket_table = defaultdict(dict)
    for entry in struct_consts:
        bracket_table[(entry["X"], entry["Y"])][entry["Z"]] = Fraction(entry["coeff"])

    delta_f_entries = []

    for X in basis:
        pX = parity[X]
        sign1 = -1 if pX == 1 else 1

        for Y in basis:
            pY = parity[Y]
            sign2 = -1 if ((pX + 1) * pY) % 2 == 1 else 1

            # Accumulate (delta f)(X, Y) over all target basis elements W
            accum = defaultdict(Fraction)

            # Term 1: (-1)^{pX} [X, f(Y)]
            f_Y = f_dict.get(Y, {})
            for Z_i, phi_iY in f_Y.items():
                br_XZ = bracket_table.get((X, Z_i), {})
                for W, c_xz in br_XZ.items():
                    accum[W] += sign1 * phi_iY * c_xz

            # Term 2: - (-1)^{(pX+1)pY} [Y, f(X)]
            f_X = f_dict.get(X, {})
            for Z_i, phi_iX in f_X.items():
                br_YZ = bracket_table.get((Y, Z_i), {})
                for W, c_yz in br_YZ.items():
                    accum[W] -= sign2 * phi_iX * c_yz

            # Term 3: - f([X, Y])
            br_XY = bracket_table.get((X, Y), {})
            for U, c_xy in br_XY.items():
                f_U = f_dict.get(U, {})
                for W, phi_WU in f_U.items():
                    accum[W] -= c_xy * phi_WU

            for W, coeff in accum.items():
                if coeff != 0:
                    c_str = str(coeff.numerator) if coeff.denominator == 1 else f"{coeff.numerator}/{coeff.denominator}"
                    delta_f_entries.append({
                        "X": X,
                        "Y": Y,
                        "Z": W,
                        "coeff": c_str,
                        "sign_rule": "graded"
                    })

    return delta_f_entries


def generate_schema_4_dict(n, configuration="mode_paired_exchange", scaling=1, custom_f_dict=None):
    """Generates complete Schema 4 dictionary for C(n+1)."""
    schema1 = generate_schema_1_dict(n)
    basis = schema1["basis"]["odd"] + schema1["basis"]["even"]
    parity = schema1["parity"]
    struct_consts = schema1["structure_constants"]

    if custom_f_dict is not None:
        f_dict = custom_f_dict
        map_info = {
            "configuration": configuration,
            "scaling": str(scaling),
            "description": "Custom odd linear map f: g -> g",
            "mapping": [
                {"source": src, "target": tgt, "coeff": str(c)}
                for src, tgts in f_dict.items() for tgt, c in tgts.items() if c != 0
            ]
        }
    elif configuration == "mode_paired_exchange":
        f_dict, map_info = build_mode_paired_exchange_map(n, scaling=scaling)
    else:
        raise ValueError(f"Unknown map configuration: {configuration}")

    coboundary_consts = compute_coboundary(struct_consts, basis, parity, f_dict)

    schema4 = {
        "schema_version": "5.0",
        "algebra": schema1["algebra"],
        "central_elements": schema1["central_elements"],
        "map_f": map_info,
        "basis": schema1["basis"],
        "parity": schema1["parity"],
        "coboundary_structure_constants": coboundary_consts,
        "metadata": {
            "generated_by": "src/C_coboundary.py",
            "generation_date": datetime.now().strftime("%Y-%m-%d"),
            "configuration": configuration,
            "references": [
                "Frappat et al. (2000), Dictionary on Lie Algebras and Superalgebras",
                "docs/math/C_coboundary_definition.md"
            ]
        }
    }
    return schema4


def generate_all_coboundary_files(output_dir="data", configuration="mode_paired_exchange", scaling=1):
    os.makedirs(output_dir, exist_ok=True)
    generated_files = []
    for n in [1, 2, 3]:
        filepath = os.path.join(output_dir, f"C_{n}_coboundary.json")
        print(f"Generating {filepath} for C({n+1}) with configuration '{configuration}'...")
        schema_dict = generate_schema_4_dict(n, configuration=configuration, scaling=scaling)
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(schema_dict, f, indent=2, ensure_ascii=False)
        print(f"Saved {filepath} ({len(schema_dict['coboundary_structure_constants'])} coboundary entries).")
        generated_files.append(filepath)
    return generated_files


if __name__ == "__main__":
    generate_all_coboundary_files()
