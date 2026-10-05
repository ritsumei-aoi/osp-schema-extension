"""
C(n+1) = osp(2|2n) structure constant generator.

Computes the Lie superalgebra structure constants using oscillator realizations,
following the v5.0 schema specification.
"""

import json
import sys
from fractions import Fraction
from datetime import date
from itertools import combinations


def build_basis(n):
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
    for sign in ["pp", "pm", "mp", "mm"]:
        for k in range(1, n + 1):
            odd.append(f"E_eps_del{k}_{sign}")

    return even, odd


def build_parity(even, odd):
    parity = {}
    for g in even:
        parity[g] = 0
    for g in odd:
        parity[g] = 1
    return parity


def build_realizations(n):
    realizations = {}
    realizations["H_1"] = {
        "standard_form": [
            {"words": ["a_1_p", "a_1_m"], "coeff": "1"},
            {"words": ["b_1_p", "b_1_m"], "coeff": "1"},
        ],
        "frappat_form": "a_1^+ a_1^- + b_1^+ b_1^-",
        "parity": 0,
    }
    for k in range(2, n + 1):
        realizations[f"H_{k}"] = {
            "standard_form": [
                {"words": [f"b_{k-1}_p", f"b_{k-1}_m"], "coeff": "1"},
                {"words": [f"b_{k}_p", f"b_{k}_m"], "coeff": "-1"},
            ],
            "frappat_form": f"b_{k-1}^+ b_{k-1}^- - b_{k}^+ b_{k}^-",
            "parity": 0,
        }
    realizations[f"H_{n+1}"] = {
        "standard_form": [
            {"words": [f"b_{n}_p", f"b_{n}_m"], "coeff": "-1"},
            {"words": [], "coeff": "-1/2"},
        ],
        "frappat_form": f"-b_{n}^+ b_{n}^- - 1/2",
        "parity": 0,
    }
    for k in range(1, n + 1):
        realizations[f"E_2del{k}_p"] = {
            "standard_form": [{"words": [f"b_{k}_p", f"b_{k}_p"], "coeff": "1/2"}],
            "frappat_form": f"(1/2)(b_{k}^+)^2",
            "parity": 0,
        }
        realizations[f"E_2del{k}_m"] = {
            "standard_form": [{"words": [f"b_{k}_m", f"b_{k}_m"], "coeff": "1/2"}],
            "frappat_form": f"(1/2)(b_{k}^-)^2",
            "parity": 0,
        }
    for i, j in combinations(range(1, n + 1), 2):
        realizations[f"E_del{i}_del{j}_pp"] = {
            "standard_form": [{"words": [f"b_{i}_p", f"b_{j}_p"], "coeff": "1"}],
            "frappat_form": f"b_{i}^+ b_{j}^+",
            "parity": 0,
        }
        realizations[f"E_del{i}_del{j}_mm"] = {
            "standard_form": [{"words": [f"b_{i}_m", f"b_{j}_m"], "coeff": "1"}],
            "frappat_form": f"b_{i}^- b_{j}^-",
            "parity": 0,
        }
        realizations[f"E_del{i}_del{j}_pm"] = {
            "standard_form": [{"words": [f"b_{i}_p", f"b_{j}_m"], "coeff": "1"}],
            "frappat_form": f"b_{i}^+ b_{j}^-",
            "parity": 0,
        }
        realizations[f"E_del{i}_del{j}_mp"] = {
            "standard_form": [{"words": [f"b_{i}_m", f"b_{j}_p"], "coeff": "1"}],
            "frappat_form": f"b_{i}^- b_{j}^+",
            "parity": 0,
        }
    for k in range(1, n + 1):
        realizations[f"E_eps_del{k}_pp"] = {
            "standard_form": [{"words": ["a_1_p", f"b_{k}_p"], "coeff": "1"}],
            "frappat_form": f"a_1^+ b_{k}^+",
            "parity": 1,
        }
        realizations[f"E_eps_del{k}_pm"] = {
            "standard_form": [{"words": ["a_1_p", f"b_{k}_m"], "coeff": "1"}],
            "frappat_form": f"a_1^+ b_{k}^-",
            "parity": 1,
        }
        realizations[f"E_eps_del{k}_mp"] = {
            "standard_form": [{"words": ["a_1_m", f"b_{k}_p"], "coeff": "1"}],
            "frappat_form": f"a_1^- b_{k}^+",
            "parity": 1,
        }
        realizations[f"E_eps_del{k}_mm"] = {
            "standard_form": [{"words": ["a_1_m", f"b_{k}_m"], "coeff": "1"}],
            "frappat_form": f"a_1^- b_{k}^-",
            "parity": 1,
        }
    return realizations


class OscillatorAlgebra:
    """Compute graded brackets using oscillator realizations for C(n+1)."""

    def __init__(self, n):
        self.n = n

    def _parse_word(self, word):
        if word.startswith("a_1_"):
            return ("f", 1, "p" if word.endswith("_p") else "m")
        elif word.startswith("b_"):
            parts = word.split("_")
            return ("b", int(parts[1]), parts[2])
        raise ValueError(f"Unknown oscillator: {word}")

    def _osc_parity(self, osc):
        return 1 if osc[0] == "f" else 0

    def compute_bracket(self, real_X, real_Y, parity_X, parity_Y):
        """
        Compute the graded bracket [X, Y} using oscillator realizations.
        X and Y are given as lists of (coeff, word_list) terms.
        Returns a dictionary mapping oscillator monomial tuples to Fraction coefficients.
        """
        result = {}
        for cx, wx in real_X:
            for cy, wy in real_Y:
                self._bracket_monomials(cx, wx, cy, wy, parity_X, parity_Y, result)
        return {k: v for k, v in result.items() if v != 0}

    def _bracket_monomials(self, cx, wx, cy, wy, px, py, result):
        """Compute [cx*wx, cy*wy} and add to result.
        Graded bracket: [X,Y} = XY - (-1)^{p(X)p(Y)} YX."""
        coeff = cx * cy
        self._compute_product(coeff, wx, wy, result, Fraction(1))
        second_sign = -Fraction((-1) ** (px * py))
        self._compute_product(coeff * second_sign, wy, wx, result, Fraction(1))

    def _compute_product(self, coeff, left, right, result, overall_sign):
        """Normal-order the product left*right and add to result."""
        if coeff == 0:
            return
        product = list(left) + list(right)
        self._normal_order(coeff * overall_sign, product, result)

    def _normal_order(self, coeff, oscs, result):
        """Put oscillators in normal order: a_1_p, a_1_m, b_1_p, b_1_m, ..."""
        if coeff == 0:
            return
        oscs = list(oscs)
        changed = True
        while changed:
            changed = False
            for i in range(len(oscs) - 1):
                o1 = self._parse_word(oscs[i])
                o2 = self._parse_word(oscs[i + 1])
                if self._should_swap(o1, o2):
                    p1 = self._osc_parity(o1)
                    p2 = self._osc_parity(o2)
                    contract = self._contraction(o1, o2)
                    if contract is not None and contract != 0:
                        remaining = oscs[:i] + oscs[i + 2:]
                        sign = Fraction(-1) ** (p1 * p2)
                        self._normal_order(coeff * contract, remaining, result)
                    swap_sign = Fraction(-1) ** (p1 * p2)
                    oscs[i], oscs[i + 1] = oscs[i + 1], oscs[i]
                    coeff = coeff * swap_sign
                    changed = True
                    break
        key = tuple(oscs)
        result[key] = result.get(key, Fraction(0)) + coeff

    def _osc_order(self, o):
        """Return sort key for normal ordering."""
        if o[0] == "f":
            return (0, o[1], 0 if o[2] == "p" else 1)
        else:
            return (1, o[1], 0 if o[2] == "p" else 1)

    def _should_swap(self, o1, o2):
        return self._osc_order(o1) > self._osc_order(o2)

    def _contraction(self, o1, o2):
        """Return contraction value when swapping o1, o2 (if they form a pair)."""
        if o1[0] == "f" and o2[0] == "f":
            if o1[1] == o2[1] and o1[2] != o2[2]:
                if o1[2] == "m" and o2[2] == "p":
                    return Fraction(1)
                elif o1[2] == "p" and o2[2] == "m":
                    return Fraction(1)
            return None
        if o1[0] == "b" and o2[0] == "b":
            if o1[1] == o2[1] and o1[2] != o2[2]:
                if o1[2] == "m" and o2[2] == "p":
                    return Fraction(1)
                elif o1[2] == "p" and o2[2] == "m":
                    return Fraction(-1)
            return None
        return None


def realization_to_terms(real):
    terms = []
    for entry in real["standard_form"]:
        coeff = Fraction(entry["coeff"])
        words = entry["words"]
        terms.append((coeff, words))
    return terms


def build_decomposition_map(all_generators, realizations):
    """Build a map from generators to their monomial expansions,
    and the inverse map for decomposing bracket results."""
    all_monomials = set()
    gen_vectors = {}
    for gen in all_generators:
        real = realizations[gen]
        vec = {}
        for entry in real["standard_form"]:
            key = tuple(entry["words"])
            vec[key] = Fraction(entry["coeff"])
            all_monomials.add(key)
        gen_vectors[gen] = vec
    all_monomials.add(())
    return gen_vectors, sorted(all_monomials, key=lambda x: (len(x), x))


def decompose_result(bracket_result, all_generators, gen_vectors, monomial_list):
    """Decompose a bracket result (dict of monomial->coeff) as a linear
    combination of generators by solving the linear system."""
    from fractions import Fraction

    mono_idx = {m: i for i, m in enumerate(monomial_list)}
    n_mono = len(monomial_list)
    n_gen = len(all_generators)

    target = [Fraction(0)] * n_mono
    for mono, coeff in bracket_result.items():
        if mono in mono_idx:
            target[mono_idx[mono]] += coeff
        else:
            mono_idx[mono] = len(target)
            target.append(coeff)
            monomial_list.append(mono)
            n_mono += 1

    coeffs = {}
    remaining = dict(bracket_result)

    for gen in all_generators:
        vec = gen_vectors[gen]
        if not vec:
            continue
        ref_mono = next(iter(vec))
        ref_coeff = vec[ref_mono]
        if ref_mono not in remaining or remaining[ref_mono] == 0:
            continue

        candidate_c = remaining[ref_mono] / ref_coeff

        valid = True
        for mono, gc in vec.items():
            expected = candidate_c * gc
            actual = remaining.get(mono, Fraction(0))
            if actual != expected:
                valid = False
                break

        if valid:
            coeffs[gen] = candidate_c
            for mono, gc in vec.items():
                remaining[mono] = remaining.get(mono, Fraction(0)) - candidate_c * gc
                if remaining[mono] == 0:
                    del remaining[mono]

    remaining = {k: v for k, v in remaining.items() if v != 0}

    if remaining:
        unsolved_gens = list(all_generators)
        for g in coeffs:
            unsolved_gens.remove(g)
        if unsolved_gens and remaining:
            result2 = _solve_linear(remaining, unsolved_gens, gen_vectors)
            for g, c in result2.items():
                coeffs[g] = coeffs.get(g, Fraction(0)) + c
                for mono, gc in gen_vectors[g].items():
                    remaining[mono] = remaining.get(mono, Fraction(0)) - c * gc
                    if remaining.get(mono, Fraction(1)) == 0:
                        remaining.pop(mono, None)

    return coeffs


def _solve_linear(remaining, generators, gen_vectors):
    """Solve for coefficients using Gaussian elimination over Fractions."""
    all_monos = set()
    for mono in remaining:
        all_monos.add(mono)
    for gen in generators:
        for mono in gen_vectors[gen]:
            all_monos.add(mono)
    mono_list = sorted(all_monos, key=lambda x: (len(x), x))
    mono_idx = {m: i for i, m in enumerate(mono_list)}

    n_mono = len(mono_list)
    n_gen = len(generators)

    matrix = []
    for i, mono in enumerate(mono_list):
        row = []
        for j, gen in enumerate(generators):
            row.append(gen_vectors[gen].get(mono, Fraction(0)))
        row.append(remaining.get(mono, Fraction(0)))
        matrix.append(row)

    for col in range(n_gen):
        pivot = None
        for row in range(col, n_mono):
            if matrix[row][col] != 0:
                pivot = row
                break
        if pivot is None:
            continue
        matrix[col], matrix[pivot] = matrix[pivot], matrix[col]
        pivot_val = matrix[col][col]
        for row in range(n_mono):
            if row == col:
                continue
            if matrix[row][col] != 0:
                factor = matrix[row][col] / pivot_val
                for c in range(n_gen + 1):
                    matrix[row][c] -= factor * matrix[col][c]

    result = {}
    for col in range(n_gen):
        if col < n_mono and matrix[col][col] != 0:
            val = matrix[col][n_gen] / matrix[col][col]
            if val != 0:
                result[generators[col]] = val
    return result


def compute_structure_constants(n):
    even, odd = build_basis(n)
    all_gens = odd + even
    parity = build_parity(even, odd)
    realizations = build_realizations(n)
    alg = OscillatorAlgebra(n)
    gen_vectors, monomial_list = build_decomposition_map(all_gens, realizations)

    structure_constants = []

    for i, X in enumerate(all_gens):
        for j, Y in enumerate(all_gens):
            if j <= i:
                continue
            real_X = realization_to_terms(realizations[X])
            real_Y = realization_to_terms(realizations[Y])
            bracket = alg.compute_bracket(real_X, real_Y, parity[X], parity[Y])

            if not bracket:
                continue

            coeffs = decompose_result(bracket, all_gens, gen_vectors, monomial_list)

            for Z, coeff in coeffs.items():
                if coeff != 0:
                    structure_constants.append({
                        "X": X,
                        "Y": Y,
                        "Z": Z,
                        "coeff": str(coeff),
                        "sign_rule": "graded",
                    })

    return structure_constants


def generate_schema1(n):
    even, odd = build_basis(n)
    parity = build_parity(even, odd)
    realizations = build_realizations(n)
    sc = compute_structure_constants(n)

    n_even = 2 * n * n + n + 1
    n_odd = 4 * n
    n_total = n_even + n_odd

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
                "dimension_formula": "osp(2m|2n) with m=1",
            },
            "dimension": {"total": n_total, "even": n_even, "odd": n_odd},
        },
        "oscillator_generators": {
            "fermions": {
                "count": 2,
                "m": 1,
                "labels": ["a_1_p", "a_1_m"],
                "description": "Standard fermionic pair a_1^± with CAR relations",
            },
            "bosons": {
                "count": 2 * n,
                "n": n,
                "labels": boson_labels,
                "description": f"Bosonic oscillators b_i^± with i=1,...,{n}",
            },
        },
        "oscillator_relations": {
            "standard_fermion_anticommutators": {
                "description": "Canonical anticommutation relations for standard fermionic pair",
                "relations": {
                    "anticommutator": "{a_1^-, a_1^+} = 1",
                    "self_anticommutators": "{a_1^+, a_1^+} = 0, {a_1^-, a_1^-} = 0",
                },
            },
            "bosonic_commutators": {
                "description": "Canonical commutation relations for bosonic oscillators",
                "relations": {
                    "same_type": "[b_i^±, b_j^±] = 0 for all i, j",
                    "conjugate_pair": "[b_i^-, b_j^+] = δ_{ij}",
                },
            },
            "mixed_commutators": {"boson_fermion": "[b_i^±, a_1^±] = 0"},
        },
        "central_elements": {
            "K": {
                "parity": 0,
                "description": "Central identity element (= 1 in all applications)",
                "value": 1,
            },
            "kappa": {
                "parity": 1,
                "description": "Nilpotent odd central element, kappa^2 = 0",
                "nilpotent": True,
            },
        },
        "basis": {
            "even": even,
            "odd": odd,
            "ordering_convention": "PBW: κ < [odd] < [even]  (K = 1 is excluded)",
        },
        "parity": parity,
        "generator_realization": {
            "description": "Standard form with PBW ordering",
            "ordering": ", ".join(["a_1_p", "a_1_m"] + boson_labels),
            "realizations": realizations,
        },
        "structure_constants": sc,
        "metadata": {
            "generated_by": "C_generators.py",
            "generation_date": str(date.today()),
            "references": [
                "Frappat et al. (2000), Dictionary on Lie Algebras and Superalgebras",
                "Bakalov and Sullivan (2017)",
            ],
        },
    }
    return schema


def main():
    for n in [1, 2, 3]:
        print(f"Generating C({n+1}) = osp(2|{2*n}) structure [n={n}]...")
        schema = generate_schema1(n)
        filename = f"data/C_{n}_structure.json"
        with open(filename, "w") as f:
            json.dump(schema, f, indent=2)
        n_sc = len(schema["structure_constants"])
        n_even = len(schema["basis"]["even"])
        n_odd = len(schema["basis"]["odd"])
        print(f"  -> {filename}: {n_even} even + {n_odd} odd generators, {n_sc} structure constants")
    print("Done.")


if __name__ == "__main__":
    main()
