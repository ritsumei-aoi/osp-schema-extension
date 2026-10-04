"""
C_gamma.py: Inhomogeneous deformation (gamma structure) generator for C(n+1) = osp(2|2n).
Computes deformation parameters (gb matrix) and 2-cocycle gamma structure constants for Schema 2 v5.0.
"""

from fractions import Fraction
import json
import os
from typing import Dict, List, Tuple, Any
import numpy as np

from src.C_generators import (
    OscillatorMonomial,
    OscillatorPoly,
    get_C_generators,
    generate_structure_constants
)


def get_deformation_parameters(n: int) -> List[str]:
    """
    Returns the 4n deformation parameters:
    gb_a1p_b{j}p, gb_a1p_b{j}m, gb_a1m_b{j}p, gb_a1m_b{j}m for j=1..n
    """
    params = []
    for j in range(1, n + 1):
        params.extend([
            f"gb_a1p_b{j}p",
            f"gb_a1p_b{j}m",
            f"gb_a1m_b{j}p",
            f"gb_a1m_b{j}m"
        ])
    return params


def osc_parity(w: str) -> int:
    return 1 if w.startswith("a_1_") else 0


def undeformed_bracket(w1: str, w2: str, n: int) -> Fraction:
    """
    Undeformed bracket [w1, w2}_0:
    {a_1^-, a_1^+} = 1
    [b_k^-, b_k^+] = 1, [b_k^+, b_k^-] = -1
    """
    if w1 == "a_1_m" and w2 == "a_1_p":
        return Fraction(1)
    if w1 == "a_1_p" and w2 == "a_1_m":
        return Fraction(1)
    for k in range(1, n + 1):
        if w1 == f"b_{k}_m" and w2 == f"b_{k}_p":
            return Fraction(1)
        if w1 == f"b_{k}_p" and w2 == f"b_{k}_m":
            return Fraction(-1)
    return Fraction(0)


def deformed_delta(w1: str, w2: str, n: int) -> Dict[str, Fraction]:
    """
    Deformed bracket at order kappa:
    [b_j^s, a_1^sigma] = - gb_{sigma, j, s} * kappa
    [a_1^sigma, b_j^s] = + gb_{sigma, j, s} * kappa
    """
    if w1.startswith("b_") and w2.startswith("a_1_"):
        sigma = w2.split("_")[2]
        parts = w1.split("_")
        return {f"gb_a1{sigma}_b{parts[1]}{parts[2]}": Fraction(-1)}
    if w1.startswith("a_1_") and w2.startswith("b_"):
        sigma = w1.split("_")[2]
        parts = w2.split("_")
        return {f"gb_a1{sigma}_b{parts[1]}{parts[2]}": Fraction(1)}
    return {}


def normal_order_word_deformed(
    words: List[str], coeff: Fraction, n: int, osc_order: Dict[str, int]
) -> Tuple[OscillatorPoly, Dict[str, OscillatorPoly]]:
    """
    Recursively normal-orders a word of oscillators in U(A) to order kappa.
    Returns (undeformed_poly, Dict[param, poly_at_order_kappa]).
    """
    # Nilpotency check for adjacent fermions:
    for i in range(len(words) - 1):
        if words[i] == words[i + 1] and words[i] in ["a_1_p", "a_1_m"]:
            return OscillatorPoly(n), {}

    for i in range(len(words) - 1):
        w1, w2 = words[i], words[i + 1]
        if osc_order[w1] > osc_order[w2]:
            p1, p2 = osc_parity(w1), osc_parity(w2)
            sign_swap = -1 if (p1 * p2) % 2 == 1 else 1

            swapped = list(words)
            swapped[i], swapped[i + 1] = w2, w1
            res_und, res_def = normal_order_word_deformed(swapped, coeff * sign_swap, n, osc_order)

            # Undeformed contraction
            c0 = undeformed_bracket(w1, w2, n)
            if c0 != 0:
                contracted = words[:i] + words[i + 2:]
                c_und, c_def = normal_order_word_deformed(contracted, coeff * c0, n, osc_order)
                res_und = res_und + c_und
                for p, poly in c_def.items():
                    res_def[p] = res_def.get(p, OscillatorPoly(n)) + poly

            # Deformed contraction at order kappa
            d_dict = deformed_delta(w1, w2, n)
            if d_dict:
                p_prefix = sum(osc_parity(w) for w in words[:i]) % 2
                sign_prefix = -1 if p_prefix == 1 else 1
                contracted = words[:i] + words[i + 2:]
                c_und, _ = normal_order_word_deformed(contracted, Fraction(1), n, osc_order)
                for p, val in d_dict.items():
                    term_poly = c_und * (coeff * val * sign_prefix)
                    res_def[p] = res_def.get(p, OscillatorPoly(n)) + term_poly

            return res_und, res_def

    # Already sorted
    ap = words.count("a_1_p")
    am = words.count("a_1_m")
    if ap > 1 or am > 1:
        return OscillatorPoly(n), {}
    bp = tuple(words.count(f"b_{k}_p") for k in range(1, n + 1))
    bm = tuple(words.count(f"b_{k}_m") for k in range(1, n + 1))
    mon = OscillatorMonomial(n, ap, am, bp, bm)
    return OscillatorPoly(n, {mon: coeff}), {}


def decompose_in_basis_g(
    poly: OscillatorPoly, basis: List[str], realizations: Dict[str, OscillatorPoly], n: int
) -> Dict[str, Fraction]:
    """
    Decomposes an element in the span of g (with central scalar K absorbed).
    """
    extended_basis = basis + ["K"]
    ext_realizations = dict(realizations)
    ext_realizations["K"] = OscillatorPoly(n, {OscillatorMonomial(n): Fraction(1)})

    all_monomials = set(poly.terms.keys())
    for name in extended_basis:
        for mon in ext_realizations[name].terms.keys():
            all_monomials.add(mon)

    sorted_monomials = sorted(all_monomials)
    mon_to_idx = {m: i for i, m in enumerate(sorted_monomials)}

    A = np.zeros((len(sorted_monomials), len(extended_basis)), dtype=float)
    b = np.zeros(len(sorted_monomials), dtype=float)

    for j, name in enumerate(extended_basis):
        for mon, coeff in ext_realizations[name].terms.items():
            A[mon_to_idx[mon], j] = float(coeff)

    for mon, coeff in poly.terms.items():
        b[mon_to_idx[mon]] = float(coeff)

    coeffs, _, _, _ = np.linalg.lstsq(A, b, rcond=None)

    res = {}
    for j, name in enumerate(basis):
        c_val = coeffs[j]
        if abs(c_val) > 1e-7:
            res[name] = Fraction(c_val).limit_denominator(120)

    return res


def compute_gamma_structure(n: int) -> Tuple[List[Dict[str, Any]], Dict[str, Dict[Tuple[str, str], Dict[str, Fraction]]]]:
    even_basis, odd_basis, parity, realizations, _ = get_C_generators(n)
    all_basis = odd_basis + even_basis
    params = get_deformation_parameters(n)

    osc_list = ["a_1_p", "a_1_m"]
    for k in range(1, n + 1):
        osc_list.extend([f"b_{k}_p", f"b_{k}_m"])
    osc_order = {name: i for i, name in enumerate(osc_list)}

    gamma_map: Dict[str, Dict[Tuple[str, str], Dict[str, Fraction]]] = {p: {} for p in params}

    # Iterate over all basis pairs
    for x_name in all_basis:
        px = parity[x_name]
        poly_x = realizations[x_name]
        for y_name in all_basis:
            py = parity[y_name]
            poly_y = realizations[y_name]
            sign_xy = -1 if (px * py) % 2 == 1 else 1

            gamma_terms: Dict[str, OscillatorPoly] = {}
            for mx, cx in poly_x.terms.items():
                wx = mx.words_list()
                for my, cy in poly_y.terms.items():
                    wy = my.words_list()

                    # Term 1: X Y
                    _, d1 = normal_order_word_deformed(wx + wy, cx * cy, n, osc_order)
                    for p, poly in d1.items():
                        gamma_terms[p] = gamma_terms.get(p, OscillatorPoly(n)) + poly

                    # Term 2: - (-1)^{px py} Y X
                    _, d2 = normal_order_word_deformed(wy + wx, - Fraction(sign_xy) * (cx * cy), n, osc_order)
                    for p, poly in d2.items():
                        gamma_terms[p] = gamma_terms.get(p, OscillatorPoly(n)) + poly

            for p, poly in gamma_terms.items():
                if not poly.is_zero():
                    decomp = decompose_in_basis_g(poly, all_basis, realizations, n)
                    if decomp:
                        gamma_map[p][(x_name, y_name)] = decomp

    # Format JSON entries
    gamma_structure_constants = []
    for x_name in all_basis:
        for y_name in all_basis:
            # Find all Z appearing in any param
            z_set = set()
            for p in params:
                if (x_name, y_name) in gamma_map[p]:
                    z_set.update(gamma_map[p][(x_name, y_name)].keys())

            for z_name in sorted(z_set):
                linear_comb = []
                for p in params:
                    c = gamma_map[p].get((x_name, y_name), {}).get(z_name, Fraction(0))
                    if c != 0:
                        c_str = str(c.numerator) if c.denominator == 1 else f"{c.numerator}/{c.denominator}"
                        linear_comb.append({
                            "param": p,
                            "coeff": c_str
                        })
                if linear_comb:
                    gamma_structure_constants.append({
                        "X": x_name,
                        "Y": y_name,
                        "Z": z_name,
                        "linear_combination": linear_comb
                    })

    return gamma_structure_constants, gamma_map


def generate_schema_2_json(n: int) -> Dict[str, Any]:
    gamma_structure_constants, _ = compute_gamma_structure(n)
    params = get_deformation_parameters(n)
    total_dim = (2 * n * n + n + 1) + (4 * n)

    data = {
        "schema_version": "5.0",
        "algebra": {
            "family": "C",
            "m": 1,
            "n": n,
            "cartan_type": f"C({n+1})",
            "alternative_notation": {
                "osp": f"osp(2|{2*n})",
                "dimension_formula": "osp(2m|2n) with m=1"
            },
            "dimension": {
                "total": total_dim,
                "even": 2 * n * n + n + 1,
                "odd": 4 * n,
                "formula": {
                    "even": "2*n^2 + n + 1",
                    "odd": "4*n",
                    "total": "2*n^2 + 5*n + 1"
                }
            }
        },
        "deformation_parameters": params,
        "gamma_structure_constants": gamma_structure_constants,
        "metadata": {
            "generated_by": "C_gamma.py",
            "generation_date": "2026-10-04",
            "references": [
                "Frappat et al. (2000), Dictionary on Lie Algebras and Superalgebras",
                "C_inhomogeneous_definition.md"
            ]
        }
    }
    return data


def generate_and_save_all_gamma(data_dir: str = "data"):
    os.makedirs(data_dir, exist_ok=True)
    for n in [1, 2, 3]:
        data = generate_schema_2_json(n)
        filename = os.path.join(data_dir, f"C_{n}_gamma.json")
        with open(filename, "w") as f:
            json.dump(data, f, indent=2)
        print(f"Generated {filename}: {len(data['gamma_structure_constants'])} gamma terms")


if __name__ == "__main__":
    generate_and_save_all_gamma()
