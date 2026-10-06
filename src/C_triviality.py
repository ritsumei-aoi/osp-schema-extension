"""Triviality search for C(n+1): compare Layer 3 against Layer 4.  Issue I08.

Two independent investigations:

**A. Direct comparison.**  For every gb profile of Layer 3, substitute the
profile values into the Layer 4 coboundary entries and compare with the Layer 3
gamma entries, pair by pair.

**B. Linear solve (no prior knowledge of f).**  Treat

    gamma(X, Y) = (df)(X, Y)   for all X, Y

as a linear system in the unknowns ``phi[t][s]`` (``f(Z_s) = sum_t phi[t][s] Z_t``,
parity reversing) and solve it exactly over Q(gb) by sparse fraction-free
elimination.  Reports, per rank n:

* whether the system is **consistent** (= gamma is a coboundary = trivial),
* the **rank** and the **dimension of the solution space**,
* the same with the ``K`` target of ``f`` removed, which is the one setting in
  which genuine obstructions appear.

Usage::

    python src/C_triviality.py          # n = 1, 2, 3
"""

from __future__ import annotations

import json
import os
import sys
from typing import Dict, List, Tuple

import sympy as sp

try:
    from .osc_algebra import CAlgebra, gb_symbols
    from .C_gamma import build_gamma, gamma_table
    from .C_coboundary import Coboundary, canonical_f, vadd
    from .C_evaluate import PROFILES, gb_values
except ImportError:
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from osc_algebra import CAlgebra, gb_symbols  # type: ignore
    from C_gamma import build_gamma, gamma_table  # type: ignore
    from C_coboundary import Coboundary, canonical_f, vadd  # type: ignore
    from C_evaluate import PROFILES, gb_values  # type: ignore

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(REPO, "data")

Row = Dict[int, sp.Rational]


# ==========================================================================
# A. direct Layer 3 vs Layer 4 comparison
# ==========================================================================
def compare_layers(n: int) -> List[dict]:
    with open(os.path.join(DATA, f"C_{n}_coboundary.json")) as fh:
        doc4 = json.load(fh)
    delta_sym = {(e["X"], e["Y"], e["Z"]): sp.sympify(e["coeff"])
                 for e in doc4["coboundary"]["entries"]}

    _gb, labels = gb_symbols(n)
    results = []
    for profile in PROFILES:
        path = os.path.join(DATA, f"C_{n}_evaluated_{profile}.json")
        with open(path) as fh:
            doc3 = json.load(fh)
        subs = {sp.Symbol(k): sp.sympify(v) for k, v in doc3["gb_values"].items()}

        gamma = {(e["X"], e["Y"], e["Z"]): sp.sympify(e["coeff"])
                 for e in doc3["evaluated_deformation"]["entries"]}
        delta = {}
        for k, v in delta_sym.items():
            c = sp.expand(v.subs(subs))
            if c != 0:
                delta[k] = c

        mismatch = {k for k in set(gamma) | set(delta)
                    if gamma.get(k, 0) != delta.get(k, 0)}
        results.append({
            "profile": profile,
            "gamma_entries": len(gamma),
            "delta_f_entries": len(delta),
            "identical": not mismatch,
            "mismatching_triples": sorted(map(list, mismatch))[:20],
            "trivial": not mismatch,
        })
    return results


# ==========================================================================
# B. exact sparse linear solve
# ==========================================================================
class SparseSolver:
    """Row echelon over Q with sympy right-hand sides (polynomials in gb)."""

    def __init__(self) -> None:
        self.pivots: Dict[int, Tuple[Row, sp.Expr]] = {}
        self.inconsistent: List[sp.Expr] = []

    def add(self, row: Row, rhs: sp.Expr) -> None:
        row = {c: v for c, v in row.items() if v != 0}
        while row:
            c = min(row)
            if c not in self.pivots:
                factor = row[c]
                row = {k: sp.Rational(v, 1) / factor for k, v in row.items()}
                self.pivots[c] = (row, sp.expand(rhs / factor))
                return
            prow, prhs = self.pivots[c]
            f = row[c]
            for k, v in prow.items():
                nv = row.get(k, sp.Integer(0)) - f * v
                if nv == 0:
                    row.pop(k, None)
                else:
                    row[k] = nv
            rhs = sp.expand(rhs - f * prhs)
        if sp.expand(rhs) != 0:
            self.inconsistent.append(sp.expand(rhs))

    @property
    def rank(self) -> int:
        return len(self.pivots)

    def particular_solution(self, n_unknowns: int) -> Dict[int, sp.Expr]:
        """Back-substitute with all free variables set to 0."""
        sol: Dict[int, sp.Expr] = {}
        for c in sorted(self.pivots, reverse=True):
            row, rhs = self.pivots[c]
            acc = rhs
            for k, v in row.items():
                if k != c:
                    acc = acc - v * sol.get(k, sp.Integer(0))
            sol[c] = sp.expand(acc)
        return sol


def build_system(n: int, allow_K: bool = True):
    """Return ``(solver, unknowns, cob, gam)`` for ``gamma = delta f``."""
    gb, _ = gb_symbols(n)
    cob = Coboundary(n)
    _a, _p, entries, _c, _l = build_gamma(n)
    gam = gamma_table(CAlgebra(n, gb), entries)

    order = cob.order
    # equations are always imposed on every component of g + C*K: restricting the
    # *target* of f must not silently drop the K-component equations.
    eq_targets = order + ["K"]
    unk_targets = order + (["K"] if allow_K else [])
    unknowns: Dict[Tuple[str, str], int] = {}
    for s in order:
        for t in unk_targets:
            if cob.par[t] != (cob.par[s] + 1) % 2:
                continue
            unknowns[(t, s)] = len(unknowns)

    solver = SparseSolver()
    for i, x in enumerate(order):
        for y in order[i:]:
            px, py = cob.par[x], cob.par[y]
            s1 = sp.Integer(-1) ** px
            s2 = -sp.Integer(-1) ** ((px + 1) * py)
            bxy = cob.br[(x, y)]

            rows: Dict[str, Row] = {z: {} for z in eq_targets}

            def put(z: str, key: Tuple[str, str], coeff) -> None:
                if z not in rows or coeff == 0 or key not in unknowns:
                    return
                col = unknowns[key]
                rows[z][col] = rows[z].get(col, sp.Integer(0)) + coeff

            for t in unk_targets:
                if t == "K":
                    continue
                # term 1: s1 * phi[t][y] * [x, Z_t]
                for z, c in cob.br[(x, t)].items():
                    put(z, (t, y), s1 * c)
                # term 2: s2 * phi[t][x] * [y, Z_t]
                for z, c in cob.br[(y, t)].items():
                    put(z, (t, x), s2 * c)
            # term 3: - sum_w c_w(x,y) * phi[t][w] * Z_t
            for w, cw in bxy.items():
                if w == "K":
                    continue
                for t in unk_targets:
                    put(t, (t, w), -cw)

            for z in eq_targets:
                solver.add(rows[z], gam[(x, y)].get(z, sp.Integer(0)))
    return solver, unknowns, cob, gam


def analyse(n: int) -> dict:
    out: dict = {"n": n}

    solver, unknowns, cob, gam = build_system(n, allow_K=True)
    consistent = not solver.inconsistent
    out["full"] = {
        "target_of_f": "g + C*K",
        "unknowns": len(unknowns),
        "rank": solver.rank,
        "solution_space_dimension": len(unknowns) - solver.rank,
        "consistent": consistent,
        "obstructions": len(solver.inconsistent),
        "obstruction_samples": [str(e) for e in solver.inconsistent[:5]],
        "verdict": "TRIVIAL for all gb" if consistent else "NON-TRIVIAL",
    }

    # does the solver's own particular solution reproduce gamma?
    if consistent:
        sol = solver.particular_solution(len(unknowns))
        inv = {v: k for k, v in unknowns.items()}
        phi: Dict[str, Dict[str, sp.Expr]] = {s: {} for s in cob.order}
        for col, val in sol.items():
            if sp.expand(val) != 0:
                t, s = inv[col]
                phi[s][t] = sp.expand(val)
        bad = [f"({x},{y})" for i, x in enumerate(cob.order) for y in cob.order[i:]
               if vadd(cob.delta_f(phi, x, y), gam[(x, y)], -1)]
        out["full"]["solver_solution_verified"] = not bad
        out["full"]["solver_solution_failures"] = bad[:5]

        gbs, _ = gb_symbols(n)
        canon = canonical_f(n, gbs)
        out["full"]["solver_solution_equals_canonical_f"] = all(
            sp.expand(sp.Integer(0) + phi.get(s, {}).get(t, 0)
                      - canon.get(s, {}).get(t, 0)) == 0
            for s in cob.order
            for t in set(phi.get(s, {})) | set(canon.get(s, {}))
        )

    solver_k, unknowns_k, _c, _g = build_system(n, allow_K=False)
    out["restricted"] = {
        "target_of_f": "g only (K excluded)",
        "unknowns": len(unknowns_k),
        "rank": solver_k.rank,
        "solution_space_dimension": len(unknowns_k) - solver_k.rank,
        "consistent": not solver_k.inconsistent,
        "obstructions": len(solver_k.inconsistent),
        "obstruction_samples": [str(e) for e in solver_k.inconsistent[:6]],
        "verdict": ("TRIVIAL for all gb" if not solver_k.inconsistent
                    else "NON-TRIVIAL: obstruction in the K-component"),
    }
    out["solution_space"] = inner_odd_maps(n)
    return out


def inner_odd_maps(n: int) -> dict:
    """Identify the solution space: ``ker(delta) = {ad(W) : W odd}``, dim 4n.

    For odd ``W``, ``ad(W): X -> [W, X]`` is an odd linear map with
    ``delta(ad W) = 0`` (the coboundary of an inner map vanishes), so the
    solutions of ``gamma = delta f`` form a torsor over ``ad(g_odd)``.
    """
    cob = Coboundary(n)
    maps = {}
    nonzero_delta = []
    for w in cob.alg.odd:
        phi = {s: dict(cob.br[(w, s)]) for s in cob.order}
        phi = {s: v for s, v in phi.items() if v}
        assert cob.check_f_is_odd(phi) == []
        maps[w] = phi
        for i, x in enumerate(cob.order):
            for y in cob.order[i:]:
                if cob.delta_f(phi, x, y):
                    nonzero_delta.append(f"ad({w}) at ({x},{y})")

    # linear independence of {ad(W)} as maps
    cols = []
    keys = sorted({(s, t) for phi in maps.values() for s, v in phi.items() for t in v})
    for w in cob.alg.odd:
        cols.append([maps[w].get(s, {}).get(t, sp.Integer(0)) for s, t in keys])
    rank = sp.Matrix(cols).T.rank()

    return {
        "description": "ker(delta) on odd maps = inner maps ad(W), W in g_odd",
        "candidates": len(maps),
        "delta_vanishes_on_all": not nonzero_delta,
        "failures": nonzero_delta[:5],
        "rank_of_ad_g_odd": int(rank),
        "expected_rank": 4 * n,
    }


def obstruction_detail(n: int) -> List[dict]:
    """Which (X, Y, Z) carry the K-obstruction when f is restricted to g."""
    with open(os.path.join(DATA, f"C_{n}_gamma.json")) as fh:
        doc = json.load(fh)
    return [
        {"X": e["X"], "Y": e["Y"], "Z": "K", "gamma_coeff": e["coeff"],
         "delta_f_coeff_if_f_maps_into_g": "0",
         "parity_X": e["parity_X"], "parity_Y": e["parity_Y"]}
        for e in doc["inhomogeneous_deformation"]["entries"] if e["Z"] == "K"
    ]


# ==========================================================================
def main(argv: List[str]) -> int:
    ns = [int(a) for a in argv[1:]] or [1, 2, 3]
    report = {"generated_by": "src/C_triviality.py", "ranks": {}}
    ok = True
    for n in ns:
        print(f"=== n = {n}   C({n + 1}) ===")
        cmp = compare_layers(n)
        for r in cmp:
            print(f"  profile {r['profile']:<17} gamma={r['gamma_entries']:<4} "
                  f"delta_f={r['delta_f_entries']:<4} identical={r['identical']} "
                  f"-> {'TRIVIAL' if r['trivial'] else 'NON-TRIVIAL'}")
            ok &= r["trivial"]

        a = analyse(n)
        f, r = a["full"], a["restricted"]
        print(f"  linear solve  [f -> g+CK] unknowns={f['unknowns']} rank={f['rank']} "
              f"soln-dim={f['solution_space_dimension']} consistent={f['consistent']} "
              f"-> {f['verdict']}")
        if f["consistent"]:
            print(f"                 solver solution verified={f['solver_solution_verified']}, "
                  f"equals canonical f={f['solver_solution_equals_canonical_f']}")
        print(f"  linear solve  [f -> g   ] unknowns={r['unknowns']} rank={r['rank']} "
              f"soln-dim={r['solution_space_dimension']} consistent={r['consistent']} "
              f"obstructions={r['obstructions']} -> {r['verdict']}")
        ok &= f["consistent"]

        ss = a["solution_space"]
        print(f"  solution space  ad(g_odd): delta vanishes={ss['delta_vanishes_on_all']} "
              f"rank={ss['rank_of_ad_g_odd']} (expected {ss['expected_rank']}, "
              f"solver soln-dim {f['solution_space_dimension']})")

        obs = obstruction_detail(n)
        print(f"  K-obstruction pairs (restricted setting): {len(obs)}")
        report["ranks"][str(n)] = {
            "profile_comparison": cmp,
            "linear_analysis": a,
            "restricted_obstruction_entries": obs,
        }

    path = os.path.join(DATA, "C_triviality_report.json")
    with open(path, "w") as fh:
        json.dump(report, fh, indent=2)
        fh.write("\n")
    print(f"\nreport -> {os.path.relpath(path, REPO)}")
    print("SUMMARY:", "PASS" if ok else "FAIL")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
