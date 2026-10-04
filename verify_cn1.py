import sympy as sp
from itertools import product

def test_cn1(n=1):
    print(f"=== Testing C({n+1}) ===")
    # Oscillators:
    # Fermionic: a_1^+, a_1^-  (parity 1)
    # Bosonic: b_j^+, b_j^- for j=1..n (parity 0)
    # Central: K (even), kappa (odd)
    
    # We represent elements of V as:
    # ('a', 1, '+'), ('a', 1, '-'), ('b', j, '+'), ('b', j, '-')
    pass

if __name__ == '__main__':
    print("Sympy ready")
