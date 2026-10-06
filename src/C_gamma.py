"""Schema 2 (gamma structure) for the inhomogeneous deformation of C(n+1) = osp(2|2n).

Deformed oscillator relation (docs/math/C_inhomogeneous_definition.md):
    [b_j^s, a_1^sigma] = - gb_{sigma,j,s} kappa.
For basis elements X, Y the bracket computed in U(A) is
    [X, Y}_gamma = [X, Y}_0 + kappa * gamma(X, Y),   gamma(X, Y) in g ⊕ CK,
with gamma linear in the gb.  Usage: python src/C_gamma.py [n ...]
"""
import datetime
import os
import sys
from fractions import Fraction

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from C_generators import DATA_DIR, SIGNS, CAlgebra, write_json  # noqa: E402
from oscillator_algebra import gb_label  # noqa: E402
from verify_C_structure import bracket_table, load_structure  # noqa: E402


def gb_matrix(n):
    cols = [f"b_{k}_{s}" for k in range(1, n + 1) for s in SIGNS]
    rows = ["a_1_p", "a_1_m"]
    labels = [[gb_label(r[-1], int(c.split("_")[1]), c[-1]) for c in cols] for r in rows]
    return {"rows": rows, "columns": cols, "labels": labels, "count": 4 * n,
            "parity": 1,
            "parity_note": ("Labelled 'parity 1' as in the source document (parameters of the "
                            "odd-sector of the pre-oscillator form). In the computation they "
                            "are ordinary (commuting) scalars; see I05 Response."),
            "entry_meaning": "labels[r][c] = gb_{rows[r], columns[c]}"}


def gb_labels(n):
    return [x for row in gb_matrix(n)["labels"] for x in row]


def compute_gamma(n):
    """Return (undeformed table, gamma table {(X,Y): {Z or 'K': {gb: Fraction}}})."""
    calg = CAlgebra(n, deformed=True)
    und, gam = {}, {}
    for X in calg.basis:
        for Y in calg.basis:
            d0, d1 = calg.bracket_decomposed(X, Y)
            for Z, p in d0.items():
                assert set(p) == {()}, "gb leaked into undeformed part"
                und.setdefault((X, Y), {})[Z] = p[()]
            for Z, p in d1.items():
                assert all(len(m) == 1 for m in p), "gamma must be linear in gb"
                gam.setdefault((X, Y), {})[Z] = {m[0]: c for m, c in p.items()}
    return calg, und, gam


def gamma_entries(calg, gam):
    out = []
    order = calg.basis + ["K"]
    for X in calg.basis:
        for Y in calg.basis:
            v = gam.get((X, Y), {})
            for Z in order:
                if Z in v:
                    out.append({"X": X, "Y": Y, "Z": Z,
                                "coeff": {g: str(c) for g, c in sorted(v[Z].items())}})
    return out


# ------------------------------------------------------------ consistency checks


def check_against_schema1(n, und):
    s1 = bracket_table(load_structure(n)["structure_constants"])
    return s1 == und


def check_gamma_symmetry(basis, parity, gam):
    """gamma(Y,X) = -(-1)^{pXpY} gamma(X,Y)  and  p(Z) = p(X)+p(Y)+1 (K even)."""
    fails = []
    par = dict(parity, K=0)
    for X in basis:
        for Y in basis:
            s = -(-1) ** (parity[X] * parity[Y])
            a, b = gam.get((X, Y), {}), gam.get((Y, X), {})
            for Z in set(a) | set(b):
                ga, gb_ = a.get(Z, {}), b.get(Z, {})
                if any(gb_.get(g, 0) != s * ga.get(g, 0) for g in set(ga) | set(gb_)):
                    fails.append(("antisym", X, Y, Z))
                if par[Z] != (parity[X] + parity[Y] + 1) % 2:
                    fails.append(("parity", X, Y, Z))
    return fails


def check_deformed_jacobi(basis, parity, und, gam):
    """kappa-part of the super-Jacobiator of L = g ⊕ kappa(g ⊕ CK):
        sum_cyc (-1)^{pA pC} ( gamma(A,[B,C]_0) + (-1)^{pA} [A, gamma(B,C)]_0 ) = 0,
    computed with symbolic gb coefficients (keys (W, gb))."""
    def gamma_lin(A, vec):  # gamma(A, sum c W)
        out = {}
        for W, c in vec.items():
            for Z, coeffs in gam.get((A, W), {}).items():
                for g, d in coeffs.items():
                    out[(Z, g)] = out.get((Z, g), 0) + c * d
        return out

    def und_lin(A, vec):  # [A, sum c_(W,g) W]_0 , K is central
        out = {}
        for (W, g), c in vec.items():
            if W == "K":
                continue
            for Z, d in und.get((A, W), {}).items():
                out[(Z, g)] = out.get((Z, g), 0) + c * d
        return out

    fails, count = [], 0
    for X in basis:
        for Y in basis:
            for Z in basis:
                count += 1
                tot = {}
                for A, B, C in ((X, Y, Z), (Y, Z, X), (Z, X, Y)):
                    s = (-1) ** (parity[A] * parity[C])
                    t1 = gamma_lin(A, und.get((B, C), {}))
                    gBC = {(W, g): c for W, cs in gam.get((B, C), {}).items()
                           for g, c in cs.items()}
                    t2 = und_lin(A, gBC)
                    sA = (-1) ** parity[A]
                    for k, v in t1.items():
                        tot[k] = tot.get(k, 0) + s * v
                    for k, v in t2.items():
                        tot[k] = tot.get(k, 0) + s * sA * v
                tot = {k: v for k, v in tot.items() if v}
                if tot:
                    fails.append((X, Y, Z, tot))
    return count, fails


def build_schema2(n, date=None):
    calg, und, gam = compute_gamma(n)
    entries = gamma_entries(calg, gam)
    k_entries = sum(1 for e in entries if e["Z"] == "K")
    return {
        "schema_version": "5.0",
        "layer": 2,
        "algebra": {"family": "C", "m": 1, "n": n, "cartan_type": f"C({n+1})",
                    "osp": f"osp(2|{2*n})"},
        "structure_file": f"C_{n}_structure.json",
        "basis_ordering": calg.basis,
        "gb_matrix": gb_matrix(n),
        "deformed_relations": {
            "rule": "[b_j^s, a_1^σ] = - gb_{σ,j,s} κ   (i.e. b_j^s a_1^σ = a_1^σ b_j^s - gb_{σ,j,s} κ)",
            "kappa": "odd, central in A: x κ = (-1)^{p(x)} κ x, κ^2 = 0",
            "unchanged": "{a_1^-, a_1^+} = 1, (a_1^±)^2 = 0, [b_i^-, b_j^+] = δ_ij",
        },
        "inhomogeneous_deformation": {
            "bracket": "[X,Y]_γ = [X,Y]_0 + κ γ(X,Y)  (κ on the left)",
            "value_space": "g ⊕ CK  (Z = 'K' is the central K = 1 component)",
            "linearity": "γ is linear in the gb parameters; coeff maps gb label -> rational",
            "pairs": "all ordered pairs (X, Y); γ(Y,X) = -(-1)^{p(X)p(Y)} γ(X,Y)",
            "parity_rule": "p(Z) = p(X) + p(Y) + 1 (γ is an odd cochain)",
            "num_entries": len(entries),
            "num_K_entries": k_entries,
            "entries": entries,
        },
        "metadata": {"generated_by": "src/C_gamma.py",
                     "generation_date": date or datetime.date.today().isoformat(),
                     "conventions": "handover/notation.md",
                     "math_reference": "docs/math/C_inhomogeneous_definition.md"},
    }


def main(ns):
    for n in ns:
        s2 = build_schema2(n)
        path = os.path.join(DATA_DIR, f"C_{n}_gamma.json")
        write_json(s2, path)
        calg, und, gam = compute_gamma(n)
        ok1 = check_against_schema1(n, und)
        sym = check_gamma_symmetry(calg.basis, calg.parity, gam)
        cnt, jac = check_deformed_jacobi(calg.basis, calg.parity, und, gam)
        d = s2["inhomogeneous_deformation"]
        print(f"n={n}: gamma entries={d['num_entries']} (K-entries={d['num_K_entries']}), "
              f"undeformed==Schema1: {ok1}, antisym/parity failures: {len(sym)}, "
              f"deformed Jacobi triples: {cnt}, failures: {len(jac)} -> {path}")


if __name__ == "__main__":
    main([int(a) for a in sys.argv[1:]] or [1, 2, 3])
