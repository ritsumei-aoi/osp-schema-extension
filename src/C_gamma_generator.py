#!/usr/bin/env python3
"""
Schema 2 (Gamma) and Schema 3 (Evaluated) generator for C(n+1).
"""

import json
import sys
from pathlib import Path
sys.path.insert(0, 'src')
from C_generators import generate_structure_constants, CAlgebra


def generate_gamma_schema(n: int) -> dict:
    """Generate Schema 2: Gamma structure with deformation parameters."""
    schema1 = generate_structure_constants(n)

    # Add deformation parameters (gb matrix)
    # For C(n+1), 4n parameters: gb_{a_1^σ, b_j^s} for σ,s ∈ {+,-}, j=1,...,n
    gb_params = []
    for j in range(1, n + 1):
        for sigma in ["p", "m"]:
            for s in ["p", "m"]:
                gb_params.append(f"gb_a1{sigma}_b{j}{s}")

    schema2 = {
        **schema1,
        "deformation_parameters": {
            "description": "Inhomogeneous deformation parameters (gb matrix)",
            "count": 4 * n,
            "parameters": gb_params,
            "exchange_relations": "[b_j^s, a_1^sigma] = -gb_{sigma,j,s} * kappa"
        },
        "inhomogeneous_deformation": {
            "description": "Gamma coefficients gamma_{abc} in deformed bracket",
            "note": "To be computed for specific representations"
        }
    }

    return schema2


def generate_evaluated_schema(n: int, gb_values: dict = None) -> dict:
    """Generate Schema 3: Evaluated structure with concrete gb assignments."""
    if gb_values is None:
        # Default: all gb = +1
        gb_values = {f"gb_a1{sigma}_b{j}{s}": 1
                    for j in range(1, n+1)
                    for sigma in ["p", "m"]
                    for s in ["p", "m"]}

    schema2 = generate_gamma_schema(n)

    schema3 = {
        **schema2,
        "evaluation": {
            "gb_assignment": gb_values,
            "signature": "all_positive"
        },
        "evaluated_structure_constants": {
            "note": "Structure constants with evaluated deformation parameters"
        }
    }

    return schema3


if __name__ == "__main__":
    for n in [1, 2, 3]:
        # Generate Schema 2
        schema2 = generate_gamma_schema(n)
        filename2 = f"data/C_{n}_gamma.json"
        with open(filename2, "w") as f:
            json.dump(schema2, f, indent=2)
        print(f"Generated {filename2}")

        # Generate Schema 3
        schema3 = generate_evaluated_schema(n)
        filename3 = f"data/C_{n}_evaluated_allpos.json"
        with open(filename3, "w") as f:
            json.dump(schema3, f, indent=2)
        print(f"Generated {filename3}")
