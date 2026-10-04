"""
C_generators.py: Generator for C(n+1) = osp(2|2n) Lie superalgebra structure constants.
Produces Schema 1 JSON data for n=1, 2, 3 (C(2), C(3), C(4)).
"""

import json
import os
from fractions import Fraction
from collections import defaultdict
import itertools
from math import comb, factorial
import sympy as sp


class OscillatorPoly:
    """Polynomial in normal-ordered fermionic and bosonic oscillators."""
    def __init__(self, terms=None):
        self.terms = defaultdict(Fraction)
        if terms:
            for k, v in terms.items():
                if v != 0:
                    self.terms[k] = Fraction(v)

    @classmethod
    def from_monomial(cls, n, coeff=1, a_p=0, a_m=0, bosons=None):
        if bosons is None:
            bosons = [(0, 0)] * n
        else:
            bosons = list(bosons)
            while len(bosons) < n:
                bosons.append((0, 0))
        key = (a_p, a_m, tuple(bosons))
        return cls({key: Fraction(coeff)})

    def __add__(self, other):
        res = defaultdict(Fraction, self.terms)
        for k, v in other.terms.items():
            res[k] += v
            if res[k] == 0:
                del res[k]
        return OscillatorPoly(res)

    def __sub__(self, other):
        res = defaultdict(Fraction, self.terms)
        for k, v in other.terms.items():
            res[k] -= v
            if res[k] == 0:
                del res[k]
        return OscillatorPoly(res)

    def __mul__(self, other):
        if isinstance(other, (int, Fraction)):
            return OscillatorPoly({k: v * Fraction(other) for k, v in self.terms.items() if v * Fraction(other) != 0})
        res = OscillatorPoly()
        for k1, v1 in self.terms.items():
            for k2, v2 in other.terms.items():
                p = mul_normal_monomials(k1, k2)
                p = p * (v1 * v2)
                res = res + p
        return res


def mul_boson_modes(b1, b2):
    p1, m1 = b1
    p2, m2 = b2
    res = {}
    for k in range(min(m1, p2) + 1):
        c = factorial(k) * comb(m1, k) * comb(p2, k)
        res[(p1 + p2 - k, m1 + m2 - k)] = c
    return res


def mul_fermion_modes(f1, f2):
    p1, m1 = f1
    p2, m2 = f2
    if m1 == 0:
        if p1 + p2 <= 1:
            return {(p1 + p2, m2): 1}
        else:
            return {}
    if p2 == 0:
        if m2 == 0:
            return {(p1, 1): 1}
        else:
            return {}
    res = {}
    res[(p1, m2)] = 1
    if p1 == 0 and m2 == 0:
        res[(1, 1)] = -1
    return res


def mul_normal_monomials(k1, k2):
    f_res = mul_fermion_modes((k1[0], k1[1]), (k2[0], k2[1]))
    n = len(k1[2])
    b_res_list = [mul_boson_modes(k1[2][i], k2[2][i]) for i in range(n)]
    poly_terms = {}
    for (f_p, f_m), f_c in f_res.items():
        all_b_combos = [b_res_list[i].items() for i in range(n)]
        for combo in itertools.product(*all_b_combos):
            c = f_c
            b_tuple = []
            for b_mode, b_coeff in combo:
                c *= b_coeff
                b_tuple.append(b_mode)
            key = (f_p, f_m, tuple(b_tuple))
            poly_terms[key] = poly_terms.get(key, 0) + c
    return OscillatorPoly(poly_terms)


def build_basis_and_generators(n):
    """Build the PBW-ordered basis, parities, and oscillator representations for C(n+1)."""
    parity = {}
    gen_poly = {}

    # Even basis in strict PBW order
    ordered_even = [f"H_{i}" for i in range(1, n + 2)]
    ordered_even += [f"E_2del{k}_p" for k in range(1, n + 1)]
    for i in range(1, n + 1):
        for j in range(i + 1, n + 1):
            ordered_even.append(f"E_del{i}_del{j}_pp")
    ordered_even += [f"E_2del{k}_m" for k in range(1, n + 1)]
    for i in range(1, n + 1):
        for j in range(i + 1, n + 1):
            ordered_even.append(f"E_del{i}_del{j}_mm")
    for i in range(1, n + 1):
        for j in range(i + 1, n + 1):
            ordered_even.append(f"E_del{i}_del{j}_pm")
    for i in range(1, n + 1):
        for j in range(i + 1, n + 1):
            ordered_even.append(f"E_del{i}_del{j}_mp")
    even_basis = ordered_even
    for g in even_basis:
        parity[g] = 0

    # Odd basis in strict PBW order
    odd_basis = []
    for k in range(1, n + 1):
        for suffix in ["pp", "pm", "mp", "mm"]:
            name = f"E_eps1_del{k}_{suffix}"
            odd_basis.append(name)
            parity[name] = 1

    # Define polynomial realizations
    # H_1 = a_1^+ a_1^- + b_1^+ b_1^-
    b1_mode = [(1, 1) if idx == 0 else (0, 0) for idx in range(n)]
    gen_poly["H_1"] = OscillatorPoly.from_monomial(n, 1, a_p=1, a_m=1) + OscillatorPoly.from_monomial(n, 1, bosons=b1_mode)

    # H_k = b_{k-1}^+ b_{k-1}^- - b_k^+ b_k^- for 2 <= k <= n
    for k in range(2, n + 1):
        bk_prev = [(1, 1) if idx == k - 2 else (0, 0) for idx in range(n)]
        bk_curr = [(1, 1) if idx == k - 1 else (0, 0) for idx in range(n)]
        gen_poly[f"H_{k}"] = OscillatorPoly.from_monomial(n, 1, bosons=bk_prev) - OscillatorPoly.from_monomial(n, 1, bosons=bk_curr)

    # H_{n+1} = b_n^+ b_n^- + 1/2
    bn_mode = [(1, 1) if idx == n - 1 else (0, 0) for idx in range(n)]
    gen_poly[f"H_{n+1}"] = OscillatorPoly.from_monomial(n, 1, bosons=bn_mode) + OscillatorPoly.from_monomial(n, Fraction(1, 2))

    # Long roots: E_2del{k}_p = (b_k^+)^2, E_2del{k}_m = (b_k^-)^2
    for k in range(1, n + 1):
        bk_p = [(2, 0) if idx == k - 1 else (0, 0) for idx in range(n)]
        bk_m = [(0, 2) if idx == k - 1 else (0, 0) for idx in range(n)]
        gen_poly[f"E_2del{k}_p"] = OscillatorPoly.from_monomial(n, 1, bosons=bk_p)
        gen_poly[f"E_2del{k}_m"] = OscillatorPoly.from_monomial(n, 1, bosons=bk_m)

    # Short roots:
    for i in range(1, n + 1):
        for j in range(i + 1, n + 1):
            def make_b(bi, bj):
                return [bi if idx == i - 1 else (bj if idx == j - 1 else (0, 0)) for idx in range(n)]
            gen_poly[f"E_del{i}_del{j}_pp"] = OscillatorPoly.from_monomial(n, 1, bosons=make_b((1, 0), (1, 0)))
            gen_poly[f"E_del{i}_del{j}_mm"] = OscillatorPoly.from_monomial(n, 1, bosons=make_b((0, 1), (0, 1)))
            gen_poly[f"E_del{i}_del{j}_pm"] = OscillatorPoly.from_monomial(n, 1, bosons=make_b((1, 0), (0, 1)))
            gen_poly[f"E_del{i}_del{j}_mp"] = OscillatorPoly.from_monomial(n, 1, bosons=make_b((0, 1), (1, 0)))

    # Odd roots:
    for k in range(1, n + 1):
        def make_bk(b_mode):
            return [b_mode if idx == k - 1 else (0, 0) for idx in range(n)]
        gen_poly[f"E_eps1_del{k}_pp"] = OscillatorPoly.from_monomial(n, 1, a_p=1, a_m=0, bosons=make_bk((1, 0)))
        gen_poly[f"E_eps1_del{k}_pm"] = OscillatorPoly.from_monomial(n, 1, a_p=1, a_m=0, bosons=make_bk((0, 1)))
        gen_poly[f"E_eps1_del{k}_mp"] = OscillatorPoly.from_monomial(n, 1, a_p=0, a_m=1, bosons=make_bk((1, 0)))
        gen_poly[f"E_eps1_del{k}_mm"] = OscillatorPoly.from_monomial(n, 1, a_p=0, a_m=1, bosons=make_bk((0, 1)))

    return even_basis, odd_basis, parity, gen_poly


def format_fraction(f):
    if f.denominator == 1:
        return str(f.numerator)
    return f"{f.numerator}/{f.denominator}"


def poly_to_realization_entry(poly, name, parity_val, n):
    """Convert an OscillatorPoly to a standard_form and frappat_form description."""
    standard_form = []
    # Sort terms deterministically
    sorted_keys = sorted(poly.terms.keys())
    frappat_terms = []
    for k in sorted_keys:
        coeff = poly.terms[k]
        coeff_str = format_fraction(coeff)
        words = []
        if k[0] == 1:
            words.append("a_1_p")
        if k[1] == 1:
            words.append("a_1_m")
        for idx, (bp, bm) in enumerate(k[2]):
            j = idx + 1
            words.extend([f"b_{j}_p"] * bp)
            words.extend([f"b_{j}_m"] * bm)
        standard_form.append({"words": words, "coeff": coeff_str})

        # Build readable frappat string
        op_str = " ".join(w.replace("_p", "^+").replace("_m", "^-") for w in words)
        if not op_str:
            frappat_terms.append(coeff_str)
        else:
            if coeff == 1:
                frappat_terms.append(op_str)
            elif coeff == -1:
                frappat_terms.append(f"-{op_str}")
            else:
                frappat_terms.append(f"{coeff_str} {op_str}")

    frappat_form = " + ".join(frappat_terms).replace("+ -", "- ")
    return {
        "standard_form": standard_form,
        "frappat_form": frappat_form,
        "parity": parity_val
    }


def compute_structure_constants(n):
    """Compute the full structure constant dictionary and bracket list for C(n+1)."""
    even_basis, odd_basis, parity, gen_poly = build_basis_and_generators(n)
    all_gens = even_basis + odd_basis

    all_monomials = set()
    for g in all_gens:
        all_monomials.update(gen_poly[g].terms.keys())
    sorted_monomials = sorted(list(all_monomials))

    M = sp.Matrix([[gen_poly[g].terms.get(m, 0) for g in all_gens] for m in sorted_monomials])

    structure_constants = []
    bracket_dict = {}

    for i, X in enumerate(all_gens):
        for j, Y in enumerate(all_gens):
            pX = parity[X]
            pY = parity[Y]
            pXY = (-1) ** (pX * pY)
            polyX = gen_poly[X]
            polyY = gen_poly[Y]
            # Graded bracket [X, Y} = X Y - (-1)^{pX pY} Y X
            poly_bracket = polyX * polyY - polyY * polyX * pXY

            if not poly_bracket.terms:
                continue

            v = sp.Matrix([poly_bracket.terms.get(m, 0) for m in sorted_monomials])
            c, _ = M.gauss_jordan_solve(v)

            for k, Z in enumerate(all_gens):
                val = c[k]
                if val != 0:
                    coeff_frac = Fraction(int(val.p), int(val.q)) if isinstance(val, sp.Rational) else Fraction(val)
                    coeff_str = format_fraction(coeff_frac)
                    structure_constants.append({
                        "X": X,
                        "Y": Y,
                        "Z": Z,
                        "coeff": coeff_str,
                        "sign_rule": "graded"
                    })
                    bracket_dict[(X, Y, Z)] = coeff_frac

    return even_basis, odd_basis, parity, gen_poly, structure_constants, bracket_dict


def generate_c_structure_json(n):
    """Build complete Schema 1 JSON object for C(n+1)."""
    even_basis, odd_basis, parity, gen_poly, structure_constants, _ = compute_structure_constants(n)

    dim_even = 2 * n**2 + n + 1
    dim_odd = 4 * n
    dim_total = dim_even + dim_odd

    boson_labels = []
    for k in range(1, n + 1):
        boson_labels.extend([f"b_{k}_p", f"b_{k}_m"])

    realizations = {}
    for g in even_basis + odd_basis:
        realizations[g] = poly_to_realization_entry(gen_poly[g], g, parity[g], n)

    data = {
        "schema_version": "5.0",
        "algebra": {
            "family": "C",
            "m": 1,
            "n": n,
            "cartan_type": f"C({n+1})",
            "alternative_notation": {
                "osp": f"osp(2|{2*n})",
                "dimension_formula": "osp(2m|2n) with m=1"
            },
            "dimension": {
                "total": dim_total,
                "even": dim_even,
                "odd": dim_odd
            },
            "dimension_formulas": {
                "even": "2n^2 + n + 1",
                "odd": "4n",
                "total": "2n^2 + 5n + 1"
            }
        },
        "oscillator_generators": {
            "fermions": {
                "count": 2,
                "m": 1,
                "labels": ["a_1_p", "a_1_m"],
                "description": "Standard CAR fermionic oscillator pair a_1^±"
            },
            "bosons": {
                "count": 2 * n,
                "n": n,
                "labels": boson_labels,
                "description": f"Bosonic oscillators b_j^± with j=1,...,{n}"
            }
        },
        "oscillator_relations": {
            "standard_fermion_anticommutators": {
                "description": "Canonical anticommutation relations (CAR) for fermions",
                "relations": {
                    "same_type": "{a_1^±, a_1^±} = 0",
                    "conjugate_pair": "{a_1^-, a_1^+} = 1"
                }
            },
            "bosonic_commutators": {
                "description": "Canonical commutation relations (CCR) for bosons",
                "relations": {
                    "same_type": "[b_i^±, b_j^±] = 0 for all i, j",
                    "conjugate_pair": "[b_i^-, b_j^+] = δ_{ij}"
                }
            },
            "mixed_commutators": {
                "boson_fermion": "[b_i^±, a_1^±] = 0"
            }
        },
        "central_elements": {
            "kappa": {
                "parity": 1,
                "nilpotent_order": 2,
                "description": "Odd central element generating the nilpotent extension (kappa^2 = 0)"
            },
            "K": {
                "parity": 0,
                "description": "Even central identity element (K = 1 in standard realization)"
            }
        },
        "basis": {
            "even": even_basis,
            "odd": odd_basis,
            "ordering_convention": "PBW: κ < [odd] < [even]"
        },
        "parity": parity,
        "generator_realization": {
            "description": "Standard form with PBW oscillator ordering",
            "ordering": "a_1_p, a_1_m, " + ", ".join(boson_labels),
            "realizations": realizations
        },
        "structure_constants": structure_constants,
        "metadata": {
            "generated_by": "src/C_generators.py",
            "generation_date": "2026-10-04",
            "references": [
                "Frappat et al. (2000), Dictionary on Lie Algebras and Superalgebras, arXiv:hep-th/9607161",
                "Bakalov and Sullivan (2017)"
            ]
        }
    }
    return data


def generate_all_files(output_dir="data"):
    os.makedirs(output_dir, exist_ok=True)
    for n in [1, 2, 3]:
        data = generate_c_structure_json(n)
        filepath = os.path.join(output_dir, f"C_{n}_structure.json")
        with open(filepath, "w") as f:
            json.dump(data, f, indent=2)
        print(f"Generated {filepath} (even={len(data['basis']['even'])}, odd={len(data['basis']['odd'])}, non-zero brackets={len(data['structure_constants'])})")


if __name__ == "__main__":
    generate_all_files()
