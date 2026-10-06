"""Triviality search for the inhomogeneous deformation of C(n+1) (Issue I08).

1. Compare Layer 3 (gamma, profile P) with Layer 4 (delta f, profile Q), entry by entry and up to a scalar.
2. List the (X,Y,Z) entries where they differ.
3. Solve delta f = gamma for a *general* odd map f (linear algebra) in three readings:
     A: f: g -> g (+) C K, full gamma (incl. K-component)
     B: f: g -> g,         compare only the g-valued part of gamma
     C: f: g -> g,         compare the full gamma (incl. K-component)
"""
import os
import sys
from fractions import Fraction

import numpy as np

sys.path.insert(0, os.path.dirname(__file__))
import C_coboundary as CB  # noqa: E402
import C_evaluate as EV  # noqa: E402
import C_gamma as GM  # noqa: E402
import C_generators as G  # noqa: E402

K = GM.K_LABEL


def ratio(gam, df):
    """Return lambda with gam = lambda * df, or None. (0 == 0 gives 0 for empty df.)"""
    if not gam and not df:
        return Fraction(0)
    if set(gam) != set(df):
        return None
    lam = None
    for xy in gam:
        if set(gam[xy]) != set(df[xy]):
            return None
        for z in gam[xy]:
            r = gam[xy][z] / df[xy][z]
            if lam is None:
                lam = r
            elif r != lam:
                return None
    return lam


def differences(gam, df):
    diff = []
    for xy in sorted(set(gam) | set(df)):
        for z in sorted(set(gam.get(xy, {})) | set(df.get(xy, {}))):
            a, b = gam.get(xy, {}).get(z, Fraction(0)), df.get(xy, {}).get(z, Fraction(0))
            if a != b:
                diff.append((xy[0], xy[1], z, a, b))
    return diff


def comparison_matrix(n):
    profs = list(EV.profiles(n))
    rows = {}
    for p in profs:
        _, gam, _ = EV.load_evaluated(n, p)
        for q in profs:
            _, _, df = CB.load_coboundary(n, q)
            rows[(p, q)] = (gam == df, ratio(gam, df))
    return profs, rows


def build_operator(n, with_K):
    """Sparse matrix of delta on odd maps. Unknowns: phi[(from, to)], p(from) != p(to) (to may be K).
    Rows: (X, Y, Z). Returns (A, unknowns, row_index)."""
    sc0, _, _ = G.structure_constants(n)
    par = G.parity_map(n)
    labels = G.all_labels(n)
    targets = labels + ([K] if with_K else [])
    pz = dict(par)
    pz[K] = 0
    unknowns = [(zj, zi) for zj in labels for zi in targets if pz[zj] != pz[zi]]
    uidx = {u: i for i, u in enumerate(unknowns)}
    rows, cols, vals = [], [], []
    ridx = {}

    def row(X, Y, Z):
        key = (X, Y, Z)
        if key not in ridx:
            ridx[key] = len(ridx)
        return ridx[key]

    def add(X, Y, Z, u, v):
        if v != 0:
            rows.append(row(X, Y, Z))
            cols.append(uidx[u])
            vals.append(float(v))

    for X in labels:
        for Y in labels:
            s1 = (-1) ** par[X]
            s2 = (-1) ** ((par[X] + 1) * par[Y])
            # (-1)^{pX} [X, f(Y)] : f(Y) = sum_i phi_{iY} Z_i
            for zi in labels:
                if (Y, zi) in uidx:
                    for z, v in sc0.get((X, zi), {}).items():
                        add(X, Y, z, (Y, zi), s1 * v)
                if (X, zi) in uidx:
                    for z, v in sc0.get((Y, zi), {}).items():
                        add(X, Y, z, (X, zi), -s2 * v)
            # - f([X,Y]) : sum_w c_w phi_{iw} Z_i
            for w, v in sc0.get((X, Y), {}).items():
                for zi in targets:
                    if (w, zi) in uidx:
                        add(X, Y, zi, (w, zi), -v)
    return rows, cols, vals, unknowns, ridx, targets


def gamma_vector(gam, ridx, nrows, mask=None):
    b = np.zeros(nrows)
    extra = 0.0
    for (X, Y), d in gam.items():
        for z, v in d.items():
            if mask is not None and not mask(z):
                continue
            if (X, Y, z) in ridx:
                b[ridx[(X, Y, z)]] += float(v)
            else:
                extra += abs(float(v))   # not reachable by delta f at all
    return b, extra


def solve_reading(n, reading):
    with_K = reading == "A"
    rows, cols, vals, unknowns, ridx, targets = build_operator(n, with_K)
    # rows for gamma entries that delta f cannot touch (e.g. K rows in reading B/C) must still be counted
    key_all = {}
    nrow = len(ridx)
    A = np.zeros((nrow, len(unknowns)))
    np.add.at(A, (np.array(rows), np.array(cols)), np.array(vals))
    AtA = A.T @ A
    rank = np.linalg.matrix_rank(AtA)
    out = {"unknowns": len(unknowns), "rank": int(rank), "kernel_dim": len(unknowns) - int(rank), "cases": {}}
    _, lin = GM.load_gamma(n)
    cases = {"all_plus": None}
    for p, vals_ in EV.profiles(n).items():
        cases[p] = vals_
    for key in GM.gb_keys(n):
        cases[f"unit_{GM.gb_name(key)}"] = {GM.gb_name(key): Fraction(1)}
    cases["all_plus"] = EV.profiles(n)["all_plus"]
    for name, gbv in cases.items():
        gam = GM.evaluate(lin, gbv)
        if reading == "B":
            gam = {xy: {z: v for z, v in d.items() if z != K} for xy, d in gam.items()}
            gam = {xy: d for xy, d in gam.items() if d}
        b, extra = gamma_vector(gam, ridx, nrow)
        if name.startswith("zero"):
            continue
        rhs = A.T @ b
        sol = np.linalg.lstsq(AtA, rhs, rcond=None)[0]
        resid = np.abs(A @ sol - b).max() if nrow else 0.0
        out["cases"][name] = max(resid, extra)
    return out


def main():
    for n in (1, 2, 3):
        print(f"===== n={n}: C({n + 1}) =====")
        profs, M = comparison_matrix(n)
        print("Layer3 (rows) vs Layer4 (cols): '=' identical, 'λ' proportional (λ shown), '.' not proportional")
        print(" " * 14 + " ".join(f"{q[:12]:>12}" for q in profs))
        for p in profs:
            cells = []
            for q in profs:
                eq, lam = M[(p, q)]
                cells.append("=" if eq else (f"λ={lam}" if lam is not None else "."))
            print(f"{p:>14}" + " ".join(f"{c:>12}" for c in cells))
        # discrepancy example
        _, gam, _ = EV.load_evaluated(n, "all_plus")
        _, _, df = CB.load_coboundary(n, "alternating")
        diff = differences(gam, df)
        print(f"discrepancies L3[all_plus] vs L4[alternating]: {len(diff)} entries; first 6:")
        for X, Y, Z, a, b in diff[:6]:
            print(f"   ({X}, {Y}) -> {Z}: gamma={a}  delta f={b}")
        for reading in ("A", "B", "C"):
            res = solve_reading(n, reading)
            worst = max(res["cases"].values())
            print(f"reading {reading}: unknowns={res['unknowns']} rank={res['rank']} kernel_dim={res['kernel_dim']} "
                  f"max residual over {len(res['cases'])} gamma cases = {worst:.2e}")
            if reading == "C":
                bad = [k for k, v in res["cases"].items() if v > 1e-8]
                print(f"   unsolvable cases: {len(bad)} of {len(res['cases'])}: {bad[:4]}...")


if __name__ == "__main__":
    main()
