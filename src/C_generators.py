"""
C(n+1) = osp(2|2n) Generator and Structure Constants Builder

Generates Schema 1 (Algebra Structure) JSON for C(n+1) for bosonic ranks n=1, 2, 3.
"""

import os
import json
import datetime

def get_C_basis(n):
    """
    Returns the even and odd basis lists and parity map for C(n+1) = osp(2|2n).
    
    Bosonic rank n:
    - n=1: C(2) = osp(2|2), dim = 4 | 4 (total 8)
    - n=2: C(3) = osp(2|4), dim = 11 | 8 (total 19)
    - n=3: C(4) = osp(2|6), dim = 22 | 12 (total 34)
    """
    # Cartans: H_0 (so(2)) and H_1..H_n (sp(2n))
    cartans = ["H_0"] + [f"H_{k}" for k in range(1, n + 1)]
    
    # Positive roots of sp(2n)
    pos_2del = [f"E_2del{k}_p" for k in range(1, n + 1)]
    pos_pair = []
    for i in range(1, n + 1):
        for j in range(i + 1, n + 1):
            pos_pair.append(f"E_del{i}_del{j}_pp")
            
    # Negative roots of sp(2n)
    neg_2del = [f"E_2del{k}_m" for k in range(1, n + 1)]
    neg_pair = []
    for i in range(1, n + 1):
        for j in range(i + 1, n + 1):
            neg_pair.append(f"E_del{i}_del{j}_mm")
            
    # Mixed roots of sp(2n)
    mixed_pm = []
    mixed_mp = []
    for i in range(1, n + 1):
        for j in range(i + 1, n + 1):
            mixed_pm.append(f"E_del{i}_del{j}_pm")
            mixed_mp.append(f"E_del{i}_del{j}_mp")
            
    even_basis = cartans + pos_2del + pos_pair + neg_2del + neg_pair + mixed_pm + mixed_mp
    
    # Odd basis: 4 generators per k in 1..n
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

def get_generator_realizations(n):
    """
    Returns standard oscillator realization representation for all basis generators.
    """
    realizations = {}
    
    # H_0: a_1^+ a_1^- - 1/2
    realizations["H_0"] = {
        "standard_form": [
            {"words": ["a_1_p", "a_1_m"], "coeff": "1"},
            {"words": [], "coeff": "-1/2"}
        ],
        "frappat_form": r"a_1^+ a_1^- - 1/2",
        "parity": 0
    }
    
    # H_k: b_k^+ b_k^- + 1/2
    for k in range(1, n + 1):
        realizations[f"H_{k}"] = {
            "standard_form": [
                {"words": [f"b_{k}_p", f"b_{k}_m"], "coeff": "1"},
                {"words": [], "coeff": "1/2"}
            ],
            "frappat_form": rf"b_{k}^+ b_{k}^- + 1/2",
            "parity": 0
        }
        
        # 2del_p, 2del_m
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
        
        # Odd generators
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
    """
    Internal calculation returning {Z_name: int_coeff}.
    """
    basis_info = get_C_basis(n)
    parity = basis_info["parity"]
    pX = parity[X]
    pY = parity[Y]
    
    result = {}
    
    def add_term(Z, coeff):
        if Z not in result:
            result[Z] = 0
        result[Z] += coeff

    # Parity 0 brackets (Lie commutators)
    if pX == 0 and pY == 0:
        # H_0 is central to sp(2n), so [H_0, Even] = 0
        if X == "H_0" or Y == "H_0":
            pass
            
        # [H_k, ...]
        elif X.startswith("H_") and Y.startswith("H_"):
            pass
        elif X.startswith("H_"):
            k = int(X.split("_")[1])
            if Y == f"E_2del{k}_p":
                add_term(Y, 2)
            elif Y == f"E_2del{k}_m":
                add_term(Y, -2)
            elif Y.startswith("E_del"):
                parts = Y.split("_")
                i, j = int(parts[1].replace("del", "")), int(parts[2].replace("del", ""))
                s_i, s_j = parts[3][0], parts[3][1]
                if k == i:
                    add_term(Y, 1 if s_i == 'p' else -1)
                elif k == j:
                    add_term(Y, 1 if s_j == 'p' else -1)
        elif Y.startswith("H_"):
            # Anti-symmetry [Y, X] = -[X, Y]
            sub = compute_graded_bracket_numeric(Y, X, n)
            for z, c in sub.items():
                add_term(z, -c)
                
        # [E_2del_p / m, ...]
        elif X.startswith("E_2del") and Y.startswith("E_2del"):
            kx, sx = int(X[6]), X[8]
            ky, sy = int(Y[6]), Y[8]
            if kx == ky and sx != sy:
                # [E_2delk_p, E_2delk_m] = -4 H_k
                if sx == 'p' and sy == 'm':
                    add_term(f"H_{kx}", -4)
                else:
                    add_term(f"H_{kx}", 4)
                    
        # [E_2delk, E_del_del]
        elif X.startswith("E_2del") and Y.startswith("E_del"):
            kx, sx = int(X[6]), X[8]
            parts = Y.split("_")
            i, j = int(parts[1].replace("del", "")), int(parts[2].replace("del", ""))
            s_i, s_j = parts[3][0], parts[3][1]
            
            if kx == i:
                if sx == 'p' and s_i == 'm':
                    # [(b_i^+)^2, b_i^- b_j^s] = -2 b_i^+ b_j^s
                    target_sign = 'p' + s_j
                    target_name = f"E_del{i}_del{j}_{target_sign}"
                    add_term(target_name, -2)
                elif sx == 'm' and s_i == 'p':
                    # [(b_i^-)^2, b_i^+ b_j^s] = 2 b_i^- b_j^s
                    target_sign = 'm' + s_j
                    target_name = f"E_del{i}_del{j}_{target_sign}"
                    add_term(target_name, 2)
            elif kx == j:
                if sx == 'p' and s_j == 'm':
                    # [(b_j^+)^2, b_i^s b_j^-] = -2 b_i^s b_j^+
                    target_sign = s_i + 'p'
                    target_name = f"E_del{i}_del{j}_{target_sign}"
                    add_term(target_name, -2)
                elif sx == 'm' and s_j == 'p':
                    target_sign = s_i + 'm'
                    target_name = f"E_del{i}_del{j}_{target_sign}"
                    add_term(target_name, 2)

        elif Y.startswith("E_2del") and X.startswith("E_del"):
            sub = compute_graded_bracket_numeric(Y, X, n)
            for z, c in sub.items():
                add_term(z, -c)
                
        # [E_del_del, E_del_del]
        elif X.startswith("E_del") and Y.startswith("E_del"):
            pX_parts = X.split("_")
            ix, jx = int(pX_parts[1].replace("del", "")), int(pX_parts[2].replace("del", ""))
            six, sjx = pX_parts[3][0], pX_parts[3][1]
            
            pY_parts = Y.split("_")
            iy, jy = int(pY_parts[1].replace("del", "")), int(pY_parts[2].replace("del", ""))
            siy, sjy = pY_parts[3][0], pY_parts[3][1]
            
            if ix == iy and jx == jy:
                if six == 'p' and sjx == 'p' and siy == 'm' and sjy == 'm':
                    # [b_i^+ b_j^+, b_i^- b_j^-] = -H_i - H_j
                    add_term(f"H_{ix}", -1)
                    add_term(f"H_{jx}", -1)
                elif six == 'm' and sjx == 'm' and siy == 'p' and sjy == 'p':
                    add_term(f"H_{ix}", 1)
                    add_term(f"H_{jx}", 1)
                elif six == 'p' and sjx == 'm' and siy == 'm' and sjy == 'p':
                    # [b_i^+ b_j^-, b_i^- b_j^+] = H_i - H_j
                    add_term(f"H_{ix}", 1)
                    add_term(f"H_{jx}", -1)
                elif six == 'm' and sjx == 'p' and siy == 'p' and sjy == 'm':
                    add_term(f"H_{ix}", -1)
                    add_term(f"H_{jx}", 1)
            elif ix == iy: # jx != jy
                if six == 'p' and siy == 'm':
                    min_j, max_j = min(jx, jy), max(jx, jy)
                    s_min = sjx if min_j == jx else sjy
                    s_max = sjy if min_j == jx else sjx
                    target = f"E_del{min_j}_del{max_j}_{s_min}{s_max}"
                    add_term(target, -1)
                elif six == 'm' and siy == 'p':
                    min_j, max_j = min(jx, jy), max(jx, jy)
                    s_min = sjx if min_j == jx else sjy
                    s_max = sjy if min_j == jx else sjx
                    target = f"E_del{min_j}_del{max_j}_{s_min}{s_max}"
                    add_term(target, 1)

    # Parity 0 (X) and Parity 1 (Y)
    elif pX == 0 and pY == 1:
        y_parts = Y.split("_")
        ky = int(y_parts[2].replace("del", ""))
        s_eps, s_b = y_parts[3][0], y_parts[3][1]
        
        if X == "H_0":
            # [H_0, a_1^\pm b_k^\pm] = \pm a_1^\pm b_k^\pm
            add_term(Y, 1 if s_eps == 'p' else -1)
        elif X.startswith("H_"):
            kx = int(X.split("_")[1])
            if kx == ky:
                add_term(Y, 1 if s_b == 'p' else -1)
        elif X.startswith("E_2del"):
            kx, sx = int(X[6]), X[8]
            if kx == ky:
                if sx == 'p' and s_b == 'm':
                    # [(b_k^+)^2, a_1^\sigma b_k^-] = -2 a_1^\sigma b_k^+
                    target = f"E_eps1_del{ky}_{s_eps}p"
                    add_term(target, -2)
                elif sx == 'm' and s_b == 'p':
                    # [(b_k^-)^2, a_1^\sigma b_k^+] = 2 a_1^\sigma b_k^-
                    target = f"E_eps1_del{ky}_{s_eps}m"
                    add_term(target, 2)
        elif X.startswith("E_del"):
            x_parts = X.split("_")
            ix, jx = int(x_parts[1].replace("del", "")), int(x_parts[2].replace("del", ""))
            six, sjx = x_parts[3][0], x_parts[3][1]
            if ky == ix and s_b != six:
                sign = -1 if s_b == 'p' else 1
                target = f"E_eps1_del{jx}_{s_eps}{sjx}"
                add_term(target, sign)
            elif ky == jx and s_b != sjx:
                sign = -1 if s_b == 'p' else 1
                target = f"E_eps1_del{ix}_{s_eps}{six}"
                add_term(target, sign)

    elif pX == 1 and pY == 0:
        sub = compute_graded_bracket_numeric(Y, X, n)
        for z, c in sub.items():
            add_term(z, -c)

    # Parity 1 (X) and Parity 1 (Y): Graded commutator is anticommutator {X, Y}
    elif pX == 1 and pY == 1:
        x_parts = X.split("_")
        kx = int(x_parts[2].replace("del", ""))
        sx_eps, sx_b = x_parts[3][0], x_parts[3][1]
        
        y_parts = Y.split("_")
        ky = int(y_parts[2].replace("del", ""))
        sy_eps, sy_b = y_parts[3][0], y_parts[3][1]
        
        if sx_eps != sy_eps:
            if kx == ky:
                if sx_b == 'p' and sy_b == 'p':
                    add_term(f"E_2del{kx}_p", 1)
                elif sx_b == 'm' and sy_b == 'm':
                    add_term(f"E_2del{kx}_m", 1)
                elif sx_b == 'p' and sy_b == 'm':
                    # {a_1^+ b_k^+, a_1^- b_k^-} = -H_0 + H_k
                    add_term("H_0", -1 if sx_eps == 'p' else 1)
                    add_term(f"H_{kx}", 1)
                elif sx_b == 'm' and sy_b == 'p':
                    # {a_1^+ b_k^-, a_1^- b_k^+} = H_0 + H_k
                    add_term("H_0", 1 if sx_eps == 'p' else -1)
                    add_term(f"H_{kx}", 1)
            else:
                min_k, max_k = min(kx, ky), max(kx, ky)
                s_min = sx_b if min_k == kx else sy_b
                s_max = sy_b if min_k == kx else sx_b
                if s_min == 'p' and s_max == 'p':
                    add_term(f"E_del{min_k}_del{max_k}_pp", 1)
                elif s_min == 'm' and s_max == 'm':
                    add_term(f"E_del{min_k}_del{max_k}_mm", 1)
                elif s_min == 'p' and s_max == 'm':
                    add_term(f"E_del{min_k}_del{max_k}_pm", 1)
                elif s_min == 'm' and s_max == 'p':
                    add_term(f"E_del{min_k}_del{max_k}_mp", 1)

    return {z: c for z, c in result.items() if c != 0}

def compute_graded_bracket(X, Y, n):
    """
    Public function returning {Z_name: str_coeff}.
    """
    res_num = compute_graded_bracket_numeric(X, Y, n)
    return {z: str(c) for z, c in res_num.items()}

def get_C_structure(n):
    """
    Generates complete Schema 1 v5.0 dictionary for C(n+1) = osp(2|2n).
    """
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
