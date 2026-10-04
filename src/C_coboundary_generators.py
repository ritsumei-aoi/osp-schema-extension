"""
C_coboundary_generators.py: Computes the coboundary operator delta f for odd linear maps
f: g -> g on C(n+1) = osp(2|2n) and exports Schema 4 JSON files.
"""

from fractions import Fraction
import json
import os
import sys
from typing import Dict, List, Tuple, Any, Optional

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def compute_coboundary_structure(n: int, data_dir: str = "data") -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
    """
    Computes all coboundary coefficients (delta f)(X, Y) for the basis of odd linear maps f: g -> g.
    Formula: (delta f)(X, Y) = (-1)^{p(X)} [X, f(Y)] - (-1)^{(p(X)+1)p(Y)} [Y, f(X)] - f([X, Y])
    """
    struct_path = os.path.join(data_dir, f"C_{n}_structure.json")
    with open(struct_path, "r", encoding="utf-8") as f:
        s1_data = json.load(f)

    basis = s1_data["basis"]["odd"] + s1_data["basis"]["even"]
    parity = s1_data["parity"]

    brackets: Dict[Tuple[str, str], Dict[str, Fraction]] = {}
    for item in s1_data["structure_constants"]:
        x, y, z = item["X"], item["Y"], item["Z"]
        if (x, y) not in brackets:
            brackets[(x, y)] = {}
        brackets[(x, y)][z] = Fraction(item["coeff"])

    def br(v1: Dict[str, Fraction], v2: Dict[str, Fraction]) -> Dict[str, Fraction]:
        res: Dict[str, Fraction] = {}
        for g1, c1 in v1.items():
            for g2, c2 in v2.items():
                pair_br = brackets.get((g1, g2), {})
                for z, cz in pair_br.items():
                    res[z] = res.get(z, Fraction(0)) + c1 * c2 * cz
        return {k: v for k, v in res.items() if v != 0}

    # Generate odd linear map parameter basis: f(src) = dst with p(src) != p(dst)
    phi_params = []
    for src in basis:
        for dst in basis:
            if parity[src] != parity[dst]:
                phi_params.append((src, dst, f"phi_{dst}_{src}"))

    coboundary_structure = []
    for src, dst, pname in phi_params:
        def f_map(v: Dict[str, Fraction]) -> Dict[str, Fraction]:
            if src in v and v[src] != 0:
                return {dst: v[src]}
            return {}

        for x in basis:
            px = parity[x]
            for y in basis:
                py = parity[y]
                sign1 = -1 if px == 1 else 1
                sign2 = -1 if ((px + 1) * py) % 2 == 1 else 1

                # term 1: (-1)^{p(X)} [X, f(Y)]
                fY = f_map({y: Fraction(1)})
                t1 = br({x: Fraction(sign1)}, fY) if fY else {}

                # term 2: - (-1)^{(p(X)+1)p(Y)} [Y, f(X)]
                fX = f_map({x: Fraction(1)})
                t2 = br({y: Fraction(-sign2)}, fX) if fX else {}

                # term 3: - f([X, Y])
                br_xy = brackets.get((x, y), {})
                t3 = {}
                if br_xy:
                    f_br = f_map(br_xy)
                    for k, v in f_br.items():
                        t3[k] = -v

                # total
                tot: Dict[str, Fraction] = {}
                for t in (t1, t2, t3):
                    for z, c in t.items():
                        tot[z] = tot.get(z, Fraction(0)) + c
                tot = {k: v for k, v in tot.items() if v != 0}

                for z in sorted(tot.keys()):
                    c = tot[z]
                    coeff_str = str(c.numerator) if c.denominator == 1 else f"{c.numerator}/{c.denominator}"
                    coboundary_structure.append({
                        "X": x,
                        "Y": y,
                        "Z": z,
                        "phi_param": pname,
                        "coeff": coeff_str
                    })

    param_names = [p[2] for p in phi_params]
    schema_dict = {
        "schema_version": "5.0",
        "algebra": s1_data["algebra"],
        "map_f": {
            "dimension": len(param_names),
            "parameters": param_names,
            "description": "Basis of odd linear maps f: g -> g reversing Z2-parity (Hom_odd(g, g))"
        },
        "coboundary_structure": {
            "formula": "(delta f)(X, Y) = (-1)^{p(X)} [X, f(Y)] - (-1)^{(p(X)+1)p(Y)} [Y, f(X)] - f([X, Y])",
            "terms_count": len(coboundary_structure),
            "terms": coboundary_structure
        },
        "metadata": {
            "generated_by": "src/C_coboundary_generators.py",
            "generation_date": "2026-10-04",
            "references": [
                "docs/math/C_coboundary_definition.md"
            ]
        }
    }
    return coboundary_structure, schema_dict


def save_c_coboundary(n: int, output_dir: str = "data") -> str:
    """Generates and writes C_{n}_coboundary.json to output directory."""
    os.makedirs(output_dir, exist_ok=True)
    _, schema = compute_coboundary_structure(n, data_dir=output_dir)
    filepath = os.path.join(output_dir, f"C_{n}_coboundary.json")
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(schema, f, indent=2)
    return filepath


if __name__ == "__main__":
    for n_val in [1, 2, 3]:
        out_path = save_c_coboundary(n_val)
        print(f"Generated {out_path} for C({n_val+1})")
