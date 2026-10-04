"""
Verification script for C(n+1) = osp(2|2n) inhomogeneous deformation triviality.
"""
import sympy as sp
from itertools import product

def test_algebra(n=1):
    print(f"=== Testing C({n+1}) = osp(2|{2*n}) ===")
    # Define oscillators:
    # Fermions: a_1^+, a_1^- (parity 1)
    # Bosons: b_j^+, b_j^- for j=1..n (parity 0)
    
if __name__ == '__main__':
    test_algebra(1)
