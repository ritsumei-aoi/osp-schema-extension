#!/usr/bin/env python3
"""
verify_artifacts.py
===================

Independent re-verification that uses ONLY the data stored in the JSON
artifacts (no oscillator algebra, no sympy).  A human researcher can run this
against ``artifacts/cn1_n{n}.json`` to confirm, with exact rational
arithmetic, that

  (A) the structure constants c define a Lie superalgebra of the stated
      dimension (super skew-symmetry + super Jacobi),
  (B) gamma_gb is a 2-cocycle for every gb (first-order super-Jacobi),
  (C) gamma_gb = delta f_gb  for the stored odd map f_gb, for every gb,
      with delta the coboundary of docs/math/C_coboundary_definition.md,
  (D) the stored scalar parts satisfy s1(X,Y) = -lambda([X,Y]) (the part
      that the "up to scalar" clause discards), i.e. Gamma = delta(-F) in Q,
  (E) gamma_gb != 0 for every nonzero gb (the map gb -> gamma_gb is injective).

Run:  python3 scripts/verify_artifacts.py artifacts/cn1_n1.json artifacts/cn1_n2.json artifacts/cn1_n3.json
"""
import json
import sys
from fractions import Fraction


def lin(d):
    """{'gb[..]': '1/2', ...} -> {label: Fraction}"""
    return {k: Fraction(v) for k, v in d.items()}


def lin_add(a, b, c=1):
    out = dict(a)
    for k, v in b.items():
        nv = out.get(k, Fraction(0)) + c * v
        if nv == 0:
            out.pop(k, None)
        else:
            out[k] = nv
    return out


def verify(path):
    data = json.load(open(path))
    n, d = data["n"], data["dim"]["total"]
    P = [b["parity"] for b in data["basis"]]
    gb_labels = data["conventions"]["gb_parameters"]
    c = {}
    for e in data["structure_constants"]:
        c[(e["i"], e["j"], e["k"])] = Fraction(e["value"])
    gamma = {}
    for e in data["gamma_gb"]:
        gamma[(e["i"], e["j"], e["k"])] = lin(e["value"])
    s1 = {(e["i"], e["j"]): lin(e["value"]) for e in data["scalar_part_s1"]}
    f = {(e["m"], e["j"]): lin(e["phi_mj"]) for e in data["f_gb"]}
    lam = {e["j"]: lin(e["value"]) for e in data["lambda_gb"]}
    report = {"file": path, "n": n, "dim": d}

    def cvec(i, j):
        return {k: v for (ii, jj, k), v in c.items() if ii == i and jj == j}

    C = [[cvec(i, j) for j in range(d)] for i in range(d)]
    G = [[{k: v for (ii, jj, k), v in gamma.items() if ii == i and jj == j} for j in range(d)] for i in range(d)]

    # (A) Lie superalgebra axioms
    ok_skew = True
    for i in range(d):
        for j in range(d):
            sgn = -1 if (P[i] and P[j]) else 1
            for k in range(d):
                if C[i][j].get(k, 0) + sgn * C[j][i].get(k, 0) != 0:
                    ok_skew = False
    ok_jac = True
    for i in range(d):
        for j in range(d):
            for k in range(d):
                acc = {}
                # [Z_i,[Z_j,Z_k]]
                for m, v in C[j][k].items():
                    for l, w in C[i][m].items():
                        acc[l] = acc.get(l, 0) + v * w
                # -[[Z_i,Z_j],Z_k]
                for m, v in C[i][j].items():
                    for l, w in C[m][k].items():
                        acc[l] = acc.get(l, 0) - v * w
                # -(-1)^{p_i p_j}[Z_j,[Z_i,Z_k]]
                sgn = -1 if (P[i] and P[j]) else 1
                for m, v in C[i][k].items():
                    for l, w in C[j][m].items():
                        acc[l] = acc.get(l, 0) - sgn * v * w
                if any(x != 0 for x in acc.values()):
                    ok_jac = False
    report["A_super_skew"] = ok_skew
    report["A_super_jacobi"] = ok_jac
    # parity consistency of c and gamma
    report["A_c_parity_ok"] = all(P[k] == (P[i] + P[j]) % 2 for (i, j, k) in c)
    report["B_gamma_parity_odd"] = all(P[k] == (P[i] + P[j] + 1) % 2 for (i, j, k) in gamma)

    # (B) cocycle condition, with gb symbolic (dict-valued linear forms)
    ok_coc = True
    for i in range(d):
        for j in range(d):
            for k in range(d):
                acc = {}
                # [Z_i,[Z_j,Z_k]] first order: gamma(Z_i,[Z_j,Z_k]_0) + (-1)^{p_i}[Z_i, gamma(Z_j,Z_k)]
                for m, v in C[j][k].items():
                    for l, w in G[i][m].items():
                        acc[l] = lin_add(acc.get(l, {}), w, v)
                s = -1 if P[i] else 1
                for m, w in G[j][k].items():
                    for l, v in C[i][m].items():
                        acc[l] = lin_add(acc.get(l, {}), w, s * v)
                # -[[Z_i,Z_j],Z_k]: gamma([Z_i,Z_j]_0, Z_k) + [gamma(Z_i,Z_j), Z_k]
                for m, v in C[i][j].items():
                    for l, w in G[m][k].items():
                        acc[l] = lin_add(acc.get(l, {}), w, -v)
                for m, w in G[i][j].items():
                    for l, v in C[m][k].items():
                        acc[l] = lin_add(acc.get(l, {}), w, -v)
                # -(-1)^{p_i p_j}[Z_j,[Z_i,Z_k]]
                sgn = -1 if (P[i] and P[j]) else 1
                for m, v in C[i][k].items():
                    for l, w in G[j][m].items():
                        acc[l] = lin_add(acc.get(l, {}), w, -sgn * v)
                s = -1 if P[j] else 1
                for m, w in G[i][k].items():
                    for l, v in C[j][m].items():
                        acc[l] = lin_add(acc.get(l, {}), w, -sgn * s * v)
                if any(acc[l] for l in acc):
                    ok_coc = False
    report["B_gamma_is_cocycle"] = ok_coc

    # (C) gamma = delta f  and (D) scalar parts
    F = [[f.get((m, j), {}) for j in range(d)] for m in range(d)]
    report["C_f_is_odd"] = all(P[m] != P[j] for (m, j) in f)
    ok_cob, ok_scal = True, True
    for i in range(d):
        for j in range(d):
            vec = {}
            s = -1 if P[i] else 1
            for m in range(d):
                if F[m][j]:
                    for k, v in C[i][m].items():
                        vec[k] = lin_add(vec.get(k, {}), F[m][j], s * v)
            s = -1 if ((P[i] + 1) * P[j]) % 2 else 1
            for m in range(d):
                if F[m][i]:
                    for k, v in C[j][m].items():
                        vec[k] = lin_add(vec.get(k, {}), F[m][i], -s * v)
            scal = {}
            for l, v in C[i][j].items():
                for m in range(d):
                    if F[m][l]:
                        vec[m] = lin_add(vec.get(m, {}), F[m][l], -v)
                if l in lam:
                    scal = lin_add(scal, lam[l], -v)
            for k in range(d):
                if lin_add(vec.get(k, {}), G[i][j].get(k, {}), -1):
                    ok_cob = False
            if lin_add(scal, s1.get((i, j), {}), -1):
                ok_scal = False
    report["C_gamma_equals_delta_f"] = ok_cob
    report["D_scalar_parts_equal_minus_lambda_of_bracket"] = ok_scal

    # (E) injectivity of gb -> gamma  (rank over Q by elimination)
    rows = []
    for lab in gb_labels:
        row = {}
        for (i, j, k), form in gamma.items():
            if lab in form:
                row[(i, j, k)] = form[lab]
        rows.append(row)
    rank = 0
    pivots = {}
    for row in rows:
        row = dict(row)
        changed = True
        while changed and row:
            changed = False
            for pc, prow in pivots.items():
                if pc in row:
                    fct = row[pc]
                    for cc, vv in prow.items():
                        nv = row.get(cc, 0) - fct * vv
                        if nv == 0:
                            row.pop(cc, None)
                        else:
                            row[cc] = nv
                    changed = True
        if row:
            pc = min(row)
            inv = 1 / row[pc]
            pivots[pc] = {cc: vv * inv for cc, vv in row.items()}
            rank += 1
    report["E_rank_gb_to_gamma"] = rank
    report["E_injective"] = rank == len(gb_labels) == 4 * n
    report["ALL_OK"] = all(v for k, v in report.items() if isinstance(v, bool))
    return report


if __name__ == "__main__":
    paths = sys.argv[1:] or [f"artifacts/cn1_n{n}.json" for n in (1, 2, 3)]
    all_ok = True
    for p in paths:
        r = verify(p)
        all_ok &= r["ALL_OK"]
        print(json.dumps(r, indent=1))
    print("ALL ARTIFACTS VERIFIED" if all_ok else "VERIFICATION FAILED")
    sys.exit(0 if all_ok else 1)
