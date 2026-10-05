"""
C(n+1) Inhomogeneous Deformation (Gamma Structure) Generator & Schema 2 Module
"""
import json
import os
import sys
from fractions import Fraction
from typing import Dict, List, Tuple, Any

try:
    from C_generators import (
        Monomial, OscillatorExpr, build_C_basis, decompose_expr,
        _normal_order_fermion, _normal_order_boson_single
    )
except ImportError:
    from src.C_generators import (
        Monomial, OscillatorExpr, build_C_basis, decompose_expr,
        _normal_order_fermion, _normal_order_boson_single
    )

def multiply_monomials_deformed(m1: Monomial, m2: Monomial, n: int) -> Dict[str, OscillatorExpr]:
    """
    Computes deformed product m1 *_gamma m2.
    Returns a dict mapping gb_param_name -> OscillatorExpr (coeff of kappa * gb_param).
    Also includes key 'undeformed' -> OscillatorExpr for the 0th order product.
    """
    results = {}

    # 1. Undeformed product
    try:
        from C_generators import multiply_monomials
    except ImportError:
        from src.C_generators import multiply_monomials
    results["undeformed"] = multiply_monomials(m1, m2, n)

    # 2. Deformed 1st order terms in kappa * gb
    # M1 = F1 * B1
    # M2 = F2 * B2
    # Swaps occur when moving B1 (bosonic factors of M1) past F2 (fermionic factors of M2).
    f2_factors = []
    if m2.a1p == 1: f2_factors.append(("a1p", 1, 0))
    if m2.a1m == 1: f2_factors.append(("a1m", 0, 1))

    if not f2_factors:
        return results

    b1_factors = []
    for k in range(n):
        p_count = m1.bp[k] if k < len(m1.bp) else 0
        m_count = m1.bm[k] if k < len(m1.bm) else 0
        for _ in range(p_count):
            b1_factors.append((f"b{k+1}p", k, True))
        for _ in range(m_count):
            b1_factors.append((f"b{k+1}m", k, False))

    if not b1_factors:
        return results

    f1_a1p = m1.a1p
    f1_a1m = m1.a1m

    for b_idx, (b_name, k_idx, is_pos) in enumerate(b1_factors):
        for f_idx, (f_name, f_a1p, f_a1m) in enumerate(f2_factors):
            gb_param = f"gb_{f_name}_{b_name}"

            rem_f2_a1p = 0 if f_name == "a1p" else m2.a1p
            rem_f2_a1m = 0 if f_name == "a1m" else m2.a1m

            f_terms = _normal_order_fermion(f1_a1p, f1_a1m, rem_f2_a1p, rem_f2_a1m)
            if not f_terms:
                continue

            rem_b1_bp = list(m1.bp)
            rem_b1_bm = list(m1.bm)
            if is_pos:
                rem_b1_bp[k_idx] -= 1
            else:
                rem_b1_bm[k_idx] -= 1

            b_term_lists = []
            for k in range(n):
                p1 = rem_b1_bp[k] if k < len(rem_b1_bp) else 0
                m1_b = rem_b1_bm[k] if k < len(rem_b1_bm) else 0
                p2 = m2.bp[k] if k < len(m2.bp) else 0
                m2_b = m2.bm[k] if k < len(m2.bm) else 0
                b_terms_k = _normal_order_boson_single(p1, m1_b, p2, m2_b)
                b_term_lists.append(b_terms_k)

            combined_b = [((), Fraction(1))]
            for k in range(n):
                new_combined = []
                for (b_prev, c_prev) in combined_b:
                    for ((p_k, m_k), c_k) in b_term_lists[k]:
                        new_combined.append((b_prev + ((p_k, m_k),), c_prev * c_k))
                combined_b = new_combined

            swap_coeff = Fraction(-1)

            expr = results.get(gb_param, OscillatorExpr())
            for f_mon, c_f in f_terms:
                for b_tuple, c_b in combined_b:
                    bp = tuple(t[0] for t in b_tuple)
                    bm = tuple(t[1] for t in b_tuple)
                    full_mon = Monomial(a1p=f_mon.a1p, a1m=f_mon.a1m, bp=bp, bm=bm)
                    expr.add_term(full_mon, swap_coeff * c_f * c_b)
            results[gb_param] = expr

    return results

def supercommutator_gamma(e1: OscillatorExpr, p1: int, e2: OscillatorExpr, p2: int, n: int) -> Dict[str, OscillatorExpr]:
    sign = -1 if (p1 == 1 and p2 == 1) else 1
    res_dict: Dict[str, OscillatorExpr] = {}

    for m1, c1 in e1.terms.items():
        for m2, c2 in e2.terms.items():
            prod_dict = multiply_monomials_deformed(m1, m2, n)
            for key, expr in prod_dict.items():
                if key not in res_dict:
                    res_dict[key] = OscillatorExpr()
                res_dict[key] = res_dict[key] + expr * (c1 * c2)

    for m2, c2 in e2.terms.items():
        for m1, c1 in e1.terms.items():
            prod_dict = multiply_monomials_deformed(m2, m1, n)
            for key, expr in prod_dict.items():
                if key not in res_dict:
                    res_dict[key] = OscillatorExpr()
                res_dict[key] = res_dict[key] - expr * (c1 * c2 * sign)

    return res_dict

def generate_C_gamma_json(n: int) -> Dict[str, Any]:
    even_labels, odd_labels, parity_dict, realizations = build_C_basis(n)
    all_basis = odd_labels + even_labels

    gb_labels = []
    col_labels = []
    for k in range(1, n + 1):
        col_labels.extend([f"b_{k}_p", f"b_{k}_m"])
        gb_labels.extend([
            f"gb_a1p_b{k}p", f"gb_a1p_b{k}m",
            f"gb_a1m_b{k}p", f"gb_a1m_b{k}m"
        ])

    gamma_terms = []
    total_gens = len(all_basis)

    for i in range(total_gens):
        for j in range(total_gens):
            lbl1 = all_basis[i]
            lbl2 = all_basis[j]
            p1 = parity_dict[lbl1]
            p2 = parity_dict[lbl2]

            expr1 = realizations[lbl1]
            expr2 = realizations[lbl2]

            sc_gamma = supercommutator_gamma(expr1, p1, expr2, p2, n)

            for gb_param in gb_labels:
                if gb_param in sc_gamma:
                    gamma_expr = sc_gamma[gb_param]
                    decomp = decompose_expr(gamma_expr, even_labels, odd_labels, realizations, n)
                    for target_lbl, coeff in decomp.items():
                        if coeff != 0:
                            gamma_terms.append({
                                "X": lbl1,
                                "Y": lbl2,
                                "Z": target_lbl,
                                "gb_param": gb_param,
                                "coeff": str(coeff.numerator) if coeff.denominator == 1 else f"{coeff.numerator}/{coeff.denominator}"
                            })

    schema_json = {
        "schema_version": "5.0",
        "algebra": {
            "family": "C",
            "m": 1,
            "n": n,
            "cartan_type": f"C({n+1})"
        },
        "gb_parameters": {
            "count": 4 * n,
            "matrix_shape": [2, 2 * n],
            "row_labels": ["a_1_p", "a_1_m"],
            "column_labels": col_labels,
            "labels": gb_labels
        },
        "gamma_terms": gamma_terms,
        "metadata": {
            "generated_by": "src/C_gamma.py",
            "references": [
                "docs/math/C_inhomogeneous_definition.md",
                "docs/json_schema_specification.md"
            ]
        }
    }
    return schema_json

def save_all_C_gamma_json(output_dir: str = "data"):
    os.makedirs(output_dir, exist_ok=True)
    for n in (1, 2, 3):
        data = generate_C_gamma_json(n)
        filepath = os.path.join(output_dir, f"C_{n}_gamma.json")
        with open(filepath, "w") as f:
            json.dump(data, f, indent=2)
        print(f"Saved {filepath} (gb_count: {data['gb_parameters']['count']}, gamma_terms count: {len(data['gamma_terms'])})")

if __name__ == "__main__":
    save_all_C_gamma_json()
