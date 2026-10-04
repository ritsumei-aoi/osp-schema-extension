"""
Trace the exact relations leading to the constraints on gb.
"""
import sympy as sp
from collections import defaultdict
from verification.analyze_linear import analyze_linear_system
from verification.cn1_algebra import create_algebra, get_generators, superbracket
from verification.test_jacobi import decompose_into_basis

def trace_obstruction(n=1):
    gb, reduce_word = create_algebra(n)
    gens, parities = get_generators(n)
    gen_names = list(gens.keys())
    dim = len(gen_names)
    
    # We want to look at specific triplets or pairs of generators
    # Let's inspect the row equations of M that correspond to:
    # (delta f)(X, Y)_r = gamma(X, Y)_r
    
    # In particular, look at:
    # X = F_p_1_p, Y = E_2d_1
    # or X = E_2d_1, Y = E_-2d_1
    # Let's write a script that examines the delta f formulas for root vectors and Cartan elements!
    
    # Let's find the non-zero left nullspace vectors that have very few non-zero components (sparse)!
    pass

if __name__ == '__main__':
    trace_obstruction(1)
