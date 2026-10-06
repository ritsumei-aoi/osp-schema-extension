"""
analyze.py  (clean rebuild)
===========================
For g = C(n+1) = osp(2|2n):
  (1) structure constants C (degree-2 projection of the oscillator bracket),
  (2) inhomogeneous deformation cocycle gamma_{gb} (kappa^1 degree-2 part),
  (3) coboundary delta f for a general odd linear map f (phi variables),
  (4) exact triviality: subspace of gb-space with gamma_{gb} = delta f solvable.

The delta-f construction mirrors the independently verified test_shift.py.
"""
import json
from sympy import symbols, simplify, Matrix, zeros, S, Rational
from osp_engine import make_gb_symbols, super_bracket
from basis import build_basis, monomial_to_index


def project_g(elem, idx):
    g0, g1, leftover = {}, {}, {}
    for (kp, toks), c in elem.items():
        if toks in idx and kp in (0, 1):
            (g0 if kp == 0 else g1).setdefault(idx[toks], 0)
            if kp == 0:
                g0[idx[toks]] += c
            else:
                g1[idx[toks]] += c
        else:
            leftover[(kp, toks)] = c
    return g0, g1, leftover


def build_structures(n):
    gb = make_gb_symbols(n)
    gb_keys = list(gb.keys())
    gb_syms = [gb[k] for k in gb_keys]
    basis, parity, names = build_basis(n)
    idx = monomial_to_index(n, names)
    D = len(basis)
    zero_sub = {gb[k]: 0 for k in gb}
    C, Gamma = {}, {}
    scalar_kappa = []
    for a in range(D):
        for b in range(D):
            br = super_bracket(basis[a], basis[b], parity[a], parity[b], gb)
            g0, g1, leftover = project_g(br, idx)
            C[(a, b)] = {c: simplify(v.subs(zero_sub)) for c, v in g0.items()
                         if simplify(v.subs(zero_sub)) != 0}
            Gamma[(a, b)] = {c: simplify(v) for c, v in g1.items() if simplify(v) != 0}
            for (kp, toks), c in leftover.items():
                if kp == 1 and simplify(c) != 0:
                    scalar_kappa.append((names[a], names[b], toks, str(c)))
    return dict(gb=gb, gb_keys=gb_keys, gb_syms=gb_syms, basis=basis,
                parity=parity, names=names, idx=idx, D=D, C=C, Gamma=Gamma,
                scalar_kappa=scalar_kappa)


def check_jacobi(S_, sample_cap=400):
    import itertools, random
    C, parity, D = S_['C'], S_['parity'], S_['D']
    def bracket_elt(coeffs, b):
        out = {}
        for c, val in coeffs.items():
            for d, cc in C[(c, b)].items():
                out[d] = out.get(d, 0) + val * cc
        return {k: v for k, v in out.items() if v != 0}
    triples = list(itertools.combinations(range(D), 3))
    random.seed(1)
    sample = triples if len(triples) <= sample_cap else random.sample(triples, sample_cap)
    fail = 0
    for (a, b, c) in sample:
        pa, pb, pc = parity[a], parity[b], parity[c]
        t1 = bracket_elt(C[(a, b)], c); s1 = (-1) ** (pa * pc)
        t2 = bracket_elt(C[(b, c)], a); s2 = (-1) ** (pb * pa)
        t3 = bracket_elt(C[(c, a)], b); s3 = (-1) ** (pc * pb)
        acc = {}
        for t, s in ((t1, s1), (t2, s2), (t3, s3)):
            for k, v in t.items():
                acc[k] = acc.get(k, 0) + s * v
        if any(simplify(v) != 0 for v in acc.values()):
            fail += 1
    return fail, len(sample)


def triviality(S_, verbose=True):
    C, Gamma, parity, D = S_['C'], S_['Gamma'], S_['parity'], S_['D']
    names, gb_syms, gb_keys = S_['names'], S_['gb_syms'], S_['gb_keys']
    G = len(gb_syms)

    # odd map variables phi[(i,j)] : parity[i] != parity[j]
    phi_cols = {}
    for j in range(D):
        for i in range(D):
            if parity[i] != parity[j]:
                phi_cols[(i, j)] = len(phi_cols)
    P = len(phi_cols)
    gb_col = {gb_syms[t]: P + t for t in range(G)}
    ncol = P + G

    rows = []
    for a in range(D):
        for b in range(a + 1, D):
            pa, pb = parity[a], parity[b]
            comp = {}
            def addc(c, col, val):
                comp.setdefault(c, {})
                comp[c][col] = comp[c].get(col, 0) + val
            # delta f(a,b) = (-1)^pa [a,f(b)] - (-1)^{(pa+1)pb}[b,f(a)] - f([a,b])
            s1 = (-1) ** pa
            for i in range(D):
                if (i, b) in phi_cols:
                    col = phi_cols[(i, b)]
                    for c, cc in C[(a, i)].items():
                        addc(c, col, s1 * cc)
            s2 = -((-1) ** ((pa + 1) * pb))
            for i in range(D):
                if (i, a) in phi_cols:
                    col = phi_cols[(i, a)]
                    for c, cc in C[(b, i)].items():
                        addc(c, col, s2 * cc)
            for d, cab in C[(a, b)].items():
                for i in range(D):
                    if (i, d) in phi_cols:
                        addc(i, phi_cols[(i, d)], -cab)
            # subtract gamma: delta f - gamma = 0
            for c, expr in Gamma[(a, b)].items():
                for sym in gb_syms:
                    k = expr.coeff(sym)
                    if k != 0:
                        addc(c, gb_col[sym], -k)
            for c, d in comp.items():
                row = {col: S(v) for col, v in d.items() if v != 0}
                if row:
                    rows.append(row)

    M = zeros(len(rows), ncol)
    for r, row in enumerate(rows):
        for col, v in row.items():
            M[r, col] = v
    ns = M.nullspace()
    gb_vectors = []
    for vec in ns:
        gbpart = [vec[P + t] for t in range(G)]
        if any(x != 0 for x in gbpart):
            gb_vectors.append(gbpart)
    if gb_vectors:
        Mgb = Matrix(gb_vectors)
        triv_dim = Mgb.rank()
    else:
        triv_dim = 0
    return dict(P=P, G=G, n_eq=len(rows), triv_dim=int(triv_dim),
                nontrivial_dim=int(G - triv_dim),
                gb_vectors=[[str(x) for x in v] for v in gb_vectors])


def jsonable(C, names):
    out = {}
    for (a, b), d in C.items():
        if d:
            out[f"{names[a]}|{names[b]}"] = {names[c]: str(v) for c, v in d.items()}
    return out


def run(n):
    S_ = build_structures(n)
    jf, js = check_jacobi(S_)
    tv = triviality(S_)
    print(f"n={n}: dim g={S_['D']} (even {S_['parity'].count(0)}, odd {S_['parity'].count(1)}), "
          f"gb params={tv['G']}, phi vars={tv['P']}, eqs={tv['n_eq']}")
    print(f"      Jacobi violations {jf}/{js}; scalar*kappa leftovers={len(S_['scalar_kappa'])}")
    print(f"      trivializable gb-dim = {tv['triv_dim']} / {tv['G']}  "
          f"=> nontrivial classes dim = {tv['nontrivial_dim']}")
    return S_, jf, js, tv


if __name__ == "__main__":
    import sys
    ns_arg = [int(x) for x in sys.argv[1:]] or [1, 2]
    summary = []
    for n in ns_arg:
        S_, jf, js, tv = run(n)
        with open(f"../artifacts/struct_constants_n{n}.json", "w") as fh:
            json.dump({
                "n": n,
                "algebra": f"C({n+1}) = osp(2|{2*n})",
                "basis_names": S_['names'],
                "parity": S_['parity'],
                "structure_constants": jsonable(S_['C'], S_['names']),
                "gamma_cocycle_gb": jsonable(S_['Gamma'], S_['names']),
                "scalar_kappa_leftovers": S_['scalar_kappa'],
            }, fh, indent=1)
        summary.append({
            "n": n, "dim_g": S_['D'],
            "num_even": S_['parity'].count(0), "num_odd": S_['parity'].count(1),
            "num_gb_params": tv['G'], "num_phi_vars": tv['P'],
            "jacobi_violations": jf, "jacobi_sample": js,
            "scalar_kappa_leftover_count": len(S_['scalar_kappa']),
            "trivializable_gb_dim": tv['triv_dim'],
            "nontrivial_class_dim": tv['nontrivial_dim'],
            "trivializable_gb_basis": tv['gb_vectors'],
            "conclusion": ("ALL gb deformations trivial" if tv['triv_dim'] == tv['G']
                           else ("only gb=0 trivial" if tv['triv_dim'] == 0
                                 else "partial: see trivializable basis")),
        })
    with open("../artifacts/triviality_summary.json", "w") as fh:
        json.dump(summary, fh, indent=2)
    print("\nwrote artifacts: struct_constants_n*.json, triviality_summary.json")
