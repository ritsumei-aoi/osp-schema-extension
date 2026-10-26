"""
Test coboundary operator delta(f)(X, Y) on C(2).
Check what subspace B^1(g, g)_odd has.
"""
from test_coboundary import compute_coboundary_matrix
import sympy as sp
from collections import defaultdict
from fractions import Fraction

full_basis, parity, bracket_dict = compute_coboundary_matrix(1)
even_basis = [g for g in full_basis if parity[g] == 0]
odd_basis = [g for g in full_basis if parity[g] == 1]

# Basis for odd linear maps f:
# Type 1: f_{E, O}: f(E) = O, all other generators 0 (E in even, O in odd)
# Type 2: f_{O, E}: f(O) = E, all other generators 0 (O in odd, E in even)

# Let's compute delta(f)(X, Y) for each elementary map f:
# delta(f)(X, Y) = (-1)^{p(X)} [X, f(Y)] - (-1)^{(p(X)+1)p(Y)} [Y, f(X)] - f([X, Y])

def get_delta_f(f_dict, X, Y):
    # f_dict: generator -> {generator: Fraction}
    pX, pY = parity[X], parity[Y]
    res = defaultdict(Fraction)
    
    # Term 1: (-1)^{pX} [X, f(Y)]
    fY = f_dict.get(Y, {})
    s1 = -1 if pX == 1 else 1
    for mid, c_mid in fY.items():
        for fin, c_fin in bracket_dict.get((X, mid), {}).items():
            res[fin] += s1 * c_mid * c_fin
            
    # Term 2: - (-1)^{(pX + 1) pY} [Y, f(X)]
    fX = f_dict.get(X, {})
    s2 = -1 if ((pX + 1) * pY) % 2 == 1 else 1
    for mid, c_mid in fX.items():
        for fin, c_fin in bracket_dict.get((Y, mid), {}).items():
            res[fin] -= s2 * c_mid * c_fin
            
    # Term 3: - f([X, Y])
    xy = bracket_dict.get((X, Y), {})
    for mid, c_mid in xy.items():
        for fin, c_fin in f_dict.get(mid, {}).items():
            res[fin] -= c_mid * c_fin
            
    return {fin: c for fin, c in res.items() if c != 0}

# Let's test all elementary maps:
elementary_maps = []
# Type 1:
for E in even_basis:
    for O in odd_basis:
        f = {E: {O: Fraction(1)}}
        elementary_maps.append((f"{E}->{O}", f))
# Type 2:
for O in odd_basis:
    for E in even_basis:
        f = {O: {E: Fraction(1)}}
        elementary_maps.append((f"{O}->{E}", f))
        
print(f"Total elementary maps: {len(elementary_maps)}")

# Evaluate coboundary for each elementary map:
coboundary_vectors = []
pair_list = []
for X in full_basis:
    for Y in full_basis:
        pair_list.append((X, Y))

# Build big matrix of coboundary images:
# rows = pair_list x full_basis
# cols = elementary maps
row_entries = []
for (X, Y) in pair_list:
    for Z in full_basis:
        row_entries.append((X, Y, Z))
        
M_cob = sp.zeros(len(row_entries), len(elementary_maps))
for col_idx, (name, f) in enumerate(elementary_maps):
    for row_idx, (X, Y, Z) in enumerate(row_entries):
        val = get_delta_f(f, X, Y).get(Z, Fraction(0))
        M_cob[row_idx, col_idx] = val

rank_cob = M_cob.rank()
print(f"Coboundary space B^1(g, g)_odd rank: {rank_cob} / {len(elementary_maps)}")
