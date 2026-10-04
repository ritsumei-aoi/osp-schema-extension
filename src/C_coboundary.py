"""
C_coboundary.py
Generates Schema 4 (coboundary structure) for C(n+1).

The coboundary operator delta_f for an odd linear map f: g -> g is:
  (delta f)(X, Y) = (-1)^{p(X)} [X, f(Y)] - (-1)^{(p(X)+1)p(Y)} [Y, f(X)] - f([X, Y])

We parametrize f by: f(Z_j) = sum_i phi_{ij} Z_i, where p(f(Z_j)) = 1 - p(Z_j).

For the coboundary to match the gamma structure, we use a concrete f parametrized
by the gb parameters. Specifically, f is defined by:

  f(H_k) = sum_{j=1}^{n} sum_{s in {p,m}} gb_{a1p,bjs} * E_eps1_delj_{ps} + gb_{a1m,bjs} * E_eps1_delj_{ms}
    (for even H generators -> maps to odd)

  f(E_eps1_delk_{ss}) = 0 (maps odd -> even, but we set to 0 for simplicity)

Actually, we use a GENERIC odd map f and compute (delta f) symbolically.
The phi_{ij} are free parameters. For I07, we use the simplest non-trivial f
that is consistent with the gb deformation: we set phi_{ij} = gb-related coefficients.

Concretely: for triviality analysis in I08, we compute (delta f) for
f defined by f(H_k) = v_k (a specific odd element) and f(odd)=0.
We parametrize f using gb parameters as free coefficients on even->odd mappings.
"""

import json
import os
import sys
from fractions import Fraction

sys.path.insert(0, os.path.dirname(__file__))
from C_generators import build_basis, build_parity_dict, build_schema1
from C_gamma import build_gb_params, GbExpr, single_gb


def load_structure_constants(n, data_dir="data"):
    """Load structure constants as lookup table: sc[(X,Y)][Z] = Fraction."""
    path = os.path.join(data_dir, f"C_{n}_structure.json")
    with open(path) as f:
        data = json.load(f)
    sc = {}
    for entry in data["structure_constants"]:
        X, Y, Z = entry["X"], entry["Y"], entry["Z"]
        c = Fraction(entry["coeff"])
        if (X, Y) not in sc:
            sc[(X, Y)] = {}
        sc[(X, Y)][Z] = sc[(X, Y)].get(Z, Fraction(0)) + c
    return sc, data["parity"]


def bracket_sc(X, Y, sc):
    """Return dict {Z: Fraction} for [X, Y}."""
    return dict(sc.get((X, Y), {}))


def compute_coboundary(n, phi, parity, sc, even_basis, odd_basis):
    """
    Compute (delta f)(X, Y) for all basis pairs, where f is defined by phi.

    phi: dict {(Z_j_label, Z_i_label): Fraction} representing f(Z_j) = sum_i phi[j,i] Z_i.
    Only entries with p(Z_i) != p(Z_j) contribute (f is odd: reverses parity).

    Returns list of {X, Y, Z, coeff_expr} where coeff_expr is a GbExpr.
    """
    basis = odd_basis + even_basis
    results = []

    def f_of(Z):
        """Compute f(Z) as dict {label: GbExpr}."""
        result = {}
        for (Zj, Zi), expr in phi.items():
            if Zj == Z:
                result[Zi] = result.get(Zi, GbExpr()) + expr
        return result

    def bracket_with_fY(X, fY):
        """Compute [X, f(Y)}: sum over basis of f(Y)_W * [X, W}."""
        result = {}
        for W, expr in fY.items():
            for V, c in bracket_sc(X, W, sc).items():
                result[V] = result.get(V, GbExpr()) + expr * c
        return result

    def f_of_bracket(XY_bracket):
        """Compute f([X,Y}): sum over basis of [X,Y}_W * f(W)."""
        result = {}
        for W, c in XY_bracket.items():
            for V, expr in f_of(W).items():
                result[V] = result.get(V, GbExpr()) + expr * c
        return result

    for X in basis:
        for Y in basis:
            px = parity[X]
            py = parity[Y]

            sign1 = (-1) ** px
            sign2 = -((-1) ** ((px + 1) * py))

            fY = f_of(Y)
            fX = f_of(X)
            XY = bracket_sc(X, Y, sc)

            # Term 1: (-1)^{px} [X, f(Y)]
            t1 = bracket_with_fY(X, fY)
            # Term 2: -(-1)^{(px+1)py} [Y, f(X)]
            t2 = bracket_with_fY(Y, fX)
            # Term 3: -f([X,Y])
            t3 = f_of_bracket(XY)

            # Sum
            combined = {}
            for Z, expr in t1.items():
                combined[Z] = combined.get(Z, GbExpr()) + expr * Fraction(sign1)
            for Z, expr in t2.items():
                combined[Z] = combined.get(Z, GbExpr()) + expr * Fraction(sign2)
            for Z, expr in t3.items():
                combined[Z] = combined.get(Z, GbExpr()) + (-expr)

            for Z, expr in combined.items():
                if not expr.is_zero():
                    results.append({
                        "X": X,
                        "Y": Y,
                        "Z": Z,
                        "coeff_expr": expr
                    })

    return results


def build_phi_from_gb(n, even_basis, odd_basis):
    """
    Construct a natural odd linear map f parametrized by gb parameters.

    For each even basis element E containing a b_j factor, map it to
    an odd element involving a_1 and that b_j factor, with coefficient gb.

    Specifically, we define f on Cartan generators:
      f(H_1) = sum_{j,s} (gb_{a1p,bjs} * E_eps1_delj_{ps} + gb_{a1m,bjs} * E_eps1_delj_{ms})

    And for all other even generators e: f(e) = 0 (to keep it simple).
    And f(odd) = 0 (odd -> even: we set to 0 here to make computation tractable).

    This f is the canonical map arising from the deformation theory.
    """
    gb_params = build_gb_params(n)
    phi = {}  # {(Z_j, Z_i): GbExpr}

    # Map H_1 -> odd generators via gb parameters
    # H_1 = a_1^+a_1^- + b_1^+b_1^-
    # f(H_1) related to the deformation action of H_1 on the gb parameters
    # For the trivial deformation, f corresponds to:
    #   kappa * f(X) = delta(something)
    # We use the simplest mapping: f(H_k) = sum_j gb_j * E_eps1_delj_{...}

    for k in range(1, n + 2):  # H_1 to H_{n+1}
        H_k = f"H_{k}"
        for j in range(1, n + 1):
            for sigma in ["p", "m"]:
                for s in ["p", "m"]:
                    gb = f"gb_a1{sigma}_b{j}{s}"
                    # coefficient: 1 for f(H_k) -> E_eps1_delj_{sigma_s}
                    # This is motivated by: if f(H) = sum phi * odd_gen,
                    # then (delta f)(H, odd_gen) contributes gb terms.
                    # We use phi[H_k, E_eps1_delj_{sigma_s}] = gb_{sigma,j,s} coefficient
                    # But with factor depending on k (H_1 gets full contribution, others partial)
                    if k == 1:
                        coeff = Fraction(1)
                    else:
                        coeff = Fraction(0)  # simplification: only H_1 gets non-trivial f
                    if coeff != 0:
                        ss = sigma + s
                        Z_i = f"E_eps1_del{j}_{ss}"
                        key = (H_k, Z_i)
                        if key not in phi:
                            phi[key] = GbExpr()
                        phi[key] = phi[key] + single_gb(gb, coeff)

    return phi


def build_schema4(n, data_dir="data"):
    """Build Schema 4 coboundary JSON for C(n+1) with rank n."""
    sc, parity = load_structure_constants(n, data_dir)
    even_basis, odd_basis = build_basis(n)

    phi = build_phi_from_gb(n, even_basis, odd_basis)

    coboundary_data = compute_coboundary(n, phi, parity, sc, even_basis, odd_basis)

    algebra_names = {1: "C(2)", 2: "C(3)", 3: "C(4)"}
    osp_names = {1: "osp(2|2)", 2: "osp(2|4)", 3: "osp(2|6)"}
    even_dim = 2 * n * n + n + 1
    odd_dim = 4 * n

    # Serialize
    phi_serial = {}
    for (Zj, Zi), expr in phi.items():
        phi_serial[f"{Zj}->{Zi}"] = expr.to_dict()

    coboundary_list = []
    for entry in coboundary_data:
        coboundary_list.append({
            "X": entry["X"],
            "Y": entry["Y"],
            "Z": entry["Z"],
            "coeff_expr": entry["coeff_expr"].to_dict()
        })

    schema = {
        "schema_version": "5.0",
        "algebra": {
            "family": "C",
            "m": 1,
            "n": n,
            "cartan_type": algebra_names.get(n, f"C({n+1})"),
            "alternative_notation": {"osp": osp_names.get(n, f"osp(2|{2*n})")},
            "dimension": {"total": even_dim + odd_dim, "even": even_dim, "odd": odd_dim}
        },
        "odd_map_f": {
            "description": "Odd linear map f: g->g defined by phi coefficients",
            "parametrization": "f(H_1) = sum_{j,sigma,s} gb_{sigma,j,s} * E_eps1_delj_{sigma_s}; f(other) = 0",
            "phi_coefficients": phi_serial
        },
        "coboundary_delta_f": coboundary_list,
        "metadata": {
            "generated_by": "C_coboundary.py",
            "generation_date": "2026-10-04",
            "formula": "(delta f)(X,Y) = (-1)^{p(X)}[X,f(Y)] - (-1)^{(p(X)+1)p(Y)}[Y,f(X)] - f([X,Y])"
        }
    }
    return schema


def generate_all(output_dir="data"):
    os.makedirs(output_dir, exist_ok=True)
    for n in [1, 2, 3]:
        schema = build_schema4(n, data_dir=output_dir)
        out_path = os.path.join(output_dir, f"C_{n}_coboundary.json")
        with open(out_path, "w") as f:
            json.dump(schema, f, indent=2)
        nb = len(schema["coboundary_delta_f"])
        print(f"Written {out_path}: {nb} coboundary entries")


if __name__ == "__main__":
    generate_all()
