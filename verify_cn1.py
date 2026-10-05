"""
Comprehensive Lie superalgebra and deformation computation for C(n+1) = osp(2|2n)
"""
import sympy as sp
from itertools import product
import json

def get_algebra(n):
    # Oscillators:
    # 0: a1+ (p=1), 1: a1- (p=1)
    # for k=1..n:
    # 2k: bk+ (p=0), 2k+1: bk- (p=0)
    
    osc_names = ['a1+', 'a1-']
    osc_parities = [1, 1]
    
    for k in range(1, n+1):
        osc_names.extend([f'b{k}+', f'b{k}-'])
        osc_parities.extend([0, 0])
        
    num_osc = 2 + 2*n
    
    # Omega0 (standard CCR / CAR):
    # {a1-, a1+} = 1  => [a1-, a1+] = 1, [a1+, a1-] = 1
    # [bk-, bk+] = 1, [bk+, bk-] = -1
    omega0 = sp.zeros(num_osc, num_osc)
    omega0[1, 0] = 1 # [a1-, a1+]
    omega0[0, 1] = 1 # [a1+, a1-]
    
    for k in range(1, n+1):
        bp = 2*k
        bm = 2*k + 1
        omega0[bm, bp] = 1
        omega0[bp, bm] = -1
        
    # Deformation symbols gb:
    # [b_j^s, a_1^sigma] = - gb_{sigma, j, s} * kappa
    # [a_1^sigma, b_j^s] = gb_{sigma, j, s} * kappa
    gb_symbols = {}
    Omega_def = sp.zeros(num_osc, num_osc)
    
    for sigma in ['+', '-']:
        sig_idx = 0 if sigma == '+' else 1
        for j in range(1, n+1):
            for s in ['+', '-']:
                s_idx = 2*j if s == '+' else 2*j + 1
                sym = sp.Symbol(f'gb_{sigma}_{j}_{s}')
                gb_symbols[(sigma, j, s)] = sym
                # [a_sigma, b_{j,s}] = + sym
                # [b_{j,s}, a_sigma] = - sym
                Omega_def[sig_idx, s_idx] = sym
                Omega_def[s_idx, sig_idx] = -sym
                
    # Define Lie superalgebra basis elements
    # We represent basis elements as linear combinations of ordered pairs (i, j) of oscillators
    # In osp(2|2n), generators are quadratic:
    # For fermions: a1+ a1- - 1/2  (so(2))
    # For bosons: bk+ bl+, bk- bl-, bk+ bl- (sp(2n))
    # Mixed: a1^sigma bk^s (odd generators)
    
    generators = []
    
    # Even:
    # 1. H_0 = a1+ a1-
    generators.append({
        'name': 'H_0',
        'parity': 0,
        'terms': [(1, 0, 1)] # 1 * a1+ a1-
    })
    
    # 2. Sp(2n) Cartan: H_k = bk+ bk-
    for k in range(1, n+1):
        bp = 2*k
        bm = 2*k + 1
        generators.append({
            'name': f'H_{k}',
            'parity': 0,
            'terms': [(1, bp, bm)]
        })
        
    # 3. Sp(2n) root vectors:
    # 2 delta_k: (bk+)^2, -2 delta_k: (bk-)^2
    for k in range(1, n+1):
        bp = 2*k
        bm = 2*k + 1
        generators.append({
            'name': f'E_+2d{k}',
            'parity': 0,
            'terms': [(1, bp, bp)]
        })
        generators.append({
            'name': f'E_-2d{k}',
            'parity': 0,
            'terms': [(1, bm, bm)]
        })
        
    # delta_k + delta_l, -delta_k - delta_l, delta_k - delta_l, -delta_k + delta_l
    for k in range(1, n+1):
        for l in range(k+1, n+1):
            kp, km = 2*k, 2*k+1
            lp, lm = 2*l, 2*l+1
            generators.append({'name': f'E_+d{k}+d{l}', 'parity': 0, 'terms': [(1, kp, lp)]})
            generators.append({'name': f'E_-d{k}-d{l}', 'parity': 0, 'terms': [(1, km, lm)]})
            generators.append({'name': f'E_+d{k}-d{l}', 'parity': 0, 'terms': [(1, kp, lm)]})
            generators.append({'name': f'E_-d{k}+d{l}', 'parity': 0, 'terms': [(1, km, lp)]})
            
    # Odd generators:
    for sigma in ['+', '-']:
        sig_idx = 0 if sigma == '+' else 1
        for j in range(1, n+1):
            for s in ['+', '-']:
                s_idx = 2*j if s == '+' else 2*j + 1
                generators.append({
                    'name': f'F_{sigma}eps_{s}d{j}',
                    'parity': 1,
                    'terms': [(1, sig_idx, s_idx)]
                })
                
    dim_g = len(generators)
    
    return {
        'n': n,
        'num_osc': num_osc,
        'osc_names': osc_names,
        'osc_parities': osc_parities,
        'omega0': omega0,
        'Omega_def': Omega_def,
        'gb_symbols': gb_symbols,
        'generators': generators,
        'dim_g': dim_g
    }

print("Algebra setup function ready.")
