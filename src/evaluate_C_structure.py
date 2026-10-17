"""
C(n+1) = osp(2|2n) Evaluated Structure (Schema 3) Generator
Substitutes concrete sign profiles into gb matrix parameters and generates Schema 3 JSON.
"""

import json
import os
import sys
import argparse
from fractions import Fraction
from collections import defaultdict
from typing import Dict, Any, Tuple

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DATA_DIR = os.path.join(REPO_ROOT, "data")

PROFILES = {
    "all_plus": {
        "description": "Canonical uniform evaluation profile with all gb parameters set to +1",
        "func": lambda sigma, j, s: 1
    },
    "fermion_alternating": {
        "description": "Chiral fermionic sign profile: +1 for a_1^+, -1 for a_1^-",
        "func": lambda sigma, j, s: 1 if sigma == 'p' else -1
    },
    "boson_alternating": {
        "description": "Bosonic sign profile: +1 for b_j^+, -1 for b_j^-",
        "func": lambda sigma, j, s: 1 if s == 'p' else -1
    },
    "mode_alternating": {
        "description": "Mode parity profile: alternating signs (-1)^(j-1) across modes",
        "func": lambda sigma, j, s: 1 if (j % 2 == 1) else -1
    }
}

def get_profile_dict(n: int, profile_name: str) -> Tuple[Dict[str, int], str]:
    if profile_name not in PROFILES:
        raise ValueError(f"Unknown profile '{profile_name}'. Available: {list(PROFILES.keys())}")
    
    spec = PROFILES[profile_name]
    func = spec["func"]
    profile_dict = {}
    for sigma in ['p', 'm']:
        for j in range(1, n + 1):
            for s in ['p', 'm']:
                param = f"gb_a1{sigma}_b{j}{s}"
                profile_dict[param] = func(sigma, j, s)
    return profile_dict, spec["description"]

def build_schema3_json(n: int, profile_name: str = "all_plus") -> Dict[str, Any]:
    structure_file = os.path.join(DATA_DIR, f"C_{n}_structure.json")
    gamma_file = os.path.join(DATA_DIR, f"C_{n}_gamma.json")

    if not os.path.exists(structure_file):
        raise FileNotFoundError(f"Missing Schema 1 file: {structure_file}")
    if not os.path.exists(gamma_file):
        raise FileNotFoundError(f"Missing Schema 2 file: {gamma_file}")

    with open(structure_file, "r", encoding="utf-8") as f:
        s1 = json.load(f)
    with open(gamma_file, "r", encoding="utf-8") as f:
        s2 = json.load(f)

    profile_dict, profile_desc = get_profile_dict(n, profile_name)

    all_basis = s1["basis"]["even"] + s1["basis"]["odd"]
    basis_idx = {g: idx for idx, g in enumerate(all_basis)}

    # 1. Base structure constants from Schema 1: (X, Y, Z) -> Fraction
    base_brackets = defaultdict(Fraction)
    for entry in s1["structure_constants"]:
        base_brackets[(entry["X"], entry["Y"], entry["Z"])] = Fraction(entry["coeff"])

    # 2. Evaluate gamma structure constants from Schema 2: (X, Y, Z) -> Fraction
    eval_gamma = defaultdict(Fraction)
    for entry in s2["inhomogeneous_deformation"]:
        X, Y, Z = entry["X"], entry["Y"], entry["Z"]
        param = entry["param"]
        coeff = Fraction(entry["coeff"])
        val = profile_dict[param]
        eval_gamma[(X, Y, Z)] += coeff * val

    # Build evaluated_deformation list (non-zero gamma brackets)
    evaluated_deformation = []
    for (X, Y, Z), coeff in eval_gamma.items():
        if coeff != 0:
            coeff_str = str(coeff) if coeff.denominator == 1 else f"{coeff.numerator}/{coeff.denominator}"
            evaluated_deformation.append({
                "X": X,
                "Y": Y,
                "Z": Z,
                "coeff": coeff_str,
                "sign_rule": "graded"
            })

    evaluated_deformation.sort(key=lambda e: (basis_idx[e["X"]], basis_idx[e["Y"]], basis_idx[e["Z"]]))

    # Build deformed_structure_constants list: union of all non-zero base or gamma brackets
    all_triples = set(base_brackets.keys()) | set(k for k, v in eval_gamma.items() if v != 0)
    sorted_triples = sorted(all_triples, key=lambda t: (basis_idx[t[0]], basis_idx[t[1]], basis_idx[t[2]]))

    deformed_structure_constants = []
    for (X, Y, Z) in sorted_triples:
        c_base = base_brackets[(X, Y, Z)]
        c_kappa = eval_gamma[(X, Y, Z)]
        c_base_str = str(c_base) if c_base.denominator == 1 else f"{c_base.numerator}/{c_base.denominator}"
        c_kappa_str = str(c_kappa) if c_kappa.denominator == 1 else f"{c_kappa.numerator}/{c_kappa.denominator}"
        deformed_structure_constants.append({
            "X": X,
            "Y": Y,
            "Z": Z,
            "coeff_base": c_base_str,
            "coeff_kappa": c_kappa_str,
            "sign_rule": "graded"
        })

    return {
        "schema_version": "5.0",
        "algebra": s1["algebra"],
        "central_elements": s1["central_elements"],
        "basis": s1["basis"],
        "parity": s1["parity"],
        "evaluation_profile": {
            "name": profile_name,
            "description": profile_desc,
            "parameters": {p: str(val) for p, val in profile_dict.items()}
        },
        "evaluated_deformation": evaluated_deformation,
        "deformed_structure_constants": deformed_structure_constants,
        "metadata": {
            "generated_by": "src/evaluate_C_structure.py",
            "generation_date": "2026-10-17",
            "source_structure_file": f"data/C_{n}_structure.json",
            "source_gamma_file": f"data/C_{n}_gamma.json",
            "references": [
                "Frappat et al. (2000), Dictionary on Lie Algebras and Superalgebras",
                "Bakalov and Sullivan (2017)",
                "docs/math/C_inhomogeneous_definition.md"
            ]
        }
    }

def main():
    parser = argparse.ArgumentParser(description="Generate Schema 3 Evaluated Structure JSON for C(n+1)")
    parser.add_argument("--profile", default="all_plus", choices=list(PROFILES.keys()),
                        help="Sign profile to evaluate (default: all_plus)")
    parser.add_argument("--ranks", nargs="+", type=int, default=[1, 2, 3],
                        help="Bosonic ranks n to evaluate (default: 1 2 3)")
    args = parser.parse_args()

    os.makedirs(DATA_DIR, exist_ok=True)
    for n in args.ranks:
        data = build_schema3_json(n, profile_name=args.profile)
        
        # Primary file: C_{n}_evaluated.json
        primary_file = os.path.join(DATA_DIR, f"C_{n}_evaluated.json")
        with open(primary_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

        # Profile-specific file: C_{n}_evaluated_{profile}.json
        profile_file = os.path.join(DATA_DIR, f"C_{n}_evaluated_{args.profile}.json")
        with open(profile_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

        print(f"Generated {primary_file} & {profile_file}:")
        print(f"  - Profile: {args.profile}")
        print(f"  - Non-zero evaluated gamma brackets: {len(data['evaluated_deformation'])}")
        print(f"  - Total deformed structure constants: {len(data['deformed_structure_constants'])}")

if __name__ == "__main__":
    main()
