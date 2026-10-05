import json
import os
import sys
from fractions import Fraction
import numpy as np
import sympy

def load_json(path):
    with open(path, "r") as f:
        return json.load(f)

def analyze_triviality(n):
    gamma_schema = load_json(f"data/C_{n}_gamma.json")
    coboundary_schema = load_json(f"data/C_{n}_coboundary.json")
    
    gb_params = gamma_schema["gb_matrix"]["parameters"]
    f_params = coboundary_schema["f_map"]["parameters"]
    
    # We will build equations for each (X, Y, Z) tuple.
    # We map each tuple to a row index.
    eq_map = {}
    row_idx = 0
    
    # Collect all (X, Y, Z) that have either a gb_term or f_term
    tuples = set()
    for sc in gamma_schema["gamma_structure_constants"]:
        tuples.add((sc["X"], sc["Y"], sc["Z"]))
    for sc in coboundary_schema["coboundary_structure_constants"]:
        tuples.add((sc["X"], sc["Y"], sc["Z"]))
        
    tuples = sorted(list(tuples))
    tuple_to_row = {t: i for i, t in enumerate(tuples)}
    
    # M matrix for f_params (size: |tuples| x |f_params|)
    M = np.zeros((len(tuples), len(f_params)), dtype=object)
    for sc in coboundary_schema["coboundary_structure_constants"]:
        r = tuple_to_row[(sc["X"], sc["Y"], sc["Z"])]
        for f_p, c_str in sc["f_terms"].items():
            c = Fraction(c_str)
            c_sym = sympy.Rational(c.numerator, c.denominator)
            c_idx = f_params.index(f_p)
            M[r, c_idx] = c_sym
            
    # G matrix for gb_params (size: |tuples| x |gb_params|)
    G = np.zeros((len(tuples), len(gb_params)), dtype=object)
    for sc in gamma_schema["gamma_structure_constants"]:
        r = tuple_to_row[(sc["X"], sc["Y"], sc["Z"])]
        for gb_p, c_str in sc["gb_terms"].items():
            c = Fraction(c_str)
            c_sym = sympy.Rational(c.numerator, c.denominator)
            c_idx = gb_params.index(gb_p)
            G[r, c_idx] = c_sym
            
    # Convert to sympy matrices
    M_sym = sympy.Matrix(M)
    G_sym = sympy.Matrix(G)
    
    print(f"\n--- Analysis for C({n+1}) ---")
    print(f"Number of equations (X,Y,Z tuples): {len(tuples)}")
    print(f"Number of f_params (variables): {len(f_params)}")
    print(f"Number of gb_params (deformation params): {len(gb_params)}")
    
    # Check if column space of G is contained in column space of M.
    # We can do this by computing the rank of M, and the rank of [M | G].
    rank_M = M_sym.rank()
    print(f"Rank of M: {rank_M}")
    
    M_aug_G = M_sym.row_join(G_sym)
    rank_aug = M_aug_G.rank()
    print(f"Rank of [M | G]: {rank_aug}")
    
    if rank_M == rank_aug:
        print("CONCLUSION: The deformation is ALWAYS TRIVIAL (G is in the column space of M).")
    else:
        print("CONCLUSION: The deformation is NON-TRIVIAL. There are constraints on gb_params.")
        # Find the constraints by looking at the left nullspace of M
        # L * M = 0. Then we need L * G * gb = 0.
        L = M_sym.T.nullspace()
        constraints = []
        for vec in L:
            constraint = vec.T * G_sym
            if not constraint.is_zero_matrix:
                constraints.append(constraint)
                
        print(f"Number of independent constraints on gb_params: {rank_aug - rank_M}")
        
        # Display constraints
        import sympy as sp
        gb_vars = sp.symbols(' '.join(gb_params))
        for i, c in enumerate(constraints):
            expr = sum(c[j] * gb_vars[j] for j in range(len(gb_params)))
            if expr != 0:
                print(f"Constraint {i+1}: {expr} == 0")

if __name__ == "__main__":
    for n in [1, 2]:
        analyze_triviality(n)
