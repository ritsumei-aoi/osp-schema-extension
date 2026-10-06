"""
Produces verification/artifacts_n{1,2,3}.json and verification/summary.json.

For each n:
  (A) generic exact linear-algebra test (no ansatz): dim{gb : gamma_gb in im(delta)} == 4n ?
  (B) explicit witness: f_lambda = odd derivation D of S(V) with D(a^s) = sum_{j,t} t*gb_{s,j,t} b_j^{-t},
      D(b) = 0, restricted to g = S^2 V.  Check delta f_lambda == gamma_gb exactly for random integer gb.
  (C) uniqueness: ker(delta) on odd f has dim = dim g_odd (inner: ad of odd elements).
"""
import json, random, sys
from fractions import Fraction as Fr
from cn1_triviality import (analyse, structure, delta_columns, label, build_letters, P)


def witness_check(n, seed):
    rnd = random.Random(seed)
    names = [(s, j, t) for j in range(1, n + 1) for s in "+-" for t in "+-"]
    gb = {nm: rnd.randint(-5, 5) for nm in names}
    basis, par, S = structure(n, gb)
    _, _, S0 = structure(n, {})
    N = len(basis)
    pos = {}
    for i, (x, y) in enumerate(basis):
        pos[(x, y)] = i
        pos[(y, x)] = i
    # D(a^s) = sum_{j,t} t*gb[s,j,t] * b_j^{-t}
    ell = {}
    for s in "+-":
        v = {}
        for j in range(1, n + 1):
            for t in "+-":
                sign = 1 if t == "+" else -1
                other = "-" if t == "+" else "+"
                v[("b", other, j)] = sign * gb[(s, j, t)]
        ell[("a", s, 0)] = v
    phi = {}
    for i, (x, y) in enumerate(basis):  # D(xy) = D(x)y + (-1)^{|x|} x D(y)
        for (u, w, sg) in [(x, y, 1), (y, x, (-1) ** (1 if x[0] == "a" else 0))]:
            pass
        if x in ell:
            for b, c in ell[x].items():
                phi[(pos[(b, y)], i)] = phi.get((pos[(b, y)], i), 0) + c
        if y in ell:
            sg = -1 if x[0] == "a" else 1
            for b, c in ell[y].items():
                phi[(pos[(x, b)], i)] = phi.get((pos[(x, b)], i), 0) + sg * c
    c0 = {ij: K for ij, (K, kap) in S0.items()}
    unk, rows = delta_columns(N, par, c0)
    uidx = {u: t for t, u in enumerate(unk)}
    delta = {}
    for u, d in rows.items():
        pass
    for key, d in rows.items():
        for (k, m), v in phi.items():
            u = uidx[(k, m)]
            if u in d:
                delta[key] = delta.get(key, 0) + d[u] * v
    delta = {k: v for k, v in delta.items() if v}
    gamma = {(i, j, k): v for (i, j), (K, kap) in S.items() for k, v in kap.items()}
    ok = (delta == gamma)
    return ok, gb, len(gamma), phi, basis


def main(ns):
    summary = {}
    for n in ns:
        res, ctx = analyse(n)
        ok, gb, ngam, phi, basis = witness_check(n, 1000 + n)
        res["explicit_witness_delta_f_equals_gamma_generic_gb"] = ok
        res["generic_gb_used"] = {f"{s},{j},{t}": v for (s, j, t), v in gb.items()}
        res["dim_ker_delta_odd"] = res["n_unknown_phi"] - res["rank_delta"]
        res["dim_ker_delta_equals_dim_g_odd"] = (res["dim_ker_delta_odd"] == res["dim_odd"])
        summary[f"n={n}"] = res
        art = dict(
            n=n,
            conventions="kappa written to the LEFT: [X,Y]_gamma = [X,Y]_0 + kappa*gamma(X,Y); "
                        "basis = super-Weyl-symmetrised quadratics sym(xy); [b_j^s,a^sigma] = -gb[sigma,j,s]*kappa",
            basis=[label(b) for b in ctx["basis"]], parity=ctx["par"],
            structure_constants_c0={f"{i},{j}": {str(k): str(v) for k, v in K.items()}
                                    for (i, j), K in ctx["c0"].items()},
            gamma_unit={f"{s},{j},{t}": {f"{i},{jj},{k}": str(v) for (i, jj, k), v in g.items()}
                        for (s, j, t), g in ctx["gam"].items()},
            witness_f_for_generic_gb={f"{k},{m}": str(v) for (k, m), v in phi.items()},
            witness_gb=res["generic_gb_used"],
            result=res)
        with open(f"artifacts_n{n}.json", "w") as fh:
            json.dump(art, fh, separators=(",", ":"))
        print(json.dumps(res), flush=True)
    with open("summary.json", "w") as fh:
        json.dump(summary, fh, indent=1)


if __name__ == "__main__":
    main([int(a) for a in sys.argv[1:]] or [1, 2, 3])
