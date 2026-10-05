"""Verification Script for C(n+1) Lie Superalgebra Structure.

Checks:
1. Graded anti-symmetry: [X, Y} = -(-1)^{p(X)p(Y)} [Y, X} for all pairs (X, Y).
2. Super Jacobi identity:
   (-1)^{p(X)p(Z)} [X, [Y, Z}} + (-1)^{p(Y)p(X)} [Y, [Z, X}} + (-1)^{p(Z)p(Y)} [Z, [X, Y}} = 0
   for all triples (X, Y, Z).
"""

from collections import defaultdict
from fractions import Fraction
import json
import os
import sys
from typing import Dict, List, Tuple

def load_structure_data(filepath: str):
    """Load JSON structure data and return basis, parities, and bracket lookup table."""
    with open(filepath, 'r') as f:
        data = json.load(f)
    
    basis = data["basis"]["even"] + data["basis"]["odd"]
    parities = data["parity"]
    
    # Bracket table: (X, Y) -> dict of {Z: Fraction(coeff)}
    bracket_table: Dict[Tuple[str, str], Dict[str, Fraction]] = defaultdict(dict)
    for entry in data["structure_constants"]:
        x, y, z = entry["X"], entry["Y"], entry["Z"]
        bracket_table[(x, y)][z] = Fraction(entry["coeff"])
        
    return data, basis, parities, bracket_table

def bracket_of(bracket_table, x: str, y: str) -> Dict[str, Fraction]:
    """Return [X, Y} as a dict of {generator: Fraction}."""
    return bracket_table.get((x, y), {})

def bracket_with_poly(bracket_table, gen: str, poly: Dict[str, Fraction]) -> Dict[str, Fraction]:
    """Compute [gen, poly} = sum_W poly[W] * [gen, W}."""
    res = defaultdict(Fraction)
    for w, coeff in poly.items():
        if coeff == 0:
            continue
        for z, c_gw in bracket_of(bracket_table, gen, w).items():
            res[z] += coeff * c_gw
    return {k: v for k, v in res.items() if v != 0}

def check_antisymmetry(basis: List[str], parities: Dict[str, int], bracket_table) -> Tuple[bool, List[str]]:
    """Check graded anti-symmetry for all pairs in the basis."""
    errors = []
    for i, x in enumerate(basis):
        for j, y in enumerate(basis):
            p_xy = (-1) ** (parities[x] * parities[y])
            br_xy = bracket_of(bracket_table, x, y)
            br_yx = bracket_of(bracket_table, y, x)
            
            all_z = set(br_xy.keys()) | set(br_yx.keys())
            for z in all_z:
                c_xy = br_xy.get(z, Fraction(0))
                c_yx = br_yx.get(z, Fraction(0))
                if c_xy + p_xy * c_yx != 0:
                    errors.append(f"Antisymmetry fail at ({x}, {y}, {z}): [X,Y]={c_xy}, [Y,X]={c_yx}")
                    if len(errors) >= 10:
                        return False, errors
    return len(errors) == 0, errors

def check_super_jacobi(basis: List[str], parities: Dict[str, int], bracket_table) -> Tuple[bool, int, List[str]]:
    """Check Super Jacobi identity for all triples (X, Y, Z)."""
    errors = []
    total_triples = 0
    for x in basis:
        px = parities[x]
        for y in basis:
            py = parities[y]
            br_xy = bracket_of(bracket_table, x, y)
            for z in basis:
                pz = parities[z]
                total_triples += 1
                
                # Term 1: (-1)^{p(X)p(Z)} [X, [Y, Z}}
                s1 = (-1) ** (px * pz)
                br_yz = bracket_of(bracket_table, y, z)
                t1 = bracket_with_poly(bracket_table, x, br_yz)
                
                # Term 2: (-1)^{p(Y)p(X)} [Y, [Z, X}}
                s2 = (-1) ** (py * px)
                br_zx = bracket_of(bracket_table, z, x)
                t2 = bracket_with_poly(bracket_table, y, br_zx)
                
                # Term 3: (-1)^{p(Z)p(Y)} [Z, [X, Y}}
                s3 = (-1) ** (pz * py)
                t3 = bracket_with_poly(bracket_table, z, br_xy)
                
                # Sum terms
                all_w = set(t1.keys()) | set(t2.keys()) | set(t3.keys())
                for w in all_w:
                    val = s1 * t1.get(w, Fraction(0)) + s2 * t2.get(w, Fraction(0)) + s3 * t3.get(w, Fraction(0))
                    if val != 0:
                        errors.append(f"Jacobi fail at ({x}, {y}, {z}) on {w}: sum = {val}")
                        if len(errors) >= 10:
                            return False, total_triples, errors
                            
    return len(errors) == 0, total_triples, errors

def verify_all(data_dir: str = "data") -> bool:
    """Run verification for all three ranks n=1, 2, 3."""
    all_passed = True
    print("=" * 60)
    print("Super Jacobi and Graded Anti-symmetry Verification Report")
    print("=" * 60)
    
    for n in [1, 2, 3]:
        filepath = os.path.join(data_dir, f"C_{n}_structure.json")
        data, basis, parities, bracket_table = load_structure_data(filepath)
        dim = len(basis)
        
        # 1. Antisymmetry
        anti_ok, anti_errors = check_antisymmetry(basis, parities, bracket_table)
        
        # 2. Super Jacobi
        jacobi_ok, total_triples, jacobi_errors = check_super_jacobi(basis, parities, bracket_table)
        
        print(f"\n--- C({n+1}) = osp(2|{2*n}) [File: C_{n}_structure.json] ---")
        print(f"Dimension: {dim} ({len(data['basis']['even'])} even, {len(data['basis']['odd'])} odd)")
        print(f"Anti-symmetry check: {'PASS' if anti_ok else 'FAIL'}")
        if not anti_ok:
            for err in anti_errors[:5]:
                print(f"  Error: {err}")
                
        print(f"Super Jacobi check: {'PASS' if jacobi_ok else 'FAIL'} ({total_triples} triples checked)")
        if not jacobi_ok:
            for err in jacobi_errors[:5]:
                print(f"  Error: {err}")
                
        if not (anti_ok and jacobi_ok):
            all_passed = False
            
    print("\n" + "=" * 60)
    print(f"OVERALL STATUS: {'PASS' if all_passed else 'FAIL'}")
    print("=" * 60)
    return all_passed

if __name__ == "__main__":
    success = verify_all()
    sys.exit(0 if success else 1)
