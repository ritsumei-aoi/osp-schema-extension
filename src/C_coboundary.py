import json
from collections import defaultdict

def build_coboundary(n):
    with open(f"data/C_{n}_structure.json") as f:
        data = json.load(f)
        
    basis = data["basis"]["even"] + data["basis"]["odd"]
    parities = data["parity"]
    
    C = defaultdict(lambda: defaultdict(lambda: defaultdict(int)))
    for entry in data["structure_constants"]:
        X = entry["X"]
        Y = entry["Y"]
        Z = entry["Z"]
        c = int(entry["coeff"])
        C[X][Y][Z] = c
        
    # Fill in anti-symmetry for C
    for X in basis:
        for Y in basis:
            if X == Y:
                continue
            if not C[Y][X]:
                sign = -1 if parities[X] * parities[Y] == 1 else 1
                for Z, c in C[X][Y].items():
                    if c != 0:
                        C[Y][X][Z] = -sign * c

    # (delta f)(X, Y) = (-1)^{p(X)} [X, f(Y)] - (-1)^{(p(X)+1)p(Y)} [Y, f(X)] - f([X, Y])
    # f(U) = V is parameterized by phi_{U, V}
    # coeff of Z in (delta f)(X, Y) for phi_{U, V} is:
    # delta_{Y, U} * (-1)^{p(X)} C[X][V][Z]
    # - delta_{X, U} * (-1)^{(p(X)+1)*p(Y)} C[Y][V][Z]
    # - delta_{Z, V} * C[X][Y][U]
    
    coboundary_constants = []
    
    # We only care about X <= Y for the output table
    for i, X in enumerate(basis):
        for j in range(i, len(basis)):
            Y = basis[j]
            
            # Since f is odd, p(U) != p(V).
            # We can iterate over all possible pairs (U, V) that might contribute.
            # To be efficient, we only consider (U, V) where one of the deltas is non-zero.
            
            # Case 1: Y = U, so we need C[X][V][Z] != 0
            # For each V, Z where C[X][V][Z] != 0
            U = Y
            for V in basis:
                if parities[U] == parities[V]: continue
                for Z, cXVZ in C[X][V].items():
                    if cXVZ == 0: continue
                    term1 = ((-1) ** parities[X]) * cXVZ
                    # check if other cases overlap
                    term2 = 0
                    if X == U:
                        term2 = -((-1) ** ((parities[X] + 1) * parities[Y])) * C[Y][V][Z]
                    term3 = 0
                    if Z == V:
                        term3 = -C[X][Y][U]
                    
                    total = term1 + term2 + term3
                    if total != 0:
                        coboundary_constants.append((X, Y, Z, U, V, total))
                        
            # Case 2: X = U
            U = X
            if X != Y: # If X==Y, it's already covered by Case 1
                for V in basis:
                    if parities[U] == parities[V]: continue
                    for Z, cYVZ in C[Y][V].items():
                        if cYVZ == 0: continue
                        
                        term1 = 0 # Y = U (meaning X=Y) is handled above
                        term2 = -((-1) ** ((parities[X] + 1) * parities[Y])) * cYVZ
                        term3 = 0
                        if Z == V:
                            term3 = -C[X][Y][U]
                            
                        total = term1 + term2 + term3
                        if total != 0:
                            coboundary_constants.append((X, Y, Z, U, V, total))
                            
            # Case 3: Z = V
            for U in basis:
                if C[X][Y][U] == 0: continue
                V = Z # wait, Z is not bound yet.
                # For each Z, we set V = Z
                for Z in basis:
                    V = Z
                    if parities[U] == parities[V]: continue
                    
                    # check overlap
                    if Y == U and C[X][V][Z] != 0: continue # Handled in Case 1
                    if X == U and C[Y][V][Z] != 0: continue # Handled in Case 2 (or 1)
                    
                    term3 = -C[X][Y][U]
                    total = term3
                    if total != 0:
                        coboundary_constants.append((X, Y, Z, U, V, total))
                        
    # Remove duplicates because overlaps were somewhat loosely handled, just use a set or dict
    # Wait, the logic above has a flaw: iterating and continuing might miss terms if total was non-zero but one term was handled!
    # Much safer: just build a dict.
    
    coboundary_dict = defaultdict(int)
    for i, X in enumerate(basis):
        for j in range(i, len(basis)):
            Y = basis[j]
            
            # For each U, V where parities differ
            # we only need to look at U in {X, Y} or U in C[X][Y].keys()
            active_Us = set([X, Y])
            for U, c in C[X][Y].items():
                if c != 0: active_Us.add(U)
                
            for U in active_Us:
                for V in basis:
                    if parities[U] == parities[V]: continue
                    
                    total = 0
                    if Y == U:
                        total += ((-1) ** parities[X]) * C[X][V].get(Z, 0) # Wait, Z is not fixed!
    
    # Better logic:
    coboundary_dict_final = defaultdict(int)
    for i, X in enumerate(basis):
        for j in range(i, len(basis)):
            Y = basis[j]
            
            # term1: Y = U => iterate V, Z in C[X][V]
            U = Y
            for V in basis:
                if parities[U] == parities[V]: continue
                for Z, c in C[X][V].items():
                    coboundary_dict_final[(X, Y, Z, U, V)] += ((-1) ** parities[X]) * c
                    
            # term2: X = U => iterate V, Z in C[Y][V]
            U = X
            for V in basis:
                if parities[U] == parities[V]: continue
                for Z, c in C[Y][V].items():
                    coboundary_dict_final[(X, Y, Z, U, V)] -= ((-1) ** ((parities[X] + 1) * parities[Y])) * c
                    
            # term3: iterate U in C[X][Y]
            for U, c in C[X][Y].items():
                if c == 0: continue
                # Z = V
                for V in basis:
                    if parities[U] == parities[V]: continue
                    Z = V
                    coboundary_dict_final[(X, Y, Z, U, V)] -= c

    coboundary_out = []
    for (X, Y, Z, U, V), coeff in coboundary_dict_final.items():
        if coeff != 0:
            coboundary_out.append({
                "X": X, "Y": Y, "Z": Z,
                "f_in": U, "f_out": V,
                "coeff": str(coeff)
            })
            
    schema4 = {
        "schema_version": "5.0",
        "algebra": data["algebra"],
        "coboundary_structure": coboundary_out,
        "metadata": {
            "generated_by": "C_coboundary.py",
            "generation_date": "2026-10-10"
        }
    }
    
    with open(f"data/C_{n}_coboundary.json", "w") as f:
        json.dump(schema4, f, indent=2)

if __name__ == "__main__":
    for n in [1, 2, 3]:
        build_coboundary(n)
        print(f"Generated Coboundary for n={n}")
