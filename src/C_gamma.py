"""Issue I05: Schema 2 (inhomogeneous deformation / gamma structure) for C(n+1).

Deformed oscillator relations (docs/math/C_inhomogeneous_definition.md):
    [b_j^s, a_1^sigma] = - gb_{sigma, j, s} * kappa,   kappa odd central, kappa^2 = 0.
For basis elements X, Y (symmetrized quadratics) the deformed bracket is
    [X, Y]_gamma = [X, Y]_0 + kappa * gamma(X, Y),       gamma(X,Y) in g + C K,
and gamma is linear in the 4n parameters gb.

Usage: python3 src/C_gamma.py [n ...]   -> data/C_{n}_gamma.json
"""
from __future__ import annotations

import datetime as _dt
import json
import os
import sys
from fractions import Fraction
from typing import Dict, List, Tuple

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from C_common import (DATA_DIR, LieSuperalgebra, LinForm, lf_add, lf_json, lf_str,  # noqa: E402
                      vec_add)
from C_generators import (REFERENCES, algebra_block, build_elements,  # noqa: E402
                          central_elements_block, make_decomposer, pbw_order)
from oscillator_algebra import OscillatorAlgebra, graded_commutator  # noqa: E402

GammaTable = Dict[Tuple[str, str], Dict[str, LinForm]]  # (X,Y) -> {Z: linear form in gb}


def gb_matrix_block(alg: OscillatorAlgebra) -> dict:
    n = alg.n
    rows = ["a_1_p", "a_1_m"]
    cols = alg.bosons
    params = [[f"gb_a1{sig}_b{j}{s}" for j in range(1, n + 1) for s in ("p", "m")] for sig in ("p", "m")]
    return {
        "shape": [2, 2 * n],
        "rows": rows,
        "columns": cols,
        "parameters": params,
        "flat": alg.params,
        "count": 4 * n,
        "parity": 1,
        "parity_note": ("The deformation term gb*kappa is odd (kappa carries the odd parity); "
                        "gb values are treated as scalar (c-number) coefficients in all computations, "
                        "following the pre-oscillator form (b|a) in C_inhomogeneous_definition.md."),
        "definition": "[b_j^s, a_1^sigma] = - gb_a1{sigma}_b{j}{s} * kappa",
    }


def compute_gamma(n: int, check_against_schema1: bool = True) -> Tuple[GammaTable, OscillatorAlgebra]:
    alg = OscillatorAlgebra(n, deformed=True)
    elements = build_elements(alg)
    dec = make_decomposer(alg, elements, with_K=True)
    labels = pbw_order(n)
    g = LieSuperalgebra.load(n) if check_against_schema1 else None
    gamma: GammaTable = {}
    for X in labels:
        for Y in labels:
            br = graded_commutator(elements[X], elements[Y])
            x0, kparts = br.split_kappa()
            # consistency with Schema 1: the kappa-free part is the undeformed bracket
            c0 = dec.decompose(x0)
            if g is not None:
                stored = g.bracket(X, Y)
                if {k: v for k, v in c0.items()} != stored:
                    raise RuntimeError(f"[{X},{Y}}}: kappa-free part {c0} != Schema 1 {stored}")
            if "" in kparts:
                raise RuntimeError(f"[{X},{Y}}}: kappa term without parameter")
            entry: Dict[str, LinForm] = {}
            for param, el in kparts.items():
                for Z, c in dec.decompose(el).items():
                    entry[Z] = lf_add(entry.get(Z, {}), {param: c})
            entry = {Z: lf for Z, lf in entry.items() if lf}
            if entry:
                gamma[(X, Y)] = entry
    return gamma, alg


# ---------------------------------------------------------------------------
# Consistency checks on gamma
# ---------------------------------------------------------------------------
def check_gamma_antisymmetry(gamma: GammaTable, parity: Dict[str, int], labels: List[str]) -> List:
    """gamma(X,Y) = -(-1)^{p(X)p(Y)} gamma(Y,X)."""
    failures = []
    for X in labels:
        for Y in labels:
            sign = -1 if (parity[X] and parity[Y]) else 1
            lhs = gamma.get((X, Y), {})
            rhs = {Z: lf_add({}, lf, Fraction(-sign)) for Z, lf in gamma.get((Y, X), {}).items()}
            if lhs != rhs:
                failures.append((X, Y))
    return failures


def check_L_jacobi(gamma: GammaTable, g: LieSuperalgebra) -> Tuple[int, List]:
    """Super-Jacobi on L = g + kappa (g + C K) with
       [X, Y]     = [X,Y]_0 + kappa gamma(X,Y)
       [X, kW]    = (-1)^{p(X)} kappa [X,W]_0
       [kW, X]    = kappa [W, X]_0
       [kW, kW']  = 0.
    Elements are pairs (v, w) meaning v + kappa w, with w-components linear forms in gb.
    Checked on all triples of basis elements of g (triples involving kappa-elements reduce
    to the Schema 1 Jacobi identity, already verified in I04).
    """
    labels = g.labels
    p = g.parity

    def br_g(X: str, Y: str):  # returns (v: Vec, w: {Z: LinForm})
        return g.bracket(X, Y), gamma.get((X, Y), {})

    def br_elem(A: str, v, w):
        """[A, (v, w)] for basis element A and element (v, w) with w symbolic."""
        out_v = g.bracket_vec(A, v)
        out_w: Dict[str, LinForm] = {}
        # kappa-part from [A, v]: gamma(A, V) * v_V
        for V, c in v.items():
            for Z, lf in gamma.get((A, V), {}).items():
                out_w[Z] = lf_add(out_w.get(Z, {}), lf, c)
        # kappa-part from [A, kappa w] = (-1)^{p(A)} kappa [A, w]_0
        sign = Fraction(-1 if p[A] else 1)
        for W, lf in w.items():
            for Z, c in g.bracket(A, W).items():
                out_w[Z] = lf_add(out_w.get(Z, {}), lf, sign * c)
        return out_v, {Z: lf for Z, lf in out_w.items() if lf}

    failures = []
    count = 0
    for X in labels:
        for Y in labels:
            for Z in labels:
                count += 1
                tot_v, tot_w = {}, {}
                for (A, B, C) in ((X, Y, Z), (Y, Z, X), (Z, X, Y)):
                    sign = Fraction(-1 if (p[A] and p[C]) else 1)
                    v, w = br_g(B, C)
                    rv, rw = br_elem(A, v, w)
                    tot_v = vec_add(tot_v, rv, sign)
                    for W, lf in rw.items():
                        tot_w[W] = lf_add(tot_w.get(W, {}), lf, sign)
                tot_w = {W: lf for W, lf in tot_w.items() if lf}
                if tot_v or tot_w:
                    failures.append((X, Y, Z, tot_v, tot_w))
    return count, failures


# ---------------------------------------------------------------------------
# Schema 2 document
# ---------------------------------------------------------------------------
def build_schema2(n: int) -> Tuple[dict, GammaTable]:
    gamma, alg = compute_gamma(n)
    labels = pbw_order(n)
    order = {lab: i for i, lab in enumerate(labels + ["K"])}
    entries = []
    for X in labels:
        for Y in labels:
            for Z in sorted(gamma.get((X, Y), {}), key=lambda z: order[z]):
                lf = gamma[(X, Y)][Z]
                entries.append({"X": X, "Y": Y, "Z": Z, "coeff": lf_json(lf), "expr": lf_str(lf)})
    n_K = sum(1 for e in entries if e["Z"] == "K")
    doc = {
        "schema_version": "5.0",
        "schema_layer": 2,
        "algebra": algebra_block(n),
        "central_elements": central_elements_block(),
        "basis_ref": f"C_{n}_structure.json",
        "inhomogeneous_deformation": {
            "description": ("Inhomogeneous deformation of C(n+1): the fermion-boson exchange relations "
                            "acquire an odd central term kappa (docs/math/C_inhomogeneous_definition.md)."),
            "deformed_oscillator_relations": {
                "boson_fermion": "[b_j^s, a_1^σ] = - gb_{σ,j,s} kappa   (σ, s ∈ {+,-}, j = 1..n)",
                "unchanged": ["{a_1^-, a_1^+} = 1", "[b_i^-, b_j^+] = δ_ij", "kappa central, kappa^2 = 0"],
            },
            "gb_matrix": gb_matrix_block(alg),
            "gamma_convention": {
                "bracket": "[X,Y]_gamma = [X,Y]_0 + kappa * gamma(X,Y)",
                "target": "g + C K  (entries with Z = 'K' are constant terms of the symmetrized-quadratic realization)",
                "pairs": "all ordered pairs (X, Y) with non-zero gamma",
                "coeff_encoding": "linear form {gb parameter: rational}; gamma is homogeneous linear in gb",
            },
            "gamma": entries,
            "gamma_count": len(entries),
            "gamma_K_count": n_K,
        },
        "metadata": {
            "generated_by": "src/C_gamma.py",
            "generation_date": _dt.date.today().isoformat(),
            "notation": "handover/notation.md",
            "references": REFERENCES,
        },
    }
    return doc, gamma


def write_schema2(n: int, data_dir: str = DATA_DIR) -> Tuple[str, GammaTable]:
    doc, gamma = build_schema2(n)
    path = os.path.join(data_dir, f"C_{n}_gamma.json")
    with open(path, "w") as fh:
        json.dump(doc, fh, indent=1, ensure_ascii=False)
        fh.write("\n")
    return path, gamma


def load_gamma(n: int, data_dir: str = DATA_DIR) -> Tuple[dict, GammaTable]:
    with open(os.path.join(data_dir, f"C_{n}_gamma.json")) as fh:
        doc = json.load(fh)
    gamma: GammaTable = {}
    for e in doc["inhomogeneous_deformation"]["gamma"]:
        gamma.setdefault((e["X"], e["Y"]), {})[e["Z"]] = {k: Fraction(v) for k, v in e["coeff"].items()}
    return doc, gamma


if __name__ == "__main__":
    ns = [int(a) for a in sys.argv[1:]] or [1, 2, 3]
    ok_all = True
    for n in ns:
        path, gamma = write_schema2(n)
        g = LieSuperalgebra.load(n)
        doc = json.load(open(path))
        print(f"=== C({n+1}): wrote {os.path.basename(path)}: "
              f"{doc['inhomogeneous_deformation']['gamma_count']} gamma entries "
              f"({doc['inhomogeneous_deformation']['gamma_K_count']} with Z=K), "
              f"{len(gamma)} ordered pairs ===")
        print("kappa-free part == Schema 1 structure constants : PASS (asserted during generation)")
        af = check_gamma_antisymmetry(gamma, g.parity, g.labels)
        print(f"gamma super-antisymmetry                        : {'PASS' if not af else 'FAIL'}")
        cnt, jf = check_L_jacobi(gamma, g)
        print(f"super-Jacobi of deformed bracket on L=g+kappa(g+K): {'PASS' if not jf else 'FAIL'} ({cnt} triples)")
        for f in jf[:5]:
            print("   failure:", f)
        ok_all &= not (af or jf)
    print("SUMMARY:", "ALL PASS" if ok_all else "FAILURES")
    sys.exit(0 if ok_all else 1)
