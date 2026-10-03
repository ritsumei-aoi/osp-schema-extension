#!/usr/bin/env python3
"""
C_coboundary.py: Compute the coboundary structure (Schema 4) for C(n+1).

The coboundary operator delta_f for an odd linear map f: g -> g is:
  (delta_f)(X, Y) = (-1)^{p(X)} [X, f(Y)] - (-1)^{(p(X)+1)p(Y)} [Y, f(X)] - f([X,Y])

The map f reverses parity:
  f(Z_j) = sum_i phi_{ij} * Z_i   where p(Z_i) != p(Z_j)

phi_{ij} parametrizes f: Z_j (source) -> Z_i (target).
phi_label: 'phi_{src}_{tgt}' (coefficient of Z_tgt in f(Z_src) is phi_{src}_{tgt}).

Output: for each pair (X, Y) and target generator Z, the coefficient of each
phi parameter in (delta_f)(X, Y)_Z.
"""

import json
import os
import sys
from fractions import Fraction
from collections import defaultdict
from datetime import date

sys.path.insert(0, os.path.join(os.path.dirname(__file__)))
from C_generators import CnPlusOne


def phi_label(src, tgt):
    """Label for phi parameter: coefficient of Z_tgt in f(Z_src)."""
    return f'phi_{src}_{tgt}'


def compute_coboundary(alg):
    """
    Compute (delta_f)(X, Y) symbolically in terms of phi parameters.

    (delta_f)(X, Y)_Z = sum over phi_{A} parameters of phi_{A} * C(A, X, Y, Z)

    Returns:
      entries: list of dicts {X, Y, Z, phi_coefficients: {phi_label: str}}

    Implementation:
      For each pair (gx, gy) and for each possible f-parameter phi_{gsrc_gtgt}
      where p(gsrc) != p(gtgt), compute the contribution to (delta_f)(gx, gy).

      Contribution of phi_{gsrc_gtgt}:
        - Term 1: (-1)^{p(gx)} * [gx, gtgt] when gsrc = gy
        - Term 2: -(-1)^{(p(gx)+1)*p(gy)} * [gy, gtgt] when gsrc = gx
        - Term 3: -gtgt when gsrc = [gx, gy] component

    This is computed by iterating over the phi parameters.
    """
    gens = alg.generators
    parity = alg.gen_parity

    # Precompute all brackets
    br_cache = {}
    for gx in gens:
        for gy in gens:
            br = alg.element_to_gens(alg.bracket(gx, gy))
            br_cache[(gx, gy)] = br

    # For each pair (gx, gy), accumulate {Z: {phi_label: coeff}}
    result = {}

    for gx in gens:
        for gy in gens:
            px = parity[gx]
            py = parity[gy]

            # (delta_f)(X, Y) has parity p(X) + p(Y) + 1 (mod 2)
            # because f is odd (reverses parity) and delta_f is odd too
            target_parity = (px + py + 1) % 2

            acc = defaultdict(lambda: defaultdict(Fraction))
            # {Z: {phi_label: Fraction}}

            # -- Term 1: (-1)^{p(X)} * [X, f(Y)] --
            # f(Y) = sum_{gtgt: p(gtgt) != p(gy)} phi_{gy_gtgt} * Z_gtgt
            sign1 = Fraction((-1) ** px)
            for gtgt in gens:
                if parity[gtgt] == parity[gy]:
                    continue  # f reverses parity: only include opposite parity
                phi = phi_label(gy, gtgt)
                # [gx, gtgt] -> {Z: coeff}
                br = br_cache[(gx, gtgt)]
                for gz, c in br.items():
                    if parity[gz] == target_parity:
                        acc[gz][phi] += sign1 * c

            # -- Term 2: -(-1)^{(p(X)+1)*p(Y)} * [Y, f(X)] --
            sign2 = Fraction(-(-1) ** ((px + 1) * py))
            for gtgt in gens:
                if parity[gtgt] == parity[gx]:
                    continue
                phi = phi_label(gx, gtgt)
                br = br_cache[(gy, gtgt)]
                for gz, c in br.items():
                    if parity[gz] == target_parity:
                        acc[gz][phi] += sign2 * c

            # -- Term 3: -f([X, Y]) --
            # [X, Y] = sum_gk c_k * Z_k
            # f([X,Y]) = sum_gk c_k * f(Z_k) = sum_gk c_k * sum_gtgt phi_{gk_gtgt} * Z_gtgt
            br_xy = br_cache[(gx, gy)]
            for gk, ck in br_xy.items():
                for gtgt in gens:
                    if parity[gtgt] == parity[gk]:
                        continue
                    phi = phi_label(gk, gtgt)
                    if parity[gtgt] == target_parity:
                        acc[gtgt][phi] -= ck

            # Store non-zero entries
            for gz, phi_dict in acc.items():
                clean = {phi: v for phi, v in phi_dict.items() if v}
                if clean:
                    key = (gx, gy, gz)
                    result[key] = clean

    return result


def build_schema4(n, output_dir='data'):
    alg = CnPlusOne(n)
    gens = alg.generators
    parity = alg.gen_parity

    # Build phi parameter list
    phi_labels = []
    for gsrc in gens:
        for gtgt in gens:
            if parity[gtgt] != parity[gsrc]:
                phi_labels.append(phi_label(gsrc, gtgt))

    # Compute coboundary
    coboundary_map = compute_coboundary(alg)

    entries = []
    for (gx, gy, gz), phi_dict in sorted(coboundary_map.items()):
        entries.append({
            'X': gx,
            'Y': gy,
            'Z': gz,
            'phi_coefficients': {phi: str(v) for phi, v in phi_dict.items()},
        })

    doc = {
        'schema_version': '5.0',
        'algebra': {
            'family': 'C',
            'm': 1,
            'n': n,
            'cartan_type': f'C({n+1})',
            'osp': f'osp(2|{2*n})',
        },
        'f_map_parameters': {
            'count': len(phi_labels),
            'labels': phi_labels,
            'description': (
                'phi_{src}_{tgt}: coefficient of Z_tgt in f(Z_src). '
                'f is odd: p(Z_tgt) != p(Z_src). '
                'Total = dim_even * dim_odd + dim_odd * dim_even = 2 * dim_even * dim_odd.'
            ),
        },
        'coboundary': entries,
        'metadata': {
            'generated_by': 'src/C_coboundary.py',
            'generation_date': str(date.today()),
            'formula': (
                '(delta_f)(X,Y) = (-1)^{p(X)} [X,f(Y)] '
                '- (-1)^{(p(X)+1)p(Y)} [Y,f(X)] - f([X,Y])'
            ),
        },
    }
    return doc


def generate_and_save(n, output_dir='data'):
    os.makedirs(output_dir, exist_ok=True)
    doc = build_schema4(n, output_dir=output_dir)
    out_path = os.path.join(output_dir, f'C_{n}_coboundary.json')
    with open(out_path, 'w') as f:
        json.dump(doc, f, indent=2)
    n_phi = doc['f_map_parameters']['count']
    n_entries = len(doc['coboundary'])
    print(f"C({n+1}) = osp(2|{2*n}): {n_phi} phi params, "
          f"{n_entries} coboundary entries → {out_path}")
    return doc


if __name__ == '__main__':
    for n in [1, 2, 3]:
        generate_and_save(n)
