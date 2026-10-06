"""Verify graded antisymmetry and the super Jacobi identity for data/C_{n}_structure.json.

Usage: python src/verify_C_structure.py [n ...]      (default n = 1 2 3)
Exit code 0 iff every check passes.
"""
import json
import sys
from fractions import Fraction as F
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"


def load_structure(path):
    d = json.load(open(path))
    basis = d["basis"]["even"] + d["basis"]["odd"]
    parity = d["parity"]
    table = {}
    for e in d["structure_constants"]:
        table.setdefault((e["X"], e["Y"]), {})[e["Z"]] = F(e["coeff"])
    return basis, parity, table


def br_vec_basis(table, u, Y):
    """[u, Y} for a vector u = {label: coeff} and basis element Y."""
    out = {}
    for x, c in u.items():
        for z, v in table.get((x, Y), {}).items():
            out[z] = out.get(z, F(0)) + c * v
    return {k: v for k, v in out.items() if v}


def br_basis_vec(table, X, u):
    out = {}
    for y, c in u.items():
        for z, v in table.get((X, y), {}).items():
            out[z] = out.get(z, F(0)) + c * v
    return {k: v for k, v in out.items() if v}


def check_antisymmetry(basis, parity, table):
    bad = []
    for i, X in enumerate(basis):
        for Y in basis[i:]:
            sign = -1 if (parity[X] and parity[Y]) else 1
            lhs = table.get((X, Y), {})
            rhs = {z: -sign * c for z, c in table.get((Y, X), {}).items()}
            if lhs != rhs:
                bad.append((X, Y))
    return bad


def check_jacobi(basis, parity, table, limit_bad=10):
    """[X,[Y,Z]] = [[X,Y],Z] + (-1)^{|X||Y|} [Y,[X,Z]] for all ordered triples."""
    bad, count = [], 0
    for X in basis:
        for Y in basis:
            xy = table.get((X, Y), {})
            sgn = -1 if (parity[X] and parity[Y]) else 1
            for Z in basis:
                count += 1
                lhs = br_basis_vec(table, X, table.get((Y, Z), {}))
                rhs = br_vec_basis(table, xy, Z)
                for k, v in br_basis_vec(table, Y, table.get((X, Z), {})).items():
                    rhs[k] = rhs.get(k, F(0)) + sgn * v
                diff = {k: lhs.get(k, F(0)) - rhs.get(k, F(0)) for k in set(lhs) | set(rhs)}
                if any(diff.values()):
                    if len(bad) < limit_bad:
                        bad.append((X, Y, Z, {k: str(v) for k, v in diff.items() if v}))
    return count, bad


def verify(n, table_override=None):
    basis, parity, table = load_structure(DATA / f"C_{n}_structure.json")
    if table_override is not None:
        table = table_override
    asym_bad = check_antisymmetry(basis, parity, table)
    count, jac_bad = check_jacobi(basis, parity, table)
    return {
        "n": n,
        "dim": len(basis),
        "pairs_checked": len(basis) * (len(basis) + 1) // 2,
        "antisymmetry_failures": len(asym_bad),
        "triples_checked": count,
        "jacobi_failures_shown": jac_bad,
        "passed": not asym_bad and not jac_bad,
    }


def main(argv):
    ns = [int(a) for a in argv] or [1, 2, 3]
    ok = True
    for n in ns:
        r = verify(n)
        status = "PASS" if r["passed"] else "FAIL"
        print(
            f"C(n+1), n={n}: dim={r['dim']}  antisymmetry pairs={r['pairs_checked']} failures={r['antisymmetry_failures']}  "
            f"Jacobi triples={r['triples_checked']} failures={'>=' + str(len(r['jacobi_failures_shown'])) if r['jacobi_failures_shown'] else 0}  -> {status}"
        )
        if not r["passed"]:
            ok = False
            for f in r["jacobi_failures_shown"]:
                print("   Jacobi failure", f)
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
