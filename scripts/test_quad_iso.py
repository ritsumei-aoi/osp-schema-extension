import sympy as sp
from collections import defaultdict

def test_basis_quadratic_isomorphism(n):
    # Oscillators:
    osc_list = ['a+', 'a-']
    for k in range(1, n + 1):
        osc_list.extend([f'b+{k}', f'b-{k}'])
    osc_order = {name: i for i, name in enumerate(osc_list)}
    
    # Basis definitions
    basis = {}
    basis_parity = {}
    
    basis['H1'] = {('a+', 'a-'): 1, ('b+1', 'b-1'): 1}
    basis_parity['H1'] = 0
    for k in range(2, n + 1):
        basis[f'H{k}'] = {(f'b+{k-1}', f'b-{k-1}'): 1, (f'b+{k}', f'b-{k}'): -1}
        basis_parity[f'H{k}'] = 0
    basis[f'H{n+1}'] = {(f'b+{n}', f'b-{n}'): -1, (): -sp.Rational(1, 2)}
    basis_parity[f'H{n+1}'] = 0
    
    for k in range(1, n + 1):
        basis[f'E_2d{k}'] = {(f'b+{k}', f'b+{k}'): sp.Rational(1, 2)}
        basis_parity[f'E_2d{k}'] = 0
        basis[f'E_-2d{k}'] = {(f'b-{k}', f'b-{k}'): sp.Rational(1, 2)}
        basis_parity[f'E_-2d{k}'] = 0
        
    for k in range(1, n + 1):
        for l in range(1, n + 1):
            if k != l:
                if osc_order[f'b+{k}'] < osc_order[f'b-{l}']:
                    basis[f'E_d{k}-d{l}'] = {(f'b+{k}', f'b-{l}'): 1}
                else:
                    basis[f'E_d{k}-d{l}'] = {(f'b-{l}', f'b+{k}'): 1}
                basis_parity[f'E_d{k}-d{l}'] = 0
                
    for k in range(1, n + 1):
        for l in range(k + 1, n + 1):
            basis[f'E_d{k}+d{l}'] = {(f'b+{k}', f'b+{l}'): 1}
            basis_parity[f'E_d{k}+d{l}'] = 0
            basis[f'E_-d{k}-d{l}'] = {(f'b-{k}', f'b-{l}'): 1}
            basis_parity[f'E_-d{k}-d{l}'] = 0
            
    for k in range(1, n + 1):
        basis[f'E_eps+d{k}'] = {('a+', f'b+{k}'): 1}
        basis_parity[f'E_eps+d{k}'] = 1
        basis[f'E_eps-d{k}'] = {('a+', f'b-{k}'): 1}
        basis_parity[f'E_eps-d{k}'] = 1
        basis[f'E_-eps+d{k}'] = {('a-', f'b+{k}'): 1}
        basis_parity[f'E_-eps+d{k}'] = 1
        basis[f'E_-eps-d{k}'] = {('a-', f'b-{k}'): 1}
        basis_parity[f'E_-eps-d{k}'] = 1
        
    basis_names = list(basis.keys())
    # Collect only QUADRATIC monomials (length 2)
    quad_monomials = set()
    for b_dict in basis.values():
        for m in b_dict.keys():
            if len(m) == 2:
                quad_monomials.add(m)
    quad_list = sorted(list(quad_monomials), key=lambda m: [osc_order[x] for x in m])
    
    print(f"n={n}: dim(g) = {len(basis_names)}, #quadratic monomials = {len(quad_list)}")
    assert len(basis_names) == len(quad_list)
    
    # Check square matrix determinant
    M_quad = sp.zeros(len(quad_list), len(basis_names))
    for j, name in enumerate(basis_names):
        for m, c in basis[name].items():
            if len(m) == 2:
                i = quad_list.index(m)
                M_quad[i, j] = c
                
    det = M_quad.det()
    print(f"Determinant of quadratic basis matrix: {det}")
    assert det != 0, "Quadratic matrix is singular!"
    print(f"n={n}: Quadratic isomorphism VERIFIED!")

for n in [1, 2, 3]:
    test_basis_quadratic_isomorphism(n)
