"""
Schema 2: gamma (inhomogeneous deformation) computation for C(n+1) = osp(2|2n).

The deformation: [b_j^s, a_1^sigma] = -gb_{sigma,j,s} * kappa.
For each generator pair (X, Y), gamma(X, Y) = sum_{sigma,j,s} gb_{sigma,j,s} * gamma_contrib_{sigma,j,s}(X, Y)
where gamma_contrib is a basis element (or linear combination).

Output: C_{n}_gamma.json for n=1,2,3.
"""

from __future__ import annotations
import json
import os
from datetime import date
from fractions import Fraction
from itertools import combinations

import sys
sys.path.insert(0, os.path.dirname(__file__))
from C_generators import (
    get_basis, get_parity, generator_monomials, express_in_basis,
    osc_parity, osc_stats, osc_order
)


def gb_label(sigma_char: str, j: int, s_char: str) -> str:
    """gb_{sigma,j,s} parameter label. sigma_char in {'p','m'}, s_char in {'p','m'}."""
    return f"gb_{sigma_char}_{j}_{s_char}"


def get_gb_params(n: int) -> dict:
    """Return gb_matrix parameters for C(n+1)."""
    params = {}
    for j in range(1, n + 1):
        for sigma_char in ['p', 'm']:
            for s_char in ['p', 'm']:
                label = gb_label(sigma_char, j, s_char)
                params[label] = {
                    "sigma": "+" if sigma_char == 'p' else "-",
                    "j": j,
                    "s": "+" if s_char == 'p' else "-",
                    "parity": 1
                }
    return params


def normal_order_with_gamma(oscs: list[str]) -> tuple[dict[tuple, Fraction], dict[str, dict[tuple, Fraction]]]:
    """
    Like normal_order_product but also tracks gamma contributions.

    The deformed relation: b_j^s * a_1^sigma = a_1^sigma * b_j^s - gb_{sigma,j,s}
    adds a contraction of -gb_{sigma,j,s} whenever b_j^s is swapped past a_1^sigma.

    Returns:
      (normal_dict, gamma_dict)
      - normal_dict: PBW monomial -> coefficient (same as normal_order_product)
      - gamma_dict: gb_label -> {PBW monomial -> coefficient}
    """
    order_map = {"a_1_p": 0, "a_1_m": 1}
    for k in range(1, 20):
        order_map[f"b_{k}_p"] = 2 + 2 * (k - 1)
        order_map[f"b_{k}_m"] = 3 + 2 * (k - 1)

    def zero_nilpotent(mono_list):
        seen = set()
        for x in mono_list:
            if osc_parity(x) == 1:
                if x in seen:
                    return True
                seen.add(x)
        return False

    def _is_b_a_pair(a_label, b_label):
        """Check if a_label is a bosonic oscillator and b_label is a fermionic oscillator."""
        return osc_parity(a_label) == 0 and osc_parity(b_label) == 1

    def _get_gb_label_for_swap(boson_label: str, fermion_label: str):
        """
        Return the gb label for the deformation contribution when boson (left) swaps with fermion (right).
        boson_label: e.g. 'b_1_p', fermion_label: e.g. 'a_1_p'
        Relation: [b_j^s, a_1^sigma] = b*a - a*b = -gb_{sigma,j,s}
        """
        # fermion: a_1_p -> sigma='p', a_1_m -> sigma='m'
        sigma_char = fermion_label[-1]  # 'p' or 'm'
        # boson: b_j_p -> j, s='p'; b_j_m -> j, s='m'
        parts = boson_label.split('_')  # ['b', '1', 'p'] or ['b', '1', 'm']
        j = int(parts[1])
        s_char = parts[2]
        return gb_label(sigma_char, j, s_char)

    # State: (normal_terms, gamma_terms)
    # normal_terms: {mono_tuple: Fraction}
    # gamma_terms: {gb_label: {mono_tuple: Fraction}}

    normal = {tuple(oscs): Fraction(1)}
    gamma: dict[str, dict[tuple, Fraction]] = {}

    def add_gamma(gb_lbl, mono_tuple, coeff):
        if gb_lbl not in gamma:
            gamma[gb_lbl] = {}
        gamma[gb_lbl][mono_tuple] = gamma[gb_lbl].get(mono_tuple, Fraction(0)) + coeff

    changed = True
    while changed:
        changed = False
        new_normal = {}
        new_gamma: dict[str, dict[tuple, Fraction]] = {}

        def merge_gamma(src_gamma: dict[str, dict[tuple, Fraction]]):
            for lbl, md in src_gamma.items():
                if lbl not in new_gamma:
                    new_gamma[lbl] = {}
                for mono, c in md.items():
                    new_gamma[lbl][mono] = new_gamma[lbl].get(mono, Fraction(0)) + c

        # Process normal terms
        for mono, coeff in normal.items():
            mono_list = list(mono)
            swapped = False
            for i in range(len(mono_list) - 1):
                a_label = mono_list[i]
                b_label = mono_list[i + 1]

                if order_map.get(a_label, 999) > order_map.get(b_label, 999):
                    pa = osc_parity(a_label)
                    pb = osc_parity(b_label)
                    sign = (-1) ** (pa * pb)
                    c = osc_stats(a_label, b_label)  # undeformed stat

                    new_mono_list = mono_list[:i] + [b_label, a_label] + mono_list[i + 2:]
                    c_mono_list = mono_list[:i] + mono_list[i + 2:]

                    key1 = tuple(new_mono_list)
                    key2 = tuple(c_mono_list)

                    new_normal[key1] = new_normal.get(key1, Fraction(0)) + coeff * sign
                    if c != 0:
                        new_normal[key2] = new_normal.get(key2, Fraction(0)) + coeff * c

                    # Gamma contribution: only when boson (left=a_label) passes fermion (right=b_label)
                    if _is_b_a_pair(a_label, b_label):
                        gb_lbl = _get_gb_label_for_swap(a_label, b_label)
                        # Contribution: coeff * (-1) * c_mono (from -gb * c_mono)
                        # Sign: b*a = a*b - gb*kappa, so contraction = -gb (per gb unit)
                        add_gamma(gb_lbl, key2, coeff * Fraction(-1))

                    swapped = True
                    break

            if not swapped:
                if not zero_nilpotent(mono_list):
                    new_normal[mono] = new_normal.get(mono, Fraction(0)) + coeff

        # Process gamma terms (they also need to be normal-ordered)
        for gb_lbl, gd in gamma.items():
            if gb_lbl not in new_gamma:
                new_gamma[gb_lbl] = {}
            for mono, coeff in gd.items():
                mono_list = list(mono)
                swapped = False
                for i in range(len(mono_list) - 1):
                    a_label = mono_list[i]
                    b_label = mono_list[i + 1]

                    if order_map.get(a_label, 999) > order_map.get(b_label, 999):
                        pa = osc_parity(a_label)
                        pb = osc_parity(b_label)
                        sign = (-1) ** (pa * pb)
                        c = osc_stats(a_label, b_label)

                        new_mono_list = mono_list[:i] + [b_label, a_label] + mono_list[i + 2:]
                        c_mono_list = mono_list[:i] + mono_list[i + 2:]

                        key1 = tuple(new_mono_list)
                        key2 = tuple(c_mono_list)

                        new_gamma[gb_lbl][key1] = new_gamma[gb_lbl].get(key1, Fraction(0)) + coeff * sign
                        if c != 0:
                            new_gamma[gb_lbl][key2] = new_gamma[gb_lbl].get(key2, Fraction(0)) + coeff * c

                        # Note: gamma terms don't generate second-order gamma (we neglect O(gb^2))
                        swapped = True
                        break

                if not swapped:
                    if not zero_nilpotent(mono_list):
                        new_gamma[gb_lbl][mono] = new_gamma[gb_lbl].get(mono, Fraction(0)) + coeff

        # Prune zeros
        new_normal = {k: v for k, v in new_normal.items() if v != 0}
        for lbl in list(new_gamma.keys()):
            new_gamma[lbl] = {k: v for k, v in new_gamma[lbl].items() if v != 0}
            if not new_gamma[lbl]:
                del new_gamma[lbl]

        if new_normal != normal or new_gamma != gamma:
            changed = True
        normal = new_normal
        gamma = new_gamma

    return normal, gamma


def supercommutator_with_gamma(X: dict, pX: int, Y: dict, pY: int) -> tuple[dict, dict[str, dict]]:
    """
    Compute [X,Y} with gamma tracking.
    Returns (normal_result, gamma_result).
    """
    normal_result = {}
    gamma_result: dict[str, dict[tuple, Fraction]] = {}

    def add_n(k, v):
        normal_result[k] = normal_result.get(k, Fraction(0)) + v

    def add_g(lbl, k, v):
        if lbl not in gamma_result:
            gamma_result[lbl] = {}
        gamma_result[lbl][k] = gamma_result[lbl].get(k, Fraction(0)) + v

    sign = (-1) ** (pX * pY)

    for mX, cX in X.items():
        for mY, cY in Y.items():
            # XY term
            n_xy, g_xy = normal_order_with_gamma(list(mX) + list(mY))
            for mono, c in n_xy.items():
                add_n(mono, cX * cY * c)
            for lbl, gd in g_xy.items():
                for mono, c in gd.items():
                    add_g(lbl, mono, cX * cY * c)

            # -sign * YX term
            n_yx, g_yx = normal_order_with_gamma(list(mY) + list(mX))
            for mono, c in n_yx.items():
                add_n(mono, -sign * cX * cY * c)
            for lbl, gd in g_yx.items():
                for mono, c in gd.items():
                    add_g(lbl, mono, -sign * cX * cY * c)

    normal_result = {k: v for k, v in normal_result.items() if v != 0}
    for lbl in list(gamma_result.keys()):
        gamma_result[lbl] = {k: v for k, v in gamma_result[lbl].items() if v != 0}
        if not gamma_result[lbl]:
            del gamma_result[lbl]

    return normal_result, gamma_result


def compute_gamma_coefficients(n: int) -> list[dict]:
    """
    Compute all non-zero gamma coefficients for C(n+1).
    Returns list of entries: {X, Y, Z, gb_param, coeff, sign_rule}.
    """
    even_basis, odd_basis = get_basis(n)
    all_basis = even_basis + odd_basis
    parity_map = get_parity(even_basis, odd_basis)
    gen_mono = generator_monomials(n)

    gen_order = {g: i for i, g in enumerate(all_basis)}
    entries = []

    for X in all_basis:
        for Y in all_basis:
            if gen_order[X] > gen_order[Y]:
                continue
            pX = parity_map[X]
            pY = parity_map[Y]
            mdX, _ = gen_mono[X]
            mdY, _ = gen_mono[Y]

            _, gamma = supercommutator_with_gamma(mdX, pX, mdY, pY)

            if not gamma:
                continue

            for gb_lbl, gd in gamma.items():
                if not gd:
                    continue
                try:
                    expressed = express_in_basis(gd, gen_mono)
                except ValueError as e:
                    print(f"WARNING: gamma[{X},{Y},{gb_lbl}] -> {e}")
                    continue

                for Z, c in expressed.items():
                    if c != 0:
                        entries.append({
                            "X": X, "Y": Y, "Z": Z,
                            "gb_param": gb_lbl,
                            "coeff": str(c),
                            "sign_rule": "graded"
                        })

    # Also generate reverse entries: [Y,X} = -(-1)^{pX*pY} [X,Y}
    reverses = []
    seen_forward = {(e["X"], e["Y"]) for e in entries}
    for e in entries:
        X, Y = e["X"], e["Y"]
        if X == Y:
            continue
        Z = e["Z"]
        gb_lbl = e["gb_param"]
        c = Fraction(e["coeff"])
        sign = -(-1) ** (parity_map[X] * parity_map[Y])
        reverse_c = sign * c
        if reverse_c != 0:
            reverses.append({
                "X": Y, "Y": X, "Z": Z,
                "gb_param": gb_lbl,
                "coeff": str(reverse_c),
                "sign_rule": "graded"
            })

    entries.extend(reverses)
    return entries


def build_schema2(n: int) -> dict:
    even_basis, odd_basis = get_basis(n)
    parity = get_parity(even_basis, odd_basis)
    gb_params = get_gb_params(n)
    gamma_entries = compute_gamma_coefficients(n)

    boson_labels = []
    for k in range(1, n + 1):
        boson_labels += [f"b_{k}_p", f"b_{k}_m"]

    return {
        "schema_version": "5.0",
        "algebra": {
            "family": "C", "m": 1, "n": n,
            "cartan_type": f"C({n+1})",
            "alternative_notation": {"osp": f"osp(2|{2*n})"},
        },
        "gb_matrix": {
            "size": 4 * n,
            "parameters": gb_params,
            "deformation_relation": "[b_j^s, a_1^sigma] = -gb_{sigma,j,s} * kappa",
            "description": "4n parity-1 deformation parameters for C(n+1)."
        },
        "gamma_coefficients": gamma_entries,
        "metadata": {
            "generated_by": "src/C_gamma.py",
            "generation_date": str(date.today()),
            "references": [
                "Frappat, Sciarrino, Sorba (2000)",
                "Bakalov and Sullivan (2017)"
            ]
        }
    }


def main():
    os.makedirs("data", exist_ok=True)
    for n in [1, 2, 3]:
        print(f"Building gamma n={n}...", flush=True)
        schema = build_schema2(n)
        fname = f"data/C_{n}_gamma.json"
        with open(fname, "w") as f:
            json.dump(schema, f, indent=2)
        gc_count = len(schema["gamma_coefficients"])
        print(f"  C_{n}_gamma.json: {gc_count} gamma entries")


if __name__ == "__main__":
    main()
