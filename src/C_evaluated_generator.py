#!/usr/bin/env python3
"""
C(n+1) Schema 3: Evaluated Structure Generator

Evaluates the symbolic gamma structure (Schema 2) by substituting concrete
values for the gb deformation parameters.

This produces the evaluated structure constants with explicit numerical
coefficients, ready for computational applications.
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Any
from fractions import Fraction


class CnPlus1EvaluatedGenerator:
    """Generator for C(n+1) evaluated structure (Schema 3)."""

    def __init__(self, n: int, gb_assignment: Dict[str, int] = None):
        """
        Initialize evaluated generator for C(n+1).

        Args:
            n: Bosonic rank
            gb_assignment: Dictionary mapping parameter names to values (+1 or -1)
                          If None, uses default (all +1)
        """
        if n < 1:
            raise ValueError("Bosonic rank n must be >= 1")
        self.n = n
        self.algebra_name = f"C({n+1})"

        # Default assignment: all parameters set to +1
        if gb_assignment is None:
            gb_assignment = self._default_assignment()

        self.gb_assignment = gb_assignment

    def _default_assignment(self) -> Dict[str, int]:
        """Create default gb assignment (all parameters = +1)."""
        assignment = {}

        fermi_labels = ["a_1_p", "a_1_m"]
        for f_label in fermi_labels:
            for j in range(1, self.n + 1):
                for s in ["p", "m"]:
                    b_label = f"b_{j}_{s}"
                    param_name = f"gb_{f_label}_{b_label}"
                    assignment[param_name] = 1  # All +1

        return assignment

    def evaluate_gamma_entry(self, gamma_entry: Dict) -> Dict:
        """
        Evaluate a single gamma entry by substituting parameter values.

        Args:
            gamma_entry: Dictionary with 'coefficient' as a string expression

        Returns:
            Evaluated entry with numerical coefficient
        """
        evaluated = gamma_entry.copy()
        coeff_expr = gamma_entry["coefficient"]

        # Evaluate coefficient expression
        value = self._evaluate_expression(coeff_expr)
        evaluated["coefficient"] = str(value)
        evaluated["coefficient_numerical"] = float(value)

        return evaluated

    def _evaluate_expression(self, expr: str) -> Fraction:
        """
        Evaluate a coefficient expression with gb parameters.

        Args:
            expr: Expression like "-gb_a_1_p_b_1_p" or "gb_a_1_m_b_2_m"

        Returns:
            Evaluated coefficient as Fraction
        """
        # Handle simple cases
        expr = expr.strip()

        # Check for negation
        negate = False
        if expr.startswith("-"):
            negate = True
            expr = expr[1:].strip()

        # Extract parameter name
        if expr.startswith("gb_"):
            param_name = expr
            if param_name in self.gb_assignment:
                value = Fraction(self.gb_assignment[param_name])
            else:
                # Parameter not found, return 0
                return Fraction(0)
        else:
            # Not a gb parameter, try to parse as constant
            try:
                value = Fraction(expr)
            except:
                return Fraction(0)

        if negate:
            value = -value

        return value

    def generate_schema_3(self, schema_2: Dict) -> Dict:
        """
        Generate Schema 3 by evaluating Schema 2.

        Args:
            schema_2: Schema 2 JSON structure

        Returns:
            Schema 3 JSON with evaluated coefficients
        """
        # Evaluate all gamma entries
        evaluated_gamma = []
        for gamma_entry in schema_2["deformation_structure"]["gamma_structure"]:
            evaluated_gamma.append(self.evaluate_gamma_entry(gamma_entry))

        # Build evaluated structure constants
        # Include both undeformed and deformed brackets
        evaluated_scs = []

        # Start with undeformed structure constants from Schema 1
        schema_1_file = os.path.join("data", f"C_{self.n}_structure.json")
        with open(schema_1_file, 'r') as f:
            schema_1 = json.load(f)

        # Copy undeformed structure constants
        for sc in schema_1["structure_constants"]:
            evaluated_scs.append({
                "X": sc["X"],
                "Y": sc["Y"],
                "Z": sc["Z"],
                "coeff_undeformed": sc["coeff"],
                "coeff_deformation": "0",  # No deformation for undeformed pairs
                "coeff_total": sc["coeff"]
            })

        # Add deformed brackets (from gamma structure)
        for gamma_entry in evaluated_gamma:
            if gamma_entry["coefficient_numerical"] != 0:
                evaluated_scs.append({
                    "X": gamma_entry["generators"][0],
                    "Y": gamma_entry["generators"][1],
                    "Z": gamma_entry["result_element"],
                    "coeff_undeformed": "0",
                    "coeff_deformation": str(gamma_entry["coefficient"]),
                    "coeff_total": str(gamma_entry["coefficient"]),
                    "source": "deformation"
                })

        # Build Schema 3
        schema_3 = {
            "schema_version": "5.0",
            "schema_layer": 3,
            "algebra": schema_2["algebra"],
            "central_elements": schema_2["central_elements"],
            "gb_assignment": {
                "description": "Concrete assignment of gb parameters",
                "parameters": self.gb_assignment,
                "assignment_type": "all_positive"
            },
            "evaluated_structure": {
                "description": "Evaluated structure constants with concrete gb values",
                "undeformed_brackets_count": len(schema_1["structure_constants"]),
                "deformed_brackets_count": len(evaluated_gamma),
                "structure_constants": evaluated_scs,
                "gamma_evaluated": evaluated_gamma
            },
            "deformation_summary": {
                "nonzero_deformations": sum(1 for g in evaluated_gamma if g["coefficient_numerical"] != 0),
                "deformation_type": "fermionic_bosonic_interaction",
                "parameter_assignment": "all gb parameters = +1"
            },
            "metadata": {
                "generated_by": "src/C_evaluated_generator.py",
                "generation_date": datetime.now().isoformat(),
                "algebra": self.algebra_name,
                "gb_assignment": "default (all +1)"
            }
        }

        return schema_3


def generate_all_schema_3(schema_2_dir: str = "data", output_dir: str = "data"):
    """Generate Schema 3 JSON files from Schema 2."""
    os.makedirs(output_dir, exist_ok=True)

    for n in range(1, 4):
        # Load Schema 2
        schema_2_file = os.path.join(schema_2_dir, f"C_{n}_gamma.json")
        with open(schema_2_file, 'r') as f:
            schema_2 = json.load(f)

        # Generate Schema 3
        gen = CnPlus1EvaluatedGenerator(n)
        schema_3 = gen.generate_schema_3(schema_2)

        # Save Schema 3
        schema_3_file = os.path.join(output_dir, f"C_{n}_evaluated_gb1.json")
        with open(schema_3_file, 'w') as f:
            json.dump(schema_3, f, indent=2)

        print(f"Generated {schema_3_file}")
        print(f"  Algebra: {gen.algebra_name}")
        print(f"  GB assignment: all +1")
        print(f"  Undeformed brackets: {schema_3['evaluated_structure']['undeformed_brackets_count']}")
        print(f"  Deformed brackets: {schema_3['evaluated_structure']['deformed_brackets_count']}")
        print(f"  Nonzero deformations: {schema_3['deformation_summary']['nonzero_deformations']}")


if __name__ == "__main__":
    generate_all_schema_3()
