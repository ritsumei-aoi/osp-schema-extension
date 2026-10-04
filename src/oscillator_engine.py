"""
Symbolic Oscillator Engine for C(n+1)
"""

from fractions import Fraction

# Operator ordering: a_1_p < a_1_m < b_1_p < b_1_m < b_2_p < ...
def op_key(op):
    if op == "a_1_p": return (0, 1)
    if op == "a_1_m": return (0, 2)
    parts = op.split("_")
    k = int(parts[1])
    s = 1 if parts[2] == 'p' else 2
    return (k, s)

def is_fermion(op):
    return op.startswith("a_")

def op_parity(op):
    return 1 if is_fermion(op) else 0

def word_parity(word):
    return sum(op_parity(op) for op in word) % 2

def swap_adjacent(word, i):
    """
    Swaps word[i] and word[i+1].
    Returns list of (coeff, new_word) terms resulting from swap.
    """
    A = word[i]
    B = word[i+1]
    prefix = word[:i]
    suffix = word[i+2:]
    
    pA = op_parity(A)
    pB = op_parity(B)
    
    if pA == 1 and pB == 1:
        # AB = {A, B} - BA
        # {a_1_m, a_1_p} = 1
        anticomm = 0
        if (A == "a_1_m" and B == "a_1_p") or (A == "a_1_p" and B == "a_1_m"):
            anticomm = 1
        terms = []
        if anticomm != 0:
            terms.append((Fraction(anticomm), prefix + suffix))
        terms.append((Fraction(-1), prefix + (B, A) + suffix))
        return terms
    elif pA == 0 and pB == 0:
        # AB = [A, B] + BA
        # [b_k_m, b_k_p] = 1, [b_k_p, b_k_m] = -1
        comm = 0
        if A.startswith("b_") and B.startswith("b_"):
            kA, sA = int(A.split("_")[1]), A.split("_")[2]
            kB, sB = int(B.split("_")[1]), B.split("_")[2]
            if kA == kB:
                if sA == 'm' and sB == 'p': comm = 1
                elif sA == 'p' and sB == 'm': comm = -1
        terms = []
        if comm != 0:
            terms.append((Fraction(comm), prefix + suffix))
        terms.append((Fraction(1), prefix + (B, A) + suffix))
        return terms
    else:
        # Mixed fermion/boson: commute trivially AB = BA
        return [(Fraction(1), prefix + (B, A) + suffix)]

def reduce_word(word):
    """
    Reduces any tuple of operator labels to a canonical dict {sorted_word_tuple: Fraction_coeff}.
    """
    # Work with dict of {word_tuple: coeff}
    state = {tuple(word): Fraction(1)}
    
    while True:
        next_state = {}
        all_sorted = True
        
        for w, c in state.items():
            # Find first out-of-order adjacent pair
            out_of_order_i = -1
            for i in range(len(w) - 1):
                if op_key(w[i]) > op_key(w[i+1]):
                    out_of_order_i = i
                    break
            if out_of_order_i != -1:
                all_sorted = False
                expanded = swap_adjacent(w, out_of_order_i)
                for coeff_factor, new_w in expanded:
                    next_state[new_w] = next_state.get(new_w, Fraction(0)) + c * coeff_factor
            else:
                next_state[w] = next_state.get(w, Fraction(0)) + c
                
        state = {w: c for w, c in next_state.items() if c != 0}
        if all_sorted:
            break
            
    return state

def poly_multiply_graded(poly1, poly2):
    """
    poly1, poly2 are list of {"words": tuple, "coeff": Fraction}
    Computes poly1 * poly2 - (-1)^(p1*p2) poly2 * poly1.
    """
    res = {}
    for term1 in poly1:
        w1, c1 = tuple(term1["words"]), Fraction(term1["coeff"])
        p1 = word_parity(w1)
        for term2 in poly2:
            w2, c2 = tuple(term2["words"]), Fraction(term2["coeff"])
            p2 = word_parity(w2)
            
            sign = -1 if (p1 == 1 and p2 == 1) else 1
            # term1 * term2
            w_12 = w1 + w2
            red12 = reduce_word(w_12)
            for w, c in red12.items():
                res[w] = res.get(w, Fraction(0)) + c1 * c2 * c
                
            # - (-1)^(p1*p2) term2 * term1
            w_21 = w2 + w1
            red21 = reduce_word(w_21)
            for w, c in red21.items():
                res[w] = res.get(w, Fraction(0)) - Fraction(sign) * c1 * c2 * c
                
    return {w: c for w, c in res.items() if c != 0}
