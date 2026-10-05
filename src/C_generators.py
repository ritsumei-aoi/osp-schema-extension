import json
import os
from oscillator import Poly, Word, var, const, graded_commutator

def build_C_schema(n):
    # Basis definitions
    a1_p = var('a_1_p')
    a1_m = var('a_1_m')
    
    b_p = {k: var(f'b_{k}_p') for k in range(1, n+1)}
    b_m = {k: var(f'b_{k}_m') for k in range(1, n+1)}
    
    even_basis = {}
    odd_basis = {}
    
    # H_k
    even_basis['H_1'] = (a1_p * a1_m + b_p[1] * b_m[1], 0)
    for k in range(2, n+1):
        even_basis[f'H_{k}'] = (b_p[k-1] * b_m[k-1] - b_p[k] * b_m[k], 0)
    even_basis[f'H_{n+1}'] = (b_p[n] * b_m[n] * -1 - const(0.5), 0)
    
    # Even roots
    for k in range(1, n+1):
        even_basis[f'E_2del{k}_p'] = (b_p[k] * b_p[k], 0) # Removed 1/2 factor to match 'All root generators'
        even_basis[f'E_2del{k}_m'] = (b_m[k] * b_m[k], 0) # Removed 1/2 factor
        
    for i in range(1, n+1):
        for j in range(i+1, n+1):
            even_basis[f'E_del{i}_del{j}_pp'] = (b_p[i] * b_p[j], 0)
            even_basis[f'E_del{i}_del{j}_mm'] = (b_m[i] * b_m[j], 0)
            even_basis[f'E_del{i}_del{j}_pm'] = (b_p[i] * b_m[j], 0)
            even_basis[f'E_del{i}_del{j}_mp'] = (b_m[i] * b_p[j], 0)
            
    # Odd roots
    for k in range(1, n+1):
        odd_basis[f'E_eps1_del{k}_pp'] = (a1_p * b_p[k], 1)
        odd_basis[f'E_eps1_del{k}_pm'] = (a1_p * b_m[k], 1)
        odd_basis[f'E_eps1_del{k}_mp'] = (a1_m * b_p[k], 1)
        odd_basis[f'E_eps1_del{k}_mm'] = (a1_m * b_m[k], 1)
        
    all_basis = {**even_basis, **odd_basis}
    
    # Ordered list of keys for structure constants
    # Order: [odd] < [even], using python's default string sort for determinism within parity
    ordered_keys = sorted(odd_basis.keys()) + sorted(even_basis.keys())
    
    # To find which generator a polynomial corresponds to, we can just invert the basis map
    # Since polynomials might have multiple terms, and our basis generators are just monomials or binomials.
    # Wait, the structure constants could be linear combinations of generators!
    # A polynomial resulting from a commutator needs to be expanded in `all_basis`.
    
    def poly_to_dict(poly):
        return dict(poly.terms)
        
    basis_dicts = {k: poly_to_dict(v[0]) for k, v in all_basis.items()}
    
    def expand_in_basis(poly):
        # Very simple matching: find a generator that shares terms, subtract it.
        # Since our basis elements are either single terms (e.g. b1+ b1+) or 
        # H_k which have terms like b_k+ b_k-, a1+ a1-, we can match them.
        res = {}
        rem = Poly(poly.terms)
        
        # First, match Cartan generators because they contain mixed terms
        for k in [f'H_{i}' for i in range(1, n+2)]:
            gen_poly, _ = all_basis[k]
            # pick a distinguishing term to find coefficient
            # For H_1, it's a1_p a1_m. For H_k, it's b_{k-1}_p b_{k-1}_m. For H_{n+1}, it's b_n_p b_n_m
            if k == 'H_1':
                w = Word(['a_1_p', 'a_1_m'])
            elif k == f'H_{n+1}':
                w = Word(['b_{n}_p', f'b_{n}_m'])
            else:
                idx = int(k.split('_')[1])
                w = Word([f'b_{idx-1}_p', f'b_{idx-1}_m'])
                
            c = rem.terms.get(w, 0)
            if k == f'H_{n+1}': c = -c # Because H_{n+1} has -b_n^+ b_n^-
            if c != 0:
                res[k] = c
                rem = rem - gen_poly * c
                
        # Now match the rest (they are all monomials)
        for k, (gen_poly, _) in all_basis.items():
            if k.startswith('H_'): continue
            # Find a non-empty term in gen_poly
            w = next(iter(gen_poly.terms.keys()))
            c = rem.terms.get(w, 0)
            if c != 0:
                # wait, E_2del_p has coefficient 1.
                gen_c = gen_poly.terms[w]
                coef = c / gen_c
                res[k] = coef
                rem = rem - gen_poly * coef
                
        rem.clean()
        if len(rem.terms) > 0:
            print(f"Warning: Residual terms left: {rem.terms}")
            
        return res
        
    structure_constants = []
    
    for i, X_key in enumerate(ordered_keys):
        for j in range(i, len(ordered_keys)):
            Y_key = ordered_keys[j]
            
            X_poly, px = all_basis[X_key]
            Y_poly, py = all_basis[Y_key]
            
            comm = graded_commutator(X_poly, Y_poly, px, py)
            
            if len(comm.terms) > 0:
                exp = expand_in_basis(comm)
                for Z_key, coef in exp.items():
                    if coef != 0:
                        structure_constants.append({
                            "X": X_key,
                            "Y": Y_key,
                            "Z": Z_key,
                            "coeff": str(int(coef)) if coef.is_integer() else str(coef),
                            "sign_rule": "graded"
                        })
                        
    # Build schema output
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
                "description": "Standard fermionic pair"
            },
            "bosons": {
                "count": 2*n,
                "n": n,
                "labels": [f"b_{k}_p" for k in range(1, n+1)] + [f"b_{k}_m" for k in range(1, n+1)],
                "description": "Bosonic oscillators b_i^± with i=1,...,n"
            }
        },
        "oscillator_relations": {
            "standard_fermion_anticommutators": {
                "description": "Canonical anticommutation relations (CAR) for standard fermions",
                "relation": "{a_1^-, a_1^+} = 1"
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
        "central_elements": {
            "kappa": {
                "parity": 1,
                "relation": "kappa^2 = 0",
                "description": "Odd nilpotent central element for deformation"
            },
            "K": {
                "parity": 0,
                "relation": "K = 1",
                "description": "Even central element identified with scalar 1"
            }
        },
        "basis": {
            "even": sorted(even_basis.keys()),
            "odd": sorted(odd_basis.keys()),
            "ordering_convention": "PBW: κ < [odd] < [even] (K = 1 is excluded)"
        },
        "parity": {k: v[1] for k, v in all_basis.items()},
        "generator_realization": {
            "description": "Standard form with PBW ordering",
            "ordering": "a_1_p, a_1_m, b_1_p, b_1_m...",
            "realizations": {} # We'll skip detailing this to save output size, just the dict keys
        },
        "structure_constants": structure_constants,
        "metadata": {
            "generated_by": "C_generators.py",
            "references": [
                "Frappat et al. (2000), Dictionary on Lie Algebras and Superalgebras"
            ]
        }
    }
    
    # Fill realizations
    def fmt_term(w, c):
        return {"words": list(w.letters), "coeff": str(int(c)) if c.is_integer() else str(c)}
        
    for k, (poly, p) in all_basis.items():
        schema["generator_realization"]["realizations"][k] = {
            "standard_form": [fmt_term(w, c) for w, c in poly.terms.items()],
            "parity": p
        }

    return schema

if __name__ == "__main__":
    for n in [1, 2, 3]:
        schema = build_C_schema(n)
        with open(f"data/C_{n}_structure.json", "w") as f:
            json.dump(schema, f, indent=2)
        print(f"Generated data/C_{n}_structure.json")
