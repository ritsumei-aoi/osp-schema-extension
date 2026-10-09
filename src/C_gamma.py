"""
C_gamma.py: Compute Schema 2 (inhomogeneous deformation / gamma structure)
for C(n+1) = osp(2|2n).

The inhomogeneous deformation is defined by the exchange relations:
  [b_j^s, a_1^sigma] = -gb_{sigma,j,s} * kappa

The deformed bracket is: [X,Y]_gamma = [X,Y]_0 + kappa * gamma(X,Y)

gamma(X,Y) is computed by substituting the deformed oscillator relations
into the standard brackets.

For each pair (X, Y) of generators, gamma(X,Y) receives contributions when
the standard computation of [X,Y]_0 involves a commutator [b_j^s, a_1^sigma].
In the deformed theory: [b_j^s, a_1^sigma] = -gb_{sigma,j,s} * kappa.

So gamma_XY_Z is proportional to gb parameters when the path X*Y - Y*X
passes through a b-a commutator.

Concretely: for generators involving both a_1 and b factors:
  E_even = b_i^si * b_j^sj  (no a_1)
  E_odd  = a_1^sigma * b_k^s

The deformation affects:
  [E_even, E_odd]: in the undeformed theory, [b_i^si*b_j^sj, a_1^sigma*b_k^s]
    = a_1^sigma * [b_i^si*b_j^sj, b_k^s] (since [b,a]=0 in undeformed theory)
    In deformed: [b_j^sj, a_1^sigma] = -gb_{sigma,j,s_k=?} ... wait.

Actually the deformation modifies [b_j^s, a_1^sigma] but since the generators
are realized in the universal enveloping algebra, the deformation changes
the ALGEBRA, not just the generators.

Specifically, in the deformed algebra:
  [b_j^s, a_1^sigma]_gamma = -gb_{sigma,j,s} * kappa  (new relation)

This introduces kappa-corrections to brackets involving both a_1 and b.

For E_odd = a_1^sigma * b_k^s and E_even = b_i^si * b_j^sj:
  [E_even, E_odd]_gamma = [b_i^si*b_j^sj, a_1^sigma*b_k^s]_gamma
  = a_1^sigma * [b_i^si*b_j^sj, b_k^s] + [b_i^si*b_j^sj, a_1^sigma] * b_k^s
    + correction terms from b-a deformation

  The key deformation: in [b_i^si, a_1^sigma], the deformed relation gives
  [b_i^si, a_1^sigma] = gb_{sigma,i,si} * kappa (with appropriate sign convention).

  Actually from the definition: [b_j^s, a_1^sigma] = -gb_{sigma,j,s} * kappa.
  Note this is in the Lie superalgebra bracket (commutator for even-odd = regular commutator).

  So [E_even, E_odd]_gamma = [E_even, E_odd]_0 + kappa * gamma(E_even, E_odd)

  gamma(E_even, E_odd) comes from the terms where b_i^si or b_j^sj "crosses" a_1^sigma:
  In the computation of [b_i^si*b_j^sj, a_1^sigma*b_k^s]:
  = b_i^si*b_j^sj*a_1^sigma*b_k^s - a_1^sigma*b_k^s*b_i^si*b_j^sj
  = b_i^si*a_1^sigma*b_j^sj*b_k^s + b_i^si*[b_j^sj,a_1^sigma]*b_k^s
    - a_1^sigma*b_i^si*b_k^s*b_j^sj - [a_1^sigma*b_k^s, b_i^si]*b_j^sj

  This is getting complex. Let me use the linearized approach:

  gamma(X,Y) = lim_{gb->0} d/d(gb) [X,Y]_gamma

  Equivalently, gamma(X,Y) is the coefficient of kappa in [X,Y]_gamma.

  For generators X = b_i^si * b_j^sj (even) and Y = a_1^sigma * b_k^s (odd):
  [X, Y] = [b_i^si*b_j^sj, a_1^sigma*b_k^s]

  In the deformed theory: a_1^sigma "passes through" b's using [b, a_1] = gb*kappa:
  b_j^sj * a_1^sigma = a_1^sigma * b_j^sj + [b_j^sj, a_1^sigma] = a_1^sigma*b_j^sj - gb_{sigma,j,sj}*kappa

  So XY = b_i^si * b_j^sj * a_1^sigma * b_k^s
       = b_i^si * (a_1^sigma*b_j^sj - gb_{sigma,j,sj}*kappa) * b_k^s
       = b_i^si*a_1^sigma*b_j^sj*b_k^s - gb_{sigma,j,sj} * kappa * b_i^si * b_k^s
       = (a_1^sigma*b_i^si - gb_{sigma,i,si}*kappa)*b_j^sj*b_k^s - gb_{sigma,j,sj}*kappa*b_i^si*b_k^s
       = a_1^sigma*b_i^si*b_j^sj*b_k^s - gb_{sigma,i,si}*kappa*b_j^sj*b_k^s - gb_{sigma,j,sj}*kappa*b_i^si*b_k^s

  YX = a_1^sigma * b_k^s * b_i^si * b_j^sj (bosons commute freely)
     = a_1^sigma * b_i^si * b_j^sj * b_k^s  (bosons commute)

  [X,Y] = XY - YX = -gb_{sigma,i,si}*kappa*b_j^sj*b_k^s - gb_{sigma,j,sj}*kappa*b_i^si*b_k^s

  (The a_1^sigma terms cancel!)

  So gamma(E_even, E_odd) = -gb_{sigma,i,si}*(b_j^sj*b_k^s) - gb_{sigma,j,sj}*(b_i^si*b_k^s)

  Each b*b term maps to an even generator.

  For X = E_del{i}_del{j}_{si sj} = b_i^si * b_j^sj and Y = E_eps1_del{k}_{sigma s}:
  gamma(X, Y) = -gb_{sigma,i,si} * E(b_j^sj, b_k^s) - gb_{sigma,j,sj} * E(b_i^si, b_k^s)
  where E(b_a^r, b_b^t) is the even generator b_a^r * b_b^t.

  For Cartan generators H_l acting on odd generator Y = a_1^sigma * b_k^s:
  In the deformed theory: H_l * Y = [H_l, Y]_0 (since H_l is purely bosonic + N_a term;
  the deformation [b,a]=gb*kappa affects only mixed products.
  Wait, H_1 = a_1^+ a_1^- + b_1^+ b_1^-. The fermionic part N_a = a_1^+*a_1^- can
  "cross" with b in the deformed sense.

  Actually: H_1 = a_1^+*a_1^- + b_1^+*b_1^-. This IS an element involving a_1.

  [H_1, E_eps1_del{k}_{sigma s}] = [a_1^+*a_1^- + b_1^+*b_1^-, a_1^sigma*b_k^s]

  Deformed: [a_1^+*a_1^-, a_1^sigma*b_k^s]_gamma = ?
  a_1^+*a_1^- * a_1^sigma*b_k^s - a_1^sigma*b_k^s*a_1^+*a_1^-
  = a_1^+*(a_1^- * a_1^sigma)*b_k^s - a_1^sigma*b_k^s*a_1^+*a_1^-
  These are pure fermionic terms; the deformation [b,a] doesn't affect this part.

  [b_1^+*b_1^-, a_1^sigma*b_k^s]_gamma:
  Using the same calculation as above with (i=1,si='p') and (j=1,sj='m'):
  = -gb_{sigma,1,'p'}*b_1^-*b_k^s - gb_{sigma,1,'m'}*b_1^+*b_k^s
  Wait, H_1 has a_1 part AND b_1 part, and the b_1 part can deform with a_1.

  [b_1^+*b_1^-, a_1^sigma*b_k^s]:
  X = b_1^+*b_1^-, Y = a_1^sigma*b_k^s.
  From the formula: XY - YX:
  XY = b_1^+*b_1^-*a_1^sigma*b_k^s
  = b_1^+*(a_1^sigma*b_1^- - gb_{sigma,1,'m'}*kappa)*b_k^s
  = b_1^+*a_1^sigma*b_1^-*b_k^s - gb_{sigma,1,'m'}*kappa*b_1^+*b_k^s
  = (a_1^sigma*b_1^+ - gb_{sigma,1,'p'}*kappa)*b_1^-*b_k^s - gb_{sigma,1,'m'}*kappa*b_1^+*b_k^s
  = a_1^sigma*b_1^+*b_1^-*b_k^s - gb_{sigma,1,'p'}*kappa*b_1^-*b_k^s - gb_{sigma,1,'m'}*kappa*b_1^+*b_k^s

  YX = a_1^sigma*b_k^s*b_1^+*b_1^- = a_1^sigma*b_1^+*b_1^-*b_k^s (bosons commute)

  [b_1^+*b_1^-, a_1^sigma*b_k^s] = -gb_{sigma,1,'p'}*kappa*b_1^-*b_k^s - gb_{sigma,1,'m'}*kappa*b_1^+*b_k^s

  So for H_l with l >= 2 (no a_1 part): similar formula applies.
  For H_1 = N_a + N_b1: the N_a part gives the undeformed contribution (eigenvalue).
  The N_b1 part gives kappa corrections.

  So gamma(H_l, E_eps1_del{k}_{sigma,s}) = contribution from the bosonic part of H_l.

  For H_l = b_{l-1}^+*b_{l-1}^- - b_l^+*b_l^- (l=2..n):
  The bosonic part is b_{l-1}^+*b_{l-1}^- and -b_l^+*b_l^-.
  gamma = -gb_{sigma,l-1,'p'}*kappa*b_{l-1}^-*b_k^s - gb_{sigma,l-1,'m'}*kappa*b_{l-1}^+*b_k^s
          +gb_{sigma,l,'p'}*kappa*b_l^-*b_k^s + gb_{sigma,l,'m'}*kappa*b_l^+*b_k^s

  For H_{n+1} = -N_bn - 1/2:
  gamma = gb_{sigma,n,'p'}*kappa*b_n^-*b_k^s + gb_{sigma,n,'m'}*kappa*b_n^+*b_k^s

  For H_1 = N_a + N_b1:
  gamma from N_b1 part = -gb_{sigma,1,'p'}*kappa*b_1^-*b_k^s - gb_{sigma,1,'m'}*kappa*b_1^+*b_k^s
  N_a part: a_1^+*a_1^-. [a_1^+*a_1^-, a_1^sigma*b_k^s] is purely fermionic; no b-a crossing → gamma=0.

  So gamma(H_l, E_odd) comes from the bosonic N_b terms in H_l.

  For odd-odd brackets: {E_eps1_del{k}_{sigma1,s1}, E_eps1_del{l}_{sigma2,s2}}_gamma
  = a_1^sigma1*b_k^s1*a_1^sigma2*b_l^s2 + a_1^sigma2*b_l^s2*a_1^sigma1*b_k^s1

  Deformed: a_1^sigma2*b_k^s1 = b_k^s1*a_1^sigma2 - [b_k^s1, a_1^sigma2] = b_k^s1*a_1^sigma2 + gb_{sigma2,k,s1}*kappa
  Wait: [b_j^s, a_1^sigma] = -gb_{sigma,j,s}*kappa, so a_1^sigma*b_j^s = b_j^s*a_1^sigma + [a_1^sigma, b_j^s] = b_j^s*a_1^sigma - (-gb_{sigma,j,s}*kappa) = b_j^s*a_1^sigma + gb_{sigma,j,s}*kappa.

  So: a_1^sigma2 * b_k^s1 = b_k^s1 * a_1^sigma2 + gb_{sigma2,k,s1}*kappa.

  First term of anticommutator:
  a_1^sigma1*b_k^s1*a_1^sigma2*b_l^s2
  = a_1^sigma1*(b_k^s1*a_1^sigma2 + gb_{sigma2,k,s1}*kappa)*b_l^s2  (using bosonic b_k^s1 passing through a_1^sigma2... wait this is the REVERSE)

  Actually: a_1^sigma2 * b_k^s1 = b_k^s1 * a_1^sigma2 + gb_{sigma2,k,s1}*kappa.
  But in the product a_1^sigma1*b_k^s1*a_1^sigma2*b_l^s2, I need to move a_1^sigma2 past b_k^s1:
  This is NOT what's needed here. The product is already in order.

  Let me re-think. The anticommutator {X,Y} = XY + YX.
  XY = a_1^sigma1*b_k^s1*a_1^sigma2*b_l^s2
  YX = a_1^sigma2*b_l^s2*a_1^sigma1*b_k^s1

  In the deformed algebra, we need to normal-order these. The deformation says b_j^s and a_1^sigma don't commute freely.

  For XY = a_1^sigma1*(b_k^s1*a_1^sigma2)*b_l^s2:
  b_k^s1*a_1^sigma2 = a_1^sigma2*b_k^s1 - [a_1^sigma2, b_k^s1]_deformed
  [a_1^sigma2, b_k^s1]_deformed = -[b_k^s1, a_1^sigma2]_deformed = gb_{sigma2,k,s1}*kappa
  So b_k^s1*a_1^sigma2 = a_1^sigma2*b_k^s1 - gb_{sigma2,k,s1}*kappa.

  XY = a_1^sigma1*(a_1^sigma2*b_k^s1 - gb_{sigma2,k,s1}*kappa)*b_l^s2
     = a_1^sigma1*a_1^sigma2*b_k^s1*b_l^s2 - gb_{sigma2,k,s1}*kappa*a_1^sigma1*b_l^s2

  For YX = a_1^sigma2*(b_l^s2*a_1^sigma1)*b_k^s1:
  b_l^s2*a_1^sigma1 = a_1^sigma1*b_l^s2 - gb_{sigma1,l,s2}*kappa.
  YX = a_1^sigma2*(a_1^sigma1*b_l^s2 - gb_{sigma1,l,s2}*kappa)*b_k^s1
     = a_1^sigma2*a_1^sigma1*b_l^s2*b_k^s1 - gb_{sigma1,l,s2}*kappa*a_1^sigma2*b_k^s1

  {X,Y} = XY + YX
  = (a_1^sigma1*a_1^sigma2 + a_1^sigma2*a_1^sigma1)*b_k^s1*b_l^s2
    - gb_{sigma2,k,s1}*kappa*a_1^sigma1*b_l^s2
    - gb_{sigma1,l,s2}*kappa*a_1^sigma2*b_k^s1

  (Note: b_k^s1*b_l^s2 = b_l^s2*b_k^s1 bosons commute)

  The kappa terms: kappa * a_1^sigma*b = kappa * E_odd (since kappa commutes with everything).
  But wait, kappa is odd and central, so kappa * E_odd is proportional to kappa^2 * ... no.
  Actually kappa * (a_1^sigma * b_l^s2) is a product in U(A).
  In the Lie superalgebra, the bracket lands in the algebra, not in kappa*(algebra).
  But the deformation has bracket = [X,Y]_0 + kappa * gamma(X,Y).
  So gamma should be in the original algebra g (without kappa).

  Looking at the kappa terms: -gb_{sigma2,k,s1}*kappa*a_1^sigma1*b_l^s2 is proportional to kappa * E_eps1_del{l}_{sigma1,s2}.
  This IS of the form kappa * (element in g). So:

  gamma(E_eps1_del{k}_{sigma1,s1}, E_eps1_del{l}_{sigma2,s2}) from the deformation:
  = -gb_{sigma2,k,s1} * E_eps1_del{l}_{sigma1,s2} - gb_{sigma1,l,s2} * E_eps1_del{k}_{sigma2,s1}

  (where E_eps1_del{l}_{sigma1,s2} = a_1^sigma1 * b_l^s2)

Summary of gamma computations:
  1. [E_even, E_odd]: gamma(E_even, E_odd) from b-a crossings
  2. [H_l, E_odd]: gamma(H_l, E_odd) from N_b terms in H_l
  3. {E_odd, E_odd}: gamma(E_odd_X, E_odd_Y) from b-a crossings
  4. [E_even, E_even]: gamma = 0 (no a_1 involved)
  5. [H_l, E_even]: gamma = 0 (no a_1 crossing)
"""

import json
import itertools
from fractions import Fraction
from datetime import date
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))
from C_generators import build_basis, parity_of, N_bk_in_H, N_a_in_H, normalize_boson_pair, gen_to_boson_terms


def gb_label(sigma, j, s):
    """Label for gb parameter: gb_{sigma}_{j}_{s}."""
    return f"gb_{sigma}{j}{s}"


def boson_to_even_label(a_idx, a_sgn, b_idx, b_sgn, n):
    """
    Map b_{a_idx}^{a_sgn} * b_{b_idx}^{b_sgn} to an even generator label.
    Returns (label, coeff) or None.
    """
    if a_idx == b_idx and a_sgn == b_sgn:
        return f"E_2del{a_idx}_{a_sgn}", Fraction(2)
    if a_idx == b_idx and a_sgn != b_sgn:
        # Number operator - expressed in terms of H (Cartan)
        return ('N', a_idx), Fraction(1)
    if a_idx < b_idx:
        return f"E_del{a_idx}_del{b_idx}_{a_sgn}{b_sgn}", Fraction(1)
    else:
        return f"E_del{b_idx}_del{a_idx}_{b_sgn}{a_sgn}", Fraction(1)


def compute_gamma(n):
    """
    Compute symbolic gamma coefficients for the inhomogeneous deformation of C(n+1).

    Returns a list of {X, Y, Z, coeff_symbolic} where coeff_symbolic is a
    linear combination of gb parameters.
    """
    even, odd = build_basis(n)
    gamma_entries = []

    def add_gamma(X, Y, Z, gb_sym, coeff):
        """Add entry: gamma(X,Y) has Z-coefficient = coeff * gb_sym."""
        if coeff == 0:
            return
        gamma_entries.append({
            "X": X, "Y": Y, "Z": Z,
            "gb_param": gb_sym,
            "coeff": str(coeff)
        })

    non_cartan_even = [g for g in even if not g.startswith("H_")]
    cartan_gens = [g for g in even if g.startswith("H_")]

    def H_boson_terms(H_label):
        """Return bosonic terms of H_l as list of (coeff, (i,si,j,sj))."""
        l = int(H_label[2:])
        if l == 1:
            # H_1 = N_a + N_b1 = a1p*a1m + b1p*b1m
            # Only the b part contributes to gamma
            return [(Fraction(1), (1, 'p', 1, 'm'))]
        elif l <= n:
            # H_l = N_b{l-1} - N_bl
            return [(Fraction(1), (l-1, 'p', l-1, 'm')), (Fraction(-1), (l, 'p', l, 'm'))]
        else:
            # H_{n+1} = -N_bn - 1/2
            return [(Fraction(-1), (n, 'p', n, 'm'))]

    # Case 1: [E_even (non-Cartan), E_odd]
    # gamma(X, Y) = -gb_{sigma,i,si}*E(b_j^sj,b_k^s) - gb_{sigma,j,sj}*E(b_i^si,b_k^s)
    for X in non_cartan_even:
        X_terms = gen_to_boson_terms(X, n)
        for Y in odd:
            parts = Y.split("_")
            ky = int(parts[2][3:])
            sgns_y = parts[3]
            sigma, s = sgns_y[0], sgns_y[1]

            for (cx, (ix, sx, jx, sx2)) in X_terms:
                # Contribution from b_{ix}^{sx} crossing a_1^sigma:
                # gamma += -cx * gb_{sigma,ix,sx} * E(b_{jx}^{sx2}, b_{ky}^s)
                gb_sym = gb_label(sigma, ix, sx)
                lbl, c = boson_to_even_label(jx, sx2, ky, s, n)
                if isinstance(lbl, tuple) and lbl[0] == 'N':
                    # Cartan: N_bq expressed in H_l
                    q = lbl[1]
                    for H_l, coeff_H in N_bk_in_H(q, n).items():
                        if H_l == 'const':
                            continue
                        add_gamma(X, Y, H_l, gb_sym, -cx * c * coeff_H)
                else:
                    add_gamma(X, Y, lbl, gb_sym, -cx * c)

                # Contribution from b_{jx}^{sx2} crossing a_1^sigma:
                gb_sym2 = gb_label(sigma, jx, sx2)
                lbl2, c2 = boson_to_even_label(ix, sx, ky, s, n)
                if isinstance(lbl2, tuple) and lbl2[0] == 'N':
                    q = lbl2[1]
                    for H_l, coeff_H in N_bk_in_H(q, n).items():
                        if H_l == 'const':
                            continue
                        add_gamma(X, Y, H_l, gb_sym2, -cx * c2 * coeff_H)
                else:
                    add_gamma(X, Y, lbl2, gb_sym2, -cx * c2)

    # Case 2: [H_l, E_odd]
    for H in cartan_gens:
        H_terms = H_boson_terms(H)
        for Y in odd:
            parts = Y.split("_")
            ky = int(parts[2][3:])
            sgns_y = parts[3]
            sigma, s = sgns_y[0], sgns_y[1]

            for (cx, (ix, sx, jx, sx2)) in H_terms:
                # Same formula as Case 1:
                # gamma(H_l, Y) = -cx * gb_{sigma,ix,sx} * E(b_{jx}^{sx2}, b_{ky}^s)
                #                 -cx * gb_{sigma,jx,sx2} * E(b_{ix}^{sx}, b_{ky}^s)
                for (gb_idx, gb_sgn, other_idx, other_sgn) in [
                    (ix, sx, jx, sx2),
                    (jx, sx2, ix, sx)
                ]:
                    gb_sym = gb_label(sigma, gb_idx, gb_sgn)
                    lbl, c = boson_to_even_label(other_idx, other_sgn, ky, s, n)
                    if isinstance(lbl, tuple) and lbl[0] == 'N':
                        q = lbl[1]
                        for H_l, coeff_H in N_bk_in_H(q, n).items():
                            if H_l == 'const':
                                continue
                            add_gamma(H, Y, H_l, gb_sym, -cx * c * coeff_H)
                    else:
                        add_gamma(H, Y, lbl, gb_sym, -cx * c)

    # Case 3: {E_odd_X, E_odd_Y} - only for pairs where X <= Y in odd basis index
    for xi, X in enumerate(odd):
        px = X.split("_")
        kx = int(px[2][3:])
        sgns_x = px[3]
        sigma1, s1 = sgns_x[0], sgns_x[1]

        for yi, Y in enumerate(odd):
            if yi < xi:
                continue
            py = Y.split("_")
            ky = int(py[2][3:])
            sgns_y = py[3]
            sigma2, s2 = sgns_y[0], sgns_y[1]

            # gamma(X,Y) from deformation:
            # = -gb_{sigma2,kx,s1} * E_eps1_del{ky}_{sigma1,s2}
            #   -gb_{sigma1,ky,s2} * E_eps1_del{kx}_{sigma2,s1}

            # Term 1: -gb_{sigma2,kx,s1} * E_eps1_del{ky}_{sigma1,s2}
            gb_sym1 = gb_label(sigma2, kx, s1)
            Z1 = f"E_eps1_del{ky}_{sigma1}{s2}"
            add_gamma(X, Y, Z1, gb_sym1, Fraction(-1))

            # Term 2: -gb_{sigma1,ky,s2} * E_eps1_del{kx}_{sigma2,s1}
            gb_sym2 = gb_label(sigma1, ky, s2)
            Z2 = f"E_eps1_del{kx}_{sigma2}{s1}"
            add_gamma(X, Y, Z2, gb_sym2, Fraction(-1))

    return gamma_entries


def consolidate_gamma(gamma_entries):
    """Consolidate gamma entries: sum coefficients for same (X,Y,Z,gb_param)."""
    consolidated = {}
    for entry in gamma_entries:
        key = (entry["X"], entry["Y"], entry["Z"], entry["gb_param"])
        c = Fraction(entry["coeff"])
        consolidated[key] = consolidated.get(key, Fraction(0)) + c
    result = []
    for (X, Y, Z, gb), c in consolidated.items():
        if c != 0:
            result.append({"X": X, "Y": Y, "Z": Z, "gb_param": gb, "coeff": str(c)})
    return result


def build_schema2(n):
    even, odd = build_basis(n)
    gamma_raw = compute_gamma(n)
    gamma = consolidate_gamma(gamma_raw)

    # Build gb_matrix labels
    gb_labels = []
    for sigma in ['p', 'm']:
        for j in range(1, n + 1):
            for s in ['p', 'm']:
                gb_labels.append(gb_label(sigma, j, s))

    schema = {
        "schema_version": "5.0",
        "algebra": {
            "family": "C", "m": 1, "n": n,
            "cartan_type": f"C({n+1})",
            "alternative_notation": {"osp": f"osp(2|{2*n})"}
        },
        "gb_matrix": {
            "description": "4n deformation parameters gb_{sigma,j,s} (parity 1)",
            "count": 4 * n,
            "labels": gb_labels,
            "index_convention": "sigma in {p,m} for a_1^sigma, j in 1..n, s in {p,m} for b_j^s"
        },
        "inhomogeneous_deformation": {
            "description": "[X,Y]_gamma = [X,Y]_0 + kappa * gamma(X,Y)",
            "gamma_coefficients": gamma
        },
        "metadata": {
            "generated_by": "src/C_gamma.py",
            "generation_date": str(date.today()),
            "references": [
                "docs/math/C_inhomogeneous_definition.md",
                "Frappat et al. (2000)"
            ]
        }
    }
    return schema


def verify_consistency_with_schema1(n, schema2, schema1):
    """Check that gamma entries reference valid generators from Schema 1."""
    basis_set = set(schema1["basis"]["even"] + schema1["basis"]["odd"])
    errors = []
    for entry in schema2["inhomogeneous_deformation"]["gamma_coefficients"]:
        for key in ["X", "Y", "Z"]:
            if entry[key] not in basis_set:
                errors.append(f"Invalid generator {key}={entry[key]} in gamma entry")
    return errors


def main():
    import os
    os.makedirs("data", exist_ok=True)
    for n in [1, 2, 3]:
        schema2 = build_schema2(n)
        fname = f"data/C_{n}_gamma.json"
        with open(fname, "w") as f:
            json.dump(schema2, f, indent=2)

        # Load Schema 1 for consistency check
        with open(f"data/C_{n}_structure.json") as f:
            schema1 = json.load(f)
        errors = verify_consistency_with_schema1(n, schema2, schema1)

        gamma_count = len(schema2["inhomogeneous_deformation"]["gamma_coefficients"])
        gb_count = schema2["gb_matrix"]["count"]
        print(f"C_{n}: gb_params={gb_count}, gamma_entries={gamma_count}, "
              f"errors={len(errors)} -> {fname}")
        if errors:
            for e in errors[:5]:
                print(f"  ERROR: {e}")


if __name__ == "__main__":
    main()
