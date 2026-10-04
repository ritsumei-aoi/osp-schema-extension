import sympy as sp
from itertools import product

def build_algebra(n):
    # Basis elements: name -> (parity, expression in oscillators)
    # Oscillators: ('a', '+'), ('a', '-'), ('b', j, '+'), ('b', j, '-')
    # Each generator is a sum of pairs of oscillators with coefficients.
    # We represent a quadratic monomial as: coeff * (osc1, osc2)
    
    basis = []
    
    # Even generators:
    # 1. H_0 = a^+ a^-
    basis.append(('H_0', 0, [ (1, ('a', '+'), ('a', '-')) ]))
    
    # 2. N_j = b_j^+ b_j^-
    for j in range(1, n + 1):
        basis.append((f'N_{j}', 0, [ (1, ('b', j, '+'), ('b', j, '-')) ]))
        
    # 3. E_{2\delta_j} = 1/2 (b_j^+)^2, E_{-2\delta_j} = 1/2 (b_j^-)^2
    for j in range(1, n + 1):
        basis.append((f'E_+2d_{j}', 0, [ (sp.Rational(1, 2), ('b', j, '+'), ('b', j, '+')) ]))
        basis.append((f'E_-2d_{j}', 0, [ (sp.Rational(1, 2), ('b', j, '-'), ('b', j, '-')) ]))
        
    # 4. E_{\pm\delta_j \pm\delta_k} for j < k
    for j in range(1, n + 1):
        for k in range(j + 1, n + 1):
            basis.append((f'E_+d{j}+d{k}', 0, [ (1, ('b', j, '+'), ('b', k, '+')) ]))
            basis.append((f'E_-d{j}-d{k}', 0, [ (1, ('b', j, '-'), ('b', k, '-')) ]))
            basis.append((f'E_+d{j}-d{k}', 0, [ (1, ('b', j, '+'), ('b', k, '-')) ]))
            basis.append((f'E_-d{j}+d{k}', 0, [ (1, ('b', j, '-'), ('b', k, '+')) ]))
            
    # Odd generators:
    for j in range(1, n + 1):
        basis.append((f'E_+e+d{j}', 1, [ (1, ('a', '+'), ('b', j, '+')) ]))
        basis.append((f'E_+e-d{j}', 1, [ (1, ('a', '+'), ('b', j, '-')) ]))
        basis.append((f'E_-e+d{j}', 1, [ (1, ('a', '-'), ('b', j, '+')) ]))
        basis.append((f'E_-e-d{j}', 1, [ (1, ('a', '-'), ('b', j, '-')) ]))
        
    return basis

print("Algebra builder defined.")
