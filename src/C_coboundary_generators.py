import os
import sys
import json
from fractions import Fraction
from typing import Dict, List, Tuple, Any

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from src.C_generators import CSuperalgebra


def compute_coboundary(n: int) -> Dict[str, Any]:
    with open(f"data/C_{n}_structure.json", "r") as f:
        s1 = json.load(f)

    basis_odd = s1["basis"]["odd"]
    basis_even = s1["basis"]["even"]
    basis = basis_odd + basis_even
    parity = s1["parity"]

    # Store brackets: (X, Y) -> {Z: coeff}
    brackets: Dict[Tuple[str, str], Dict[str, Fraction]] = {}
    for entry in s1["structure_constants"]:
        key = (entry["X"], entry["Y"])
        brackets.setdefault(key, {})[entry["Z"]] = Fraction(entry["coeff"])

    # Odd linear map f: g -> g
    # Parameterized by phi_{a, b} where p(a) != p(b)
    # f(Z_b) = Z_a
    phi_params = []
    for b in basis:
        for a in basis:
            if parity[a] != parity[b]:
                param_name = f"phi_{a}_{b}"
                phi_params.append({
                    "param": param_name,
                    "source": b,
                    "target": a,
                    "p_source": parity[b],
                    "p_target": parity[a]
                })

    # Compute (delta f_{a, b})(X, Y)
    # delta f(X, Y) = (-1)^pX [X, f(Y)] - (-1)^((pX+1)pY) [Y, f(X)] - f([X, Y])
    coboundary_entries = []

    for p_info in phi_params:
        param = p_info["param"]
        b = p_info["source"]
        a = p_info["target"]

        for X in basis:
            pX = parity[X]
            for Y in basis:
                pY = parity[Y]
                
                res: Dict[str, Fraction] = {}

                # Term 1: (-1)^pX [X, f(Y)] where f(Y) = delta_{Y, b} a
                if Y == b:
                    s1_sign = -1 if (pX == 1) else 1
                    xy_br = brackets.get((X, a), {})
                    for Z, c in xy_br.items():
                        res[Z] = res.get(Z, Fraction(0)) + s1_sign * c

                # Term 2: - (-1)^((pX+1)pY) [Y, f(X)] where f(X) = delta_{X, b} a
                if X == b:
                    s2_sign = -1 if (((pX + 1) * pY) % 2 == 1) else 1
                    yx_br = brackets.get((Y, a), {})
                    for Z, c in yx_br.items():
                        res[Z] = res.get(Z, Fraction(0)) - s2_sign * c

                # Term 3: - f([X, Y])
                # [X, Y] = sum_m C_{XY}^m m, f(m) = delta_{m, b} a
                xy_bracket = brackets.get((X, Y), {})
                if b in xy_bracket:
                    c_b = xy_bracket[b]
                    res[a] = res.get(a, Fraction(0)) - c_b

                for Z, c in res.items():
                    if c != 0:
                        c_str = str(c.numerator) if c.denominator == 1 else f"{c.numerator}/{c.denominator}"
                        coboundary_entries.append({
                            "X": X,
                            "Y": Y,
                            "Z": Z,
                            "phi_param": param,
                            "coeff": c_str
                        })

    return {
        "schema_version": "5.0",
        "algebra": s1["algebra"],
        "linear_map_parameters": {
            "parameter_count": len(phi_params),
            "parameters": [p["param"] for p in phi_params]
        },
        "coboundary_structure": {
            "entry_count": len(coboundary_entries),
            "entries": coboundary_entries
        },
        "metadata": {
            "generated_by": "C_coboundary_generators.py",
            "generation_date": "2026-10-05",
            "formula": "(delta f)(X, Y) = (-1)^p(X) [X, f(Y)] - (-1)^((p(X)+1)p(Y)) [Y, f(X)] - f([X, Y])"
        }
    }


def generate_all_schema4():
    for n in [1, 2, 3]:
        data = compute_coboundary(n)
        out_path = f"data/C_{n}_coboundary.json"
        with open(out_path, "w") as f:
            json.dump(data, f, indent=2)
        print(f"Generated {out_path}: {data['linear_map_parameters']['parameter_count']} phi parameters, {data['coboundary_structure']['entry_count']} coboundary entries.")


if __name__ == "__main__":
    generate_all_schema4()
