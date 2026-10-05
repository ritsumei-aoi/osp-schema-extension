"""
C(n+1) = osp(2|2n) gamma structure (Schema 2) generator.

Computes gamma coefficients γ(X,Y) for the inhomogeneous deformation
    [bj^s, a1^σ] = −gb_{σ,j,s}·κ   (Option A sign convention)

producing Schema 2 JSON files C_{n}_gamma.json for n=1, 2, 3.

γ(X,Y) is linear in gb parameters and valued in C(n+1). It is defined via:
    [X,Y]_γ = [X,Y]_0 + κ·γ(X,Y)

Only γ(X,Y) for X ≤ Y in PBW basis order is recorded (upper-triangle,
use graded anti-symmetry for the rest).

Oscillator index convention (same as build_C_structure_constants.py):
  0         : a1+  (fermionic creation, parity 1)
  1..n      : b1+..bn+  (bosonic creation, parity 0)
  n+1       : a1-  (fermionic annihilation, parity 1)
  n+2..2n+1 : b1-..bn-  (bosonic annihilation, parity 0)

Kappa-contraction table (from [bj^s, a1^σ] = -gb_{σ,j,s}·κ):
  Case 1: bj^+ (idx j) moves past a1^+ (idx 0): contraction = -gb_pp_j
  Case 2: bj^- (idx n+1+j) moves past a1^+ (idx 0): contraction = -gb_pm_j
  Case 3: a1^- (idx n+1) moves past bj^+ (idx j): contraction = +gb_mp_j
  Case 4: bj^- (idx n+1+j) moves past a1^- (idx n+1): contraction = -gb_mm_j
"""

from fractions import Fraction
from collections import defaultdict
import json
from datetime import date
import os
import sys

# Add parent src directory to path so we can import shared helpers
sys.path.insert(0, os.path.dirname(__file__))
from build_C_structure_constants import (
    osc_parity, contraction, normal_order_seq,
    build_basis, build_generators, label_parity, decompose,
    op_add, op_scale,
)


# ---------------------------------------------------------------------------
# Kappa-contraction table (deformation, first-order in gb)
# ---------------------------------------------------------------------------

def kappa_contraction(a, b, n):
    """
    Return (gb_label, sign: int) for the κ-valued contraction when moving
    oscillator at index a past oscillator at index b (a > b).
    Returns None if no κ-contraction exists.

    The actual contraction value is sign × gb_label (linear in gb).
    """
    # Case 1: bj^+ (1≤j≤n, idx=j) past a1^+ (idx=0) → −gb_pp_j
    if 1 <= a <= n and b == 0:
        return (f"gb_pp_{a}", -1)
    # Case 2: bj^- (1≤j≤n, idx=n+1+j) past a1^+ (idx=0) → −gb_pm_j
    if n + 2 <= a <= 2 * n + 1 and b == 0:
        j = a - (n + 1)
        return (f"gb_pm_{j}", -1)
    # Case 3: a1^- (idx=n+1) past bj^+ (1≤j≤n, idx=j) → +gb_mp_j
    if a == n + 1 and 1 <= b <= n:
        return (f"gb_mp_{b}", +1)
    # Case 4: bj^- (1≤j≤n, idx=n+1+j) past a1^- (idx=n+1) → −gb_mm_j
    if n + 2 <= a <= 2 * n + 1 and b == n + 1:
        j = a - (n + 1)
        return (f"gb_mm_{j}", -1)
    return None


# ---------------------------------------------------------------------------
# Dual normal ordering: tracks ordinary AND kappa terms (first order in gb)
# ---------------------------------------------------------------------------

def normal_order_seq_dual(seq, n, coeff, ordinary_result, kappa_result):
    """
    Recursively bring seq to normal order, collecting:
      ordinary_result: dict {monomial: Fraction}   — the g-part (Schema 1)
      kappa_result:    dict {(gb_label, monomial): Fraction} — the κ·g-part

    Kappa-contracted residuals are further reduced using ordinary normal_order_seq
    (second-order gb terms dropped — first-order computation only).
    """
    for i in range(len(seq) - 1):
        a, b = seq[i], seq[i + 1]
        if a > b:
            pa = osc_parity(a, n)
            pb = osc_parity(b, n)
            grade_sign = Fraction((-1) ** (pa * pb))

            swapped = seq[:i] + [b, a] + seq[i + 2:]

            # Swapped term — ordinary recursion (also propagates kappa)
            normal_order_seq_dual(swapped, n, coeff * grade_sign,
                                  ordinary_result, kappa_result)

            # Standard (non-κ) contraction term
            c = contraction(a, b, n)
            if c != Fraction(0):
                contracted = seq[:i] + seq[i + 2:]
                normal_order_seq_dual(contracted, n, coeff * c,
                                      ordinary_result, kappa_result)

            # Kappa contraction term — first-order only
            kc = kappa_contraction(a, b, n)
            if kc is not None:
                gb_label, sign = kc
                contracted = seq[:i] + seq[i + 2:]
                # Ordinary-normalize the residual (drops second-order κ terms)
                mono_result = {}
                normal_order_seq(contracted, n, coeff * Fraction(sign), mono_result)
                for mono, c_val in mono_result.items():
                    key = (gb_label, mono)
                    kappa_result[key] = (
                        kappa_result.get(key, Fraction(0)) + c_val
                    )
            return

    # Already in normal order — apply fermionic nilpotency
    if seq.count(0) > 1 or seq.count(n + 1) > 1:
        return
    key = tuple(seq)
    ordinary_result[key] = ordinary_result.get(key, Fraction(0)) + coeff


def op_mul_dual(op1, op2, n):
    """
    Multiply two operators (each a dict {monomial: Fraction}), tracking
    both ordinary and kappa terms.

    Returns (ordinary: dict, kappa: dict {(gb_label, monomial): Fraction}).
    """
    ordinary_result = {}
    kappa_result = {}
    for m1, c1 in op1.items():
        for m2, c2 in op2.items():
            combined = list(m1) + list(m2)
            normal_order_seq_dual(combined, n, c1 * c2,
                                  ordinary_result, kappa_result)
    ordinary = {m: c for m, c in ordinary_result.items() if c != 0}
    kappa = {k: c for k, c in kappa_result.items() if c != 0}
    return ordinary, kappa


def graded_bracket_gamma(X, Xp, Y, Yp, n):
    """
    Compute [X,Y} = XY − (−1)^{Xp·Yp} YX, returning (ordinary, kappa) dicts.
    """
    sign = Fraction((-1) ** (Xp * Yp))
    XY_ord, XY_kap = op_mul_dual(X, Y, n)
    YX_ord, YX_kap = op_mul_dual(Y, X, n)

    ordinary = op_add(XY_ord, op_scale(YX_ord, -sign))

    kappa = {}
    for k, c in XY_kap.items():
        kappa[k] = kappa.get(k, Fraction(0)) + c
    for k, c in YX_kap.items():
        kappa[k] = kappa.get(k, Fraction(0)) - sign * c
    kappa = {k: c for k, c in kappa.items() if c != 0}

    return ordinary, kappa


# ---------------------------------------------------------------------------
# Robust decomposition (handles K scalar term)
# ---------------------------------------------------------------------------

def decompose_gamma(op, n, basis_labels, gen_ops):
    """
    Decompose operator op (dict {monomial: Fraction}) into basis generators.
    Returns dict {label: Fraction}, where label is a basis generator name
    or "K" for the scalar (identity K=1) component.

    Algorithm: resolve Cartans from degree-2 monomials first (chain H_1..H_{n+1}),
    then compute the K (scalar) residual from the () monomial.

    Cartan contributions to degree-2 monomials:
      H_1 = a1+a1- + b1+b1-      → (0,n+1): +1, (1,n+2): +1
      H_k (2≤k≤n) = b{k-1}+b{k-1}- - bk+bk-
                                   → (k-1,n+k): +1, (k,n+k+1): -1
      H_{n+1} = -bn+bn- - 1/2    → (n,2n+1): -1, (): -1/2

    Extraction order:
      1. H_1 from monomial (0, n+1)   [unique to H_1]
      2. H_k (k=2..n) from chain (k-1, n+k):
            k=2: c_H2 = val_(1,n+2) - c_H1   [H_1+H_2 both contribute +1]
            k≥3: c_Hk = val_(k-1,n+k) + c_{k-1}  [H_{k-1} -1, H_k +1]
      3. H_{n+1} from monomial (n, 2n+1):
            n=1: c_H2 = c_H1 - C_last  [H_1 +1, H_2 -1]
            n≥2: c_{H_{n+1}} = -C_last - c_Hn  [H_n -1, H_{n+1} -1]
      4. K from scalar (): c_K = val_() - c_{H_{n+1}}×(-1/2) = val_() + c_{H_{n+1}}/2
    """
    coeffs = {}
    remaining = dict(op)

    # Non-Cartan even generators (unique monomials)
    for k in range(1, n + 1):
        m_p = (k, k)
        if m_p in remaining:
            c = remaining.pop(m_p) / Fraction(1, 2)
            if c != 0:
                coeffs[f"E_2del{k}_p"] = c

        m_m = (n + 1 + k, n + 1 + k)
        if m_m in remaining:
            c = remaining.pop(m_m) / Fraction(1, 2)
            if c != 0:
                coeffs[f"E_2del{k}_m"] = c

    for i in range(1, n + 1):
        for j in range(i + 1, n + 1):
            for suffix, mono in [
                ("pp", (i, j)),
                ("mm", (n + 1 + i, n + 1 + j)),
                ("pm", (i, n + 1 + j)),
                ("mp", (j, n + 1 + i)),
            ]:
                if mono in remaining:
                    c = remaining.pop(mono)
                    if c != 0:
                        coeffs[f"E_del{i}_del{j}_{suffix}"] = c

    # Odd generators (unique monomials)
    for k in range(1, n + 1):
        for suffix, mono in [
            ("pp", (0, k)),
            ("pm", (0, n + 1 + k)),
            ("mp", (k, n + 1)),
            ("mm", (n + 1, n + 1 + k)),
        ]:
            if mono in remaining:
                c = remaining.pop(mono)
                if c != 0:
                    coeffs[f"E_eps1_del{k}_{suffix}"] = c

    # ---------------------------------------------------------------
    # Cartan generators: resolve from degree-2 monomials first
    # ---------------------------------------------------------------

    # Step 1: H_1 from (0, n+1) = a1+a1-  [unique to H_1]
    c_H1 = remaining.pop((0, n + 1), Fraction(0))
    if c_H1 != 0:
        coeffs["H_1"] = c_H1
    c_prev = c_H1

    # Step 2: H_k (k=2..n) from the (k-1, n+k) chain
    for k in range(2, n + 1):
        mono = (k - 1, n + k)
        C_val = remaining.pop(mono, Fraction(0))
        if k == 2:
            # H_1 contributes +1 and H_2 contributes +1 to (1, n+2)
            c_k = C_val - c_prev
        else:
            # H_{k-1} contributes -1 and H_k contributes +1 to (k-1, n+k)
            c_k = C_val + c_prev
        if c_k != 0:
            coeffs[f"H_{k}"] = c_k
        c_prev = c_k  # c_prev = c_{H_k} after this step

    # Step 3: H_{n+1} from monomial (n, 2n+1)
    mono_last = (n, 2 * n + 1)
    C_last = remaining.pop(mono_last, Fraction(0))
    if n == 1:
        # For n=1: H_1 contributes +1 and H_2=H_{n+1} contributes -1 to (1,3)
        # c_H1*(+1) + c_H2*(-1) = C_last  →  c_H2 = c_H1 - C_last
        c_H_np1 = c_H1 - C_last
    else:
        # For n≥2: H_n contributes -1 and H_{n+1} contributes -1 to (n, 2n+1)
        # c_Hn*(-1) + c_{H_{n+1}}*(-1) = C_last  →  c_{H_{n+1}} = -C_last - c_Hn
        c_H_np1 = -C_last - c_prev   # c_prev = c_Hn here
    if c_H_np1 != 0:
        coeffs[f"H_{n+1}"] = c_H_np1

    # Step 4: K from scalar ()
    # H_{n+1} contributes -1/2 to (); K contributes +1
    # c_{H_{n+1}}*(-1/2) + c_K*(1) = val_()  →  c_K = val_() + c_{H_{n+1}}/2
    scalar = remaining.pop((), Fraction(0))
    c_K = scalar + c_H_np1 * Fraction(1, 2)
    if c_K != 0:
        coeffs["K"] = c_K

    # Sanity check: all monomials accounted for
    if remaining:
        raise ValueError(
            f"decompose_gamma: unaccounted monomials {remaining}\n"
            f"  operator: {op}"
        )

    return {lbl: c for lbl, c in coeffs.items() if c != 0}


# ---------------------------------------------------------------------------
# Gamma coefficient computation
# ---------------------------------------------------------------------------

def compute_gamma_coefficients(n):
    """
    Return list of non-zero gamma records for C(n+1).

    Each record: {X, Y, gb_key, Z, coeff}
    meaning γ(X,Y) ∋ coeff * gb_key * Z  (X ≤ Y in PBW order).
    """
    odd_labels, even_labels = build_basis(n)
    all_labels = odd_labels + even_labels
    gen_ops = build_generators(n)
    basis_labels = odd_labels + even_labels

    records = []

    for i, X_label in enumerate(all_labels):
        Xp = label_parity(X_label)
        X_op = gen_ops[X_label]
        for j in range(i, len(all_labels)):
            Y_label = all_labels[j]
            Yp = label_parity(Y_label)
            Y_op = gen_ops[Y_label]

            _, kappa = graded_bracket_gamma(X_op, Xp, Y_op, Yp, n)
            if not kappa:
                continue

            # Group by gb_label, then decompose each group
            gb_groups = defaultdict(dict)
            for (gb_label, mono), c in kappa.items():
                gb_groups[gb_label][mono] = (
                    gb_groups[gb_label].get(mono, Fraction(0)) + c
                )

            for gb_label, op in gb_groups.items():
                op = {m: c for m, c in op.items() if c != 0}
                if not op:
                    continue

                Z_coeffs = decompose_gamma(op, n, basis_labels, gen_ops)

                for Z_label, coeff in Z_coeffs.items():
                    if coeff != 0:
                        records.append({
                            "X": X_label,
                            "Y": Y_label,
                            "gb_key": gb_label,
                            "Z": Z_label,
                            "coeff": str(coeff),
                        })

    return records


# ---------------------------------------------------------------------------
# Schema 2 JSON builder
# ---------------------------------------------------------------------------

def build_gb_parameter_list(n):
    params = []
    for j in range(1, n + 1):
        for sigma, s, suffix in [
            ("+", "+", f"pp_{j}"),
            ("+", "-", f"pm_{j}"),
            ("-", "+", f"mp_{j}"),
            ("-", "-", f"mm_{j}"),
        ]:
            params.append({
                "label": f"gb_{suffix}",
                "sigma": sigma,
                "j": j,
                "s": s,
            })
    return params


def build_schema2(n):
    gamma_records = compute_gamma_coefficients(n)

    total = 2 * n * n + 5 * n + 1
    n_even = 2 * n * n + n + 1
    n_odd = 4 * n

    schema = {
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
                "total": total,
                "even": n_even,
                "odd": n_odd,
            },
        },
        "inhomogeneous_deformation": {
            "deformation_type": "gb",
            "sign_convention": "Option_A",
            "defining_relation": "[bj^s, a1^sigma] = -gb_{sigma,j,s} * kappa",
            "gb_matrix": {
                "description": (
                    "Deformation parameters gb_{sigma,j,s}: "
                    "sigma in {+,-} (fermionic oscillator sign), "
                    "j in 1..n (bosonic mode), "
                    "s in {+,-} (bosonic oscillator sign). "
                    "Label convention: gb_{sigma_suffix}{s_suffix}_{j}, "
                    "where p=+, m=-."
                ),
                "size": [2, 2 * n],
                "parameters": build_gb_parameter_list(n),
            },
            "gamma_description": (
                "γ(X,Y) = Σ_{gb_key, Z} coeff · gb_key · Z. "
                "Records stored for X ≤ Y in PBW order only. "
                "Graded anti-symmetry: γ(Y,X) = -(-1)^{p(X)p(Y)} γ(X,Y)."
            ),
            "gamma_coefficients": gamma_records,
        },
        "metadata": {
            "generated_by": "build_C_gamma.py",
            "generation_date": str(date.today()),
            "references": [
                "Frappat et al. (2000), Dictionary on Lie Algebras and Superalgebras",
                "C_inhomogeneous_definition.md",
            ],
        },
    }
    return schema


# ---------------------------------------------------------------------------
# Consistency check against Schema 1
# ---------------------------------------------------------------------------

def verify_gamma_parity(schema2, n):
    """
    Parity check: γ(X,Y) must have parity p(X)+p(Y)+1 mod 2.
    Even-Even brackets must have zero gamma.
    """
    odd_labels, even_labels = build_basis(n)
    parity = {lbl: 1 for lbl in odd_labels}
    parity.update({lbl: 0 for lbl in even_labels})

    errors = []
    for rec in schema2["inhomogeneous_deformation"]["gamma_coefficients"]:
        X, Y, Z = rec["X"], rec["Y"], rec["Z"]
        if Z == "K":
            continue  # K is even; parity check handled separately
        pX = parity.get(X, None)
        pY = parity.get(Y, None)
        pZ = parity.get(Z, None)
        if None in (pX, pY, pZ):
            errors.append(f"Unknown label in record {rec}")
            continue
        expected_pZ = (pX + pY + 1) % 2
        if pZ != expected_pZ:
            errors.append(
                f"Parity mismatch: γ({X},{Y})→{Z}: "
                f"expected parity {expected_pZ}, got {pZ}"
            )
    return errors


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    data_dir = os.path.join(os.path.dirname(__file__), "..", "data")
    os.makedirs(data_dir, exist_ok=True)

    for n in [1, 2, 3]:
        print(f"\n=== C({n+1}) = osp(2|{2*n}), n={n} ===")
        schema = build_schema2(n)
        gc = schema["inhomogeneous_deformation"]["gamma_coefficients"]
        gb_params = schema["inhomogeneous_deformation"]["gb_matrix"]["parameters"]

        print(f"  gb parameters: {len(gb_params)}")
        print(f"  Non-zero γ records: {len(gc)}")

        # Parity consistency check
        errors = verify_gamma_parity(schema, n)
        if errors:
            print(f"  PARITY ERRORS ({len(errors)}):")
            for e in errors:
                print(f"    {e}")
        else:
            print("  Parity check: PASSED")

        # K-term check
        k_terms = [r for r in gc if r["Z"] == "K"]
        if k_terms:
            print(f"  WARNING: {len(k_terms)} K (scalar) terms found:")
            for r in k_terms:
                print(f"    {r}")
        else:
            print("  K-term check: none (clean)")

        fname = os.path.join(data_dir, f"C_{n}_gamma.json")
        with open(fname, "w") as f:
            json.dump(schema, f, indent=2)
        print(f"  Written: {fname}")
