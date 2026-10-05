import sympy as sp
from collections import defaultdict

# Let's test the normal ordering function for oscillators.

def test_normal_order():
    # Oscillators: a+ (p=1), a- (p=1), b+ (p=0), b- (p=0)
    # Order: a+, a-, b+, b-
    osc_order = {'a+': 0, 'a-': 1, 'b+': 2, 'b-': 3}
    parity = {'a+': 1, 'a-': 1, 'b+': 0, 'b-': 0}
    
    # C(u, v) = [u, v] = uv - (-1)^{pu pv} vu
    # Undeformed:
    # [b-, b+] = 1, [b+, b-] = -1
    # [a-, a+] = 1, [a+, a-] = 1
    def C_und(u, v):
        if u == 'b-' and v == 'b+': return 1
        if u == 'b+' and v == 'b-': return -1
        if (u == 'a-' and v == 'a+') or (u == 'a+' and v == 'a-'): return 1
        return 0

    # Let's reduce a sequence of oscillators to normal order:
    # An element is a dict: { tuple_of_oscillators: coefficient }
    # where tuple_of_oscillators is sorted according to osc_order.
    # Note: for fermions, if a+ a+ occurs, it is 0 because {a+, a+} = 0 => 2(a+)^2 = 0 => (a+)^2 = 0.
    
    def reduce_word(word, coeff=1):
        # word is a tuple of oscillator names
        # returns dict of sorted tuples -> coeff
        # We find the first adjacent inversion
        for i in range(len(word) - 1):
            u, v = word[i], word[i+1]
            if u == v and parity[u] == 1:
                # fermion squared is 0!
                return {}
            if osc_order[u] > osc_order[v]:
                # Swap: uv = (-1)^{pu pv} vu + [u, v]
                sign = -1 if (parity[u] == 1 and parity[v] == 1) else 1
                comm = C_und(u, v)
                
                # Term 1: swap u and v
                word1 = word[:i] + (v, u) + word[i+2:]
                res1 = reduce_word(word1, coeff * sign)
                
                # Term 2: contraction [u, v]
                res2 = {}
                if comm != 0:
                    word2 = word[:i] + word[i+2:]
                    res2 = reduce_word(word2, coeff * comm)
                
                # Combine res1 and res2
                combined = defaultdict(int)
                for w, c in res1.items(): combined[w] += c
                for w, c in res2.items(): combined[w] += c
                return {w: c for w, c in combined.items() if c != 0}
        
        # Check if identical fermions remain
        for i in range(len(word) - 1):
            if word[i] == word[i+1] and parity[word[i]] == 1:
                return {}
        return {word: coeff}

    # Test [b-, b+] = b- b+ - b+ b- = 1
    # b- b+ -> b+ b- + 1
    print("b- b+ ->", reduce_word(('b-', 'b+')))
    # a- a+ -> - a+ a- + 1
    print("a- a+ ->", reduce_word(('a-', 'a+')))
    
    # Test [a+ b-, b+ a-] = {a+ b-, b+ a-}
    # (a+ b-) (b+ a-) = a+ b- b+ a-
    t1 = reduce_word(('a+', 'b-', 'b+', 'a-'))
    # (b+ a-) (a+ b-) = b+ a- a+ b-
    t2 = reduce_word(('b+', 'a-', 'a+', 'b-'))
    # Supercommutator for two odd elements is t1 + t2:
    comm = defaultdict(int)
    for w, c in t1.items(): comm[w] += c
    for w, c in t2.items(): comm[w] += c
    comm = {w: c for w, c in comm.items() if c != 0}
    print("[a+ b-, b+ a-] ->", comm)

test_normal_order()
