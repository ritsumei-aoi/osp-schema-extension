"""Super-Jacobi check of the undeformed (and gb-deformed, to first order in kappa) structure."""
import sys
from itertools import product
from cn1_triviality import Model


def br(C, x, y):
    out = {}
    for i, ci in x.items():
        for j, cj in y.items():
            for k, v in C.get((i, j), {}).items():
                out[k] = out.get(k, 0) + ci * cj * v
    return out


def jacobi_defect(M, C):
    bad = 0
    d = M.dim
    for a, b, c in product(range(d), repeat=3):
        pa, pb, pc = M.bpar[a], M.bpar[b], M.bpar[c]
        # [a,[b,c]] = [[a,b],c] + (-1)^{pa pb} [b,[a,c]]
        lhs = br(C, {a: 1}, br(C, {b: 1}, {c: 1}))
        r1 = br(C, br(C, {a: 1}, {b: 1}), {c: 1})
        r2 = br(C, {b: 1}, br(C, {a: 1}, {c: 1}))
        keys = set(lhs) | set(r1) | set(r2)
        for k in keys:
            if lhs.get(k, 0) - r1.get(k, 0) - (-1) ** (pa * pb) * r2.get(k, 0) != 0:
                bad += 1
                break
    return bad


if __name__ == "__main__":
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 1
    M = Model(n)
    C = M.structure()
    print("n", n, "jacobi violations:", jacobi_defect(M, C))
    if n == 1:
        for (a, b), d in sorted(C.items()):
            print(M.names[M.basis[a][0]], M.names[M.basis[a][1]], "|", M.names[M.basis[b][0]], M.names[M.basis[b][1]],
                  "->", {(M.names[M.basis[c][0]], M.names[M.basis[c][1]]): str(v) for c, v in d.items()})
