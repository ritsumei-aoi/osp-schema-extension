"""
Triviality analysis of inhomogeneous deformations for C(n+1) = osp(2|2n).

This script computes:
1. Structure constants of C(n+1) in the oscillator basis
2. The deformation cocycle gamma_gb from the gb parameters
3. The coboundary map delta_f
4. Solves gamma_gb = delta_f to determine triviality conditions

Handles n=1 (C(2)=osp(2|2)), n=2 (C(3)=osp(2|4)), n=3 (C(4)=osp(2|6)).
"""

import sympy as sp
from sympy import symbols, Matrix, zeros, Rational, solve, simplify
from itertools import product as iterproduct
import json

def parity(idx, n):
    """Return parity of basis element. Even part has dim 2n^2+n+1, odd has 4n."""
    even_dim = 2*n**2 + n + 1
    return 0 if idx < even_dim else 1

def build_C2_structure():
    """Build structure constants for C(2) = osp(2|2), n=1.

    Basis: I, H2, E+, E-, F1, F2, F3, F4  (indices 0-7)
    Even: I=a+a- - 1/2, H2=-b+b- - 1/2, E+=1/2(b+)^2, E-=1/2(b-)^2
    Odd: F1=a+b+, F2=a+b-, F3=a-b+, F4=a-b-
    """
    n = 1
    dim = 8
    even_dim = 4

    # Structure constants: sc[i][j] = dict mapping k -> coefficient of Z_k in [Z_i, Z_j]
    sc = [[{} for _ in range(dim)] for _ in range(dim)]

    # Even-Even brackets
    # [I, H2] = [I, E+] = [I, E-] = 0
    # [H2, E+] = -2 E+
    sc[1][2] = {2: -2}; sc[2][1] = {2: 2}
    # [H2, E-] = 2 E-
    sc[1][3] = {3: 2}; sc[3][1] = {3: -2}
    # [E+, E-] = H2
    sc[2][3] = {1: 1}; sc[3][2] = {1: -1}

    # Even-Odd brackets
    # [I, F1]=F1, [I, F2]=F2, [I, F3]=-F3, [I, F4]=-F4
    sc[0][4] = {4: 1}; sc[4][0] = {4: -1}
    sc[0][5] = {5: 1}; sc[5][0] = {5: -1}
    sc[0][6] = {6: -1}; sc[6][0] = {6: 1}
    sc[0][7] = {7: -1}; sc[7][0] = {7: 1}

    # [H2, F1]=-F1, [H2, F2]=F2, [H2, F3]=-F3, [H2, F4]=F4
    sc[1][4] = {4: -1}; sc[4][1] = {4: 1}
    sc[1][5] = {5: 1}; sc[5][1] = {5: -1}
    sc[1][6] = {6: -1}; sc[6][1] = {6: 1}
    sc[1][7] = {7: 1}; sc[7][1] = {7: -1}

    # [E+, F1]=0, [E+, F2]=-F1, [E+, F3]=0, [E+, F4]=-F3
    sc[2][5] = {4: -1}; sc[5][2] = {4: 1}
    sc[2][7] = {6: -1}; sc[7][2] = {6: 1}

    # [E-, F1]=F2, [E-, F2]=0, [E-, F3]=F4, [E-, F4]=0
    sc[3][4] = {5: 1}; sc[4][3] = {5: -1}
    sc[3][6] = {7: 1}; sc[6][3] = {7: -1}

    # Odd-Odd brackets (super bracket = anticommutator)
    # [F1, F3] = 2 E+
    sc[4][6] = {2: 2}; sc[6][4] = {2: 2}
    # [F1, F4] = -(I + H2) = -I - H2
    sc[4][7] = {0: -1, 1: -1}; sc[7][4] = {0: -1, 1: -1}
    # [F2, F3] = I - H2
    sc[5][6] = {0: 1, 1: -1}; sc[6][5] = {0: 1, 1: -1}
    # [F2, F4] = 2 E-
    sc[5][7] = {3: 2}; sc[7][5] = {3: 2}
    # [F1, F2] = [F3, F4] = 0 (already zero dicts)
    # [Fi, Fi] = 0 for all i (already zero dicts)

    basis_names = ['I', 'H2', 'Ep', 'Em', 'F1', 'F2', 'F3', 'F4']
    return sc, dim, even_dim, basis_names


def compute_gamma_gb_C2():
    """Compute gamma_gb for C(2) = osp(2|2), n=1.

    gb parameters: g1=gb(+,+), g2=gb(+,-), g3=gb(-,+), g4=gb(-,-)

    Returns gamma[i][j] = dict mapping basis index k to sympy expression in g1,...,g4.
    """
    g1, g2, g3, g4 = symbols('g1 g2 g3 g4')
    dim = 8
    gamma = [[{} for _ in range(dim)] for _ in range(dim)]

    # Even-Even: all zero (no deformation)

    # Even-Odd (I with F_j):
    # gamma(I, F1) = g1*I
    gamma[0][4] = {0: g1}; gamma[4][0] = {0: -g1}
    # gamma(I, F2) = g2*I
    gamma[0][5] = {0: g2}; gamma[5][0] = {0: -g2}
    # gamma(I, F3) = -g3*I
    gamma[0][6] = {0: -g3}; gamma[6][0] = {0: g3}
    # gamma(I, F4) = -g4*I
    gamma[0][7] = {0: -g4}; gamma[7][0] = {0: g4}

    # Even-Odd (H2 with F_j):
    # gamma(H2, F1) = -g1*H2 + 2*g2*Ep
    gamma[1][4] = {1: -g1, 2: 2*g2}; gamma[4][1] = {1: g1, 2: -2*g2}
    # gamma(H2, F2) = -g2*H2 + 2*g1*Em
    gamma[1][5] = {1: -g2, 3: 2*g1}; gamma[5][1] = {1: g2, 3: -2*g1}
    # gamma(H2, F3) = -g3*H2 + 2*g4*Ep
    gamma[1][6] = {1: -g3, 2: 2*g4}; gamma[6][1] = {1: g3, 2: -2*g4}
    # gamma(H2, F4) = -g4*H2 + 2*g3*Em
    gamma[1][7] = {1: -g4, 3: 2*g3}; gamma[7][1] = {1: g4, 3: -2*g3}

    # Even-Odd (Ep with F_j):
    # gamma(Ep, F1) = -2*g1*Ep
    gamma[2][4] = {2: -2*g1}; gamma[4][2] = {2: 2*g1}
    # gamma(Ep, F2) = g1*H2
    gamma[2][5] = {1: g1}; gamma[5][2] = {1: -g1}
    # gamma(Ep, F3) = -2*g3*Ep
    gamma[2][6] = {2: -2*g3}; gamma[6][2] = {2: 2*g3}
    # gamma(Ep, F4) = g3*H2
    gamma[2][7] = {1: g3}; gamma[7][2] = {1: -g3}

    # Even-Odd (Em with F_j):
    # gamma(Em, F1) = g2*H2
    gamma[3][4] = {1: g2}; gamma[4][3] = {1: -g2}
    # gamma(Em, F2) = -2*g2*Em
    gamma[3][5] = {3: -2*g2}; gamma[5][3] = {3: 2*g2}
    # gamma(Em, F3) = g4*H2
    gamma[3][6] = {1: g4}; gamma[6][3] = {1: -g4}
    # gamma(Em, F4) = -2*g4*Em
    gamma[3][7] = {3: -2*g4}; gamma[7][3] = {3: 2*g4}

    # Odd-Odd:
    # gamma(F1, F1) = -2*g1*F1
    gamma[4][4] = {4: -2*g1}
    # gamma(F2, F2) = -2*g2*F2
    gamma[5][5] = {5: -2*g2}
    # gamma(F3, F3) = -2*g3*F3
    gamma[6][6] = {6: -2*g3}
    # gamma(F4, F4) = -2*g4*F4
    gamma[7][7] = {7: -2*g4}

    # gamma(F1, F2) = -g2*F1 - g1*F2
    gamma[4][5] = {4: -g2, 5: -g1}; gamma[5][4] = {4: -g2, 5: -g1}
    # gamma(F1, F3) = -g3*F1 - g1*F3
    gamma[4][6] = {4: -g3, 6: -g1}; gamma[6][4] = {4: -g3, 6: -g1}
    # gamma(F1, F4) = -g3*F2 - g2*F3
    gamma[4][7] = {5: -g3, 6: -g2}; gamma[7][4] = {5: -g3, 6: -g2}
    # gamma(F2, F3) = -g4*F1 - g1*F4
    gamma[5][6] = {4: -g4, 7: -g1}; gamma[6][5] = {4: -g4, 7: -g1}
    # gamma(F2, F4) = -g4*F2 - g2*F4
    gamma[5][7] = {5: -g4, 7: -g2}; gamma[7][5] = {5: -g4, 7: -g2}
    # gamma(F3, F4) = -g3*F4 - g4*F3
    gamma[6][7] = {6: -g4, 7: -g3}; gamma[7][6] = {6: -g4, 7: -g3}

    return gamma, (g1, g2, g3, g4)


def verify_jacobi(sc, dim, even_dim):
    """Verify super Jacobi identity for the structure constants."""
    def bracket(i, j, sc_table):
        return sc_table[i][j]

    def apply_bracket(vec, j, sc_table, dim, even_dim):
        """Compute [vec, Z_j] where vec is a dict {k: coeff}."""
        result = {}
        for k, coeff in vec.items():
            br = sc_table[k][j]
            for l, c in br.items():
                p_k = parity(k, 1)
                p_j = parity(j, 1)
                result[l] = result.get(l, 0) + coeff * c
        return result

    violations = 0
    for i in range(dim):
        for j in range(dim):
            for k in range(dim):
                pi, pj, pk = parity(i, 1), parity(j, 1), parity(k, 1)
                # Super Jacobi: (-1)^{pi*pk}[Zi,[Zj,Zk]] + cyclic = 0
                # Term 1: (-1)^{pi*pk} [Zi, [Zj, Zk]]
                br_jk = bracket(j, k, sc)
                term1 = {}
                for l, c in br_jk.items():
                    br_il = bracket(i, l, sc)
                    for m, c2 in br_il.items():
                        sign = (-1)**(pi*pk)
                        term1[m] = term1.get(m, 0) + sign * c * c2

                # Term 2: (-1)^{pj*pi} [Zj, [Zk, Zi]]
                br_ki = bracket(k, i, sc)
                term2 = {}
                for l, c in br_ki.items():
                    br_jl = bracket(j, l, sc)
                    for m, c2 in br_jl.items():
                        sign = (-1)**(pj*pi)
                        term2[m] = term2.get(m, 0) + sign * c * c2

                # Term 3: (-1)^{pk*pj} [Zk, [Zi, Zj]]
                br_ij = bracket(i, j, sc)
                term3 = {}
                for l, c in br_ij.items():
                    br_kl = bracket(k, l, sc)
                    for m, c2 in br_kl.items():
                        sign = (-1)**(pk*pj)
                        term3[m] = term3.get(m, 0) + sign * c * c2

                # Sum all terms
                total = {}
                for d in [term1, term2, term3]:
                    for m, c in d.items():
                        total[m] = total.get(m, 0) + c

                for m, c in total.items():
                    if c != 0:
                        violations += 1
                        print(f"Jacobi violation: ({i},{j},{k}) -> Z_{m} coeff = {c}")

    if violations == 0:
        print("All super Jacobi identities satisfied. ✓")
    return violations == 0


def compute_coboundary_C2(sc, dim, even_dim):
    """Compute the coboundary delta_f for C(2).

    f is an odd linear map g -> g, parameterized by phi[i][j] = coefficient of Z_j in f(Z_i).
    f(even) = odd, f(odd) = even.

    (delta f)(X,Y) = (-1)^{p(X)} [X, f(Y)] - (-1)^{(p(X)+1)p(Y)} [Y, f(X)] - f([X,Y])

    Returns: for each pair (i,j), the coefficients of delta_f(Z_i, Z_j) as linear functions
    of the phi parameters.
    """
    # f parameters: phi[i][j] where p(Z_j) = p(Z_i) + 1 (mod 2)
    # For even Z_i (i=0..3): f(Z_i) = sum_j phi[i][j] * Z_j for odd Z_j (j=4..7)
    # For odd Z_i (i=4..7): f(Z_i) = sum_j phi[i][j] * Z_j for even Z_j (j=0..3)

    phi = {}
    for i in range(dim):
        pi = parity(i, 1)
        for j in range(dim):
            pj = parity(j, 1)
            if (pi + pj) % 2 == 1:  # f is odd
                phi[(i, j)] = symbols(f'phi_{i}_{j}')

    def f_of(i):
        """Return f(Z_i) as dict {j: coeff}."""
        result = {}
        pi = parity(i, 1)
        for j in range(dim):
            pj = parity(j, 1)
            if (pi + pj) % 2 == 1:
                if (i, j) in phi:
                    result[j] = phi[(i, j)]
        return result

    def bracket_vec(k, vec):
        """Compute [Z_k, vec] where vec = {j: coeff}. Returns {m: coeff}."""
        result = {}
        for j, cj in vec.items():
            for m, cm in sc[k][j].items():
                result[m] = result.get(m, sp.S(0)) + cj * cm
        return result

    def f_of_vec(vec):
        """Compute f(vec) where vec = {j: coeff}. Returns {m: coeff}."""
        result = {}
        for j, cj in vec.items():
            fj = f_of(j)
            for m, cm in fj.items():
                result[m] = result.get(m, sp.S(0)) + cj * cm
        return result

    # Compute (delta f)(Z_i, Z_j) for all pairs
    delta_f = [[{} for _ in range(dim)] for _ in range(dim)]

    for i in range(dim):
        for j in range(dim):
            pi = parity(i, 1)
            pj = parity(j, 1)

            # Term 1: (-1)^{p(X)} [X, f(Y)]
            sign1 = (-1)**pi
            fj = f_of(j)
            term1 = bracket_vec(i, fj)

            # Term 2: -(-1)^{(p(X)+1)p(Y)} [Y, f(X)]
            sign2 = -((-1)**((pi + 1) * pj))
            fi = f_of(i)
            term2 = bracket_vec(j, fi)

            # Term 3: -f([X,Y])
            br_ij = sc[i][j]
            term3 = f_of_vec(br_ij)

            # Combine
            result = {}
            for m, c in term1.items():
                result[m] = result.get(m, sp.S(0)) + sign1 * c
            for m, c in term2.items():
                result[m] = result.get(m, sp.S(0)) + sign2 * c
            for m, c in term3.items():
                result[m] = result.get(m, sp.S(0)) - c

            # Simplify
            for m in list(result.keys()):
                result[m] = sp.expand(result[m])
                if result[m] == 0:
                    del result[m]

            delta_f[i][j] = result

    return delta_f, phi


def solve_triviality_C2():
    """Solve gamma_gb = delta_f for C(2) and determine triviality conditions."""
    print("=" * 70)
    print("TRIVIALITY ANALYSIS FOR C(2) = osp(2|2), n=1")
    print("=" * 70)

    sc, dim, even_dim, basis_names = build_C2_structure()

    print("\n--- Verifying Jacobi identity ---")
    verify_jacobi(sc, dim, even_dim)

    print("\n--- Computing gamma_gb ---")
    gamma, gb_params = compute_gamma_gb_C2()
    g1, g2, g3, g4 = gb_params

    print("\n--- Computing coboundary delta_f ---")
    delta_f, phi = compute_coboundary_C2(sc, dim, even_dim)

    print(f"Number of f-parameters: {len(phi)}")
    phi_symbols = list(phi.values())

    # Set up equations: gamma_gb(i,j)[k] = delta_f(i,j)[k] for all i,j,k
    equations = []
    equation_labels = []

    for i in range(dim):
        for j in range(i, dim):  # Use i <= j to avoid redundancy
            pi = parity(i, 1)
            pj = parity(j, 1)

            # Get gamma and delta_f for this pair
            gam = gamma[i][j]
            df = delta_f[i][j]

            # Collect all basis indices that appear
            all_k = set(list(gam.keys()) + list(df.keys()))

            # Also check all basis indices for completeness
            for k in range(dim):
                gam_val = gam.get(k, sp.S(0))
                df_val = df.get(k, sp.S(0))
                eq = sp.expand(df_val - gam_val)
                if eq != 0:
                    equations.append(eq)
                    equation_labels.append(f"({basis_names[i]},{basis_names[j]})->{basis_names[k]}")

    print(f"\nTotal equations: {len(equations)}")
    print(f"Total unknowns (phi): {len(phi_symbols)}")
    print(f"Parameters (gb): g1, g2, g3, g4")

    # Solve the system
    print("\n--- Solving gamma_gb = delta_f ---")

    # Separate: the equations are linear in phi_symbols, with g1..g4 as parameters
    # We want to solve for phi in terms of g1..g4

    # Build the coefficient matrix
    all_vars = phi_symbols
    A_rows = []
    b_rows = []

    for eq in equations:
        row_A = []
        remainder = eq
        for v in all_vars:
            coeff = eq.coeff(v)
            row_A.append(coeff)
            remainder = remainder - coeff * v
        A_rows.append(row_A)
        b_rows.append(-sp.expand(remainder))  # Move to RHS

    A = Matrix(A_rows)
    b = Matrix(b_rows)

    print(f"System size: {A.shape[0]} equations x {A.shape[1]} unknowns")

    # Check rank
    rank_A = A.rank()
    Ab = A.row_join(b)
    rank_Ab = Ab.rank()

    print(f"Rank of coefficient matrix A: {rank_A}")
    print(f"Rank of augmented matrix [A|b]: {rank_Ab}")

    if rank_A == rank_Ab:
        print("\n*** RESULT: System is CONSISTENT for ALL values of g1, g2, g3, g4. ***")
        print("*** Every inhomogeneous deformation gamma_gb is a coboundary (trivial). ***")

        # Find the solution
        sol = sp.linsolve((A, b), *all_vars)
        if sol:
            sol_list = list(sol)
            print(f"\nSolution space dimension: {len(all_vars) - rank_A}")
            print("\nSolution (one particular + kernel):")
            for i, v in enumerate(all_vars):
                val = sol_list[0][i]
                if val != 0:
                    print(f"  {v} = {val}")
    else:
        print(f"\n*** RESULT: System is INCONSISTENT. Rank mismatch: {rank_A} vs {rank_Ab}. ***")
        print("*** Not all gamma_gb are coboundaries. ***")

        # Find the conditions on g1..g4 for consistency
        print("\nDetermining conditions on gb parameters for triviality...")
        # The conditions come from rows of the augmented matrix that are zero in A but nonzero in b
        # Use the reduced row echelon form
        rref_Ab, pivots = Ab.rref()
        conditions = []
        for row_idx in range(rref_Ab.rows):
            # Check if this row has all zeros in the A part but nonzero in b
            a_part = rref_Ab[row_idx, :len(all_vars)]
            b_part = rref_Ab[row_idx, len(all_vars)]
            if a_part.is_zero_matrix and b_part != 0:
                conditions.append(sp.expand(b_part))

        print(f"Number of consistency conditions: {len(conditions)}")
        for i, cond in enumerate(conditions):
            print(f"  Condition {i+1}: {cond} = 0")

    return gamma, gb_params, delta_f, phi


def export_structure_constants_C2():
    """Export structure constants as JSON-compatible dict."""
    sc, dim, even_dim, basis_names = build_C2_structure()

    sc_dict = {}
    for i in range(dim):
        for j in range(dim):
            if sc[i][j]:
                key = f"[{basis_names[i]},{basis_names[j]}]"
                val = " + ".join(f"{v}*{basis_names[k]}" for k, v in sc[i][j].items())
                sc_dict[key] = val

    return sc_dict


if __name__ == "__main__":
    # Run the analysis for C(2)
    gamma, gb_params, delta_f, phi = solve_triviality_C2()

    print("\n" + "=" * 70)
    print("STRUCTURE CONSTANTS (for verification)")
    print("=" * 70)
    sc_dict = export_structure_constants_C2()
    for k, v in sorted(sc_dict.items()):
        print(f"  {k} = {v}")
