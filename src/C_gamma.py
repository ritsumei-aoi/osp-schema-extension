"""
C_gamma.py: Computes inhomogeneous deformation (gamma structure, Schema 2)
for C(n+1) = osp(2|2n) Lie superalgebras and generates Schema 2 JSON files.
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

from src.C_generators import (

    build_c_generators,
    generate_schema_1_dict,
    Monomial,
    Poly
)


def get_gb_matrix_info(n):
    """Construct gb_matrix structure and parameter names for C(n+1)."""
    row_labels = ["a_1_p", "a_1_m"]
    col_labels = []
    for j in range(1, n + 1):
        col_labels.extend([f"b_{j}_p", f"b_{j}_m"])

    param_names = []
    for row in ["p", "m"]:
        row_params = []
        for j in range(1, n + 1):
            for col in ["p", "m"]:
                row_params.append(f"gb_a1{row}_b{j}{col}")
        param_names.append(row_params)

    flat_params = [p for row in param_names for p in row]

    return {
        "dimensions": [2, 2 * n],
        "row_labels": row_labels,
        "col_labels": col_labels,
        "parameter_names": param_names,
        "flat_parameters": flat_params,
        "parity": 1,
        "exchange_relations": "[b_j^s, a_1^sigma] = - gb_{sigma, j, s} * kappa"
    }


def osc_rank(name, n):
    """Ordering for PBW standard form: a_1_p < a_1_m < b_1_p < b_1_m < ..."""
    if name == "a_1_p":
        return 0
    if name == "a_1_m":
        return 1
    parts = name.split("_")
    k = int(parts[1]) - 1
    s = 0 if parts[2] == "p" else 1
    return 2 + 2 * k + s


def normal_order_word_ua(word, n, sign_choice=1):
    """
    Normal order an oscillator word in U(A) to first order in kappa.
    Option 1 (Document standard):
    [b_j^s, a_1^sigma] = - gb_{sigma, j, s} * kappa
    => b_j^s a_1^sigma = a_1^sigma b_j^s - gb_{sigma, j, s} * kappa
    """
    current_terms = [(word, Fraction(1), False, None)]

    while True:
        next_terms = []
        all_sorted = True
        for w, coeff, is_kap, par in current_terms:
            pair_found = False
            for i in range(len(w) - 1):
                x, y = w[i], w[i + 1]
                rx, ry = osc_rank(x, n), osc_rank(y, n)
                if rx > ry:
                    pair_found = True
                    all_sorted = False
                    pre = w[:i]
                    suf = w[i + 2:]

                    if x == "a_1_m" and y == "a_1_p":
                        next_terms.append((pre + ("a_1_p", "a_1_m") + suf, -coeff, is_kap, par))
                        next_terms.append((pre + suf, coeff, is_kap, par))
                    elif x.startswith("b_") and y.startswith("b_"):
                        px, py = x.split("_"), y.split("_")
                        if px[1] == py[1] and px[2] == "m" and py[2] == "p":
                            next_terms.append((pre + (y, x) + suf, coeff, is_kap, par))
                            next_terms.append((pre + suf, coeff, is_kap, par))
                        else:
                            next_terms.append((pre + (y, x) + suf, coeff, is_kap, par))
                    elif x.startswith("b_") and y.startswith("a_"):
                        next_terms.append((pre + (y, x) + suf, coeff, is_kap, par))
                        if not is_kap:
                            sigma = "p" if "p" in y else "m"
                            px = x.split("_")
                            j, s = px[1], px[2]
                            gb_param = f"gb_a1{sigma}_b{j}{s}"
                            next_terms.append((pre + suf, -coeff * sign_choice, True, gb_param))
                    else:
                        next_terms.append((pre + (y, x) + suf, coeff, is_kap, par))
                    break

            if not pair_found:
                next_terms.append((w, coeff, is_kap, par))

        current_terms = next_terms
        if all_sorted:
            break

    undeff_poly = Poly(n=n)
    def_poly_by_param = defaultdict(lambda: Poly(n=n))

    for w, coeff, is_kap, par in current_terms:
        if w.count("a_1_p") > 1 or w.count("a_1_m") > 1:
            continue
        p_single = Poly.const(coeff, n=n)
        for osc in w:
            p_single = p_single * Poly.from_osc(osc, n)

        if not is_kap:
            undeff_poly = undeff_poly + p_single
        else:
            def_poly_by_param[par] = def_poly_by_param[par] + p_single

    return undeff_poly, def_poly_by_param


def decompose_mod_K(poly, basis_list, generators, n):
    """Decompose poly into basis_list of g modulo central K = 1."""
    all_monos = set()
    for b in basis_list:
        all_monos.update(generators[b].terms.keys())
    const_m = Monomial(0, 0, (0,) * n, (0,) * n)
    all_monos.add(const_m)
    all_monos = sorted(list(all_monos), key=lambda m: (m.fp, m.fm, m.bp, m.bm))
    mono_to_idx = {m: i for i, m in enumerate(all_monos)}

    for m in poly.terms.keys():
        if m not in mono_to_idx:
            return None

    M = sp.zeros(len(all_monos), len(basis_list) + 1)
    for col, b in enumerate(basis_list):
        for m, coeff in generators[b].terms.items():
            M[mono_to_idx[m], col] = sp.Rational(coeff.numerator, coeff.denominator)
    M[mono_to_idx[const_m], len(basis_list)] = 1

    v = sp.zeros(len(all_monos), 1)
    for m, coeff in poly.terms.items():
        v[mono_to_idx[m], 0] = sp.Rational(coeff.numerator, coeff.denominator)

    try:
        sol, params = M.gauss_jordan_solve(v)
        residual = M * sol - v
        if any(r != 0 for r in residual):
            return None
        res_g = {}
        for col, b in enumerate(basis_list):
            val = sol[col]
            if val != 0:
                res_g[b] = Fraction(int(val.p), int(val.q))
        return res_g
    except Exception:
        return None


def compute_gamma_structure_constants(n, data=None):
    """Compute all gamma coefficients gamma_{abc} (c_{XY}^{Z, param}) for C(n+1)."""
    if data is None:
        data = build_c_generators(n)

    full_basis = data["odd_basis"] + data["even_basis"]
    generators = data["generators"]
    parities = data["parities"]

    gamma_constants = []

    for X in full_basis:
        poly_X = generators[X]
        pX = parities[X]
        for Y in full_basis:
            poly_Y = generators[Y]
            pY = parities[Y]
            sign_XY = -1 if (pX * pY) % 2 == 1 else 1

            def_res = defaultdict(lambda: Poly(n=n))
            for mX, cX in poly_X.terms.items():
                wX = mX.to_words()
                for mY, cY in poly_Y.terms.items():
                    wY = mY.to_words()
                    c_prod = cX * cY

                    _, d_XY = normal_order_word_ua(tuple(wX + wY), n)
                    for par, poly in d_XY.items():
                        def_res[par] = def_res[par] + poly * c_prod

                    _, d_YX = normal_order_word_ua(tuple(wY + wX), n)
                    for par, poly in d_YX.items():
                        def_res[par] = def_res[par] - poly * (c_prod * sign_XY)

            for par, poly in def_res.items():
                if poly.terms:
                    decomp = decompose_mod_K(poly, full_basis, generators, n)
                    if decomp is None:
                        raise ValueError(f"Deformed bracket [{X}, {Y}] for {par} does not close in g mod K!")
                    for Z in full_basis:
                        if Z in decomp:
                            coeff = decomp[Z]
                            c_str = str(coeff.numerator) if coeff.denominator == 1 else f"{coeff.numerator}/{coeff.denominator}"
                            gamma_constants.append({
                                "X": X,
                                "Y": Y,
                                "Z": Z,
                                "param": par,
                                "coeff": c_str,
                                "sign_rule": "graded"
                            })

    return gamma_constants


def generate_schema_2_dict(n):
    """Generate complete Schema 2 dict conforming to json_schema_specification.md."""
    schema1 = generate_schema_1_dict(n)
    gb_info = get_gb_matrix_info(n)
    gamma_consts = compute_gamma_structure_constants(n)

    schema2 = {
        "schema_version": "5.0",
        "algebra": schema1["algebra"],
        "central_elements": schema1["central_elements"],
        "oscillator_generators": schema1["oscillator_generators"],
        "oscillator_relations": schema1["oscillator_relations"],
        "basis": schema1["basis"],
        "parity": schema1["parity"],
        "generator_realization": schema1["generator_realization"],
        "deformation_parameters": {
            "gb_matrix": {
                "dimensions": gb_info["dimensions"],
                "row_labels": gb_info["row_labels"],
                "col_labels": gb_info["col_labels"],
                "parameter_names": gb_info["parameter_names"],
                "parity": gb_info["parity"],
                "exchange_relations": gb_info["exchange_relations"]
            }
        },
        "inhomogeneous_deformation": {
            "gb_matrix": {
                "dimensions": gb_info["dimensions"],
                "row_labels": gb_info["row_labels"],
                "col_labels": gb_info["col_labels"],
                "parameter_names": gb_info["parameter_names"],
                "parity": gb_info["parity"],
                "exchange_relations": gb_info["exchange_relations"]
            },
            "gamma_structure_constants": gamma_consts
        },
        "gamma_structure_constants": gamma_consts,
        "metadata": {
            "generated_by": "src/C_gamma.py",
            "generation_date": datetime.now().strftime("%Y-%m-%d"),
            "references": [
                "Frappat et al. (2000), Dictionary on Lie Algebras and Superalgebras",
                "docs/math/C_inhomogeneous_definition.md"
            ]
        }
    }
    return schema2


def generate_all_gamma_files(output_dir="data"):
    os.makedirs(output_dir, exist_ok=True)
    generated_files = []
    for n in [1, 2, 3]:
        filepath = os.path.join(output_dir, f"C_{n}_gamma.json")
        print(f"Generating {filepath} for C({n+1})...")
        schema_dict = generate_schema_2_dict(n)
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(schema_dict, f, indent=2, ensure_ascii=False)
        print(f"Saved {filepath} ({len(schema_dict['gamma_structure_constants'])} gamma entries).")
        generated_files.append(filepath)
    return generated_files


if __name__ == "__main__":
    generate_all_gamma_files()
