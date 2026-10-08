import sympy as sp

# We need the structure constants of C(2).
# Basis:
# B1 = b+ b+
# B2 = b- b-
# B3 = b+ b- + 1/2
# B4 = a+ a- - 1/2
# F1 = a+ b+
# F2 = a+ b-
# F3 = a- b+
# F4 = a- b-

def NO_product(t1, t2):
    # normal order the product of two terms, returning dict of {term: coeff}
    # terms are represented as tuple of strings e.g. ('a+', 'b+', 'b+')
    term = list(t1) + list(t2)
    
    res = [(1, term)]
    changed = True
    while changed:
        changed = False
        new_res = []
        for coeff, t in res:
            swapped = False
            for i in range(len(t)-1):
                o1, o2 = t[i], t[i+1]
                rank = {'a+':1, 'a-':2, 'b+':3, 'b-':4}
                if rank[o1] > rank[o2]:
                    if o1[0] == 'a' and o2[0] == 'a': # a- a+
                        t1_ = t[:i] + [] + t[i+2:]
                        t2_ = t[:i] + ['a+', 'a-'] + t[i+2:]
                        new_res.append((coeff, t1_))
                        new_res.append((-coeff, t2_))
                        swapped = True
                        break
                    elif o1[0] == 'b' and o2[0] == 'b': # b- b+
                        t1_ = t[:i] + [] + t[i+2:]
                        t2_ = t[:i] + ['b+', 'b-'] + t[i+2:]
                        new_res.append((coeff, t1_))
                        new_res.append((coeff, t2_))
                        swapped = True
                        break
                    else: # b a -> a b
                        new_t = t[:i] + [o2, o1] + t[i+2:]
                        new_res.append((coeff, new_t))
                        swapped = True
                        break
            if not swapped:
                new_res.append((coeff, t))
            else:
                changed = True
        res = new_res
        
        comb = {}
        for c, t in res:
            key = tuple(t)
            comb[key] = comb.get(key, 0) + c
        res = [(c, list(key)) for key, c in comb.items() if c != 0]
    
    return {tuple(t): c for c, t in res}

def NO_add(d1, d2, sign=1):
    res = dict(d1)
    for k, v in d2.items():
        res[k] = res.get(k, 0) + sign * v
    return {k: v for k, v in res.items() if v != 0}

def NO_scale(d, s):
    return {k: v * s for k, v in d.items() if v * s != 0}

basis_defs = {
    'B1': {('b+','b+'): 1},
    'B2': {('b-','b-'): 1},
    'B3': {('b+','b-'): 1, (): 0.5},
    'B4': {('a+','a-'): 1, (): -0.5},
    'F1': {('a+','b+'): 1},
    'F2': {('a+','b-'): 1},
    'F3': {('a-','b+'): 1},
    'F4': {('a-','b-'): 1},
}

basis_names = ['B1', 'B2', 'B3', 'B4', 'F1', 'F2', 'F3', 'F4']

def p(name):
    return 1 if name.startswith('F') else 0

def commutator(name1, name2):
    d1 = basis_defs[name1]
    d2 = basis_defs[name2]
    
    # multiply d1 * d2
    prod12 = {}
    for k1, v1 in d1.items():
        for k2, v2 in d2.items():
            res = NO_product(k1, k2)
            prod12 = NO_add(prod12, NO_scale(res, v1 * v2))
            
    # multiply d2 * d1
    prod21 = {}
    for k1, v1 in d1.items():
        for k2, v2 in d2.items():
            res = NO_product(k2, k1)
            prod21 = NO_add(prod21, NO_scale(res, v1 * v2))
            
    sign = -1 if (p(name1) * p(name2) == 0) else 1
    
    return NO_add(prod12, prod21, -sign)

# Try to express the result in the basis
def express_in_basis(d):
    res = {}
    d_copy = dict(d)
    
    # greedy match
    # B1: ('b+','b+')
    if ('b+','b+') in d_copy:
        c = d_copy[('b+','b+')]
        res['B1'] = c
        d_copy = NO_add(d_copy, NO_scale(basis_defs['B1'], -c))
    if ('b-','b-') in d_copy:
        c = d_copy[('b-','b-')]
        res['B2'] = c
        d_copy = NO_add(d_copy, NO_scale(basis_defs['B2'], -c))
    if ('b+','b-') in d_copy:
        c = d_copy[('b+','b-')]
        res['B3'] = c
        d_copy = NO_add(d_copy, NO_scale(basis_defs['B3'], -c))
    if ('a+','a-') in d_copy:
        c = d_copy[('a+','a-')]
        res['B4'] = c
        d_copy = NO_add(d_copy, NO_scale(basis_defs['B4'], -c))
    if ('a+','b+') in d_copy:
        c = d_copy[('a+','b+')]
        res['F1'] = c
        d_copy = NO_add(d_copy, NO_scale(basis_defs['F1'], -c))
    if ('a+','b-') in d_copy:
        c = d_copy[('a+','b-')]
        res['F2'] = c
        d_copy = NO_add(d_copy, NO_scale(basis_defs['F2'], -c))
    if ('a-','b+') in d_copy:
        c = d_copy[('a-','b+')]
        res['F3'] = c
        d_copy = NO_add(d_copy, NO_scale(basis_defs['F3'], -c))
    if ('a-','b-') in d_copy:
        c = d_copy[('a-','b-')]
        res['F4'] = c
        d_copy = NO_add(d_copy, NO_scale(basis_defs['F4'], -c))
        
    # verify d_copy is empty
    d_copy = {k: v for k, v in d_copy.items() if abs(v) > 1e-9}
    if len(d_copy) > 0:
        print("ERROR: Could not express in basis:", d_copy)
    return res

print("Computing structure constants...")
for n1 in basis_names:
    for n2 in basis_names:
        comm = commutator(n1, n2)
        expr = express_in_basis(comm)
        if expr:
            print(f"[{n1}, {n2}] = {expr}")

