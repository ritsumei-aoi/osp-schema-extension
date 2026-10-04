"""
Symbolic verification of C(n+1) algebra and deformation.
"""
import sympy as sp
from itertools import product

def run():
    n = 1
    # Oscillators:
    # 0: a_1^+ (parity 1)
    # 1: a_1^- (parity 1)
    # 2: b_1^+ (parity 0)
    # 3: b_1^- (parity 0)
    
    # Let's generalize for arbitrary n:
    # Fermions:
    #   a_1^+ -> ('a', 1, '+')
    #   a_1^- -> ('a', 1, '-')
    # Bosons:
    #   b_j^+ -> ('b', j, '+')
    #   b_j^- -> ('b', j, '-')
    
    pass

if __name__ == '__main__':
    run()
