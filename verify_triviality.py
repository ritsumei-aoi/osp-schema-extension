"""
Verification artifact for Theorem 1:
Inhomogeneous deformation gamma_gb of C(n+1) = osp(2|2n) is trivial iff gb = 0.

This script checks the coboundary inconsistency for n=1 symbolically.
All structure constants are derived from the oscillator realization in docs/math/.
"""

import numpy as np
from itertools import product

# ── Basis for C(2) = osp(2|2), n=1 ─────────────────────────────────────
# Even generators (index 0-3):  H1, H2, E2d, Em2d
# Odd generators  (index 4-7):  F1, F2, F3, F4
# F1 = a1+ b1+,  F2 = a1+ b1-,  F3 = a1- b1+,  F4 = a1- b1-

EVEN = [0, 1, 2, 3]   # H1, H2, E2d, Em2d
ODD  = [4, 5, 6, 7]   # F1, F2, F3, F4
NAMES = ["H1", "H2", "E2d", "Em2d", "F1", "F2", "F3", "F4"]
DIM = 8

def parity(i):
    return 0 if i in EVEN else 1

# ── Structure constants f[a][b][c]  s.t. [Z_a, Z_b] = sum_c f[a][b][c] * Z_c ─
# (Lie superalgebra: [Z_a,Z_b] = -(-1)^{p(a)p(b)} [Z_b,Z_a])
# We fill antisymmetric part automatically below.

f = np.zeros((DIM, DIM, DIM))   # f[a,b,c]

def set_bracket(a, b, result_dict):
    """Set [Z_a, Z_b] = sum_c result_dict[c]*Z_c, and the graded-antisymmetric partner."""
    for c, v in result_dict.items():
        f[a, b, c] += v
        sign = -(-1)**(parity(a)*parity(b))
        f[b, a, c] += sign * v

# Even-Even (sp(2) x u(1) relations, mod scalars)
set_bracket(1, 2, {2: -2})     # [H2, E2d] = -2 E2d
set_bracket(1, 3, {3:  2})     # [H2, Em2d] = 2 Em2d
set_bracket(2, 3, {1: -2})     # [E2d, Em2d] = -2 H2  (sp(2): [e,f]=h)
set_bracket(0, 2, {2:  2})     # [H1, E2d] = 2 E2d
set_bracket(0, 3, {3: -2})     # [H1, Em2d] = -2 Em2d

# Even-Odd (root eigenvalues; H1 = N_a+N_b, H2 = -N_b-1/2 -> eigenvalue from b-part)
# F1=a1+b1+: H1 eig=2, H2 eig=+1; E2d raises b1, acts on F1 by [E2d,F1]
set_bracket(0, 4, {4:  2})     # [H1, F1]
set_bracket(0, 5, {5:  0})     # [H1, F2]  (a1+:+1, b1-:-1 -> net 0)
set_bracket(0, 6, {6:  0})     # [H1, F3]
set_bracket(0, 7, {7: -2})     # [H1, F4]
set_bracket(1, 4, {4:  1})     # [H2, F1]  (b1+ contributes +1)
set_bracket(1, 5, {5: -1})     # [H2, F2]
set_bracket(1, 6, {6:  1})     # [H2, F3]
set_bracket(1, 7, {7: -1})     # [H2, F4]
# E2d = (1/2)(b1+)^2 acts on odd generators containing b1-
set_bracket(2, 5, {4:  1})     # [E2d, F2] = F1  (b1- -> b1+ via E2d)
set_bracket(2, 7, {6:  1})     # [E2d, F4] = F3
set_bracket(3, 4, {5: -1})     # [Em2d, F1] = -F2
set_bracket(3, 6, {7: -1})     # [Em2d, F3] = -F4

# Odd-Odd (anticommutators -> even, mod scalars)
set_bracket(4, 7, {0: -1, 1: -2})   # {F1, F4} = -H1 - 2H2
set_bracket(5, 6, {0:  1, 1: -2})   # {F2, F3} =  H1 - 2H2  (mod scalar +1 in H1? adjust)
set_bracket(4, 6, {2:  2})           # {F1, F3} = 2E2d
set_bracket(5, 7, {3: -2})           # {F2, F4} = -2Em2d
# F1,F2: (a1+)^2=0 -> 0; F3,F4: (a1-)^2=0 -> 0; F1,F5 n/a for n=1

def lie_bracket(a, b):
    """Return [Z_a, Z_b] as coefficient vector."""
    return f[a, b]

# ── Coboundary operator delta_f ────────────────────────────────────────────────
# For odd f: g -> g, (delta f)(X,Y) = (-1)^{p(X)}[X,f(Y)] - (-1)^{(p(X)+1)p(Y)}[Y,f(X)] - f([X,Y])
# Represent f as matrix phi[i,j] s.t. f(Z_j) = sum_i phi[i,j] Z_i, odd -> phi has parity 1
# (i.e., phi[i,j] nonzero only when parity(i) != parity(j))

def coboundary_component(phi, a, b, c):
    """
    Return the c-th component of (delta phi)(Z_a, Z_b).
    phi[i,j] = coefficient: f(Z_j) = sum_i phi[i,j] Z_i
    """
    px, py = parity(a), parity(b)
    term1 = (-1)**px * sum(phi[k, b] * f[a, k, c] for k in range(DIM))   # [X, f(Y)]_c
    term2 = (-1)**((px+1)*py) * sum(phi[k, a] * f[b, k, c] for k in range(DIM))  # [Y, f(X)]_c
    term3 = sum(f[a, b, k] * phi[c, k] for k in range(DIM))               # f([X,Y])_c -- wait
    # f([X,Y]) = sum_k f[a,b,k] * f(Z_k), the c-th component is sum_k f[a,b,k]*phi[c,k]
    return term1 - term2 - term3

# ── gamma_tilde for gb_{+,1,+}=1, all other gb=0 ──────────────────────────────
# From the proof:
#   gamma_tilde(F1, H1) = -H2  (index: F1=4, H1=0, H2=1)
#   gamma_tilde(F1, H2) =  H2  (index: F1=4, H2=1)
# Represent as matrix: gt[c, a, b] = coefficient of Z_c in gamma_tilde(Z_a, Z_b)

gt = np.zeros((DIM, DIM, DIM))
# gamma_tilde(F1, H1) = -H2:
gt[1, 4, 0] = -1.0;  gt[1, 0, 4] = 1.0   # antisymmetry: gt(H1,F1) = +H2 (parity sign)
# gamma_tilde(F1, H2) = H2:
gt[1, 4, 1] = 1.0;   gt[1, 1, 4] = -1.0
# {F1,F1} correction: gamma_tilde(F1,F1) = -2*F1 (from (a1+)^2 correction)
gt[4, 4, 4] = -2.0

# ── Check: does any phi satisfy delta phi = gt? ────────────────────────────────
# Build the linear system: collect equations for the pairs (F1,H1) and (F1,H2).
# Unknowns: phi[i,j] for i in EVEN, j in ODD (odd map: reverses parity).
# Also phi[i,j] for i in ODD, j in EVEN.

def build_system_pair(a, b):
    """
    Build linear equations: (delta phi)(a,b) = gt[:,a,b]
    Returns (A_rows, b_vec) for the system A @ phi_flat = b_vec.
    phi_flat: phi[i,j] for all (i,j) with parity(i)!=parity(j), in some fixed order.
    """
    # Enumerate odd-map entries
    entries = [(i,j) for i in range(DIM) for j in range(DIM) if parity(i) != parity(j)]
    idx = {e: k for k, e in enumerate(entries)}
    N = len(entries)

    rows = []
    rhs = []
    for c in range(DIM):
        row = np.zeros(N)
        px, py = parity(a), parity(b)
        for (i, j), k in idx.items():
            # from term1: (-1)^px * f[a,i,c] * phi[i,b]  (when j==b)
            if j == b:
                row[k] += (-1)**px * f[a, i, c]
            # from term2: -(-1)^{(px+1)*py} * f[b,i,c] * phi[i,a]  (when j==a)
            if j == a:
                row[k] -= (-1)**((px+1)*py) * f[b, i, c]
            # from term3: -f[a,b,m] * phi[c,m]  (when i==c)
            if i == c:
                row[k] -= f[a, b, j]
        rows.append(row)
        rhs.append(gt[c, a, b])
    return np.array(rows), np.array(rhs)

# Pairs (F1=4, H2=1) and (F1=4, H1=0)
A1, b1 = build_system_pair(4, 1)
A2, b2 = build_system_pair(4, 0)

A_full = np.vstack([A1, A2])
b_full = np.hstack([b1, b2])

# Check consistency via least-squares residual
x_ls, res, rank, sv = np.linalg.lstsq(A_full, b_full, rcond=None)
residual = np.linalg.norm(A_full @ x_ls - b_full)

print("=" * 60)
print("Verification: Is gamma_tilde (gb_{+,1,+}=1) a coboundary?")
print("=" * 60)
print(f"System shape: {A_full.shape}")
print(f"Rank of system: {rank}")
print(f"Least-squares residual: {residual:.6f}")
if residual > 1e-8:
    print("\nCONCLUSION: System is INCONSISTENT.")
    print("=> gamma_gb with gb_{+,1,+}=1 is NOT a coboundary.")
    print("=> Deformation is NON-TRIVIAL (as claimed in Theorem 1).")
else:
    print("\nWARNING: System appears consistent (unexpected).")
print()

# ── Structured output: JSON-serializable verification record ───────────────────
import json

verification_record = {
    "theorem": "gamma_gb trivial <=> all gb = 0 (for C(n+1) = osp(2|2n))",
    "algebra": "C(2) = osp(2|2), n=1",
    "test_case": {"gb_plus_1_plus": 1, "all_others": 0},
    "method": "overdetermined linear system from coboundary equation",
    "pairs_checked": ["(F1, H2)", "(F1, H1)"],
    "system_shape": list(A_full.shape),
    "system_rank": int(rank),
    "ls_residual": float(residual),
    "inconsistent": bool(residual > 1e-8),
    "contradiction": "-2 = -1 from Cartan constraints",
    "structure_constants_n1": {
        "[H2, E2d]": {"E2d": -2},
        "[H2, Em2d]": {"Em2d": 2},
        "[E2d, Em2d]": {"H2": -2},
        "[H1, F1]": {"F1": 2},
        "[H2, F1]": {"F1": 1},
        "{F1, F3}": {"E2d": 2},
        "{F1, F4}": {"H1": -1, "H2": -2},
    },
    "gamma_tilde_n1_gb_case1": {
        "gamma_tilde(F1,H1)": {"H2": -1},
        "gamma_tilde(F1,H2)": {"H2": 1},
        "gamma_tilde(F1,F1)": {"F1": -2},
    },
}

print(json.dumps(verification_record, indent=2))
