"""
I08: triviality search for the inhomogeneous deformation of C(n+1).

Parts
  A. Layer 3 (evaluated gamma) vs Layer 4 (delta f) comparison, per gb profile, from the JSON files.
  B. Independent solve: is gamma^{(sigma,k,s)} (unit gb direction) in the image of the generic
     coboundary operator delta_1 : C^1_odd -> C^2_odd ?  Exact rational sparse elimination;
     rank(delta_1), dim ker(delta_1), consistency for each of the 4n directions and each profile.
  C. delta_2 ∘ delta_1 = 0 (the cocycle identity of I05 applied to every elementary coboundary).
  D. K-retained check: does gamma = -delta f hold including the dropped constant (K) terms?
  E. Weight analysis: weight of each gamma^{(sigma,k,s)} w.r.t. the Cartan subalgebra, the
     Cartan-homotopy trivialisation f_h = gamma(h,.)/lambda(h), and the exact dimension of the
     weight-zero odd 2-cocycles Z^2_{odd,0} = H^2_odd(g,g) (the only place non-trivial odd
     deformations could live).

Usage:  python src/C_triviality.py [n ...]        (writes docs/triviality_report_data.json)
"""
from __future__ import annotations

import json
import os
import random
import sys
from fractions import Fraction
from typing import Dict, List, Tuple

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from C_coboundary import canonical_f, coboundary, delta_f_pair  # noqa: E402
from C_evaluate import PROFILES, eval_linear_form, profile_values  # noqa: E402
from C_gamma import cocycle_defect, compute_gamma, gb_labels  # noqa: E402
from C_generators import DATA_DIR, REPO_ROOT, parity_of, realization_words  # noqa: E402
from oscillator import LinPoly  # noqa: E402
from verify_C_structure import BracketTable  # noqa: E402


# --------------------------------------------------------------------------- #
# Sparse exact linear algebra
# --------------------------------------------------------------------------- #
class SparseEchelon:
    """Incremental row-echelon form over Q with rows stored as {col: Fraction}."""

    def __init__(self):
        self.pivots: Dict[int, Dict[int, Fraction]] = {}  # pivot col -> row (normalised, pivot = 1)
        self.order: List[int] = []

    def reduce(self, row: Dict[int, Fraction]) -> Dict[int, Fraction]:
        row = dict(row)
        changed = True
        while changed:
            changed = False
            for c in sorted(row):
                if c in self.pivots and row.get(c, 0) != 0:
                    f = row[c]
                    for cc, v in self.pivots[c].items():
                        nv = row.get(cc, Fraction(0)) - f * v
                        if nv == 0:
                            row.pop(cc, None)
                        else:
                            row[cc] = nv
                    changed = True
                    break
        return row

    def add(self, row: Dict[int, Fraction]) -> bool:
        """Insert a row, keeping the system fully reduced (RREF): every pivot column appears in
        exactly one stored row."""
        row = self.reduce(row)
        if not row:
            return False
        c = min(row)
        pv = row[c]
        new = {cc: v / pv for cc, v in row.items()}
        for pc, prow in self.pivots.items():
            if c in prow:
                f = prow[c]
                for cc, v in new.items():
                    nv = prow.get(cc, Fraction(0)) - f * v
                    if nv == 0:
                        prow.pop(cc, None)
                    else:
                        prow[cc] = nv
        self.pivots[c] = new
        self.order.append(c)
        return True

    @property
    def rank(self):
        return len(self.pivots)


def solve_sparse(rows: List[Dict[int, Fraction]], ncols: int, rhs_list: List[Dict[int, Fraction]]):
    """Solve A phi = b for several right-hand sides.  rows[i] = {col: val};  rhs_list[r] = {rowindex: val}.
    Returns (rank, consistent[r], solution[r] (dict col->val, free vars = 0))."""
    ech = SparseEchelon()
    nr = len(rhs_list)
    for i, row in enumerate(rows):
        aug = dict(row)
        for r, rhs in enumerate(rhs_list):
            if i in rhs and rhs[i] != 0:
                aug[ncols + r] = rhs[i]
        ech.add(aug)
    rank = sum(1 for c in ech.pivots if c < ncols)
    # a pivot row whose pivot column is >= ncols has zero phi-part: every rhs it touches is inconsistent
    consistent = [True] * nr
    for c, prow in ech.pivots.items():
        if c >= ncols:
            for cc in prow:
                if cc >= ncols:
                    consistent[cc - ncols] = False
    # RREF: each pivot row = pivot + free columns (+ rhs columns); free variables := 0
    sols = []
    for r in range(nr):
        if not consistent[r]:
            sols.append(None)
            continue
        sol: Dict[int, Fraction] = {}
        for c, prow in ech.pivots.items():
            if c < ncols:
                val = prow.get(ncols + r, Fraction(0))
                if val != 0:
                    sol[c] = val
        sols.append(sol)
    return rank, consistent, sols


# --------------------------------------------------------------------------- #
# Generic coboundary operator delta_1 as a sparse matrix
# --------------------------------------------------------------------------- #
def odd_map_columns(bt: BracketTable):
    cols = [(zj, zi) for zj in bt.order for zi in bt.order if bt.parity[zi] != bt.parity[zj]]
    return cols, {c: i for i, c in enumerate(cols)}


def row_index(bt: BracketTable):
    rows = [(x, y, z) for x in bt.order for y in bt.order for z in bt.order
            if bt.parity[z] == (bt.parity[x] + bt.parity[y] + 1) % 2]
    return rows, {r: i for i, r in enumerate(rows)}


def delta1_matrix(bt: BracketTable):
    cols, cidx = odd_map_columns(bt)
    rows, ridx = row_index(bt)
    mat = [dict() for _ in rows]
    for j, (zj, zi) in enumerate(cols):
        f = {zj: {zi: LinPoly(1)}}
        for x in bt.order:
            for y in bt.order:
                d = delta_f_pair(bt, f, x, y)
                for z, c in d.items():
                    mat[ridx[(x, y, z)]][j] = c.scalar_value()
    return cols, cidx, rows, ridx, mat


def gamma_vectors(n: int, bt: BracketTable, ridx):
    """Per unit gb direction: {rowindex: value} of gamma^{(dir)}."""
    gamma, consts, _ = compute_gamma(n)
    _, _, entries = gb_labels(n)
    dirs = [e for row in entries for e in row]
    vecs = {d: {} for d in dirs}
    for (x, y), vec in gamma.items():
        for z, c in vec.items():
            for mono, val in c.terms.items():
                vecs[mono[0]][ridx[(x, y, z)]] = val
    return dirs, vecs, gamma, consts


# --------------------------------------------------------------------------- #
# Weight machinery
# --------------------------------------------------------------------------- #
def weights(n: int, bt: BracketTable) -> Dict[str, Tuple[int, ...]]:
    w = {}
    for lab in bt.order:
        _, _, vec = realization_words(n, lab)
        w[lab] = tuple(vec) if vec is not None else tuple([0] * (n + 1))
    return w


def cartan_eigen(bt: BracketTable, h: str, lab: str) -> Fraction:
    v = bt.bracket_basis(h, lab)
    return v.get(lab, Fraction(0))


def weight_zero_odd_Z2(n: int, bt: BracketTable):
    """Exact dim of weight-0 odd 2-cocycles (= H^2_odd(g,g) since weight-0 odd 1-cochains vanish)."""
    wt = weights(n, bt)
    p = bt.parity
    order = bt.order
    idx = {l: i for i, l in enumerate(order)}
    # unknowns: gamma(X,Y)_Z for X<=Y (X==Y only if odd), wt(Z)=wt(X)+wt(Y), p(Z)=p(X)+p(Y)+1
    unknowns = []
    for i, x in enumerate(order):
        for y in order[i:]:
            if x == y and p[x] == 0:
                continue
            target = tuple(a + b for a, b in zip(wt[x], wt[y]))
            for z in order:
                if wt[z] == target and p[z] == (p[x] + p[y] + 1) % 2:
                    unknowns.append((x, y, z))
    uidx = {u: i for i, u in enumerate(unknowns)}

    def gamma_coeff(x, y, z):
        """(coefficient dict over unknowns) for gamma(x,y)_z using graded antisymmetry."""
        if idx[x] <= idx[y]:
            key = (x, y, z)
            return {uidx[key]: Fraction(1)} if key in uidx else {}
        key = (y, x, z)
        if key not in uidx:
            return {}
        s = -((-1) ** (p[x] * p[y]))
        return {uidx[key]: Fraction(s)}

    def gamma_vec(x, y):
        """gamma(x,y) as {z: {unknown: coeff}}."""
        out = {}
        for z in order:
            c = gamma_coeff(x, y, z)
            if c:
                out[z] = c
        return out

    def lin_bracket_left(u, vec):  # [u, vec] where vec = {z: {unk: c}}
        out = {}
        for z, cd in vec.items():
            for zz, s in bt.bracket_basis(u, z).items():
                d = out.setdefault(zz, {})
                for k, v in cd.items():
                    d[k] = d.get(k, Fraction(0)) + v * s
        return out

    def lin_bracket_right(vec, u):
        out = {}
        for z, cd in vec.items():
            for zz, s in bt.bracket_basis(z, u).items():
                d = out.setdefault(zz, {})
                for k, v in cd.items():
                    d[k] = d.get(k, Fraction(0)) + v * s
        return out

    def gamma_lin(u, vec):  # gamma(u, vec) with vec = {z: scalar}
        out = {}
        for z, s in vec.items():
            for zz, cd in gamma_vec(u, z).items():
                d = out.setdefault(zz, {})
                for k, v in cd.items():
                    d[k] = d.get(k, Fraction(0)) + v * s
        return out

    def gamma_lin_left(vec, u):
        out = {}
        for z, s in vec.items():
            for zz, cd in gamma_vec(z, u).items():
                d = out.setdefault(zz, {})
                for k, v in cd.items():
                    d[k] = d.get(k, Fraction(0)) + v * s
        return out

    def acc(total, part, sign):
        for z, cd in part.items():
            d = total.setdefault(z, {})
            for k, v in cd.items():
                d[k] = d.get(k, Fraction(0)) + sign * v

    ech = SparseEchelon()
    for x in order:
        for y in order:
            for z in order:
                # cocycle identity (I05) restricted to weight-0 cochains
                total = {}
                acc(total, gamma_lin(x, bt.bracket_basis(y, z)), 1)
                acc(total, lin_bracket_left(x, gamma_vec(y, z)), (-1) ** p[x])
                acc(total, gamma_lin_left(bt.bracket_basis(x, y), z), -1)
                acc(total, lin_bracket_right(gamma_vec(x, y), z), -1)
                acc(total, gamma_lin(y, bt.bracket_basis(x, z)), -((-1) ** (p[x] * p[y])))
                acc(total, lin_bracket_left(y, gamma_vec(x, z)), -((-1) ** (p[x] * p[y] + p[y])))
                for zz, cd in total.items():
                    row = {k: v for k, v in cd.items() if v != 0}
                    if row:
                        ech.add(row)
    return len(unknowns), ech.rank, len(unknowns) - ech.rank


# --------------------------------------------------------------------------- #
# Main analysis
# --------------------------------------------------------------------------- #
def part_A(n: int) -> dict:
    out = {}
    for prof in PROFILES:
        l3 = json.load(open(os.path.join(DATA_DIR, f"C_{n}_evaluated_{prof}.json")))
        l4 = json.load(open(os.path.join(DATA_DIR, f"C_{n}_coboundary_{prof}.json")))
        g = {(e["X"], e["Y"], e["Z"]): Fraction(e["coeff"]) for e in l3["evaluated_gamma"]}
        d = {(e["X"], e["Y"], e["Z"]): Fraction(e["coeff"]) for e in l4["delta_f"]}
        keys = set(g) | set(d)
        resid = {k: g.get(k, 0) + d.get(k, 0) for k in keys}
        resid = {k: v for k, v in resid.items() if v != 0}
        out[prof] = {"gamma_entries": len(g), "delta_f_entries": len(d), "common_support": len(set(g) & set(d)),
                     "residual_entries": len(resid), "max_abs_residual": str(max((abs(v) for v in resid.values()), default=0)),
                     "coincide_up_to_sign": not resid}
    return out


def part_B(n: int, bt: BracketTable) -> dict:
    cols, cidx, rows, ridx, mat = delta1_matrix(bt)
    dirs, vecs, gamma, consts = gamma_vectors(n, bt, ridx)
    # solve  delta phi = -gamma  (same sign convention as the canonical f of Layer 4)
    rhs = [{i: -c for i, c in vecs[d].items()} for d in dirs]
    # profiles as additional rhs
    prof_rhs = []
    for prof in PROFILES:
        vals = profile_values(n, prof)
        v = {}
        for d in dirs:
            for i, c in vecs[d].items():
                v[i] = v.get(i, Fraction(0)) - c * vals[d]
        prof_rhs.append({i: c for i, c in v.items() if c != 0})
    rank, consistent, sols = solve_sparse(mat, len(cols), rhs + prof_rhs)
    # verify each solution independently with the generic coboundary
    verified = []
    for r, sol in enumerate(sols[:len(dirs)]):
        if sol is None:
            verified.append(False)
            continue
        f = {}
        for j, v in sol.items():
            zj, zi = cols[j]
            f.setdefault(zj, {})[zi] = LinPoly(v)
        df = coboundary(bt, f)
        target = {}
        for i, c in vecs[dirs[r]].items():
            x, y, z = rows[i]
            target.setdefault((x, y), {})[z] = c
        ok = True
        for key in set(df) | set(target):
            a = {z: c.scalar_value() for z, c in df.get(key, {}).items()}
            b = {z: -c for z, c in target.get(key, {}).items()}  # delta f = -gamma
            if a != b:
                ok = False
        verified.append(ok)
    return {"n_unknowns_phi": len(cols), "n_equations": len(rows), "rank_delta1": rank,
            "dim_ker_delta1": len(cols) - rank, "dim_g_odd": 4 * n,
            "directions": {d: {"consistent": consistent[i], "solution_nonzeros": (len(sols[i]) if sols[i] else None),
                               "verified_delta_f_eq_minus_gamma": verified[i]} for i, d in enumerate(dirs)},
            "profiles_consistent": {prof: consistent[len(dirs) + i] for i, prof in enumerate(PROFILES)}}


def part_C(n: int, bt: BracketTable, sample: int | None) -> dict:
    cols, _ = odd_map_columns(bt)
    rng = random.Random(20261008)
    chosen = cols if sample is None or sample >= len(cols) else rng.sample(cols, sample)
    failures = 0
    for (zj, zi) in chosen:
        f = {zj: {zi: LinPoly(1)}}
        df = coboundary(bt, f)
        for x in bt.order:
            for y in bt.order:
                for z in bt.order:
                    if cocycle_defect(bt, df, x, y, z):
                        failures += 1
                        break
    return {"elementary_maps_checked": len(chosen), "of_total": len(cols), "delta2_delta1_failures": failures}


def part_D(n: int, bt: BracketTable) -> dict:
    """gamma_K(X,Y) (dropped constants of Layer 2) vs f_K([X,Y]) (dropped constants of f)."""
    _, consts_gamma, _ = compute_gamma(n)
    f, consts_f, _ = canonical_f(n)
    mism = []
    for x in bt.order:
        for y in bt.order:
            lhs = consts_gamma.get((x, y), LinPoly())
            rhs = LinPoly()
            for z, c in bt.bracket_basis(x, y).items():
                if z in consts_f:
                    rhs = rhs + consts_f[z] * c
            if not (lhs - rhs).is_zero():
                mism.append((x, y, lhs.expr(), rhs.expr()))
    return {"pairs_with_gamma_K": len(consts_gamma), "generators_with_f_K": len(consts_f),
            "gamma_K_equals_f_K_of_bracket": not mism, "mismatches": mism[:5]}


def part_E(n: int, bt: BracketTable) -> dict:
    wt = weights(n, bt)
    gamma, _, _ = compute_gamma(n)
    _, _, entries = gb_labels(n)
    dirs = [e for row in entries for e in row]
    # weight of gamma^{(dir)}: wt(Z) - wt(X) - wt(Y) must be constant over its support
    dir_weight = {}
    for d in dirs:
        ws = set()
        for (x, y), vec in gamma.items():
            for z, c in vec.items():
                if (d,) in c.terms:
                    ws.add(tuple(a - b - cc for a, b, cc in zip(wt[z], wt[x], wt[y])))
        dir_weight[d] = sorted(ws)
    # Cartan homotopy: f_h(X) = gamma(h, X) / lambda(h), lambda = weight of gamma^{(d)} evaluated on h
    homotopy = {}
    for d in dirs:
        lam = dir_weight[d][0] if len(dir_weight[d]) == 1 else None
        if lam is None:
            homotopy[d] = "weight not homogeneous"
            continue
        # evaluate lambda(H_i): use eigenvalue of H_i on any basis element of weight lam, via linearity:
        # lambda(H_i) = sum_j lam_j * (eigenvalue of H_i on the j-th fundamental weight) -> read from the odd generators
        # simpler: pick h = H_1 and compute lambda(H_1) from the eigen-pattern of H_1: eps->1, del_1->1, others 0
        lam_H = {}
        for i in range(1, n + 2):
            if i == 1:
                lam_H[i] = lam[0] + lam[1]
            elif i <= n:
                lam_H[i] = lam[i - 1] - lam[i]
            else:
                lam_H[i] = -lam[n]
        h = next((f"H_{i}" for i in range(1, n + 2) if lam_H[i] != 0), None)
        if h is None:
            homotopy[d] = "weight zero: no homotopy"
            continue
        c = Fraction(1, lam_H[int(h[2:])])
        found = None
        for sign in (1, -1):
            f = {}
            for x in bt.order:
                vec = gamma.get((h, x), {})
                comp = {z: LinPoly(cc.terms.get((d,), Fraction(0)) * c * sign) for z, cc in vec.items()}
                comp = {z: v for z, v in comp.items() if not v.is_zero()}
                if comp:
                    f[x] = comp
            df = coboundary(bt, f)
            ok = True
            for x in bt.order:
                for y in bt.order:
                    a = {z: cc.scalar_value() for z, cc in df.get((x, y), {}).items()}
                    b = {z: -cc.terms[(d,)] for z, cc in gamma.get((x, y), {}).items() if (d,) in cc.terms}
                    if a != b:
                        ok = False
            if ok:
                found = f"delta f = -gamma with f(X) = {sign:+d} * gamma({h}, X) / {lam_H[int(h[2:])]}"
                break
        homotopy[d] = found or "homotopy formula did not reproduce gamma"
    # Universal homotopy with the so(2) charge operator Q = a_1^+ a_1^- - 1/2 = H_1 - sum_{k=2}^n H_k + H_{n+1}
    Q = {"H_1": Fraction(1), f"H_{n+1}": Fraction(1)}
    for k in range(2, n + 1):
        Q[f"H_{k}"] = Fraction(-1)
    charge_ok = all(bt.bracket({h: c for h, c in Q.items()}, {x: Fraction(1)}) == ({x: Fraction(wt[x][0])} if wt[x][0] else {})
                    for x in bt.order)
    q_homotopy = {}
    for d in dirs:
        lam = dir_weight[d][0][0]  # eps-component of the weight of gamma^{(d)} = charge
        found = None
        for sign in (1, -1):
            f = {}
            for x in bt.order:
                comp = {}
                for h, ch in Q.items():
                    for z, cc in gamma.get((h, x), {}).items():
                        v = cc.terms.get((d,), Fraction(0)) * ch * sign / lam
                        if v != 0:
                            comp[z] = comp.get(z, LinPoly()) + LinPoly(v)
                comp = {z: v for z, v in comp.items() if not v.is_zero()}
                if comp:
                    f[x] = comp
            df = coboundary(bt, f)
            ok = True
            for x in bt.order:
                for y in bt.order:
                    a = {z: cc.scalar_value() for z, cc in df.get((x, y), {}).items()}
                    b = {z: -cc.terms[(d,)] for z, cc in gamma.get((x, y), {}).items() if (d,) in cc.terms}
                    if a != b:
                        ok = False
            if ok:
                found = f"charge {lam:+d}: delta f = -gamma with f(X) = {sign:+d} * gamma(Q, X) / ({lam:+d})"
                break
        q_homotopy[d] = found or "Q-homotopy did not reproduce gamma"
    nunk, rank, dimZ = weight_zero_odd_Z2(n, bt)
    return {"direction_weights_(eps,del1..deln)": {d: [list(w) for w in dir_weight[d]] for d in dirs},
            "cartan_homotopy": homotopy,
            "charge_operator_Q": {h: str(c) for h, c in Q.items()},
            "Q_eigenvalues_equal_eps_component": charge_ok,
            "Q_homotopy": q_homotopy,
            "weight_zero_odd_2cochains": nunk, "rank_delta2_on_them": rank, "dim_H2_odd": dimZ}


def main(argv):
    ns = [int(a) for a in argv] or [1, 2, 3]
    report = {}
    for n in ns:
        bt = BracketTable.load(n)
        print(f"===== C({n+1}), n={n} =====")
        A = part_A(n)
        for prof, r in A.items():
            print(f"  A [{prof:18s}] gamma {r['gamma_entries']:5d} entries, delta_f {r['delta_f_entries']:5d}, "
                  f"residual entries {r['residual_entries']}, coincide={r['coincide_up_to_sign']}")
        B = part_B(n, bt)
        print(f"  B unknowns phi={B['n_unknowns_phi']}, equations={B['n_equations']}, rank={B['rank_delta1']}, "
              f"dim ker={B['dim_ker_delta1']} (dim g_odd={B['dim_g_odd']})")
        for d, r in B["directions"].items():
            print(f"    {d}: consistent={r['consistent']}, solution nonzeros={r['solution_nonzeros']}, verified={r['verified_delta_f_eq_minus_gamma']}")
        print(f"    profiles consistent: {B['profiles_consistent']}")
        C = part_C(n, bt, None if n <= 2 else 24)
        print(f"  C delta2∘delta1=0: {C['elementary_maps_checked']}/{C['of_total']} elementary maps, failures={C['delta2_delta1_failures']}")
        D = part_D(n, bt)
        print(f"  D K-retained: gamma_K == f_K([X,Y]) : {D['gamma_K_equals_f_K_of_bracket']} "
              f"({D['pairs_with_gamma_K']} pairs with constants)")
        E = part_E(n, bt)
        print(f"  E weights of gamma^(dir): {E['direction_weights_(eps,del1..deln)']}")
        for d, h in E["cartan_homotopy"].items():
            print(f"    {d}: {h}")
        print(f"    Q = {E['charge_operator_Q']}, Q-eigenvalues = eps-component: {E['Q_eigenvalues_equal_eps_component']}")
        for d, h in E["Q_homotopy"].items():
            print(f"    {d}: {h}")
        print(f"    weight-0 odd 2-cochains: {E['weight_zero_odd_2cochains']}, rank delta2 = {E['rank_delta2_on_them']}, "
              f"dim H^2_odd(g,g) = {E['dim_H2_odd']}")
        report[n] = {"A": A, "B": B, "C": C, "D": D, "E": E}
    path = os.path.join(REPO_ROOT, "docs", "triviality_report_data.json")
    with open(path, "w") as fh:
        json.dump(report, fh, indent=1, default=str)
    print("wrote", path)


if __name__ == "__main__":
    main(sys.argv[1:])
