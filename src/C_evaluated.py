"""
C_evaluated.py — Schema 3 (Evaluated Structure) generator for C(n+1) = osp(2|2n).

Substitutes concrete gb parameter values into the Schema 2 gamma matrix and
combines with Schema 1 structure constants to produce the full deformed algebra
structure constants at specific parameter values.

Deformed bracket:  [X, Y]_gamma = [X, Y]_0  +  kappa · gamma(X, Y)|_{gb=specific}

Schema 3 encodes both sectors in a single list with a "part" discriminator:
  "body":  coefficients of Z    in [X, Y]_0           (Schema 1, gb-independent)
  "kappa": coefficients of κ·Z  in κ·gamma(X,Y)       (Schema 2, gb-dependent)

For profile gb0 (all gb = 0): kappa entries are absent; Schema 3 body == Schema 1.
For profile gb1 (all gb = 1): body unchanged; kappa entries are fully populated.
"""

import json
import sys
import os
from fractions import Fraction
from datetime import date
from typing import Callable, Dict, List, Tuple


# ---------------------------------------------------------------------------
# gb profiles
# ---------------------------------------------------------------------------

PROFILES: Dict[str, dict] = {
    "gb0": {
        "description": (
            "All 4n gb parameters set to 0 "
            "(trivial deformation; evaluated structure = Schema 1)"
        ),
        "value": Fraction(0),
    },
    "gb1": {
        "description": (
            "All 4n gb parameters set to +1 "
            "(uniform non-trivial deformation)"
        ),
        "value": Fraction(1),
    },
}


# ---------------------------------------------------------------------------
# Core evaluation
# ---------------------------------------------------------------------------

def _evaluate_gamma(
    gamma_matrix: List[dict], gb_value: Fraction
) -> List[dict]:
    """
    Evaluate gamma matrix entries at a uniform gb value (all parameters equal).

    For each (X, Y, Z) triple, sums contributions across all gb parameters:
        coeff_evaluated = sum_{gb} coeff[gb] * gb_value

    Returns list of {X, Y, Z, coeff} entries with non-zero rational coefficients.
    """
    acc: Dict[Tuple[str, str, str], Fraction] = {}
    for entry in gamma_matrix:
        x, y, z = entry["X"], entry["Y"], entry["Z"]
        total = Fraction(0)
        for coeff_str in entry["coeff"].values():
            total += Fraction(coeff_str) * gb_value
        if total != 0:
            key = (x, y, z)
            acc[key] = acc.get(key, Fraction(0)) + total

    result = []
    for (x, y, z), coeff in acc.items():
        if coeff != 0:
            result.append({"X": x, "Y": y, "Z": z, "coeff": str(coeff)})
    return result


def build_schema3(n: int, profile_name: str) -> dict:
    """Build Schema 3 JSON for C(n+1) at a specific gb profile."""
    profile = PROFILES[profile_name]
    gb_value = profile["value"]

    with open(f"data/C_{n}_structure.json") as f:
        s1 = json.load(f)
    with open(f"data/C_{n}_gamma.json") as f:
        s2 = json.load(f)

    gd = s2["inhomogeneous_deformation"]

    # Collect all gb parameter labels from the gamma matrix
    all_gb_labels: List[str] = list(
        gd["gb_matrix"]["entries"][0] + gd["gb_matrix"]["entries"][1]
    )
    gb_assignment_values = {label: str(gb_value) for label in all_gb_labels}

    # Body entries: pass Schema 1 structure constants through unchanged
    body_entries = [
        {
            "X": sc["X"],
            "Y": sc["Y"],
            "Z": sc["Z"],
            "coeff": sc["coeff"],
            "part": "body",
            "sign_rule": sc.get("sign_rule", "graded"),
        }
        for sc in s1["structure_constants"]
    ]

    # Kappa entries: evaluate gamma at the given gb_value
    kappa_raw = _evaluate_gamma(gd["gamma_matrix"], gb_value)
    kappa_entries = [
        {
            "X": e["X"],
            "Y": e["Y"],
            "Z": e["Z"],
            "coeff": e["coeff"],
            "part": "kappa",
            "sign_rule": "graded",
        }
        for e in kappa_raw
    ]

    evaluated = body_entries + kappa_entries

    return {
        "schema_version": "5.0",
        "schema_layer": 3,
        "algebra": s1["algebra"],
        "gb_assignment": {
            "profile": profile_name,
            "description": profile["description"],
            "values": gb_assignment_values,
        },
        "evaluated_structure_constants": evaluated,
        "entry_count": {
            "body": len(body_entries),
            "kappa": len(kappa_entries),
            "total": len(evaluated),
        },
        "metadata": {
            "generated_by": "C_evaluated.py",
            "generation_date": date.today().isoformat(),
            "issue": "I06-1",
            "source_schema1": f"C_{n}_structure.json",
            "source_schema2": f"C_{n}_gamma.json",
        },
    }


# ---------------------------------------------------------------------------
# Consistency verification
# ---------------------------------------------------------------------------

def _verify_gb0(n: int, schema3: dict) -> bool:
    """
    Verify that the gb0 profile:
    1. Has zero kappa entries (no deformation).
    2. Body entries match Schema 1 structure constants exactly.
    """
    ok = True

    kappa_count = schema3["entry_count"]["kappa"]
    if kappa_count != 0:
        print(f"    [FAIL] gb0 has {kappa_count} kappa entries (expected 0)")
        ok = False

    with open(f"data/C_{n}_structure.json") as f:
        s1 = json.load(f)

    s1_set = {
        (sc["X"], sc["Y"], sc["Z"], sc["coeff"])
        for sc in s1["structure_constants"]
    }
    s3_body_set = {
        (e["X"], e["Y"], e["Z"], e["coeff"])
        for e in schema3["evaluated_structure_constants"]
        if e["part"] == "body"
    }

    if s1_set != s3_body_set:
        diff = s1_set.symmetric_difference(s3_body_set)
        print(
            f"    [FAIL] gb0 body ≠ Schema 1 "
            f"(|s1|={len(s1_set)}, |s3_body|={len(s3_body_set)}, "
            f"|diff|={len(diff)})"
        )
        for item in list(diff)[:3]:
            print(f"           diff item: {item}")
        ok = False

    return ok


def _verify_gb1_body(n: int, schema3: dict) -> bool:
    """
    Verify that gb1 body entries are identical to Schema 1
    (the deformation only adds kappa terms, not modifying body terms).
    """
    with open(f"data/C_{n}_structure.json") as f:
        s1 = json.load(f)

    s1_set = {
        (sc["X"], sc["Y"], sc["Z"], sc["coeff"])
        for sc in s1["structure_constants"]
    }
    s3_body_set = {
        (e["X"], e["Y"], e["Z"], e["coeff"])
        for e in schema3["evaluated_structure_constants"]
        if e["part"] == "body"
    }

    if s1_set != s3_body_set:
        print(
            f"    [FAIL] gb1 body entries ≠ Schema 1 "
            f"(|s1|={len(s1_set)}, |s3_body|={len(s3_body_set)})"
        )
        return False
    return True


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main() -> None:
    os.makedirs("data", exist_ok=True)
    all_ok = True

    for n in (1, 2, 3):
        for profile_name in PROFILES:
            schema = build_schema3(n, profile_name)
            path = f"data/C_{n}_evaluated_{profile_name}.json"
            with open(path, "w") as f:
                json.dump(schema, f, indent=2)

            ec = schema["entry_count"]
            print(
                f"C({n + 1}) n={n} {profile_name}: "
                f"body={ec['body']}  kappa={ec['kappa']}  total={ec['total']}"
                f"  -> {path}"
            )

            if profile_name == "gb0":
                ok = _verify_gb0(n, schema)
                print(f"    {'[OK] gb0 consistency check passed' if ok else '[ERROR] FAILED'}")
                if not ok:
                    all_ok = False
            elif profile_name == "gb1":
                ok = _verify_gb1_body(n, schema)
                print(f"    {'[OK] gb1 body check passed' if ok else '[ERROR] gb1 body FAILED'}")
                if not ok:
                    all_ok = False

    if not all_ok:
        sys.exit(1)

    print("\nAll Schema 3 files generated and verified successfully.")


if __name__ == "__main__":
    main()
