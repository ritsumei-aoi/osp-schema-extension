"""
C_gamma.py
Generates Schema 2 (gamma structure / inhomogeneous deformation) for C(n+1).

The inhomogeneous deformation of C(n+1) is parametrized by 4n symbolic
gb parameters:
  gb_{a1p, bj+}, gb_{a1p, bj-}, gb_{a1m, bj+}, gb_{a1m, bj-}  for j=1,...,n

The deformed oscillator relations are:
  [b_j^s, a_1^sigma] = -gb_{sigma, j, s} * kappa

The gamma 2-cocycle coefficients gamma_{abc} are determined by computing
[X, Y]_gamma = [X, Y]_0 + kappa * gamma(X, Y)
and comparing with the deformed oscillator bracket.

We implement this symbolically: gamma(X, Y) is a polynomial in gb parameters.
"""

import json
import os
import sys
from fractions import Fraction

sys.path.insert(0, os.path.dirname(__file__))
from C_generators import build_basis, build_parity_dict, parse_label, cartan_eigenvalue


def gb_label(sigma, j, s):
    """Return gb parameter label. sigma in {p, m}, j int, s in {p, m}."""
    return f"gb_a1{sigma}_b{j}{s}"


def build_gb_params(n):
    """Return list of 4n gb parameter labels."""
    params = []
    for j in range(1, n + 1):
        for sigma in ["p", "m"]:
            for s in ["p", "m"]:
                params.append(gb_label(sigma, j, s))
    return params


class GbExpr:
    """Symbolic linear expression in gb parameters (for gamma coefficients)."""
    def __init__(self, terms=None):
        self.terms = terms or {}  # {gb_label: Fraction(coeff)}

    def __add__(self, other):
        r = GbExpr(dict(self.terms))
        for k, v in other.terms.items():
            r.terms[k] = r.terms.get(k, Fraction(0)) + v
        r.terms = {k: v for k, v in r.terms.items() if v != 0}
        return r

    def __mul__(self, scalar):
        return GbExpr({k: v * scalar for k, v in self.terms.items()})

    def __rmul__(self, scalar):
        return self.__mul__(scalar)

    def __neg__(self):
        return self.__mul__(Fraction(-1))

    def is_zero(self):
        return len(self.terms) == 0

    def to_dict(self):
        return {k: str(v) for k, v in self.terms.items()}

    def __repr__(self):
        return f"GbExpr({self.terms})"


def single_gb(label, coeff=Fraction(1)):
    return GbExpr({label: coeff})


def compute_gamma_coefficients(n, even_basis, odd_basis):
    """
    Compute gamma(X, Y) for all basis pairs (X, Y).

    The deformation: [b_j^s, a_1^sigma] = -gb_{sigma,j,s} * kappa.

    gamma(X, Y) is non-zero only when:
    - X or Y involves a_1 (odd generator) and the other involves b (any).
    - Specifically, only brackets involving odd generators with the a_1^sigma
      oscillator coupled to b_j oscillators produce gb-terms.

    We compute: for each pair (X, Y) of basis generators,
    gamma(X, Y) = sum_Z gamma_{XY}^Z * Z (as a GbExpr for each Z).

    Returns: list of {X, Y, Z, gamma_expr} dicts where gamma_expr is a GbExpr.
    """
    parity = build_parity_dict(even_basis, odd_basis)
    basis = odd_basis + even_basis
    results = []

    for X in basis:
        for Y in basis:
            gamma_XY = _compute_gamma_XY(X, Y, n, parity, even_basis, odd_basis)
            for Z, expr in gamma_XY.items():
                if not expr.is_zero():
                    results.append({
                        "X": X,
                        "Y": Y,
                        "Z": Z,
                        "gamma_expr": expr
                    })
    return results


def _compute_gamma_XY(X, Y, n, parity, even_basis, odd_basis):
    """
    Compute gamma(X, Y) by evaluating the deformed bracket.

    The deformation only affects brackets involving a_1^sigma with b_j^s,
    via [b_j^s, a_1^sigma] = -gb_{sigma,j,s} * kappa.

    gamma(X,Y) is the coefficient of kappa in the deformed bracket [X,Y]_{gamma}.

    For the oscillator algebra, the bracket [X,Y]_{gamma} differs from [X,Y]_0
    only when X or Y contains a_1^sigma and the other contains b_j^s in a
    configuration that creates a deformed commutation.

    The main contributions come from:
    1. Brackets between odd generators (eps_del type) and even generators (2del, del_del)
       where the deformed [b_j, a_1] relation is applied.
    2. Brackets involving the Cartan generators H_k which involve b_k^+b_k^-.
    """
    px = parity.get(X, 0)
    py = parity.get(Y, 0)

    Xr = parse_label(X, n)
    Yr = parse_label(Y, n)
    if Xr is None or Yr is None:
        return {}

    Xt, Xdata = Xr
    Yt, Ydata = Yr

    result = {}  # Z -> GbExpr

    def add(Z, expr):
        if Z is None or expr.is_zero():
            return
        if Z not in result:
            result[Z] = GbExpr()
        result[Z] = result[Z] + expr

    # Only eps_del generators carry the a_1^sigma oscillator.
    # The deformation [b_j^s, a_1^sigma] = -gb_{sigma,j,s} * kappa arises when:
    # We have an eps_del generator (a_1^sigma * b_k^delta) and another generator
    # containing b_j (which it does if it's: 2del, del_del, or H).
    #
    # gamma(X, Y) comes from replacing [b_j^s, a_1^sigma] -> gb term in the bracket.

    # Case: X = eps_del, Y = H
    if Xt == "eps_del" and Yt == "H":
        # [a_1^{es}b_k^{ds}, H_m]_gamma
        # H_m is built from number operators, so [b_k, H_m] has no deformation.
        # But H_1 includes a_1^+a_1^-: [a_1^{es}b_k^{ds}, a_1^+a_1^-]
        # The a_1 part of H_1 doesn't have b terms, so no deformation contribution.
        # -> gamma = 0 (undeformed Cartan action)
        return {}

    if Xt == "H" and Yt == "eps_del":
        return {}

    # Case: X = eps_del, Y = eps_del
    # {a_1^{es1}b_k^{ds1}, a_1^{es2}b_l^{ds2}}
    # The deformation [b_j, a_1] creates new terms when the b from one generator
    # meets the a_1 from the other. In the graded product:
    # XY + YX with deformed relations:
    # The b_k^{ds1} from X meets a_1^{es2} from Y via [b_k, a_1] deformation.
    # Similarly b_l^{ds2} from Y meets a_1^{es1} from X.
    #
    # Term from XY: a_1^{es1}(b_k^{ds1} a_1^{es2}) b_l^{ds2}
    #   = a_1^{es1}(a_1^{es2}b_k^{ds1} - gb_{es2,k,ds1}*kappa) b_l^{ds2}
    #   = [XY]_0 - gb_{es2,k,ds1} * kappa * a_1^{es1}b_l^{ds2}
    # Term from YX: a_1^{es2}(b_l^{ds2} a_1^{es1}) b_k^{ds1}
    #   = a_1^{es2}(a_1^{es1}b_l^{ds2} - gb_{es1,l,ds2}*kappa) b_k^{ds1}
    #   = [YX]_0 - gb_{es1,l,ds2} * kappa * a_1^{es2}b_k^{ds1}
    #
    # gamma(X,Y) = -(gb_{es2,k,ds1} * a_1^{es1}b_l^{ds2} + gb_{es1,l,ds2} * a_1^{es2}b_k^{ds1})
    # (The kappa contribution to the bracket.)
    if Xt == "eps_del" and Yt == "eps_del":
        es1, k, ds1 = Xdata
        es2, l, ds2 = Ydata

        sigma2 = "p" if es2 > 0 else "m"
        s1 = "p" if ds1 > 0 else "m"
        gb2 = gb_label(sigma2, k, s1)  # gb_{sigma2, k, ds1}

        sigma1 = "p" if es1 > 0 else "m"
        s2 = "p" if ds2 > 0 else "m"
        gb1 = gb_label(sigma1, l, s2)  # gb_{sigma1, l, ds2}

        # Contribution 1: -gb_{es2,k,ds1} * E_eps1_del{l}_{es1,ds2}
        ss1 = ("p" if es1 > 0 else "m") + ("p" if ds2 > 0 else "m")
        Z1 = f"E_eps1_del{l}_{ss1}"
        add(Z1, single_gb(gb2, Fraction(-1)))

        # Contribution 2: -gb_{es1,l,ds2} * E_eps1_del{k}_{es2,ds1}
        ss2 = ("p" if es2 > 0 else "m") + ("p" if ds1 > 0 else "m")
        Z2 = f"E_eps1_del{k}_{ss2}"
        add(Z2, single_gb(gb1, Fraction(-1)))

        return {Z: expr for Z, expr in result.items() if not expr.is_zero()}

    # Case: X = eps_del, Y = 2del
    # [a_1^{es}b_k^{ds}, (b_l^{ls})^2]_gamma
    # Deformed: b_k^{ds}*(b_l^{ls})^2 -> a_1^{es}*(b_l^{ls} * b_k^{ds} * b_l^{ls} + ...)
    # Wait, actually we use: [b_k^{ds}, b_l^{ls}] = 0 (bosons, no deformation).
    # Deformation only affects [b, a_1]. In [a_1^{es}b_k^{ds}, (b_l^{ls})^2]:
    # = a_1^{es}[b_k^{ds}, (b_l^{ls})^2] + [a_1^{es}, (b_l^{ls})^2]*b_k^{ds}
    # The second term: [a_1^{es}, (b_l^{ls})^2] = ... this is a bosonic-fermionic commutator.
    # In the deformed algebra: [b_l^{ls}, a_1^{es}] = gb_{es,l,ls}*kappa.
    # So [a_1^{es}, (b_l^{ls})^2] = -[(b_l^{ls})^2, a_1^{es}]
    # = -(b_l^{ls}[b_l^{ls}, a_1^{es}] + [b_l^{ls}, a_1^{es}]b_l^{ls})
    # = -(b_l^{ls}*gb_{es,l,ls}*kappa + gb_{es,l,ls}*kappa*b_l^{ls})
    # = -2*gb_{es,l,ls}*kappa*b_l^{ls}   (since kappa is central, b_l*kappa = kappa*b_l)
    # So: [a_1^{es}b_k^{ds}, (b_l^{ls})^2]_gamma
    #   = [a_1^{es}b_k^{ds}, (b_l^{ls})^2]_0 + (-2*gb_{es,l,ls}*kappa*b_l^{ls})*b_k^{ds}
    # gamma contribution: -2*gb_{es,l,ls} * b_l^{ls}*b_k^{ds}
    # This is an even generator E_del_del or E_2del.
    if Xt == "eps_del" and Yt == "2del":
        es, k, ds = Xdata
        l, ls = Ydata
        sigma_e = "p" if es > 0 else "m"
        s_ls = "p" if ls > 0 else "m"
        gb = single_gb(gb_label(sigma_e, l, s_ls), Fraction(-2))
        # Result: -2*gb_{es,l,ls} * b_l^{ls} * b_k^{ds}
        _add_boson_product_gb(l, ls, k, ds, n, gb, add)
        return {Z: expr for Z, expr in result.items() if not expr.is_zero()}

    if Xt == "2del" and Yt == "eps_del":
        # [Y, X} for (even, odd) -> -gamma(X, Y) since gamma is antisymmetric
        # Actually: gamma([Y,X}) = -gamma(X,Y) with graded sign
        # For even Y, odd X: [Y,X} = -[X,Y} => gamma(Y,X) = -gamma(X,Y)... no wait.
        # The deformed bracket [Y,X}_gamma = [Y,X}_0 + kappa*gamma(Y,X).
        # And [Y,X}_0 = -[X,Y}_0 for even Y, odd X (graded antisymmetry p(Y)*p(X)=0).
        # gamma(Y,X) from direct computation: swap X,Y in above.
        es, k, ds = Ydata
        l, ls = Xdata
        sigma_e = "p" if es > 0 else "m"
        s_ls = "p" if ls > 0 else "m"
        gb = single_gb(gb_label(sigma_e, l, s_ls), Fraction(-2))
        # gamma(Y=2del, X=eps_del): from [b_l^{ls}, a_1^{es}] = gb * kappa in (b_l^{ls})^2 * a_1^{es}b_k^{ds}
        # Same computation: -2*gb * b_l^{ls}*b_k^{ds} (same formula by symmetry of computation)
        # But wait: graded antisymmetry says gamma(Y,X) = -(-1)^{p(X)p(Y)} gamma(X,Y).
        # p(X)=1 (eps_del), p(Y)=0 (2del): gamma(Y,X) = -gamma(X,Y).
        # However, we should compute directly rather than use this.
        # For [Y, X]_gamma with Y = (b_l^{ls})^2, X = a_1^{es}b_k^{ds}:
        # = Y*X + (graded sign)*X*Y ... actually the bracket is defined as [Y,X} = YX - (-1)^{p(Y)p(X)} XY.
        # p(Y)=0, p(X)=1: [Y,X} = YX - XY = -[X,Y}.
        # So [Y,X}_gamma = -[X,Y}_gamma, meaning gamma(Y,X) = -gamma(X,Y).
        # gamma(X,Y) = -2*gb * b_l^{ls}b_k^{ds} generator.
        # gamma(Y,X) = +2*gb * b_l^{ls}b_k^{ds} generator.
        gb_pos = single_gb(gb_label(sigma_e, l, s_ls), Fraction(2))
        _add_boson_product_gb(l, ls, k, ds, n, gb_pos, add)
        return {Z: expr for Z, expr in result.items() if not expr.is_zero()}

    # Case: X = eps_del, Y = del_del
    # [a_1^{es}b_k^{ds}, b_i^{t1}b_j^{t2}]_gamma
    # Deformed via [b_i^{t1}, a_1^{es}] = gb_{es,i,t1}*kappa (rearranging [b,a]=gb*kappa)
    # [a_1^{es}b_k^{ds}, b_i^{t1}b_j^{t2}]_gamma
    # = [a_1^{es}b_k^{ds}, b_i^{t1}b_j^{t2}]_0
    #   + deformation from [a_1^{es}, b_i^{t1}b_j^{t2}]: kappa * (b_i^{t1}*gb_{es,j,t2} + gb_{es,i,t1}*b_j^{t2}) * b_k^{ds}
    # Wait: [a_1^{es}, b_i^{t1}b_j^{t2}] = [a_1^{es}, b_i^{t1}]*b_j^{t2} + b_i^{t1}*[a_1^{es}, b_j^{t2}]
    # [a_1^{es}, b_p^{tp}] = -[b_p^{tp}, a_1^{es}] = gb_{es,p,tp}*kappa.
    # So [a_1^{es}, b_i^{t1}b_j^{t2}] = gb_{es,i,t1}*kappa*b_j^{t2} + gb_{es,j,t2}*kappa*b_i^{t1}
    # Full bracket: a_1^{es}[b_k^{ds}, b_i^{t1}b_j^{t2}] + [a_1^{es}, b_i^{t1}b_j^{t2}]*b_k^{ds}
    # gamma contribution: gb_{es,i,t1}*b_j^{t2}*b_k^{ds} + gb_{es,j,t2}*b_i^{t1}*b_k^{ds}
    if Xt == "eps_del" and Yt == "del_del":
        es, k, ds = Xdata
        i, j, t1, t2 = Ydata
        sigma_e = "p" if es > 0 else "m"

        s_t1 = "p" if t1 > 0 else "m"
        gb_i = single_gb(gb_label(sigma_e, i, s_t1), Fraction(1))
        # Contribution: gb_{es,i,t1} * b_j^{t2}*b_k^{ds}
        _add_boson_product_gb(j, t2, k, ds, n, gb_i, add)

        s_t2 = "p" if t2 > 0 else "m"
        gb_j = single_gb(gb_label(sigma_e, j, s_t2), Fraction(1))
        # Contribution: gb_{es,j,t2} * b_i^{t1}*b_k^{ds}
        _add_boson_product_gb(i, t1, k, ds, n, gb_j, add)

        return {Z: expr for Z, expr in result.items() if not expr.is_zero()}

    if Xt == "del_del" and Yt == "eps_del":
        # gamma(del_del, eps_del) = -gamma(eps_del, del_del) by graded antisymmetry
        # (del_del is even, eps_del is odd)
        sub = _compute_gamma_XY(Y, X, n, parity, even_basis, odd_basis)
        return {Z: -expr for Z, expr in sub.items()}

    # Case: H with eps_del
    # H involves number operators but no direct [b, a_1] deformation in the bracket.
    # [H_k, a_1^{es}b_j^{ds}]_gamma: H_k = {number ops in b and a_1}.
    # H_1 = a_1^+a_1^- + b_1^+b_1^-: action on odd generator via adjoint.
    # The deformation doesn't affect Cartan action (H acts by eigenvalue, no gb mixing).
    # However, if H contains a_1^+a_1^-, when this acts on b_j^{ds} there could be
    # indirect deformation effects, but in practice the commutator [H_1, E_eps_del]
    # is purely an eigenvalue scaling, so gamma = 0.

    # All other cases (H-H, H-even, even-even): no a_1 involvement -> gamma = 0.
    return {}


def _add_boson_product_gb(p, sp, q, tq, n, gb_expr, add):
    """Add gb_expr * (even generator for b_p^{sp}*b_q^{tq}) to result."""
    if gb_expr.is_zero():
        return

    if p == q:
        if sp == tq:
            sign_str = "p" if sp > 0 else "m"
            add(f"E_2del{p}_{sign_str}", gb_expr)
        else:
            # Number operator: express in H (only the bosonic part, no eps_N here)
            # This is b_p^+ b_p^- or b_p^-b_p^+ in an even bracket context -> just N_{b_p}
            if sp > 0:
                _add_N_bk_gb(p, n, gb_expr, add)
            else:
                _add_N_bk_gb(p, n, gb_expr, add)
                # constant 1 dropped
    else:
        if p < q:
            i, j, s1, s2 = p, q, sp, tq
        else:
            i, j, s1, s2 = q, p, tq, sp
        ss = ("p" if s1 > 0 else "m") + ("p" if s2 > 0 else "m")
        add(f"E_del{i}_del{j}_{ss}", gb_expr)


def _add_N_bk_gb(k, n, expr, add):
    """Add expr * N_{b_k} = expr * (H_{k+1}+...+H_n - H_{n+1}) in H basis."""
    for m in range(k + 1, n + 1):
        add(f"H_{m}", expr)
    add(f"H_{n+1}", expr * Fraction(-1))


def build_schema2(n):
    """Build the Schema 2 dict for C(n+1) with bosonic rank n."""
    import json as _json
    even_basis, odd_basis = build_basis(n)

    gb_params = build_gb_params(n)
    gamma_data = compute_gamma_coefficients(n, even_basis, odd_basis)

    algebra_names = {1: "C(2)", 2: "C(3)", 3: "C(4)"}
    osp_names = {1: "osp(2|2)", 2: "osp(2|4)", 3: "osp(2|6)"}
    even_dim = 2 * n * n + n + 1
    odd_dim = 4 * n

    gamma_list = []
    for entry in gamma_data:
        gamma_list.append({
            "X": entry["X"],
            "Y": entry["Y"],
            "Z": entry["Z"],
            "gamma_expr": entry["gamma_expr"].to_dict()
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
        "inhomogeneous_deformation": {
            "description": "Gamma coefficients for C(n+1) inhomogeneous deformation",
            "deformed_relation": "[b_j^s, a_1^sigma]_gamma = -gb_{sigma,j,s} * kappa",
            "gb_matrix": {
                "size": f"2 x 2n = {2 * 2 * n}",
                "parameters": gb_params,
                "parity": 1
            },
            "gamma_coefficients": gamma_list
        },
        "metadata": {
            "generated_by": "C_gamma.py",
            "generation_date": "2026-10-04",
            "references": [
                "Frappat et al. (2000)",
                "C_inhomogeneous_definition.md"
            ]
        }
    }
    return schema


def generate_all(output_dir="data"):
    os.makedirs(output_dir, exist_ok=True)
    for n in [1, 2, 3]:
        schema = build_schema2(n)
        out_path = os.path.join(output_dir, f"C_{n}_gamma.json")
        with open(out_path, "w") as f:
            json.dump(schema, f, indent=2)
        nb_gamma = len(schema["inhomogeneous_deformation"]["gamma_coefficients"])
        print(f"Written {out_path}: {nb_gamma} gamma entries")

    # Consistency check: verify gamma Z labels are in basis
    for n in [1, 2, 3]:
        even, odd = build_basis(n)
        basis_set = set(even + odd)
        path = os.path.join(output_dir, f"C_{n}_gamma.json")
        with open(path) as f:
            data = json.load(f)
        for entry in data["inhomogeneous_deformation"]["gamma_coefficients"]:
            for lbl in [entry["X"], entry["Y"], entry["Z"]]:
                if lbl not in basis_set:
                    print(f"  WARNING n={n}: label {lbl} not in basis!")


if __name__ == "__main__":
    generate_all()
