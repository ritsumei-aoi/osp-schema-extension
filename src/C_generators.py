"""
C_generators.py - Generator and structure constant builder for C(n+1) = osp(2|2n).

This module defines the basis, parities, oscillator realizations, and computes
exact structure constants for C(n+1) = osp(2|2n) for any bosonic rank n (n=1, 2, 3).
It outputs Schema 1 JSON files adhering to docs/json_schema_specification.md.
"""

import json
import os
from fractions import Fraction
from typing import Dict, List, Tuple, Any


class Monomial:
    """
    Represents a normal-ordered oscillator monomial:
    (a_1_p)^{e_ap} * (a_1_m)^{e_am} * prod_{k=1}^n (b_k_p)^{e_bkp} * (b_k_m)^{e_bkm}
    """
    def __init__(self, e_ap: int = 0, e_am: int = 0, bosons: Tuple[int, ...] = ()):
        # bosons is a tuple of 2*n integers: (e_b1p, e_b1m, e_b2p, e_b2m, ...)
        self.e_ap = e_ap
        self.e_am = e_am
        self.bosons = tuple(bosons)

    def is_zero(self) -> bool:
        # Fermion exclusion: e_ap > 1 or e_am > 1
        return self.e_ap > 1 or self.e_am > 1

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, Monomial):
            return False
        return (self.e_ap, self.e_am, self.bosons) == (other.e_ap, other.e_am, other.bosons)

    def __hash__(self) -> int:
        return hash((self.e_ap, self.e_am, self.bosons))

    def __repr__(self) -> str:
        parts = []
        if self.e_ap:
            parts.append(f"a1p^{self.e_ap}" if self.e_ap > 1 else "a1p")
        if self.e_am:
            parts.append(f"a1m^{self.e_am}" if self.e_am > 1 else "a1m")
        for idx, count in enumerate(self.bosons):
            k = idx // 2 + 1
            pm = "p" if idx % 2 == 0 else "m"
            if count:
                parts.append(f"b{k}{pm}^{count}" if count > 1 else f"b{k}{pm}")
        return " * ".join(parts) if parts else "1"

    def to_word_list(self) -> List[str]:
        words = []
        if self.e_ap:
            words.extend(["a_1_p"] * self.e_ap)
        if self.e_am:
            words.extend(["a_1_m"] * self.e_am)
        for idx, count in enumerate(self.bosons):
            k = idx // 2 + 1
            pm = "p" if idx % 2 == 0 else "m"
            words.extend([f"b_{k}_{pm}"] * count)
        return words


class Poly:
    """
    Linear combination of Monomials with exact Fraction coefficients.
    """
    def __init__(self, terms: Dict[Monomial, Fraction] = None):
        self.terms: Dict[Monomial, Fraction] = {}
        if terms:
            for mono, coeff in terms.items():
                if mono.is_zero() or coeff == 0:
                    continue
                self.terms[mono] = self.terms.get(mono, Fraction(0)) + Fraction(coeff)
                if self.terms[mono] == 0:
                    del self.terms[mono]

    @classmethod
    def zero(cls, n_boson_pairs: int) -> "Poly":
        return cls({})

    @classmethod
    def from_fermion(cls, name: str, n_boson_pairs: int) -> "Poly":
        zero_bosons = (0,) * (2 * n_boson_pairs)
        if name == "a_1_p":
            return cls({Monomial(1, 0, zero_bosons): Fraction(1)})
        elif name == "a_1_m":
            return cls({Monomial(0, 1, zero_bosons): Fraction(1)})
        raise ValueError(f"Unknown fermion {name}")

    @classmethod
    def from_boson(cls, k: int, pm: str, n_boson_pairs: int) -> "Poly":
        b_list = [0] * (2 * n_boson_pairs)
        idx = 2 * (k - 1) + (0 if pm == "p" else 1)
        b_list[idx] = 1
        return cls({Monomial(0, 0, tuple(b_list)): Fraction(1)})

    @classmethod
    def constant(cls, val: Fraction, n_boson_pairs: int) -> "Poly":
        zero_bosons = (0,) * (2 * n_boson_pairs)
        return cls({Monomial(0, 0, zero_bosons): Fraction(val)})

    def __add__(self, other: "Poly") -> "Poly":
        res = dict(self.terms)
        for m, c in other.terms.items():
            res[m] = res.get(m, Fraction(0)) + c
            if res[m] == 0:
                del res[m]
        return Poly(res)

    def __sub__(self, other: "Poly") -> "Poly":
        return self + (other * Fraction(-1))

    def __mul__(self, other: Any) -> "Poly":
        if isinstance(other, (int, Fraction)):
            if other == 0:
                return Poly({})
            return Poly({m: c * Fraction(other) for m, c in self.terms.items()})
        elif isinstance(other, Poly):
            res = Poly({})
            for m1, c1 in self.terms.items():
                for m2, c2 in other.terms.items():
                    prod = mul_monomials(m1, m2) * (c1 * c2)
                    res = res + prod
            return res
        return NotImplemented

    def __rmul__(self, other: Any) -> "Poly":
        return self * other

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, Poly):
            return False
        return self.terms == other.terms

    def is_zero(self) -> bool:
        return len(self.terms) == 0


def mul_monomials(m1: Monomial, m2: Monomial) -> Poly:
    """
    Multiplies two normal-ordered monomials and returns a Poly in normal order:
    Fermions: {a1m, a1p} = 1, a1p^2 = 0, a1m^2 = 0
    Bosons: [bkm, bkp] = 1, all others commute.
    Fermions and bosons commute with each other.
    """
    n_boson_pairs = len(m1.bosons) // 2
    zero_b = (0,) * (2 * n_boson_pairs)

    # 1. Fermionic product:
    # m1 fermions: (a1p^e1p * a1m^e1m)
    # m2 fermions: (a1p^e2p * a1m^e2m)
    # Product in middle is a1m^e1m * a1p^e2p
    # If e1m == 0 or e2p == 0: already in order a1p^(e1p+e2p) * a1m^(e1m+e2m)
    f_res: Dict[Tuple[int, int], Fraction] = {}
    e1p, e1m = m1.e_ap, m1.e_am
    e2p, e2m = m2.e_ap, m2.e_am

    if e1m == 0 or e2p == 0:
        tot_p = e1p + e2p
        tot_m = e1m + e2m
        if tot_p <= 1 and tot_m <= 1:
            f_res[(tot_p, tot_m)] = Fraction(1)
    else:
        # e1m == 1 and e2p == 1:
        # a1m * a1p = 1 - a1p * a1m
        # m1: a1p^e1p * a1m, m2: a1p * a1m^e2m
        # prod = a1p^e1p * (1 - a1p * a1m) * a1m^e2m
        # term 1: a1p^e1p * a1m^e2m
        # term 2: - a1p^e1p * a1p * a1m * a1m^e2m = - a1p^(e1p+1) * a1m^(e2m+1)
        if e1p <= 1 and e2m <= 1:
            f_res[(e1p, e2m)] = Fraction(1)
        if (e1p + 1) <= 1 and (e2m + 1) <= 1:
            f_res[(e1p + 1, e2m + 1)] = f_res.get((e1p + 1, e2m + 1), Fraction(0)) - Fraction(1)

    if not f_res:
        return Poly.zero(n_boson_pairs)

    # 2. Bosonic product:
    # For each pair k: m1 has (b_k_p^u_p, b_k_m^u_m), m2 has (b_k_p^v_p, b_k_m^v_m)
    # Product is b_k_m^u_m * b_k_p^v_p
    # Using normal ordering formula for (b^-)^u (b^+)^v:
    # (b^-)^u (b^+)^v = sum_{s=0}^{min(u,v)} s! * binom(u,s) * binom(v,s) * (b^+)^{v-s} (b^-)^{u-s}
    import math

    def normal_order_boson_pair(u_m: int, v_p: int) -> List[Tuple[int, int, int]]:
        # returns list of (exp_p, exp_m, coeff)
        res = []
        for s in range(min(u_m, v_p) + 1):
            c = math.factorial(s) * math.comb(u_m, s) * math.comb(v_p, s)
            res.append((v_p - s, u_m - s, c))
        return res

    # Accumulate bosonic terms for each pair
    b_terms: Dict[Tuple[int, ...], Fraction] = {(): Fraction(1)}
    for k in range(n_boson_pairs):
        u_p = m1.bosons[2 * k]
        u_m = m1.bosons[2 * k + 1]
        v_p = m2.bosons[2 * k]
        v_m = m2.bosons[2 * k + 1]

        pair_exp_list = normal_order_boson_pair(u_m, v_p)
        new_b_terms: Dict[Tuple[int, ...], Fraction] = {}
        for prev_b, prev_c in b_terms.items():
            for exp_p, exp_m, coeff in pair_exp_list:
                tot_p = u_p + exp_p
                tot_m = exp_m + v_m
                full_b = prev_b + (tot_p, tot_m)
                new_b_terms[full_b] = new_b_terms.get(full_b, Fraction(0)) + prev_c * coeff
        b_terms = new_b_terms

    # Combine fermionic and bosonic terms
    final_terms: Dict[Monomial, Fraction] = {}
    for (fp, fm), fc in f_res.items():
        if fc == 0:
            continue
        for b_tup, bc in b_terms.items():
            if bc == 0:
                continue
            mono = Monomial(fp, fm, b_tup)
            final_terms[mono] = final_terms.get(mono, Fraction(0)) + fc * bc

    return Poly(final_terms)


def supercommutator(P1: Poly, p1: int, P2: Poly, p2: int) -> Poly:
    """
    Computes [P1, P2] = P1 * P2 - (-1)^{p1 * p2} P2 * P1
    """
    sign = -1 if (p1 == 1 and p2 == 1) else 1
    term1 = P1 * P2
    term2 = P2 * P1
    return term1 - (term2 * Fraction(sign))


def build_basis_and_realizations(n: int) -> Tuple[List[str], List[str], Dict[str, int], Dict[str, Poly], Dict[str, str]]:
    """
    Builds the C(n+1) basis lists, parities, and Poly realizations.
    Returns (even_basis, odd_basis, parity_dict, poly_dict, frappat_dict).
    """
    even_basis: List[str] = []
    odd_basis: List[str] = []
    parity: Dict[str, int] = {}
    poly: Dict[str, Poly] = {}
    frappat: Dict[str, str] = {}

    # 1. Fermionic & Bosonic operators
    a1p = Poly.from_fermion("a_1_p", n)
    a1m = Poly.from_fermion("a_1_m", n)

    bp = [Poly.from_boson(k, "p", n) for k in range(1, n + 1)]
    bm = [Poly.from_boson(k, "m", n) for k in range(1, n + 1)]

    # 2. Odd Generators (4n)
    # Ordered lexicographically by k=1..n, then pp, pm, mp, mm
    for k in range(1, n + 1):
        # E_eps1_del{k}_pp = a1p * bp[k-1]
        name_pp = f"E_eps1_del{k}_pp"
        odd_basis.append(name_pp)
        parity[name_pp] = 1
        poly[name_pp] = a1p * bp[k-1]
        frappat[name_pp] = f"a_1^+ b_{k}^+"

        # E_eps1_del{k}_pm = a1p * bm[k-1]
        name_pm = f"E_eps1_del{k}_pm"
        odd_basis.append(name_pm)
        parity[name_pm] = 1
        poly[name_pm] = a1p * bm[k-1]
        frappat[name_pm] = f"a_1^+ b_{k}^-"

        # E_eps1_del{k}_mp = a1m * bp[k-1]
        name_mp = f"E_eps1_del{k}_mp"
        odd_basis.append(name_mp)
        parity[name_mp] = 1
        poly[name_mp] = a1m * bp[k-1]
        frappat[name_mp] = f"a_1^- b_{k}^+"

        # E_eps1_del{k}_mm = a1m * bm[k-1]
        name_mm = f"E_eps1_del{k}_mm"
        odd_basis.append(name_mm)
        parity[name_mm] = 1
        poly[name_mm] = a1m * bm[k-1]
        frappat[name_mm] = f"a_1^- b_{k}^-"

    # 3. Even Cartan Generators (n+1)
    # H_1 = a1p a1m + b1p b1m
    h1_name = "H_1"
    even_basis.append(h1_name)
    parity[h1_name] = 0
    poly[h1_name] = (a1p * a1m) + (bp[0] * bm[0])
    frappat[h1_name] = "a_1^+ a_1^- + b_1^+ b_1^-"

    for k in range(2, n + 1):
        hk_name = f"H_{k}"
        even_basis.append(hk_name)
        parity[hk_name] = 0
        poly[hk_name] = (bp[k-2] * bm[k-2]) - (bp[k-1] * bm[k-1])
        frappat[hk_name] = f"b_{k-1}^+ b_{k-1}^- - b_{k}^+ b_{k}^-"

    hn1_name = f"H_{n+1}"
    even_basis.append(hn1_name)
    parity[hn1_name] = 0
    poly[hn1_name] = (bp[n-1] * bm[n-1] * Fraction(-1)) + Poly.constant(Fraction(-1, 2), n)
    frappat[hn1_name] = f"-b_{n}^+ b_{n}^- - 1/2"

    # 4. Even Long Roots (2n)
    # E_2del{k}_p = (b_k^+)^2
    for k in range(1, n + 1):
        name_2p = f"E_2del{k}_p"
        even_basis.append(name_2p)
        parity[name_2p] = 0
        poly[name_2p] = bp[k-1] * bp[k-1]
        frappat[name_2p] = f"(b_{k}^+)^2"

    # E_2del{k}_m = (b_k^-)^2
    for k in range(1, n + 1):
        name_2m = f"E_2del{k}_m"
        even_basis.append(name_2m)
        parity[name_2m] = 0
        poly[name_2m] = bm[k-1] * bm[k-1]
        frappat[name_2m] = f"(b_{k}^-)^2"

    # 5. Even Mixed Roots (for n >= 2: 2n(n-1))
    for i in range(1, n + 1):
        for j in range(i + 1, n + 1):
            name_pp = f"E_del{i}_del{j}_pp"
            even_basis.append(name_pp)
            parity[name_pp] = 0
            poly[name_pp] = bp[i-1] * bp[j-1]
            frappat[name_pp] = f"b_{i}^+ b_{j}^+"

            name_mm = f"E_del{i}_del{j}_mm"
            even_basis.append(name_mm)
            parity[name_mm] = 0
            poly[name_mm] = bm[i-1] * bm[j-1]
            frappat[name_mm] = f"b_{i}^- b_{j}^-"

            name_pm = f"E_del{i}_del{j}_pm"
            even_basis.append(name_pm)
            parity[name_pm] = 0
            poly[name_pm] = bp[i-1] * bm[j-1]
            frappat[name_pm] = f"b_{i}^+ b_{j}^-"

            name_mp = f"E_del{i}_del{j}_mp"
            even_basis.append(name_mp)
            parity[name_mp] = 0
            poly[name_mp] = bm[i-1] * bp[j-1]
            frappat[name_mp] = f"b_{i}^- b_{j}^+"

    return even_basis, odd_basis, parity, poly, frappat


def decompose_poly(target: Poly, basis: List[str], poly_dict: Dict[str, Poly], n: int) -> Dict[str, Fraction]:
    """
    Decomposes target Poly uniquely into a linear combination of basis generators.
    Raises ValueError if target cannot be represented as a pure linear combination of basis elements.
    """
    if target.is_zero():
        return {}

    # Collect all monomials present in basis elements
    all_monos = set()
    for gen in basis:
        all_monos.update(poly_dict[gen].terms.keys())
    target_monos = set(target.terms.keys())

    # Check for constant term or unexpected monomials
    zero_b = (0,) * (2 * n)
    const_mono = Monomial(0, 0, zero_b)

    # Matrix representation
    mono_list = sorted(list(all_monos | target_monos), key=lambda m: (m.e_ap, m.e_am, m.bosons))
    mono_to_row = {m: i for i, m in enumerate(mono_list)}

    # Build linear system A * x = b
    # Number of rows = len(mono_list), number of cols = len(basis)
    # We solve over Fractions
    import numpy as np

    matrix_data = [[Fraction(0) for _ in basis] for _ in mono_list]
    for col, gen in enumerate(basis):
        for m, coeff in poly_dict[gen].terms.items():
            matrix_data[mono_to_row[m]][col] = coeff

    b_vec = [target.terms.get(m, Fraction(0)) for m in mono_list]

    # Gaussian elimination with Fraction
    M = [row[:] + [b_vec[i]] for i, row in enumerate(matrix_data)]
    n_rows = len(M)
    n_cols = len(basis)

    pivot_row = 0
    pivot_cols = []
    for col in range(n_cols):
        # find pivot
        found = -1
        for r in range(pivot_row, n_rows):
            if M[r][col] != 0:
                found = r
                break
        if found == -1:
            continue
        # swap
        M[pivot_row], M[found] = M[found], M[pivot_row]
        pivot_val = M[pivot_row][col]
        # normalize
        for c in range(col, n_cols + 1):
            M[pivot_row][c] /= pivot_val
        # eliminate
        for r in range(n_rows):
            if r != pivot_row and M[r][col] != 0:
                factor = M[r][col]
                for c in range(col, n_cols + 1):
                    M[r][c] -= factor * M[pivot_row][c]
        pivot_cols.append((pivot_row, col))
        pivot_row += 1

    # Check for consistency in remaining rows
    for r in range(pivot_row, n_rows):
        if M[r][n_cols] != 0:
            raise ValueError(f"Target poly {target.terms} not in basis span! Inconsistent at mono {mono_list[r]}")

    # Back-substitute solution
    sol: Dict[str, Fraction] = {}
    for r, col in pivot_cols:
        val = M[r][n_cols]
        if val != 0:
            sol[basis[col]] = val

    return sol


def compute_structure_constants(n: int) -> Tuple[Dict[str, Any], List[Dict[str, Any]]]:
    """
    Computes all graded brackets and generates Schema 1 data for C(n+1).
    """
    even_basis, odd_basis, parity, poly, frappat = build_basis_and_realizations(n)
    full_basis = odd_basis + even_basis  # PBW ordering: odd before even

    structure_constants = []
    for i, gen_x in enumerate(full_basis):
        for j, gen_y in enumerate(full_basis):
            px = parity[gen_x]
            py = parity[gen_y]
            poly_x = poly[gen_x]
            poly_y = poly[gen_y]

            bracket_poly = supercommutator(poly_x, px, poly_y, py)
            if bracket_poly.is_zero():
                continue

            decomp = decompose_poly(bracket_poly, full_basis, poly, n)
            for gen_z, coeff in decomp.items():
                if coeff != 0:
                    structure_constants.append({
                        "X": gen_x,
                        "Y": gen_y,
                        "Z": gen_z,
                        "coeff": str(coeff.numerator) if coeff.denominator == 1 else f"{coeff.numerator}/{coeff.denominator}",
                        "sign_rule": "graded"
                    })

    # Build Schema 1 dictionary
    even_dim = 2 * n * n + n + 1
    odd_dim = 4 * n
    total_dim = 2 * n * n + 5 * n + 1

    schema1_data = {
        "schema_version": "5.0",
        "algebra": {
            "family": "C",
            "m": 1,
            "n": n,
            "cartan_type": f"C({n+1})",
            "alternative_notation": {
                "osp": f"osp(2|{2*n})",
                "dimension_formula": f"osp(2m|2n) with m=1, even = 2n^2 + n + 1, odd = 4n, total = 2n^2 + 5n + 1"
            },
            "dimension": {
                "total": total_dim,
                "even": even_dim,
                "odd": odd_dim
            }
        },
        "central_elements": {
            "kappa": {
                "label": "kappa",
                "parity": 1,
                "nilpotent_order": 2,
                "description": "Odd central element parametrizing inhomogeneous deformations (kappa^2 = 0)"
            },
            "K": {
                "label": "K",
                "parity": 0,
                "value": 1,
                "description": "Even central identity element from oscillator canonical relations"
            }
        },
        "oscillator_generators": {
            "fermions": {
                "m": 1,
                "labels": ["a_1_p", "a_1_m"],
                "parity": 1,
                "description": "Standard fermionic oscillator pair a_1^± satisfying CAR"
            },
            "bosons": {
                "count": 2 * n,
                "n": n,
                "labels": [f"b_{k}_{pm}" for k in range(1, n + 1) for pm in ["p", "m"]],
                "parity": 0,
                "description": f"Bosonic oscillators b_k^± with k=1,...,{n}"
            }
        },
        "oscillator_relations": {
            "standard_fermion_anticommutators": {
                "description": "Canonical anticommutation relations (CAR) for fermions",
                "relations": {
                    "conjugate_pair": "{a_1^-, a_1^+} = a_1^- a_1^+ + a_1^+ a_1^- = 1",
                    "nilpotency": "(a_1^+)^2 = 0, (a_1^-)^2 = 0"
                }
            },
            "bosonic_commutators": {
                "description": "Canonical commutation relations (CCR) for bosons",
                "relations": {
                    "same_type": "[b_j^±, b_k^±] = 0",
                    "conjugate_pair": "[b_j^-, b_k^+] = δ_{jk}"
                }
            },
            "mixed_commutators": {
                "boson_fermion": "[b_j^±, a_1^±] = 0 (undeformed)"
            }
        },
        "basis": {
            "even": even_basis,
            "odd": odd_basis,
            "ordering_convention": "PBW: kappa < [odd: E_eps1_del{k}_pp/pm/mp/mm] < [even: H_k, E_2del{k}_p/m, E_del{i}_del{j}_pp/mm/pm/mp]"
        },
        "parity": parity,
        "generator_realization": {
            "description": "Normal ordered form: fermions then bosons",
            "ordering": "a_1_p, a_1_m, " + ", ".join([f"b_{k}_p, b_{k}_m" for k in range(1, n + 1)]),
            "realizations": {
                gen: {
                    "standard_form": [
                        {
                            "words": m.to_word_list(),
                            "coeff": str(c.numerator) if c.denominator == 1 else f"{c.numerator}/{c.denominator}"
                        }
                        for m, c in poly[gen].terms.items()
                    ],
                    "frappat_form": frappat[gen],
                    "parity": parity[gen]
                }
                for gen in full_basis
            }
        },
        "structure_constants": structure_constants,
        "metadata": {
            "generated_by": "src/C_generators.py",
            "generation_date": "2026-10-05",
            "references": [
                "Frappat et al. (2000), Dictionary on Lie Algebras and Superalgebras",
                "Bakalov and Sullivan (2017)"
            ]
        }
    }

    return schema1_data, structure_constants


def generate_all_schema1_files(output_dir: str = "data"):
    os.makedirs(output_dir, exist_ok=True)
    for n in [1, 2, 3]:
        schema1_data, _ = compute_structure_constants(n)
        filepath = os.path.join(output_dir, f"C_{n}_structure.json")
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(schema1_data, f, indent=2)
        print(f"Generated {filepath}: {len(schema1_data['structure_constants'])} structure constant entries.")


if __name__ == "__main__":
    generate_all_schema1_files()
