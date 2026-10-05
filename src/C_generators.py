"""
C(n+1) = osp(2|2n) Generator & Structure Constant Module
"""
import json
import os
from fractions import Fraction
from typing import Dict, List, Tuple, Any

class Monomial:
    """
    Represents a normal-ordered word in oscillator operators:
    (a_1^+)^{a1p} (a_1^-)^{a1m} (b_1^+)^{b1p} (b_1^-)^{b1m} ... (b_n^+)^{bnp} (b_n^-)^{bnm}
    """
    def __init__(self, a1p: int = 0, a1m: int = 0, bp: Tuple[int, ...] = (), bm: Tuple[int, ...] = ()):
        self.a1p = a1p
        self.a1m = a1m
        self.bp = tuple(bp)
        self.bm = tuple(bm)

    def __eq__(self, other):
        if not isinstance(other, Monomial):
            return False
        return (self.a1p == other.a1p and self.a1m == other.a1m and
                self.bp == other.bp and self.bm == other.bm)

    def __hash__(self):
        return hash((self.a1p, self.a1m, self.bp, self.bm))

    def __repr__(self):
        parts = []
        if self.a1p: parts.append("a_1_p")
        if self.a1m: parts.append("a_1_m")
        for i, (p, m) in enumerate(zip(self.bp, self.bm)):
            if p == 1: parts.append(f"b_{i+1}_p")
            elif p > 1: parts.append(f"b_{i+1}_p^{p}")
            if m == 1: parts.append(f"b_{i+1}_m")
            elif m > 1: parts.append(f"b_{i+1}_m^{m}")
        return "*".join(parts) if parts else "1"

class OscillatorExpr:
    """
    Linear combination of Monomials with Fraction coefficients.
    """
    def __init__(self, terms: Dict[Monomial, Fraction] = None):
        self.terms = {}
        if terms:
            for m, c in terms.items():
                c = Fraction(c)
                if c != 0:
                    self.terms[m] = c

    def add_term(self, monomial: Monomial, coeff: Fraction):
        coeff = Fraction(coeff)
        if coeff == 0:
            return
        new_coeff = self.terms.get(monomial, Fraction(0)) + coeff
        if new_coeff == 0:
            if monomial in self.terms:
                del self.terms[monomial]
        else:
            self.terms[monomial] = new_coeff

    def __add__(self, other: 'OscillatorExpr') -> 'OscillatorExpr':
        res = OscillatorExpr(self.terms)
        for m, c in other.terms.items():
            res.add_term(m, c)
        return res

    def __sub__(self, other: 'OscillatorExpr') -> 'OscillatorExpr':
        res = OscillatorExpr(self.terms)
        for m, c in other.terms.items():
            res.add_term(m, -c)
        return res

    def __mul__(self, scalar) -> 'OscillatorExpr':
        s = Fraction(scalar)
        res = OscillatorExpr()
        for m, c in self.terms.items():
            res.add_term(m, c * s)
        return res

    __rmul__ = __mul__

def _normal_order_fermion(p1: int, m1: int, p2: int, m2: int) -> List[Tuple[Monomial, Fraction]]:
    """
    Normal orders a product of fermionic operators: (a_1^+)^p1 (a_1^-)^m1 * (a_1^+)^p2 (a_1^-)^m2.
    Uses CAR: {a_1^-, a_1^+} = 1 => a_1^- a_1^+ = 1 - a_1^+ a_1^-.
    Returns list of (Monomial_fermion_part, coeff).
    """
    if p1 == 0:
        if m1 == 0:
            return [(Monomial(a1p=p2, a1m=m2), Fraction(1))]
        else: # m1 == 1
            if p2 == 0:
                if m2 == 1:
                    return [] # (a_1^-)^2 = 0
                return [(Monomial(a1p=0, a1m=1), Fraction(1))]
            else: # p2 == 1
                if m2 == 1: # a_1^- a_1^+ a_1^- = a_1^-
                    return [(Monomial(a1p=0, a1m=1), Fraction(1))]
                else: # a_1^- a_1^+ = 1 - a_1^+ a_1^-
                    return [
                        (Monomial(a1p=0, a1m=0), Fraction(1)),
                        (Monomial(a1p=1, a1m=1), Fraction(-1))
                    ]
    else: # p1 == 1
        if m1 == 0:
            if p2 == 1:
                return [] # (a_1^+)^2 = 0
            return [(Monomial(a1p=1, a1m=m2), Fraction(1))]
        else: # m1 == 1
            if p2 == 0:
                if m2 == 1:
                    return [] # (a_1^-)^2 = 0
                return [(Monomial(a1p=1, a1m=1), Fraction(1))]
            else: # p2 == 1
                if m2 == 1: # a_1^+ a_1^- a_1^+ a_1^- = a_1^+ a_1^-
                    return [(Monomial(a1p=1, a1m=1), Fraction(1))]
                else: # a_1^+ a_1^- a_1^+ = a_1^+
                    return [(Monomial(a1p=1, a1m=0), Fraction(1))]

def _normal_order_boson_single(p1: int, m1: int, p2: int, m2: int) -> List[Tuple[Tuple[int, int], Fraction]]:
    """
    Normal orders a single bosonic pair (b_k^+)^p1 (b_k^-)^m1 * (b_k^+)^p2 (b_k^-)^m2.
    Uses CCR: [b^-, b^+] = 1 => b^- (b^+)^p2 = (b^+)^p2 b^- + p2 (b^+)^(p2-1).
    Returns list of ((p_total, m_total), coeff).
    """
    import math
    res = []
    max_r = min(m1, p2)
    for r in range(max_r + 1):
        coeff = math.perm(m1, r) * math.comb(p2, r)
        p_tot = p1 + p2 - r
        m_tot = m1 + m2 - r
        res.append(((p_tot, m_tot), Fraction(coeff)))
    return res

def multiply_monomials(m1: Monomial, m2: Monomial, n: int) -> OscillatorExpr:
    """
    Multiplies two normal-ordered monomials m1 and m2 for rank n.
    """
    # Fermionic multiplication
    f_terms = _normal_order_fermion(m1.a1p, m1.a1m, m2.a1p, m2.a1m)
    if not f_terms:
        return OscillatorExpr()

    # Bosonic multiplication for each k=1..n
    b_term_lists = []
    for k in range(n):
        p1 = m1.bp[k] if k < len(m1.bp) else 0
        m1_b = m1.bm[k] if k < len(m1.bm) else 0
        p2 = m2.bp[k] if k < len(m2.bp) else 0
        m2_b = m2.bm[k] if k < len(m2.bm) else 0
        b_terms_k = _normal_order_boson_single(p1, m1_b, p2, m2_b)
        b_term_lists.append(b_terms_k)

    # Combine all bosonic terms
    combined_b = [((), Fraction(1))] # list of ( ( (p1, m1), (p2, m2)... ), coeff )
    for k in range(n):
        new_combined = []
        for (b_prev, c_prev) in combined_b:
            for ((p_k, m_k), c_k) in b_term_lists[k]:
                new_combined.append((b_prev + ((p_k, m_k),), c_prev * c_k))
        combined_b = new_combined

    res = OscillatorExpr()
    for f_mon, c_f in f_terms:
        for b_tuple, c_b in combined_b:
            bp = tuple(t[0] for t in b_tuple)
            bm = tuple(t[1] for t in b_tuple)
            full_mon = Monomial(a1p=f_mon.a1p, a1m=f_mon.a1m, bp=bp, bm=bm)
            res.add_term(full_mon, c_f * c_b)

    return res

def multiply_exprs(e1: OscillatorExpr, e2: OscillatorExpr, n: int) -> OscillatorExpr:
    res = OscillatorExpr()
    for m1, c1 in e1.terms.items():
        for m2, c2 in e2.terms.items():
            prod = multiply_monomials(m1, m2, n)
            res = res + prod * (c1 * c2)
    return res

def supercommutator(e1: OscillatorExpr, p1: int, e2: OscillatorExpr, p2: int, n: int) -> OscillatorExpr:
    term1 = multiply_exprs(e1, e2, n)
    term2 = multiply_exprs(e2, e1, n)
    sign = -1 if (p1 == 1 and p2 == 1) else 1
    return term1 - term2 * sign

def build_C_basis(n: int):
    """
    Builds the C(n+1) basis elements and realizations.
    Returns:
      even_labels: list
      odd_labels: list
      parity_dict: dict
      realizations: dict mapping label -> OscillatorExpr
    """
    even_labels = []
    odd_labels = []
    parity_dict = {}
    realizations = {}

    z_b = (0,) * n

    # 1. Cartans H_1 ... H_{n+1}
    # H_1 = a_1^+ a_1^- + b_1^+ b_1^-
    bp1 = list(z_b); bm1 = list(z_b); bp1[0] = 1; bm1[0] = 1
    h1_expr = OscillatorExpr({
        Monomial(a1p=1, a1m=1, bp=z_b, bm=z_b): Fraction(1),
        Monomial(a1p=0, a1m=0, bp=tuple(bp1), bm=tuple(bm1)): Fraction(1)
    })
    realizations["H_1"] = h1_expr
    even_labels.append("H_1")
    parity_dict["H_1"] = 0

    # H_k = b_{k-1}^+ b_{k-1}^- - b_k^+ b_k^- for k=2..n
    for k in range(2, n + 1):
        lbl = f"H_{k}"
        bp_km1 = list(z_b); bm_km1 = list(z_b); bp_km1[k-2] = 1; bm_km1[k-2] = 1
        bp_k = list(z_b); bm_k = list(z_b); bp_k[k-1] = 1; bm_k[k-1] = 1
        hk_expr = OscillatorExpr({
            Monomial(a1p=0, a1m=0, bp=tuple(bp_km1), bm=tuple(bm_km1)): Fraction(1),
            Monomial(a1p=0, a1m=0, bp=tuple(bp_k), bm=tuple(bm_k)): Fraction(-1)
        })
        realizations[lbl] = hk_expr
        even_labels.append(lbl)
        parity_dict[lbl] = 0

    # H_{n+1} = -b_n^+ b_n^- - 1/2
    lbl_np1 = f"H_{n+1}"
    bp_n = list(z_b); bm_n = list(z_b); bp_n[n-1] = 1; bm_n[n-1] = 1
    h_np1_expr = OscillatorExpr({
        Monomial(a1p=0, a1m=0, bp=tuple(bp_n), bm=tuple(bm_n)): Fraction(-1),
        Monomial(a1p=0, a1m=0, bp=z_b, bm=z_b): Fraction(-1, 2)
    })
    realizations[lbl_np1] = h_np1_expr
    even_labels.append(lbl_np1)
    parity_dict[lbl_np1] = 0

    # 2. Bosonic roots 2\delta_k (p and m) for k=1..n
    # E_2del{k}_p = (b_k^+)^2
    # E_2del{k}_m = (b_k^-)^2
    for k in range(1, n + 1):
        lbl_p = f"E_2del{k}_p"
        bp_k2 = list(z_b); bp_k2[k-1] = 2
        realizations[lbl_p] = OscillatorExpr({Monomial(a1p=0, a1m=0, bp=tuple(bp_k2), bm=z_b): Fraction(1)})
        even_labels.append(lbl_p)
        parity_dict[lbl_p] = 0

    for k in range(1, n + 1):
        lbl_m = f"E_2del{k}_m"
        bm_k2 = list(z_b); bm_k2[k-1] = 2
        realizations[lbl_m] = OscillatorExpr({Monomial(a1p=0, a1m=0, bp=z_b, bm=tuple(bm_k2)): Fraction(1)})
        even_labels.append(lbl_m)
        parity_dict[lbl_m] = 0

    # 3. Bosonic roots \delta_i \pm \delta_j (1 <= i < j <= n)
    for i in range(1, n + 1):
        for j in range(i + 1, n + 1):
            # pp: b_i^+ b_j^+
            lbl_pp = f"E_del{i}_del{j}_pp"
            bp_ij = list(z_b); bp_ij[i-1] += 1; bp_ij[j-1] += 1
            realizations[lbl_pp] = OscillatorExpr({Monomial(a1p=0, a1m=0, bp=tuple(bp_ij), bm=z_b): Fraction(1)})
            even_labels.append(lbl_pp)
            parity_dict[lbl_pp] = 0

            # mm: b_i^- b_j^-
            lbl_mm = f"E_del{i}_del{j}_mm"
            bm_ij = list(z_b); bm_ij[i-1] += 1; bm_ij[j-1] += 1
            realizations[lbl_mm] = OscillatorExpr({Monomial(a1p=0, a1m=0, bp=z_b, bm=tuple(bm_ij)): Fraction(1)})
            even_labels.append(lbl_mm)
            parity_dict[lbl_mm] = 0

            # pm: b_i^+ b_j^-
            lbl_pm = f"E_del{i}_del{j}_pm"
            bp_i = list(z_b); bm_j = list(z_b); bp_i[i-1] = 1; bm_j[j-1] = 1
            realizations[lbl_pm] = OscillatorExpr({Monomial(a1p=0, a1m=0, bp=tuple(bp_i), bm=tuple(bm_j)): Fraction(1)})
            even_labels.append(lbl_pm)
            parity_dict[lbl_pm] = 0

            # mp: b_i^- b_j^+
            lbl_mp = f"E_del{i}_del{j}_mp"
            bm_i = list(z_b); bp_j = list(z_b); bm_i[i-1] = 1; bp_j[j-1] = 1
            realizations[lbl_mp] = OscillatorExpr({Monomial(a1p=0, a1m=0, bp=tuple(bp_j), bm=tuple(bm_i)): Fraction(1)})
            even_labels.append(lbl_mp)
            parity_dict[lbl_mp] = 0

    # 4. Odd roots \pm \varepsilon \pm \delta_k (k=1..n)
    for k in range(1, n + 1):
        # pp: a_1^+ b_k^+
        lbl_pp = f"E_eps1_del{k}_pp"
        bp_k = list(z_b); bp_k[k-1] = 1
        realizations[lbl_pp] = OscillatorExpr({Monomial(a1p=1, a1m=0, bp=tuple(bp_k), bm=z_b): Fraction(1)})
        odd_labels.append(lbl_pp)
        parity_dict[lbl_pp] = 1

        # pm: a_1^+ b_k^-
        lbl_pm = f"E_eps1_del{k}_pm"
        bm_k = list(z_b); bm_k[k-1] = 1
        realizations[lbl_pm] = OscillatorExpr({Monomial(a1p=1, a1m=0, bp=z_b, bm=tuple(bm_k)): Fraction(1)})
        odd_labels.append(lbl_pm)
        parity_dict[lbl_pm] = 1

        # mp: a_1^- b_k^+
        lbl_mp = f"E_eps1_del{k}_mp"
        bp_k = list(z_b); bp_k[k-1] = 1
        realizations[lbl_mp] = OscillatorExpr({Monomial(a1p=0, a1m=1, bp=tuple(bp_k), bm=z_b): Fraction(1)})
        odd_labels.append(lbl_mp)
        parity_dict[lbl_mp] = 1

        # mm: a_1^- b_k^-
        lbl_mm = f"E_eps1_del{k}_mm"
        bm_k = list(z_b); bm_k[k-1] = 1
        realizations[lbl_mm] = OscillatorExpr({Monomial(a1p=0, a1m=1, bp=z_b, bm=tuple(bm_k)): Fraction(1)})
        odd_labels.append(lbl_mm)
        parity_dict[lbl_mm] = 1

    return even_labels, odd_labels, parity_dict, realizations

def decompose_expr(expr: OscillatorExpr, even_labels: List[str], odd_labels: List[str], realizations: Dict[str, OscillatorExpr], n: int) -> Dict[str, Fraction]:
    """
    Decomposes an OscillatorExpr into a linear combination of basis generators.
    """
    coeffs = {}
    z_b = (0,) * n

    # Extract non-diagonal terms directly by matching monomial keys
    # 1. Odd terms
    for lbl in odd_labels:
        r_expr = realizations[lbl]
        mon = list(r_expr.terms.keys())[0]
        if mon in expr.terms:
            coeffs[lbl] = expr.terms[mon]

    # 2. Even non-Cartan terms
    for lbl in even_labels:
        if lbl.startswith("H_"):
            continue
        r_expr = realizations[lbl]
        mon = list(r_expr.terms.keys())[0]
        if mon in expr.terms:
            coeffs[lbl] = expr.terms[mon]

    # 3. Cartan terms
    mon_a1 = Monomial(a1p=1, a1m=1, bp=z_b, bm=z_b)
    c0 = expr.terms.get(mon_a1, Fraction(0))

    c_b = []
    for k in range(1, n + 1):
        bp_k = list(z_b); bm_k = list(z_b); bp_k[k-1] = 1; bm_k[k-1] = 1
        mon_bk = Monomial(a1p=0, a1m=0, bp=tuple(bp_k), bm=tuple(bm_k))
        c_b.append(expr.terms.get(mon_bk, Fraction(0)))

    mon_1 = Monomial(a1p=0, a1m=0, bp=z_b, bm=z_b)
    d = expr.terms.get(mon_1, Fraction(0))

    if c0 != 0 or any(ck != 0 for ck in c_b) or d != 0:
        h = [Fraction(0)] * (n + 1)
        h[0] = c0
        if n >= 1:
            h[1] = c_b[0] - h[0]
        for k in range(2, n):
            h[k] = h[k-1] + c_b[k-1]
        h[n] = -2 * d

        for idx, val in enumerate(h):
            if val != 0:
                coeffs[f"H_{idx+1}"] = val

    return coeffs

def generate_C_structure_json(n: int) -> Dict[str, Any]:
    even_labels, odd_labels, parity_dict, realizations = build_C_basis(n)
    all_basis = odd_labels + even_labels

    structure_constants = []
    total_gens = len(all_basis)

    for i in range(total_gens):
        for j in range(total_gens):
            lbl1 = all_basis[i]
            lbl2 = all_basis[j]
            p1 = parity_dict[lbl1]
            p2 = parity_dict[lbl2]
            
            expr1 = realizations[lbl1]
            expr2 = realizations[lbl2]

            comm = supercommutator(expr1, p1, expr2, p2, n)
            decomp = decompose_expr(comm, even_labels, odd_labels, realizations, n)

            for target_lbl, coeff in decomp.items():
                if coeff != 0:
                    structure_constants.append({
                        "X": lbl1,
                        "Y": lbl2,
                        "Z": target_lbl,
                        "coeff": str(coeff.numerator) if coeff.denominator == 1 else f"{coeff.numerator}/{coeff.denominator}",
                        "sign_rule": "graded"
                    })

    realizations_json = {}
    for lbl in all_basis:
        expr = realizations[lbl]
        words_list = []
        for mon, coeff in expr.terms.items():
            w = []
            if mon.a1p: w.append("a_1_p")
            if mon.a1m: w.append("a_1_m")
            for k in range(n):
                for _ in range(mon.bp[k]): w.append(f"b_{k+1}_p")
                for _ in range(mon.bm[k]): w.append(f"b_{k+1}_m")
            words_list.append({
                "words": w,
                "coeff": str(coeff.numerator) if coeff.denominator == 1 else f"{coeff.numerator}/{coeff.denominator}"
            })
        realizations_json[lbl] = {
            "standard_form": words_list,
            "parity": parity_dict[lbl]
        }

    boson_labels = []
    for k in range(1, n + 1):
        boson_labels.extend([f"b_{k}_p", f"b_{k}_m"])

    schema_json = {
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
                "total": 2*n**2 + 5*n + 1,
                "even": 2*n**2 + n + 1,
                "odd": 4*n
            }
        },
        "oscillator_generators": {
            "fermions": {
                "count": 2,
                "m": 1,
                "labels": ["a_1_p", "a_1_m"],
                "description": "Standard fermionic pair a_1^± with CAR {a_1^-, a_1^+} = 1"
            },
            "bosons": {
                "count": 2*n,
                "n": n,
                "labels": boson_labels,
                "description": f"Bosonic oscillators b_i^± with i=1,...,{n}"
            }
        },
        "oscillator_relations": {
            "standard_fermion_anticommutators": {
                "description": "Canonical anticommutation relations (CAR) for fermionic oscillators",
                "relations": {
                    "same_type": "{a_i^±, a_j^±} = 0 for all i, j",
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
                "boson_fermion": "[b_i^±, a_1^±] = 0"
            }
        },
        "central_elements": {
            "kappa": {
                "label": "kappa",
                "parity": 1,
                "nilpotent": True,
                "description": "Odd central element parametrizing the 2-cocycle deformation (kappa^2 = 0)"
            },
            "K": {
                "label": "K",
                "parity": 0,
                "description": "Even central element identified with scalar identity 1"
            }
        },
        "basis": {
            "even": even_labels,
            "odd": odd_labels,
            "ordering_convention": "PBW: κ < [odd] < [even]"
        },
        "parity": parity_dict,
        "generator_realization": {
            "description": f"Standard form with PBW ordering for C({n+1})",
            "ordering": "a_1_p, a_1_m, " + ", ".join(boson_labels),
            "realizations": realizations_json
        },
        "structure_constants": structure_constants,
        "metadata": {
            "generated_by": "src/C_generators.py",
            "references": [
                "Frappat et al. (2000), Dictionary on Lie Algebras and Superalgebras",
                "docs/json_schema_specification.md"
            ]
        }
    }
    return schema_json

def save_all_C_json(output_dir: str = "data"):
    os.makedirs(output_dir, exist_ok=True)
    for n in (1, 2, 3):
        data = generate_C_structure_json(n)
        filepath = os.path.join(output_dir, f"C_{n}_structure.json")
        with open(filepath, "w") as f:
            json.dump(data, f, indent=2)
        print(f"Saved {filepath} (total dim: {data['algebra']['dimension']['total']}, structure constants count: {len(data['structure_constants'])})")

if __name__ == "__main__":
    save_all_C_json()
