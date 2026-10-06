#!/usr/bin/env python3
"""
Export machine-readable artifacts for C(n+1) = osp(2|2n), n = 1,2,3:

  artifacts/Cn1_structure_n<N>.json
      basis            : labels + parities of the super-symmetrised basis Z_a
      structure_constants : C0[a][b][c], the UNDEFORMED bracket of C(n+1)
      gamma            : gamma[a][b][c], affine-linear in the gb parameters
      trivialiser_phi  : phi[i][j] = coeff of Z_i in f(Z_j), linear in gb,
                         the explicit odd map with  gamma = - delta f
      twist_T          : the generating odd map T : V -> V

Linear forms in gb are encoded as  {"<symbol>": "<rational>", ...}, where the
key "1" denotes the constant term.  All values are exact rationals as strings.

Re-verification from these files alone:  python3 verify_artifacts.py
"""
from fractions import Fraction
import json
import sys

from osp_algebra import ZERO, ONE, const
from osp_deformation import Deformation

NMAX = int(sys.argv[1]) if len(sys.argv) > 1 else 3


def enc(lin):
    out = {}
    for k, v in lin.items():
        if v:
            out["1" if k is None else k] = str(v)
    return out


for n in range(1, NMAX + 1):
    D = Deformation(n, section="SYM").compute()
    D0 = Deformation(n, gb={k: ZERO for k in D.A.gb}, section="SYM").compute()
    d = D.dim

    Zt = D.twisted_Z()
    phi = [[ZERO] * d for _ in range(d)]
    from osp_algebra import sub
    for a in range(d):
        C, G, tau, sg = D.decompose(sub(Zt[a], D.Z[a]))
        for i in range(d):
            phi[i][a] = G[i]

    T = D.twist_T()
    twist = {}
    for i, img in T.items():
        if not img:
            continue
        twist[D.A.names[i]] = {D.A.names[w[0]]: enc(c) for (w, k), c in img.items()}

    data = {
        "algebra": f"C({n+1}) = osp(2|{2*n})",
        "n": n,
        "dim": d,
        "dim_even": sum(1 for p in D.zpar if p == 0),
        "dim_odd": sum(1 for p in D.zpar if p == 1),
        "conventions": {
            "basis": "Z_{ij} = (1/2)(v_i v_j + (-1)^{p_i p_j} v_j v_i), i<=j, "
                     "omitting i=j with p_i=1; super-symmetrised INSIDE the "
                     "deformed algebra (section SYM)",
            "generators_V": D.A.names,
            "parities_V": D.A.par,
            "relations": "v_i v_j - (-1)^{p_i p_j} v_j v_i = omega_ij + mu_ij kappa, "
                         "K = 1, kappa odd central, kappa^2 = 0",
            "mu": "mu(b_j^s, a^sigma) = -gb[sigma,j,s] = -mu(a^sigma, b_j^s)",
            "bracket": "[Z_a, Z_b] = sum_c C_ab^c Z_c + kappa sum_c gamma_ab^c Z_c",
            "coboundary": "(delta f)(X,Y) = (-1)^{p(X)}[X,f(Y)] "
                          "- (-1)^{(p(X)+1)p(Y)}[Y,f(X)] - f([X,Y])",
            "theorem": "gamma_gb = - delta f for the phi recorded below, for ALL gb",
        },
        "basis": [{"index": a, "label": D.labels[a], "parity": D.zpar[a],
                   "pair": [D.A.names[i], D.A.names[j]]}
                  for a, (i, j) in enumerate(D.pairs)],
        "gb_parameters": [f"gb[{s},{j},{t}]" for (s, j, t) in
                          sorted(D.A.gb.keys(), key=lambda t: (t[1], t[0], t[2]))],
        "structure_constants": {
            f"{a},{b},{c}": str(D0.C[a][b][c].get(None, Fraction(0)))
            for a in range(d) for b in range(d) for c in range(d)
            if not D0.C[a][b][c].is_zero()},
        "gamma": {f"{a},{b},{c}": enc(D.G[a][b][c])
                  for a in range(d) for b in range(d) for c in range(d)
                  if not D.G[a][b][c].is_zero()},
        "trivialiser_phi": {f"{i},{j}": enc(phi[i][j])
                            for i in range(d) for j in range(d)
                            if not phi[i][j].is_zero()},
        "twist_T": twist,
    }
    path = f"../artifacts/Cn1_structure_n{n}.json"
    with open(path, "w") as fh:
        json.dump(data, fh, indent=1)
    print(f"wrote {path}: dim={d}, "
          f"{len(data['structure_constants'])} structure constants, "
          f"{len(data['gamma'])} gamma entries, "
          f"{len(data['trivialiser_phi'])} phi entries")
