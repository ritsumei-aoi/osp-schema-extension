"""
C_generators.py: Generator for C(n+1) = osp(2|2n) Lie superalgebra structure.
Generates Schema 1 JSON files for n=1, 2, 3.
"""

import json
from fractions import Fraction
from typing import Dict, List, Tuple, Any


class Monomial:
    """
    Normal-ordered monomial in the Weyl-Clifford algebra W(1|n).
    Ordering of operators:
    a_1_p, a_1_m, b_1_p, ..., b_n_p, b_1_m, ..., b_n_m
    Powers of a_1_p, a_1_m are in {0, 1}.
    Powers of b_k_p, b_k_m are in {0, 1, 2, ...}.
    """
    def __init__(self, a_p: int, a_m: int, b_p: Tuple[int, ...], b_m: Tuple[int, ...]):
        self.a_p = a_p
        self.a_m = a_m
        self.b_p = tuple(b_p)
        self.b_m = tuple(b_m)
        self.n = len(self.b_p)

    def is_zero(self) -> bool:
        return self.a_p > 1 or self.a_m > 1

    def __hash__(self):
        return hash((self.a_p, self.a_m, self.b_p, self.b_m))

    def __eq__(self, other):
        return (self.a_p, self.a_m, self.b_p, self.b_m) == (other.a_p, other.a_m, other.b_p, other.b_m)

    def __repr__(self):
        words = []
        if self.a_p:
            words.append("a_1_p")
        if self.a_m:
            words.append("a_1_m")
        for i, p in enumerate(self.b_p, 1):
            words.extend([f"b_{i}_p"] * p)
        for i, m in enumerate(self.b_m, 1):
            words.extend([f"b_{i}_m"] * m)
        return "*".join(words) if words else "1"

    def to_word_list(self) -> List[str]:
        words = []
        if self.a_p:
            words.append("a_1_p")
        if self.a_m:
            words.append("a_1_m")
        for i, p in enumerate(self.b_p, 1):
            words.extend([f"b_{i}_p"] * p)
        for i, m in enumerate(self.b_m, 1):
            words.extend([f"b_{i}_m"] * m)
        return words


class SuperElement:
    """
    Linear combination of normal-ordered monomials with rational coefficients.
    """
    def __init__(self, terms: Dict[Monomial, Fraction] = None):
        self.terms: Dict[Monomial, Fraction] = {}
        if terms:
            for m, coeff in terms.items():
                if not m.is_zero() and coeff != 0:
                    self.terms[m] = self.terms.get(m, Fraction(0)) + coeff
                    if self.terms[m] == Fraction(0):
                        del self.terms[m]

    @classmethod
    def zero(cls) -> 'SuperElement':
        return cls({})

    @classmethod
    def from_monomial(cls, m: Monomial, coeff: Fraction = Fraction(1)) -> 'SuperElement':
        if m.is_zero() or coeff == 0:
            return cls({})
        return cls({m: coeff})

    def __add__(self, other: 'SuperElement') -> 'SuperElement':
        res = dict(self.terms)
        for m, c in other.terms.items():
            res[m] = res.get(m, Fraction(0)) + c
        return SuperElement(res)

    def __sub__(self, other: 'SuperElement') -> 'SuperElement':
        res = dict(self.terms)
        for m, c in other.terms.items():
            res[m] = res.get(m, Fraction(0)) - c
        return SuperElement(res)

    def __mul__(self, scalar: Any) -> 'SuperElement':
        if isinstance(scalar, (int, Fraction)):
            c = Fraction(scalar)
            if c == 0:
                return SuperElement.zero()
            return SuperElement({m: v * c for m, v in self.terms.items()})
        raise NotImplementedError

    def __rmul__(self, scalar: Any) -> 'SuperElement':
        return self.__mul__(scalar)

    def is_zero(self) -> bool:
        return len(self.terms) == 0


def multiply_monomials(m1: Monomial, m2: Monomial) -> SuperElement:
    """
    Compute m1 * m2 using CAR and CCR normal ordering relations.
    CAR:
      a_1_m * a_1_p = 1 - a_1_p * a_1_m
      (a_1_p)^2 = 0, (a_1_m)^2 = 0
    CCR:
      b_k_m * b_k_p = b_k_p * b_k_m + 1
      [b_j, b_k] = 0 for j != k
      [a, b] = 0 (mixed)
    """
    n = m1.n
    # Fermionic sector:
    # m1 has (a_p1, a_m1), m2 has (a_p2, a_m2)
    # Total product is (a_1_p^a_p1 a_1_m^a_m1) * (a_1_p^a_p2 a_1_m^a_m2)
    fermion_terms: List[Tuple[int, int, Fraction]] = []
    
    # Case analysis for fermions:
    a_p1, a_m1 = m1.a_p, m1.a_m
    a_p2, a_m2 = m2.a_p, m2.a_m

    if a_p1 == 1 and a_p2 == 1:
        # a_1_p ... a_1_p = 0
        return SuperElement.zero()
    if a_m1 == 1 and a_m2 == 1 and a_p2 == 0:
        # a_1_m * a_1_m = 0
        return SuperElement.zero()

    if a_m1 == 0:
        # (a_1_p^a_p1) * (a_1_p^a_p2 a_1_m^a_m2)
        if a_p1 == 1 and a_p2 == 1:
            return SuperElement.zero()
        fermion_terms.append((a_p1 + a_p2, a_m2, Fraction(1)))
    else:
        # a_m1 == 1
        if a_p2 == 0:
            # (a_1_p^a_p1 a_1_m) * (a_1_m^a_m2)
            if a_m2 == 1:
                return SuperElement.zero()
            fermion_terms.append((a_p1, 1, Fraction(1)))
        else:
            # a_p2 == 1
            # (a_1_p^a_p1 a_1_m) * (a_1_p a_1_m^a_m2)
            # a_1_m * a_1_p = 1 - a_1_p * a_1_m
            # Term 1: 1 -> a_1_p^a_p1 * a_1_m^a_m2
            fermion_terms.append((a_p1, a_m2, Fraction(1)))
            # Term 2: - a_1_p * a_1_m -> - a_1_p^(a_p1+1) * a_1_m^(1+a_m2)
            if a_p1 == 0 and a_m2 == 0:
                fermion_terms.append((1, 1, Fraction(-1)))
            # If a_p1 == 1 or a_m2 == 1, (a_1_p)^2 or (a_1_m)^2 becomes 0

    # Bosonic sector:
    # For each mode k, we have (b_k_p^p1 b_k_m^m1) * (b_k_p^p2 b_k_m^m2)
    # We normal order b_k_m^m1 * b_k_p^p2 using CCR: b_m b_p = b_p b_m + 1
    # By Wick's theorem:
    # b_m^m1 b_p^p2 = sum_{r=0}^{min(m1, p2)} r! * binom(m1, r) * binom(p2, r) * b_p^(p2-r) b_m^(m1-r)
    import math

    mode_contributions: List[List[Tuple[int, int, Fraction]]] = []
    for k in range(n):
        p1, m_1_val = m1.b_p[k], m1.b_m[k]
        p2, m_2_val = m2.b_p[k], m2.b_m[k]

        terms_k = []
        max_r = min(m_1_val, p2)
        for r in range(max_r + 1):
            c = math.factorial(r) * math.comb(m_1_val, r) * math.comb(p2, r)
            terms_k.append((p1 + p2 - r, m_1_val + m_2_val - r, Fraction(c)))
        mode_contributions.append(terms_k)

    # Combine all bosonic modes by Cartesian product
    from itertools import product
    boson_terms: List[Tuple[Tuple[int, ...], Tuple[int, ...], Fraction]] = []
    for comb in product(*mode_contributions):
        # comb has n elements: (p_k, m_k, coeff_k)
        b_p = tuple(item[0] for item in comb)
        b_m = tuple(item[1] for item in comb)
        coeff = Fraction(1)
        for item in comb:
            coeff *= item[2]
        boson_terms.append((b_p, b_m, coeff))

    # Combine fermionic and bosonic terms
    total_dict: Dict[Monomial, Fraction] = {}
    for f_ap, f_am, f_c in fermion_terms:
        for b_p, b_m, b_c in boson_terms:
            m = Monomial(f_ap, f_am, b_p, b_m)
            c = f_c * b_c
            total_dict[m] = total_dict.get(m, Fraction(0)) + c

    return SuperElement(total_dict)


def multiply_elements(e1: SuperElement, e2: SuperElement) -> SuperElement:
    res = SuperElement.zero()
    for m1, c1 in e1.terms.items():
        for m2, c2 in e2.terms.items():
            prod = multiply_monomials(m1, m2)
            res = res + (prod * (c1 * c2))
    return res


def supercommutator(e1: SuperElement, p1: int, e2: SuperElement, p2: int) -> SuperElement:
    """
    [e1, e2} = e1*e2 - (-1)^(p1*p2) * e2*e1
    """
    sign = -1 if (p1 * p2 == 1) else 1
    prod1 = multiply_elements(e1, e2)
    prod2 = multiply_elements(e2, e1)
    return prod1 - (prod2 * sign)


class CSuperalgebra:
    """
    Builds basis, oscillator realizations, and structure constants for C(n+1) = osp(2|2n).
    """
    def __init__(self, n: int):
        self.n = n
        self.m = 1
        self.even_dim = 2 * n * n + n + 1
        self.odd_dim = 4 * n
        self.total_dim = 2 * n * n + 5 * n + 1

        self.basis_even: List[str] = []
        self.basis_odd: List[str] = []
        self.parity: Dict[str, int] = {}
        self.realizations: Dict[str, SuperElement] = {}
        self.frappat_forms: Dict[str, str] = {}
        self.standard_forms: Dict[str, List[Dict[str, Any]]] = {}

        self._build_basis_and_realizations()

    def _build_basis_and_realizations(self):
        n = self.n

        # 1. Cartan generators H_1, ..., H_{n+1}
        # H_1 = a_1^+ a_1^- + b_1^+ b_1^-
        h1_m_a = Monomial(1, 1, tuple([0]*n), tuple([0]*n))
        h1_bp = [0]*n
        h1_bm = [0]*n
        h1_bp[0] = 1
        h1_bm[0] = 1
        h1_m_b = Monomial(0, 0, tuple(h1_bp), tuple(h1_bm))
        self.realizations["H_1"] = SuperElement({h1_m_a: Fraction(1), h1_m_b: Fraction(1)})
        self.frappat_forms["H_1"] = "a_1^+ a_1^- + b_1^+ b_1^-"
        self.basis_even.append("H_1")
        self.parity["H_1"] = 0

        # H_k = b_{k-1}^+ b_{k-1}^- - b_k^+ b_k^- for 2 <= k <= n
        for k in range(2, n + 1):
            label = f"H_{k}"
            bp1, bm1 = [0]*n, [0]*n
            bp1[k-2] = 1
            bm1[k-2] = 1
            m1 = Monomial(0, 0, tuple(bp1), tuple(bm1))

            bp2, bm2 = [0]*n, [0]*n
            bp2[k-1] = 1
            bm2[k-1] = 1
            m2 = Monomial(0, 0, tuple(bp2), tuple(bm2))

            self.realizations[label] = SuperElement({m1: Fraction(1), m2: Fraction(-1)})
            self.frappat_forms[label] = f"b_{k-1}^+ b_{k-1}^- - b_{k}^+ b_{k}^-"
            self.basis_even.append(label)
            self.parity[label] = 0

        # H_{n+1} = -b_n^+ b_n^- - 1/2
        hn1_label = f"H_{n+1}"
        bpn, bmn = [0]*n, [0]*n
        bpn[n-1] = 1
        bmn[n-1] = 1
        mn = Monomial(0, 0, tuple(bpn), tuple(bmn))
        m_const = Monomial(0, 0, tuple([0]*n), tuple([0]*n))
        self.realizations[hn1_label] = SuperElement({mn: Fraction(-1), m_const: Fraction(-1, 2)})
        self.frappat_forms[hn1_label] = f"-b_{n}^+ b_{n}^- - 1/2"
        self.basis_even.append(hn1_label)
        self.parity[hn1_label] = 0

        # 2. Long even roots: E_2del{k}_p and E_2del{k}_m
        for k in range(1, n + 1):
            label_p = f"E_2del{k}_p"
            bp = [0]*n
            bp[k-1] = 2
            self.realizations[label_p] = SuperElement({Monomial(0, 0, tuple(bp), tuple([0]*n)): Fraction(1)})
            self.frappat_forms[label_p] = f"(b_{k}^+)^2"
            self.basis_even.append(label_p)
            self.parity[label_p] = 0

        # Short positive roots (E_del{i}_del{j}_pp)
        for i in range(1, n + 1):
            for j in range(i + 1, n + 1):
                label = f"E_del{i}_del{j}_pp"
                bp = [0]*n
                bp[i-1] = 1
                bp[j-1] = 1
                self.realizations[label] = SuperElement({Monomial(0, 0, tuple(bp), tuple([0]*n)): Fraction(1)})
                self.frappat_forms[label] = f"b_{i}^+ b_{j}^+"
                self.basis_even.append(label)
                self.parity[label] = 0

        # Long negative roots (E_2del{k}_m)
        for k in range(1, n + 1):
            label_m = f"E_2del{k}_m"
            bm = [0]*n
            bm[k-1] = 2
            self.realizations[label_m] = SuperElement({Monomial(0, 0, tuple([0]*n), tuple(bm)): Fraction(1)})
            self.frappat_forms[label_m] = f"(b_{k}^-)^2"
            self.basis_even.append(label_m)
            self.parity[label_m] = 0

        # Short negative roots (E_del{i}_del{j}_mm)
        for i in range(1, n + 1):
            for j in range(i + 1, n + 1):
                label = f"E_del{i}_del{j}_mm"
                bm = [0]*n
                bm[i-1] = 1
                bm[j-1] = 1
                self.realizations[label] = SuperElement({Monomial(0, 0, tuple([0]*n), tuple(bm)): Fraction(1)})
                self.frappat_forms[label] = f"b_{i}^- b_{j}^-"
                self.basis_even.append(label)
                self.parity[label] = 0

        # Short mixed roots (E_del{i}_del{j}_pm, E_del{i}_del{j}_mp)
        for i in range(1, n + 1):
            for j in range(i + 1, n + 1):
                label_pm = f"E_del{i}_del{j}_pm"
                bp = [0]*n
                bm = [0]*n
                bp[i-1] = 1
                bm[j-1] = 1
                self.realizations[label_pm] = SuperElement({Monomial(0, 0, tuple(bp), tuple(bm)): Fraction(1)})
                self.frappat_forms[label_pm] = f"b_{i}^+ b_{j}^-"
                self.basis_even.append(label_pm)
                self.parity[label_pm] = 0

        for i in range(1, n + 1):
            for j in range(i + 1, n + 1):
                label_mp = f"E_del{i}_del{j}_mp"
                bp = [0]*n
                bm = [0]*n
                bm[i-1] = 1
                bp[j-1] = 1
                self.realizations[label_mp] = SuperElement({Monomial(0, 0, tuple(bp), tuple(bm)): Fraction(1)})
                self.frappat_forms[label_mp] = f"b_{i}^- b_{j}^+"
                self.basis_even.append(label_mp)
                self.parity[label_mp] = 0

        # 3. Odd generators (4n total)
        for k in range(1, n + 1):
            label = f"E_eps1_del{k}_pp"
            bp = [0]*n
            bp[k-1] = 1
            self.realizations[label] = SuperElement({Monomial(1, 0, tuple(bp), tuple([0]*n)): Fraction(1)})
            self.frappat_forms[label] = f"a_1^+ b_{k}^+"
            self.basis_odd.append(label)
            self.parity[label] = 1

        for k in range(1, n + 1):
            label = f"E_eps1_del{k}_pm"
            bm = [0]*n
            bm[k-1] = 1
            self.realizations[label] = SuperElement({Monomial(1, 0, tuple([0]*n), tuple(bm)): Fraction(1)})
            self.frappat_forms[label] = f"a_1^+ b_{k}^-"
            self.basis_odd.append(label)
            self.parity[label] = 1

        for k in range(1, n + 1):
            label = f"E_eps1_del{k}_mp"
            bp = [0]*n
            bp[k-1] = 1
            self.realizations[label] = SuperElement({Monomial(0, 1, tuple(bp), tuple([0]*n)): Fraction(1)})
            self.frappat_forms[label] = f"a_1^- b_{k}^+"
            self.basis_odd.append(label)
            self.parity[label] = 1

        for k in range(1, n + 1):
            label = f"E_eps1_del{k}_mm"
            bm = [0]*n
            bm[k-1] = 1
            self.realizations[label] = SuperElement({Monomial(0, 1, tuple([0]*n), tuple(bm)): Fraction(1)})
            self.frappat_forms[label] = f"a_1^- b_{k}^-"
            self.basis_odd.append(label)
            self.parity[label] = 1

        # Standard forms for JSON
        for name, el in self.realizations.items():
            sf_list = []
            for m, coeff in el.terms.items():
                sf_list.append({
                    "words": m.to_word_list(),
                    "coeff": str(coeff.numerator) if coeff.denominator == 1 else f"{coeff.numerator}/{coeff.denominator}"
                })
            self.standard_forms[name] = sf_list

    @property
    def basis_all(self) -> List[str]:
        return self.basis_odd + self.basis_even

    def decompose(self, elem: SuperElement) -> Dict[str, Fraction]:
        """
        Decompose an element in W(1|n) into a linear combination of basis elements.
        """
        if elem.is_zero():
            return {}

        res: Dict[str, Fraction] = {}
        rem = SuperElement(dict(elem.terms))

        # First, match odd generators and non-Cartan even generators (which are pure single monomials)
        for name in self.basis_all:
            if name.startswith("H_"):
                continue
            # For non-Cartan, realization is exactly 1 monomial with coeff 1
            m = list(self.realizations[name].terms.keys())[0]
            if m in rem.terms:
                c = rem.terms[m]
                res[name] = c
                rem = rem - (self.realizations[name] * c)

        # Remaining part must be in Cartan subalgebra
        if not rem.is_zero():
            # Cartan basis elements: H_1, ..., H_{n+1}
            # We solve linear system for Cartan coefficients:
            # sum_{i=1}^{n+1} c_i H_i = rem
            import numpy as np
            cartans = [f"H_{i}" for i in range(1, self.n + 2)]
            # Collect all monomials appearing in Cartans or rem
            all_monos = set(rem.terms.keys())
            for h in cartans:
                all_monos.update(self.realizations[h].terms.keys())
            mono_list = list(all_monos)

            mat = np.zeros((len(mono_list), len(cartans)))
            vec = np.zeros(len(mono_list))

            for col_idx, h in enumerate(cartans):
                for row_idx, m in enumerate(mono_list):
                    mat[row_idx, col_idx] = float(self.realizations[h].terms.get(m, Fraction(0)))

            for row_idx, m in enumerate(mono_list):
                vec[row_idx] = float(rem.terms.get(m, Fraction(0)))

            # Solve least squares / exact
            sol, residuals, rank, s = np.linalg.lstsq(mat, vec, rcond=None)
            
            # Check accuracy
            check_rem = rem
            for col_idx, h in enumerate(cartans):
                val = Fraction(round(sol[col_idx] * 120), 120)
                # Simplify fraction if close to integer
                if round(float(val)) == float(val):
                    val = Fraction(round(float(val)))
                elif round(float(val) * 2) == float(val) * 2:
                    val = Fraction(round(float(val) * 2), 2)
                if val != 0:
                    res[h] = val
                    check_rem = check_rem - (self.realizations[h] * val)

            if not check_rem.is_zero():
                raise ValueError(f"Decomposition failed for {elem.terms}, remaining: {check_rem.terms}")

        return res

    def compute_structure_constants(self) -> List[Dict[str, Any]]:
        """
        Compute [X, Y} for all ordered pairs (X, Y) in basis_all.
        """
        sc_list = []
        basis = self.basis_all

        for X in basis:
            pX = self.parity[X]
            eX = self.realizations[X]
            for Y in basis:
                pY = self.parity[Y]
                eY = self.realizations[Y]

                bracket = supercommutator(eX, pX, eY, pY)
                if bracket.is_zero():
                    continue

                decomp = self.decompose(bracket)
                for Z, coeff in decomp.items():
                    if coeff != 0:
                        coeff_str = str(coeff.numerator) if coeff.denominator == 1 else f"{coeff.numerator}/{coeff.denominator}"
                        sc_list.append({
                            "X": X,
                            "Y": Y,
                            "Z": Z,
                            "coeff": coeff_str,
                            "sign_rule": "graded"
                        })
        return sc_list

    def to_schema1_json(self) -> Dict[str, Any]:
        n = self.n
        # Boson labels
        boson_labels = []
        for k in range(1, n + 1):
            boson_labels.extend([f"b_{k}_p", f"b_{k}_m"])

        ordering_str = "a_1_p, a_1_m, " + ", ".join(boson_labels)

        # Realizations dict
        realizations_dict = {}
        for name in self.basis_all:
            realizations_dict[name] = {
                "standard_form": self.standard_forms[name],
                "frappat_form": self.frappat_forms[name],
                "parity": self.parity[name]
            }

        sc = self.compute_structure_constants()

        return {
            "schema_version": "5.0",
            "algebra": {
                "family": "C",
                "m": 1,
                "n": n,
                "cartan_type": f"C({n+1})",
                "alternative_notation": {
                    "osp": f"osp(2|{2*n})",
                    "dimension_formula": f"osp(2m|2n) with m=1: even = 2n^2 + n + 1, odd = 4n, total = 2n^2 + 5n + 1"
                },
                "dimension": {
                    "total": self.total_dim,
                    "even": self.even_dim,
                    "odd": self.odd_dim
                }
            },
            "central_elements": {
                "kappa": {
                    "label": "kappa",
                    "parity": 1,
                    "relation": "kappa^2 = 0",
                    "description": "Nilpotent odd central element parameterizing the inhomogeneous deformation"
                },
                "K": {
                    "label": "K",
                    "parity": 0,
                    "relation": "K = 1",
                    "description": "Even central identity element from pre-oscillator bilinear form"
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
                    "description": f"Bosonic CCR oscillators b_k^± with k=1,...,{n}"
                }
            },
            "oscillator_relations": {
                "standard_fermion_anticommutators": {
                    "description": "Canonical anticommutation relations (CAR) for standard fermionic pair",
                    "relations": {
                        "same_type": "{a_1^±, a_1^±} = 0",
                        "conjugate_pair": "{a_1^-, a_1^+} = 1"
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
                    "description": "Undeformed mixed commutators between bosons and fermions",
                    "boson_fermion": "[b_i^±, a_1^±] = 0"
                }
            },
            "basis": {
                "even": self.basis_even,
                "odd": self.basis_odd,
                "ordering_convention": "PBW: κ < [odd] < [even]"
            },
            "parity": self.parity,
            "generator_realization": {
                "description": "Standard form with PBW ordering",
                "ordering": ordering_str,
                "realizations": realizations_dict
            },
            "structure_constants": sc,
            "metadata": {
                "generated_by": "C_generators.py",
                "generation_date": "2026-10-05",
                "references": [
                    "Frappat et al. (2000), Dictionary on Lie Algebras and Superalgebras",
                    "Aoi (2026)"
                ]
            }
        }


def generate_all_schema1():
    for n in [1, 2, 3]:
        alg = CSuperalgebra(n)
        data = alg.to_schema1_json()
        out_path = f"data/C_{n}_structure.json"
        with open(out_path, "w") as f:
            json.dump(data, f, indent=2)
        print(f"Generated {out_path}: {len(alg.basis_even)} even, {len(alg.basis_odd)} odd, {len(data['structure_constants'])} brackets.")


if __name__ == "__main__":
    generate_all_schema1()
