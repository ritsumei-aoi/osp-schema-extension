"""
Inspect single-support null vectors and exact vanishing of delta f.
"""
import sympy as sp
from verification.cn1_algebra import create_algebra, get_generators, superbracket
from verification.test_jacobi import decompose_into_basis
from verification.analyze_linear import analyze_linear_system

def inspect_single_row():
    n = 1
    gb, reduce_word = create_algebra(n)
    gens, parities = get_generators(n)
    
    # Let's inspect br(F_p_1_m, H_1)
    br = superbracket("F_p_1_m", "H_1", gens, parities, reduce_word)
    t0 = {k: v[0] for k, v in br.items() if v[0] != 0}
    tk = {k: v[1] for k, v in br.items() if v[1] != 0}
    dec0, c0_const = decompose_into_basis(t0, gens, n)
    deck, ck_const = decompose_into_basis(tk, gens, n)
    
    print("Undeformed [F_p_1_m, H_1]:", dec0, "const:", c0_const)
    print("Deformed gamma(F_p_1_m, H_1):", deck, "const:", ck_const)
    
    # Check [H_1, F_p_1_m]_0:
    # F_p_1_m = a+ b1-
    # H_1 = a+ a- + b1+ b1-
    # [a+ b1-, a+ a- + b1+ b1-]
    
if __name__ == '__main__':
    inspect_single_row()
