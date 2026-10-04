"""
C_coboundary.py
Computes the coboundary operator (delta f)(X,Y) for C(n+1) = osp(2|2n).

Coboundary formula (odd map f: g -> g):
  (delta f)(X,Y) = (-1)^{p(X)} [X, f(Y)] - (-1)^{(p(X)+1)*p(Y)} [Y, f(X)] - f([X,Y])

f is parametrized by phi_{source}_{target} where:
  - f(even generator) = sum over odd generators (phi params)
  - f(odd generator) = sum over even generators (phi params)

Output: Schema 4 JSON with symbolic coboundary coefficients in phi parameters.
"""

import json
import os
import sys
from fractions import Fraction
from collections import defaultdict
from datetime import datetime

sys.path.insert(0, os.path.dirname(__file__))
from C_generators import CnPlus1


def phi_label(src, tgt):
    return f'phi_{src}_{tgt}'


def build_f_map(alg):
    """
    Build the symbolic f map: f(g_i) = sum_j phi_{g_i_g_j} * g_j
    where g_j has opposite parity to g_i.

    Returns:
        phi_params: sorted list of all phi parameter names
        f_image: dict {basis_elem: {phi_label: Fraction(1)}} (each phi appears once)
        f_values: list of dicts for JSON output
    """
    phi_params = []
    f_image = {}  # basis_elem -> {phi_label: coeff}
    f_values = []

    for src in alg.basis:
        p_src = alg.parity_map[src]
        # target generators have opposite parity
        targets = [g for g in alg.basis if alg.parity_map[g] != p_src]
        f_image[src] = {}
        for tgt in targets:
            label = phi_label(src, tgt)
            phi_params.append(label)
            f_image[src][label] = Fraction(1)
            f_values.append({'input': src, 'output_basis': tgt, 'coeff': label})

    return sorted(set(phi_params)), f_image, f_values


def apply_f(f_image, elem, coeff, result):
    """
    Add coeff * f(elem) to result.
    result: defaultdict(lambda: defaultdict(Fraction))
           result[basis_gen][phi_label] += contribution
    """
    for phi_lbl, phi_coeff in f_image[elem].items():
        # phi_lbl is the phi parameter; the target gen is encoded in the phi label
        # We need to know which basis gen this phi_lbl maps to.
        # Recover: phi_label(src, tgt) -> tgt is the last part after src_
        # We store the target gen alongside; let's use a separate lookup.
        pass


def apply_f_direct(f_image, elem, coeff, basis_from_phi, result):
    """
    result[tgt_gen][phi_lbl] += coeff * phi_coeff
    """
    for phi_lbl, phi_coeff in f_image[elem].items():
        tgt = basis_from_phi[phi_lbl]
        result[tgt][phi_lbl] += coeff * phi_coeff


def build_basis_from_phi(alg):
    """Build lookup: phi_label -> target basis gen."""
    lookup = {}
    for src in alg.basis:
        p_src = alg.parity_map[src]
        targets = [g for g in alg.basis if alg.parity_map[g] != p_src]
        for tgt in targets:
            lookup[phi_label(src, tgt)] = tgt
    return lookup


def get_sc(sc_dict, alg, X, Y):
    """Get structure constants [X,Y] = sum_Z c_Z * Z from precomputed dict."""
    key = (X, Y)
    if key in sc_dict:
        return sc_dict[key]
    rev_key = (Y, X)
    if rev_key in sc_dict:
        sign = Fraction((-1) ** (alg.parity_map[X] * alg.parity_map[Y] + 1))
        return {Z: sign * c for Z, c in sc_dict[rev_key].items()}
    return {}


def compute_coboundary(n, output_dir='data'):
    from C_generators import CnPlus1, graded_bracket

    alg = CnPlus1(n)
    basis = alg.basis

    # Build SC dict from oscillator algebra (all ordered pairs X<=Y)
    sc_dict = {}
    for i in range(len(basis)):
        for j in range(i + 1, len(basis)):
            X, Y = basis[i], basis[j]
            p_X, p_Y = alg.parity_map[X], alg.parity_map[Y]
            osc_br = graded_bracket(alg.realizations[X], alg.realizations[Y], p_X, p_Y, alg.osc_idx)
            if osc_br:
                decomp = alg.decompose(osc_br)
                if decomp:
                    sc_dict[(X, Y)] = decomp

    phi_params, f_image, f_values = build_f_map(alg)
    basis_from_phi = build_basis_from_phi(alg)

    # Compute (delta f)(X, Y) for all X <= Y
    # (delta f)(X,Y) = (-1)^{p_X} [X, f(Y)] - (-1)^{(p_X+1)*p_Y} [Y, f(X)] - f([X,Y])
    delta_f_entries = []

    for i in range(len(basis)):
        for j in range(i, len(basis)):
            X, Y = basis[i], basis[j]
            p_X = alg.parity_map[X]
            p_Y = alg.parity_map[Y]

            # For each phi param: coefficient of each Z in (delta f)(X,Y)
            # result[Z][phi_label] = total coefficient
            result = defaultdict(lambda: defaultdict(Fraction))

            # Term 1: (-1)^{p_X} [X, f(Y)]
            sign1 = Fraction((-1) ** p_X)
            # f(Y) = sum_{tgt_Y, phi_l} phi_l * tgt_Y  (where phi_l = phi_label(Y, tgt_Y))
            for phi_l, phi_c in f_image[Y].items():
                tgt_Y = basis_from_phi[phi_l]
                p_tgt_Y = alg.parity_map[tgt_Y]
                # [X, tgt_Y] in terms of Z
                br = get_sc(sc_dict, alg, X, tgt_Y)
                for Z, c in br.items():
                    result[Z][phi_l] += sign1 * phi_c * c

            # Term 2: -(-1)^{(p_X+1)*p_Y} [Y, f(X)]
            sign2 = Fraction(-(-1) ** ((p_X + 1) * p_Y))
            for phi_l, phi_c in f_image[X].items():
                tgt_X = basis_from_phi[phi_l]
                br = get_sc(sc_dict, alg, Y, tgt_X)
                for Z, c in br.items():
                    result[Z][phi_l] += sign2 * phi_c * c

            # Term 3: -f([X,Y])
            # [X,Y] = sum_W c_W * W; f(W) = sum_{tgt_W, phi_l2} phi_l2 * tgt_W
            xy_br = get_sc(sc_dict, alg, X, Y)
            for W, c_W in xy_br.items():
                for phi_l, phi_c in f_image[W].items():
                    tgt_W = basis_from_phi[phi_l]
                    result[tgt_W][phi_l] += Fraction(-1) * c_W * phi_c

            # Collect non-zero entries
            for Z in basis:
                phi_dict = {phi_l: c for phi_l, c in result[Z].items() if c != 0}
                if phi_dict:
                    # Build coeff_expr string
                    terms = []
                    for phi_l in sorted(phi_dict.keys()):
                        c = phi_dict[phi_l]
                        if c == 1:
                            terms.append(phi_l)
                        elif c == -1:
                            terms.append(f'-{phi_l}')
                        elif c > 0:
                            terms.append(f'{c}*{phi_l}')
                        else:
                            terms.append(f'{c}*{phi_l}')
                    coeff_expr = ' + '.join(terms).replace(' + -', ' - ')
                    delta_f_entries.append({
                        'X': X,
                        'Y': Y,
                        'Z': Z,
                        'coeff_expr': coeff_expr,
                        'phi_coeffs': {phi_l: str(c) for phi_l, c in phi_dict.items()}
                    })

    algebra_info = {
        'family': 'C',
        'm': 1,
        'n': n,
        'name': f'C({n + 1}) = osp(2|{2 * n})',
        'layer': 4
    }

    out = {
        'schema_version': '5.0',
        'algebra': algebra_info,
        'f_map': {
            'description': 'Odd linear map f: g -> g, parameterized by phi_{src}_{tgt}',
            'phi_params': phi_params,
            'f_values': f_values
        },
        'delta_f_coefficients': delta_f_entries,
        'metadata': {
            'n_phi_params': len(phi_params),
            'n_delta_f_entries': len(delta_f_entries),
            'formula': '(delta f)(X,Y) = (-1)^{p(X)}[X,f(Y)] - (-1)^{(p(X)+1)p(Y)}[Y,f(X)] - f([X,Y])',
            'generated_at': datetime.now().isoformat()
        }
    }

    path = os.path.join(output_dir, f'C_{n}_coboundary.json')
    with open(path, 'w') as f_out:
        json.dump(out, f_out, indent=2)
    print(f"n={n}: {len(phi_params)} phi params, {len(delta_f_entries)} delta_f entries → {path}")
    return out


def generate_all(output_dir='data'):
    for n in range(1, 4):
        compute_coboundary(n, output_dir)


if __name__ == '__main__':
    generate_all()
