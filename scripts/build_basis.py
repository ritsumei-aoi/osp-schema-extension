import sympy as sp
from collections import defaultdict
import json

def build_basis(n):
    # Basis elements defined as linear combinations of normal-ordered oscillator words
    # Oscillator names:
    # 'a+', 'a-' (parity 1)
    # 'b+1', 'b-1', ..., 'b+n', 'b-n' (parity 0)
    
    osc_list = ['a+', 'a-']
    for k in range(1, n + 1):
        osc_list.extend([f'b+{k}', f'b-{k}'])
    
    osc_order = {name: i for i, name in enumerate(osc_list)}
    parity = {name: (1 if name.startswith('a') else 0) for name in osc_list}
    
    basis = {}
    basis_parity = {}
    
    # Cartan generators:
    # H_1 = a+ a- + b+1 b-1
    basis['H1'] = {('a+', 'a-'): 1, ('b+1', 'b-1'): 1}
    basis_parity['H1'] = 0
    
    for k in range(2, n + 1):
        # H_k = b+_{k-1} b-_{k-1} - b+_k b-_k
        basis[f'H{k}'] = {(f'b+{k-1}', f'b-{k-1}'): 1, (f'b+{k}', f'b-{k}'): -1}
        basis_parity[f'H{k}'] = 0
    
    # H_{n+1} = - b+_n b-_n - 1/2
    basis[f'H{n+1}'] = {(f'b+{n}', f'b-{n}'): -1, (): -sp.Rational(1, 2)}
    basis_parity[f'H{n+1}'] = 0
    
    # Bosonic root generators:
    for k in range(1, n + 1):
        # E_{2\delta_k} = 1/2 (b+_k)^2
        basis[f'E_2d{k}'] = {(f'b+{k}', f'b+{k}'): sp.Rational(1, 2)}
        basis_parity[f'E_2d{k}'] = 0
        # E_{-2\delta_k} = 1/2 (b-_k)^2
        basis[f'E_-2d{k}'] = {(f'b-{k}', f'b-{k}'): sp.Rational(1, 2)}
        basis_parity[f'E_-2d{k}'] = 0
    
    for k in range(1, n + 1):
        for l in range(1, n + 1):
            if k != l:
                # E_{\delta_k - \delta_l} = b+_k b-_l
                # Need to normal order if osc_order[b+_k] > osc_order[b-_l]
                if osc_order[f'b+{k}'] < osc_order[f'b-{l}']:
                    basis[f'E_d{k}-d{l}'] = {(f'b+{k}', f'b-{l}'): 1}
                else:
                    # b+_k b-_l = b-_l b+_k - [b-_l, b+_k] = b-_l b+_k (since k != l, comm=0)
                    basis[f'E_d{k}-d{l}'] = {(f'b-{l}', f'b+{k}'): 1}
                basis_parity[f'E_d{k}-d{l}'] = 0
    
    for k in range(1, n + 1):
        for l in range(k + 1, n + 1):
            # E_{\delta_k + \delta_l} = b+_k b+_l
            basis[f'E_d{k}+d{l}'] = {(f'b+{k}', f'b+{l}'): 1}
            basis_parity[f'E_d{k}+d{l}'] = 0
            # E_{-\delta_k - \delta_l} = b-_k b-_l
            basis[f'E_-d{k}-d{l}'] = {(f'b-{k}', f'b-{l}'): 1}
            basis_parity[f'E_-d{k}-d{l}'] = 0
            
    # Odd root generators:
    for k in range(1, n + 1):
        # E_{\varepsilon + \delta_k} = a+ b+_k
        basis[f'E_eps+d{k}'] = {('a+', f'b+{k}'): 1}
        basis_parity[f'E_eps+d{k}'] = 1
        # E_{\varepsilon - \delta_k} = a+ b-_k
        basis[f'E_eps-d{k}'] = {('a+', f'b-{k}'): 1}
        basis_parity[f'E_eps-d{k}'] = 1
        # E_{-\varepsilon + \delta_k} = a- b+_k
        basis[f'E_-eps+d{k}'] = {('a-', f'b+{k}'): 1}
        basis_parity[f'E_-eps+d{k}'] = 1
        # E_{-\varepsilon - \delta_k} = a- b-_k
        basis[f'E_-eps-d{k}'] = {('a-', f'b-{k}'): 1}
        basis_parity[f'E_-eps-d{k}'] = 1
        
    return osc_list, osc_order, parity, basis, basis_parity

print("Basis builder defined.")
