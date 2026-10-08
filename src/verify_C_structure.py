"""Verify the Schema 1 structure constants of C(n+1) (I04).

This is an independent check of data/C_{n}_structure.json. It does NOT use the
bracket table stored in the file as its source of truth. Instead it:

1. Reads the oscillator words of `generator_realization` (the content the
   generator asserts), and recomputes every ordered bracket [X, Y} from them
   with its own normal-ordering routine (not imported from C_generators.py).
2. Compares the recomputed brackets with the stored `structure_constants`.
3. Checks antisymmetry on all ordered pairs:
       [X, Y} = -(-1)^(p(X) p(Y)) [Y, X}
   using the recomputed brackets in both orders.
4. Checks the super Jacobi identity on all triples of basis elements:
       (-1)^(p(X) p(Z)) [X,[Y,Z}} + (-1)^(p(Y) p(X)) [Y,[Z,X}}
         + (-1)^(p(Z) p(Y)) [Z,[X,Y}} = 0.

Usage:  python3 -I src/verify_C_structure.py [n ...]   (default n = 1 2 3)
Exit status is 0 only if every check passes for every requested n.
"""

import itertools
import json
import sys
from fractions import Fraction
from pathlib import Path

import sympy


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"


def load(n):
    return json.loads((DATA / f"C_{n}_structure.json").read_text())


class Normal:
    """Normal ordering of words in fermions (CAR) and bosons (CCR).

    Symbols are ordered by their position in `order` (fermions first). A word is
    sorted by repeatedly applying one swap rule at the first inversion:
      fermions:  x y = -y x + {x, y}    with {a_1_m, a_1_p} = 1, {a, a} = 0
      bosons:    x y =  y x + [x, y]    with [b_k_m, b_k_p] = 1, other pairs 0
      mixed:     x y =  y x
    """

    def __init__(self, order):
        self.order = {s: i for i, s in enumerate(order)}
        self.cache = {}

    def fermion(self, s):
        return s.startswith("a_")

    def contraction(self, x, y):
        if self.fermion(x) and self.fermion(y):
            return Fraction(1) if {x, y} == {"a_1_p", "a_1_m"} else Fraction(0)
        if self.fermion(x) or self.fermion(y):
            return Fraction(0)
        if x.split("_")[1] != y.split("_")[1]:
            return Fraction(0)
        if x.endswith("_m") and y.endswith("_p"):
            return Fraction(1)
        if x.endswith("_p") and y.endswith("_m"):
            return Fraction(-1)
        return Fraction(0)

    def word(self, w):
        if w in self.cache:
            return self.cache[w]
        result = None
        for i in range(len(w) - 1):
            x, y = w[i], w[i + 1]
            if x == y and self.fermion(x):
                result = {}
                break
            if self.order[x] > self.order[y]:
                result = {}
                sign = -1 if (self.fermion(x) and self.fermion(y)) else 1
                for u, c in self.word(w[:i] + (y, x) + w[i + 2:]).items():
                    result[u] = result.get(u, 0) + sign * c
                c0 = self.contraction(x, y)
                if c0:
                    for u, c in self.word(w[:i] + w[i + 2:]).items():
                        result[u] = result.get(u, 0) + c0 * c
                break
        if result is None:
            result = {w: Fraction(1)}
        result = {u: c for u, c in result.items() if c != 0}
        self.cache[w] = result
        return result

    def poly(self, p):
        out = {}
        for w, c in p.items():
            for u, d in self.word(w).items():
                out[u] = out.get(u, 0) + c * d
        return {u: c for u, c in out.items() if c != 0}


def mul(norm, A, B):
    p = {}
    for wa, ca in A.items():
        for wb, cb in B.items():
            p[wa + wb] = p.get(wa + wb, 0) + ca * cb
    return norm.poly(p)


def graded(norm, A, pA, B, pB):
    sign = -1 if (pA * pB) % 2 else 1
    out = dict(mul(norm, A, B))
    for w, c in mul(norm, B, A).items():
        out[w] = out.get(w, 0) - sign * c
    return {w: c for w, c in out.items() if c != 0}


def check(n):
    data = load(n)
    # PBW order from handover/notation.md: odd block first, then even block.
    labels = data["basis"]["odd"] + data["basis"]["even"]
    parity = data["parity"]
    real = data["generator_realization"]

    # Symbol order: fermions first, then bosons in file order.
    order = ["a_1_p", "a_1_m"] + data["oscillator_generators"]["bosons"]["labels"]
    norm = Normal(order)

    polys = {}
    for l in labels:
        p = {}
        for term in real[l]["standard_form"]:
            p[tuple(term["words"])] = Fraction(term["coeff"])
        polys[l] = norm.poly(p)

    # Column space for solving [X,Y} in the basis: basis elements plus K.
    cols = labels + ["K"]
    monomials = sorted({m for p in polys.values() for m in p} | {()})
    polys_all = dict(polys, K={(): Fraction(1)})

    def q(x):
        return sympy.Rational(x.numerator, x.denominator)

    A = sympy.Matrix([[q(polys_all[c].get(m, Fraction(0))) for c in cols] for m in monomials])

    def to_basis(poly):
        rhs = sympy.Matrix([q(poly.get(m, Fraction(0))) for m in monomials])
        sol, params = A.gauss_jordan_solve(rhs)
        assert not params, "basis not unique"
        return {c: Fraction(int(s.p), int(s.q)) for c, s in zip(cols, sol) if s != 0}

    # Recompute the full ordered bracket table from the oscillator realization.
    table = {}
    failures = []
    for X, Y in itertools.product(labels, repeat=2):
        comm = graded(norm, polys[X], parity[X], polys[Y], parity[Y])
        table[(X, Y)] = to_basis(comm) if comm else {}
        if "K" in table[(X, Y)]:
            failures.append(f"central term K appears in [{X},{Y}]")

    # (a) Stored structure constants agree with the recomputed ones (X before Y).
    stored = {}
    for e in data["structure_constants"]:
        stored.setdefault((e["X"], e["Y"]), {})[e["Z"]] = Fraction(e["coeff"])
    for (X, Y), terms in stored.items():
        if table[(X, Y)] != terms:
            failures.append(f"stored [{X},{Y}] = {terms} but recomputed {table[(X, Y)]}")
    for (X, Y), terms in table.items():
        if terms and (X, Y) not in stored and labels.index(X) <= labels.index(Y):
            failures.append(f"recomputed [{X},{Y}] = {terms} missing from file")

    # (b) Antisymmetry on all ordered pairs, both orientations recomputed.
    n_anti = 0
    for X, Y in itertools.product(labels, repeat=2):
        sign = -1 if (parity[X] * parity[Y]) % 2 else 1
        lhs = table[(X, Y)]
        rhs = {z: -sign * c for z, c in table[(Y, X)].items()}
        n_anti += 1
        if {z: c for z, c in lhs.items() if c} != {z: c for z, c in rhs.items() if c}:
            failures.append(f"antisymmetry fails for ({X},{Y}): {lhs} vs {rhs}")

    # (c) Super Jacobi on all triples (X, Y, Z) of basis elements.
    n_jac = 0
    for X, Y, Z in itertools.product(labels, repeat=3):
        pX, pY, pZ = parity[X], parity[Y], parity[Z]
        total = {}
        for coeff, (a, b, c) in [
            ((-1) ** (pX * pZ), (X, Y, Z)),
            ((-1) ** (pY * pX), (Y, Z, X)),
            ((-1) ** (pZ * pY), (Z, X, Y)),
        ]:
            # [a, [b, c}} with [b, c} computed from the table.
            inner = table[(b, c)]
            for z, cz in inner.items():
                if z == "K":  # already reported above
                    continue
                for w, cw in table[(a, z)].items():
                    total[w] = total.get(w, 0) + coeff * cz * cw
        n_jac += 1
        nz = {w: c for w, c in total.items() if c != 0}
        if nz:
            failures.append(f"Jacobi fails for ({X},{Y},{Z}): {nz}")
            if len(failures) > 20:
                break

    return {
        "n": n,
        "basis": len(labels),
        "antisymmetry_pairs": n_anti,
        "jacobi_triples": n_jac,
        "failures": failures,
    }


def main(argv):
    ns = [int(a) for a in argv] or [1, 2, 3]
    all_ok = True
    for n in ns:
        r = check(n)
        ok = not r["failures"]
        all_ok &= ok
        print(
            f"C(n={n}) basis={r['basis']}: antisymmetry pairs={r['antisymmetry_pairs']}, "
            f"Jacobi triples={r['jacobi_triples']}, "
            f"{'PASS' if ok else 'FAIL'} ({len(r['failures'])} failures)"
        )
        for f in r["failures"][:10]:
            print("   ", f)
    return 0 if all_ok else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
