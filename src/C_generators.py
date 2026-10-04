"""
C_generators.py: Generator for C(n+1) = osp(2|2n) Lie superalgebra structures.
Computes basis, oscillator realizations, and structure constants for Schema 1 v5.0.
"""

from fractions import Fraction
import json
import os
from typing import Dict, List, Tuple, Any


class OscillatorMonomial:
    """
    Represents a normal-ordered monomial:
    (a_1_p)^ap * (a_1_m)^am * prod_k (b_k_p)^bp_k * (b_k_m)^bm_k
    where ap, am in {0, 1} and bp_k, bm_k in Non-negative integers.
    """
    def __init__(self, n: int, ap: int = 0, am: int = 0, bp: Tuple[int, ...] = None, bm: Tuple[int, ...] = None):
        self.n = n
        self.ap = ap
        self.am = am
        self.bp = bp if bp is not None else tuple(0 for _ in range(n))
        self.bm = bm if bm is not None else tuple(0 for _ in range(n))

    def __key(self):
        return (self.n, self.ap, self.am, self.bp, self.bm)

    def __hash__(self):
        return hash(self.__key())

    def __eq__(self, other):
        return isinstance(other, OscillatorMonomial) and self.__key() == other.__key()

    def __lt__(self, other):
        return self.__key() < other.__key()

    def is_zero(self) -> bool:
        return self.ap > 1 or self.am > 1

    def words_list(self) -> List[str]:
        words = []
        if self.ap > 0:
            words.extend(["a_1_p"] * self.ap)
        if self.am > 0:
            words.extend(["a_1_m"] * self.am)
        for k in range(self.n):
            if self.bp[k] > 0:
                words.extend([f"b_{k+1}_p"] * self.bp[k])
            if self.bm[k] > 0:
                words.extend([f"b_{k+1}_m"] * self.bm[k])
        return words


class OscillatorPoly:
    """
    Linear combination of normal-ordered OscillatorMonomials with Fraction coefficients.
    """
    def __init__(self, n: int, terms: Dict[OscillatorMonomial, Fraction] = None):
        self.n = n
        self.terms: Dict[OscillatorMonomial, Fraction] = {}
        if terms:
            for mon, coeff in terms.items():
                if coeff != 0 and not mon.is_zero():
                    self.terms[mon] = self.terms.get(mon, Fraction(0)) + Fraction(coeff)
                    if self.terms[mon] == 0:
                        del self.terms[mon]

    def __add__(self, other: 'OscillatorPoly') -> 'OscillatorPoly':
        assert self.n == other.n
        new_terms = dict(self.terms)
        for mon, coeff in other.terms.items():
            new_terms[mon] = new_terms.get(mon, Fraction(0)) + coeff
        return OscillatorPoly(self.n, new_terms)

    def __sub__(self, other: 'OscillatorPoly') -> 'OscillatorPoly':
        return self + (other * Fraction(-1))

    def __mul__(self, other) -> 'OscillatorPoly':
        if isinstance(other, (int, Fraction)):
            if other == 0:
                return OscillatorPoly(self.n)
            return OscillatorPoly(self.n, {mon: coeff * Fraction(other) for mon, coeff in self.terms.items()})
        elif isinstance(other, OscillatorPoly):
            assert self.n == other.n
            res = OscillatorPoly(self.n)
            for m1, c1 in self.terms.items():
                for m2, c2 in other.terms.items():
                    prod = multiply_monomials(m1, m2) * (c1 * c2)
                    res = res + prod
            return res
        else:
            raise TypeError(f"Unsupported operand type for *: {type(other)}")

    def __rmul__(self, other):
        return self * other

    def is_zero(self) -> bool:
        return len(self.terms) == 0

    def to_standard_form(self) -> List[Dict[str, Any]]:
        result = []
        for mon in sorted(self.terms.keys()):
            coeff = self.terms[mon]
            coeff_str = str(coeff.numerator) if coeff.denominator == 1 else f"{coeff.numerator}/{coeff.denominator}"
            result.append({
                "words": mon.words_list(),
                "coeff": coeff_str
            })
        return result


def multiply_monomials(m1: OscillatorMonomial, m2: OscillatorMonomial) -> OscillatorPoly:
    """
    Computes m1 * m2 and normal orders using CAR/CCR:
    - a_1_m a_1_p = 1 - a_1_p a_1_m, (a_1_p)^2 = 0, (a_1_m)^2 = 0
    - b_k_m b_k_p = b_k_p b_k_m + 1
    - all other pairs commute
    """
    n = m1.n
    # Fermionic part multiplication:
    # m1 has (a_1_p)^ap1 (a_1_m)^am1
    # m2 has (a_1_p)^ap2 (a_1_m)^am2
    # Product is (a_1_p)^ap1 * (a_1_m)^am1 * (a_1_p)^ap2 * (a_1_m)^am2
    fermion_terms: List[Tuple[int, int, Fraction]] = []
    if m1.am == 0:
        ap = m1.ap + m2.ap
        am = m2.am
        if ap <= 1 and am <= 1:
            fermion_terms.append((ap, am, Fraction(1)))
    elif m1.am == 1 and m2.ap == 0:
        ap = m1.ap
        am = 1 + m2.am
        if ap <= 1 and am <= 1:
            fermion_terms.append((ap, am, Fraction(1)))
    elif m1.am == 1 and m2.ap == 1:
        # am1 * ap2 = a_1_m a_1_p = 1 - a_1_p a_1_m
        # Term 1: (a_1_p)^ap1 * 1 * (a_1_m)^am2 = (a_1_p)^ap1 * (a_1_m)^am2
        # Term 2: (a_1_p)^ap1 * (- a_1_p a_1_m) * (a_1_m)^am2 = - (a_1_p)^(ap1+1) * (a_1_m)^(am2+1)
        ap_t1 = m1.ap
        am_t1 = m2.am
        if ap_t1 <= 1 and am_t1 <= 1:
            fermion_terms.append((ap_t1, am_t1, Fraction(1)))
        ap_t2 = m1.ap + 1
        am_t2 = m2.am + 1
        if ap_t2 <= 1 and am_t2 <= 1:
            fermion_terms.append((ap_t2, am_t2, Fraction(-1)))

    if not fermion_terms:
        return OscillatorPoly(n)

    # Bosonic part multiplication for each mode k=0..n-1:
    # m1 has (b_k_p)^bp1 (b_k_m)^bm1
    # m2 has (b_k_p)^bp2 (b_k_m)^bm2
    # We need to normal order (b_k_m)^bm1 * (b_k_p)^bp2
    # Using CCR: (b_m)^A (b_p)^B = sum_j j! * C(A,j) * C(B,j) * (b_p)^(B-j) * (b_m)^(A-j)
    def normal_order_boson_mode(bm1: int, bp2: int) -> List[Tuple[int, int, int]]:
        # returns list of (bp_out, bm_out, coeff)
        from math import comb, factorial
        res = []
        for j in range(min(bm1, bp2) + 1):
            c = factorial(j) * comb(bm1, j) * comb(bp2, j)
            res.append((bp2 - j, bm1 - j, c))
        return res

    boson_modes_res: List[List[Tuple[int, int, int]]] = []
    for k in range(n):
        boson_modes_res.append(normal_order_boson_mode(m1.bm[k], m2.bp[k]))

    # Combine all boson modes:
    import itertools
    combined_boson = []
    for prod_tuple in itertools.product(*boson_modes_res):
        c_prod = 1
        bp_out = []
        bm_out = []
        for k in range(n):
            mode_bp, mode_bm, mode_coeff = prod_tuple[k]
            c_prod *= mode_coeff
            bp_out.append(m1.bp[k] + mode_bp)
            bm_out.append(mode_bm + m2.bm[k])
        combined_boson.append((tuple(bp_out), tuple(bm_out), Fraction(c_prod)))

    poly_terms = {}
    for ap, am, f_coeff in fermion_terms:
        for bp_t, bm_t, b_coeff in combined_boson:
            mon = OscillatorMonomial(n, ap, am, bp_t, bm_t)
            coeff = f_coeff * b_coeff
            poly_terms[mon] = poly_terms.get(mon, Fraction(0)) + coeff

    return OscillatorPoly(n, poly_terms)


def make_single_monomial(n: int, ap: int = 0, am: int = 0, bp: Tuple[int, ...] = None, bm: Tuple[int, ...] = None) -> OscillatorPoly:
    mon = OscillatorMonomial(n, ap, am, bp, bm)
    return OscillatorPoly(n, {mon: Fraction(1)})


def get_C_generators(n: int) -> Tuple[List[str], List[str], Dict[str, int], Dict[str, OscillatorPoly], Dict[str, str]]:
    """
    Returns (even_basis, odd_basis, parity_dict, realizations_dict, frappat_form_dict)
    following PBW ordering.
    """
    even_basis = []
    odd_basis = []
    parity = {}
    realizations = {}
    frappat_forms = {}

    # 1. Odd basis: E_eps1_del{k}_{pp, pm, mp, mm}
    for k in range(1, n + 1):
        idx = k - 1
        # pp: a_1_p * b_k_p
        bp_k = tuple(1 if i == idx else 0 for i in range(n))
        bm_0 = tuple(0 for _ in range(n))
        gen_pp = f"E_eps1_del{k}_pp"
        odd_basis.append(gen_pp)
        parity[gen_pp] = 1
        realizations[gen_pp] = make_single_monomial(n, ap=1, am=0, bp=bp_k, bm=bm_0)
        frappat_forms[gen_pp] = f"a_1^+ b_{k}^+"

        # pm: a_1_p * b_k_m
        bm_k = tuple(1 if i == idx else 0 for i in range(n))
        gen_pm = f"E_eps1_del{k}_pm"
        odd_basis.append(gen_pm)
        parity[gen_pm] = 1
        realizations[gen_pm] = make_single_monomial(n, ap=1, am=0, bp=bm_0, bm=bm_k)
        frappat_forms[gen_pm] = f"a_1^+ b_{k}^-"

        # mp: a_1_m * b_k_p
        gen_mp = f"E_eps1_del{k}_mp"
        odd_basis.append(gen_mp)
        parity[gen_mp] = 1
        realizations[gen_mp] = make_single_monomial(n, ap=0, am=1, bp=bp_k, bm=bm_0)
        frappat_forms[gen_mp] = f"a_1^- b_{k}^+"

        # mm: a_1_m * b_k_m
        gen_mm = f"E_eps1_del{k}_mm"
        odd_basis.append(gen_mm)
        parity[gen_mm] = 1
        realizations[gen_mm] = make_single_monomial(n, ap=0, am=1, bp=bm_0, bm=bm_k)
        frappat_forms[gen_mm] = f"a_1^- b_{k}^-"

    # 2. Even basis:
    # 2.1 Cartans: H_1, ..., H_{n+1}
    # H_1 = a_1^+ a_1^- + b_1^+ b_1^-
    bp_1 = tuple(1 if i == 0 else 0 for i in range(n))
    bm_1 = tuple(1 if i == 0 else 0 for i in range(n))
    h1_poly = make_single_monomial(n, ap=1, am=1) + make_single_monomial(n, ap=0, am=0, bp=bp_1, bm=bm_1)
    even_basis.append("H_1")
    parity["H_1"] = 0
    realizations["H_1"] = h1_poly
    frappat_forms["H_1"] = "a_1^+ a_1^- + b_1^+ b_1^-"

    for k in range(2, n + 1):
        gen_hk = f"H_{k}"
        bp_km1 = tuple(1 if i == k - 2 else 0 for i in range(n))
        bm_km1 = tuple(1 if i == k - 2 else 0 for i in range(n))
        bp_k = tuple(1 if i == k - 1 else 0 for i in range(n))
        bm_k = tuple(1 if i == k - 1 else 0 for i in range(n))
        hk_poly = make_single_monomial(n, bp=bp_km1, bm=bm_km1) - make_single_monomial(n, bp=bp_k, bm=bm_k)
        even_basis.append(gen_hk)
        parity[gen_hk] = 0
        realizations[gen_hk] = hk_poly
        frappat_forms[gen_hk] = f"b_{k-1}^+ b_{k-1}^- - b_{k}^+ b_{k}^-"

    # H_{n+1} = - b_n^+ b_n^- - 1/2
    gen_hn1 = f"H_{n+1}"
    bp_n = tuple(1 if i == n - 1 else 0 for i in range(n))
    bm_n = tuple(1 if i == n - 1 else 0 for i in range(n))
    hn1_poly = (make_single_monomial(n, bp=bp_n, bm=bm_n) * -1) + (make_single_monomial(n) * Fraction(-1, 2))
    even_basis.append(gen_hn1)
    parity[gen_hn1] = 0
    realizations[gen_hn1] = hn1_poly
    frappat_forms[gen_hn1] = f"-b_{n}^+ b_{n}^- - 1/2"

    # 2.2 Positive long roots E_2del{k}_p = (b_k^+)^2
    for k in range(1, n + 1):
        gen = f"E_2del{k}_p"
        bp_2k = tuple(2 if i == k - 1 else 0 for i in range(n))
        even_basis.append(gen)
        parity[gen] = 0
        realizations[gen] = make_single_monomial(n, bp=bp_2k)
        frappat_forms[gen] = f"(b_{k}^+)^2"

    # 2.3 Positive cross roots E_del{i}_del{j}_pp = b_i^+ b_j^+ (1 <= i < j <= n)
    for i in range(1, n + 1):
        for j in range(i + 1, n + 1):
            gen = f"E_del{i}_del{j}_pp"
            bp_ij = tuple(1 if (x == i - 1 or x == j - 1) else 0 for x in range(n))
            even_basis.append(gen)
            parity[gen] = 0
            realizations[gen] = make_single_monomial(n, bp=bp_ij)
            frappat_forms[gen] = f"b_{i}^+ b_{j}^+"

    # 2.4 Negative long roots E_2del{k}_m = (b_k^-)^2
    for k in range(1, n + 1):
        gen = f"E_2del{k}_m"
        bm_2k = tuple(2 if i == k - 1 else 0 for i in range(n))
        even_basis.append(gen)
        parity[gen] = 0
        realizations[gen] = make_single_monomial(n, bm=bm_2k)
        frappat_forms[gen] = f"(b_{k}^-)^2"

    # 2.5 Negative cross roots E_del{i}_del{j}_mm = b_i^- b_j^- (1 <= i < j <= n)
    for i in range(1, n + 1):
        for j in range(i + 1, n + 1):
            gen = f"E_del{i}_del{j}_mm"
            bm_ij = tuple(1 if (x == i - 1 or x == j - 1) else 0 for x in range(n))
            even_basis.append(gen)
            parity[gen] = 0
            realizations[gen] = make_single_monomial(n, bm=bm_ij)
            frappat_forms[gen] = f"b_{i}^- b_{j}^-"

    # 2.6 Mixed cross roots E_del{i}_del{j}_pm = b_i^+ b_j^-, E_del{i}_del{j}_mp = b_i^- b_j^+ (1 <= i < j <= n)
    for i in range(1, n + 1):
        for j in range(i + 1, n + 1):
            gen_pm = f"E_del{i}_del{j}_pm"
            bp_i = tuple(1 if x == i - 1 else 0 for x in range(n))
            bm_j = tuple(1 if x == j - 1 else 0 for x in range(n))
            even_basis.append(gen_pm)
            parity[gen_pm] = 0
            realizations[gen_pm] = make_single_monomial(n, bp=bp_i, bm=bm_j)
            frappat_forms[gen_pm] = f"b_{i}^+ b_{j}^-"

            gen_mp = f"E_del{i}_del{j}_mp"
            bm_i = tuple(1 if x == i - 1 else 0 for x in range(n))
            bp_j = tuple(1 if x == j - 1 else 0 for x in range(n))
            even_basis.append(gen_mp)
            parity[gen_mp] = 0
            realizations[gen_mp] = make_single_monomial(n, bp=bp_j, bm=bm_i)
            frappat_forms[gen_mp] = f"b_{i}^- b_{j}^+"

    return even_basis, odd_basis, parity, realizations, frappat_forms


def compute_graded_commutator(poly_x: OscillatorPoly, poly_y: OscillatorPoly, px: int, py: int) -> OscillatorPoly:
    """
    [X, Y} = X Y - (-1)^{px * py} Y X
    """
    sign = -1 if (px == 1 and py == 1) else 1
    term1 = poly_x * poly_y
    term2 = (poly_y * poly_x) * Fraction(sign)
    return term1 - term2


def decompose_in_basis(poly: OscillatorPoly, basis: List[str], realizations: Dict[str, OscillatorPoly], parity_dict: Dict[str, int]) -> Dict[str, Fraction]:
    """
    Decomposes an element of the Lie superalgebra into basis elements.
    Solves linear combination poly = sum c_i * realizations[Z_i].
    """
    if poly.is_zero():
        return {}

    # Get all monomials present in poly and candidate basis elements
    all_monomials = set(poly.terms.keys())
    for name in basis:
        for mon in realizations[name].terms.keys():
            all_monomials.add(mon)

    sorted_monomials = sorted(all_monomials)
    mon_to_idx = {m: i for i, m in enumerate(sorted_monomials)}

    import numpy as np
    num_mons = len(sorted_monomials)
    num_basis = len(basis)

    A = np.zeros((num_mons, num_basis), dtype=float)
    b = np.zeros(num_mons, dtype=float)

    for j, name in enumerate(basis):
        for mon, coeff in realizations[name].terms.items():
            A[mon_to_idx[mon], j] = float(coeff)

    for mon, coeff in poly.terms.items():
        b[mon_to_idx[mon]] = float(coeff)

    # Solve least squares / linear system
    coeffs, residuals, rank, s = np.linalg.lstsq(A, b, rcond=None)

    # Verify and convert to Fraction
    result = {}
    reconstructed = OscillatorPoly(poly.n)
    for j, name in enumerate(basis):
        c_val = coeffs[j]
        # Round to nearest simple fraction
        if abs(c_val) > 1e-7:
            # check small integer / simple fraction
            frac = Fraction(c_val).limit_denominator(120)
            if abs(float(frac) - c_val) > 1e-5:
                raise ValueError(f"Could not convert coefficient {c_val} to exact fraction for {name}")
            result[name] = frac
            reconstructed = reconstructed + (realizations[name] * frac)

    diff = poly - reconstructed
    if not diff.is_zero():
        raise ValueError(f"Polynomial could not be decomposed in basis! Diff: {diff.terms}")

    return result


def generate_structure_constants(n: int) -> List[Dict[str, Any]]:
    even_basis, odd_basis, parity, realizations, _ = get_C_generators(n)
    all_basis = odd_basis + even_basis  # PBW ordering: odd < even

    structure_constants = []
    for x_name in all_basis:
        px = parity[x_name]
        poly_x = realizations[x_name]
        for y_name in all_basis:
            py = parity[y_name]
            poly_y = realizations[y_name]

            comm = compute_graded_commutator(poly_x, poly_y, px, py)
            if not comm.is_zero():
                decomp = decompose_in_basis(comm, all_basis, realizations, parity)
                for z_name, coeff in decomp.items():
                    coeff_str = str(coeff.numerator) if coeff.denominator == 1 else f"{coeff.numerator}/{coeff.denominator}"
                    structure_constants.append({
                        "X": x_name,
                        "Y": y_name,
                        "Z": z_name,
                        "coeff": coeff_str,
                        "sign_rule": "graded"
                    })

    return structure_constants


def build_schema_1_json(n: int) -> Dict[str, Any]:
    even_basis, odd_basis, parity, realizations, frappat_forms = get_C_generators(n)
    total_dim = (2 * n * n + n + 1) + (4 * n)

    boson_labels = []
    for k in range(1, n + 1):
        boson_labels.extend([f"b_{k}_p", f"b_{k}_m"])

    sc = generate_structure_constants(n)

    realizations_json = {}
    all_basis = odd_basis + even_basis
    for gen in all_basis:
        realizations_json[gen] = {
            "standard_form": realizations[gen].to_standard_form(),
            "frappat_form": frappat_forms[gen],
            "parity": parity[gen]
        }

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
                "total": total_dim,
                "even": 2 * n * n + n + 1,
                "odd": 4 * n,
                "formula": {
                    "even": "2*n^2 + n + 1",
                    "odd": "4*n",
                    "total": "2*n^2 + 5*n + 1"
                }
            }
        },
        "central_elements": {
            "K": {
                "label": "K",
                "parity": 0,
                "description": "Even central element, identified with scalar 1 in oscillator algebra"
            },
            "kappa": {
                "label": "kappa",
                "parity": 1,
                "description": "Odd central nilpotent parameter (kappa^2 = 0) governing deformation"
            }
        },
        "oscillator_generators": {
            "fermions": {
                "count": 2,
                "m": 1,
                "labels": ["a_1_p", "a_1_m"],
                "description": "Standard fermionic CAR pair a_1^± with parity 1"
            },
            "bosons": {
                "count": 2 * n,
                "n": n,
                "labels": boson_labels,
                "description": f"Bosonic oscillators b_k^± with k=1,...,{n} and parity 0"
            }
        },
        "oscillator_relations": {
            "fermionic_anticommutators": {
                "description": "Canonical anticommutation relations (CAR) for fermionic oscillators",
                "relations": {
                    "conjugate_pair": "{a_1^-, a_1^+} = 1",
                    "nilpotency": "(a_1^+)^2 = 0, (a_1^-)^2 = 0"
                }
            },
            "bosonic_commutators": {
                "description": "Canonical commutation relations (CCR) for bosonic oscillators",
                "relations": {
                    "same_type": "[b_i^±, b_j^±] = 0 for all i, j",
                    "conjugate_pair": "[b_i^-, b_j^+] = δ_{ij}"
                }
            },
            "mixed_commutators": {
                "description": "Undeformed commutation relations between bosons and fermions",
                "relations": {
                    "boson_fermion": "[b_i^±, a_1^±] = 0"
                }
            }
        },
        "basis": {
            "even": even_basis,
            "odd": odd_basis,
            "ordering_convention": "PBW: κ < [odd] < [even]  (K = 1 is excluded)"
        },
        "parity": parity,
        "generator_realization": {
            "description": "Standard form with PBW ordering",
            "ordering": "a_1_p, a_1_m, " + ", ".join(boson_labels),
            "realizations": realizations_json
        },
        "structure_constants": sc,
        "metadata": {
            "generated_by": "C_generators.py",
            "generation_date": "2026-10-04",
            "references": [
                "Frappat et al. (2000), Dictionary on Lie Algebras and Superalgebras, arXiv:hep-th/9607161"
            ]
        }
    }
    return data


def generate_and_save_all(data_dir: str = "data"):
    os.makedirs(data_dir, exist_ok=True)
    for n in [1, 2, 3]:
        data = build_schema_1_json(n)
        filename = os.path.join(data_dir, f"C_{n}_structure.json")
        with open(filename, "w") as f:
            json.dump(data, f, indent=2)
        print(f"Generated {filename}: total_dim={data['algebra']['dimension']['total']}, structure_constants_count={len(data['structure_constants'])}")


if __name__ == "__main__":
    generate_and_save_all()
