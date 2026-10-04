import json
from fractions import Fraction
import numpy as np
from typing import Dict, List, Tuple, Any

class TrivialitySolver:
    def __init__(self, n: int):
        self.n = n
        with open(f"data/C_{n}_gamma.json", "r") as f:
            self.schema2 = json.load(f)
        with open(f"data/C_{n}_coboundary.json", "r") as f:
            self.schema4 = json.load(f)

        self.basis_even = self.schema2["basis"]["even"]
        self.basis_odd = self.schema2["basis"]["odd"]
        self.basis_all = self.basis_odd + self.basis_even
        self.basis_with_K = self.basis_all + ["K"]

        self.gb_params = self.schema2["inhomogeneous_deformation"]["gb_matrix"]["parameters"]
        self.map_params = self.schema4["coboundary_structure"]["map_parameters"]

        # Build index maps
        self.gb_idx = {param: i for i, param in enumerate(self.gb_params)}
        self.map_idx = {param: i for i, param in enumerate(self.map_params)}

        # Filter unique pairs (X, Y) with X <= Y in PBW order to avoid redundant anti-symmetric equations
        self.pairs = []
        for i, x in enumerate(self.basis_all):
            for j in range(i, len(self.basis_all)):
                y = self.basis_all[j]
                self.pairs.append((x, y))

        # Build list of equations indexed by ((X, Y), Z)
        self.eq_keys = []
        for pair in self.pairs:
            for z in self.basis_with_K:
                self.eq_keys.append((pair, z))
        self.eq_idx = {key: i for i, key in enumerate(self.eq_keys)}

        # Construct Coboundary Matrix M (num_eqs x num_map_params)
        self.M = np.zeros((len(self.eq_keys), len(self.map_params)), dtype=object)
        for sc in self.schema4["coboundary_structure"]["coboundary_coefficients"]:
            x, y, z, map_p = sc["X"], sc["Y"], sc["Z"], sc["map_param"]
            # Enforce pair ordering (X <= Y)
            if (x, y) in self.pairs:
                pair = (x, y)
                sign_factor = Fraction(1)
            elif (y, x) in self.pairs:
                pair = (y, x)
                # [Y, X] = - (-1)^{px py} [X, Y]
                px, py = self.schema2["parity"][x], self.schema2["parity"][y]
                sign_factor = Fraction(-1) if (px == 1 and py == 1) else Fraction(-1)
            else:
                continue

            eq_k = (pair, z)
            if eq_k in self.eq_idx and map_p in self.map_idx:
                r = self.eq_idx[eq_k]
                c = self.map_idx[map_p]
                self.M[r, c] += Fraction(sc["coeff"]) * sign_factor

        # Construct Gamma Matrix G (num_eqs x num_gb_params)
        self.G = np.zeros((len(self.eq_keys), len(self.gb_params)), dtype=object)
        for gsc in self.schema2["inhomogeneous_deformation"]["gamma_structure_constants"]:
            x, y, z, gb_p = gsc["X"], gsc["Y"], gsc["Z"], gsc["gb_param"]
            if (x, y) in self.pairs:
                pair = (x, y)
                sign_factor = Fraction(1)
            elif (y, x) in self.pairs:
                pair = (y, x)
                px, py = self.schema2["parity"][x], self.schema2["parity"][y]
                sign_factor = Fraction(-1) if (px == 1 and py == 1) else Fraction(-1)
            else:
                continue

            eq_k = (pair, z)
            if eq_k in self.eq_idx and gb_p in self.gb_idx:
                r = self.eq_idx[eq_k]
                c = self.gb_idx[gb_p]
                self.G[r, c] += Fraction(gsc["coeff"]) * sign_factor

    def analyze_triviality(self, gb_values: Dict[str, int]) -> Tuple[bool, str]:
        # Form RHS vector v = G * gb_vector
        gb_vec = np.zeros(len(self.gb_params), dtype=object)
        for p, val in gb_values.items():
            gb_vec[self.gb_idx[p]] = Fraction(val)

        v = self.G.dot(gb_vec)

        # Solve M * phi = v
        from src.C_generators import gaussian_elimination_fractions
        sol = gaussian_elimination_fractions(self.M, v)
        if sol is None:
            return False, "Non-trivial (No solution phi exists for M phi = gamma(gb))"
        else:
            return True, "Trivial (Solution phi exists)"

    def solve_symbolic_conditions(self):
        """
        Computes row echelon form of [M | G] to extract exact linear constraints on gb.
        """
        rows, cols_M = self.M.shape
        cols_G = self.G.shape[1]
        
        # Augmented matrix [M | G]
        Aug = [[self.M[r, c] for c in range(cols_M)] + [self.G[r, c] for c in range(cols_G)] for r in range(rows)]

        pivot_row = 0
        for c in range(cols_M):
            if pivot_row >= rows:
                break
            r_pivot = -1
            for r in range(pivot_row, rows):
                if Aug[r][c] != 0:
                    r_pivot = r
                    break
            if r_pivot == -1:
                continue

            Aug[pivot_row], Aug[r_pivot] = Aug[r_pivot], Aug[pivot_row]
            pivot_val = Aug[pivot_row][c]

            for j in range(c, cols_M + cols_G):
                Aug[pivot_row][j] /= pivot_val

            for r in range(rows):
                if r != pivot_row and Aug[r][c] != 0:
                    factor = Aug[r][c]
                    for j in range(c, cols_M + cols_G):
                        Aug[r][j] -= factor * Aug[pivot_row][j]

            pivot_row += 1

        # Zero rows in M part give constraints on G part!
        constraints = []
        for r in range(pivot_row, rows):
            gb_row = Aug[r][cols_M:]
            if any(val != 0 for val in gb_row):
                # Extract linear equation in gb
                eq_terms = []
                for c, val in enumerate(gb_row):
                    if val != 0:
                        gb_p = self.gb_params[c]
                        val_str = str(val.numerator) if val.denominator == 1 else f"{val.numerator}/{val.denominator}"
                        eq_terms.append(f"{val_str} * {gb_p}")
                constraints.append(" + ".join(eq_terms) + " = 0")

        return constraints

if __name__ == "__main__":
    for n in [1, 2, 3]:
        solver = TrivialitySolver(n)
        
        # Case 1: Uniform profile all +1
        gb_all_ones = {p: 1 for p in solver.gb_params}
        is_triv_ones, msg_ones = solver.analyze_triviality(gb_all_ones)
        
        # Case 2: All zeros
        gb_all_zeros = {p: 0 for p in solver.gb_params}
        is_triv_zeros, msg_zeros = solver.analyze_triviality(gb_all_zeros)

        # Symbolic constraints
        constraints = solver.solve_symbolic_conditions()

        print(f"C({n+1}) Triviality Analysis:")
        print(f"  All +1 profile: {msg_ones}")
        print(f"  All 0  profile: {msg_zeros}")
        print(f"  Constraint equations count on gb: {len(constraints)}")
        if constraints:
            print("  Sample constraints on gb:")
            for eq in constraints[:10]:
                print(f"    {eq}")
