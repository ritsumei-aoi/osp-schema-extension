"""
C(n+1) = osp(2|2n) Structure Constants Generator
Generates Schema 1 JSON specifications for n=1, 2, 3.
"""

import json
from fractions import Fraction
from typing import Dict, List, Tuple, Any

class Monomial:
    """
    Represents a normal-ordered oscillator monomial:
    (a1_p, a1_m, b1_p, b1_m, b2_p, b2_m, ...)
    a1_p, a1_m in {0, 1}
    bi_p, bi_m >= 0
    """
    def __init__(self, a1_p: int = 0, a1_m: int = 0, b_powers: Tuple[int, ...] = ()):
        self.a1_p = a1_p
        self.a1_m = a1_m
        self.b_powers = tuple(b_powers) # (b1_p, b1_m, b2_p, b2_m, ...)

    def __eq__(self, other):
        return (isinstance(other, Monomial) and 
                self.a1_p == other.a1_p and 
                self.a1_m == other.a1_m and 
                self.b_powers == other.b_powers)

    def __hash__(self):
        return hash((self.a1_p, self.a1_m, self.b_powers))

    def __repr__(self):
        parts = []
        if self.a1_p: parts.append("a_1^+")
        if self.a1_m: parts.append("a_1^-")
        for i in range(len(self.b_powers) // 2):
            bp = self.b_powers[2 * i]
            bm = self.b_powers[2 * i + 1]
            if bp == 1: parts.append(f"b_{i+1}^+")
            elif bp > 1: parts.append(f"(b_{i+1}^+)^{bp}")
            if bm == 1: parts.append(f"b_{i+1}^-")
            elif bm > 1: parts.append(f"(b_{i+1}^-)^{bm}")
        return " ".join(parts) if parts else "1"

class Polynomial:
    """
    Linear combination of Monomials with Fraction coefficients.
    """
    def __init__(self, terms: Dict[Monomial, Fraction] = None):
        self.terms = {}
        if terms:
            for mon, coeff in terms.items():
                c = Fraction(coeff)
                if c != 0:
                    self.terms[mon] = c

    def __add__(self, other: 'Polynomial') -> 'Polynomial':
        res = dict(self.terms)
        for mon, coeff in other.terms.items():
            res[mon] = res.get(mon, Fraction(0)) + coeff
        return Polynomial(res)

    def __sub__(self, other: 'Polynomial') -> 'Polynomial':
        res = dict(self.terms)
        for mon, coeff in other.terms.items():
            res[mon] = res.get(mon, Fraction(0)) - coeff
        return Polynomial(res)

    def __mul__(self, scalar) -> 'Polynomial':
        s = Fraction(scalar)
        if s == 0:
            return Polynomial()
        return Polynomial({mon: c * s for mon, c in self.terms.items()})

    def __rmul__(self, scalar) -> 'Polynomial':
        return self.__mul__(scalar)


def normal_order_word(ops: List[str], max_b_idx: int) -> Polynomial:
    """
    Normal orders a list of operator tokens, e.g. ['a_1_p', 'b_1_p', 'b_1_m'].
    Fermions: a_1_p, a_1_m. Relations: a_1_m a_1_p = 1 - a_1_p a_1_m, a_1_p^2 = 0, a_1_m^2 = 0.
    Bosons: b_i_p, b_i_m. Relations: b_i_m b_i_p = b_i_p b_i_m + 1.
    All distinct modes commute, except same mode non-normal pairs.
    """
    # Base case: empty token list
    if not ops:
        mon = Monomial(0, 0, (0,) * (2 * max_b_idx))
        return Polynomial({mon: Fraction(1)})

    # Recursive algorithm: scan for first adjacent out-of-order pair
    # Desired order: a_1_p < a_1_m < b_1_p < b_1_m < b_2_p < b_2_m ...
    def op_rank(op: str) -> int:
        if op == 'a_1_p': return 0
        if op == 'a_1_m': return 1
        if op.startswith('b_'):
            parts = op.split('_')
            idx = int(parts[1])
            t = 0 if parts[2] == 'p' else 1
            return 2 * idx + t
        return 999

    for i in range(len(ops) - 1):
        r1, r2 = op_rank(ops[i]), op_rank(ops[i+1])
        if r1 > r2:
            op1, op2 = ops[i], ops[i+1]
            # Check interaction
            if op1 == 'a_1_m' and op2 == 'a_1_p':
                # a_1_m a_1_p = 1 - a_1_p a_1_m
                ops_term1 = ops[:i] + ops[i+2:]
                ops_term2 = ops[:i] + ['a_1_p', 'a_1_m'] + ops[i+2:]
                return normal_order_word(ops_term1, max_b_idx) - normal_order_word(ops_term2, max_b_idx)
            elif op1.startswith('b_') and op2.startswith('b_'):
                p1, idx1, sign1 = op1.split('_')
                p2, idx2, sign2 = op2.split('_')
                if idx1 == idx2 and sign1 == 'm' and sign2 == 'p':
                    # b_k_m b_k_p = b_k_p b_k_m + 1
                    ops_term1 = ops[:i] + [f'b_{idx1}_p', f'b_{idx1}_m'] + ops[i+2:]
                    ops_term2 = ops[:i] + ops[i+2:]
                    return normal_order_word(ops_term1, max_b_idx) + normal_order_word(ops_term2, max_b_idx)
            # If they commute (or fermions square to zero, etc.)
            if op1 == op2 and op1 in ('a_1_p', 'a_1_m'):
                return Polynomial() # zero!
            # Otherwise they simply commute:
            ops_swapped = ops[:i] + [op2, op1] + ops[i+2:]
            return normal_order_word(ops_swapped, max_b_idx)

    # Check for duplicate fermions
    a1_p_count = ops.count('a_1_p')
    a1_m_count = ops.count('a_1_m')
    if a1_p_count > 1 or a1_m_count > 1:
        return Polynomial()

    # Build final monomial
    b_pow = [0] * (2 * max_b_idx)
    for op in ops:
        if op.startswith('b_'):
            parts = op.split('_')
            idx = int(parts[1]) - 1
            if parts[2] == 'p':
                b_pow[2 * idx] += 1
            else:
                b_pow[2 * idx + 1] += 1

    mon = Monomial(1 if a1_p_count else 0, 1 if a1_m_count else 0, tuple(b_pow))
    return Polynomial({mon: Fraction(1)})


def multiply_polynomials(poly1: Polynomial, poly2: Polynomial, max_b_idx: int) -> Polynomial:
    res = Polynomial()
    for mon1, c1 in poly1.terms.items():
        # Monomial 1 ops
        ops1 = []
        if mon1.a1_p: ops1.append('a_1_p')
        if mon1.a1_m: ops1.append('a_1_m')
        for i in range(max_b_idx):
            ops1.extend([f'b_{i+1}_p'] * mon1.b_powers[2*i])
            ops1.extend([f'b_{i+1}_m'] * mon1.b_powers[2*i+1])

        for mon2, c2 in poly2.terms.items():
            ops2 = []
            if mon2.a1_p: ops2.append('a_1_p')
            if mon2.a1_m: ops2.append('a_1_m')
            for i in range(max_b_idx):
                ops2.extend([f'b_{i+1}_p'] * mon2.b_powers[2*i])
                ops2.extend([f'b_{i+1}_m'] * mon2.b_powers[2*i+1])

            combined_ops = ops1 + ops2
            term_poly = normal_order_word(combined_ops, max_b_idx)
            res = res + (term_poly * (c1 * c2))
    return res


def compute_superbracket(poly1: Polynomial, poly2: Polynomial, p1: int, p2: int, max_b_idx: int) -> Polynomial:
    p1p2 = multiply_polynomials(poly1, poly2, max_b_idx)
    p2p1 = multiply_polynomials(poly2, poly1, max_b_idx)
    sign = (-1) ** (p1 * p2)
    return p1p2 - (p2p1 * Fraction(sign))


def get_basis_and_realizations(n: int) -> Tuple[List[str], List[str], Dict[str, Polynomial], Dict[str, int]]:
    """
    Returns (even_basis, odd_basis, realizations, parity_map)
    """
    even_basis = []
    odd_basis = []
    realizations = {}
    parity_map = {}

    # Cartans: H_1, ..., H_{n+1}
    # H_1 = a_1^+ a_1^- + b_1^+ b_1^-
    # H_k = b_{k-1}^+ b_{k-1}^- - b_k^+ b_k^- (2 <= k <= n)
    # H_{n+1} = -b_n^+ b_n^- - 1/2
    for k in range(1, n + 2):
        name = f"H_{k}"
        even_basis.append(name)
        parity_map[name] = 0
        if k == 1:
            realizations[name] = normal_order_word(['a_1_p', 'a_1_m'], n) + normal_order_word(['b_1_p', 'b_1_m'], n)
        elif 2 <= k <= n:
            realizations[name] = normal_order_word([f'b_{k-1}_p', f'b_{k-1}_m'], n) - normal_order_word([f'b_{k}_p', f'b_{k}_m'], n)
        else: # k == n+1
            realizations[name] = (normal_order_word([f'b_{n}_p', f'b_{n}_m'], n) * Fraction(-1)) - normal_order_word([], n) * Fraction(1, 2)

    # Positive 2\delta_k roots
    for k in range(1, n + 1):
        name = f"E_2del{k}_p"
        even_basis.append(name)
        parity_map[name] = 0
        realizations[name] = normal_order_word([f'b_{k}_p', f'b_{k}_p'], n)

    # Positive \delta_i + \delta_j roots (i < j)
    for i in range(1, n + 1):
        for j in range(i + 1, n + 1):
            name = f"E_del{i}_del{j}_pp"
            even_basis.append(name)
            parity_map[name] = 0
            realizations[name] = normal_order_word([f'b_{i}_p', f'b_{j}_p'], n)

    # Negative 2\delta_k roots
    for k in range(1, n + 1):
        name = f"E_2del{k}_m"
        even_basis.append(name)
        parity_map[name] = 0
        realizations[name] = normal_order_word([f'b_{k}_m', f'b_{k}_m'], n)

    # Negative \delta_i + \delta_j roots (i < j)
    for i in range(1, n + 1):
        for j in range(i + 1, n + 1):
            name = f"E_del{i}_del{j}_mm"
            even_basis.append(name)
            parity_map[name] = 0
            realizations[name] = normal_order_word([f'b_{i}_m', f'b_{j}_m'], n)

    # Mixed \delta_i - \delta_j roots (i < j)
    for i in range(1, n + 1):
        for j in range(i + 1, n + 1):
            name_pm = f"E_del{i}_del{j}_pm"
            even_basis.append(name_pm)
            parity_map[name_pm] = 0
            realizations[name_pm] = normal_order_word([f'b_{i}_p', f'b_{j}_m'], n)

            name_mp = f"E_del{i}_del{j}_mp"
            even_basis.append(name_mp)
            parity_map[name_mp] = 0
            realizations[name_mp] = normal_order_word([f'b_{i}_m', f'b_{j}_p'], n)

    # Odd roots: E_eps1_del{k}_pp/pm/mp/mm
    for k in range(1, n + 1):
        for s1, s1_label in [('p', 'p'), ('m', 'm')]:
            for s2, s2_label in [('p', 'p'), ('m', 'm')]:
                name = f"E_eps1_del{k}_{s1_label}{s2_label}"
                odd_basis.append(name)
                parity_map[name] = 1
                op_a = 'a_1_p' if s1 == 'p' else 'a_1_m'
                op_b = f'b_{k}_p' if s2 == 'p' else f'b_{k}_m'
                realizations[name] = normal_order_word([op_a, op_b], n)

    return even_basis, odd_basis, realizations, parity_map


def decompose_into_basis(poly: Polynomial, n: int, even_basis: List[str], odd_basis: List[str], realizations: Dict[str, Polynomial]) -> List[Tuple[str, str]]:
    """
    Decomposes a polynomial into a linear combination of basis elements.
    Returns list of (generator_name, coeff_str).
    """
    if not poly.terms:
        return []

    rem = Polynomial(poly.terms)
    decomp = {}

    # 1. Non-Cartan generators (each has a unique monomial!)
    for name in odd_basis + [b for b in even_basis if not b.startswith("H_")]:
        real = realizations[name]
        # Realization has single monomial
        for mon, coeff in real.terms.items():
            if mon in rem.terms:
                c = rem.terms[mon] / coeff
                if c != 0:
                    decomp[name] = decomp.get(name, Fraction(0)) + c
                    rem = rem - (real * c)

    # 2. Cartan generators and constant (expressed via b_k^+ b_k^- and a_1^+ a_1^-)
    # Monomials present in Cartans:
    # a_1^+ a_1^- (a1_p=1, a1_m=1, b_powers=all 0)
    # b_k^+ b_k^- (a1_p=0, a1_m=0, b_powers has 1 at 2k-2 and 2k-1)
    # constant (a1_p=0, a1_m=0, b_powers=all 0)

    # Let's check remaining monomials
    for mon, coeff in list(rem.terms.items()):
        if coeff == 0: continue

        # Check if it's a_1^+ a_1^-
        if mon.a1_p == 1 and mon.a1_m == 1 and all(p == 0 for p in mon.b_powers):
            # a_1^+ a_1^- = H_1 - H_2 - ... - H_n + H_{n+1} + 1/2
            decomp["H_1"] = decomp.get("H_1", Fraction(0)) + coeff
            for j in range(2, n + 1):
                decomp[f"H_{j}"] = decomp.get(f"H_{j}", Fraction(0)) - coeff
            decomp[f"H_{n+1}"] = decomp.get(f"H_{n+1}", Fraction(0)) + coeff
            # Constant 1/2 * coeff
            rem = rem - (Polynomial({mon: coeff}))

        # Check if it's b_k^+ b_k^-
        elif mon.a1_p == 0 and mon.a1_m == 0:
            active_b = [i for i, p in enumerate(mon.b_powers) if p > 0]
            if len(active_b) == 2 and active_b[0] % 2 == 0 and active_b[1] == active_b[0] + 1 and mon.b_powers[active_b[0]] == 1 and mon.b_powers[active_b[1]] == 1:
                k = (active_b[0] // 2) + 1 # 1-indexed b_k
                # b_k^+ b_k^- = H_{k+1} + ... + H_n - H_{n+1} - 1/2
                for j in range(k + 1, n + 1):
                    decomp[f"H_{j}"] = decomp.get(f"H_{j}", Fraction(0)) + coeff
                decomp[f"H_{n+1}"] = decomp.get(f"H_{n+1}", Fraction(0)) - coeff
                rem = rem - (Polynomial({mon: coeff}))

    result = []
    for name, coeff in decomp.items():
        if coeff != 0:
            result.append((name, str(coeff)))
    return result


def build_C_structure(n: int) -> Dict[str, Any]:
    even_basis, odd_basis, realizations, parity_map = get_basis_and_realizations(n)
    all_generators = odd_basis + even_basis # PBW order: odd < even

    dim_even = 2 * n * n + n + 1
    dim_odd = 4 * n
    dim_total = dim_even + dim_odd

    # Format realizations for JSON
    realizations_json = {}
    for name in all_generators:
        poly = realizations[name]
        words_list = []
        frappat_parts = []
        for mon, c in poly.terms.items():
            w = []
            if mon.a1_p: w.append("a_1_p")
            if mon.a1_m: w.append("a_1_m")
            for i in range(n):
                bp = mon.b_powers[2*i]
                bm = mon.b_powers[2*i+1]
                w.extend([f"b_{i+1}_p"] * bp)
                w.extend([f"b_{i+1}_m"] * bm)

            words_list.append({
                "words": w,
                "coeff": str(c)
            })

            # Frappat string
            f_str = repr(mon)
            if c != 1:
                f_str = f"{c} ({f_str})"
            frappat_parts.append(f_str)

        realizations_json[name] = {
            "standard_form": words_list,
            "frappat_form": " + ".join(frappat_parts),
            "parity": parity_map[name]
        }

    # Structure constants computation
    struct_consts = []
    for i, g1 in enumerate(all_generators):
        for j, g2 in enumerate(all_generators):
            # Compute graded bracket [g1, g2}
            p1 = parity_map[g1]
            p2 = parity_map[g2]
            bracket_poly = compute_superbracket(realizations[g1], realizations[g2], p1, p2, n)
            decomp = decompose_into_basis(bracket_poly, n, even_basis, odd_basis, realizations)

            for target, coeff in decomp:
                struct_consts.append({
                    "X": g1,
                    "Y": g2,
                    "Z": target,
                    "coeff": coeff,
                    "sign_rule": "graded"
                })

    schema_data = {
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
                "count": 2 * n,
                "n": n,
                "labels": [f"b_{i}_p" for i in range(1, n+1)] + [f"b_{i}_m" for i in range(1, n+1)],
                "description": f"Bosonic oscillators b_i^± with i=1,...,{n}"
            }
        },
        "central_elements": {
            "kappa": {
                "label": "kappa",
                "parity": 1,
                "nilpotent": True,
                "description": "Odd central parameter for deformation"
            },
            "K": {
                "label": "K",
                "parity": 0,
                "description": "Even central scalar multiplier (identified with 1)"
            }
        },
        "oscillator_relations": {
            "standard_fermion_anticommutators": {
                "description": "Canonical anticommutation relations for fermionic oscillators",
                "relations": {
                    "same_type": "{a_1^±, a_1^±} = 0",
                    "conjugate_pair": "{a_1^-, a_1^+} = 1"
                }
            },
            "bosonic_commutators": {
                "description": "Canonical commutation relations for bosonic oscillators",
                "relations": {
                    "same_type": "[b_i^±, b_j^±] = 0 for all i, j",
                    "conjugate_pair": "[b_i^-, b_j^+] = δ_{ij}"
                }
            },
            "mixed_commutators": {
                "boson_fermion": "[b_i^±, a_1^±] = 0"
            }
        },
        "basis": {
            "even": even_basis,
            "odd": odd_basis,
            "ordering_convention": "PBW: kappa < [odd] < [even]"
        },
        "parity": parity_map,
        "generator_realization": realizations_json,
        "structure_constants": struct_consts,
        "metadata": {
            "generated_by": "src/C_generators.py",
            "generation_date": "2026-10-05",
            "references": [
                "Frappat et al. (2000), Dictionary on Lie Algebras and Superalgebras",
                "Bakalov and Sullivan (2017)"
            ]
        }
    }

    return schema_data


def generate_all():
    import os
    os.makedirs("data", exist_ok=True)
    for n in [1, 2, 3]:
        data = build_C_structure(n)
        filepath = f"data/C_{n}_structure.json"
        with open(filepath, "w") as f:
            json.dump(data, f, indent=2)
        print(f"Generated {filepath} (total dim: {data['algebra']['dimension']['total']}, struct consts count: {len(data['structure_constants'])})")


if __name__ == "__main__":
    generate_all()
