"""
C(n+1) = osp(2|2n) structure constant generator.

Generates Schema 1 JSON files for n=1,2,3 following the v5.0 specification.
Uses oscillator realization with standard fermionic pair (a_1^+, a_1^-) and
bosonic oscillators (b_k^+, b_k^-).
"""

import json
import os
from fractions import Fraction
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
        odd.append(f"E_eps1_del{k}_pm")
    for k in range(1, n + 1):
        odd.append(f"E_eps1_del{k}_mp")
        odd.append(f"E_eps1_del{k}_mm")

    return even, odd


def get_parity(label):
    if label.startswith("E_eps1"):
        return 1
    return 0


def get_realization(label, n):
    """Return oscillator realization as list of (coeff, [osc_labels])."""
    if label.startswith("H_"):
        k = int(label.split("_")[1])
        if k == 1:
            return [(Fraction(1), ["a_1_p", "a_1_m"]),
                    (Fraction(1), ["b_1_p", "b_1_m"])]
        elif 2 <= k <= n:
            return [(Fraction(1), [f"b_{k-1}_p", f"b_{k-1}_m"]),
                    (Fraction(-1), [f"b_{k}_p", f"b_{k}_m"])]
        elif k == n + 1:
            return [(Fraction(-1), [f"b_{n}_p", f"b_{n}_m"]),
                    (Fraction(-1, 2), [])]
    elif label.startswith("E_2del"):
        # E_2del{k}_p or E_2del{k}_m
        import re
        m = re.match(r"E_2del(\d+)_(p|m)", label)
        k = int(m.group(1))
        s = m.group(2)
        return [(Fraction(1), [f"b_{k}_{s}", f"b_{k}_{s}"])]
    elif label.startswith("E_del") and not label.startswith("E_eps"):
        import re
        m = re.match(r"E_del(\d+)_del(\d+)_(pp|pm|mp|mm)", label)
        i = int(m.group(1))
        j = int(m.group(2))
        signs = m.group(3)
        si = "p" if signs[0] == "p" else "m"
        sj = "p" if signs[1] == "p" else "m"
        return [(Fraction(1), [f"b_{i}_{si}", f"b_{j}_{sj}"])]
    elif label.startswith("E_eps1_del"):
        import re
        m = re.match(r"E_eps1_del(\d+)_(pp|pm|mp|mm)", label)
        k = int(m.group(1))
        signs = m.group(2)
        sa = "p" if signs[0] == "p" else "m"
        sb = "p" if signs[1] == "p" else "m"
        return [(Fraction(1), [f"a_1_{sa}", f"b_{k}_{sb}"])]
    return []


OSC_PARITY = {}

def osc_parity(label):
    if label.startswith("a_"):
        return 1
    return 0


def compute_bracket_oscillator(real_X, real_Y, n):
    """Compute [X, Y} using oscillator algebra.

    Returns a dict mapping oscillator word tuples to Fraction coefficients.
    """
    result = {}

    pX = sum(osc_parity(o) for o in real_X[0][1]) % 2 if real_X else 0
    pY = sum(osc_parity(o) for o in real_Y[0][1]) % 2 if real_Y else 0

    for cX, word_X in real_X:
        for cY, word_Y in real_Y:
            xy = multiply_words(word_X, word_Y, n)
            parity_x_term = sum(osc_parity(o) for o in word_X) % 2
            parity_y_term = sum(osc_parity(o) for o in word_Y) % 2
            sign = (-1) ** (parity_x_term * parity_y_term)
            yx = multiply_words(word_Y, word_X, n)

            for word, coeff in xy.items():
                val = result.get(word, Fraction(0))
                result[word] = val + cX * cY * coeff
            for word, coeff in yx.items():
                val = result.get(word, Fraction(0))
                result[word] = val - cX * cY * coeff * sign

    cleaned = {k: v for k, v in result.items() if v != 0}
    return cleaned


def multiply_words(w1, w2, n):
    """Multiply two oscillator words using normal ordering.

    Returns dict mapping word tuples to Fraction coefficients.
    """
    word = list(w1) + list(w2)
    return normal_order(word, n)


def normal_order(word, n):
    """Normal-order an oscillator word.

    Ordering: a_1_p, a_1_m, b_1_p, b_1_m, ..., b_n_p, b_n_m
    Creators before annihilators for each pair.
    """
    osc_order = ["a_1_p", "a_1_m"]
    for k in range(1, n + 1):
        osc_order.extend([f"b_{k}_p", f"b_{k}_m"])

    order_map = {o: i for i, o in enumerate(osc_order)}

    terms = {tuple(word): Fraction(1)}

    changed = True
    max_iter = 100
    iteration = 0
    while changed and iteration < max_iter:
        changed = False
        iteration += 1
        new_terms = {}
        for w, c in terms.items():
            if c == 0:
                continue
            swapped = False
            for pos in range(len(w) - 1):
                o1, o2 = w[pos], w[pos + 1]
                if order_map.get(o1, 0) > order_map.get(o2, 0):
                    p1 = osc_parity(o1)
                    p2 = osc_parity(o2)
                    sign = (-1) ** (p1 * p2)

                    swapped_word = list(w)
                    swapped_word[pos] = o2
                    swapped_word[pos + 1] = o1
                    sw_key = tuple(swapped_word)

                    val = new_terms.get(sw_key, Fraction(0))
                    new_terms[sw_key] = val + c * sign

                    contraction = get_contraction(o1, o2, n)
                    if contraction != 0:
                        contracted_word = tuple(list(w[:pos]) + list(w[pos+2:]))
                        val2 = new_terms.get(contracted_word, Fraction(0))
                        new_terms[contracted_word] = val2 + c * contraction

                    swapped = True
                    changed = True
                    break
            if not swapped:
                val = new_terms.get(w, Fraction(0))
                new_terms[w] = val + c

        terms = {k: v for k, v in new_terms.items() if v != 0}

    # Fermionic nilpotency: any word with duplicate fermionic oscillators vanishes
    cleaned = {}
    for w, c in terms.items():
        fermion_labels = [o for o in w if osc_parity(o) == 1]
        if len(fermion_labels) != len(set(fermion_labels)):
            continue
        cleaned[w] = c

    return cleaned


def get_contraction(o1, o2, n):
    """Get contraction value when swapping o1 past o2 (o1 is to the left, needs to move right)."""
    if o1 == "a_1_m" and o2 == "a_1_p":
        return Fraction(1)
    for k in range(1, n + 1):
        if o1 == f"b_{k}_m" and o2 == f"b_{k}_p":
            return Fraction(1)
    return Fraction(0)


def express_in_basis(osc_result, all_generators, n):
    """Express an oscillator result as a linear combination of basis generators.

    Solves the linear system: sum_i c_i * realization(gen_i) = osc_result
    """
    if not osc_result:
        return {}

    all_words = set()
    gen_vectors = {}
    for g in all_generators:
        real = get_realization(g, n)
        vec = {}
        for coeff, words in real:
            key = tuple(words)
            vec[key] = vec.get(key, Fraction(0)) + coeff
            all_words.add(key)
    for word in osc_result:
        all_words.add(word)

    gen_vectors = {}
    for g in all_generators:
        real = get_realization(g, n)
        vec = {}
        for coeff, words in real:
            key = tuple(words)
            vec[key] = vec.get(key, Fraction(0)) + coeff
        gen_vectors[g] = vec

    word_list = sorted(all_words, key=lambda w: (len(w), w))

    remaining = dict(osc_result)
    result = {}

    for g in all_generators:
        gvec = gen_vectors[g]
        unique_words = [w for w in gvec if not any(
            w in gen_vectors[g2] for g2 in all_generators if g2 != g
        ) and gvec[w] != 0]

        if unique_words:
            w = unique_words[0]
            if w in remaining and remaining[w] != 0:
                ratio = remaining[w] / gvec[w]
                result[g] = result.get(g, Fraction(0)) + ratio
                for gw, gc in gvec.items():
                    remaining[gw] = remaining.get(gw, Fraction(0)) - ratio * gc
                remaining = {k: v for k, v in remaining.items() if v != 0}

    for g in all_generators:
        if g in result:
            continue
        gvec = gen_vectors[g]
        nonzero_words = [w for w in gvec if gvec[w] != 0]
        if nonzero_words:
            w = nonzero_words[0]
            if w in remaining and remaining[w] != 0:
                ratio = remaining[w] / gvec[w]
                result[g] = result.get(g, Fraction(0)) + ratio
                for gw, gc in gvec.items():
                    remaining[gw] = remaining.get(gw, Fraction(0)) - ratio * gc
                remaining = {k: v for k, v in remaining.items() if v != 0}

    return {k: v for k, v in result.items() if v != 0}


def compute_all_structure_constants(n):
    even, odd = build_basis(n)
    all_gens = odd + even

    structure_constants = []

    for i, X in enumerate(all_gens):
        for j, Y in enumerate(all_gens):
            if j <= i:
                continue

            real_X = get_realization(X, n)
            real_Y = get_realization(Y, n)

            bracket = compute_bracket_oscillator(real_X, real_Y, n)

            decomp = express_in_basis(bracket, all_gens, n)

            for Z, coeff in decomp.items():
                if coeff != 0:
                    structure_constants.append({
                        "X": X,
                        "Y": Y,
                        "Z": Z,
                        "coeff": str(coeff),
                        "sign_rule": "graded"
                    })

    return structure_constants


def build_parity_dict(n):
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
    for g in all_gens:
        real = get_realization(g, n)
        standard_form = []
        for coeff, words in real:
            standard_form.append({
                "words": words,
                "coeff": str(coeff)
            })
        realizations[g] = {
            "standard_form": standard_form,
            "parity": get_parity(g)
        }
    return realizations


def build_schema1_json(n):
    even, odd = build_basis(n)

    dim_even = 2 * n * n + n + 1
    dim_odd = 4 * n
    dim_total = dim_even + dim_odd

    assert len(even) == dim_even, f"Even count {len(even)} != {dim_even}"
    assert len(odd) == dim_odd, f"Odd count {len(odd)} != {dim_odd}"

    boson_labels = []
    for k in range(1, n + 1):
        boson_labels.extend([f"b_{k}_p", f"b_{k}_m"])

    schema = {
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
                "description": "Standard fermionic pair a_1^± with CAR"
            },
            "bosons": {
                "count": 2 * n,
                "n": n,
                "labels": boson_labels,
                "description": f"Bosonic oscillators b_i^± with i=1,...,{n}"
            }
        },
        "oscillator_relations": {
            "standard_fermion_anticommutators": {
                "description": "Canonical anticommutation relations for fermionic oscillators",
                "relations": {
                    "conjugate_pair": "{a_1^-, a_1^+} = 1",
                    "same_type": "{a_1^±, a_1^±} = 0"
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
                "boson_fermion": "[b_i^±, a_1^±] = 0"
            }
        },
        "central_elements": {
            "kappa": {
                "label": "kappa",
                "parity": 1,
                "nilpotency": "kappa^2 = 0",
                "description": "Odd central element for inhomogeneous deformation"
            },
            "K": {
                "label": "K",
                "parity": 0,
                "description": "Even central element, identified with scalar 1"
            }
        },
        "basis": {
            "even": even,
            "odd": odd,
            "ordering_convention": "PBW: κ < [odd] < [even]  (K = 1 is excluded)"
        },
        "parity": build_parity_dict(n),
        "generator_realization": {
            "description": "Standard form with PBW ordering",
            "ordering": ", ".join(["a_1_p", "a_1_m"] + boson_labels),
            "realizations": build_generator_realizations(n)
        },
        "structure_constants": compute_all_structure_constants(n),
        "metadata": {
            "generated_by": "C_generators.py",
            "generation_date": "2026-10-05",
            "references": [
                "Frappat et al. (2000), Dictionary on Lie Algebras and Superalgebras",
                "Bakalov and Sullivan (2017)"
            ]
        }
    }

    return schema


def generate_all(output_dir="data"):
    os.makedirs(output_dir, exist_ok=True)
    for n in [1, 2, 3]:
        print(f"Generating C({n+1}) = osp(2|{2*n}), n={n}...")
        schema = build_schema1_json(n)
        filename = os.path.join(output_dir, f"C_{n}_structure.json")
        with open(filename, "w") as f:
            json.dump(schema, f, indent=2)
        sc_count = len(schema["structure_constants"])
        print(f"  Written to {filename} ({sc_count} structure constants)")


if __name__ == "__main__":
    generate_all()
