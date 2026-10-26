#!/usr/bin/env python3
"""check_artifacts.py — Independent check of a Worker's C(n+1) artifacts.

Usage:
    python3 scripts/check_artifacts.py <WORKSPACE_DIR> [--json OUT.json]

What it checks (n = 1, 2, 3):
  1. Presence: data/C_{n}_{structure,gamma,evaluated,coboundary}*.json
     (suffixes such as _gb1 or _pos are accepted).
  2. Parse: every JSON file found anywhere in the workspace parses.
  3. Layer 1 (structure) against the unified rules of I02:
     algebra.family == "C", algebra.m == 1, algebra.n == n,
     even = 2n^2 + n + 1, odd = 4n, top-level central_elements with kappa / K,
     basis and parity consistent with these dimensions.
  4. Layer 1 algebra, if structure_constants is a list of {X, Y, Z, coeff}
     (the B(0,n) v5.0 style): graded antisymmetry and the super Jacobi
     identity, recomputed here in exact rational arithmetic.

The checker does not judge the triviality conclusion; that is a human
judgment. It reports facts for the "artifact completeness" metric.
"""
import itertools
import json
import sys
from fractions import Fraction
from pathlib import Path

LAYERS = ["structure", "gamma", "evaluated", "coboundary"]


def frac(v):
    if isinstance(v, (int, float)):
        return Fraction(v).limit_denominator(10**9)
    return Fraction(str(v).strip())


def basis_list(d):
    b = d.get("basis")
    if isinstance(b, dict) and "even" in b and "odd" in b:
        return list(b["even"]), list(b["odd"])
    par = d.get("parity")
    if isinstance(par, dict):
        return [k for k, p in par.items() if p == 0], [k for k, p in par.items() if p == 1]
    return None


def check_structure(d, n):
    out = {}
    alg = d.get("algebra", {}) if isinstance(d, dict) else {}
    out["family_C"] = alg.get("family") == "C"
    out["m_eq_1"] = alg.get("m") == 1
    out["n_matches"] = alg.get("n") == n
    dim = alg.get("dimension", {})
    out["dim_even_ok"] = dim.get("even") == 2 * n * n + n + 1
    out["dim_odd_ok"] = dim.get("odd") == 4 * n
    ce = d.get("central_elements")
    out["central_top_level"] = isinstance(ce, dict) and "kappa" in ce and "K" in ce
    bl = basis_list(d)
    if bl:
        ev, od = bl
        out["basis_even_count_ok"] = len(ev) == 2 * n * n + n + 1
        out["basis_odd_count_ok"] = len(od) == 4 * n
    else:
        out["basis_even_count_ok"] = out["basis_odd_count_ok"] = None
    out.update(check_algebra(d, bl))
    return out


def check_algebra(d, bl):
    sc = d.get("structure_constants")
    if not (bl and isinstance(sc, list) and sc and all(isinstance(e, dict) and {"X", "Y", "Z", "coeff"} <= set(e) for e in sc)):
        return {"algebra_check": "skipped (format not recognised)"}
    ev, od = bl
    par = {x: 0 for x in ev}
    par.update({x: 1 for x in od})
    br = {}
    try:
        for e in sc:
            c = frac(e["coeff"])
            if c != 0:
                key = (e["X"], e["Y"])
                br.setdefault(key, {})
                br[key][e["Z"]] = br[key].get(e["Z"], 0) + c
    except Exception as ex:  # noqa: BLE001
        return {"algebra_check": f"skipped (coeff parse error: {ex})"}
    if any(z not in par for v in br.values() for z in v) or any(x not in par or y not in par for x, y in br):
        return {"algebra_check": "skipped (labels outside basis; central terms?)"}
    basis = ev + od

    def bracket(x, y):
        if (x, y) in br:
            return dict(br[(x, y)])
        if (y, x) in br:  # fill from graded antisymmetry
            s = -((-1) ** (par[x] * par[y]))
            return {z: s * c for z, c in br[(y, x)].items()}
        return {}

    def bracket_vec(x, v):
        r = {}
        for y, c in v.items():
            for z, cz in bracket(x, y).items():
                r[z] = r.get(z, 0) + c * cz
        return {k: c for k, c in r.items() if c != 0}

    anti_bad = 0
    for (x, y), v in br.items():
        if (y, x) in br:
            s = -((-1) ** (par[x] * par[y]))
            w = br[(y, x)]
            if any(v.get(z, 0) != s * w.get(z, 0) for z in set(v) | set(w)):
                anti_bad += 1
    jac_bad = 0
    for x, y, z in itertools.product(basis, repeat=3):
        # [x,[y,z]] = [[x,y],z] + (-1)^{p(x)p(y)} [y,[x,z]]
        lhs = bracket_vec(x, bracket(y, z))
        t1 = {}
        for w, c in bracket(x, y).items():
            for u, cu in bracket(w, z).items():
                t1[u] = t1.get(u, 0) + c * cu
        t2 = bracket_vec(y, bracket(x, z))
        s = (-1) ** (par[x] * par[y])
        if any(lhs.get(u, 0) != t1.get(u, 0) + s * t2.get(u, 0) for u in set(lhs) | set(t1) | set(t2)):
            jac_bad += 1
    return {"antisymmetry_violations": anti_bad, "jacobi_violations": jac_bad,
            "algebra_check": "pass" if anti_bad == 0 and jac_bad == 0 else "FAIL"}


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    ws = Path(sys.argv[1])
    report = {"workspace": str(ws), "layers": {}, "json_parse_errors": [], "json_files": []}
    for f in sorted(ws.rglob("*.json")):
        if ".git" in f.parts:
            continue
        rel = str(f.relative_to(ws))
        report["json_files"].append(rel)
        try:
            json.loads(f.read_text())
        except Exception as ex:  # noqa: BLE001
            report["json_parse_errors"].append(f"{rel}: {ex}")
    for n in (1, 2, 3):
        row = {}
        for L in LAYERS:
            hits = sorted((ws / "data").glob(f"C_{n}_{L}*.json")) if (ws / "data").is_dir() else []
            row[L] = [str(h.relative_to(ws)) for h in hits]
        s = [h for h in row["structure"] if h.endswith("_structure.json")] or row["structure"]
        if s:
            try:
                row["structure_check"] = check_structure(json.loads((ws / s[0]).read_text()), n)
            except Exception as ex:  # noqa: BLE001
                row["structure_check"] = {"error": str(ex)}
        report["layers"][n] = row
    complete = all(report["layers"][n][L] for n in (1, 2, 3) for L in LAYERS)
    report["four_layers_complete"] = complete

    print(f"# Artifact check: {ws}\n")
    print("| n | structure | gamma | evaluated | coboundary | Layer-1 algebra |")
    print("|---|---|---|---|---|---|")
    for n in (1, 2, 3):
        r = report["layers"][n]
        cells = ["yes" if r[L] else "—" for L in LAYERS]
        alg = r.get("structure_check", {}).get("algebra_check", "—")
        print(f"| {n} | " + " | ".join(cells) + f" | {alg} |")
    print(f"\nFour layers complete for n=1,2,3: {complete}")
    print(f"JSON files found: {len(report['json_files'])}; parse errors: {len(report['json_parse_errors'])}")
    for n in (1, 2, 3):
        sc = report["layers"][n].get("structure_check")
        if sc:
            bad = {k: v for k, v in sc.items() if v is False}
            print(f"n={n} Layer-1 rule failures: {', '.join(bad) if bad else 'none'}")
    if "--json" in sys.argv:
        Path(sys.argv[sys.argv.index("--json") + 1]).write_text(json.dumps(report, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
