#!/usr/bin/env python3
"""
src/C_generators.py

Generate Schema 1 structure constants for C(n+1) = osp(2|2n).
Outputs C_{n}_structure.json for n = 1, 2, 3.

Oscillator index encoding:
  a_1_p -> 0,  a_1_m -> 1
  b_k_p -> 2k, b_k_m -> 2k+1   (k = 1, ..., n)
"""

from fractions import Fraction
from itertools import combinations
import json
import os
from datetime import date


# ── Oscillator helpers ────────────────────────────────────────────────────────

def _is_fermionic(idx: int) -> bool:
    return idx < 2


def _osc_label(idx: int) -> str:
    if idx == 0:
        return "a_1_p"
    if idx == 1:
        return "a_1_m"
    k = idx // 2
    return f"b_{k}_p" if idx % 2 == 0 else f"b_{k}_m"


# ── Polynomial arithmetic (oscillator algebra) ────────────────────────────────
# A polynomial is dict[tuple[int, ...], Fraction].

def _sort_mono(mono: tuple) -> dict:
    """
    Normal-order a monomial using CAR/CCR. Returns {sorted_tuple: Fraction}.

    Reduction rules:
      - a_1_m * a_1_p  = 1 - a_1_p * a_1_m  (anticommutator {a_1_m, a_1_p} = 1)
      - b_k_m * b_k_p  = b_k_p * b_k_m + 1   (commutator [b_k_m, b_k_p] = 1)
      - all other out-of-order pairs commute or anticommute without extra term
    """
    indices = list(mono)
    for i in range(len(indices) - 1):
        if indices[i] > indices[i + 1]:
            a, b = indices[i], indices[i + 1]
            pa = 1 if _is_fermionic(a) else 0
            pb = 1 if _is_fermionic(b) else 0
            swap_sign = Fraction((-1) ** (pa * pb))

            extra_val = Fraction(0)
            if pa and pb:
                # {a_1_m, a_1_p} = 1  (a=1, b=0)
                extra_val = Fraction(1)
            elif (not pa) and (not pb):
                # [b_k_m, b_k_p] = 1  iff a = b+1, b even
                if a % 2 == 1 and b % 2 == 0 and a == b + 1:
                    extra_val = Fraction(1)
            # mixed (boson,fermion): commute freely, extra_val = 0

            prefix = indices[:i]
            suffix = indices[i + 2:]

            # Main term (swapped pair)
            main = _sort_mono(tuple(prefix + [b, a] + suffix))
            result = {k: swap_sign * v for k, v in main.items()}

            # Extra term from (anti)commutator
            if extra_val:
                for k, v in _sort_mono(tuple(prefix + suffix)).items():
                    result[k] = result.get(k, Fraction(0)) + extra_val * v

            return {k: v for k, v in result.items() if v}

    # Already in PBW order; check for fermionic self-product (= 0)
    for i in range(len(indices) - 1):
        if indices[i] == indices[i + 1] and _is_fermionic(indices[i]):
            return {}
    return {mono: Fraction(1)}


def _clean(p: dict) -> dict:
    return {k: v for k, v in p.items() if v}


def _mul(p1: dict, p2: dict) -> dict:
    res: dict = {}
    for m1, c1 in p1.items():
        for m2, c2 in p2.items():
            for k, v in _sort_mono(m1 + m2).items():
                res[k] = res.get(k, Fraction(0)) + c1 * c2 * v
    return _clean(res)


def _add(p1: dict, p2: dict, c1=Fraction(1), c2=Fraction(1)) -> dict:
    res: dict = {}
    for k, v in p1.items():
        res[k] = res.get(k, Fraction(0)) + c1 * v
    for k, v in p2.items():
        res[k] = res.get(k, Fraction(0)) + c2 * v
    return _clean(res)


def bracket(X: dict, Y: dict, px: int, py: int) -> dict:
    """Graded bracket [X, Y} = XY - (-1)^{px·py} YX."""
    sign = Fraction((-1) ** (px * py))
    return _add(_mul(X, Y), _mul(Y, X), Fraction(1), -sign)


# ── C(n+1) generator definitions ─────────────────────────────────────────────

def build_generators(n: int):
    """
    Return (gens, parity, basis) for C(n+1) = osp(2|2n).

    basis is the ordered list of generator labels following the approved
    PBW convention: κ < [ε+ odd] < [ε− odd] < [even].
    """
    gens: dict = {}
    par:  dict = {}

    # ── Odd generators ──────────────────────────────────────────────────────
    # ε+ group: E_eps1_del{k}_pp, E_eps1_del{k}_pm  (k ascending)
    # ε− group: E_eps1_del{k}_mp, E_eps1_del{k}_mm  (k ascending)
    odd_plus:  list = []
    odd_minus: list = []
    for k in range(1, n + 1):
        for lbl, mono in [
            (f"E_eps1_del{k}_pp", (0, 2 * k)),
            (f"E_eps1_del{k}_pm", (0, 2 * k + 1)),
        ]:
            gens[lbl] = {mono: Fraction(1)}
            par[lbl] = 1
            odd_plus.append(lbl)
        for lbl, mono in [
            (f"E_eps1_del{k}_mp", (1, 2 * k)),
            (f"E_eps1_del{k}_mm", (1, 2 * k + 1)),
        ]:
            gens[lbl] = {mono: Fraction(1)}
            par[lbl] = 1
            odd_minus.append(lbl)

    # ── Even generators ─────────────────────────────────────────────────────
    even_lbls: list = []

    # Cartan elements H_1, ..., H_{n+1}
    gens["H_1"] = {(0, 1): Fraction(1), (2, 3): Fraction(1)}
    par["H_1"] = 0
    even_lbls.append("H_1")
    for k in range(2, n + 1):
        lbl = f"H_{k}"
        gens[lbl] = {
            (2 * (k - 1), 2 * (k - 1) + 1): Fraction(1),
            (2 * k, 2 * k + 1): Fraction(-1),
        }
        par[lbl] = 0
        even_lbls.append(lbl)
    hn1 = f"H_{n + 1}"
    gens[hn1] = {(2 * n, 2 * n + 1): Fraction(-1), (): Fraction(-1, 2)}
    par[hn1] = 0
    even_lbls.append(hn1)

    # sp(2n) positive long roots: E_2del{k}_p
    for k in range(1, n + 1):
        lbl = f"E_2del{k}_p"
        gens[lbl] = {(2 * k, 2 * k): Fraction(1)}
        par[lbl] = 0
        even_lbls.append(lbl)

    # sp(2n) positive short roots: E_del{i}_del{j}_pp  (i < j)
    for i, j in combinations(range(1, n + 1), 2):
        lbl = f"E_del{i}_del{j}_pp"
        gens[lbl] = {(2 * i, 2 * j): Fraction(1)}
        par[lbl] = 0
        even_lbls.append(lbl)

    # sp(2n) negative long roots: E_2del{k}_m
    for k in range(1, n + 1):
        lbl = f"E_2del{k}_m"
        gens[lbl] = {(2 * k + 1, 2 * k + 1): Fraction(1)}
        par[lbl] = 0
        even_lbls.append(lbl)

    # sp(2n) negative short roots: E_del{i}_del{j}_mm  (i < j)
    for i, j in combinations(range(1, n + 1), 2):
        lbl = f"E_del{i}_del{j}_mm"
        gens[lbl] = {(2 * i + 1, 2 * j + 1): Fraction(1)}
        par[lbl] = 0
        even_lbls.append(lbl)

    # sp(2n) mixed roots: pm and mp  (i < j)
    for i, j in combinations(range(1, n + 1), 2):
        for lbl, mono in [
            (f"E_del{i}_del{j}_pm", (2 * i, 2 * j + 1)),
            (f"E_del{i}_del{j}_mp", (2 * i + 1, 2 * j)),
        ]:
            gens[lbl] = {mono: Fraction(1)}
            par[lbl] = 0
            even_lbls.append(lbl)

    basis = odd_plus + odd_minus + even_lbls
    return gens, par, basis


# ── Express oscillator polynomial in the Lie algebra basis ────────────────────

def _solve_cartan(b: list, n: int) -> list:
    """
    Solve for Cartan coefficients c[0],...,c[n]  (H_1,...,H_{n+1}).

    b[k] = coefficient of cartan_mono[k] in the bracket result, where
      cartan_monos = [(0,1), (2,3), (4,5), ..., (2n,2n+1), ()]
    (n+2 entries: n+1 number operators plus the constant).

    The system (derived from the Cartan matrix):
      eq 0 : c[0]          = b[0]
      eq 1 : c[0] + c[1]   = b[1]   (H_1,H_2 both contribute to (2,3))
      eq k (2≤k≤n-1): -c[k-1] + c[k] = b[k]
      eq n : -c[n-1] - c[n] = b[n]
      eq n+1: (-1/2)·c[n]  = b[n+1]  → c[n] = -2·b[n+1]
    """
    N = n + 1  # number of unknowns
    c = [Fraction(0)] * N
    c[0] = b[0]
    if N >= 2:
        c[N - 1] = Fraction(-2) * b[N]   # from constant-term equation
    if N >= 3:
        c[1] = b[1] - c[0]
        for k in range(2, N - 1):
            c[k] = b[k] + c[k - 1]
    return c


def express(poly: dict, n: int, gens: dict) -> dict:
    """
    Decompose an oscillator polynomial into a linear combination of generators.
    Returns {label: Fraction}.  Raises ValueError if non-algebra monomials remain.
    """
    if not poly:
        return {}

    result: dict = {}
    rem = dict(poly)

    # Step 1: non-Cartan generators are each a single unique monomial
    for lbl, gp in gens.items():
        if lbl.startswith("H_"):
            continue
        m = next(iter(gp))
        if m in rem:
            result[lbl] = rem.pop(m) / gp[m]

    if not rem:
        return _clean(result)

    # Step 2: remaining monomials must be Cartan (number operators + constant)
    cartan_monos = [(0, 1)] + [(2 * k, 2 * k + 1) for k in range(1, n + 1)] + [()]
    b = [rem.pop(m, Fraction(0)) for m in cartan_monos]

    unexpected = {k: v for k, v in rem.items() if v}
    if unexpected:
        raise ValueError(f"Non-algebra monomials remain after bracket: {unexpected}")

    cartan_labels = [f"H_{k}" for k in range(1, n + 2)]
    for lbl, cv in zip(cartan_labels, _solve_cartan(b, n)):
        if cv:
            result[lbl] = result.get(lbl, Fraction(0)) + cv

    return _clean(result)


# ── Schema 1 JSON builder ─────────────────────────────────────────────────────

def dim_even(n: int) -> int:
    return 2 * n * n + n + 1

def dim_odd(n: int) -> int:
    return 4 * n

def dim_total(n: int) -> int:
    return dim_even(n) + dim_odd(n)


def _frac_str(f: Fraction) -> str:
    return str(f.numerator) if f.denominator == 1 else f"{f.numerator}/{f.denominator}"


def build_schema(n: int) -> dict:
    gens, par, basis = build_generators(n)

    # Compute all non-zero structure constants [Z_i, Z_j}  (i ≤ j in basis order)
    sc = []
    for i, xi in enumerate(basis):
        for j, xj in enumerate(basis):
            if j < i:
                continue
            br = bracket(gens[xi], gens[xj], par[xi], par[xj])
            if not br:
                continue
            coeffs = express(br, n, gens)
            if not coeffs:
                continue
            for z, c in sorted(coeffs.items()):
                sc.append({
                    "X": xi,
                    "Y": xj,
                    "Z": z,
                    "coeff": _frac_str(c),
                    "sign_rule": "graded",
                })

    # Oscillator labels
    boson_labels = []
    for k in range(1, n + 1):
        boson_labels += [f"b_{k}_p", f"b_{k}_m"]

    # Generator realization entries
    real_entries: dict = {}
    for lbl in basis:
        sf = []
        for mono, coeff in sorted(gens[lbl].items()):
            sf.append({
                "words": [_osc_label(idx) for idx in mono],
                "coeff": _frac_str(coeff),
            })
        real_entries[lbl] = {"standard_form": sf, "parity": par[lbl]}

    odd_basis  = [l for l in basis if par[l] == 1]
    even_basis = [l for l in basis if par[l] == 0]

    return {
        "schema_version": "5.0",
        "algebra": {
            "family": "C",
            "m": 1,
            "n": n,
            "cartan_type": f"C({n + 1})",
            "alternative_notation": {
                "osp": f"osp(2|{2 * n})",
                "dimension_formula": "osp(2m|2n) with m=1",
            },
            "dimension": {
                "total": dim_total(n),
                "even": dim_even(n),
                "odd": dim_odd(n),
                "even_formula": "2n^2 + n + 1",
                "odd_formula": "4n",
            },
        },
        "central_elements": {
            "kappa": {
                "label": "kappa",
                "parity": 1,
                "nilpotency": "kappa^2 = 0",
                "description": "Odd central element; parametrizes the inhomogeneous deformation.",
            },
            "K": {
                "label": "K",
                "parity": 0,
                "value": "K = 1 (scalar identification)",
                "description": "Even central identity; not included as an independent basis element.",
            },
        },
        "oscillator_generators": {
            "fermions": {
                "m": 1,
                "labels": ["a_1_p", "a_1_m"],
                "parity": 1,
                "description": "Standard fermionic pair a_1^± satisfying CAR {a_1^-, a_1^+} = 1",
            },
            "bosons": {
                "count": 2 * n,
                "n": n,
                "labels": boson_labels,
                "description": f"Bosonic oscillators b_i^± with i=1,...,{n}",
            },
        },
        "oscillator_relations": {
            "standard_fermion_anticommutators": {
                "description": "Canonical anticommutation relations for the fermionic pair",
                "relations": {
                    "anticommutator": "{a_1^-, a_1^+} = 1",
                    "self_anticommutators": "{a_1^+, a_1^+} = 0, {a_1^-, a_1^-} = 0",
                },
            },
            "bosonic_commutators": {
                "description": "Canonical commutation relations for bosonic oscillators",
                "relations": {
                    "same_type": "[b_i^±, b_j^±] = 0 for all i, j",
                    "conjugate_pair": "[b_i^-, b_j^+] = delta_{ij}",
                },
            },
            "mixed_commutators": {"boson_fermion": "[b_i^±, a_1^±] = 0"},
        },
        "basis": {
            "even": even_basis,
            "odd": odd_basis,
            "ordering_convention": (
                "PBW: κ < [ε+ odd, k ascending, δ+ before δ−] "
                "< [ε− odd, k ascending, δ+ before δ−] < [even]  "
                "(K = 1 is excluded)"
            ),
        },
        "parity": {l: par[l] for l in basis},
        "generator_realization": {
            "description": "Standard form with PBW ordering",
            "ordering": ", ".join(["a_1_p", "a_1_m"] + boson_labels),
            "realizations": real_entries,
        },
        "structure_constants": sc,
        "metadata": {
            "generated_by": "src/C_generators.py",
            "generation_date": date.today().isoformat(),
            "n": n,
            "references": [
                "Frappat, Sciarrino, Sorba, Dictionary on Lie Algebras and Superalgebras (2000)",
                "arXiv:hep-th/9607161",
            ],
        },
    }


def main():
    os.makedirs("data", exist_ok=True)
    for n in [1, 2, 3]:
        print(f"Computing C({n + 1}) = osp(2|{2 * n}), n={n}...")
        schema = build_schema(n)
        out = f"data/C_{n}_structure.json"
        with open(out, "w") as f:
            json.dump(schema, f, indent=2)
        dim = schema["algebra"]["dimension"]
        sc_count = len(schema["structure_constants"])
        print(f"  dim: even={dim['even']}, odd={dim['odd']}, total={dim['total']}")
        print(f"  non-zero structure constants: {sc_count}")
        print(f"  written: {out}")


if __name__ == "__main__":
    main()
