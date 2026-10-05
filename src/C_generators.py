"""
C(n+1) = osp(2|2n) structure constant generator.
Produces Schema 1 JSON files for n=1, 2, 3.
"""

import json
import os
import sys
from fractions import Fraction
from datetime import date
from itertools import product


def build_basis(n):
    even = []
    odd = []

    for k in range(1, n + 2):
        even.append(f"H_{k}")

    for k in range(1, n + 1):
        even.append(f"E_2del{k}_p")
    for i in range(1, n + 1):
        for j in range(i + 1, n + 1):
            even.append(f"E_del{i}_del{j}_pp")

    for k in range(1, n + 1):
        even.append(f"E_2del{k}_m")
    for i in range(1, n + 1):
        for j in range(i + 1, n + 1):
            even.append(f"E_del{i}_del{j}_mm")

    for i in range(1, n + 1):
        for j in range(i + 1, n + 1):
            even.append(f"E_del{i}_del{j}_pm")
    for i in range(1, n + 1):
        for j in range(i + 1, n + 1):
            even.append(f"E_del{i}_del{j}_mp")

    for k in range(1, n + 1):
        odd.append(f"E_eps_del{k}_pp")
    for k in range(1, n + 1):
        odd.append(f"E_eps_del{k}_pm")
    for k in range(1, n + 1):
        odd.append(f"E_eps_del{k}_mp")
    for k in range(1, n + 1):
        odd.append(f"E_eps_del{k}_mm")

    return even, odd


def get_parity(label):
    if label.startswith("H_") or label.startswith("E_2del") or label.startswith("E_del"):
        return 0
    if label.startswith("E_eps_"):
        return 1
    raise ValueError(f"Unknown label: {label}")


def parse_generator(label):
    """Parse a generator label into its root type and indices."""
    if label.startswith("H_"):
        k = int(label[2:])
        return ("H", k)
    if label.startswith("E_2del"):
        rest = label[6:]
        parts = rest.split("_")
        k = int(parts[0])
        sign = parts[1]
        return ("2delta", k, sign)
    if label.startswith("E_del") and not label.startswith("E_eps"):
        rest = label[2:]
        parts = rest.split("_")
        i = int(parts[0][3:])
        j = int(parts[1][3:])
        sign = parts[2]
        return ("delta_delta", i, j, sign)
    if label.startswith("E_eps_del"):
        rest = label[6:]
        parts = rest.split("_")
        k = int(parts[0][3:])
        sign = parts[1]
        return ("eps_delta", k, sign)
    raise ValueError(f"Cannot parse: {label}")


def oscillator_form(label, n):
    """Return the oscillator realization as a list of (coeff, word_tuple).
    word_tuple elements: 'a1p', 'a1m', 'b{k}p', 'b{k}m'
    """
    parsed = parse_generator(label)
    kind = parsed[0]

    if kind == "H":
        k = parsed[1]
        if k == 1:
            return [(Fraction(1), ("a1p", "a1m")), (Fraction(1), ("b1p", "b1m"))]
        elif 2 <= k <= n:
            km1 = k - 1
            return [(Fraction(1), (f"b{km1}p", f"b{km1}m")),
                    (Fraction(-1), (f"b{k}p", f"b{k}m"))]
        elif k == n + 1:
            return [(Fraction(-1), (f"b{n}p", f"b{n}m")),
                    (Fraction(-1, 2), ())]
        else:
            raise ValueError(f"Invalid Cartan index: {k}")

    elif kind == "2delta":
        k, sign = parsed[1], parsed[2]
        if sign == "p":
            return [(Fraction(1, 2), (f"b{k}p", f"b{k}p"))]
        else:
            return [(Fraction(1, 2), (f"b{k}m", f"b{k}m"))]

    elif kind == "delta_delta":
        i, j, sign = parsed[1], parsed[2], parsed[3]
        si = "p" if sign[0] == "p" else "m"
        sj = "p" if sign[1] == "p" else "m"
        return [(Fraction(1), (f"b{i}{si}", f"b{j}{sj}"))]

    elif kind == "eps_delta":
        k, sign = parsed[1], parsed[2]
        sa = "p" if sign[0] == "p" else "m"
        sb = "p" if sign[1] == "p" else "m"
        return [(Fraction(1), (f"a1{sa}", f"b{k}{sb}"))]

    raise ValueError(f"Unknown kind: {kind}")


def osc_type(osc):
    """Return 'f' for fermionic, 'b' for bosonic."""
    if osc.startswith("a"):
        return "f"
    return "b"


def osc_parity(osc):
    return 1 if osc_type(osc) == "f" else 0


def compute_bracket_oscillator(form_X, form_Y, n):
    """Compute [X, Y] using oscillator algebra.
    Returns a dict mapping basis labels to Fraction coefficients.
    """
    px = sum(osc_parity(o) for _, word in form_X for o in word) % 2
    py = sum(osc_parity(o) for _, word in form_Y for o in word) % 2

    result_words = {}

    for cx, wx in form_X:
        for cy, wy in form_Y:
            products = multiply_words(wx, wy, n)
            for coeff, word in products:
                total = cx * cy * coeff
                if total != 0:
                    result_words[word] = result_words.get(word, Fraction(0)) + total

            sign = (-1) ** (px * py)
            products_rev = multiply_words(wy, wx, n)
            for coeff, word in products_rev:
                total = -sign * cx * cy * coeff
                if total != 0:
                    result_words[word] = result_words.get(word, Fraction(0)) + total

    result_words = {k: v for k, v in result_words.items() if v != 0}
    return result_words


def multiply_words(w1, w2, n):
    """Multiply two oscillator words and normal-order using CCR/CAR.
    Returns list of (coeff, normal_ordered_word_tuple).
    """
    word = list(w1) + list(w2)
    results = [(Fraction(1), word)]
    final = []

    for coeff, w in results:
        ordered = normal_order(w, n)
        for c2, w2 in ordered:
            final.append((coeff * c2, tuple(w2)))

    combined = {}
    for c, w in final:
        combined[w] = combined.get(w, Fraction(0)) + c
    return [(c, w) for w, c in combined.items() if c != 0]


def normal_order(word, n):
    """Normal order a word of oscillator symbols.
    Order: a1p, a1m, b1p, b1m, b2p, b2m, ...
    Uses bubble sort with commutation/anticommutation relations.
    Returns list of (coeff, word_list).
    """
    def osc_order(osc):
        if osc == "a1p":
            return 0
        if osc == "a1m":
            return 1
        if osc.startswith("b"):
            rest = osc[1:]
            k_str = ""
            i = 0
            while i < len(rest) and rest[i].isdigit():
                k_str += rest[i]
                i += 1
            k = int(k_str)
            s = rest[i:]
            return 2 + 2 * (k - 1) + (0 if s == "p" else 1)
        raise ValueError(f"Unknown oscillator: {osc}")

    def has_duplicate_fermion(w):
        fermions_seen = set()
        for osc in w:
            if osc_parity(osc) == 1:
                if osc in fermions_seen:
                    return True
                fermions_seen.add(osc)
        return False

    results = [(Fraction(1), list(word))]
    changed = True
    max_iter = 100
    iteration = 0

    while changed and iteration < max_iter:
        changed = False
        iteration += 1
        new_results = []
        for coeff, w in results:
            if has_duplicate_fermion(w):
                continue
            swapped = False
            for i in range(len(w) - 1):
                if osc_order(w[i]) > osc_order(w[i + 1]):
                    a, b = w[i], w[i + 1]
                    pa = osc_parity(a)
                    pb = osc_parity(b)

                    swapped_word = w[:i] + [b, a] + w[i + 2:]
                    sign = (-1) ** (pa * pb)
                    new_results.append((coeff * sign, swapped_word))

                    commutator_val = get_commutator(a, b)
                    if commutator_val != 0:
                        contracted_word = w[:i] + w[i + 2:]
                        new_results.append((coeff * commutator_val, contracted_word))

                    swapped = True
                    changed = True
                    break
            if not swapped:
                new_results.append((coeff, w))

        combined = {}
        for c, w in new_results:
            key = tuple(w)
            combined[key] = combined.get(key, Fraction(0)) + c
        results = [(c, list(w)) for w, c in combined.items() if c != 0]

    return results


def get_commutator(a, b):
    """Return [a, b] or {a, b} contraction value.
    For fermions: {a1m, a1p} = 1 (anticommutator).
    For bosons: [b_k_m, b_k_p] = 1 (commutator).
    """
    if a == "a1m" and b == "a1p":
        return Fraction(1)
    if a == "a1p" and b == "a1m":
        return Fraction(1)

    if a.startswith("b") and b.startswith("b"):
        ka = extract_boson_index(a)
        kb = extract_boson_index(b)
        sa = extract_boson_sign(a)
        sb = extract_boson_sign(b)
        if ka == kb and sa == "m" and sb == "p":
            return Fraction(1)
        if ka == kb and sa == "p" and sb == "m":
            return Fraction(-1)
    return Fraction(0)


def extract_boson_index(osc):
    rest = osc[1:]
    k_str = ""
    for ch in rest:
        if ch.isdigit():
            k_str += ch
        else:
            break
    return int(k_str)


def extract_boson_sign(osc):
    if osc.endswith("p"):
        return "p"
    return "m"


def word_to_basis_label(word, n):
    """Convert a normal-ordered oscillator word to a basis generator label."""
    if len(word) == 0:
        return "scalar"
    if len(word) == 2:
        a, b = word
        if a == "a1p" and b == "a1m":
            return "N_f"
        if a.startswith("a1") and b.startswith("b"):
            sa = "p" if a == "a1p" else "m"
            k = extract_boson_index(b)
            sb = extract_boson_sign(b)
            return f"E_eps_del{k}_{sa}{sb}"
        if a.startswith("b") and b.startswith("b"):
            ka = extract_boson_index(a)
            kb = extract_boson_index(b)
            sa = extract_boson_sign(a)
            sb = extract_boson_sign(b)
            if ka == kb and sa == sb:
                sign = "p" if sa == "p" else "m"
                return f"E_2del{ka}_{sign}_half"
            if ka == kb and sa == "p" and sb == "m":
                return f"N_b{ka}"
            if ka < kb:
                return f"E_del{ka}_del{kb}_{sa}{sb}"
            else:
                return f"E_del{kb}_del{ka}_{sb}{sa}"
    return f"word_{'_'.join(word)}"


def compute_structure_constants(n):
    """Compute all non-zero structure constants [X, Y] for C(n+1)."""
    even_basis, odd_basis = build_basis(n)
    all_basis = odd_basis + even_basis
    parity_map = {g: get_parity(g) for g in all_basis}

    osc_forms = {}
    for g in all_basis:
        osc_forms[g] = oscillator_form(g, n)

    basis_osc_map = build_basis_osc_map(n, all_basis, osc_forms)

    structure_constants = []

    for i, X in enumerate(all_basis):
        for j, Y in enumerate(all_basis):
            if j <= i:
                continue

            bracket = compute_bracket(X, Y, n, osc_forms, basis_osc_map, parity_map)

            for Z, coeff in sorted(bracket.items()):
                if coeff != 0:
                    structure_constants.append({
                        "X": X,
                        "Y": Y,
                        "Z": Z,
                        "coeff": str(coeff),
                        "sign_rule": "graded"
                    })

    return structure_constants, even_basis, odd_basis, parity_map


def build_basis_osc_map(n, all_basis, osc_forms):
    """Build a mapping from normal-ordered oscillator words to basis elements."""
    mapping = {}

    for g in all_basis:
        form = osc_forms[g]
        if len(form) == 1 and form[0][0] == Fraction(1):
            word = form[0][1]
            mapping[word] = g

    for k in range(1, n + 1):
        mapping[(f"b{k}p", f"b{k}p")] = (f"E_2del{k}_p", Fraction(2))
        mapping[(f"b{k}m", f"b{k}m")] = (f"E_2del{k}_m", Fraction(2))

    return mapping


def compute_bracket(X, Y, n, osc_forms, basis_osc_map, parity_map):
    """Compute the graded bracket [X, Y} and express in the basis."""
    fx = osc_forms[X]
    fy = osc_forms[Y]
    px = parity_map[X]
    py = parity_map[Y]

    raw_result = {}

    for cx, wx in fx:
        for cy, wy in fy:
            product_xy = normal_order(list(wx) + list(wy), n)
            for c, w in product_xy:
                key = tuple(w)
                raw_result[key] = raw_result.get(key, Fraction(0)) + cx * cy * c

            sign = (-1) ** (px * py)
            product_yx = normal_order(list(wy) + list(wx), n)
            for c, w in product_yx:
                key = tuple(w)
                raw_result[key] = raw_result.get(key, Fraction(0)) - sign * cx * cy * c

    raw_result = {k: v for k, v in raw_result.items() if v != 0}

    return express_in_basis(raw_result, n, parity_map)


def express_in_basis(raw_result, n, parity_map):
    """Convert oscillator expression to basis generator coefficients."""
    even_basis, odd_basis = build_basis(n)
    all_basis = odd_basis + even_basis

    osc_to_gen = {}

    for g in all_basis:
        form = oscillator_form(g, n)
        if len(form) == 1:
            c, w = form[0]
            osc_to_gen[w] = (g, Fraction(1) / c)

    result = {}

    for word, coeff in raw_result.items():
        if len(word) == 0:
            continue
        if word in osc_to_gen:
            gen, scale = osc_to_gen[word]
            result[gen] = result.get(gen, Fraction(0)) + coeff * scale
        elif len(word) == 2:
            a, b = word
            if a.startswith("b") and b.startswith("b"):
                ka = extract_boson_index(a)
                sa = extract_boson_sign(a)
                kb = extract_boson_index(b)
                sb = extract_boson_sign(b)
                if ka == kb and sa == "p" and sb == "m":
                    found_cartan = False
                    for g in all_basis:
                        if g.startswith("H_"):
                            form = oscillator_form(g, n)
                            for fc, fw in form:
                                if fw == word:
                                    result[g] = result.get(g, Fraction(0)) + coeff / fc
                                    found_cartan = True
                            if found_cartan:
                                break
                    if not found_cartan:
                        result[f"raw_{a}_{b}"] = coeff
                else:
                    matched = False
                    for g in all_basis:
                        form = oscillator_form(g, n)
                        if len(form) == 1:
                            fc, fw = form[0]
                            if fw == word:
                                result[g] = result.get(g, Fraction(0)) + coeff / fc
                                matched = True
                                break
                    if not matched:
                        result[f"raw_{a}_{b}"] = coeff
            elif a.startswith("a") and b.startswith("b"):
                matched = False
                for g in all_basis:
                    form = oscillator_form(g, n)
                    if len(form) == 1:
                        fc, fw = form[0]
                        if fw == word:
                            result[g] = result.get(g, Fraction(0)) + coeff / fc
                            matched = True
                            break
                if not matched:
                    result[f"raw_{a}_{b}"] = coeff
            elif a == "a1p" and b == "a1m":
                for g in all_basis:
                    if g.startswith("H_"):
                        form = oscillator_form(g, n)
                        for fc, fw in form:
                            if fw == ("a1p", "a1m"):
                                result[g] = result.get(g, Fraction(0)) + coeff / fc
                                break
                        break
            else:
                result[f"raw_{'_'.join(word)}"] = coeff
        else:
            result[f"raw_{'_'.join(word)}"] = coeff

    result = {k: v for k, v in result.items() if v != 0}
    return result


def generate_realization_json(n):
    """Generate the generator_realization section."""
    even_basis, odd_basis = build_basis(n)
    all_basis = odd_basis + even_basis
    realizations = {}

    for g in all_basis:
        form = oscillator_form(g, n)
        std_form = []
        for c, w in form:
            words_json = []
            for osc in w:
                if osc.startswith("a1"):
                    words_json.append(f"a_1_{osc[2:]}")
                elif osc.startswith("b"):
                    k = extract_boson_index(osc)
                    s = extract_boson_sign(osc)
                    words_json.append(f"b_{k}_{s}")
                else:
                    words_json.append(osc)
            std_form.append({"words": words_json, "coeff": str(c)})
        realizations[g] = {
            "standard_form": std_form,
            "parity": get_parity(g)
        }

    return realizations


def generate_schema1_json(n):
    """Generate complete Schema 1 JSON for C(n+1)."""
    structure_constants, even_basis, odd_basis, parity_map = compute_structure_constants(n)

    dim_even = 2 * n * n + n + 1
    dim_odd = 4 * n
    dim_total = dim_even + dim_odd

    assert len(even_basis) == dim_even, f"Even basis count mismatch: {len(even_basis)} != {dim_even}"
    assert len(odd_basis) == dim_odd, f"Odd basis count mismatch: {len(odd_basis)} != {dim_odd}"

    boson_labels = []
    for k in range(1, n + 1):
        boson_labels.extend([f"b_{k}_p", f"b_{k}_m"])

    schema = {
        "schema_version": "5.0",
        "algebra": {
            "family": "C",
            "m": 1,
            "n": n,
            "cartan_type": f"C({n + 1})",
            "alternative_notation": {
                "osp": f"osp(2|{2 * n})",
                "dimension_formula": "osp(2m|2n) with m=1"
            },
            "dimension": {
                "total": dim_total,
                "even": dim_even,
                "odd": dim_odd
            }
        },
        "oscillator_generators": {
            "fermions": {
                "m": 1,
                "count": 2,
                "labels": ["a_1_p", "a_1_m"],
                "parity": 1,
                "description": "Standard fermionic pair a_1^+, a_1^- with CAR: {a_1^-, a_1^+} = 1"
            },
            "bosons": {
                "n": n,
                "count": 2 * n,
                "labels": boson_labels,
                "parity": 0,
                "description": f"Bosonic oscillators b_i^± with i=1,...,{n}"
            }
        },
        "oscillator_relations": {
            "standard_fermion_anticommutators": {
                "description": "Canonical anticommutation relations for fermionic oscillators",
                "relations": {
                    "canonical_pair": "{a_1^-, a_1^+} = 1",
                    "self_anticommutators": "{a_1^+, a_1^+} = 0, {a_1^-, a_1^-} = 0"
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
        "central_elements": {
            "kappa": {
                "parity": 1,
                "nilpotency": "kappa^2 = 0",
                "description": "Odd central element for inhomogeneous deformation"
            },
            "K": {
                "parity": 0,
                "value": 1,
                "description": "Even central identity element (= scalar 1, excluded from basis)"
            }
        },
        "basis": {
            "even": even_basis,
            "odd": odd_basis,
            "ordering_convention": "PBW: κ < [odd] < [even]  (K = 1 excluded)"
        },
        "parity": parity_map,
        "generator_realization": {
            "description": "Standard form with PBW ordering",
            "ordering": "a_1_p, a_1_m, " + ", ".join(boson_labels),
            "realizations": generate_realization_json(n)
        },
        "structure_constants": structure_constants,
        "metadata": {
            "generated_by": "C_generators.py",
            "generation_date": str(date.today()),
            "references": [
                "Frappat et al. (2000), Dictionary on Lie Algebras and Superalgebras",
                "Bakalov and Sullivan (2017)"
            ]
        }
    }

    return schema


def main():
    data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
    os.makedirs(data_dir, exist_ok=True)

    for n in [1, 2, 3]:
        print(f"Generating C({n + 1}) = osp(2|{2 * n}) structure constants (n={n})...")
        schema = generate_schema1_json(n)
        filename = os.path.join(data_dir, f"C_{n}_structure.json")
        with open(filename, "w") as f:
            json.dump(schema, f, indent=2)
        sc_count = len(schema["structure_constants"])
        print(f"  Written {filename}: {sc_count} non-zero structure constants")
        print(f"  Dimension: {schema['algebra']['dimension']}")

    print("Done.")


if __name__ == "__main__":
    main()
