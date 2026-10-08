import json
import os

def generate_C_n(n):
    total_dim = 2 * n**2 + 5 * n + 1
    even_dim = 2 * n**2 + n + 1
    odd_dim = 4 * n

    # Cartans
    cartans = [f"H_{k}" for k in range(1, n+2)]
    
    # Even roots
    even_roots = []
    for k in range(1, n+1):
        even_roots.extend([f"E_2del{k}_p", f"E_2del{k}_m"])
    for i in range(1, n):
        for j in range(i+1, n+1):
            even_roots.extend([
                f"E_del{i}_del{j}_pp",
                f"E_del{i}_del{j}_pm",
                f"E_del{i}_del{j}_mp",
                f"E_del{i}_del{j}_mm"
            ])
            
    # Odd roots
    odd_roots = []
    for k in range(1, n+1):
        odd_roots.extend([
            f"E_eps1_del{k}_pp",
            f"E_eps1_del{k}_pm",
            f"E_eps1_del{k}_mp",
            f"E_eps1_del{k}_mm"
        ])
        
    even_basis = cartans + even_roots
    odd_basis = odd_roots
    
    # Parity
    parity = {}
    for g in even_basis:
        parity[g] = 0
    for g in odd_basis:
        parity[g] = 1

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
                "description": "Standard fermionic oscillators a_i^± with i=1,...,m"
            },
            "bosons": {
                "count": 2*n,
                "n": n,
                "labels": [f"b_{k}_{s}" for k in range(1, n+1) for s in ("p", "m")],
                "description": "Bosonic oscillators b_k^± with k=1,...,n"
            }
        },
        "oscillator_relations": {
            "fermionic_anticommutators": {
                "description": "Canonical anticommutation relations for fermionic oscillators",
                "relations": {
                    "same_type": "{a_i^±, a_j^±} = 0 for all i, j",
                    "conjugate_pair": "{a_i^-, a_j^+} = δ_{ij}"
                }
            },
            "bosonic_commutators": {
                "description": "Canonical commutation relations for bosonic oscillators",
                "relations": {
                    "same_type": "[b_k^±, b_l^±] = 0 for all k, l",
                    "conjugate_pair": "[b_k^-, b_l^+] = δ_{kl}"
                }
            },
            "mixed_commutators": {
                "boson_fermion": "[b_k^±, a_i^±] = 0"
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
                "description": "Even central element (identified with scalar 1)"
            }
        },
        "basis": {
            "even": even_basis,
            "odd": odd_basis,
            "ordering_convention": "PBW: [odd] < [even]"
        },
        "parity": parity,
        "generator_realization": {},
        "structure_constants": [],
        "metadata": {
            "generated_by": "C_generators.py",
            "generation_date": "2026-10-08"
        }
    }
    return schema

if __name__ == "__main__":
    os.makedirs("data", exist_ok=True)
    for n in [1, 2, 3]:
        schema = generate_C_n(n)
        with open(f"data/C_{n}_structure.json", "w") as f:
            json.dump(schema, f, indent=2)
        print(f"Generated data/C_{n}_structure.json")
