import json
import numpy as np

# Let's write a script to define C(n+1) basis and compute both gamma_gb and delta_f

def get_basis(n):
    """
    Returns basis elements of C(n+1) = osp(2|2n).
    Oscillators:
    Fermionic: a+, a- (index 0, 1)
    Bosonic: b_1+, b_1-, ..., b_n+, b_n-
    
    Generators:
    Even generators:
      - Z0 = a+ a- - 1/2  (so(2) generator)
      - B_{k,s1; l,s2} = b_k^{s1} b_l^{s2} for k,l in 1..n, s1,s2 in {+,-}
        Note: B_{k,s1; l,s2} = B_{l,s2; k,s1}.
        For k=l, s1=s2: (b_k^s)^2 / 2 or b_k^s b_k^s?
        Let's use normalized symmetric basis:
        For (k,s1) == (l,s2): 0.5 * (b_k^s1)^2
        For (k,s1) != (l,s2): b_k^s1 b_l^s2 (with (k,s1) < (l,s2) ordering).
    Odd generators:
      - F_{sigma, k, s} = a^\sigma b_k^s for sigma in {+,-}, k in 1..n, s in {+,-}
    """
    even_basis = []
    # Z0
    even_basis.append(('Z0',))
    
    # Bosonic pairs (k, s)
    bosons = []
    for k in range(1, n+1):
        bosons.append((k, '+'))
        bosons.append((k, '-'))
        
    for i in range(len(bosons)):
        for j in range(i, len(bosons)):
            even_basis.append(('B', bosons[i], bosons[j]))
            
    odd_basis = []
    for sigma in ['+', '-']:
        for k in range(1, n+1):
            for s in ['+', '-']:
                odd_basis.append(('F', sigma, (k, s)))
                
    return even_basis, odd_basis

print("Testing basis generation:")
for n in [1, 2, 3]:
    eb, ob = get_basis(n)
    print(f"n={n}: even dim = {len(eb)}, odd dim = {len(ob)}, total = {len(eb)+len(ob)}")
