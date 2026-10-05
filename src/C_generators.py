import json
import os
from fractions import Fraction

def format_coeff(c):
    if c.denominator == 1:
        return str(c.numerator)
    return f"{c.numerator}/{c.denominator}"

def parity(gen_name):
    if "eps1" in gen_name:
        return 1
    if "kappa" in gen_name:
        return 1
    return 0

def get_osc_parity(osc):
    if "a_" in osc:
        return 1
    return 0

# Normal ordering rules
# standard order: a_1_p, a_1_m, b_1_p, b_1_m, b_2_p, b_2_m, ...
def get_osc_rank(osc):
    if osc == 'a_1_p': return 0
    if osc == 'a_1_m': return 1
    if osc.startswith('b_'):
        parts = osc.split('_')
        idx = int(parts[1])
        is_m = (parts[2] == 'm')
        return 1 + 2*idx + (1 if is_m else 0)
    return 999

def swap_oscillators(X, Y):
    """
    Returns (sign, scalar) for X Y = sign * Y X + scalar
    where X > Y in rank.
    """
    px = get_osc_parity(X)
    py = get_osc_parity(Y)
    
    if X == 'a_1_m' and Y == 'a_1_p':
        return (-1, Fraction(1))
    
    if X.startswith('b_') and Y.startswith('b_'):
        partsX = X.split('_')
        partsY = Y.split('_')
        if partsX[1] == partsY[1]:
            if partsX[2] == 'm' and partsY[2] == 'p':
                return (1, Fraction(1))
    
    sign = -1 if (px == 1 and py == 1) else 1
    return (sign, Fraction(0))

def normal_order_monomial(words):
    # Returns a list of (coeff, words_tuple)
    # words is a list of strings
    if len(words) <= 1:
        return [(Fraction(1), tuple(words))]
    
    # Bubble sort approach
    terms = [(Fraction(1), list(words))]
    
    changed = True
    while changed:
        changed = False
        new_terms = []
        for coeff, term in terms:
            term_changed = False
            for i in range(len(term) - 1):
                X, Y = term[i], term[i+1]
                if get_osc_rank(X) > get_osc_rank(Y):
                    # swap needed: X Y = sign * Y X + scalar
                    sign, scalar = swap_oscillators(X, Y)
                    
                    # Add swapped term
                    swapped = term[:]
                    swapped[i], swapped[i+1] = Y, X
                    new_terms.append((coeff * sign, swapped))
                    
                    # Add scalar term if non-zero
                    if scalar != 0:
                        reduced = term[:i] + term[i+2:]
                        new_terms.append((coeff * scalar, reduced))
                    
                    term_changed = True
                    changed = True
                    break
            
            if not term_changed:
                new_terms.append((coeff, term))
                
        # Consolidate terms
        cons = {}
        for c, t in new_terms:
            tt = tuple(t)
            cons[tt] = cons.get(tt, Fraction(0)) + c
        
        terms = [(c, list(t)) for t, c in cons.items() if c != 0]
        
    return [(c, tuple(t)) for c, t in terms if c != 0]

def multiply_polys(p1, p2):
    # p1, p2 are dicts: tuple -> coeff
    res = {}
    for t1, c1 in p1.items():
        for t2, c2 in p2.items():
            c = c1 * c2
            combined = list(t1) + list(t2)
            no_terms = normal_order_monomial(combined)
            for sub_c, sub_t in no_terms:
                res[sub_t] = res.get(sub_t, Fraction(0)) + c * sub_c
    return {k: v for k, v in res.items() if v != 0}

def add_polys(p1, p2, sign=1):
    res = dict(p1)
    for t, c in p2.items():
        res[t] = res.get(t, Fraction(0)) + sign * c
    return {k: v for k, v in res.items() if v != 0}

def scale_poly(p, scalar):
    res = {k: v * scalar for k, v in p.items()}
    return {k: v for k, v in res.items() if v != 0}

def commutator(p1, p2, p1_parity, p2_parity):
    # [p1, p2} = p1 p2 - (-1)^{p1 * p2} p2 p1
    s = -1 if (p1_parity == 1 and p2_parity == 1) else 1
    term1 = multiply_polys(p1, p2)
    term2 = multiply_polys(p2, p1)
    return add_polys(term1, term2, sign=-s)

def build_generators(n):
    gens = {}
    
    # H_1 = a_1^+ a_1^- + b_1^+ b_1^-
    gens['H_1'] = {
        ('a_1_p', 'a_1_m'): Fraction(1),
        ('b_1_p', 'b_1_m'): Fraction(1)
    }
    
    # H_k for k=2..n
    for k in range(2, n+1):
        gens[f'H_{k}'] = {
            (f'b_{k-1}_p', f'b_{k-1}_m'): Fraction(1),
            (f'b_{k}_p', f'b_{k}_m'): Fraction(-1)
        }
        
    # H_{n+1} = -b_n^+ b_n^- - 1/2
    gens[f'H_{n+1}'] = {
        (f'b_{n}_p', f'b_{n}_m'): Fraction(-1),
        (): Fraction(-1, 2)
    }
    
    # E_2del{k}_p, E_2del{k}_m
    for k in range(1, n+1):
        gens[f'E_2del{k}_p'] = {(f'b_{k}_p', f'b_{k}_p'): Fraction(1, 2)}
        gens[f'E_2del{k}_m'] = {(f'b_{k}_m', f'b_{k}_m'): Fraction(1, 2)}
        
    # E_del{i}_del{j}_...
    for i in range(1, n+1):
        for j in range(i+1, n+1):
            gens[f'E_del{i}_del{j}_pp'] = {(f'b_{i}_p', f'b_{j}_p'): Fraction(1)}
            gens[f'E_del{i}_del{j}_mm'] = {(f'b_{i}_m', f'b_{j}_m'): Fraction(1)}
            gens[f'E_del{i}_del{j}_pm'] = {(f'b_{i}_p', f'b_{j}_m'): Fraction(1)}
            gens[f'E_del{i}_del{j}_mp'] = {(f'b_{i}_m', f'b_{j}_p'): Fraction(1)}
            
    # E_eps1_del{k}_...
    for k in range(1, n+1):
        gens[f'E_eps1_del{k}_pp'] = {('a_1_p', f'b_{k}_p'): Fraction(1)}
        gens[f'E_eps1_del{k}_pm'] = {('a_1_p', f'b_{k}_m'): Fraction(1)}
        gens[f'E_eps1_del{k}_mp'] = {('a_1_m', f'b_{k}_p'): Fraction(1)}
        gens[f'E_eps1_del{k}_mm'] = {('a_1_m', f'b_{k}_m'): Fraction(1)}
        
    # Normal order everything
    for k, v in gens.items():
        no_v = {}
        for term, coeff in v.items():
            no_terms = normal_order_monomial(list(term))
            for c, t in no_terms:
                no_v[t] = no_v.get(t, Fraction(0)) + coeff * c
        gens[k] = {t: c for t, c in no_v.items() if c != 0}
        
    return gens

def get_basis_lists(n, gens):
    even = []
    odd = []
    for k in gens:
        if parity(k) == 0:
            even.append(k)
        else:
            odd.append(k)
            
    # Sort odd by k, then pp, pm, mp, mm
    def odd_sort_key(k):
        # E_eps1_del{k}_{suf}
        parts = k.split('_')
        idx = int(parts[2][3:])
        suf = parts[3]
        suf_val = {'pp': 0, 'pm': 1, 'mp': 2, 'mm': 3}[suf]
        return (idx, suf_val)
    odd.sort(key=odd_sort_key)
    
    # Sort even: H's, then E's (lexicographically or just by parts)
    def even_sort_key(k):
        if k.startswith('H'):
            return (0, int(k.split('_')[1]))
        return (1, k)
    even.sort(key=even_sort_key)
    
    return even, odd

def generate_schema(n):
    gens = build_generators(n)
    even, odd = get_basis_lists(n, gens)
    
    # Compute structure constants
    sc = []
    all_basis = odd + even # PBW ordering [odd] < [even]
    basis_inv = {k: gens[k] for k in all_basis}
    
    # Helper to find representation of a poly in terms of basis
    def express_in_basis(poly):
        # The basis polynomials are all linearly independent by definition.
        # Simple greedy matching because each basis element has a unique leading term in normal order,
        # or we can just match exactly. Actually, they are orthogonal in their term support!
        # Except Cartans which overlap on ().
        # Let's just solve the linear system for the coefficients.
        
        # We need a quick linear solver, but actually our generators are very sparse.
        # Roots are single monomials (except maybe sign/factor).
        # Cartans are linear combinations.
        # Let's collect all terms.
        terms = set(poly.keys())
        for k in gens:
            terms.update(gens[k].keys())
        terms = list(terms)
        
        # Build matrix
        import sys
        
        # For small n, we can just do Gaussian elimination on fractions.
        # Matrix size: |terms| x |basis|
        M = [[Fraction(0) for _ in range(len(all_basis))] for _ in range(len(terms))]
        for j, b in enumerate(all_basis):
            b_poly = gens[b]
            for t, c in b_poly.items():
                M[terms.index(t)][j] = c
                
        target = [poly.get(t, Fraction(0)) for t in terms]
        
        # Solve M * x = target
        # We can augment and row reduce.
        aug = [row[:] + [target[i]] for i, row in enumerate(M)]
        
        rows = len(aug)
        cols = len(aug[0]) - 1
        
        pivot_row = 0
        for c in range(cols):
            # find pivot
            for r in range(pivot_row, rows):
                if aug[r][c] != 0:
                    aug[pivot_row], aug[r] = aug[r], aug[pivot_row]
                    break
            else:
                continue
            
            pivot_val = aug[pivot_row][c]
            for j in range(c, cols + 1):
                aug[pivot_row][j] /= pivot_val
                
            for r in range(rows):
                if r != pivot_row and aug[r][c] != 0:
                    factor = aug[r][c]
                    for j in range(c, cols + 1):
                        aug[r][j] -= factor * aug[pivot_row][j]
            pivot_row += 1
            
        # Extract solution
        # The system must be consistent!
        coeffs = {}
        for c in range(cols):
            # Find the row where this column is 1
            val = Fraction(0)
            for r in range(rows):
                if aug[r][c] == 1:
                    is_pivot = True
                    for j in range(cols):
                        if j != c and aug[r][j] != 0:
                            is_pivot = False
                    if is_pivot:
                        val = aug[r][-1]
            if val != 0:
                coeffs[all_basis[c]] = val
                
        return coeffs
    
    for i in range(len(all_basis)):
        for j in range(i, len(all_basis)):
            X = all_basis[i]
            Y = all_basis[j]
            px = parity(X)
            py = parity(Y)
            
            comm = commutator(gens[X], gens[Y], px, py)
            if not comm:
                continue
                
            res = express_in_basis(comm)
            for Z, coeff in res.items():
                if coeff != 0:
                    sc.append({
                        "X": X,
                        "Y": Y,
                        "Z": Z,
                        "coeff": format_coeff(coeff),
                        "sign_rule": "graded"
                    })
                    
    # Build schema dict
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
                "description": "Standard fermionic pair satisfying CAR"
            },
            "bosons": {
                "count": 2*n,
                "n": n,
                "labels": [f"b_{i}_{s}" for i in range(1, n+1) for s in ("p", "m")],
                "description": f"Bosonic oscillators b_i^± with i=1,...,{n}"
            }
        },
        "central_elements": {
            "kappa": {
                "parity": 1,
                "description": "Odd central extension element"
            },
            "K": {
                "parity": 0,
                "description": "Even central extension element, typically 1"
            }
        },
        "oscillator_relations": {
            "fermionic_anticommutators": {
                "description": "Standard CAR for fermions",
                "relations": {
                    "same_type": "{a_i^±, a_i^±} = 0",
                    "conjugate_pair": "{a_i^-, a_i^+} = 1"
                }
            },
            "bosonic_commutators": {
                "description": "Canonical commutation relations for bosonic oscillators",
                "relations": {
                    "same_type": "[b_i^±, b_j^±] = 0 for all i, j",
                    "conjugate_pair": "[b_i^-, b_j^+] = \delta_{ij}"
                }
            },
            "mixed_commutators": {
                "boson_fermion": "[b_i^±, a_j^±] = 0"
            }
        },
        "basis": {
            "even": even,
            "odd": odd,
            "ordering_convention": "PBW: [odd] < [even]"
        },
        "parity": {k: parity(k) for k in all_basis},
        "generator_realization": {
            "description": "Standard form with PBW ordering",
            "ordering": "a_1_p, a_1_m, " + ", ".join([f"b_{i}_{s}" for i in range(1, n+1) for s in ("p", "m")]),
            "realizations": {}
        },
        "structure_constants": sc,
        "metadata": {
            "generated_by": "C_generators.py",
            "references": [
                "Frappat et al. (2000), Dictionary on Lie Algebras and Superalgebras"
            ]
        }
    }
    
    for k in all_basis:
        sf = []
        for term, coeff in gens[k].items():
            sf.append({
                "words": list(term),
                "coeff": format_coeff(coeff)
            })
        schema["generator_realization"]["realizations"][k] = {
            "standard_form": sf,
            "parity": parity(k)
        }
        
    return schema

if __name__ == "__main__":
    for n in [1, 2, 3]:
        sch = generate_schema(n)
        with open(f"data/C_{n}_structure.json", "w") as f:
            json.dump(sch, f, indent=2)
        print(f"Generated data/C_{n}_structure.json with {len(sch['structure_constants'])} brackets.")
