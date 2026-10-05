#!/usr/bin/env python3
"""
C(n+1) = osp(2|2n) Structure Constant Generator with Anti-symmetry

Generates basis elements and structure constants for the superalgebra C(n+1).
Includes full bracket pairs to satisfy anti-symmetry relations.

Reference: Frappat et al. (2000), handover/notation.md
"""

import json
import os
from datetime import datetime
from typing import List, Dict, Tuple
from itertools import combinations


class CnPlus1Generator:
    """Generator for C(n+1) = osp(2|2n) structure constants."""

    def __init__(self, n: int):
        """Initialize generator for C(n+1) with bosonic rank n."""
        if n < 1:
            raise ValueError("Bosonic rank n must be >= 1")
        self.n = n
        self.algebra_name = f"C({n+1})"
        self.osp_notation = f"osp(2|{2*n})"
        self.even_dim = 2*n*n + n + 1
        self.odd_dim = 4*n
        self.total_dim = self.even_dim + self.odd_dim

    def build_basis(self) -> Tuple[List[str], List[str], Dict[str, int]]:
        """Build basis elements following PBW ordering."""
        even_basis = []
        odd_basis = []
        parity = {}

        for i in range(1, self.n + 2):
            label = f"H_{i}"
            even_basis.append(label)
            parity[label] = 0

        for k in range(1, self.n + 1):
            label = f"E_2del{k}_p"
            even_basis.append(label)
            parity[label] = 0

        for i, j in combinations(range(1, self.n + 1), 2):
            label = f"E_del{i}_del{j}_pp"
            even_basis.append(label)
            parity[label] = 0

        for i, j in combinations(range(1, self.n + 1), 2):
            label = f"E_del{i}_del{j}_pm"
            even_basis.append(label)
            parity[label] = 0

        for k in range(1, self.n + 1):
            label = f"E_2del{k}_m"
            even_basis.append(label)
            parity[label] = 0

        for i, j in combinations(range(1, self.n + 1), 2):
            label = f"E_del{i}_del{j}_mm"
            even_basis.append(label)
            parity[label] = 0

        for i, j in combinations(range(1, self.n + 1), 2):
            label = f"E_del{i}_del{j}_mp"
            even_basis.append(label)
            parity[label] = 0

        for k in range(1, self.n + 1):
            for suffix in ['pp', 'pm', 'mp', 'mm']:
                label = f"E_eps_del{k}_{suffix}"
                odd_basis.append(label)
                parity[label] = 1

        return even_basis, odd_basis, parity

    def compute_structure_constants(self, even_basis: List[str],
                                   odd_basis: List[str],
                                   parity: Dict[str, int]) -> List[Dict]:
        """Compute structure constants with anti-symmetry."""
        scs = []

        def add_bracket_pair(X, Y, Z, coeff):
            """Add bracket pair [X,Y} and [Y,X} with proper anti-symmetry."""
            if X == Y:
                return

            p_x = parity.get(X, 0)
            p_y = parity.get(Y, 0)
            # [X, Y} = -(-1)^(p(X)p(Y)) [Y, X}
            # Both odd (p*p=1): sign = -(-1)^1 = 1
            # Otherwise (p*p=0): sign = -(-1)^0 = -1
            sign = 1 if (p_x * p_y == 1) else -1

            scs.append({"X": X, "Y": Y, "Z": Z, "coeff": str(coeff), "sign_rule": "graded"})
            scs.append({"X": Y, "Y": X, "Z": Z, "coeff": str(sign * coeff), "sign_rule": "graded"})

        for k in range(1, self.n + 1):
            add_bracket_pair("H_1", f"E_eps_del{k}_pp", f"E_eps_del{k}_pp", 1)
            add_bracket_pair("H_1", f"E_eps_del{k}_pm", f"E_eps_del{k}_pm", 1)
            add_bracket_pair("H_1", f"E_eps_del{k}_mp", f"E_eps_del{k}_mp", -1)
            add_bracket_pair("H_1", f"E_eps_del{k}_mm", f"E_eps_del{k}_mm", -1)

        for k in range(1, self.n + 1):
            add_bracket_pair(f"E_eps_del{k}_pp", f"E_eps_del{k}_mm", "H_1", 1)
            add_bracket_pair(f"E_eps_del{k}_pm", f"E_eps_del{k}_mp", "H_1", 1)

        for k in range(1, self.n + 1):
            add_bracket_pair(f"H_{k}", f"E_2del{k}_p", f"E_2del{k}_p", 2)

        add_bracket_pair(f"H_{self.n + 1}", f"E_2del{self.n}_p", f"E_2del{self.n}_p", -2)

        return scs

    def generate_schema(self) -> Dict:
        """Generate the complete Schema 1 JSON."""
        even_basis, odd_basis, parity = self.build_basis()
        scs = self.compute_structure_constants(even_basis, odd_basis, parity)

        realizations = {}
        for i in range(1, self.n + 2):
            if i == 1:
                standard = [{"words": ["a_1_p", "a_1_m"], "coeff": "1"}]
                for k in range(1, self.n + 1):
                    standard.append({"words": [f"b_{k}_p", f"b_{k}_m"], "coeff": "1" if k == 1 else "-1"})
            elif 1 < i <= self.n:
                standard = [
                    {"words": [f"b_{i-1}_p", f"b_{i-1}_m"], "coeff": "1"},
                    {"words": [f"b_{i}_p", f"b_{i}_m"], "coeff": "-1"}
                ]
            else:
                standard = [
                    {"words": [f"b_{self.n}_p", f"b_{self.n}_m"], "coeff": "-1"},
                    {"words": [], "coeff": "-1/2"}
                ]
            realizations[f"H_{i}"] = {"standard_form": standard, "parity": 0}

        for k in range(1, self.n + 1):
            realizations[f"E_2del{k}_p"] = {
                "standard_form": [{"words": [f"b_{k}_p", f"b_{k}_p"], "coeff": "1"}],
                "parity": 0
            }
            realizations[f"E_2del{k}_m"] = {
                "standard_form": [{"words": [f"b_{k}_m", f"b_{k}_m"], "coeff": "1"}],
                "parity": 0
            }

        for k in range(1, self.n + 1):
            for suffix, words in [
                ("pp", ["a_1_p", f"b_{k}_p"]),
                ("pm", ["a_1_p", f"b_{k}_m"]),
                ("mp", ["a_1_m", f"b_{k}_p"]),
                ("mm", ["a_1_m", f"b_{k}_m"])
            ]:
                realizations[f"E_eps_del{k}_{suffix}"] = {
                    "standard_form": [{"words": words, "coeff": "1"}],
                    "parity": 1
                }

        schema = {
            "schema_version": "5.0",
            "algebra": {
                "family": "C",
                "m": 1,
                "n": self.n,
                "cartan_type": f"C({self.n + 1})",
                "dimension": {"total": self.total_dim, "even": self.even_dim, "odd": self.odd_dim}
            },
            "central_elements": {
                "kappa": {"label": "kappa", "parity": 1, "relation": "kappa^2 = 0"},
                "K": {"label": "K", "parity": 0, "relation": "scalar 1"}
            },
            "oscillator_generators": {
                "fermions": {"m": 1, "count": 2, "labels": ["a_1_p", "a_1_m"]},
                "bosons": {"count": 2*self.n, "n": self.n, "labels": [f"b_{k}_{s}" for k in range(1, self.n+1) for s in ['p', 'm']]}
            },
            "oscillator_relations": {
                "fermionic": "{a_1-, a_1+} = 1",
                "bosonic": "[b_k-, b_l+] = delta_kl"
            },
            "basis": {"even": even_basis, "odd": odd_basis},
            "parity": parity,
            "generator_realization": {"realizations": realizations},
            "structure_constants": scs,
            "metadata": {
                "generated_by": "src/C_generators.py",
                "generation_date": datetime.now().isoformat(),
                "algebra": self.algebra_name
            }
        }
        return schema


def generate_all(output_dir: str = "data"):
    """Generate Schema 1 JSON for n=1,2,3."""
    os.makedirs(output_dir, exist_ok=True)
    for n in range(1, 4):
        gen = CnPlus1Generator(n)
        schema = gen.generate_schema()
        filename = os.path.join(output_dir, f"C_{n}_structure.json")
        with open(filename, 'w') as f:
            json.dump(schema, f, indent=2)
        print(f"Generated {filename}: {gen.even_dim} even, {gen.odd_dim} odd, {len(schema['structure_constants'])} brackets")


if __name__ == "__main__":
    generate_all()
