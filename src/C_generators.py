#!/usr/bin/env python3
"""
C(n+1) = osp(2|2n) Structure Constant Generator

Generates Schema 1 JSON for C(n+1) algebras with complete basis, parity,
and oscillator realizations (structure constants computed in later schemas).

Reference: docs/math/Cn1_definition.md, handover/notation.md
"""

import json
from fractions import Fraction
from typing import List, Dict


class CnGenerator:
    """Generator for C(n+1) structure and schema."""

    def __init__(self, n: int):
        self.n = n
        self.cartan_dim = n + 1
        self.even_dim = 2 * n**2 + n + 1
        self.odd_dim = 4 * n
        self.total_dim = self.even_dim + self.odd_dim

        # Build basis elements
        self.cartan = self._build_cartan()
        self.pos_odd = self._build_pos_odd()
        self.pos_even = self._build_pos_even()
        self.neg_even = [self._negate_gen(g) for g in reversed(self.pos_even)]
        self.neg_odd = [self._negate_gen(g) for g in reversed(self.pos_odd)]

        self.basis = self.cartan + self.pos_odd + self.pos_even + self.neg_even + self.neg_odd
        self.realizations = self._compute_realizations()

    def _negate_gen(self, gen: str) -> str:
        """Convert a root generator to its negative."""
        # Handle roots with two subscripts (pp, pm, mp, mm)
        if gen.endswith(('_pp', '_mm', '_pm', '_mp')):
            if gen.endswith('_pp'):
                return gen[:-3] + '_mm'
            elif gen.endswith('_mm'):
                return gen[:-3] + '_pp'
            elif gen.endswith('_pm'):
                return gen[:-3] + '_mp'
            elif gen.endswith('_mp'):
                return gen[:-3] + '_pm'
        # Handle roots with single subscript (p, m)
        elif gen.endswith('_p'):
            return gen[:-2] + '_m'
        elif gen.endswith('_m'):
            return gen[:-2] + '_p'
        return gen

    def _build_cartan(self) -> List[str]:
        """Build Cartan subalgebra: H_1, ..., H_{n+1}."""
        return [f"H_{k+1}" for k in range(self.n + 1)]

    def _build_pos_odd(self) -> List[str]:
        """Build positive odd roots: ε+δ_k, ε-δ_k for k=1,...,n."""
        odd = []
        for k in range(1, self.n + 1):
            odd.append(f"E_eps_del{k}_pp")  # ε+δ_k
        for k in range(1, self.n + 1):
            odd.append(f"E_eps_del{k}_pm")  # ε-δ_k
        return odd

    def _build_pos_even(self) -> List[str]:
        """Build positive even roots: 2δ_k, δ_i-δ_j, δ_i+δ_j."""
        even = []
        for k in range(1, self.n + 1):
            even.append(f"E_2del{k}_p")
        for i in range(1, self.n):
            for j in range(i + 1, self.n + 1):
                even.append(f"E_del{i}_del{j}_pm")  # δ_i - δ_j
        for i in range(1, self.n):
            for j in range(i + 1, self.n + 1):
                even.append(f"E_del{i}_del{j}_pp")  # δ_i + δ_j
        return even

    def _compute_realizations(self) -> Dict[str, List]:
        """Compute oscillator realizations for all basis elements."""
        realizations = {}

        # Cartan elements
        for k in range(1, self.n):
            # H_k = b_{k}^+ b_{k}^- - b_{k+1}^+ b_{k+1}^-
            realizations[f"H_{k}"] = [
                (["b_{k}_p", "b_{k}_m"], Fraction(1)),
                (["b_{k+1}_p", "b_{k+1}_m"], Fraction(-1))
            ]

        # H_1 = a_1^+ a_1^- + b_1^+ b_1^-
        realizations["H_1"] = [
            (["a_1_p", "a_1_m"], Fraction(1)),
            (["b_1_p", "b_1_m"], Fraction(1))
        ]

        # Terminal Cartan H_{n+1} = -b_n^+ b_n^- - 1/2
        realizations[f"H_{self.n + 1}"] = [
            (["b_{self.n}_p", "b_{self.n}_m"], Fraction(-1)),
            ([], Fraction(-1, 2))
        ]

        # Positive odd roots
        for k in range(1, self.n + 1):
            # E_{ε+δ_k} = a_1^+ b_k^+
            realizations[f"E_eps_del{k}_pp"] = [(["a_1_p", f"b_{k}_p"], Fraction(1))]
            # E_{ε-δ_k} = a_1^+ b_k^-
            realizations[f"E_eps_del{k}_pm"] = [(["a_1_p", f"b_{k}_m"], Fraction(1))]
            # E_{-ε+δ_k} = a_1^- b_k^+
            realizations[f"E_eps_del{k}_mp"] = [(["a_1_m", f"b_{k}_p"], Fraction(1))]
            # E_{-ε-δ_k} = a_1^- b_k^-
            realizations[f"E_eps_del{k}_mm"] = [(["a_1_m", f"b_{k}_m"], Fraction(1))]

        # Positive even roots
        for k in range(1, self.n + 1):
            # E_{2δ_k} = (1/2)(b_k^+)^2
            realizations[f"E_2del{k}_p"] = [([f"b_{k}_p", f"b_{k}_p"], Fraction(1, 2))]

        for i in range(1, self.n):
            for j in range(i + 1, self.n + 1):
                # E_{δ_i - δ_j} = b_i^+ b_j^-
                realizations[f"E_del{i}_del{j}_pm"] = [([f"b_{i}_p", f"b_{j}_m"], Fraction(1))]

        for i in range(1, self.n):
            for j in range(i + 1, self.n + 1):
                # E_{δ_i + δ_j} = b_i^+ b_j^+
                realizations[f"E_del{i}_del{j}_pp"] = [([f"b_{i}_p", f"b_{j}_p"], Fraction(1))]

        # Add negative generators
        neg_gens = set()
        for gen in list(realizations.keys()):
            if gen not in self.cartan:
                neg_gen = self._negate_gen(gen)
                if neg_gen not in realizations:
                    neg_realization = []
                    for word, coeff in realizations[gen]:
                        neg_word = [self._negate_oscillator_label(w) for w in word]
                        neg_realization.append((neg_word, coeff))
                    realizations[neg_gen] = neg_realization
                    neg_gens.add(neg_gen)

        return realizations

    def _negate_oscillator_label(self, label: str) -> str:
        """Negate an oscillator label (swap p and m)."""
        if label.endswith('_p'):
            return label[:-2] + '_m'
        elif label.endswith('_m'):
            return label[:-2] + '_p'
        return label

    def generate_schema(self) -> Dict:
        """Generate complete Schema 1 JSON."""
        return {
            "schema_version": "5.0",
            "algebra": {
                "family": "C",
                "m": 1,
                "n": self.n,
                "cartan_type": f"C({self.n + 1})",
                "alternative_notation": {
                    "osp": f"osp(2|{2*self.n})",
                    "dimension_formula": "osp(2m|2n) with m=1"
                },
                "dimension": {
                    "total": self.total_dim,
                    "even": self.even_dim,
                    "odd": self.odd_dim
                }
            },
            "oscillator_generators": {
                "fermions": {
                    "label": "a_1",
                    "m": 1,
                    "parity": 1,
                    "relation": "{a_1^-, a_1^+} = 1",
                    "description": "Standard fermionic pair (CAR)",
                    "labels": ["a_1_p", "a_1_m"]
                },
                "bosons": {
                    "count": 2 * self.n,
                    "n": self.n,
                    "labels": [f"b_{k}_{s}" for k in range(1, self.n + 1) for s in ['p', 'm']],
                    "description": f"Bosonic oscillators b_i^± with i=1,...,{self.n}"
                }
            },
            "oscillator_relations": {
                "standard_fermion_anticommutators": {
                    "description": "Canonical anticommutation relations",
                    "relations": {
                        "pair": "{a_1^-, a_1^+} = 1",
                        "same": "{a_1^±, a_1^±} = 0"
                    }
                },
                "bosonic_commutators": {
                    "description": "Canonical commutation relations",
                    "relations": {
                        "same_type": "[b_i^±, b_j^±] = 0 for all i, j",
                        "conjugate_pair": "[b_i^-, b_j^+] = δ_ij"
                    }
                },
                "mixed_anticommutators": {
                    "fermion_boson": "{a_1^±, b_j^±} = 0"
                }
            },
            "central_elements": {
                "kappa": {
                    "label": "κ",
                    "parity": 1,
                    "nilpotency": "κ^2 = 0",
                    "description": "Odd central element for deformation"
                },
                "K": {
                    "label": "K",
                    "parity": 0,
                    "note": "Even central element; identified with scalar 1"
                }
            },
            "basis": {
                "even": self.cartan + self.pos_even + self.neg_even,
                "odd": self.pos_odd + self.neg_odd,
                "ordering_convention": "PBW: Cartan < pos_odd < pos_even < neg_even < neg_odd"
            },
            "parity": {gen: self._get_parity(gen) for gen in self.basis},
            "generator_realization": {
                "description": "Oscillator realizations in standard form",
                "ordering": ["a_1_p", "a_1_m"] +
                           [f"b_{k}_{s}" for k in range(1, self.n + 1) for s in ['p', 'm']],
                "realizations": self._format_realizations()
            },
            "structure_constants": [],
            "metadata": {
                "generated_by": "C_generators.py",
                "algebra": f"C({self.n + 1}) = osp(2|{2*self.n})",
                "dimension_formula": f"even = {self.even_dim}, odd = {self.odd_dim}, total = {self.total_dim}",
                "note": "Structure constants to be computed in Schema 2 layer"
            }
        }

    def _get_parity(self, gen: str) -> int:
        """Get parity of a generator."""
        if gen.startswith('H'):
            return 0
        elif 'E_eps' in gen:
            return 1
        else:
            return 0

    def _format_realizations(self) -> Dict:
        """Format realizations for JSON output."""
        output = {}
        for gen in self.basis:
            if gen in self.realizations:
                terms = self.realizations[gen]
                formatted_terms = []
                for word, coeff in terms:
                    formatted_terms.append({
                        "words": word,
                        "coeff": str(coeff)
                    })

                parity = self._get_parity(gen)

                output[gen] = {
                    "standard_form": formatted_terms,
                    "parity": parity
                }
        return output


def main():
    """Generate Schema 1 JSON files for C(n+1), n=1,2,3."""
    for n in [1, 2, 3]:
        print(f"Generating C({n+1}) (n={n})...")
        gen = CnGenerator(n)
        schema = gen.generate_schema()

        filename = f"data/C_{n}_structure.json"
        with open(filename, 'w') as f:
            json.dump(schema, f, indent=2)

        print(f"  Dimensions: even={schema['algebra']['dimension']['even']}, "
              f"odd={schema['algebra']['dimension']['odd']}")
        print(f"  Basis size: {len(gen.basis)}")
        print(f"  Realizations: {len(schema['generator_realization']['realizations'])}")
        print(f"  Saved to {filename}")


if __name__ == "__main__":
    main()
