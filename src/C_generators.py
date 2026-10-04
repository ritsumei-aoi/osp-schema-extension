"""
C_generators.py: Generator functions and structure constant builder for C(n+1) = osp(2|2n).
Generates Schema 1 JSON data for n=1, 2, 3 following docs/json_schema_specification.md.
"""

import json
import math
import os
from collections import defaultdict
from fractions import Fraction
from typing import Dict, List, Tuple, Any
import sympy as sp


def mult_fermion(f1: Tuple[int, int], f2: Tuple[int, int]) -> List[Tuple[int, Tuple[int, int]]]:
    """CAR multiplication for standard fermion pair a_1^+, a_1^-:
    {a_1^-, a_1^+} = 1, (a_1^+)^2 = (a_1^-)^2 = 0.
    Normal order: a_1^+ before a_1^-.
    Returns list of (coeff, (fp, fm)).
    """
    p1, m1 = f1
    p2, m2 = f2
    if m1 == 0:
        if p1 + p2 > 1:
            return []
        return [(1, (p1 + p2, m2))]
    if p2 == 0:
        if m1 + m2 > 1:
            return []
        return [(1, (p1, m1 + m2))]
    # m1 == 1 and p2 == 1: a_1^- a_1^+ = 1 - a_1^+ a_1^-
    res = [(1, (p1, m2))]
    if p1 == 0 and m2 == 0:
        res.append((-1, (1, 1)))
    return res


def mult_boson_mode(b1: Tuple[int, int], b2: Tuple[int, int]) -> List[Tuple[int, Tuple[int, int]]]:
    """CCR multiplication for single bosonic mode (b_k^+)^p1 (b_k^-)^m1 * (b_k^+)^p2 (b_k^-)^m2.
    [b_k^-, b_k^+] = 1.
    Normal order: b_k^+ before b_k^-.
    Returns list of (coeff, (bp, bm)).
    """
    p1, m1 = b1
    p2, m2 = b2
    res = []
    for l in range(min(m1, p2) + 1):
        c = math.comb(m1, l) * math.comb(p2, l) * math.factorial(l)
        res.append((c, (p1 + p2 - l, m1 + m2 - l)))
    return res


class Operator:
    """Normal-ordered operator in oscillator algebra."""
    def __init__(self, n: int, terms: Dict[Any, Fraction] = None):
        self.n = n
        self.terms = defaultdict(Fraction)
        if terms:
            for m, c in terms.items():
                fc = Fraction(c)
                if fc != 0:
                    self.terms[m] = fc

    def add(self, other: 'Operator') -> 'Operator':
        res = Operator(self.n, dict(self.terms))
        for m, c in other.terms.items():
            res.terms[m] += c
            if res.terms[m] == 0:
                del res.terms[m]
        return res

    def scale(self, s: Any) -> 'Operator':
        res = Operator(self.n)
        fs = Fraction(s)
        for m, c in self.terms.items():
            val = c * fs
            if val != 0:
                res.terms[m] = val
        return res

    def mul(self, other: 'Operator') -> 'Operator':
        res = Operator(self.n)
        for m1, c1 in self.terms.items():
            f1, b1_list = m1
            for m2, c2 in other.terms.items():
                f2, b2_list = m2
                f_prod = mult_fermion(f1, f2)
                if not f_prod:
                    continue
                b_prods = [mult_boson_mode(b1_list[k], b2_list[k]) for k in range(self.n)]

                def combine_modes(idx, current_c, current_b):
                    if idx == self.n:
                        for fc, fm in f_prod:
                            tot_c = c1 * c2 * current_c * fc
                            mon = (fm, tuple(current_b))
                            res.terms[mon] += tot_c
                            if res.terms[mon] == 0:
                                del res.terms[mon]
                        return
                    for c_k, b_k in b_prods[idx]:
                        combine_modes(idx + 1, current_c * c_k, current_b + [b_k])

                combine_modes(0, 1, [])
        return res


def get_basis_lists(n: int) -> Tuple[List[str], List[str]]:
    """Return even and odd basis generator names following handover/notation.md."""
    # Even basis
    cartan = [f"H_{i}" for i in range(1, n + 2)]
    long_p = [f"E_2del{k}_p" for k in range(1, n + 1)]
    short_pp = [f"E_del{i}_del{j}_pp" for i in range(1, n + 1) for j in range(i + 1, n + 1)]
    long_m = [f"E_2del{k}_m" for k in range(1, n + 1)]
    short_mm = [f"E_del{i}_del{j}_mm" for i in range(1, n + 1) for j in range(i + 1, n + 1)]
    short_pm = [f"E_del{i}_del{j}_pm" for i in range(1, n + 1) for j in range(i + 1, n + 1)]
    short_mp = [f"E_del{i}_del{j}_mp" for i in range(1, n + 1) for j in range(i + 1, n + 1)]
    even_basis = cartan + long_p + short_pp + long_m + short_mm + short_pm + short_mp

    # Odd basis
    odd_basis = []
    for k in range(1, n + 1):
        for s in ["pp", "pm", "mp", "mm"]:
            odd_basis.append(f"E_eps1_del{k}_{s}")

    return even_basis, odd_basis


def get_generator_operators(n: int) -> Tuple[Dict[str, Operator], Dict[str, int], Dict[str, Any]]:
    """Build Operator realizations, parity, and schema metadata for all generators."""
    even_basis, odd_basis = get_basis_lists(n)
    all_basis = odd_basis + even_basis

    gens = {}
    parities = {}
    realizations = {}

    m_a1 = ((1, 1), tuple((0, 0) for _ in range(n)))
    def m_bk(k):
        return ((0, 0), tuple((1, 1) if i == k else (0, 0) for i in range(n)))
    m_const = ((0, 0), tuple((0, 0) for _ in range(n)))

    # H_1 = a_1^+ a_1^- + b_1^+ b_1^-
    gens["H_1"] = Operator(n, {m_a1: 1, m_bk(0): 1})
    parities["H_1"] = 0
    realizations["H_1"] = {
        "standard_form": [
            {"words": ["a_1_p", "a_1_m"], "coeff": "1"},
            {"words": ["b_1_p", "b_1_m"], "coeff": "1"}
        ],
        "frappat_form": "a_1^+ a_1^- + b_1^+ b_1^-",
        "parity": 0
    }

    # H_k = b_{k-1}^+ b_{k-1}^- - b_k^+ b_k^- (for k=2..n)
    for k in range(2, n + 1):
        gens[f"H_{k}"] = Operator(n, {m_bk(k - 2): 1, m_bk(k - 1): -1})
        parities[f"H_{k}"] = 0
        realizations[f"H_{k}"] = {
            "standard_form": [
                {"words": [f"b_{k-1}_p", f"b_{k-1}_m"], "coeff": "1"},
                {"words": [f"b_{k}_p", f"b_{k}_m"], "coeff": "-1"}
            ],
            "frappat_form": f"b_{k-1}^+ b_{k-1}^- - b_{k}^+ b_{k}^-",
            "parity": 0
        }

    # H_{n+1} = -b_n^+ b_n^- - 1/2
    gens[f"H_{n+1}"] = Operator(n, {m_bk(n - 1): -1, m_const: Fraction(-1, 2)})
    parities[f"H_{n+1}"] = 0
    realizations[f"H_{n+1}"] = {
        "standard_form": [
            {"words": [f"b_{n}_p", f"b_{n}_m"], "coeff": "-1"},
            {"words": [], "coeff": "-1/2"}
        ],
        "frappat_form": f"-b_{n}^+ b_{n}^- - 1/2",
        "parity": 0,
        "note": "Terminal Cartan; includes constant term from symplectic trace"
    }

    # Long roots
    for k in range(1, n + 1):
        m_2p = ((0, 0), tuple((2, 0) if i == k - 1 else (0, 0) for i in range(n)))
        m_2m = ((0, 0), tuple((0, 2) if i == k - 1 else (0, 0) for i in range(n)))
        gens[f"E_2del{k}_p"] = Operator(n, {m_2p: 1})
        gens[f"E_2del{k}_m"] = Operator(n, {m_2m: 1})
        parities[f"E_2del{k}_p"] = 0
        parities[f"E_2del{k}_m"] = 0
        realizations[f"E_2del{k}_p"] = {
            "standard_form": [{"words": [f"b_{k}_p", f"b_{k}_p"], "coeff": "1"}],
            "frappat_form": f"(b_{k}^+)^2",
            "parity": 0
        }
        realizations[f"E_2del{k}_m"] = {
            "standard_form": [{"words": [f"b_{k}_m", f"b_{k}_m"], "coeff": "1"}],
            "frappat_form": f"(b_{k}^-)^2",
            "parity": 0
        }

    # Short roots
    for i in range(1, n + 1):
        for j in range(i + 1, n + 1):
            def m_short(pi, mi, pj, mj):
                b = []
                for k in range(n):
                    if k == i - 1:
                        b.append((pi, mi))
                    elif k == j - 1:
                        b.append((pj, mj))
                    else:
                        b.append((0, 0))
                return ((0, 0), tuple(b))

            gens[f"E_del{i}_del{j}_pp"] = Operator(n, {m_short(1, 0, 1, 0): 1})
            gens[f"E_del{i}_del{j}_mm"] = Operator(n, {m_short(0, 1, 0, 1): 1})
            gens[f"E_del{i}_del{j}_pm"] = Operator(n, {m_short(1, 0, 0, 1): 1})
            gens[f"E_del{i}_del{j}_mp"] = Operator(n, {m_short(0, 1, 1, 0): 1})

            for s in ["pp", "mm", "pm", "mp"]:
                name = f"E_del{i}_del{j}_{s}"
                parities[name] = 0

            realizations[f"E_del{i}_del{j}_pp"] = {
                "standard_form": [{"words": [f"b_{i}_p", f"b_{j}_p"], "coeff": "1"}],
                "frappat_form": f"b_{i}^+ b_{j}^+",
                "parity": 0
            }
            realizations[f"E_del{i}_del{j}_mm"] = {
                "standard_form": [{"words": [f"b_{i}_m", f"b_{j}_m"], "coeff": "1"}],
                "frappat_form": f"b_{i}^- b_{j}^-",
                "parity": 0
            }
            realizations[f"E_del{i}_del{j}_pm"] = {
                "standard_form": [{"words": [f"b_{i}_p", f"b_{j}_m"], "coeff": "1"}],
                "frappat_form": f"b_{i}^+ b_{j}^-",
                "parity": 0
            }
            realizations[f"E_del{i}_del{j}_mp"] = {
                "standard_form": [{"words": [f"b_{i}_m", f"b_{j}_p"], "coeff": "1"}],
                "frappat_form": f"b_{i}^- b_{j}^+",
                "parity": 0
            }

    # Odd roots
    for k in range(1, n + 1):
        def m_odd(fp, fm, bp, bm):
            b = tuple((bp, bm) if i == k - 1 else (0, 0) for i in range(n))
            return ((fp, fm), b)

        gens[f"E_eps1_del{k}_pp"] = Operator(n, {m_odd(1, 0, 1, 0): 1})
        gens[f"E_eps1_del{k}_pm"] = Operator(n, {m_odd(1, 0, 0, 1): 1})
        gens[f"E_eps1_del{k}_mp"] = Operator(n, {m_odd(0, 1, 1, 0): 1})
        gens[f"E_eps1_del{k}_mm"] = Operator(n, {m_odd(0, 1, 0, 1): 1})

        for s in ["pp", "pm", "mp", "mm"]:
            name = f"E_eps1_del{k}_{s}"
            parities[name] = 1

        realizations[f"E_eps1_del{k}_pp"] = {
            "standard_form": [{"words": ["a_1_p", f"b_{k}_p"], "coeff": "1"}],
            "frappat_form": f"a_1^+ b_{k}^+",
            "parity": 1
        }
        realizations[f"E_eps1_del{k}_pm"] = {
            "standard_form": [{"words": ["a_1_p", f"b_{k}_m"], "coeff": "1"}],
            "frappat_form": f"a_1^+ b_{k}^-",
            "parity": 1
        }
        realizations[f"E_eps1_del{k}_mp"] = {
            "standard_form": [{"words": ["a_1_m", f"b_{k}_p"], "coeff": "1"}],
            "frappat_form": f"a_1^- b_{k}^+",
            "parity": 1
        }
        realizations[f"E_eps1_del{k}_mm"] = {
            "standard_form": [{"words": ["a_1_m", f"b_{k}_m"], "coeff": "1"}],
            "frappat_form": f"a_1^- b_{k}^-",
            "parity": 1
        }

    return gens, parities, realizations


def compute_structure_constants(n: int) -> Tuple[List[Dict[str, str]], Dict[Tuple[str, str], Dict[str, Fraction]]]:
    """Compute all graded structure constants [X, Y} = sum c_Z Z."""
    even_basis, odd_basis = get_basis_lists(n)
    all_basis = odd_basis + even_basis
    gens, parities, _ = get_generator_operators(n)

    cartan = [f"H_{i}" for i in range(1, n + 2)]
    root_names = [name for name in all_basis if not name.startswith("H_")]

    m_a1 = ((1, 1), tuple((0, 0) for _ in range(n)))
    def m_bk(k):
        return ((0, 0), tuple((1, 1) if i == k else (0, 0) for i in range(n)))

    # Invert Cartan system
    M = sp.zeros(n + 1, n + 1)
    M[0, 0] = 1
    M[1, 0] = 1
    for k in range(2, n + 1):
        M[k - 1, k - 1] = 1
        M[k, k - 1] = -1
    M[n, n] = -1
    inv_M = M.inv()

    def decompose(op: Operator) -> Dict[str, Fraction]:
        rem = Operator(n, dict(op.terms))
        coeffs = {}
        # 1. Roots are unique single monomials
        for rname in root_names:
            rmon = list(gens[rname].terms.keys())[0]
            if rmon in rem.terms:
                c = rem.terms[rmon]
                coeffs[rname] = c
                rem = rem.add(gens[rname].scale(-c))
        # 2. Cartan diagonal terms
        if len(rem.terms) > 0:
            v = sp.zeros(n + 1, 1)
            v[0] = rem.terms.get(m_a1, Fraction(0))
            for k in range(n):
                v[k + 1] = rem.terms.get(m_bk(k), Fraction(0))
            c_cartan = inv_M * v
            for idx in range(n + 1):
                val = Fraction(int(c_cartan[idx, 0]))
                if val != 0:
                    coeffs[cartan[idx]] = val
                    rem = rem.add(gens[cartan[idx]].scale(-val))
            if len(rem.terms) > 0:
                raise ValueError(f"Decomposition failed for n={n}! Residual: {dict(rem.terms)}")
        return coeffs

    bracket_dict = {}
    structure_constants_list = []

    for X in all_basis:
        for Y in all_basis:
            pX, pY = parities[X], parities[Y]
            opX, opY = gens[X], gens[Y]
            if pX == 1 and pY == 1:
                # {X, Y} = XY + YX
                bracket_op = opX.mul(opY).add(opY.mul(opX))
            else:
                # [X, Y] = XY - YX
                bracket_op = opX.mul(opY).add(opY.mul(opX).scale(-1))
            res = decompose(bracket_op)
            bracket_dict[(X, Y)] = res
            for Z, coeff in res.items():
                if coeff != 0:
                    structure_constants_list.append({
                        "X": X,
                        "Y": Y,
                        "Z": Z,
                        "coeff": str(coeff) if coeff.denominator != 1 else str(coeff.numerator),
                        "sign_rule": "graded"
                    })

    return structure_constants_list, bracket_dict


def generate_schema1_json(n: int) -> Dict[str, Any]:
    """Generate complete Schema 1 dictionary for C(n+1) = osp(2|2n)."""
    even_basis, odd_basis = get_basis_lists(n)
    gens, parities, realizations = get_generator_operators(n)
    sc_list, _ = compute_structure_constants(n)

    boson_labels = []
    for k in range(1, n + 1):
        boson_labels.extend([f"b_{k}_p", f"b_{k}_m"])

    schema1_data = {
        "schema_version": "5.0",
        "algebra": {
            "family": "C",
            "m": 1,
            "n": n,
            "cartan_type": f"C({n+1})",
            "alternative_notation": {
                "osp": f"osp(2|{2*n})",
                "dimension_formula": "osp(2m|2n) with m=1, even = 2n^2 + n + 1, odd = 4n"
            },
            "dimension": {
                "total": 2 * n**2 + 5 * n + 1,
                "even": 2 * n**2 + n + 1,
                "odd": 4 * n
            }
        },
        "central_elements": {
            "kappa": {
                "label": "kappa",
                "parity": 1,
                "nilpotency": "kappa^2 = 0",
                "description": "Formal odd central element parametrizing inhomogeneous deformation"
            },
            "K": {
                "label": "K",
                "parity": 0,
                "value": 1,
                "description": "Even central identity element (identified with scalar 1)"
            }
        },
        "oscillator_generators": {
            "fermions": {
                "count": 2,
                "m": 1,
                "labels": ["a_1_p", "a_1_m"],
                "description": "Standard fermionic pair satisfying CAR: {a_1^-, a_1^+} = 1, (a_1^+)^2 = (a_1^-)^2 = 0"
            },
            "bosons": {
                "count": 2 * n,
                "n": n,
                "labels": boson_labels,
                "description": "Bosonic oscillators b_k^± with k=1,...,n satisfying CCR: [b_i^-, b_j^+] = δ_{ij}"
            }
        },
        "oscillator_relations": {
            "standard_fermion_anticommutators": {
                "description": "Canonical anticommutation relations (CAR) for standard fermionic pair",
                "relations": {
                    "conjugate_pair": "{a_1^-, a_1^+} = 1",
                    "nilpotency": "(a_1^+)^2 = 0, (a_1^-)^2 = 0"
                }
            },
            "bosonic_commutators": {
                "description": "Canonical commutation relations (CCR) for bosonic oscillators",
                "relations": {
                    "same_type": "[b_i^±, b_j^±] = 0 for all i, j",
                    "conjugate_pair": "[b_i^-, b_j^+] = δ_{ij}"
                }
            },
            "mixed_commutators": {
                "boson_fermion": "[b_i^±, a_1^±] = 0 (undeformed; deformed by -gb * kappa in Schema 2)"
            }
        },
        "basis": {
            "even": even_basis,
            "odd": odd_basis,
            "ordering_convention": "PBW: kappa < [odd: E_eps1_del{k}_pp/pm/mp/mm] < [even: H_k, E_2del{k}_p/m, E_del{i}_del{j}_pp/mm/pm/mp] (K = 1 is excluded)"
        },
        "parity": parities,
        "generator_realization": {
            "description": "Standard form with PBW ordering",
            "ordering": "a_1_p, a_1_m, " + ", ".join(boson_labels),
            "realizations": realizations
        },
        "structure_constants": sc_list,
        "metadata": {
            "generated_by": "src/C_generators.py",
            "generation_date": "2026-10-04",
            "references": [
                "Frappat et al. (2000), Dictionary on Lie Algebras and Superalgebras",
                "Bakalov and Sullivan (2017)"
            ]
        }
    }
    return schema1_data


def main():
    os.makedirs("data", exist_ok=True)
    for n in [1, 2, 3]:
        print(f"Generating C_{n}_structure.json for C({n+1}) = osp(2|{2*n})...")
        data = generate_schema1_json(n)
        filepath = f"data/C_{n}_structure.json"
        with open(filepath, "w") as f:
            json.dump(data, f, indent=2)
        print(f"  Saved {filepath}: {len(data['structure_constants'])} structure constant entries.")


if __name__ == "__main__":
    main()
