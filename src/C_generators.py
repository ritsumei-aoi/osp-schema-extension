#!/usr/bin/env python3
"""
C(n+1) Structure Constant Generator
Generates JSON schema for C(n+1) = osp(2|2n) algebra structure.
"""

import json
from typing import Dict, List, Tuple, Any
from fractions import Fraction
from dataclasses import dataclass, field, asdict


@dataclass
class Monomial:
    """Represents a monomial in oscillator algebra: product of a_1_p, a_1_m, b_k_p, b_k_m."""
    terms: Tuple[str, ...] = field(default_factory=tuple)

    def __init__(self, *args):
        self.terms = tuple(sorted(args)) if args else ()

    def __hash__(self):
        return hash(self.terms)

    def __eq__(self, other):
        return isinstance(other, Monomial) and self.terms == other.terms

    def __repr__(self):
        return f"Monomial({', '.join(self.terms)})" if self.terms else "Monomial(1)"

    def __lt__(self, other):
        return self.terms < other.terms


@dataclass
class OscillatorElement:
    """Represents a linear combination of monomials."""
    coeff_dict: Dict[Monomial, Fraction] = field(default_factory=dict)

    def __init__(self, *args, **kwargs):
        if args and isinstance(args[0], dict):
            self.coeff_dict = {Monomial(*k.split()) if isinstance(k, str) else k: Fraction(v)
                               for k, v in args[0].items()}
        else:
            self.coeff_dict = {}

    def add_term(self, monomial: Monomial, coeff: Fraction):
        if coeff != 0:
            self.coeff_dict[monomial] = self.coeff_dict.get(monomial, Fraction(0)) + coeff
            if self.coeff_dict[monomial] == 0:
                del self.coeff_dict[monomial]

    def __add__(self, other):
        result = OscillatorElement()
        for m, c in self.coeff_dict.items():
            result.add_term(m, c)
        for m, c in other.coeff_dict.items():
            result.add_term(m, c)
        return result

    def __sub__(self, other):
        result = OscillatorElement()
        for m, c in self.coeff_dict.items():
            result.add_term(m, c)
        for m, c in other.coeff_dict.items():
            result.add_term(m, -c)
        return result

    def __mul__(self, scalar):
        result = OscillatorElement()
        scalar = Fraction(scalar)
        for m, c in self.coeff_dict.items():
            result.add_term(m, c * scalar)
        return result

    def __rmul__(self, scalar):
        return self.__mul__(scalar)

    def to_standard_form(self) -> List[Dict[str, Any]]:
        """Convert to standard JSON form."""
        return [
            {"words": list(m.terms) if m.terms else [], "coeff": str(c)}
            for m, c in sorted(self.coeff_dict.items())
        ]


class CAlgebra:
    """C(n+1) = osp(2|2n) algebra."""

    def __init__(self, n: int):
        self.n = n
        self.basis = self._build_basis()
        self.parity = self._compute_parity()
        self.realizations = self._compute_realizations()

    def _build_basis(self) -> Dict[str, str]:
        """Build basis following PBW ordering."""
        basis = {"even": [], "odd": []}

        # Cartan elements: H_1, ..., H_{n+1}
        for i in range(1, self.n + 2):
            basis["even"].append(f"H_{i}")

        # Even positive roots: E_2del{k}_p
        for k in range(1, self.n + 1):
            basis["even"].append(f"E_2del{k}_p")

        # Even mixed roots: E_del{i}_del{j}_pp (i < j)
        for i in range(1, self.n + 1):
            for j in range(i + 1, self.n + 1):
                basis["even"].append(f"E_del{i}_del{j}_pp")

        # Even negative roots: E_2del{k}_m
        for k in range(1, self.n + 1):
            basis["even"].append(f"E_2del{k}_m")

        # Even mixed roots negative: E_del{i}_del{j}_mm (i < j)
        for i in range(1, self.n + 1):
            for j in range(i + 1, self.n + 1):
                basis["even"].append(f"E_del{i}_del{j}_mm")

        # Even mixed roots (pm/mp): E_del{i}_del{j}_{pm/mp} (i < j)
        for i in range(1, self.n + 1):
            for j in range(i + 1, self.n + 1):
                basis["even"].append(f"E_del{i}_del{j}_pm")

        for i in range(1, self.n + 1):
            for j in range(i + 1, self.n + 1):
                basis["even"].append(f"E_del{i}_del{j}_mp")

        # Odd generators: E_eps1_del{k}_{σ₁σ₂}
        for k in range(1, self.n + 1):
            for s1 in ["p", "m"]:
                for s2 in ["p", "m"]:
                    basis["odd"].append(f"E_eps1_del{k}_{s1}{s2}")

        return basis

    def _compute_parity(self) -> Dict[str, int]:
        """Compute parity for each basis element."""
        parity = {}

        # Even generators have parity 0
        for elem in self.basis["even"]:
            parity[elem] = 0

        # Odd generators have parity 1
        for elem in self.basis["odd"]:
            parity[elem] = 1

        return parity

    def _compute_realizations(self) -> Dict[str, OscillatorElement]:
        """Compute oscillator realizations for each generator."""
        real = {}

        # Cartan elements
        # H_1 = a_1^+ a_1^- + b_1^+ b_1^-
        real["H_1"] = OscillatorElement()
        real["H_1"].add_term(Monomial("a_1_m", "a_1_p"), Fraction(1))
        real["H_1"].add_term(Monomial("b_1_m", "b_1_p"), Fraction(1))

        # H_i = b_{i-1}^+ b_{i-1}^- - b_i^+ b_i^- for i = 2, ..., n
        for i in range(2, self.n + 1):
            real[f"H_{i}"] = OscillatorElement()
            real[f"H_{i}"].add_term(Monomial(f"b_{i-1}_m", f"b_{i-1}_p"), Fraction(1))
            real[f"H_{i}"].add_term(Monomial(f"b_{i}_m", f"b_{i}_p"), Fraction(-1))

        # H_{n+1} = -b_n^+ b_n^- - 1/2
        real[f"H_{self.n + 1}"] = OscillatorElement()
        real[f"H_{self.n + 1}"].add_term(Monomial(f"b_{self.n}_m", f"b_{self.n}_p"), Fraction(-1))
        real[f"H_{self.n + 1}"].add_term(Monomial(), Fraction(-1, 2))

        # Even roots: E_{2δₖ} = (b_k^+)^2
        for k in range(1, self.n + 1):
            real[f"E_2del{k}_p"] = OscillatorElement()
            real[f"E_2del{k}_p"].add_term(Monomial(f"b_{k}_p", f"b_{k}_p"), Fraction(1))

        # Even roots: E_{-2δₖ} = (b_k^-)^2
        for k in range(1, self.n + 1):
            real[f"E_2del{k}_m"] = OscillatorElement()
            real[f"E_2del{k}_m"].add_term(Monomial(f"b_{k}_m", f"b_{k}_m"), Fraction(1))

        # Even roots: E_{δᵢ ± δⱼ} for i < j
        for i in range(1, self.n + 1):
            for j in range(i + 1, self.n + 1):
                # E_{δᵢ + δⱼ}
                real[f"E_del{i}_del{j}_pp"] = OscillatorElement()
                real[f"E_del{i}_del{j}_pp"].add_term(Monomial(f"b_{i}_p", f"b_{j}_p"), Fraction(1))

                # E_{-δᵢ - δⱼ}
                real[f"E_del{i}_del{j}_mm"] = OscillatorElement()
                real[f"E_del{i}_del{j}_mm"].add_term(Monomial(f"b_{i}_m", f"b_{j}_m"), Fraction(1))

                # E_{δᵢ - δⱼ}
                real[f"E_del{i}_del{j}_pm"] = OscillatorElement()
                real[f"E_del{i}_del{j}_pm"].add_term(Monomial(f"b_{i}_p", f"b_{j}_m"), Fraction(1))

                # E_{-δᵢ + δⱼ}
                real[f"E_del{i}_del{j}_mp"] = OscillatorElement()
                real[f"E_del{i}_del{j}_mp"].add_term(Monomial(f"b_{i}_m", f"b_{j}_p"), Fraction(1))

        # Odd generators: E_{ε ± δₖ}
        for k in range(1, self.n + 1):
            # E_{ε + δₖ} = a_1^+ b_k^+
            real[f"E_eps1_del{k}_pp"] = OscillatorElement()
            real[f"E_eps1_del{k}_pp"].add_term(Monomial("a_1_p", f"b_{k}_p"), Fraction(1))

            # E_{ε - δₖ} = a_1^+ b_k^-
            real[f"E_eps1_del{k}_pm"] = OscillatorElement()
            real[f"E_eps1_del{k}_pm"].add_term(Monomial("a_1_p", f"b_{k}_m"), Fraction(1))

            # E_{-ε + δₖ} = a_1^- b_k^+
            real[f"E_eps1_del{k}_mp"] = OscillatorElement()
            real[f"E_eps1_del{k}_mp"].add_term(Monomial("a_1_m", f"b_{k}_p"), Fraction(1))

            # E_{-ε - δₖ} = a_1^- b_k^-
            real[f"E_eps1_del{k}_mm"] = OscillatorElement()
            real[f"E_eps1_del{k}_mm"].add_term(Monomial("a_1_m", f"b_{k}_m"), Fraction(1))

        return real

    def _anticommute(self, m1: Monomial, m2: Monomial) -> Tuple[OscillatorElement, Fraction]:
        """Compute anticommutator {a, b} accounting for oscillator algebra."""
        result = OscillatorElement()
        sign = Fraction(1)

        # Map term labels to types
        def term_type(t: str) -> str:
            if t.startswith("a_1"):
                return "f"  # fermion
            return "b"  # boson

        # Combine and sort terms
        all_terms = list(m1.terms) + list(m2.terms)

        # Track anticommutations: each swap of adjacent fermions costs a sign
        terms1_list = list(m1.terms)
        terms2_list = list(m2.terms)

        # Simple approach: compute {m1, m2} = m1*m2 + (-1)^(p1*p2) * m2*m1
        parity_pairs = sum(1 for t1 in terms1_list
                          for t2 in terms2_list
                          if term_type(t1) == "f" and term_type(t2) == "f")

        p1 = parity_pairs % 2

        # m1 * m2
        combined_terms = all_terms
        result.add_term(Monomial(*combined_terms), sign)

        # (-1)^(p1*p2) * m2 * m1
        combined_terms_rev = terms2_list + terms1_list
        sign_factor = Fraction(-1) ** p1 if p1 else Fraction(1)
        result.add_term(Monomial(*combined_terms_rev), sign_factor)

        return result, sign


def generate_structure_constants(n: int) -> Dict[str, Any]:
    """Generate structure constants for C(n+1)."""
    alg = CAlgebra(n)

    # Dimension check
    expected_even = 2 * n * n + n + 1
    expected_odd = 4 * n
    assert len(alg.basis["even"]) == expected_even, f"Even basis mismatch: got {len(alg.basis['even'])}, expected {expected_even}"
    assert len(alg.basis["odd"]) == expected_odd, f"Odd basis mismatch: got {len(alg.basis['odd'])}, expected {expected_odd}"

    # Compute structure constants via oscillator brackets
    structure_constants = []
    all_basis = alg.basis["even"] + alg.basis["odd"]

    for i, X in enumerate(all_basis):
        for j, Y in enumerate(all_basis):
            if i >= j:
                continue  # Skip lower triangle

            # Compute [X, Y} using oscillator realizations
            real_X = alg.realizations[X]
            real_Y = alg.realizations[Y]

            # For now, store zero structure constants (will be computed properly)
            # TODO: Implement proper oscillator bracket computation
            pass

    return {
        "schema_version": "5.0",
        "algebra": {
            "family": "C",
            "m": 1,
            "n": n,
            "cartan_type": f"C({n+1})",
            "alternative_notation": {
                "osp": f"osp(2|{2*n})",
                "dimension_formula": f"osp(2m|2n) with m=1"
            },
            "dimension": {
                "total": 2*n*n + 5*n + 1,
                "even": 2*n*n + n + 1,
                "odd": 4*n
            }
        },
        "oscillator_generators": {
            "fermions": {
                "count": 2,
                "m": 1,
                "labels": ["a_1_p", "a_1_m"],
                "car_relation": "{a_1^-, a_1^+} = 1",
                "parity": 1
            },
            "bosons": {
                "count": 2*n,
                "n": n,
                "labels": [f"b_{k}_{s}" for k in range(1, n+1) for s in ["p", "m"]],
                "description": f"Bosonic oscillators b_i^± with i=1,...,{n}"
            }
        },
        "oscillator_relations": {
            "standard_fermion_anticommutators": {
                "description": "{a_1^-, a_1^+} = 1",
                "relation": "{a_1_m, a_1_p} = 1"
            },
            "bosonic_commutators": {
                "description": "Canonical commutation relations",
                "relations": {
                    "same_type": "[b_i^±, b_j^±] = 0",
                    "conjugate_pair": "[b_i^-, b_j^+] = δ_{ij}"
                }
            },
            "mixed_commutators": {
                "fermion_boson": "[b_i^±, a_1^±] = 0"
            }
        },
        "central_elements": {
            "kappa": {
                "label": "κ",
                "parity": 1,
                "property": "κ² = 0",
                "role": "Deformation parametrization"
            },
            "K": {
                "label": "K",
                "parity": 0,
                "property": "identified with 1",
                "role": "Even central element"
            }
        },
        "basis": {
            "even": alg.basis["even"],
            "odd": alg.basis["odd"],
            "ordering_convention": "PBW: κ < [odd] < [even]"
        },
        "parity": alg.parity,
        "generator_realization": {
            "description": "Oscillator realization for C(n+1) generators",
            "ordering": f"a_1_p, a_1_m, " + ", ".join([f"b_{k}_{s}" for k in range(1, n+1) for s in ["p", "m"]]),
            "realizations": {
                label: {
                    "standard_form": alg.realizations[label].to_standard_form(),
                    "parity": alg.parity[label]
                }
                for label in all_basis
            }
        },
        "structure_constants": [],  # Placeholder
        "metadata": {
            "generated_by": "C_generators.py",
            "schema_version": "5.0",
            "algebra_family": f"C({n+1})",
            "references": [
                "Frappat, Sciarrino, Sorba (2000)",
                "Bakalov and Sullivan (2017)"
            ]
        }
    }


if __name__ == "__main__":
    import sys

    for n in [1, 2, 3]:
        schema = generate_structure_constants(n)
        filename = f"data/C_{n}_structure.json"
        with open(filename, "w") as f:
            json.dump(schema, f, indent=2)
        print(f"Generated {filename}")
