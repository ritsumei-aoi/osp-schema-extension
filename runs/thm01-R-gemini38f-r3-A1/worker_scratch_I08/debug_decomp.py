import sys, os
from fractions import Fraction
from collections import defaultdict
import sympy as sp

REPO_ROOT = "<home>/notebook/git/thm01-R/thm01-R-gemini38f-r3-A1"
sys.path.insert(0, REPO_ROOT)
from src.C_generators import get_generators, parity_of

def osc_key(osc: str):
    if osc == 'a_1_p': return (0, 0, 0)
    if osc == 'a_1_m': return (0, 1, 0)
    parts = osc.split('_')
    return (1, int(parts[1]), 0 if parts[2] == 'p' else 1)

def normal_order_deformed_word(word: tuple):
    current = {(word, None): Fraction(1, 1)}
    while True:
        next_dict = defaultdict(Fraction)
        all_sorted = True
        for (w, param), coeff in current.items():
            if coeff == 0:
                continue
            found = False
            for i in range(len(w) - 1):
                o1, o2 = w[i], w[i+1]
                if o1 == o2 and parity_of(o1) == 1:
                    found = True
                    all_sorted = False
                    break
                elif osc_key(o1) > osc_key(o2):
                    found = True
                    all_sorted = False
                    if o1 == 'a_1_m' and o2 == 'a_1_p':
                        next_dict[(w[:i] + (o2, o1) + w[i+2:], param)] += -coeff
                        next_dict[(w[:i] + w[i+2:], param)] += coeff
                    elif o1.startswith('b_') and o2.startswith('b_'):
                        p1, p2 = o1.split('_'), o2.split('_')
                        j, s1 = int(p1[1]), p1[2]
                        k, s2 = int(p2[1]), p2[2]
                        if s1 == 'm' and s2 == 'p' and j == k:
                            next_dict[(w[:i] + (o2, o1) + w[i+2:], param)] += coeff
                            next_dict[(w[:i] + w[i+2:], param)] += coeff
                        else:
                            next_dict[(w[:i] + (o2, o1) + w[i+2:], param)] += coeff
                    elif o1.startswith('b_') and o2.startswith('a_'):
                        next_dict[(w[:i] + (o2, o1) + w[i+2:], param)] += coeff
                        if param is None:
                            parts_b = o1.split('_')
                            j, s = int(parts_b[1]), parts_b[2]
                            sigma = o2.split('_')[2]
                            p_name = f"gb_a1{sigma}_b{j}{s}"
                            next_dict[(w[:i] + w[i+2:], p_name)] += -coeff
                    else:
                        raise ValueError(f"Unhandled pair: {o1}, {o2}")
                    break
            if not found:
                next_dict[(w, param)] += coeff
        if all_sorted:
            return {k: v for k, v in current.items() if v != 0}
        current = next_dict

n = 1
even_basis, odd_basis, realizations, _, _, parity = get_generators(n)
all_basis = even_basis + odd_basis

all_words = set()
for b in all_basis:
    for w in realizations[b].keys():
        all_words.add(w)

word_list = sorted(list(all_words))
mat = []
for w in word_list:
    row = []
    for b in all_basis:
        row.append(realizations[b].get(w, Fraction(0)))
    mat.append(row)

M = sp.Matrix(mat)

for idx_X, X in enumerate(all_basis):
    pX = parity[X]
    polyX = realizations[X]
    for idx_Y, Y in enumerate(all_basis):
        pY = parity[Y]
        polyY = realizations[Y]

        XY = defaultdict(Fraction)
        for wX, cX in polyX.items():
            for wY, cY in polyY.items():
                res = normal_order_deformed_word(wX + wY)
                for k, v in res.items():
                    XY[k] += cX * cY * v

        YX = defaultdict(Fraction)
        for wY, cY in polyY.items():
            for wX, cX in polyX.items():
                res = normal_order_deformed_word(wY + wX)
                for k, v in res.items():
                    YX[k] += cY * cX * v

        sign_XY = -1 if (pX * pY) % 2 == 1 else 1
        bracket = defaultdict(Fraction)
        for k, v in XY.items(): bracket[k] += v
        for k, v in YX.items(): bracket[k] -= sign_XY * v

        by_param = defaultdict(lambda: defaultdict(Fraction))
        for (w, param), coeff in bracket.items():
            if coeff == 0 or param is None: continue
            by_param[param][w] += coeff

        for param, poly in by_param.items():
            rhs = sp.Matrix([poly.get(w, Fraction(0)) for w in word_list])
            # Check which words in poly are NOT in word_list:
            extra = {w: c for w, c in poly.items() if w not in word_list}
            if extra:
                print(f"X={X}, Y={Y}, param={param}: Extra words not in word_list: {extra}")
                sys.exit(0)
            try:
                M.gauss_jordan_solve(rhs)
            except Exception as e:
                print(f"Failed to solve for X={X}, Y={Y}, param={param}")
                print(f"poly={dict(poly)}")
                sys.exit(0)
