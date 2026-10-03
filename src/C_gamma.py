"""
C_gamma.py

Computes the inhomogeneous deformation (Schema 2) for C(n+1) = osp(2|2n).

The deformation is defined by the modified exchange relations:
  [b_j^s, a_1^sigma] = -gb_{sigma,j,s} * kappa

where sigma in {+,-}, j=1..n, s in {+,-}.

The deformation parameter labels are:
  gb_p_j_p  (sigma=+, index=j, s=+)
  gb_p_j_m  (sigma=+, index=j, s=-)
  gb_m_j_p  (sigma=-, index=j, s=+)
  gb_m_j_m  (sigma=-, index=j, s=-)

The gamma 2-cocycle γ(X,Y) is computed by substituting the deformed oscillator
relations into the generator brackets and collecting terms proportional to kappa.

[X,Y]_gamma = [X,Y]_0 + kappa * gamma(X,Y)

In the oscillator algebra with deformation:
When computing [G_X, G_Y} where G_X, G_Y are expressed as oscillator words,
any occurrence of a "b a" pair (not in normal order) that must be commuted
now produces a gb*kappa term instead of 0.

Convention: gamma_{XYZ} is the coefficient such that kappa*gamma(X,Y) has
Z-component gamma_{XYZ}:  gamma(X,Y) = sum_Z gamma_{XYZ} * Z

Since kappa is odd, gamma(X,Y) must have parity p(X)+p(Y)+1 (mod 2).
"""

import json
import os
from fractions import Fraction
from datetime import date

# Import from C_generators
import sys
sys.path.insert(0, os.path.dirname(__file__))
from C_generators import (
    get_basis, get_parity, gen_monomials, build_mono_to_gen,
    osc_parity, osc_order_list
)


def compute_gamma(n, all_basis, parity, mono_map):
    """
    Compute gamma coefficients gamma_{XYZ} for C(n+1).

    γ(X,Y) arises from the deformation [b_j^s, a_1^sigma] → -gb_{sigma,j,s} * kappa.

    When computing [G_X, G_Y} in the deformed algebra, wherever we would normally
    commute b_j^s past a_1^sigma (giving 0), we now get -gb_{sigma,j,s} * kappa.

    Algorithm:
    1. For each generator pair (X, Y), compute the commutator [G_X, G_Y} in the
       DEFORMED algebra.
    2. The terms linear in gb_* parameters that are proportional to kappa give
       gamma(X, Y) * kappa.
    3. These gamma terms must be expressible as linear combinations of basis generators
       times gb parameters.

    Returns dict: {(X,Y,Z): {gb_label: Fraction}}
    where gamma_{XYZ} = sum_{gb_label} coeff_{XYZ,gb} * gb_{gb_label}
    """
    # Oscillator ordering
    osc_order = osc_order_list(n)
    osc_idx = {o: i for i, o in enumerate(osc_order)}

    def gb_label(sigma, j, s):
        """Return label for deformation parameter gb_{sigma,j,s}."""
        ss = "p" if sigma == "a_1_p" else "m"
        st = "p" if s == "p" else "m"
        return f"gb_{ss}_{j}_{st}"

    def is_boson(osc):
        return osc.startswith("b_")

    def is_fermion(osc):
        return osc.startswith("a_1")

    def deformed_commute_pair(xi, xj):
        """
        When xi comes before xj in normal order but osc_idx[xi] > osc_idx[xj],
        compute the deformed commutation.

        Returns (standard_val, gb_dict) where:
        - standard_val: Fraction (the undeformed bracket value [xi,xj})
        - gb_dict: {gb_label: Fraction} (deformation contribution *kappa/kappa)

        The deformed exchange: xi*xj = [xi,xj}_deformed + (-1)^{pi*pj} xj*xi
        where [xi,xj}_deformed includes gb terms for b-a commutation.
        """
        pi = osc_parity(xi)
        pj = osc_parity(xj)

        # The only deformation: [b_j^s, a_1^sigma] = -gb_{sigma,j,s} * kappa
        # In our context this is the anti/commutator in the deformed algebra.
        # But kappa is a new element; the generator bracket gamma(X,Y) collects
        # the coefficient of kappa in the full bracket.

        # Standard (undeformed) bracket contribution
        # We need to compute: xi * xj → [xi, xj}_0 + (-1)^{pi*pj} xj*xi
        # But in deformed: if xi=b_j_s and xj=a_1_sigma (or vice versa):
        #   [b_j_s, a_1_sigma] = -gb_{sigma,j,s} * kappa  (deformation)
        # So the bracket gives a kappa contribution.

        gb_dict = {}
        standard_val = Fraction(0)

        # Undeformed bracket
        from C_generators import _osc_bracket
        standard_val = _osc_bracket(xi, xj)

        # Deformation: b-a or a-b pair
        if is_boson(xi) and is_fermion(xj):
            # [b_j^s, a_1^sigma}: deformed bracket adds -gb_{sigma,j,s} * kappa
            # From definition: [b_j^s, a_1^sigma] = -gb_{sigma,j,s} * kappa
            bparts = xi.split("_")
            j = int(bparts[1])
            s = bparts[2]
            sigma = xj  # "a_1_p" or "a_1_m"
            lbl = gb_label(sigma, j, s)
            gb_dict[lbl] = gb_dict.get(lbl, Fraction(0)) - Fraction(1)
        elif is_fermion(xi) and is_boson(xj):
            # [a_1^sigma, b_j^s}: use antisymmetry of graded commutator
            # [a_1^sigma, b_j^s} = -(-1)^{p(a)*p(b)} [b_j^s, a_1^sigma}
            # p(a)=1, p(b)=0 → (-1)^0 = 1
            # = -[b_j^s, a_1^sigma} = -(-gb_{sigma,j,s} * kappa) = gb_{sigma,j,s} * kappa
            bparts = xj.split("_")
            j = int(bparts[1])
            s = bparts[2]
            sigma = xi
            lbl = gb_label(sigma, j, s)
            gb_dict[lbl] = gb_dict.get(lbl, Fraction(0)) + Fraction(1)

        return standard_val, gb_dict

    # We compute [X, Y}_deformed by tracking:
    # - The "regular" scalar part (same as undeformed)
    # - The "kappa" part (new, from deformation)
    # Then project the kappa part onto basis generators.

    def normal_order_deformed(word):
        """
        Normal-order a word in the deformed algebra.
        Returns (list of (Fraction, tuple) [undeformed part],
                 list of (Fraction_or_dict, tuple) [kappa part])

        kappa part: list of ({gb_label: Fraction}, tuple of remaining oscs)
        """
        # We track:
        # undeformed: list of (Fraction, list_of_oscs)
        # kappa_part: list of ({gb_label: Fraction}, list_of_oscs)

        undeformed = [(Fraction(1), list(word))]
        kappa_part = []  # list of ({gb_label: Fraction}, list_of_oscs)

        changed = True
        while changed:
            changed = False
            new_undeformed = []
            new_kappa = []

            # Process undeformed terms
            for (c, w) in undeformed:
                swapped = False
                for i in range(len(w) - 1):
                    xi, xj = w[i], w[i + 1]
                    if osc_idx[xi] > osc_idx[xj]:
                        pi = osc_parity(xi)
                        pj = osc_parity(xj)
                        sign = Fraction((-1) ** (pi * pj))

                        std_val, gb_dict = deformed_commute_pair(xi, xj)

                        # Swapped term
                        new_w = w[:i] + [xj, xi] + w[i + 2:]
                        new_undeformed.append((c * sign, new_w))

                        # Scalar (undeformed) contribution
                        if std_val != 0:
                            scalar_w = w[:i] + w[i + 2:]
                            new_undeformed.append((c * std_val, scalar_w))

                        # Kappa contribution
                        if gb_dict:
                            kappa_w = w[:i] + w[i + 2:]
                            scaled_gb = {k: c * v for k, v in gb_dict.items()}
                            new_kappa.append((scaled_gb, kappa_w))

                        changed = True
                        swapped = True
                        break
                if not swapped:
                    new_undeformed.append((c, w))

            # Process kappa terms (only undeformed normal-ordering, no more kappa)
            for (gb_d, w) in kappa_part:
                swapped = False
                for i in range(len(w) - 1):
                    xi, xj = w[i], w[i + 1]
                    if osc_idx[xi] > osc_idx[xj]:
                        pi = osc_parity(xi)
                        pj = osc_parity(xj)
                        sign = Fraction((-1) ** (pi * pj))
                        # Only undeformed bracket for kappa part (kappa^2=0)
                        from C_generators import _osc_bracket
                        std_val = _osc_bracket(xi, xj)

                        new_w = w[:i] + [xj, xi] + w[i + 2:]
                        new_kappa.append(({k: v * sign for k, v in gb_d.items()}, new_w))

                        if std_val != 0:
                            scalar_w = w[:i] + w[i + 2:]
                            new_kappa.append(
                                ({k: v * std_val for k, v in gb_d.items()}, scalar_w)
                            )

                        changed = True
                        swapped = True
                        break
                if not swapped:
                    new_kappa.append((gb_d, w))

            undeformed = new_undeformed
            kappa_part = new_kappa

        # Collect undeformed terms
        uf_combined = {}
        for (c, w) in undeformed:
            key = tuple(w)
            uf_combined[key] = uf_combined.get(key, Fraction(0)) + c
        uf = [(v, k) for k, v in uf_combined.items() if v != 0]

        # Collect kappa terms
        kp_combined = {}
        for (gb_d, w) in kappa_part:
            key = tuple(w)
            if key not in kp_combined:
                kp_combined[key] = {}
            for lbl, val in gb_d.items():
                kp_combined[key][lbl] = kp_combined[key].get(lbl, Fraction(0)) + val
        kp = [(v, k) for k, v in kp_combined.items() if any(c != 0 for c in v.values())]

        return uf, kp

    def graded_commutator_deformed(m1, m2):
        """
        Compute [m1, m2} in the deformed algebra.
        Returns (undeformed_part, kappa_part) where both are lists of (coeff/gb_dict, tuple).
        """
        pm1 = sum(osc_parity(o) for o in m1) % 2
        pm2 = sum(osc_parity(o) for o in m2) % 2
        sign = Fraction((-1) ** (pm1 * pm2))

        uf1, kp1 = normal_order_deformed(list(m1) + list(m2))
        uf2, kp2 = normal_order_deformed(list(m2) + list(m1))

        # [m1,m2} = (m1 m2) - sign * (m2 m1)
        uf_combined = {}
        for (c, w) in uf1:
            uf_combined[w] = uf_combined.get(w, Fraction(0)) + c
        for (c, w) in uf2:
            uf_combined[w] = uf_combined.get(w, Fraction(0)) - sign * c
        uf = [(v, k) for k, v in uf_combined.items() if v != 0]

        kp_combined = {}
        for (gb_d, w) in kp1:
            if w not in kp_combined:
                kp_combined[w] = {}
            for lbl, val in gb_d.items():
                kp_combined[w][lbl] = kp_combined[w].get(lbl, Fraction(0)) + val
        for (gb_d, w) in kp2:
            if w not in kp_combined:
                kp_combined[w] = {}
            for lbl, val in gb_d.items():
                kp_combined[w][lbl] = kp_combined[w].get(lbl, Fraction(0)) - sign * val
        kp = [(v, k) for k, v in kp_combined.items()
              if any(c != 0 for c in v.values())]

        return uf, kp

    # Compute gamma_{XYZ} for all (X,Y) pairs
    # gamma(X,Y) = sum_Z gamma_{XYZ} * Z (as element of g)
    # where the kappa part of [X,Y}_deformed = kappa * gamma(X,Y)

    gamma = {}  # (X,Y,Z) -> {gb_label: Fraction}

    for X in all_basis:
        X_monos = gen_monomials(X, n)
        for Y in all_basis:
            Y_monos = gen_monomials(Y, n)

            # Total kappa part of [X,Y}
            total_kp = {}
            for (cx, mx) in X_monos:
                for (cy, my) in Y_monos:
                    _, kp = graded_commutator_deformed(mx, my)
                    for (gb_d, mono) in kp:
                        if mono not in total_kp:
                            total_kp[mono] = {}
                        for lbl, val in gb_d.items():
                            total_kp[mono][lbl] = (
                                total_kp[mono].get(lbl, Fraction(0)) + cx * cy * val
                            )

            if not total_kp:
                continue

            # Express kappa part in terms of generators
            for (mono, gb_d) in total_kp.items():
                if mono in mono_map:
                    for gl, gc in mono_map[mono].items():
                        if gl == "__K__":
                            continue  # scalar, should be zero for valid gamma
                        for lbl, val in gb_d.items():
                            contribution = gc * val
                            if contribution != 0:
                                key = (X, Y, gl)
                                if key not in gamma:
                                    gamma[key] = {}
                                gamma[key][lbl] = (
                                    gamma[key].get(lbl, Fraction(0)) + contribution
                                )

    # Clean up zeros
    gamma = {k: {lbl: v for lbl, v in v_dict.items() if v != 0}
             for k, v_dict in gamma.items()}
    gamma = {k: v for k, v in gamma.items() if v}

    return gamma


def build_gamma_schema(n):
    """Build Schema 2 JSON for C(n+1)."""
    even_basis, odd_basis = get_basis(n)
    all_basis = even_basis + odd_basis
    parity = get_parity(n)
    mono_map = build_mono_to_gen(n, all_basis)

    gamma = compute_gamma(n, all_basis, parity, mono_map)

    # Format gamma coefficients
    gamma_list = []
    for (X, Y, Z), gb_dict in sorted(gamma.items()):
        entry = {
            "X": X,
            "Y": Y,
            "Z": Z,
            "gamma_coeff": {lbl: str(c) for lbl, c in sorted(gb_dict.items())},
        }
        gamma_list.append(entry)

    # Build gb_matrix
    gb_labels = []
    for sigma in ["p", "m"]:
        for j in range(1, n + 1):
            for s in ["p", "m"]:
                gb_labels.append(f"gb_{sigma}_{j}_{s}")

    schema = {
        "schema_version": "5.0",
        "algebra": f"C({n+1})",
        "n": n,
        "layer": 2,
        "description": "Inhomogeneous deformation (gamma structure) for C(n+1) = osp(2|2n)",
        "deformation_definition": {
            "modified_relation": "[b_j^s, a_1^sigma] = -gb_{sigma,j,s} * kappa",
            "parity_of_kappa": 1,
            "parity_of_gb_params": 1,
            "num_gb_params": 4 * n,
        },
        "gb_matrix": {
            "size": f"2 x 2n = 2 x {2*n} = {4*n}",
            "labels": gb_labels,
            "parity": 1,
            "description": (
                "gb_{sigma}_{j}_{s}: sigma in {p,m}, j=1..n, s in {p,m}. "
                "Parity 1 (odd parameters)."
            ),
        },
        "inhomogeneous_deformation": {
            "bracket_formula": "[X,Y]_gamma = [X,Y]_0 + kappa * gamma(X,Y)",
            "gamma_coefficients": gamma_list,
        },
        "consistency_check": {
            "schema_1_reference": f"C_{n}_structure.json",
            "note": (
                "gamma(X,Y) has Z-component with parity p(X)+p(Y)+1 mod 2, "
                "consistent with kappa being odd."
            ),
        },
        "metadata": {
            "generated_by": "C_gamma.py",
            "generation_date": str(date.today()),
            "references": [
                "docs/math/C_inhomogeneous_definition.md",
                "Frappat et al. (2000)",
            ],
        },
    }
    return schema, gamma


def verify_consistency(n, gamma, all_basis, parity):
    """
    Verify that gamma(X,Y) has the correct parity:
    parity(gamma(X,Y)) = p(X) + p(Y) + 1  (mod 2)
    since kappa is odd (p=1) and [X,Y]_gamma has parity p(X)+p(Y).
    """
    errors = []
    for (X, Y, Z), gb_dict in gamma.items():
        expected_parity = (parity[X] + parity[Y] + 1) % 2
        actual_parity = parity[Z]
        if actual_parity != expected_parity:
            errors.append(
                f"Parity error: gamma({X},{Y})[{Z}]: "
                f"expected parity {expected_parity}, got {actual_parity}"
            )
    return errors


def main():
    os.makedirs("data", exist_ok=True)
    for n in [1, 2, 3]:
        print(f"Building C_{n}_gamma.json (C({n+1}) = osp(2|{2*n}))...")
        even_basis, odd_basis = get_basis(n)
        all_basis = even_basis + odd_basis
        parity = get_parity(n)

        schema, gamma = build_gamma_schema(n)

        # Consistency check
        errors = verify_consistency(n, gamma, all_basis, parity)
        if errors:
            print(f"  CONSISTENCY ERRORS for n={n}:")
            for e in errors:
                print(f"    {e}")
        else:
            print(f"  Parity consistency: OK")

        outfile = f"data/C_{n}_gamma.json"
        with open(outfile, "w") as f:
            json.dump(schema, f, indent=2)
        print(f"  Non-zero gamma entries: {len(schema['inhomogeneous_deformation']['gamma_coefficients'])}")
        print(f"  Written to {outfile}")


if __name__ == "__main__":
    main()
