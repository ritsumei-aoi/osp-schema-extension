"""
C_generators.py: Generator script for C(n+1) = osp(2|2n) Lie superalgebras.
Computes basis, parity, oscillator realization, and graded structure constants.
"""

from fractions import Fraction
from collections import defaultdict
import itertools
import math
import sympy
from datetime import datetime


class Monomial:
    """Normal-ordered oscillator monomial:
    (a_1^+)^{fp} (a_1^-)^{fm} * prod_{k=1}^n (b_k^+)^{bp[k-1]} (b_k^-)^{bm[k-1]}
    """
    def __init__(self, fp, fm, bp, bm):
        self.fp = fp
        self.fm = fm
        self.bp = tuple(bp)
        self.bm = tuple(bm)
        self.n = len(self.bp)

    @property
    def parity(self):
        return (self.fp + self.fm) % 2

    def __eq__(self, other):
        return (self.fp, self.fm, self.bp, self.bm) == (other.fp, other.fm, other.bp, other.bm)

    def __hash__(self):
        return hash((self.fp, self.fm, self.bp, self.bm))

    def to_words(self):
        words = []
        if self.fp:
            words.append("a_1_p")
        if self.fm:
            words.append("a_1_m")
        for k in range(self.n):
            for _ in range(self.bp[k]):
                words.append(f"b_{k+1}_p")
            for _ in range(self.bm[k]):
                words.append(f"b_{k+1}_m")
        return words


def mul_fermions(f1p, f1m, f2p, f2m):
    if f1m == 0:
        if f1p == 1 and f2p == 1:
            return []
        return [((f1p + f2p, f2m), Fraction(1))]
    if f2p == 0:
        if f2m == 1:
            return []
        return [((f1p, 1), Fraction(1))]
    res = [((f1p, f2m), Fraction(1))]
    if f1p == 0 and f2m == 0:
        res.append(((1, 1), Fraction(-1)))
    return res


def mul_boson_mode(u1, v1, u2, v2):
    res = []
    max_r = min(u2, v1)
    for r in range(max_r + 1):
        coeff = Fraction(math.factorial(r) * math.comb(v1, r) * math.comb(u2, r))
        res.append(((u1 + u2 - r, v1 - r + v2), coeff))
    return res


def mul_monomials(m1, m2):
    ferm_terms = mul_fermions(m1.fp, m1.fm, m2.fp, m2.fm)
    boson_modes = []
    for k in range(m1.n):
        u1, v1 = m1.bp[k], m1.bm[k]
        u2, v2 = m2.bp[k], m2.bm[k]
        boson_modes.append(mul_boson_mode(u1, v1, u2, v2))

    total_terms = []
    for f_mono, f_coeff in ferm_terms:
        for b_comb in itertools.product(*boson_modes):
            b_coeff = Fraction(1)
            bp = []
            bm = []
            for (uk, vk), ck in b_comb:
                b_coeff *= ck
                bp.append(uk)
                bm.append(vk)
            total_terms.append((Monomial(f_mono[0], f_mono[1], bp, bm), f_coeff * b_coeff))
    return total_terms


class Poly:
    """Polynomial element of the oscillator algebra."""
    def __init__(self, terms=None, n=1):
        self.n = n
        self.terms = defaultdict(Fraction)
        if terms:
            for m, c in terms.items():
                c = Fraction(c)
                if c != 0:
                    self.terms[m] += c
            self.terms = defaultdict(Fraction, {m: c for m, c in self.terms.items() if c != 0})

    @classmethod
    def from_osc(cls, name, n):
        bp = [0] * n
        bm = [0] * n
        fp, fm = 0, 0
        if name == "a_1_p":
            fp = 1
        elif name == "a_1_m":
            fm = 1
        elif name.startswith("b_"):
            parts = name.split("_")
            k = int(parts[1]) - 1
            if parts[2] == "p":
                bp[k] = 1
            else:
                bm[k] = 1
        return cls({Monomial(fp, fm, bp, bm): Fraction(1)}, n=n)

    @classmethod
    def const(cls, val, n):
        m = Monomial(0, 0, (0,) * n, (0,) * n)
        return cls({m: Fraction(val)}, n=n)

    def __add__(self, other):
        res = defaultdict(Fraction, self.terms)
        for m, c in other.terms.items():
            res[m] += c
        return Poly({m: c for m, c in res.items() if c != 0}, n=self.n)

    def __sub__(self, other):
        return self + (other * Fraction(-1))

    def __mul__(self, other):
        if isinstance(other, (int, Fraction)):
            if other == 0:
                return Poly(n=self.n)
            return Poly({m: c * Fraction(other) for m, c in self.terms.items()}, n=self.n)
        elif isinstance(other, Poly):
            res = defaultdict(Fraction)
            for m1, c1 in self.terms.items():
                for m2, c2 in other.terms.items():
                    prod_terms = mul_monomials(m1, m2)
                    for pm, pc in prod_terms:
                        res[pm] += c1 * c2 * pc
            return Poly({m: c for m, c in res.items() if c != 0}, n=self.n)

    def __rmul__(self, other):
        return self.__mul__(other)


def graded_bracket(X_poly, pX, Y_poly, pY):
    """Graded Lie bracket [X, Y} = XY - (-1)^{pX * pY} YX."""
    sign = -1 if (pX * pY) % 2 == 1 else 1
    return X_poly * Y_poly - Y_poly * X_poly * sign


def build_c_generators(n):
    """Build basis, parity, polynomial representations, and text descriptions for C(n+1)."""
    ap = Poly.from_osc("a_1_p", n)
    am = Poly.from_osc("a_1_m", n)
    bps = [Poly.from_osc(f"b_{k+1}_p", n) for k in range(n)]
    bms = [Poly.from_osc(f"b_{k+1}_m", n) for k in range(n)]

    generators = {}
    parities = {}
    frappat_forms = {}

    # 1. Cartan
    # H_1 = a_1^+ a_1^- + b_1^+ b_1^-
    generators["H_1"] = ap * am + bps[0] * bms[0]
    parities["H_1"] = 0
    frappat_forms["H_1"] = "a_1^+ a_1^- + b_1^+ b_1^-"

    for k in range(2, n + 1):
        generators[f"H_{k}"] = bps[k-2] * bms[k-2] - bps[k-1] * bms[k-1]
        parities[f"H_{k}"] = 0
        frappat_forms[f"H_{k}"] = f"b_{k-1}^+ b_{k-1}^- - b_{k}^+ b_{k}^-"

    generators[f"H_{n+1}"] = bps[n-1] * bms[n-1] * Fraction(-1) - Poly.const(Fraction(1, 2), n)
    parities[f"H_{n+1}"] = 0
    frappat_forms[f"H_{n+1}"] = f"-b_{n}^+ b_{n}^- - 1/2"

    even_cartan = [f"H_{k}" for k in range(1, n + 2)]

    # 2. Long even roots
    even_long_p = []
    even_long_m = []
    for k in range(1, n + 1):
        name_p = f"E_2del{k}_p"
        name_m = f"E_2del{k}_m"
        generators[name_p] = bps[k-1] * bps[k-1]
        generators[name_m] = bms[k-1] * bms[k-1]
        parities[name_p] = 0
        parities[name_m] = 0
        frappat_forms[name_p] = f"(b_{k}^+)^2"
        frappat_forms[name_m] = f"(b_{k}^-)^2"
        even_long_p.append(name_p)
        even_long_m.append(name_m)

    # 3. Short even roots
    even_short = []
    for i in range(1, n + 1):
        for j in range(i + 1, n + 1):
            pp = f"E_del{i}_del{j}_pp"
            mm = f"E_del{i}_del{j}_mm"
            pm = f"E_del{i}_del{j}_pm"
            mp = f"E_del{i}_del{j}_mp"
            generators[pp] = bps[i-1] * bps[j-1]
            generators[mm] = bms[i-1] * bms[j-1]
            generators[pm] = bps[i-1] * bms[j-1]
            generators[mp] = bms[i-1] * bps[j-1]
            parities[pp] = 0
            parities[mm] = 0
            parities[pm] = 0
            parities[mp] = 0
            frappat_forms[pp] = f"b_{i}^+ b_{j}^+"
            frappat_forms[mm] = f"b_{i}^- b_{j}^-"
            frappat_forms[pm] = f"b_{i}^+ b_{j}^-"
            frappat_forms[mp] = f"b_{i}^- b_{j}^+"
            even_short.extend([pp, mm, pm, mp])

    even_basis = even_cartan + even_long_p + even_long_m + even_short

    # 4. Odd roots (Option A: Boson Mode Block Ordering)
    odd_basis = []
    for k in range(1, n + 1):
        pp = f"E_eps1_del{k}_pp"
        pm = f"E_eps1_del{k}_pm"
        mp = f"E_eps1_del{k}_mp"
        mm = f"E_eps1_del{k}_mm"
        generators[pp] = ap * bps[k-1]
        generators[pm] = ap * bms[k-1]
        generators[mp] = am * bps[k-1]
        generators[mm] = am * bms[k-1]
        for name in [pp, pm, mp, mm]:
            parities[name] = 1
            odd_basis.append(name)
        frappat_forms[pp] = f"a_1^+ b_{k}^+"
        frappat_forms[pm] = f"a_1^+ b_{k}^-"
        frappat_forms[mp] = f"a_1^- b_{k}^+"
        frappat_forms[mm] = f"a_1^- b_{k}^-"

    return {
        "even_basis": even_basis,
        "odd_basis": odd_basis,
        "generators": generators,
        "parities": parities,
        "frappat_forms": frappat_forms
    }


def decompose_in_basis(poly, basis_list, generators):
    all_monos = set()
    for b in basis_list:
        all_monos.update(generators[b].terms.keys())
    all_monos = sorted(list(all_monos), key=lambda m: (m.fp, m.fm, m.bp, m.bm))
    mono_to_idx = {m: i for i, m in enumerate(all_monos)}

    for m in poly.terms.keys():
        if m not in mono_to_idx:
            return None

    M = sympy.zeros(len(all_monos), len(basis_list))
    for col, b in enumerate(basis_list):
        for m, coeff in generators[b].terms.items():
            M[mono_to_idx[m], col] = sympy.Rational(coeff.numerator, coeff.denominator)

    v = sympy.zeros(len(all_monos), 1)
    for m, coeff in poly.terms.items():
        v[mono_to_idx[m], 0] = sympy.Rational(coeff.numerator, coeff.denominator)

    try:
        sol, params = M.gauss_jordan_solve(v)
        residual = M * sol - v
        if any(r != 0 for r in residual):
            return None
        res = {}
        for col, b in enumerate(basis_list):
            val = sol[col]
            if val != 0:
                res[b] = Fraction(int(val.p), int(val.q))
        return res
    except Exception:
        return None


def compute_structure_constants(n, data=None):
    """Compute all graded structure constants for C(n+1)."""
    if data is None:
        data = build_c_generators(n)
    full_basis = data["odd_basis"] + data["even_basis"]
    generators = data["generators"]
    parities = data["parities"]

    struct_consts = []
    for X in full_basis:
        for Y in full_basis:
            pX = parities[X]
            pY = parities[Y]
            br = graded_bracket(generators[X], pX, generators[Y], pY)
            if not br.terms:
                continue
            decomp = decompose_in_basis(br, full_basis, generators)
            if decomp is None:
                raise ValueError(f"Bracket [{X}, {Y}] does not close in basis!")
            for Z in full_basis:
                if Z in decomp:
                    coeff = decomp[Z]
                    coeff_str = str(coeff.numerator) if coeff.denominator == 1 else f"{coeff.numerator}/{coeff.denominator}"
                    struct_consts.append({
                        "X": X,
                        "Y": Y,
                        "Z": Z,
                        "coeff": coeff_str,
                        "sign_rule": "graded"
                    })
    return struct_consts


def generate_schema_1_dict(n):
    """Generate complete Schema 1 dict conforming to json_schema_specification.md."""
    data = build_c_generators(n)
    even_basis = data["even_basis"]
    odd_basis = data["odd_basis"]
    full_basis = odd_basis + even_basis
    generators = data["generators"]
    parities = data["parities"]
    frappat_forms = data["frappat_forms"]

    dim_even = 2 * n**2 + n + 1
    dim_odd = 4 * n
    dim_total = dim_even + dim_odd

    # Boson labels
    boson_labels = []
    for k in range(1, n + 1):
        boson_labels.extend([f"b_{k}_p", f"b_{k}_m"])

    # Oscillator ordering
    osc_ordering = ["a_1_p", "a_1_m"] + boson_labels

    # Generator realizations
    realizations = {}
    for name in full_basis:
        poly = generators[name]
        std_form = []
        # Sort terms by monomial
        sorted_terms = sorted(poly.terms.items(), key=lambda item: (item[0].fp, item[0].fm, item[0].bp, item[0].bm))
        for m, coeff in sorted_terms:
            c_str = str(coeff.numerator) if coeff.denominator == 1 else f"{coeff.numerator}/{coeff.denominator}"
            std_form.append({
                "words": m.to_words(),
                "coeff": c_str
            })
        realizations[name] = {
            "standard_form": std_form,
            "frappat_form": frappat_forms[name],
            "parity": parities[name]
        }

    struct_consts = compute_structure_constants(n, data)

    schema1 = {
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
                "odd": dim_odd,
                "formulas": {
                    "even": "2*n^2 + n + 1",
                    "odd": "4*n",
                    "total": "2*n^2 + 5*n + 1"
                }
            }
        },
        "central_elements": {
            "kappa": {
                "label": "kappa",
                "parity": 1,
                "nilpotent": True,
                "relation": "kappa^2 = 0",
                "description": "Odd central extension parameter for inhomogeneous deformation; acts trivially on g"
            },
            "K": {
                "label": "K",
                "parity": 0,
                "scalar_value": 1,
                "description": "Central identity element; identified with scalar 1 and excluded from PBW basis"
            }
        },
        "oscillator_generators": {
            "fermions": {
                "count": 2,
                "m": 1,
                "labels": ["a_1_p", "a_1_m"],
                "description": "Standard CAR fermionic pair a_1^± with parity 1"
            },
            "bosons": {
                "count": 2 * n,
                "n": n,
                "labels": boson_labels,
                "description": f"Bosonic CCR oscillators b_i^± with i=1,...,{n} and parity 0"
            }
        },
        "oscillator_relations": {
            "standard_fermion_anticommutators": {
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
                "boson_fermion": "[b_i^±, a_1^±] = 0 (undeformed)"
            }
        },
        "basis": {
            "even": even_basis,
            "odd": odd_basis,
            "ordering_convention": "PBW: kappa < [odd: Mode Block (eps1_del{k}_pp/pm/mp/mm)] < [even: Cartan, Long roots, Short roots] (K = 1 is excluded)"
        },
        "parity": {name: parities[name] for name in full_basis},
        "generator_realization": {
            "description": "Standard form with PBW ordering",
            "ordering": ", ".join(osc_ordering),
            "realizations": realizations
        },
        "structure_constants": struct_consts,
        "metadata": {
            "generated_by": "src/C_generators.py",
            "generation_date": datetime.now().strftime("%Y-%m-%d"),
            "references": [
                "Frappat et al. (2000), Dictionary on Lie Algebras and Superalgebras",
                "Bakalov and Sullivan (2017)"
            ]
        }
    }
    return schema1
