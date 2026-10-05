import json
import itertools
from collections import defaultdict
import os

class Word:
    def __init__(self, letters):
        self.letters = tuple(letters)

    def __hash__(self):
        return hash(self.letters)

    def __eq__(self, other):
        return self.letters == other.letters

class Poly:
    def __init__(self, terms=None):
        self.terms = defaultdict(int)
        if terms:
            for w, c in terms.items():
                if c != 0:
                    self.terms[w] += c
        self.clean()

    def clean(self):
        to_del = [w for w, c in self.terms.items() if c == 0]
        for w in to_del:
            del self.terms[w]

    def __add__(self, other):
        res = Poly(self.terms)
        for w, c in other.terms.items():
            res.terms[w] += c
        res.clean()
        return res

    def __sub__(self, other):
        res = Poly(self.terms)
        for w, c in other.terms.items():
            res.terms[w] -= c
        res.clean()
        return res

    def __mul__(self, other):
        if isinstance(other, (int, float)):
            res = Poly()
            for w, c in self.terms.items():
                res.terms[w] = c * other
            res.clean()
            return res
        
        res = Poly()
        for w1, c1 in self.terms.items():
            for w2, c2 in other.terms.items():
                res.terms[Word(w1.letters + w2.letters)] += c1 * c2
        res.clean()
        return normal_order(res)

def normal_order(poly):
    """
    Normal order a polynomial.
    Variables: a_1_p, a_1_m, b_{k}_p, b_{k}_m
    Parity: a are odd (1), b are even (0)
    Order: a_1_p > a_1_m > b_1_p > b_1_m > b_2_p > b_2_m ...
    Wait, the string values can be sorted. We want to sort them lexicographically if we just use a suitable key.
    """
    def order_key(letter):
        if letter == 'a_1_p': return 0
        if letter == 'a_1_m': return 1
        if letter.startswith('b_'):
            parts = letter.split('_')
            k = int(parts[1])
            is_m = (parts[2] == 'm')
            return 2 + 2*k + (1 if is_m else 0)
        return 99

    def parity(letter):
        if letter.startswith('a_'): return 1
        return 0

    def commutator(A, B):
        # returns [A, B} depending on parities, as a scalar.
        # Actually A B - (-1)^{|A||B|} B A = C
        # A B = (-1)^{|A||B|} B A + C
        if A == 'a_1_m' and B == 'a_1_p':
            # {a_1^-, a_1^+} = 1 => a_1^- a_1^+ = -a_1^+ a_1^- + 1
            return 1
        if A.startswith('b_') and B.startswith('b_'):
            partsA = A.split('_')
            partsB = B.split('_')
            if partsA[1] == partsB[1] and partsA[2] == 'm' and partsB[2] == 'p':
                # [b_k^-, b_k^+] = 1 => b_k^- b_k^+ = b_k^+ b_k^- + 1
                return 1
        return 0

    res = Poly()
    for w, c in poly.terms.items():
        letters = list(w.letters)
        swapped = True
        current_polys = [(letters, c)]
        
        while current_polys:
            new_polys = []
            for l, coef in current_polys:
                swapped = False
                for i in range(len(l) - 1):
                    A, B = l[i], l[i+1]
                    if order_key(A) > order_key(B):
                        # Swap A and B
                        sign = -1 if parity(A) * parity(B) == 1 else 1
                        new_l = l[:]
                        new_l[i], new_l[i+1] = B, A
                        new_polys.append((new_l, sign * coef))
                        
                        comm = commutator(A, B)
                        if comm != 0:
                            comm_l = l[:i] + l[i+2:]
                            new_polys.append((comm_l, coef * comm))
                        swapped = True
                        break
                if not swapped:
                    res.terms[Word(l)] += coef
            current_polys = new_polys
    res.clean()
    return res

def var(name):
    return Poly({Word([name]): 1})

def const(val):
    return Poly({Word([]): val})

def graded_commutator(X, Y, px, py):
    # [X, Y} = X Y - (-1)^{px * py} Y X
    sign = -1 if px * py == 1 else 1
    return normal_order(X * Y - Y * X * sign)
