"""
Inspect constraints on gb and determine minimal obstructions to triviality.
"""
import sympy as sp
from verification.analyze_linear import analyze_linear_system

def inspect_constraints():
    M, b, gb_constraints, gb_list = analyze_linear_system(1)
    print("\n--- Independent constraints on gb ---")
    # Take a basis of the constraints:
    C_matrix = sp.Matrix([[sp.diff(c, g) for g in gb_list] for c in gb_constraints])
    rref_matrix, pivots = C_matrix.rref()
    print(f"Pivot rows in constraint matrix: {pivots}")
    for p in pivots:
        print(f"Constraint {p}: {gb_constraints[p]} = 0")
        
if __name__ == '__main__':
    inspect_constraints()
