"""
C_generators.py: Generator script for C(n+1) = osp(2|2n) structure constants.
Produces Schema 1 JSON datasets conforming to docs/json_schema_specification.md.
"""

from collections import defaultdict
from fractions import Fraction
import itertools
import json
import os
from typing import Dict, List, Tuple, Any
import sympy as sp


def op_key(op: str) -> Tuple[int, int]:
    """Ordering key for individual oscillator operators."""
    if op == "a_1_p":
        return (0, 0)
    if op == "a_1_m":
        return (0, 1)
    parts = op.split("_")
    k = int(parts[1])
    s = 0 if parts[2] == "p" else 1
    return (k, s)


def reduce_word(word: List[str], coeff: Fraction = Fraction(1)) -> Dict[Tuple[str, ...], Fraction]:
    """
    Reduce an arbitrary oscillator word to normal-ordered form using CAR and CCR.
    - CAR: {a_1^-, a_1^+} = 1, (a_1^+)^2 = 0, (a_1^-)^2 = 0
    - CCR: [b_j^-, b_k^+] = delta_{jk}, [b_j^pm, b_k^pm] = 0
    - Cross: [b_k^pm, a_1^pm] = 0
    """
    terms = {tuple(word): coeff}
    while True:
        next_terms = defaultdict(Fraction)
        all_ordered = True
        for w, c in terms.items():
            if c == 0:
                continue
            # Nilpotent fermions check
            nilpotent = False
            for i in range(len(w) - 1):
                if w[i] == w[i + 1] and w[i].startswith("a_1"):
                    nilpotent = True
                    break
            if nilpotent:
                continue

            # Find first out-of-order adjacent pair
            inv_idx = -1
            for i in range(len(w) - 1):
                if op_key(w[i]) > op_key(w[i + 1]):
                    inv_idx = i
                    break

            if inv_idx == -1:
                next_terms[w] += c
            else:
                all_ordered = False
                u, v = w[inv_idx], w[inv_idx + 1]
                pre = w[:inv_idx]
                post = w[inv_idx + 2 :]
                if u.startswith("a_1") and v.startswith("a_1"):
                    # a_1_m * a_1_p = 1 - a_1_p * a_1_m
                    next_terms[pre + (v, u) + post] += -c
                    next_terms[pre + post] += c
                elif u.startswith("b_") and v.startswith("b_"):
                    parts_u = u.split("_")
                    parts_v = v.split("_")
                    if parts_u[1] == parts_v[1] and parts_u[2] == "m" and parts_v[2] == "p":
                        # b_k_m * b_k_p = b_k_p * b_k_m + 1
                        next_terms[pre + (v, u) + post] += c
                        next_terms[pre + post] += c
                    else:
                        # Commute
                        next_terms[pre + (v, u) + post] += c
                elif u.startswith("b_") and v.startswith("a_1"):
                    # Commute
                    next_terms[pre + (v, u) + post] += c
                else:
                    raise ValueError(f"Unhandled pair: {u}, {v}")
        terms = {k: v for k, v in next_terms.items() if v != 0}
        if all_ordered:
            break
    return terms


def add_elements(e1: Dict[Tuple[str, ...], Fraction], e2: Dict[Tuple[str, ...], Fraction]) -> Dict[Tuple[str, ...], Fraction]:
    res = defaultdict(Fraction, e1)
    for k, v in e2.items():
        res[k] += v
    return {k: v for k, v in res.items() if v != 0}


def scale_element(e: Dict[Tuple[str, ...], Fraction], factor: Fraction) -> Dict[Tuple[str, ...], Fraction]:
    return {k: v * factor for k, v in e.items() if v * factor != 0}


def multiply_elements(e1: Dict[Tuple[str, ...], Fraction], e2: Dict[Tuple[str, ...], Fraction]) -> Dict[Tuple[str, ...], Fraction]:
    res = defaultdict(Fraction)
    for w1, c1 in e1.items():
        for w2, c2 in e2.items():
            prod_word = list(w1) + list(w2)
            red = reduce_word(prod_word, c1 * c2)
            for w, c in red.items():
                res[w] += c
    return {k: v for k, v in res.items() if v != 0}


def super_bracket(e1: Dict[Tuple[str, ...], Fraction], p1: int,
                  e2: Dict[Tuple[str, ...], Fraction], p2: int) -> Dict[Tuple[str, ...], Fraction]:
    """Graded commutator: [e1, e2] = e1 * e2 - (-1)^(p1*p2) * e2 * e1."""
    prod1 = multiply_elements(e1, e2)
    prod2 = multiply_elements(e2, e1)
    sign = -1 if (p1 * p2 % 2 == 1) else 1
    return add_elements(prod1, scale_element(prod2, Fraction(-sign, 1)))


def build_basis(n: int) -> Dict[str, List[str]]:
    """Builds even and odd basis lists in PBW order."""
    even = []
    # 1. Cartans
    for k in range(1, n + 2):
        even.append(f"H_{k}")
    # 2. Positive long roots
    for k in range(1, n + 1):
        even.append(f"E_2del{k}_p")
    # 3. Positive cross roots
    for i in range(1, n + 1):
        for j in range(i + 1, n + 1):
            even.append(f"E_del{i}_del{j}_pp")
    # 4. Negative long roots
    for k in range(1, n + 1):
        even.append(f"E_2del{k}_m")
    # 5. Negative cross roots
    for i in range(1, n + 1):
        for j in range(i + 1, n + 1):
            even.append(f"E_del{i}_del{j}_mm")
    # 6. Mixed cross roots
    for i in range(1, n + 1):
        for j in range(i + 1, n + 1):
            even.append(f"E_del{i}_del{j}_pm")
            even.append(f"E_del{i}_del{j}_mp")

    odd = []
    for k in range(1, n + 1):
        odd.append(f"E_eps1_del{k}_pp")
        odd.append(f"E_eps1_del{k}_pm")
        odd.append(f"E_eps1_del{k}_mp")
        odd.append(f"E_eps1_del{k}_mm")

    return {
        "even": even,
        "odd": odd,
        "ordering_convention": "PBW: κ < [odd] < [even]"
    }


def build_oscillator_realizations(n: int) -> Tuple[Dict[str, Dict[Tuple[str, ...], Fraction]], Dict[str, int], Dict[str, Any]]:
    """
    Returns:
    - algebraic representations: dict mapping gen_name -> Dict[word, Fraction]
    - parities: dict mapping gen_name -> int
    - schema generator_realization block
    """
    gens: Dict[str, Dict[Tuple[str, ...], Fraction]] = {}
    parities: Dict[str, int] = {}
    realizations: Dict[str, Any] = {}

    # H_1
    gens["H_1"] = {("a_1_p", "a_1_m"): Fraction(1), ("b_1_p", "b_1_m"): Fraction(1)}
    parities["H_1"] = 0
    realizations["H_1"] = {
        "standard_form": [
            {"words": ["a_1_p", "a_1_m"], "coeff": "1"},
            {"words": ["b_1_p", "b_1_m"], "coeff": "1"}
        ],
        "frappat_form": "a_1^+ a_1^- + b_1^+ b_1^-",
        "parity": 0
    }

    # H_k (2 <= k <= n)
    for k in range(2, n + 1):
        gens[f"H_{k}"] = {
            (f"b_{k-1}_p", f"b_{k-1}_m"): Fraction(1),
            (f"b_{k}_p", f"b_{k}_m"): Fraction(-1)
        }
        parities[f"H_{k}"] = 0
        realizations[f"H_{k}"] = {
            "standard_form": [
                {"words": [f"b_{k-1}_p", f"b_{k-1}_m"], "coeff": "1"},
                {"words": [f"b_{k}_p", f"b_{k}_m"], "coeff": "-1"}
            ],
            "frappat_form": f"b_{k-1}^+ b_{k-1}^- - b_{k}^+ b_{k}^-",
            "parity": 0
        }

    # H_{n+1}
    gens[f"H_{n+1}"] = {
        (f"b_{n}_p", f"b_{n}_m"): Fraction(-1),
        (): Fraction(-1, 2)
    }
    parities[f"H_{n+1}"] = 0
    realizations[f"H_{n+1}"] = {
        "standard_form": [
            {"words": [f"b_{n}_p", f"b_{n}_m"], "coeff": "-1"},
            {"words": [], "coeff": "-1/2"}
        ],
        "frappat_form": f"-b_{n}^+ b_{n}^- - 1/2",
        "parity": 0
    }

    # Long roots
    for k in range(1, n + 1):
        gens[f"E_2del{k}_p"] = {(f"b_{k}_p", f"b_{k}_p"): Fraction(1)}
        parities[f"E_2del{k}_p"] = 0
        realizations[f"E_2del{k}_p"] = {
            "standard_form": [{"words": [f"b_{k}_p", f"b_{k}_p"], "coeff": "1"}],
            "frappat_form": f"(b_{k}^+)^2",
            "parity": 0
        }

        gens[f"E_2del{k}_m"] = {(f"b_{k}_m", f"b_{k}_m"): Fraction(1)}
        parities[f"E_2del{k}_m"] = 0
        realizations[f"E_2del{k}_m"] = {
            "standard_form": [{"words": [f"b_{k}_m", f"b_{k}_m"], "coeff": "1"}],
            "frappat_form": f"(b_{k}^-)^2",
            "parity": 0
        }

    # Cross roots
    for i in range(1, n + 1):
        for j in range(i + 1, n + 1):
            gens[f"E_del{i}_del{j}_pp"] = {(f"b_{i}_p", f"b_{j}_p"): Fraction(1)}
            parities[f"E_del{i}_del{j}_pp"] = 0
            realizations[f"E_del{i}_del{j}_pp"] = {
                "standard_form": [{"words": [f"b_{i}_p", f"b_{j}_p"], "coeff": "1"}],
                "frappat_form": f"b_{i}^+ b_{j}^+",
                "parity": 0
            }

            gens[f"E_del{i}_del{j}_mm"] = {(f"b_{i}_m", f"b_{j}_m"): Fraction(1)}
            parities[f"E_del{i}_del{j}_mm"] = 0
            realizations[f"E_del{i}_del{j}_mm"] = {
                "standard_form": [{"words": [f"b_{i}_m", f"b_{j}_m"], "coeff": "1"}],
                "frappat_form": f"b_{i}^- b_{j}^-",
                "parity": 0
            }

            gens[f"E_del{i}_del{j}_pm"] = {(f"b_{i}_p", f"b_{j}_m"): Fraction(1)}
            parities[f"E_del{i}_del{j}_pm"] = 0
            realizations[f"E_del{i}_del{j}_pm"] = {
                "standard_form": [{"words": [f"b_{i}_p", f"b_{j}_m"], "coeff": "1"}],
                "frappat_form": f"b_{i}^+ b_{j}^-",
                "parity": 0
            }

            gens[f"E_del{i}_del{j}_mp"] = {(f"b_{i}_m", f"b_{j}_p"): Fraction(1)}
            parities[f"E_del{i}_del{j}_mp"] = 0
            realizations[f"E_del{i}_del{j}_mp"] = {
                "standard_form": [{"words": [f"b_{i}_m", f"b_{j}_p"], "coeff": "1"}],
                "frappat_form": f"b_{i}^- b_{j}^+",
                "parity": 0
            }

    # Odd roots
    for k in range(1, n + 1):
        gens[f"E_eps1_del{k}_pp"] = {("a_1_p", f"b_{k}_p"): Fraction(1)}
        parities[f"E_eps1_del{k}_pp"] = 1
        realizations[f"E_eps1_del{k}_pp"] = {
            "standard_form": [{"words": ["a_1_p", f"b_{k}_p"], "coeff": "1"}],
            "frappat_form": f"a_1^+ b_{k}^+",
            "parity": 1
        }

        gens[f"E_eps1_del{k}_pm"] = {("a_1_p", f"b_{k}_m"): Fraction(1)}
        parities[f"E_eps1_del{k}_pm"] = 1
        realizations[f"E_eps1_del{k}_pm"] = {
            "standard_form": [{"words": ["a_1_p", f"b_{k}_m"], "coeff": "1"}],
            "frappat_form": f"a_1^+ b_{k}^-",
            "parity": 1
        }

        gens[f"E_eps1_del{k}_mp"] = {("a_1_m", f"b_{k}_p"): Fraction(1)}
        parities[f"E_eps1_del{k}_mp"] = 1
        realizations[f"E_eps1_del{k}_mp"] = {
            "standard_form": [{"words": ["a_1_m", f"b_{k}_p"], "coeff": "1"}],
            "frappat_form": f"a_1^- b_{k}^+",
            "parity": 1
        }

        gens[f"E_eps1_del{k}_mm"] = {("a_1_m", f"b_{k}_m"): Fraction(1)}
        parities[f"E_eps1_del{k}_mm"] = 1
        realizations[f"E_eps1_del{k}_mm"] = {
            "standard_form": [{"words": ["a_1_m", f"b_{k}_m"], "coeff": "1"}],
            "frappat_form": f"a_1^- b_{k}^-",
            "parity": 1
        }

    # Ordering description
    osc_list = ["a_1_p", "a_1_m"]
    for k in range(1, n + 1):
        osc_list.extend([f"b_{k}_p", f"b_{k}_m"])

    gen_realization_block = {
        "description": "Standard form with PBW ordering",
        "ordering": ", ".join(osc_list),
        "realizations": realizations
    }

    return gens, parities, gen_realization_block


def project_onto_basis(elem: Dict[Tuple[str, ...], Fraction],
                       basis_list: List[str],
                       gens: Dict[str, Dict[Tuple[str, ...], Fraction]]) -> Dict[str, Fraction]:
    """Decomposes an oscillator expression into the Lie superalgebra basis."""
    if not elem:
        return {}
    all_words = set(elem.keys())
    for name in basis_list:
        all_words.update(gens[name].keys())
    word_list = sorted(list(all_words), key=lambda w: (len(w), [op_key(x) for x in w]))

    M = []
    b = []
    for w in word_list:
        row = [gens[name].get(w, Fraction(0)) for name in basis_list]
        M.append(row)
        b.append(elem.get(w, Fraction(0)))

    sp_M = sp.Matrix(M)
    sp_b = sp.Matrix(b)
    sol = sp_M.gauss_jordan_solve(sp_b)[0]
    res = sp_M * sol - sp_b
    if any(r != 0 for r in res):
        raise ValueError(f"Expression {elem} not in the span of the basis!")

    coeffs = {}
    for i, name in enumerate(basis_list):
        if sol[i] != 0:
            coeffs[name] = Fraction(int(sol[i].p), int(sol[i].q))
    return coeffs


def compute_structure_constants(n: int) -> Tuple[List[Dict[str, Any]], List[str], Dict[str, int]]:
    """Computes all non-zero canonical graded brackets [X, Y] for X <= Y in PBW order."""
    basis_info = build_basis(n)
    # Total PBW order: odd then even
    total_pbw = basis_info["odd"] + basis_info["even"]
    gens, parities, _ = build_oscillator_realizations(n)

    struct_consts = []
    for i, name1 in enumerate(total_pbw):
        for j in range(i, len(total_pbw)):
            name2 = total_pbw[j]
            p1 = parities[name1]
            p2 = parities[name2]
            br = super_bracket(gens[name1], p1, gens[name2], p2)
            decomp = project_onto_basis(br, total_pbw, gens)
            for z_name, coeff in decomp.items():
                coeff_str = str(coeff.numerator) if coeff.denominator == 1 else f"{coeff.numerator}/{coeff.denominator}"
                struct_consts.append({
                    "X": name1,
                    "Y": name2,
                    "Z": z_name,
                    "coeff": coeff_str,
                    "sign_rule": "graded"
                })

    return struct_consts, total_pbw, parities


def generate_schema1(n: int) -> Dict[str, Any]:
    """Generates the complete Schema 1 dictionary for C(n+1) = osp(2|2n)."""
    basis_info = build_basis(n)
    gens, parities, gen_realizations = build_oscillator_realizations(n)
    struct_consts, total_pbw, _ = compute_structure_constants(n)

    boson_labels = []
    for k in range(1, n + 1):
        boson_labels.extend([f"b_{k}_p", f"b_{k}_m"])

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
                "total": 2 * n**2 + 5 * n + 1,
                "even": 2 * n**2 + n + 1,
                "odd": 4 * n,
                "formulas": {
                    "even": "2n^2 + n + 1",
                    "odd": "4n",
                    "total": "2n^2 + 5n + 1"
                }
            }
        },
        "oscillator_generators": {
            "fermions": {
                "count": 2,
                "m": 1,
                "labels": ["a_1_p", "a_1_m"],
                "description": "Standard fermionic CAR pair"
            },
            "bosons": {
                "count": 2 * n,
                "n": n,
                "labels": boson_labels,
                "description": f"Bosonic CCR oscillators b_i^± with i=1,...,n"
            }
        },
        "central_elements": {
            "kappa": {
                "parity": 1,
                "nilpotent_order": 2,
                "relation": "kappa^2 = 0",
                "description": "Odd central parameter for inhomogeneous deformation"
            },
            "K": {
                "parity": 0,
                "relation": "K = 1",
                "description": "Even central element (identity scaling)"
            }
        },
        "oscillator_relations": {
            "standard_fermion_anticommutators": {
                "description": "Canonical anticommutation relations for standard fermions",
                "relations": {
                    "anticommutator": "{a_1^-, a_1^+} = 1",
                    "nilpotency": "(a_1^+)^2 = 0, (a_1^-)^2 = 0"
                }
            },
            "bosonic_commutators": {
                "description": "Canonical commutation relations for bosonic oscillators",
                "relations": {
                    "same_type": "[b_i^±, b_j^±] = 0 for all i, j",
                    "conjugate_pair": "[b_i^-, b_j^+] = δ_{ij}"
                }
            },
            "mixed_commutators": {
                "boson_fermion": "[b_i^±, a_1^±] = 0 (undeformed)"
            }
        },
        "basis": basis_info,
        "parity": {gen: parities[gen] for gen in total_pbw},
        "generator_realization": gen_realizations,
        "structure_constants": struct_consts,
        "metadata": {
            "generated_by": "src/C_generators.py",
            "generation_date": "2026-10-05",
            "references": [
                "Frappat et al. (2000), Dictionary on Lie Algebras and Superalgebras",
                "handover/notation.md"
            ]
        }
    }
    return data


def main():
    os.makedirs("data", exist_ok=True)
    for n in [1, 2, 3]:
        schema = generate_schema1(n)
        filename = os.path.join("data", f"C_{n}_structure.json")
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(schema, f, indent=2)
        print(f"Generated {filename}: even={schema['algebra']['dimension']['even']}, "
              f"odd={schema['algebra']['dimension']['odd']}, "
              f"total={schema['algebra']['dimension']['total']}, "
              f"num_structure_constants={len(schema['structure_constants'])}")


if __name__ == "__main__":
    main()
