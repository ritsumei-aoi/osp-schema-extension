"""
C(n+1) = osp(2|2n) Schema 1 structure constant generator.
Generates Schema 1 JSON definitions following docs/json_schema_specification.md
and handover/notation.md.
"""

from collections import defaultdict
from fractions import Fraction
import json
import math
from pathlib import Path
from typing import Any, Dict, List, Tuple
import sympy as sp


class OscillatorPoly:
    """Represents a polynomial in the oscillator algebra of C(n+1).

    Terms are stored as:
      (f_key, b_tuple) -> Fraction
    where:
      f_key in {'1', 'a+', 'a-', 'a+a-'}
      b_tuple is a tuple of 2n non-negative integers:
        (p_1, m_1, p_2, m_2, ..., p_n, m_n)
        corresponding to (b_1^+)^p_1 (b_1^-)^m_1 ...
    """

    def __init__(self, terms: Dict[Tuple[str, Tuple[int, ...]], Fraction] = None):
        self.terms: Dict[Tuple[str, Tuple[int, ...]], Fraction] = defaultdict(Fraction)
        if terms:
            for k, v in terms.items():
                if v != 0:
                    self.terms[k] = Fraction(v)

    def __add__(self, other: "OscillatorPoly") -> "OscillatorPoly":
        res = OscillatorPoly(self.terms)
        for k, v in other.terms.items():
            res.terms[k] += v
            if res.terms[k] == 0:
                del res.terms[k]
        return res

    def __sub__(self, other: "OscillatorPoly") -> "OscillatorPoly":
        res = OscillatorPoly(self.terms)
        for k, v in other.terms.items():
            res.terms[k] -= v
            if res.terms[k] == 0:
                del res.terms[k]
        return res

    def scale(self, c: Any) -> "OscillatorPoly":
        res = OscillatorPoly()
        for k, v in self.terms.items():
            res.terms[k] = v * Fraction(c)
            if res.terms[k] == 0:
                del res.terms[k]
        return res

    def __mul__(self, other: "OscillatorPoly") -> "OscillatorPoly":
        res = OscillatorPoly()
        for k1, v1 in self.terms.items():
            for k2, v2 in other.terms.items():
                prod = _multiply_monomials(k1, k2)
                for k, v in prod.terms.items():
                    res.terms[k] += v1 * v2 * v
                    if res.terms[k] == 0:
                        del res.terms[k]
        return res

    def is_zero(self) -> bool:
        return len(self.terms) == 0


def _fermion_mult(f1: str, f2: str) -> Dict[str, Fraction]:
    if f1 == "1":
        return {f2: Fraction(1)}
    if f2 == "1":
        return {f1: Fraction(1)}
    if f1 == "a+":
        if f2 == "a+":
            return {}
        elif f2 == "a-":
            return {"a+a-": Fraction(1)}
        elif f2 == "a+a-":
            return {}
    elif f1 == "a-":
        if f2 == "a+":
            return {"1": Fraction(1), "a+a-": Fraction(-1)}
        elif f2 == "a-":
            return {}
        elif f2 == "a+a-":
            return {"a-": Fraction(1)}
    elif f1 == "a+a-":
        if f2 == "a+":
            return {"a+": Fraction(1)}
        elif f2 == "a-":
            return {}
        elif f2 == "a+a-":
            return {"a+a-": Fraction(1)}
    raise ValueError(f"Unknown fermionic pair ({f1}, {f2})")


def _reduce_single_boson(m1: int, p2: int) -> Dict[Tuple[int, int], Fraction]:
    res = {}
    for k in range(min(m1, p2) + 1):
        coeff = math.factorial(k) * math.comb(m1, k) * math.comb(p2, k)
        res[(p2 - k, m1 - k)] = Fraction(coeff)
    return res


def _multiply_monomials(
    k1: Tuple[str, Tuple[int, ...]], k2: Tuple[str, Tuple[int, ...]]
) -> OscillatorPoly:
    f1, b1 = k1
    f2, b2 = k2
    f_res = _fermion_mult(f1, f2)
    if not f_res:
        return OscillatorPoly()

    n = len(b1) // 2
    mode_results = []
    for k in range(n):
        pk1, mk1 = b1[2 * k], b1[2 * k + 1]
        pk2, mk2 = b2[2 * k], b2[2 * k + 1]
        mid = _reduce_single_boson(mk1, pk2)
        mode_k = {}
        for (pm, mm), coeff in mid.items():
            mode_k[(pk1 + pm, mk2 + mm)] = coeff
        mode_results.append(mode_k)

    current = {(): Fraction(1)}
    for k in range(n):
        nxt = {}
        for cur_b, cur_coeff in current.items():
            for (p, m), coeff in mode_results[k].items():
                nxt[cur_b + (p, m)] = cur_coeff * coeff
        current = nxt

    res = OscillatorPoly()
    for f, f_coeff in f_res.items():
        for b, b_coeff in current.items():
            res.terms[(f, b)] += f_coeff * b_coeff
            if res.terms[(f, b)] == 0:
                del res.terms[(f, b)]
    return res


def graded_bracket(
    X: OscillatorPoly, Y: OscillatorPoly, px: int, py: int
) -> OscillatorPoly:
    sign = -1 if (px * py % 2 == 1) else 1
    return (X * Y) - (Y * X).scale(sign)


def get_basis(n: int) -> Tuple[List[str], List[str]]:
    """Returns (even_basis, odd_basis) in Option 1 PBW order."""
    cartan = [f"H_{k}" for k in range(1, n + 2)]
    long_p = [f"E_2del{k}_p" for k in range(1, n + 1)]
    short_pp = [
        f"E_del{i}_del{j}_pp"
        for i in range(1, n + 1)
        for j in range(i + 1, n + 1)
    ]
    long_m = [f"E_2del{k}_m" for k in range(1, n + 1)]
    short_mm = [
        f"E_del{i}_del{j}_mm"
        for i in range(1, n + 1)
        for j in range(i + 1, n + 1)
    ]
    short_pm = [
        f"E_del{i}_del{j}_pm"
        for i in range(1, n + 1)
        for j in range(i + 1, n + 1)
    ]
    short_mp = [
        f"E_del{i}_del{j}_mp"
        for i in range(1, n + 1)
        for j in range(i + 1, n + 1)
    ]
    even_basis = (
        cartan + long_p + short_pp + long_m + short_mm + short_pm + short_mp
    )

    odd_pp = [f"E_eps1_del{k}_pp" for k in range(1, n + 1)]
    odd_pm = [f"E_eps1_del{k}_pm" for k in range(1, n + 1)]
    odd_mp = [f"E_eps1_del{k}_mp" for k in range(1, n + 1)]
    odd_mm = [f"E_eps1_del{k}_mm" for k in range(1, n + 1)]
    odd_basis = odd_pp + odd_pm + odd_mp + odd_mm

    return even_basis, odd_basis


def get_generator_polys_and_realizations(
    n: int,
) -> Tuple[Dict[str, OscillatorPoly], Dict[str, int], Dict[str, Any]]:
    even_basis, odd_basis = get_basis(n)
    gens = {}
    parities = {}
    realizations = {}

    zero_b = tuple([0] * (2 * n))

    def b_pair(m1, pm1, m2, pm2):
        lst = [0] * (2 * n)
        idx1 = 2 * (m1 - 1) + (0 if pm1 == "p" else 1)
        idx2 = 2 * (m2 - 1) + (0 if pm2 == "p" else 1)
        lst[idx1] += 1
        lst[idx2] += 1
        return tuple(lst)

    def b_unit(m1, pm1):
        lst = [0] * (2 * n)
        idx1 = 2 * (m1 - 1) + (0 if pm1 == "p" else 1)
        lst[idx1] += 1
        return tuple(lst)

    # H_1
    gens["H_1"] = OscillatorPoly(
        {("a+a-", zero_b): Fraction(1), ("1", b_pair(1, "p", 1, "m")): Fraction(1)}
    )
    parities["H_1"] = 0
    realizations["H_1"] = {
        "standard_form": [
            {"words": ["a_1_p", "a_1_m"], "coeff": "1"},
            {"words": ["b_1_p", "b_1_m"], "coeff": "1"},
        ],
        "frappat_form": "a_1^+ a_1^- + b_1^+ b_1^-",
        "parity": 0,
    }

    # H_k (2 <= k <= n)
    for k in range(2, n + 1):
        name = f"H_{k}"
        gens[name] = OscillatorPoly(
            {
                ("1", b_pair(k - 1, "p", k - 1, "m")): Fraction(1),
                ("1", b_pair(k, "p", k, "m")): Fraction(-1),
            }
        )
        parities[name] = 0
        realizations[name] = {
            "standard_form": [
                {"words": [f"b_{k-1}_p", f"b_{k-1}_m"], "coeff": "1"},
                {"words": [f"b_{k}_p", f"b_{k}_m"], "coeff": "-1"},
            ],
            "frappat_form": f"b_{k-1}^+ b_{k-1}^- - b_{k}^+ b_{k}^-",
            "parity": 0,
        }

    # H_{n+1}
    h_end = f"H_{n+1}"
    gens[h_end] = OscillatorPoly(
        {
            ("1", b_pair(n, "p", n, "m")): Fraction(-1),
            ("1", zero_b): Fraction(-1, 2),
        }
    )
    parities[h_end] = 0
    realizations[h_end] = {
        "standard_form": [
            {"words": [f"b_{n}_p", f"b_{n}_m"], "coeff": "-1"},
            {"words": [], "coeff": "-1/2"},
        ],
        "frappat_form": f"-b_{n}^+ b_{n}^- - 1/2",
        "parity": 0,
    }

    # Long roots
    for k in range(1, n + 1):
        name_p = f"E_2del{k}_p"
        gens[name_p] = OscillatorPoly({("1", b_pair(k, "p", k, "p")): Fraction(1)})
        parities[name_p] = 0
        realizations[name_p] = {
            "standard_form": [{"words": [f"b_{k}_p", f"b_{k}_p"], "coeff": "1"}],
            "frappat_form": f"(b_{k}^+)^2",
            "parity": 0,
        }

        name_m = f"E_2del{k}_m"
        gens[name_m] = OscillatorPoly({("1", b_pair(k, "m", k, "m")): Fraction(1)})
        parities[name_m] = 0
        realizations[name_m] = {
            "standard_form": [{"words": [f"b_{k}_m", f"b_{k}_m"], "coeff": "1"}],
            "frappat_form": f"(b_{k}^-)^2",
            "parity": 0,
        }

    # Short roots
    for i in range(1, n + 1):
        for j in range(i + 1, n + 1):
            n_pp = f"E_del{i}_del{j}_pp"
            gens[n_pp] = OscillatorPoly({("1", b_pair(i, "p", j, "p")): Fraction(1)})
            parities[n_pp] = 0
            realizations[n_pp] = {
                "standard_form": [{"words": [f"b_{i}_p", f"b_{j}_p"], "coeff": "1"}],
                "frappat_form": f"b_{i}^+ b_{j}^+",
                "parity": 0,
            }

            n_mm = f"E_del{i}_del{j}_mm"
            gens[n_mm] = OscillatorPoly({("1", b_pair(i, "m", j, "m")): Fraction(1)})
            parities[n_mm] = 0
            realizations[n_mm] = {
                "standard_form": [{"words": [f"b_{i}_m", f"b_{j}_m"], "coeff": "1"}],
                "frappat_form": f"b_{i}^- b_{j}^-",
                "parity": 0,
            }

            n_pm = f"E_del{i}_del{j}_pm"
            gens[n_pm] = OscillatorPoly({("1", b_pair(i, "p", j, "m")): Fraction(1)})
            parities[n_pm] = 0
            realizations[n_pm] = {
                "standard_form": [{"words": [f"b_{i}_p", f"b_{j}_m"], "coeff": "1"}],
                "frappat_form": f"b_{i}^+ b_{j}^-",
                "parity": 0,
            }

            n_mp = f"E_del{i}_del{j}_mp"
            gens[n_mp] = OscillatorPoly({("1", b_pair(i, "m", j, "p")): Fraction(1)})
            parities[n_mp] = 0
            realizations[n_mp] = {
                "standard_form": [{"words": [f"b_{i}_m", f"b_{j}_p"], "coeff": "1"}],
                "frappat_form": f"b_{i}^- b_{j}^+",
                "parity": 0,
            }

    # Odd roots
    for k in range(1, n + 1):
        o_pp = f"E_eps1_del{k}_pp"
        gens[o_pp] = OscillatorPoly({("a+", b_unit(k, "p")): Fraction(1)})
        parities[o_pp] = 1
        realizations[o_pp] = {
            "standard_form": [{"words": ["a_1_p", f"b_{k}_p"], "coeff": "1"}],
            "frappat_form": f"a_1^+ b_{k}^+",
            "parity": 1,
        }

        o_pm = f"E_eps1_del{k}_pm"
        gens[o_pm] = OscillatorPoly({("a+", b_unit(k, "m")): Fraction(1)})
        parities[o_pm] = 1
        realizations[o_pm] = {
            "standard_form": [{"words": ["a_1_p", f"b_{k}_m"], "coeff": "1"}],
            "frappat_form": f"a_1^+ b_{k}^-",
            "parity": 1,
        }

        o_mp = f"E_eps1_del{k}_mp"
        gens[o_mp] = OscillatorPoly({("a-", b_unit(k, "p")): Fraction(1)})
        parities[o_mp] = 1
        realizations[o_mp] = {
            "standard_form": [{"words": ["a_1_m", f"b_{k}_p"], "coeff": "1"}],
            "frappat_form": f"a_1^- b_{k}^+",
            "parity": 1,
        }

        o_mm = f"E_eps1_del{k}_mm"
        gens[o_mm] = OscillatorPoly({("a-", b_unit(k, "m")): Fraction(1)})
        parities[o_mm] = 1
        realizations[o_mm] = {
            "standard_form": [{"words": ["a_1_m", f"b_{k}_m"], "coeff": "1"}],
            "frappat_form": f"a_1^- b_{k}^-",
            "parity": 1,
        }

    return gens, parities, realizations


def compute_structure_constants(n: int) -> Tuple[List[Dict[str, str]], List[str]]:
    """Computes all non-zero graded structure constants for C(n+1)."""
    even_basis, odd_basis = get_basis(n)
    full_basis = odd_basis + even_basis  # PBW order: odd < even
    gens, parities, _ = get_generator_polys_and_realizations(n)

    all_monomials = sorted(
        list(set(m for g in gens.values() for m in g.terms.keys()))
    )
    M = sp.zeros(len(all_monomials), len(full_basis))
    for j, bname in enumerate(full_basis):
        g = gens[bname]
        for i, mkey in enumerate(all_monomials):
            if mkey in g.terms:
                M[i, j] = sp.Rational(
                    g.terms[mkey].numerator, g.terms[mkey].denominator
                )

    structure_constants = []
    for x_name in full_basis:
        for y_name in full_basis:
            px = parities[x_name]
            py = parities[y_name]
            br = graded_bracket(gens[x_name], gens[y_name], px, py)
            if br.is_zero():
                continue

            v = sp.zeros(len(all_monomials), 1)
            for mkey, coeff in br.terms.items():
                v[all_monomials.index(mkey), 0] = sp.Rational(
                    coeff.numerator, coeff.denominator
                )

            sol, _ = M.gauss_jordan_solve(v)
            if not (M * sol - v).is_zero_matrix:
                raise ValueError(
                    f"Bracket [{x_name}, {y_name}}} cannot be expressed in basis"
                )

            for k, z_name in enumerate(full_basis):
                c = sol[k, 0]
                if c != 0:
                    c_str = str(c)
                    structure_constants.append(
                        {
                            "X": x_name,
                            "Y": y_name,
                            "Z": z_name,
                            "coeff": c_str,
                            "sign_rule": "graded",
                        }
                    )

    return structure_constants, full_basis


def build_schema1_json(n: int) -> Dict[str, Any]:
    """Builds the complete Schema 1 dictionary for C(n+1)."""
    even_basis, odd_basis = get_basis(n)
    _, parities, realizations = get_generator_polys_and_realizations(n)
    structure_constants, full_basis = compute_structure_constants(n)

    boson_labels = []
    for k in range(1, n + 1):
        boson_labels.extend([f"b_{k}_p", f"b_{k}_m"])

    dim_even = 2 * n * n + n + 1
    dim_odd = 4 * n
    dim_total = 2 * n * n + 5 * n + 1

    ordering_desc = (
        "a_1_p, a_1_m, " + ", ".join(boson_labels)
    )

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
            "dimension": {
                "total": dim_total,
                "even": dim_even,
                "odd": dim_odd,
            },
            "dimension_formulas": {
                "even": "2n^2 + n + 1",
                "odd": "4n",
                "total": "2n^2 + 5n + 1",
            },
        },
        "oscillator_generators": {
            "fermions": {
                "count": 2,
                "m": 1,
                "labels": ["a_1_p", "a_1_m"],
                "description": "Standard fermionic pair a_1^± with m=1 (CAR)",
            },
            "bosons": {
                "count": 2 * n,
                "n": n,
                "labels": boson_labels,
                "description": f"Bosonic oscillators b_k^± with k=1,...,{n} (CCR)",
            },
        },
        "oscillator_relations": {
            "fermionic_anticommutators": {
                "description": "Canonical anticommutation relations (CAR) for standard fermionic pair",
                "relations": {
                    "conjugate_pair": "{a_1^-, a_1^+} = 1",
                    "nilpotency": "(a_1^±)^2 = 0",
                },
            },
            "bosonic_commutators": {
                "description": "Canonical commutation relations (CCR) for bosonic oscillators",
                "relations": {
                    "same_type": "[b_i^±, b_j^±] = 0 for all i, j",
                    "conjugate_pair": "[b_i^-, b_j^+] = δ_{ij}",
                },
            },
            "mixed_commutators": {
                "boson_fermion": "[b_k^±, a_1^±] = 0 (undeformed)"
            },
        },
        "central_elements": {
            "kappa": {
                "label": "kappa",
                "parity": 1,
                "nilpotency": "kappa^2 = 0",
                "description": "Odd central element parametrizing inhomogeneous deformation",
            },
            "K": {
                "label": "K",
                "parity": 0,
                "value": 1,
                "description": "Even central element (identity scalar unit K = 1)",
            },
        },
        "basis": {
            "even": even_basis,
            "odd": odd_basis,
            "ordering_convention": "PBW: kappa < [odd: Delta_{1}^+ (pp, pm) < Delta_{1}^- (mp, mm)] < [even: Cartan < Long(+) < Short(++) < Long(-) < Short(--) < Short(+-) < Short(-+)]",
        },
        "parity": {g: parities[g] for g in full_basis},
        "generator_realization": {
            "description": "Standard form with PBW ordering",
            "ordering": ordering_desc,
            "realizations": {g: realizations[g] for g in full_basis},
        },
        "structure_constants": structure_constants,
        "metadata": {
            "generated_by": "C_generators.py",
            "generation_date": "2026-10-12",
            "references": [
                "Frappat et al. (2000), Dictionary on Lie Algebras and Superalgebras, arXiv:hep-th/9607161"
            ],
        },
    }
    return schema


def generate_all_schema1_files(output_dir: Path) -> List[Path]:
    """Generates C_1_structure.json, C_2_structure.json, C_3_structure.json."""
    output_dir.mkdir(parents=True, exist_ok=True)
    generated = []
    for n in [1, 2, 3]:
        schema = build_schema1_json(n)
        target = output_dir / f"C_{n}_structure.json"
        with open(target, "w", encoding="utf-8") as f:
            json.dump(schema, f, indent=2)
        generated.append(target)
    return generated


if __name__ == "__main__":
    repo_root = Path(__file__).resolve().parent.parent
    data_dir = repo_root / "data"
    files = generate_all_schema1_files(data_dir)
    for p in files:
        print(f"Generated {p}")
