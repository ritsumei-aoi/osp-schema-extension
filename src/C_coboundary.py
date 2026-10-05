"""C(n+1) = osp(2|2n) Coboundary Structure (Layer 4) Generator.

This script implements the coboundary operator:
    (delta f)(X, Y) = (-1)^{p(X)} [X, f(Y)] - (-1)^{(p(X)+1)p(Y)} [Y, f(X)] - f([X, Y])
for a canonically parameterized odd linear map f: g -> g that reverses parity,
generating Schema 4 JSON files (data/C_{n}_coboundary.json) for n = 1, 2, 3.
"""

from collections import defaultdict
from fractions import Fraction
import json
import os
import sys
from typing import Any, Dict, List, Tuple

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.C_generators import (
    build_basis,
    build_generator_realizations
)

def build_canonical_odd_map(n: int, even_basis: List[str], odd_basis: List[str]) -> Dict[str, Dict[str, Fraction]]:
    """Define canonical odd linear map f: g -> g reversing parity.
    
    Even generators map to odd generators; odd generators map to even generators.
    """
    f_map: Dict[str, Dict[str, Fraction]] = defaultdict(lambda: defaultdict(Fraction))
    
    # 1. Cartans
    for k in range(1, n + 1):
        f_map["H_1"][f"E_eps1_del{k}_pp"] += 1
        f_map["H_1"][f"E_eps1_del{k}_mm"] += 1
    for k in range(1, n + 1):
        f_map[f"H_{k+1}"][f"E_eps1_del{k}_pm"] += 1
        f_map[f"H_{k+1}"][f"E_eps1_del{k}_mp"] += 1
        
    # 2. Long even roots
    for k in range(1, n + 1):
        f_map[f"E_2del{k}_p"][f"E_eps1_del{k}_pp"] += 1
        f_map[f"E_2del{k}_m"][f"E_eps1_del{k}_mm"] += 1
        
    # 3. Short even roots
    for i in range(1, n + 1):
        for j in range(i + 1, n + 1):
            f_map[f"E_del{i}_del{j}_pp"][f"E_eps1_del{i}_pp"] += 1
            f_map[f"E_del{i}_del{j}_mm"][f"E_eps1_del{i}_mm"] += 1
            f_map[f"E_del{i}_del{j}_pm"][f"E_eps1_del{i}_pm"] += 1
            f_map[f"E_del{i}_del{j}_mp"][f"E_eps1_del{i}_mp"] += 1
            
    # 4. Odd roots
    for k in range(1, n + 1):
        f_map[f"E_eps1_del{k}_pp"][f"E_2del{k}_p"] += 1
        f_map[f"E_eps1_del{k}_mm"][f"E_2del{k}_m"] += 1
        f_map[f"E_eps1_del{k}_pm"][f"H_{k+1}"] += 1
        f_map[f"E_eps1_del{k}_mp"]["H_1"] += 1
        
    return {k: dict(v) for k, v in f_map.items()}

def compute_coboundary_structure(n: int, data_dir: str = "data") -> Dict[str, Any]:
    """Compute Layer 4 coboundary data for rank n."""
    s1_path = os.path.join(data_dir, f"C_{n}_structure.json")
    with open(s1_path, "r") as f:
        d1 = json.load(f)
        
    basis = d1["basis"]["even"] + d1["basis"]["odd"]
    parities = d1["parity"]
    
    # Structure constant lookup
    bracket_table: Dict[Tuple[str, str], Dict[str, Fraction]] = defaultdict(dict)
    for entry in d1["structure_constants"]:
        bracket_table[(entry["X"], entry["Y"])][entry["Z"]] = Fraction(entry["coeff"])
        
    def bracket(x: str, y: str) -> Dict[str, Fraction]:
        return bracket_table.get((x, y), {})
        
    def bracket_poly(gen: str, poly: Dict[str, Fraction]) -> Dict[str, Fraction]:
        res: Dict[str, Fraction] = defaultdict(Fraction)
        for w, c in poly.items():
            for z, br_c in bracket(gen, w).items():
                res[z] += c * br_c
        return {k: v for k, v in res.items() if v != 0}

    f_map = build_canonical_odd_map(n, d1["basis"]["even"], d1["basis"]["odd"])
    
    def apply_f(poly: Dict[str, Fraction]) -> Dict[str, Fraction]:
        res: Dict[str, Fraction] = defaultdict(Fraction)
        for g, c in poly.items():
            for target, fc in f_map.get(g, {}).items():
                res[target] += c * fc
        return {k: v for k, v in res.items() if v != 0}

    coboundary_entries = []
    
    for x in basis:
        px = parities[x]
        for y in basis:
            py = parities[y]
            
            # (delta f)(X, Y) = (-1)^{p(X)} [X, f(Y)] - (-1)^{(p(X)+1)p(Y)} [Y, f(X)] - f([X, Y])
            s1 = (-1) ** px
            t1 = bracket_poly(x, f_map.get(y, {}))
            
            s2 = - ((-1) ** ((px + 1) * py))
            t2 = bracket_poly(y, f_map.get(x, {}))
            
            t3 = apply_f(bracket(x, y))
            
            res: Dict[str, Fraction] = defaultdict(Fraction)
            for z, c in t1.items():
                res[z] += s1 * c
            for z, c in t2.items():
                res[z] += s2 * c
            for z, c in t3.items():
                res[z] -= c
                
            for z, c in sorted(res.items()):
                if c != 0:
                    coboundary_entries.append({
                        "X": x,
                        "Y": y,
                        "Z": z,
                        "coeff": str(c.numerator) if c.denominator == 1 else f"{c.numerator}/{c.denominator}"
                    })

    # Prepare string representation for f_map JSON
    f_map_json = {}
    for g, targets in sorted(f_map.items()):
        f_map_json[g] = {tgt: str(c) for tgt, c in sorted(targets.items())}

    schema_4 = {
        "schema_version": "5.0",
        "layer": 4,
        "algebra": d1["algebra"],
        "basis": d1["basis"],
        "parity": d1["parity"],
        "odd_linear_map_f": {
            "description": "Canonical odd linear map f: g -> g reversing parity p(f(X)) = 1 - p(X)",
            "map_table": f_map_json
        },
        "coboundary_operator": {
            "description": "(delta f)(X, Y) = (-1)^{p(X)} [X, f(Y)] - (-1)^{(p(X)+1)p(Y)} [Y, f(X)] - f([X, Y])",
            "sign_rule": "graded",
            "total_entries": len(coboundary_entries),
            "coboundary_coefficients": coboundary_entries
        },
        "metadata": {
            "generated_by": "src/C_coboundary.py",
            "generation_date": "2026-10-05",
            "references": [
                "docs/math/C_coboundary_definition.md"
            ]
        }
    }
    
    return schema_4

def generate_all_schema_4(output_dir: str = "data"):
    """Generate C_1_coboundary.json, C_2_coboundary.json, and C_3_coboundary.json."""
    os.makedirs(output_dir, exist_ok=True)
    for n in [1, 2, 3]:
        schema_4 = compute_coboundary_structure(n, data_dir=output_dir)
        filepath = os.path.join(output_dir, f"C_{n}_coboundary.json")
        with open(filepath, "w") as f:
            json.dump(schema_4, f, indent=2)
        print(f"Generated {filepath}: {len(schema_4['odd_linear_map_f']['map_table'])} generators mapped, "
              f"{schema_4['coboundary_operator']['total_entries']} non-zero coboundary coefficients")

if __name__ == "__main__":
    generate_all_schema_4()
