"""Schema 2 (inhomogeneous deformation, gamma structure) for C(n+1)  (Issue I05).

Deformed oscillator relation:  [b_k^s, a_1^sigma] = - gb_{a_1^sigma, b_k^s} kappa,
kappa odd, central, kappa^2 = 0.  For basis elements X, Y the deformed bracket is
    [X, Y}_gamma = [X, Y}_0 + kappa * gamma(X, Y),       gamma(X, Y) in g ⊕ C K,
and gamma is linear in the 4n parameters gb.  We compute gamma one parameter at a
time (set that gb = 1, all others 0) and store the linear forms.

Usage: python3 src/C_gamma.py [--outdir data] [n ...]
"""
from __future__ import annotations

import argparse
import datetime as _dt
import json
import os
import sys
from fractions import Fraction

sys.path.insert(0, os.path.dirname(__file__))
from C_generators import (  # noqa: E402
    Decomposer, OscillatorAlgebra, algebra_block, build_basis, central_elements_block, fr,
    metadata_block,
)


def gb_labels(n: int):
    """Ordered list of (label, (sigma, k, s)) for the 2 x 2n gb matrix (row-major)."""
    out = []
    for sigma in ("p", "m"):
        for k in range(1, n + 1):
            for s in ("p", "m"):
                out.append((f"gb_a1{sigma}_b{k}{s}", (sigma, k, s)))
    return out


def linear_form_str(coeff: dict) -> str:
    parts = []
    for lab, c in coeff.items():
        c = Fraction(c)
        if c == 1:
            t = lab
        elif c == -1:
            t = f"-{lab}"
        else:
            t = f"{c}*{lab}"
        parts.append(t)
    s = " + ".join(parts)
    return s.replace("+ -", "- ") if s else "0"


def compute_gamma(n: int):
    """Return (order, par, sc_table, gamma_table, labels) where
    gamma_table[(X,Y)] = {Z: {gb_label: Fraction}} (Z may be 'K')."""
    odd, even, real, roots = build_basis(n)
    order = odd + even
    par = {l: 1 for l in odd}
    par.update({l: 0 for l in even})
    alg0 = OscillatorAlgebra(n)
    elements0 = {lab: alg0.element(terms) for lab, terms in real.items()}
    dec = Decomposer(alg0, order, elements0, include_K=True)
    sc_table = {}
    for X in order:
        for Y in order:
            A0, A1 = alg0.split_kappa(alg0.bracket(elements0[X], elements0[Y]))
            assert not A1
            sc_table[(X, Y)] = dec.decompose(A0)
    gamma = {(X, Y): {} for X in order for Y in order}
    labels = gb_labels(n)
    for lab, key in labels:
        alg = OscillatorAlgebra(n, gb={key: Fraction(1)})
        elements = {l: alg.element(terms) for l, terms in real.items()}
        for X in order:
            for Y in order:
                A0, A1 = alg.split_kappa(alg.bracket(elements[X], elements[Y]))
                c0 = dec.decompose(A0)
                assert c0 == sc_table[(X, Y)], f"kappa-free part changed for ({X},{Y})"
                for Z, c in dec.decompose(A1).items():
                    gamma[(X, Y)].setdefault(Z, {})[lab] = c
    return order, par, sc_table, gamma, labels


# ---------------------------------------------------------------------- consistency checks

def check_gamma_consistency(order, par, sc_table, gamma, labels):
    """Parity, graded antisymmetry, and the first-order (cocycle) Jacobi identity of gamma.

    The deformed bracket lives in L = g ⊕ kappa (g ⊕ C K) with
      [X, Y}_γ = [X,Y}_0 + κ γ(X,Y),  [X, κZ} = (-1)^{p(X)} κ [X,Z}_0,  [κZ, κW} = 0,
    and κ K central.  The Jacobi identity of this bracket at order κ^1 is the cocycle
    condition for γ (κ^2 = 0 kills higher orders).  Checked per gb parameter.
    """
    problems = []
    for (X, Y), comps in gamma.items():
        sign = -1 if (par[X] and par[Y]) else 1
        for Z, lf in comps.items():
            pz = 0 if Z == "K" else par[Z]
            if pz != (par[X] + par[Y] + 1) % 2:
                problems.append(("parity", X, Y, Z))
        back = gamma[(Y, X)]
        expect = {Z: {l: -sign * c for l, c in lf.items()} for Z, lf in comps.items()}
        if expect != back:
            problems.append(("antisymmetry", X, Y))

    def pz(Z):
        return 0 if Z == "K" else par[Z]

    def br(u: dict, v: dict, lab: str) -> dict:
        """Bracket in L of vectors u, v = {(label, kappa_order): coeff}, truncated at kappa^1."""
        out: dict = {}
        for (A, ka), ca in u.items():
            for (B, kb), cb in v.items():
                if ka + kb > 1:
                    continue
                if A == "K" or B == "K":
                    continue
                if ka == 0 and kb == 0:
                    for Z, c in sc_table[(A, B)].items():
                        out[(Z, 0)] = out.get((Z, 0), Fraction(0)) + ca * cb * c
                    for Z, lf in gamma[(A, B)].items():
                        if lab in lf:
                            out[(Z, 1)] = out.get((Z, 1), Fraction(0)) + ca * cb * lf[lab]
                elif ka == 0 and kb == 1:        # [A, κB} = (-1)^{p(A)} κ [A,B}
                    s = -1 if par[A] else 1
                    for Z, c in sc_table[(A, B)].items():
                        out[(Z, 1)] = out.get((Z, 1), Fraction(0)) + s * ca * cb * c
                else:                             # [κA, B} = κ [A,B}
                    for Z, c in sc_table[(A, B)].items():
                        out[(Z, 1)] = out.get((Z, 1), Fraction(0)) + ca * cb * c
        return {k: v for k, v in out.items() if v != 0}

    for lab, _ in labels:
        for X in order:
            for Y in order:
                sXY = -1 if (par[X] and par[Y]) else 1
                for Z in order:
                    vX, vY, vZ = {(X, 0): Fraction(1)}, {(Y, 0): Fraction(1)}, {(Z, 0): Fraction(1)}
                    lhs = br(vX, br(vY, vZ, lab), lab)
                    rhs = br(br(vX, vY, lab), vZ, lab)
                    for k, v in br(vY, br(vX, vZ, lab), lab).items():
                        rhs[k] = rhs.get(k, Fraction(0)) + sXY * v
                    rhs = {k: v for k, v in rhs.items() if v != 0}
                    if lhs != rhs:
                        problems.append(("jacobi", lab, X, Y, Z, lhs, rhs))
    return problems


# ---------------------------------------------------------------------- JSON

def build_schema2(n: int, check=True):
    order, par, sc_table, gamma, labels = compute_gamma(n)
    problems = check_gamma_consistency(order, par, sc_table, gamma, labels) if check else []
    if problems:
        raise RuntimeError(f"gamma consistency failed: {problems[:5]}")
    bos = [f"b_{k}_{s}" for k in range(1, n + 1) for s in ("p", "m")]
    entries = []
    zorder = order + ["K"]
    for X in order:
        for Y in order:
            for Z in zorder:
                if Z in gamma[(X, Y)]:
                    lf = gamma[(X, Y)][Z]
                    coeff = {lab: fr(lf[lab]) for lab, _ in labels if lab in lf}
                    entries.append({"X": X, "Y": Y, "Z": Z, "coeff": coeff, "linear_form": linear_form_str(coeff)})
    schema = {
        "schema_version": "5.0",
        "schema_layer": 2,
        "algebra": algebra_block(n),
        "source_structure": f"C_{n}_structure.json",
        "central_elements": central_elements_block(),
        "gb_matrix": {
            "description": "Deformation parameters gb_{a_1^σ, b_k^s}; rows = fermions a_1^±, columns = bosons b_k^±",
            "shape": [2, 2 * n],
            "rows": ["a_1_p", "a_1_m"],
            "cols": bos,
            "parity": 1,
            "parity_note": "The product gb·kappa is the odd super-central symbol used in the computation; gb coefficients are extracted as commuting scalars (see docs/json_schema_specification.md §2).",
            "entries": [
                {"label": lab, "fermion": f"a_1_{key[0]}", "boson": f"b_{key[1]}_{key[2]}",
                 "row": 0 if key[0] == "p" else 1, "col": bos.index(f"b_{key[1]}_{key[2]}")}
                for lab, key in labels
            ],
        },
        "deformed_oscillator_relations": {
            "boson_fermion": "[b_k^s, a_1^σ] = - gb_{a_1^σ, b_k^s} kappa",
            "unchanged": ["{a_1^-, a_1^+} = 1, (a_1^±)^2 = 0", "[b_k^-, b_l^+] = δ_{kl}, [b_k^±, b_l^±] = 0",
                          "kappa odd, super-central, kappa^2 = 0"],
        },
        "inhomogeneous_deformation": {
            "description": "[X,Y]_γ = [X,Y]_0 + kappa * γ(X,Y); γ(X,Y) ∈ g ⊕ C K with p(γ(X,Y)) = p(X)+p(Y)+1; all ordered pairs stored",
            "gamma_is_linear_in_gb": True,
            "cocycle_condition_verified": bool(check),
            "gamma": entries,
        },
        "metadata": metadata_block("src/C_gamma.py"),
    }
    return schema, (order, par, sc_table, gamma, labels)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("ns", nargs="*", type=int, default=[1, 2, 3])
    ap.add_argument("--outdir", default=os.path.join(os.path.dirname(__file__), "..", "data"))
    args = ap.parse_args(argv)
    for n in args.ns:
        schema, (order, par, sc_table, gamma, labels) = build_schema2(n)
        path = os.path.join(args.outdir, f"C_{n}_gamma.json")
        with open(path, "w") as fh:
            json.dump(schema, fh, indent=1, ensure_ascii=False)
        g = schema["inhomogeneous_deformation"]["gamma"]
        nz_pairs = sum(1 for v in gamma.values() if v)
        kcomp = sum(1 for e in g if e["Z"] == "K")
        print(f"C({n+1}): {len(labels)} gb parameters, {nz_pairs}/{len(order)**2} pairs with non-zero gamma, "
              f"{len(g)} gamma entries ({kcomp} with Z=K); kappa-free part == Schema 1; "
              f"parity/antisymmetry/cocycle checks passed -> {os.path.relpath(path)}")


if __name__ == "__main__":
    main()
