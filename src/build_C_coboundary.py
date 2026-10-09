#!/usr/bin/env python3
"""
build_C_coboundary.py
Construct Schema 4 (Coboundary Structure) for C(n+1) = osp(2|2n).

Odd linear map f (index-paired, φ=1, human-approved):
  Even → Odd:
    f(E_2del{j}_s) = E_eps1_del{j}_ps + E_eps1_del{j}_ms   (both σ variants)
    f(H_k)         = 0
    f(E_del{j}del{k}_{..}) = 0

  Odd → Even:
    f(E_eps1_del{j}_{σ}_{s}) = E_2del{j}_s   (same j and s, all σ collapse)

Coboundary formula (from docs/math/C_coboundary_definition.md):
  (δf)(X,Y) = (-1)^{p(X)} [X, f(Y)]
             - (-1)^{(p(X)+1)p(Y)} [Y, f(X)]
             - f([X,Y])
"""
from __future__ import annotations
import json
import os
import sys
from collections import defaultdict
from datetime import date
from fractions import Fraction

SCHEMA_VERSION = "5.0"
F_DESCRIPTION = (
    "Index-paired map, φ=1: "
    "f(E_eps1_del{j}_{σ}_{s}) = E_2del{j}_{s}; "
    "f(E_2del{j}_{s}) = E_eps1_del{j}_p_{s} + E_eps1_del{j}_m_{s}; "
    "f(H_k) = f(E_del{j}del{k}_...) = 0"
)


# ── helpers ──────────────────────────────────────────────────────────────────

def load_json(path: str) -> dict:
    with open(path) as f:
        return json.load(f)


def parse_frac(s: str) -> Fraction:
    if '/' in s:
        num, den = s.split('/')
        return Fraction(int(num), int(den))
    return Fraction(int(s))


def frac_str(f: Fraction) -> str:
    if f.denominator == 1:
        return str(f.numerator)
    return f'{f.numerator}/{f.denominator}'


# ── generator classification ─────────────────────────────────────────────────

def _odd_j_sigma_s(name: str) -> tuple[int, str, str] | None:
    """If name is E_eps1_del{j}_{σ}{s}, return (j, σ, s); else None."""
    if not name.startswith('E_eps1_'):
        return None
    parts = name.split('_')   # ['E', 'eps1', 'del{j}', '{σ}{s}']
    if len(parts) != 4:
        return None
    try:
        j = int(parts[2][3:])  # after 'del'
        σ = parts[3][0]
        s = parts[3][1]
        return (j, σ, s)
    except (ValueError, IndexError):
        return None


def _even_boson_j_s(name: str) -> tuple[int, str] | None:
    """If name is E_2del{j}_{s}, return (j, s); else None."""
    if not name.startswith('E_2del'):
        return None
    parts = name.split('_')   # ['E', '2del{j}', '{s}']
    if len(parts) != 3:
        return None
    try:
        j = int(parts[1][4:])  # after '2del'
        s = parts[2]
        return (j, s)
    except (ValueError, IndexError):
        return None


def odd_label(j: int, σ: str, s: str) -> str:
    return f'E_eps1_del{j}_{σ}{s}'


def boson_label(j: int, s: str) -> str:
    return f'E_2del{j}_{s}'


# ── build f map ──────────────────────────────────────────────────────────────

def build_f_map(basis_even: list[str], basis_odd: list[str]) -> dict[str, dict[str, Fraction]]:
    """
    Build the map f as {gen_name: {image_gen: coeff}}.
    Generators not in the dict (or empty dict) map to 0.
    """
    f: dict[str, dict[str, Fraction]] = {}

    for name in basis_odd:
        info = _odd_j_sigma_s(name)
        if info is None:
            f[name] = {}
            continue
        j, σ, s = info
        image = boson_label(j, s)
        if image in basis_even:
            f[name] = {image: Fraction(1)}
        else:
            f[name] = {}

    for name in basis_even:
        info = _even_boson_j_s(name)
        if info is None:
            f[name] = {}  # H_k and mixed roots → 0
            continue
        j, s = info
        img: dict[str, Fraction] = {}
        for σ in ('p', 'm'):
            lbl = odd_label(j, σ, s)
            if lbl in basis_odd:
                img[lbl] = Fraction(1)
        f[name] = img

    return f


# ── bracket lookup ───────────────────────────────────────────────────────────

def build_bracket_fn(schema1: dict):
    """Returns bracket_fn(X, Y) -> {Z: Fraction}."""
    raw: dict = defaultdict(lambda: defaultdict(lambda: defaultdict(Fraction)))
    for e in schema1['structure_constants']:
        raw[e['X']][e['Y']][e['Z']] += parse_frac(e['coeff'])
    sc = {X: {Y: {Z: c for Z, c in Zd.items() if c}
              for Y, Zd in Yd.items()}
          for X, Yd in raw.items()}

    def bracket_fn(X: str, Y: str) -> dict[str, Fraction]:
        return dict(sc.get(X, {}).get(Y, {}))

    return bracket_fn


# ── apply f to a polynomial ──────────────────────────────────────────────────

def apply_f(poly: dict[str, Fraction],
            f_map: dict[str, dict[str, Fraction]]) -> dict[str, Fraction]:
    """f(Σ_k c_k Z_k) = Σ_k c_k f(Z_k)."""
    result: dict[str, Fraction] = {}
    for Z, c in poly.items():
        for W, fc in f_map.get(Z, {}).items():
            v = result.get(W, Fraction(0)) + c * fc
            if v:
                result[W] = v
            else:
                result.pop(W, None)
    return result


# ── coboundary computation ───────────────────────────────────────────────────

def coboundary(X: str, Y: str, pX: int, pY: int,
               bracket_fn, f_map: dict) -> dict[str, Fraction]:
    """
    (δf)(X,Y) = (-1)^{pX} [X, f(Y)]
               - (-1)^{(pX+1)pY} [Y, f(X)]
               - f([X,Y])
    """
    fY = f_map.get(Y, {})
    fX = f_map.get(X, {})
    XY = bracket_fn(X, Y)

    sign_XfY = Fraction((-1) ** pX)
    sign_YfX = Fraction((-1) ** ((pX + 1) * pY))

    result: dict[str, Fraction] = {}

    def add(poly: dict[str, Fraction], scale: Fraction) -> None:
        for Z, c in poly.items():
            v = result.get(Z, Fraction(0)) + scale * c
            if v:
                result[Z] = v
            else:
                result.pop(Z, None)

    # term 1: (-1)^{pX} [X, f(Y)]
    for W, cW in fY.items():
        add(bracket_fn(X, W), sign_XfY * cW)

    # term 2: -(-1)^{(pX+1)pY} [Y, f(X)]
    for W, cW in fX.items():
        add(bracket_fn(Y, W), -sign_YfX * cW)

    # term 3: -f([X,Y])
    add(apply_f(XY, f_map), Fraction(-1))

    return result


# ── build Schema 4 for one n ─────────────────────────────────────────────────

def build_coboundary_n(n: int, data_dir: str) -> dict:
    schema1 = load_json(os.path.join(data_dir, f'C_{n}_structure.json'))

    parity_raw = {k: int(v) for k, v in schema1['parity'].items()}
    basis_even: list[str] = schema1['basis']['even']
    basis_odd:  list[str] = schema1['basis']['odd']
    basis_all = basis_even + basis_odd

    f_map = build_f_map(basis_even, basis_odd)
    bracket_fn = build_bracket_fn(schema1)

    entries = []
    for X in basis_all:
        pX = parity_raw[X]
        for Y in basis_all:
            pY = parity_raw[Y]
            cb = coboundary(X, Y, pX, pY, bracket_fn, f_map)
            for Z, coeff in cb.items():
                if coeff:
                    entries.append({
                        'X': X, 'Y': Y, 'Z': Z,
                        'coeff': frac_str(coeff),
                        'sign_rule': 'graded',
                    })

    _check_consistency(entries, parity_raw, bracket_fn, f_map, basis_all, basis_even)

    f_spec = {
        gen: {img: frac_str(c) for img, c in img_map.items()}
        for gen, img_map in f_map.items()
        if img_map
    }

    return {
        'schema_version': SCHEMA_VERSION,
        'schema_layer': 4,
        'algebra': schema1['algebra'],
        'basis': schema1['basis'],
        'parity': schema1['parity'],
        'f_map': {
            'phi': '1',
            'description': F_DESCRIPTION,
            'nonzero': f_spec,
        },
        'coboundary': entries,
        'metadata': {
            'description': (
                'Schema 4: coboundary (δf)(X,Y) for C(n+1) = osp(2|2n). '
                '(δf)(X,Y) = (-1)^{p(X)}[X,f(Y)] '
                '- (-1)^{(p(X)+1)p(Y)}[Y,f(X)] - f([X,Y]). '
                'f is the index-paired odd linear map with φ=1.'
            ),
            'generated_by': 'build_C_coboundary.py',
            'generation_date': str(date.today()),
            'references': ['Frappat, Sciarrino, Sorba (2000)'],
        },
    }


# ── consistency checks ────────────────────────────────────────────────────────

def _check_consistency(entries, parity, bracket_fn, f_map, basis_all, basis_even):
    # 1. Parity of coboundary entries: (δf)(X,Y) has parity p(X)+p(Y)+1 mod 2
    #    (since f reverses parity and δ raises degree by 1 in the cochain complex)
    for e in entries:
        X, Y, Z = e['X'], e['Y'], e['Z']
        pX, pY, pZ = parity[X], parity[Y], parity[Z]
        expected = (pX + pY + 1) % 2
        assert pZ == expected, (
            f'Parity mismatch in (δf)({X},{Y}): Z={Z} has p={pZ}, '
            f'expected {expected}')

    # 2. f maps even → odd and odd → even
    for gen, img in f_map.items():
        pGen = parity[gen]
        for img_gen in img:
            pImg = parity.get(img_gen)
            assert pImg is not None, f'Unknown image generator {img_gen}'
            assert (pGen + pImg) % 2 == 1, (
                f'f({gen}) → {img_gen} violates parity reversal')

    # 3. Anti-symmetry: (δf)(X,Y) = -(-1)^{pX pY} (δf)(Y,X)
    cb_lookup: dict[tuple, dict] = {}
    raw = defaultdict(lambda: defaultdict(Fraction))
    for e in entries:
        raw[(e['X'], e['Y'])][e['Z']] += parse_frac(e['coeff'])
    cb_lookup = {k: {Z: c for Z, c in v.items() if c} for k, v in raw.items()}

    for X in basis_all:
        pX = parity[X]
        for Y in basis_all:
            pY = parity[Y]
            XY = cb_lookup.get((X, Y), {})
            YX = cb_lookup.get((Y, X), {})
            sign = Fraction((-1) ** (pX * pY))
            residual: dict[str, Fraction] = {}
            for Z, c in XY.items():
                v = residual.get(Z, Fraction(0)) + c
                if v:
                    residual[Z] = v
                else:
                    residual.pop(Z, None)
            for Z, c in YX.items():
                v = residual.get(Z, Fraction(0)) + sign * c
                if v:
                    residual[Z] = v
                else:
                    residual.pop(Z, None)
            assert not residual, (
                f'Anti-symmetry failure: (δf)({X},{Y}) + sign*(δf)({Y},{X}) = {residual}')


# ── main ─────────────────────────────────────────────────────────────────────

def main():
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    data_dir = os.path.join(root, 'data')

    print('C(n+1) Schema 4 — coboundary build')
    print('=' * 60)
    print(f'f: {F_DESCRIPTION}')
    print()

    overall_pass = True
    for n in [1, 2, 3]:
        print(f'n={n}  C({n+1}) = osp(2|{2*n})')
        try:
            result = build_coboundary_n(n, data_dir)
            entries = result['coboundary']
            nz_images = sum(1 for v in result['f_map']['nonzero'].values() if v)
            print(f'  f non-zero images    : {nz_images} generators')
            print(f'  Coboundary entries   : {len(entries)}')
            print(f'  Consistency checks   : PASS')

            out_path = os.path.join(data_dir, f'C_{n}_coboundary.json')
            with open(out_path, 'w') as fh:
                json.dump(result, fh, indent=2, ensure_ascii=False)
            print(f'  Written : {out_path}')
        except Exception as exc:
            overall_pass = False
            import traceback
            traceback.print_exc()
            print(f'  FAIL: {exc}')
        print()

    print('=' * 60)
    if overall_pass:
        print('ALL CHECKS PASSED')
    else:
        print('FAILURES DETECTED — see above')
        sys.exit(1)


if __name__ == '__main__':
    main()
