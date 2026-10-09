#!/usr/bin/env python3
"""
Schema 2: Inhomogeneous deformation (gamma structure) for C(n+1) = osp(2|2n).

The deformation is defined by:
  [b_j^s, a_1^sigma]_deformed = -gb_{sigma,j,s} * kappa

This changes the oscillator algebra. The gamma-2-cocycle coefficients
gamma(X, Y) are derived by computing [X, Y] in the deformed algebra
and extracting the coefficient of kappa.

The deformed bracket is:
  [X, Y]_gamma = [X, Y]_0 + kappa * gamma(X, Y)

Since kappa is an odd central element and gamma(X,Y) must have parity
p(X)+p(Y)+1 (mod 2) to preserve total parity, we only get non-zero
gamma(X,Y) for pairs where p(X)+p(Y) is odd (i.e., one even, one odd).

Concretely: the deformed relation [b_j^s, a_1^sigma] = -gb_{sigma,j,s} * kappa
affects brackets involving a_1^± and b_k^±.

For each generator X, Y in the Lie superalgebra, gamma(X,Y) is computed by:
1. Replace each occurrence of the deformed commutator [b_j^s, a_1^sigma]
   with -gb_{sigma,j,s} in the oscillator computation.
2. The result is a polynomial in gb parameters times basis generators.

Since all generators are bilinear in oscillators, gamma(X,Y) is at most
linear in the gb parameters (each bilinear generator contributes at most
one deformed oscillator pair).
"""

from fractions import Fraction
from collections import defaultdict
import json
import os
import sys
from datetime import date

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data')
SRC_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SRC_DIR)
from C_generators import CnAlgebra, _mon_to_osc_names


def gb_label(sigma, j, s):
    """Return the gb parameter label gb_{sigma,j,s}."""
    sigma_str = 'a1p' if sigma == 'p' else 'a1m'
    s_str = 'p' if s == 'p' else 'm'
    return f'gb_{sigma_str}_b{j}{s_str}'


def compute_gamma(n):
    """Compute gamma(X,Y) coefficients as symbolic expressions in gb parameters.

    Returns: list of dicts {X, Y, Z, coeff_expr} where
      gamma(X,Y) = sum_Z coeff_expr_Z * Z (linear in gb params)
    """
    alg = CnAlgebra(n)
    gens, pars, basis_order = alg.build_generators()

    # The deformed relation: [b_j^s, a_1^sigma] = -gb_{sigma,j,s} * kappa
    # In the standard algebra: [b_j^s, a_1^sigma] = 0.
    # The deformation shifts the bracket by kappa * gamma(X,Y).

    # Strategy: for each pair (X, Y), compute the "deformed contribution"
    # which arises from replacing standard oscillator commutators with deformed ones.
    #
    # Since gamma(X,Y) is only non-zero when p(X) + p(Y) is odd (parity constraint),
    # we only need to consider even-odd and odd-even pairs.
    #
    # For a pair (X, Y) where X is even (bosonic bilinear) and Y is odd (mixed a1*b),
    # the deformation enters through the bracket of b^pm with a_1^pm.
    #
    # Concretely: [b_i^r * b_j^s, a_1^sigma * b_k^tau] involves moving b_i^r and b_j^s
    # past a_1^sigma. In the deformed algebra, b_i^r a_1^sigma = a_1^sigma b_i^r - gb_{sigma,i,r} * kappa.
    #
    # So the deformed bracket produces a kappa term proportional to gb.
    # We compute this symbolically.

    gamma_terms = []
    labels = basis_order

    for xi in labels:
        for xj in labels:
            pX = pars[xi]
            pY = pars[xj]
            # gamma(X,Y) is non-zero only for odd total parity (one even, one odd)
            if (pX + pY) % 2 == 0:
                continue

            # Compute gamma by working with the oscillator algebra directly
            # For a pair (X_even, Y_odd):
            # X_even is a bilinear in b's: b_i^r b_j^s or (b_k^pm)^2 or N_k or N^f+N_1
            # Y_odd is a_1^sigma b_k^tau

            # The bracket [X_even, Y_odd] in the deformed algebra gains a term
            # from the deformed commutator [b_i^r, a_1^sigma] = -gb_{sigma,i,r} * kappa.

            # Compute gamma numerically: gamma is the "kappa coefficient" in the deformed bracket.
            # Since gamma is linear in gb, we can compute it by computing the bracket
            # with one gb parameter set to 1 (and others to 0) and extracting the coefficient.

            gamma_contrib = _compute_gamma_for_pair(alg, gens, pars, basis_order, xi, xj, n)
            for z, expr in gamma_contrib.items():
                if expr:  # non-zero expression
                    gamma_terms.append({
                        'X': xi,
                        'Y': xj,
                        'Z': z,
                        'coeff_expr': expr,
                    })

    return gamma_terms


def _compute_gamma_for_pair(alg, gens, pars, basis_order, xi, xj, n):
    """Compute gamma(X,Y) for a specific pair.

    Returns: dict {Z: coeff_expr_string} where coeff_expr is a sum of gb params with signs.
    The coeff_expr is a string like "gb_a1p_b1p" or "-gb_a1m_b2m" or "gb_a1p_b1p + gb_a1m_b1m" etc.

    Implementation: for each gb parameter, compute the contribution to gamma
    by evaluating the bracket with that parameter = 1 (all others 0).
    """
    X = gens[xi]
    Y = gens[xj]
    pX = pars[xi]
    pY = pars[xj]

    # We need to find how the deformation affects [X, Y].
    # The deformed bracket: [b_j^s, a_1^sigma]_def = -gb_{sigma,j,s} * kappa
    # In normal algebra, this is 0.
    # So the deformed contribution to gamma(X, Y) comes from replacing
    # the zero commutator [b_j^s, a_1^sigma] = 0 with -gb * kappa.

    # For generators X = product of b's and Y = a1^sigma * b_k^tau:
    # The bracket [X, Y] involves moving b's in X past a_1^sigma in Y.
    # Each such move can contribute a gb term.

    # Approach: compute d[X,Y]/d(gb_{sigma,j,s}) for each gb parameter,
    # by setting that gb = epsilon and computing [X,Y]_deformed - [X,Y]_0 to O(epsilon).
    # This gives the linear coefficient of that gb parameter in gamma.

    result = {}  # Z -> list of (gb_label, coefficient)
    gb_contribs = {}  # Z -> {gb_label: Fraction}

    for j in range(1, n+1):
        for sigma in ['p', 'm']:
            for s in ['p', 'm']:
                gb = gb_label(sigma, j, s)
                # Compute the contribution from this gb parameter:
                # Replace [b_j^s, a_1^sigma] by -1 (and set this gb=1, others=0)
                # and compute the resulting change to the bracket.
                delta = _deformed_bracket_delta(alg, X, pX, Y, pY, j, sigma, s, n)
                if delta:
                    decomp = alg.decompose(delta, gens, pars, basis_order)
                    for z, c in decomp.items():
                        if z not in gb_contribs:
                            gb_contribs[z] = {}
                        existing = gb_contribs[z].get(gb, Fraction(0))
                        gb_contribs[z][gb] = existing + c

    # Build coeff_expr strings
    result = {}
    for z, gb_dict in gb_contribs.items():
        parts = []
        for gb_param, coeff in sorted(gb_dict.items()):
            if coeff == 0:
                continue
            if coeff == 1:
                parts.append(gb_param)
            elif coeff == -1:
                parts.append(f'-{gb_param}')
            else:
                parts.append(f'{coeff}*{gb_param}')
        if parts:
            result[z] = ' + '.join(parts).replace('+ -', '- ')
    return result


def _deformed_bracket_delta(alg, X, pX, Y, pY, j, sigma, s, n):
    """Compute the O(gb_{sigma,j,s}) contribution to [X,Y]_deformed - [X,Y]_0.

    This is the result of replacing one instance of the commutator
    [b_j^s, a_1^sigma] = 0 with -1 (setting gb_{sigma,j,s} = 1).

    The result is an algebra element (not containing kappa; kappa is factored out).

    Algorithm:
    - XY_deformed - XY_0 = sum over each position where b_j^s moves past a_1^sigma:
        X_{left} * (-1) * X_{right} * Y
      (the -1 comes from the deformed commutator replacing the zero commutator)
    - Similarly for YX.
    - Total delta = delta_XY - (-1)^{pX*pY} delta_YX
    """
    delta_XY = _delta_product(alg, X, Y, j, sigma, s, n, pX, pY)
    delta_YX = _delta_product(alg, Y, X, j, sigma, s, n, pY, pX)

    sign = -1 if (pX * pY) % 2 == 1 else 1
    result = defaultdict(Fraction)
    for m, c in delta_XY.items():
        result[m] += c
    for m, c in delta_YX.items():
        result[m] -= Fraction(sign) * c
    return {k: v for k, v in result.items() if v != 0}


def _delta_product(alg, X, Y, j, sigma, s, n, pX, pY):
    """Compute the deformed contribution to XY from gb_{sigma,j,s}=1.

    When moving X_monomials (containing b_j^s) past Y_monomials (containing a_1^sigma),
    each passage of b_j^s past a_1^sigma contributes -1 (instead of 0).

    For monomials X_m and Y_m, the contribution arises when b_j^s (from X_m)
    is moved past a_1^sigma (from Y_m) in normal ordering.

    Since all monomials are at most bilinear and b_j^s commutes with a_1^sigma
    normally (delta_deformed = 0 -> -1 shift), the deformed contribution is:
    for each (b_j^s in X_m) x (a_1^sigma in Y_m): contribute -(count) * X_m_without_bjs * Y_m_without_a1sig
    """
    # X_m * Y_m: normally we have XY via normal_ordering.
    # Deformed: each time b_j^s (from X part) moves past a_1^sigma (from Y part),
    # we get an extra -1 times the remainder.
    # This is the "contraction" between b_j^s and a_1^sigma.

    # b_j^s is a bosonic oscillator (parity 0), a_1^sigma is a fermionic (parity 1).
    # In normal product: X_m * Y_m, to bring X_m to normal order with Y_m,
    # the b_j^s operators from X_m pass through the fermionic a_1^sigma from Y_m.
    # In the standard algebra: b_j^s * a_1^sigma = a_1^sigma * b_j^s (they commute).
    # In the deformed algebra: b_j^s * a_1^sigma = a_1^sigma * b_j^s - gb * kappa.
    # So each passage of b_j^s past a_1^sigma contributes -gb * kappa * (reduced product).

    # Since monomial X_m has at most 2 bosonic oscillators (bilinear) and
    # Y_m has exactly 1 fermionic oscillator, the number of b_j^s operators
    # in X_m that need to pass a_1^sigma is the power of b_j^s in X_m.
    # But we only care about the power of b_j^s (of species j and sign s) in X_m.

    a1_idx = 0 if sigma == 'p' else 1
    b_idx = 2 + 2*(j-1) + (0 if s == 'p' else 1)

    result = defaultdict(Fraction)

    for mx, cx in X.items():
        for my, cy in Y.items():
            # Count b_j^s in X_m: mx[b_idx]
            # Count a_1^sigma in Y_m: my[a1_idx]
            n_bjs_in_X = mx[b_idx]
            n_a1sigma_in_Y = my[a1_idx]

            if n_bjs_in_X == 0 or n_a1sigma_in_Y == 0:
                continue

            # Number of times b_j^s from X passes a_1^sigma from Y:
            # Since the fermionic operators commute with bosonic, and in normal ordering
            # we first write all of X then Y, we need to move b_j^s (in X) past a_1^sigma (in Y).
            # There are n_bjs_in_X * n_a1sigma_in_Y such passages.
            # But since n_a1sigma_in_Y <= 1 (at most one a_1^sigma per monomial),
            # and n_bjs_in_X <= 2, the contribution is n_bjs_in_X passages.

            # Each passage: b_j^s * a_1^sigma -> a_1^sigma * b_j^s - 1 (coefficient of kappa term).
            # So the deformed contribution replaces one b_j^s ... a_1^sigma -> -1 * (remove both).
            # The "remainder" monomial: X_m with b_j^s power reduced by 1, Y_m with a_1^sigma reduced by 1.
            # Then the remaining operators combine via normal product.

            # Number of contractions = n_bjs_in_X (each b_j^s from X passes the a_1^sigma from Y)
            contractions = n_bjs_in_X * n_a1sigma_in_Y  # = n_bjs_in_X since n_a1sigma_in_Y=1

            # Build reduced monomials
            mx_reduced = list(mx)
            mx_reduced[b_idx] -= 1
            mx_red = tuple(mx_reduced)

            my_reduced = list(my)
            my_reduced[a1_idx] -= 1
            my_red = tuple(my_reduced)

            # Multiply the reduced monomials
            X_red = {mx_red: Fraction(cx * contractions)}
            Y_red = {my_red: Fraction(cy)}
            prod = alg.multiply(X_red, Y_red)

            # The deformed contribution is -1 times this product (negative from the relation)
            for m, c in prod.items():
                result[m] -= c

    return {k: v for k, v in result.items() if v != 0}


def build_schema2_json(n, gamma_terms):
    """Build Schema 2 JSON for C(n+1) with bosonic rank n."""
    # Load Schema 1 for base structure
    path1 = os.path.join(DATA_DIR, f'C_{n}_structure.json')
    with open(path1) as f:
        schema1 = json.load(f)

    # Build gb parameter list (4n parameters)
    gb_params = []
    for j in range(1, n+1):
        for sigma in ['a1p', 'a1m']:
            for s_label in ['p', 'm']:
                gb_params.append(f'gb_{sigma}_b{j}{s_label}')

    schema2 = dict(schema1)
    schema2['schema_version'] = '5.0'
    schema2['inhomogeneous_deformation'] = {
        'gb_matrix': {
            'description': f'4n={4*n} deformation parameters (parity 1)',
            'size': 4 * n,
            'parameters': gb_params,
            'parity': 1,
            'deformed_relation': '[b_j^s, a_1^sigma]_def = -gb_{sigma,j,s} * kappa',
        },
        'gamma_coefficients': gamma_terms,
    }
    schema2['metadata'] = {
        'generated_by': 'src/C_gamma.py',
        'generation_date': str(date.today()),
        'references': [
            'docs/math/C_inhomogeneous_definition.md',
            'docs/math/Cn1_definition.md',
        ],
    }
    return schema2


def main():
    for n in [1, 2, 3]:
        print(f'Computing gamma structure for C({n+1}) (n={n})...')
        gamma_terms = compute_gamma(n)
        print(f'  Found {len(gamma_terms)} non-zero gamma coefficients')

        schema2 = build_schema2_json(n, gamma_terms)
        fname = os.path.join(DATA_DIR, f'C_{n}_gamma.json')
        with open(fname, 'w') as f:
            json.dump(schema2, f, indent=2)
        print(f'  Written: {fname}')


if __name__ == '__main__':
    main()
