"""
C_gamma_generator.py: Generates Schema 2 (gamma structure / inhomogeneous deformation)
for C(n+1) = osp(2|2n) across n=1, 2, 3.
"""

import json
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from collections import defaultdict
from fractions import Fraction
from typing import Dict, List, Tuple, Any
import sympy as sp

from src.C_generators import (
    get_basis_lists,
    get_generator_operators,
    Operator,
)


def get_order_key(n: int) -> Dict[str, int]:
    keys = {"a_1_p": 0, "a_1_m": 1}
    idx = 2
    for k in range(1, n + 1):
        keys[f"b_{k}_p"] = idx
        keys[f"b_{k}_m"] = idx + 1
        idx += 2
    return keys


def get_gb_matrix_info(n: int) -> Dict[str, Any]:
    """Define the gb_matrix (size 2 x 2n) and parameter listing."""
    rows = ["a_1_p", "a_1_m"]
    cols = []
    for k in range(1, n + 1):
        cols.extend([f"b_{k}_p", f"b_{k}_m"])

    matrix = []
    all_params = []
    for r in rows:
        row_params = []
        for c in cols:
            pname = f"gb_{r}_{c}"
            row_params.append(pname)
            all_params.append(pname)
        matrix.append(row_params)

    return {
        "dimensions": [2, 2 * n],
        "rows": rows,
        "columns": cols,
        "parameters": all_params,
        "matrix": matrix,
        "count": 4 * n,
        "parity": 1,
        "description": f"Inhomogeneous deformation gb parameter matrix of size 2 x {2*n} (total {4*n} parameters, parity 1)"
    }


def compute_gamma_structure(n: int) -> Tuple[Dict[Tuple[str, str, str, str], Fraction], Dict[str, Any]]:
    """Compute all gamma coefficients gamma_{abc}^{mu} where
    [X_a, Y_b]_gamma = [X_a, Y_b]_0 + kappa * sum_{c, mu} Gamma_{abc}^{mu} * gb_{mu} * Z_c.
    """
    order_keys = get_order_key(n)
    memo_reduce = {}

    def reduce_word_memo(word_tuple: tuple) -> Tuple[Operator, Dict[str, Operator]]:
        if word_tuple in memo_reduce:
            return memo_reduce[word_tuple]
        word = list(word_tuple)
        inv_idx = -1
        for i in range(len(word) - 1):
            if order_keys[word[i]] > order_keys[word[i + 1]]:
                inv_idx = i
                break
        if inv_idx == -1:
            if word.count("a_1_p") > 1 or word.count("a_1_m") > 1:
                res = (Operator(n), {})
                memo_reduce[word_tuple] = res
                return res
            fp = word.count("a_1_p")
            fm = word.count("a_1_m")
            b_modes = []
            for k in range(1, n + 1):
                bp = word.count(f"b_{k}_p")
                bm = word.count(f"b_{k}_m")
                b_modes.append((bp, bm))
            mon = ((fp, fm), tuple(b_modes))
            op = Operator(n, {mon: 1})
            res = (op, {})
            memo_reduce[word_tuple] = res
            return res

        x, y = word[inv_idx], word[inv_idx + 1]
        prefix = word[:inv_idx]
        suffix = word[inv_idx + 2:]

        # Case 1: Both fermions
        if x.startswith("a_") and y.startswith("a_"):
            res_A = reduce_word_memo(tuple(prefix + suffix))
            res_B = reduce_word_memo(tuple(prefix + [y, x] + suffix))
            op0 = res_A[0].add(res_B[0].scale(-1))
            gb_dict = defaultdict(lambda: Operator(n))
            for gb, op in res_A[1].items():
                gb_dict[gb] = gb_dict[gb].add(op)
            for gb, op in res_B[1].items():
                gb_dict[gb] = gb_dict[gb].add(op.scale(-1))
            clean_gb = {k: v for k, v in gb_dict.items() if len(v.terms) > 0}
            res = (op0, clean_gb)
            memo_reduce[word_tuple] = res
            return res

        # Case 2: Both bosons
        if x.startswith("b_") and y.startswith("b_"):
            px, py = x.split("_"), y.split("_")
            if px[1] == py[1] and px[2] == "m" and py[2] == "p":
                res_A = reduce_word_memo(tuple(prefix + suffix))
                res_B = reduce_word_memo(tuple(prefix + [y, x] + suffix))
                op0 = res_A[0].add(res_B[0])
                gb_dict = defaultdict(lambda: Operator(n))
                for gb, op in res_A[1].items():
                    gb_dict[gb] = gb_dict[gb].add(op)
                for gb, op in res_B[1].items():
                    gb_dict[gb] = gb_dict[gb].add(op)
                clean_gb = {k: v for k, v in gb_dict.items() if len(v.terms) > 0}
                res = (op0, clean_gb)
                memo_reduce[word_tuple] = res
                return res
            else:
                res = reduce_word_memo(tuple(prefix + [y, x] + suffix))
                memo_reduce[word_tuple] = res
                return res

        # Case 3: x is boson, y is fermion
        if x.startswith("b_") and y.startswith("a_"):
            gb_name = f"gb_{y}_{x}"
            res_A = reduce_word_memo(tuple(prefix + [y, x] + suffix))
            res_B_op = reduce_word_memo(tuple(prefix + suffix))[0]
            op0 = res_A[0]
            gb_dict = defaultdict(lambda: Operator(n))
            for gb, op in res_A[1].items():
                gb_dict[gb] = gb_dict[gb].add(op)
            gb_dict[gb_name] = gb_dict[gb_name].add(res_B_op.scale(-1))
            clean_gb = {k: v for k, v in gb_dict.items() if len(v.terms) > 0}
            res = (op0, clean_gb)
            memo_reduce[word_tuple] = res
            return res

        raise ValueError(f"Unhandled pair {x}, {y}")

    even_basis, odd_basis = get_basis_lists(n)
    all_basis = odd_basis + even_basis
    gens, parities, realizations = get_generator_operators(n)

    cartan = [f"H_{i}" for i in range(1, n + 2)]
    root_names = [name for name in all_basis if not name.startswith("H_")]
    m_a1 = ((1, 1), tuple((0, 0) for _ in range(n)))
    def m_bk(k):
        return ((0, 0), tuple((1, 1) if i == k else (0, 0) for i in range(n)))

    M = sp.zeros(n + 1, n + 1)
    M[0, 0] = 1
    M[1, 0] = 1
    for k in range(2, n + 1):
        M[k - 1, k - 1] = 1
        M[k, k - 1] = -1
    M[n, n] = -1
    inv_M = M.inv()

    def decompose_g(op: Operator) -> Dict[str, Fraction]:
        coeffs = {}
        for rname in root_names:
            rmon = list(gens[rname].terms.keys())[0]
            if rmon in op.terms:
                c = op.terms[rmon]
                if c != 0:
                    coeffs[rname] = c
        v = sp.zeros(n + 1, 1)
        v[0] = op.terms.get(m_a1, Fraction(0))
        for k in range(n):
            v[k + 1] = op.terms.get(m_bk(k), Fraction(0))
        c_cartan = inv_M * v
        for idx in range(n + 1):
            val = Fraction(int(c_cartan[idx, 0]))
            if val != 0:
                coeffs[cartan[idx]] = val
        return coeffs

    gamma_entries = []
    gamma_dict = defaultdict(lambda: defaultdict(lambda: defaultdict(Fraction)))

    for X in all_basis:
        tX = realizations[X]["standard_form"]
        pX = parities[X]
        for Y in all_basis:
            tY = realizations[Y]["standard_form"]
            pY = parities[Y]
            sign_YX = - ((-1)**(pX * pY))

            # XY
            gb_XY = defaultdict(lambda: Operator(n))
            for t1 in tX:
                c1 = Fraction(t1["coeff"])
                w1 = t1["words"]
                for t2 in tY:
                    c2 = Fraction(t2["coeff"])
                    w2 = t2["words"]
                    _, gb_d = reduce_word_memo(tuple(w1 + w2))
                    for gb, op in gb_d.items():
                        gb_XY[gb] = gb_XY[gb].add(op.scale(c1 * c2))

            # YX
            gb_YX = defaultdict(lambda: Operator(n))
            for t1 in tY:
                c1 = Fraction(t1["coeff"])
                w1 = t1["words"]
                for t2 in tX:
                    c2 = Fraction(t2["coeff"])
                    w2 = t2["words"]
                    _, gb_d = reduce_word_memo(tuple(w1 + w2))
                    for gb, op in gb_d.items():
                        gb_YX[gb] = gb_YX[gb].add(op.scale(c1 * c2))

            all_gbs = set(gb_XY.keys()) | set(gb_YX.keys())
            for gb in sorted(all_gbs):
                op_gb = gb_XY.get(gb, Operator(n)).add(gb_YX.get(gb, Operator(n)).scale(sign_YX))
                dec = decompose_g(op_gb)
                for Z, c in sorted(dec.items()):
                    if c != 0:
                        gamma_dict[(X, Y)][Z][gb] += c
                        gamma_entries.append({
                            "X": X,
                            "Y": Y,
                            "Z": Z,
                            "param": gb,
                            "coeff": str(c) if c.denominator != 1 else str(c.numerator),
                            "sign_rule": "graded"
                        })

    return gamma_entries, gamma_dict


def generate_schema2_json(n: int) -> Dict[str, Any]:
    """Generate Schema 2 dictionary for C(n+1) = osp(2|2n)."""
    even_basis, odd_basis = get_basis_lists(n)
    gens, parities, _ = get_generator_operators(n)
    gb_info = get_gb_matrix_info(n)
    gamma_entries, _ = compute_gamma_structure(n)

    data = {
        "schema_version": "5.0",
        "algebra": {
            "family": "C",
            "m": 1,
            "n": n,
            "cartan_type": f"C({n+1})",
            "alternative_notation": {
                "osp": f"osp(2|{2*n})",
                "dimension_formula": "osp(2m|2n) with m=1, even = 2n^2 + n + 1, odd = 4n"
            },
            "dimension": {
                "total": 2 * n**2 + 5 * n + 1,
                "even": 2 * n**2 + n + 1,
                "odd": 4 * n
            }
        },
        "gb_matrix": gb_info,
        "basis": {
            "even": even_basis,
            "odd": odd_basis,
            "ordering_convention": "PBW: kappa < [odd: E_eps1_del{k}_pp/pm/mp/mm] < [even: H_k, E_2del{k}_p/m, E_del{i}_del{j}_pp/mm/pm/mp] (K = 1 is excluded)"
        },
        "parity": parities,
        "inhomogeneous_deformation": {
            "description": "Inhomogeneous deformation 2-cocycle gamma(X, Y) defined by [b_j^s, a_1^sigma] = -gb_{sigma, j, s} * kappa",
            "deformation_bracket_formula": "[X, Y]_gamma = [X, Y]_0 + kappa * gamma(X, Y)",
            "sign_rule": "graded: gamma(Y, X) = -(-1)^{p(X)p(Y)} gamma(X, Y)",
            "total_entries": len(gamma_entries),
            "gamma_coefficients": gamma_entries
        },
        "metadata": {
            "generated_by": "src/C_gamma_generator.py",
            "generation_date": "2026-10-04",
            "references": [
                "Frappat et al. (2000), Dictionary on Lie Algebras and Superalgebras",
                "Bakalov and Sullivan (2017)"
            ]
        }
    }
    return data


def main():
    os.makedirs("data", exist_ok=True)
    for n in [1, 2, 3]:
        t0 = time.time()
        print(f"Generating Schema 2 C_{n}_gamma.json for C({n+1}) = osp(2|{2*n})...")
        data = generate_schema2_json(n)
        filepath = f"data/C_{n}_gamma.json"
        with open(filepath, "w") as f:
            json.dump(data, f, indent=2)
        print(f"  Saved {filepath}: {data['inhomogeneous_deformation']['total_entries']} entries ({time.time() - t0:.2f}s).")


if __name__ == "__main__":
    main()
