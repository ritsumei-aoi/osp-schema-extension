import json
import itertools
from collections import defaultdict
import os

def parity(osc):
    if osc.startswith('a'): return 1
    return 0

def omega(X, Y):
    # X Y - (-1)^{p(X)p(Y)} Y X = omega(X, Y)
    # [b_j^-, b_k^+] = delta_{jk} => b_j^- b_k^+ - b_k^+ b_j^- = delta_{jk} => omega(b_j^-, b_k^+) = delta_{jk}
    # {a_1^-, a_1^+} = 1 => a_1^- a_1^+ + a_1^+ a_1^- = 1 => omega(a_1^-, a_1^+) = 1
    if X.startswith('b') and Y.startswith('b'):
        if X[-2:] == '_m' and Y[-2:] == '_p' and X[:-2] == Y[:-2]: return 1
        if X[-2:] == '_p' and Y[-2:] == '_m' and X[:-2] == Y[:-2]: return -1
    elif X.startswith('a') and Y.startswith('a'):
        if X[-2:] == '_m' and Y[-2:] == '_p' and X[:-2] == Y[:-2]: return 1
        if X[-2:] == '_p' and Y[-2:] == '_m' and X[:-2] == Y[:-2]: return 1
    return 0

def get_order(osc):
    if osc == '1': return -1
    parts = osc.split('_')
    type_ = parts[0]
    idx = int(parts[1])
    sign = 0 if parts[2] == 'p' else 1
    return (0 if type_ == 'a' else 1, idx, sign)

def sort_term(term):
    # term is a tuple of oscillators, e.g. ('b_1_p', 'a_1_m')
    # returns a list of (coeff, new_term)
    if len(term) <= 1:
        return [(1, term)]
    
    # check for immediate duplicates before sorting
    for i in range(len(term) - 1):
        if term[i] == term[i+1] and parity(term[i]) == 1:
            return []
    
    terms = [(1, list(term))]
    changed = True
    while changed:
        changed = False
        new_terms = []
        for coeff, t in terms:
            # Check for duplicate fermions
            dup = False
            for i in range(len(t) - 1):
                if t[i] == t[i+1] and parity(t[i]) == 1:
                    dup = True
                    break
            if dup: continue

            swapped_this_term = False
            for i in range(len(t) - 1):
                if get_order(t[i]) > get_order(t[i+1]):
                    # Need to swap t[i] and t[i+1]
                    X, Y = t[i+1], t[i] # we want to replace Y X with X Y and scalar
                    # Y X = (-1)^{p(X)p(Y)} X Y - (-1)^{p(X)p(Y)} omega(X, Y)
                    sign = -1 if parity(X) * parity(Y) == 1 else 1
                    
                    t1 = list(t)
                    t1[i], t1[i+1] = X, Y
                    new_terms.append((coeff * sign, t1))
                    
                    om = omega(X, Y)
                    if om != 0:
                        t2 = list(t[:i] + t[i+2:])
                        new_terms.append((coeff * (-sign) * om, t2))
                    
                    swapped_this_term = True
                    changed = True
                    break
            
            if not swapped_this_term:
                new_terms.append((coeff, t))
        
        # Combine similar terms to avoid explosion
        combined = defaultdict(int)
        for c, t in new_terms:
            combined[tuple(t)] += c
        terms = [(c, list(t)) for t, c in combined.items() if c != 0]

    return [(c, tuple(t)) for c, t in terms if c != 0]

def multiply_polys(poly1, poly2):
    # poly is dict: tuple -> coeff
    res = defaultdict(int)
    for t1, c1 in poly1.items():
        for t2, c2 in poly2.items():
            combined_t = t1 + t2
            for c3, t3 in sort_term(combined_t):
                res[t3] += c1 * c2 * c3
    return {t: c for t, c in res.items() if c != 0}

def add_polys(poly1, poly2, factor=1):
    res = defaultdict(int, poly1)
    for t, c in poly2.items():
        res[t] += c * factor
    return {t: c for t, c in res.items() if c != 0}

def graded_commutator(poly1, poly2, p1, p2):
    # [X, Y} = X Y - (-1)^{p(X)p(Y)} Y X
    termA = multiply_polys(poly1, poly2)
    termB = multiply_polys(poly2, poly1)
    sign = -1 if p1 * p2 == 1 else 1
    return add_polys(termA, termB, -sign)

def build_generators(n):
    gens = {}
    parities = {}
    
    # H_1 = a_1^+ a_1^- + b_1^+ b_1^-
    gens['H_1'] = {('a_1_p', 'a_1_m'): 1, ('b_1_p', 'b_1_m'): 1}
    parities['H_1'] = 0
    
    for k in range(2, n + 1):
        gens[f'H_{k}'] = {(f'b_{k-1}_p', f'b_{k-1}_m'): 1, (f'b_{k}_p', f'b_{k}_m'): -1}
        parities[f'H_{k}'] = 0
        
    gens[f'H_{n+1}'] = {(f'b_{n}_p', f'b_{n}_m'): -1, (): -0.5}
    parities[f'H_{n+1}'] = 0
    
    # E_2del_k
    for k in range(1, n + 1):
        gens[f'E_2del{k}_p'] = {(f'b_{k}_p', f'b_{k}_p'): 0.5}
        parities[f'E_2del{k}_p'] = 0
        gens[f'E_2del{k}_m'] = {(f'b_{k}_m', f'b_{k}_m'): 0.5}
        parities[f'E_2del{k}_m'] = 0
        
    # E_del_i_del_j
    for i in range(1, n + 1):
        for j in range(i + 1, n + 1):
            gens[f'E_del{i}_del{j}_pp'] = {(f'b_{i}_p', f'b_{j}_p'): 1}
            gens[f'E_del{i}_del{j}_pm'] = {(f'b_{i}_p', f'b_{j}_m'): 1}
            gens[f'E_del{i}_del{j}_mp'] = {(f'b_{i}_m', f'b_{j}_p'): 1}
            gens[f'E_del{i}_del{j}_mm'] = {(f'b_{i}_m', f'b_{j}_m'): 1}
            for suf in ['pp', 'pm', 'mp', 'mm']:
                parities[f'E_del{i}_del{j}_{suf}'] = 0
                
    # Odd generators E_eps1_del_k
    for k in range(1, n + 1):
        gens[f'E_eps1_del{k}_pp'] = {('a_1_p', f'b_{k}_p'): 1}
        gens[f'E_eps1_del{k}_pm'] = {('a_1_p', f'b_{k}_m'): 1}
        gens[f'E_eps1_del{k}_mp'] = {('a_1_m', f'b_{k}_p'): 1}
        gens[f'E_eps1_del{k}_mm'] = {('a_1_m', f'b_{k}_m'): 1}
        for suf in ['pp', 'pm', 'mp', 'mm']:
            parities[f'E_eps1_del{k}_{suf}'] = 1
            
    # Re-normalize generator dicts
    for k, v in gens.items():
        nv = defaultdict(int)
        for c, t in sort_term(list(v.keys())[0]):
            nv[t] += c * list(v.values())[0] if len(v) == 1 else 0
        if len(v) > 1:
            for tt, cc in v.items():
                for c, t in sort_term(tt):
                    nv[t] += c * cc
        gens[k] = {t: c for t, c in nv.items() if c != 0}
        
    return gens, parities

def format_realization(poly):
    res = []
    for t, c in poly.items():
        if isinstance(c, float) and c.is_integer():
            c = int(c)
        res.append({"words": list(t), "coeff": str(c)})
    return res

def identify_generator(poly, all_gens):
    for name, gpoly in all_gens.items():
        # Check if poly is a multiple of gpoly
        if not poly and not gpoly:
            return name, 1
        if not poly or not gpoly:
            continue
        
        # Check proportional
        t1 = next(iter(poly))
        if t1 not in gpoly:
            continue
        ratio = poly[t1] / gpoly[t1]
        
        match = True
        for t, c in poly.items():
            if t not in gpoly or abs(gpoly[t] * ratio - c) > 1e-9:
                match = False
                break
        for t, c in gpoly.items():
            if t not in poly:
                match = False
                break
                
        if match:
            return name, ratio
    return None, None

def generate_for_n(n):
    gens, parities = build_generators(n)
    
    basis_odd = []
    for k in range(1, n + 1):
        for suf in ['pp', 'pm', 'mp', 'mm']:
            basis_odd.append(f'E_eps1_del{k}_{suf}')
            
    basis_even = [f'H_{k}' for k in range(1, n + 2)]
    for k in range(1, n + 1):
        basis_even.append(f'E_2del{k}_p')
    for i in range(1, n + 1):
        for j in range(i + 1, n + 1):
            basis_even.append(f'E_del{i}_del{j}_pp')
    for k in range(1, n + 1):
        basis_even.append(f'E_2del{k}_m')
    for i in range(1, n + 1):
        for j in range(i + 1, n + 1):
            basis_even.append(f'E_del{i}_del{j}_mm')
            basis_even.append(f'E_del{i}_del{j}_pm')
            basis_even.append(f'E_del{i}_del{j}_mp')

    structure_constants = []
    all_names = basis_odd + basis_even
    
    for i, X in enumerate(all_names):
        for j in range(i, len(all_names)):
            Y = all_names[j]
            comm = graded_commutator(gens[X], gens[Y], parities[X], parities[Y])
            # Only quadratic parts for structure constants
            quad_comm = {t: c for t, c in comm.items() if len(t) > 0}
            if not quad_comm:
                continue
                
            Z_name, coeff = identify_generator(quad_comm, gens)
            if Z_name:
                if isinstance(coeff, float) and coeff.is_integer():
                    coeff = int(coeff)
                structure_constants.append({
                    "X": X,
                    "Y": Y,
                    "Z": Z_name,
                    "coeff": str(coeff),
                    "sign_rule": "graded"
                })
            else:
                # Need to decompose into Cartans if possible
                cartan_names = [f'H_{k}' for k in range(1, n + 2)]
                rem = dict(quad_comm)
                decomp = []
                for H in cartan_names:
                    H_poly = {t: c for t, c in gens[H].items() if len(t) > 0}
                    t1 = next(iter(H_poly))
                    if t1 in rem:
                        ratio = rem[t1] / H_poly[t1]
                        decomp.append((H, ratio))
                        rem = add_polys(rem, H_poly, -ratio)
                
                rem = {t: c for t, c in rem.items() if abs(c) > 1e-9}
                if not rem:
                    for Z_name, coeff in decomp:
                        if isinstance(coeff, float) and coeff.is_integer():
                            coeff = int(coeff)
                        structure_constants.append({
                            "X": X,
                            "Y": Y,
                            "Z": Z_name,
                            "coeff": str(coeff),
                            "sign_rule": "graded"
                        })
                else:
                    print(f"Warning: could not identify commutator [{X}, {Y}] = {quad_comm}")
                    print(f"Remainder: {rem}")

    # Build schema JSON
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
                "description": "Fermionic oscillators a_1^±"
            },
            "bosons": {
                "count": 2*n,
                "n": n,
                "labels": [f"b_{i}_{s}" for i in range(1, n+1) for s in ['p', 'm']],
                "description": "Bosonic oscillators b_i^± with i=1,...,n"
            }
        },
        "oscillator_relations": {
            "standard_fermion_anticommutators": {
                "description": "Canonical anticommutation relations for fermionic oscillators",
                "relations": {
                    "same_type": "{a_i^±, a_j^±} = 0",
                    "conjugate_pair": "{a_i^-, a_j^+} = δ_{ij}"
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
                "boson_fermion": "[b_i^±, a_j^±] = 0"
            }
        },
        "central_elements": {
            "kappa": {
                "parity": 1,
                "relation": "kappa^2 = 0",
                "description": "Odd nilpotent central element for inhomogeneous deformation"
            },
            "K": {
                "parity": 0,
                "relation": "K = 1",
                "description": "Even central element, identified with scalar 1"
            }
        },
        "basis": {
            "even": basis_even,
            "odd": basis_odd,
            "ordering_convention": "PBW: κ < [odd] < [even]  (K = 1 is excluded; see note below)"
        },
        "parity": parities,
        "generator_realization": {
            "description": "Standard form with PBW ordering",
            "ordering": "a_1_p, a_1_m, b_1_p, b_1_m, ...",
            "realizations": {k: {"standard_form": format_realization(v), "parity": parities[k]} for k, v in gens.items()}
        },
        "structure_constants": structure_constants,
        "metadata": {
            "generated_by": "C_generators.py",
            "generation_date": "2026-10-10",
            "references": [
                "Frappat et al. (2000), Dictionary on Lie Algebras and Superalgebras"
            ]
        }
    }
    
    with open(f"data/C_{n}_structure.json", "w") as f:
        json.dump(schema, f, indent=2)

if __name__ == "__main__":
    for n in [1, 2, 3]:
        generate_for_n(n)
        print(f"Generated for n={n}")
