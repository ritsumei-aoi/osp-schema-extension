"""
C_gamma.py — Generate Schema 2 (gamma/inhomogeneous deformation) JSON for C(n+1) = osp(2|2n).

The inhomogeneous deformation is defined by the exchange relation:
  [b_j^s, a_1^sigma] = -gb_{sigma, j, s} * kappa

where kappa is the odd central element. The deformation gives a 2-cocycle gamma
on the Lie superalgebra g = C(n+1), defined by:
  [X, Y]_gamma = [X, Y]_0 + kappa * gamma(X, Y)

The gamma coefficients gamma_{abc} (where [X_a, X_b] has a component kappa * gamma_{abc} X_c)
are derived by substituting the oscillator realizations and applying the deformed relations.

Since kappa is odd and the deformation is via gb parameters (parity 1), gamma is an
odd 2-cochain: gamma(X, Y) ≠ 0 only when p(X) + p(Y) is odd (one even, one odd argument).

Concretely: the deformation affects brackets involving b_j^s and a_1^sigma.
The only affected brackets are those where the bracket computation uses the
mixed commutator [b_j^s, a_1^sigma]. In the undeformed algebra this is 0,
but in the deformed case it contributes -gb_{sigma,j,s} * kappa.

From the deformed bracket formula, gamma(X, Y) is determined by:
  gamma(X, Y) = sum_{j,s,sigma} (contribution from gb_{sigma,j,s})

For C(n+1), the non-zero gamma coefficients arise from brackets of the form:
  [E_even, E_odd] or [E_odd, E_even]
where the bracket in the undeformed case picks up a contribution from [b^s, a_1^sigma].
"""

from __future__ import annotations
import json
import datetime
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from C_generators import make_basis, make_parity


def load_schema(n: int) -> dict:
    data_dir = os.path.join(os.path.dirname(__file__), "..", "data")
    path = os.path.join(data_dir, f"C_{n}_structure.json")
    with open(path) as f:
        return json.load(f)


def gb_label(sigma: int, j: int, s: int) -> str:
    """Return gb parameter label for (sigma, j, s): sigma=±1, j=1..n, s=±1."""
    sa = "p" if sigma == 1 else "m"
    sb = "p" if s == 1 else "m"
    return f"gb_a1{sa}_b{j}{sb}"


def compute_gamma(n: int) -> list:
    """
    Compute gamma coefficients for the inhomogeneous deformation of C(n+1).

    The deformation: [b_j^s, a_1^sigma] = -gb_{sigma,j,s} * kappa

    The affected brackets: wherever a b_j^s and a_1^sigma "meet" in a bracket computation.
    For the generators of C(n+1):

    Even generators: H_k, E_2del{k}_p/m, E_del{i}_del{j}_pp/mm/pm/mp
    Odd generators: E_eps1_del{k}_pp/pm/mp/mm (= a_1^sigma b_k^s)

    Key deformed brackets (derived from oscillator algebra with [b_j^s, a_1^sigma] = -gb * kappa):

    1. [H_1, E_eps1_del{k}_σs] deformed term:
       H_1 = a_1^+ a_1^- + b_1^+ b_1^-
       E_eps1_del{k}_σs = a_1^sigma b_k^s
       [H_1, a_1^sigma b_k^s] = (a_1^+ a_1^- + b_1^+b_1^-)(a_1^sigma b_k^s) - (a_1^sigma b_k^s)(a_1^+ a_1^- + b_1^+b_1^-)
       ...the deformation affects only the part involving b_1^± and a_1^±.
       In the deformed algebra, [b_j^s, a_1^sigma] = -gb_{sigma,j,s} kappa.
       The contribution to gamma comes from b_1^± acting on a_1^sigma:
       [b_1^+b_1^-, a_1^sigma b_k^s] deformed term = b_1^+ [b_1^-, a_1^sigma] b_k^s + [b_1^+, a_1^sigma] b_1^- b_k^s
                                                   = b_1^+(-gb_{sigma,1,-}) kappa b_k^s + (-gb_{sigma,1,+}) kappa b_1^- b_k^s
       ...but these involve kappa * b, which is in kappa*g (the abelian extension), not g itself.
       Actually, the deformation formula gives the gamma coefficient as the coefficient of kappa
       in [X,Y]_deformed when restricted to contributions in g (not kappa*g).

       More precisely: gamma(X, Y) is the coefficient in g such that
       [X, Y]_gamma = [X, Y]_0 + kappa * gamma(X, Y).

       The relevant contributions are from brackets where a b_j^s and a_1^sigma
       appear as "crossing" oscillators. From the oscillator algebra:

       For [E_even, E_odd]: the even generator contains b_i operators, the odd contains a_1^sigma b_k.
       The deformation contribution at first order in gb is:
       [b_i^t, a_1^sigma] = -gb_{sigma,i,t} kappa  (only when i=k for relevant brackets)

       Let me compute the gamma coefficients systematically by considering all pairs (X_even, X_odd)
       where the bracket picks up a deformation term.

    The systematic approach:
    For X = even generator (b_i^t composition) and Y = E_eps1_del{k}_sigma_s (= a_1^sigma b_k^s):
    [X, Y]_deformed = [X, Y]_0 + kappa * gamma(X, Y)

    gamma(X, Y) comes from the deformed oscillator relation [b_i^t, a_1^sigma] = -gb_{sigma,i,t} kappa.

    In the bracket [X, Y], wherever b_i^t from X and a_1^sigma from Y "commute past each other",
    they contribute -gb_{sigma,i,t} kappa times the remaining operator product.

    For even generator X = b_i^t b_j^u (or (b_i^t)^2):
    [b_i^t b_j^u, a_1^sigma b_k^s]
    = b_i^t [b_j^u, a_1^sigma b_k^s] + [b_i^t, a_1^sigma b_k^s] b_j^u
    = b_i^t ((-gb_{sigma,j,u} kappa) b_k^s + a_1^sigma [b_j^u, b_k^s]) + ((-gb_{sigma,i,t} kappa) b_k^s + a_1^sigma [b_i^t, b_k^s]) b_j^u

    The kappa terms: b_i^t (-gb_{sigma,j,u} kappa) b_k^s + (-gb_{sigma,i,t} kappa) b_k^s b_j^u
    = -gb_{sigma,j,u} b_i^t kappa b_k^s - gb_{sigma,i,t} kappa b_k^s b_j^u

    Since kappa commutes trivially with everything (it's central), and kappa acts trivially on g:
    = -kappa (gb_{sigma,j,u} b_i^t b_k^s + gb_{sigma,i,t} b_j^u b_k^s)

    The coefficient of kappa gives gamma(X, Y):
    gamma(b_i^t b_j^u, a_1^sigma b_k^s) ~ -(gb_{sigma,j,u} b_i^t b_k^s + gb_{sigma,i,t} b_j^u b_k^s)

    But this gives terms in bosonic oscillator algebra (b products), which correspond to even generators.
    We need to express these in terms of the basis generators.

    For the case i=j (X = (b_i^t)^2):
    gamma((b_i^t)^2, a_1^sigma b_k^s) ~ -2 gb_{sigma,i,t} b_k^s b_i^t

    This gives a linear combination of b-oscillator products = even generators.

    Since we want gamma(X,Y) as an element of g (expressed in the basis {Z_c}):
    gamma(X, Y) = sum_c gamma_{XY}^c Z_c

    where Z_c runs over the basis. But here the result is an even generator (since X is even and Y is odd,
    and kappa is odd, so kappa*gamma must be odd → gamma is even).

    Let me implement this computation for all relevant pairs.
    """
    gamma_list = []

    def add_gamma(X, Y, Z, coeff_str):
        gamma_list.append({"X": X, "Y": Y, "Z": Z, "gamma_coeff": coeff_str})

    # For each even generator X = b_i^{si} b_j^{sj} (or (b_i^{si})^2)
    # and each odd generator Y = a_1^{sigma} b_k^{s}:
    # gamma(X, Y) is computed from the deformation [b^t, a_1^sigma] = -gb_{sigma,t} kappa

    # Even generator types:
    # E_2del{i}_p: (b_i^+)^2 = b_i^+ b_i^+
    # E_2del{i}_m: (b_i^-)^2 = b_i^- b_i^-
    # E_del{i}_del{j}_pp: b_i^+ b_j^+
    # E_del{i}_del{j}_mm: b_i^- b_j^-
    # E_del{i}_del{j}_pm: b_i^+ b_j^-
    # E_del{i}_del{j}_mp: b_i^- b_j^+

    # Odd generator Y = E_eps1_del{k}_{sigma}{s}: a_1^sigma b_k^s
    # where sigma ∈ {+,-}, s ∈ {+,-}

    # gamma(X, Y) = sum of terms from [b^t, a_1^sigma] deformation

    for sigma in [1, -1]:
        sigma_str = "p" if sigma == 1 else "m"
        for k in range(1, n + 1):
            for s in [1, -1]:
                s_str = "p" if s == 1 else "m"
                Y = f"E_eps1_del{k}_{sigma_str}{s_str}"

                # For each even generator X:
                # The gamma(X, Y) = -(sum over b oscillators A in X) gb_{sigma,A_index,A_sign} * (remaining b product with b_k^s)

                # Case: X = E_2del{i}_p = (b_i^+)^2
                for i in range(1, n + 1):
                    X = f"E_2del{i}_p"
                    # [b_i^+ b_i^+, a_1^sigma b_k^s]:
                    # gamma = -(gb_{sigma,i,+} b_i^+ b_k^s + gb_{sigma,i,+} b_i^+ b_k^s) = -2 gb_{sigma,i,+} b_i^+ b_k^s
                    # Note: actually it's:
                    # Term from first b_i^+: -gb_{sigma,i,+} b_i^+ b_k^s
                    # Term from second b_i^+: -gb_{sigma,i,+} b_i^+ b_k^s
                    # Wait: for X = b_i^+ b_i^+:
                    # gamma(b_i^+ b_i^+, a_1^sigma b_k^s) = -gb_{sigma,i,+} * (b_i^+ b_k^s) [from first b]
                    #                                      + (-gb_{sigma,i,+}) * (b_i^+ b_k^s) [from second b]
                    # = -2 gb_{sigma,i,+} b_i^+ b_k^s
                    gb = gb_label(sigma, i, 1)  # gb_{sigma, i, +}
                    # Result: -2 gb_{sigma,i,+} * b_i^+ b_k^s
                    # b_i^+ b_k^s is an even generator
                    if i == k and s == 1:
                        Z = f"E_2del{i}_p"
                        add_gamma(X, Y, Z, f"-2*{gb}")
                    elif i != k and s == 1:
                        idx_i, idx_k = min(i, k), max(i, k)
                        si_lab = "p" if i < k else "p"
                        sk_lab = "p"
                        Z = f"E_del{min(i,k)}_del{max(i,k)}_pp"
                        coeff = -2
                        add_gamma(X, Y, Z, f"{coeff}*{gb}")
                    elif i == k and s == -1:
                        # b_i^+ b_i^- = N_i contribution → Cartan
                        # We don't record Cartan contributions in gamma for now (they contribute to H terms)
                        # Actually, this DOES contribute. b_i^+ b_k^s for k=i, s=-1: that's b_i^+ b_i^- = N_i.
                        # This is an even generator combination. We'll record it as a Cartan contribution.
                        # N_i is not directly a basis element, but contributes to H generators.
                        # gamma(X, Y) = -2 gb * N_i expressed in Cartans.
                        # N_i = sum_{j=i+1}^n H_j - H_{n+1} - 1/2 (but the 1/2 is a scalar, drops from g)
                        # Since we're working in g (not the scalar extension), the 1/2 drops.
                        # We record gamma as a linear combination of Cartan generators.
                        for j in range(i + 1, n + 1):
                            add_gamma(X, Y, f"H_{j}", f"-2*{gb}")
                        add_gamma(X, Y, f"H_{n+1}", f"2*{gb}")
                    elif i != k and s == -1:
                        # b_i^+ b_k^- : E_del{min}_del{max}_{pm or mp}
                        if i < k:
                            Z = f"E_del{i}_del{k}_pm"
                        else:
                            Z = f"E_del{k}_del{i}_mp"
                        add_gamma(X, Y, Z, f"-2*{gb}")

                # Case: X = E_2del{i}_m = (b_i^-)^2
                for i in range(1, n + 1):
                    X = f"E_2del{i}_m"
                    gb = gb_label(sigma, i, -1)  # gb_{sigma, i, -}
                    # gamma = -2 gb_{sigma,i,-} b_i^- b_k^s
                    if i == k and s == -1:
                        Z = f"E_2del{i}_m"
                        add_gamma(X, Y, Z, f"-2*{gb}")
                    elif i != k and s == -1:
                        Z = f"E_del{min(i,k)}_del{max(i,k)}_mm"
                        add_gamma(X, Y, Z, f"-2*{gb}")
                    elif i == k and s == 1:
                        # b_i^- b_i^+ = N_i + 1 (scalar dropped)
                        for j in range(i + 1, n + 1):
                            add_gamma(X, Y, f"H_{j}", f"-2*{gb}")
                        add_gamma(X, Y, f"H_{n+1}", f"2*{gb}")
                    elif i != k and s == 1:
                        if k < i:
                            Z = f"E_del{k}_del{i}_pm"
                        else:
                            Z = f"E_del{i}_del{k}_mp"
                        add_gamma(X, Y, Z, f"-2*{gb}")

                # Case: X = E_del{i}_del{j}_pp = b_i^+ b_j^+ (i < j)
                for i in range(1, n + 1):
                    for j in range(i + 1, n + 1):
                        X = f"E_del{i}_del{j}_pp"
                        # gamma(b_i^+ b_j^+, a_1^sigma b_k^s):
                        # = -gb_{sigma,j,+} b_i^+ b_k^s - gb_{sigma,i,+} b_j^+ b_k^s
                        gb_i = gb_label(sigma, i, 1)
                        gb_j = gb_label(sigma, j, 1)

                        # Term from b_j^+: -gb_{sigma,j,+} * b_i^+ b_k^s
                        _add_bosonic_pair(add_gamma, X, Y, i, 1, k, s, n, f"-1*{gb_j}")
                        # Term from b_i^+: -gb_{sigma,i,+} * b_j^+ b_k^s
                        _add_bosonic_pair(add_gamma, X, Y, j, 1, k, s, n, f"-1*{gb_i}")

                # Case: X = E_del{i}_del{j}_mm = b_i^- b_j^- (i < j)
                for i in range(1, n + 1):
                    for j in range(i + 1, n + 1):
                        X = f"E_del{i}_del{j}_mm"
                        gb_i = gb_label(sigma, i, -1)
                        gb_j = gb_label(sigma, j, -1)
                        _add_bosonic_pair(add_gamma, X, Y, i, -1, k, s, n, f"-1*{gb_j}")
                        _add_bosonic_pair(add_gamma, X, Y, j, -1, k, s, n, f"-1*{gb_i}")

                # Case: X = E_del{i}_del{j}_pm = b_i^+ b_j^- (i < j)
                for i in range(1, n + 1):
                    for j in range(i + 1, n + 1):
                        X = f"E_del{i}_del{j}_pm"
                        gb_i = gb_label(sigma, i, 1)
                        gb_j = gb_label(sigma, j, -1)
                        _add_bosonic_pair(add_gamma, X, Y, i, 1, k, s, n, f"-1*{gb_j}")  # wait, sign
                        # [b_i^+ b_j^-, a_1^sigma b_k^s]:
                        # from b_j^-: -gb_{sigma,j,-} b_i^+ b_k^s
                        # from b_i^+: -gb_{sigma,i,+} b_j^- b_k^s
                        _add_bosonic_pair(add_gamma, X, Y, j, -1, k, s, n, f"-1*{gb_i}")

                # Case: X = E_del{i}_del{j}_mp = b_i^- b_j^+ (i < j)
                for i in range(1, n + 1):
                    for j in range(i + 1, n + 1):
                        X = f"E_del{i}_del{j}_mp"
                        gb_i = gb_label(sigma, i, -1)
                        gb_j = gb_label(sigma, j, 1)
                        _add_bosonic_pair(add_gamma, X, Y, i, -1, k, s, n, f"-1*{gb_j}")
                        _add_bosonic_pair(add_gamma, X, Y, j, 1, k, s, n, f"-1*{gb_i}")

                # Also: Cartan generators H_k contain b oscillators (H_1 also has a_1 oscillators)
                # For H_1 = a_1^+ a_1^- + b_1^+ b_1^-:
                # [H_1, a_1^sigma b_k^s]:
                # b_1^+ b_1^- part: [b_1^+ b_1^-, a_1^sigma b_k^s] deformed
                #   = b_1^+(-gb_{sigma,1,-} kappa) b_k^s + (-gb_{sigma,1,+} kappa) b_1^- b_k^s + (undeformed terms)
                # gamma contribution: -gb_{sigma,1,-} b_1^+ b_k^s - gb_{sigma,1,+} b_1^- b_k^s
                # These are odd generator contributions... wait no: b_1^± b_k^s are even generators.
                # But gamma(X,Y) for X=H_1 (even) and Y=odd must be even.
                # b_1^+ b_k^s and b_1^- b_k^s ARE even operators.
                # Express them as basis generators...
                #
                # Wait: gamma(H_k, E_odd) where the result is an even generator Z?
                # The deformed [H_k, E_odd] = [H_k, E_odd]_0 + kappa * gamma(H_k, E_odd)
                # gamma(H_k, E_odd) must be an even element of g.
                #
                # For H_1 = a_1^+a_1^- + b_1^+b_1^-:
                # a_1^+ a_1^- part: [a_1^+a_1^-, a_1^sigma b_k^s]
                #   deformed contribution: a_1^+[a_1^-, a_1^sigma b_k^s]_deformed + [a_1^+, a_1^sigma b_k^s]_deformed a_1^-
                #   But [a_1, b] = 0, so no deformation here.
                # b_1^+b_1^- part: [b_1^+b_1^-, a_1^sigma b_k^s]
                #   deformed: b_1^+[b_1^-, a_1^sigma] b_k^s + [b_1^+, a_1^sigma] b_1^- b_k^s
                #   = b_1^+(-gb_{sigma,1,-} kappa) b_k^s + (-gb_{sigma,1,+} kappa) b_1^- b_k^s
                #   gamma(H_1, Y) from this = -gb_{sigma,1,-} * b_1^+ b_k^s - gb_{sigma,1,+} * b_1^- b_k^s

                # H_1: contributes for k_boson=1 only (from b_1^+b_1^- part)
                H_label = "H_1"
                gb_1m = gb_label(sigma, 1, -1)
                gb_1p = gb_label(sigma, 1, 1)
                # Term: -gb_{sigma,1,-} b_1^+ b_k^s
                _add_bosonic_pair(add_gamma, H_label, Y, 1, 1, k, s, n, f"-1*{gb_1m}")
                # Term: -gb_{sigma,1,+} b_1^- b_k^s
                _add_bosonic_pair(add_gamma, H_label, Y, 1, -1, k, s, n, f"-1*{gb_1p}")

                # H_j (j=2..n): H_j = b_{j-1}^+ b_{j-1}^- - b_j^+ b_j^-
                for h_j in range(2, n + 1):
                    H_label = f"H_{h_j}"
                    # From b_{j-1}^+ b_{j-1}^-:
                    gb_jm1_m = gb_label(sigma, h_j - 1, -1)
                    gb_jm1_p = gb_label(sigma, h_j - 1, 1)
                    _add_bosonic_pair(add_gamma, H_label, Y, h_j - 1, 1, k, s, n, f"-1*{gb_jm1_m}")
                    _add_bosonic_pair(add_gamma, H_label, Y, h_j - 1, -1, k, s, n, f"-1*{gb_jm1_p}")
                    # From -b_j^+ b_j^-: negative sign
                    gb_j_m = gb_label(sigma, h_j, -1)
                    gb_j_p = gb_label(sigma, h_j, 1)
                    _add_bosonic_pair(add_gamma, H_label, Y, h_j, 1, k, s, n, f"1*{gb_j_m}")
                    _add_bosonic_pair(add_gamma, H_label, Y, h_j, -1, k, s, n, f"1*{gb_j_p}")

                # H_{n+1} = -b_n^+ b_n^-:
                H_label = f"H_{n+1}"
                gb_n_m = gb_label(sigma, n, -1)
                gb_n_p = gb_label(sigma, n, 1)
                _add_bosonic_pair(add_gamma, H_label, Y, n, 1, k, s, n, f"1*{gb_n_m}")
                _add_bosonic_pair(add_gamma, H_label, Y, n, -1, k, s, n, f"1*{gb_n_p}")

    return gamma_list


def _add_bosonic_pair(add_fn, X, Y, b_idx1, b_sign1, b_idx2, b_sign2, n, coeff_str):
    """
    Add gamma contribution for b_{b_idx1}^{b_sign1} b_{b_idx2}^{b_sign2} as even generator Z.
    Handle equal indices (squared term) and ordering conventions.
    """
    if b_idx1 == b_idx2:
        if b_sign1 == b_sign2:
            s = "p" if b_sign1 == 1 else "m"
            Z = f"E_2del{b_idx1}_{s}"
            add_fn(X, Y, Z, coeff_str)
        else:
            # b_i^+ b_i^- or b_i^- b_i^+: both are N_i (or N_i+1, scalar dropped)
            # Express N_i as Cartan combination (without the -1/2 constant)
            i = b_idx1
            # N_i = sum_{j=i+1}^n H_j - H_{n+1}  (dropping constant -1/2)
            for j in range(i + 1, n + 1):
                add_fn(X, Y, f"H_{j}", coeff_str)
            add_fn(X, Y, f"H_{n+1}", f"-({coeff_str})" if not coeff_str.startswith("-") else coeff_str[1:])
    else:
        i, si = min(b_idx1, b_idx2), (b_sign1 if b_idx1 < b_idx2 else b_sign2)
        j, sj = max(b_idx1, b_idx2), (b_sign2 if b_idx1 < b_idx2 else b_sign1)
        si_str = "p" if si == 1 else "m"
        sj_str = "p" if sj == 1 else "m"
        Z = f"E_del{i}_del{j}_{si_str}{sj_str}"
        add_fn(X, Y, Z, coeff_str)


def build_schema2(n: int) -> dict:
    """Build Schema 2 JSON for C(n+1) with bosonic rank n."""
    # Load Schema 1 for algebra/basis info
    schema1 = load_schema(n)

    # Build gb_matrix
    gb_params = {}
    for sigma in [1, -1]:
        sa = "p" if sigma == 1 else "m"
        for j in range(1, n + 1):
            for s in [1, -1]:
                sb = "p" if s == 1 else "m"
                label = f"gb_a1{sa}_b{j}{sb}"
                gb_params[label] = {
                    "parity": 1,
                    "index": {"sigma": sa, "j": j, "s": sb},
                    "description": f"[b_{j}^{sb}, a_1^{sa}] deformation parameter",
                }

    gamma_coeffs = compute_gamma(n)

    schema = {
        "schema_version": "5.0",
        "algebra": schema1["algebra"],
        "gb_matrix": {
            "size": f"2 x 2n = {4*n}",
            "description": "4n deformation parameters of parity 1",
            "parameters": gb_params,
        },
        "inhomogeneous_deformation": {
            "description": (
                "Gamma 2-cocycle: [X,Y]_deformed = [X,Y]_0 + kappa * gamma(X,Y). "
                "Non-zero only when p(X) + p(Y) is odd (even-odd or odd-even pair). "
                "gamma_coeff is a symbolic expression in gb parameters."
            ),
            "gamma_coefficients": gamma_coeffs,
        },
        "metadata": {
            "generated_by": "src/C_gamma.py",
            "generation_date": datetime.date.today().isoformat(),
        },
    }
    return schema


def main():
    data_dir = os.path.join(os.path.dirname(__file__), "..", "data")
    os.makedirs(data_dir, exist_ok=True)

    for n in range(1, 4):
        schema = build_schema2(n)
        out_path = os.path.join(data_dir, f"C_{n}_gamma.json")
        with open(out_path, "w") as f:
            json.dump(schema, f, indent=2)
        n_gamma = len(schema["inhomogeneous_deformation"]["gamma_coefficients"])
        n_gb = len(schema["gb_matrix"]["parameters"])
        print(f"Generated {out_path}: {n_gb} gb params, {n_gamma} gamma coefficients")


if __name__ == "__main__":
    main()
