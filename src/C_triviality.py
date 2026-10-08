"""Triviality analysis of the inhomogeneous deformation of C(n+1)  (Issue I08).

Compares Layer 3 (evaluated gamma) with Layer 4 (coboundary delta f) and decides for which gb the
deformation is trivial, i.e. gamma(gb) in image(delta).

Three variants of the target of the odd map f are analysed:
    "K"      : f: g -> g (+) C K           (primary; gamma itself has K-components)
    "strict" : f: g -> g                   (literal reading of C_coboundary_definition.md)
    "mod_K"  : f: g -> g and gamma projected to g (K-components discarded)

Method (exact rational arithmetic):
    * unknowns: phi parameters of Schema 4; equations: one per (X, Y, Z) component,
      (delta f)_{XY}^Z (phi) = gamma_{XY}^Z (gb).
    * gamma is linear in gb, gamma = sum_p gb_p gamma^{(p)}; row-reducing the augmented matrix
      [D | Gamma] with pivots restricted to the D columns leaves rows whose D-part vanishes; their
      Gamma-parts are exactly the linear conditions on gb for solvability.
    * for each Layer 3 profile the system is solved explicitly and delta f == gamma re-verified.
    * the closed-form candidate f_shift induced by the oscillator change of variables
          b_j^s -> b_j^s + kappa (gb_{+,j,s} a_1^- + gb_{-,j,s} a_1^+)
      is computed with the oscillator engine and checked against gamma for all n.

Usage:  python src/C_triviality.py            (writes data/C_{n}_triviality.json and prints a report)
"""
from __future__ import annotations

import datetime as _dt
import json
import os
import sys
from fractions import Fraction
from typing import Dict, List, Tuple

import sympy as sp

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import C_coboundary as CB  # noqa: E402
import C_evaluate as CE  # noqa: E402
import C_gamma as CG  # noqa: E402
import C_generators as G  # noqa: E402
from oscillator_algebra import OscillatorAlgebra, gb_label, gb_labels  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(ROOT, "data")


# ------------------------------------------------------------ exact row reduction
class EchelonReducer:
    """Incremental sparse row echelon form over Q with pivots restricted to columns < n_pivot."""

    def __init__(self, n_pivot: int):
        self.n_pivot = n_pivot
        self.pivots: Dict[int, Dict[int, Fraction]] = {}   # pivot col -> row (min col == pivot col)

    def reduce(self, row: Dict[int, Fraction]) -> Dict[int, Fraction]:
        """Reduce ``row`` by the current pivots; returns the remainder (empty if dependent)."""
        row = {c: v for c, v in row.items() if v != 0}
        while row:
            c = min(row)
            if c >= self.n_pivot or c not in self.pivots:
                return row
            f = row[c]
            for cc, vv in self.pivots[c].items():
                nv = row.get(cc, Fraction(0)) - f * vv
                if nv == 0:
                    row.pop(cc, None)
                else:
                    row[cc] = nv
        return row

    def add(self, row: Dict[int, Fraction]):
        """Reduce and insert as a pivot if possible. Returns ('pivot', c) | ('zero', None) | ('residual', rem)."""
        rem = self.reduce(row)
        if not rem:
            return "zero", None
        c = min(rem)
        if c >= self.n_pivot:
            return "residual", rem
        f = rem[c]
        self.pivots[c] = {cc: vv / f for cc, vv in rem.items()}
        return "pivot", c

    @property
    def rank(self) -> int:
        return len(self.pivots)

    def back_substitute(self, rhs_col: int) -> Dict[int, Fraction]:
        """Solve for the pivot variables with free variables = 0 (rows must contain only pivot cols and rhs_col)."""
        sol: Dict[int, Fraction] = {}
        for c in sorted(self.pivots, reverse=True):
            row = self.pivots[c]
            val = row.get(rhs_col, Fraction(0))
            for cc, vv in row.items():
                if cc != c and cc != rhs_col:
                    val -= vv * sol.get(cc, Fraction(0))
            sol[c] = val
        return {c: v for c, v in sol.items() if v != 0}


# ---------------------------------------------------------------- the linear system
class TrivialitySystem:
    def __init__(self, n: int, variant: str = "K"):
        assert variant in ("K", "strict", "mod_K")
        self.n, self.variant = n, variant
        self.s1 = json.load(open(G.structure_path(n)))
        self.s2 = CG.load_schema2(n)
        self.s4 = CB.load_schema4(n)
        self.gb = gb_labels(n)
        params = [p["label"] for p in self.s4["odd_linear_map"]["parameters"]]
        if variant != "K":
            params = [p for p in params if not p.startswith("phi__K__")]
        self.params = params
        self.col = {p: i for i, p in enumerate(params)}
        self.m = len(params)
        self.gcol = {g: self.m + i for i, g in enumerate(self.gb)}
        # rows: (X, Y, Z) -> {col: coeff}; D-part from Schema 4, Gamma-part from Schema 2
        rows: Dict[Tuple[str, str, str], Dict[int, Fraction]] = {}
        for e in self.s4["coboundary"]["entries"]:
            if variant != "K" and e["Z"] == "K":
                if variant == "mod_K":
                    continue
                # strict: K-components of delta f are 0 after dropping phi__K__*, nothing to add
            for lab, c in e["linear_form"].items():
                if lab in self.col:
                    rows.setdefault((e["X"], e["Y"], e["Z"]), {})[self.col[lab]] = Fraction(c)
        for e in self.s2["inhomogeneous_deformation"]["gamma"]:
            if variant == "mod_K" and e["Z"] == "K":
                continue
            r = rows.setdefault((e["X"], e["Y"], e["Z"]), {})
            for lab, c in e["linear_form"].items():
                r[self.gcol[lab]] = r.get(self.gcol[lab], Fraction(0)) - Fraction(c)   # D phi - Gamma gb = 0
        self.rows = rows
        self.keys = sorted(rows)
        self.gamma_by_pair = {}
        for e in self.s2["inhomogeneous_deformation"]["gamma"]:
            self.gamma_by_pair.setdefault((e["X"], e["Y"]), {})[e["Z"]] = e["linear_form"]

    # -- symbolic analysis -----------------------------------------------------
    def solvability_conditions(self):
        """Row-reduce [D | -Gamma] with pivots on D only. Returns (rank_D, constraint rows on gb)."""
        red = EchelonReducer(self.m)
        residuals = []
        for k in self.keys:
            status, rem = red.add(self.rows[k])
            if status == "residual":
                residuals.append(rem)
        # independent constraints on gb
        cred = EchelonReducer(self.m + len(self.gb))
        constraints = []
        for rem in residuals:
            st, _ = cred.add(rem)
            if st == "pivot":
                constraints.append(rem)
        cons = []
        for rem in constraints:
            piv = min(rem)
            cons.append({self.gb[c - self.m]: str(v / rem[piv]) for c, v in rem.items()})
        return red.rank, cons, len(residuals)

    # -- explicit solve at numeric gb -------------------------------------------
    def solve(self, gb_values: Dict[str, Fraction]):
        """Solve D phi = gamma(gb). Returns (solvable, phi dict, inconsistent components)."""
        rhs_col = self.m
        red = EchelonReducer(self.m)
        bad = []
        for k in self.keys:
            row = {c: v for c, v in self.rows[k].items() if c < self.m}
            b = sum((-v * gb_values[self.gb[c - self.m]] for c, v in self.rows[k].items() if c >= self.m), Fraction(0))
            if b != 0:
                row[rhs_col] = b
            st, rem = red.add(row)
            if st == "residual":
                bad.append((k, rem[rhs_col]))
        if bad:
            return False, {}, bad
        sol = red.back_substitute(rhs_col)
        return True, {self.params[c]: v for c, v in sol.items()}, []

    def check_solution(self, gb_values: Dict[str, Fraction], phi: Dict[str, Fraction], gamma_table=None):
        """Independent re-check from the JSON data: evaluate delta f (Layer 4) at phi and compare with
        gamma at gb (Layer 2 linear forms, or a Layer 3 table passed in ``gamma_table``)."""
        cochain = CB.cochain_from_schema4(self.s4)
        df = CB.CoboundaryOperator.evaluate(cochain, phi)
        gam = CG.gamma_table(self.s2, gb_values) if gamma_table is None else gamma_table
        if self.variant == "mod_K":
            df = {k: {z: c for z, c in v.items() if z != "K"} for k, v in df.items()}
            gam = {k: {z: c for z, c in v.items() if z != "K"} for k, v in gam.items()}
            df = {k: v for k, v in df.items() if v}
            gam = {k: v for k, v in gam.items() if v}
        mismatches = []
        for key in set(df) | set(gam):
            if df.get(key, {}) != gam.get(key, {}):
                mismatches.append((key, gam.get(key, {}), df.get(key, {})))
        return mismatches


def layer3_gamma_table(n: int, name: str):
    """gamma from the Layer 3 file data/C_{n}_evaluated[_name].json as (X, Y) -> {Z: Fraction}."""
    d = json.load(open(CE.evaluated_path(n, name)))
    tab = {}
    for e in d["evaluated_structure"]["gamma_evaluated"]:
        tab.setdefault((e["X"], e["Y"]), {})[e["Z"]] = Fraction(e["coeff"])
    gb = {l: Fraction(v) for l, v in d["gb_assignment"]["values"].items()}
    return gb, tab


# ----------------------------------------------------- closed-form candidate f_shift
def shift_map(n: int, gb_values: Dict[str, Fraction]):
    """f_shift from b_j^s -> b_j^s + kappa (gb_{+,j,s} a_1^- + gb_{-,j,s} a_1^+): X' = X + kappa f(X).

    Returns (phi dict, residual) where residual lists any X whose kappa^0 part is not X itself.
    Computed in the *deformed* oscillator algebra at the same gb (kappa^2 = 0 makes the result identical
    in the undeformed one for the kappa^1 part).
    """
    alg = OscillatorAlgebra(n, deformed=True, gb={l: sp.Rational(str(v)) for l, v in gb_values.items()})
    dec = G.Decomposer(n)
    one = sp.Integer(1)

    def primed(sym: str):
        if not sym.startswith("b_"):
            return {(sym,): one}
        _, j, s = sym.split("_")
        out = {(sym,): one}
        cp = sp.Rational(str(gb_values[gb_label("p", int(j), s)]))
        cm = sp.Rational(str(gb_values[gb_label("m", int(j), s)]))
        if cp != 0:
            out[("kappa", "a_1_m")] = cp
        if cm != 0:
            out[("kappa", "a_1_p")] = cm
        return out

    phi: Dict[str, Fraction] = {}
    residual = []
    for X, elem in dec.elems.items():
        acc = {}
        for word, c in elem.items():
            term = {(): c}
            for sym in word:
                term = alg.mul(term, primed(sym))
            alg._add(acc, term, one)
        acc = alg.clean(acc)
        p0, p1 = alg.split_kappa(acc)
        if dec.decompose(p0) != {X: 1}:
            residual.append((X, dec.decompose(p0)))
        for Z, c in dec.decompose(p1).items():
            phi[CB.phi_label(Z, X)] = Fraction(str(c))
    return phi, residual


def check_shift_map(n: int, gb_values: Dict[str, Fraction]):
    """Verify that gamma = -delta f_shift (equivalently that X' satisfy the undeformed brackets)."""
    phi, residual = shift_map(n, gb_values)
    sys_ = TrivialitySystem(n, "K")
    neg_phi = {k: -v for k, v in phi.items()}
    mism = sys_.check_solution(gb_values, neg_phi)
    return phi, residual, mism


def symbolic_shift_map(n: int):
    """f_shift with symbolic gb; returns {phi label: sympy expr} for human-readable reporting."""
    syms = {l: sp.Symbol(l) for l in gb_labels(n)}
    alg = OscillatorAlgebra(n, deformed=True, gb=syms)
    dec = G.Decomposer(n)
    one = sp.Integer(1)

    def primed(sym: str):
        if not sym.startswith("b_"):
            return {(sym,): one}
        _, j, s = sym.split("_")
        return {(sym,): one, ("kappa", "a_1_m"): syms[gb_label("p", int(j), s)],
                ("kappa", "a_1_p"): syms[gb_label("m", int(j), s)]}

    out = {}
    for X, elem in dec.elems.items():
        acc = {}
        for word, c in elem.items():
            term = {(): c}
            for sym in word:
                term = alg.mul(term, primed(sym))
            alg._add(acc, term, one)
        _, p1 = alg.split_kappa(alg.clean(acc))
        d = dec.decompose(p1)
        if d:
            out[X] = {Z: str(c) for Z, c in d.items()}
    return out


# ------------------------------------------------------------------------ report
def analyse(n: int) -> dict:
    out = {"n": n, "algebra": f"C({n + 1}) = osp(2|{2 * n})", "gb_count": 4 * n, "variants": {}, "profiles": {}}
    for variant in ("K", "strict", "mod_K"):
        sys_ = TrivialitySystem(n, variant)
        rank, cons, n_res = sys_.solvability_conditions()
        out["variants"][variant] = {
            "f_target": {"K": "g (+) C K", "strict": "g", "mod_K": "g (gamma projected to g)"}[variant],
            "phi_parameters": sys_.m,
            "equations": len(sys_.keys),
            "rank_D": rank,
            "independent_gb_constraints": cons,
            "trivial_subspace_dim": 4 * n - len(cons),
        }
    # explicit solutions for every Layer 3 profile (variant K) and strictness test
    for name in CE.PROFILES:
        gb, l3 = layer3_gamma_table(n, name)        # Layer 3 data (evaluated gamma)
        assert gb == CE.profile(name, n)
        rec = {"gb": {l: str(v) for l, v in gb.items()}, "layer3_file": os.path.basename(CE.evaluated_path(n, name))}
        for variant in ("K", "strict"):
            sys_ = TrivialitySystem(n, variant)
            ok, phi, bad = sys_.solve(gb)
            r = {"solvable": ok}
            if ok:
                mism = sys_.check_solution(gb, phi, gamma_table=l3)   # Layer 4 at phi == Layer 3 ?
                r["phi_nonzero"] = len(phi)
                r["recheck_mismatches"] = len(mism)
                if variant == "K":
                    r["phi"] = {k: str(v) for k, v in sorted(phi.items())}
            else:
                r["inconsistent_components"] = [{"X": k[0], "Y": k[1], "Z": k[2], "gamma_minus_deltaf": str(b)} for k, b in bad[:8]]
                r["inconsistent_count"] = len(bad)
            rec[variant] = r
        rec["gamma_K_entries"] = len([1 for (X, Y), comp in TrivialitySystem(n, "K").gamma_by_pair.items()
                                     if "K" in comp and any(Fraction(c) * gb[l] != 0 for l, c in comp["K"].items())])
        out["profiles"][name] = rec
    # closed-form candidate
    shift = {}
    for name in ("all_plus", "checkerboard", "single_pp"):
        gb = CE.profile(name, n)
        phi, residual, mism = check_shift_map(n, gb)
        shift[name] = {"kappa0_residual": len(residual), "gamma_plus_delta_f_shift_mismatches": len(mism),
                       "phi_nonzero": len(phi)}
    out["shift_map"] = {"definition": "b_j^s -> b_j^s + kappa (gb_a1p_bjs a_1_m + gb_a1m_bjs a_1_p); X' = X + kappa f_shift(X)",
                        "claim": "gamma = -delta f_shift for all gb (so gamma is trivial with f = -f_shift)",
                        "checks": shift,
                        "f_shift_symbolic": symbolic_shift_map(n)}
    return out


def write(n: int, res: dict) -> str:
    path = os.path.join(DATA_DIR, f"C_{n}_triviality.json")
    res["metadata"] = {"generated_by": "src/C_triviality.py", "generation_date": _dt.date.today().isoformat()}
    with open(path, "w") as fh:
        json.dump(res, fh, indent=1, ensure_ascii=False)
        fh.write("\n")
    return path


def print_report(res: dict):
    n = res["n"]
    print(f"=== {res['algebra']}  (4n = {res['gb_count']} gb parameters) ===")
    for v, r in res["variants"].items():
        print(f"  variant {v:7s} f: g -> {r['f_target']:28s} phi={r['phi_parameters']:4d} eqs={r['equations']:6d} "
              f"rank(D)={r['rank_D']:4d}  gb-constraints={len(r['independent_gb_constraints']):2d}  "
              f"trivial subspace dim={r['trivial_subspace_dim']}")
        for c in r["independent_gb_constraints"]:
            print("      constraint: " + " + ".join(f"({v})*{k}" for k, v in c.items()) + " = 0")
    for name, rec in res["profiles"].items():
        k, s = rec["K"], rec["strict"]
        print(f"  profile {name:13s}: with K -> {'TRIVIAL' if k['solvable'] else 'NON-TRIVIAL'}"
              f" (phi nonzero={k.get('phi_nonzero', '-')}, recheck mismatches={k.get('recheck_mismatches', '-')}) ; "
              f"strict -> {'TRIVIAL' if s['solvable'] else 'NON-TRIVIAL'}"
              f" (inconsistent components={s.get('inconsistent_count', 0)}, gamma K-pairs={rec['gamma_K_entries']})")
    for name, c in res["shift_map"]["checks"].items():
        print(f"  f_shift @ {name:13s}: kappa^0 residual={c['kappa0_residual']}, "
              f"gamma + delta f_shift mismatches={c['gamma_plus_delta_f_shift_mismatches']}")


if __name__ == "__main__":
    ns = [int(a) for a in sys.argv[1:]] or [1, 2, 3]
    for n in ns:
        res = analyse(n)
        p = write(n, res)
        print_report(res)
        print(f"  -> wrote {os.path.relpath(p, ROOT)}")
