import json
import itertools
from collections import defaultdict
import os

def parity(osc):
    if osc.startswith('a'): return 1
    return 0

def omega(X, Y):
    if X.startswith('b') and Y.startswith('b'):
        if X[-2:] == '_m' and Y[-2:] == '_p' and X[:-2] == Y[:-2]: return 1
        if X[-2:] == '_p' and Y[-2:] == '_m' and X[:-2] == Y[:-2]: return -1
    elif X.startswith('a') and Y.startswith('a'):
        if X[-2:] == '_m' and Y[-2:] == '_p' and X[:-2] == Y[:-2]: return 1
        if X[-2:] == '_p' and Y[-2:] == '_m' and X[:-2] == Y[:-2]: return 1
    return 0

def eta(X, Y):
    # returns dict of { gb_label: coeff }
    res = {}
    if X.startswith('a') and Y.startswith('b'):
        sigma = 'p' if X[-2:] == '_p' else 'm'
        j = Y.split('_')[1]
        s = 'p' if Y[-2:] == '_p' else 'm'
        res[f"gb_{sigma}_{j}_{s}"] = 1
    elif X.startswith('b') and Y.startswith('a'):
        sigma = 'p' if Y[-2:] == '_p' else 'm'
        j = X.split('_')[1]
        s = 'p' if X[-2:] == '_p' else 'm'
        res[f"gb_{sigma}_{j}_{s}"] = -1
    return res

def get_order(osc):
    if osc == '1': return -1
    parts = osc.split('_')
    type_ = parts[0]
    idx = int(parts[1])
    sign = 0 if parts[2] == 'p' else 1
    return (0 if type_ == 'a' else 1, idx, sign)

def sort_term_gamma(term):
    # term is a tuple of oscillators.
    # returns dict of (kappa_label) -> list of (coeff, new_term)
    # kappa_label = "" means no kappa.
    # kappa_label = "gb_..." means it has one kappa and that gb parameter.
    
    if len(term) <= 1:
        return {"": [(1, term)]}
        
    for i in range(len(term) - 1):
        if term[i] == term[i+1] and parity(term[i]) == 1:
            return {}
            
    # We maintain a state: (coeff, term_tuple)
    terms = {"": [(1, list(term))]}
    
    changed = True
    while changed:
        changed = False
        new_terms = defaultdict(list)
        
        for kl, t_list in terms.items():
            for coeff, t in t_list:
                dup = False
                for i in range(len(t) - 1):
                    if t[i] == t[i+1] and parity(t[i]) == 1:
                        dup = True
                        break
                if dup: continue
                
                swapped_this_term = False
                for i in range(len(t) - 1):
                    if get_order(t[i]) > get_order(t[i+1]):
                        X, Y = t[i+1], t[i]
                        sign = -1 if parity(X) * parity(Y) == 1 else 1
                        
                        t1 = list(t)
                        t1[i], t1[i+1] = X, Y
                        new_terms[kl].append((coeff * sign, t1))
                        
                        om = omega(X, Y)
                        if om != 0:
                            t2 = list(t[:i] + t[i+2:])
                            new_terms[kl].append((coeff * (-sign) * om, t2))
                            
                        et = eta(X, Y)
                        if et and kl == "": # only one kappa allowed (kappa^2 = 0)
                            # sign for moving kappa to front:
                            # kappa is odd, moving it past t[:i]
                            k_sign = 1
                            for j in range(i):
                                if parity(t[j]) == 1:
                                    k_sign *= -1
                                    
                            t2 = list(t[:i] + t[i+2:])
                            for gb, val in et.items():
                                new_terms[gb].append((coeff * (-sign) * val * k_sign, t2))
                                
                        swapped_this_term = True
                        changed = True
                        break
                        
                if not swapped_this_term:
                    new_terms[kl].append((coeff, t))
                    
        # Combine
        combined_terms = defaultdict(list)
        for kl, t_list in new_terms.items():
            combined = defaultdict(int)
            for c, t in t_list:
                combined[tuple(t)] += c
            for t, c in combined.items():
                if c != 0:
                    combined_terms[kl].append((c, list(t)))
        terms = combined_terms

    res = defaultdict(list)
    for kl, t_list in terms.items():
        for c, t in t_list:
            res[kl].append((c, tuple(t)))
    return res

def multiply_polys_gamma(poly1, poly2):
    # poly: dict of term -> coeff (no kappa)
    res = defaultdict(lambda: defaultdict(int)) # gb -> term -> coeff
    for t1, c1 in poly1.items():
        for t2, c2 in poly2.items():
            combined_t = t1 + t2
            sorted_res = sort_term_gamma(combined_t)
            for kl, t_list in sorted_res.items():
                for c3, t3 in t_list:
                    res[kl][t3] += c1 * c2 * c3
                    
    return {kl: {t: c for t, c in d.items() if c != 0} for kl, d in res.items() if any(c != 0 for c in d.values())}

def add_gamma_res(res1, res2, factor=1):
    out = defaultdict(lambda: defaultdict(int))
    for kl, d in res1.items():
        for t, c in d.items():
            out[kl][t] += c
    for kl, d in res2.items():
        for t, c in d.items():
            out[kl][t] += c * factor
            
    return {kl: {t: c for t, c in d.items() if c != 0} for kl, d in out.items() if any(c != 0 for c in d.values())}

def build_generators(n):
    gens = {}
    parities = {}
    
    gens['H_1'] = {('a_1_p', 'a_1_m'): 1, ('b_1_p', 'b_1_m'): 1}
    parities['H_1'] = 0
    for k in range(2, n + 1):
        gens[f'H_{k}'] = {(f'b_{k-1}_p', f'b_{k-1}_m'): 1, (f'b_{k}_p', f'b_{k}_m'): -1}
        parities[f'H_{k}'] = 0
    gens[f'H_{n+1}'] = {(f'b_{n}_p', f'b_{n}_m'): -1, (): -0.5}
    parities[f'H_{n+1}'] = 0
    
    for k in range(1, n + 1):
        gens[f'E_2del{k}_p'] = {(f'b_{k}_p', f'b_{k}_p'): 0.5}
        parities[f'E_2del{k}_p'] = 0
        gens[f'E_2del{k}_m'] = {(f'b_{k}_m', f'b_{k}_m'): 0.5}
        parities[f'E_2del{k}_m'] = 0
        
    for i in range(1, n + 1):
        for j in range(i + 1, n + 1):
            gens[f'E_del{i}_del{j}_pp'] = {(f'b_{i}_p', f'b_{j}_p'): 1}
            gens[f'E_del{i}_del{j}_pm'] = {(f'b_{i}_p', f'b_{j}_m'): 1}
            gens[f'E_del{i}_del{j}_mp'] = {(f'b_{i}_m', f'b_{j}_p'): 1}
            gens[f'E_del{i}_del{j}_mm'] = {(f'b_{i}_m', f'b_{j}_m'): 1}
            for suf in ['pp', 'pm', 'mp', 'mm']: parities[f'E_del{i}_del{j}_{suf}'] = 0
                
    for k in range(1, n + 1):
        gens[f'E_eps1_del{k}_pp'] = {('a_1_p', f'b_{k}_p'): 1}
        gens[f'E_eps1_del{k}_pm'] = {('a_1_p', f'b_{k}_m'): 1}
        gens[f'E_eps1_del{k}_mp'] = {('a_1_m', f'b_{k}_p'): 1}
        gens[f'E_eps1_del{k}_mm'] = {('a_1_m', f'b_{k}_m'): 1}
        for suf in ['pp', 'pm', 'mp', 'mm']: parities[f'E_eps1_del{k}_{suf}'] = 1
            
    for k, v in gens.items():
        nv = defaultdict(int)
        for tt, cc in v.items():
            sorted_res = sort_term_gamma(tt)
            # Only care about un-deformed part for generators themselves
            if "" in sorted_res:
                for c, t in sorted_res[""]:
                    nv[t] += c * cc
        gens[k] = {t: c for t, c in nv.items() if c != 0}
        
    return gens, parities

def identify_generator(poly, all_gens):
    for name, gpoly in all_gens.items():
        if not poly and not gpoly: return name, 1
        if not poly or not gpoly: continue
        t1 = next(iter(poly))
        if t1 not in gpoly: continue
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
        if match: return name, ratio
    return None, None

def generate_gamma_for_n(n):
    gens, parities = build_generators(n)
    
    basis_odd = [f'E_eps1_del{k}_{suf}' for k in range(1, n + 1) for suf in ['pp', 'pm', 'mp', 'mm']]
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
            basis_even.extend([f'E_del{i}_del{j}_mm', f'E_del{i}_del{j}_pm', f'E_del{i}_del{j}_mp'])

    all_names = basis_odd + basis_even
    
    gamma_constants = []
    
    for i, X in enumerate(all_names):
        for j in range(i, len(all_names)):
            Y = all_names[j]
            termA = multiply_polys_gamma(gens[X], gens[Y])
            termB = multiply_polys_gamma(gens[Y], gens[X])
            sign = -1 if parities[X] * parities[Y] == 1 else 1
            
            comm_gamma = add_gamma_res(termA, termB, -sign)
            
            for gb, quad_comm in comm_gamma.items():
                if gb == "": continue # skip un-deformed
                quad_comm = {t: c for t, c in quad_comm.items() if len(t) > 0}
                if not quad_comm: continue
                
                Z_name, coeff = identify_generator(quad_comm, gens)
                if Z_name:
                    if isinstance(coeff, float) and coeff.is_integer(): coeff = int(coeff)
                    gamma_constants.append({
                        "X": X, "Y": Y, "Z": Z_name, "gb": gb, "coeff": str(coeff)
                    })
                else:
                    # Decompose into Cartans
                    cartan_names = [f'H_{k}' for k in range(1, n + 2)]
                    rem = dict(quad_comm)
                    decomp = []
                    for H in cartan_names:
                        H_poly = {t: c for t, c in gens[H].items() if len(t) > 0}
                        t1 = next(iter(H_poly))
                        if t1 in rem:
                            ratio = rem[t1] / H_poly[t1]
                            decomp.append((H, ratio))
                            for t, c in H_poly.items():
                                rem[t] = rem.get(t, 0) - c * ratio
                                if abs(rem[t]) < 1e-9: del rem[t]
                                
                    if not rem:
                        for Z_name, coeff in decomp:
                            if isinstance(coeff, float) and coeff.is_integer(): coeff = int(coeff)
                            gamma_constants.append({
                                "X": X, "Y": Y, "Z": Z_name, "gb": gb, "coeff": str(coeff)
                            })
                    else:
                        print(f"Warning: could not identify gamma [{X}, {Y}]_gamma = {quad_comm}")
                        
    # Schema 2 JSON
    schema2 = {
        "schema_version": "5.0",
        "algebra": {
            "family": "C",
            "m": 1,
            "n": n,
            "cartan_type": f"C({n+1})"
        },
        "inhomogeneous_deformation": {
            "description": "Deformation parameterized by gb matrix defining exchange between a_1^\u00b1 and b_k^\u00b1.",
            "gb_matrix_shape": [2, 2*n],
            "gb_labels": [f"gb_{sig}_{j}_{s}" for sig in ['p', 'm'] for j in range(1, n+1) for s in ['p', 'm']]
        },
        "gamma_structure": gamma_constants,
        "metadata": {
            "generated_by": "C_gamma.py",
            "generation_date": "2026-10-10"
        }
    }
    
    with open(f"data/C_{n}_gamma.json", "w") as f:
        json.dump(schema2, f, indent=2)

if __name__ == "__main__":
    for n in [1, 2, 3]:
        generate_gamma_for_n(n)
        print(f"Generated Gamma for n={n}")
