import json
from fractions import Fraction
from typing import Dict, List, Tuple, Any

class OscillatorPoly:
    """
    Represents a polynomial in oscillators:
    Fermions: a_1_p, a_1_m (CAR)
    Bosons: b_k_p, b_k_m for k=1..n (CCR)
    
    A monomial is represented by:
    ( (u_p, u_m), tuple((v_1p, v_1m), ..., (v_np, v_nm)) )
    where u_p, u_m in {0, 1}.
    """
    def __init__(self, n: int, terms: Dict[Tuple[Tuple[int, int], Tuple[Tuple[int, int], ...]], Fraction] = None):
        self.n = n
        self.terms = {}
        if terms:
            for k, v in terms.items():
                if v != 0:
                    self.terms[k] = Fraction(v)

    @classmethod
    def zero(cls, n: int):
        return cls(n, {})

    @classmethod
    def constant(cls, n: int, val):
        zero_b = tuple((0, 0) for _ in range(n))
        return cls(n, {((0, 0), zero_b): Fraction(val)})

    @classmethod
    def fermion(cls, n: int, is_p: bool):
        zero_b = tuple((0, 0) for _ in range(n))
        u = (1, 0) if is_p else (0, 1)
        return cls(n, {(u, zero_b): Fraction(1)})

    @classmethod
    def boson(cls, n: int, k: int, is_p: bool):
        # k is 1-indexed
        zero_b = list((0, 0) for _ in range(n))
        zero_b[k-1] = (1, 0) if is_p else (0, 1)
        return cls(n, {((0, 0), tuple(zero_b)): Fraction(1)})

    def add(self, other: 'OscillatorPoly') -> 'OscillatorPoly':
        res_terms = dict(self.terms)
        for k, v in other.terms.items():
            res_terms[k] = res_terms.get(k, Fraction(0)) + v
            if res_terms[k] == 0:
                del res_terms[k]
        return OscillatorPoly(self.n, res_terms)

    def scale(self, c) -> 'OscillatorPoly':
        c = Fraction(c)
        if c == 0:
            return OscillatorPoly.zero(self.n)
        return OscillatorPoly(self.n, {k: v * c for k, v in self.terms.items()})

    def mul(self, other: 'OscillatorPoly') -> 'OscillatorPoly':
        res = OscillatorPoly.zero(self.n)
        for k1, v1 in self.terms.items():
            for k2, v2 in other.terms.items():
                prod_terms = mul_monomials(self.n, k1, k2)
                for k_p, v_p in prod_terms.items():
                    res = res.add(OscillatorPoly(self.n, {k_p: v1 * v2 * v_p}))
        return res

def mul_monomials(n: int, m1, m2) -> Dict[Any, Fraction]:
    """
    Multiply monomial m1 and m2 into normal order:
    m1 = (f1, b1), m2 = (f2, b2)
    """
    f1, b1 = m1
    f2, b2 = m2

    # Fermionic multiplication: f1 * f2
    # f1 = (up1, um1), f2 = (up2, um2)
    # product term: (a1^+)^up1 (a1^-)^um1 (a1^+)^up2 (a1^-)^um2
    f_res = mul_fermions(f1, f2)

    # Bosonic multiplication: b1 * b2
    b_res = mul_bosons(n, b1, b2)

    # Combine tensor product
    res = {}
    for (f_k, f_v) in f_res.items():
        for (b_k, b_v) in b_res.items():
            k = (f_k, b_k)
            res[k] = res.get(k, Fraction(0)) + f_v * b_v
            if res[k] == 0:
                del res[k]
    return res

def mul_fermions(f1, f2) -> Dict[Tuple[int, int], Fraction]:
    """
    (a1^+)^up1 (a1^-)^um1 * (a1^+)^up2 (a1^-)^um2
    CAR: a1^- a1^+ = 1 - a1^+ a1^-
    (a1^+)^2 = 0, (a1^-)^2 = 0
    """
    up1, um1 = f1
    up2, um2 = f2

    # Case 1: um1 == 0
    if um1 == 0:
        if up1 == 1 and up2 == 1:
            return {} # (a1^+)^2 = 0
        return {(up1 + up2, um2): Fraction(1)}

    # Case 2: um1 == 1
    # um1=1, so we have (a1^+)^up1 a1^- (a1^+)^up2 (a1^-)^um2
    if up2 == 0:
        if um1 == 1 and um2 == 1:
            return {} # (a1^-)^2 = 0
        return {(up1, um1 + um2): Fraction(1)}

    # Here um1 == 1 and up2 == 1
    # a1^- a1^+ = 1 - a1^+ a1^-
    # So (a1^+)^up1 (1 - a1^+ a1^-) (a1^-)^um2
    # = (a1^+)^up1 (a1^-)^um2 - (a1^+)^(up1+1) a1^- (a1^-)^um2
    res = {}
    # First term: (a1^+)^up1 (a1^-)^um2
    if not (up1 == 0 and um2 == 0):
        # check if valid
        pass
    # Actually: (a1^+)^up1 (a1^-)^um2 has normal order (up1, um2)
    # But wait, if um2 == 1, second subterm has (a1^-)^2 = 0.
    # Term 1:
    res[(up1, um2)] = Fraction(1)
    
    # Term 2: - (a1^+)^(up1+1) (a1^-)^(1+um2)
    if up1 + 1 <= 1 and 1 + um2 <= 1:
        res[(up1 + 1, 1 + um2)] = Fraction(-1)

    return res

def mul_bosons(n: int, b1, b2) -> Dict[Tuple[Tuple[int, int], ...], Fraction]:
    """
    Multiply multi-boson monomials for k=1..n
    Each mode k multiplies independently since modes commute!
    """
    res = {(): Fraction(1)}
    for k in range(n):
        vk1 = b1[k]
        vk2 = b2[k]
        mode_res = mul_single_boson(vk1, vk2)
        new_res = {}
        for prev_k, prev_v in res.items():
            for m_k, m_v in mode_res.items():
                comb_k = prev_k + (m_k,)
                new_res[comb_k] = new_res.get(comb_k, Fraction(0)) + prev_v * m_v
        res = new_res
    return res

def mul_single_boson(v1, v2) -> Dict[Tuple[int, int], Fraction]:
    """
    (b^+)^vp1 (b^-)^vm1 * (b^+)^vp2 (b^-)^vm2
    CCR: b^- b^+ = b^+ b^- + 1
    So (b^-)^m (b^+)^p
    Using formula: (b^-)^m (b^+)^p = sum_{j=0}^{min(m,p)} j! C(m,j) C(p,j) (b^+)^(p-j) (b^-)^(m-j)
    """
    vp1, vm1 = v1
    vp2, vm2 = v2

    # We need to normal order (b^-)^vm1 (b^+)^vp2
    # m = vm1, p = vp2
    m, p = vm1, vp2
    res = {}
    import math
    for j in range(min(m, p) + 1):
        coeff = Fraction(math.factorial(j) * math.comb(m, j) * math.comb(p, j))
        p_eff = p - j
        m_eff = m - j
        final_p = vp1 + p_eff
        final_m = m_eff + vm2
        res[(final_p, final_m)] = res.get((final_p, final_m), Fraction(0)) + coeff
    return res


class CAlgebra:
    def __init__(self, n: int):
        self.n = n
        self.basis_even, self.basis_odd = self._build_basis_lists()
        self.basis_all = self.basis_odd + self.basis_even  # PBW: odd then even (kappa is central extension)
        self.realizations = self._build_realizations()
        self.parities = self._build_parities()

    def _build_basis_lists(self):
        n = self.n
        # Cartans
        even = [f"H_{i}" for i in range(1, n + 2)]
        # Double roots
        for k in range(1, n + 1):
            even.append(f"E_2del{k}_p")
        for k in range(1, n + 1):
            even.append(f"E_2del{k}_m")
        # Mixed bosonic roots
        for i in range(1, n + 1):
            for j in range(i + 1, n + 1):
                even.append(f"E_del{i}_del{j}_pp")
        for i in range(1, n + 1):
            for j in range(i + 1, n + 1):
                even.append(f"E_del{i}_del{j}_mm")
        for i in range(1, n + 1):
            for j in range(i + 1, n + 1):
                even.append(f"E_del{i}_del{j}_pm")
                even.append(f"E_del{i}_del{j}_mp")

        # Odd roots
        odd = []
        for k in range(1, n + 1):
            odd.append(f"E_eps1_del{k}_pp")
            odd.append(f"E_eps1_del{k}_pm")
            odd.append(f"E_eps1_del{k}_mp")
            odd.append(f"E_eps1_del{k}_mm")

        return even, odd

    def _build_parities(self) -> Dict[str, int]:
        p = {}
        for g in self.basis_even:
            p[g] = 0
        for g in self.basis_odd:
            p[g] = 1
        return p

    def _build_realizations(self) -> Dict[str, OscillatorPoly]:
        n = self.n
        reals = {}
        # H_1 = a1_p a1_m + b1_p b1_m
        a1_p = OscillatorPoly.fermion(n, True)
        a1_m = OscillatorPoly.fermion(n, False)
        b1_p = OscillatorPoly.boson(n, 1, True)
        b1_m = OscillatorPoly.boson(n, 1, False)
        
        reals["H_1"] = a1_p.mul(a1_m).add(b1_p.mul(b1_m))

        # H_k = b_{k-1}_p b_{k-1}_m - b_k_p b_k_m for 2 <= k <= n
        for k in range(2, n + 1):
            bk1_p = OscillatorPoly.boson(n, k - 1, True)
            bk1_m = OscillatorPoly.boson(n, k - 1, False)
            bk_p = OscillatorPoly.boson(n, k, True)
            bk_m = OscillatorPoly.boson(n, k, False)
            reals[f"H_{k}"] = bk1_p.mul(bk1_m).add(bk_p.mul(bk_m).scale(-1))

        # H_{n+1} = - b_n_p b_n_m - 1/2
        bn_p = OscillatorPoly.boson(n, n, True)
        bn_m = OscillatorPoly.boson(n, n, False)
        reals[f"H_{n+1}"] = bn_p.mul(bn_m).scale(-1).add(OscillatorPoly.constant(n, Fraction(-1, 2)))

        # E_2delk_p = 1/2 (bk_p)^2
        # E_2delk_m = 1/2 (bk_m)^2
        for k in range(1, n + 1):
            bk_p = OscillatorPoly.boson(n, k, True)
            bk_m = OscillatorPoly.boson(n, k, False)
            reals[f"E_2del{k}_p"] = bk_p.mul(bk_p).scale(Fraction(1, 2))
            reals[f"E_2del{k}_m"] = bk_m.mul(bk_m).scale(Fraction(1, 2))

        # Mixed bosonic roots
        for i in range(1, n + 1):
            for j in range(i + 1, n + 1):
                bi_p = OscillatorPoly.boson(n, i, True)
                bi_m = OscillatorPoly.boson(n, i, False)
                bj_p = OscillatorPoly.boson(n, j, True)
                bj_m = OscillatorPoly.boson(n, j, False)

                reals[f"E_del{i}_del{j}_pp"] = bi_p.mul(bj_p)
                reals[f"E_del{i}_del{j}_mm"] = bi_m.mul(bj_m)
                reals[f"E_del{i}_del{j}_pm"] = bi_p.mul(bj_m)
                reals[f"E_del{i}_del{j}_mp"] = bi_m.mul(bj_p)

        # Odd roots: a1_p/m * bk_p/m
        for k in range(1, n + 1):
            bk_p = OscillatorPoly.boson(n, k, True)
            bk_m = OscillatorPoly.boson(n, k, False)

            reals[f"E_eps1_del{k}_pp"] = a1_p.mul(bk_p)
            reals[f"E_eps1_del{k}_pm"] = a1_p.mul(bk_m)
            reals[f"E_eps1_del{k}_mp"] = a1_m.mul(bk_p)
            reals[f"E_eps1_del{k}_mm"] = a1_m.mul(bk_m)

        return reals

    def compute_bracket(self, x_name: str, y_name: str) -> OscillatorPoly:
        """
        [X, Y} = XY - (-1)^{p(X)p(Y)} YX
        """
        px = self.parities[x_name]
        py = self.parities[y_name]
        rx = self.realizations[x_name]
        ry = self.realizations[y_name]

        xy = rx.mul(ry)
        yx = ry.mul(rx)

        sign = -1 if (px == 1 and py == 1) else 1
        return xy.add(yx.scale(-sign))

    def express_in_basis(self, poly: OscillatorPoly) -> Dict[str, Fraction]:
        """
        Express poly as sum_Z c_Z Z.
        Returns map {Z_name: coeff}
        """
        rem = OscillatorPoly(self.n, dict(poly.terms))
        coeffs = {}

        # First match constant term if any (should match part of H_{n+1} or Cartans)
        # We can form a linear system of basis realizations!
        # Since number of basis elements is small (4, 11, 22), let's collect all monomial keys present
        # in the basis realizations and solve a linear system!
        
        all_monos = set()
        for g_name in self.basis_all:
            all_monos.update(self.realizations[g_name].terms.keys())
        all_monos.update(poly.terms.keys())
        mono_list = sorted(list(all_monos))

        import numpy as np
        # Build matrix A (len(mono_list) x len(basis_all))
        A = np.zeros((len(mono_list), len(self.basis_all)), dtype=object)
        for col, g_name in enumerate(self.basis_all):
            g_poly = self.realizations[g_name]
            for row, mono in enumerate(mono_list):
                if mono in g_poly.terms:
                    A[row, col] = g_poly.terms[mono]
                else:
                    A[row, col] = Fraction(0)

        b = np.zeros(len(mono_list), dtype=object)
        for row, mono in enumerate(mono_list):
            if mono in poly.terms:
                b[row] = poly.terms[mono]
            else:
                b[row] = Fraction(0)

        # Solve linear system A x = b exactly using Gaussian Elimination over Fractions
        x = gaussian_elimination_fractions(A, b)
        if x is None:
            raise ValueError(f"Poly {poly.terms} cannot be expressed in basis!")

        for col, g_name in enumerate(self.basis_all):
            if x[col] != 0:
                coeffs[g_name] = x[col]
        return coeffs


def gaussian_elimination_fractions(A, b):
    rows, cols = A.shape
    M = [[A[r, c] for c in range(cols)] + [b[r]] for r in range(rows)]

    pivot_row = 0
    pivot_cols = []
    for c in range(cols):
        if pivot_row >= rows:
            break
        # Find non-zero pivot
        r_pivot = -1
        for r in range(pivot_row, rows):
            if M[r][c] != 0:
                r_pivot = r
                break
        if r_pivot == -1:
            continue

        # Swap rows
        M[pivot_row], M[r_pivot] = M[r_pivot], M[pivot_row]
        pivot_val = M[pivot_row][c]

        # Scale pivot row
        for j in range(c, cols + 1):
            M[pivot_row][j] /= pivot_val

        # Eliminate in other rows
        for r in range(rows):
            if r != pivot_row and M[r][c] != 0:
                factor = M[r][c]
                for j in range(c, cols + 1):
                    M[r][j] -= factor * M[pivot_row][j]

        pivot_cols.append((pivot_row, c))
        pivot_row += 1

    # Check consistency
    for r in range(pivot_row, rows):
        if M[r][cols] != 0:
            return None  # Inconsistent

    sol = [Fraction(0)] * cols
    for r, c in pivot_cols:
        sol[c] = M[r][cols]

    return sol


def generate_schema_1(n: int) -> Dict[str, Any]:
    alg = CAlgebra(n)
    
    # Compute all non-zero structure constants
    sc_list = []
    for i, x in enumerate(alg.basis_all):
        for j, y in enumerate(alg.basis_all):
            bracket = alg.compute_bracket(x, y)
            if not bracket.terms:
                continue
            coeffs = alg.express_in_basis(bracket)
            for z, coeff in coeffs.items():
                # Format coeff as string rational e.g. "1", "-1", "1/2"
                coeff_str = str(coeff.numerator) if coeff.denominator == 1 else f"{coeff.numerator}/{coeff.denominator}"
                sc_list.append({
                    "X": x,
                    "Y": y,
                    "Z": z,
                    "coeff": coeff_str,
                    "sign_rule": "graded"
                })

    # Build generator realization dict for JSON
    gen_real = {}
    for g in alg.basis_all:
        poly = alg.realizations[g]
        std_form = []
        for mono, c in poly.terms.items():
            f_mono, b_mono = mono
            words = []
            if f_mono[0] == 1: words.append("a_1_p")
            if f_mono[1] == 1: words.append("a_1_m")
            for k_idx, (bp, bm) in enumerate(b_mono):
                for _ in range(bp): words.append(f"b_{k_idx+1}_p")
                for _ in range(bm): words.append(f"b_{k_idx+1}_m")
            c_str = str(c.numerator) if c.denominator == 1 else f"{c.numerator}/{c.denominator}"
            std_form.append({"words": words, "coeff": c_str})
        
        gen_real[g] = {
            "standard_form": std_form,
            "parity": alg.parities[g]
        }

    schema = {
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
                "total": 2*n*n + 5*n + 1,
                "even": 2*n*n + n + 1,
                "odd": 4*n
            }
        },
        "oscillator_generators": {
            "fermions": {
                "m": 1,
                "labels": ["a_1_p", "a_1_m"],
                "description": "Standard CAR pair a_1^±"
            },
            "bosons": {
                "n": n,
                "labels": [f"b_{i}_{s}" for i in range(1, n+1) for s in ["p", "m"]],
                "description": f"Bosonic oscillators b_i^± with i=1,...,{n}"
            }
        },
        "oscillator_relations": {
            "standard_fermion_anticommutators": {
                "description": "Canonical anticommutation relations (CAR)",
                "relations": {
                    "{a_1^-, a_1^+}": 1,
                    "(a_1^±)^2": 0
                }
            },
            "bosonic_commutators": {
                "description": "Canonical commutation relations (CCR)",
                "relations": {
                    "[b_i^-, b_j^+]": "δ_{ij}",
                    "[b_i^±, b_j^±]": 0
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
                "description": "Odd nilpotent central element, kappa^2 = 0"
            },
            "K": {
                "label": "K",
                "parity": 0,
                "description": "Even central identity element"
            }
        },
        "basis": {
            "even": alg.basis_even,
            "odd": alg.basis_odd,
            "ordering_convention": "PBW: κ < [odd] < [even]"
        },
        "parity": alg.parities,
        "generator_realization": gen_real,
        "structure_constants": sc_list,
        "metadata": {
            "generated_by": "src/C_generators.py",
            "generation_date": "2026-10-05",
            "references": [
                "Frappat et al. (2000), Dictionary on Lie Algebras and Superalgebras",
                "Bakalov and Sullivan (2017)"
            ]
        }
    }
    return schema


if __name__ == "__main__":
    import os
    os.makedirs("data", exist_ok=True)
    for n in [1, 2, 3]:
        data = generate_schema_1(n)
        filename = f"data/C_{n}_structure.json"
        with open(filename, "w") as f:
            json.dump(data, f, indent=2)
        print(f"Generated {filename} (Total dim: {data['algebra']['dimension']['total']})")
