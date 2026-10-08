import json
import sympy

def analyze_triviality(n):
    with open(f"data/C_{n}_gamma.json", "r") as f:
        schema2 = json.load(f)
        
    with open(f"data/C_{n}_coboundary.json", "r") as f:
        schema4 = json.load(f)
        
    # Collect all (X, Y, Z)
    triples = set()
    gamma_terms = schema2["inhomogeneous_deformation"]
    for t in gamma_terms:
        triples.add((t["X"], t["Y"], t["Z"]))
        
    cob_terms = schema4["coboundary_operator"]
    for t in cob_terms:
        triples.add((t["X"], t["Y"], t["Z"]))
        
    triples = sorted(list(triples))
    triple_to_idx = {t: i for i, t in enumerate(triples)}
    
    # Collect all gb parameters
    gbs = sorted(list(set(t["gb_parameter"] for t in gamma_terms)))
    gb_to_idx = {g: i for i, g in enumerate(gbs)}
    
    # Collect all phi parameters
    phis = sorted(list(set(t["phi_parameter"] for t in cob_terms)))
    phi_to_idx = {p: i for i, p in enumerate(phis)}
    
    import numpy as np
    
    # We will build dense matrices in sympy
    # M: (rows, len(phis)), G: (rows, len(gbs))
    M = sympy.zeros(len(triples), len(phis))
    G = sympy.zeros(len(triples), len(gbs))
    
    for t in cob_terms:
        r = triple_to_idx[(t["X"], t["Y"], t["Z"])]
        c = phi_to_idx[t["phi_parameter"]]
        M[r, c] = sympy.Rational(t["coeff"])
        
    for t in gamma_terms:
        r = triple_to_idx[(t["X"], t["Y"], t["Z"])]
        c = gb_to_idx[t["gb_parameter"]]
        G[r, c] = sympy.Rational(t["coeff"])
        
    # We want conditions v^T G = 0 for v in left nullspace of M
    print(f"n={n}: Computing left nullspace for M ({M.shape[0]}x{M.shape[1]})...")
    
    # Left nullspace is nullspace of M transpose
    # Since sympy nullspace can be slow for large matrices, let's use rref
    # Actually, sympy.Matrix.nullspace() is ok for small n
    L_basis = M.T.nullspace()
    print(f"Left nullspace dimension: {len(L_basis)}")
    
    conditions = []
    if L_basis:
        L_matrix = sympy.Matrix.hstack(*L_basis).T
        # L_matrix is (dim, rows)
        # We compute L_matrix * G
        cond_matrix = L_matrix * G
        
        # Now we extract independent rows of cond_matrix
        cond_rref, pivots = cond_matrix.rref()
        
        for i in range(len(pivots)):
            row = cond_rref[i, :]
            # build equation string
            eq = []
            for j in range(len(gbs)):
                if row[j] != 0:
                    eq.append(f"{row[j]} * {gbs[j]}")
            if eq:
                conditions.append(" + ".join(eq) + " = 0")
                
    return gbs, conditions

if __name__ == "__main__":
    for n in [1, 2]: # just n=1, 2 to be fast
        gbs, conds = analyze_triviality(n)
        print(f"--- n={n} Conditions ---")
        for c in conds:
            print(c)
        if not conds:
            print("No conditions on gb! (Always trivial)")
        print()
