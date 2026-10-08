#!/usr/bin/env python3
"""
run_verification.py -- generates the verification artifacts for the triviality analysis of the
inhomogeneous (gb) deformation of C(n+1) = osp(2|2n), n = 1, 2, 3.

Usage:  python3 verification/run_verification.py [n ...]        (default: 1 2 3)
Output: verification/artifacts/osp2_2n_n{n}.json  and a summary on stdout.

For each n the script
  1. builds the basis of g = osp(2|2n) (docs/math/Cn1_definition.md) inside the deformed oscillator
     algebra U(A') and extracts the structure constants  c_ab^k  (undeformed) and the cocycle
     gamma_ab^k (coefficient of kappa), exactly, as linear forms in the 4n parameters gb;
  2. checks closure [g,g] in g, that gamma is linear in gb and that gamma mod scalars is a 2-cocycle;
  3. constructs the explicit odd map f_gb (kappa-part of  Phi: a^s -> a^s + kappa u^s)  and verifies
       (i)  gamma_gb = delta f_gb   EXACTLY in ghat = g + C.1          (f_gb : g -> ghat)
       (ii) gamma_gb = delta f_gb   modulo scalars                       (f_gb : g -> g)
     for ALL gb simultaneously (identity of polynomials in gb);
  4. independently solves the linear system  delta f = gamma_gb  by rank computations (mod two
     primes and in floating point) under the three readings of the equality:
       R1  modulo scalars (adjoint representation)             [docs/math/C_coboundary_definition.md]
       R2  exact in ghat with f allowed to take scalar values
       R3  exact in ghat with f : g -> g (no scalar values)
     and reports the dimension of the space of admissible gb under each reading;
  5. computes dim H^2_odd(g, g) for n = 1, 2 (context only).
"""
import json
import os
import sys
import time
from fractions import Fraction

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from osp_deform import (compute_structure, coboundary, explicit_f, check_phi_relations, jacobi_defect,
                        coboundary_system, rank_mod_p, to_int_rows, odd_H2, vec_to_sparse)


def float_rank(rows):
    import numpy as np
    if not rows:
        return 0
    M = np.array(rows, dtype=float)
    return int(np.linalg.matrix_rank(M))


def analyse(n, do_H2):
    t0 = time.time()
    B, dec, c, gamma, names = compute_structure(n)
    dim = len(B)
    par = [p for _, _, p, _ in B]
    report = {"n": n, "algebra": f"C({n + 1}) = osp(2|{2 * n})", "dim_g": dim,
              "dim_g_even": sum(1 for p in par if p == 0), "dim_g_odd": sum(1 for p in par if p == 1),
              "gb_parameters": names, "conventions": {
                  "K": "set to 1 (quotient of U(A) by K-1)",
                  "kappa": "odd central, kappa^2 = 0",
                  "deformed_relation": "[b_j^s, a^sigma] = - gb[sigma][j][s] * kappa",
                  "coboundary": "(df)(X,Y) = (-1)^{p(X)}[X,f(Y)] - (-1)^{(p(X)+1)p(Y)}[Y,f(X)] - f([X,Y])",
                  "ghat": "g + C.1 = span of all quadratic oscillator monomials; g = [ghat,ghat]",
                  "basis_order": [nm for nm, _, _, _ in B],
                  "vector_coordinates": "dicts keyed by basis name; key '1' = scalar (unit) component"}}
    report["basis"] = [{"index": i, "name": nm, "parity": p, "root": r,
                        "oscillator_expression": {" ".join("kappa" if g == ('k',) else
                                                            (f"a{g[1]}" if g[0] == 'a' else f"b{g[1]}{g[2]}")
                                                            for g in w) or "1": str(cf[()]) for w, cf in X.items()}}
                       for i, (nm, X, p, r) in enumerate(B)]

    # ---- 1. structure constants and gamma -------------------------------------------------------------
    sc = []
    for (i, j), v in c.items():
        for k in range(dim):
            if v[k] != 0:
                sc.append([B[i][0], B[j][0], B[k][0], str(v[k])])
    report["structure_constants"] = {"format": "[Z_a, Z_b] = sum_k value * Z_k ; entries [a, b, k, value]",
                                     "entries": sc}
    gm = []
    gm_scalar = []
    for (i, j), d in gamma.items():
        for nm, v in d.items():
            for k in range(dim + 1):
                if v[k] != 0:
                    (gm if k < dim else gm_scalar).append([B[i][0], B[j][0], B[k][0] if k < dim else "1", nm, str(v[k])])
    report["gamma"] = {"format": "[Z_a,Z_b]_deformed = [Z_a,Z_b]_0 + kappa * sum_k (sum_gb value*gb) Z_k ; "
                                 "entries [a, b, k, gb_name, value]",
                       "entries_in_g": gm, "entries_scalar": gm_scalar}

    # ---- 2. consistency checks ---------------------------------------------------------------------------
    checks = {}
    checks["closure_[g,g]_in_g"] = True        # asserted inside compute_structure
    checks["gamma_linear_in_gb"] = True        # asserted inside compute_structure
    checks["gamma_parity_odd"] = all(
        all(v[k] == 0 for k in range(dim) if par[k] != (par[i] + par[j] + 1) % 2)
        for (i, j), d in gamma.items() for v in d.values())
    checks["gamma_super_skew"] = all(
        all(gamma[(i, j)].get(nm, [0] * (dim + 1))[k] == -((-1) ** (par[i] * par[j])) * gamma[(j, i)].get(nm, [0] * (dim + 1))[k]
            for nm in names for k in range(dim + 1))
        for i in range(dim) for j in range(dim))
    # cocycle condition for each gb-direction separately (gamma is linear in gb)
    bad = 0
    for nm in names:
        gv = {(i, j): gamma[(i, j)].get(nm, [Fraction(0)] * (dim + 1))[:dim] for i in range(dim) for j in range(dim)}
        bad += jacobi_defect(B, c, gv)
    checks["gamma_mod_scalars_is_2cocycle"] = (bad == 0)
    checks["jacobi_failures"] = bad
    checks["Phi_preserves_oscillator_relations"] = check_phi_relations(n)

    # ---- 3. explicit f and the identity gamma = delta f ---------------------------------------------------
    f = explicit_f(B, dec, n)
    df = coboundary(B, c, f, names)
    zero = [Fraction(0)] * (dim + 1)
    exact = all(df[(i, j)].get(nm, zero) == gamma[(i, j)].get(nm, zero)
                for i in range(dim) for j in range(dim) for nm in names)
    checks["gamma_equals_delta_f_exactly_in_ghat"] = exact
    f_g = {j: {nm: v[:dim] + [Fraction(0)] for nm, v in d.items()} for j, d in f.items()}
    df_g = coboundary(B, c, f_g, names)
    mod = all(df_g[(i, j)].get(nm, zero)[:dim] == gamma[(i, j)].get(nm, zero)[:dim]
              for i in range(dim) for j in range(dim) for nm in names)
    checks["gamma_equals_delta_f_mod_scalars_with_f_g_to_g"] = mod
    checks["f_is_odd"] = all(all(v[i] == 0 for i in range(dim) if par[i] == par[j]) for j, d in f.items() for v in d.values())
    fe = []
    for j, d in f.items():
        for nm, v in d.items():
            for i in range(dim + 1):
                if v[i] != 0:
                    fe.append([B[j][0], B[i][0] if i < dim else "1", nm, str(v[i])])
    report["explicit_f"] = {"definition": "f_gb(Z) = kappa-coefficient of Phi(Z), Phi(a^s) = a^s + kappa*sum_j(-gb[s][j][-] b_j^+ + gb[s][j][+] b_j^-), Phi(b)=b",
                            "format": "f(Z_j) = sum_i value*gb * Z_i ; entries [j, i, gb_name, value]",
                            "entries": fe,
                            "scalar_part_f_C": {B[j][0]: {nm: str(v[dim]) for nm, v in d.items() if v[dim] != 0}
                                                for j, d in f.items() if any(v[dim] != 0 for v in d.values())}}

    # ---- 4. independent linear-algebra solution of delta f = gamma ------------------------------------------
    rank_results = {}
    for label, incl_scalar_rows, allow_scalar_f in [("R1_mod_scalars", False, False),
                                                  ("R2_exact_f_into_ghat", True, True),
                                                  ("R3_exact_f_into_g", True, False)]:
        unknowns, rows_A, rows_G = coboundary_system(B, c, gamma, names, incl_scalar_rows, allow_scalar_f)
        nA = len(unknowns)
        rows_AG = [dict(ra) | {nA + t: v for t, v in rg.items()} for ra, rg in zip(rows_A, rows_G)]
        res = {"num_unknowns_phi": nA, "num_equations": len(rows_A)}
        rks = {}
        for p in (1000003, 998244353):
            rA = rank_mod_p(to_int_rows(rows_A, nA), nA, p=p)
            rAG = rank_mod_p(to_int_rows(rows_AG, nA + len(names)), nA + len(names), p=p)
            rks[f"mod_{p}"] = {"rank_A": rA, "rank_[A|Gamma]": rAG}
        if len(rows_A) * (nA + len(names)) <= 60_000_000:
            rks["float"] = {"rank_A": float_rank(list(to_int_rows(rows_A, nA))),
                            "rank_[A|Gamma]": float_rank(list(to_int_rows(rows_AG, nA + len(names))))}
        res["ranks"] = rks
        rA, rAG = rks["mod_1000003"]["rank_A"], rks["mod_1000003"]["rank_[A|Gamma]"]
        res["codim_of_admissible_gb"] = rAG - rA
        res["dim_admissible_gb_subspace"] = len(names) - (rAG - rA)
        res["dim_solution_space_of_f_for_fixed_gb (= dim Z^1_odd)"] = len(unknowns) - rA
        res["all_gb_trivial"] = (rAG == rA)
        rank_results[label] = res
    report["linear_system"] = rank_results

    # R3 explicit conditions: gamma_C(a,b) = 0 for all a,b  (scalar part of gamma must vanish)
    conds = {}
    for (i, j), d in gamma.items():
        form = {nm: str(v[dim]) for nm, v in d.items() if v[dim] != 0}
        if form:
            conds[f"gamma_C({B[i][0]},{B[j][0]})"] = form
    report["R3_scalar_part_conditions"] = {"explanation": "under R3 one needs gamma_C(a,b) = 0 for all a,b; "
                                                          "these are the linear forms (in gb) that must vanish",
                                           "forms": conds}
    # the linear span of these forms
    vecs = []
    for (i, j), d in gamma.items():
        row = [d.get(nm, zero)[dim] for nm in names]
        if any(row):
            vecs.append(row)
    report["R3_scalar_part_conditions"]["rank_of_conditions"] = rank_mod_p(to_int_rows(vecs), len(names)) if vecs else 0

    # ---- 5. H^2 odd ----------------------------------------------------------------------------------------
    if do_H2:
        report["odd_cohomology_H2(g,Pi g)"] = odd_H2(B, c)
    report["checks"] = checks
    report["elapsed_seconds"] = round(time.time() - t0, 1)
    return report


def main():
    ns = [int(x) for x in sys.argv[1:]] or [1, 2, 3]
    here = os.path.dirname(os.path.abspath(__file__))
    outdir = os.path.join(here, "artifacts")
    os.makedirs(outdir, exist_ok=True)
    summary = {}
    for n in ns:
        rep = analyse(n, do_H2=(n <= 2))
        path = os.path.join(outdir, f"osp2_2n_n{n}.json")
        with open(path, "w") as fh:
            json.dump(rep, fh, indent=1)
        s = {"dim_g": rep["dim_g"], "checks": rep["checks"],
             "linear_system": {k: {kk: vv for kk, vv in v.items() if kk != "ranks"} | {"ranks": v["ranks"]}
                               for k, v in rep["linear_system"].items()},
             "R3_rank_of_scalar_conditions": rep["R3_scalar_part_conditions"]["rank_of_conditions"],
             "elapsed_seconds": rep["elapsed_seconds"]}
        if "odd_cohomology_H2(g,Pi g)" in rep:
            s["odd_cohomology_H2(g,Pi g)"] = rep["odd_cohomology_H2(g,Pi g)"]
        summary[n] = s
        print(f"=== n = {n}: {rep['algebra']}, dim g = {rep['dim_g']}  ({rep['elapsed_seconds']} s) ===")
        print(json.dumps(s, indent=1))
    with open(os.path.join(outdir, "summary.json"), "w") as fh:
        json.dump(summary, fh, indent=1)


if __name__ == "__main__":
    main()
