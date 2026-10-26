"""
Scratch script to test Jacobi identity on C(n+1) for n=1, 2.
"""
from test_closure import get_c_generators, superbracket, decompose_into_basis
import sympy as sp
from fractions import Fraction

def test_jacobi(n):
    gens = get_c_generators(n)
    names = list(gens.keys())
    all_words = set()
    for g in gens.values():
        all_words.update(g["poly"].keys())
    word_list = sorted(list(all_words))
    M_sp = sp.Matrix([[gens[name]["poly"].get(w, Fraction(0)) for name in names] for w in word_list])
    
    # Precompute bracket table
    table = {}
    for i, n1 in enumerate(names):
        for j, n2 in enumerate(names):
            p1, p2 = gens[n1]["parity"], gens[n2]["parity"]
            br = superbracket(gens[n1]["poly"], p1, gens[n2]["poly"], p2)
            if not br:
                table[(n1, n2)] = {}
                continue
            br_vec = sp.Matrix([br.get(w, Fraction(0)) for w in word_list])
            sol, _ = M_sp.gauss_jordan_solve(br_vec)
            decomp = {names[k]: sol[k] for k in range(len(names)) if sol[k] != 0}
            table[(n1, n2)] = decomp
            
    print(f"Table computed for n={n}.")
    
    # Check graded Jacobi identity for all triples (X, Y, Z)
    # (-1)^{p(X)p(Z)} [X, [Y, Z]} + (-1)^{p(Y)p(X)} [Y, [Z, X]} + (-1)^{p(Z)p(Y)} [Z, [X, Y]} = 0
    jacobi_ok = True
    tested = 0
    for i in range(len(names)):
        n1 = names[i]
        p1 = gens[n1]["parity"]
        for j in range(len(names)):
            n2 = names[j]
            p2 = gens[n2]["parity"]
            for k in range(len(names)):
                n3 = names[k]
                p3 = gens[n3]["parity"]
                tested += 1
                
                # term 1: (-1)^{p1 p3} [n1, [n2, n3]}
                term1 = {}
                for mid, c in table[(n2, n3)].items():
                    for fin, c2 in table[(n1, mid)].items():
                        term1[fin] = term1.get(fin, 0) + c * c2
                s1 = -1 if (p1 * p3) % 2 == 1 else 1
                
                # term 2: (-1)^{p2 p1} [n2, [n3, n1]}
                term2 = {}
                for mid, c in table[(n3, n1)].items():
                    for fin, c2 in table[(n2, mid)].items():
                        term2[fin] = term2.get(fin, 0) + c * c2
                s2 = -1 if (p2 * p1) % 2 == 1 else 1
                
                # term 3: (-1)^{p3 p2} [n3, [n1, n2]}
                term3 = {}
                for mid, c in table[(n1, n2)].items():
                    for fin, c2 in table[(n3, mid)].items():
                        term3[fin] = term3.get(fin, 0) + c * c2
                s3 = -1 if (p3 * p2) % 2 == 1 else 1
                
                all_fin = set(term1.keys()) | set(term2.keys()) | set(term3.keys())
                for fin in all_fin:
                    tot = s1 * term1.get(fin, 0) + s2 * term2.get(fin, 0) + s3 * term3.get(fin, 0)
                    if tot != 0:
                        print(f"Jacobi failed for ({n1}, {n2}, {n3}) on {fin}: {tot}")
                        jacobi_ok = False
                        break
                if not jacobi_ok:
                    break
            if not jacobi_ok:
                break
        if not jacobi_ok:
            break
            
    print(f"Jacobi identity verified for n={n} ({tested} triples): {jacobi_ok}")

if __name__ == "__main__":
    test_jacobi(1)
    test_jacobi(2)
