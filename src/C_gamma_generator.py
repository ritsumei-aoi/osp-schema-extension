#!/usr/bin/env python3
"""
C(n+1) Schema 2: Inhomogeneous Deformation (Gamma Structure) Generator

Generates the gamma (γ) structure for C(n+1) = osp(2|2n).
The deformation is parametrized by a gb matrix encoding the interaction
between the standard fermionic pair (a_1^±) and bosonic oscillators (b_k^±).

Reference: C_inhomogeneous_definition.md
"""

import json
import os
from datetime import datetime
from typing import List, Dict, Tuple


class CnPlus1GammaGenerator:
    """Generator for C(n+1) gamma structure (Schema 2)."""

    def __init__(self, n: int):
        """Initialize gamma generator for C(n+1)."""
        if n < 1:
            raise ValueError("Bosonic rank n must be >= 1")
        self.n = n
        self.algebra_name = f"C({n+1})"
        self.gb_rows = 2  # a_1^+ and a_1^-
        self.gb_cols = 2 * n  # b_k^+ and b_k^-
        self.gb_size = self.gb_rows * self.gb_cols

    def build_gb_matrix(self) -> Dict[Tuple[str, str], str]:
        """
        Build the gb deformation matrix.

        gb_{σ,j,s} for σ ∈ {+,-}, j ∈ {1,...,n}, s ∈ {+,-}

        Returns:
            Dictionary mapping (fermionic_label, bosonic_label) to parameter name
        """
        gb_matrix = {}

        fermi_labels = ["a_1_p", "a_1_m"]  # a_1^+ and a_1^-

        for f_label in fermi_labels:
            for j in range(1, self.n + 1):
                for s in ["p", "m"]:
                    b_label = f"b_{j}_{s}"
                    param_name = f"gb_{f_label}_{b_label}"
                    gb_matrix[(f_label, b_label)] = param_name

        return gb_matrix

    def compute_gamma_structure(self, gb_matrix: Dict) -> List[Dict]:
        """
        Compute gamma coefficients for the inhomogeneous deformation.

        The deformed bracket is: [X, Y]_γ = [X, Y]_0 + κ · γ(X, Y)

        γ encodes the deviation from the undeformed structure constants.
        For fermionic-bosonic pairs, γ relates to the gb parameters.

        Returns:
            List of gamma structure entries
        """
        gamma_entries = []

        # For C(n+1), the gamma structure relates to:
        # [b_j^s, a_1^σ] = -gb_{σ,j,s} · κ

        # In terms of gamma coefficients:
        # γ(b_j^s, a_1^σ) = -gb_{σ,j,s}

        for (f_label, b_label), param_name in gb_matrix.items():
            # Deformed bracket between bosonic and fermionic pair
            # [b_j^s, a_1^σ} = -gb_{σ,j,s} · κ
            gamma_entries.append({
                "generators": [b_label, f_label],
                "coefficient": f"-{param_name}",
                "result_element": "kappa",
                "description": f"Fermionic-bosonic interaction: [{b_label}, {f_label}]_γ"
            })

            # Anti-symmetry: γ(a_1^σ, b_j^s) = -γ(b_j^s, a_1^σ) (with grading sign)
            # For even-odd pair: γ(a_1, b) = γ(b, a_1)
            gamma_entries.append({
                "generators": [f_label, b_label],
                "coefficient": f"{param_name}",
                "result_element": "kappa",
                "description": f"Anti-symmetry: [{f_label}, {b_label}]_γ"
            })

        return gamma_entries

    def generate_schema_2(self, schema_1: Dict) -> Dict:
        """Generate Schema 2 (gamma structure) from Schema 1."""
        gb_matrix = self.build_gb_matrix()
        gamma = self.compute_gamma_structure(gb_matrix)

        # Build deformation parameters list
        deformation_params = {}
        for (f_label, b_label), param_name in gb_matrix.items():
            deformation_params[param_name] = {
                "label": param_name,
                "parity": 1,
                "fermionic_index": f_label,
                "bosonic_index": b_label,
                "description": f"Deformation parameter between {f_label} and {b_label}"
            }

        # Build Schema 2
        schema_2 = {
            "schema_version": "5.0",
            "schema_layer": 2,
            "algebra": schema_1["algebra"],
            "central_elements": schema_1["central_elements"],
            "deformation_structure": {
                "description": "Inhomogeneous deformation (gamma structure) for C(n+1)",
                "deformation_type": "oscillator_interaction",
                "gb_matrix": {
                    "rows": self.gb_rows,
                    "row_labels": ["a_1_p", "a_1_m"],
                    "columns": self.gb_cols,
                    "column_labels": [f"b_{j}_{s}" for j in range(1, self.n+1) for s in ['p', 'm']],
                    "total_parameters": self.gb_size
                },
                "deformation_parameters": deformation_params,
                "gamma_structure": gamma
            },
            "bracket_deformation": {
                "undeformed": "[X, Y]_0 (from Schema 1)",
                "deformed": "[X, Y]_γ = [X, Y]_0 + κ · γ(X, Y)",
                "central_extension": "κ is odd central element with κ^2 = 0"
            },
            "metadata": {
                "generated_by": "src/C_gamma_generator.py",
                "generation_date": datetime.now().isoformat(),
                "algebra": self.algebra_name,
                "references": ["C_inhomogeneous_definition.md"]
            }
        }

        return schema_2


def generate_all_schema_2(schema_1_dir: str = "data", output_dir: str = "data"):
    """Generate Schema 2 JSON files from Schema 1."""
    os.makedirs(output_dir, exist_ok=True)

    for n in range(1, 4):
        # Load Schema 1
        schema_1_file = os.path.join(schema_1_dir, f"C_{n}_structure.json")
        with open(schema_1_file, 'r') as f:
            schema_1 = json.load(f)

        # Generate Schema 2
        gen = CnPlus1GammaGenerator(n)
        schema_2 = gen.generate_schema_2(schema_1)

        # Save Schema 2
        schema_2_file = os.path.join(output_dir, f"C_{n}_gamma.json")
        with open(schema_2_file, 'w') as f:
            json.dump(schema_2, f, indent=2)

        print(f"Generated {schema_2_file}")
        print(f"  Algebra: {gen.algebra_name}")
        print(f"  Deformation parameters: {gen.gb_size} (2 × {2*n})")
        print(f"  Gamma entries: {len(schema_2['deformation_structure']['gamma_structure'])}")


if __name__ == "__main__":
    generate_all_schema_2()
