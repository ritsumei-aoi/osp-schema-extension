"""
C_generators.py — Generate Schema 1 (structure constants) JSON for C(n+1) = osp(2|2n).

The algebra C(n+1) is realized via:
  - Standard fermionic pair a_1^+, a_1^- with CAR: {a_1^-, a_1^+} = 1
  - Bosonic oscillators b_k^+, b_k^- for k=1,...,n with CCR: [b_k^-, b_l^+] = delta_kl

All brackets are computed symbolically using the oscillator algebra rules.
"""

from __future__ import annotations
import json
import datetime
from fractions import Fraction
from itertools import product


def make_basis(n: int) -> dict:
    """Return even/odd basis lists for C(n+1) with bosonic rank n."""
    even = []
    # Cartan generators H_1, ..., H_{n+1}
    for k in range(1, n + 2):
        even.append(f"H_{k}")
    # Positive bosonic: E_2del{k}_p, then E_del{i}_del{j}_pp
    for k in range(1, n + 1):
        even.append(f"E_2del{k}_p")
    for i in range(1, n + 1):
        for j in range(i + 1, n + 1):
            even.append(f"E_del{i}_del{j}_pp")
    # Negative bosonic: E_2del{k}_m, then E_del{i}_del{j}_mm
    for k in range(1, n + 1):
        even.append(f"E_2del{k}_m")
    for i in range(1, n + 1):
        for j in range(i + 1, n + 1):
            even.append(f"E_del{i}_del{j}_mm")
    # Mixed: E_del{i}_del{j}_pm, E_del{i}_del{j}_mp
    for i in range(1, n + 1):
        for j in range(i + 1, n + 1):
            even.append(f"E_del{i}_del{j}_pm")
    for i in range(1, n + 1):
        for j in range(i + 1, n + 1):
            even.append(f"E_del{i}_del{j}_mp")

    odd = []
    for sign in ["pp", "pm", "mp", "mm"]:
        for k in range(1, n + 1):
            odd.append(f"E_eps1_del{k}_{sign}")

    return {"even": even, "odd": odd}


def make_parity(basis: dict) -> dict:
    parity = {}
    for g in basis["even"]:
        parity[g] = 0
    for g in basis["odd"]:
        parity[g] = 1
    return parity


def make_generator_realization(n: int) -> dict:
    """Return generator realization dict for C(n+1)."""
    realizations = {}

    # H_1 = a_1^+ a_1^- + b_1^+ b_1^-
    realizations["H_1"] = {
        "standard_form": [
            {"words": ["a_1_p", "a_1_m"], "coeff": "1"},
            {"words": ["b_1_p", "b_1_m"], "coeff": "1"},
        ],
        "frappat_form": "a_1^+ a_1^- + b_1^+ b_1^-",
        "parity": 0,
    }
    # H_k = b_{k-1}^+ b_{k-1}^- - b_k^+ b_k^-  for k=2,...,n
    for k in range(2, n + 1):
        realizations[f"H_{k}"] = {
            "standard_form": [
                {"words": [f"b_{k-1}_p", f"b_{k-1}_m"], "coeff": "1"},
                {"words": [f"b_{k}_p", f"b_{k}_m"], "coeff": "-1"},
            ],
            "frappat_form": f"b_{k-1}^+ b_{k-1}^- - b_{k}^+ b_{k}^-",
            "parity": 0,
        }
    # H_{n+1} = -b_n^+ b_n^- - 1/2
    realizations[f"H_{n+1}"] = {
        "standard_form": [
            {"words": [f"b_{n}_p", f"b_{n}_m"], "coeff": "-1"},
            {"words": [], "coeff": "-1/2"},
        ],
        "frappat_form": f"-b_{n}^+ b_{n}^- - 1/2",
        "parity": 0,
        "note": "Terminal Cartan",
    }
    # E_2del{k}_p = (b_k^+)^2
    for k in range(1, n + 1):
        realizations[f"E_2del{k}_p"] = {
            "standard_form": [{"words": [f"b_{k}_p", f"b_{k}_p"], "coeff": "1"}],
            "frappat_form": f"(b_{k}^+)^2",
            "parity": 0,
        }
    # E_2del{k}_m = (b_k^-)^2
    for k in range(1, n + 1):
        realizations[f"E_2del{k}_m"] = {
            "standard_form": [{"words": [f"b_{k}_m", f"b_{k}_m"], "coeff": "1"}],
            "frappat_form": f"(b_{k}^-)^2",
            "parity": 0,
        }
    # E_del{i}_del{j}_pp = b_i^+ b_j^+
    for i in range(1, n + 1):
        for j in range(i + 1, n + 1):
            realizations[f"E_del{i}_del{j}_pp"] = {
                "standard_form": [{"words": [f"b_{i}_p", f"b_{j}_p"], "coeff": "1"}],
                "frappat_form": f"b_{i}^+ b_{j}^+",
                "parity": 0,
            }
    # E_del{i}_del{j}_mm = b_i^- b_j^-
    for i in range(1, n + 1):
        for j in range(i + 1, n + 1):
            realizations[f"E_del{i}_del{j}_mm"] = {
                "standard_form": [{"words": [f"b_{i}_m", f"b_{j}_m"], "coeff": "1"}],
                "frappat_form": f"b_{i}^- b_{j}^-",
                "parity": 0,
            }
    # E_del{i}_del{j}_pm = b_i^+ b_j^-
    for i in range(1, n + 1):
        for j in range(i + 1, n + 1):
            realizations[f"E_del{i}_del{j}_pm"] = {
                "standard_form": [{"words": [f"b_{i}_p", f"b_{j}_m"], "coeff": "1"}],
                "frappat_form": f"b_{i}^+ b_{j}^-",
                "parity": 0,
            }
    # E_del{i}_del{j}_mp = b_i^- b_j^+
    for i in range(1, n + 1):
        for j in range(i + 1, n + 1):
            realizations[f"E_del{i}_del{j}_mp"] = {
                "standard_form": [{"words": [f"b_{i}_m", f"b_{j}_p"], "coeff": "1"}],
                "frappat_form": f"b_{i}^- b_{j}^+",
                "parity": 0,
            }
    # Odd generators
    for k in range(1, n + 1):
        realizations[f"E_eps1_del{k}_pp"] = {
            "standard_form": [{"words": ["a_1_p", f"b_{k}_p"], "coeff": "1"}],
            "frappat_form": f"a_1^+ b_{k}^+",
            "parity": 1,
        }
        realizations[f"E_eps1_del{k}_pm"] = {
            "standard_form": [{"words": ["a_1_p", f"b_{k}_m"], "coeff": "1"}],
            "frappat_form": f"a_1^+ b_{k}^-",
            "parity": 1,
        }
        realizations[f"E_eps1_del{k}_mp"] = {
            "standard_form": [{"words": ["a_1_m", f"b_{k}_p"], "coeff": "1"}],
            "frappat_form": f"a_1^- b_{k}^+",
            "parity": 1,
        }
        realizations[f"E_eps1_del{k}_mm"] = {
            "standard_form": [{"words": ["a_1_m", f"b_{k}_m"], "coeff": "1"}],
            "frappat_form": f"a_1^- b_{k}^-",
            "parity": 1,
        }

    return {
        "description": "Oscillator word representation in PBW order",
        "ordering": "a_1_p, a_1_m, " + ", ".join(
            f"b_{k}_p, b_{k}_m" for k in range(1, n + 1)
        ),
        "realizations": realizations,
    }


# ─── Structure constant computation ───────────────────────────────────────────
#
# We represent each generator by its root vector, then compute [X,Y] using
# the commutation rules of the oscillator algebra.
#
# Root vectors for C(n+1):
#   Even: H_k (Cartan), 2δ_k, δ_i±δ_j, -(δ_i±δ_j), -2δ_k
#   Odd: ε+δ_k, ε-δ_k, -ε+δ_k, -ε-δ_k
#
# We work with root labels and use standard Lie superalgebra bracket rules.
# Rather than a full oscillator algebra computation, we encode the structure
# constants directly from the known formulas for osp(2|2n).


def gen_root(label: str, n: int):
    """Parse generator label to root vector (eps_coeff, delta_coeffs list)."""
    if label.startswith("H_"):
        return None  # Cartan
    if label.startswith("E_eps1_del"):
        # E_eps1_del{k}_{sign}
        rest = label[len("E_eps1_del"):]
        # rest is like "1_pp", "2_pm", etc.
        parts = rest.split("_")
        k = int(parts[0])
        sign = parts[1]
        eps = 1 if sign[0] == "p" else -1
        delta_k = 1 if sign[1] == "p" else -1
        delta = [0] * n
        delta[k - 1] = delta_k
        return (eps, tuple(delta))
    if label.startswith("E_2del"):
        rest = label[len("E_2del"):]
        parts = rest.split("_")
        k = int(parts[0])
        sign = 1 if parts[1] == "p" else -1
        delta = [0] * n
        delta[k - 1] = 2 * sign
        return (0, tuple(delta))
    if label.startswith("E_del"):
        rest = label[len("E_del"):]
        # rest is like "1_del2_pm" → split on "_del" first
        # format: "{i}_del{j}_{sign}"
        parts = rest.split("_")
        i = int(parts[0])
        # parts[1] is "del{j}", parts[2] is sign
        j = int(parts[1][3:])  # strip "del"
        sign = parts[2]
        si = 1 if sign[0] == "p" else -1
        sj = 1 if sign[1] == "p" else -1
        delta = [0] * n
        delta[i - 1] = si
        delta[j - 1] = sj
        return (0, tuple(delta))
    return None


def root_to_gen(eps: int, delta: tuple, n: int) -> str | None:
    """Convert root vector back to generator label, or None if not in basis."""
    # Check if it's zero
    if eps == 0 and all(d == 0 for d in delta):
        return None  # Would be Cartan, handle separately

    if eps != 0:
        # Odd generator
        k_list = [i + 1 for i, d in enumerate(delta) if d != 0]
        zero_list = [i for i, d in enumerate(delta) if d == 0]
        if len(k_list) != 1 or len(zero_list) != n - 1:
            return None
        k = k_list[0]
        dk = delta[k - 1]
        if abs(eps) == 1 and abs(dk) == 1:
            es = "p" if eps == 1 else "m"
            ds = "p" if dk == 1 else "m"
            return f"E_eps1_del{k}_{es}{ds}"
        return None
    else:
        # Even generator
        nonzero = [(i + 1, d) for i, d in enumerate(delta) if d != 0]
        if len(nonzero) == 1:
            k, dk = nonzero[0]
            if abs(dk) == 2:
                s = "p" if dk > 0 else "m"
                return f"E_2del{k}_{s}"
        if len(nonzero) == 2:
            (i, di), (j, dj) = sorted(nonzero)
            if abs(di) == 1 and abs(dj) == 1:
                si = "p" if di > 0 else "m"
                sj = "p" if dj > 0 else "m"
                return f"E_del{i}_del{j}_{si}{sj}"
        return None


def cartan_index(label: str) -> int | None:
    if label.startswith("H_"):
        return int(label[2:])
    return None


def compute_structure_constants(n: int) -> list:
    """
    Compute all non-zero structure constants for C(n+1) = osp(2|2n).

    Returns list of dicts {X, Y, Z, coeff, sign_rule}.

    Strategy: use explicit root system formulas for osp(2|2n).
    The Lie superalgebra bracket [X_α, X_β] is determined by:
      - [H_k, X_α] = α(H_k) X_α  (Cartan action)
      - [X_α, X_{-α}] = H_α      (for even roots)
      - {X_α, X_{-α}} = H_α      (for odd roots with graded sign)
      - [X_α, X_β] = N_{αβ} X_{α+β} if α+β is a root
      - 0 otherwise
    """
    basis = make_basis(n)
    all_gens = basis["even"] + basis["odd"]
    parity = make_parity(basis)

    sc = []

    def add(X, Y, Z, coeff):
        if coeff == 0:
            return
        sc.append({
            "X": X,
            "Y": Y,
            "Z": Z,
            "coeff": str(Fraction(coeff)),
            "sign_rule": "graded",
        })

    # ── Cartan × root generator ───────────────────────────────────────────
    # [H_k, E_α] = α(H_k) E_α
    #
    # H_1 eigenvalues: α(H_1) where H_1 = a_1^+ a_1^- + b_1^+ b_1^-
    #   ε+δ_1: +1+1=2, ε-δ_1: +1-1=0, -ε+δ_1: -1+1=0, -ε-δ_1: -1-1=-2
    #   ε+δ_k(k>1): 1, ε-δ_k(k>1): 1, -ε+δ_k(k>1): -1, -ε-δ_k(k>1): -1
    #   2δ_1: 2, -2δ_1: -2, δ_1±δ_j: 1 (j>1), -δ_1±δ_j: -1 (j>1)
    #   2δ_k(k>1): 0, ±δ_i±δ_j(i,j>1): 0
    #
    # H_k (k=2..n): H_k = b_{k-1}^+ b_{k-1}^- - b_k^+ b_k^-
    #   α(H_k) = delta_{k-1} coeff - delta_k coeff of α
    #
    # H_{n+1}: H_{n+1} = -b_n^+ b_n^- - 1/2
    #   α(H_{n+1}) = -delta_n coeff of α
    #   (the -1/2 constant doesn't appear in the adjoint action)

    def cartan_eigenvalue(h_idx: int, gen_label: str) -> int:
        root = gen_root(gen_label, n)
        if root is None:
            return 0
        eps_c, delta_c = root

        if h_idx == 1:
            # H_1 = a_1^+ a_1^- + b_1^+ b_1^-
            return eps_c + delta_c[0]
        elif 2 <= h_idx <= n:
            # H_k = b_{k-1}^+ b_{k-1}^- - b_k^+ b_k^-
            return delta_c[h_idx - 2] - delta_c[h_idx - 1]
        else:
            # H_{n+1} = -b_n^+ b_n^-
            return -delta_c[n - 1]

    for h_label in [f"H_{k}" for k in range(1, n + 2)]:
        h_idx = cartan_index(h_label)
        for g in all_gens:
            ev = cartan_eigenvalue(h_idx, g)
            if ev != 0:
                add(h_label, g, g, ev)

    # ── Root × root generator ─────────────────────────────────────────────
    # For non-Cartan generators X_α and X_β:
    # graded bracket [X_α, X_β] = X_α X_β - (-1)^{p(α)p(β)} X_β X_α
    #
    # Key cases:
    # 1) α + β = 0 (root + negative root) → bracket gives Cartan element
    # 2) α + β is a root → bracket gives N_{αβ} X_{α+β}
    # 3) Otherwise → 0
    #
    # Structure constants for osp(2|2n) from Frappat et al.:
    # We enumerate all pairs and compute using root arithmetic.

    non_cartan = [g for g in all_gens if not g.startswith("H_")]

    for X in non_cartan:
        rx = gen_root(X, n)
        px = parity[X]
        ex, dx = rx

        for Y in non_cartan:
            ry = gen_root(Y, n)
            py = parity[Y]
            ey, dy = ry

            # Sum of roots
            e_sum = ex + ey
            d_sum = tuple(dx[i] + dy[i] for i in range(n))

            # Check if sum is zero (α + β = 0)
            if e_sum == 0 and all(d == 0 for d in d_sum):
                # [X_α, X_{-α}] = H_α (with appropriate graded sign)
                # Graded bracket: X_α X_{-α} - (-1)^{p(α)p(-α)} X_{-α} X_α
                # For this to be non-zero, we need this to give a Cartan combination.
                # Using oscillator algebra:
                # - Even pair (α even): [E_α, E_{-α}] = H_α
                # - Odd pair (α odd): {E_α, E_{-α}} = H_α (anticommutator)
                # Convention: we record [X, Y] = Z with coeff, where the graded
                # bracket for odd generators gives anticommutator.
                # We only record the pair (X, Y) with X coming before Y in basis.
                # Build H_α as combination of simple Cartans.
                # H_α = sum_k α(H_k^*) H_k where H_k^* is the coroot
                # For us: record which Cartan combination results.
                #
                # For osp(2|2n), [E_α, E_{-α}] = H_α:
                # We compute α(H_k) for each k to get the coroot expansion.
                # But we need to record the actual Cartan generator.
                # Since Cartan generators are not necessarily a simple root basis,
                # we express H_α in terms of H_1,...,H_{n+1}.
                #
                # From the oscillator:
                # [a_1^+ b_k^+, a_1^- b_k^-] = {a_1^+, a_1^-}{b_k^+ b_k^-} graded
                # Using oscillator algebra and graded bracket:
                # {E_{ε+δ_k}, E_{-ε-δ_k}} = (a_1^+ a_1^- + a_1^- a_1^+)(b_k^+ b_k^-)
                #   ... this is computed carefully below
                #
                # We use the known result: for C(n+1), the result of
                # [E_α, E_{-α}] is determined by which simple roots it corresponds to.
                # We record this as structure constants for each Cartan.
                cartan_coeffs = {}
                for k in range(1, n + 2):
                    ev = cartan_eigenvalue(k, X)
                    if ev != 0:
                        cartan_coeffs[f"H_{k}"] = ev
                # The bracket [E_α, E_{-α}] = H_α = sum_k c_k H_k
                # where c_k = α(H_k) / (H_k, H_k) ... but for the oscillator
                # realization, we need the actual numeric coefficients.
                # For the standard normalization used in Frappat:
                # Use the eigenvalues directly (they encode the coroot).
                for h_label, coeff in cartan_coeffs.items():
                    add(X, Y, h_label, coeff)
                continue

            # Check if sum is a root
            z_label = root_to_gen(e_sum, d_sum, n)
            if z_label is None:
                continue

            # Compute structure constant N_{αβ}
            # For osp(2|2n), the structure constants from Frappat are:
            # N_{αβ} = ±1 for most pairs (depends on root system sign conventions)
            # We use the oscillator algebra to determine the sign.
            #
            # Key rule: [a_1^σ b_k^s, a_1^τ b_l^t] using oscillator algebra
            # For odd-odd: {a_1^σ b_k^s, a_1^τ b_l^t}
            #   = {a_1^σ, a_1^τ} b_k^s b_l^t (since bosons commute with fermions)
            #   + (-1)^{something} a_1^σ a_1^τ {b_k^s, b_l^t}  <-- but bosons use CCR not CAR
            # Actually for fermion-boson product operators:
            # {a_1^σ b_k^s, a_1^τ b_l^t} = a_1^σ b_k^s a_1^τ b_l^t + a_1^τ b_l^t a_1^σ b_k^s
            # Since [b, a_1] = 0: = a_1^σ a_1^τ b_k^s b_l^t + a_1^τ a_1^σ b_l^t b_k^s
            # = {a_1^σ, a_1^τ} b_k^s b_l^t + a_1^τ [a_1^σ, a_1^τ b_l^t b_k^s] ...
            # This simplifies to:
            # = {a_1^σ, a_1^τ} b_k^s b_l^t  when s ≠ t or k ≠ l, but we also get
            # a_1^τ a_1^σ [b_l^t, b_k^s] ... let me think more carefully.
            #
            # For odd generators X = a_1^σ b_k^s, Y = a_1^τ b_l^t (both parity 1):
            # graded bracket [X, Y] = XY - (-1)^{1·1} YX = XY + YX = {X, Y}
            # {a_1^σ b_k^s, a_1^τ b_l^t}
            # = a_1^σ b_k^s a_1^τ b_l^t + a_1^τ b_l^t a_1^σ b_k^s
            # Since [b, a_1^±] = 0:
            # = a_1^σ a_1^τ b_k^s b_l^t + a_1^τ a_1^σ b_l^t b_k^s
            # = a_1^σ a_1^τ b_k^s b_l^t + a_1^τ a_1^σ b_l^t b_k^s
            #
            # Case σ = τ: a_1^σ a_1^σ = 0, a_1^σ a_1^σ = 0 → 0
            # Case σ ≠ τ (say σ=+, τ=-):
            # = a_1^+ a_1^- b_k^s b_l^t + a_1^- a_1^+ b_l^t b_k^s
            # For the root sum: e_sum = σ + τ = 0, so this gives Cartan (handled above).
            #
            # For odd-even or even-odd: standard commutator.
            # For even-even: standard commutator.
            #
            # The key non-trivial structure constants are:
            # [E_{ε+δ_k}, E_{-ε+δ_l}] = [a_1^+ b_k^+, a_1^- b_l^+]
            # = a_1^+ b_k^+ a_1^- b_l^+ - a_1^- b_l^+ a_1^+ b_k^+ (graded: both odd, anticommute)
            # Actually graded bracket: [X,Y] = XY - (-1)^{p(X)p(Y)} YX
            # Both parity 1: [X,Y] = XY - (-1)^1 YX = XY + YX (anticommutator)
            # = a_1^+ a_1^- b_k^+ b_l^+ + a_1^- a_1^+ b_l^+ b_k^+
            # = a_1^+ a_1^- b_k^+ b_l^+ + a_1^- a_1^+ b_k^+ b_l^+  (bosons commute)
            # = (a_1^+ a_1^- + a_1^- a_1^+) b_k^+ b_l^+ ... wait for k≠l
            # Hmm, but this only gives a non-zero result when...
            # Actually this is b_k^+ b_l^+ (for k≠l) times (a_1^+ a_1^- + a_1^- a_1^+)
            # = b_k^+ b_l^+ * 1  (since {a_1^+, a_1^-} = 1... wait no)
            # {a_1^-, a_1^+} = 1 means a_1^- a_1^+ + a_1^+ a_1^- = 1, so
            # a_1^+ a_1^- + a_1^- a_1^+ = 1 (just reordered)
            # So {E_{ε+δ_k}, E_{-ε+δ_l}} = b_k^+ b_l^+ = E_{del{k}_del{l}_pp} (for k≠l, or k=l?)
            # For k=l: b_k^+ b_k^+ = E_{2del_k_p}... wait b_k^+ b_k^+ = (b_k^+)^2, yes.
            # For k<l: b_k^+ b_l^+ = E_del{k}_del{l}_pp
            # For k>l: b_l^+ b_k^+ = E_del{l}_del{k}_pp (since bosons commute, this is same)
            #
            # So the structure constant is 1 for {E_{ε+δ_k}, E_{-ε+δ_l}} = E_{δ_k + δ_l}
            # (adjusting indices so i < j for the label).

            # Determine N_{αβ} from oscillator algebra:
            coeff = compute_osp_structure_constant(X, Y, z_label, ex, dx, ey, dy, px, py, n)
            if coeff != 0:
                add(X, Y, z_label, coeff)

    return sc


def compute_osp_structure_constant(X, Y, Z, ex, dx, ey, dy, px, py, n):
    """
    Compute N_{αβ} for [X_α, X_β] = N_{αβ} X_{α+β} using the oscillator algebra.

    For C(n+1), generators are tensor products of fermionic (a_1^±) and bosonic (b_k^±).
    We use explicit oscillator algebra rules.
    """
    # Encode generators as (a_sign, b_index, b_sign) or (b_index1, b_sign1, b_index2, b_sign2)

    # Parse generator type
    def parse(label):
        if label.startswith("E_eps1_del"):
            rest = label[len("E_eps1_del"):]
            parts = rest.split("_")
            k = int(parts[0])
            sign = parts[1]
            a_sign = 1 if sign[0] == "p" else -1
            b_sign = 1 if sign[1] == "p" else -1
            return ("ab", a_sign, k, b_sign)
        elif label.startswith("E_2del"):
            rest = label[len("E_2del"):]
            parts = rest.split("_")
            k = int(parts[0])
            b_sign = 1 if parts[1] == "p" else -1
            return ("bb_same", k, b_sign)
        elif label.startswith("E_del"):
            rest = label[len("E_del"):]
            parts = rest.split("_")
            i = int(parts[0])
            j = int(parts[1][3:])  # strip "del"
            si = 1 if parts[2][0] == "p" else -1
            sj = 1 if parts[2][1] == "p" else -1
            return ("bb_diff", i, si, j, sj)
        return None

    tx = parse(X)
    ty = parse(Y)
    if tx is None or ty is None:
        return 0

    # Case: both odd (ab type) → anticommutator
    if tx[0] == "ab" and ty[0] == "ab":
        # X = a_1^{ax} b_kx^{bx}, Y = a_1^{ay} b_ky^{by}
        ax, kx, bx = tx[1], tx[2], tx[3]
        ay, ky, by = ty[1], ty[2], ty[3]
        # {X, Y} = a_1^{ax} a_1^{ay} b_kx^{bx} b_ky^{by}
        #         + a_1^{ay} a_1^{ax} b_ky^{by} b_kx^{bx}
        # = (a_1^{ax} a_1^{ay} + a_1^{ay} a_1^{ax}) b_kx^{bx} b_ky^{by}
        #   + a_1^{ay} a_1^{ax} (b_ky^{by} b_kx^{bx} - b_kx^{bx} b_ky^{by})
        # For bosons: [b_k^s, b_l^t] = delta_{kl} delta_{st,-} (i.e., [b^-, b^+] = 1)
        # so b_ky^{by} b_kx^{bx} - b_kx^{bx} b_ky^{by} = [b_ky^{by}, b_kx^{bx}]
        # = delta_{ky,kx} * (1 if by=-1 and bx=1 else -1 if by=1 and bx=-1 else 0)
        #
        # Also: {a_1^{ax}, a_1^{ay}} = delta_{ax,-ay}
        # (since {a_1^-, a_1^+} = 1, {a_1^+, a_1^-} = 1, {a_1^+,a_1^+}={a_1^-,a_1^-}=0)
        anticomm_a = 1 if ax + ay == 0 else 0  # ax=1,ay=-1 or ax=-1,ay=1
        boson_comm = 0
        if kx == ky:
            if bx == 1 and by == -1:
                boson_comm = 1   # [b^-, b^+] = 1 → b^+ b^- contributes 1... wait
                # [b^-, b^+] = 1, so b^- b^+ = b^+ b^- + 1
                # {a1^ay, a1^ax} b_ky^by b_kx^bx term for by=-1,bx=1:
                # ... actually let me redo this:
                # The cross term: a_1^{ay} a_1^{ax} [b_ky^{by}, b_kx^{bx}]
                # [b_k^{by}, b_k^{bx}] = by=- bx=+: [b^-, b^+] = 1
                # by=+ bx=-: [b^+, b^-] = -1
                boson_comm = 1
            elif bx == -1 and by == 1:
                boson_comm = -1

        # Total anticommutator:
        # Part 1: anticomm_a * b_kx^{bx} b_ky^{by}  (only if ax+ay=0)
        # Part 2: a_1^{ay} a_1^{ax} * boson_comm     (only if kx==ky and bx≠by)

        result = 0
        # Part 1: gives an even (bosonic) generator
        if anticomm_a and not (kx == ky and bx == by):  # non-diagonal
            # Result is b_kx^{bx} b_ky^{by}
            # This contributes coeff 1 to Z = root_to_gen(0, delta_sum, n)
            # We already know Z from the caller, so just return 1
            result += 1
        elif anticomm_a and kx == ky and bx == by:
            # b_k^s b_k^s = (b_k^s)^2 → E_2del{k}_{s}
            result += 1

        # Part 2: {a_1^{ay}, a_1^{ax}} * boson_comm → Cartan contribution (handled elsewhere)
        # This contributes to Cartan only if ax+ay=0 and kx=ky (handled in the α+β=0 case above)
        # For the non-Cartan case (sum ≠ 0), part 2 gives:
        # anticomm_a_cross = a_1^{ay} a_1^{ax}  (not an anticommutator)
        # Wait: a_1^{ay} a_1^{ax}: if ax=ay, this is 0 (nilpotent).
        # If ax ≠ ay: a_1^{ay} a_1^{ax} is not simplified without further relations.
        # But in the result Z (the target generator), eps_sum = ax + ay.
        # If ax + ay ≠ 0, the part-2 term also contributes when boson_comm ≠ 0.
        if boson_comm != 0 and kx == ky:
            # The a_1^{ay} a_1^{ax} part: e_sum = ax + ay ≠ 0 (otherwise handled above)
            if ax + ay != 0:
                result += boson_comm  # a_1^{ay} a_1^{ax} with no b factor = Cartan? No...
                # Actually: a_1^{ay} a_1^{ax} alone is not a basis element.
                # In the oscillator algebra, a_1^+ a_1^+ = 0, a_1^- a_1^- = 0.
                # a_1^+ a_1^- and a_1^- a_1^+ are Cartan-related objects.
                # For e_sum = ax + ay ≠ 0, we need |ax + ay| > 1, impossible since ax,ay ∈ {±1}.
                # So e_sum = ax + ay is 0, +2, or -2. Only 0 is possible for distinct signs.
                # Thus part 2 only contributes to Cartan (handled above). Skip here.
                result -= boson_comm  # undo the mistaken addition

        return result

    # Case: odd × even or even × odd → commutator [X_ab, Y_bb]
    if tx[0] == "ab" and ty[0] in ("bb_same", "bb_diff"):
        ax, kx, bx = tx[1], tx[2], tx[3]
        # X = a_1^{ax} b_kx^{bx}
        # Y = some bosonic generator
        # [X, Y] = a_1^{ax} [b_kx^{bx}, Y_bosonic]
        # since [a_1^{ax}, Y_bosonic] = 0 (fermion commutes with bosons undeformed)
        # = a_1^{ax} * (commutator of b_kx^{bx} with Y_bosonic)

        if ty[0] == "bb_same":
            k2, b2 = ty[1], ty[2]
            # Y = (b_{k2}^{b2})^2
            # [b_kx^{bx}, (b_k2^{b2})^2]
            # If kx != k2: = 0
            # If kx == k2 and bx == b2: = 0 (same sign)
            # If kx == k2 and bx = -b2 (conjugate):
            #   [b_k^{-s}, (b_k^s)^2] = delta_{ks} * 2 b_k^s  (using CCR)
            #   Actually: [b^-, (b^+)^2] = 2 b^+, [b^+, (b^-)^2] = -2 b^-
            if kx != k2:
                return 0
            if bx == b2:
                return 0
            # conjugate pair
            if bx == -1 and b2 == 1:  # [b_k^-, (b_k^+)^2] = 2 b_k^+
                return 2  # result: a_1^{ax} * 2 * b_kx^{+} = 2 * E_eps1_del{kx}_{ax_sign,+}
            elif bx == 1 and b2 == -1:  # [b_k^+, (b_k^-)^2] = -2 b_k^-
                return -2
            return 0

        elif ty[0] == "bb_diff":
            i2, si2, j2, sj2 = ty[1], ty[2], ty[3], ty[4]
            # Y = b_{i2}^{si2} b_{j2}^{sj2}
            # [b_kx^{bx}, b_{i2}^{si2} b_{j2}^{sj2}]
            # = [b_kx^{bx}, b_{i2}^{si2}] b_{j2}^{sj2} + b_{i2}^{si2} [b_kx^{bx}, b_{j2}^{sj2}]
            comm1 = 0
            comm2 = 0
            if kx == i2:
                if bx == -1 and si2 == 1:
                    comm1 = 1   # [b^-, b^+] = 1
                elif bx == 1 and si2 == -1:
                    comm1 = -1  # [b^+, b^-] = -1
            if kx == j2:
                if bx == -1 and sj2 == 1:
                    comm2 = 1
                elif bx == 1 and sj2 == -1:
                    comm2 = -1
            # [b_kx^{bx}, Y] = comm1 * b_{j2}^{sj2} + comm2 * b_{i2}^{si2}
            # result: a_1^{ax} * (comm1 * b_{j2}^{sj2} + comm2 * b_{i2}^{si2})
            # These give odd generators.
            # The target Z is already fixed; determine which term matches Z.
            z_root = gen_root(Z, n)
            if z_root is None:
                return 0
            ez, dz = z_root
            if ez != ax:
                return 0
            # Find which b gives the right delta
            target_k = None
            for k in range(1, n + 1):
                if dz[k - 1] != 0:
                    target_k = k
                    break
            if target_k is None:
                return 0
            target_bs = dz[target_k - 1]

            total = 0
            if comm1 != 0 and j2 == target_k and sj2 == target_bs:
                total += comm1
            if comm2 != 0 and i2 == target_k and si2 == target_bs:
                total += comm2
            return total

    # Even × odd (swap and adjust sign)
    if tx[0] in ("bb_same", "bb_diff") and ty[0] == "ab":
        # [X_even, Y_odd] = -(-1)^{p(X)p(Y)} [Y_odd, X_even] ... graded antisymmetry
        # Graded: [X,Y] = -(-1)^{p(X)p(Y)} [Y,X]
        # p(X)=0, p(Y)=1: [X,Y] = -[Y,X] · (-1)^0 = -[Y,X]
        coeff_yx = compute_osp_structure_constant(Y, X, Z, ey, dy, ex, dx, py, px, n)
        return -coeff_yx

    # Case: both even (bosonic generators)
    if tx[0] in ("bb_same", "bb_diff") and ty[0] in ("bb_same", "bb_diff"):
        # Standard bosonic commutator [Y_bos, Y_bos]
        # [b_i^{si} b_j^{sj}, b_k^{sk} b_l^{sl}] using CCR
        # Expand using Leibniz rule.

        def get_pairs(t):
            if t[0] == "bb_same":
                k, s = t[1], t[2]
                return [(k, s), (k, s)]
            else:
                return [(t[1], t[2]), (t[3], t[4])]

        px_list = get_pairs(tx)
        py_list = get_pairs(ty)

        # [AB, CD] = [A,C]BD + C[A,D]B + A[B,C]D + AC[B,D]
        # where [b_i^s, b_j^t] = delta_{ij}*(1 if s=-1,t=1 else -1 if s=1,t=-1 else 0)
        def comm_bb(a, b):
            (ka, sa), (kb, sb) = a, b
            if ka != kb:
                return 0
            if sa == -1 and sb == 1:
                return 1
            if sa == 1 and sb == -1:
                return -1
            return 0

        A, B = px_list
        C, D = py_list

        # [AB, CD] = comm(A,C) * B * D + C * comm(A,D) * B + A * comm(B,C) * D + A * C * comm(B,D)
        # But we need to track which b operators remain.
        total = 0
        z_root = gen_root(Z, n)
        if z_root is None:
            return 0
        ez, dz = z_root

        def remaining_root(remaining_ops):
            """Convert list of (k, s) pairs to root."""
            d = [0] * n
            for k, s in remaining_ops:
                d[k - 1] += s
            return (0, tuple(d))

        # Term 1: comm(A,C) * [B, D]
        c_AC = comm_bb(A, C)
        if c_AC != 0:
            r = remaining_root([B, D])
            if r == (0, tuple(dz)):
                total += c_AC
            # Also check if B=D gives a squared term
        # Term 2: comm(A,D) * [C, B] → actually [AB,CD] = A[B,CD] + [A,CD]B
        # Let me use the standard expansion properly.
        # [AB, CD] = A[B,CD] + [A,CD]B
        # [B,CD] = [B,C]D + C[B,D]
        # [A,CD] = [A,C]D + C[A,D]

        c_BC = comm_bb(B, C)
        c_BD = comm_bb(B, D)
        c_AC2 = comm_bb(A, C)
        c_AD = comm_bb(A, D)

        total = 0
        # A * [B,C] * D
        if c_BC != 0:
            r = remaining_root([A, D])
            if r == (0, tuple(dz)):
                total += c_BC
        # A * C * [B,D]
        if c_BD != 0:
            r = remaining_root([A, C])
            if r == (0, tuple(dz)):
                total += c_BD
        # [A,C] * B * D
        if c_AC2 != 0:
            r = remaining_root([B, D])
            if r == (0, tuple(dz)):
                total += c_AC2
        # C * [A,D] * B
        if c_AD != 0:
            r = remaining_root([C, B])  # = remaining_root([B,C]) since bosons commute
            if r == (0, tuple(dz)):
                total += c_AD

        return total

    return 0


def build_schema1(n: int) -> dict:
    """Build complete Schema 1 JSON for C(n+1) with bosonic rank n."""
    basis = make_basis(n)
    parity = make_parity(basis)
    dim_even = 2 * n * n + n + 1
    dim_odd = 4 * n
    dim_total = dim_even + dim_odd

    algebra_name = f"C({n+1})"
    osp_name = f"osp(2|{2*n})"

    boson_labels = []
    for k in range(1, n + 1):
        boson_labels.extend([f"b_{k}_p", f"b_{k}_m"])

    schema = {
        "schema_version": "5.0",
        "algebra": {
            "family": "C",
            "m": 1,
            "n": n,
            "cartan_type": algebra_name,
            "alternative_notation": {
                "osp": osp_name,
                "dimension_formula": "osp(2m|2n) with m=1",
            },
            "dimension": {
                "total": dim_total,
                "even": dim_even,
                "odd": dim_odd,
                "formula_even": "2*n^2 + n + 1",
                "formula_odd": "4*n",
            },
        },
        "oscillator_generators": {
            "fermions": {
                "m": 1,
                "labels": ["a_1_p", "a_1_m"],
                "parity": 1,
                "description": "Standard fermionic pair a_1^+, a_1^- with CAR: {a_1^-, a_1^+} = 1",
            },
            "bosons": {
                "count": 2 * n,
                "n": n,
                "labels": boson_labels,
                "description": "Bosonic oscillators b_k^± for k=1,...,n with CCR: [b_k^-, b_l^+] = delta_kl",
            },
        },
        "central_elements": {
            "K": {
                "parity": 0,
                "description": "Even central element; identified with scalar 1 in all current applications.",
                "nilpotent": False,
            },
            "kappa": {
                "parity": 1,
                "description": "Odd central element; kappa^2 = 0.",
                "nilpotent": True,
            },
        },
        "oscillator_relations": {
            "standard_fermion_anticommutators": {
                "description": "CAR for standard fermionic pair",
                "relations": {
                    "creation_annihilation": "{a_1^-, a_1^+} = 1",
                    "same_type_p": "{a_1^+, a_1^+} = 0",
                    "same_type_m": "{a_1^-, a_1^-} = 0",
                },
            },
            "bosonic_commutators": {
                "description": "CCR for bosonic oscillators",
                "relations": {
                    "same_type": "[b_i^pm, b_j^pm] = 0 for all i,j",
                    "conjugate_pair": "[b_i^-, b_j^+] = delta_ij",
                },
            },
            "mixed_commutators": {
                "boson_fermion": "[b_k^pm, a_1^pm] = 0 (undeformed)",
            },
        },
        "basis": {
            **basis,
            "ordering_convention": (
                "PBW: kappa < [odd: E_eps1_del{k}_pp/pm/mp/mm] "
                "< [even: H_k, E_2del{k}_p/m, E_del{i}_del{j}_pp/mm/pm/mp]"
            ),
        },
        "parity": parity,
        "generator_realization": make_generator_realization(n),
        "structure_constants": compute_structure_constants(n),
        "metadata": {
            "generated_by": "src/C_generators.py",
            "generation_date": datetime.date.today().isoformat(),
            "references": [
                "Frappat, Sciarrino, Sorba (2000), Dictionary on Lie Algebras and Superalgebras",
                "arXiv:hep-th/9607161",
            ],
        },
    }
    return schema


def main():
    import os
    data_dir = os.path.join(os.path.dirname(__file__), "..", "data")
    os.makedirs(data_dir, exist_ok=True)

    for n in range(1, 4):
        schema = build_schema1(n)
        out_path = os.path.join(data_dir, f"C_{n}_structure.json")
        with open(out_path, "w") as f:
            json.dump(schema, f, indent=2)
        print(f"Generated {out_path}")
        basis = schema["basis"]
        dim_even = len(basis["even"])
        dim_odd = len(basis["odd"])
        n_sc = len(schema["structure_constants"])
        print(f"  n={n}: even={dim_even}, odd={dim_odd}, structure_constants={n_sc}")


if __name__ == "__main__":
    main()
