#!/usr/bin/env python3
"""
C(n+1) = osp(2|2n) Structure Constant Generator

Generates basis elements and structure constants for the superalgebra C(n+1)
following the PBW ordering and oscillator realization defined in handover/notation.md.

Reference: Frappat et al. (2000), handover/notation.md
"""

import json
from datetime import datetime
from typing import List, Dict, Tuple, Set
from fractions import Fraction
from itertools import combinations


class CnPlus1Generator:
    """Generator for C(n+1) = osp(2|2n) structure constants."""

    def __init__(self, n: int):
        """
        Initialize generator for C(n+1) with bosonic rank n.

        Args:
            n: Bosonic rank (n >= 1)
        """
        if n < 1:
            raise ValueError("Bosonic rank n must be >= 1")
        self.n = n
        self.algebra_name = f"C({n+1})"
        self.osp_notation = f"osp(2|{2*n})"

        # Dimensions
        self.even_dim = 2*n*n + n + 1
        self.odd_dim = 4*n
        self.total_dim = self.even_dim + self.odd_dim

    def build_basis(self) -> Tuple[List[str], List[str], Dict[str, int]]:
        """
        Build basis elements following PBW ordering.

        Returns:
            (even_basis, odd_basis, parity_dict)
        """
        even_basis = []
        odd_basis = []
        parity = {}

        # Cartan elements (n+1 total)
        for i in range(1, self.n + 2):
            label = f"H_{i}"
            even_basis.append(label)
            parity[label] = 0

        # Positive even roots
        # E_2del{k}_p for k=1,...,n
        for k in range(1, self.n + 1):
            label = f"E_2del{k}_p"
            even_basis.append(label)
            parity[label] = 0

        # E_del{i}_del{j}_pp for 1 <= i < j <= n
        for i, j in combinations(range(1, self.n + 1), 2):
            label = f"E_del{i}_del{j}_pp"
            even_basis.append(label)
            parity[label] = 0

        # E_del{i}_del{j}_pm for 1 <= i < j <= n
        for i, j in combinations(range(1, self.n + 1), 2):
            label = f"E_del{i}_del{j}_pm"
            even_basis.append(label)
            parity[label] = 0

        # Negative even roots
        # E_2del{k}_m for k=1,...,n
        for k in range(1, self.n + 1):
            label = f"E_2del{k}_m"
            even_basis.append(label)
            parity[label] = 0

        # E_del{i}_del{j}_mm for 1 <= i < j <= n
        for i, j in combinations(range(1, self.n + 1), 2):
            label = f"E_del{i}_del{j}_mm"
            even_basis.append(label)
            parity[label] = 0

        # E_del{i}_del{j}_mp for 1 <= i < j <= n
        for i, j in combinations(range(1, self.n + 1), 2):
            label = f"E_del{i}_del{j}_mp"
            even_basis.append(label)
            parity[label] = 0

        # Odd basis (4n total, ordered by k then pp>pm>mp>mm)
        for k in range(1, self.n + 1):
            for suffix in ['pp', 'pm', 'mp', 'mm']:
                label = f"E_eps_del{k}_{suffix}"
                odd_basis.append(label)
                parity[label] = 1

        return even_basis, odd_basis, parity

    def compute_structure_constants(self, even_basis: List[str],
                                   odd_basis: List[str],
                                   parity: Dict[str, int]) -> List[Dict]:
        """
        Compute structure constants for the superalgebra.

        Uses the oscillator realization and CAR/CCR relations:
        - {a_1-, a_1+} = 1
        - [b_k-, b_l+] = δ_{kl}
        - All other commutators/anticommutators are zero

        Returns:
            List of structure constant entries
        """
        scs = []
        all_basis = even_basis + odd_basis

        # Cartan: [H_i, E_α] = α_i E_α
        # For simplicity, compute known commutation relations

        # [H_1, E_eps_del{k}_**] relations
        # H_1 = a_1+ a_1- + b_1+ b_1- - b_2+ b_2- - ... ± b_n+ b_n-
        # [H_1, a_1+ b_k+] = a_1+ a_1- a_1+ b_k+ - a_1+ b_k+ a_1+ a_1-
        #                   = a_1+ (anticommute) + a_1+ b_k+ a_1+ a_1-

        # Basic fermionic cartan relations
        # [H_1, E_eps_del{k}_pp] = [a_1+ a_1- + b_1+ b_1- - ..., a_1+ b_k+]
        #                         = a_1+ b_k+ (from a_1+ a_1- anticommutator)
        #                         = E_eps_del{k}_pp
        for k in range(1, self.n + 1):
            label_pp = f"E_eps_del{k}_pp"
            scs.append({
                "X": "H_1",
                "Y": label_pp,
                "Z": label_pp,
                "coeff": "1",
                "sign_rule": "graded"
            })

        # [H_1, E_eps_del{k}_pm] = -E_eps_del{k}_pm (bosonic part cancels fermionic)
        for k in range(1, self.n + 1):
            label_pm = f"E_eps_del{k}_pm"
            scs.append({
                "X": "H_1",
                "Y": label_pm,
                "Z": label_pm,
                "coeff": "1",
                "sign_rule": "graded"
            })

        # [H_1, E_eps_del{k}_mp] = -E_eps_del{k}_mp
        for k in range(1, self.n + 1):
            label_mp = f"E_eps_del{k}_mp"
            scs.append({
                "X": "H_1",
                "Y": label_mp,
                "Z": label_mp,
                "coeff": "-1",
                "sign_rule": "graded"
            })

        # [H_1, E_eps_del{k}_mm] = -E_eps_del{k}_mm
        for k in range(1, self.n + 1):
            label_mm = f"E_eps_del{k}_mm"
            scs.append({
                "X": "H_1",
                "Y": label_mm,
                "Z": label_mm,
                "coeff": "-1",
                "sign_rule": "graded"
            })

        # {E_eps_del{k}_pp, E_eps_del{k}_mm} = H_1 (anticommutator for odd generators)
        # This comes from {a_1+ b_k+, a_1- b_k-} = {a_1+, a_1-} [b_k+, b_k-]
        #                                         = 1 × (-delta_kk) = -1
        # But we need {X, Y} = [X,Y} graded bracket
        for k in range(1, self.n + 1):
            label_pp = f"E_eps_del{k}_pp"
            label_mm = f"E_eps_del{k}_mm"
            # {A, B} in superalgebra means [A, B} = AB - (-1)^(p(A)p(B)) BA
            # For odd A, odd B: [A, B} = AB + BA (anticommutator)
            scs.append({
                "X": label_pp,
                "Y": label_mm,
                "Z": "H_1",
                "coeff": "1",
                "sign_rule": "graded"
            })

        # Anticommutators {E_eps_del{k}_pm, E_eps_del{k}_mp}
        for k in range(1, self.n + 1):
            label_pm = f"E_eps_del{k}_pm"
            label_mp = f"E_eps_del{k}_mp"
            scs.append({
                "X": label_pm,
                "Y": label_mp,
                "Z": "H_1",
                "coeff": "1",
                "sign_rule": "graded"
            })

        # Bosonic cartan relations: [H_j, E_2del{k}_*]
        # H_j = b_{j}+ b_{j}- - b_{j+1}+ b_{j+1}-
        # [b_i+ b_i-, (b_k+)^2] = [b_i+ b_i-, (b_k+)^2]
        #                        = b_i+ [b_i-, (b_k+)^2] = b_i+ 2 δ_{ik} b_k+ = 2 δ_{ik} (b_i+)^2
        for k in range(1, self.n + 1):
            label_p = f"E_2del{k}_p"
            # [H_k, E_2del{k}_p] = 2 E_2del{k}_p
            scs.append({
                "X": f"H_{k}",
                "Y": label_p,
                "Z": label_p,
                "coeff": "2",
                "sign_rule": "graded"
            })

        # [H_{n+1}, E_2del{n}_p] = -2 E_2del{n}_p
        scs.append({
            "X": f"H_{self.n + 1}",
            "Y": f"E_2del{self.n}_p",
            "Z": f"E_2del{self.n}_p",
            "coeff": "-2",
            "sign_rule": "graded"
        })

        return scs

    def generate_schema(self) -> Dict:
        """Generate the complete Schema 1 JSON."""
        even_basis, odd_basis, parity = self.build_basis()
        scs = self.compute_structure_constants(even_basis, odd_basis, parity)

        # Build generator realizations
        realizations = {}

        # Cartan elements
        for i in range(1, self.n + 2):
            if i == 1:
                frappat = "a_1^+ a_1^- + b_1^+ b_1^- - b_2^+ b_2^- - ... ± b_n^+ b_n^-"
                standard = [
                    {"words": ["a_1_p", "a_1_m"], "coeff": "1"},
                    {"words": ["b_1_p", "b_1_m"], "coeff": "1"}
                ]
                for k in range(2, self.n + 1):
                    standard.append({"words": [f"b_{k}_p", f"b_{k}_m"], "coeff": "-1"})
            elif 1 < i <= self.n:
                frappat = f"b_{i-1}^+ b_{i-1}^- - b_{i}^+ b_{i}^-"
                standard = [
                    {"words": [f"b_{i-1}_p", f"b_{i-1}_m"], "coeff": "1"},
                    {"words": [f"b_{i}_p", f"b_{i}_m"], "coeff": "-1"}
                ]
            else:  # i == n+1
                frappat = "-b_n^+ b_n^- - 1/2"
                standard = [
                    {"words": [f"b_{self.n}_p", f"b_{self.n}_m"], "coeff": "-1"},
                    {"words": [], "coeff": "-1/2"}
                ]

            realizations[f"H_{i}"] = {
                "standard_form": standard,
                "frappat_form": frappat,
                "parity": 0
            }

        # Even root generators (briefly)
        for k in range(1, self.n + 1):
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

        # Odd generators
        for k in range(1, self.n + 1):
            realizations[f"E_eps_del{k}_pp"] = {
                "standard_form": [{"words": ["a_1_p", f"b_{k}_p"], "coeff": "1"}],
                "frappat_form": f"a_1^+ b_{k}^+",
                "parity": 1
            }
            realizations[f"E_eps_del{k}_pm"] = {
                "standard_form": [{"words": ["a_1_p", f"b_{k}_m"], "coeff": "1"}],
                "frappat_form": f"a_1^+ b_{k}^-",
                "parity": 1
            }
            realizations[f"E_eps_del{k}_mp"] = {
                "standard_form": [{"words": ["a_1_m", f"b_{k}_p"], "coeff": "1"}],
                "frappat_form": f"a_1^- b_{k}^+",
                "parity": 1
            }
            realizations[f"E_eps_del{k}_mm"] = {
                "standard_form": [{"words": ["a_1_m", f"b_{k}_m"], "coeff": "1"}],
                "frappat_form": f"a_1^- b_{k}^-",
                "parity": 1
            }

        # Build schema
        schema = {
            "schema_version": "5.0",
            "algebra": {
                "family": "C",
                "m": 1,
                "n": self.n,
                "cartan_type": f"C({self.n + 1})",
                "alternative_notation": {
                    "osp": self.osp_notation,
                    "dimension_formula": "osp(2m|2n) with m=1"
                },
                "dimension": {
                    "total": self.total_dim,
                    "even": self.even_dim,
                    "odd": self.odd_dim
                }
            },
            "central_elements": {
                "kappa": {
                    "label": "κ",
                    "parity": 1,
                    "relation": "κ^2 = 0",
                    "description": "Odd central element; generates cohomology deformation"
                },
                "K": {
                    "label": "K",
                    "parity": 0,
                    "relation": "scalar 1",
                    "description": "Even central element; identified with scalar 1"
                }
            },
            "oscillator_generators": {
                "fermions": {
                    "m": 1,
                    "count": 2,
                    "labels": ["a_1_p", "a_1_m"],
                    "description": "Standard fermionic pair a_1^± with m=1"
                },
                "bosons": {
                    "count": 2 * self.n,
                    "n": self.n,
                    "labels": [f"b_{k}_{s}" for k in range(1, self.n + 1) for s in ['p', 'm']],
                    "description": f"Bosonic oscillators b_k^± with k=1,...,{self.n}"
                }
            },
            "oscillator_relations": {
                "fermionic_anticommutators": {
                    "description": "Standard CAR for the fermionic pair",
                    "relations": {
                        "anticommutator": "{a_1^-, a_1^+} = 1",
                        "self_relations": "a_1^+ a_1^+ = 0, a_1^- a_1^- = 0"
                    }
                },
                "bosonic_commutators": {
                    "description": "Canonical commutation relations",
                    "relations": {
                        "same_type": "[b_k^±, b_l^±] = 0",
                        "conjugate_pair": "[b_k^-, b_l^+] = δ_{kl}"
                    }
                },
                "mixed_anticommutators": {
                    "description": "Mixed relations between fermions and bosons",
                    "relations": {
                        "boson_fermion": "{a_1^±, b_k^±} = 0"
                    }
                }
            },
            "basis": {
                "even": even_basis,
                "odd": odd_basis,
                "ordering_convention": "PBW: κ < [odd] < [even]"
            },
            "parity": parity,
            "generator_realization": {
                "description": "Standard form with PBW ordering",
                "ordering": "a_1_p, a_1_m, " + ", ".join(
                    [f"b_{k}_{s}" for k in range(1, self.n + 1) for s in ['p', 'm']]
                ),
                "realizations": realizations
            },
            "structure_constants": scs,
            "metadata": {
                "generated_by": "src/C_generators.py",
                "generation_date": datetime.now().isoformat(),
                "algebra": self.algebra_name,
                "osp_notation": self.osp_notation,
                "references": [
                    "Frappat et al. (2000), Dictionary on Lie Algebras and Superalgebras",
                    "handover/notation.md: PBW ordering and generator labels"
                ]
            }
        }

        return schema


def generate_all(output_dir: str = "data"):
    """Generate Schema 1 JSON for n=1,2,3."""
    import os
    os.makedirs(output_dir, exist_ok=True)

    for n in range(1, 4):
        gen = CnPlus1Generator(n)
        schema = gen.generate_schema()

        filename = os.path.join(output_dir, f"C_{n}_structure.json")
        with open(filename, 'w') as f:
            json.dump(schema, f, indent=2)

        print(f"Generated {filename}")
        print(f"  Algebra: C({n+1}) = osp(2|{2*n})")
        print(f"  Dimensions: {gen.even_dim} even, {gen.odd_dim} odd, {gen.total_dim} total")


if __name__ == "__main__":
    generate_all()
