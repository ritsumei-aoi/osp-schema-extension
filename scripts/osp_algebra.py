"""
Comprehensive algebraic verification of the triviality condition for C(n+1) = osp(2|2n).
Constructs the algebra, the deformed bracket gamma_gb, the coboundary delta f,
and computes the exact constraint space on gb parameters.
"""

import sympy as sp
from collections import defaultdict
import json
import os

class OspAlgebra:
    def __init__(self, n):
        self.n = n
        self.build_basis()
        self.build_gb_params()
        
    def build_basis(self):
        n = self.n
        self.even_generators = []
        self.odd_generators = []
        
        # Cartan generators: H_1, ..., H_{n+1}
        for i in range(1, n + 2):
            self.even_generators.append(f'H_{i}')
            
        # Long roots: E_{2d_k}, E_{-2d_k}
        for k in range(1, n + 1):
            self.even_generators.append(f'E_2d_{k}')
            self.even_generators.append(f'E_-2d_{k}')
            
        # Short roots: k < l
        for k in range(1, n + 1):
            for l in range(k + 1, n + 1):
                self.even_generators.append(f'E_d{k}+d{l}')
                self.even_generators.append(f'E_-d{k}-d{l}')
                self.even_generators.append(f'E_d{k}-d{l}')
                self.even_generators.append(f'E_d{l}-d{k}')
                
        # Odd generators: F_{sigma, k, s}
        for k in range(1, n + 1):
            self.odd_generators.append(f'F_p_{k}_p')
            self.odd_generators.append(f'F_p_{k}_m')
            self.odd_generators.append(f'F_m_{k}_p')
            self.odd_generators.append(f'F_m_{k}_m')
            
        self.basis = self.even_generators + self.odd_generators
        self.dim_even = len(self.even_generators)
        self.dim_odd = len(self.odd_generators)
        self.dim_total = len(self.basis)
        
        # Parity dict
        self.parity = {}
        for g in self.even_generators:
            self.parity[g] = 0
        for g in self.odd_generators:
            self.parity[g] = 1

    def build_gb_params(self):
        n = self.n
        self.gb_dict = {}
        self.gb_symbols = []
        for k in range(1, n + 1):
            for sigma in ['+', '-']:
                for s in ['+', '-']:
                    sig_char = 'p' if sigma == '+' else 'm'
                    s_char = 'p' if s == '+' else 'm'
                    sym = sp.Symbol(f'gb_{sig_char}_{k}_{s_char}')
                    self.gb_dict[(sigma, k, s)] = sym
                    self.gb_symbols.append(sym)

print('OspAlgebra class skeleton ready')
