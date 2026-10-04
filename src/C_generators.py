"""
C(n+1) = osp(2|2n) Generator and Structure Constants Builder

Generates Schema 1 (Algebra Structure) JSON for C(n+1) for bosonic ranks n=1, 2, 3 using
exact symbolic oscillator algebra reduction.
"""

import os
import sys
import json
import datetime
from fractions import Fraction

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from src.oscillator_engine import poly_multiply_graded

def get_C_basis(n):
    """
    Returns the even and odd basis lists and parity map for C(n+1) = osp(2|2n).
    """
    cartans = ["H_0"] + [f"H_{k}" for k in range(1, n + 1)]
    
    pos_2del = [f"E_2del{k}_p" for k in range(1, n + 1)]
    pos_pair = []
    for i in range(1, n + 1):
        for j in range(i + 1, n + 1):
            pos_pair.append(f"E_del{i}_del{j}_pp")
            
    neg_2del = [f"E_2del{k}_m" for k in range(1, n + 1)]
    neg_pair = []
    for i in range(1, n + 1):
        for j in range(i + 1, n + 1):
            neg_pair.append(f"E_del{i}_del{j}_mm")
            
    mixed_pm = []
    mixed_mp = []
    for i in range(1, n + 1):
        for j in range(i + 1, n + 1):
            mixed_pm.append(f"E_del{i}_del{j}_pm")
            mixed_mp.append(f"E_del{i}_del{j}_mp")
            
    even_basis = cartans + pos_2del + pos_pair + neg_2del + neg_pair + mixed_pm + mixed_mp
    
    odd_basis = []
    for k in range(1, n + 1):
        odd_basis.append(f"E_eps1_del{k}_pp")
        odd_basis.append(f"E_eps1_del{k}_pm")
        odd_basis.append(f"E_eps1_del{k}_mp")
        odd_basis.append(f"E_eps1_del{k}_mm")
        
    parity = {}
    for g in even_basis:
        parity[g] = 0
    for g in odd_basis:
        parity[g] = 1
        
    return {
        "even": even_basis,
        "odd": odd_basis,
        "parity": parity,
        "ordering_convention": "PBW: κ < [odd] < [even]"
    }

def word_dict_to_generator_dict(reduced_words, n):
    """
    Converts a dict of {reduced_word_tuple: Fraction_coeff} into {basis_generator_name: Fraction_coeff}.
    """
    res = {}
    for w, c in reduced_words.items():
        if len(w) == 0:
            # Constant scalar term in Lie superalgebra bracket (should be 0)
            pass
        elif len(w) == 2:
            o1, o2 = w[0], w[1]
            if o1 == "a_1_p" and o2 == "a_1_m":
                # a_1^+ a_1^- = H_0 + 1/2
                res["H_0"] = res.get("H_0", Fraction(0)) + c
            elif o1.startswith("b_") and o2.startswith("b_"):
                k1, s1 = int(o1.split("_")[1]), o1.split("_")[2]
                k2, s2 = int(o2.split("_")[1]), o2.split("_")[2]
                if k1 == k2:
                    if s1 == 'p' and s2 == 'm':
                        # b_k^+ b_k^- = H_k - 1/2
                        gen_name = f"H_{k1}"
                        res[gen_name] = res.get(gen_name, Fraction(0)) + c
                    elif s1 == 'p' and s2 == 'p':
                        gen_name = f"E_2del{k1}_p"
                        res[gen_name] = res.get(gen_name, Fraction(0)) + c
                    elif s1 == 'm' and s2 == 'm':
                        gen_name = f"E_2del{k1}_m"
                        res[gen_name] = res.get(gen_name, Fraction(0)) + c
                else: # k1 < k2
                    gen_name = f"E_del{k1}_del{k2}_{s1}{s2}"
                    res[gen_name] = res.get(gen_name, Fraction(0)) + c
            elif o1.startswith("a_") and o2.startswith("b_"):
                s1 = o1.split("_")[2]
                k2, s2 = int(o2.split("_")[1]), o2.split("_")[2]
                gen_name = f"E_eps1_del{k2}_{s1}{s2}"
                res[gen_name] = res.get(gen_name, Fraction(0)) + c
    return {g: c for g, c in res.items() if c != 0}

def get_generator_realizations(n):
    realizations = {}
    
    realizations["H_0"] = {
        "standard_form": [
            {"words": ["a_1_p", "a_1_m"], "coeff": "1"},
            {"words": [], "coeff": "-1/2"}
        ],
        "frappat_form": r"a_1^+ a_1^- - 1/2",
        "parity": 0
    }
    
    for k in range(1, n + 1):
        realizations[f"H_{k}"] = {
            "standard_form": [
                {"words": [f"b_{k}_p", f"b_{k}_m"], "coeff": "1"},
                {"words": [], "coeff": "1/2"}
            ],
            "frappat_form": rf"b_{k}^+ b_{k}^- + 1/2",
            "parity": 0
        }
        
        realizations[f"E_2del{k}_p"] = {
            "standard_form": [{"words": [f"b_{k}_p", f"b_{k}_p"], "coeff": "1"}],
            "frappat_form": rf"(b_{k}^+)^2",
            "parity": 0
        }
        realizations[f"E_2del{k}_m"] = {
            "standard_form": [{"words": [f"b_{k}_m", f"b_{k}_m"], "coeff": "1"}],
            "frappat_form": rf"(b_{k}^-)^2",
            "parity": 0
        }
        
        realizations[f"E_eps1_del{k}_pp"] = {
            "standard_form": [{"words": ["a_1_p", f"b_{k}_p"], "coeff": "1"}],
            "frappat_form": rf"a_1^+ b_{k}^+",
            "parity": 1
        }
        realizations[f"E_eps1_del{k}_pm"] = {
            "standard_form": [{"words": ["a_1_p", f"b_{k}_m"], "coeff": "1"}],
            "frappat_form": rf"a_1^+ b_{k}^-",
            "parity": 1
        }
        realizations[f"E_eps1_del{k}_mp"] = {
            "standard_form": [{"words": ["a_1_m", f"b_{k}_p"], "coeff": "1"}],
            "frappat_form": rf"a_1^- b_{k}^+",
            "parity": 1
        }
        realizations[f"E_eps1_del{k}_mm"] = {
            "standard_form": [{"words": ["a_1_m", f"b_{k}_m"], "coeff": "1"}],
            "frappat_form": rf"a_1^- b_{k}^-",
            "parity": 1
        }

    for i in range(1, n + 1):
        for j in range(i + 1, n + 1):
            realizations[f"E_del{i}_del{j}_pp"] = {
                "standard_form": [{"words": [f"b_{i}_p", f"b_{j}_p"], "coeff": "1"}],
                "frappat_form": rf"b_{i}^+ b_{j}^+",
                "parity": 0
            }
            realizations[f"E_del{i}_del{j}_mm"] = {
                "standard_form": [{"words": [f"b_{i}_m", f"b_{j}_m"], "coeff": "1"}],
                "frappat_form": rf"b_{i}^- b_{j}^-",
                "parity": 0
            }
            realizations[f"E_del{i}_del{j}_pm"] = {
                "standard_form": [{"words": [f"b_{i}_p", f"b_{j}_m"], "coeff": "1"}],
                "frappat_form": rf"b_{i}^+ b_{j}^-",
                "parity": 0
            }
            realizations[f"E_del{i}_del{j}_mp"] = {
                "standard_form": [{"words": [f"b_{i}_m", f"b_{j}_p"], "coeff": "1"}],
                "frappat_form": rf"b_{i}^- b_{j}^+",
                "parity": 0
            }
            
    return realizations

def compute_graded_bracket_numeric(X, Y, n):
    realizations = get_generator_realizations(n)
    poly1 = realizations[X]["standard_form"]
    poly2 = realizations[Y]["standard_form"]
    
    reduced_words = poly_multiply_graded(poly1, poly2)
    return word_dict_to_generator_dict(reduced_words, n)

def compute_graded_bracket(X, Y, n):
    res_num = compute_graded_bracket_numeric(X, Y, n)
    return {z: str(c) for z, c in res_num.items()}

def get_C_structure(n):
    basis_info = get_C_basis(n)
    even_basis = basis_info["even"]
    odd_basis = basis_info["odd"]
    all_basis = even_basis + odd_basis
    parity = basis_info["parity"]
    
    sc_list = []
    for i in range(len(all_basis)):
        for j in range(len(all_basis)):
            X = all_basis[i]
            Y = all_basis[j]
            brackets = compute_graded_bracket(X, Y, n)
            for Z, coeff in brackets.items():
                sc_list.append({
                    "X": X,
                    "Y": Y,
                    "Z": Z,
                    "coeff": coeff,
                    "sign_rule": "graded"
                })
                
    boson_labels = []
    for k in range(1, n + 1):
        boson_labels.extend([f"b_{k}_p", f"b_{k}_m"])
        
    schema_1 = {
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
                "total": 2 * n**2 + 5 * n + 1,
                "even": 2 * n**2 + n + 1,
                "odd": 4 * n
            }
        },
        "oscillator_generators": {
            "fermions": {
                "m": 1,
                "labels": ["a_1_p", "a_1_m"],
                "parity": 1,
                "description": r"Standard CAR fermionic pair a_1^\pm"
            },
            "bosons": {
                "count": 2 * n,
                "n": n,
                "labels": boson_labels,
                "description": r"Bosonic CCR oscillators b_i^\pm with i=1,...," + str(n)
            }
        },
        "oscillator_relations": {
            "standard_fermion_anticommutators": {
                "description": "{a_1_m, a_1_p} = 1, {a_1_p, a_1_p} = 0, {a_1_m, a_1_m} = 0",
                "relation": "{a_1^-, a_1^+} = 1"
            },
            "bosonic_commutators": {
                "description": "Canonical commutation relations for bosonic oscillators",
                "relations": {
                    "same_type": "[b_i^±, b_j^±] = 0 for all i, j",
                    "conjugate_pair": r"[b_i^-, b_j^+] = \delta_{ij}"
                }
            },
            "mixed_commutators": {
                "boson_fermion": r"[b_i^\pm, a_1^\pm] = 0"
            }
        },
        "central_elements": {
            "kappa": {
                "parity": 1,
                "nilpotent": True,
                "relation": "kappa^2 = 0",
                "description": "Odd central element parametrizing deformation"
            },
            "K": {
                "parity": 0,
                "relation": "K = 1",
                "description": "Even central element (identity scalar)"
            }
        },
        "basis": basis_info,
        "parity": parity,
        "generator_realization": {
            "description": "Standard oscillator representation",
            "realizations": get_generator_realizations(n)
        },
        "structure_constants": sc_list,
        "metadata": {
            "generated_by": "src/C_generators.py",
            "generation_date": datetime.date.today().isoformat(),
            "references": [
                "Frappat et al. (2000), Dictionary on Lie Algebras and Superalgebras",
                "Google Antigravity C(n+1) extension study"
            ]
        }
    }
    return schema_1

def generate_all_C_structures(data_dir="data"):
    os.makedirs(data_dir, exist_ok=True)
    for n in [1, 2, 3]:
        data = get_C_structure(n)
        filename = os.path.join(data_dir, f"C_{n}_structure.json")
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
        print(f"Generated {filename} (dim={data['algebra']['dimension']['total']}, structure constants count={len(data['structure_constants'])})")

if __name__ == "__main__":
    generate_all_C_structures()
