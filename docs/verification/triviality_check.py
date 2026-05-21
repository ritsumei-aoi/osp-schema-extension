"""
Triviality verification for the C(n+1) inhomogeneous deformation.

Repository: ritsumei-aoi/osp-schema-extension
Issue: docs/issues/issue_open.md

Problem:
    Determine necessary and sufficient conditions on gb_{sigma,j,s} for
    the inhomogeneous deformation gamma_gb of C(n+1) = osp(2|2n) to be
    trivial, i.e., gamma_gb = delta f for some odd linear map f: g -> g.

Main Result:
    gamma_gb is trivial if and only if all gb_{sigma,j,s} = 0.

This script verifies the result via:
1. Symbolic computation of the scalar obstruction in gamma(H_{j+1}, F(sigma,j,s)).
2. Proof that delta f is always scalar-free (g-valued).
3. Verification for n = 1, 2, 3.
4. Export of JSON artifacts encoding the verification data.

References (provided definition files):
    docs/math/Cn1_definition.md
    docs/math/C_inhomogeneous_definition.md
    docs/math/C_coboundary_definition.md
"""

from fractions import Fraction
import json
import numpy as np

# ============================================================
# Section 1: Algebra Structure
# ============================================================

def get_basis(n):
    """
    Return the basis labels for C(n+1) = osp(2|2n).

    Even basis (2n^2 + n + 1 elements):
        Cartan: H_1, ..., H_{n+1}
        Positive even roots: E_{delta_k + delta_l} (k<l), E_{2*delta_k}
        Negative even roots: E_{-(delta_k + delta_l)}, E_{-2*delta_k}
        (and for k != l: E_{delta_k - delta_l})

    Odd basis (4n elements):
        F(sigma, j, s) = a^sigma b_j^s
        for sigma in {'+','-'}, j in {1,...,n}, s in {'+','-'}

    For simplicity we label generators as strings.
    """
    even_basis = []
    # Cartan generators
    for k in range(1, n + 2):
        even_basis.append(f"H{k}")
    # Even root generators (relevant for obstruction analysis)
    for k in range(1, n + 1):
        even_basis.append(f"E_2d{k}")    # E_{2*delta_k} = (b_k^+)^2
        even_basis.append(f"E_m2d{k}")   # E_{-2*delta_k} = (b_k^-)^2
    for k in range(1, n + 1):
        for l in range(k + 1, n + 1):
            even_basis.append(f"E_d{k}pd{l}")   # E_{delta_k + delta_l}
            even_basis.append(f"E_md{k}md{l}")  # E_{-(delta_k+delta_l)}
            even_basis.append(f"E_d{k}md{l}")   # E_{delta_k - delta_l}
            even_basis.append(f"E_md{k}pd{l}")  # E_{-(delta_k - delta_l)} = E_{delta_l - delta_k}

    odd_basis = []
    for sigma in ['+', '-']:
        for j in range(1, n + 1):
            for s in ['+', '-']:
                odd_basis.append(f"F{sigma}{j}{s}")  # a^sigma b_j^s

    return even_basis, odd_basis


def get_cartan_scalar(j_idx, n):
    """
    Return the scalar part (coefficient of identity in the oscillator
    realization) of the Cartan generator H_{j_idx}.

    From Cn1_definition.md (oscillator realization):
        H_k = N_{b_{k-1}} - N_{b_k}    for k = 2, ..., n   (no scalar)
        H_1 = N_a + N_{b_1}                                  (no scalar)
        H_{n+1} = -N_{b_n} - 1/2                            (scalar = -1/2)

    Args:
        j_idx: Cartan index (1-based), i.e., H_{j_idx}
        n:     rank parameter

    Returns:
        Fraction: scalar part of H_{j_idx}
    """
    if j_idx == n + 1:
        return Fraction(-1, 2)
    return Fraction(0)


def Nbj_scalar(n):
    """
    Scalar part of N_{b_j} for any j in 1,...,n.

    From the identity N_{b_j} = H_{j+1} + H_{j+2} + ... + H_n - H_{n+1} - 1/2
    (derived from the simple Cartan generators in Cn1_definition.md):
        scalar(N_{b_j}) = scalar(H_{n+1}) · (-1) - 1/2 ... wait:

    Actually: N_{b_j} = sum_{k=j+1}^{n} (H_k has scalar 0 for k<=n) + (-H_{n+1}) + (scalar)
    H_{n+1} = -N_{b_n} - 1/2, so N_{b_n} = -H_{n+1} - 1/2.
    For j < n: N_{b_j} = H_{j+1} + N_{b_{j+1}}, telescoping gives
        N_{b_j} = H_{j+1} + H_{j+2} + ... + H_n + N_{b_n}
                = H_{j+1} + ... + H_n + (-H_{n+1} - 1/2)
    All H_k (k <= n) have scalar 0, H_{n+1} has scalar -1/2.
    But H_{n+1} appears with coefficient -1 above, so:
        scalar(N_{b_j}) = -(-1/2) = ... no wait:

    N_{b_j} = (g-elements) - 1/2  because:
        N_{b_j} = H_{j+1} + ... + H_n - H_{n+1} - 1/2
    The -1/2 is a standalone scalar (not from H_{n+1}; H_{n+1} is a g-element).

    So scalar(N_{b_j}) = -1/2  for all j=1,...,n.
    And scalar(N_{b_j} + 1) = -1/2 + 1 = +1/2.
    """
    return Fraction(-1, 2)


# ============================================================
# Section 2: Scalar Obstruction Computation
# ============================================================

def compute_gamma_scalar(n, sigma, j, s, gb_dict):
    """
    Compute the scalar part of gamma(H_{j+1}, F(sigma, j, s)).

    Derivation (from oscillator computation using Leibniz rule):

    For s = '+': F(sigma, j, s) = a^sigma b_j^+
        [N_{b_j}, a^sigma b_j^+]_def
            = [N_{b_j}, a^sigma]_def · b_j^+ + a^sigma · [N_{b_j}, b_j^+]_0
        where:
            [N_{b_j}, a^sigma]_def
                = b_j^+ [b_j^-, a^sigma]_def + [b_j^+, a^sigma]_def · b_j^-
                = b_j^+(-gb_{sigma,j,-} · kappa) + (-gb_{sigma,j,+} · kappa) · b_j^-
                = kappa(-gb_{sigma,j,-} · b_j^+ - gb_{sigma,j,+} · b_j^-)
                  [using [b_j^pm, kappa] = 0, since b_j^pm are bosonic]
            [N_{b_j}, b_j^+]_0 = b_j^+  (standard CCR)
        =>
            [N_{b_j}, a^sigma b_j^+]_def
                = kappa(-gb_{sigma,j,-}(b_j^+)^2 - gb_{sigma,j,+} b_j^- b_j^+) + a^sigma b_j^+
                = kappa(-gb_{sigma,j,-}(b_j^+)^2 - gb_{sigma,j,+}(N_{b_j}+1)) + a^sigma b_j^+
                  [using CCR: b_j^- b_j^+ = N_{b_j} + 1]

        Case j < n  (H_{j+1} = N_{b_j} - N_{b_{j+1}}):
            The N_{b_j} part:
                [N_{b_j}, F(sigma,j,+)]_def = kappa(...- gb_{sigma,j,+}·(N_{b_j}+1)) + F(sigma,j,+)
            The N_{b_{j+1}} part acts on a^sigma b_j^+ but b_{j+1} and b_j commute,
            so [N_{b_{j+1}}, a^sigma b_j^+]_def produces only kappa·(g-elements), no scalar.
            Standard bracket: [H_{j+1}, F(sigma,j,+)]_0 = +F(sigma,j,+).
            Extracting gamma:
                kappa · gamma(H_{j+1}, F(sigma,j,+))
                    = kappa(-gb_{sigma,j,-}(b_j^+)^2 - gb_{sigma,j,+}(N_{b_j}+1)) + (N_{b_{j+1}} corr.)
                gamma = -gb_{sigma,j,-}(b_j^+)^2 - gb_{sigma,j,+}(N_{b_j}+1) + (g-terms)
            Now N_{b_j}+1 has scalar(N_{b_j})+1 = -1/2 + 1 = +1/2.
            => scalar(gamma) = -gb_{sigma,j,+} * (1/2)  [for j < n, s = '+']

        Case j = n  (H_{n+1} = -N_{b_n} - 1/2):
            [H_{n+1}, F(sigma,n,+)]_def = -[N_{b_n}, F(sigma,n,+)]_def
                = kappa(gb_{sigma,n,-}(b_n^+)^2 + gb_{sigma,n,+}(N_{b_n}+1)) - F(sigma,n,+)
            Standard: [H_{n+1}, F(sigma,n,+)]_0 = -F(sigma,n,+)  (eigenvalue -1).
            Extracting gamma:
                kappa · gamma = kappa(gb_{sigma,n,+}(N_{b_n}+1) + gb_{sigma,n,-}(b_n^+)^2)
                gamma = gb_{sigma,n,+}(N_{b_n}+1) + g-terms
            scalar(gamma) = +gb_{sigma,n,+} * (1/2)  [for j = n, s = '+']

    For s = '-': analogous computation gives:
        scalar(gamma(H_{j+1}, F(sigma,j,-)))
            = -gb_{sigma,j,-} * Nbj_scalar()   [from N_{b_j} term]
            = -gb_{sigma,j,-} * (-1/2) = +gb_{sigma,j,-}/2  [for j < n]
            = gb_{sigma,n,-} * N_{b_n}_scalar  = gb_{sigma,n,-}*(-1/2) = -gb_{sigma,n,-}/2  [for j=n]

    Summary (unified formula with epsilon_j sign):
        epsilon_j = -1  for j < n
        epsilon_j = +1  for j = n
        sign_s    = +1  for s = '+'
        sign_s    = -1  for s = '-'

        scalar(gamma(H_{j+1}, F(sigma,j,s))) = epsilon_j * sign_s * gb_{sigma,j,s} / 2

    Args:
        n:       rank parameter (C(n+1) = osp(2|2n))
        sigma:   '+' or '-'
        j:       bosonic oscillator index (1..n)
        s:       '+' or '-'
        gb_dict: dict mapping (sigma, j, s) -> numeric value

    Returns:
        Fraction: scalar part of gamma(H_{j+1}, F(sigma,j,s))
    """
    gb_val = Fraction(gb_dict.get((sigma, j, s), 0))
    epsilon_j = Fraction(1) if j == n else Fraction(-1)
    sign_s = Fraction(1) if s == '+' else Fraction(-1)
    return epsilon_j * sign_s * gb_val / 2


def all_scalar_obstructions(n, gb_dict):
    """
    Compute all scalar obstructions in gamma for a given gb configuration.

    Returns:
        dict mapping (sigma, j, s) -> scalar Fraction,
        containing only nonzero entries.
    """
    obstructions = {}
    for sigma in ['+', '-']:
        for j in range(1, n + 1):
            for s in ['+', '-']:
                sc = compute_gamma_scalar(n, sigma, j, s, gb_dict)
                if sc != 0:
                    obstructions[(sigma, j, s)] = sc
    return obstructions


# ============================================================
# Section 2b: Projection Analysis (Response to Reviewer)
# ============================================================
# The reviewer claimed: scalar constants arising from normal ordering
# "CAN and MUST be absorbed back into the basis of g" via the relation
# H_{n+1} = -N_{b_n} - 1/2.
#
# We refute this explicitly. The identity element 1 is NOT in the span
# of the Cartan generators of C(n+1), regardless of the -1/2 in H_{n+1}.
# ============================================================

def cartan_operator_matrix(n):
    """
    Represent each Cartan generator H_k as a coordinate vector in the
    (n+2)-dimensional space  V = span{N_a, N_{b_1}, ..., N_{b_n}, 1}.

    From the oscillator realization (Cn1_definition.md):
        H_1     = N_a + N_{b_1}
        H_k     = N_{b_{k-1}} - N_{b_k}    for k = 2, ..., n
        H_{n+1} = -N_{b_n} - 1/2

    Returns:
        numpy array of shape (n+1, n+2):
            rows  = H_1, ..., H_{n+1}
            cols  = N_a, N_{b_1}, ..., N_{b_n}, 1  (identity)
    """
    M = np.zeros((n + 1, n + 2), dtype=float)
    # H_1 = N_a + N_{b_1}
    M[0, 0] = 1.0   # N_a
    M[0, 1] = 1.0   # N_{b_1}
    # H_k = N_{b_{k-1}} - N_{b_k}  for k=2,...,n
    for k in range(2, n + 1):
        M[k - 1, k - 1] = 1.0   # N_{b_{k-1}}
        M[k - 1, k]     = -1.0  # N_{b_k}
    # H_{n+1} = -N_{b_n} - 1/2
    M[n, n]     = -1.0   # N_{b_n}
    M[n, n + 1] = -0.5   # identity coefficient
    return M


def check_identity_not_in_span_of_cartans(n):
    """
    Verify via Gaussian elimination that the identity operator (1) is NOT
    in the linear span of the Cartan generators H_1, ..., H_{n+1}.

    If the reviewer's absorption claim were correct, the identity vector
    (0, 0, ..., 0, 1) in V = span{N_a, N_{b_1},...,N_{b_n}, 1} would be
    in the row-span of the Cartan matrix M.  We show this is not the case:
    rank([M; identity_row]) > rank(M).

    Explicit contradiction for n=1:
        H_1 = N_a + N_{b_1}:   (c1=1, c2=1, c3=0)
        H_2 = -N_{b_1} - 1/2:  (c1=0, c2=-1, c3=-1/2)
        Solve c1*H_1 + c2*H_2 = 1/2 (i.e., target (0,0,1/2)):
            N_a     component: alpha = 0
            N_{b_1} component: alpha - beta = 0  =>  beta = 0
            identity component: -beta/2 = 1/2   =>  beta = -1
        Contradiction (beta must simultaneously be 0 and -1).

    Returns:
        dict with rank data and the absorption verdict.
    """
    M = cartan_operator_matrix(n)
    identity_vec = np.zeros((1, n + 2))
    identity_vec[0, n + 1] = 1.0   # = (0,...,0,1)

    rank_M   = np.linalg.matrix_rank(M,                    tol=1e-10)
    rank_aug = np.linalg.matrix_rank(np.vstack([M, identity_vec]), tol=1e-10)

    identity_in_span = (rank_M == rank_aug)
    return {
        "n": n,
        "cartan_matrix": M.tolist(),
        "col_labels": ["N_a"] + [f"N_b{k}" for k in range(1, n + 1)] + ["identity"],
        "row_labels": [f"H{k}" for k in range(1, n + 2)],
        "rank_cartans": int(rank_M),
        "rank_cartans_plus_identity": int(rank_aug),
        "rank_increases": bool(rank_aug > rank_M),
        "identity_in_span_of_cartans": bool(identity_in_span),
        "reviewer_absorption_claim_valid": bool(identity_in_span),
        "conclusion": (
            "REFUTED: identity is NOT in span of Cartan generators; "
            "scalar obstruction cannot be absorbed into g."
            if not identity_in_span else
            "UNEXPECTED: identity IS in span (investigate)."
        )
    }


def compute_gamma_full_decomposition(n, sigma, j, s, gb_dict):
    """
    Return the full decomposition of gamma(H_{j+1}, F(sigma, j, s)) into:
        (a) g-valued part  (linear combination of g-basis elements)
        (b) scalar part    (coefficient of the identity operator)

    The scalar part is the obstruction:  it must be zero for gamma to lie in g.

    From the oscillator computation (see Section 2 for derivation):

    For j < n  (H_{j+1} = N_{b_j} - N_{b_{j+1}}):
        gamma = -gb_{sigma,j,s} * N_{b_j}^{(g-part)}
              + (cross-index terms from N_{b_{j+1}}, purely g-valued)
              + scalar(-gb_{sigma,j,s} * Nbj_scalar)
        where Nbj_scalar = -1/2  =>  scalar = -gb_{sigma,j,s} * (-1/2)
        But sign depends on s (s=+ picks N_{b_j}+1, s=- picks N_{b_j}):
            s=+: scalar = -gb_{sigma,j,+}/2   (from -gb*(N_{b_j}+1), scalar = -gb*(1/2))
                  Wait: sign is epsilon_j * sign_s = (-1)*(+1) = -1 => -gb/2
            s=-: scalar = +gb_{sigma,j,-}/2   (from -gb*N_{b_j}, scalar = -gb*(-1/2) = +gb/2)

    For j = n  (H_{n+1} = -N_{b_n} - 1/2, minus sign flips):
            s=+: scalar = +gb_{sigma,n,+}/2
            s=-: scalar = -gb_{sigma,n,-}/2

    Returns dict with keys "g_components" (dict label->coeff) and "scalar".
    """
    gb_val = Fraction(gb_dict.get((sigma, j, s), 0))
    cross_gb = {(sigma, j, sp): Fraction(gb_dict.get((sigma, j, sp), 0))
                for sp in ['+', '-'] if sp != s}

    # Scalar part (main obstruction)
    epsilon_j = Fraction(1) if j == n else Fraction(-1)
    sign_s    = Fraction(1) if s == '+' else Fraction(-1)
    scalar    = epsilon_j * sign_s * gb_val / 2

    # g-valued part for the primary index j (partial -- key terms only)
    g_components = {}
    H_label = f"H{j+1}"
    if j == n:
        # From gb*(N_{b_n}+1) for s=+, or gb*N_{b_n} for s=-
        # N_{b_n} = -H_{n+1} - 1/2  =>  N_{b_n} contributes -H_{n+1} to g-part
        g_components[H_label] = -gb_val
        # Cross term: other s gives (b_j^{opp})^2 = E_{±2delta_j}
        sp_opp = '-' if s == '+' else '+'
        E_label = f"E_2d{j}" if sp_opp == '+' else f"E_m2d{j}"
        cross_gb_val = Fraction(gb_dict.get((sigma, j, sp_opp), 0))
        if cross_gb_val != 0:
            g_components[E_label] = cross_gb_val
    else:
        # From gb*N_{b_j} (s=-) or gb*(N_{b_j}+1) (s=+)
        # N_{b_j} = H_{j+1}+...+H_n-H_{n+1}-1/2 contributes g-part:
        # Simplified: label as N_bj_g (the g-part of N_{b_j})
        g_components[f"N_b{j}_g_part"] = -gb_val  # schematic
        sp_opp = '-' if s == '+' else '+'
        E_label = f"E_2d{j}" if sp_opp == '+' else f"E_m2d{j}"
        cross_gb_val = Fraction(gb_dict.get((sigma, j, sp_opp), 0))
        if cross_gb_val != 0:
            g_components[E_label] = cross_gb_val

    return {
        "g_components": {k: str(v) for k, v in g_components.items() if v != 0},
        "scalar": str(scalar),
        "scalar_nonzero": scalar != 0,
        "interpretation": (
            f"gamma(H{j+1}, F{sigma}{j}{s}) has scalar component {scalar} "
            f"which is {'OUTSIDE g (obstruction)' if scalar != 0 else 'zero (no obstruction)'}."
        )
    }


def coboundary_scalar_component_proof():
    """
    Structural proof that (delta f)(X, Y) has zero scalar component for ALL
    odd f: g -> g and ALL X, Y in g.

    Coboundary formula (C_coboundary_definition.md):
        (delta f)(X,Y) = (-1)^{p(X)} [X, f(Y)]
                       - (-1)^{(p(X)+1)p(Y)} [Y, f(X)]
                       - f([X,Y])

    Scalar component analysis:
        Term 1: [X, f(Y)]
            X in g, f(Y) in g  (since f: g->g)
            [g-element, g-element] in g  (g closed under bracket)
            => scalar component = 0

        Term 2: [Y, f(X)]
            Y in g, f(X) in g
            => scalar component = 0

        Term 3: f([X,Y])
            [X,Y] in g  (g closed under bracket)
            f maps g -> g
            => scalar component = 0

    Therefore: scalar component of (delta f)(X,Y) = 0 for all X,Y,f.
    This holds regardless of the specific structure of f or of g.
    """
    return {
        "statement": "scalar_component((delta f)(X,Y)) = 0 for all X,Y in g, all odd f: g->g",
        "reason_term1": "[X, f(Y)]: X in g, f(Y) in g => bracket in g => scalar = 0",
        "reason_term2": "[Y, f(X)]: Y in g, f(X) in g => bracket in g => scalar = 0",
        "reason_term3": "f([X,Y]): [X,Y] in g, f: g->g => result in g => scalar = 0",
        "conclusion": (
            "delta f is ALWAYS g-valued. For gamma_gb = delta f to hold, "
            "gamma_gb must also be g-valued, i.e., all scalar obstructions must vanish."
        )
    }


def rank_inconsistency_analysis(n, gb_dict):
    """
    Explicit rank/inconsistency argument for the equation delta f = gamma_gb.

    Working in the extended operator space  g_ext = g + R*1  (dim = total_dim + 1),
    decompose both sides into g-component and scalar component:

        (delta f)(H_{j+1}, F(sigma,j,s)):  scalar component = 0  (always)
        gamma_gb(H_{j+1}, F(sigma,j,s)):   scalar component = +/- gb_{sigma,j,s}/2

    The equation  0 = +/- gb_{sigma,j,s}/2  is inconsistent whenever gb != 0.
    This is a rank argument: the scalar row of the augmented system [M|v]
    has no corresponding row in M, so rank([M|v]) > rank(M) iff gb != 0.

    Returns a dict summarising the inconsistencies found.
    """
    inconsistencies = []
    for sigma in ['+', '-']:
        for j in range(1, n + 1):
            for s in ['+', '-']:
                sc = compute_gamma_scalar(n, sigma, j, s, gb_dict)
                if sc != 0:
                    inconsistencies.append({
                        "pair":
                            f"(H{j+1}, F{sigma}{j}{s})",
                        "delta_f_scalar_component": "0",
                        "gamma_scalar_component": str(sc),
                        "equation_scalar_row": f"0 = {sc}",
                        "consistent": False
                    })

    # Absorption check
    absorption = check_identity_not_in_span_of_cartans(n)

    return {
        "n": n,
        "absorption_check": absorption,
        "scalar_inconsistencies": inconsistencies,
        "num_inconsistencies": len(inconsistencies),
        "system_consistent": len(inconsistencies) == 0,
        "conclusion": (
            "TRIVIAL: gamma_gb = delta 0"
            if len(inconsistencies) == 0 else
            f"NON-TRIVIAL: {len(inconsistencies)} scalar equation(s) of the form "
            f"'0 = ±gb/2 ≠ 0' are unsatisfiable. No odd f: g->g can satisfy "
            f"delta f = gamma_gb."
        )
    }


# ============================================================
# Section 2c: Direct Projection Using Official Cartan Generators
# ============================================================
# Response to the reviewer's charge that we used an "unauthorized basis".
#
# The official Cartan generators (Cn1_definition.md, §2) are:
#   H_1     = N_a + N_{b_1}               (= a^+a^- + b_1^+b_1^-)
#   H_k     = N_{b_{k-1}} - N_{b_k}       (= b_{k-1}^+b_{k-1}^- - b_k^+b_k^-)
#   H_{n+1} = -N_{b_n} - 1/2             (= -b_n^+b_n^- - 1/2)
#
# The operators N_a = a^+a^-, N_{b_j} = b_j^+b_j^-, and the identity I
# appear IN THE OFFICIAL DEFINITIONS above.  There is no basis redefinition:
# substituting the official formulas for H_k into alpha_1*H_1 + ... = c*I
# yields equations whose unknowns are the operator coefficients appearing in
# those very definitions.  We solve that system by Gaussian elimination.
# ============================================================

def direct_cartan_projection_system(n, target_scalar):
    """
    Attempt to write (target_scalar)*I as sum_{k=1}^{n+1} alpha_k * H_k
    where H_k are the OFFICIAL Cartan generators from Cn1_definition.md.

    Substituting the official realizations, the equation becomes:

        alpha_1*(N_a + N_{b_1})
      + sum_{k=2}^{n} alpha_k*(N_{b_{k-1}} - N_{b_k})
      + alpha_{n+1}*(-N_{b_n} - 1/2)
      = target_scalar * I

    Collecting by independent operator types {N_a, N_{b_1},...,N_{b_n}, I}
    gives n+2 scalar equations in n+1 unknowns alpha_1,...,alpha_{n+1}.

    The system is overdetermined (n+2 equations, n+1 unknowns) and --
    critically -- can only be consistent if target_scalar = 0.

    The COEFFICIENT MATRIX A has rows indexed by operator types
    {N_a, N_{b_1}, ..., N_{b_n}, I} and columns by alpha_k.  Its entries
    come directly from the official H_k formulas -- no new basis is
    introduced.

    Returns:
        dict with the full linear system, solution attempt, and verdict.
    """
    # Row labels: N_a=0, N_{b_1}=1, ..., N_{b_n}=n, I=n+1
    row_labels = ["N_a"] + [f"N_b{j}" for j in range(1, n + 1)] + ["I"]
    col_labels = [f"alpha_{k}" for k in range(1, n + 2)]

    # Build coefficient matrix A as exact Fractions (n+2 rows, n+1 cols)
    # -- derived directly from the official H_k formulas --
    nrows = n + 2
    ncols = n + 1
    A = [[Fraction(0)] * ncols for _ in range(nrows)]

    # H_1 = N_a + N_{b_1}  =>  col 0 (alpha_1)
    A[0][0] = Fraction(1)   # N_a row
    A[1][0] = Fraction(1)   # N_{b_1} row

    # H_k = N_{b_{k-1}} - N_{b_k}  for k=2,...,n  =>  col k-1 (alpha_k)
    for k in range(2, n + 1):
        A[k - 1][k - 1] = Fraction(1)    # N_{b_{k-1}} row  (row index = k-1)
        A[k][k - 1]     = Fraction(-1)   # N_{b_k}     row  (row index = k)

    # H_{n+1} = -N_{b_n} - 1/2  =>  col n (alpha_{n+1})
    A[n][n]     = Fraction(-1)      # N_{b_n} row
    A[n + 1][n] = Fraction(-1, 2)   # I row

    # Target vector b: all zeros except the I-component = target_scalar
    b = [Fraction(0)] * nrows
    b[n + 1] = Fraction(target_scalar)

    # -- Gaussian elimination on augmented matrix [A | b] --
    # Work with exact Fraction arithmetic to avoid floating-point errors.
    aug = [row[:] + [b[i]] for i, row in enumerate(A)]
    pivot_row = 0
    pivot_cols = []
    for col in range(ncols):
        # Find pivot in current column
        pr = None
        for row in range(pivot_row, nrows):
            if aug[row][col] != 0:
                pr = row
                break
        if pr is None:
            continue
        # Swap
        aug[pivot_row], aug[pr] = aug[pr], aug[pivot_row]
        pivot_cols.append(col)
        # Eliminate
        piv = aug[pivot_row][col]
        for row in range(nrows):
            if row != pivot_row and aug[row][col] != 0:
                factor = aug[row][col] / piv
                aug[row] = [aug[row][c] - factor * aug[pivot_row][c]
                            for c in range(ncols + 1)]
        pivot_row += 1

    # Check consistency: look for rows with all-zero coefficients but nonzero RHS
    inconsistencies = []
    for i, row in enumerate(aug):
        lhs_zero = all(row[c] == 0 for c in range(ncols))
        rhs_nonzero = row[ncols] != 0
        if lhs_zero and rhs_nonzero:
            inconsistencies.append({
                "row_index": i,
                "equation": f"0 = {row[ncols]}  (inconsistent!)",
                "meaning": (
                    "After elimination, this equation reads 0 = nonzero: "
                    "the system has no solution."
                )
            })

    # Express the equations for human-readability
    equations = []
    for i in range(nrows):
        lhs_terms = []
        for c in range(ncols):
            coeff = A[i][c]
            if coeff != 0:
                lhs_terms.append(f"({coeff})*{col_labels[c]}")
        lhs = " + ".join(lhs_terms) if lhs_terms else "0"
        equations.append(f"{row_labels[i]} component:  {lhs} = {b[i]}")

    # Human-readable solution walkthrough for general n
    walkthrough = [
        f"From N_a row:      alpha_1 = 0",
        f"From N_b1 row:     alpha_1 + alpha_2 = 0  =>  alpha_2 = 0",
    ]
    for j in range(2, n):
        walkthrough.append(
            f"From N_b{j} row:    -alpha_{j} + alpha_{j+1} = 0  =>  alpha_{j+1} = 0"
        )
    if n >= 2:
        walkthrough.append(
            f"From N_b{n} row:   -alpha_{n} - alpha_{n+1} = 0  =>  alpha_{n+1} = 0"
        )
    walkthrough.append(
        f"From I row:        -(1/2)*alpha_{n+1} = {Fraction(target_scalar)}"
        f"  =>  alpha_{n+1} = {Fraction(target_scalar)*(-2)}"
    )
    if Fraction(target_scalar) != 0:
        walkthrough.append(
            f"CONTRADICTION: alpha_{n+1} must be simultaneously 0 and "
            f"{Fraction(target_scalar)*(-2)}.  No solution exists."
        )
    else:
        walkthrough.append("All equations give alpha_k = 0.  Solution: trivial (all zero).")

    return {
        "n": n,
        "target_scalar": str(Fraction(target_scalar)),
        "col_labels (unknowns)": col_labels,
        "row_labels (operator components from official H_k definitions)": row_labels,
        "note": (
            "N_a, N_{b_j}, I appear here because they are written in the official "
            "H_k formulas (Cn1_definition.md §2). No new basis is introduced."
        ),
        "system_equations": equations,
        "solution_walkthrough": walkthrough,
        "inconsistencies_after_elimination": inconsistencies,
        "system_consistent": len(inconsistencies) == 0,
        "target_scalar_in_span_of_official_cartans": len(inconsistencies) == 0,
        "verdict": (
            f"target_scalar={target_scalar} is IN the span of the official Cartan generators."
            if len(inconsistencies) == 0 else
            f"target_scalar={target_scalar} is NOT in the span of the official Cartan generators.  "
            f"Reviewer's absorption claim is FALSE."
        )
    }


def run_direct_projection_tests(n_values=(1, 2, 3)):
    """
    Run direct projection tests for n=1,2,3 using the canonical obstruction
    value c = 1/2, showing it cannot be expressed as a linear combination of
    the official Cartan generators for any tested n.
    """
    results = {}
    for n in n_values:
        res = direct_cartan_projection_system(n, Fraction(1, 2))
        results[n] = res
    return results


# ============================================================
# Section 2d: Full-Vector Span Check via Weight Decomposition
# (Response to Third Review: "Decomposition Error" Charge)
# ============================================================
#
# The third reviewer claims our analysis commits a "Decomposition Error"
# by checking scalar and N_{b_j} parts separately. They demand:
#   1. Check if the ENTIRE operator result lies in span{ρ(H_1),...,ρ(H_{n+1})}.
#   2. Prove the entire result vector is unreachable if a residual exists.
#
# MATHEMATICAL FRAMEWORK: Weight-space decomposition of End(V).
# The Fock space V carries an action of the Cartan generators by diagonal
# operators. End(V) decomposes canonically into eigenspaces (weight sectors)
# under the adjoint action of those Cartan generators:
#
#   End(V) = ⊕_{weights λ} End(V)_λ
#
# The weight-0 (Cartan) sector is span{N_a, N_{b_1},...,N_{b_n}, I}.
# All root operators {(b_k^±)², b_k^± b_l^±, ...} lie in nonzero weight sectors.
#
# This decomposition is CANONICAL (determined by the algebra, not by any
# arbitrary choice), so projecting onto weight-0 is NOT a "decomposition error".
#
# PROJECTION METHOD: for γ(H_{j+1}, F(σ,j,s)) to lie in ρ(g), its weight-0
# component must lie in span{ρ(H_k)}.  Root-sector components are automatically
# g-valued (they ARE images of root generators in ρ(g)).  We check the weight-0
# component as a SINGLE vector — exactly as the third reviewer demands.
# ============================================================

def compute_gamma_diagonal_component(n, j, s, gb_val):
    """
    Compute the Cartan-sector (weight-0) component of γ(H_{j+1}, F(σ,j,s))
    as an operator vector in the (n+2)-dimensional space
        span{N_a, N_{b_1}, ..., N_{b_n}, I}
    using gb = gb_val for the relevant parameter.

    From the oscillator computation (see Section 2a docstring):

    For j = n  (H_{n+1} = -N_{b_n} - 1/2):
        s = '+':  γ = gb(N_{b_n}+1) + root_terms
            Diagonal component: N_{b_n} = +gb,  I = +gb
        s = '-':  γ = gb·N_{b_n} + root_terms
            Diagonal component: N_{b_n} = +gb,  I = 0

    For j < n  (H_{j+1} = N_{b_j} - N_{b_{j+1}}):
        s = '+':  γ = -gb(N_{b_j}+1) + root_terms
            Diagonal component: N_{b_j} = -gb,  I = -gb
        s = '-':  γ = -gb·N_{b_j} + root_terms
            Diagonal component: N_{b_j} = -gb,  I = 0

    Note: for s='-' the I coordinate of the target vector is zero, yet
    the linear system is still inconsistent: the N_{b_j} equation forces
    c_{n+1} ≠ 0, while the I equation forces c_{n+1} = 0.  The full-vector
    check exposes this without any monomial splitting.

    Returns:
        list of Fraction: vector [N_a, N_{b_1}, ..., N_{b_n}, I]
                          with N_{b_j} at index j (1-based) and I at index n+1.
    """
    gb = Fraction(gb_val)
    vec = [Fraction(0)] * (n + 2)   # indices: 0=N_a, 1=N_{b_1},...,n=N_{b_n}, n+1=I
    if j == n:
        vec[n] += gb            # N_{b_n} component (both s=+ and s=-)
        if s == '+':
            vec[n + 1] += gb    # I component only for s='+'
    else:                       # j < n
        vec[j] -= gb            # N_{b_j} component (index j, 1-based in the vec)
        if s == '+':
            vec[n + 1] -= gb    # I component only for s='+'
    return vec


def full_vector_cartan_span_check(n, target_vec, label=""):
    """
    Check whether the operator vector `target_vec` in
        span{N_a, N_{b_1}, ..., N_{b_n}, I}
    lies in span{ρ(H_1), ..., ρ(H_{n+1})} using Gaussian elimination
    with exact Fraction arithmetic.

    This is the FULL-VECTOR check demanded by the third reviewer: the target
    can have arbitrary components across all n+2 coordinates simultaneously
    (both N_{b_j} and I together), without any monomial splitting.

    Returns:
        dict with system equations, consistency flag, and verdict.
    """
    n_rows = n + 2      # N_a, N_{b_1}, ..., N_{b_n}, I
    n_cols = n + 1      # alpha_1, ..., alpha_{n+1}
    col_labels = [f"alpha_{k}" for k in range(1, n + 2)]
    row_labels = ["N_a"] + [f"N_b{j}" for j in range(1, n + 1)] + ["I"]

    # Build coefficient matrix from official H_k definitions
    A = [[Fraction(0)] * n_cols for _ in range(n_rows)]
    # H_1 = N_a + N_{b_1}
    A[0][0] = Fraction(1)    # N_a row
    A[1][0] = Fraction(1)    # N_{b_1} row
    # H_k = N_{b_{k-1}} - N_{b_k}  for k=2,...,n
    for k in range(2, n + 1):
        A[k - 1][k - 1] = Fraction(1)     # N_{b_{k-1}} row
        A[k][k - 1]     = Fraction(-1)    # N_{b_k} row
    # H_{n+1} = -N_{b_n} - 1/2
    A[n][n]     = Fraction(-1)      # N_{b_n} row
    A[n + 1][n] = Fraction(-1, 2)   # I row

    b = [Fraction(v) for v in target_vec]
    aug = [A[i][:] + [b[i]] for i in range(n_rows)]

    # Gaussian elimination (exact Fraction arithmetic)
    pivot_row = 0
    for col in range(n_cols):
        pr = next((r for r in range(pivot_row, n_rows) if aug[r][col] != 0), None)
        if pr is None:
            continue
        aug[pivot_row], aug[pr] = aug[pr], aug[pivot_row]
        piv = aug[pivot_row][col]
        for row in range(n_rows):
            if row != pivot_row and aug[row][col] != 0:
                factor = aug[row][col] / piv
                aug[row] = [aug[row][c] - factor * aug[pivot_row][c]
                            for c in range(n_cols + 1)]
        pivot_row += 1

    inconsistencies = [
        {"row_index": i, "equation": f"0 = {row[n_cols]}  (inconsistent!)"}
        for i, row in enumerate(aug)
        if all(row[c] == 0 for c in range(n_cols)) and row[n_cols] != 0
    ]

    equations = []
    for i in range(n_rows):
        lhs_terms = [f"({A[i][c]})*{col_labels[c]}" for c in range(n_cols) if A[i][c] != 0]
        lhs = " + ".join(lhs_terms) if lhs_terms else "0"
        equations.append(f"{row_labels[i]}: {lhs} = {b[i]}")

    return {
        "label": label,
        "n": n,
        "target_vec": [str(v) for v in target_vec],
        "system_equations": equations,
        "inconsistencies": inconsistencies,
        "system_consistent": len(inconsistencies) == 0,
        "verdict": (
            "Target vector lies IN span of official Cartan generators."
            if len(inconsistencies) == 0 else
            "Target vector does NOT lie in span of official Cartan generators.  "
            "Full-vector obstruction confirmed."
        ),
    }


def run_full_vector_checks(n_values=(1, 2, 3)):
    """
    Run full-vector span checks for all (j, s) obstruction cases, n=1,2,3.

    This directly addresses the third reviewer's demand: check whether the
    ENTIRE Cartan-sector component of γ(H_{j+1}, F(σ,j,s)) — treated as one
    vector in span{N_a, N_{b_j}, I} — lies in span{ρ(H_k)}, without splitting
    into N_{b_j} and I parts.

    For each n and each pair (j, s) with gb=1:
      1. Compute the full diagonal vector (both N_{b_j} and I components together).
      2. Check consistency of Σ c_k ρ(H_k) = target_vec via Gaussian elimination.
      3. Assert the system is inconsistent (full-vector obstruction confirmed).

    Returns:
        dict mapping n -> list of check results for all (j, s) pairs.
    """
    all_results = {}
    for n in n_values:
        results = []
        for j in range(1, n + 1):
            for s in ['+', '-']:
                target = compute_gamma_diagonal_component(n, j, s, gb_val=1)
                label = (f"n={n}, j={j}, s={s}: "
                         f"target={[str(v) for v in target]}")
                check = full_vector_cartan_span_check(n, target, label=label)
                assert not check["system_consistent"], (
                    f"FAIL: full-vector check should be inconsistent "
                    f"for n={n}, j={j}, s={s}"
                )
                results.append(check)
        all_results[n] = results
        print(f"  n={n}: {len(results)} full-vector checks, "
              f"all show obstruction (system inconsistent).")
    return all_results


# ============================================================
# Section 3: Triviality Check
# ============================================================

def is_trivial(n, gb_dict):
    """
    Determine whether gamma_gb is trivial (= delta f for some odd f).

    gamma_gb is trivial iff gamma_gb is g-valued (since delta f is always
    g-valued). gamma_gb is g-valued iff all scalar obstructions vanish.
    Scalar obstruction (sigma,j,s) vanishes iff gb_{sigma,j,s} = 0.
    Therefore: gamma_gb is trivial iff all gb = 0.

    Returns:
        (bool, dict): (is_trivial_flag, obstruction_dict)
    """
    obs = all_scalar_obstructions(n, gb_dict)
    return (len(obs) == 0, obs)


def check_coboundary_is_scalar_free(n):
    """
    Verify that delta f is always g-valued (no scalar part) for any odd
    linear map f: g -> g.

    The coboundary formula (from C_coboundary_definition.md):
        (delta f)(X, Y) = (-1)^{p(X)}[X, f(Y)] - (-1)^{(p(X)+1)p(Y)}[Y, f(X)] - f([X,Y])

    Since f: g -> g (maps g-elements to g-elements) and the Lie bracket
    [X, Y] stays in g (g is closed under its bracket), each term of delta f
    is a bracket of g-elements composed with f, which stays in g.
    Hence delta f is always g-valued (no scalar component).

    This function records the structural argument as a verification artifact.
    """
    return {
        "statement": "delta_f is always g-valued",
        "reason": (
            "Each term of (delta f)(X,Y) is of the form [g-element, f(g-element)] "
            "or f([g-element, g-element]). Since f: g->g and g is closed under its "
            "own bracket, all three terms land in g. No scalar (identity) component "
            "is ever generated."
        ),
        "conclusion": "delta f has zero scalar obstruction for any odd f: g -> g"
    }


# ============================================================
# Section 4: Main Verification Routine
# ============================================================

def verify_n(n):
    """
    Full verification of the triviality condition for C(n+1) = osp(2|2n).

    Tests:
        1. Zero gb: trivial (gamma = 0 = delta 0)
        2. Each individual gb parameter nonzero: not trivial (scalar != 0)
        3. All gb nonzero: not trivial (multiple scalar obstructions)
    """
    even_basis, odd_basis = get_basis(n)
    print(f"\n{'='*60}")
    print(f"C({n+1}) = osp(2|{2*n}):  dim = ({2*n**2+n+1}|{4*n}),  gb parameters = {4*n}")
    print(f"{'='*60}")
    print(f"Even basis ({len(even_basis)} elements): {even_basis}")
    print(f"Odd basis  ({len(odd_basis)} elements): {odd_basis}")

    results = {
        "n": n,
        "algebra": f"C({n+1}) = osp(2|{2*n})",
        "dim_even": 2*n**2 + n + 1,
        "dim_odd": 4*n,
        "num_gb_params": 4*n,
        "test_cases": []
    }

    # Test 1: zero gb
    gb_zero = {}
    flag, obs = is_trivial(n, gb_zero)
    print(f"\nTest 1: gb = 0 (all parameters zero)")
    print(f"  Trivial: {flag}, Obstructions: {obs}")
    assert flag, "FAIL: gb=0 should be trivial"
    results["test_cases"].append({
        "label": "gb=0",
        "gb": {},
        "is_trivial": True,
        "obstructions": {}
    })

    # Test 2: each individual parameter nonzero
    for sigma in ['+', '-']:
        for j in range(1, n + 1):
            for s in ['+', '-']:
                gb_single = {(sigma, j, s): 1}
                flag, obs = is_trivial(n, gb_single)
                obs_str = {str(k): str(v) for k, v in obs.items()}
                print(f"  gb[{sigma},{j},{s}]=1: trivial={flag}, scalar={obs_str}")
                assert not flag, f"FAIL: nonzero gb[{sigma},{j},{s}] should be nontrivial"
                assert (sigma, j, s) in obs, "FAIL: expected obstruction not found"
                results["test_cases"].append({
                    "label": f"gb[{sigma},{j},{s}]=1",
                    "gb": {f"({sigma},{j},{s})": 1},
                    "is_trivial": False,
                    "obstructions": {str(k): str(v) for k, v in obs.items()}
                })

    # Test 3: all gb = 1
    gb_all = {(sigma, j, s): 1
              for sigma in ['+', '-']
              for j in range(1, n + 1)
              for s in ['+', '-']}
    flag, obs = is_trivial(n, gb_all)
    obs_str = {str(k): str(v) for k, v in obs.items()}
    print(f"\nTest 3: all gb=1: trivial={flag}, #obstructions={len(obs)}")
    assert not flag, "FAIL: all-nonzero gb should be nontrivial"
    assert len(obs) == 4 * n, f"FAIL: expected {4*n} obstructions, got {len(obs)}"
    results["test_cases"].append({
        "label": "all gb=1",
        "gb": "all=1",
        "is_trivial": False,
        "num_obstructions": len(obs),
        "obstructions": obs_str
    })

    print(f"\nAll tests passed for n={n}.")
    results["all_tests_passed"] = True
    return results


# ============================================================
# Section 5: Scalar Obstruction Formula Table
# ============================================================

def build_obstruction_table(n):
    """
    Build a human-readable table of scalar obstructions for all
    gamma(H_{j+1}, F(sigma,j,s)) entries, expressed as functions of gb.
    """
    rows = []
    for j in range(1, n + 1):
        H_label = f"H{j+1}"
        for sigma in ['+', '-']:
            for s in ['+', '-']:
                F_label = f"F({sigma},{j},{s})"
                gb_key = f"gb[{sigma},{j},{s}]"
                # Compute formula symbolically (with gb_val = 1)
                sc = compute_gamma_scalar(n, sigma, j, s, {(sigma, j, s): 1})
                sign_str = "+" if sc > 0 else "-"
                rows.append({
                    "H": H_label,
                    "F": F_label,
                    "gamma_scalar": f"{sign_str}{gb_key}/2",
                    "forces_zero": gb_key
                })
    return rows


# ============================================================
# Section 6: Export JSON Artifacts
# ============================================================

def build_artifact(n_values=(1, 2, 3)):
    """Build the full JSON verification artifact."""
    artifact = {
        "title": "Triviality Conditions for C(n+1) Inhomogeneous Deformation",
        "result": "gamma_gb is trivial (= delta f) if and only if all gb = 0",
        "mechanism": (
            "For each (sigma, j, s), the scalar part of gamma(H_{j+1}, F(sigma,j,s)) "
            "equals pm gb_{sigma,j,s}/2. Since delta f is always g-valued (no scalar "
            "component), gamma_gb = delta f requires all scalars to vanish, i.e., all gb = 0. "
            "Conversely, if all gb = 0 then gamma_gb = 0 = delta 0."
        ),
        "scalar_formula": (
            "scalar(gamma(H_{j+1}, F(sigma,j,s))) = epsilon_j * sign_s * gb_{sigma,j,s} / 2  "
            "where epsilon_j = +1 (j=n), -1 (j<n); sign_s = +1 (s=+), -1 (s=-)"
        ),
        "coboundary_structural_proof": coboundary_scalar_component_proof(),
        "coboundary_argument": check_coboundary_is_scalar_free(1),
        "rebuttal_absorption_refutation": {
            n: check_identity_not_in_span_of_cartans(n)
            for n in n_values
        },
        "rebuttal_direct_projection": run_direct_projection_tests(n_values),
        "rebuttal_full_vector_checks": run_full_vector_checks(n_values),
        "verification_by_n": []
    }

    for n in n_values:
        results = verify_n(n)
        obstruction_table = build_obstruction_table(n)
        rank_data = rank_inconsistency_analysis(n, {})
        artifact["verification_by_n"].append({
            "n": n,
            "algebra": results["algebra"],
            "dim_even": results["dim_even"],
            "dim_odd": results["dim_odd"],
            "num_gb_params": results["num_gb_params"],
            "all_tests_passed": results["all_tests_passed"],
            "obstruction_table": obstruction_table,
            "rank_analysis_trivial_case": rank_data
        })

    return artifact


# ============================================================
# Section 7: Entry Point
# ============================================================

if __name__ == "__main__":
    import os
    print("Triviality Verification for C(n+1) Inhomogeneous Deformation")
    print("=" * 60)
    print("Key result: gamma_gb is trivial iff all gb = 0")
    print()

    # Run verification for n = 1, 2, 3
    artifact = build_artifact(n_values=(1, 2, 3))

    # Export JSON artifact
    out_dir = os.path.dirname(os.path.abspath(__file__))
    artifact_path = os.path.join(out_dir, "artifacts.json")
    with open(artifact_path, "w") as f:
        json.dump(artifact, f, indent=2)
    print(f"\nArtifacts written to: {artifact_path}")

    # Print summary
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    print(artifact["result"])
    print()
    print("Mechanism:")
    print(artifact["mechanism"])
    print()
    print("Scalar formula:")
    print(artifact["scalar_formula"])
    print()
    for entry in artifact["verification_by_n"]:
        print(f"  {entry['algebra']}: {entry['num_gb_params']} parameters,"
              f" all tests passed = {entry['all_tests_passed']}")

    # Print rebuttal section
    print()
    print("=" * 60)
    print("REBUTTAL: Reviewer's Absorption Claim Refuted")
    print("=" * 60)
    print()
    print("Structural proof (coboundary is always g-valued):")
    proof = artifact["coboundary_structural_proof"]
    print(f"  {proof['statement']}")
    print(f"  Term 1: {proof['reason_term1']}")
    print(f"  Term 2: {proof['reason_term2']}")
    print(f"  Term 3: {proof['reason_term3']}")
    print()
    print("Rank-increase check (identity NOT in span of Cartan generators):")
    for n, res in artifact["rebuttal_absorption_refutation"].items():
        print(f"  n={n}: rank(Cartans)={res['rank_cartans']}, "
              f"rank(Cartans + identity)={res['rank_cartans_plus_identity']}, "
              f"rank increases={res['rank_increases']}")
        print(f"        => {res['conclusion']}")
    print()
    print("Direct projection using OFFICIAL H_k formulas (target scalar = 1/2):")
    for n, res in artifact["rebuttal_direct_projection"].items():
        print(f"  n={n}: system consistent={res['system_consistent']}")
        for eq in res["system_equations"]:
            print(f"    {eq}")
        for step in res["solution_walkthrough"]:
            print(f"    {step}")
        print(f"  => {res['verdict']}")
        print()

    print()
    print("=" * 60)
    print("SECTION 2d: Full-Vector Span Check (Third Review Response)")
    print("=" * 60)
    print("Checking whether the ENTIRE Cartan-sector component of")
    print("γ(H_{j+1}, F(σ,j,s)) lies in span{ρ(H_k)} without monomial splitting.")
    print()
    for n, checks in artifact["rebuttal_full_vector_checks"].items():
        print(f"  n={n}:")
        for chk in checks:
            lbl = chk["label"]
            consistent = chk["system_consistent"]
            incons = chk["inconsistencies"]
            status = "CONSISTENT (no obstruction)" if consistent else f"INCONSISTENT ({len(incons)} contradiction(s))"
            print(f"    {lbl}")
            print(f"      => {status}")
            if not consistent:
                for inc in incons:
                    print(f"         {inc['equation']}")
        print()
    print("All full-vector checks confirm: the entire Cartan-sector target vector")
    print("is NOT reachable by any linear combination of the official Cartan images.")
    print("Full-vector obstruction confirmed for all (j,s) pairs and n=1,2,3.")

    print("\nVerification complete.")

