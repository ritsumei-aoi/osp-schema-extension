import json
import os
from fractions import Fraction
from collections import defaultdict
from typing import List, Dict, Any, Tuple

class CCoboundaryGenerator:
    def __init__(self, n: int):
        self.n = n
        self.s1_path = f"data/C_{n}_structure.json"
        self.output_path = f"data/C_{n}_coboundary.json"

    def load_schema1(self) -> Dict[str, Any]:
        if not os.path.exists(self.s1_path):
            raise FileNotFoundError(f"Schema 1 file not found: {self.s1_path}")
        with open(self.s1_path, 'r') as f:
            return json.load(f)

    def get_odd_map_f(self, basis_even: List[str], basis_odd: List[str]) -> Dict[str, Dict[str, Fraction]]:
        """
        f: g -> g (odd map)
        Returns a dict: source_gen -> {target_gen: coeff}
        """
        f_map = defaultdict(dict)
        
        # Approved Configuration:
        # Even -> Odd: f(H_k) = E_eps1_del1_pp, f(K) = E_eps1_del1_pp
        for gen in basis_even:
            if gen.startswith("H_"):
                f_map[gen]["E_eps1_del1_pp"] = Fraction(1)
        f_map["K"]["E_eps1_del1_pp"] = Fraction(1)
        
        # Odd -> Even: f(E_eps1_del1_pp) = K
        f_map["E_eps1_del1_pp"]["K"] = Fraction(1)
        
        return f_map

    def compute(self):
        s1 = self.load_schema1()
        basis_even = s1['basis']['even']
        basis_odd = s1['basis']['odd']
        all_basis = basis_odd + basis_even + ["K"]
        parity = s1['parity']
        if "K" not in parity: parity["K"] = 0
        
        f_map = self.get_odd_map_f(basis_even, basis_odd)
        
        # Structure constants map: (X, Y) -> {Z: coeff}
        sc = defaultdict(dict)
        for entry in s1['structure_constants']:
            X, Y, Z = entry['X'], entry['Y'], entry['Z']
            sc[(X, Y)][Z] = Fraction(entry['coeff'])

        def get_bracket(X: str, Y: str) -> Dict[str, Fraction]:
            if (X, Y) in sc: return sc[(X, Y)]
            pX, pY = parity[X], parity[Y]
            sign = -1 if (pX == 1 and pY == 1) else 1
            if (Y, X) in sc:
                return {Z: -val * sign for Z, val in sc[(Y, X)].items()}
            return {}

        def apply_f(X: str) -> Dict[str, Fraction]:
            return f_map.get(X, {})

        # (delta f)(X, Y) = (-1)^pX [X, f(Y)] - (-1)^{(pX+1)pY} [Y, f(X)] - f([X, Y])
        coboundary_matrix = []

        for i, X in enumerate(all_basis):
            for j, Y in enumerate(all_basis):
                pX, pY = parity[X], parity[Y]
                
                # Term 1: (-1)^pX [X, f(Y)]
                t1 = defaultdict(Fraction)
                s1_val = -1 if pX == 1 else 1
                fY = apply_f(Y)
                for W, cW in fY.items():
                    br = get_bracket(X, W)
                    for Z, cZ in br.items():
                        t1[Z] += s1_val * cW * cZ

                # Term 2: - (-1)^{(pX+1)pY} [Y, f(X)]
                t2 = defaultdict(Fraction)
                s2_val = - (-1 if ((pX + 1) == 1 and pY == 1) else 1)
                fX = apply_f(X)
                for W, cW in fX.items():
                    br = get_bracket(Y, W)
                    for Z, cZ in br.items():
                        t2[Z] += s2_val * cW * cZ

                # Term 3: - f([X, Y])
                t3 = defaultdict(Fraction)
                brXY = get_bracket(X, Y)
                for Z, cZ in brXY.items():
                    fZ = apply_f(Z)
                    for W, cW in fZ.items():
                        t3[W] -= cZ * cW

                # Aggregate
                total = defaultdict(Fraction)
                for Z, val in t1.items(): total[Z] += val
                for Z, val in t2.items(): total[Z] += val
                for Z, val in t3.items(): total[Z] += val

                for Z, val in total.items():
                    if val != 0:
                        coboundary_matrix.append({
                            "X": X, "Y": Y, "Z": Z, "coeff": str(val)
                        })

        data = {
            "schema_version": "5.0",
            "algebra": s1['algebra'],
            "map_definition": {k: {tk: str(tv) for tk, tv in v.items()} for k, v in f_map.items()},
            "coboundary_metadata": {
                "formula": "(delta f)(X, Y) = (-1)^pX [X, f(Y)] - (-1)^{(pX+1)pY} [Y, f(X)] - f([X, Y])",
                "generated_by": "C_coboundary_generators.py",
                "f_parity": 1
            },
            "coboundary_structure": coboundary_matrix
        }

        with open(self.output_path, 'w') as f:
            json.dump(data, f, indent=2)
        print(f"Generated {self.output_path}")

if __name__ == "__main__":
    for n in [1, 2, 3]:
        try:
            gen = CCoboundaryGenerator(n)
            gen.compute()
        except FileNotFoundError as e:
            print(f"Skipping n={n}: {e}")
