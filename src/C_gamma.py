"""Schema 2 (inhomogeneous deformation / gamma structure) for C(n+1) = osp(2|2n).

Deformation (docs/math/C_inhomogeneous_definition.md):  [b_j^s, a_1^sigma] = -gb_{sigma,j,s} kappa.
For generators X, Y (oscillator quadratics) the bracket computed in U(A) is
    [X, Y]_gamma = [X, Y]_0 + kappa * ( gamma(X, Y) + gamma_K(X, Y) K ),
gamma(X, Y) in g (linear in gb), gamma_K the central (kappa K) component.

Usage:  python3 src/C_gamma.py        (writes data/C_{1,2,3}_gamma.json)
"""
import datetime
import json
import os
import sys
from fractions import Fraction

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from C_generators import DATA, make_algebra, write_json  # noqa: E402
from C_oscillator import ONE, lin_add, lin_from_json, lin_scale, lin_str  # noqa: E402


def gb_matrix(n):
    cols = [f"b_{j}_{s}" for j in range(1, n + 1) for s in "pm"]
    rows = ["a_1_p", "a_1_m"]
    sym = [[f"gb_a1{r[-1]}_b{c.split('_')[1]}{c[-1]}" for c in cols] for r in rows]
    return rows, cols, sym


def compute_gamma(n):
    """Returns (alg, undeformed {(X,Y): {Z: Fraction}}, gamma {(X,Y): {Z: Lin}}, central {(X,Y): Lin})."""
    alg = make_algebra(n, deformed=True)
    sc0, gam, cen = {}, {}, {}
    for x in alg.basis:
        for y in alg.basis:
            dec = alg.decompose(alg.bracket_labels(x, y))
            p0 = dec.get(0, {})
            assert "K" not in p0
            assert all(set(v) == {ONE} for v in p0.values()), "gb leaked into kappa^0 part"
            if p0:
                sc0[(x, y)] = {z: v[ONE] for z, v in p0.items()}
            p1 = dict(dec.get(1, {}))
            k = p1.pop("K", None)
            assert all(ONE not in v for v in p1.values()), "kappa term without gb"
            if p1:
                gam[(x, y)] = p1
            if k:
                cen[(x, y)] = k
    return alg, sc0, gam, cen


# ------------------------------------------------------------------ consistency checks
def load_schema1(n):
    with open(os.path.join(DATA, f"C_{n}_structure.json")) as fh:
        d = json.load(fh)
    sc = {}
    for e in d["structure_constants"]:
        sc.setdefault((e["X"], e["Y"]), {})[e["Z"]] = Fraction(e["coeff"])
    return d, sc


def _add(acc, key, c):
    v = lin_add(acc.get(key, {}), c)
    if v:
        acc[key] = v
    else:
        acc.pop(key, None)


def L_bracket(sc, gam, cen, parity, x, u):
    """[x, u]_gamma in L = g + kappa(g + C K), x a basis label of g,
    u = (g-part {Z: Fraction}, kappa-part {Z|'K': Lin}).
    [x, kappa W] = (-1)^{p(x)} kappa [x, W]_0 ; [x, kappa K] = 0."""
    g_out, k_out = {}, {}
    gpart, kpart = u
    for z, c in gpart.items():
        for w, v in sc.get((x, z), {}).items():
            g_out[w] = g_out.get(w, 0) + c * v
        for w, v in gam.get((x, z), {}).items():
            _add(k_out, w, lin_scale(v, c))
        if (x, z) in cen:
            _add(k_out, "K", lin_scale(cen[(x, z)], c))
    s = (-1) ** parity[x]
    for z, c in kpart.items():
        if z == "K":
            continue
        for w, v in sc.get((x, z), {}).items():
            _add(k_out, w, lin_scale(c, s * v))
    return {k: v for k, v in g_out.items() if v}, k_out


def deformed_jacobi_failures(n, sc, gam, cen, parity, basis, with_central=True):
    """Super Jacobi of [,]_gamma on all basis triples of g, to first order in kappa
    (equivalent to the cocycle condition for gamma; with_central adds the kappa K part)."""
    if not with_central:
        cen = {}
    fails = []
    for x in basis:
        for y in basis:
            for z in basis:
                px, py, pz = parity[x], parity[y], parity[z]
                tg, tk = {}, {}
                for sgn, a, b, c in (((-1) ** (px * pz), x, y, z),
                                     ((-1) ** (py * px), y, z, x),
                                     ((-1) ** (pz * py), z, x, y)):
                    inner = (dict(sc.get((b, c), {})), dict(gam.get((b, c), {})))
                    if (b, c) in cen:
                        inner[1]["K"] = cen[(b, c)]
                    g_o, k_o = L_bracket(sc, gam, cen, parity, a, inner)
                    for w, v in g_o.items():
                        tg[w] = tg.get(w, 0) + sgn * v
                    for w, v in k_o.items():
                        _add(tk, w, lin_scale(v, sgn))
                tg = {k: v for k, v in tg.items() if v}
                if tg or tk:
                    fails.append((x, y, z, tg, tk))
    return fails


def build_schema2(n):
    alg, sc0, gam, cen = compute_gamma(n)
    d1, sc_file = load_schema1(n)
    rows, cols, sym = gb_matrix(n)
    assert sorted(x for r in sym for x in r) == sorted(alg.osc.gb_names())
    checks = {}
    checks["undeformed_part_equals_schema1"] = (sc0 == sc_file)
    checks["gamma_parity_odd"] = all(
        alg.parity[z] == (alg.parity[x] + alg.parity[y] + 1) % 2 for (x, y), r in gam.items() for z in r)
    checks["central_only_for_mixed_parity"] = all(
        (alg.parity[x] + alg.parity[y]) % 2 == 1 for (x, y) in cen)
    anti = True
    for (x, y), r in list(gam.items()) + [((a, b), {"K": v}) for (a, b), v in cen.items()]:
        other = dict(gam.get((y, x), {}))
        if (y, x) in cen:
            other["K"] = cen[(y, x)]
        # gamma inherits graded antisymmetry of the bracket: kappa gamma(X,Y) = -(-1)^{pxpy} kappa gamma(Y,X)
        s = -(-1) ** (alg.parity[x] * alg.parity[y])
        for z, v in r.items():
            if lin_add(v, lin_scale(other.get(z, {}), s), -1):
                anti = False
    checks["gamma_graded_antisymmetric"] = anti
    jac_g = deformed_jacobi_failures(n, sc_file, gam, cen, alg.parity, alg.basis, with_central=False)
    jac_full = deformed_jacobi_failures(n, sc_file, gam, cen, alg.parity, alg.basis, with_central=True)
    checks["cocycle_gamma_g_valued_failures"] = len(jac_g)
    checks["cocycle_gamma_with_central_failures"] = len(jac_full)
    checks["linear_in_gb"] = all(k in alg.osc.gb_names() for r in gam.values() for v in r.values() for k in v)

    gamma_list = [{"X": x, "Y": y, "Z": z, "coeff": lin_str(gam[(x, y)][z])}
                  for x in alg.basis for y in alg.basis if (x, y) in gam
                  for z in alg.basis if z in gam[(x, y)]]
    central_list = [{"X": x, "Y": y, "coeff": lin_str(cen[(x, y)])}
                    for x in alg.basis for y in alg.basis if (x, y) in cen]
    obj = {
        "schema_version": "5.0",
        "layer": 2,
        "algebra": d1["algebra"],
        "central_elements": d1["central_elements"],
        "basis": d1["basis"],
        "parity": d1["parity"],
        "inhomogeneous_deformation": {
            "description": "Inhomogeneous (gb) deformation of C(n+1) obtained from the deformed "
                           "mixed relation of the oscillator algebra",
            "deformed_relation": "[b_j^s, a_1^σ] = -gb_{σ,j,s} κ",
            "bracket_form": "[X,Y]_γ = [X,Y]_0 + κ (γ(X,Y) + γ_K(X,Y) K), κ on the left",
            "gb_matrix": {
                "shape": [2, 2 * n],
                "rows": rows,
                "columns": cols,
                "symbols": sym,
                "parameter_type": "scalar (even) coefficient; the deformation term κ·gb is odd",
            },
            "parameters": [s for r in sym for s in r],
            "gamma_parity": "p(γ(X,Y)) = p(X) + p(Y) + 1",
            "pair_coverage": "all ordered pairs (X, Y); only non-zero coefficients listed",
            "gamma_coefficients": gamma_list,
            "gamma_central": central_list,
        },
        "consistency_checks": checks,
        "metadata": {
            "generated_by": "src/C_gamma.py",
            "generation_date": datetime.date.today().isoformat(),
            "source_schema1": f"C_{n}_structure.json",
            "conventions": "handover/notation.md",
        },
    }
    return obj


def main(ns=(1, 2, 3)):
    for n in ns:
        obj = build_schema2(n)
        p = write_json(obj, f"C_{n}_gamma.json")
        idf = obj["inhomogeneous_deformation"]
        print(f"n={n}: gamma entries={len(idf['gamma_coefficients'])}, central entries="
              f"{len(idf['gamma_central'])}, checks={obj['consistency_checks']} -> {p}")


if __name__ == "__main__":
    main()
