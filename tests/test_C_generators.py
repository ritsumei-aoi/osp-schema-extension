"""
Unit tests for C_generators.py.

Tests:
  T1  Dimension formulas for n=1,2,3
  T2  Generator count per type
  T3  Parity assignments
  T4  Cartan eigenvalue formula on selected generators
  T5  Specific odd-odd brackets (from spec derivation)
  T6  Even-odd bracket example
  T7  Anti-symmetry: [X,Y} = -(-1)^{pX*pY} [Y,X}
  T8  Jacobi identity on three representative triples
  T9  All SC coefficients are Fraction (exact rational)
  T10 Schema field completeness
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from fractions import Fraction
from C_generators import (
    make_generators, basis_list, compute_structure_constants,
    generate_schema1, _graded_bracket, _pbw_index, identify,
)


# ── helpers ────────────────────────────────────────────────────────

def bracket(n, lx, ly):
    """Return identify'd bracket [lx, ly} for C(n+1)."""
    gens = make_generators(n)
    pbw = _pbw_index(n)
    ex, px = gens[lx]
    ey, py = gens[ly]
    raw = _graded_bracket(ex, px, ey, py, pbw)
    if not raw:
        return {}
    return identify(raw, gens, n)


# ── T1: Dimension formulas ─────────────────────────────────────────

def test_dimensions():
    for n in [1, 2, 3]:
        odd, even = basis_list(n)
        assert len(even) == 2*n*n + n + 1, f"n={n}: even dim"
        assert len(odd)  == 4*n,            f"n={n}: odd dim"
        assert len(even) + len(odd) == 2*n*n + 5*n + 1, f"n={n}: total dim"
    print("T1 PASS: dimension formulas")


# ── T2: Generator count per type ──────────────────────────────────

def test_generator_counts():
    for n in [1, 2, 3]:
        gens = make_generators(n)
        n_cartan = sum(1 for l in gens if l.startswith('H_'))
        n_odd    = sum(1 for l in gens if l.startswith('E_eps1'))
        n_2del   = sum(1 for l in gens if l.startswith('E_2del'))
        n_cross  = sum(1 for l in gens if l.startswith('E_del'))

        assert n_cartan == n + 1,       f"n={n}: Cartan count {n_cartan}"
        assert n_odd    == 4 * n,        f"n={n}: odd count {n_odd}"
        assert n_2del   == 2 * n,        f"n={n}: E_2del count {n_2del}"
        # E_del: 4 * C(n,2) = 4 * n*(n-1)/2 = 2*n*(n-1)
        assert n_cross  == 2*n*(n-1),   f"n={n}: E_del cross count {n_cross}"
    print("T2 PASS: generator counts")


# ── T3: Parity assignments ────────────────────────────────────────

def test_parity():
    for n in [1, 2, 3]:
        gens = make_generators(n)
        for lbl, (_, p) in gens.items():
            expected = 1 if lbl.startswith('E_eps1') else 0
            assert p == expected, f"n={n}: parity mismatch for {lbl}"
    print("T3 PASS: parity assignments")


# ── T4: Cartan eigenvalues ────────────────────────────────────────

def test_cartan_eigenvalues():
    # [H_k, E_beta] = eig(H_k, E_beta) * E_beta
    # Verify using the eigenvalue formula from notation.md
    for n in [1, 2, 3]:
        gens = make_generators(n)
        pbw = _pbw_index(n)

        # [H_1, E_eps1_del1_pp] should give eigenvalue s_eps+s_1 = 1+1 = 2
        res = bracket(n, 'H_1', 'E_eps1_del1_pp')
        assert res == {'E_eps1_del1_pp': Fraction(2)}, \
            f"n={n}: [H_1, E_eps1_del1_pp] = {res}"

        # [H_1, E_eps1_del1_mm] should give s_eps+s_1 = (-1)+(-1) = -2
        res = bracket(n, 'H_1', 'E_eps1_del1_mm')
        assert res == {'E_eps1_del1_mm': Fraction(-2)}, \
            f"n={n}: [H_1, E_eps1_del1_mm] = {res}"

        # [H_1, E_eps1_del1_pm] should give s_eps+s_1 = 1+(-1) = 0 → zero
        res = bracket(n, 'H_1', 'E_eps1_del1_pm')
        assert res == {}, f"n={n}: [H_1, E_eps1_del1_pm] should be 0, got {res}"

        # [H_2, E_eps1_del1_pp] (n>=2): s_{k-1}-s_k = s_1-s_eps ... wait
        # H_2 = N_1 - N_2, eigenvalue = s_1 - s_2
        # E_eps1_del1_pp: s_1=+1, s_2=0 → eigenvalue = 1
        if n >= 2:
            res = bracket(n, 'H_2', 'E_eps1_del1_pp')
            assert res == {'E_eps1_del1_pp': Fraction(1)}, \
                f"n={n}: [H_2, E_eps1_del1_pp] = {res}"

        # [H_1, E_2del1_p] = (s_eps + s_1) = (0 + 2) = 2 (two b_1^+ factors)
        res = bracket(n, 'H_1', 'E_2del1_p')
        assert res == {'E_2del1_p': Fraction(2)}, \
            f"n={n}: [H_1, E_2del1_p] = {res}"

    print("T4 PASS: Cartan eigenvalues")


# ── T5: Odd-odd brackets (from spec derivation) ──────────────────

def test_odd_odd_diagonal():
    # {E_eps1_delj_pp, E_eps1_delj_mm} = -H_1 + Σ_{l=2}^{j} H_l + 2Σ_{l=j+1}^{n} H_l - 2H_{n+1}
    for n in [1, 2, 3]:
        for j in range(1, n + 1):
            res = bracket(n, f'E_eps1_del{j}_pp', f'E_eps1_del{j}_mm')
            # Build expected from formula
            expected: dict[str, Fraction] = {}
            expected['H_1'] = Fraction(-1)
            for l in range(2, j + 1):
                expected[f'H_{l}'] = expected.get(f'H_{l}', Fraction(0)) + Fraction(1)
            for l in range(j + 1, n + 1):
                expected[f'H_{l}'] = expected.get(f'H_{l}', Fraction(0)) + Fraction(2)
            expected[f'H_{n+1}'] = expected.get(f'H_{n+1}', Fraction(0)) + Fraction(-2)
            expected = {k: v for k, v in expected.items() if v != 0}

            assert res == expected, \
                f"n={n}, j={j}: {{E_eps1_del{j}_pp, E_eps1_del{j}_mm}} = {res}, expected {expected}"
    print("T5 PASS: odd-odd diagonal brackets")


def test_odd_odd_offdiagonal():
    # {E_eps1_deli_pp, E_eps1_delj_mm} = E_del{min}_{max}_pm (i<j) or E_del{min}_{max}_mp (i>j)
    # more precisely:
    # {E_eps1_deli_pp, E_eps1_delj_mm} (i<j) = E_del{i}_del{j}_pm
    # {E_eps1_deli_pp, E_eps1_delj_mm} (i>j) = E_del{j}_del{i}_mp  ← verify
    for n in [2, 3]:
        # i < j case
        res = bracket(n, 'E_eps1_del1_pp', 'E_eps1_del2_mm')
        assert res == {'E_del1_del2_pm': Fraction(1)}, \
            f"n={n}: {{E_eps1_del1_pp, E_eps1_del2_mm}} = {res}"

        if n >= 3:
            res = bracket(n, 'E_eps1_del1_pp', 'E_eps1_del3_mm')
            assert res == {'E_del1_del3_pm': Fraction(1)}, \
                f"n={n}: {{E_eps1_del1_pp, E_eps1_del3_mm}} = {res}"

        # i > j case: {E_eps1_del2_pp, E_eps1_del1_mm}
        # (eps+del2) + (-eps-del1) = del2-del1 = -(del1-del2)
        # In our labeling: del1-del2 = E_del1_del2_pm (b_1^+ b_2^-)
        # del2-del1 = E_del1_del2_mp (b_1^- b_2^+)
        res = bracket(n, 'E_eps1_del1_mm', 'E_eps1_del2_pp')
        # {E_eps1_del2_pp, E_eps1_del1_mm} = E_del1_del2_mp (coefficient to check)
        # In sc_ordering: E_eps1_del1_mm comes after E_eps1_del2_pp? Let's just check the raw bracket
        gens = make_generators(n)
        pbw = _pbw_index(n)
        ex, px = gens['E_eps1_del2_pp']
        ey, py = gens['E_eps1_del1_mm']
        raw = _graded_bracket(ex, px, ey, py, pbw)
        res2 = identify(raw, gens, n) if raw else {}
        assert res2 == {'E_del1_del2_mp': Fraction(1)}, \
            f"n={n}: {{E_eps1_del2_pp, E_eps1_del1_mm}} = {res2}"

    print("T5b PASS: odd-odd off-diagonal brackets")


# ── T6: Even-odd bracket ─────────────────────────────────────────

def test_even_odd_bracket():
    # [E_2del1_p, E_eps1_del1_pm] = -2 * E_eps1_del1_pp
    # (from computation: [(b_1^+)^2, a_1^+ b_1^-] = -2 a_1^+ b_1^+)
    for n in [1, 2, 3]:
        res = bracket(n, 'E_2del1_p', 'E_eps1_del1_pm')
        assert res == {'E_eps1_del1_pp': Fraction(-2)}, \
            f"n={n}: [E_2del1_p, E_eps1_del1_pm] = {res}"
    print("T6 PASS: even-odd bracket")


# ── T7: Anti-symmetry ─────────────────────────────────────────────

def test_antisymmetry():
    # [X,Y} = -(-1)^{pX*pY} [Y,X}
    for n in [1, 2]:
        gens = make_generators(n)
        pbw = _pbw_index(n)
        pairs_to_check = [
            ('H_1', 'E_eps1_del1_pp'),
            ('E_eps1_del1_pp', 'E_eps1_del1_mm'),
            ('E_2del1_p', 'E_2del1_m'),
        ]
        if n >= 2:
            pairs_to_check += [
                ('E_eps1_del1_pp', 'E_eps1_del2_mm'),
                ('H_2', 'E_del1_del2_pp'),
            ]

        for lx, ly in pairs_to_check:
            ex, px = gens[lx]
            ey, py = gens[ly]
            xy = _graded_bracket(ex, px, ey, py, pbw)
            yx = _graded_bracket(ey, py, ex, px, pbw)
            sign = (-1) ** (px * py)
            # [X,Y} + (-1)^{pX pY} [Y,X} should be zero
            from collections import defaultdict
            combined: dict = defaultdict(Fraction)
            for w, c in xy.items():
                combined[w] += c
            for w, c in yx.items():
                combined[w] += sign * c
            combined = {k: v for k, v in combined.items() if v != 0}
            assert combined == {}, \
                f"n={n}: anti-symmetry failed for ({lx}, {ly}): residual={combined}"
    print("T7 PASS: graded anti-symmetry")


# ── T8: Jacobi identity ───────────────────────────────────────────

def test_jacobi():
    # [X, [Y, Z}} + (-1)^{pX(pY+pZ)} [Y, [Z, X}} + (-1)^{pZ(pX+pY)} [Z, [X, Y}} = 0
    for n in [1, 2]:
        gens = make_generators(n)
        pbw = _pbw_index(n)

        triples = [
            ('H_1', 'E_eps1_del1_pp', 'E_eps1_del1_mm'),
            ('E_eps1_del1_pp', 'E_eps1_del1_mm', 'H_1'),
            ('E_2del1_p', 'E_eps1_del1_pm', 'E_eps1_del1_mp'),
        ]
        if n >= 2:
            triples += [
                ('E_eps1_del1_pp', 'E_eps1_del2_pp', 'E_eps1_del2_mm'),
            ]

        for lx, ly, lz in triples:
            ex, px = gens[lx]
            ey, py = gens[ly]
            ez, pz = gens[lz]

            def br(e1, p1, e2, p2):
                return _graded_bracket(e1, p1, e2, p2, pbw)

            # [Y, Z]
            yz = br(ey, py, ez, pz)
            # [X, [Y, Z]]
            x_yz = br(ex, px, yz, py + pz) if yz else {}
            # [Z, X]
            zx = br(ez, pz, ex, px)
            # [Y, [Z, X]]
            y_zx = br(ey, py, zx, pz + px) if zx else {}
            # [X, Y]
            xy = br(ex, px, ey, py)
            # [Z, [X, Y]]
            z_xy = br(ez, pz, xy, px + py) if xy else {}

            s1 = 1
            s2 = (-1) ** (px * (py + pz))
            s3 = (-1) ** (pz * (px + py))

            from collections import defaultdict
            jacobi: dict = defaultdict(Fraction)
            for w, c in x_yz.items(): jacobi[w] += s1 * c
            for w, c in y_zx.items(): jacobi[w] += s2 * c
            for w, c in z_xy.items(): jacobi[w] += s3 * c
            jacobi = {k: v for k, v in jacobi.items() if v != 0}
            assert jacobi == {}, \
                f"n={n}: Jacobi failed for ({lx},{ly},{lz}): {jacobi}"

    print("T8 PASS: Jacobi identity")


# ── T9: All SC coefficients are Fraction ─────────────────────────

def test_sc_are_rational():
    for n in [1, 2, 3]:
        sc = compute_structure_constants(n)
        for entry in sc:
            for lbl, coeff in entry['terms']:
                assert isinstance(coeff, Fraction), \
                    f"n={n}: SC coeff {coeff!r} is not Fraction for ({entry['X']},{entry['Y']})"
    print("T9 PASS: structure constants are exact rationals")


# ── T10: Schema field completeness (10 top-level keys per spec §2) ──

def test_schema_fields():
    # Exact 10 top-level keys from docs/json_schema_specification.md Section 2
    REQUIRED_KEYS = {
        'schema_version',
        'algebra',
        'oscillator_generators',
        'oscillator_relations',
        'central_elements',
        'basis',
        'parity',
        'generator_realization',
        'structure_constants',
        'metadata',
    }
    for n in [1, 2, 3]:
        schema = generate_schema1(n)

        # Top-level key check
        assert set(schema.keys()) == REQUIRED_KEYS, \
            f"n={n}: top-level keys mismatch.\n  got:      {sorted(schema.keys())}\n  expected: {sorted(REQUIRED_KEYS)}"

        # schema_version
        assert schema['schema_version'] == '5.0', f"n={n}: schema_version"

        # algebra sub-fields
        alg = schema['algebra']
        assert alg['family'] == 'C'
        assert alg['m'] == 1
        assert alg['n'] == n
        assert alg['dimension']['even'] == 2*n*n + n + 1, f"n={n}: algebra.dimension.even"
        assert alg['dimension']['odd']  == 4*n,           f"n={n}: algebra.dimension.odd"

        # oscillator_generators sub-fields
        og = schema['oscillator_generators']
        assert 'fermions' in og and 'bosons' in og, f"n={n}: oscillator_generators keys"
        assert og['fermions']['parity'] == 1
        assert og['bosons']['count'] == 2 * n

        # oscillator_relations sub-fields
        orel = schema['oscillator_relations']
        assert 'standard_fermion_anticommutators' in orel
        assert 'bosonic_commutators' in orel
        assert 'mixed_commutators' in orel

        # central_elements: must have kappa (parity 1) and K (parity 0)
        ce = schema['central_elements']
        assert 'kappa' in ce and 'K' in ce, f"n={n}: central_elements keys"
        assert ce['kappa']['parity'] == 1
        assert ce['K']['parity'] == 0

        # basis sizes
        assert len(schema['basis']['odd'])  == 4*n,        f"n={n}: basis.odd size"
        assert len(schema['basis']['even']) == 2*n*n+n+1,  f"n={n}: basis.even size"
        assert 'ordering_convention' in schema['basis'],   f"n={n}: basis.ordering_convention"

        # parity: every basis generator present, correct values
        par = schema['parity']
        for lbl in schema['basis']['odd']:
            assert par[lbl] == 1, f"n={n}: parity[{lbl}] should be 1"
        for lbl in schema['basis']['even']:
            assert par[lbl] == 0, f"n={n}: parity[{lbl}] should be 0"

        # generator_realization sub-fields
        gr = schema['generator_realization']
        assert 'description' in gr and 'ordering' in gr and 'realizations' in gr
        real = gr['realizations']
        for lbl in schema['basis']['odd'] + schema['basis']['even']:
            assert lbl in real, f"n={n}: generator_realization missing {lbl}"
            entry = real[lbl]
            assert 'standard_form' in entry
            assert 'frappat_form' in entry
            assert 'parity' in entry

        # structure_constants: list of {X,Y,Z,coeff,sign_rule}
        for sc_entry in schema['structure_constants']:
            assert set(sc_entry.keys()) == {'X', 'Y', 'Z', 'coeff', 'sign_rule'}, \
                f"n={n}: SC entry keys: {sc_entry}"
            assert sc_entry['sign_rule'] == 'graded'

        # metadata sub-fields
        md = schema['metadata']
        assert 'generated_by' in md
        assert 'generation_date' in md
        assert 'references' in md

    print("T10 PASS: schema field completeness (10 top-level keys per spec §2)")


# ── run all ───────────────────────────────────────────────────────

if __name__ == '__main__':
    test_dimensions()
    test_generator_counts()
    test_parity()
    test_cartan_eigenvalues()
    test_odd_odd_diagonal()
    test_odd_odd_offdiagonal()
    test_even_odd_bracket()
    test_antisymmetry()
    test_jacobi()
    test_sc_are_rational()
    test_schema_fields()
    print("\nAll tests PASSED.")
