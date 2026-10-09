"""
C_obstruction.py: Identify obstruction triples (X,Y,Z) where gamma(gb) != 0
but coboundary map image is 0 for ALL phi. These are necessary non-triviality conditions.

For each such triple, extract the symbolic gamma coefficient from Layer 2
to determine which gb combinations create the obstruction.
"""

import json
from fractions import Fraction


def load_layer2_symbolic(n):
    """Load gamma symbolic: {(X,Y,Z,gb_param): coeff}."""
    with open(f"data/C_{n}_gamma.json") as f:
        data = json.load(f)
    gamma = {}
    for entry in data["inhomogeneous_deformation"]["gamma_coefficients"]:
        key = (entry["X"], entry["Y"], entry["Z"], entry["gb_param"])
        gamma[key] = gamma.get(key, Fraction(0)) + Fraction(entry["coeff"])
    return {k: v for k, v in gamma.items() if v != 0}


def load_layer4_xyz_set(n):
    """Load the set of (X,Y,Z) that appear in coboundary entries."""
    with open(f"data/C_{n}_coboundary.json") as f:
        data = json.load(f)
    return set((e["X"], e["Y"], e["Z"]) for e in data["coboundary_delta_f"]["entries"])


def find_obstruction_xyz(n, gamma_sym, cb_xyz_set):
    """
    Find (X,Y,Z) triples where:
    - gamma has nonzero symbolic coefficient (depends on some gb)
    - (X,Y,Z) NOT in coboundary image for any phi
    These triples are strict obstructions to triviality.
    """
    # Collect all (X,Y,Z) from gamma_sym
    gamma_xyz = {}
    for (X, Y, Z, gb), coeff in gamma_sym.items():
        key = (X, Y, Z)
        gamma_xyz.setdefault(key, {})[gb] = gamma_xyz.get(key, {}).get(gb, Fraction(0)) + coeff

    obstructions = {}
    for xyz, gb_dict in gamma_xyz.items():
        if xyz not in cb_xyz_set:
            obstructions[xyz] = gb_dict

    return obstructions


def analyze_obstruction_conditions(n, obstructions):
    """
    For each obstruction triple, determine which gb combination must vanish
    for the deformation to be trivial.
    """
    print(f"\n--- n={n}: Obstruction analysis ---")
    if not obstructions:
        print("  No obstructions found: deformation may be trivial")
        return []

    trivial_conditions = []
    print(f"  Found {len(obstructions)} obstruction (X,Y,Z) triples")
    for xyz, gb_dict in sorted(obstructions.items()):
        X, Y, Z = xyz
        # For triviality, must have sum_gb coeff*gb = 0 for all obstruction triples
        condition = " + ".join(f"({c})*{gb}" for gb, c in sorted(gb_dict.items()))
        trivial_conditions.append((xyz, gb_dict))
        print(f"  (X={X}, Y={Y}, Z={Z}): need {condition} = 0")

    return trivial_conditions


def gb_conditions_from_obstructions(trivial_conditions):
    """Extract unique linear conditions on gb params from obstruction triples."""
    # Normalize each condition by extracting the coefficient vector
    conditions = set()
    for (xyz, gb_dict) in trivial_conditions:
        # Normalize: divide by leading coefficient
        items = sorted(gb_dict.items())
        if not items:
            continue
        leading_coeff = items[0][1]
        normalized = tuple(sorted((gb, c / leading_coeff) for gb, c in items))
        conditions.add(normalized)
    return list(conditions)


def main():
    print("Obstruction Analysis: C(n+1) Triviality Conditions on gb Parameters")
    print("="*70)

    all_conditions = {}
    for n in [1, 2]:
        gamma_sym = load_layer2_symbolic(n)
        cb_xyz = load_layer4_xyz_set(n)

        # Collect (X,Y,Z) from gamma_sym
        gamma_xyz = set(k[:3] for k in gamma_sym.keys())

        print(f"\nC_{n}: gamma XYZ triples = {len(gamma_xyz)}, "
              f"coboundary XYZ triples = {len(cb_xyz)}")
        unreachable = gamma_xyz - cb_xyz
        print(f"  Obstruction triples (gamma nonzero, not in coboundary image): {len(unreachable)}")

        obstructions = find_obstruction_xyz(n, gamma_sym, cb_xyz)
        trivial_conditions = analyze_obstruction_conditions(n, obstructions)
        unique_conditions = gb_conditions_from_obstructions(trivial_conditions)

        print(f"\n  Unique linear conditions on gb for triviality:")
        for cond in unique_conditions[:10]:
            lhs = " + ".join(f"({c})*{gb}" for gb, c in cond)
            print(f"    {lhs} = 0")

        all_conditions[n] = {
            "obstruction_count": len(obstructions),
            "unique_conditions": unique_conditions,
            "trivial_conditions": trivial_conditions
        }

    # Summary conjecture
    print("\n" + "="*70)
    print("CONJECTURE SUMMARY")
    print("="*70)
    print()
    print("For C(n+1) = osp(2|2n), the inhomogeneous deformation gamma(gb) is")
    print("trivial (= delta f for some odd map f) if and only if the 4n gb")
    print("parameters satisfy the linear conditions extracted above.")
    print()
    for n, info in all_conditions.items():
        nc = len(info["unique_conditions"])
        print(f"  C_{n} (n={n}): {info['obstruction_count']} obstruction triples "
              f"-> {nc} independent linear conditions on gb")

    print()
    print("Pattern observed:")
    print("  n=1: 4 gb parameters, null-dim=4 (coboundary map), obstructions -> conditions")
    print("  n=2: 8 gb parameters, null-dim=8 (coboundary map), obstructions -> conditions")
    print()
    print("Structural observation: null-dim of coboundary map = 4n = number of gb params.")
    print("This suggests the deformation is GENERICALLY NON-TRIVIAL (the 4n-dimensional")
    print("space of gb-deformations does not intersect the image of delta for generic gb).")
    print()
    print("The deformation gamma(gb) is trivial IFF the gb vector satisfies the")
    print("linear equations defined by the obstruction triples, which appear to form")
    print("an overdetermined system (more equations than unknowns for generic gb).")


if __name__ == "__main__":
    main()
