import json
import os
from collections import defaultdict
from C_generators import build_generators, format_word

def normal_order_word_gamma(word):
    """
    word is a tuple of strings.
    Returns a list of (coeff, gb_term, new_word)
    gb_term is a string representing the gb parameter, or None if 0.
    """
    order = {"a1_p": 0, "a1_m": 1}
    for k in range(1, 10):
        order[f"b{k}_p"] = 2*k
        order[f"b{k}_m"] = 2*k + 1
        
    w = list(word)
    n = len(w)
    
    for i in range(n - 1):
        left, right = w[i], w[i+1]
        if order.get(left, 99) > order.get(right, 99):
            is_f_left = left.startswith("a")
            is_f_right = right.startswith("a")
            
            res = []
            if is_f_left and is_f_right:
                if left == right:
                    return []
                elif left == "a1_m" and right == "a1_p":
                    # a1_m a1_p = 1 - a1_p a1_m
                    w1 = w[:i] + w[i+2:]
                    res.extend(normal_order_word_gamma(w1))
                    w2 = w[:i] + ["a1_p", "a1_m"] + w[i+2:]
                    for c, gb, rw in normal_order_word_gamma(w2):
                        res.append((-c, gb, rw))
                    return res
            elif not is_f_left and not is_f_right:
                if left.startswith("b") and right.startswith("b"):
                    left_idx = left[1]
                    right_idx = right[1]
                    if left_idx == right_idx and left.endswith("_m") and right.endswith("_p"):
                        # bk_m bk_p = bk_p bk_m + 1
                        w1 = w[:i] + w[i+2:]
                        res.extend(normal_order_word_gamma(w1))
                        w2 = w[:i] + [right, left] + w[i+2:]
                        res.extend(normal_order_word_gamma(w2))
                        return res
                    else:
                        w2 = w[:i] + [right, left] + w[i+2:]
                        return normal_order_word_gamma(w2)
            else:
                # Boson and fermion
                # b * a = a * b - gb * kappa
                # Since we want to find the gamma term, this applies when left is b and right is a.
                w_base = w[:i] + [right, left] + w[i+2:]
                res.extend(normal_order_word_gamma(w_base))
                
                # gb term: left is b, right is a.
                # The parameter is gb_{a, b}
                # relation: [b, a] = - gb * kappa => b a = a b - gb kappa
                gb_name = f"gb_{right}_{left}"
                w_kappa = w[:i] + w[i+2:]
                for c, gb, rw in normal_order_word_gamma(w_kappa):
                    if gb is None:
                        res.append((-c, gb_name, rw))
                    else:
                        pass # kappa^2 = 0
                return res
                
    if w.count("a1_p") > 1 or w.count("a1_m") > 1:
        return []
    return [(1.0, None, tuple(w))]

def multiply_exprs_gamma(e1, e2):
    # e1, e2 are dicts: word -> coeff
    res_base = defaultdict(float)
    res_gamma = defaultdict(lambda: defaultdict(float))
    
    for w1, c1 in e1.items():
        for w2, c2 in e2.items():
            w = w1 + w2
            c = c1 * c2
            for nc, gb, nw in normal_order_word_gamma(w):
                if gb is None:
                    res_base[nw] += c * nc
                else:
                    res_gamma[gb][nw] += c * nc
                    
    # cleanup base
    base = {w: c for w, c in res_base.items() if abs(c) > 1e-9}
    gamma = {}
    for gb, expr in res_gamma.items():
        clean = {w: c for w, c in expr.items() if abs(c) > 1e-9}
        if clean:
            gamma[gb] = clean
    return base, gamma

def add_gamma_exprs(g1, g2, coeff2=1.0):
    res = defaultdict(lambda: defaultdict(float))
    for gb, expr in g1.items():
        for w, c in expr.items():
            res[gb][w] += c
    for gb, expr in g2.items():
        for w, c in expr.items():
            res[gb][w] += c * coeff2
            
    out = {}
    for gb, expr in res.items():
        clean = {w: c for w, c in expr.items() if abs(c) > 1e-9}
        if clean:
            out[gb] = clean
    return out

def graded_bracket_gamma(e1, e2, p1, p2):
    sign = -1 if (p1 == 1 and p2 == 1) else 1
    _, g1 = multiply_exprs_gamma(e1, e2)
    _, g2 = multiply_exprs_gamma(e2, e1)
    return add_gamma_exprs(g1, g2, -sign)

def generate_schema2(n):
    gens, parities = build_generators(n)
    
    with open(f"data/C_{n}_structure.json") as f:
        schema1 = json.load(f)
    
    all_gens = schema1["basis"]["even"] + schema1["basis"]["odd"]
    
    gb_matrix = []
    for sig in ["a1_p", "a1_m"]:
        for k in range(1, n+1):
            for s in ["p", "m"]:
                gb_matrix.append(f"gb_{sig}_b{k}_{s}")
                
    gamma_structure = []
    
    # Build matrix of generators
    gen_names = list(all_gens) + ["K"]
    gen_exprs = []
    for g in all_gens:
        gen_exprs.append(gens[g])
    gen_exprs.append({(): 1.0})
    
    all_words = set()
    for e in gen_exprs:
        all_words.update(e.keys())
    all_words = list(all_words)
    
    # M[word_idx][gen_idx]
    M = [[0.0 for _ in range(len(gen_names))] for _ in range(len(all_words))]
    for j, e in enumerate(gen_exprs):
        for w, c in e.items():
            i = all_words.index(w)
            M[i][j] = c
            
    # Gaussian elimination to find pseudo-inverse or just solve
    # Actually, the generators might not span the whole space (they span g).
    # But we know `target` is in the span of `g`.
    # We can just solve M * x = target for each target.
    
    def decompose(expr, label):
        # build target vector
        B = [0.0] * len(all_words)
        for w, c in expr.items():
            if w not in all_words:
                raise ValueError(f"Word {w} not in basis space")
            B[all_words.index(w)] = c
            
        # We need to solve M * x = B.
        # Since M is fixed, we can just do Gaussian elimination on [M | B].
        aug = [row[:] + [B[i]] for i, row in enumerate(M)]
        n_rows = len(aug)
        n_cols = len(gen_names)
        
        # pivot
        r = 0
        for c_idx in range(n_cols):
            # find pivot
            pivot_r = r
            while pivot_r < n_rows and abs(aug[pivot_r][c_idx]) < 1e-9:
                pivot_r += 1
            if pivot_r == n_rows:
                continue # Free variable, but our basis is linearly independent
            
            # swap
            aug[r], aug[pivot_r] = aug[pivot_r], aug[r]
            
            # normalize
            pivot_val = aug[r][c_idx]
            for j in range(c_idx, n_cols + 1):
                aug[r][j] /= pivot_val
                
            # eliminate below and above
            for i in range(n_rows):
                if i != r:
                    factor = aug[i][c_idx]
                    for j in range(c_idx, n_cols + 1):
                        aug[i][j] -= factor * aug[r][j]
            r += 1
            
        # extract solution
        sol = {}
        for c_idx in range(n_cols):
            # find row where this col is 1
            val = 0.0
            for i in range(n_rows):
                if abs(aug[i][c_idx] - 1.0) < 1e-9:
                    is_pivot = True
                    for j in range(n_cols):
                        if j != c_idx and abs(aug[i][j]) > 1e-9:
                            is_pivot = False
                    if is_pivot:
                        val = aug[i][-1]
                        break
            if abs(val) > 1e-9:
                sol[gen_names[c_idx]] = val
                
        # check if it fully solved
        check = defaultdict(float)
        for g, val in sol.items():
            e = gen_exprs[gen_names.index(g)]
            for w, c in e.items():
                check[w] += c * val
        
        for w, c in expr.items():
            if abs(check[w] - c) > 1e-7:
                raise ValueError(f"Failed to decompose {label}: {expr}. Got {sol}")
                
        return sol

    for i in range(len(all_gens)):
        for j in range(i, len(all_gens)):
            g1 = all_gens[i]
            g2 = all_gens[j]
            e1 = gens[g1]
            e2 = gens[g2]
            p1 = parities[g1]
            p2 = parities[g2]
            
            gb_exprs = graded_bracket_gamma(e1, e2, p1, p2)
            if gb_exprs:
                print(f"Bracket {g1} {g2} has gamma terms")
            
            for gb_name, expr in gb_exprs.items():
                decomp = decompose(expr, f"[{g1}, {g2}]_gamma")
                for z, c in decomp.items():
                    if abs(c) > 1e-9:
                        val_str = str(int(c)) if c.is_integer() else str(c)
                        gamma_structure.append({
                            "X": g1,
                            "Y": g2,
                            "Z": z,
                            "gb_param": gb_name,
                            "coeff": val_str
                        })
                        
    schema2 = {
        "schema_version": "5.0",
        "algebra_ref": f"C({n+1})",
        "inhomogeneous_deformation": {
            "gb_matrix": {
                "description": "Deformation parameters gb_{sigma, j, s}",
                "parameters": gb_matrix
            },
            "gamma_structure": gamma_structure
        },
        "metadata": {
            "generated_by": "gamma_generators.py"
        }
    }
    
    return schema2

if __name__ == "__main__":
    for n in [1, 2, 3]:
        s2 = generate_schema2(n)
        with open(f"data/C_{n}_gamma.json", "w") as f:
            json.dump(s2, f, indent=2)
        print(f"Generated data/C_{n}_gamma.json")
