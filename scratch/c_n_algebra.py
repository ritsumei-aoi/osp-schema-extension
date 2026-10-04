import sympy as sp
from collections import defaultdict

class OscillatorAlgebra:
    """
    Symbolic algebra for C(n+1) = osp(2|2n) generators and their deformed brackets.
    """
    def __init__(self, n):
        self.n = n
        
        # Deformation parameters gb_{sigma, j, s}
        # sigma in {'+', '-'}, j in 1..n, s in {'+', '-'}
        self.gb_params = {}
        for sigma in ['+', '-']:
            for j in range(1, n + 1):
                for s in ['+', '-']:
                    name = f"gb_{sigma}_{j}_{s}"
                    self.gb_params[(sigma, j, s)] = sp.Symbol(name)

        # Define basis of g = osp(2|2n)
        # Even generators:
        # Z = a1+ a1- - 1/2 (so(2) generator)
        # For sp(2n):
        # E_{2delta_j} = 1/2 (b_j+)^2
        # E_{-2delta_j} = 1/2 (b_j-)^2
        # H_j = b_j+ b_j- + 1/2
        # E_{delta_j + delta_k} = b_j+ b_k+ (j < k)
        # E_{-delta_j - delta_k} = b_j- b_k- (j < k)
        # E_{delta_j - delta_k} = b_j+ b_k- (j != k)
        
        self.even_basis = []
        self.even_basis.append("Z") # Z = a1+ a1- - 1/2
        
        for j in range(1, n + 1):
            self.even_basis.append(f"E_2d_{j}") # 1/2 (b_j+)^2
            self.even_basis.append(f"E_-2d_{j}") # 1/2 (b_j-)^2
            self.even_basis.append(f"H_{j}") # b_j+ b_j- + 1/2
            
        for j in range(1, n + 1):
            for k in range(j + 1, n + 1):
                self.even_basis.append(f"E_d_{j}+d_{k}") # b_j+ b_k+
                self.even_basis.append(f"E_-d_{j}-d_{k}") # b_j- b_k-
                
        for j in range(1, n + 1):
            for k in range(1, n + 1):
                if j != k:
                    self.even_basis.append(f"E_d_{j}-d_{k}") # b_j+ b_k-

        # Odd basis:
        # F_{sigma, j, s} = a1^sigma b_j^s
        self.odd_basis = []
        for sigma in ['+', '-']:
            for j in range(1, n + 1):
                for s in ['+', '-']:
                    self.odd_basis.append(f"F_{sigma}_{j}_{s}")

        self.basis = self.even_basis + self.odd_basis
        self.dim_even = len(self.even_basis)
        self.dim_odd = len(self.odd_basis)
        self.dim = len(self.basis)
        
    def parity(self, elem):
        return 0 if elem in self.even_basis else 1

print("OscillatorAlgebra class created.")
