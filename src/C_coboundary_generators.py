import json
import os
from fractions import Fraction
from collections import defaultdict
from typing import List, Dict, Any

class CCoboundaryGenerator:
    def __init__(self, n: int, map_label: str = "cartan"):
        self.n = n
        self.map_label = map_label
        self.s1_path = f"data/C_{n}_structure.json"
        self.output_path = f"data/C_{n}_coboundary_{map_label}.json"

    def load_schema1(self) -> Dict[str, Any]:
        if not os.path.exists(self.s1_path):
            raise FileNotFoundError(f"Schema 1 file not found: {self.s1_path}")
        with open(self.s1_path, 'r') as f:
            return json.load(f)

    def get_map_definition(self, basis_even: List[str], basis_odd: List[str]) -> Dict[str, int]:
        phi = {}
        # Default all to 0
        all_gens = basis_even + basis_odd + ["K"]
        for gen in all_gens:
            phi[gen] = 0
            
        if self.map_label == "cartan":
            # f(H_k) = 1, f(K) = 1
            for gen in basis_even:
                if gen.startswith("H_"):
                    phi[gen] = 1
            phi["K"] = 1
        return phi

    def compute(self):
        s1 = self.load_schema1()
        basis_even = s1['basis']['even']
        basis_odd = s1['basis']['odd']
        phi = self.get_map_definition(basis_even, basis_odd)
        
        # gamma_f(X, Y) = f([X, Y]_0) = sum_c f(Z_c) * C_{XY}^c
        # results[(X, Y, Z_res)] = total_coeff
        # Note: In Layer 4, we technically map to scalars, 
        # but the JSON Schema 4 "Coboundary Matrix" usually records 
        # the coefficients of the reference 2-cocycle.
        # Since gamma_f is a map G x G -> R (scalars), 
        # we store it as a list of entries with Z="K" (central identity) 
        # to represent the scalar result in the algebra extension context.
        
        coboundary_results = defaultdict(Fraction)
        
        for entry in s1['structure_constants']:
            X, Y, Z = entry['X'], entry['Y'], entry['Z']
            coeff = Fraction(entry['coeff'])
            
            # contribution = phi(Z) * coeff
            # Resulting Z in coboundary is always "K" (scalar part)
            val = coeff * phi[Z]
            if val != 0:
                coboundary_results[(X, Y)] += val

        gamma_f_list = []
        for (X, Y), val in coboundary_results.items():
            if val != 0:
                gamma_f_list.append({
                    "X": X,
                    "Y": Y,
                    "Z": "K", # Resulting scalar value associated with identity
                    "coeff": str(val)
                })

        # Sort for consistency
        gamma_f_list.sort(key=lambda x: (x['X'], x['Y']))

        data = {
            "schema_version": "5.0",
            "algebra": s1['algebra'],
            "map_definition": {k: v for k, v in phi.items() if v != 0},
            "coboundary_metadata": {
                "label": self.map_label,
                "formula": "gamma_f(X, Y) = f([X, Y]_0)",
                "generated_by": "C_coboundary_generators.py"
            },
            "coboundary_structure": gamma_f_list
        }

        os.makedirs("data", exist_ok=True)
        with open(self.output_path, 'w') as f:
            json.dump(data, f, indent=2)
        print(f"Generated {self.output_path}")

if __name__ == "__main__":
    for n in [1, 2, 3]:
        try:
            gen = CCoboundaryGenerator(n, "cartan")
            gen.compute()
        except FileNotFoundError as e:
            print(f"Skipping n={n}: {e}")
