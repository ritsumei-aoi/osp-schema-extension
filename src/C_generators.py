"""
C(n+1) Generator and Structure Constant Builder

This module defines the basis, oscillator realization, PBW ordering,
and structure constants for the Lie superalgebra family C(n+1) = osp(2|2n).
"""

from collections import defaultdict
from fractions import Fraction
import json
import os
from typing import Dict, List, Tuple, Any
import sympy as sp


def order_key(osc: str) -> Tuple[int, int]:
    """Return sorting key for oscillator ordering.
    Ordering: a_1_p < a_1_m < b_1_p < b_1_m < ... < b_n_p < b_n_m
    """
    if osc == "a_1_p":
        return (0, 0)
    if osc == "a_1_m":
        return (0, 1)
    if osc.startswith("b_"):
        parts = osc.split("_")
        k = int(parts[1])
        s = 0 if parts[2] == "p" else 1
        return (k, s)
    raise ValueError(f"Unknown oscillator: {osc}")


def normal_order_word(word: List[str], coeff: Fraction) -> Dict[Tuple[str, ...], Fraction]:
    """Reduce a word of oscillators to normally ordered PBW form using CAR and CCR."""
    current = {tuple(word): coeff}
    changed = True
    while changed:
        changed = False
        new_current = defaultdict(Fraction)
        for w, c in current.items():
            if c == 0:
                continue
            inversion_idx = -1
            for i in range(len(w) - 1):
                if order_key(w[i]) > order_key(w[i + 1]):
                    inversion_idx = i
                    break
                elif w[i] == w[i + 1]:
                    if w[i] in ("a_1_p", "a_1_m"):
                        inversion_idx = -2
                        break

            if inversion_idx == -2:
                # Nilpotent fermion
                changed = True
                continue
            elif inversion_idx == -1:
                new_current[w] += c
            else:
                changed = True
                i = inversion_idx
                x, y = w[i], w[i + 1]
                prefix = w[:i]
                suffix = w[i + 2:]

                if x == "a_1_m" and y == "a_1_p":
                    # CAR: a_1^- a_1^+ = 1 - a_1^+ a_1^-
                    new_current[prefix + ("a_1_p", "a_1_m") + suffix] += -c
                    new_current[prefix + suffix] += c
                elif x.startswith("b_") and y.startswith("b_"):
                    px = x.split("_")
                    py = y.split("_")
                    if px[1] == py[1] and px[2] == "m" and py[2] == "p":
                        # CCR: b_k^- b_k^+ = 1 + b_k^+ b_k^-
                        new_current[prefix + (f"b_{px[1]}_p", f"b_{px[1]}_m") + suffix] += c
                        new_current[prefix + suffix] += c
                    else:
                        # Commute
                        new_current[prefix + (y, x) + suffix] += c
                else:
                    # Mixed boson/fermion commute
                    new_current[prefix + (y, x) + suffix] += c
        current = new_current
    return {w: c for w, c in current.items() if c != 0}


def multiply_elements(
    poly1: Dict[Tuple[str, ...], Fraction], poly2: Dict[Tuple[str, ...], Fraction]
) -> Dict[Tuple[str, ...], Fraction]:
    """Multiply two oscillator polynomials and return the normally ordered result."""
    res = defaultdict(Fraction)
    for w1, c1 in poly1.items():
        for w2, c2 in poly2.items():
            combined_w = list(w1) + list(w2)
            c = c1 * c2
            no = normal_order_word(combined_w, c)
            for w, cw in no.items():
                res[w] += cw
    return {w: c for w, c in res.items() if c != 0}


def add_elements(
    poly1: Dict[Tuple[str, ...], Fraction],
    poly2: Dict[Tuple[str, ...], Fraction],
    scale2: Fraction = Fraction(1),
) -> Dict[Tuple[str, ...], Fraction]:
    """Add two oscillator polynomials."""
    res = defaultdict(Fraction, poly1)
    for w, c in poly2.items():
        res[w] += c * scale2
    return {w: c for w, c in res.items() if c != 0}


def superbracket(
    poly1: Dict[Tuple[str, ...], Fraction],
    p1: int,
    poly2: Dict[Tuple[str, ...], Fraction],
    p2: int,
) -> Dict[Tuple[str, ...], Fraction]:
    """Compute the Lie superalgebra bracket [X, Y} = X Y - (-1)^{p1 p2} Y X."""
    sign = Fraction(-1) if (p1 * p2) % 2 == 1 else Fraction(1)
    xy = multiply_elements(poly1, poly2)
    yx = multiply_elements(poly2, poly1)
    return add_elements(xy, yx, -sign)


def build_c_basis(n: int) -> Tuple[List[str], List[str], Dict[str, Dict[str, Any]]]:
    """Build the even basis, odd basis, and generator realizations for C(n+1).
    PBW ordering (Option A):
      odd roots grouped by sign of eps, then even Cartan, then even root vectors.
    """
    generators = {}

    # Odd basis (Option A order)
    odd_basis = []
    # eps > 0
    for k in range(1, n + 1):
        name = f"E_eps_del{k}_pp"
        odd_basis.append(name)
        generators[name] = {
            "poly": {("a_1_p", f"b_{k}_p"): Fraction(1)},
            "frappat_form": f"a_1^+ b_{k}^+",
            "parity": 1,
        }
    for k in range(1, n + 1):
        name = f"E_eps_del{k}_pm"
        odd_basis.append(name)
        generators[name] = {
            "poly": {("a_1_p", f"b_{k}_m"): Fraction(1)},
            "frappat_form": f"a_1^+ b_{k}^-",
            "parity": 1,
        }
    # eps < 0
    for k in range(1, n + 1):
        name = f"E_eps_del{k}_mp"
        odd_basis.append(name)
        generators[name] = {
            "poly": {("a_1_m", f"b_{k}_p"): Fraction(1)},
            "frappat_form": f"a_1^- b_{k}^+",
            "parity": 1,
        }
    for k in range(1, n + 1):
        name = f"E_eps_del{k}_mm"
        odd_basis.append(name)
        generators[name] = {
            "poly": {("a_1_m", f"b_{k}_m"): Fraction(1)},
            "frappat_form": f"a_1^- b_{k}^-",
            "parity": 1,
        }

    # Even basis
    even_basis = []
    # Cartan
    for k in range(1, n + 2):
        name = f"H_{k}"
        even_basis.append(name)
        if k == 1:
            generators[name] = {
                "poly": {("a_1_p", "a_1_m"): Fraction(1), ("b_1_p", "b_1_m"): Fraction(1)},
                "frappat_form": "a_1^+ a_1^- + b_1^+ b_1^-",
                "parity": 0,
            }
        elif k <= n:
            generators[name] = {
                "poly": {
                    (f"b_{k-1}_p", f"b_{k-1}_m"): Fraction(1),
                    (f"b_{k}_p", f"b_{k}_m"): Fraction(-1),
                },
                "frappat_form": f"b_{k-1}^+ b_{k-1}^- - b_{k}^+ b_{k}^-",
                "parity": 0,
            }
        else:  # k == n + 1
            generators[name] = {
                "poly": {(f"b_{n}_p", f"b_{n}_m"): Fraction(-1), (): Fraction(-1, 2)},
                "frappat_form": f"-b_{n}^+ b_{n}^- - 1/2",
                "parity": 0,
            }

    # Positive creation roots
    for k in range(1, n + 1):
        name = f"E_2del{k}_p"
        even_basis.append(name)
        generators[name] = {
            "poly": {(f"b_{k}_p", f"b_{k}_p"): Fraction(1)},
            "frappat_form": f"(b_{k}^+)^2",
            "parity": 0,
        }
    for i in range(1, n + 1):
        for j in range(i + 1, n + 1):
            name = f"E_del{i}_del{j}_pp"
            even_basis.append(name)
            generators[name] = {
                "poly": {(f"b_{i}_p", f"b_{j}_p"): Fraction(1)},
                "frappat_form": f"b_{i}^+ b_{j}^+",
                "parity": 0,
            }

    # Negative annihilation roots
    for k in range(1, n + 1):
        name = f"E_2del{k}_m"
        even_basis.append(name)
        generators[name] = {
            "poly": {(f"b_{k}_m", f"b_{k}_m"): Fraction(1)},
            "frappat_form": f"(b_{k}^-)^2",
            "parity": 0,
        }
    for i in range(1, n + 1):
        for j in range(i + 1, n + 1):
            name = f"E_del{i}_del{j}_mm"
            even_basis.append(name)
            generators[name] = {
                "poly": {(f"b_{i}_m", f"b_{j}_m"): Fraction(1)},
                "frappat_form": f"b_{i}^- b_{j}^-",
                "parity": 0,
            }

    # Mixed roots
    for i in range(1, n + 1):
        for j in range(i + 1, n + 1):
            name = f"E_del{i}_del{j}_pm"
            even_basis.append(name)
            generators[name] = {
                "poly": {(f"b_{i}_p", f"b_{j}_m"): Fraction(1)},
                "frappat_form": f"b_{i}^+ b_{j}^-",
                "parity": 0,
            }
            name2 = f"E_del{i}_del{j}_mp"
            even_basis.append(name2)
            generators[name2] = {
                "poly": {(f"b_{i}_m", f"b_{j}_p"): Fraction(1)},
                "frappat_form": f"b_{i}^- b_{j}^+",
                "parity": 0,
            }

    return even_basis, odd_basis, generators


def compute_structure_constants(n: int) -> Tuple[List[Dict[str, str]], Dict[str, Any]]:
    """Compute all non-vanishing structure constants and generate Schema 1 JSON dictionary."""
    even_basis, odd_basis, generators = build_c_basis(n)
    full_basis = even_basis + odd_basis

    # Collect all words appearing in basis
    all_words = set()
    for g in generators.values():
        all_words.update(g["poly"].keys())
    word_list = sorted(list(all_words))

    # Matrix for decomposing brackets into basis elements
    M_sp = sp.Matrix(
        [[generators[name]["poly"].get(w, Fraction(0)) for name in full_basis] for w in word_list]
    )

    structure_constants = []

    # Compute brackets for all pairs
    for i, X in enumerate(full_basis):
        pX = generators[X]["parity"]
        for j, Y in enumerate(full_basis):
            pY = generators[Y]["parity"]
            br = superbracket(generators[X]["poly"], pX, generators[Y]["poly"], pY)
            if not br:
                continue

            br_vec = sp.Matrix([br.get(w, Fraction(0)) for w in word_list])
            sol, _ = M_sp.gauss_jordan_solve(br_vec)

            for k, Z in enumerate(full_basis):
                c = sol[k]
                if c != 0:
                    structure_constants.append({
                        "X": X,
                        "Y": Y,
                        "Z": Z,
                        "coeff": str(c),
                        "sign_rule": "graded",
                    })

    # Prepare generator realizations in schema standard_form format
    ordering_str = "a_1_p, a_1_m, " + ", ".join(
        [f"b_{k}_p, b_{k}_m" for k in range(1, n + 1)]
    )
    realizations_dict = {}
    for name in full_basis:
        g = generators[name]
        sf = []
        for w, c in g["poly"].items():
            sf.append({"words": list(w), "coeff": str(c)})
        realizations_dict[name] = {
            "standard_form": sf,
            "frappat_form": g["frappat_form"],
            "parity": g["parity"],
        }

    # Parity dictionary
    parity_dict = {name: generators[name]["parity"] for name in full_basis}

    # Oscillator labels
    boson_labels = []
    for k in range(1, n + 1):
        boson_labels.extend([f"b_{k}_p", f"b_{k}_m"])

    schema_data = {
        "schema_version": "5.0",
        "algebra": {
            "family": "C",
            "m": 1,
            "n": n,
            "cartan_type": f"C({n+1})",
            "alternative_notation": {
                "osp": f"osp(2|{2*n})",
                "dimension_formula": "osp(2m|2n) with m=1",
            },
            "dimension": {
                "total": 2 * n**2 + 5 * n + 1,
                "even": 2 * n**2 + n + 1,
                "odd": 4 * n,
                "formula": {
                    "even": "2*n^2 + n + 1",
                    "odd": "4*n",
                    "total": "2*n^2 + 5*n + 1",
                },
            },
        },
        "central_elements": {
            "kappa": {
                "parity": 1,
                "description": "Formal odd central nilpotent parameter (kappa^2 = 0) parametrizing the inhomogeneous deformation",
            },
            "K": {
                "parity": 0,
                "description": "Even central element associated with canonical identity scalar in oscillator algebra",
            },
        },
        "oscillator_generators": {
            "fermions": {
                "count": 2,
                "m": 1,
                "labels": ["a_1_p", "a_1_m"],
                "description": "Standard fermionic oscillator pair a_1^± satisfying canonical anticommutation relations (CAR)",
            },
            "bosons": {
                "count": 2 * n,
                "n": n,
                "labels": boson_labels,
                "description": f"Bosonic oscillators b_k^± with k=1,...,{n} satisfying CCR",
            },
        },
        "oscillator_relations": {
            "standard_fermion_anticommutators": {
                "description": "Canonical anticommutation relations (CAR) for fermionic oscillators",
                "relations": {
                    "conjugate_pair": "{a_1^-, a_1^+} = 1",
                    "same_type": "{a_1^±, a_1^±} = 0",
                },
            },
            "bosonic_commutators": {
                "description": "Canonical commutation relations (CCR) for bosonic oscillators",
                "relations": {
                    "same_type": "[b_j^±, b_k^±] = 0 for all j, k",
                    "conjugate_pair": "[b_j^-, b_k^+] = δ_{jk}",
                },
            },
            "mixed_commutators": {
                "boson_fermion": "[b_k^±, a_1^σ] = 0 for all k and σ in {+,-}",
            },
        },
        "basis": {
            "even": even_basis,
            "odd": odd_basis,
            "ordering_convention": "PBW: κ < [odd] < [even]",
        },
        "parity": parity_dict,
        "generator_realization": {
            "description": "Standard form with PBW ordering",
            "ordering": ordering_str,
            "realizations": realizations_dict,
        },
        "structure_constants": structure_constants,
        "metadata": {
            "generated_by": "C_generators.py",
            "generation_date": "2026-10-12",
            "references": [
                "Frappat et al. (2000), Dictionary on Lie Algebras and Superalgebras",
                "Bakalov and Sullivan (2017)",
            ],
        },
    }

    return structure_constants, schema_data


def generate_all_schemas(output_dir: str = "data") -> None:
    """Generate Schema 1 JSON files for n=1, 2, 3."""
    os.makedirs(output_dir, exist_ok=True)
    for n in (1, 2, 3):
        _, schema_data = compute_structure_constants(n)
        filename = os.path.join(output_dir, f"C_{n}_structure.json")
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(schema_data, f, indent=2)
        print(f"Generated {filename}")


if __name__ == "__main__":
    generate_all_schemas()
