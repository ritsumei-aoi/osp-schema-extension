"""
Schema 3 (evaluated structure) generator for C(n+1) = osp(2|2n).

Substitutes specific gb parameter values into symbolic gamma structure (Schema 2)
to produce evaluated structure constants.

Author: Claude Haiku 4.5
"""

import json
from datetime import date
from fractions import Fraction


class CnEvaluatedGenerator:
    """Generates Schema 3 (evaluated structure) for C(n+1)."""

    def __init__(self, n, schema2_file, gb_assignment=None):
        self.n = n
        self.schema2_file = schema2_file
        self.schema2 = self._load_schema2()
        self.gb_assignment = gb_assignment or self._default_gb_assignment()

    def _load_schema2(self):
        """Load the corresponding Schema 2 file."""
        with open(self.schema2_file, "r") as f:
            return json.load(f)

    def _default_gb_assignment(self):
        """
        Default assignment: all gb parameters set to +1.

        This is a canonical choice that evaluates the deformed structure
        at a symmetric point in parameter space.
        """
        assignment = {}
        for param in self.schema2["deformation_parameters"]["gb_matrix"]["parameters"]:
            label = param["label"]
            assignment[label] = 1
        return assignment

    def _substitute_gamma_terms(self):
        """
        Substitute gb parameter values into symbolic gamma terms.

        Converts symbolic references like "gb_a1_p_b1_p" to their numerical values.
        """
        evaluated_terms = []

        for term in self.schema2["inhomogeneous_deformation"]["gamma_terms"]:
            X = term["X"]
            Y = term["Y"]
            Z = term["Z"]
            gamma_coeff_str = term["gamma_coeff"]

            if gamma_coeff_str.startswith("gb_"):
                param_label = gamma_coeff_str
                if param_label in self.gb_assignment:
                    coeff = Fraction(self.gb_assignment[param_label])
                else:
                    coeff = Fraction(1)
            elif gamma_coeff_str.startswith("-gb_"):
                param_label = gamma_coeff_str[1:]
                if param_label in self.gb_assignment:
                    coeff = -Fraction(self.gb_assignment[param_label])
                else:
                    coeff = Fraction(-1)
            else:
                try:
                    coeff = Fraction(gamma_coeff_str)
                except:
                    coeff = Fraction(0)

            if coeff != 0:
                evaluated_terms.append({
                    "X": X,
                    "Y": Y,
                    "Z": Z,
                    "coeff": str(coeff),
                    "assignment": gamma_coeff_str,
                    "sign_rule": "graded"
                })

        return evaluated_terms

    def to_json(self):
        """Generate complete Schema 3 JSON."""
        schema2 = self.schema2
        evaluated_structure = self._substitute_gamma_terms()

        schema3 = {
            "schema_version": "5.0",
            "schema_layer": 3,
            "schema_name": "evaluated_structure",
            "algebra": schema2["algebra"],
            "oscillator_generators": schema2["oscillator_generators"],
            "oscillator_relations": schema2["oscillator_relations"],
            "central_elements": schema2["central_elements"],
            "deformation_parameters": schema2["deformation_parameters"],
            "gb_assignment": {
                "description": "Specific numerical values for deformation parameters",
                "type": "canonical",
                "assignment_label": "gb = +1 (symmetric point)",
                "values": self.gb_assignment
            },
            "evaluated_bracket": {
                "description": "Deformed bracket with gb parameters substituted",
                "bracket_form": "[X, Y]_evaluated = [X, Y]_0 + κ · γ_evaluated(X, Y)",
                "structure_constants": evaluated_structure
            },
            "schema2_reference": {
                "file": self.schema2_file,
                "generation_date": schema2["metadata"]["generation_date"]
            },
            "metadata": {
                "generated_by": "src/C_evaluated_generator.py",
                "generation_date": str(date.today()),
                "schema_version": "5.0",
                "schema_layer": 3,
                "evaluation_point": "gb = +1",
                "notes": "Schema 3 evaluates the deformed structure at a specific point in the gb-parameter space",
                "references": [
                    "Frappat, Sciarrino, Sorba (2000), Dictionary on Lie Algebras and Superalgebras",
                    "C_inhomogeneous_definition.md"
                ]
            }
        }

        return schema3


def generate_all_schema3_files(output_dir="data"):
    """Generate Schema 3 JSON files for n=1, 2, 3."""
    for n in [1, 2, 3]:
        schema2_file = f"{output_dir}/C_{n}_gamma.json"
        gen = CnEvaluatedGenerator(n, schema2_file)
        schema3 = gen.to_json()

        filename = f"{output_dir}/C_{n}_evaluated.json"
        with open(filename, "w") as f:
            json.dump(schema3, f, indent=2)
        print(f"Generated {filename}")


if __name__ == "__main__":
    import sys
    import os

    output_dir = sys.argv[1] if len(sys.argv) > 1 else "data"

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    generate_all_schema3_files(output_dir)
    print("Schema 3 generation complete.")
