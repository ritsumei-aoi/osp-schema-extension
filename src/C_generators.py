import json
import os

def normal_order(coeff, word):
    """
    word is a tuple of integers.
    0: a_p, 1: a_m
    2: b_1_p, 3: b_1_m
    4: b_2_p, 5: b_2_m
    ...
    Returns a dict of {tuple: coeff}
    """
    if coeff == 0:
        return {}
    
    word = list(word)
    for i in range(len(word) - 1):
        # Fermion nilpotent check
        if word[i] == word[i+1] and word[i] in (0, 1):
            return {}
        
        # Out of order check
        if word[i] > word[i+1]:
            A, B = word[i], word[i+1]
            if A == 1 and B == 0:
                # a_m a_p = 1 - a_p a_m
                w1 = tuple(word[:i] + [0, 1] + word[i+2:])
                w2 = tuple(word[:i] + word[i+2:])
                d1 = normal_order(-coeff, w1)
                d2 = normal_order(coeff, w2)
                # merge
                res = {}
                for k, v in d1.items(): res[k] = res.get(k, 0) + v
                for k, v in d2.items(): res[k] = res.get(k, 0) + v
                return res
            elif A % 2 == 1 and B == A - 1 and A >= 3:
                # b_k_m b_k_p = b_k_p b_k_m + 1
                w1 = tuple(word[:i] + [B, A] + word[i+2:])
                w2 = tuple(word[:i] + word[i+2:])
                d1 = normal_order(coeff, w1)
                d2 = normal_order(coeff, w2)
                # merge
                res = {}
                for k, v in d1.items(): res[k] = res.get(k, 0) + v
                for k, v in d2.items(): res[k] = res.get(k, 0) + v
                return res
            else:
                # commute
                w1 = tuple(word[:i] + [B, A] + word[i+2:])
                return normal_order(coeff, w1)
                
    return {tuple(word): coeff}

def normal_order_poly(poly):
    res = {}
    for w, c in poly.items():
        d = normal_order(c, w)
        for kw, kc in d.items():
            res[kw] = res.get(kw, 0) + kc
    # filter 0
    return {k: v for k, v in res.items() if abs(v) > 1e-9}

def multiply(p1, p2):
    res = {}
    for w1, c1 in p1.items():
        for w2, c2 in p2.items():
            w = w1 + w2
            res[w] = res.get(w, 0) + c1 * c2
    return res

def add(p1, p2, sign=1):
    res = {}
    for w, c in p1.items(): res[w] = res.get(w, 0) + c
    for w, c in p2.items(): res[w] = res.get(w, 0) + sign * c
    return {k: v for k, v in res.items() if abs(v) > 1e-9}

def bracket(p1, p2, parity1, parity2):
    term1 = multiply(p1, p2)
    term2 = multiply(p2, p1)
    sign = -1 if (parity1 == 1 and parity2 == 1) else 1
    res = add(term1, term2, -sign)
    return normal_order_poly(res)

def get_basis(n):
    # build basis elements as polynomials
    basis = {}
    parity = {}
    
    # helper
    def P(w, c=1.0): return normal_order_poly({w: c})
    
    # cartans
    # H_1 = a_1^+ a_1^- + b_1^+ b_1^-
    basis['H_1'] = add(P((0,1)), P((2,3)))
    parity['H_1'] = 0
    
    for k in range(2, n+1):
        # H_k = b_{k-1}^+ b_{k-1}^- - b_k^+ b_k^-
        basis[f'H_{k}'] = add(P((2*(k-1), 2*(k-1)+1)), P((2*k, 2*k+1)), -1)
        parity[f'H_{k}'] = 0
    
    # H_{n+1} = -b_n^+ b_n^- - 1/2
    basis[f'H_{n+1}'] = add(P((2*n, 2*n+1), -1), P((), -0.5))
    parity[f'H_{n+1}'] = 0
    
    # Even roots
    for k in range(1, n+1):
        basis[f'E_2del{k}_p'] = P((2*k, 2*k), 0.5) if n == 1 else P((2*k, 2*k)) # Wait, formula says (b_k^+)^2 for all, but simple root says 1/2 (b_n^+)^2. Let's just use 1.0, structure constants will adapt.
        # Actually Cn1_definition.md says: E_pm2del_k = (b_k^pm)^2
        basis[f'E_2del{k}_p'] = P((2*k, 2*k))
        basis[f'E_2del{k}_m'] = P((2*k+1, 2*k+1))
        parity[f'E_2del{k}_p'] = 0
        parity[f'E_2del{k}_m'] = 0
        
    for i in range(1, n+1):
        for j in range(i+1, n+1):
            basis[f'E_del{i}_del{j}_pp'] = P((2*i, 2*j))
            basis[f'E_del{i}_del{j}_pm'] = P((2*i, 2*j+1))
            basis[f'E_del{i}_del{j}_mp'] = P((2*i+1, 2*j))
            basis[f'E_del{i}_del{j}_mm'] = P((2*i+1, 2*j+1))
            parity[f'E_del{i}_del{j}_pp'] = 0
            parity[f'E_del{i}_del{j}_pm'] = 0
            parity[f'E_del{i}_del{j}_mp'] = 0
            parity[f'E_del{i}_del{j}_mm'] = 0
            
    # Odd roots
    for k in range(1, n+1):
        basis[f'E_eps1_del{k}_pp'] = P((0, 2*k))
        basis[f'E_eps1_del{k}_pm'] = P((0, 2*k+1))
        basis[f'E_eps1_del{k}_mp'] = P((1, 2*k))
        basis[f'E_eps1_del{k}_mm'] = P((1, 2*k+1))
        parity[f'E_eps1_del{k}_pp'] = 1
        parity[f'E_eps1_del{k}_pm'] = 1
        parity[f'E_eps1_del{k}_mp'] = 1
        parity[f'E_eps1_del{k}_mm'] = 1
        
    return basis, parity

def format_coeff(c):
    if abs(c - round(c)) < 1e-9:
        return str(int(round(c)))
    return str(c)

def generate_schema(n):
    basis_poly, parity = get_basis(n)
    
    # Sort basis keys
    odd_keys = sorted([k for k, v in parity.items() if v == 1])
    even_keys_cartan = sorted([k for k in parity.keys() if parity[k] == 0 and k.startswith('H')])
    even_keys_root = sorted([k for k in parity.keys() if parity[k] == 0 and k.startswith('E')])
    basis_order = odd_keys + even_keys_cartan + even_keys_root
    
    structure_constants = []
    
    for i, X in enumerate(basis_order):
        for j, Y in enumerate(basis_order):
            if i > j: continue # only compute X, Y where i <= j
            
            pX = basis_poly[X]
            pY = basis_poly[Y]
            res = bracket(pX, pY, parity[X], parity[Y])
            if not res: continue
            
            # Decompose res into basis elements
            # Since basis elements are linearly independent and mostly monomials, this is easy.
            # But H_k are linear combinations of diagonal terms.
            # We can build a matrix of basis vectors and solve, or just do it greedily.
            
            # Diagonal terms in res:
            # They are composed of (0,1), (2,3), (4,5) etc, and ()
            # Non-diagonal are direct matches.
            
            decomposition = {}
            # first extract non-diagonals
            rem = dict(res)
            for B_name in basis_order:
                if B_name.startswith('E_'):
                    B_poly = basis_poly[B_name]
                    # B_poly has exactly one term
                    term = list(B_poly.keys())[0]
                    if term in rem:
                        c = rem[term] / B_poly[term]
                        decomposition[B_name] = c
                        rem = add(rem, B_poly, -c)
            
            # Solve for diagonals using numpy
            if len([k for k, v in rem.items() if abs(v) > 1e-9]) > 0:
                import numpy as np
                # variables: H_1, ..., H_{n+1}, K
                # We have n+1 cartans and 1 central element K (which is identity)
                # Let's collect the terms present in Cartans and Identity
                # They are: (0,1), (2,3), ..., (2n, 2n+1) and ()
                term_list = [(0,1)] + [(2*i, 2*i+1) for i in range(1, n+1)] + [()]
                num_terms = len(term_list)
                
                A = np.zeros((num_terms, n + 2))
                # column 0: H_1
                A[0, 0] = 1.0 # (0,1)
                A[1, 0] = 1.0 # (2,3)
                
                # column k-1: H_k for k=2..n
                for k in range(2, n+1):
                    # H_k = b_{k-1}^+ b_{k-1}^- - b_k^+ b_k^-
                    # index k-1 is b_k
                    A[k-1, k-1] = 1.0
                    A[k, k-1] = -1.0
                    
                # column n: H_n+1
                # H_n+1 = -b_n^+ b_n^- - 1/2
                A[n, n] = -1.0
                A[n+1, n] = -0.5
                
                # column n+1: K
                # K is identity ()
                A[n+1, n+1] = 1.0
                
                b = np.zeros(num_terms)
                for i, t in enumerate(term_list):
                    b[i] = rem.get(t, 0)
                    
                try:
                    c, residuals, rank, s = np.linalg.lstsq(A, b, rcond=None)
                    if np.max(np.abs(A @ c - b)) < 1e-8:
                        for k in range(1, n+2):
                            if abs(c[k-1]) > 1e-9:
                                decomposition[f'H_{k}'] = float(c[k-1])
                        if abs(c[n+1]) > 1e-9:
                            # Central element K, represented by identity
                            decomposition['K'] = float(c[n+1])
                        # Zero out rem
                        for t in term_list:
                            rem[t] = 0.0
                except Exception as e:
                    pass
            
            # clean rem and check if unhandled
            rem = {k: v for k, v in rem.items() if abs(v) > 1e-9}
            if len(rem) > 0:
                print(f"WARNING: unhandled remainder in [{X}, {Y}]: {rem}")            
            for Z, c in decomposition.items():
                if abs(c) > 1e-9:
                    structure_constants.append({
                        "X": X,
                        "Y": Y,
                        "Z": Z,
                        "coeff": format_coeff(c),
                        "sign_rule": "graded"
                    })
                    
    # Generate schema
    b_labels = []
    for i in range(1, n+1):
        b_labels.extend([f"b_{i}_p", f"b_{i}_m"])
        
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
        "central_elements": {
            "kappa": {
                "label": "kappa",
                "parity": 1,
                "description": "Odd central element"
            },
            "K": {
                "label": "K",
                "parity": 0,
                "description": "Even central element (typically identified with scalar 1)"
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
                "count": 2*n,
                "n": n,
                "labels": b_labels,
                "description": "Bosonic oscillators b_i^± with i=1,...,n"
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
            "even": even_keys_cartan + even_keys_root,
            "odd": odd_keys,
            "ordering_convention": "PBW: κ < [odd] < [even]  (K = 1 is excluded; see note below)"
        },
        "parity": parity,
        "structure_constants": structure_constants,
        "metadata": {
            "generated_by": "C_generators.py",
            "references": [
                "Frappat et al. (2000), Dictionary on Lie Algebras and Superalgebras"
            ]
        }
    }
    
    with open(f'data/C_{n}_structure.json', 'w') as f:
        json.dump(schema, f, indent=2)

if __name__ == '__main__':
    os.makedirs('data', exist_ok=True)
    generate_schema(1)
    generate_schema(2)
    generate_schema(3)
    print("Done")
