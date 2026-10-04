"""
C_gamma.py: Computes the inhomogeneous deformation (gamma structure / Schema 2)
for C(n+1) = osp(2|2n) across n=1, 2, 3.
"""

import json
import os
import sys
from fractions import Fraction
from collections import defaultdict
import sympy as sp

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.C_generators import (
    build_basis_and_generators,
    OscillatorPoly,
    format_fraction,
)


def parse_word(w):
    parts = w.split("_")
    if parts[0] == "a":
        return ("a", parts[2])
    else:
        return ("b", int(parts[1]), parts[2])


def get_single_bracket_kappa(op1, op2):
    t1, *r1 = op1
    t2, *r2 = op2
    if t1 == "a" and t2 == "b":
        sigma = r1[0]
        j, s = r2
        return {f"gb_a1_{sigma}_b{j}_{s}": 1}
    elif t1 == "b" and t2 == "a":
        j, s = r1
        sigma = r2[0]
        return {f"gb_a1_{sigma}_b{j}_{s}": -1}
    return {}


def op_parity(op):
    return 1 if op[0] == "a" else 0


def op_to_poly(op, n):
    if op[0] == "a":
        sigma = op[1]
        return OscillatorPoly.from_monomial(n, 1, a_p=(1 if sigma == "p" else 0), a_m=(1 if sigma == "m" else 0))
    else:
        j, s = op[1], op[2]
        b_mode = [((1, 0) if s == "p" else (0, 1)) if idx == j - 1 else (0, 0) for idx in range(n)]
        return OscillatorPoly.from_monomial(n, 1, bosons=b_mode)


def compute_word_bracket_kappa(w1, w2, n):
    if len(w1) == 0 or len(w2) == 0:
        return defaultdict(OscillatorPoly)
    ops1 = [parse_word(x) for x in w1]
    ops2 = [parse_word(x) for x in w2]

    if len(ops1) == 2 and len(ops2) == 2:
        u1, u2 = ops1
        v1, v2 = ops2

        def single_u_bracket_v(u, v1, v2):
            r = defaultdict(OscillatorPoly)
            p_u = op_parity(u)
            p_v1 = op_parity(v1)
            poly_v1 = op_to_poly(v1, n)
            poly_v2 = op_to_poly(v2, n)

            b_u_v1 = get_single_bracket_kappa(u, v1)
            for gb, coeff in b_u_v1.items():
                r[gb] = r[gb] + poly_v2 * coeff

            b_u_v2 = get_single_bracket_kappa(u, v2)
            sign = (-1) ** (p_u * p_v1)
            for gb, coeff in b_u_v2.items():
                r[gb] = r[gb] + poly_v1 * (sign * coeff)
            return r

        p_u1 = op_parity(u1)
        p_u2 = op_parity(u2)
        p_v = (op_parity(v1) + op_parity(v2)) % 2
        poly_u1 = op_to_poly(u1, n)
        poly_u2 = op_to_poly(u2, n)

        res = defaultdict(OscillatorPoly)
        u2_v = single_u_bracket_v(u2, v1, v2)
        for gb, poly in u2_v.items():
            res[gb] = res[gb] + (poly_u1 * poly)

        u1_v = single_u_bracket_v(u1, v1, v2)
        sign2 = (-1) ** (p_u2 * p_v)
        for gb, poly in u1_v.items():
            res[gb] = res[gb] + (poly * poly_u2) * sign2
        return res
    return defaultdict(OscillatorPoly)


def compute_gen_bracket_kappa(real1, real2, n):
    res = defaultdict(OscillatorPoly)
    for t1 in real1:
        c1 = Fraction(t1["coeff"])
        w1 = t1["words"]
        for t2 in real2:
            c2 = Fraction(t2["coeff"])
            w2 = t2["words"]
            w_res = compute_word_bracket_kappa(w1, w2, n)
            for gb, poly in w_res.items():
                res[gb] = res[gb] + poly * (c1 * c2)
    return res


def compute_gamma_structure(n, structure_json_path=None):
    if structure_json_path is None:
        structure_json_path = f"data/C_{n}_structure.json"

    with open(structure_json_path, "r") as f:
        data = json.load(f)

    reals = data["generator_realization"]["realizations"]
    even_basis = data["basis"]["even"]
    odd_basis = data["basis"]["odd"]
    all_gens = even_basis + odd_basis
    parity = data["parity"]

    _, _, _, gen_poly = build_basis_and_generators(n)
    all_monomials = set()
    for g in all_gens:
        all_monomials.update(gen_poly[g].terms.keys())
    const_mono = (0, 0, tuple([(0, 0)] * n))
    all_monomials.add(const_mono)
    sorted_monomials = sorted(list(all_monomials))

    basis_plus_K = all_gens + ["K"]
    M = []
    for m in sorted_monomials:
        row = [gen_poly[g].terms.get(m, 0) for g in all_gens]
        row.append(Fraction(1) if m == const_mono else Fraction(0))
        M.append(row)
    M_sp = sp.Matrix(M)

    gamma_coefficients = []

    # Deformation parameters list
    gb_params = []
    for sigma in ["p", "m"]:
        for j in range(1, n + 1):
            for s in ["p", "m"]:
                gb_params.append(f"gb_a1_{sigma}_b{j}_{s}")

    for X in all_gens:
        for Y in all_gens:
            gb_polys = compute_gen_bracket_kappa(reals[X]["standard_form"], reals[Y]["standard_form"], n)
            for gb in gb_params:
                poly = gb_polys.get(gb)
                if not poly or not poly.terms:
                    continue
                v = sp.Matrix([poly.terms.get(m, 0) for m in sorted_monomials])
                c, _ = M_sp.gauss_jordan_solve(v)
                for idx, Z in enumerate(basis_plus_K):
                    val = c[idx]
                    if val != 0:
                        coeff_frac = Fraction(int(val.p), int(val.q)) if isinstance(val, sp.Rational) else Fraction(val)
                        gamma_coefficients.append({
                            "X": X,
                            "Y": Y,
                            "Z": Z,
                            "gb_param": gb,
                            "coeff": format_fraction(coeff_frac)
                        })

    boson_labels = []
    for k in range(1, n + 1):
        boson_labels.extend([f"b_{k}_p", f"b_{k}_m"])

    schema2_data = {
        "schema_version": "5.0",
        "layer": "Schema 2: Inhomogeneous Deformation (Gamma Structure)",
        "algebra": data["algebra"],
        "gb_matrix": {
            "dimensions": [2, 2 * n],
            "count": 4 * n,
            "fermion_labels": ["a_1_p", "a_1_m"],
            "boson_labels": boson_labels,
            "parameters": gb_params
        },
        "basis": data["basis"],
        "parity": parity,
        "gamma_coefficients": gamma_coefficients,
        "metadata": {
            "generated_by": "src/C_gamma.py",
            "generation_date": "2026-10-04",
            "references": [
                "docs/math/C_inhomogeneous_definition.md",
                "Frappat et al. (2000), arXiv:hep-th/9607161"
            ]
        }
    }
    return schema2_data


def generate_all_gamma_files(output_dir="data"):
    os.makedirs(output_dir, exist_ok=True)
    for n in [1, 2, 3]:
        data = compute_gamma_structure(n)
        filepath = os.path.join(output_dir, f"C_{n}_gamma.json")
        with open(filepath, "w") as f:
            json.dump(data, f, indent=2)
        print(f"Generated {filepath} ({len(data['gb_matrix']['parameters'])} gb params, {len(data['gamma_coefficients'])} gamma terms)")


if __name__ == "__main__":
    generate_all_gamma_files()
