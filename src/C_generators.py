"""C(n+1) = osp(2|2n) Lie Superalgebra Basis and Structure Constants Generator.

This script constructs the basis, oscillator realizations, and graded Lie superalgebra
structure constants for C(n+1) = osp(2|2n) for n = 1, 2, 3, outputting Schema 1 JSON
conforming to docs/json_schema_specification.md.
"""

from collections import defaultdict
from fractions import Fraction
import json
import os
from typing import Dict, List, Tuple, Any

def get_oscillator_order(n: int) -> List[str]:
    """Return standard PBW normal ordering for oscillators: fermions first, then bosons."""
    order = ['a_1_p', 'a_1_m']
    for j in range(1, n + 1):
        order.extend([f'b_{j}_p', f'b_{j}_m'])
    return order

def osc_parity(name: str) -> int:
    """Return 1 for fermionic oscillator, 0 for bosonic."""
    return 1 if name.startswith('a_') else 0

def normal_order_word(word: List[str], coeff: Fraction, osc_rank: Dict[str, int]) -> Dict[Tuple[str, ...], Fraction]:
    """Put an oscillator word into normal order using CAR and CCR."""
    for i in range(len(word) - 1):
        u, v = word[i], word[i + 1]
        if u == v and osc_parity(u) == 1:
            # Nilpotency: (a_1^±)^2 = 0
            return {}
        if osc_rank[u] > osc_rank[v]:
            p_uv = osc_parity(u) * osc_parity(v)
            sign = -1 if p_uv == 1 else 1
            comm = 0
            if u == 'a_1_m' and v == 'a_1_p':
                # {a_1^-, a_1^+} = 1 => a_1^- a_1^+ = 1 - a_1^+ a_1^-
                comm = 1
            elif u.startswith('b_') and v.startswith('b_'):
                uj, us = u.split('_')[1], u.split('_')[2]
                vj, vs = v.split('_')[1], v.split('_')[2]
                if uj == vj and us == 'm' and vs == 'p':
                    # [b_j^-, b_j^+] = 1 => b_j^- b_j^+ = b_j^+ b_j^- + 1
                    comm = 1
            
            res: Dict[Tuple[str, ...], Fraction] = defaultdict(Fraction)
            w1 = word[:i] + [v, u] + word[i + 2:]
            for nw, c in normal_order_word(w1, coeff * sign, osc_rank).items():
                res[nw] += c
            if comm != 0:
                w2 = word[:i] + word[i + 2:]
                for nw, c in normal_order_word(w2, coeff * comm, osc_rank).items():
                    res[nw] += c
            return {k: v for k, v in res.items() if v != 0}
            
    for i in range(len(word) - 1):
        if word[i] == word[i + 1] and osc_parity(word[i]) == 1:
            return {}
    return {tuple(word): coeff}

def poly_add(p1: Dict[Tuple[str, ...], Fraction], p2: Dict[Tuple[str, ...], Fraction]) -> Dict[Tuple[str, ...], Fraction]:
    res = defaultdict(Fraction, p1)
    for k, v in p2.items():
        res[k] += v
    return {k: v for k, v in res.items() if v != 0}

def poly_sub(p1: Dict[Tuple[str, ...], Fraction], p2: Dict[Tuple[str, ...], Fraction]) -> Dict[Tuple[str, ...], Fraction]:
    res = defaultdict(Fraction, p1)
    for k, v in p2.items():
        res[k] -= v
    return {k: v for k, v in res.items() if v != 0}

def poly_mul(p1: Dict[Tuple[str, ...], Fraction], p2: Dict[Tuple[str, ...], Fraction], osc_rank: Dict[str, int]) -> Dict[Tuple[str, ...], Fraction]:
    res: Dict[Tuple[str, ...], Fraction] = defaultdict(Fraction)
    for w1, c1 in p1.items():
        for w2, c2 in p2.items():
            w = list(w1 + w2)
            for nw, c in normal_order_word(w, c1 * c2, osc_rank).items():
                res[nw] += c
    return {k: v for k, v in res.items() if v != 0}

def poly_bracket(p1: Dict[Tuple[str, ...], Fraction], parity1: int,
                 p2: Dict[Tuple[str, ...], Fraction], parity2: int,
                 osc_rank: Dict[str, int]) -> Dict[Tuple[str, ...], Fraction]:
    """Compute graded Lie bracket [X, Y} = XY - (-1)^{p(X)p(Y)} YX."""
    sign = -1 if (parity1 * parity2) == 1 else 1
    xy = poly_mul(p1, p2, osc_rank)
    yx = poly_mul(p2, p1, osc_rank)
    return poly_sub(xy, {k: v * sign for k, v in yx.items()})

def build_basis(n: int) -> Tuple[List[str], List[str]]:
    """Build even and odd basis generator names under PBW Option A."""
    even_basis = []
    # Cartans
    for k in range(1, n + 2):
        even_basis.append(f'H_{k}')
    # Long positive roots
    for k in range(1, n + 1):
        even_basis.append(f'E_2del{k}_p')
    # Short positive roots
    for i in range(1, n + 1):
        for j in range(i + 1, n + 1):
            even_basis.append(f'E_del{i}_del{j}_pp')
    # Long negative roots
    for k in range(1, n + 1):
        even_basis.append(f'E_2del{k}_m')
    # Short negative roots
    for i in range(1, n + 1):
        for j in range(i + 1, n + 1):
            even_basis.append(f'E_del{i}_del{j}_mm')
    # Mixed roots
    for i in range(1, n + 1):
        for j in range(i + 1, n + 1):
            even_basis.append(f'E_del{i}_del{j}_pm')
    for i in range(1, n + 1):
        for j in range(i + 1, n + 1):
            even_basis.append(f'E_del{i}_del{j}_mp')

    odd_basis = []
    for k in range(1, n + 1):
        odd_basis.append(f'E_eps1_del{k}_pp')
    for k in range(1, n + 1):
        odd_basis.append(f'E_eps1_del{k}_pm')
    for k in range(1, n + 1):
        odd_basis.append(f'E_eps1_del{k}_mp')
    for k in range(1, n + 1):
        odd_basis.append(f'E_eps1_del{k}_mm')

    return even_basis, odd_basis

def build_generator_realizations(n: int) -> Tuple[Dict[str, Dict[Tuple[str, ...], Fraction]], Dict[str, int], Dict[str, Dict[str, Any]]]:
    """Return dictionary of polynomial realizations, parities, and schema details."""
    even_basis, odd_basis = build_basis(n)
    polys: Dict[str, Dict[Tuple[str, ...], Fraction]] = {}
    parities: Dict[str, int] = {}
    schema_realizations: Dict[str, Dict[str, Any]] = {}

    # H_1 = a_1^+ a_1^- + b_1^+ b_1^-
    polys['H_1'] = {('a_1_p', 'a_1_m'): Fraction(1), ('b_1_p', 'b_1_m'): Fraction(1)}
    parities['H_1'] = 0
    schema_realizations['H_1'] = {
        'standard_form': [
            {'words': ['a_1_p', 'a_1_m'], 'coeff': '1'},
            {'words': ['b_1_p', 'b_1_m'], 'coeff': '1'}
        ],
        'frappat_form': 'a_1^+ a_1^- + b_1^+ b_1^-',
        'parity': 0
    }

    for k in range(2, n + 1):
        polys[f'H_{k}'] = {
            (f'b_{k-1}_p', f'b_{k-1}_m'): Fraction(1),
            (f'b_{k}_p', f'b_{k}_m'): Fraction(-1)
        }
        parities[f'H_{k}'] = 0
        schema_realizations[f'H_{k}'] = {
            'standard_form': [
                {'words': [f'b_{k-1}_p', f'b_{k-1}_m'], 'coeff': '1'},
                {'words': [f'b_{k}_p', f'b_{k}_m'], 'coeff': '-1'}
            ],
            'frappat_form': f'b_{k-1}^+ b_{k-1}^- - b_{k}^+ b_{k}^-',
            'parity': 0
        }

    polys[f'H_{n+1}'] = {
        (f'b_{n}_p', f'b_{n}_m'): Fraction(-1),
        (): Fraction(-1, 2)
    }
    parities[f'H_{n+1}'] = 0
    schema_realizations[f'H_{n+1}'] = {
        'standard_form': [
            {'words': [f'b_{n}_p', f'b_{n}_m'], 'coeff': '-1'},
            {'words': [], 'coeff': '-1/2'}
        ],
        'frappat_form': f'-b_{n}^+ b_{n}^- - 1/2',
        'parity': 0
    }

    # Long even roots
    for k in range(1, n + 1):
        polys[f'E_2del{k}_p'] = {(f'b_{k}_p', f'b_{k}_p'): Fraction(1)}
        parities[f'E_2del{k}_p'] = 0
        schema_realizations[f'E_2del{k}_p'] = {
            'standard_form': [{'words': [f'b_{k}_p', f'b_{k}_p'], 'coeff': '1'}],
            'frappat_form': f'(b_{k}^+)^2',
            'parity': 0
        }
        polys[f'E_2del{k}_m'] = {(f'b_{k}_m', f'b_{k}_m'): Fraction(1)}
        parities[f'E_2del{k}_m'] = 0
        schema_realizations[f'E_2del{k}_m'] = {
            'standard_form': [{'words': [f'b_{k}_m', f'b_{k}_m'], 'coeff': '1'}],
            'frappat_form': f'(b_{k}^-)^2',
            'parity': 0
        }

    # Short even roots
    for i in range(1, n + 1):
        for j in range(i + 1, n + 1):
            polys[f'E_del{i}_del{j}_pp'] = {(f'b_{i}_p', f'b_{j}_p'): Fraction(1)}
            parities[f'E_del{i}_del{j}_pp'] = 0
            schema_realizations[f'E_del{i}_del{j}_pp'] = {
                'standard_form': [{'words': [f'b_{i}_p', f'b_{j}_p'], 'coeff': '1'}],
                'frappat_form': f'b_{i}^+ b_{j}^+',
                'parity': 0
            }

            polys[f'E_del{i}_del{j}_mm'] = {(f'b_{i}_m', f'b_{j}_m'): Fraction(1)}
            parities[f'E_del{i}_del{j}_mm'] = 0
            schema_realizations[f'E_del{i}_del{j}_mm'] = {
                'standard_form': [{'words': [f'b_{i}_m', f'b_{j}_m'], 'coeff': '1'}],
                'frappat_form': f'b_{i}^- b_{j}^-',
                'parity': 0
            }

            polys[f'E_del{i}_del{j}_pm'] = {(f'b_{i}_p', f'b_{j}_m'): Fraction(1)}
            parities[f'E_del{i}_del{j}_pm'] = 0
            schema_realizations[f'E_del{i}_del{j}_pm'] = {
                'standard_form': [{'words': [f'b_{i}_p', f'b_{j}_m'], 'coeff': '1'}],
                'frappat_form': f'b_{i}^+ b_{j}^-',
                'parity': 0
            }

            polys[f'E_del{i}_del{j}_mp'] = {(f'b_{i}_m', f'b_{j}_p'): Fraction(1)}
            parities[f'E_del{i}_del{j}_mp'] = 0
            schema_realizations[f'E_del{i}_del{j}_mp'] = {
                'standard_form': [{'words': [f'b_{i}_m', f'b_{j}_p'], 'coeff': '1'}],
                'frappat_form': f'b_{i}^- b_{j}^+',
                'parity': 0
            }

    # Odd roots
    for k in range(1, n + 1):
        polys[f'E_eps1_del{k}_pp'] = {('a_1_p', f'b_{k}_p'): Fraction(1)}
        parities[f'E_eps1_del{k}_pp'] = 1
        schema_realizations[f'E_eps1_del{k}_pp'] = {
            'standard_form': [{'words': ['a_1_p', f'b_{k}_p'], 'coeff': '1'}],
            'frappat_form': f'a_1^+ b_{k}^+',
            'parity': 1
        }

        polys[f'E_eps1_del{k}_pm'] = {('a_1_p', f'b_{k}_m'): Fraction(1)}
        parities[f'E_eps1_del{k}_pm'] = 1
        schema_realizations[f'E_eps1_del{k}_pm'] = {
            'standard_form': [{'words': ['a_1_p', f'b_{k}_m'], 'coeff': '1'}],
            'frappat_form': f'a_1^+ b_{k}^-',
            'parity': 1
        }

        polys[f'E_eps1_del{k}_mp'] = {('a_1_m', f'b_{k}_p'): Fraction(1)}
        parities[f'E_eps1_del{k}_mp'] = 1
        schema_realizations[f'E_eps1_del{k}_mp'] = {
            'standard_form': [{'words': ['a_1_m', f'b_{k}_p'], 'coeff': '1'}],
            'frappat_form': f'a_1^- b_{k}^+',
            'parity': 1
        }

        polys[f'E_eps1_del{k}_mm'] = {('a_1_m', f'b_{k}_m'): Fraction(1)}
        parities[f'E_eps1_del{k}_mm'] = 1
        schema_realizations[f'E_eps1_del{k}_mm'] = {
            'standard_form': [{'words': ['a_1_m', f'b_{k}_m'], 'coeff': '1'}],
            'frappat_form': f'a_1^- b_{k}^-',
            'parity': 1
        }

    return polys, parities, schema_realizations

def solve_exact_linear(A: List[List[Fraction]], b: List[Fraction]) -> List[Fraction]:
    """Solve A x = b exactly using Gaussian elimination over Fraction."""
    m = len(A)
    num_vars = len(A[0])
    M = [list(row) + [b[i]] for i, row in enumerate(A)]
    row = 0
    pivots: List[Tuple[int, int]] = []
    for col in range(num_vars):
        if row >= m:
            break
        i = row
        while i < m and M[i][col] == 0:
            i += 1
        if i == m:
            continue
        M[row], M[i] = M[i], M[row]
        pivot = M[row][col]
        M[row] = [val / pivot for val in M[row]]
        for j in range(m):
            if j != row and M[j][col] != 0:
                factor = M[j][col]
                M[j] = [M[j][c] - factor * M[row][c] for c in range(num_vars + 1)]
        pivots.append((row, col))
        row += 1

    for r in range(len(pivots), m):
        if M[r][num_vars] != 0:
            raise ValueError("Inconsistent linear system in bracket decomposition!")

    sol = [Fraction(0)] * num_vars
    for r, c in pivots:
        sol[c] = M[r][num_vars]
    return sol

def compute_structure_constants(n: int) -> Tuple[List[Dict[str, str]], Dict[str, Any]]:
    """Compute all non-zero graded brackets [X, Y} and full Schema 1 JSON."""
    osc_order = get_oscillator_order(n)
    osc_rank = {name: i for i, name in enumerate(osc_order)}
    even_basis, odd_basis = build_basis(n)
    total_basis = even_basis + odd_basis
    polys, parities, schema_realizations = build_generator_realizations(n)

    # Collect all unique monomials present in basis generators
    all_words = sorted(list({w for poly in polys.values() for w in poly.keys()}))
    word_to_idx = {w: i for i, w in enumerate(all_words)}

    # Build basis matrix: rows = monomials, columns = basis generators
    A: List[List[Fraction]] = [[Fraction(0)] * len(total_basis) for _ in all_words]
    for col_idx, gen_name in enumerate(total_basis):
        for w, c in polys[gen_name].items():
            A[word_to_idx[w]][col_idx] = c

    structure_constants = []
    for x in total_basis:
        for y in total_basis:
            br = poly_bracket(polys[x], parities[x], polys[y], parities[y], osc_rank)
            if not br:
                continue
            b = [Fraction(0)] * len(all_words)
            for w, c in br.items():
                if w not in word_to_idx:
                    raise ValueError(f"Monomial {w} in [{x}, {y}] not in basis word span!")
                b[word_to_idx[w]] = c
            
            coeffs = solve_exact_linear(A, b)
            for z_idx, coeff in enumerate(coeffs):
                if coeff != 0:
                    structure_constants.append({
                        "X": x,
                        "Y": y,
                        "Z": total_basis[z_idx],
                        "coeff": str(coeff.numerator) if coeff.denominator == 1 else f"{coeff.numerator}/{coeff.denominator}",
                        "sign_rule": "graded"
                    })

    # Assemble full Schema 1 dictionary
    schema_1 = {
        "schema_version": "5.0",
        "algebra": {
            "family": "C",
            "m": 1,
            "n": n,
            "cartan_type": f"C({n+1})",
            "alternative_notation": {
                "osp": f"osp(2|{2*n})",
                "dimension_formula": {
                    "even": "2*n^2 + n + 1",
                    "odd": "4*n",
                    "total": "2*n^2 + 5*n + 1"
                }
            },
            "dimension": {
                "total": 2 * n**2 + 5 * n + 1,
                "even": 2 * n**2 + n + 1,
                "odd": 4 * n
            }
        },
        "central_elements": {
            "kappa": {
                "parity": 1,
                "nilpotent_order": 2,
                "relation": "kappa^2 = 0",
                "description": "Odd central element governing inhomogeneous deformation"
            },
            "K": {
                "parity": 0,
                "relation": "K = 1",
                "description": "Even central identity element"
            }
        },
        "oscillator_generators": {
            "fermions": {
                "count": 2,
                "m": 1,
                "labels": ["a_1_p", "a_1_m"],
                "description": "Standard fermionic CAR pair a_1^±"
            },
            "bosons": {
                "count": 2 * n,
                "n": n,
                "labels": [f"b_{j}_{s}" for j in range(1, n + 1) for s in ["p", "m"]],
                "description": f"Bosonic oscillators b_i^± with i=1,...,{n}"
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
                "boson_fermion": "[b_i^±, a_1^σ] = 0 for all i, σ ∈ {+,-}"
            }
        },
        "basis": {
            "even": even_basis,
            "odd": odd_basis,
            "ordering_convention": "PBW: kappa < [odd: Polarity-First] < [even: Cartans, pos roots, neg roots, mixed roots]"
        },
        "parity": parities,
        "generator_realization": {
            "ordering": ", ".join(osc_order),
            "realizations": schema_realizations
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

    return structure_constants, schema_1

def generate_all_schema_1(output_dir: str = "data"):
    """Generate C_1_structure.json, C_2_structure.json, and C_3_structure.json."""
    os.makedirs(output_dir, exist_ok=True)
    for n in [1, 2, 3]:
        sc, schema_1 = compute_structure_constants(n)
        filepath = os.path.join(output_dir, f"C_{n}_structure.json")
        with open(filepath, "w") as f:
            json.dump(schema_1, f, indent=2)
        print(f"Generated {filepath}: {len(schema_1['basis']['even'])} even, {len(schema_1['basis']['odd'])} odd, {len(sc)} structure constants")

if __name__ == "__main__":
    generate_all_schema_1()
