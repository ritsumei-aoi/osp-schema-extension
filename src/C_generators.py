"""
C(n+1) = osp(2|2n) structure constant generator.

Computes the full Lie superalgebra structure using the oscillator realization:
  - Standard fermionic pair a_1^± with {a_1^-, a_1^+} = 1
  - Bosonic oscillators b_k^± with [b_k^-, b_l^+] = δ_{kl}

Outputs Schema 1 JSON files for n=1,2,3.
"""

import json
import os
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
        odd.append(f"E_eps1_del{k}_pp")
    for k in range(n, 0, -1):
        odd.append(f"E_eps1_del{k}_pm")
    for k in range(1, n + 1):
        odd.append(f"E_eps1_del{k}_mp")
    for k in range(n, 0, -1):
        odd.append(f"E_eps1_del{k}_mm")

    return even, odd


def get_parity(label):
    if label.startswith("H_"):
        return 0
    if label.startswith("E_eps1_"):
        return 1
    return 0


def get_realization(label, n):
    """Return oscillator realization as list of (coeff, word) pairs.
    A 'word' is a tuple of oscillator labels in normal order."""

    if label.startswith("H_"):
        k = int(label.split("_")[1])
        if k == 1:
            return [(Fraction(1), ("a_1_p", "a_1_m")),
                    (Fraction(1), ("b_1_p", "b_1_m"))]
        elif 2 <= k <= n:
            return [(Fraction(1), (f"b_{k-1}_p", f"b_{k-1}_m")),
                    (Fraction(-1), (f"b_{k}_p", f"b_{k}_m"))]
        elif k == n + 1:
            return [(Fraction(-1), (f"b_{n}_p", f"b_{n}_m")),
                    (Fraction(-1, 2), ())]

    if label.startswith("E_2del"):
        parts = label.split("_")
        k_str = parts[1].replace("2del", "")
        k = int(k_str)
        sign = parts[2]
        osc = f"b_{k}_p" if sign == "p" else f"b_{k}_m"
        return [(Fraction(1), (osc, osc))]

    if label.startswith("E_del") and not label.startswith("E_eps1"):
        parts = label.split("_")
        i_str = parts[1].replace("del", "")
        j_str = parts[2].replace("del", "")
        i = int(i_str)
        j = int(j_str)
        signs = parts[3]
        s_i = "p" if signs[0] == "p" else "m"
        s_j = "p" if signs[1] == "p" else "m"
        return [(Fraction(1), (f"b_{i}_{s_i}", f"b_{j}_{s_j}"))]

    if label.startswith("E_eps1_del"):
        parts = label.split("_")
        k_str = parts[2].replace("del", "")
        k = int(k_str)
        signs = parts[3]
        a_sign = "p" if signs[0] == "p" else "m"
        b_sign = "p" if signs[1] == "p" else "m"
        return [(Fraction(1), (f"a_1_{a_sign}", f"b_{k}_{b_sign}"))]

    return []


def osc_type(label):
    if label.startswith("a_"):
        return "fermion"
    return "boson"


def osc_index(label):
    parts = label.split("_")
    return (parts[0], int(parts[1]), parts[2])


def osc_parity(label):
    return 1 if label.startswith("a_") else 0


def normal_order_product(w1, w2, n):
    """Compute the product of two oscillator words in normal-ordered form.
    Returns list of (coeff, word) pairs."""
    if not w1 and not w2:
        return [(Fraction(1), ())]
    if not w1:
        return [(Fraction(1), w2)]
    if not w2:
        return [(Fraction(1), w1)]

    result = [(Fraction(1), w1 + w2)]
    result = _normal_order(result, n)
    return result


def _normal_order(terms, n):
    changed = True
    while changed:
        changed = False
        new_terms = []
        for coeff, word in terms:
            if coeff == 0:
                continue
            swapped = False
            for pos in range(len(word) - 1):
                a, b = word[pos], word[pos + 1]
                if _should_swap(a, b):
                    swapped = True
                    pa = osc_parity(a)
                    pb = osc_parity(b)
                    new_word = word[:pos] + (b, a) + word[pos + 2:]
                    if pa == 1 and pb == 1:
                        new_terms.append((-coeff, new_word))
                        contraction = _anticommutator(a, b)
                        if contraction != 0:
                            contracted_word = word[:pos] + word[pos + 2:]
                            new_terms.append((coeff * contraction, contracted_word))
                    else:
                        new_terms.append((coeff, new_word))
                        contraction = _commutator(a, b)
                        if contraction != 0:
                            contracted_word = word[:pos] + word[pos + 2:]
                            new_terms.append((coeff * contraction, contracted_word))
                    changed = True
                    break
            if not swapped:
                new_terms.append((coeff, word))
        terms = new_terms

    combined = {}
    for coeff, word in terms:
        if word in combined:
            combined[word] += coeff
        else:
            combined[word] = coeff
    return [(c, w) for w, c in combined.items() if c != 0]


def _osc_order_key(label):
    parts = label.split("_")
    kind = 0 if parts[0] == "a" else 1
    idx = int(parts[1])
    sign = 0 if parts[2] == "p" else 1
    return (kind, idx, sign)


def _should_swap(a, b):
    return _osc_order_key(a) > _osc_order_key(b)


def _anticommutator(a, b):
    ai = osc_index(a)
    bi = osc_index(b)
    if ai[0] == "a" and bi[0] == "a" and ai[1] == bi[1]:
        if ai[2] == "m" and bi[2] == "p":
            return Fraction(1)
    return Fraction(0)


def _commutator(a, b):
    ai = osc_index(a)
    bi = osc_index(b)
    if ai[0] == "b" and bi[0] == "b" and ai[1] == bi[1]:
        if ai[2] == "m" and bi[2] == "p":
            return Fraction(1)
    return Fraction(0)


def compute_bracket(gen_x, gen_y, n):
    """Compute graded bracket [X, Y} using oscillator realization."""
    real_x = get_realization(gen_x, n)
    real_y = get_realization(gen_y, n)
    px = get_parity(gen_x)
    py = get_parity(gen_y)

    xy_terms = _multiply_realizations(real_x, real_y, n)
    yx_terms = _multiply_realizations(real_y, real_x, n)

    if px == 1 and py == 1:
        result = {}
        for coeff, word in xy_terms:
            result[word] = result.get(word, Fraction(0)) + coeff
        for coeff, word in yx_terms:
            result[word] = result.get(word, Fraction(0)) + coeff
        return [(c, w) for w, c in result.items() if c != 0]
    else:
        sign = (-1) ** (px * py)
        result = {}
        for coeff, word in xy_terms:
            result[word] = result.get(word, Fraction(0)) + coeff
        for coeff, word in yx_terms:
            result[word] = result.get(word, Fraction(0)) - Fraction(sign) * coeff
        return [(c, w) for w, c in result.items() if c != 0]


def _multiply_realizations(real_a, real_b, n):
    result = []
    for ca, wa in real_a:
        for cb, wb in real_b:
            prod = normal_order_product(wa, wb, n)
            for cp, wp in prod:
                result.append((ca * cb * cp, wp))
    combined = {}
    for c, w in result:
        combined[w] = combined.get(w, Fraction(0)) + c
    return [(c, w) for w, c in combined.items() if c != 0]


def build_realization_map(n):
    """Build map from oscillator words -> generator label for single-term generators."""
    even, odd = build_basis(n)
    all_gens = odd + even
    word_to_gen = {}
    for gen in all_gens:
        real = get_realization(gen, n)
        if len(real) == 1:
            word_to_gen[real[0][1]] = (gen, real[0][0])
    return word_to_gen


def _solve_cartan_system(cartan_word_coeffs, n):
    """Solve for Cartan generator coefficients given oscillator word coefficients.

    cartan_word_coeffs maps oscillator words -> target coefficient.
    Returns dict mapping Cartan generator label -> coefficient.
    """
    cartan_labels = [f"H_{k}" for k in range(1, n + 2)]
    cartan_words = [("a_1_p", "a_1_m")]
    for k in range(1, n + 1):
        cartan_words.append((f"b_{k}_p", f"b_{k}_m"))
    cartan_words.append(())

    M = []
    target = []
    for w in cartan_words:
        row = []
        for h in cartan_labels:
            real = get_realization(h, n)
            c = Fraction(0)
            for rc, rw in real:
                if rw == w:
                    c = rc
            row.append(c)
        M.append(row)
        target.append(cartan_word_coeffs.get(w, Fraction(0)))

    num_gens = len(cartan_labels)
    num_eqs = len(cartan_words)

    coeffs = [Fraction(0)] * num_gens
    used_rows = [False] * num_eqs

    for col in range(num_gens - 1, -1, -1):
        pivot_row = -1
        for r in range(num_eqs - 1, -1, -1):
            if not used_rows[r] and M[r][col] != 0:
                pivot_row = r
                break
        if pivot_row == -1:
            continue
        used_rows[pivot_row] = True
        rhs = target[pivot_row]
        for c2 in range(col + 1, num_gens):
            rhs -= M[pivot_row][c2] * coeffs[c2]
        coeffs[col] = rhs / M[pivot_row][col]

    result = {}
    for i, label in enumerate(cartan_labels):
        if coeffs[i] != 0:
            result[label] = coeffs[i]
    return result


def express_in_basis(osc_terms, n):
    """Express oscillator-word result in terms of basis generators."""
    word_to_gen = build_realization_map(n)
    even, odd = build_basis(n)
    all_gens = odd + even
    gen_coeffs = {g: Fraction(0) for g in all_gens}

    cartan_words_set = {("a_1_p", "a_1_m"), ()}
    for k in range(1, n + 1):
        cartan_words_set.add((f"b_{k}_p", f"b_{k}_m"))

    cartan_word_coeffs = {}
    for coeff, word in osc_terms:
        if coeff == 0:
            continue
        if word in cartan_words_set:
            cartan_word_coeffs[word] = cartan_word_coeffs.get(word, Fraction(0)) + coeff
        elif word in word_to_gen:
            gen_label, gen_coeff = word_to_gen[word]
            gen_coeffs[gen_label] += coeff / gen_coeff
        else:
            for gen in all_gens:
                real = get_realization(gen, n)
                if len(real) == 1:
                    rc, rw = real[0]
                    if rw == word and rc != 0:
                        gen_coeffs[gen] += coeff / rc
                        break

    if cartan_word_coeffs:
        cartan_result = _solve_cartan_system(cartan_word_coeffs, n)
        for g, c in cartan_result.items():
            gen_coeffs[g] += c

    return {g: c for g, c in gen_coeffs.items() if c != 0}


def compute_all_structure_constants(n):
    """Compute all non-zero graded brackets for C(n+1) with bosonic rank n."""
    even, odd = build_basis(n)
    all_gens = odd + even

    structure_constants = []

    for i, x in enumerate(all_gens):
        for j, y in enumerate(all_gens):
            if j <= i:
                continue

            bracket = compute_bracket(x, y, n)
            if not bracket:
                continue

            gen_result = express_in_basis(bracket, n)
            if not gen_result:
                continue

            result_list = []
            for z, c in sorted(gen_result.items(), key=lambda item: all_gens.index(item[0])):
                result_list.append({
                    "Z": z,
                    "coeff": str(c)
                })

            structure_constants.append({
                "X": x,
                "Y": y,
                "result": result_list,
                "sign_rule": "graded"
            })

    return structure_constants


def build_parity_map(n):
    even, odd = build_basis(n)
    parity = {}
    for g in even:
        parity[g] = 0
    for g in odd:
        parity[g] = 1
    return parity


def build_generator_realizations(n):
    even, odd = build_basis(n)
    all_gens = odd + even
    realizations = {}

    for gen in all_gens:
        real = get_realization(gen, n)
        terms = []
        for coeff, word in real:
            terms.append({
                "words": list(word),
                "coeff": str(coeff)
            })
        realizations[gen] = {
            "standard_form": terms,
            "parity": get_parity(gen)
        }

    return realizations


def generate_schema1(n):
    even, odd = build_basis(n)
    parity = build_parity_map(n)
    realizations = build_generator_realizations(n)
    structure_constants = compute_all_structure_constants(n)

    dim_even = 2 * n * n + n + 1
    dim_odd = 4 * n
    dim_total = dim_even + dim_odd

    assert len(even) == dim_even, f"Even count {len(even)} != {dim_even}"
    assert len(odd) == dim_odd, f"Odd count {len(odd)} != {dim_odd}"

    boson_labels = []
    for k in range(1, n + 1):
        boson_labels.extend([f"b_{k}_p", f"b_{k}_m"])

    osc_ordering_parts = ["a_1_p", "a_1_m"] + boson_labels

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
                "count": 2,
                "m": 1,
                "labels": ["a_1_p", "a_1_m"],
                "description": "Standard fermionic pair a_1^± with {a_1^-, a_1^+} = 1"
            },
            "bosons": {
                "count": 2 * n,
                "n": n,
                "labels": boson_labels,
                "description": f"Bosonic oscillators b_k^± with k=1,...,{n}"
            }
        },
        "oscillator_relations": {
            "standard_fermion_anticommutators": {
                "description": "Canonical anti-commutation relations for fermionic pair",
                "relations": {
                    "conjugate_pair": "{a_1^-, a_1^+} = 1",
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
                "boson_fermion": "[b_k^±, a_1^±] = 0"
            }
        },
        "central_elements": {
            "kappa": {
                "parity": 1,
                "property": "kappa^2 = 0",
                "description": "Odd nilpotent central element for deformation"
            },
            "K": {
                "parity": 0,
                "property": "K = 1",
                "description": "Even central identity element (Bakalov-Sullivan); identified with scalar 1"
            }
        },
        "basis": {
            "even": even,
            "odd": odd,
            "ordering_convention": "PBW: κ < [odd] < [even]  (K = 1 is excluded)"
        },
        "parity": parity,
        "generator_realization": {
            "description": "Standard form with PBW ordering",
            "ordering": ", ".join(osc_ordering_parts),
            "realizations": realizations
        },
        "structure_constants": structure_constants,
        "metadata": {
            "generated_by": "C_generators.py",
            "generation_date": str(date.today()),
            "schema_version": "5.0",
            "references": [
                "Frappat et al. (2000), Dictionary on Lie Algebras and Superalgebras",
                "Bakalov and Sullivan (2017)"
            ]
        }
    }

    return schema


def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(os.path.dirname(script_dir), "data")
    os.makedirs(data_dir, exist_ok=True)

    for n in [1, 2, 3]:
        print(f"Generating C({n + 1}) = osp(2|{2 * n}) structure (n={n})...")
        schema = generate_schema1(n)
        filename = os.path.join(data_dir, f"C_{n}_structure.json")
        with open(filename, "w") as f:
            json.dump(schema, f, indent=2)
        print(f"  Written to {filename}")
        print(f"  Even: {len(schema['basis']['even'])}, Odd: {len(schema['basis']['odd'])}")
        print(f"  Structure constants: {len(schema['structure_constants'])} non-zero brackets")


if __name__ == "__main__":
    main()
