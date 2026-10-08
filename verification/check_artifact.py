"""
Independent re-verification from the JSON artifacts alone (no oscillator
algebra involved).  Usage:

    python3 verification/check_artifact.py artifacts/C2_osp2_2.json [...]

For each artifact it reads the structure constants C, the cochain gamma
(linear in gb) and the explicit odd map f (linear in gb), picks random
integer values for gb, and checks with exact rational arithmetic that

    gamma(Z_a, Z_b) = (-1)^{p_a}[Z_a, f Z_b] - (-1)^{(p_a+1)p_b}[Z_b, f Z_a] - f([Z_a, Z_b])

holds for every pair (a, b), both for the g-part and for the scalar part
(scalar part of f contributes -f_0([Z_a,Z_b]) to the scalar part of delta f).
It also checks the super-Jacobi identity of C and that f is odd.
"""
import json
import random
import sys
from fractions import Fraction


def evaluate(poly: dict, gbval: dict) -> Fraction:
    tot = Fraction(0)
    for k, v in poly.items():
        tot += Fraction(v) * (Fraction(1) if k == "1" else gbval[k])
    return tot


def check(path: str, trials: int = 3, seed: int = 1) -> bool:
    art = json.load(open(path))
    d, par = art["dim"], art["parity"]
    gbn = art["gb_parameters"]
    C = {}
    for a, b, c, q in art["structure_constants"]:
        C.setdefault((a, b), {})[c] = Fraction(q)

    def br(u, v):  # bracket of coefficient vectors
        out = [Fraction(0)] * d
        for a, ua in enumerate(u):
            if ua == 0:
                continue
            for b, vb in enumerate(v):
                if vb == 0:
                    continue
                for c, q in C.get((a, b), {}).items():
                    out[c] += ua * vb * q
        return out

    # super-Jacobi of C
    jac_ok = True
    E = [[Fraction(int(i == j)) for j in range(d)] for i in range(d)]
    for a in range(d):
        for b in range(d):
            ab = br(E[a], E[b])
            for c in range(d):
                lhs = br(E[a], br(E[b], E[c]))
                r1 = br(ab, E[c])
                s = -1 if (par[a] * par[b]) % 2 else 1
                r2 = [s * x for x in br(E[b], br(E[a], E[c]))]
                if any(lhs[i] - r1[i] - r2[i] != 0 for i in range(d)):
                    jac_ok = False
    rng = random.Random(seed)
    all_ok = jac_ok
    for _ in range(trials):
        gbval = {name: Fraction(rng.randint(-7, 7)) for name in gbn}
        G = {}
        for a, b, c, poly in art["gamma"]:
            G[(a, b, c)] = evaluate(poly, gbval)
        G0 = {}
        for a, b, poly in art["gamma_scalar"]:
            G0[(a, b)] = evaluate(poly, gbval)
        F = [[Fraction(0)] * d for _ in range(d)]  # F[j] = coefficient vector of f(Z_j)
        for i, j, poly in art["explicit_f_phi"]:
            F[j][i] = evaluate(poly, gbval)
        F0 = [Fraction(0)] * d
        for j, poly in art["explicit_f_phi_scalar"]:
            F0[j] = evaluate(poly, gbval)
        odd_ok = all(F[j][i] == 0 for j in range(d) for i in range(d) if par[i] == par[j])
        ok = odd_ok
        for a in range(d):
            for b in range(d):
                pa, pb = par[a], par[b]
                s1 = -1 if pa else 1
                s2 = -(-1 if ((pa + 1) * pb) % 2 else 1)
                t1 = br(E[a], F[b])
                t2 = br(E[b], F[a])
                vec = [s1 * t1[i] + s2 * t2[i] for i in range(d)]
                sc = Fraction(0)
                for c, q in C.get((a, b), {}).items():
                    for i in range(d):
                        vec[i] -= q * F[c][i]
                    sc -= q * F0[c]
                for c in range(d):
                    if vec[c] != G.get((a, b, c), Fraction(0)):
                        ok = False
                if sc != G0.get((a, b), Fraction(0)):
                    ok = False
        all_ok &= ok
    print(f"{path}: {art['algebra']}  dim={d}  jacobi={jac_ok}  gamma==delta(f) for {trials} random gb: {all_ok}")
    return all_ok


if __name__ == "__main__":
    paths = sys.argv[1:] or [f"artifacts/C{n+1}_osp2_{2*n}.json" for n in (1, 2, 3)]
    ok = all(check(p) for p in paths)
    sys.exit(0 if ok else 1)
