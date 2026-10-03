"""
C_generators.py — Structure constant generator for C(n+1) = osp(2|2n).

Computes Schema 1 JSON for bosonic rank n=1, 2, 3.
"""

from fractions import Fraction
import json
import os
from datetime import date


# ---------------------------------------------------------------------------
# Basis construction
# ---------------------------------------------------------------------------

def build_basis(n):
    odd = []
    for k in range(1, n + 1):
        odd += [f"E_eps1_del{k}_pp", f"E_eps1_del{k}_pm",
                f"E_eps1_del{k}_mp", f"E_eps1_del{k}_mm"]

    even = [f"H_{k}" for k in range(1, n + 2)]
    for k in range(1, n + 1):
        even += [f"E_2del{k}_p", f"E_2del{k}_m"]
    for i in range(1, n + 1):
        for j in range(i + 1, n + 1):
            even += [f"E_del{i}_del{j}_pp", f"E_del{i}_del{j}_mm",
                     f"E_del{i}_del{j}_pm", f"E_del{i}_del{j}_mp"]
    return odd, even


def build_parity(odd, even):
    parity = {g: 1 for g in odd}
    parity.update({g: 0 for g in even})
    return parity


# ---------------------------------------------------------------------------
# Oscillator algebra: polynomials in a1p, a1m, b1p, b1m, ...
#
# We represent algebra elements as dict: frozenset_multiset -> Fraction
# where keys are sorted tuples (normal-ordered monomials).
# Normal order: a1p < a1m < b1p < b1m < b2p < b2m < ...
#
# Relations:
#   a1p * a1p = 0       (fermion)
#   a1m * a1m = 0       (fermion)
#   a1m * a1p = 1 - a1p * a1m    ({a1m,a1p}=1)
#   bkm * bkp = 1 + bkp * bkm   ([bkm,bkp]=1, so bkm*bkp - bkp*bkm = 1)
#   [bip, bjm] = delta_{ij} → bim*bjp = delta_{ij} + bjp*bim
#   All other pairs commute.
# ---------------------------------------------------------------------------

def osc_order(n):
    """Return list of oscillator labels in PBW order."""
    return ["a1p", "a1m"] + [f"b{k}{s}" for k in range(1, n + 1) for s in ["p", "m"]]


def osc_par(label):
    return 1 if label.startswith("a") else 0


def _multiply_monomial(m1, m2, order_idx):
    """
    Multiply two normal-ordered monomials (tuples).
    Returns dict: tuple -> Fraction of normal-ordered terms.
    Uses insertion sort to bubble m2 elements into m1, applying CAR/CCR.
    """
    # Start with the concatenation, then normal-order via bubble sort
    return _normal_order(m1 + m2, order_idx)


def _is_zero_monomial(m):
    """Return True if monomial is zero: any fermion letter appears twice."""
    seen = set()
    for label in m:
        if osc_par(label) == 1:
            if label in seen:
                return True
            seen.add(label)
    return False


def _normal_order(mon, order_idx):
    """
    Reduce a monomial tuple to normal order using CAR/CCR.
    Returns dict: tuple -> Fraction.
    """
    results = {tuple(mon): Fraction(1)}

    changed = True
    while changed:
        changed = False
        new_results = {}
        for m, coeff in results.items():
            # Check if this monomial is zero (fermion squared)
            if _is_zero_monomial(m):
                changed = True
                continue  # term vanishes

            m = list(m)
            swapped = False
            for i in range(len(m) - 1):
                a, b = m[i], m[i + 1]
                ia, ib = order_idx[a], order_idx[b]
                if ia > ib:
                    pa, pb = osc_par(a), osc_par(b)
                    sign = (-1) ** (pa * pb)

                    # Remainder from CAR/CCR
                    remainder = None
                    if pa == 0 and pb == 0:
                        # bosons: CCR [b_k^-, b_k^+] = 1
                        # a is "later" in order (higher idx), b is "earlier"
                        # Case: a = bkm, b = bkp (same k) → bkm*bkp = 1 + bkp*bkm
                        if (a.endswith("m") and b.endswith("p") and
                                a[:-1] == b[:-1]):
                            remainder = tuple(m[:i] + m[i + 2:])
                    elif pa == 1 and pb == 1:
                        # fermions: {a1m, a1p} = 1
                        if a == "a1m" and b == "a1p":
                            remainder = tuple(m[:i] + m[i + 2:])

                    swapped_m = tuple(m[:i] + [b, a] + m[i + 2:])
                    new_results[swapped_m] = new_results.get(swapped_m, Fraction(0)) + coeff * sign
                    if remainder is not None:
                        new_results[remainder] = new_results.get(remainder, Fraction(0)) + coeff

                    swapped = True
                    changed = True
                    break

            if not swapped:
                t = tuple(m)
                new_results[t] = new_results.get(t, Fraction(0)) + coeff

        results = {k: v for k, v in new_results.items() if v != 0}

    return results


def multiply_elements(d1, d2, order_idx):
    """Multiply two algebra elements (dict: tuple->Fraction)."""
    result = {}
    for m1, c1 in d1.items():
        for m2, c2 in d2.items():
            prod = _multiply_monomial(m1, m2, order_idx)
            for m, c in prod.items():
                result[m] = result.get(m, Fraction(0)) + c1 * c2 * c
    return {k: v for k, v in result.items() if v != 0}


def graded_bracket(X, Y, pX, pY, order_idx):
    """[X,Y} = XY - (-1)^{pX*pY} YX."""
    XY = multiply_elements(X, Y, order_idx)
    YX = multiply_elements(Y, X, order_idx)
    sign = (-1) ** (pX * pY)
    result = dict(XY)
    for m, c in YX.items():
        result[m] = result.get(m, Fraction(0)) - sign * c
    return {k: v for k, v in result.items() if v != 0}


# ---------------------------------------------------------------------------
# Generator realizations
# ---------------------------------------------------------------------------

def gen_realization(n):
    real = {}
    # H_1 = a1p*a1m + b1p*b1m
    real["H_1"] = {("a1p", "a1m"): Fraction(1), ("b1p", "b1m"): Fraction(1)}
    for k in range(2, n + 1):
        real[f"H_{k}"] = {(f"b{k-1}p", f"b{k-1}m"): Fraction(1),
                          (f"b{k}p", f"b{k}m"): Fraction(-1)}
    real[f"H_{n+1}"] = {(f"b{n}p", f"b{n}m"): Fraction(-1), (): Fraction(-1, 2)}

    for k in range(1, n + 1):
        real[f"E_eps1_del{k}_pp"] = {("a1p", f"b{k}p"): Fraction(1)}
        real[f"E_eps1_del{k}_pm"] = {("a1p", f"b{k}m"): Fraction(1)}
        real[f"E_eps1_del{k}_mp"] = {("a1m", f"b{k}p"): Fraction(1)}
        real[f"E_eps1_del{k}_mm"] = {("a1m", f"b{k}m"): Fraction(1)}

    for k in range(1, n + 1):
        real[f"E_2del{k}_p"] = {(f"b{k}p", f"b{k}p"): Fraction(1)}
        real[f"E_2del{k}_m"] = {(f"b{k}m", f"b{k}m"): Fraction(1)}
    for i in range(1, n + 1):
        for j in range(i + 1, n + 1):
            real[f"E_del{i}_del{j}_pp"] = {(f"b{i}p", f"b{j}p"): Fraction(1)}
            real[f"E_del{i}_del{j}_mm"] = {(f"b{i}m", f"b{j}m"): Fraction(1)}
            real[f"E_del{i}_del{j}_pm"] = {(f"b{i}p", f"b{j}m"): Fraction(1)}
            real[f"E_del{i}_del{j}_mp"] = {(f"b{i}m", f"b{j}p"): Fraction(1)}
    return real


# ---------------------------------------------------------------------------
# Decompose bracket result in basis
# ---------------------------------------------------------------------------

def decompose_in_basis(element, realization, basis_all):
    """
    Express element as linear combination of basis generators.
    Scalar () remainder maps to K. Generators with scalar terms in their
    realization (like H_{n+1}) are handled by matching non-scalar pivots first.
    Returns dict: label -> Fraction (may include 'K' for scalar part).
    """
    coeffs = {}
    remaining = dict(element)

    # Iterative greedy matching: prefer non-scalar pivots in generators
    for _ in range(len(basis_all) + 1):  # at most |basis| passes
        for g in basis_all:
            g_real = realization[g]
            # Find the first non-scalar pivot
            pivot = None
            pivot_coeff = None
            for m, c in g_real.items():
                if m != () and m in remaining and remaining[m] != 0:
                    pivot = m
                    pivot_coeff = c
                    break
            if pivot is None:
                continue
            c = remaining[pivot] / pivot_coeff
            if c == 0:
                continue
            coeffs[g] = coeffs.get(g, Fraction(0)) + c
            for m, v in g_real.items():
                remaining[m] = remaining.get(m, Fraction(0)) - c * v
        remaining = {k: v for k, v in remaining.items() if v != 0}
        if not remaining or remaining.keys() == {()}:
            break

    # Any remaining scalar is the K component
    if () in remaining:
        coeffs["K"] = remaining.pop(())

    remaining = {k: v for k, v in remaining.items() if v != 0}
    if remaining:
        raise ValueError(f"Cannot decompose bracket result: remaining={remaining}")

    return {k: v for k, v in coeffs.items() if v != 0}


def compute_structure_constants(n, odd, even, realization, parity, order_idx):
    basis_all = odd + even
    sc = []
    for i, X in enumerate(basis_all):
        for j, Y in enumerate(basis_all):
            if i > j:
                continue
            pX, pY = parity[X], parity[Y]
            bracket = graded_bracket(realization[X], realization[Y], pX, pY, order_idx)
            if not bracket:
                continue
            decomp = decompose_in_basis(bracket, realization, basis_all)
            for Z, c in decomp.items():
                sc.append({"X": X, "Y": Y, "Z": Z, "coeff": str(c), "sign_rule": "graded"})
    return sc


def build_schema1(n):
    odd, even = build_basis(n)
    basis_all = odd + even
    parity = build_parity(odd, even)
    realization = gen_realization(n)
    order_idx = {l: i for i, l in enumerate(osc_order(n))}

    sc = compute_structure_constants(n, odd, even, realization, parity, order_idx)

    even_dim = 2 * n * n + n + 1
    odd_dim = 4 * n
    boson_labels = [f"b_{k}_{s}" for k in range(1, n + 1) for s in ["p", "m"]]

    def ser_real(d):
        return [{"words": list(m), "coeff": str(c)} for m, c in d.items()]

    gen_real_serial = {g: {"standard_form": ser_real(realization[g]),
                           "parity": parity[g]} for g in basis_all}

    return {
        "schema_version": "5.0",
        "algebra": {
            "family": "C", "m": 1, "n": n,
            "cartan_type": f"C({n+1})",
            "alternative_notation": {"osp": f"osp(2|{2*n})",
                                     "dimension_formula": "osp(2m|2n) with m=1"},
            "dimension": {"total": even_dim + odd_dim, "even": even_dim, "odd": odd_dim}
        },
        "central_elements": {
            "K": {"label": "K", "parity": 0, "nilpotent": False,
                  "description": "Even central identity; identified with scalar 1."},
            "kappa": {"label": "kappa", "parity": 1, "nilpotent": True,
                      "description": "Odd nilpotent; kappa^2=0."}
        },
        "oscillator_generators": {
            "fermions": {"m": 1, "labels": ["a_1_p", "a_1_m"], "parity": 1},
            "bosons": {"count": 2 * n, "n": n, "labels": boson_labels}
        },
        "oscillator_relations": {
            "standard_fermion_anticommutators": {
                "raising_lowering": "{a_1^-, a_1^+} = 1",
                "same_type": "{a_1^s, a_1^s} = 0"
            },
            "bosonic_commutators": {
                "conjugate_pair": "[b_i^-, b_j^+] = delta_{ij}",
                "same_type": "[b_i^s, b_j^s] = 0"
            },
            "mixed_commutators": {"boson_fermion_undeformed": "[b_i^s, a_1^s] = 0"}
        },
        "basis": {
            "odd": odd, "even": even,
            "ordering_convention": "PBW: kappa < [odd] < [even]"
        },
        "parity": parity,
        "generator_realization": {
            "description": "Oscillator realization PBW-ordered",
            "ordering": ", ".join(osc_order(n)),
            "realizations": gen_real_serial
        },
        "structure_constants": sc,
        "metadata": {
            "generated_by": "src/C_generators.py",
            "generation_date": str(date.today()),
            "references": ["Frappat et al. (2000)", "Bakalov & Sullivan (2017)"]
        }
    }


def main():
    os.makedirs("data", exist_ok=True)
    for n in [1, 2, 3]:
        print(f"Generating C_{n}_structure.json (n={n}, C({n+1}) = osp(2|{2*n}))...")
        schema = build_schema1(n)
        path = f"data/C_{n}_structure.json"
        with open(path, "w") as f:
            json.dump(schema, f, indent=2)
        sc_count = len(schema["structure_constants"])
        odd_c = len(schema["basis"]["odd"])
        even_c = len(schema["basis"]["even"])
        print(f"  Basis: {odd_c} odd + {even_c} even = {odd_c+even_c}")
        print(f"  Structure constants (i<=j, non-zero): {sc_count}")
    print("Done.")


if __name__ == "__main__":
    main()
