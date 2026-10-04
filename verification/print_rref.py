"""
Print RREF of constraints on gb.
"""
import sympy as sp
from verification.analyze_linear import analyze_linear_system

def print_rref():
    M, b, gb_constraints, gb_list = analyze_linear_system(1)
    C_matrix = sp.Matrix([[sp.diff(c, g) for g in gb_list] for c in gb_constraints])
    rref_m, pivots = C_matrix.rref()
    print("gb variables:", gb_list)
    print("RREF of C_matrix:")
    sp.pprint(rref_m[:4, :])
    
if __name__ == '__main__':
    print_rref()
