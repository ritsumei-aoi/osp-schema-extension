"""Unit tests for the oscillator engine (src/c_algebra.py) and the Schema 1 generator."""

import os
import sys
from fractions import Fraction

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), 'src'))

from c_algebra import (  # noqa: E402
    IDENTITY_KEY, B, F, bracket, build_basis, lin, mono, mul, parity, structure,
)

RANKS = (1, 2, 3)
EXPECTED = {1: (4, 4), 2: (11, 8), 3: (22, 12)}  # (even, odd)


@pytest.mark.parametrize('n', RANKS)
def test_dimensions_and_parity(n):
    basis = build_basis(n)
    even = [x for x in basis if x['parity'] == 0]
    odd = [x for x in basis if x['parity'] == 1]
    assert (len(even), len(odd)) == EXPECTED[n]
    assert len(basis) == 2 * n * n + 5 * n + 1
    assert len(odd) == 4 * n
    assert len(even) == 2 * n * n + n + 1
    for x in basis:
        assert parity(x['element']) == x['parity']
    assert len({x['label'] for x in basis}) == len(basis)


@pytest.mark.parametrize('n', RANKS)
def test_structure_closes(n):
    # structure() raises if any kappa-free or kappa-part bracket leaves span(basis) + C*K
    basis, sc, gamma, gamma_k = structure(n)
    assert len(sc) == len(basis) ** 2


def test_normal_ordering_relations():
    # b^- b^+ = b^+ b^- + 1
    lhs = mono(B('-', 1), B('+', 1))
    rhs = lin((1, mono(B('+', 1), B('-', 1))), (1, {IDENTITY_KEY: Fraction(1)}))
    assert lhs == rhs
    # a^- a^+ = 1 - a^+ a^-
    lhs = mono(F('-'), F('+'))
    rhs = lin((1, {IDENTITY_KEY: Fraction(1)}), (-1, mono(F('+'), F('-'))))
    assert lhs == rhs
    # (a^+)^2 = 0
    assert mono(F('+'), F('+')) == {}


def test_deformed_relation_b_a():
    # b a = a b - gb_{sigma,j,s} kappa,  with tag (sigma, j, s)
    ba = mono(B('+', 1), F('-'))
    ab = mono(F('-'), B('+', 1))
    # the contraction removes both letters, so the kappa term is -gb * K (constant)
    expected_tag = {((), (), ('-', 1, '+')): Fraction(-1)}
    kappa_part = {k: v for k, v in ba.items() if k[2] is not None}
    assert kappa_part == expected_tag
    kappa_free = {k: v for k, v in ba.items() if k[2] is None}
    assert kappa_free == ab


def test_kappa_squared_vanishes():
    # the kappa part of b^+ a^- is -gb * K; its square is zero, although the
    # kappa-free part times the kappa part is not
    ba = mono(B('+', 1), F('-'))
    k_part = {k: v for k, v in ba.items() if k[2] is not None}
    assert mul(k_part, k_part) == {}
    full_square = mul(ba, ba)
    assert any(k[2] is not None for k in full_square)


def test_bracket_is_graded_antisymmetric_undeformed():
    basis = build_basis(2)
    for X in basis[:6]:
        for Y in basis[:6]:
            lhs = bracket(X['element'], Y['element'])
            rhs = bracket(Y['element'], X['element'])
            sign = (-1) ** (X['parity'] * Y['parity'])
            combined = {k: v for k, v in lhs.items()}
            for k, v in rhs.items():
                combined[k] = combined.get(k, 0) + sign * v
            assert all(v == 0 for v in combined.values())


@pytest.mark.parametrize('n', (1, 2))
def test_jacobi_undeformed(n):
    basis, sc, _gamma, _gk = structure(n)
    size = len(basis)

    def br(i, j):
        return {c: v for c, v in sc[(i, j)].items()}

    def bracket_vec(vec_a, vec_b):
        out = {}
        for i, a in vec_a.items():
            for j, b in vec_b.items():
                for c, v in br(i, j).items():
                    out[c] = out.get(c, 0) + a * b * v
        return {c: v for c, v in out.items() if v != 0}

    for i in range(size):
        for j in range(size):
            for k in range(size):
                pi, pj = basis[i]['parity'], basis[j]['parity']
                lhs = bracket_vec({i: Fraction(1)}, bracket_vec({j: Fraction(1)}, {k: Fraction(1)}))
                t1 = bracket_vec(bracket_vec({i: Fraction(1)}, {j: Fraction(1)}), {k: Fraction(1)})
                t2 = bracket_vec({j: Fraction(1)}, bracket_vec({i: Fraction(1)}, {k: Fraction(1)}))
                sign = (-1) ** (pi * pj)
                rhs = dict(t1)
                for c, v in t2.items():
                    rhs[c] = rhs.get(c, 0) + sign * v
                diff = {c: lhs.get(c, 0) - rhs.get(c, 0) for c in set(lhs) | set(rhs)}
                assert all(v == 0 for v in diff.values()), (i, j, k)


def test_generator_writes_schema1(tmp_path):
    from C_generators import write_schema1
    import json
    path = write_schema1(1, out_dir=str(tmp_path), generation_date='2026-10-08')
    with open(path, encoding='utf-8') as fh:
        doc = json.load(fh)
    assert doc['algebra']['dimension'] == {'total': 8, 'even': 4, 'odd': 4,
                                           'formulas': {'even': '2n^2 + n + 1', 'odd': '4n',
                                                        'total': '2n^2 + 5n + 1'}}
    assert set(doc['oscillator_generators']) == {'fermions', 'bosons'}
    assert 'central_elements' in doc and set(doc['central_elements']) == {'kappa', 'K'}
    assert doc['basis']['odd'] == ['E_eps1_del1_pp', 'E_eps1_del1_pm', 'E_eps1_del1_mp', 'E_eps1_del1_mm']
    assert all(doc['parity'][x] == 1 for x in doc['basis']['odd'])


def test_kappa_is_super_central_leibniz_on_car():
    # a^- a^+ + a^+ a^- = 1, so b a^- a^+ + b a^+ a^- must equal b, with kappa terms included.
    # This holds only if kappa anticommutes with a^±.
    b_then_aa = lin((1, mono(B('+', 1), F('-'), F('+'))), (1, mono(B('+', 1), F('+'), F('-'))))
    assert b_then_aa == mono(B('+', 1))


@pytest.mark.parametrize('n', (1, 2))
def test_associativity_of_deformed_algebra(n):
    els = [x['element'] for x in build_basis(n)]
    for X in els:
        for Y in els:
            for Z in els:
                assert mul(mul(X, Y), Z) == mul(X, mul(Y, Z))


@pytest.mark.parametrize('n', (1, 2))
def test_gamma_cocycle_and_antisymmetry(n):
    # gamma satisfies the cocycle condition and graded anti-symmetry (kappa odd, super-central)
    from C_gamma import gamma_checks
    basis, sc, gamma, _gk = structure(n)
    result = gamma_checks(basis, gamma, sc)
    assert result['parity_failures'] == 0
    assert result['antisymmetry_failures'] == 0
    assert result['cocycle_failures'] == 0
    assert result['algebra_jacobi_failures'] == 0


def test_verifier_detects_corrupted_structure_constant():
    # Negative control: the independent verifier must flag a perturbed structure constant.
    from verify_C_structure import check_table, load_structure
    doc, basis, parity, table = load_structure(1)
    _pairs, _triples, clean = check_table(basis, parity, table)
    assert not any(clean.values())
    corrupted = {k: dict(v) for k, v in table.items()}
    key = next(k for k, v in corrupted.items() if v and parity[k[0]] == parity[k[1]] == 1)
    z = next(iter(corrupted[key]))
    corrupted[key][z] = corrupted[key][z] + 1
    _pairs, _triples, bad = check_table(basis, parity, corrupted)
    assert bad['jacobi'] or bad['antisymmetry']


def _weights(elem, n):
    """Eigenvalues of ad(F) (F = a^+a^-) and ad(N_k) (N_k = b_k^+b_k^-) on a homogeneous element.

    Computed by counting letters, which is independent of the normal-ordering code.
    """
    wF = set()
    wN = {k: set() for k in range(1, n + 1)}
    for (fer, bos, tag), _ in elem.items():
        assert tag is None
        wF.add(sum(1 if x[1] == '+' else -1 for x in fer))
        for k in range(1, n + 1):
            wN[k].add(sum(1 if (x[2] == k and x[1] == '+') else (-1 if x[2] == k else 0) for x in bos))
    assert len(wF) == 1 and all(len(s) == 1 for s in wN.values())
    return wF.pop(), {k: s.pop() for k, s in wN.items()}


@pytest.mark.parametrize('n', RANKS)
def test_cartan_brackets_match_letter_weights(n):
    # Cartan generators in the (F, N_k) basis:
    #   H_1 = F + N_1,  H_k = N_{k-1} - N_k (2<=k<=n),  H_{n+1} = -N_n - 1/2
    basis, sc, _g, _gk = structure(n)
    cartan = {'H_1': (1, {1: 1})}
    for k in range(2, n + 1):
        cartan['H_%d' % k] = (0, {k - 1: 1, k: -1})
    cartan['H_%d' % (n + 1)] = (0, {n: -1})
    index = {x['label']: i for i, x in enumerate(basis)}
    weights = [_weights(x['element'], n) for x in basis]
    for h_label, (fcoef, ncoef) in cartan.items():
        h = index[h_label]
        for a, (x, (wf, wn)) in enumerate(zip(basis, weights)):
            eigen = fcoef * wf + sum(c * wn[k] for k, c in ncoef.items())
            expected = {a: Fraction(eigen)} if eigen else {}
            assert sc[(h, a)] == expected, (h_label, x['label'])
