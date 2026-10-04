"""
C_generators.py: Generator script for C(n+1) = osp(2|2n) Lie superalgebra
structure constants and v5.0 JSON schema.
"""

from fractions import Fraction
import json
import math
import os
from typing import Dict, List, Tuple, Any, Optional


def multiply_fermion(f1: Tuple[int, int], f2: Tuple[int, int]) -> Dict[Tuple[int, int], Fraction]:
    """Multiplies two standard fermion normal-ordered monomials (a_1^+)^{e_p} (a_1^-)^{e_m}."""
    ep1, em1 = f1
    ep2, em2 = f2
    if em1 == 0:
        if ep1 + ep2 > 1:
            return {}
        return {(ep1 + ep2, em2): Fraction(1)}
    else:  # em1 == 1
        if ep2 == 0:
            if em1 + em2 > 1:
                return {}
            return {(ep1, em1 + em2): Fraction(1)}
        else:  # em1 == 1 and ep2 == 1: a_1^- a_1^+ = 1 - a_1^+ a_1^-
            if ep1 == 0 and em2 == 0:
                return {(0, 0): Fraction(1), (1, 1): Fraction(-1)}
            elif ep1 == 1 and em2 == 0:
                return {(1, 0): Fraction(1)}
            elif ep1 == 0 and em2 == 1:
                return {(0, 1): Fraction(1)}
            else:
                return {(1, 1): Fraction(1)}


def multiply_boson_mode(b1: Tuple[int, int], b2: Tuple[int, int]) -> Dict[Tuple[int, int], Fraction]:
    """Multiplies two normal-ordered monomials for a single bosonic mode (b_k^+)^u (b_k^-)^v."""
    u, v = b1
    up, vp = b2
    res = {}
    for j in range(min(v, up) + 1):
        coeff = Fraction(math.comb(v, j) * math.comb(up, j) * math.factorial(j))
        mon = (u + up - j, v + vp - j)
        res[mon] = res.get(mon, Fraction(0)) + coeff
    return res


def multiply_poly(p1: Dict[Tuple, Fraction], p2: Dict[Tuple, Fraction], n: int) -> Dict[Tuple, Fraction]:
    """Multiplies two polynomial elements in the oscillator algebra of C(n+1)."""
    res = {}
    for m1, c1 in p1.items():
        f1 = (m1[0], m1[1])
        b1_list = [(m1[2 + 2 * k], m1[3 + 2 * k]) for k in range(n)]
        for m2, c2 in p2.items():
            f2 = (m2[0], m2[1])
            b2_list = [(m2[2 + 2 * k], m2[3 + 2 * k]) for k in range(n)]
            f_prod = multiply_fermion(f1, f2)
            b_prods = [multiply_boson_mode(b1_list[k], b2_list[k]) for k in range(n)]
            curr = {(): Fraction(1)}
            for bp in b_prods:
                nxt = {}
                for prefix, pcoeff in curr.items():
                    for bmode, bcoeff in bp.items():
                        nxt[prefix + bmode] = pcoeff * bcoeff
                curr = nxt
            for fterm, fcoeff in f_prod.items():
                for bterm, bcoeff in curr.items():
                    full_mon = (fterm[0], fterm[1]) + bterm
                    tot_coeff = c1 * c2 * fcoeff * bcoeff
                    res[full_mon] = res.get(full_mon, Fraction(0)) + tot_coeff
    return {k: v for k, v in res.items() if v != 0}


def add_poly(p1: Dict[Tuple, Fraction], p2: Dict[Tuple, Fraction]) -> Dict[Tuple, Fraction]:
    res = dict(p1)
    for k, v in p2.items():
        res[k] = res.get(k, Fraction(0)) + v
    return {k: v for k, v in res.items() if v != 0}


def scale_poly(p: Dict[Tuple, Fraction], c: Any) -> Dict[Tuple, Fraction]:
    frac = Fraction(c)
    return {k: v * frac for k, v in p.items() if v * frac != 0}


def sub_poly(p1: Dict[Tuple, Fraction], p2: Dict[Tuple, Fraction]) -> Dict[Tuple, Fraction]:
    return add_poly(p1, scale_poly(p2, -1))


def superbracket(p1: Dict[Tuple, Fraction], p2: Dict[Tuple, Fraction],
                 p1_parity: int, p2_parity: int, n: int) -> Dict[Tuple, Fraction]:
    """Computes the Lie superbracket [p1, p2] = p1 p2 - (-1)^{p(p1)p(p2)} p2 p1."""
    p1p2 = multiply_poly(p1, p2, n)
    p2p1 = multiply_poly(p2, p1, n)
    if p1_parity == 1 and p2_parity == 1:
        return add_poly(p1p2, p2p1)
    else:
        return sub_poly(p1p2, p2p1)


def build_basis(n: int) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    """
    Constructs the even and odd basis generators of C(n+1) = osp(2|2n)
    in PBW order with their polynomial oscillator realizations.
    """
    def zero_mon():
        return tuple([0, 0] + [0, 0] * n)

    def mon_with(f=(0, 0), b_dict=None):
        if b_dict is None:
            b_dict = {}
        m = [f[0], f[1]]
        for k in range(1, n + 1):
            u, v = b_dict.get(k, (0, 0))
            m.extend([u, v])
        return tuple(m)

    even = []
    odd = []

    # 1. Cartan generators (n+1)
    # H_1 = a1+ a1- + b1+ b1-
    even.append({
        "name": "H_1",
        "parity": 0,
        "poly": {mon_with(f=(1, 1)): Fraction(1), mon_with(b_dict={1: (1, 1)}): Fraction(1)},
        "standard_form": [
            {"words": ["a_1_p", "a_1_m"], "coeff": "1"},
            {"words": ["b_1_p", "b_1_m"], "coeff": "1"}
        ],
        "frappat_form": "a_1^+ a_1^- + b_1^+ b_1^-"
    })

    # H_k = b_{k-1}+ b_{k-1}- - b_k+ b_k- for 2 <= k <= n
    for k in range(2, n + 1):
        even.append({
            "name": f"H_{k}",
            "parity": 0,
            "poly": {mon_with(b_dict={k - 1: (1, 1)}): Fraction(1), mon_with(b_dict={k: (1, 1)}): Fraction(-1)},
            "standard_form": [
                {"words": [f"b_{k-1}_p", f"b_{k-1}_m"], "coeff": "1"},
                {"words": [f"b_{k}_p", f"b_{k}_m"], "coeff": "-1"}
            ],
            "frappat_form": f"b_{k-1}^+ b_{k-1}^- - b_{k}^+ b_{k}^-"
        })

    # H_{n+1} = - b_n+ b_n- - 1/2
    even.append({
        "name": f"H_{n+1}",
        "parity": 0,
        "poly": {mon_with(b_dict={n: (1, 1)}): Fraction(-1), zero_mon(): Fraction(-1, 2)},
        "standard_form": [
            {"words": [f"b_{n}_p", f"b_{n}_m"], "coeff": "-1"},
            {"words": [], "coeff": "-1/2"}
        ],
        "frappat_form": f"-b_{n}^+ b_{n}^- - 1/2"
    })

    # 2. Even roots: 2\delta_k
    for k in range(1, n + 1):
        even.append({
            "name": f"E_2del{k}_p",
            "parity": 0,
            "poly": {mon_with(b_dict={k: (2, 0)}): Fraction(1)},
            "standard_form": [{"words": [f"b_{k}_p", f"b_{k}_p"], "coeff": "1"}],
            "frappat_form": f"(b_{k}^+)^2"
        })

    for i in range(1, n + 1):
        for j in range(i + 1, n + 1):
            even.append({
                "name": f"E_del{i}_del{j}_pp",
                "parity": 0,
                "poly": {mon_with(b_dict={i: (1, 0), j: (1, 0)}): Fraction(1)},
                "standard_form": [{"words": [f"b_{i}_p", f"b_{j}_p"], "coeff": "1"}],
                "frappat_form": f"b_{i}^+ b_{j}^+"
            })

    for k in range(1, n + 1):
        even.append({
            "name": f"E_2del{k}_m",
            "parity": 0,
            "poly": {mon_with(b_dict={k: (0, 2)}): Fraction(1)},
            "standard_form": [{"words": [f"b_{k}_m", f"b_{k}_m"], "coeff": "1"}],
            "frappat_form": f"(b_{k}^-)^2"
        })

    for i in range(1, n + 1):
        for j in range(i + 1, n + 1):
            even.append({
                "name": f"E_del{i}_del{j}_mm",
                "parity": 0,
                "poly": {mon_with(b_dict={i: (0, 1), j: (0, 1)}): Fraction(1)},
                "standard_form": [{"words": [f"b_{i}_m", f"b_{j}_m"], "coeff": "1"}],
                "frappat_form": f"b_{i}^- b_{j}^-"
            })

    for i in range(1, n + 1):
        for j in range(i + 1, n + 1):
            even.append({
                "name": f"E_del{i}_del{j}_pm",
                "parity": 0,
                "poly": {mon_with(b_dict={i: (1, 0), j: (0, 1)}): Fraction(1)},
                "standard_form": [{"words": [f"b_{i}_p", f"b_{j}_m"], "coeff": "1"}],
                "frappat_form": f"b_{i}^+ b_{j}^-"
            })

    for i in range(1, n + 1):
        for j in range(i + 1, n + 1):
            even.append({
                "name": f"E_del{i}_del{j}_mp",
                "parity": 0,
                "poly": {mon_with(b_dict={i: (0, 1), j: (1, 0)}): Fraction(1)},
                "standard_form": [{"words": [f"b_{i}_m", f"b_{j}_p"], "coeff": "1"}],
                "frappat_form": f"b_{i}^- b_{j}^+"
            })

    # 3. Odd roots: eps1 +- del_k
    for k in range(1, n + 1):
        odd.append({
            "name": f"E_eps1_del{k}_pp",
            "parity": 1,
            "poly": {mon_with(f=(1, 0), b_dict={k: (1, 0)}): Fraction(1)},
            "standard_form": [{"words": ["a_1_p", f"b_{k}_p"], "coeff": "1"}],
            "frappat_form": f"a_1^+ b_{k}^+"
        })
        odd.append({
            "name": f"E_eps1_del{k}_pm",
            "parity": 1,
            "poly": {mon_with(f=(1, 0), b_dict={k: (0, 1)}): Fraction(1)},
            "standard_form": [{"words": ["a_1_p", f"b_{k}_m"], "coeff": "1"}],
            "frappat_form": f"a_1^+ b_{k}^-"
        })
        odd.append({
            "name": f"E_eps1_del{k}_mp",
            "parity": 1,
            "poly": {mon_with(f=(0, 1), b_dict={k: (1, 0)}): Fraction(1)},
            "standard_form": [{"words": ["a_1_m", f"b_{k}_p"], "coeff": "1"}],
            "frappat_form": f"a_1^- b_{k}^+"
        })
        odd.append({
            "name": f"E_eps1_del{k}_mm",
            "parity": 1,
            "poly": {mon_with(f=(0, 1), b_dict={k: (0, 1)}): Fraction(1)},
            "standard_form": [{"words": ["a_1_m", f"b_{k}_m"], "coeff": "1"}],
            "frappat_form": f"a_1^- b_{k}^-"
        })

    return even, odd


def solve_in_basis(poly: Dict[Tuple, Fraction], basis_list: List[Dict[str, Any]]) -> Optional[Dict[str, Fraction]]:
    """Expresses an oscillator polynomial as a linear combination of basis elements."""
    all_mons = sorted(list(set().union(*[b["poly"].keys() for b in basis_list] + [poly.keys()])))
    M = []
    for mon in all_mons:
        row = [b["poly"].get(mon, Fraction(0)) for b in basis_list]
        row.append(poly.get(mon, Fraction(0)))
        M.append(row)

    rows = len(M)
    cols = len(basis_list)
    r = 0
    pivots = {}
    for c in range(cols):
        piv = None
        for i in range(r, rows):
            if M[i][c] != 0:
                piv = i
                break
        if piv is None:
            continue
        M[r], M[piv] = M[piv], M[r]
        lead = M[r][c]
        M[r] = [x / lead for x in M[r]]
        for i in range(rows):
            if i != r and M[i][c] != 0:
                factor = M[i][c]
                M[i] = [M[i][k] - factor * M[r][k] for k in range(cols + 1)]
        pivots[c] = r
        r += 1

    for i in range(r, rows):
        if M[i][-1] != 0:
            return None

    coeffs = {}
    for c, row_idx in pivots.items():
        val = M[row_idx][-1]
        if val != 0:
            coeffs[basis_list[c]["name"]] = val
    return coeffs


def build_c_structure_schema(n: int) -> Dict[str, Any]:
    """Generates the full Schema 1 JSON dictionary for C(n+1) = osp(2|2n)."""
    even_basis_objs, odd_basis_objs = build_basis(n)
    all_basis_objs = odd_basis_objs + even_basis_objs  # PBW: kappa < odd < even

    even_names = [g["name"] for g in even_basis_objs]
    odd_names = [g["name"] for g in odd_basis_objs]

    parity_dict = {}
    for g in even_basis_objs:
        parity_dict[g["name"]] = 0
    for g in odd_basis_objs:
        parity_dict[g["name"]] = 1

    generator_realizations = {}
    for g in all_basis_objs:
        generator_realizations[g["name"]] = {
            "standard_form": g["standard_form"],
            "frappat_form": g["frappat_form"],
            "parity": g["parity"]
        }

    structure_constants = []
    for g1 in all_basis_objs:
        for g2 in all_basis_objs:
            br = superbracket(g1["poly"], g2["poly"], g1["parity"], g2["parity"], n)
            if not br:
                continue
            decomp = solve_in_basis(br, all_basis_objs)
            if decomp is None:
                raise ValueError(f"Bracket [{g1['name']}, {g2['name']}] failed to decompose in basis!")
            for z_name, coeff in decomp.items():
                coeff_str = str(coeff.numerator) if coeff.denominator == 1 else f"{coeff.numerator}/{coeff.denominator}"
                structure_constants.append({
                    "X": g1["name"],
                    "Y": g2["name"],
                    "Z": z_name,
                    "coeff": coeff_str,
                    "sign_rule": "graded"
                })

    boson_labels = []
    for k in range(1, n + 1):
        boson_labels.extend([f"b_{k}_p", f"b_{k}_m"])

    schema_dict = {
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
                "total": 2 * n**2 + 5 * n + 1,
                "even": 2 * n**2 + n + 1,
                "odd": 4 * n
            }
        },
        "central_elements": {
            "kappa": {
                "label": "kappa",
                "parity": 1,
                "relation": "kappa^2 = 0",
                "description": "Odd central element parametrizing deformations."
            },
            "K": {
                "label": "K",
                "parity": 0,
                "relation": "K = 1",
                "description": "Even central identity element."
            }
        },
        "oscillator_generators": {
            "fermions": {
                "count": 2,
                "m": 1,
                "labels": ["a_1_p", "a_1_m"],
                "description": "Standard fermionic oscillator pair satisfying CAR."
            },
            "bosons": {
                "count": 2 * n,
                "n": n,
                "labels": boson_labels,
                "description": "Bosonic oscillators satisfying CCR."
            }
        },
        "oscillator_relations": {
            "standard_fermion_anticommutators": {
                "description": "Canonical anticommutation relations (CAR)",
                "relations": {
                    "conjugate_pair": "{a_1_m, a_1_p} = 1",
                    "nilpotency": "(a_1_p)^2 = 0, (a_1_m)^2 = 0"
                }
            },
            "bosonic_commutators": {
                "description": "Canonical commutation relations (CCR)",
                "relations": {
                    "same_type": "[b_i^±, b_j^±] = 0 for all i, j",
                    "conjugate_pair": "[b_i^-, b_j^+] = delta_{ij}"
                }
            },
            "mixed_commutators": {
                "boson_fermion": "[b_i^±, a_1^±] = 0 (unperturbed)"
            }
        },
        "basis": {
            "even": even_names,
            "odd": odd_names,
            "ordering_convention": "PBW: kappa < [odd] < [even]"
        },
        "parity": parity_dict,
        "generator_realization": {
            "description": "Standard form with PBW ordering",
            "ordering": f"a_1_p, a_1_m, {', '.join(boson_labels)}",
            "realizations": generator_realizations
        },
        "structure_constants": structure_constants,
        "metadata": {
            "generated_by": "src/C_generators.py",
            "generation_date": "2026-10-04",
            "references": [
                "Frappat et al. (2000), Dictionary on Lie Algebras and Superalgebras",
                "Bakalov and Sullivan (2017)"
            ]
        }
    }
    return schema_dict


def save_c_structure(n: int, output_dir: str = "data") -> str:
    """Generates and writes C_{n}_structure.json to the output directory."""
    os.makedirs(output_dir, exist_ok=True)
    schema = build_c_structure_schema(n)
    filepath = os.path.join(output_dir, f"C_{n}_structure.json")
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(schema, f, indent=2)
    return filepath


if __name__ == "__main__":
    for n_val in [1, 2, 3]:
        out_path = save_c_structure(n_val)
        print(f"Generated {out_path} for C({n_val+1})")
