#!/usr/bin/env python3
"""
Schema 2 (Gamma Structure) Generator for C(n+1)

Implements the inhomogeneous deformation parametrization through the gb-matrix,
which controls the exchange relations between fermionic and bosonic oscillators.

Reference: docs/math/C_inhomogeneous_definition.md
"""

import json
from fractions import Fraction
from typing import Dict, List


class CnGammaGenerator:
    """Generator for C(n+1) Schema 2 (deformation structure)."""

    def __init__(self, n: int):
        self.n = n
        self.fermion_labels = ["a_1_p", "a_1_m"]  # σ ∈ {+, -}
        self.bosons = [f"b_{k}_{s}" for k in range(1, n + 1) for s in ["p", "m"]]

        # gb-matrix dimensions: 2 fermionic × 2n bosonic = 4n parameters
        self.gb_parameters = self._define_gb_parameters()

    def _define_gb_parameters(self) -> List[Dict]:
        """Define all gb deformation parameters."""
        parameters = []

        sigma_labels = ["+", "-"]
        for sigma_idx, sigma in enumerate(sigma_labels):
            for k in range(1, self.n + 1):
                for s_idx, s in enumerate(["p", "m"]):
                    param = {
                        "label": f"gb_{sigma}_{k}_{s}",
                        "index": {
                            "fermionic": sigma,
                            "bosonic_k": k,
                            "bosonic_sign": s
                        },
                        "parity": 1,  # All gb parameters are odd
                        "description": f"Deformation parameter for [b_{k}^{s}, a_1^{sigma}] = -gb_{{sigma,{k},{s}}} · κ"
                    }
                    parameters.append(param)

        return parameters

    def load_schema1(self, schema1_file: str) -> Dict:
        """Load Schema 1 JSON for consistency check."""
        with open(schema1_file) as f:
            return json.load(f)

    def generate_schema2(self, schema1: Dict) -> Dict:
        """Generate Schema 2 JSON from Schema 1."""
        algebra = schema1['algebra']
        n = algebra['n']

        return {
            "schema_version": "5.0",
            "algebra": algebra,
            "inhomogeneous_deformation": {
                "description": "Inhomogeneous deformation parametrization via gb-matrix",
                "reference": "docs/math/C_inhomogeneous_definition.md",
                "deformation_type": "oscillator_exchange_relation",
                "central_element": "κ",
                "exchange_relation": "[b_j^s, a_1^σ] = -gb_{σ,j,s} · κ",
                "gb_matrix": {
                    "shape": f"2 × {2*n}",
                    "size": 4*n,
                    "parity": 1,
                    "description": "Deformation parameters indexed by (fermionic sign, bosonic oscillator)"
                },
                "gb_parameters": self.gb_parameters,
                "gamma_cocycle": {
                    "status": "to be computed",
                    "method": "oscillator bracket evaluation",
                    "formula": "γ_abc derived from [X_a, X_b] = δ(a,b) + κ·γ_abc(gb)·X_c",
                    "note": "Gamma coefficients depend on gb parameters and are computed in evaluation layer"
                }
            },
            "coboundary_structure": {
                "description": "Framework for triviality analysis (Schema 4)",
                "linear_map_f": {
                    "parity": "odd (reverses parity of input)",
                    "domain": "Lie algebra g",
                    "codomain": "Lie algebra g",
                    "parametrization": "to be determined"
                },
                "coboundary_operator": {
                    "formula": "(δf)(X,Y) = (-1)^{p(X)}[X,f(Y)] - (-1)^{(p(X)+1)p(Y)}[Y,f(X)] - f([X,Y])",
                    "triviality_condition": "γ(X,Y) = (δf)(X,Y) for all X,Y ∈ g"
                }
            },
            "consistency": {
                "schema1_elements": len(schema1['basis']['even']) + len(schema1['basis']['odd']),
                "cartan_dimension": len(schema1['basis']['even']),  # Approximation
                "gb_matrix_size": 4*n,
                "note": "γ-coefficients will be computed for all ${dim(g)^2}$ pairs"
            },
            "metadata": {
                "generated_by": "C_gamma_generator.py",
                "schema1_source": f"C_{n}_structure.json",
                "algebra": f"C({n+1}) = osp(2|{2*n})",
                "status": "parametrization defined; gamma computation pending"
            }
        }


def main():
    """Generate Schema 2 JSON files for C(n+1), n=1,2,3."""
    for n in [1, 2, 3]:
        schema1_file = f"data/C_{n}_structure.json"
        schema2_file = f"data/C_{n}_gamma.json"

        print(f"Generating Schema 2 for C({n+1}) (n={n})...")

        gen = CnGammaGenerator(n)
        schema1 = gen.load_schema1(schema1_file)
        schema2 = gen.generate_schema2(schema1)

        with open(schema2_file, 'w') as f:
            json.dump(schema2, f, indent=2)

        print(f"  gb-matrix size: {len(gen.gb_parameters)}")
        print(f"  Saved to {schema2_file}")


if __name__ == "__main__":
    main()
