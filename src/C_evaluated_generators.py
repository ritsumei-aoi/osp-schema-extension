import json
import os
from fractions import Fraction
from collections import defaultdict
from typing import List, Dict, Any

class CEvaluatedGenerator:
    def __init__(self, n: int, profile_label: str = "pos"):
        self.n = n
        self.profile_label = profile_label
        self.s1_path = f"data/C_{n}_structure.json"
        self.s2_path = f"data/C_{n}_gamma.json"
        self.output_path = f"data/C_{n}_evaluated_{profile_label}.json"

    def load_data(self):
        with open(self.s1_path, 'r') as f:
            self.s1 = json.load(f)
        with open(self.s2_path, 'r') as f:
            self.s2 = json.load(f)

    def get_assignment(self) -> Dict[str, int]:
        assignment = {}
        for param in self.s2['inhomogeneous_deformation']['parameters']:
            if self.profile_label == "pos":
                assignment[param] = 1
            else:
                # Default fallback or logic for other profiles can be added here
                assignment[param] = 1
        return assignment

    def evaluate(self):
        self.load_data()
        assignment = self.get_assignment()
        
        # Deformed structure constant map: (X, Y, Z) -> total_coeff
        # f_abc_total = f_abc_0 + kappa * gamma_abc
        # Since Schema 3 typically records the full coefficients of each generator Z in [X, Y],
        # and kappa is central, we treat kappa as a formal parameter.
        # In this project's architecture, Schema 3 usually stores components separately:
        # "structure_constants": base constants
        # "deformation_constants": evaluated gamma components
        
        evaluated_gamma = defaultdict(Fraction)
        for entry in self.s2['inhomogeneous_deformation']['gamma_structure']:
            X, Y, Z = entry['X'], entry['Y'], entry['Z']
            param = entry['parameter']
            coeff = Fraction(entry['coeff'])
            
            val = coeff * assignment[param]
            evaluated_gamma[(X, Y, Z)] += val

        gamma_list = []
        for (X, Y, Z), val in evaluated_gamma.items():
            if val != 0:
                gamma_list.append({
                    "X": X,
                    "Y": Y,
                    "Z": Z,
                    "coeff": str(val)
                })

        # Sort for consistency
        gamma_list.sort(key=lambda x: (x['X'], x['Y'], x['Z']))

        data = {
            "schema_version": "5.0",
            "algebra": self.s1['algebra'],
            "evaluation_metadata": {
                "profile": self.profile_label,
                "assignment": assignment,
                "generated_by": "C_evaluated_generators.py"
            },
            "base_structure_constants": self.s1['structure_constants'],
            "evaluated_gamma_structure": gamma_list,
            "parity": self.s1['parity'],
            "basis": self.s1['basis']
        }

        with open(self.output_path, 'w') as f:
            json.dump(data, f, indent=2)
        print(f"Generated {self.output_path}")

if __name__ == "__main__":
    for n in [1, 2, 3]:
        gen = CEvaluatedGenerator(n, "pos")
        if os.path.exists(f"data/C_{n}_gamma.json"):
            gen.evaluate()
        else:
            print(f"Skipping n={n}: Gamma file not found.")
