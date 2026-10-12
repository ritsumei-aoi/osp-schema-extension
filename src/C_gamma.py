"""
C_gamma.py
Computes Schema 2 (inhomogeneous deformation / gamma structure) for C(n+1) = osp(2|2n).

Mathematical background (docs/math/C_inhomogeneous_definition.md):
  The inhomogeneous deformation is defined by the exchange relations between
  fermionic and bosonic oscillators:
    [b_j^s, a_1^sigma] = -gb_{sigma, j, s} * kappa
  for sigma in {+,-}, s in {+,-}.

  This modifies the Lie superalgebra bracket to:
    [X, Y]_gamma = [X, Y]_0 + kappa * gamma(X, Y)

  The gamma coefficients are computed by substituting the oscillator realizations
  of generators and evaluating the deformed bracket.

The key idea: In the deformed algebra, the relation
  b_j^s * a_1^sigma - a_1^sigma * b_j^s = -gb_{sigma,j,s} * kappa
replaces the undeformed commutator [b_j^s, a_1^sigma] = 0.

For any two generators X = o1*o2, Y = o3*o4, the gamma contribution is:
  gamma(X,Y) = (corrections from using -gb*kappa instead of 0 for mixed commutators)

Since kappa^2 = 0, only first-order terms in kappa contribute.
The gamma coefficient gamma(X,Y) arises when a boson-fermion contraction occurs
in the bracket computation.

Specifically: when computing [o1*o2, o3*o4}_0, if a mixed boson-fermion pair
would normally commute (c=0 in undeformed algebra), in the deformed algebra
[b_j^s, a_1^sigma] = -gb_{sigma,j,s} * kappa.

This contributes kappa * gamma term to the bracket.
"""

import json
import os
import sys
from fractions import Fraction
from datetime import date

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
from C_generators import build_basis, build_parity, gen_to_osc_pair, osc_parity, is_boson, is_fermion, parse_boson


def gb_label(sigma, j, s):
    """Return the gb parameter label for [b_j^s, a_1^sigma] = -gb * kappa."""
    sigma_str = "a1p" if sigma == "p" else "a1m"
    return f"gb_{sigma_str}_b{j}{s}"


def mixed_contraction_symbol(osc_a, osc_b):
    """
    In the deformed algebra, [b_j^s, a_1^sigma] = -gb_{sigma,j,s} * kappa.
    Returns gb_label if (osc_a, osc_b) is such a pair, else None.
    Convention: [boson, fermion] = -gb * kappa.
    """
    if is_boson(osc_a) and is_fermion(osc_b):
        j, s = parse_boson(osc_a)
        sigma = "p" if osc_b == "a_1_p" else "m"
        return gb_label(sigma, j, s)
    if is_fermion(osc_a) and is_boson(osc_b):
        j, s = parse_boson(osc_b)
        sigma = "p" if osc_a == "a_1_p" else "m"
        # [a_1^sigma, b_j^s] = -[b_j^s, a_1^sigma] (but these are odd,even so graded comm applies)
        # For odd a_1^sigma (p=1) and even b_j^s (p=0):
        # [a, b}_g = ab - (-1)^{1*0} ba = ab - ba = [a,b] (commutator, since different parities)
        # [b,a}_g = ba - (-1)^{0*1} ab = ba - ab = -[a,b]
        # So [a_1,b_j}_g = -[b_j, a_1}_g = -(-gb*kappa) = gb*kappa.
        return None  # Handled indirectly: when o_a=fermion, o_b=boson in the Wick formula,
                     # it's the fermion-boson mixed term, not boson-fermion.
                     # Actually we need to handle [a_1^sigma, b_j^s] = gb*kappa separately.
    return None


def mixed_contraction_symbol_full(osc_a, osc_b):
    """
    Return (gb_label, sign) for the contraction [osc_a, osc_b}_g in the deformed algebra.
    In undeformed algebra this is 0 for mixed pairs; in deformed it gets a kappa contribution.

    [b_j^s, a_1^sigma}_g = [b_j^s, a_1^sigma] = -gb_{sigma,j,s} (coefficient of kappa)
    [a_1^sigma, b_j^s}_g = [a_1^sigma, b_j^s] = +gb_{sigma,j,s}
    (since [b,a} = -[a,b} for even-odd pairs)
    """
    if is_boson(osc_a) and is_fermion(osc_b):
        j, s = parse_boson(osc_a)
        sigma = "p" if osc_b == "a_1_p" else "m"
        return gb_label(sigma, j, s), Fraction(-1)
    if is_fermion(osc_a) and is_boson(osc_b):
        j, s = parse_boson(osc_b)
        sigma = "p" if osc_a == "a_1_p" else "m"
        return gb_label(sigma, j, s), Fraction(1)
    return None, None


def compute_gamma(n):
    """
    Compute gamma coefficients for C(n+1).
    Returns list of {X, Y, Z, coeff_expr} where coeff_expr is a string
    expression in gb parameters (e.g. "gb_a1p_b1p" or "-gb_a1m_b2m").

    The gamma(X,Y) is the coefficient in:
      [X, Y]_gamma = [X, Y]_0 + kappa * gamma(X,Y)

    gamma(X,Y) is expressed in the basis of g (not kappa*g):
      [X, Y]_gamma contrib to kappa*Z means gamma_{XY}^Z coefficient.

    From the Wick contraction formula for [o1*o2, o3*o4}_g:
    Terms 1-4 come from contracting pairs (o2,o3), (o2,o4), (o1,o3), (o1,o4).
    In the deformed algebra, mixed pairs contribute gb*kappa instead of 0.
    Each such term gives a kappa * (single oscillator product expression).

    Since the result of a gb-deformation term is a single oscillator (not bilinear),
    and kappa*osc lives in kappa*g (the abelian extension), these terms give:
    kappa * (sum of oscillators acting on the vacuum) = kappa * (linear combination of basis).

    But actually: in the deformed algebra, the gb terms come from the modified bracket.
    The term kappa * gamma(X,Y) where gamma: g x g -> g.
    gamma(X,Y) is in g (the Lie superalgebra), so it's a linear combination of basis elements.

    For X = a_1^+ b_k^+ and Y = a_1^- b_l^-:
    In the deformed bracket, the mixed contractions [b_k^+, a_1^-] = -gb_{-,k,+} * kappa
    contribute. But since we're computing the coefficient of kappa, we need the
    remaining oscillator factor to be scalar or a basis element.

    Since X and Y are bilinears in oscillators (= two oscillators each), the
    gb correction to [X,Y} comes from:
    - Replacing one commutator [o_i, o_j} (normally 0 for mixed) with gb * kappa
    - The remaining oscillator product is then a single oscillator or scalar

    The result kappa * gamma(X,Y) has gamma(X,Y) being a linear combination
    of basis generators (the remaining oscillator factor after contraction).

    Key: For X = o1*o2, Y = o3*o4:
    gb-correction to Term 1 from (o2, o3) mixed pair:
      If o2 is boson and o3 is fermion (or vice versa):
        contrib = (gb_label, sign) * (o1 * o4) as a Lie algebra element
        (single osc product = basis element if o1,o4 are single osc.
         But o1*o4 is a product of two single oscillators = basis generator or number op.)

    Wait, the gb term comes from the deformed relation:
      [b_j^s, a_1^sigma} = -gb * kappa (instead of 0).
    This is a scalar in the kappa direction, not a generator.
    So the Wick formula term c_{23} * (o1 * o4) becomes:
      (-gb * kappa) * (o1 * o4) = kappa * (-gb) * (o1 * o4).
    And (o1 * o4) is a single oscillator or needs to be expressed as a sum of basis elements...

    Actually no: (o1 * o4) when the contraction involves a mixed pair means o2 and o3
    are consumed (contracted to kappa factor), leaving o1 and o4 as the remaining product.
    This product of two oscillators IS a Lie algebra generator or number operator.

    But we need kappa * (Lie algebra element), and kappa * g_element is in kappa*g
    (the abelian extension). In the Schema 2 formalism, gamma(X,Y) maps to g elements.
    So the coefficient of kappa*Z gives gamma_{XY}^Z.

    Implementation:
    For each pair (X, Y) of basis generators, go through the 4 Wick terms.
    For each term, check if the contraction is a mixed boson-fermion pair (gb-type).
    If so, record the gb coefficient and the remaining oscillator product (as basis element).
    """
    even, odd = build_basis(n)
    all_basis = even + odd
    basis_set = set(all_basis)
    parity = build_parity(even, odd)

    # Accumulate into dict keyed by (X, Y, Z, gb_param)
    gamma_acc = {}

    for i, X in enumerate(all_basis):
        for j, Y in enumerate(all_basis):
            if j <= i:
                continue

            x_pair = gen_to_osc_pair(X, n)
            y_pair = gen_to_osc_pair(Y, n)
            if x_pair is None or y_pair is None:
                continue

            (o1, o2), cx = x_pair
            (o3, o4), cy = y_pair
            p1 = osc_parity(o1)
            p2 = osc_parity(o2)
            p3 = osc_parity(o3)
            p4 = osc_parity(o4)

            coeff_total = cx * cy

            # Check each of the 4 Wick terms for mixed (gb) contractions
            pairs_and_signs = [
                (o2, o3, (o1, o4), Fraction(1)),
                (o2, o4, (o1, o3), Fraction((-1) ** (p2 * p3))),
                (o1, o3, (o4, o2), Fraction((-1) ** (p2 * (p3 + p4)))),
                (o1, o4, (o3, o2), Fraction((-1) ** (p2 * (p3 + p4) + p1 * p3))),
            ]

            for osc_a, osc_b, (rem_a, rem_b), sign in pairs_and_signs:
                gb_lbl, gb_sign = mixed_contraction_symbol_full(osc_a, osc_b)
                if gb_lbl is None:
                    continue

                rem_gens = _osc_pair_to_gens_simple(rem_a, rem_b, n)
                for Z, z_coeff in rem_gens.items():
                    if Z not in basis_set:
                        continue
                    total = coeff_total * sign * gb_sign * z_coeff
                    if total != 0:
                        key = (X, Y, Z, gb_lbl)
                        gamma_acc[key] = gamma_acc.get(key, Fraction(0)) + total

    # Convert to list, dropping zeros
    gamma_list = []
    for (X, Y, Z, gb_lbl), total in gamma_acc.items():
        if total != 0:
            gamma_list.append({
                "X": X,
                "Y": Y,
                "Z": Z,
                "coeff_expr": _coeff_to_expr(total, gb_lbl),
                "gb_param": gb_lbl,
                "numeric_coeff": str(total)
            })

    return gamma_list


def _osc_pair_to_gens_simple(o_a, o_b, n):
    """
    Express o_a * o_b as a dict {gen_label: coeff} of Lie algebra generators.
    Includes Cartan contributions from bosonic number operators n_k.
    The central element K is discarded (K ∉ g).
    """
    from C_generators import number_op_to_cartans
    result = {}

    if is_boson(o_a) and is_boson(o_b):
        ka, sa = parse_boson(o_a)
        kb, sb = parse_boson(o_b)
        if ka == kb and sa == sb:
            result[f"E_2del{ka}_{sa}"] = Fraction(1)
        elif ka < kb:
            result[f"E_del{ka}_del{kb}_{sa}{sb}"] = Fraction(1)
        elif ka > kb:
            result[f"E_del{kb}_del{ka}_{sb}{sa}"] = Fraction(1)
        else:
            # ka == kb, sa != sb: bosonic number operator n_ka → Cartan generators
            # b_k^+ b_k^- = n_k;  b_k^- b_k^+ = K + n_k (K discarded)
            cart, _ = number_op_to_cartans(ka, n, False)
            for g, c in cart.items():
                result[g] = result.get(g, Fraction(0)) + c
    elif is_fermion(o_a) and is_boson(o_b):
        sf = "p" if o_a == "a_1_p" else "m"
        kb, sb = parse_boson(o_b)
        result[f"E_eps1_del{kb}_{sf}{sb}"] = Fraction(1)
    elif is_boson(o_a) and is_fermion(o_b):
        ka, sa = parse_boson(o_a)
        sf = "p" if o_b == "a_1_p" else "m"
        result[f"E_eps1_del{ka}_{sf}{sa}"] = Fraction(1)
    elif is_fermion(o_a) and is_fermion(o_b):
        # a^+a^- = n_a → Cartan; a^-a^+ = K - n_a (K discarded); same^2 = 0
        if o_a != o_b:
            cart, _ = number_op_to_cartans(None, n, True)
            if o_a == "a_1_p" and o_b == "a_1_m":
                for g, c in cart.items():
                    result[g] = result.get(g, Fraction(0)) + c
            else:
                for g, c in cart.items():
                    result[g] = result.get(g, Fraction(0)) - c

    return result


def _coeff_to_expr(coeff, gb_lbl):
    """Format as coefficient string like '2*gb_a1p_b1p' or '-gb_a1m_b1m'."""
    if coeff == 1:
        return gb_lbl
    elif coeff == -1:
        return f"-{gb_lbl}"
    else:
        return f"{coeff}*{gb_lbl}"


def build_gb_parameters(n):
    """Return list of all 4n gb parameter labels."""
    params = []
    for j in range(1, n + 1):
        for sigma in ["p", "m"]:
            for s in ["p", "m"]:
                params.append(gb_label(sigma, j, s))
    return params


def build_schema2(n):
    """Build Schema 2 JSON for C(n+1) with bosonic rank n."""
    gb_params = build_gb_parameters(n)

    print(f"Computing gamma coefficients for C({n+1}) (n={n})...")
    gamma_list = compute_gamma(n)
    print(f"  Found {len(gamma_list)} gamma coefficient terms.")

    return {
        "schema_version": "5.0",
        "algebra": {
            "family": "C",
            "m": 1,
            "n": n,
            "cartan_type": f"C({n+1})",
            "alternative_notation": {"osp": f"osp(2|{2*n})"}
        },
        "gb_matrix": {
            "description": f"4n = {4*n} deformation parameters, parity 1",
            "size": 4 * n,
            "parameters": gb_params,
            "relation": "[b_j^s, a_1^sigma] = -gb_{sigma,j,s} * kappa",
            "parameter_parity": 1
        },
        "gamma_coefficients": gamma_list,
        "consistency_check": {
            "description": "Gamma computed from deformed oscillator relations",
            "schema1_basis_used": f"C_{n}_structure.json"
        },
        "metadata": {
            "generated_by": "src/C_gamma.py",
            "generation_date": str(date.today()),
            "references": [
                "docs/math/C_inhomogeneous_definition.md",
                "Frappat, Sciarrino, Sorba (2000)"
            ]
        }
    }


def main():
    os.makedirs("data", exist_ok=True)
    for n in [1, 2, 3]:
        schema = build_schema2(n)
        fname = f"data/C_{n}_gamma.json"
        with open(fname, "w") as f:
            json.dump(schema, f, indent=2)
        print(f"Written {fname}")


if __name__ == "__main__":
    main()
