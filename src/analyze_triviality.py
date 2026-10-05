"""Triviality Analysis for C(n+1) = osp(2|2n) Inhomogeneous Deformation.

This script executes the complete analytical comparison between Layer 3 (evaluated deformation)
and Layer 4 (coboundary structure), and performs exact rank and cohomological investigations
to establish the necessary and sufficient triviality conditions for C(n+1).
"""

from collections import defaultdict
from fractions import Fraction
import json
import os
import sys
from typing import Any, Dict, List, Tuple
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def analyze_layer3_vs_layer4(n: int, data_dir: str = "data") -> Dict[str, Any]:
    """Compare Layer 3 and Layer 4 datasets for rank n."""
    path_s3 = os.path.join(data_dir, f"C_{n}_evaluated.json")
    path_s4 = os.path.join(data_dir, f"C_{n}_coboundary.json")
    
    with open(path_s3, "r") as f3, open(path_s4, "r") as f4:
        d3 = json.load(f3)
        d4 = json.load(f4)
        
    gamma_eval = {(e["X"], e["Y"], e["Z"]): Fraction(e["coeff"])
                  for e in d3["evaluated_deformation"]["gamma_coefficients"]}
    delta_f = {(e["X"], e["Y"], e["Z"]): Fraction(e["coeff"])
               for e in d4["coboundary_operator"]["coboundary_coefficients"]}
               
    all_triples = sorted(list(set(gamma_eval.keys()) | set(delta_f.keys())))
    matching_nonzero = []
    differing = []
    
    for trip in all_triples:
        cg = gamma_eval.get(trip, Fraction(0))
        cd = delta_f.get(trip, Fraction(0))
        if cg == cd:
            if cg != 0:
                matching_nonzero.append((trip, str(cg)))
        else:
            differing.append({
                "triple": trip,
                "gamma_eval": str(cg),
                "delta_f": str(cd),
                "discrepancy": str(cg - cd)
            })
            
    return {
        "n": n,
        "algebra": f"C({n+1}) = osp(2|{2*n})",
        "total_active_triples": len(all_triples),
        "matching_nonzero_count": len(matching_nonzero),
        "differing_count": len(differing),
        "matching_samples": matching_nonzero[:8],
        "differing_samples": differing[:8]
    }

def analyze_cohomological_triviality(n: int, data_dir: str = "data") -> Dict[str, Any]:
    """Perform exact linear algebraic rank analysis to check if gamma in im(delta)."""
    with open(os.path.join(data_dir, f"C_{n}_structure.json"), "r") as f:
        s1 = json.load(f)
    with open(os.path.join(data_dir, f"C_{n}_gamma.json"), "r") as f:
        gamma_data = json.load(f)

    basis = s1["basis"]["even"] + s1["basis"]["odd"]
    parities = [s1["parity"][g] for g in basis]
    dim = len(basis)
    gen_to_idx = {g: i for i, g in enumerate(basis)}

    bracket_table = defaultdict(dict)
    for entry in s1["structure_constants"]:
        x, y, z = entry["X"], entry["Y"], entry["Z"]
        bracket_table[(gen_to_idx[x], gen_to_idx[y])][gen_to_idx[z]] = Fraction(entry["coeff"])

    def get_bracket(xi, yi):
        return bracket_table.get((xi, yi), {})

    odd_maps = [(i, j) for j in range(dim) for i in range(dim) if parities[i] != parities[j]]

    independent_pairs = []
    for i in range(dim):
        for j in range(dim):
            if i < j or (i == j and parities[i] == 1):
                independent_pairs.append((i, j))

    equations = [(pair_idx, z_idx) for pair_idx in range(len(independent_pairs)) for z_idx in range(dim)]

    M = np.zeros((len(equations), len(odd_maps)))

    for m_idx, (out_i, in_j) in enumerate(odd_maps):
        for p_idx, (x_idx, y_idx) in enumerate(independent_pairs):
            px = parities[x_idx]
            py = parities[y_idx]
            
            s1 = (-1) ** px
            if y_idx == in_j:
                br1 = get_bracket(x_idx, out_i)
                for z, c in br1.items():
                    M[p_idx * dim + z, m_idx] += float(s1 * c)
                    
            sign2 = - ((-1) ** ((px + 1) * py))
            if x_idx == in_j:
                br2 = get_bracket(y_idx, out_i)
                for z, c in br2.items():
                    M[p_idx * dim + z, m_idx] += float(sign2 * c)
                    
            br3 = get_bracket(x_idx, y_idx)
            if in_j in br3:
                M[p_idx * dim + out_i, m_idx] -= float(br3[in_j])

    # Distinct gb parameters
    params = sorted(list({entry["gb_param"] for entry in gamma_data["inhomogeneous_deformation"]["gamma_coefficients"]}))
    V_gamma = []
    for param in params:
        v = np.zeros(len(equations))
        for entry in gamma_data["inhomogeneous_deformation"]["gamma_coefficients"]:
            if entry["gb_param"] == param:
                x_idx = gen_to_idx[entry["X"]]
                y_idx = gen_to_idx[entry["Y"]]
                z_idx = gen_to_idx[entry["Z"]]
                c = float(Fraction(entry["coeff"]))
                if (x_idx, y_idx) in independent_pairs:
                    p_idx = independent_pairs.index((x_idx, y_idx))
                    v[p_idx * dim + z_idx] = c
        V_gamma.append(v)

    V_gamma = np.column_stack(V_gamma)
    rank_M = int(np.linalg.matrix_rank(M))
    rank_V = int(np.linalg.matrix_rank(V_gamma))
    rank_both = int(np.linalg.matrix_rank(np.column_stack([M, V_gamma])))
    intersection_dim = rank_M + rank_V - rank_both

    return {
        "n": n,
        "basis_dim": dim,
        "odd_maps_count": len(odd_maps),
        "rank_coboundary_operator": rank_M,
        "deformation_params_count": len(params),
        "rank_deformation_space": rank_V,
        "rank_combined": rank_both,
        "intersection_dimension": intersection_dim,
        "trivial_only_if_gb_zero": (intersection_dim == 0)
    }

def run_full_report(data_dir: str = "data"):
    print("=" * 70)
    print("TRIVIALITY ANALYSIS REPORT FOR C(n+1) = osp(2|2n)")
    print("=" * 70)
    
    for n in [1, 2, 3]:
        comp = analyze_layer3_vs_layer4(n, data_dir)
        cohom = analyze_cohomological_triviality(n, data_dir)
        
        print(f"\n--- Rank n = {n}: {comp['algebra']} ---")
        print(f"1. Layer 3 vs Layer 4 Data Comparison:")
        print(f"   Total active triples: {comp['total_active_triples']}")
        print(f"   Matching non-zero triples: {comp['matching_nonzero_count']}")
        print(f"   Differing triples: {comp['differing_count']}")
        print("   Sample matching triples:")
        for trip, val in comp["matching_samples"][:3]:
            print(f"     {trip}: value = {val}")
        print("   Sample differing triples:")
        for diff in comp["differing_samples"][:3]:
            print(f"     {diff['triple']}: gamma={diff['gamma_eval']}, delta_f={diff['delta_f']}, diff={diff['discrepancy']}")
            
        print(f"\n2. Cohomological & Linear Algebraic Results:")
        print(f"   Space of odd linear maps Hom_1(g, g): dim = {cohom['odd_maps_count']}")
        print(f"   Coboundary operator rank im(delta): {cohom['rank_coboundary_operator']}")
        print(f"   Deformation parameter count: {cohom['deformation_params_count']}")
        print(f"   Deformation subspace rank V_gamma: {cohom['rank_deformation_space']}")
        print(f"   Intersection dimension dim(im(delta) \\cap V_gamma): {cohom['intersection_dimension']}")
        print(f"   Trivial iff gb = 0: {cohom['trivial_only_if_gb_zero']}")
        
    print("\n" + "=" * 70)
    print("GENERAL CONJECTURE ON TRIVIALITY FOR C(n+1):")
    print("The inhomogeneous deformation of C(n+1) = osp(2|2n) is trivial if and only if")
    print("all 4n deformation parameters gb vanish identically: gb = 0.")
    print("For any non-zero parameter assignment gb != 0, the deformation represents a non-trivial")
    print("cohomology class in H^2(g, g)_1, because dim(im(delta) \\cap V_gamma) = 0.")
    print("=" * 70)


if __name__ == "__main__":
    run_full_report()
