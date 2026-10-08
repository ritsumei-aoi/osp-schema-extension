import fractions
import itertools
import json
import os

def rank(op):
    if op == "a_1_p": return 0
    if op == "a_1_m": return 1
    if op.startswith("b_") and op.endswith("_p"):
        k = int(op.split("_")[1])
        return 2*k
    if op.startswith("b_") and op.endswith("_m"):
        k = int(op.split("_")[1])
        return 2*k + 1
    return 99

def is_odd(op):
    return op.startswith("a_")

def add_term(poly, word, coeff):
    if word in poly:
        poly[word] += coeff
    else:
        poly[word] = coeff
    if poly[word] == 0:
        del poly[word]

def normal_order(word):
    poly = {word: fractions.Fraction(1)}
    changed = True
    while changed:
        changed = False
        new_poly = {}
        for w, coeff in poly.items():
            if coeff == 0: continue
            
            ordered = True
            for i in range(len(w) - 1):
                if rank(w[i]) > rank(w[i+1]):
                    ordered = False
                    x, y = w[i], w[i+1]
                    
                    if is_odd(x) and is_odd(y):
                        # xy = -yx + {x,y}
                        w_swapped = w[:i] + (y, x) + w[i+2:]
                        add_term(new_poly, w_swapped, -coeff)
                        if x == "a_1_m" and y == "a_1_p":
                            w_rest = w[:i] + w[i+2:]
                            add_term(new_poly, w_rest, coeff)
                    elif not is_odd(x) and not is_odd(y):
                        # xy = yx + [x,y]
                        w_swapped = w[:i] + (y, x) + w[i+2:]
                        add_term(new_poly, w_swapped, coeff)
                        if x.endswith("_m") and y.endswith("_p") and x[2:-2] == y[2:-2]:
                            w_rest = w[:i] + w[i+2:]
                            add_term(new_poly, w_rest, coeff)
                    else:
                        # boson and fermion commute
                        w_swapped = w[:i] + (y, x) + w[i+2:]
                        add_term(new_poly, w_swapped, coeff)
                    break
            
            if ordered:
                # check fermionic squares
                has_square = False
                for i in range(len(w)-1):
                    if w[i] == w[i+1] and is_odd(w[i]):
                        has_square = True
                if not has_square:
                    add_term(new_poly, w, coeff)
            else:
                changed = True
        
        if changed:
            poly = new_poly
            
    return {w: c for w, c in poly.items() if c != 0}

def mul_polys(p1, p2):
    res = {}
    for w1, c1 in p1.items():
        for w2, c2 in p2.items():
            add_term(res, w1 + w2, c1 * c2)
    
    # normal order the result
    no_res = {}
    for w, c in res.items():
        w_poly = normal_order(w)
        for w_no, c_no in w_poly.items():
            add_term(no_res, w_no, c * c_no)
    return no_res

def add_polys(p1, p2):
    res = dict(p1)
    for w, c in p2.items():
        add_term(res, w, c)
    return res

def mul_scalar(p, s):
    return {w: c * fractions.Fraction(s) for w, c in p.items() if c * s != 0}

# Testing the engine
if __name__ == "__main__":
    p1 = {("a_1_m",): 1}
    p2 = {("a_1_p",): 1}
    print(mul_polys(p1, p2))
