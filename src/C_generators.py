"""Basis construction and Schema 1 structure-constant generation for C(n+1).

Usage:
    python3 src/C_generators.py            # writes data/C_{n}_structure.json for n=1,2,3
"""

import datetime
import itertools
import json
import os
import sys
from fractions import Fraction

sys.path.insert(0, os.path.dirname(__file__))
from oscillator_algebra import Element, super_bracket, letter_index, word_parity

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")


def even_basis_labels(n):
    labels = ["H_eps"] + [f"H_{k}" for k in range(1, n + 1)]
    labels += [f"E_2del{k}_p" for k in range(1, n + 1)]
    labels += [f"E_del{i}_del{j}_pp" for i, j in itertools.combinations(range(1, n + 1), 2)]
    labels += [f"E_2del{k}_m" for k in range(1, n + 1)]
    labels += [f"E_del{i}_del{j}_mm" for i, j in itertools.combinations(range(1, n + 1), 2)]
    labels += [f"E_del{i}_del{j}_pm" for i, j in itertools.combinations(range(1, n + 1), 2)]
    labels += [f"E_del{i}_del{j}_mp" for i, j in itertools.combinations(range(1, n + 1), 2)]
    return labels


def odd_basis_labels(n):
    labels = []
    for sigma in ("p", "m"):
        for s in ("p", "m"):
            labels += [f"E_eps_del{k}_{sigma}{s}" for k in range(1, n + 1)]
    return labels


def realization_words(label):
    """Oscillator realization of a basis generator as [(words, coeff)]."""
    if label == "H_eps":
        return [(("a_1_p", "a_1_m"), Fraction(1)), ((), Fraction(-1, 2))]
    if label.startswith("H_"):
        k = int(label[2:])
        return [((f"b_{k}_p", f"b_{k}_m"), Fraction(1)), ((), Fraction(1, 2))]
    if label.startswith("E_2del"):
        k, s = label[6:].split("_")
        return [((f"b_{k}_{s}", f"b_{k}_{s}"), Fraction(1))]
    if label.startswith("E_eps_del"):
        body = label[9:]
        k, ss = body.split("_")
        sigma, s = ss[0], ss[1]
        return [((f"a_1_{sigma}", f"b_{k}_{s}"), Fraction(1))]
    if label.startswith("E_del"):
        # E_del{i}_del{j}_{s1}{s2}
        parts = label.split("_")  # ['E', 'del{i}', 'del{j}', '{s1}{s2}']
        i = int(parts[1][3:])
        j = int(parts[2][3:])
        s1, s2 = parts[3][0], parts[3][1]
        return [((f"b_{i}_{s1}", f"b_{j}_{s2}"), Fraction(1))]
    raise ValueError(f"unknown label {label}")


def build_basis(n):
    """Return (labels, parity_map, elements) for C(n+1) with bosonic rank n."""
    odd = odd_basis_labels(n)
    even = even_basis_labels(n)
    labels = odd + even  # PBW: kappa < [odd] < [even]
    parity = {l: (1 if l in set(odd) else 0) for l in labels}
    elements = {}
    for l in labels:
        wc = [
            (tuple(letter_index(w) for w in words), coeff)
            for words, coeff in realization_words(l)
        ]
        elements[l] = Element.from_words(wc)
    return labels, parity, elements


def decompose(element, n, allow_constant=False):
    """Decompose an Element (quadratic words + constant) into basis labels.

    Returns dict label -> Fraction; constant parts fold into H_eps/H_k shifts.
    If allow_constant, residual scalar is returned under 'K'; otherwise it
    must vanish (closure) or ValueError is raised.
    """
    out = {}
    const = Fraction(0)
    word_to_label = {}
    _, _, elems = _basis_cache(n)
    for lbl, el in elems.items():
        for w, c in el.terms.items():
            if len(w) == 2:
                word_to_label[w] = (lbl, c)
    for w, c in element.terms.items() if not isinstance(element, dict) else element.items():
        if len(w) == 0:
            const += c
            continue
        if w not in word_to_label:
            raise ValueError(f"word {w} not in basis span")
        lbl, lead = word_to_label[w]
        coeff = c / lead
        out[lbl] = out.get(lbl, Fraction(0)) + coeff
        # subtract the constant that the basis element carries
        _, _, elems2 = _basis_cache(n)
        for w2, c2 in elems2[lbl].terms.items():
            if len(w2) == 0:
                const -= coeff * c2
    if const != 0:
        if allow_constant:
            out["K"] = const
        else:
            raise ValueError(f"algebra does not close: residual constant {const}")
    return {k: v for k, v in out.items() if v != 0}


_CACHE = {}


def _basis_cache(n):
    if n not in _CACHE:
        _CACHE[n] = build_basis(n)
    return _CACHE[n]


def compute_structure_constants(n):
    labels, parity, elems = _basis_cache(n)
    records = []
    for x in labels:
        for y in labels:
            br = super_bracket(elems[x], elems[y], parity[x], parity[y])
            dec = decompose(br, n)
            for z, c in sorted(dec.items()):
                records.append(
                    {"X": x, "Y": y, "Z": z, "coeff": str(c), "sign_rule": "graded"}
                )
    return records


def realization_json(n):
    labels, parity, _ = _basis_cache(n)
    real = {}
    for l in labels:
        std = [
            {"words": list(words), "coeff": str(coeff)}
            for words, coeff in realization_words(l)
        ]
        real[l] = {"standard_form": std, "parity": parity[l]}
    return real


def schema1(n):
    labels, parity, _ = _basis_cache(n)
    odd = odd_basis_labels(n)
    even = even_basis_labels(n)
    dim_even, dim_odd = 2 * n * n + n + 1, 4 * n
    assert len(even) == dim_even and len(odd) == dim_odd
    return {
        "schema_version": "5.0",
        "algebra": {
            "family": "C",
            "m": 1,
            "n": n,
            "cartan_type": f"C({n + 1})",
            "alternative_notation": {
                "osp": f"osp(2|{2 * n})",
                "dimension_formula": "osp(2m|2n) with m=1; even = 2n^2 + n + 1, odd = 4n",
            },
            "dimension": {
                "total": dim_even + dim_odd,
                "even": dim_even,
                "odd": dim_odd,
            },
        },
        "oscillator_generators": {
            "fermions": {
                "m": 1,
                "count": 2,
                "labels": ["a_1_p", "a_1_m"],
                "parity": 1,
                "description": "Standard fermionic pair a_1^± with CAR {a_1^-, a_1^+} = 1",
            },
            "bosons": {
                "n": n,
                "count": 2 * n,
                "labels": [f"b_{k}_{s}" for k in range(1, n + 1) for s in ("p", "m")],
                "parity": 0,
                "description": "Bosonic oscillators b_k^± with k=1,...,n (CCR)",
            },
        },
        "oscillator_relations": {
            "standard_fermion_anticommutators": {
                "description": "Canonical anticommutation relations for the standard fermionic pair",
                "relations": {
                    "conjugate_pair": "{a_1^-, a_1^+} = 1",
                    "same_type": "{a_1^+, a_1^+} = {a_1^-, a_1^-} = 0",
                },
            },
            "bosonic_commutators": {
                "description": "Canonical commutation relations for bosonic oscillators",
                "relations": {
                    "same_type": "[b_i^±, b_j^±] = 0 for all i, j",
                    "conjugate_pair": "[b_i^-, b_j^+] = δ_{ij}",
                },
            },
            "mixed_commutators": {
                "boson_fermion": "[b_i^±, a_1^±] = 0 (undeformed; see Schema 2 for the gb deformation)"
            },
        },
        "central_elements": {
            "kappa": {
                "label": "kappa",
                "parity": 1,
                "relation": "kappa^2 = 0",
                "description": "Odd nilpotent central element; carrier of the inhomogeneous deformation.",
            },
            "K": {
                "label": "K",
                "parity": 0,
                "relation": "K = 1",
                "description": "Even central element identified with the scalar 1; excluded from the basis.",
            },
        },
        "basis": {
            "even": even,
            "odd": odd,
            "ordering_convention": "PBW: kappa < [odd] < [even]  (K = 1 is excluded)",
        },
        "parity": parity,
        "generator_realization": {
            "description": "Standard form with PBW-ordered oscillator words",
            "ordering": ", ".join(
                ["a_1_p", "a_1_m"]
                + [f"b_{k}_{s}" for k in range(1, n + 1) for s in ("p", "m")]
            ),
            "realizations": realization_json(n),
        },
        "structure_constants": compute_structure_constants(n),
        "metadata": {
            "generated_by": "src/C_generators.py",
            "generation_date": datetime.date.today().isoformat(),
            "references": [
                "Frappat et al. (2000), Dictionary on Lie Algebras and Superalgebras",
                "docs/math/Cn1_definition.md",
            ],
        },
    }


def main():
    os.makedirs(DATA_DIR, exist_ok=True)
    for n in (1, 2, 3):
        data = schema1(n)
        path = os.path.join(DATA_DIR, f"C_{n}_structure.json")
        with open(path, "w") as f:
            json.dump(data, f, indent=1)
        nsc = len(data["structure_constants"])
        print(
            f"C({n + 1}) = osp(2|{2 * n}): dim {data['algebra']['dimension']['total']} "
            f"(even {data['algebra']['dimension']['even']}, odd {data['algebra']['dimension']['odd']}), "
            f"{nsc} nonzero structure-constant records -> {os.path.relpath(path)}"
        )


if __name__ == "__main__":
    main()
