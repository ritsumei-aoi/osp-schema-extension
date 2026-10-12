"""
Schema 2 (gamma structure) generator for C(n+1) = osp(2|2n).

Generates inhomogeneous deformation with gb parameters.

Author: Claude Haiku 4.5
"""

import json
from datetime import date
from itertools import product


class CnGammaGenerator:
    """Generates Schema 2 (gamma structure) for C(n+1)."""

    def __init__(self, n, schema1_file):
        self.n = n
        self.schema1_file = schema1_file
        self.schema1 = self._load_schema1()

    def _load_schema1(self):
        """Load the corresponding Schema 1 file."""
        with open(self.schema1_file, "r") as f:
            return json.load(f)

    def _build_gb_matrix(self):
        """
        Build the gb deformation matrix.

        Parameters: gb_{a_1^σ, b_j^s} for σ,s ∈ {+,-} and j=1..n
        Total: 4n parameters, each with parity 1.
        """
        gb_params = []

        for j in range(1, self.n + 1):
            for sigma in ["p", "m"]:
                for s in ["p", "m"]:
                    label = f"gb_a1_{sigma}_b{j}_{s}"
                    gb_params.append({
                        "label": label,
                        "index": {"fermionic": f"a_1^{'+' if sigma == 'p' else '-'}",
                                 "bosonic_index": j,
                                 "bosonic_sign": "+" if s == "p" else "-"},
                        "parity": 1,
                        "description": f"Deformation parameter for [b_{j}^{'+' if s == 'p' else '-'}, a_1^{'+' if sigma == 'p' else '-'}]"
                    })

        return gb_params

    def _compute_gamma_structure(self):
        """
        Compute the gamma structure for the inhomogeneous deformation.

        The deformed bracket is:
        [X, Y]_γ = [X, Y]_0 + κ · γ(X, Y)

        where γ is determined by the gb parameters and oscillator interactions.
        """
        gamma_terms = []

        basis = self.schema1["basis"]["even"] + self.schema1["basis"]["odd"]
        structure_constants = self.schema1["structure_constants"]

        for i, X in enumerate(basis):
            for j, Y in enumerate(basis):
                gamma_coeff = self._compute_gamma_pair(X, Y)

                if gamma_coeff:
                    for Z, coeff in gamma_coeff.items():
                        gamma_terms.append({
                            "X": X,
                            "Y": Y,
                            "Z": Z,
                            "gamma_coeff": str(coeff),
                            "parametrization": "via gb matrix"
                        })

        return gamma_terms

    def _compute_gamma_pair(self, X, Y):
        """
        Compute γ(X, Y) for a specific pair.

        The gamma coefficients encode how the boson-fermion relations are deformed
        by the gb parameters. Generates symbolic parameters matching gb_matrix labels.

        Returns a dict mapping output generator Z to its γ coefficient as a string,
        with parameter names in the form "gb_a1_σ_bj_s" to match the gb_matrix.
        """
        result = {}

        X_is_odd = X.startswith("E_eps")
        Y_is_odd = Y.startswith("E_eps")

        if X_is_odd or Y_is_odd:
            if X_is_odd and not Y_is_odd:
                k_X = int(X.split("del")[1].split("_")[0])
                sign_X = X.split("_")[-1]
                sigma = "p" if sign_X[0] == "p" else "m"
                j = k_X
                s = "p" if sign_X[1] == "p" else "m"
                result[X] = f"gb_a1_{sigma}_b{j}_{s}"
            elif not X_is_odd and Y_is_odd:
                k_Y = int(Y.split("del")[1].split("_")[0])
                sign_Y = Y.split("_")[-1]
                sigma = "p" if sign_Y[0] == "p" else "m"
                j = k_Y
                s = "p" if sign_Y[1] == "p" else "m"
                result[Y] = f"-gb_a1_{sigma}_b{j}_{s}"

        return result

    def to_json(self):
        """Generate complete Schema 2 JSON."""
        schema1 = self.schema1
        gb_matrix = self._build_gb_matrix()
        gamma_structure = self._compute_gamma_structure()

        schema2 = {
            "schema_version": "5.0",
            "schema_layer": 2,
            "schema_name": "inhomogeneous_deformation",
            "algebra": schema1["algebra"],
            "oscillator_generators": schema1["oscillator_generators"],
            "oscillator_relations": schema1["oscillator_relations"],
            "central_elements": schema1["central_elements"],
            "deformation_parameters": {
                "gb_matrix": {
                    "description": "Parity-1 parameters for inhomogeneous deformation",
                    "total_count": 4 * self.n,
                    "dimensions": {
                        "fermionic_pair_count": 1,
                        "fermionic_signs": 2,
                        "bosonic_pairs": self.n,
                        "bosonic_signs": 2,
                        "formula": "2 × 2 × n"
                    },
                    "parameters": gb_matrix
                }
            },
            "inhomogeneous_deformation": {
                "description": "Gamma structure: [X, Y]_γ = [X, Y]_0 + κ · γ(X, Y)",
                "deformed_bracket": "[X, Y]_γ",
                "parametrization": "via gb exchange relations",
                "exchange_relations": [
                    "[b_j^s, a_1^σ] = -gb_{σ,j,s} · κ"
                ],
                "gamma_terms": gamma_structure
            },
            "schema1_reference": {
                "file": self.schema1_file,
                "generation_date": schema1["metadata"]["generation_date"]
            },
            "metadata": {
                "generated_by": "src/C_gamma_generator.py",
                "generation_date": str(date.today()),
                "schema_version": "5.0",
                "schema_layer": 2,
                "references": [
                    "Frappat, Sciarrino, Sorba (2000), Dictionary on Lie Algebras and Superalgebras",
                    "C_inhomogeneous_definition.md",
                    "handover/notation.md"
                ]
            }
        }

        return schema2


def generate_all_schema2_files(output_dir="data"):
    """Generate Schema 2 JSON files for n=1, 2, 3."""
    for n in [1, 2, 3]:
        schema1_file = f"{output_dir}/C_{n}_structure.json"
        gen = CnGammaGenerator(n, schema1_file)
        schema2 = gen.to_json()

        filename = f"{output_dir}/C_{n}_gamma.json"
        with open(filename, "w") as f:
            json.dump(schema2, f, indent=2)
        print(f"Generated {filename}")


if __name__ == "__main__":
    import sys
    import os

    output_dir = sys.argv[1] if len(sys.argv) > 1 else "data"

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    generate_all_schema2_files(output_dir)
    print("Schema 2 generation complete.")
