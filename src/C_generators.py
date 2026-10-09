import json
from collections import defaultdict
import os

def normal_order_word(word):
    """
    Sorts a word into normal order: a1_p, a1_m, b1_p, b1_m, ...
    Returns a list of (coefficient, new_word)
    """
    order = {"a1_p": 0, "a1_m": 1}
    for k in range(1, 10):
        order[f"b{k}_p"] = 2*k
        order[f"b{k}_m"] = 2*k + 1
    
    # We will do bubble sort
    w = list(word)
    n = len(w)
    
    # Base case of recursion:
    # We look for the first out-of-order pair
    for i in range(n - 1):
        left, right = w[i], w[i+1]
        if order[left] > order[right]:
            # swap needed
            # check the relation between left and right
            is_f_left = left.startswith("a")
            is_f_right = right.startswith("a")
            
            res = []
            if is_f_left and is_f_right:
                # Both fermions
                if left == right:
                    # a1_p a1_p = 0, a1_m a1_m = 0
                    return []
                elif left == "a1_m" and right == "a1_p":
                    # a1_m a1_p = 1 - a1_p a1_m
                    # Term 1: 1 * (rest of word without these two)
                    w1 = w[:i] + w[i+2:]
                    res.extend(normal_order_word(w1))
                    # Term 2: -1 * (swapped)
                    w2 = w[:i] + ["a1_p", "a1_m"] + w[i+2:]
                    for c, rw in normal_order_word(w2):
                        res.append((-c, rw))
                    return res
            elif not is_f_left and not is_f_right:
                # Both bosons
                if left.startswith("b") and right.startswith("b"):
                    left_idx = left[1]
                    right_idx = right[1]
                    if left_idx == right_idx and left.endswith("_m") and right.endswith("_p"):
                        # bk_m bk_p = bk_p bk_m + 1
                        w1 = w[:i] + w[i+2:]
                        res.extend(normal_order_word(w1))
                        w2 = w[:i] + [right, left] + w[i+2:]
                        res.extend(normal_order_word(w2))
                        return res
                    else:
                        # commute
                        w2 = w[:i] + [right, left] + w[i+2:]
                        return normal_order_word(w2)
            else:
                # Boson and fermion commute
                w2 = w[:i] + [right, left] + w[i+2:]
                return normal_order_word(w2)
                
    # if it reaches here, it's ordered. Check for duplicates of fermions
    if w.count("a1_p") > 1 or w.count("a1_m") > 1:
        return []
    return [(1.0, tuple(w))]

def multiply_exprs(e1, e2):
    res = defaultdict(float)
    for w1, c1 in e1.items():
        for w2, c2 in e2.items():
            w = w1 + w2
            c = c1 * c2
            for nc, nw in normal_order_word(w):
                res[nw] += c * nc
    
    # Clean up zeros
    return {w: c for w, c in res.items() if abs(c) > 1e-9}

def add_exprs(e1, e2, coeff2=1.0):
    res = defaultdict(float)
    for w, c in e1.items():
        res[w] += c
    for w, c in e2.items():
        res[w] += c * coeff2
    return {w: c for w, c in res.items() if abs(c) > 1e-9}

def scalar_expr(val):
    if abs(val) < 1e-9:
        return {}
    return {(): val}

def graded_bracket(e1, e2, p1, p2):
    # [A, B} = A B - (-1)^{pA pB} B A
    sign = -1 if (p1 == 1 and p2 == 1) else 1
    term1 = multiply_exprs(e1, e2)
    term2 = multiply_exprs(e2, e1)
    return add_exprs(term1, term2, -sign)

def build_generators(n):
    gens = {}
    parities = {}
    
    # H_1 = a1_p a1_m + b1_p b1_m
    gens["H_1"] = {("a1_p", "a1_m"): 1.0, (f"b1_p", f"b1_m"): 1.0}
    parities["H_1"] = 0
    
    for k in range(2, n + 1):
        gens[f"H_{k}"] = {(f"b{k-1}_p", f"b{k-1}_m"): 1.0, (f"b{k}_p", f"b{k}_m"): -1.0}
        parities[f"H_{k}"] = 0
        
    gens[f"H_{n+1}"] = {(f"b{n}_p", f"b{n}_m"): -1.0, (): -0.5}
    parities[f"H_{n+1}"] = 0
    
    for k in range(1, n + 1):
        gens[f"E_2del{k}_p"] = {(f"b{k}_p", f"b{k}_p"): 1.0}
        gens[f"E_2del{k}_m"] = {(f"b{k}_m", f"b{k}_m"): 1.0}
        parities[f"E_2del{k}_p"] = 0
        parities[f"E_2del{k}_m"] = 0
        
        for l in range(k + 1, n + 1):
            gens[f"E_del{k}_del{l}_pp"] = {(f"b{k}_p", f"b{l}_p"): 1.0}
            gens[f"E_del{k}_del{l}_mm"] = {(f"b{k}_m", f"b{l}_m"): 1.0}
            gens[f"E_del{k}_del{l}_pm"] = {(f"b{k}_p", f"b{l}_m"): 1.0}
            gens[f"E_del{k}_del{l}_mp"] = {(f"b{l}_p", f"b{k}_m"): 1.0} # Normal order
            parities[f"E_del{k}_del{l}_pp"] = 0
            parities[f"E_del{k}_del{l}_mm"] = 0
            parities[f"E_del{k}_del{l}_pm"] = 0
            parities[f"E_del{k}_del{l}_mp"] = 0
            
    for k in range(1, n + 1):
        gens[f"E_eps_del{k}_pp"] = {("a1_p", f"b{k}_p"): 1.0}
        gens[f"E_eps_del{k}_pm"] = {("a1_p", f"b{k}_m"): 1.0}
        gens[f"E_eps_del{k}_mp"] = {("a1_m", f"b{k}_p"): 1.0}
        gens[f"E_eps_del{k}_mm"] = {("a1_m", f"b{k}_m"): 1.0}
        parities[f"E_eps_del{k}_pp"] = 1
        parities[f"E_eps_del{k}_pm"] = 1
        parities[f"E_eps_del{k}_mp"] = 1
        parities[f"E_eps_del{k}_mm"] = 1
        
    # We must normal-order all generators just in case
    no_gens = {}
    for name, expr in gens.items():
        no_expr = defaultdict(float)
        for w, c in expr.items():
            for nc, nw in normal_order_word(w):
                no_expr[nw] += c * nc
        no_gens[name] = {w: c for w, c in no_expr.items() if abs(c) > 1e-9}
        
    return no_gens, parities

def format_word(w):
    if len(w) == 0:
        return "1"
    return " ".join(w)

def generate_schema(n):
    gens, parities = build_generators(n)
    even = sorted([k for k, v in parities.items() if v == 0])
    odd = sorted([k for k, v in parities.items() if v == 1])
    
    # Re-order even to put Cartans first
    cartans = [f"H_{k}" for k in range(1, n + 2)]
    even_roots = [k for k in even if not k.startswith("H_")]
    even = cartans + even_roots
    
    labels_b = []
    for k in range(1, n + 1):
        labels_b.extend([f"b{k}_p", f"b{k}_m"])
        
    schema = {
        "schema_version": "5.0",
        "algebra": {
            "family": "C",
            "m": 1,
            "n": n,
            "cartan_type": f"C({n+1})",
            "dimension_formula": "osp(2m|2n)",
            "dimension": {
                "total": 2*n*n + 5*n + 1,
                "even": 2*n*n + n + 1,
                "odd": 4*n
            }
        },
        "oscillator_generators": {
            "fermions": {
                "count": 2,
                "m": 1,
                "labels": ["a1_p", "a1_m"],
                "description": "Standard fermionic pair a_1^±"
            },
            "bosons": {
                "count": 2*n,
                "n": n,
                "labels": labels_b,
                "description": "Bosonic oscillators b_i^± with i=1,...,n"
            }
        },
        "oscillator_relations": {
            "standard_fermion_anticommutators": {
                "description": "Canonical anticommutation relations for fermions",
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
                "description": "Odd central element for inhomogeneous deformation, kappa^2 = 0"
            },
            "K": {
                "parity": 0,
                "description": "Even central identity element (K = 1)"
            }
        },
        "basis": {
            "even": even,
            "odd": odd,
            "ordering_convention": "PBW: kappa < [odd] < [even]  (K = 1 is excluded; see note below)"
        },
        "parity": parities,
        "generator_realization": {
            "description": "Standard form with PBW ordering",
            "ordering": "a1_p, a1_m, " + ", ".join(labels_b),
            "realizations": {}
        },
        "structure_constants": [],
        "metadata": {
            "generated_by": "C_generators.py",
            "generation_date": "2026-10-09"
        }
    }
    
    for name, expr in gens.items():
        std_form = []
        for w, c in expr.items():
            std_form.append({"words": list(w), "coeff": str(c) if c.is_integer() else str(c)})
        schema["generator_realization"]["realizations"][name] = {
            "standard_form": std_form,
            "parity": parities[name]
        }
        
    # Calculate structure constants
    all_gens = odd + even
    sc = []
    
    def expr_to_string(e):
        s = []
        for w, c in sorted(e.items()):
            s.append(f"{c}*{format_word(w)}")
        return " + ".join(s)

    for i in range(len(all_gens)):
        for j in range(i, len(all_gens)):
            g1 = all_gens[i]
            g2 = all_gens[j]
            e1 = gens[g1]
            e2 = gens[g2]
            p1 = parities[g1]
            p2 = parities[g2]
            
            bracket = graded_bracket(e1, e2, p1, p2)
            if not bracket:
                continue
                
            # Now we need to express `bracket` as a linear combination of generators
            # Since our generators form a basis, we can do this.
            # We'll just try to match it directly using a simple greedy approach or system of equations.
            # The structure constants will only involve generators.
            rem = bracket.copy()
            decomp = defaultdict(float)
            
            # Simple matching: the generators are mostly unique in their terms.
            # But let's build a matrix and solve it, or just match largest term.
            # Actually, since bracket is in the Lie algebra, we can match by looking at terms.
            # For H_k, it's a bit mixed, but we can match.
            
            while rem:
                # Find a term in rem
                w_target, c_target = next(iter(rem.items()))
                # Find a generator that has this term
                matched = False
                for g_name in all_gens:
                    if w_target in gens[g_name]:
                        c_gen = gens[g_name][w_target]
                        factor = c_target / c_gen
                        decomp[g_name] += factor
                        rem = add_exprs(rem, gens[g_name], -factor)
                        matched = True
                        break
                if not matched:
                    # Could be central K (identity)
                    if len(w_target) == 0:
                        decomp["K"] += c_target
                        rem = add_exprs(rem, {(): c_target}, -1.0)
                    else:
                        raise ValueError(f"Could not decompose {bracket} into generators. Remainder: {rem}")
            
            for z, c in decomp.items():
                if abs(c) > 1e-9:
                    val_str = str(int(c)) if c.is_integer() else str(c)
                    sc.append({
                        "X": g1,
                        "Y": g2,
                        "Z": z,
                        "coeff": val_str,
                        "sign_rule": "graded"
                    })
    
    schema["structure_constants"] = sc
    return schema

if __name__ == "__main__":
    os.makedirs("data", exist_ok=True)
    for n in [1, 2, 3]:
        schema = generate_schema(n)
        with open(f"data/C_{n}_structure.json", "w") as f:
            json.dump(schema, f, indent=2)
        print(f"Generated data/C_{n}_structure.json")
