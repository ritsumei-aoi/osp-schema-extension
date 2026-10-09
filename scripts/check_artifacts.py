"""
Independent re-verification that uses ONLY the JSON artifacts
(artifacts/Cn1_triviality_n{n}.json) and the two formulas quoted in the
artifact's "conventions" block.  It does not import the oscillator engine.

Checks, for every gb direction alpha:
   (A)  gamma_alpha(Z_i,Z_j) = (delta f_alpha)(Z_i,Z_j)        (g-valued part, exact)
   (B)  gamma0_alpha(Z_i,Z_j) = - sum_k c_ij^k f''_alpha(Z_k)   (scalar part)
   (C)  d gamma_alpha = 0                                       (cocycle)
   (D)  f_alpha is odd, and the super-Jacobi identity holds for c.
Usage:  python3 scripts/check_artifacts.py [n ...]
"""
import json
import os
import sys
from fractions import Fraction

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def load(n):
    with open(os.path.join(ROOT, "artifacts", f"Cn1_triviality_n{n}.json")) as fh:
        return json.load(fh)


def check(n):
    D = load(n)
    dim, ngb = D["dim"], D["n_gb"]
    p = [b["parity"] for b in D["basis"]]
    c = {}
    for i, j, k, v in D["structure_constants"]:
        c.setdefault((i, j), {})[k] = Fraction(v)
    gamma = [dict() for _ in range(ngb)]
    for i, j, m, a, v in D["gamma_g_part"]:
        gamma[a].setdefault((i, j), {})[m] = Fraction(v)
    gamma0 = [dict() for _ in range(ngb)]
    for i, j, a, v in D["gamma_scalar_part"]:
        gamma0[a][(i, j)] = Fraction(v)
    f = [dict() for _ in range(ngb)]
    for m, i, a, v in D["f_explicit"]["entries"]:
        f[a][(m, i)] = Fraction(v)
    f2 = [dict() for _ in range(ngb)]
    for i, a, v in D["f_explicit"]["scalar_part"]:
        f2[a][i] = Fraction(v)

    def C(i, j):
        return c.get((i, j), {})

    def br(x, y):
        """bracket of vectors x, y (dict index->coeff)."""
        out = {}
        for i, xi in x.items():
            for j, yj in y.items():
                for k, v in C(i, j).items():
                    out[k] = out.get(k, Fraction(0)) + xi * yj * v
        return {k: v for k, v in out.items() if v != 0}

    def sgn(e):
        return -1 if e % 2 else 1

    ok = True
    # (D) super-Jacobi
    for i in range(dim):
        for j in range(dim):
            for k in range(dim):
                acc = {}
                for m, v in br({i: 1}, br({j: 1}, {k: 1})).items():
                    acc[m] = acc.get(m, 0) + v
                for m, v in br(br({i: 1}, {j: 1}), {k: 1}).items():
                    acc[m] = acc.get(m, 0) - v
                for m, v in br({j: 1}, br({i: 1}, {k: 1})).items():
                    acc[m] = acc.get(m, 0) - sgn(p[i] * p[j]) * v
                if any(v != 0 for v in acc.values()):
                    ok = False
    print(f"n={n}: super-Jacobi for structure constants: {ok}")

    for a in range(ngb):
        fa = f[a]
        odd = all(p[m] != p[i] for (m, i) in fa)
        fcol = {}
        for (m, i), v in fa.items():
            fcol.setdefault(i, {})[m] = v

        def F(i):
            return fcol.get(i, {})

        okA = okB = okC = True
        for i in range(dim):
            for j in range(dim):
                # (A)
                acc = {}
                for m, v in br({i: 1}, F(j)).items():
                    acc[m] = acc.get(m, 0) + sgn(p[i]) * v
                for m, v in br({j: 1}, F(i)).items():
                    acc[m] = acc.get(m, 0) - sgn((p[i] + 1) * p[j]) * v
                for k, cc in C(i, j).items():
                    for m, v in F(k).items():
                        acc[m] = acc.get(m, 0) - cc * v
                acc = {m: v for m, v in acc.items() if v != 0}
                if acc != gamma[a].get((i, j), {}):
                    okA = False
                # (B)
                s = -sum((cc * f2[a].get(k, 0) for k, cc in C(i, j).items()), Fraction(0))
                if s != gamma0[a].get((i, j), 0):
                    okB = False
        # (C) cocycle
        G = gamma[a]

        def g(x, y):
            out = {}
            for i, xi in x.items():
                for j, yj in y.items():
                    for m, v in G.get((i, j), {}).items():
                        out[m] = out.get(m, 0) + xi * yj * v
            return out

        for i in range(dim):
            for j in range(dim):
                for k in range(dim):
                    X, Y, Z = {i: 1}, {j: 1}, {k: 1}
                    acc = {}
                    for m, v in g(X, br(Y, Z)).items():
                        acc[m] = acc.get(m, 0) + v
                    for m, v in br(X, g(Y, Z)).items():
                        acc[m] = acc.get(m, 0) + sgn(p[i]) * v
                    for m, v in g(br(X, Y), Z).items():
                        acc[m] = acc.get(m, 0) - v
                    for m, v in br(g(X, Y), Z).items():
                        acc[m] = acc.get(m, 0) - v
                    for m, v in g(Y, br(X, Z)).items():
                        acc[m] = acc.get(m, 0) - sgn(p[i] * p[j]) * v
                    for m, v in br(Y, g(X, Z)).items():
                        acc[m] = acc.get(m, 0) - sgn(p[i] * p[j] + p[j]) * v
                    if any(v != 0 for v in acc.values()):
                        okC = False
        lab = D["gb_parameters"][a]["label"]
        print(f"  gb direction {a} ({lab}): f odd={odd}  (A) gamma=delta f: {okA}  (B) scalar identity: {okB}  (C) cocycle: {okC}")
        ok &= odd and okA and okB and okC
    print(f"n={n}: ALL CHECKS PASSED = {ok}")
    return ok


if __name__ == "__main__":
    ns = [int(x) for x in sys.argv[1:]] or [1, 2, 3]
    res = all(check(n) for n in ns)
    sys.exit(0 if res else 1)
