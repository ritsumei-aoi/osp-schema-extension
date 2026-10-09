"""
Structure constant generator for C(n+1) = osp(2|2n).

Computes the Lie superalgebra bracket [X, Y} using oscillator realizations
and outputs Schema 1 JSON files.
"""

import json
import datetime
from fractions import Fraction
from itertools import product as iter_product


def build_basis(n):
    even = []
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


def get_parity(label):
    if label.startswith("H_"):
        return 0
    if label.startswith("E_eps1_"):
        return 1
    return 0


def get_realization(label, n):
    """Return oscillator realization as list of (coeff, word_tuple).
    Word tuples use canonical ordering: a_1_p/m before b_k_p/m.
    Each element is a monomial: (Fraction_coeff, (osc1, osc2, ...)).
    """
    if label.startswith("H_"):
        k = int(label.split("_")[1])
        if k == 1:
            return [
                (Fraction(1), ("a_1_p", "a_1_m")),
                (Fraction(1), ("b_1_p", "b_1_m")),
            ]
        elif 2 <= k <= n:
            return [
                (Fraction(1), (f"b_{k-1}_p", f"b_{k-1}_m")),
                (Fraction(-1), (f"b_{k}_p", f"b_{k}_m")),
            ]
        elif k == n + 1:
            return [
                (Fraction(-1), (f"b_{n}_p", f"b_{n}_m")),
                (Fraction(-1, 2), ()),
            ]
    elif label.startswith("E_eps1_"):
        parts = label.split("_")
        k = int(parts[2].replace("del", ""))
        signs = parts[3]
        a_sign = "a_1_p" if signs[0] == "p" else "a_1_m"
        b_sign = f"b_{k}_p" if signs[1] == "p" else f"b_{k}_m"
        return [(Fraction(1), (a_sign, b_sign))]
    elif label.startswith("E_2del"):
        parts = label.split("_")
        k = int(parts[1].replace("2del", ""))
        sign = parts[2]
        b = f"b_{k}_p" if sign == "p" else f"b_{k}_m"
        return [(Fraction(1, 2), (b, b))]
    elif label.startswith("E_del"):
        parts = label.split("_")
        i = int(parts[1].replace("del", ""))
        j = int(parts[2].replace("del", ""))
        signs = parts[3]
        b_i = f"b_{i}_p" if signs[0] == "p" else f"b_{i}_m"
        b_j = f"b_{j}_p" if signs[1] == "p" else f"b_{j}_m"
        return [(Fraction(1), (b_i, b_j))]
    return []


def osc_parity(osc):
    if osc.startswith("a_"):
        return 1
    return 0


def is_creation(osc):
    return osc.endswith("_p")


def osc_index(osc):
    parts = osc.split("_")
    return int(parts[1])


def osc_type(osc):
    return osc[0]


def compute_product(word_a, word_b):
    """Compute the product of two oscillator words in normal-ordered form.
    Returns a dict mapping word_tuple -> Fraction coefficient.
    Uses CCR [b_i^-, b_j^+] = delta_ij and CAR {a_1^-, a_1^+} = 1.
    """
    result = {}
    _normal_order(list(word_a) + list(word_b), Fraction(1), result)
    return result


def _normal_order(word, coeff, result):
    """Recursively normal-order a word of oscillators.
    Normal order: a_1_p, a_1_m before b's; creation before annihilation;
    within b's: lower index first, creation before annihilation.
    """
    if coeff == 0:
        return

    for i in range(len(word) - 1):
        a, b = word[i], word[i + 1]
        if _needs_swap(a, b):
            swapped = word[:i] + [b, a] + word[i + 2:]
            pa, pb = osc_parity(a), osc_parity(b)

            if pa == 1 and pb == 1:
                sign = Fraction(-1)
                contraction = _contraction_fermion(a, b)
            else:
                sign = Fraction(1)
                contraction = _contraction_boson(a, b)

            _normal_order(swapped, coeff * sign, result)

            if contraction != 0:
                contracted_word = word[:i] + word[i + 2:]
                _normal_order(contracted_word, coeff * contraction, result)
            return

    fermion_labels = [w for w in word if osc_parity(w) == 1]
    if len(fermion_labels) != len(set(fermion_labels)):
        return

    key = tuple(word)
    result[key] = result.get(key, Fraction(0)) + coeff


def _needs_swap(a, b):
    """Check if oscillators a, b need swapping for normal ordering."""
    pa, pb = osc_parity(a), osc_parity(b)
    ta, tb = osc_type(a), osc_type(b)

    if ta == "b" and tb == "a":
        return True
    if ta == "a" and tb == "a":
        if is_creation(b) and not is_creation(a):
            return True
        return False
    if ta == "b" and tb == "b":
        ia, ib = osc_index(a), osc_index(b)
        if ia > ib:
            return True
        if ia == ib:
            if is_creation(b) and not is_creation(a):
                return True
        return False
    return False


def _contraction_fermion(a, b):
    """Anticommutator contraction: {a, b} value (subtracted since we anticommuted)."""
    if osc_type(a) == "a" and osc_type(b) == "a":
        if not is_creation(a) and is_creation(b):
            return Fraction(1)
    return Fraction(0)


def _contraction_boson(a, b):
    """Commutator contraction: [a, b] value (subtracted since we commuted)."""
    if osc_type(a) == "b" and osc_type(b) == "b":
        ia, ib = osc_index(a), osc_index(b)
        if ia == ib:
            if not is_creation(a) and is_creation(b):
                return Fraction(1)
    return Fraction(0)


def multiply_realizations(real_a, real_b):
    """Multiply two realizations (lists of (coeff, word_tuple)) and return
    a combined realization in normal-ordered form."""
    result = {}
    for ca, wa in real_a:
        for cb, wb in real_b:
            prod = compute_product(wa, wb)
            for word, c in prod.items():
                result[word] = result.get(word, Fraction(0)) + ca * cb * c

    return [(c, w) for w, c in result.items() if c != 0]


def compute_bracket(label_x, label_y, n):
    """Compute [X, Y} = XY - (-1)^{p(X)p(Y)} YX in oscillator form."""
    px = get_parity(label_x)
    py = get_parity(label_y)

    real_x = get_realization(label_x, n)
    real_y = get_realization(label_y, n)

    xy = multiply_realizations(real_x, real_y)
    yx = multiply_realizations(real_y, real_x)

    sign = (-1) ** (px * py)

    result = {}
    for c, w in xy:
        result[w] = result.get(w, Fraction(0)) + c
    for c, w in yx:
        result[w] = result.get(w, Fraction(0)) - sign * c

    return {w: c for w, c in result.items() if c != 0}


def express_in_basis(osc_result, all_labels, n):
    """Express an oscillator-word result as a linear combination of basis generators."""
    realization_map = {}
    for label in all_labels:
        real = get_realization(label, n)
        for c, w in real:
            if w not in realization_map:
                realization_map[w] = []
            realization_map[w].append((label, c))

    terms = {}
    remaining = dict(osc_result)

    for w, target_coeff in list(remaining.items()):
        if target_coeff == 0:
            continue
        if w in realization_map:
            candidates = realization_map[w]
            if len(candidates) == 1:
                label, gen_coeff = candidates[0]
                ratio = target_coeff / gen_coeff
                terms[label] = terms.get(label, Fraction(0)) + ratio
            else:
                for label, gen_coeff in candidates:
                    full_real = get_realization(label, n)
                    if len(full_real) == 1:
                        ratio = target_coeff / gen_coeff
                        terms[label] = terms.get(label, Fraction(0)) + ratio
                        break
        elif w == ():
            pass

    return {k: v for k, v in terms.items() if v != 0}


def compute_all_structure_constants(n):
    """Compute all non-zero brackets for C(n+1) with bosonic rank n."""
    even, odd = build_basis(n)
    all_labels = odd + even
    parity_map = {label: get_parity(label) for label in all_labels}

    inv_map = build_inverse_map(n, all_labels)

    structure_constants = []
    processed = set()

    for i, x in enumerate(all_labels):
        for j, y in enumerate(all_labels):
            if j <= i:
                continue
            pair = (x, y)
            if pair in processed:
                continue
            processed.add(pair)

            osc_result = compute_bracket(x, y, n)
            if not osc_result:
                continue

            basis_result = decompose_via_inverse(osc_result, inv_map, n=n)
            if not basis_result:
                continue

            result_list = []
            for z, c in sorted(basis_result.items()):
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


def build_inverse_map(n, all_labels):
    """Build a map from oscillator words to basis generators for decomposition."""
    inv = {}
    for label in all_labels:
        real = get_realization(label, n)
        for c, w in real:
            if w not in inv:
                inv[w] = []
            inv[w].append((label, c))
    return inv


def decompose_via_inverse(osc_result, inv_map, n=None, all_labels=None):
    """Decompose oscillator expression into basis generators.
    Handles multi-term Cartan generators via proper linear decomposition."""
    remaining = dict(osc_result)
    terms = {}

    for w in list(remaining.keys()):
        c = remaining.get(w, Fraction(0))
        if c == 0:
            continue
        if w not in inv_map:
            if w == ():
                continue
            raise ValueError(f"Unknown oscillator word {w}")
        non_cartan = [(label, gc) for label, gc in inv_map[w]
                      if not label.startswith("H_")]
        if non_cartan:
            label, gen_coeff = non_cartan[0]
            ratio = c / gen_coeff
            terms[label] = terms.get(label, Fraction(0)) + ratio
            for rc, rw in get_realization(label, n):
                remaining[rw] = remaining.get(rw, Fraction(0)) - ratio * rc

    a_coeff = remaining.get(("a_1_p", "a_1_m"), Fraction(0))
    b_coeffs = [Fraction(0)] * (n + 1)
    for k in range(1, n + 1):
        b_coeffs[k] = remaining.get((f"b_{k}_p", f"b_{k}_m"), Fraction(0))
    const_coeff = remaining.get((), Fraction(0))

    if a_coeff != 0 or any(b != 0 for b in b_coeffs) or const_coeff != 0:
        cartan = _solve_cartan(n, a_coeff, b_coeffs, const_coeff)
        for label, c in cartan.items():
            if c != 0:
                terms[label] = terms.get(label, Fraction(0)) + c

    return {k: v for k, v in terms.items() if v != 0}


def _solve_cartan(n, a_coeff, b_coeffs, const_coeff):
    """Solve for Cartan generator coefficients.

    H_1 = a_1^+ a_1^- + b_1^+ b_1^-
    H_k = b_{k-1}^+ b_{k-1}^- - b_k^+ b_k^-  (2 <= k <= n)
    H_{n+1} = -b_n^+ b_n^- - 1/2
    """
    c = [Fraction(0)] * (n + 2)

    c[1] = a_coeff
    c[n + 1] = const_coeff / Fraction(-1, 2) if const_coeff != 0 else Fraction(0)

    if n == 1:
        pass
    else:
        c[2] = b_coeffs[1] - c[1]
        for k in range(2, n):
            c[k + 1] = b_coeffs[k] + c[k]

    return {f"H_{i}": c[i] for i in range(1, n + 2) if c[i] != 0}


def build_generator_realizations(n):
    """Build generator_realization field for the JSON schema."""
    even, odd = build_basis(n)
    all_labels = odd + even
    realizations = {}

    for label in all_labels:
        real = get_realization(label, n)
        standard_form = []
        for c, w in real:
            standard_form.append({
                "words": list(w),
                "coeff": str(c)
            })

        frappat = _to_frappat(label, real)

        realizations[label] = {
            "standard_form": standard_form,
            "frappat_form": frappat,
            "parity": get_parity(label)
        }

    return realizations


def _to_frappat(label, real):
    """Generate human-readable Frappat form string."""
    parts = []
    for c, w in real:
        if w == ():
            parts.append(str(c))
        else:
            word_str = " ".join(w).replace("_p", "^+").replace("_m", "^-").replace("a_1", "a_1").replace("b_", "b_")
            cstr = ""
            if c == 1:
                cstr = ""
            elif c == -1:
                cstr = "-"
            elif c == Fraction(1, 2):
                cstr = "1/2 "
            elif c == Fraction(-1, 2):
                cstr = "-1/2 "
            else:
                cstr = f"{c} "
            parts.append(f"{cstr}{word_str}")
    return " + ".join(parts).replace("+ -", "- ")


def generate_schema1_json(n):
    """Generate complete Schema 1 JSON for C(n+1) with bosonic rank n."""
    even, odd = build_basis(n)
    all_labels = odd + even

    dim_even = 2 * n * n + n + 1
    dim_odd = 4 * n
    dim_total = dim_even + dim_odd

    assert len(even) == dim_even, f"Even basis count {len(even)} != {dim_even}"
    assert len(odd) == dim_odd, f"Odd basis count {len(odd)} != {dim_odd}"

    boson_labels = []
    for k in range(1, n + 1):
        boson_labels.extend([f"b_{k}_p", f"b_{k}_m"])

    parity_map = {}
    for label in all_labels:
        parity_map[label] = get_parity(label)

    structure_constants = compute_all_structure_constants(n)
    realizations = build_generator_realizations(n)

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
                "type": "standard_pair",
                "m": 1,
                "labels": ["a_1_p", "a_1_m"],
                "parity": 1,
                "description": "Standard fermionic pair a_1^± with CAR: {a_1^-, a_1^+} = 1"
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
                "description": "Canonical anticommutation relations for the standard fermionic pair",
                "relations": {
                    "anticommutator": "{a_1^-, a_1^+} = 1",
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
                "boson_fermion": "[b_i^±, a_1^±] = 0"
            }
        },
        "central_elements": {
            "kappa": {
                "label": "kappa",
                "parity": 1,
                "nilpotency": "kappa^2 = 0",
                "description": "Odd central element for the nilpotent extension"
            },
            "K": {
                "label": "K",
                "parity": 0,
                "value": 1,
                "description": "Even central identity element (= scalar 1)"
            }
        },
        "basis": {
            "even": even,
            "odd": odd,
            "ordering_convention": "PBW: κ < [odd] < [even]  (K = 1 is excluded)"
        },
        "parity": parity_map,
        "generator_realization": {
            "description": "Standard form with PBW ordering",
            "ordering": ", ".join(["a_1_p", "a_1_m"] + boson_labels),
            "realizations": realizations
        },
        "structure_constants": structure_constants,
        "metadata": {
            "generated_by": "C_generators.py",
            "generation_date": datetime.date.today().isoformat(),
            "references": [
                "Frappat et al. (2000), Dictionary on Lie Algebras and Superalgebras",
                "Bakalov and Sullivan (2017)"
            ]
        }
    }

    return schema


def main():
    import os
    data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
    os.makedirs(data_dir, exist_ok=True)

    for n in [1, 2, 3]:
        print(f"Generating C({n + 1}) structure (n={n})...")
        schema = generate_schema1_json(n)
        filename = os.path.join(data_dir, f"C_{n}_structure.json")
        with open(filename, "w") as f:
            json.dump(schema, f, indent=2)
        sc_count = len(schema["structure_constants"])
        print(f"  -> {filename}: {sc_count} non-zero brackets, "
              f"dim = {schema['algebra']['dimension']['total']}")


if __name__ == "__main__":
    main()
