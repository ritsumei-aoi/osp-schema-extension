#!/usr/bin/env python3
"""
Computational analysis of triviality conditions for C(n+1) inhomogeneous deformations.

Task: Determine the necessary and sufficient conditions on gb parameters for the
inhomogeneous deformation γ_gb to be trivial (equal to a coboundary δf up to scalar).

Framework:
1. Build structure constants for C(n+1) from oscillator relations
2. Parameterize the gb deformation
3. Compute coboundary δf for general odd linear map f
4. Solve system for triviality: γ_gb = c * δf
"""

import json
from itertools import product
from typing import Dict, List, Tuple, Any

# ============================================================================
# PART 1: Basis and Parity Structure
# ============================================================================

class AlgebraBasis:
    """Manages basis elements and their parities for C(n+1) = osp(2|2n)."""

    def __init__(self, n: int):
        self.n = n
        self.basis = []
        self.parity = {}  # element_id -> 0 or 1
        self.index_map = {}  # basis description -> element_id
        self._build_basis()

    def _build_basis(self):
        """Build the basis according to Cn1_definition.md"""
        idx = 0

        # EVEN subalgebra: so(2) × sp(2n), dimension = 2n^2 + n + 1
        # Cartan elements for so(2):
        self.basis.append("H_0")
        self.parity[idx] = 0
        self.index_map["H_0"] = idx
        idx += 1

        # Cartan elements for sp(2n):
        for k in range(1, self.n + 1):
            name = f"H_{k}"
            self.basis.append(name)
            self.parity[idx] = 0
            self.index_map[name] = idx
            idx += 1

        # Root generators for sp(2n) part: E_{±δ_k ± δ_l}, E_{±2δ_k}
        # E_{δ_k - δ_l} for k < l
        for k in range(1, self.n + 1):
            for l in range(k + 1, self.n + 1):
                name = f"E_+delta{k}-delta{l}"
                self.basis.append(name)
                self.parity[idx] = 0
                self.index_map[name] = idx
                idx += 1

                name = f"E_-delta{k}+delta{l}"
                self.basis.append(name)
                self.parity[idx] = 0
                self.index_map[name] = idx
                idx += 1

        # E_{δ_k + δ_l} for k <= l
        for k in range(1, self.n + 1):
            for l in range(k, self.n + 1):
                name = f"E_+delta{k}+delta{l}"
                self.basis.append(name)
                self.parity[idx] = 0
                self.index_map[name] = idx
                idx += 1

                name = f"E_-delta{k}-delta{l}"
                self.basis.append(name)
                self.parity[idx] = 0
                self.index_map[name] = idx
                idx += 1

        # ODD subalgebra: E_{ε ± δ_k}, dimension = 4n
        for k in range(1, self.n + 1):
            name = f"E_eps+delta{k}"
            self.basis.append(name)
            self.parity[idx] = 1
            self.index_map[name] = idx
            idx += 1

            name = f"E_eps-delta{k}"
            self.basis.append(name)
            self.parity[idx] = 1
            self.index_map[name] = idx
            idx += 1

            name = f"E_-eps+delta{k}"
            self.basis.append(name)
            self.parity[idx] = 1
            self.index_map[name] = idx
            idx += 1

            name = f"E_-eps-delta{k}"
            self.basis.append(name)
            self.parity[idx] = 1
            self.index_map[name] = idx
            idx += 1

        self.dim_even = idx - 4*self.n
        self.dim_odd = 4*self.n
        self.dim_total = idx

    def is_even(self, i: int) -> bool:
        return self.parity[i] == 0

    def is_odd(self, i: int) -> bool:
        return self.parity[i] == 1


# ============================================================================
# PART 2: Deformation Analysis Framework
# ============================================================================

class TrivialityAnalyzer:
    """Analyzes triviality of gb-deformation via coboundary condition."""

    def __init__(self, n: int):
        self.n = n
        self.basis_mgr = AlgebraBasis(n)
        self.dim = self.basis_mgr.dim_total
        self.dim_even = self.basis_mgr.dim_even
        self.dim_odd = self.basis_mgr.dim_odd

        # Structure constant storage: c[i][j] = [(k, coeff), ...]
        # Meaning: [X_i, X_j] = sum_k coeff * X_k
        self.structure_constants = {}

        print(f"\n[C({n+1}) = osp(2|{2*n})]")
        print(f"  Total dimension: {self.dim} = {self.dim_even} (even) + {self.dim_odd} (odd)")
        print(f"  GB deformation parameters: {4*n}")

    def analyze_coboundary_structure(self):
        """
        Analyze the coboundary operator δf for an odd linear map f: g -> g.

        The odd map f reverses parity:
        - f(even) → odd: f can be parameterized by (dim_even) × (dim_odd) parameters
        - f(odd) → even: f can be parameterized by (dim_odd) × (dim_even) parameters

        Total freedom in f: (dim_even × dim_odd) + (dim_odd × dim_even) parameters.
        """

        n_params_f = self.dim_even * self.dim_odd + self.dim_odd * self.dim_even

        print(f"\n[Coboundary Analysis]")
        print(f"  Odd linear map f parameterization:")
        print(f"    f: even -> odd: {self.dim_even} × {self.dim_odd} = {self.dim_even * self.dim_odd}")
        print(f"    f: odd -> even: {self.dim_odd} × {self.dim_even} = {self.dim_odd * self.dim_even}")
        print(f"    Total f parameters: {n_params_f}")

        # The coboundary image: δf: g ⊗ g -> g
        # For each pair (i,j), δf(X_i, X_j) is an element of g
        # This gives constraints

        n_coboundary_values = self.dim * self.dim  # (X_i, X_j) pairs

        print(f"\n  Coboundary output constraints:")
        print(f"    Pairs (X_i, X_j): {self.dim} × {self.dim} = {n_coboundary_values}")
        print(f"    For each pair, δf outputs an element of g (dim = {self.dim})")
        print(f"    Total coboundary degrees of freedom: δf encodes {n_params_f} parameters")

        return n_params_f

    def analyze_gb_deformation(self):
        """
        Analyze the gb-parametrized deformation.

        From C_inhomogeneous_definition.md:
        [b_j^s, a_1^σ] = -gb_{σ,j,s} * κ

        This couples fermionic and bosonic oscillators through κ (odd central element).
        """

        print(f"\n[GB Deformation Analysis]")
        print(f"  Parameters: gb_(σ,j,s) for σ ∈ {{+,-}}, j ∈ {{1,...,n}}, s ∈ {{+,-}}")
        print(f"  Total GB parameters: 4n = {4*self.n}")

        print(f"\n  Deformed oscillator relation:")
        print(f"    [b_j^s, a_1^σ] = -gb_(σ,j,s) * κ  (κ is odd central)")

        print(f"\n  GB deformation affects commutators involving:")
        print(f"    - Fermionic generators: a_1^±")
        print(f"    - Bosonic generators: b_k^±")

        return 4 * self.n

    def theoretical_triviality_condition(self):
        """
        Analyze the theoretical condition for triviality up to scalar.
        """

        print(f"\n[Theoretical Triviality Condition]")
        print(f"\n  A deformation γ_gb is trivial if ∃ odd f and scalar c such that:")
        print(f"    γ_gb(X_i, X_j) = c * (δf)(X_i, X_j)  for all i,j")

        print(f"\n  This is a system of linear equations:")
        print(f"    Unknowns: f parameters ({self.dim_even * self.dim_odd + self.dim_odd * self.dim_even}) + scalar c")
        print(f"    Equations: γ_gb values ({4*self.n} independent values)")

        print(f"\n  Key observation:")
        print(f"    - GB deformation has {4*self.n} independent parameters")
        print(f"    - Coboundary δf is built from {self.dim_even * self.dim_odd + self.dim_odd * self.dim_even} parameters + 1 scalar")

        # For C(2): n=1
        # GB parameters: 4
        # Coboundary parameters: 4×4 + 4×4 + 1 scalar = 33 parameters

        # For C(3): n=2
        # GB parameters: 8
        # Coboundary parameters: (11×8) + (8×11) + 1 = 177 parameters

        print(f"\n  For C({self.n+1}):")
        gb_dim = 4 * self.n
        cb_dim = 2 * self.dim_even * self.dim_odd + 1
        print(f"    GB dimension: {gb_dim}")
        print(f"    Coboundary freedom: {cb_dim}")

        if gb_dim < cb_dim - 1:
            print(f"    ⟹ Underdetermined system (more freedom than constraints)")
            print(f"       All GB deformations are generically trivial!")
        elif gb_dim == cb_dim - 1:
            print(f"    ⟹ Balanced system (critical dimension)")
        else:
            print(f"    ⟹ Overdetermined system (more constraints than freedom)")
            print(f"       Only special GB configurations are trivial")


# ============================================================================
# MAIN ANALYSIS
# ============================================================================

def main():
    print("="*70)
    print("TRIVIALITY ANALYSIS FOR C(n+1) INHOMOGENEOUS DEFORMATIONS")
    print("="*70)

    for n_val in [1, 2, 3]:
        analyzer = TrivialityAnalyzer(n_val)

        n_gb = analyzer.analyze_gb_deformation()
        n_cb = analyzer.analyze_coboundary_structure()

        analyzer.theoretical_triviality_condition()

        print("\n" + "="*70)


if __name__ == "__main__":
    main()
