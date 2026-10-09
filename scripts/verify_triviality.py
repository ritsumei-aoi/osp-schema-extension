"""
Driver: triviality analysis of the inhomogeneous (gb) deformation of
C(n+1) = osp(2|2n) for n = 1, 2, 3.

For each n it
  1. computes the undeformed structure constants c_ij^k and the deformation
     cocycle gamma_gb (g-valued part and scalar part) in U(A_gb);
  2. constructs the explicit odd map f induced by the oscillator change of
     variables  a^sigma -> a^sigma + kappa u^sigma  and verifies
        gamma_gb = delta f   (g-valued part, exactly)   and
        gamma_gb^scalar(X,Y) = - f''([X,Y])              (scalar part);
  3. independently solves the linear system  delta phi = gamma_gb  for an
     unknown odd map phi, one system per gb direction, and reports the
     dimension of the solution space (= dim of odd derivations);
  4. checks that gamma_gb is a 2-cocycle (d gamma_gb = 0);
  5. computes dim H^2(g, Pi g) (odd second cohomology) block by block in
     the Cartan weight decomposition, and dim ker(delta) on odd 1-cochains;
  6. repeats 1-2 with the super-symmetrised ordering of the odd generators,
     where the scalar parts vanish identically;
  7. writes everything to artifacts/Cn1_triviality_n{n}.json.
"""
from __future__ import annotations

import json
import os
import sys
import time
from fractions import Fraction

sys.path.insert(0, os.path.dirname(__file__))
from osp_deformation import (  # noqa: E402
    Cn1, Poly, ZERO, Echelon, delta_f, d2, _acc,
)

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ART = os.path.join(ROOT, "artifacts")
os.makedirs(ART, exist_ok=True)


def fr(x):
    return str(x)


def explicit_f(cn: Cn1):
    """
    Change of variables  a~^sigma = a^sigma + kappa u^sigma,
       u^sigma = sum_j ( gb_{sigma,j,-} b_j^+  -  gb_{sigma,j,+} b_j^- ),
    chosen so that [b_j^s, a~^sigma] = 0 in U(A_gb).
    Then Z~_i := Z_i(a~) = Z_i + kappa g(Z_i) satisfy the undeformed relations,
    and gamma_gb = delta f with  f = -g  (g-part) and f'' = -g'' (scalar part).
    Returns (f, f2, checks) where f[(m,i)] and f2[i] are Poly (linear in gb).
    """
    A = cn.A
    n = cn.n
    u = {}
    for sigma in "+-":
        e = {}
        for j in range(1, n + 1):
            _acc(e, (0, A.b(j, "+")), Poly.var(A.gb_index[(sigma, j, "-")]))
            _acc(e, (0, A.b(j, "-")), -Poly.var(A.gb_index[(sigma, j, "+")]))
        u[sigma] = e
    ap = A.add(A.gen(1), u["+"])
    am = A.add(A.gen(2), u["-"])
    checks = {}
    # the new generators satisfy the UNDEFORMED relations inside U(A_gb)
    ok = True
    for j in range(1, n + 1):
        for s in "+-":
            for sig, aa in (("+", ap), ("-", am)):
                br = A.bracket(A.gen(A.b(j, s)), aa)
                ok &= (br == {})
    anti = A.bracket(am, ap)
    ok &= (anti == {(): Poly.const(1)})
    ok &= (A.mul(ap, ap) == {}) and (A.mul(am, am) == {})
    checks["tilde_generators_satisfy_undeformed_relations"] = bool(ok)

    new = cn.substituted_elems(ap, am)
    f, f2 = {}, {}
    for i, e in enumerate(new):
        ck, c0, gk, g0 = cn.decompose(e)
        # non-kappa part must be exactly Z_i
        assert ck == {i: Poly.const(1)} and c0.is_zero(), (i, ck, c0)
        for m, v in gk.items():
            f[(m, i)] = -v
        if not g0.is_zero():
            f2[i] = -g0
    return f, f2, checks


def split_by_gb(poly_dict, ngb):
    """dict key -> Poly (linear in gb)  ==>  list over alpha of dict key -> Fraction."""
    out = [dict() for _ in range(ngb)]
    for key, p in poly_dict.items():
        for alpha in range(ngb):
            v = p.coeff(alpha)
            if v != 0:
                out[alpha][key] = v
    return out


def analyse(n: int):
    t0 = time.time()
    print(f"\n=== n = {n}  (C({n+1}) = osp(2|{2*n})) ===")
    cn = Cn1(n, deformed=True, ordering="doc")
    dim, ngb = cn.dim, cn.A.ngb
    print(f"dim g = {dim}  (even {dim - 4*n}, odd {4*n}),  #gb = {ngb}")

    # ---- 1. structure constants and gamma --------------------------------
    c, gamma, gamma0 = cn.structure()
    c_nz = {k: v for k, v in c.items() if v}
    gamma_alpha = split_by_gb({(i, j, m): v for (i, j), d in gamma.items() for m, v in d.items()}, ngb)
    gamma0_alpha = split_by_gb({k: v for k, v in gamma0.items() if not v.is_zero()}, ngb)
    print(f"structure constants computed: {sum(len(v) for v in c_nz.values())} nonzero entries")
    print(f"gamma_gb: {sum(len(g) for g in gamma_alpha)} nonzero g-valued entries, "
          f"{sum(len(g) for g in gamma0_alpha)} nonzero scalar entries (doc ordering)")

    # undeformed structure constants coincide with those of the undeformed algebra
    cn0 = Cn1(n, deformed=False, ordering="doc")
    c0_, g0_, s0_ = cn0.structure()
    assert {k: v for k, v in c0_.items() if v} == c_nz
    assert all(not g for g in g0_.values()) and all(s.is_zero() for s in s0_.values())

    # super Jacobi identity for c (sanity)
    zero_gamma = {}
    jac = d2(cn, c, zero_gamma)  # with gamma = 0 the operator is identically 0; use a direct check instead
    jac_ok = True
    p = cn.parity
    for i in range(dim):
        for j in range(dim):
            for k in range(dim):
                acc = {}
                # [X,[Y,Z]] - [[X,Y],Z] - (-1)^{p_X p_Y}[Y,[X,Z]]
                for l, cc in c[(j, k)].items():
                    for m, v in c[(i, l)].items():
                        acc[m] = acc.get(m, Fraction(0)) + cc * v
                for l, cc in c[(i, j)].items():
                    for m, v in c[(l, k)].items():
                        acc[m] = acc.get(m, Fraction(0)) - cc * v
                s = -1 if (p[i] * p[j]) % 2 else 1
                for l, cc in c[(i, k)].items():
                    for m, v in c[(j, l)].items():
                        acc[m] = acc.get(m, Fraction(0)) - s * cc * v
                if any(v != 0 for v in acc.values()):
                    jac_ok = False
    print("super-Jacobi identity for undeformed structure constants:", jac_ok)
    assert jac_ok

    # ---- 2. explicit f ----------------------------------------------------
    f, f2, fchecks = explicit_f(cn)
    f_alpha = split_by_gb(f, ngb)
    f2_alpha = split_by_gb(f2, ngb)
    resid_max = Fraction(0)
    scalar_identity = True
    for alpha in range(ngb):
        df = delta_f(cn, c, f_alpha[alpha])
        for i in range(dim):
            for j in range(dim):
                lhs = {m: v for m, v in ((m, gamma[(i, j)][m].coeff(alpha)) for m in gamma[(i, j)]) if v != 0}
                rhs = df[(i, j)]
                for m in set(lhs) | set(rhs):
                    resid_max = max(resid_max, abs(lhs.get(m, 0) - rhs.get(m, 0)))
                # scalar identity gamma0(X,Y) = - f''([X,Y])
                s_lhs = gamma0[(i, j)].coeff(alpha)
                s_rhs = -sum((cc * f2_alpha[alpha].get(k, Fraction(0)) for k, cc in c[(i, j)].items()), Fraction(0))
                if s_lhs != s_rhs:
                    scalar_identity = False
    print("explicit f:", fchecks)
    print(f"max |gamma_gb - delta f| (g-valued part) over all gb directions: {resid_max}")
    print(f"scalar part identity gamma0 = -f''([.,.]) holds: {scalar_identity}")
    assert resid_max == 0 and scalar_identity
    # parity check of f
    f_is_odd = all(cn.parity[m] != cn.parity[i] for (m, i) in f)
    print("f is an odd map:", f_is_odd)
    assert f_is_odd

    # ---- 2b. second explicit primitive from the Cartan homotopy along N ----
    # Every odd cochain has nonzero N-weight.  For a cocycle gamma of N-weight
    # w (component-wise), the cocycle identity with X = N gives
    #     gamma = delta f_N,   f_N(Y) = gamma(N, Y) / w,   w = n(target) - n(Y),
    # where n(.) is the eigenvalue of ad_N (the epsilon-coordinate of the weight).
    iN = cn.index["N"]
    nwt = [wt[0] for wt in cn.weight]
    fN, fN2 = {}, {}
    for i in range(dim):
        for m, v in gamma[(iN, i)].items():
            wgt = nwt[m] - nwt[i]
            assert wgt != 0
            fN[(m, i)] = v * Fraction(1, wgt)
        if not gamma0[(iN, i)].is_zero():
            wgt = -nwt[i]
            assert wgt != 0
            fN2[i] = gamma0[(iN, i)] * Fraction(1, wgt)
    fN_alpha = split_by_gb(fN, ngb)
    fN2_alpha = split_by_gb(fN2, ngb)
    homotopy_ok = True
    for alpha in range(ngb):
        df = delta_f(cn, c, fN_alpha[alpha])
        for i in range(dim):
            for j in range(dim):
                lhs = {m: v for m, v in ((m, gamma[(i, j)][m].coeff(alpha)) for m in gamma[(i, j)]) if v != 0}
                if lhs != df[(i, j)]:
                    homotopy_ok = False
                s_lhs = gamma0[(i, j)].coeff(alpha)
                s_rhs = -sum((cc * fN2_alpha[alpha].get(k, Fraction(0)) for k, cc in c[(i, j)].items()), Fraction(0))
                if s_lhs != s_rhs:
                    homotopy_ok = False
    print(f"homotopy primitive f_N(Y) = gamma(N,Y)/w satisfies gamma_gb = delta f_N (g-part and scalar part): {homotopy_ok}")
    assert homotopy_ok

    # ---- 3. independent linear solve for phi ------------------------------
    # unknowns: phi_{m i} with p_m != p_i
    unk = {}
    for m in range(dim):
        for i in range(dim):
            if cn.parity[m] != cn.parity[i]:
                unk[(m, i)] = len(unk)
    # build rows of delta as linear forms in phi.  (delta phi)^{m'}_{ij} =
    #  (-1)^{p_i} sum_k phi_{kj} c^{m'}_{ik} - (-1)^{(p_i+1)p_j} sum_k phi_{ki} c^{m'}_{jk} - sum_k c^k_{ij} phi_{m'k}
    rows = {}
    for i in range(dim):
        for j in range(dim):
            s1 = -1 if p[i] else 1
            s2 = -1 if ((p[i] + 1) * p[j]) % 2 else 1
            for k in range(dim):
                for mp, cc in c[(i, k)].items():
                    if (k, j) in unk:
                        r = rows.setdefault((i, j, mp), {})
                        r[unk[(k, j)]] = r.get(unk[(k, j)], Fraction(0)) + s1 * cc
                for mp, cc in c[(j, k)].items():
                    if (k, i) in unk:
                        r = rows.setdefault((i, j, mp), {})
                        r[unk[(k, i)]] = r.get(unk[(k, i)], Fraction(0)) - s2 * cc
            for k, cc in c[(i, j)].items():
                for mp in range(dim):
                    if (mp, k) in unk:
                        r = rows.setdefault((i, j, mp), {})
                        r[unk[(mp, k)]] = r.get(unk[(mp, k)], Fraction(0)) - cc
    ech = Echelon(nrhs=ngb)
    keys = set(rows) | {(i, j, m) for alpha in range(ngb) for (i, j, m) in gamma_alpha[alpha]}
    for key in sorted(keys):
        row = {cc: v for cc, v in rows.get(key, {}).items() if v != 0}
        rhs = [gamma_alpha[alpha].get(key, Fraction(0)) for alpha in range(ngb)]
        ech.add(row, rhs)
    nullity = len(unk) - ech.rank
    solvable = [not x for x in ech.inconsistent]
    print(f"linear system delta phi = gamma_gb: unknowns {len(unk)}, rank {ech.rank}, "
          f"nullity {nullity}, solvable for every gb direction: {all(solvable)}")
    assert all(solvable)
    particular = []
    inv_unk = {v: k for k, v in unk.items()}
    for alpha in range(ngb):
        sol = ech.particular_solution(alpha)
        particular.append({inv_unk[col]: v for col, v in sol.items()})
        # verify
        df = delta_f(cn, c, particular[-1])
        for (i, j, m), v in gamma_alpha[alpha].items():
            assert df[(i, j)].get(m, 0) == v
        for (i, j), d in df.items():
            for m, v in d.items():
                assert gamma_alpha[alpha].get((i, j, m), 0) == v
    print("particular solutions re-verified against gamma_gb")

    # kernel of delta on odd 1-cochains = odd derivations; compare with inner ones ad_Z, Z odd
    inner = []
    for z in range(dim):
        if cn.parity[z] == 1:
            adz = {}
            for i in range(dim):
                for m, cc in c[(z, i)].items():
                    adz[(m, i)] = cc
            inner.append(adz)
    inner_in_kernel = all(all(not d for d in delta_f(cn, c, adz).values()) for adz in inner)
    ech_in = Echelon()
    for adz in inner:
        ech_in.add({unk[k]: v for k, v in adz.items()})
    print(f"odd inner derivations ad_Z (Z odd) lie in ker delta: {inner_in_kernel}; "
          f"their span has dim {ech_in.rank} = nullity {nullity}: {ech_in.rank == nullity}")
    assert inner_in_kernel and ech_in.rank == nullity == 4 * n

    # ---- 4. cocycle check -------------------------------------------------
    cocycle_ok = True
    for alpha in range(ngb):
        g = {}
        for (i, j, m), v in gamma_alpha[alpha].items():
            g.setdefault((i, j), {})[m] = v
        if d2(cn, c, g):
            cocycle_ok = False
    print("gamma_gb is a 2-cocycle (d gamma_gb = 0) for every gb direction:", cocycle_ok)
    assert cocycle_ok

    # ---- 5. cohomology H^2(g, Pi g) by weight blocks ----------------------
    coh = cohomology_H2_odd(cn, c)
    print(f"dim H^2(g, Pi g) = {coh['H2_dim']}   (dim C^2_odd = {coh['C2_dim']}, "
          f"dim Z^2 = {coh['Z2_dim']}, dim B^2 = {coh['B2_dim']}, #weight blocks = {len(coh['blocks'])})")
    print(f"dim ker(delta on odd 1-cochains) = {coh['Z1_dim']}, dim C^1_odd = {coh['C1_dim']}")
    assert coh["H2_dim"] == 0
    assert coh["Z1_dim"] == 4 * n

    # ---- 6. symmetrised ordering ------------------------------------------
    cns = Cn1(n, deformed=True, ordering="sym")
    cs, gs, g0s = cns.structure()
    assert {k: v for k, v in cs.items() if v} == c_nz
    sym_scalar_zero = all(v.is_zero() for v in g0s.values())
    fs, f2s, _ = explicit_f(cns)
    sym_f_scalar_zero = (len(f2s) == 0)
    # gamma' identical in both orderings
    same_gamma = all(gs[k] == gamma[k] for k in gamma)
    print(f"symmetrised ordering: scalar part of gamma vanishes: {sym_scalar_zero}; "
          f"scalar part of f vanishes: {sym_f_scalar_zero}; g-valued gamma identical to doc ordering: {same_gamma}")
    assert sym_scalar_zero and sym_f_scalar_zero and same_gamma

    # ---- 7. write artifacts -------------------------------------------------
    gb_params = [{"index": a, "sigma": s, "j": j, "s": t,
                  "label": f"gb_{{a1^{s}, b{j}^{t}}}",
                  "relation": f"[b{j}^{t}, a1^{s}] = - gb[{a}] * kappa"}
                 for a, (s, j, t) in enumerate(cn.A.gb_label)]
    basis = [{"index": i, "label": cn.labels[i], "parity": cn.parity[i],
              "weight": list(cn.weight[i]), "oscillator_expression": cn.desc[i]}
             for i in range(dim)]
    out = {
        "n": n,
        "algebra": f"C({n+1}) = osp(2|{2*n})",
        "dim": dim, "dim_even": dim - 4 * n, "dim_odd": 4 * n, "n_gb": ngb,
        "conventions": {
            "oscillators": "a1^+, a1^- odd with {a1^-, a1^+} = 1; b_j^+, b_j^- even with [b_k^-, b_l^+] = delta_kl; K = 1",
            "kappa": "odd central, kappa^2 = 0",
            "deformation": "[b_j^s, a1^sigma] = - gb_{sigma,j,s} kappa; gb are complex scalars",
            "weight_vector": "(epsilon, delta_1, ..., delta_n) coefficients",
            "bracket_decomposition": "[Z_i, Z_j] = sum_k c[i][j][k] Z_k + kappa (sum_k gamma[i][j][k] Z_k + gamma0[i][j])",
            "delta_f": "(delta f)(X,Y) = (-1)^{p(X)}[X,f(Y)] - (-1)^{(p(X)+1)p(Y)}[Y,f(X)] - f([X,Y]),  f(Z_i) = sum_m phi[m][i] Z_m",
            "d_gamma": "(d g)(X,Y,Z) = g(X,[Y,Z]) + (-1)^{p_X}[X,g(Y,Z)] - g([X,Y],Z) - [g(X,Y),Z] - (-1)^{p_X p_Y} g(Y,[X,Z]) - (-1)^{p_X p_Y + p_Y}[Y,g(X,Z)]",
            "linearity": "gamma, gamma0, f, f_scalar are linear in gb; entries are given per gb direction alpha (coefficient of gb[alpha])",
            "ordering": "odd generators written as a1^sigma b_l^s (fermion first) as in docs/math/Cn1_definition.md",
            "normalisation": "E_{2 delta_k} = (b_k^+)^2 and E_{-2 delta_k} = (b_k^-)^2 (no factor 1/2); h_k = b_k^+ b_k^- + 1/2; N = a1^+ a1^- - 1/2",
        },
        "basis": basis,
        "gb_parameters": gb_params,
        "structure_constants": [[i, j, k, fr(v)] for (i, j), d in sorted(c_nz.items()) for k, v in sorted(d.items())],
        "gamma_g_part": [[i, j, m, a, fr(v)] for a in range(ngb) for (i, j, m), v in sorted(gamma_alpha[a].items())],
        "gamma_scalar_part": [[i, j, a, fr(v)] for a in range(ngb) for (i, j), v in sorted(gamma0_alpha[a].items())],
        "f_explicit": {
            "description": "f[m][i][alpha]: coefficient of gb[alpha] in phi_{m i}; induced by a1^sigma -> a1^sigma + kappa u^sigma, u^sigma = sum_j (gb_{sigma,j,-} b_j^+ - gb_{sigma,j,+} b_j^-), f = -(kappa-part)",
            "entries": [[m, i, a, fr(v)] for a in range(ngb) for (m, i), v in sorted(f_alpha[a].items())],
            "scalar_part": [[i, a, fr(v)] for a in range(ngb) for i, v in sorted(f2_alpha[a].items())],
        },
        "f_homotopy": {
            "description": "second primitive: f_N(Y) = gamma_gb(N, Y) / (n(target) - n(Y)), n = ad_N eigenvalue (epsilon-coordinate of the weight); scalar part f_N''(Y) = gamma0(N,Y)/(-n(Y))",
            "entries": [[m, i, a, fr(v)] for a in range(ngb) for (m, i), v in sorted(fN_alpha[a].items())],
            "scalar_part": [[i, a, fr(v)] for a in range(ngb) for i, v in sorted(fN2_alpha[a].items())],
        },
        "linear_solve": {
            "unknowns": len(unk), "rank": ech.rank, "nullity": nullity,
            "solvable_for_every_gb_direction": all(solvable),
            "kernel_equals_span_of_odd_inner_derivations": bool(inner_in_kernel and ech_in.rank == nullity),
            "particular_solutions": [[m, i, a, fr(v)] for a in range(ngb) for (m, i), v in sorted(particular[a].items())],
        },
        "verification": {
            "undeformed_structure_constants_gb_independent": True,
            "undeformed_brackets_have_no_scalar_term": True,
            "super_jacobi_identity": jac_ok,
            "tilde_generators_satisfy_undeformed_relations": fchecks["tilde_generators_satisfy_undeformed_relations"],
            "gamma_g_part_equals_delta_f_exactly": resid_max == 0,
            "gamma_equals_delta_f_homotopy": homotopy_ok,
            "gamma_scalar_part_equals_minus_f_scalar_of_bracket": scalar_identity,
            "f_is_odd": f_is_odd,
            "gamma_is_2_cocycle": cocycle_ok,
            "symmetrised_ordering_scalar_parts_vanish": sym_scalar_zero and sym_f_scalar_zero,
            "symmetrised_ordering_same_g_valued_gamma": same_gamma,
        },
        "cohomology": coh,
        "conclusion": "gamma_gb is a coboundary for ALL values of gb (no condition); moreover H^2(g, Pi g) = 0.",
        "elapsed_seconds": round(time.time() - t0, 2),
    }
    path = os.path.join(ART, f"Cn1_triviality_n{n}.json")
    with open(path, "w") as fh:
        json.dump(out, fh, indent=1)
    print(f"wrote {os.path.relpath(path, ROOT)}  ({time.time() - t0:.1f}s)")
    return out


def cohomology_H2_odd(cn: Cn1, c):
    """
    dim H^2(g, Pi g) computed block-wise in the Cartan weight decomposition.
    Odd 2-cochains: gamma^m_{ij}, p_m = p_i + p_j + 1, super-skew in (i,j).
    Canonical unknowns: i<j, or i==j odd.  Weight of the unknown: w_m - w_i - w_j.
    """
    dim, p, w = cn.dim, cn.parity, cn.weight

    def wsub(a, b):
        return tuple(x - y for x, y in zip(a, b))

    def wadd(a, b):
        return tuple(x + y for x, y in zip(a, b))

    # C^2 unknowns
    unk2 = {}
    blk2 = {}
    for i in range(dim):
        for j in range(i, dim):
            if i == j and p[i] == 0:
                continue
            for m in range(dim):
                if p[m] != (p[i] + p[j] + 1) % 2:
                    continue
                mu = wsub(w[m], wadd(w[i], w[j]))
                unk2[(i, j, m)] = len(unk2)
                blk2.setdefault(mu, []).append((i, j, m))

    def canon(a, b, m):
        """index and sign of gamma^m_{ab} in terms of canonical unknowns, or None."""
        if a < b:
            return unk2.get((a, b, m)), 1
        if a > b:
            s = -1 if (p[a] * p[b]) % 2 else 1
            return unk2.get((b, a, m)), -s
        if p[a] == 1:
            return unk2.get((a, a, m)), 1
        return None, 0

    # C^1 unknowns (odd maps)
    unk1 = {}
    blk1 = {}
    for m in range(dim):
        for i in range(dim):
            if p[m] != p[i]:
                mu = wsub(w[m], w[i])
                unk1[(m, i)] = len(unk1)
                blk1.setdefault(mu, []).append((m, i))

    # rows of d : C^2 -> C^3, grouped by block
    rows_d = {}
    for i in range(dim):
        for j in range(dim):
            for k in range(dim):
                si = -1 if p[i] else 1
                sij = -1 if (p[i] * p[j]) % 2 else 1
                sijj = -1 if (p[i] * p[j] + p[j]) % 2 else 1
                acc = {}  # (m') -> {col: coeff}

                def put(mp, col, v):
                    if col is None or v == 0:
                        return
                    r = acc.setdefault(mp, {})
                    r[col] = r.get(col, Fraction(0)) + v

                for l, cc in c[(j, k)].items():
                    for mp in range(dim):
                        col, s = canon(i, l, mp)
                        put(mp, col, cc * s)
                for m in range(dim):
                    col, s = canon(j, k, m)
                    if col is None:
                        continue
                    for mp, cc in c[(i, m)].items():
                        put(mp, col, si * s * cc)
                for l, cc in c[(i, j)].items():
                    for mp in range(dim):
                        col, s = canon(l, k, mp)
                        put(mp, col, -cc * s)
                for m in range(dim):
                    col, s = canon(i, j, m)
                    if col is None:
                        continue
                    for mp, cc in c[(m, k)].items():
                        put(mp, col, -s * cc)
                for l, cc in c[(i, k)].items():
                    for mp in range(dim):
                        col, s = canon(j, l, mp)
                        put(mp, col, -sij * cc * s)
                for m in range(dim):
                    col, s = canon(i, k, m)
                    if col is None:
                        continue
                    for mp, cc in c[(j, m)].items():
                        put(mp, col, -sijj * s * cc)
                for mp, r in acc.items():
                    r = {col: v for col, v in r.items() if v != 0}
                    if r:
                        mu = wsub(w[mp], wadd(wadd(w[i], w[j]), w[k]))
                        rows_d.setdefault(mu, []).append(r)

    # columns of delta : C^1 -> C^2 (image of each basis 1-cochain), grouped by block
    cols_delta = {}
    for (m, i), col1 in unk1.items():
        img = delta_f(cn, c, {(m, i): Fraction(1)})
        vec = {}
        for (a, b), d in img.items():
            for mp, v in d.items():
                col, s = canon(a, b, mp)
                if col is None:
                    assert v == 0
                    continue
                # only keep canonical representatives (a<=b)
                if a <= b:
                    vec[col] = v
        mu = wsub(w[m], w[i])
        cols_delta.setdefault(mu, []).append(vec)

    blocks = []
    H2 = Z2 = B2 = 0
    Z1 = 0
    for mu in sorted(set(blk2) | set(blk1) | set(rows_d)):
        n2 = len(blk2.get(mu, []))
        n1 = len(blk1.get(mu, []))
        e_d = Echelon()
        for r in rows_d.get(mu, []):
            e_d.add(r)
        z2 = n2 - e_d.rank
        e_delta = Echelon()
        for v in cols_delta.get(mu, []):
            e_delta.add(v)
        b2 = e_delta.rank
        # im(delta) subset ker(d): check d(delta v) = 0 for each column
        incl = True
        for v in cols_delta.get(mu, []):
            for r in rows_d.get(mu, []):
                if sum((r[cc] * v[cc] for cc in r if cc in v), Fraction(0)) != 0:
                    incl = False
        assert incl, mu
        z1 = n1 - b2
        blocks.append({"weight": list(mu), "dim_C1": n1, "dim_C2": n2, "rank_d2": e_d.rank,
                       "dim_Z2": z2, "dim_B2": b2, "dim_H2": z2 - b2, "dim_Z1": z1})
        H2 += z2 - b2
        Z2 += z2
        B2 += b2
        Z1 += z1
        assert z2 - b2 >= 0
    # the Cartan-weight-zero block (where cohomology could live) must be empty for odd cochains
    zero_block = next((b for b in blocks if all(x == 0 for x in b["weight"])), None)
    return {
        "module": "Pi g (adjoint with parity reversed) = odd cochains",
        "C1_dim": len(unk1), "Z1_dim": Z1,
        "C2_dim": len(unk2), "Z2_dim": Z2, "B2_dim": B2, "H2_dim": H2,
        "weight_zero_block_dims": zero_block,
        "im_delta_subset_ker_d": True,
        "blocks": blocks,
    }


if __name__ == "__main__":
    ns = [int(x) for x in sys.argv[1:]] or [1, 2, 3]
    summary = {}
    for n in ns:
        out = analyse(n)
        summary[n] = {
            "dim": out["dim"], "n_gb": out["n_gb"],
            "gamma_equals_delta_f": out["verification"]["gamma_g_part_equals_delta_f_exactly"],
            "solvable_for_every_gb_direction": out["linear_solve"]["solvable_for_every_gb_direction"],
            "nullity": out["linear_solve"]["nullity"],
            "H2_odd_dim": out["cohomology"]["H2_dim"],
            "Z1_odd_dim": out["cohomology"]["Z1_dim"],
            "elapsed_seconds": out["elapsed_seconds"],
        }
    with open(os.path.join(ART, "summary.json"), "w") as fh:
        json.dump({"conclusion": "The inhomogeneous deformation gamma_gb of C(n+1) is a coboundary for every value of the 4n parameters gb (necessary and sufficient condition: none). H^2(g, Pi g) = 0 for n = 1, 2, 3.",
                   "per_n": summary}, fh, indent=1)
    print("\nSUMMARY:", json.dumps(summary, indent=1))
