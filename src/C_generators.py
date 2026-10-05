"""
C(n+1) = osp(2|2n) Generator and Structure Constant Engine.
Constructs basis, oscillator realizations, and structure constants for C(n+1).
"""

from fractions import Fraction
import json
import os
from typing import Dict, List, Tuple, Any


def get_basis(n: int) -> Dict[str, List[str]]:
    """
    Returns the even and odd basis lists for C(n+1) = osp(2|2n)
    according to the canonical PBW ordering specified in handover/notation.md.
    """
    # 1. Cartans
    cartans = [f"H_{i}" for i in range(1, n + 2)]
    
    # 2. 2*delta roots
    even_2del_p = [f"E_2del{k}_p" for k in range(1, n + 1)]
    even_2del_m = [f"E_2del{k}_m" for k in range(1, n + 1)]
    
    # 3. delta_i +- delta_j roots
    even_cross = []
    for i in range(1, n + 1):
        for j in range(i + 1, n + 1):
            even_cross.append(f"E_del{i}_del{j}_pp")
            even_cross.append(f"E_del{i}_del{j}_mm")
            even_cross.append(f"E_del{i}_del{j}_pm")
            even_cross.append(f"E_del{i}_del{j}_mp")
            
    even_basis = cartans + even_2del_p + even_2del_m + even_cross
    
    # Odd basis: 4n elements
    odd_basis = []
    for k in range(1, n + 1):
        odd_basis.append(f"E_eps1_del{k}_pp")
        odd_basis.append(f"E_eps1_del{k}_pm")
        odd_basis.append(f"E_eps1_del{k}_mp")
        odd_basis.append(f"E_eps1_del{k}_mm")
        
    return {
        "even": even_basis,
        "odd": odd_basis,
        "ordering_convention": "PBW: κ < [odd] < [even] (K = 1 is excluded from basis)"
    }


def get_parity(n: int) -> Dict[str, int]:
    """Returns mapping from generator label to parity (0 or 1)."""
    basis = get_basis(n)
    parity = {}
    for gen in basis["even"]:
        parity[gen] = 0
    for gen in basis["odd"]:
        parity[gen] = 1
    return parity


# Oscillator representation:
# An oscillator is a tuple (family, index, sign):
# e.g. ('a', 1, '+'), ('b', 2, '-')
# Monomial is a tuple of oscillators.
# An Operator is a dict mapping Monomial -> Fraction coeff.

def _osc_rank(osc: Tuple[str, int, str]) -> Tuple[int, int, int]:
    """
    Ordering for normal ordering:
    Creation operators first ('+'): 'a' then 'b_1', 'b_2', ...
    Annihilation operators second ('-'): 'a' then 'b_1', 'b_2', ...
    """
    family, idx, sign = osc
    sign_order = 0 if sign == '+' else 1
    family_order = 0 if family == 'a' else 1
    return (sign_order, family_order, idx)


def normal_order_monomial(monomial: Tuple[Tuple[str, int, str], ...], coeff: Fraction) -> Dict[Tuple[Tuple[str, int, str], ...], Fraction]:
    """
    Reduces a sequence of oscillators to normal-ordered form using CAR and CCR:
    {a_1^-, a_1^+} = 1, (a_1^+)^2 = (a_1^-)^2 = 0
    [b_j^-, b_k^+] = delta_jk, [b_j^pm, b_k^pm] = 0
    [b_j^pm, a_1^sigma] = 0
    """
    if coeff == 0:
        return {}
    
    # Check for (a_1^+)^2 = 0 or (a_1^-)^2 = 0
    for i in range(len(monomial) - 1):
        if monomial[i] == monomial[i+1] and monomial[i][0] == 'a':
            return {}

    # Find first out-of-order adjacent pair
    for i in range(len(monomial) - 1):
        o1 = monomial[i]
        o2 = monomial[i+1]
        if _osc_rank(o1) > _osc_rank(o2):
            # We must swap o1 and o2
            fam1, idx1, s1 = o1
            fam2, idx2, s2 = o2
            
            # Case 1: both 'a'
            if fam1 == 'a' and fam2 == 'a':
                if s1 == '-' and s2 == '+':
                    # a_1^- a_1^+ = 1 - a_1^+ a_1^-
                    tail = monomial[:i] + monomial[i+2:]
                    term_scalar = normal_order_monomial(tail, coeff)
                    swapped = monomial[:i] + (o2, o1) + monomial[i+2:]
                    term_swapped = normal_order_monomial(swapped, -coeff)
                    res = dict(term_scalar)
                    for k, v in term_swapped.items():
                        res[k] = res.get(k, Fraction(0)) + v
                    return {k: v for k, v in res.items() if v != 0}
                elif s1 == s2:
                    # a_1^s a_1^s = 0
                    return {}
            
            # Case 2: both 'b'
            elif fam1 == 'b' and fam2 == 'b':
                if s1 == '-' and s2 == '+':
                    # b_j^- b_k^+ = b_k^+ b_j^- + delta_jk
                    swapped = monomial[:i] + (o2, o1) + monomial[i+2:]
                    term_swapped = normal_order_monomial(swapped, coeff)
                    res = dict(term_swapped)
                    if idx1 == idx2:
                        tail = monomial[:i] + monomial[i+2:]
                        term_scalar = normal_order_monomial(tail, coeff)
                        for k, v in term_scalar.items():
                            res[k] = res.get(k, Fraction(0)) + v
                    return {k: v for k, v in res.items() if v != 0}
                else:
                    # [b_j^pm, b_k^pm] = 0
                    swapped = monomial[:i] + (o2, o1) + monomial[i+2:]
                    return normal_order_monomial(swapped, coeff)
                    
            # Case 3: one 'a' and one 'b'
            else:
                # [b, a] = 0, so they commute directly
                swapped = monomial[:i] + (o2, o1) + monomial[i+2:]
                return normal_order_monomial(swapped, coeff)
                
    # If already in normal order:
    return {monomial: coeff}


def normal_order_operator(op: Dict[Tuple[Tuple[str, int, str], ...], Fraction]) -> Dict[Tuple[Tuple[str, int, str], ...], Fraction]:
    result = {}
    for mono, coeff in op.items():
        reduced = normal_order_monomial(mono, coeff)
        for m, c in reduced.items():
            result[m] = result.get(m, Fraction(0)) + c
    return {k: v for k, v in result.items() if v != 0}


def multiply_operators(op1: Dict[Tuple, Fraction], op2: Dict[Tuple, Fraction]) -> Dict[Tuple, Fraction]:
    product = {}
    for m1, c1 in op1.items():
        for m2, c2 in op2.items():
            mono = m1 + m2
            coeff = c1 * c2
            reduced = normal_order_monomial(mono, coeff)
            for m, c in reduced.items():
                product[m] = product.get(m, Fraction(0)) + c
    return {k: v for k, v in product.items() if v != 0}


def graded_commutator(op1: Dict[Tuple, Fraction], p1: int,
                      op2: Dict[Tuple, Fraction], p2: int) -> Dict[Tuple, Fraction]:
    """Computes [op1, op2} = op1*op2 - (-1)^(p1*p2) * op2*op1"""
    prod1 = multiply_operators(op1, op2)
    prod2 = multiply_operators(op2, op1)
    sign = -1 if (p1 * p2) % 2 == 1 else 1
    
    result = dict(prod1)
    for m, c in prod2.items():
        result[m] = result.get(m, Fraction(0)) - sign * c
    return {k: v for k, v in result.items() if v != 0}


def get_generator_operators(n: int) -> Dict[str, Dict[Tuple, Fraction]]:
    """Returns mapping from generator name to its operator in normal-ordered form."""
    ops = {}
    
    # H_1 = a_1^+ a_1^- + b_1^+ b_1^-
    ops["H_1"] = {
        ((('a', 1, '+'), ('a', 1, '-'))): Fraction(1),
        ((('b', 1, '+'), ('b', 1, '-'))): Fraction(1),
    }
    
    # H_k = b_{k-1}^+ b_{k-1}^- - b_k^+ b_k^- for 2 <= k <= n
    for k in range(2, n + 1):
        ops[f"H_{k}"] = {
            ((('b', k - 1, '+'), ('b', k - 1, '-'))): Fraction(1),
            ((('b', k, '+'), ('b', k, '-'))): Fraction(-1),
        }
        
    # H_{n+1} = -b_n^+ b_n^- - 1/2
    ops[f"H_{n+1}"] = {
        ((('b', n, '+'), ('b', n, '-'))): Fraction(-1),
        (): Fraction(-1, 2)
    }
    
    # 2*delta roots
    for k in range(1, n + 1):
        ops[f"E_2del{k}_p"] = {((('b', k, '+'), ('b', k, '+'))): Fraction(1)}
        ops[f"E_2del{k}_m"] = {((('b', k, '-'), ('b', k, '-'))): Fraction(1)}
        
    # cross roots
    for i in range(1, n + 1):
        for j in range(i + 1, n + 1):
            ops[f"E_del{i}_del{j}_pp"] = {((('b', i, '+'), ('b', j, '+'))): Fraction(1)}
            ops[f"E_del{i}_del{j}_mm"] = {((('b', i, '-'), ('b', j, '-'))): Fraction(1)}
            ops[f"E_del{i}_del{j}_pm"] = {((('b', i, '+'), ('b', j, '-'))): Fraction(1)}
            ops[f"E_del{i}_del{j}_mp"] = {((('b', i, '-'), ('b', j, '+'))): Fraction(1)}
            
    # odd roots
    for k in range(1, n + 1):
        ops[f"E_eps1_del{k}_pp"] = {((('a', 1, '+'), ('b', k, '+'))): Fraction(1)}
        ops[f"E_eps1_del{k}_pm"] = {((('a', 1, '+'), ('b', k, '-'))): Fraction(1)}
        ops[f"E_eps1_del{k}_mp"] = {((('a', 1, '-'), ('b', k, '+'))): Fraction(1)}
        ops[f"E_eps1_del{k}_mm"] = {((('a', 1, '-'), ('b', k, '-'))): Fraction(1)}
        
    return {k: normal_order_operator(v) for k, v in ops.items()}


def get_generator_realizations(n: int) -> Dict[str, Any]:
    """Generates the JSON schema generator_realization block."""
    basis = get_basis(n)
    parity = get_parity(n)
    all_gens = basis["even"] + basis["odd"]
    
    realizations = {}
    for gen in all_gens:
        p = parity[gen]
        if gen == "H_1":
            realizations[gen] = {
                "standard_form": [
                    {"words": ["a_1_p", "a_1_m"], "coeff": "1"},
                    {"words": ["b_1_p", "b_1_m"], "coeff": "1"}
                ],
                "frappat_form": "a_1^+ a_1^- + b_1^+ b_1^-",
                "parity": 0
            }
        elif gen == f"H_{n+1}":
            realizations[gen] = {
                "standard_form": [
                    {"words": [f"b_{n}_p", f"b_{n}_m"], "coeff": "-1"},
                    {"words": [], "coeff": "-1/2"}
                ],
                "frappat_form": f"-b_{n}^+ b_{n}^- - 1/2",
                "parity": 0
            }
        elif gen.startswith("H_"):
            k = int(gen.split("_")[1])
            realizations[gen] = {
                "standard_form": [
                    {"words": [f"b_{k-1}_p", f"b_{k-1}_m"], "coeff": "1"},
                    {"words": [f"b_{k}_p", f"b_{k}_m"], "coeff": "-1"}
                ],
                "frappat_form": f"b_{k-1}^+ b_{k-1}^- - b_{k}^+ b_{k}^-",
                "parity": 0
            }
        elif gen.startswith("E_2del"):
            parts = gen.split("_")
            k = parts[1][4:]
            sign = parts[2]
            sign_char = "+" if sign == "p" else "-"
            realizations[gen] = {
                "standard_form": [
                    {"words": [f"b_{k}_{sign}", f"b_{k}_{sign}"], "coeff": "1"}
                ],
                "frappat_form": f"(b_{k}^{sign_char})^2",
                "parity": 0
            }
        elif gen.startswith("E_del"):
            # E_del{i}_del{j}_{s1}{s2}
            parts = gen.split("_")
            i = parts[1][3:]
            j = parts[2][3:]
            signs = parts[3]
            s1_char = "+" if signs[0] == "p" else "-"
            s2_char = "+" if signs[1] == "p" else "-"
            realizations[gen] = {
                "standard_form": [
                    {"words": [f"b_{i}_{signs[0]}", f"b_{j}_{signs[1]}"], "coeff": "1"}
                ],
                "frappat_form": f"b_{i}^{s1_char} b_{j}^{s2_char}",
                "parity": 0
            }
        elif gen.startswith("E_eps1_del"):
            parts = gen.split("_")
            k = parts[2][3:]
            signs = parts[3]
            s_f = "+" if signs[0] == "p" else "-"
            s_b = "+" if signs[1] == "p" else "-"
            realizations[gen] = {
                "standard_form": [
                    {"words": [f"a_1_{signs[0]}", f"b_{k}_{signs[1]}"], "coeff": "1"}
                ],
                "frappat_form": f"a_1^{s_f} b_{k}^{s_b}",
                "parity": 1
            }
            
    return {
        "description": "Standard form with PBW ordering",
        "ordering": f"a_1_p, a_1_m, " + ", ".join([f"b_{i}_p, b_{i}_m" for i in range(1, n + 1)]),
        "realizations": realizations
    }


def decompose_operator(op: Dict[Tuple, Fraction], n: int,
                       gen_ops: Dict[str, Dict[Tuple, Fraction]],
                       cartan_matrix_inv: Any) -> Dict[str, Fraction]:
    """
    Expresses a normal-ordered operator as a linear combination of generators.
    """
    if not op:
        return {}
        
    decomp = {}
    rem = dict(op)
    
    # 1. Non-Cartan generators have unique monomials:
    for gen, g_op in gen_ops.items():
        if gen.startswith("H_"):
            continue
        mono = list(g_op.keys())[0]
        if mono in rem:
            c = rem[mono]
            if c != 0:
                decomp[gen] = c
                del rem[mono]
                
    # 2. The remainder must be purely Cartan (diagonal monomials + scalar)
    if rem:
        # Solve for Cartans:
        # Diagonal monomials are:
        # a_1^+ a_1^-
        # b_k^+ b_k^- for k=1..n
        # and constant ()
        diag_vec = [Fraction(0)] * (n + 1)
        # index 0: a_1^+ a_1^-
        # index k (1..n): b_k^+ b_k^-
        mono_a = (('a', 1, '+'), ('a', 1, '-'))
        if mono_a in rem:
            diag_vec[0] = rem[mono_a]
            
        for k in range(1, n + 1):
            mono_b = (('b', k, '+'), ('b', k, '-'))
            if mono_b in rem:
                diag_vec[k] = rem[mono_b]
                
        # cartan_matrix_inv maps diag_vec -> cartan coefficients
        cartan_coeffs = cartan_matrix_inv(diag_vec)
        for idx, coeff in enumerate(cartan_coeffs):
            if coeff != 0:
                decomp[f"H_{idx+1}"] = coeff
                
    return decomp


def _build_cartan_solver(n: int):
    """
    Builds a function mapping [c_a, c_b1, ..., c_bn] -> [h_1, ..., h_{n+1}]
    In terms of Cartans:
    diag_vec = [c_a, c_b1, ..., c_bn]
    H_1: c_a=1, c_b1=1
    H_k (2<=k<=n): c_b{k-1}=1, c_bk=-1
    H_{n+1}: c_bn=-1
    """
    # From H_{n+1}: h_{n+1} = -c_bn - (contributions from above?)
    # Let's solve systematically:
    # c_bn = -h_{n+1} - (h_n) ... wait:
    # c_bk = (coeff of b_k^+ b_k^-)
    # H_1 contributes +1 to c_b1
    # H_2 contributes +1 to c_b1, -1 to c_b2
    # H_k contributes +1 to c_b{k-1}, -1 to c_bk
    # H_{n+1} contributes -1 to c_bn.
    # Also H_1 contributes +1 to c_a.
    # Therefore:
    # h_1 = c_a.
    # Then:
    # c_b1 = h_1 + h_2 (if n>=2) or h_1 - h_2? Wait:
    # If n=1: H_1 = a^+ a^- + b_1^+ b_1^-, H_2 = -b_1^+ b_1^- - 1/2.
    # c_a = h_1  => h_1 = c_a.
    # c_b1 = h_1 - h_2 => h_2 = h_1 - c_b1 = c_a - c_b1.
    # Check: h_1 H_1 + h_2 H_2:
    # coeff of a: h_1 = c_a. Correct!
    # coeff of b_1: h_1 - h_2 = c_b1. Correct!
    def solver(diag_vec):
        c_a = diag_vec[0]
        c_b = diag_vec[1:]
        h = [Fraction(0)] * (n + 1)
        h[0] = c_a
        
        # c_b[k-1] = coeff of b_k
        # For k=1..n-1: c_b[k-1] = h[k-1] - h[k]? Wait, let's look at H:
        # H_1: a + b_1
        # H_2: b_1 - b_2
        # H_3: b_2 - b_3
        # ...
        # H_n: b_{n-1} - b_n
        # H_{n+1}: -b_n
        #
        # Thus:
        # c_a = h[0]
        # c_b[0] = h[0] + h[1]  (for n>=2) => h[1] = c_b[0] - h[0]
        # c_b[k-1] = -h[k-1] + h[k] ??? Let's check:
        # H_k has +b_{k-1} and -b_k.
        # So b_{k-1} receives -h_{k-1}? No! H_k has +b_{k-1}^+ b_{k-1}^-.
        # So b_1 has: +h[0] (from H_1) + h[1] (from H_2).
        # b_2 has: -h[1] (from H_2) + h[2] (from H_3).
        # b_k has: -h[k-1] (from H_k) + h[k] (from H_{k+1}) for 1 <= k <= n-1.
        # b_n has: -h[n-1] (from H_n) - h[n] (from H_{n+1}).
        
        # Let's verify for n=1:
        # c_a = h[0]
        # c_b[0] = h[0] - h[1] => h[1] = h[0] - c_b[0] = c_a - c_b[0].
        if n == 1:
            h[0] = c_a
            h[1] = c_a - c_b[0]
            return h
            
        # For general n >= 2:
        h[0] = c_a
        h[1] = c_b[0] - h[0]
        for k in range(2, n):
            h[k] = c_b[k - 1] + h[k - 1]
            
        h[n] = -c_b[n - 1] - h[n - 1]
        return h

    return solver


def compute_structure_constants(n: int) -> List[Dict[str, str]]:
    """
    Computes all non-zero graded brackets [X, Y} = sum_Z c_{XY}^Z Z.
    """
    basis = get_basis(n)
    all_gens = basis["even"] + basis["odd"]
    parity = get_parity(n)
    gen_ops = get_generator_operators(n)
    cartan_solver = _build_cartan_solver(n)
    
    constants = []
    for i, x in enumerate(all_gens):
        px = parity[x]
        op_x = gen_ops[x]
        for j, y in enumerate(all_gens):
            py = parity[y]
            op_y = gen_ops[y]
            
            bracket_op = graded_commutator(op_x, px, op_y, py)
            if not bracket_op:
                continue
                
            decomp = decompose_operator(bracket_op, n, gen_ops, cartan_solver)
            for z, coeff in decomp.items():
                if coeff != 0:
                    c_str = str(coeff.numerator) if coeff.denominator == 1 else f"{coeff.numerator}/{coeff.denominator}"
                    constants.append({
                        "X": x,
                        "Y": y,
                        "Z": z,
                        "coeff": c_str,
                        "sign_rule": "graded"
                    })
    return constants


def generate_structure_json(n: int) -> Dict[str, Any]:
    """Builds complete Schema 1 JSON dictionary for C(n+1)."""
    basis = get_basis(n)
    parity = get_parity(n)
    realizations = get_generator_realizations(n)
    constants = compute_structure_constants(n)
    
    even_dim = 2 * n**2 + n + 1
    odd_dim = 4 * n
    total_dim = even_dim + odd_dim
    
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
            "dimension_formulas": {
                "even": "2*n^2 + n + 1",
                "odd": "4*n",
                "total": "2*n^2 + 5*n + 1"
            },
            "dimension": {
                "total": total_dim,
                "even": even_dim,
                "odd": odd_dim
            }
        },
        "oscillator_generators": {
            "fermions": {
                "count": 2,
                "m": 1,
                "labels": ["a_1_p", "a_1_m"],
                "description": "Standard fermionic pair a_1^± satisfying CAR"
            },
            "bosons": {
                "count": 2 * n,
                "n": n,
                "labels": [f"b_{i}_{s}" for i in range(1, n + 1) for s in ["p", "m"]],
                "description": f"Bosonic oscillators b_i^± with i=1,...,{n} satisfying CCR"
            }
        },
        "oscillator_relations": {
            "standard_fermion_anticommutators": {
                "description": "Canonical anticommutation relations (CAR) for fermionic oscillators",
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
                "boson_fermion": "[b_i^±, a_1^σ] = 0 (undeformed)"
            }
        },
        "central_elements": {
            "kappa": {
                "parity": 1,
                "nilpotent": True,
                "relation": "kappa^2 = 0",
                "description": "Odd nilpotent central extension parameter mediating inhomogeneous deformation"
            },
            "K": {
                "parity": 0,
                "scalar_value": 1,
                "description": "Even central element normalized to identity scalar"
            }
        },
        "basis": basis,
        "parity": parity,
        "generator_realization": realizations,
        "structure_constants": constants,
        "metadata": {
            "generated_by": "src/C_generators.py",
            "generation_date": "2026-10-05",
            "references": [
                "Frappat, Sciarrino, Sorba (2000), Dictionary on Lie Algebras and Superalgebras",
                "Bakalov and Sullivan (2017)"
            ]
        }
    }
    return data


def save_structure_json(n: int, output_dir: str = "data") -> str:
    """Generates and writes C_{n}_structure.json to output_dir."""
    os.makedirs(output_dir, exist_ok=True)
    filepath = os.path.join(output_dir, f"C_{n}_structure.json")
    data = generate_structure_json(n)
    with open(filepath, "w") as f:
        json.dump(data, f, indent=2)
    return filepath


if __name__ == "__main__":
    for rank in [1, 2, 3]:
        path = save_structure_json(rank)
        print(f"Generated {path}")
