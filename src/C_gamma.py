"""
C_gamma.py - Inhomogeneous deformation (gamma structure) generator for C(n+1) = osp(2|2n).

Computes the symbolic gamma coefficients gamma_{abc}(param) for C(n+1) inhomogeneous
deformation parametrized by the 2 x 2n gb matrix.
Outputs Schema 2 JSON files to data/C_{n}_gamma.json (n=1, 2, 3).
"""

import json
import os
import sys
from fractions import Fraction
from typing import Dict, List, Tuple, Any

try:
    from src.C_generators import (
        Monomial, Poly, build_basis_and_realizations
    )
except ModuleNotFoundError:
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from src.C_generators import (
        Monomial, Poly, build_basis_and_realizations
    )


def get_gb_params(n: int) -> List[str]:
    params = []
    for k in range(1, n + 1):
        params.extend([
            f"gb_a1p_b{k}p",
            f"gb_a1p_b{k}m",
            f"gb_a1m_b{k}p",
            f"gb_a1m_b{k}m"
        ])
    return params


def monomial_to_f_and_b(m: Monomial, n: int) -> Tuple[List[str], List[Tuple[int, str]]]:
    f_list = []
    if m.e_ap:
        f_list.append("p")
    if m.e_am:
        f_list.append("m")
    b_list = []
    for idx, count in enumerate(m.bosons):
        k = idx // 2 + 1
        pm = "p" if idx % 2 == 0 else "m"
        for _ in range(count):
            b_list.append((k, pm))
    return f_list, b_list


def make_fermion_poly(f_list: List[str], n: int) -> Poly:
    e_ap = f_list.count("p")
    e_am = f_list.count("m")
    if e_ap > 1 or e_am > 1:
        return Poly.zero(n)
    zero_b = (0,) * (2 * n)
    return Poly({Monomial(e_ap, e_am, zero_b): Fraction(1)})


def make_boson_poly(b_list: List[Tuple[int, str]], n: int) -> Poly:
    p = Poly.constant(Fraction(1), n)
    for k, pm in b_list:
        p = p * Poly.from_boson(k, pm, n)
    return p


def prod_kappa(m1: Monomial, m2: Monomial, n: int) -> Dict[str, Poly]:
    r"""
    Computes the first-order kappa contribution of m1 * m2.
    m1 = F1 B1, m2 = F2 B2.
    To normal-order, B1 must move past F2.
    For each b_{k_i}^{s_i} moving past a_1^{\sigma_j}, we get -gb_{a1_sigma, bk_s} * kappa.
    """
    f1, b1 = monomial_to_f_and_b(m1, n)
    f2, b2 = monomial_to_f_and_b(m2, n)
    res: Dict[str, Poly] = {}

    for i, (k, s) in enumerate(b1):
        for j, sigma in enumerate(f2):
            param = f"gb_a1{sigma}_b{k}{s}"
            rem_f2 = f2[:j] + f2[j+1:]
            rem_b1 = b1[:i] + b1[i+1:]

            f1_poly = make_fermion_poly(f1, n)
            rem_f2_poly = make_fermion_poly(rem_f2, n)
            f_poly = f1_poly * rem_f2_poly

            rem_b1_poly = make_boson_poly(rem_b1, n)
            b2_poly = make_boson_poly(b2, n)
            b_poly = rem_b1_poly * b2_poly

            term = (f_poly * b_poly) * Fraction(-1)
            res[param] = res.get(param, Poly.zero(n)) + term

    return res


def gamma_monomials(m1: Monomial, m2: Monomial, p1: int, p2: int, n: int) -> Dict[str, Poly]:
    """
    Computes [m1, m2]_kappa = prod_kappa(m1, m2) - (-1)^{p1 * p2} prod_kappa(m2, m1).
    """
    sign = -1 if (p1 == 1 and p2 == 1) else 1
    term1 = prod_kappa(m1, m2, n)
    term2 = prod_kappa(m2, m1, n)

    all_params = set(term1.keys()) | set(term2.keys())
    res: Dict[str, Poly] = {}
    for p in all_params:
        t1 = term1.get(p, Poly.zero(n))
        t2 = term2.get(p, Poly.zero(n))
        val = t1 - (t2 * Fraction(sign))
        if not val.is_zero():
            res[p] = val
    return res


def compute_gamma_poly_pair(P1: Poly, P2: Poly, n: int) -> Dict[str, Poly]:
    res: Dict[str, Poly] = {}
    for m1, c1 in P1.terms.items():
        for m2, c2 in P2.terms.items():
            p1 = (m1.e_ap + m1.e_am) % 2
            p2 = (m2.e_ap + m2.e_am) % 2
            gm = gamma_monomials(m1, m2, p1, p2, n)
            for param, p in gm.items():
                scaled = p * (c1 * c2)
                res[param] = res.get(param, Poly.zero(n)) + scaled
    return res


def decompose_onto_algebra(target: Poly, basis: List[str], poly_dict: Dict[str, Poly], n: int) -> Dict[str, Fraction]:
    """
    Decomposes target Poly into the Lie superalgebra basis modulo central scalar K=1.
    """
    if target.is_zero():
        return {}

    extended_basis = basis + ["K"]
    extended_poly = dict(poly_dict)
    extended_poly["K"] = Poly.constant(Fraction(1), n)

    all_monos = set()
    for gen in extended_basis:
        all_monos.update(extended_poly[gen].terms.keys())
    target_monos = set(target.terms.keys())

    mono_list = sorted(list(all_monos | target_monos), key=lambda m: (m.e_ap, m.e_am, m.bosons))
    mono_to_row = {m: i for i, m in enumerate(mono_list)}

    matrix_data = [[Fraction(0) for _ in extended_basis] for _ in mono_list]
    for col, gen in enumerate(extended_basis):
        for m, coeff in extended_poly[gen].terms.items():
            matrix_data[mono_to_row[m]][col] = coeff

    b_vec = [target.terms.get(m, Fraction(0)) for m in mono_list]

    M = [row[:] + [b_vec[i]] for i, row in enumerate(matrix_data)]
    n_rows = len(M)
    n_cols = len(extended_basis)

    pivot_row = 0
    pivot_cols = []
    for col in range(n_cols):
        found = -1
        for r in range(pivot_row, n_rows):
            if M[r][col] != 0:
                found = r
                break
        if found == -1:
            continue
        M[pivot_row], M[found] = M[found], M[pivot_row]
        pivot_val = M[pivot_row][col]
        for c in range(col, n_cols + 1):
            M[pivot_row][c] /= pivot_val
        for r in range(n_rows):
            if r != pivot_row and M[r][col] != 0:
                factor = M[r][col]
                for c in range(col, n_cols + 1):
                    M[r][c] -= factor * M[pivot_row][c]
        pivot_cols.append((pivot_row, col))
        pivot_row += 1

    for r in range(pivot_row, n_rows):
        if M[r][n_cols] != 0:
            raise ValueError(f"Inconsistent at mono {mono_list[r]}")

    sol: Dict[str, Fraction] = {}
    for r, col in pivot_cols:
        gen_name = extended_basis[col]
        val = M[r][n_cols]
        # Exclude central element K=1 from the Lie superalgebra basis projection
        if val != 0 and gen_name != "K":
            sol[gen_name] = val

    return sol


def generate_schema2_data(n: int) -> Dict[str, Any]:
    even_basis, odd_basis, parity, poly, frappat = build_basis_and_realizations(n)
    full_basis = odd_basis + even_basis
    params = get_gb_params(n)

    gamma_structure = []
    for gen_x in full_basis:
        for gen_y in full_basis:
            poly_x = poly[gen_x]
            poly_y = poly[gen_y]

            gamma_dict = compute_gamma_poly_pair(poly_x, poly_y, n)
            for param in params:
                gamma_poly = gamma_dict.get(param, Poly.zero(n))
                if gamma_poly.is_zero():
                    continue
                decomp = decompose_onto_algebra(gamma_poly, full_basis, poly, n)
                for gen_z, coeff in decomp.items():
                    if coeff != 0:
                        gamma_structure.append({
                            "X": gen_x,
                            "Y": gen_y,
                            "Z": gen_z,
                            "param": param,
                            "coeff": str(coeff.numerator) if coeff.denominator == 1 else f"{coeff.numerator}/{coeff.denominator}"
                        })

    filepath_s1 = f"data/C_{n}_structure.json"
    with open(filepath_s1, "r", encoding="utf-8") as f:
        s1_data = json.load(f)

    cols = []
    for k in range(1, n + 1):
        cols.extend([f"b_{k}_p", f"b_{k}_m"])

    schema2_data = {
        "schema_version": "5.0",
        "algebra": s1_data["algebra"],
        "central_elements": s1_data["central_elements"],
        "oscillator_generators": s1_data["oscillator_generators"],
        "oscillator_relations": s1_data["oscillator_relations"],
        "basis": s1_data["basis"],
        "parity": s1_data["parity"],
        "generator_realization": s1_data["generator_realization"],
        "gb_parameters": params,
        "gb_matrix": {
            "rows": ["a_1_p", "a_1_m"],
            "cols": cols,
            "shape": [2, 2 * n]
        },
        "inhomogeneous_deformation": {
            "description": "Symbolic gamma coefficients gamma_{abc}(param) where [X, Y]_gamma = [X, Y]_0 + kappa * sum_p param_p * gamma_{ab}^c(p) Z_c",
            "terms_count": len(gamma_structure),
            "gamma_structure": gamma_structure
        },
        "metadata": {
            "generated_by": "src/C_gamma.py",
            "generation_date": "2026-10-05",
            "references": [
                "docs/math/C_inhomogeneous_definition.md",
                "Frappat et al. (2000), Dictionary on Lie Algebras and Superalgebras"
            ]
        }
    }

    return schema2_data


def generate_all_schema2_files(output_dir: str = "data"):
    os.makedirs(output_dir, exist_ok=True)
    for n in [1, 2, 3]:
        schema2 = generate_schema2_data(n)
        filepath = os.path.join(output_dir, f"C_{n}_gamma.json")
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(schema2, f, indent=2)
        count = schema2["inhomogeneous_deformation"]["terms_count"]
        print(f"Generated {filepath}: {count} gamma structure entries (4n={4*n} parameters).")


if __name__ == "__main__":
    generate_all_schema2_files()
