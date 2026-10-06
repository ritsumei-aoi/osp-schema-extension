"""Control / validation of the coboundary solver.

We build a GENERAL target-cochain solver:  given a 2-cochain T (parity-odd,
g-valued), decide whether T = delta f for some odd linear f, by linear algebra
on the same delta map used in analyze.triviality.

Validation 1 (MUST be solvable): T = delta f0 for a random odd f0.
Validation 2 (independent image dim): dim(im delta) via rank, and check
           Euler identity dim(im) = P - dim(ker delta).
Then we re-examine gamma_gb against im(delta).
"""
import random
from sympy import S, zeros, Matrix, simplify, Rational
from analyze import build_structures


def delta_columns(S_):
    """Return (phi_cols, cochain_index, Dmat) where Dmat is the matrix of the
       delta map: columns = phi variables, rows = cochain coordinates (pair a<b,
       component c). Also returns function to coordinate-ize a target cochain."""
    C, parity, D = S_['C'], S_['parity'], S_['D']
    phi_cols = {}
    for j in range(D):
        for i in range(D):
            if parity[i] != parity[j]:
                phi_cols[(i, j)] = len(phi_cols)
    P = len(phi_cols)

    # enumerate cochain coordinates lazily: dict (a,b,c)->rowindex
    coch_idx = {}
    entries = {}  # (row, col) -> coeff

    def rowid(a, b, c):
        key = (a, b, c)
        if key not in coch_idx:
            coch_idx[key] = len(coch_idx)
        return coch_idx[key]

    for a in range(D):
        for b in range(a + 1, D):
            pa, pb = parity[a], parity[b]
            s1 = (-1) ** pa
            for i in range(D):
                if (i, b) in phi_cols:
                    col = phi_cols[(i, b)]
                    for c, cc in C[(a, i)].items():
                        entries[(rowid(a, b, c), col)] = entries.get((rowid(a, b, c), col), 0) + s1 * cc
            s2 = -((-1) ** ((pa + 1) * pb))
            for i in range(D):
                if (i, a) in phi_cols:
                    col = phi_cols[(i, a)]
                    for c, cc in C[(b, i)].items():
                        entries[(rowid(a, b, c), col)] = entries.get((rowid(a, b, c), col), 0) + s2 * cc
            for d, cab in C[(a, b)].items():
                for i in range(D):
                    if (i, d) in phi_cols:
                        col = phi_cols[(i, d)]
                        entries[(rowid(a, b, i), col)] = entries.get((rowid(a, b, i), col), 0) - cab
    R = len(coch_idx)
    Dmat = zeros(R, P)
    for (r, col), v in entries.items():
        Dmat[r, col] = S(v)
    return phi_cols, coch_idx, Dmat, P, R


def cochain_vec(T, coch_idx, R):
    v = zeros(R, 1)
    for (a, b, c), val in T.items():
        if (a, b, c) in coch_idx:
            v[coch_idx[(a, b, c)]] = S(val)
        elif val != 0:
            return None  # component outside delta's row space -> definitely not in image here
    return v


def delta_of_f(S_, fmap):
    """Compute delta f as cochain dict (a,b,c)->value for explicit fmap[(i,j)]=val."""
    C, parity, D = S_['C'], S_['parity'], S_['D']
    out = {}
    def add(a, b, c, v):
        out[(a, b, c)] = out.get((a, b, c), 0) + v
    def f_of(j):
        return [(i, val) for (i, jj), val in fmap.items() if jj == j]
    for a in range(D):
        for b in range(a + 1, D):
            pa, pb = parity[a], parity[b]
            s1 = (-1) ** pa
            for i, val in f_of(b):
                for c, cc in C[(a, i)].items():
                    add(a, b, c, s1 * val * cc)
            s2 = -((-1) ** ((pa + 1) * pb))
            for i, val in f_of(a):
                for c, cc in C[(b, i)].items():
                    add(a, b, c, s2 * val * cc)
            for d, cab in C[(a, b)].items():
                for i, val in f_of(d):
                    add(a, b, i, -cab * val)
    return {k: v for k, v in out.items() if simplify(v) != 0}


def in_image(Dmat, target_vec):
    """Is target_vec in column space of Dmat? Compare ranks."""
    r0 = Dmat.rank()
    aug = Dmat.row_join(target_vec)
    r1 = aug.rank()
    return r0 == r1, r0


def main(n):
    print(f"\n==== control tests n={n} ====")
    S_ = build_structures(n)
    parity, D = S_['parity'], S_['D']
    phi_cols, coch_idx, Dmat, P, R = delta_columns(S_)
    print(f"phi vars P={P}, cochain coords R={R}")
    im = Dmat.rank()
    ker = P - im
    print(f"dim im(delta)={im}, dim ker(delta)={ker}")

    # Validation 1: random coboundary must be in image
    random.seed(3)
    fmap = {}
    for (i, j) in phi_cols:
        if random.random() < 0.5:
            fmap[(i, j)] = Rational(random.randint(-3, 3))
    T = delta_of_f(S_, fmap)
    tv = cochain_vec(T, coch_idx, R)
    ok, _ = in_image(Dmat, tv) if tv is not None else (False, None)
    print(f"VALIDATION 1 (random delta f0 in image): {ok}  (expected True)")

    # Validation 2: gamma_gb for each pure gb direction - is it in image?
    import itertools
    Gamma = S_['Gamma']; gb_syms = S_['gb_syms']; gb_keys = S_['gb_keys']
    # build gamma cochain per gb basis direction
    results = {}
    for t, key in enumerate(gb_keys):
        sym = gb_syms[t]
        T = {}
        for (a, b), comp in Gamma.items():
            if a < b:
                for c, expr in comp.items():
                    k = expr.coeff(sym)
                    if k != 0:
                        T[(a, b, c)] = T.get((a, b, c), 0) + k
        tv = cochain_vec(T, coch_idx, R)
        if tv is None:
            results[key] = "outside-rowspace(nontrivial)"
            continue
        ok, _ = in_image(Dmat, tv)
        results[key] = "TRIVIAL(in image)" if ok else "NONTRIVIAL"
    print("per-direction gamma_gb:")
    for k, v in results.items():
        print(f"   gb_{k[0]}{k[1]}{k[2]}: {v}")

    # General: is a generic combination in image? check rank of [Dmat | all gamma dirs]
    cols = []
    for t, key in enumerate(gb_keys):
        sym = gb_syms[t]
        T = {}
        for (a, b), comp in Gamma.items():
            if a < b:
                for c, expr in comp.items():
                    k = expr.coeff(sym)
                    if k != 0:
                        T[(a, b, c)] = T.get((a, b, c), 0) + k
        v = cochain_vec(T, coch_idx, R)
        if v is None:
            v = None
        cols.append(v)
    # number of gamma directions lying in image = dim(im ∩ gamma-space)
    base = Dmat.rank()
    aug = Dmat
    added = 0
    for v in cols:
        if v is None:
            continue
        test = aug.row_join(v)
        if test.rank() > aug.rank():
            aug = test
            added += 1
    triv = len(cols) - added
    print(f"gamma directions in image(delta) = {triv} / {len(cols)}  "
          f"(trivializable dim); nontrivial = {added}")
    return S_, Dmat, coch_idx


if __name__ == "__main__":
    main(1)
