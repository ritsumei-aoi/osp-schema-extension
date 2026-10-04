"""
Inspect the exact linear relations leading to gb = 0 for any n.
"""
import sympy as sp
from verify_c_algebra import get_algebra

def inspect_obstruction(n=1):
    basis_elements, names, parities, gb_symbols, struct_consts, gamma_gb = get_algebra(n)
    
    # Let's see:
    # 1. gamma(H_0, E_+2d1) = gb_-_1_+ E_+e+d1 + gb_+_1_+ E_-e+d1
    # On the other hand, delta f(H_0, E_+2d1) = [H_0, f(E_+2d1)] - [E_+2d1, f(H_0)]
    # Note [H_0, E_+2d1] = 0.
    
    # 2. gamma(h_1, E_+2d1) = [h_1, E_+2d1] deformation?
    # Let's check gamma(h_1, E_+2d1):
    print("gamma(h_1, E_+2d1) =", gamma_gb.get(('h_1', 'E_+2d1'), {}))
    print("gamma(E_+2d1, E_-2d1) =", gamma_gb.get(('E_+2d1', 'E_-2d1'), {}))
    
    # Notice that bosonic-bosonic commutators [b_j^s b_k^t, b_l^u b_m^v] inside sp(2n) have gamma = 0!
    # Because cross commutators [b, b] don't involve a, so gamma(Y_1, Y_2) = 0 for all Y_1, Y_2 in sp(2n)!
    print("gamma restricted to sp(2n) x sp(2n) is identically ZERO!")

if __name__ == '__main__':
    inspect_obstruction(1)
