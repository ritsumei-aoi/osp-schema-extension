"""
Construct an EXPLICIT odd linear map f with delta f = gamma_{gb} for general gb,
proving constructively that every inhomogeneous deformation is trivial.

Method: solve the linear system  (delta f)(Z_a,Z_b)[c] = gamma_{gb}(Z_a,Z_b)[c]
for the phi-coefficients of f, treating gb as free symbolic parameters.
We obtain phi as linear forms in gb, then VERIFY delta f = gamma_gb on every
pair via the engine-derived structure constants / cocycle (symbolic identity).
"""
import json
from sympy import symbols, Matrix, zeros, simplify, linsolve, S, Eq, solve
from analyze import build_structures


def solve_f(n):
    S_ = build_structures(n)
    C, Gamma, parity, D = S_['C'], S_['Gamma'], S_['parity'], S_['D']
    names, gb_syms = S_['names'], S_['gb_syms']

    # phi variables
    phi = {}
    for j in range(D):
        for i in range(D):
            if parity[i] != parity[j]:
                phi[(i, j)] = symbols(f"phi_{i}_{j}")
    # delta f (a,b) as dict c-> expr (linear in phi)
    def deltaf(a, b):
        pa, pb = parity[a], parity[b]
        out = {}
        def add(c, v):
            out[c] = out.get(c, 0) + v
        s1 = (-1) ** pa
        for i in range(D):
            if (i, b) in phi:
                for c, cc in C[(a, i)].items():
                    add(c, s1 * phi[(i, b)] * cc)
        s2 = -((-1) ** ((pa + 1) * pb))
        for i in range(D):
            if (i, a) in phi:
                for c, cc in C[(b, i)].items():
                    add(c, s2 * phi[(i, a)] * cc)
        for d, cab in C[(a, b)].items():
            for i in range(D):
                if (i, d) in phi:
                    add(i, -cab * phi[(i, d)])
        return {c: v for c, v in out.items() if v != 0}

    # Build equations delta f - gamma = 0 over all pairs/components
    eqs = []
    for a in range(D):
        for b in range(a + 1, D):
            df = deltaf(a, b)
            gm = Gamma[(a, b)]
            comps = set(df) | set(gm)
            for c in comps:
                e = simplify(df.get(c, 0) - gm.get(c, 0))
                if e != 0:
                    eqs.append(e)

    phivars = list(phi.values())
    sol = solve(eqs, phivars, dict=True)
    if not sol:
        return S_, phi, None, False
    sol = sol[0]
    # particular solution: set free phi vars to 0
    part = {}
    for v in phivars:
        val = sol.get(v, S(0))
        # substitute remaining free vars -> 0
        freevars = [s for s in val.free_symbols if str(s).startswith('phi_')]
        val = val.subs({s: 0 for s in freevars})
        part[v] = simplify(val)

    # VERIFY: delta f_part == gamma on every pair
    ok = True
    mism = 0
    for a in range(D):
        for b in range(a + 1, D):
            df = {c: simplify(v.subs(part)) for c, v in deltaf(a, b).items()}
            df = {c: v for c, v in df.items() if v != 0}
            gm = {c: simplify(v) for c, v in Gamma[(a, b)].items() if simplify(v) != 0}
            comps = set(df) | set(gm)
            for c in comps:
                if simplify(df.get(c, 0) - gm.get(c, 0)) != 0:
                    ok = False; mism += 1
    return S_, phi, part, (ok, mism)


def f_readable(S_, phi, part):
    names = S_['names']
    out = {}
    # group by source generator j: f(Z_j) = sum_i part[phi_ij] Z_i
    D = S_['D']
    for j in range(D):
        terms = {}
        for i in range(D):
            if (i, j) in phi:
                val = part[phi[(i, j)]]
                if val != 0:
                    terms[names[i]] = str(val)
        if terms:
            out[names[j]] = terms
    return out


if __name__ == "__main__":
    import sys
    ns = [int(x) for x in sys.argv[1:]] or [1, 2, 3]
    for n in ns:
        S_, phi, part, status = solve_f(n)
        ok, mism = status
        print(f"n={n}: explicit f found, verification delta f == gamma : {ok} (mismatches {mism})")
        fr = f_readable(S_, phi, part)
        print(f"   explicit trivializing map f (nonzero images), n={n}:")
        for j, terms in fr.items():
            print(f"     f({j}) = " + " + ".join(f"({v})*{i}" for i, v in terms.items()))
        with open(f"../artifacts/explicit_trivializing_f_n{n}.json", "w") as fh:
            json.dump({"n": n, "verified_delta_f_equals_gamma": bool(ok),
                       "f_images": fr,
                       "note": "f(Z_j) = sum_i coeff * Z_i; coeffs are linear in gb params"},
                      fh, indent=1)
        print("   wrote artifact.")
