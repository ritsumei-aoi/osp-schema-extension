"""
C(n+1) = osp(2|2n) structure constant generator.

Builds Schema 1 JSON for C(n+1) for bosonic rank n.
Oscillator realization:
  - a_1^+, a_1^-: standard fermionic pair, {a_1^-, a_1^+} = 1
  - b_k^+, b_k^-: bosonic oscillators, [b_k^-, b_l^+] = delta_{kl}
"""

from __future__ import annotations
import json
import os
from datetime import date
from fractions import Fraction
from itertools import combinations


def get_basis(n: int) -> tuple[list[str], list[str]]:
    """Return (even_basis, odd_basis) for C(n+1) with bosonic rank n."""
    even = []
    # Cartan generators H_1, ..., H_{n+1}
    for k in range(1, n + 2):
        even.append(f"H_{k}")
    # Positive even roots: 2*delta_k
    for k in range(1, n + 1):
        even.append(f"E_2del{k}_p")
    # Positive even roots: delta_i + delta_j (i < j)
    for i, j in combinations(range(1, n + 1), 2):
        even.append(f"E_del{i}_del{j}_pp")
    # Negative even roots: -2*delta_k
    for k in range(1, n + 1):
        even.append(f"E_2del{k}_m")
    # Negative even roots: -(delta_i + delta_j)
    for i, j in combinations(range(1, n + 1), 2):
        even.append(f"E_del{i}_del{j}_mm")
    # Mixed even roots: delta_i - delta_j (i < j)
    for i, j in combinations(range(1, n + 1), 2):
        even.append(f"E_del{i}_del{j}_pm")
    # Mixed even roots: -(delta_i - delta_j)
    for i, j in combinations(range(1, n + 1), 2):
        even.append(f"E_del{i}_del{j}_mp")

    odd = []
    # Odd roots: eps + delta_k
    for k in range(1, n + 1):
        odd.append(f"E_eps1_del{k}_pp")
    # Odd roots: eps - delta_k
    for k in range(1, n + 1):
        odd.append(f"E_eps1_del{k}_pm")
    # Odd roots: -eps + delta_k
    for k in range(1, n + 1):
        odd.append(f"E_eps1_del{k}_mp")
    # Odd roots: -eps - delta_k
    for k in range(1, n + 1):
        odd.append(f"E_eps1_del{k}_mm")

    return even, odd


def get_parity(basis_even: list[str], basis_odd: list[str]) -> dict[str, int]:
    parity = {}
    for g in basis_even:
        parity[g] = 0
    for g in basis_odd:
        parity[g] = 1
    return parity


def generator_realization(n: int) -> dict:
    """Return oscillator realization for all generators."""
    real = {}

    # Cartan: H_1 = a_1^+ a_1^- + b_1^+ b_1^-
    real["H_1"] = {
        "standard_form": [
            {"words": ["a_1_p", "a_1_m"], "coeff": "1"},
            {"words": ["b_1_p", "b_1_m"], "coeff": "1"},
        ],
        "frappat_form": "a_1^+ a_1^- + b_1^+ b_1^-",
        "parity": 0,
    }
    # Cartan: H_k = b_{k-1}^+ b_{k-1}^- - b_k^+ b_k^- for k=2,...,n
    for k in range(2, n + 1):
        real[f"H_{k}"] = {
            "standard_form": [
                {"words": [f"b_{k-1}_p", f"b_{k-1}_m"], "coeff": "1"},
                {"words": [f"b_{k}_p", f"b_{k}_m"], "coeff": "-1"},
            ],
            "frappat_form": f"b_{k-1}^+ b_{k-1}^- - b_{k}^+ b_{k}^-",
            "parity": 0,
        }
    # Cartan: H_{n+1} = -b_n^+ b_n^- - 1/2
    real[f"H_{n+1}"] = {
        "standard_form": [
            {"words": [f"b_{n}_p", f"b_{n}_m"], "coeff": "-1"},
            {"words": [], "coeff": "-1/2"},
        ],
        "frappat_form": f"-b_{n}^+ b_{n}^- - 1/2",
        "parity": 0,
        "note": "Terminal Cartan; includes constant -1/2",
    }

    for k in range(1, n + 1):
        real[f"E_2del{k}_p"] = {
            "standard_form": [{"words": [f"b_{k}_p", f"b_{k}_p"], "coeff": "1"}],
            "frappat_form": f"(b_{k}^+)^2",
            "parity": 0,
        }
        real[f"E_2del{k}_m"] = {
            "standard_form": [{"words": [f"b_{k}_m", f"b_{k}_m"], "coeff": "1"}],
            "frappat_form": f"(b_{k}^-)^2",
            "parity": 0,
        }
        real[f"E_eps1_del{k}_pp"] = {
            "standard_form": [{"words": ["a_1_p", f"b_{k}_p"], "coeff": "1"}],
            "frappat_form": f"a_1^+ b_{k}^+",
            "parity": 1,
        }
        real[f"E_eps1_del{k}_pm"] = {
            "standard_form": [{"words": ["a_1_p", f"b_{k}_m"], "coeff": "1"}],
            "frappat_form": f"a_1^+ b_{k}^-",
            "parity": 1,
        }
        real[f"E_eps1_del{k}_mp"] = {
            "standard_form": [{"words": ["a_1_m", f"b_{k}_p"], "coeff": "1"}],
            "frappat_form": f"a_1^- b_{k}^+",
            "parity": 1,
        }
        real[f"E_eps1_del{k}_mm"] = {
            "standard_form": [{"words": ["a_1_m", f"b_{k}_m"], "coeff": "1"}],
            "frappat_form": f"a_1^- b_{k}^-",
            "parity": 1,
        }

    for i, j in combinations(range(1, n + 1), 2):
        real[f"E_del{i}_del{j}_pp"] = {
            "standard_form": [{"words": [f"b_{i}_p", f"b_{j}_p"], "coeff": "1"}],
            "frappat_form": f"b_{i}^+ b_{j}^+",
            "parity": 0,
        }
        real[f"E_del{i}_del{j}_mm"] = {
            "standard_form": [{"words": [f"b_{i}_m", f"b_{j}_m"], "coeff": "1"}],
            "frappat_form": f"b_{i}^- b_{j}^-",
            "parity": 0,
        }
        real[f"E_del{i}_del{j}_pm"] = {
            "standard_form": [{"words": [f"b_{i}_p", f"b_{j}_m"], "coeff": "1"}],
            "frappat_form": f"b_{i}^+ b_{j}^-",
            "parity": 0,
        }
        real[f"E_del{i}_del{j}_mp"] = {
            "standard_form": [{"words": [f"b_{i}_m", f"b_{j}_p"], "coeff": "1"}],
            "frappat_form": f"b_{i}^- b_{j}^+",
            "parity": 0,
        }

    return real


# ---------------------------------------------------------------------------
# Structure constant computation via oscillator algebra
# ---------------------------------------------------------------------------

def compute_structure_constants(n: int) -> list[dict]:
    """
    Compute all non-zero structure constants [X, Y} = sum_Z c_{XY}^Z * Z.

    Strategy: encode each generator as a linear combination of oscillator
    monomials, then evaluate the graded commutator symbolically using the
    CCR/CAR relations.

    We represent the algebra in terms of roots and use Frappat table directly
    where derivable from oscillator algebra.
    """
    even_basis, odd_basis = get_basis(n)
    all_basis = even_basis + odd_basis
    parity = get_parity(even_basis, odd_basis)

    sc = []

    def add(X, Y, Z, coeff):
        if coeff == 0:
            return
        sc.append({
            "X": X, "Y": Y, "Z": Z,
            "coeff": str(Fraction(coeff).limit_denominator(1000)),
            "sign_rule": "graded",
        })

    # -----------------------------------------------------------------------
    # Cartan-root brackets [H_k, E_root]
    # Root eigenvalues under H_k:
    #   H_1 = a1^+ a1^- + b1^+ b1^-
    #   H_k = b_{k-1}^+ b_{k-1}^- - b_k^+ b_k^-  (k=2,...,n)
    #   H_{n+1} = -b_n^+ b_n^- - 1/2
    #
    # Eigenvalue of b_j^+ b_j^- on E_root: +1 if root has +delta_j, -1 if -delta_j, 0 otherwise
    # Eigenvalue of a_1^+ a_1^- on E_root: +1 if +eps, -1 if -eps, 0 if no eps
    # -----------------------------------------------------------------------

    def eps_sign(label):
        """Return ε-sign of an odd root label: +1, -1, or 0."""
        if "eps1" in label:
            if label.endswith("_pp") or label.endswith("_pm"):
                return +1
            else:
                return -1
        return 0

    def delta_sign(label, k):
        """Return δ_k sign from root label."""
        # Odd: E_eps1_del{k}_{ss} -> second s = delta sign
        if f"_del{k}_" in label or label.endswith(f"_del{k}_pp") or \
           label.endswith(f"_del{k}_pm") or label.endswith(f"_del{k}_mp") or \
           label.endswith(f"_del{k}_mm"):
            # eps root: E_eps1_delK_XY -> sign from Y position
            if "eps1" in label:
                # e.g. E_eps1_del1_pp -> last two chars before end are pp -> delta sign = +
                suffix = label.split("_")[-1]  # pp, pm, mp, mm
                delta_s = suffix[1]  # second char
                return +1 if delta_s == 'p' else -1
        # Even roots
        if label == f"E_2del{k}_p":
            return +2
        if label == f"E_2del{k}_m":
            return -2
        for i2, j2 in combinations(range(1, n + 1), 2):
            if label == f"E_del{i2}_del{j2}_pp":
                if k == i2 or k == j2:
                    return +1
            elif label == f"E_del{i2}_del{j2}_mm":
                if k == i2 or k == j2:
                    return -1
            elif label == f"E_del{i2}_del{j2}_pm":
                if k == i2:
                    return +1
                if k == j2:
                    return -1
            elif label == f"E_del{i2}_del{j2}_mp":
                if k == i2:
                    return -1
                if k == j2:
                    return +1
        return 0

    for gen in all_basis:
        if gen.startswith("H_"):
            continue
        # eigenvalue of gen under H_k
        for k in range(1, n + 2):
            if k == 1:
                # H_1 = a1^+ a1^- + b1^+ b1^-
                ev = eps_sign(gen) + delta_sign(gen, 1)
            elif k <= n:
                # H_k = b_{k-1}^+ b_{k-1}^- - b_k^+ b_k^-
                ev = delta_sign(gen, k - 1) - delta_sign(gen, k)
            else:
                # H_{n+1} = -b_n^+ b_n^- - 1/2, constant term doesn't contribute to bracket
                ev = -delta_sign(gen, n)
            if ev != 0:
                add(f"H_{k}", gen, gen, ev)
                # Anti-symmetry: [gen, H_k} = -(-1)^{p(gen)*0} [H_k, gen} = -ev * gen
                add(gen, f"H_{k}", gen, -ev)

    # -----------------------------------------------------------------------
    # Brackets involving odd roots (E_eps1_del{k}_{ss})
    # Key brackets from oscillator algebra:
    #
    # {E_eps1_delk_pp, E_eps1_delk_mm} = a1^+ b_k^+ a1^- b_k^- + a1^- b_k^- a1^+ b_k^+
    #   Using {a1^-,a1^+}=1, [b_k^-,b_k^+]=1:
    #   = a1^+a1^- b_k^+ b_k^- + b_k^+b_k^- (from CAR)
    #   Wait, let's be more careful.
    #
    # For graded bracket of two odd elements: {X,Y} = XY + YX
    # X = a1^+ b_k^+, Y = a1^- b_k^-
    # XY = a1^+ b_k^+ a1^- b_k^-
    #    = a1^+ (a1^- b_k^+ + CAR?) * b_k^-   -- b_k^+ and a1^- commute
    #    = a1^+ a1^- b_k^+ b_k^-
    # YX = a1^- b_k^- a1^+ b_k^+
    #    = a1^- a1^+ b_k^- b_k^+
    #    = (1 - a1^+ a1^-)(b_k^+ b_k^- + 1)  [using [b^-, b^+]=1 => b^-b^+ = b^+b^-+1]
    #    = b_k^+ b_k^- + 1 - a1^+ a1^- b_k^+ b_k^- - a1^+ a1^-
    # XY + YX = a1^+ a1^- b_k^+ b_k^- + b_k^+ b_k^- + 1 - a1^+ a1^- b_k^+ b_k^- - a1^+ a1^-
    #         = b_k^+ b_k^- + 1 - a1^+ a1^-
    # In terms of generators: H_1 = a1^+a1^- + b_1^+b_1^-, H_{k+1} = b_{k-1}^+b_{k-1}^- - b_k^+b_k^-
    # For k=1: b_1^+b_1^- + 1 - a1^+a1^-
    # = H_1 - a1^+a1^- - b_1^+b_1^- + b_1^+b_1^- + 1 - a1^+a1^-  no...
    # Let's define N_a = a1^+a1^-, N_k = b_k^+b_k^-
    # H_1 = N_a + N_1
    # H_k = N_{k-1} - N_k for k=2,...,n
    # H_{n+1} = -N_n - 1/2
    # {E_eps1_del1_pp, E_eps1_del1_mm} = N_1 + 1 - N_a = H_1 - 2N_a + 1
    # But N_a alone is not a basis element. Let's express it via Cartans:
    # N_a = H_1 - N_1
    # N_1 = H_1 - H_2 + H_2 - ... depends on n
    # For n=1: N_1 = -H_2 - 1/2 (since H_2 = -N_1 - 1/2 => N_1 = -H_2 - 1/2)
    # So N_a = H_1 - N_1 = H_1 - (-H_2 - 1/2) = H_1 + H_2 + 1/2
    # {E_eps1_del1_pp, E_eps1_del1_mm} = N_1 + 1 - N_a
    #   = (-H_2 - 1/2) + 1 - (H_1 + H_2 + 1/2) = -H_2 - 1/2 + 1 - H_1 - H_2 - 1/2
    #   = -H_1 - 2H_2
    # Hmm, let me redo for general n.
    #
    # For general n: N_k in terms of H_j:
    # H_1 = N_a + N_1
    # H_2 = N_1 - N_2
    # H_3 = N_2 - N_3
    # ...
    # H_n = N_{n-1} - N_n
    # H_{n+1} = -N_n - 1/2
    # From H_{n+1}: N_n = -H_{n+1} - 1/2
    # From H_n: N_{n-1} = H_n + N_n = H_n - H_{n+1} - 1/2
    # From H_{n-1}: N_{n-2} = H_{n-1} + N_{n-1} = H_{n-1} + H_n - H_{n+1} - 1/2
    # Pattern: N_k = sum_{j=k+1}^{n+1} (-1)^{j-k-1?} H_j  ... let me compute
    # N_n = -H_{n+1} - 1/2
    # N_{n-1} = H_n - H_{n+1} - 1/2
    # N_{n-2} = H_{n-1} + H_n - H_{n+1} - 1/2
    # N_k = sum_{j=k+1}^{n} H_j - H_{n+1} - 1/2  (for k=1,...,n)
    # N_a = H_1 - N_1 = H_1 - (sum_{j=2}^{n} H_j - H_{n+1} - 1/2)
    #      = H_1 - sum_{j=2}^{n} H_j + H_{n+1} + 1/2
    #
    # {E_eps1_delk_pp, E_eps1_delk_mm}:
    # = N_k + 1 - N_a
    # = (sum_{j=k+1}^{n} H_j - H_{n+1} - 1/2) + 1 - (H_1 - sum_{j=2}^n H_j + H_{n+1} + 1/2)
    # = sum_{j=k+1}^{n} H_j - H_{n+1} - 1/2 + 1 - H_1 + sum_{j=2}^n H_j - H_{n+1} - 1/2
    # = -H_1 + sum_{j=2}^n H_j + sum_{j=k+1}^n H_j - 2*H_{n+1}
    # Wait this doesn't look right. Let me redo more carefully.
    #
    # {a1^+ b_k^+, a1^- b_k^-} = a1^+ b_k^+ a1^- b_k^- + a1^- b_k^- a1^+ b_k^+
    # Since fermions and bosons commute:
    # = a1^+ a1^- b_k^+ b_k^- + a1^- a1^+ b_k^- b_k^+
    # = N_a N_k + (1 - N_a)(N_k + 1)   [using a1^- a1^+ = 1 - N_a, b_k^- b_k^+ = N_k + 1]
    # = N_a N_k + N_k + 1 - N_a N_k - N_a
    # = N_k + 1 - N_a
    # This confirms the formula.
    #
    # N_k = sum_{j=k+1}^{n} H_j - H_{n+1} - 1/2  (for k >= 1)
    # N_a = H_1 - N_1 = H_1 - (H_2 + H_3 + ... + H_n - H_{n+1} - 1/2)
    #      = H_1 - H_2 - H_3 - ... - H_n + H_{n+1} + 1/2
    #
    # {E_eps1_delk_pp, E_eps1_delk_mm} = N_k + 1 - N_a
    # N_k = sum_{j=k+1}^{n} H_j - H_{n+1} - 1/2
    # -N_a = -(H_1 - H_2 - ... - H_n + H_{n+1} + 1/2)
    #       = -H_1 + H_2 + ... + H_n - H_{n+1} - 1/2
    # N_k + 1 - N_a = sum_{j=k+1}^{n} H_j - H_{n+1} - 1/2 + 1 - H_1 + H_2 + ... + H_n - H_{n+1} - 1/2
    # = -H_1 + sum_{j=2}^{k} H_j + 2*sum_{j=k+1}^{n} H_j - 2*H_{n+1}  + 1 - 1/2 - 1/2
    # = -H_1 + sum_{j=2}^{k} H_j + 2*sum_{j=k+1}^{n} H_j - 2*H_{n+1}
    #
    # For k=1: = -H_1 + 2*(H_2+...+H_n) - 2*H_{n+1}
    # For k=n: = -H_1 + (H_2+...+H_n) - 2*H_{n+1}
    # -----------------------------------------------------------------------

    def N_k_coeffs(k, n):
        """Cartan coefficients for N_k = b_k^+ b_k^-. Dict: H_j -> coeff."""
        coeffs = {}
        for j in range(k + 1, n + 1):
            coeffs[f"H_{j}"] = Fraction(1)
        coeffs[f"H_{n+1}"] = Fraction(-1)
        return coeffs, Fraction(-1, 2)  # constant -1/2

    def N_a_coeffs(n):
        """Cartan coefficients for N_a = a_1^+ a_1^-."""
        coeffs = {f"H_1": Fraction(1)}
        for j in range(2, n + 1):
            coeffs[f"H_{j}"] = Fraction(-1)
        coeffs[f"H_{n+1}"] = Fraction(1)
        return coeffs, Fraction(1, 2)  # constant +1/2

    def anticommutator_pp_mm(k, n):
        """Compute {E_eps1_delk_pp, E_eps1_delk_mm} = N_k + 1 - N_a as Cartan coefficients."""
        nk_c, nk_const = N_k_coeffs(k, n)
        na_c, na_const = N_a_coeffs(n)
        result = {}
        all_keys = set(nk_c) | set(na_c)
        for key in all_keys:
            v = nk_c.get(key, Fraction(0)) - na_c.get(key, Fraction(0))
            if v != 0:
                result[key] = v
        const = nk_const + Fraction(1) - na_const
        return result, const

    for k in range(1, n + 1):
        coeffs, const = anticommutator_pp_mm(k, n)
        for Hj, c in coeffs.items():
            add(f"E_eps1_del{k}_pp", f"E_eps1_del{k}_mm", Hj, c)
        # constant term — not in basis (K=1 is excluded), so we skip if const != 0
        # In the schema, structure constants only reference basis elements; constant means
        # there is a central K term. We record this conceptually as coeff for K but
        # since K=1, this adds to H_k coefficients structurally — document in note if nonzero.
        # Actually the bracket gives a Cartan element combination, constant should vanish
        # for a proper simple root system. Let's check: for k=1, n=1:
        # coeffs should give {E_eps1_del1_pp, E_eps1_del1_mm} = -H_1 + 2*(no H_2 since n=1) - 2*H_2
        # n=1: H_2 = H_{n+1}=-N_1-1/2, N_1=-H_2-1/2, N_a=H_1+H_2+1/2
        # {E_eps1_del1_pp,E_eps1_del1_mm} = N_1+1-N_a = (-H_2-1/2)+1-(H_1+H_2+1/2)
        #   = -H_2-1/2+1-H_1-H_2-1/2 = -H_1-2H_2
        # const = 0, coeffs = {H_1:-1, H_2:-2}. Good.

    # {E_eps1_delk_pm, E_eps1_delk_mp} = {a1^+ b_k^-, a1^- b_k^+}
    # = a1^+ b_k^- a1^- b_k^+ + a1^- b_k^+ a1^+ b_k^-
    # = a1^+ a1^- b_k^- b_k^+ + a1^- a1^+ b_k^+ b_k^-
    # = N_a (N_k+1) + (1-N_a) N_k = N_a N_k + N_a + N_k - N_a N_k = N_a + N_k
    # So {E_eps1_delk_pm, E_eps1_delk_mp} = N_a + N_k

    def anticommutator_pm_mp(k, n):
        """Compute {E_eps1_delk_pm, E_eps1_delk_mp} = N_a + N_k."""
        nk_c, nk_const = N_k_coeffs(k, n)
        na_c, na_const = N_a_coeffs(n)
        result = {}
        for key in set(nk_c) | set(na_c):
            v = nk_c.get(key, Fraction(0)) + na_c.get(key, Fraction(0))
            if v != 0:
                result[key] = v
        const = nk_const + na_const
        return result, const

    for k in range(1, n + 1):
        coeffs, const = anticommutator_pm_mp(k, n)
        for Hj, c in coeffs.items():
            add(f"E_eps1_del{k}_pm", f"E_eps1_del{k}_mp", Hj, c)

    # Cross anticommutators {E_eps1_delk_pp, E_eps1_dell_mm} for k != l
    # = {a1^+ b_k^+, a1^- b_l^-} = a1^+a1^- b_k^+ b_l^- + a1^-a1^+ b_l^- b_k^+
    # = N_a b_k^+ b_l^- + (1-N_a) b_l^- b_k^+
    # b_k^+ b_l^- = E_del{k}_del{l}_pm if k<l, else E_del{l}_del{k}_mp
    # (1-N_a) b_l^- b_k^+ = b_l^- b_k^+ - N_a b_l^- b_k^+
    # Since b_k^+ b_l^- - b_l^- b_k^+ = 0 (bosons commute for k!=l)
    # Wait: for k!=l, [b_k^+, b_l^-] = 0, so b_k^+ b_l^- = b_l^- b_k^+
    # Therefore: {E_eps1_delk_pp, E_eps1_dell_mm}
    # = N_a b_k^+ b_l^- + (1-N_a) b_l^- b_k^+
    # = N_a b_k^+ b_l^- + (1-N_a) b_k^+ b_l^-  (since b_k^+b_l^- = b_l^-b_k^+ for k!=l)
    # = b_k^+ b_l^-
    # This equals E_del{min(k,l)}_del{max(k,l)}_pm or E_del{min(k,l)}_del{max(k,l)}_mp
    # If k < l: b_k^+ b_l^- = E_del{k}_del{l}_pm
    # If k > l: b_k^+ b_l^- = b_l^- b_k^+ = but our basis has E_del{l}_del{k}_mp (l<k)
    # E_del{l}_del{k}_mp = b_l^- b_k^+ = b_k^+ b_l^- (commute) -> yes E_del{l}_del{k}_mp

    for k in range(1, n + 1):
        for l in range(1, n + 1):
            if k == l:
                continue
            i, j = min(k, l), max(k, l)
            if k < l:
                z = f"E_del{i}_del{j}_pm"
                # {E_eps1_delk_pp, E_eps1_dell_mm} = b_k^+ b_l^- = E_del{k}_del{l}_pm
                add(f"E_eps1_del{k}_pp", f"E_eps1_del{l}_mm", z, 1)
            else:
                z = f"E_del{i}_del{j}_mp"
                # k > l: b_k^+ b_l^- = b_l^-b_k^+ = E_del{l}_del{k}_mp
                add(f"E_eps1_del{k}_pp", f"E_eps1_del{l}_mm", z, 1)

    # {E_eps1_delk_pm, E_eps1_dell_mp} for k != l
    # = {a1^+ b_k^-, a1^- b_l^+} = N_a b_k^- b_l^+ + (1-N_a) b_l^+ b_k^-
    # For k!=l: b_k^- b_l^+ = b_l^+ b_k^- (bosons commute)
    # = b_k^- b_l^+ = b_l^+ b_k^-
    # If k < l: b_k^- b_l^+ = E_del{k}_del{l}_mp
    # If k > l: b_k^- b_l^+ = b_l^+ b_k^- = E_del{l}_del{k}_pm (l<k)
    for k in range(1, n + 1):
        for l in range(1, n + 1):
            if k == l:
                continue
            i, j = min(k, l), max(k, l)
            if k < l:
                z = f"E_del{i}_del{j}_mp"
                add(f"E_eps1_del{k}_pm", f"E_eps1_del{l}_mp", z, 1)
            else:
                z = f"E_del{i}_del{j}_pm"
                add(f"E_eps1_del{k}_pm", f"E_eps1_del{l}_mp", z, 1)

    # {E_eps1_delk_pp, E_eps1_dell_pm} = {a1^+b_k^+, a1^+b_l^-}
    # = (a1^+)^2 b_k^+ b_l^- + (a1^+)^2 b_l^- b_k^+ = 0  (since (a1^+)^2 = 0)
    # Similarly for other same-epsilon brackets = 0

    # {E_eps1_delk_pp, E_eps1_dell_pp} = {a1^+b_k^+, a1^+b_l^+} = 2*(a1^+)^2 b_k^+ b_l^+ = 0
    # {E_eps1_delk_mm, E_eps1_dell_mm} = 0 similarly

    # {E_eps1_delk_mp, E_eps1_dell_mm} = {a1^-b_k^+, a1^-b_l^-}
    # = (a1^-)^2 b_k^+ b_l^- + (a1^-)^2 b_l^- b_k^+ = 0

    # {E_eps1_delk_pp, E_eps1_delk_pm} = {a1^+b_k^+, a1^+b_k^-}
    # = (a1^+)^2 b_k^+ b_k^- + (a1^+)^2 b_k^- b_k^+ = 0

    # {E_eps1_delk_mp, E_eps1_delk_pp} = {a1^-b_k^+, a1^+b_k^+}
    # = a1^-a1^+ (b_k^+)^2 + a1^+a1^- (b_k^+)^2 = (a1^-a1^+ + a1^+a1^-)(b_k^+)^2
    # = {a1^-, a1^+}(b_k^+)^2 = 1*(b_k^+)^2 = E_2del{k}_p
    for k in range(1, n + 1):
        add(f"E_eps1_del{k}_mp", f"E_eps1_del{k}_pp", f"E_2del{k}_p", 1)

    # {E_eps1_delk_pm, E_eps1_delk_mm} = {a1^+b_k^-, a1^-b_k^-}
    # = a1^+a1^- (b_k^-)^2 + a1^-a1^+ (b_k^-)^2 = (b_k^-)^2 = E_2del{k}_m
    for k in range(1, n + 1):
        add(f"E_eps1_del{k}_pm", f"E_eps1_del{k}_mm", f"E_2del{k}_m", 1)

    # Cross: {E_eps1_delk_mp, E_eps1_dell_pp} for k!=l
    # = {a1^-b_k^+, a1^+b_l^+} = a1^-a1^+ b_k^+ b_l^+ + a1^+a1^- b_l^+ b_k^+
    # = (1-N_a) b_k^+ b_l^+ + N_a b_l^+ b_k^+ = b_k^+ b_l^+ (since bosons commute)
    # = E_del{i}_del{j}_pp where i=min(k,l), j=max(k,l)
    for k in range(1, n + 1):
        for l in range(1, n + 1):
            if k == l:
                continue
            i, j = min(k, l), max(k, l)
            z = f"E_del{i}_del{j}_pp"
            add(f"E_eps1_del{k}_mp", f"E_eps1_del{l}_pp", z, 1)

    # Cross: {E_eps1_delk_pm, E_eps1_dell_mm} for k!=l
    # = {a1^+b_k^-, a1^-b_l^-} = a1^+a1^- b_k^-b_l^- + a1^-a1^+ b_l^-b_k^-
    # = N_a b_k^-b_l^- + (1-N_a)b_l^-b_k^- = b_k^-b_l^- = E_del{i}_del{j}_mm
    for k in range(1, n + 1):
        for l in range(1, n + 1):
            if k == l:
                continue
            i, j = min(k, l), max(k, l)
            z = f"E_del{i}_del{j}_mm"
            add(f"E_eps1_del{k}_pm", f"E_eps1_del{l}_mm", z, 1)

    # -----------------------------------------------------------------------
    # Even-even brackets (bosonic sector):
    # [E_2delk_p, E_2delk_m] = [b_k^+^2, b_k^-^2]
    # = b_k^+ [b_k^+, b_k^-^2] + [b_k^+, b_k^-^2] b_k^+
    # [b_k^+, b_k^-^2] = b_k^- [b_k^+,b_k^-] + [b_k^+,b_k^-]b_k^- = -b_k^- - b_k^- = -2b_k^-
    # [b_k^+^2, b_k^-^2] = b_k^+(−2b_k^-) + (−2b_k^-)b_k^+ = -2N_k - 2(N_k+1) = -4N_k - 2
    # In terms of Cartans:
    # N_k = sum_{j=k+1}^{n} H_j - H_{n+1} - 1/2
    # -4N_k - 2 = -4*(sum_{j=k+1}^n H_j - H_{n+1} - 1/2) - 2
    #           = -4*sum_{j=k+1}^n H_j + 4*H_{n+1} + 2 - 2
    #           = -4*sum_{j=k+1}^n H_j + 4*H_{n+1}
    # But we need to express as H_k coefficients.
    # Let's compute explicitly using H_k = N_{k-1} - N_k for k=2,...,n, etc.

    for k in range(1, n + 1):
        nk_c, nk_const = N_k_coeffs(k, n)
        # -4*N_k - 2 in terms of H_j:
        for Hj, c in nk_c.items():
            add(f"E_2del{k}_p", f"E_2del{k}_m", Hj, -4 * c)
        # constant: -4*(-1/2) - 2 = 2 - 2 = 0
        # Actually: -4*N_k - 2 constant = -4*nk_const - 2 = -4*(-1/2) - 2 = 2 - 2 = 0
        # Good, no constant.

    # [E_del{i}_del{j}_pp, E_del{i}_del{j}_mm] = [b_i^+ b_j^+, b_i^- b_j^-]
    # = b_i^+ [b_j^+, b_i^- b_j^-] + [b_i^+, b_i^- b_j^-] b_j^+
    # [b_j^+, b_i^- b_j^-] = b_i^- [b_j^+, b_j^-] = -b_i^-
    # [b_i^+, b_i^- b_j^-] = b_j^- [b_i^+, b_i^-] + [b_i^+, b_i^-] b_j^- ... let me use:
    # [b_i^+, b_i^- b_j^-] = [b_i^+, b_i^-] b_j^- = -b_j^-  (using [b^+,b^-]=-1, or [b^-,b^+]=1)
    # Wait: [b_i^-, b_i^+] = 1, so [b_i^+, b_i^-] = -1
    # [b_i^+, b_i^- b_j^-] = [b_i^+, b_i^-] b_j^- + b_i^- [b_i^+, b_j^-] = (-1)b_j^- + 0 = -b_j^-
    # [b_i^+ b_j^+, b_i^- b_j^-]:
    # = b_i^+[b_j^+, b_i^- b_j^-] + [b_i^+, b_i^- b_j^-]b_j^+
    # = b_i^+(-b_i^-) + (-b_j^-)b_j^+
    # = -b_i^+b_i^- - b_j^-b_j^+
    # = -N_i - (N_j + 1)
    # = -N_i - N_j - 1
    # But this should be 0 up to Cartans? Let me check for i=1,j=2 in n=2:
    # -N_1 - N_2 - 1
    # N_1 (k=1,n=2): N_1 = H_2 - H_3 - 1/2
    # N_2 (k=2,n=2): N_2 = -H_3 - 1/2
    # -N_1 - N_2 - 1 = -(H_2-H_3-1/2) - (-H_3-1/2) - 1 = -H_2+H_3+1/2+H_3+1/2-1 = -H_2+2H_3
    # Hmm, let me verify this differently using the root eigenvalues.
    # [E_del1_del2_pp, E_del1_del2_mm] should give a Cartan:
    # H_k eigenvalue of E_{del1+del2}: for H_1: delta1+delta2 from H_1 = (H_1 acts on delta_1 part via N_1)
    # Actually for Cartan-root brackets we already computed these above.
    # Let me use a different approach: from root theory, [E_alpha, E_{-alpha}] = H_alpha.
    # For alpha = delta_i + delta_j: H_alpha is the coroot, expressible in terms of simple coroots.

    for i, j in combinations(range(1, n + 1), 2):
        ni_c, ni_const = N_k_coeffs(i, n)
        nj_c, nj_const = N_k_coeffs(j, n)
        # [E_del{i}_del{j}_pp, E_del{i}_del{j}_mm] = -N_i - N_j - 1
        # But constant = -ni_const - nj_const - 1 = 1/2 + 1/2 - 1 = 0 (good)
        for key in set(ni_c) | set(nj_c):
            c = -(ni_c.get(key, Fraction(0)) + nj_c.get(key, Fraction(0)))
            if c != 0:
                add(f"E_del{i}_del{j}_pp", f"E_del{i}_del{j}_mm", key, c)

    # [E_del{i}_del{j}_pm, E_del{i}_del{j}_mp] = [b_i^+ b_j^-, b_i^- b_j^+]
    # = b_i^+[b_j^-, b_i^- b_j^+] + [b_i^+, b_i^- b_j^+]b_j^-
    # [b_j^-, b_i^- b_j^+] = b_i^-[b_j^-, b_j^+] = b_i^-  (since [b^-,b^+]=1)
    # [b_i^+, b_i^- b_j^+] = [b_i^+,b_i^-]b_j^+ = -b_j^+
    # = b_i^+ b_i^- + (-b_j^+)b_j^- = N_i - N_j
    for i, j in combinations(range(1, n + 1), 2):
        ni_c, _ = N_k_coeffs(i, n)
        nj_c, _ = N_k_coeffs(j, n)
        for key in set(ni_c) | set(nj_c):
            c = ni_c.get(key, Fraction(0)) - nj_c.get(key, Fraction(0))
            if c != 0:
                add(f"E_del{i}_del{j}_pm", f"E_del{i}_del{j}_mp", key, c)

    # -----------------------------------------------------------------------
    # Even-even product brackets (root-root, same parity = 0 bracket)
    # Key brackets:
    # [E_del{i}_del{j}_pm, E_2del{j}_p] = [b_i^+b_j^-, b_j^+^2]
    # = b_i^+ [b_j^-, b_j^+^2] = b_i^+ * 2*b_j^+ = 2*b_i^+b_j^+ = 2*E_del{i}_del{j}_pp
    for i, j in combinations(range(1, n + 1), 2):
        add(f"E_del{i}_del{j}_pm", f"E_2del{j}_p", f"E_del{i}_del{j}_pp", 2)
        # [E_2del{j}_p, E_del{i}_del{j}_pm] = -2*E_del{i}_del{j}_pp
        add(f"E_2del{j}_p", f"E_del{i}_del{j}_pm", f"E_del{i}_del{j}_pp", -2)

    # [E_del{i}_del{j}_mp, E_2del{j}_m] = [b_i^-b_j^+, b_j^-^2]
    # = b_i^-[b_j^+, b_j^-^2] = b_i^-*(-2b_j^-) = -2*b_i^-b_j^- = -2*E_del{i}_del{j}_mm
    for i, j in combinations(range(1, n + 1), 2):
        add(f"E_del{i}_del{j}_mp", f"E_2del{j}_m", f"E_del{i}_del{j}_mm", -2)
        add(f"E_2del{j}_m", f"E_del{i}_del{j}_mp", f"E_del{i}_del{j}_mm", 2)

    # [E_del{i}_del{j}_pp, E_2del{i}_m] = [b_i^+b_j^+, b_i^-^2]
    # = [b_i^+, b_i^-^2]b_j^+ = (-2b_i^-)b_j^+ = -2*b_i^-b_j^+ = -2*E_del{i}_del{j}_mp
    for i, j in combinations(range(1, n + 1), 2):
        add(f"E_del{i}_del{j}_pp", f"E_2del{i}_m", f"E_del{i}_del{j}_mp", -2)
        add(f"E_2del{i}_m", f"E_del{i}_del{j}_pp", f"E_del{i}_del{j}_mp", 2)

    # [E_del{i}_del{j}_pp, E_2del{j}_m] = [b_i^+b_j^+, b_j^-^2]
    # = b_i^+[b_j^+, b_j^-^2] = b_i^+(-2b_j^-) = -2*b_i^+b_j^- = -2*E_del{i}_del{j}_pm
    for i, j in combinations(range(1, n + 1), 2):
        add(f"E_del{i}_del{j}_pp", f"E_2del{j}_m", f"E_del{i}_del{j}_pm", -2)
        add(f"E_2del{j}_m", f"E_del{i}_del{j}_pp", f"E_del{i}_del{j}_pm", 2)

    # [E_del{i}_del{j}_mm, E_2del{i}_p] = [b_i^-b_j^-, b_i^+^2]
    # = [b_i^-, b_i^+^2]b_j^- = 2b_i^+*b_j^- = 2*E_del{i}_del{j}_pm
    for i, j in combinations(range(1, n + 1), 2):
        add(f"E_del{i}_del{j}_mm", f"E_2del{i}_p", f"E_del{i}_del{j}_pm", 2)
        add(f"E_2del{i}_p", f"E_del{i}_del{j}_mm", f"E_del{i}_del{j}_pm", -2)

    # [E_del{i}_del{j}_mm, E_2del{j}_p] = 2*E_del{i}_del{j}_mp
    for i, j in combinations(range(1, n + 1), 2):
        add(f"E_del{i}_del{j}_mm", f"E_2del{j}_p", f"E_del{i}_del{j}_mp", 2)
        add(f"E_2del{j}_p", f"E_del{i}_del{j}_mm", f"E_del{i}_del{j}_mp", -2)

    # [E_del{i}_del{j}_mp, E_2del{i}_p] = [b_i^-b_j^+, b_i^+^2]
    # = [b_i^-, b_i^+^2]b_j^+ = 2b_i^+ b_j^+ = 2*E_del{i}_del{j}_pp
    for i, j in combinations(range(1, n + 1), 2):
        add(f"E_del{i}_del{j}_mp", f"E_2del{i}_p", f"E_del{i}_del{j}_pp", 2)
        add(f"E_2del{i}_p", f"E_del{i}_del{j}_mp", f"E_del{i}_del{j}_pp", -2)

    # [E_del{i}_del{j}_pm, E_2del{i}_m] = [b_i^+b_j^-, b_i^-^2]
    # = [b_i^+, b_i^-^2]b_j^- = (-2b_i^-)b_j^- = -2*E_del{i}_del{j}_mm
    for i, j in combinations(range(1, n + 1), 2):
        add(f"E_del{i}_del{j}_pm", f"E_2del{i}_m", f"E_del{i}_del{j}_mm", -2)
        add(f"E_2del{i}_m", f"E_del{i}_del{j}_pm", f"E_del{i}_del{j}_mm", 2)

    # -----------------------------------------------------------------------
    # Even-even brackets involving three distinct bosonic indices
    # [E_del{i}_del{k}_pm, E_del{j}_del{k}_pp] = [b_i^+b_k^-, b_j^+b_k^+]
    # = b_i^+[b_k^-, b_j^+b_k^+] + [b_i^+, b_j^+b_k^+]b_k^-
    # [b_k^-, b_j^+b_k^+] = b_j^+[b_k^-, b_k^+] = b_j^+
    # [b_i^+, b_j^+b_k^+] = 0 (different indices)
    # = b_i^+ b_j^+ = E_del{i}_del{j}_pp (for i<j) or E_del{j}_del{i}_pp (j<i)
    for i, j, k in [(a, b, c) for a in range(1, n+1) for b in range(1, n+1) for c in range(1, n+1)
                    if a != b and a != c and b != c]:
        if i < j:
            z = f"E_del{i}_del{j}_pp"
        else:
            z = f"E_del{j}_del{i}_pp"
        # [E_del{i}_del{k}_pm, E_del{j}_del{k}_pp] = b_i^+b_j^+
        # But we need i<k for E_del{i}_del{k}_pm to be in basis
        if i < k and j < k:
            add(f"E_del{i}_del{k}_pm", f"E_del{j}_del{k}_pp", z, 1)

    # [E_del{i}_del{k}_mp, E_del{j}_del{k}_mm] = [b_i^-b_k^+, b_j^-b_k^-]
    # = b_i^-[b_k^+, b_j^-b_k^-] + [b_i^-, b_j^-b_k^-]b_k^+
    # [b_k^+, b_j^-b_k^-] = b_j^-[b_k^+,b_k^-] = -b_j^-
    # [b_i^-, b_j^-b_k^-] = 0
    # = b_i^-(-b_j^-) = -b_i^-b_j^-
    # = -E_del{i}_del{j}_mm (i<j) or -E_del{j}_del{i}_mm (j<i)
    for i, j, k in [(a, b, c) for a in range(1, n+1) for b in range(1, n+1) for c in range(1, n+1)
                    if a != b and a != c and b != c]:
        if i < j:
            z = f"E_del{i}_del{j}_mm"
        else:
            z = f"E_del{j}_del{i}_mm"
        if i < k and j < k:
            add(f"E_del{i}_del{k}_mp", f"E_del{j}_del{k}_mm", z, -1)

    # -----------------------------------------------------------------------
    # Even-odd brackets [H_k, E_odd] already covered above.
    # Even-odd: [E_2delk_p, E_eps1_delk_mm]
    # = [b_k^+^2, a1^-b_k^-]
    # = b_k^+[b_k^+, a1^-b_k^-] + [b_k^+, a1^-b_k^-]b_k^+
    # [b_k^+, a1^-b_k^-] = a1^-[b_k^+,b_k^-] = -a1^-
    # = b_k^+(-a1^-) + (-a1^-)b_k^+ = -2a1^-b_k^+ = -2*E_eps1_delk_mp
    for k in range(1, n + 1):
        add(f"E_2del{k}_p", f"E_eps1_del{k}_mm", f"E_eps1_del{k}_mp", -2)
        add(f"E_eps1_del{k}_mm", f"E_2del{k}_p", f"E_eps1_del{k}_mp", -2)  # graded: same parity sign

    # [E_2delk_m, E_eps1_delk_pp]
    # = [b_k^-^2, a1^+b_k^+]
    # b_k^-[b_k^-, a1^+b_k^+] + [b_k^-, a1^+b_k^+]b_k^-
    # [b_k^-, a1^+b_k^+] = a1^+[b_k^-,b_k^+] = a1^+
    # = b_k^- a1^+ + a1^+ b_k^- = 2*a1^+b_k^- = 2*E_eps1_delk_pm
    for k in range(1, n + 1):
        add(f"E_2del{k}_m", f"E_eps1_del{k}_pp", f"E_eps1_del{k}_pm", 2)
        add(f"E_eps1_del{k}_pp", f"E_2del{k}_m", f"E_eps1_del{k}_pm", 2)

    # [E_2delk_p, E_eps1_delk_mp] = [b_k^+^2, a1^-b_k^+]
    # = 2*b_k^+a1^- b_k^+ ??? let me redo
    # [b_k^+^2, a1^-b_k^+] = b_k^+[b_k^+, a1^-b_k^+] + [b_k^+, a1^-b_k^+]b_k^+
    # [b_k^+, a1^-b_k^+] = a1^-[b_k^+,b_k^+] = 0
    # = 0
    # So this bracket is 0.

    # [E_2delk_m, E_eps1_delk_pm] = [b_k^-^2, a1^+b_k^-]
    # [b_k^-, a1^+b_k^-] = a1^+[b_k^-,b_k^-] = 0
    # = 0

    # [E_del{i}_del{j}_pp, E_eps1_delk_mm] for various k
    # = [b_i^+b_j^+, a1^-b_k^-]
    # If k=i: [b_i^+b_j^+, a1^-b_i^-] = b_i^+[b_j^+,a1^-b_i^-] + [b_i^+,a1^-b_i^-]b_j^+
    #   [b_j^+, a1^-b_i^-] = 0 (j!=i)
    #   [b_i^+, a1^-b_i^-] = a1^-[b_i^+,b_i^-] = -a1^-
    #   = 0 + (-a1^-)b_j^+ = -a1^-b_j^+ = -E_eps1_delj_mp
    # If k=j: similarly = -E_eps1_deli_mp
    # If k!=i and k!=j: = 0
    for i, j in combinations(range(1, n + 1), 2):
        # k=i
        add(f"E_del{i}_del{j}_pp", f"E_eps1_del{i}_mm", f"E_eps1_del{j}_mp", -1)
        add(f"E_eps1_del{i}_mm", f"E_del{i}_del{j}_pp", f"E_eps1_del{j}_mp", -1)
        # k=j
        add(f"E_del{i}_del{j}_pp", f"E_eps1_del{j}_mm", f"E_eps1_del{i}_mp", -1)
        add(f"E_eps1_del{j}_mm", f"E_del{i}_del{j}_pp", f"E_eps1_del{i}_mp", -1)

    # [E_del{i}_del{j}_mm, E_eps1_delk_pp] for k=i or k=j
    # = [b_i^-b_j^-, a1^+b_k^+]
    # k=i: [b_i^-b_j^-, a1^+b_i^+] = b_i^-[b_j^-,a1^+b_i^+] + [b_i^-,a1^+b_i^+]b_j^-
    #   = 0 + a1^+b_j^- = a1^+b_j^- = E_eps1_delj_pm
    for i, j in combinations(range(1, n + 1), 2):
        add(f"E_del{i}_del{j}_mm", f"E_eps1_del{i}_pp", f"E_eps1_del{j}_pm", 1)
        add(f"E_eps1_del{i}_pp", f"E_del{i}_del{j}_mm", f"E_eps1_del{j}_pm", 1)
        add(f"E_del{i}_del{j}_mm", f"E_eps1_del{j}_pp", f"E_eps1_del{i}_pm", 1)
        add(f"E_eps1_del{j}_pp", f"E_del{i}_del{j}_mm", f"E_eps1_del{i}_pm", 1)

    # [E_del{i}_del{j}_pm, E_eps1_delk_pp] for k=j
    # = [b_i^+b_j^-, a1^+b_j^+]
    # = b_i^+[b_j^-, a1^+b_j^+] + [b_i^+, a1^+b_j^+]b_j^-
    # [b_j^-, a1^+b_j^+] = a1^+[b_j^-,b_j^+] = a1^+
    # [b_i^+, a1^+b_j^+] = 0 (i!=j)
    # = b_i^+ a1^+ = a1^+ b_i^+ = E_eps1_deli_pp
    for i, j in combinations(range(1, n + 1), 2):
        # E_del{i}_del{j}_pm: k=j
        add(f"E_del{i}_del{j}_pm", f"E_eps1_del{j}_pp", f"E_eps1_del{i}_pp", 1)
        add(f"E_eps1_del{j}_pp", f"E_del{i}_del{j}_pm", f"E_eps1_del{i}_pp", 1)
        # E_del{i}_del{j}_pm: k=i -> [b_i^+b_j^-, a1^+b_i^+]
        # = b_i^+[b_j^-,a1^+b_i^+]+[b_i^+,a1^+b_i^+]b_j^-
        # [b_j^-,a1^+b_i^+]=0, [b_i^+,a1^+b_i^+]=0
        # = 0

    # [E_del{i}_del{j}_pm, E_eps1_delk_mm] for k=i
    # = [b_i^+b_j^-, a1^-b_i^-]
    # = b_i^+[b_j^-,a1^-b_i^-]+[b_i^+,a1^-b_i^-]b_j^-
    # [b_j^-,a1^-b_i^-]=0, [b_i^+,a1^-b_i^-]=a1^-[b_i^+,b_i^-]=-a1^-
    # = -a1^-b_j^- = -E_eps1_delj_mm
    for i, j in combinations(range(1, n + 1), 2):
        add(f"E_del{i}_del{j}_pm", f"E_eps1_del{i}_mm", f"E_eps1_del{j}_mm", -1)
        add(f"E_eps1_del{i}_mm", f"E_del{i}_del{j}_pm", f"E_eps1_del{j}_mm", -1)
        # k=j: [b_i^+b_j^-, a1^-b_j^-]
        # [b_j^-, a1^-b_j^-] = a1^-[b_j^-,b_j^-] = 0, [b_i^+,a1^-b_j^-] = 0 (i!=j)
        # = 0

    # [E_del{i}_del{j}_mp, E_eps1_delk_pp] for k=i
    # = [b_i^-b_j^+, a1^+b_i^+]
    # [b_i^-, a1^+b_i^+]b_j^+ + b_i^-[b_j^+,a1^+b_i^+]
    # [b_i^-, a1^+b_i^+] = a1^+[b_i^-,b_i^+] = a1^+
    # = a1^+b_j^+ = E_eps1_delj_pp
    for i, j in combinations(range(1, n + 1), 2):
        add(f"E_del{i}_del{j}_mp", f"E_eps1_del{i}_pp", f"E_eps1_del{j}_pp", 1)
        add(f"E_eps1_del{i}_pp", f"E_del{i}_del{j}_mp", f"E_eps1_del{j}_pp", 1)
        # k=j: [b_i^-b_j^+, a1^+b_j^+]
        # b_i^-[b_j^+,a1^+b_j^+]+[b_i^-,a1^+b_j^+]b_j^+
        # [b_j^+,a1^+b_j^+]=0, [b_i^-,a1^+b_j^+]=0
        # = 0

    # [E_del{i}_del{j}_mp, E_eps1_delk_mm] for k=j
    # = [b_i^-b_j^+, a1^-b_j^-]
    # b_i^-[b_j^+,a1^-b_j^-]+[b_i^-,a1^-b_j^-]b_j^+
    # [b_j^+,a1^-b_j^-] = a1^-[b_j^+,b_j^-] = -a1^-
    # = b_i^-(-a1^-) = -a1^-b_i^- = -E_eps1_deli_mm
    for i, j in combinations(range(1, n + 1), 2):
        add(f"E_del{i}_del{j}_mp", f"E_eps1_del{j}_mm", f"E_eps1_del{i}_mm", -1)
        add(f"E_eps1_del{j}_mm", f"E_del{i}_del{j}_mp", f"E_eps1_del{i}_mm", -1)

    # -----------------------------------------------------------------------
    # Remove duplicates (same X,Y,Z triple)
    # -----------------------------------------------------------------------
    seen = {}
    for entry in sc:
        key = (entry["X"], entry["Y"], entry["Z"])
        if key in seen:
            existing = Fraction(seen[key]["coeff"])
            new_c = Fraction(entry["coeff"])
            total = existing + new_c
            if total == 0:
                del seen[key]
            else:
                seen[key]["coeff"] = str(total)
        else:
            seen[key] = dict(entry)

    return list(seen.values())


def build_schema1(n: int) -> dict:
    even_basis, odd_basis = get_basis(n)
    parity = get_parity(even_basis, odd_basis)
    sc = compute_structure_constants(n)
    realization = generator_realization(n)

    even_dim = 2 * n * n + n + 1
    odd_dim = 4 * n
    total_dim = even_dim + odd_dim

    boson_labels = []
    for k in range(1, n + 1):
        boson_labels += [f"b_{k}_p", f"b_{k}_m"]

    fermion_labels_count = 2
    total_osc = fermion_labels_count + 2 * n

    return {
        "schema_version": "5.0",
        "algebra": {
            "family": "C",
            "m": 1,
            "n": n,
            "cartan_type": f"C({n+1})",
            "alternative_notation": {
                "osp": f"osp(2|{2*n})",
                "dimension_formula": "osp(2m|2n) with m=1",
            },
            "dimension": {
                "total": total_dim,
                "even": even_dim,
                "odd": odd_dim,
            },
        },
        "central_elements": {
            "kappa": {
                "label": "kappa",
                "parity": 1,
                "description": "Odd nilpotent central element; kappa^2 = 0.",
            },
            "K": {
                "label": "K",
                "parity": 0,
                "description": "Even central element, identified with scalar 1 in current applications.",
            },
        },
        "oscillator_generators": {
            "fermions": {
                "m": 1,
                "labels": ["a_1_p", "a_1_m"],
                "parity": 1,
                "description": "Standard fermionic pair a_1^+, a_1^- with CAR.",
            },
            "bosons": {
                "count": 2 * n,
                "n": n,
                "labels": boson_labels,
                "description": f"Bosonic oscillators b_k^± with k=1,...,{n}",
            },
        },
        "oscillator_relations": {
            "standard_fermion_anticommutators": {
                "description": "CAR for standard fermionic pair",
                "relations": {
                    "same_type": "{a_1^+, a_1^+} = 0, {a_1^-, a_1^-} = 0",
                    "conjugate_pair": "{a_1^-, a_1^+} = 1",
                },
            },
            "bosonic_commutators": {
                "description": "CCR for bosonic oscillators",
                "relations": {
                    "same_type": "[b_i^pm, b_j^pm] = 0 for all i,j",
                    "conjugate_pair": "[b_i^-, b_j^+] = delta_{ij}",
                },
            },
            "mixed_commutators": {"fermion_boson": "[b_i^pm, a_1^pm] = 0 (undeformed)"},
        },
        "basis": {
            "even": even_basis,
            "odd": odd_basis,
            "ordering_convention": "PBW: kappa < [odd] < [even]  (K=1 excluded)",
        },
        "parity": parity,
        "generator_realization": {
            "description": "Standard PBW form with oscillator ordering a_1_p, a_1_m, b_1_p, b_1_m, ...",
            "ordering": ["a_1_p", "a_1_m"] + boson_labels,
            "realizations": realization,
        },
        "structure_constants": sc,
        "metadata": {
            "generated_by": "src/C_generators.py",
            "generation_date": str(date.today()),
            "references": [
                "Frappat, Sciarrino, Sorba (2000), Dictionary on Lie Algebras and Superalgebras",
                "Bakalov and Sullivan (2017)",
            ],
        },
    }


def main():
    os.makedirs("data", exist_ok=True)
    for n in [1, 2, 3]:
        schema = build_schema1(n)
        fname = f"data/C_{n}_structure.json"
        with open(fname, "w") as f:
            json.dump(schema, f, indent=2)
        sc_count = len(schema["structure_constants"])
        print(f"C_{n}_structure.json written. dim={schema['algebra']['dimension']}, sc={sc_count}")


if __name__ == "__main__":
    main()
