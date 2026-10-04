import sympy as sp
import itertools

def p(idx):
    # 0,1,2,3 are even, 4,5,6,7 are odd
    return 0 if idx < 4 else 1

# [X, Y]_0 for C(2)
# X, Y in {E_2d, E_-2d, E_0, H, O_p_p, O_p_m, O_m_p, O_m_m}
# 0: b+ b+
# 1: b- b-
# 2: b+ b- + b- b+
# 3: a+ a- - a- a+
# 4: a+ b+
# 5: a+ b-
# 6: a- b+
# 7: a- b-

def get_comm_table():
    # Write a quick associative algebra multiplier for oscillators
    # to compute commutators automatically
    # variables: a_p, a_m, b_p, b_m
    # relations: a_m a_p = 1 - a_p a_m
    #            b_m b_p = 1 + b_p b_m
    def mul(w1, w2):
        # w1, w2 are tuples of strings
        res = {(w1 + w2): 1}
        return reduce_word(res)
        
    def reduce_word(expr):
        # expr is a dict of word (tuple) -> coeff
        changed = True
        while changed:
            changed = False
            new_expr = {}
            for w, c in expr.items():
                if c == 0: continue
                # find first non-ordered pair
                reduced = False
                for i in range(len(w)-1):
                    # order: a_p, a_m, b_p, b_m
                    val1 = {'a_p':0, 'a_m':1, 'b_p':2, 'b_m':3}[w[i]]
                    val2 = {'a_p':0, 'a_m':1, 'b_p':2, 'b_m':3}[w[i+1]]
                    if val1 > val2:
                        # swap!
                        if w[i]=='a_m' and w[i+1]=='a_p':
                            # a_m a_p = 1 - a_p a_m
                            w_new = w[:i] + ('a_p', 'a_m') + w[i+2:]
                            w_id = w[:i] + w[i+2:]
                            add(new_expr, w_new, -c)
                            add(new_expr, w_id, c)
                        elif w[i]=='b_m' and w[i+1]=='b_p':
                            # b_m b_p = 1 + b_p b_m
                            w_new = w[:i] + ('b_p', 'b_m') + w[i+2:]
                            w_id = w[:i] + w[i+2:]
                            add(new_expr, w_new, c)
                            add(new_expr, w_id, c)
                        else:
                            # everything else supercommutes.
                            # b and b commute
                            # a and b commute (in standard algebra)
                            # wait, a and a anticommute
                            if w[i].startswith('a') and w[i+1].startswith('a'):
                                w_new = w[:i] + (w[i+1], w[i]) + w[i+2:]
                                add(new_expr, w_new, -c)
                            elif w[i].startswith('b') and w[i+1].startswith('b'):
                                w_new = w[:i] + (w[i+1], w[i]) + w[i+2:]
                                add(new_expr, w_new, c)
                            else:
                                # a and b commute!
                                w_new = w[:i] + (w[i+1], w[i]) + w[i+2:]
                                add(new_expr, w_new, c)
                        reduced = True
                        changed = True
                        break
                if not reduced:
                    add(new_expr, w, c)
            expr = new_expr
        return expr
        
    def add(expr, w, c):
        expr[w] = expr.get(w, 0) + c
        
    def add_expr(expr1, expr2, factor=1):
        res = dict(expr1)
        for w, c in expr2.items():
            res[w] = res.get(w, 0) + factor * c
            if res[w] == 0: del res[w]
        return res

    gens = {
        0: {('b_p', 'b_p'): 1},
        1: {('b_m', 'b_m'): 1},
        2: {('b_p', 'b_m'): 2, (): 1}, # b+b- + b-b+ = 2 b+b- + 1
        3: {('a_p', 'a_m'): 2, (): -1}, # a+a- - a-a+ = 2 a+a- - 1
        4: {('a_p', 'b_p'): 1},
        5: {('a_p', 'b_m'): 1},
        6: {('a_m', 'b_p'): 1},
        7: {('a_m', 'b_m'): 1},
    }
    
    # Let's verify generators format
    # Now we compute supercommutators
    comm = {}
    for i in range(8):
        for j in range(8):
            expr1 = {}
            for w1, c1 in gens[i].items():
                for w2, c2 in gens[j].items():
                    expr1 = add_expr(expr1, mul(w1, w2), c1*c2)
                    
            expr2 = {}
            for w2, c2 in gens[j].items():
                for w1, c1 in gens[i].items():
                    expr2 = add_expr(expr2, mul(w2, w1), c1*c2)
                    
            # [X, Y] = X Y - (-1)^{pX pY} Y X
            sign = -1 if (p(i)==1 and p(j)==1) else 1
            bracket = add_expr(expr1, expr2, -sign)
            comm[(i, j)] = bracket
            
    # Express bracket in terms of generators
    def to_gens(expr):
        # We need to write expr (dict of words) as linear comb of gens
        # Because it's a Lie superalgebra, the result must be a linear comb of gens
        # + possibly a constant (which is central)
        res = [0]*8
        # Find coeff of b+b+
        c0 = expr.get(('b_p', 'b_p'), 0)
        res[0] = c0
        
        c1 = expr.get(('b_m', 'b_m'), 0)
        res[1] = c1
        
        c2 = expr.get(('b_p', 'b_m'), 0)
        # gens[2] = 2 b+b- + 1
        res[2] = c2 / 2
        
        c3 = expr.get(('a_p', 'a_m'), 0)
        # gens[3] = 2 a+a- - 1
        res[3] = c3 / 2
        
        c4 = expr.get(('a_p', 'b_p'), 0)
        res[4] = c4
        
        c5 = expr.get(('a_p', 'b_m'), 0)
        res[5] = c5
        
        c6 = expr.get(('a_m', 'b_p'), 0)
        res[6] = c6
        
        c7 = expr.get(('a_m', 'b_m'), 0)
        res[7] = c7
        
        return res
        
    comm_table = {}
    for k, v in comm.items():
        comm_table[k] = to_gens(v)
        
    return comm_table

if __name__ == "__main__":
    t = get_comm_table()
    print("Comm Table for 0, 4:")
    print(t[(0, 4)])
