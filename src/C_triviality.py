"""Compare Schema 2 (gamma) to Schema 4 (coboundary) for C(n+1) and
determine conditions under which the inhomogeneous deformation is trivial.
"""

from __future__ import annotations

from typing import Dict, Tuple

import sympy as sp

from src.C_coboundary import coboundary_entries
from src.C_gamma import build_gamma
from src.C_generators import build_basis


def collect_pairs(n: int):
    even, odd, _, pars = build_basis(n)
    labels = even + odd

    gamma_entries, _, _ = build_gamma(n)
    delta_entries, _, _, phi = coboundary_entries(n)

    gamma_map: Dict[Tuple[str, str, str], sp.Expr] = {}
    for e in gamma_entries:
        key = (e["X"], e["Y"], e["Z"])
        gamma_map[key] = gamma_map.get(key, sp.Integer(0)) + sp.sympify(e["coeff"])

    gamma_full: Dict[Tuple[str, str, str], sp.Expr] = {}
    for (X, Y, Z), c in gamma_map.items():
        gamma_full[(X, Y, Z)] = c
        if X != Y:
            sign = 1 if (pars[X] * pars[Y]) % 2 == 0 else -1
            gamma_full[(Y, X, Z)] = -sign * c

    delta_map: Dict[Tuple[str, str, str], sp.Expr] = {}
    for e in delta_entries:
        key = (e["X"], e["Y"], e["Z"])
        delta_map[key] = sp.sympify(e["coeff"])

    return gamma_full, delta_map, phi, labels, pars


def triviality_system(n: int):
    gamma_full, delta_map, phi_sym_dict, labels, pars = collect_pairs(n)
    keys = set(gamma_full) | set(delta_map)
    residuals = []
    for k in keys:
        diff = sp.expand(gamma_full.get(k, sp.Integer(0)) - delta_map.get(k, sp.Integer(0)))
        if diff != 0:
            residuals.append((k, diff))
    phi_syms = sorted(phi_sym_dict.values(), key=lambda s: s.name)
    return residuals, phi_syms


def coincidence_table(n: int):
    """For each (X,Y,Z) triple, report whether gamma = delta_f entry under some
    assignment (gb and phi both free) — purely by matching entries."""
    gamma_full, delta_map, phi_sym_dict, labels, pars = collect_pairs(n)
    matches = 0
    only_gamma = 0
    only_delta = 0
    for k in set(gamma_full) | set(delta_map):
        g = sp.simplify(gamma_full.get(k, sp.Integer(0)))
        d = sp.simplify(delta_map.get(k, sp.Integer(0)))
        if g == 0 and d != 0:
            only_delta += 1
        elif g != 0 and d == 0:
            only_gamma += 1
        else:
            matches += 1
    return matches, only_gamma, only_delta


def solve_triviality(n: int):
    """Attempt to find phi (as linear expressions in gb) solving gamma = delta_f."""
    residuals, phi_syms = triviality_system(n)
    if not residuals:
        return {"status": "trivially trivial (empty residual set)"}
    equations = [r for _, r in residuals]
    try:
        sol = sp.linsolve(equations, phi_syms)
    except Exception as exc:
        return {"status": f"linsolve failed: {exc}"}
    if sol == sp.EmptySet:
        return {"status": "no_solution", "equations_count": len(equations)}
    sol_tuple = next(iter(sol))
    # Check solution: substitute and verify residuals vanish.
    assign = dict(zip(phi_syms, sol_tuple))
    unresolved = []
    for key, r in residuals:
        remain = sp.simplify(r.subs(assign))
        if remain != 0:
            unresolved.append((key, remain))
    return {
        "status": "solved" if not unresolved else "partial",
        "equations_count": len(equations),
        "phi_assignments": assign,
        "unresolved": unresolved,
    }


def classify_phi_dependence(assign):
    """Count how many phi symbols are set to a non-trivial expression in gb vs
    left free (as themselves)."""
    gb_dependent = 0
    free = 0
    zero = 0
    for phi, val in assign.items():
        if val == 0:
            zero += 1
        elif val == phi:
            free += 1
        else:
            gb_dependent += 1
    return {"gb_dependent": gb_dependent, "free": free, "zero": zero}


def build_matrices(n: int):
    """Return (Delta, Gamma, gb_syms, phi_syms, keys) where equations are
    Delta · phi = Gamma · gb for the ordered pair–basis triples."""
    gamma_full, delta_map, phi_sym_dict, labels, pars = collect_pairs(n)
    phi_syms = sorted(phi_sym_dict.values(), key=lambda s: s.name)
    gb_set = set()
    for e in list(gamma_full.values()):
        gb_set |= {s for s in e.free_symbols if s.name.startswith("gb_")}
    gb_syms = sorted(gb_set, key=lambda s: s.name)
    all_keys = sorted(set(gamma_full) | set(delta_map))
    Drows = []
    Grows = []
    for key in all_keys:
        g = sp.expand(gamma_full.get(key, sp.Integer(0)))
        d = sp.expand(delta_map.get(key, sp.Integer(0)))
        drow = [d.coeff(p) for p in phi_syms]
        grow = [g.coeff(gb) for gb in gb_syms]
        Drows.append(drow)
        Grows.append(grow)
    return sp.Matrix(Drows), sp.Matrix(Grows), gb_syms, phi_syms, all_keys


def obstruction_analysis(n: int):
    Delta, Gamma, gb_syms, phi_syms, keys = build_matrices(n)
    r_D = Delta.rank()
    DG = Delta.row_join(Gamma)
    r_DG = DG.rank()
    trivial = r_D == r_DG
    # Columns of Gamma that are not in col(Delta): obstruction directions on gb.
    # For each gb symbol i, check if Gamma[:, i] is in col(Delta).
    obstructed_gb = []
    for i, gb in enumerate(gb_syms):
        col = Gamma.col(i)
        extended = Delta.row_join(col)
        if extended.rank() > r_D:
            obstructed_gb.append(gb)
    return {
        "rank_Delta": r_D,
        "rank_Delta_Gamma": r_DG,
        "universally_trivial": trivial,
        "n_gb": len(gb_syms),
        "n_phi": len(phi_syms),
        "n_equations": Delta.rows,
        "obstructed_gb_symbols": [str(s) for s in obstructed_gb],
    }


def main():
    for n in (1, 2):
        print(f"\n===== n = {n} (C({n + 1})) =====")
        m, og, od = coincidence_table(n)
        print(f"triple counts: matching={m}, γ-only={og}, δf-only={od}")
        info = obstruction_analysis(n)
        print(f"n_gb={info['n_gb']}  n_phi={info['n_phi']}  n_eqs={info['n_equations']}")
        print(f"rank(Delta)={info['rank_Delta']}  rank([Delta|Gamma])={info['rank_Delta_Gamma']}")
        print(f"universally trivial: {info['universally_trivial']}")
        if not info["universally_trivial"]:
            print(f"obstructed gb directions ({len(info['obstructed_gb_symbols'])}):")
            for s in info["obstructed_gb_symbols"]:
                print(f"  {s}")


if __name__ == "__main__":
    main()
