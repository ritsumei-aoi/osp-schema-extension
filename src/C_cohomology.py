"""Additional investigation (I08): dimension of odd 2-cocycles Z^2 and coboundaries B^2 of C(n+1).

Odd g-valued 2-cochains c (p(c(X,Y)) = p(X)+p(Y)+1, graded antisymmetric). Cocycle condition =
kappa-part of super Jacobi for [,]_0 + kappa c:
    sum_cyc (-1)^{p(A)p(C)} ( c(A,[B,C]_0) + (-1)^{p(A)} [A, c(B,C)]_0 ) = 0.
dim H^2_odd = dim Z^2 - rank(delta) (rank of delta from data/C_{n}_triviality.json, reading mod_K).

Usage: python3 src/C_cohomology.py [n ...]
"""
import json
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from C_coboundary import load_sc  # noqa: E402
from C_generators import DATA_DIR  # noqa: E402
from C_triviality import SparseSolver  # noqa: E402


def cocycle_dimensions(n):
    basis, par, sc = load_sc(n)
    idx = {x: i for i, x in enumerate(basis)}
    var = {}
    for X in basis:
        for Y in basis:
            if idx[X] > idx[Y] or (X == Y and par[X] == 0):
                continue
            for W in basis:
                if par[W] == (par[X] + par[Y] + 1) % 2:
                    var[(X, Y, W)] = len(var)

    def c_of(U, V):
        """c(U,V) as {W: {var: coeff}}."""
        if idx[U] <= idx[V]:
            key, s = (U, V), 1
        else:
            key, s = (V, U), -(-1 if (par[U] and par[V]) else 1)
        if key[0] == key[1] and par[U] == 0:
            return {}
        return {W: {var[key + (W,)]: s} for W in basis if key + (W,) in var}

    solver = SparseSolver(0)
    for a in range(len(basis)):
        for b in range(a, len(basis)):
            for cc in range(b, len(basis)):
                A, B, C = basis[a], basis[b], basis[cc]
                rows = {}
                for P, Q, R in ((A, B, C), (B, C, A), (C, A, B)):
                    sJ = -1 if (par[P] and par[R]) else 1
                    for V, k in sc.get((Q, R), {}).items():          # c(P, [Q,R]_0)
                        for W, lin in c_of(P, V).items():
                            for v, x in lin.items():
                                rows.setdefault(W, {})
                                rows[W][v] = rows[W].get(v, 0) + sJ * k * x
                    sP = -1 if par[P] else 1
                    for U, lin in c_of(Q, R).items():                # (-1)^{p(P)} [P, c(Q,R)]_0
                        for W, k in sc.get((P, U), {}).items():
                            for v, x in lin.items():
                                rows.setdefault(W, {})
                                rows[W][v] = rows[W].get(v, 0) + sJ * sP * k * x
                for W, row in rows.items():
                    solver.add_row(row, [])
    return len(var), solver.rank()


def main(ns):
    for n in ns:
        t = time.time()
        nvar, rk = cocycle_dimensions(n)
        with open(os.path.join(DATA_DIR, f"C_{n}_triviality.json")) as f:
            rank_delta = json.load(f)["readings"]["mod_K"]["rank"]
        z = nvar - rk
        print(f"n={n}: odd cochains={nvar}, rank(cocycle eqs)={rk}, dim Z^2_odd={z}, "
              f"dim B^2_odd={rank_delta}, dim H^2_odd={z - rank_delta}  ({time.time() - t:.1f}s)")


if __name__ == "__main__":
    main([int(a) for a in sys.argv[1:]] or [1, 2])
