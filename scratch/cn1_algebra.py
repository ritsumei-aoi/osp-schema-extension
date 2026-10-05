import sympy as sp
from sympy import symbols, Matrix, zeros, simplify, solve, Symbol

class Cn1Algebra:
    def __init__(self, n):
        self.n = n
        # Define gb parameters: gb_{\sigma, j, s} where \sigma \in {+, -}, j \in {1..n}, s \in {+, -}
        self.gb = {}
        for sigma in ['+', '-']:
            for j in range(1, n + 1):
                for s in ['+', '-']:
                    name = f"gb_{sigma}_{j}_{s}"
                    self.gb[(sigma, j, s)] = Symbol(name)
        
        # Build basis of C(n+1)
        # Even generators:
        # J0 = a1+ a1-
        # For each pair of bosonic operators (j, s) and (k, t):
        # We can list bosonic pairs:
        bosons = []
        for j in range(1, n + 1):
            bosons.append((j, '+'))
            bosons.append((j, '-'))
        
        self.even_basis = ['J0']
        # Bosonic quadratic generators:
        # (j, s), (k, t) with index1 <= index2
        self.boson_pairs = []
        for i in range(len(bosons)):
            for j in range(i, len(bosons)):
                self.boson_pairs.append((bosons[i], bosons[j]))
                b1, b2 = bosons[i], bosons[j]
                self.even_basis.append(f"B_({b1[0]},{b1[1]})_({b2[0]},{b2[1]})")
        
        # Odd generators: F_{\sigma, j, s} = a1^\sigma b_j^s
        self.odd_basis = []
        for sigma in ['+', '-']:
            for j in range(1, n + 1):
                for s in ['+', '-']:
                    self.odd_basis.append(f"F_{sigma}_{j}_{s}")
        
        self.dim_even = len(self.even_basis)
        self.dim_odd = len(self.odd_basis)
        self.dim_total = self.dim_even + self.dim_odd

        print(f"Initialized C({n+1}): dim_even = {self.dim_even}, dim_odd = {self.dim_odd}, total = {self.dim_total}")

if __name__ == '__main__':
    for n in [1, 2, 3]:
        alg = Cn1Algebra(n)
