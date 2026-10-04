import os
import sys
import json
from fractions import Fraction
from typing import Dict, List, Tuple, Any

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from src.C_generators import CSuperalgebra, SuperElement, Monomial


def get_order_key(osc: str) -> int:
    if osc == "a_1_p":
        return 0
    if osc == "a_1_m":
        return 1
    parts = osc.split("_")
    k = int(parts[1])
    sign = parts[2]
    if sign == "p":
        return 100 + k
    else:
        return 200 + k


def normal_order_sequence(oscs: List[str], n: int) -> Tuple[SuperElement, Dict[str, SuperElement]]:
    """
    Normal order a sequence of operators in W(1|n) with first-order deformation in kappa.
    Returns (undeformed_element, dict_of_param_to_element).
    """
    queue = [(Fraction(1), list(oscs), None)]
    final_c0 = SuperElement.zero()
    final_def: Dict[str, SuperElement] = {}

    while queue:
        coeff, current, param = queue.pop(0)

        # Check adjacent identical fermions
        has_double = False
        for i in range(len(current) - 1):
            if current[i] == current[i+1] and current[i].startswith("a_"):
                has_double = True
                break
        if has_double:
            continue

        # Check if sorted
        is_sorted = True
        for i in range(len(current) - 1):
            u, v = current[i], current[i+1]
            if get_order_key(u) > get_order_key(v):
                is_sorted = False
                if u.startswith("a_") and v.startswith("a_"):
                    # a_1_m a_1_p = 1 - a_1_p a_1_m
                    new_list1 = current[:i] + current[i+2:]
                    queue.append((coeff, new_list1, param))
                    new_list2 = current[:i] + ["a_1_p", "a_1_m"] + current[i+2:]
                    queue.append((-coeff, new_list2, param))
                elif u.startswith("b_") and v.startswith("b_"):
                    pu, pv = u.split("_"), v.split("_")
                    if pu[1] == pv[1] and pu[2] == "m" and pv[2] == "p":
                        # b_m b_p = b_p b_m + 1
                        new_list1 = current[:i] + [v, u] + current[i+2:]
                        queue.append((coeff, new_list1, param))
                        new_list2 = current[:i] + current[i+2:]
                        queue.append((coeff, new_list2, param))
                    else:
                        new_list = current[:i] + [v, u] + current[i+2:]
                        queue.append((coeff, new_list, param))
                else:
                    # u is boson, v is fermion: b_k^s a_1^sigma = a_1^sigma b_k^s - gb_{sigma, k, s} kappa
                    if u.startswith("b_") and v.startswith("a_"):
                        new_list1 = current[:i] + [v, u] + current[i+2:]
                        queue.append((coeff, new_list1, param))
                        if param is None:
                            f_clean = v.replace("_", "")
                            b_clean = u.replace("_", "")
                            p_name = f"gb_{f_clean}_{b_clean}"
                            new_list2 = current[:i] + current[i+2:]
                            queue.append((-coeff, new_list2, p_name))
                break

        if is_sorted:
            ap = current.count("a_1_p")
            am = current.count("a_1_m")
            if ap > 1 or am > 1:
                continue
            bp = [0]*n
            bm = [0]*n
            for osc in current:
                if osc.startswith("b_"):
                    parts = osc.split("_")
                    k = int(parts[1]) - 1
                    if parts[2] == "p":
                        bp[k] += 1
                    else:
                        bm[k] += 1
            m = Monomial(ap, am, tuple(bp), tuple(bm))
            elem = SuperElement({m: coeff})
            if param is None:
                final_c0 = final_c0 + elem
            else:
                final_def[param] = final_def.get(param, SuperElement.zero()) + elem

    return final_c0, final_def


def get_all_gb_params(n: int) -> List[str]:
    params = []
    fermions = ["a_1_p", "a_1_m"]
    bosons = []
    for k in range(1, n + 1):
        bosons.extend([f"b_{k}_p", f"b_{k}_m"])
    for f in fermions:
        for b in bosons:
            f_clean = f.replace("_", "")
            b_clean = b.replace("_", "")
            params.append(f"gb_{f_clean}_{b_clean}")
    return params


def decompose_into_algebra(alg: CSuperalgebra, elem: SuperElement) -> Dict[str, Fraction]:
    """
    Decompose an element in W(1|n) into the basis of C(n+1), modulo central scalar K=1.
    """
    if elem.is_zero():
        return {}

    res: Dict[str, Fraction] = {}
    rem = SuperElement(dict(elem.terms))

    # Match non-Cartan basis elements
    for name in alg.basis_all:
        if name.startswith("H_"):
            continue
        m = list(alg.realizations[name].terms.keys())[0]
        if m in rem.terms:
            c = rem.terms[m]
            res[name] = c
            rem = rem - (alg.realizations[name] * c)

    # Cartan projection (quadratic monomials a_1_p*a_1_m, and b_k_p*b_k_m for k=1..n)
    import numpy as np
    n = alg.n
    cartans = [f"H_{i}" for i in range(1, n + 2)]
    m_a = Monomial(1, 1, tuple([0]*n), tuple([0]*n))
    m_b_list = []
    for k in range(1, n + 1):
        bp, bm = [0]*n, [0]*n
        bp[k-1] = 1
        bm[k-1] = 1
        m_b_list.append(Monomial(0, 0, tuple(bp), tuple(bm)))

    vec = [float(rem.terms.get(m_a, Fraction(0)))] + [float(rem.terms.get(mb, Fraction(0))) for mb in m_b_list]
    mat = np.zeros((n + 1, n + 1))
    for j, h in enumerate(cartans):
        mat[0, j] = float(alg.realizations[h].terms.get(m_a, Fraction(0)))
        for i, mb in enumerate(m_b_list):
            mat[i + 1, j] = float(alg.realizations[h].terms.get(mb, Fraction(0)))

    sol = np.linalg.solve(mat, vec)
    for j, h in enumerate(cartans):
        val = Fraction(round(sol[j] * 120), 120)
        if round(float(val)) == float(val):
            val = Fraction(round(float(val)))
        elif round(float(val) * 2) == float(val) * 2:
            val = Fraction(round(float(val) * 2), 2)
        if val != 0:
            res[h] = val

    return res


def compute_gamma_for_pair(alg: CSuperalgebra, X: str, Y: str) -> Dict[str, Dict[str, Fraction]]:
    eX = alg.realizations[X]
    eY = alg.realizations[Y]
    pX, pY = alg.parity[X], alg.parity[Y]
    sign = -1 if (pX * pY == 1) else 1

    gamma_elem_dict: Dict[str, SuperElement] = {}

    for mX, cX in eX.terms.items():
        wX = mX.to_word_list()
        for mY, cY in eY.terms.items():
            wY = mY.to_word_list()
            # X * Y
            c0_xy, def_xy = normal_order_sequence(wX + wY, alg.n)
            # Y * X
            c0_yx, def_yx = normal_order_sequence(wY + wX, alg.n)

            all_params = set(def_xy.keys()).union(set(def_yx.keys()))
            for p in all_params:
                d_xy = def_xy.get(p, SuperElement.zero())
                d_yx = def_yx.get(p, SuperElement.zero())
                diff = (d_xy - (d_yx * sign)) * (cX * cY)
                if not diff.is_zero():
                    gamma_elem_dict[p] = gamma_elem_dict.get(p, SuperElement.zero()) + diff

    final_res: Dict[str, Dict[str, Fraction]] = {}
    for param, elem in gamma_elem_dict.items():
        if not elem.is_zero():
            decomp = decompose_into_algebra(alg, elem)
            if decomp:
                final_res[param] = decomp
    return final_res


def generate_all_schema2():
    for n in [1, 2, 3]:
        alg = CSuperalgebra(n)
        gb_params = get_all_gb_params(n)

        fermion_labels = ["a_1_p", "a_1_m"]
        boson_labels = []
        for k in range(1, n + 1):
            boson_labels.extend([f"b_{k}_p", f"b_{k}_m"])

        gamma_entries = []
        basis = alg.basis_all

        for X in basis:
            for Y in basis:
                gamma_dict = compute_gamma_for_pair(alg, X, Y)
                for param, z_dict in gamma_dict.items():
                    for Z, coeff in z_dict.items():
                        if coeff != 0:
                            coeff_str = str(coeff.numerator) if coeff.denominator == 1 else f"{coeff.numerator}/{coeff.denominator}"
                            gamma_entries.append({
                                "X": X,
                                "Y": Y,
                                "Z": Z,
                                "gb_param": param,
                                "coeff": coeff_str
                            })

        data = {
            "schema_version": "5.0",
            "algebra": {
                "family": "C",
                "m": 1,
                "n": n,
                "cartan_type": f"C({n+1})",
                "alternative_notation": {
                    "osp": f"osp(2|{2*n})",
                    "dimension_formula": f"osp(2m|2n) with m=1: even = 2n^2 + n + 1, odd = 4n, total = 2n^2 + 5n + 1"
                },
                "dimension": {
                    "total": alg.total_dim,
                    "even": alg.even_dim,
                    "odd": alg.odd_dim
                }
            },
            "gb_matrix": {
                "dimension": [2, 2 * n],
                "rows": fermion_labels,
                "cols": boson_labels,
                "parameter_count": 4 * n,
                "parameters": gb_params
            },
            "inhomogeneous_deformation": {
                "description": "Symbolic gamma coefficients gamma_{XY}^{Z, gb} for [X, Y]_gamma = [X, Y]_0 + kappa * sum(gb * gamma)",
                "gamma_structure": gamma_entries
            },
            "metadata": {
                "generated_by": "C_gamma_generators.py",
                "generation_date": "2026-10-05",
                "references": [
                    "docs/math/C_inhomogeneous_definition.md",
                    "Frappat et al. (2000)"
                ]
            }
        }

        out_path = f"data/C_{n}_gamma.json"
        with open(out_path, "w") as f:
            json.dump(data, f, indent=2)
        print(f"Generated {out_path}: {len(gb_params)} gb parameters, {len(gamma_entries)} gamma entries.")


if __name__ == "__main__":
    generate_all_schema2()
