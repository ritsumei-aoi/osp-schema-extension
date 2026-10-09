"""
C(n+1) = osp(2|2n) structure constant generator.

Computes structure constants systematically via oscillator algebra.
Oscillator realization:
  - a_1^+, a_1^-: standard fermionic pair, {a_1^-, a_1^+} = 1
  - b_k^+, b_k^-: bosonic oscillators, [b_k^-, b_l^+] = delta_{kl}
"""

from __future__ import annotations
import json
import os
from datetime import date
from fractions import Fraction
from itertools import combinations

# ---------------------------------------------------------------------------
# Oscillator algebra
# ---------------------------------------------------------------------------
# Represent elements as dict: monomial_tuple -> Fraction coefficient
# Monomials are PBW-ordered tuples of oscillator labels.
# Oscillator ordering: a_1_p < a_1_m < b_1_p < b_1_m < b_2_p < ...

SCALAR = ()  # empty tuple = scalar 1


def osc_order(n: int) -> list[str]:
    oscs = ["a_1_p", "a_1_m"]
    for k in range(1, n + 1):
        oscs += [f"b_{k}_p", f"b_{k}_m"]
    return oscs


def osc_parity(label: str) -> int:
    return 1 if label.startswith("a_") else 0


def osc_stats(a: str, b: str) -> Fraction:
    """
    [a, b] in the CCR/CAR sense, where a and b are single oscillators.
    Returns the scalar c such that a*b = (-1)^{p(a)p(b)} b*a + c.
    i.e., c = [a,b] for bosons, c = {a,b} for two fermions.
    For mixed fermion-boson: c = 0.
    """
    pa, pb = osc_parity(a), osc_parity(b)
    if pa == 0 and pb == 0:
        # Both bosonic: [b_i_m, b_j_p] = delta_{ij}, [b_i_p, b_j_m] = -delta_{ij}
        # b_i_m and b_j_p: b^- = annihilation, b^+ = creation
        # [b^-, b^+] = 1 means b_k_m * b_k_p = b_k_p * b_k_m + 1
        a_idx = a[2:]  # e.g. "1_m" from "b_1_m"
        b_idx = b[2:]
        a_num = a_idx[:-2]  # "1"
        b_num = b_idx[:-2]
        a_sign = a_idx[-1]  # "p" or "m"
        b_sign = b_idx[-1]
        if a_num == b_num and a_sign == 'm' and b_sign == 'p':
            return Fraction(1)   # [b_k^-, b_k^+] = 1
        if a_num == b_num and a_sign == 'p' and b_sign == 'm':
            return Fraction(-1)  # [b_k^+, b_k^-] = -1
        return Fraction(0)
    elif pa == 1 and pb == 1:
        # Both fermionic: {a_1_m, a_1_p} = 1
        a_name = a[:-2]  # "a_1"
        b_name = b[:-2]
        a_sign = a[-1]
        b_sign = b[-1]
        if a_name == b_name and a_sign == 'm' and b_sign == 'p':
            return Fraction(1)   # {a_1^-, a_1^+} = 1
        if a_name == b_name and a_sign == 'p' and b_sign == 'm':
            return Fraction(1)   # {a_1^+, a_1^-} = 1
        # Same sign: a^2 = 0 for fermions
        if a == b:
            return Fraction(0)  # {a,a} contributes but (a,a) -> 0 from nilpotency
        return Fraction(0)
    else:
        return Fraction(0)  # boson-fermion always commute


def normal_order_product(oscs: list[str]) -> dict[tuple, Fraction]:
    """
    Given a list of oscillator labels (in any order), compute the
    PBW-normal-ordered expression using bubble sort and CAR/CAR relations.
    Returns dict: PBW-monomial -> coefficient.
    """
    ordering = ["a_1_p", "a_1_m"]
    # Will be computed for each n; pass as global-ish via closure -- actually
    # we handle ordering by index comparison within available oscillators.

    result = {tuple(oscs): Fraction(1)}
    # Repeatedly swap adjacent out-of-order pairs.
    # Use bubble sort: swap (i, i+1) if order[i] > order[i+1].

    order_map = {"a_1_p": 0, "a_1_m": 1}
    for k in range(1, 20):
        order_map[f"b_{k}_p"] = 2 + 2 * (k - 1)
        order_map[f"b_{k}_m"] = 3 + 2 * (k - 1)

    def zero_nilpotent(mono_list):
        """Return True if a fermionic oscillator appears twice (nilpotency => 0)."""
        seen = set()
        for x in mono_list:
            if osc_parity(x) == 1:
                if x in seen:
                    return True
                seen.add(x)
        return False

    changed = True
    while changed:
        changed = False
        new_result = {}
        for mono, coeff in result.items():
            mono = list(mono)
            swapped = False
            for i in range(len(mono) - 1):
                a_label = mono[i]
                b_label = mono[i + 1]

                if order_map.get(a_label, 999) > order_map.get(b_label, 999):
                    pa = osc_parity(a_label)
                    pb = osc_parity(b_label)
                    sign = (-1) ** (pa * pb)
                    c = osc_stats(a_label, b_label)

                    new_mono = mono[:i] + [b_label, a_label] + mono[i + 2:]
                    c_mono = mono[:i] + mono[i + 2:]

                    key1 = tuple(new_mono)
                    key2 = tuple(c_mono)

                    new_result[key1] = new_result.get(key1, Fraction(0)) + coeff * sign
                    if c != 0:
                        new_result[key2] = new_result.get(key2, Fraction(0)) + coeff * c

                    swapped = True
                    break

            if not swapped:
                # Monomial is fully PBW-sorted; now zero if fermion nilpotency applies
                if not zero_nilpotent(mono):
                    key = tuple(mono)
                    new_result[key] = new_result.get(key, Fraction(0)) + coeff

        if new_result != result:
            changed = True
        result = {k: v for k, v in new_result.items() if v != 0}

    return result


def supercommutator(X: dict, pX: int, Y: dict, pY: int) -> dict:
    """
    Compute [X,Y} = XY - (-1)^{pX*pY} YX.
    X and Y are dicts: monomial -> Fraction.
    """
    result = {}

    def add(d, k, v):
        d[k] = d.get(k, Fraction(0)) + v

    sign = (-1) ** (pX * pY)

    for mX, cX in X.items():
        for mY, cY in Y.items():
            # XY term
            xy_prod = normal_order_product(list(mX) + list(mY))
            for mono, c in xy_prod.items():
                add(result, mono, cX * cY * c)
            # -(-1)^{pX*pY} YX term
            yx_prod = normal_order_product(list(mY) + list(mX))
            for mono, c in yx_prod.items():
                add(result, mono, -sign * cX * cY * c)

    return {k: v for k, v in result.items() if v != 0}


# ---------------------------------------------------------------------------
# Generator definitions as oscillator monomials
# ---------------------------------------------------------------------------

def generator_monomials(n: int) -> dict[str, tuple[dict, int]]:
    """
    Return dict: generator_label -> (monomial_dict, parity).
    monomial_dict: {oscillator_tuple: coefficient}.
    """
    gens = {}

    def mono(oscs, coeff=1):
        return {tuple(oscs): Fraction(coeff)}

    def add_mono(d1, d2):
        r = dict(d1)
        for k, v in d2.items():
            r[k] = r.get(k, Fraction(0)) + v
        return {k: v for k, v in r.items() if v != 0}

    # Cartan H_1 = a_1^+ a_1^- + b_1^+ b_1^-
    gens["H_1"] = (add_mono(mono(["a_1_p", "a_1_m"]), mono([f"b_1_p", f"b_1_m"])), 0)
    # H_k = b_{k-1}^+ b_{k-1}^- - b_k^+ b_k^-
    for k in range(2, n + 1):
        gens[f"H_{k}"] = (add_mono(mono([f"b_{k-1}_p", f"b_{k-1}_m"]),
                                   mono([f"b_{k}_p", f"b_{k}_m"], -1)), 0)
    # H_{n+1} = -b_n^+ b_n^- - 1/2
    gens[f"H_{n+1}"] = (add_mono(mono([f"b_{n}_p", f"b_{n}_m"], -1),
                                  mono([], Fraction(-1, 2))), 0)

    # Bosonic root generators
    for k in range(1, n + 1):
        gens[f"E_2del{k}_p"] = (mono([f"b_{k}_p", f"b_{k}_p"]), 0)
        gens[f"E_2del{k}_m"] = (mono([f"b_{k}_m", f"b_{k}_m"]), 0)
    for i, j in combinations(range(1, n + 1), 2):
        gens[f"E_del{i}_del{j}_pp"] = (mono([f"b_{i}_p", f"b_{j}_p"]), 0)
        gens[f"E_del{i}_del{j}_mm"] = (mono([f"b_{i}_m", f"b_{j}_m"]), 0)
        gens[f"E_del{i}_del{j}_pm"] = (mono([f"b_{i}_p", f"b_{j}_m"]), 0)
        gens[f"E_del{i}_del{j}_mp"] = (mono([f"b_{i}_m", f"b_{j}_p"]), 0)

    # Fermionic root generators
    for k in range(1, n + 1):
        gens[f"E_eps1_del{k}_pp"] = (mono(["a_1_p", f"b_{k}_p"]), 1)
        gens[f"E_eps1_del{k}_pm"] = (mono(["a_1_p", f"b_{k}_m"]), 1)
        gens[f"E_eps1_del{k}_mp"] = (mono(["a_1_m", f"b_{k}_p"]), 1)
        gens[f"E_eps1_del{k}_mm"] = (mono(["a_1_m", f"b_{k}_m"]), 1)

    return gens


def express_in_basis(mono_dict: dict, gen_monomials: dict) -> dict[str, Fraction]:
    """
    Given an oscillator polynomial, express it in terms of generators.
    Returns dict: generator_label -> coefficient.
    """
    # Build inverse map: canonical_monomial -> (generator, coefficient)
    # For each generator, its canonical monomial is the PBW-ordered tuple.
    inv = {}
    for label, (md, _) in gen_monomials.items():
        # Each generator should have exactly one canonical monomial (or a sum for Cartans)
        for mono, coeff in md.items():
            if mono not in inv:
                inv[mono] = []
            inv[mono].append((label, coeff))

    result = {}
    remaining = dict(mono_dict)

    # Handle constant term (scalar) - maps to nothing in the basis (K=1 not in basis)
    if SCALAR in remaining:
        # This is a scalar; in our context constants come from H_{n+1}'s -1/2 term.
        # We just ignore them since K=1 is excluded from basis.
        del remaining[SCALAR]

    # Match monomials to generators
    # Strategy: for each monomial in result, find matching generator(s)
    # This works cleanly since each generator has a unique set of monomials
    # Note: Cartans H_k have 2 monomials (for k=1,...,n) and 1 monomial (for H_{n+1} from constant)
    # We need to match linear combinations.

    # Simple generators have single monomials:
    single_mono_gens = {}
    multi_mono_gens = {}
    for label, (md, _) in gen_monomials.items():
        if len(md) == 1:
            single_mono_gens[label] = md
        else:
            multi_mono_gens[label] = md

    # First, resolve single-monomial generators
    for label, md in single_mono_gens.items():
        mono = next(iter(md))
        coeff_in_gen = next(iter(md.values()))
        if mono in remaining:
            contribution = remaining[mono] / coeff_in_gen
            result[label] = result.get(label, Fraction(0)) + contribution
            del remaining[mono]

    # Then, resolve multi-monomial generators (Cartans H_1,...,H_n)
    # H_k = b_{k-1}^+b_{k-1}^- - b_k^+b_k^- for k=2,...,n
    # H_1 = a_1^+a_1^- + b_1^+b_1^-
    # H_{n+1} = -b_n^+b_n^- - 1/2
    # The monomials (a_1_p,a_1_m), (b_k_p,b_k_m) appear in multiple Cartans.
    # We solve: remaining = sum_k alpha_k * H_k + ...
    # Key monomials: (a_1_p,a_1_m) only in H_1, (b_k_p,b_k_m) in H_k and H_{k+1} (adjacent)
    # H_{n+1} has (b_n_p,b_n_m) with coeff -1.

    # We need to untangle these. Order the Cartans by which monomial uniquely identifies them.
    n_val = max((int(label[2:]) for label in gen_monomials if label.startswith("H_")), default=0) - 1
    # Untangle starting from H_{n+1}: it has unique monomial (b_n_p, b_n_m)
    # Actually H_{n+1} has both (b_n_p,b_n_m) and () (constant), but we removed ()
    # H_k for k=2,...,n: H_k = (b_{k-1}_p,b_{k-1}_m) - (b_k_p,b_k_m)
    # H_1: H_1 = (a_1_p,a_1_m) + (b_1_p,b_1_m)
    # These all share monomials. We solve via back-substitution.

    # Collect Cartan monomials still in remaining
    cartan_monomials = {}
    for label, md in multi_mono_gens.items():
        for mono, c in md.items():
            if mono != SCALAR and mono in remaining:
                cartan_monomials[mono] = remaining[mono]

    if cartan_monomials:
        # Solve for Cartan coefficients in FORWARD order H_1, H_2, ..., H_{n+1}.
        # H_1 is uniquely identified by (a_1_p,a_1_m) which appears only in H_1.
        # After subtracting H_1's contribution, (b_1_p,b_1_m) is unique to H_2.
        # After subtracting H_2's contribution, (b_2_p,b_2_m) is unique to H_3. Etc.
        n_val_actual = max((int(label[2:]) for label in gen_monomials if label.startswith("H_")), default=1) - 1

        remaining_copy = dict(remaining)
        for k_h in range(1, n_val_actual + 2):
            label = f"H_{k_h}"
            if label not in multi_mono_gens:
                continue
            md = multi_mono_gens[label]
            if k_h == 1:
                # H_1's unique identifier: (a_1_p,a_1_m) (not in any other Cartan)
                unique_mono = ("a_1_p", "a_1_m")
                unique_coeff = Fraction(1)
            elif k_h <= n_val_actual:
                # H_k = N_{k-1} - N_k: after H_{k-1} is subtracted,
                # (b_{k-1}_p,b_{k-1}_m) is uniquely due to H_k (coeff +1)
                unique_mono = (f"b_{k_h-1}_p", f"b_{k_h-1}_m")
                unique_coeff = Fraction(1)
            else:
                # H_{n+1} = -N_n - 1/2: after H_n subtracted,
                # (b_n_p,b_n_m) is uniquely due to H_{n+1} (coeff -1)
                unique_mono = (f"b_{n_val_actual}_p", f"b_{n_val_actual}_m")
                unique_coeff = Fraction(-1)

            if unique_mono in remaining_copy:
                alpha = remaining_copy[unique_mono] / unique_coeff
                if alpha != 0:
                    result[label] = result.get(label, Fraction(0)) + alpha
                    # Subtract this generator's contribution from remaining_copy
                    for mono, c in md.items():
                        remaining_copy[mono] = remaining_copy.get(mono, Fraction(0)) - alpha * c
                        if remaining_copy[mono] == 0:
                                del remaining_copy[mono]

        remaining = {k: v for k, v in remaining_copy.items() if v != 0 and k != SCALAR}

    if remaining:
        # Some monomials couldn't be matched — this indicates a bug or missing generator
        raise ValueError(f"Could not express in basis. Remaining: {remaining}")

    return {k: v for k, v in result.items() if v != 0}


def compute_structure_constants(n: int) -> list[dict]:
    """Compute all non-zero structure constants via oscillator algebra."""
    even_basis, odd_basis = get_basis(n)
    all_basis = even_basis + odd_basis
    parity_map = get_parity(even_basis, odd_basis)
    gen_mono = generator_monomials(n)

    sc_dict = {}  # (X, Y) -> {Z: coeff}

    def add_forward(X, Y, Z, c):
        c = Fraction(c)
        if c == 0:
            return
        key = (X, Y)
        if key not in sc_dict:
            sc_dict[key] = {}
        sc_dict[key][Z] = sc_dict[key].get(Z, Fraction(0)) + c

    # Compute [X,Y] for all pairs (X,Y) with X <= Y in basis ordering
    gen_order = {g: i for i, g in enumerate(all_basis)}

    for X in all_basis:
        for Y in all_basis:
            if gen_order[X] > gen_order[Y]:
                continue
            pX = parity_map[X]
            pY = parity_map[Y]
            mdX, _ = gen_mono[X]
            mdY, _ = gen_mono[Y]

            bracket_result = supercommutator(mdX, pX, mdY, pY)

            if not bracket_result:
                continue

            # Express result in basis
            try:
                expressed = express_in_basis(bracket_result, gen_mono)
            except ValueError as e:
                print(f"WARNING: [{X},{Y}] -> {e}")
                continue

            for Z, c in expressed.items():
                if c != 0:
                    add_forward(X, Y, Z, c)

    # Generate reverse brackets
    reverse_additions = []
    for (X, Y), zc in sc_dict.items():
        if X == Y:
            continue
        sign = -(-1) ** (parity_map[X] * parity_map[Y])
        for Z, c in zc.items():
            reverse_additions.append((Y, X, Z, sign * c))

    for Y, X, Z, c in reverse_additions:
        if c != 0:
            add_forward(Y, X, Z, c)

    # Clean zeros
    for key in list(sc_dict.keys()):
        sc_dict[key] = {z: c for z, c in sc_dict[key].items() if c != 0}
        if not sc_dict[key]:
            del sc_dict[key]

    sc_list = []
    for (X, Y), zc in sc_dict.items():
        for Z, c in zc.items():
            sc_list.append({"X": X, "Y": Y, "Z": Z, "coeff": str(c), "sign_rule": "graded"})

    return sc_list


def get_basis(n: int) -> tuple[list[str], list[str]]:
    even = []
    for k in range(1, n + 2):
        even.append(f"H_{k}")
    for k in range(1, n + 1):
        even.append(f"E_2del{k}_p")
    for i, j in combinations(range(1, n + 1), 2):
        even.append(f"E_del{i}_del{j}_pp")
    for k in range(1, n + 1):
        even.append(f"E_2del{k}_m")
    for i, j in combinations(range(1, n + 1), 2):
        even.append(f"E_del{i}_del{j}_mm")
    for i, j in combinations(range(1, n + 1), 2):
        even.append(f"E_del{i}_del{j}_pm")
    for i, j in combinations(range(1, n + 1), 2):
        even.append(f"E_del{i}_del{j}_mp")

    odd = []
    for k in range(1, n + 1):
        odd.append(f"E_eps1_del{k}_pp")
    for k in range(1, n + 1):
        odd.append(f"E_eps1_del{k}_pm")
    for k in range(1, n + 1):
        odd.append(f"E_eps1_del{k}_mp")
    for k in range(1, n + 1):
        odd.append(f"E_eps1_del{k}_mm")

    return even, odd


def get_parity(basis_even: list[str], basis_odd: list[str]) -> dict[str, int]:
    parity = {}
    for g in basis_even:
        parity[g] = 0
    for g in basis_odd:
        parity[g] = 1
    return parity


def generator_realization(n: int) -> dict:
    real = {}
    real["H_1"] = {"standard_form": [{"words": ["a_1_p", "a_1_m"], "coeff": "1"}, {"words": ["b_1_p", "b_1_m"], "coeff": "1"}], "frappat_form": "a_1^+ a_1^- + b_1^+ b_1^-", "parity": 0}
    for k in range(2, n + 1):
        real[f"H_{k}"] = {"standard_form": [{"words": [f"b_{k-1}_p", f"b_{k-1}_m"], "coeff": "1"}, {"words": [f"b_{k}_p", f"b_{k}_m"], "coeff": "-1"}], "frappat_form": f"b_{k-1}^+ b_{k-1}^- - b_{k}^+ b_{k}^-", "parity": 0}
    real[f"H_{n+1}"] = {"standard_form": [{"words": [f"b_{n}_p", f"b_{n}_m"], "coeff": "-1"}, {"words": [], "coeff": "-1/2"}], "frappat_form": f"-b_{n}^+ b_{n}^- - 1/2", "parity": 0, "note": "Terminal Cartan; constant -1/2"}
    for k in range(1, n + 1):
        real[f"E_2del{k}_p"] = {"standard_form": [{"words": [f"b_{k}_p", f"b_{k}_p"], "coeff": "1"}], "frappat_form": f"(b_{k}^+)^2", "parity": 0}
        real[f"E_2del{k}_m"] = {"standard_form": [{"words": [f"b_{k}_m", f"b_{k}_m"], "coeff": "1"}], "frappat_form": f"(b_{k}^-)^2", "parity": 0}
        real[f"E_eps1_del{k}_pp"] = {"standard_form": [{"words": ["a_1_p", f"b_{k}_p"], "coeff": "1"}], "frappat_form": f"a_1^+ b_{k}^+", "parity": 1}
        real[f"E_eps1_del{k}_pm"] = {"standard_form": [{"words": ["a_1_p", f"b_{k}_m"], "coeff": "1"}], "frappat_form": f"a_1^+ b_{k}^-", "parity": 1}
        real[f"E_eps1_del{k}_mp"] = {"standard_form": [{"words": ["a_1_m", f"b_{k}_p"], "coeff": "1"}], "frappat_form": f"a_1^- b_{k}^+", "parity": 1}
        real[f"E_eps1_del{k}_mm"] = {"standard_form": [{"words": ["a_1_m", f"b_{k}_m"], "coeff": "1"}], "frappat_form": f"a_1^- b_{k}^-", "parity": 1}
    for i, j in combinations(range(1, n + 1), 2):
        real[f"E_del{i}_del{j}_pp"] = {"standard_form": [{"words": [f"b_{i}_p", f"b_{j}_p"], "coeff": "1"}], "frappat_form": f"b_{i}^+ b_{j}^+", "parity": 0}
        real[f"E_del{i}_del{j}_mm"] = {"standard_form": [{"words": [f"b_{i}_m", f"b_{j}_m"], "coeff": "1"}], "frappat_form": f"b_{i}^- b_{j}^-", "parity": 0}
        real[f"E_del{i}_del{j}_pm"] = {"standard_form": [{"words": [f"b_{i}_p", f"b_{j}_m"], "coeff": "1"}], "frappat_form": f"b_{i}^+ b_{j}^-", "parity": 0}
        real[f"E_del{i}_del{j}_mp"] = {"standard_form": [{"words": [f"b_{i}_m", f"b_{j}_p"], "coeff": "1"}], "frappat_form": f"b_{i}^- b_{j}^+", "parity": 0}
    return real


def build_schema1(n: int) -> dict:
    even_basis, odd_basis = get_basis(n)
    parity = get_parity(even_basis, odd_basis)
    sc = compute_structure_constants(n)
    realization = generator_realization(n)

    even_dim = 2 * n * n + n + 1
    odd_dim = 4 * n

    boson_labels = []
    for k in range(1, n + 1):
        boson_labels += [f"b_{k}_p", f"b_{k}_m"]

    return {
        "schema_version": "5.0",
        "algebra": {"family": "C", "m": 1, "n": n, "cartan_type": f"C({n+1})", "alternative_notation": {"osp": f"osp(2|{2*n})", "dimension_formula": "osp(2m|2n) with m=1"}, "dimension": {"total": even_dim + odd_dim, "even": even_dim, "odd": odd_dim}},
        "central_elements": {"kappa": {"label": "kappa", "parity": 1, "description": "Odd nilpotent central element; kappa^2 = 0."}, "K": {"label": "K", "parity": 0, "description": "Even central element, identified with scalar 1."}},
        "oscillator_generators": {"fermions": {"m": 1, "labels": ["a_1_p", "a_1_m"], "parity": 1, "description": "Standard fermionic pair a_1^+, a_1^- with CAR."}, "bosons": {"count": 2 * n, "n": n, "labels": boson_labels, "description": f"Bosonic oscillators b_k^pm with k=1,...,{n}"}},
        "oscillator_relations": {"standard_fermion_anticommutators": {"description": "CAR", "relations": {"same_type": "{a_1^pm, a_1^pm} = 0", "conjugate_pair": "{a_1^-, a_1^+} = 1"}}, "bosonic_commutators": {"description": "CCR", "relations": {"same_type": "[b_i^pm, b_j^pm] = 0", "conjugate_pair": "[b_i^-, b_j^+] = delta_{ij}"}}, "mixed_commutators": {"fermion_boson": "[b^pm, a_1^pm] = 0"}},
        "basis": {"even": even_basis, "odd": odd_basis, "ordering_convention": "PBW: kappa < [odd] < [even]  (K=1 excluded)"},
        "parity": parity,
        "generator_realization": {"description": "PBW form: a_1_p, a_1_m, b_1_p, b_1_m, ...", "ordering": ["a_1_p", "a_1_m"] + boson_labels, "realizations": realization},
        "structure_constants": sc,
        "metadata": {"generated_by": "src/C_generators.py", "generation_date": str(date.today()), "references": ["Frappat, Sciarrino, Sorba (2000)", "Bakalov and Sullivan (2017)"]},
    }


def main():
    os.makedirs("data", exist_ok=True)
    for n in [1, 2, 3]:
        print(f"Building n={n}...", flush=True)
        schema = build_schema1(n)
        fname = f"data/C_{n}_structure.json"
        with open(fname, "w") as f:
            json.dump(schema, f, indent=2)
        sc_count = len(schema["structure_constants"])
        print(f"  C_{n}_structure.json: dim={schema['algebra']['dimension']}, sc={sc_count}")


if __name__ == "__main__":
    main()
