"""Unit tests for the C(n+1) oscillator engine and Schema 1 generation (I03)."""

import pytest

from C_algebra import bracket, build_basis, kappa_free, structure_constants


@pytest.mark.parametrize('n', [1, 2, 3])
def test_generator_counts(n):
    basis = build_basis(n)
    even = [b for b in basis if b['parity'] == 0]
    odd = [b for b in basis if b['parity'] == 1]
    assert len(even) == 2 * n * n + n + 1
    assert len(odd) == 4 * n
    assert len(basis) == 2 * n * n + 5 * n + 1


@pytest.mark.parametrize('n', [1, 2, 3])
def test_parity_and_labels(n):
    basis = build_basis(n)
    labels = [b['label'] for b in basis]
    assert len(set(labels)) == len(labels)
    for b in basis:
        expected = 1 if b['label'].startswith('E_eps1_') else 0
        assert b['parity'] == expected
    odd_labels = sorted(b['label'] for b in basis if b['parity'] == 1)
    expected_odd = sorted(
        f'E_eps1_del{k}_{c}' for k in range(1, n + 1)
        for c in ('pp', 'pm', 'mp', 'mm'))
    assert odd_labels == expected_odd


@pytest.mark.parametrize('n', [1, 2, 3])
def test_closure_no_residual(n):
    _, _, residuals = structure_constants(n)
    assert residuals == {}


@pytest.mark.parametrize('n', [1, 2])
def test_super_skew_symmetry(n):
    basis = build_basis(n)
    for i, X in enumerate(basis):
        for j, Y in enumerate(basis):
            if i >= j:
                continue
            xy = kappa_free(bracket(X['elem'], Y['elem'], X['parity'], Y['parity']))
            yx = kappa_free(bracket(Y['elem'], X['elem'], Y['parity'], X['parity']))
            sign = -1 if (X['parity'] * Y['parity']) % 2 else 1
            for k in set(xy) | set(yx):
                assert yx.get(k, 0) == -sign * xy.get(k, 0)


def test_known_brackets_n1():
    _, table, _ = structure_constants(1)
    basis = build_basis(1)
    index = {b['label']: i for i, b in enumerate(basis)}

    def get(x, y):
        i, j = index[x], index[y]
        return table[(i, j)] if i <= j else None

    # [E_{2δ}, E_{-2δ}] = 4 H_2
    assert get('E_2del1_p', 'E_2del1_m') == {index['H_2']: 4}
    # {a^+ b^+, a^- b^-} = -H_1 - 2 H_2
    assert get('E_eps1_del1_pp', 'E_eps1_del1_mm') == {index['H_1']: -1, index['H_2']: -2}


@pytest.mark.parametrize('n', [1, 2, 3])
def test_cartan_diagonal(n):
    """Every Cartan generator acts diagonally on the basis (weight vectors)."""
    basis, table, _ = structure_constants(n)
    cartan = [i for i, X in enumerate(basis) if X['label'].startswith('H_')]
    for h in cartan:
        for j in range(len(basis)):
            if j == h:
                continue
            key = (min(h, j), max(h, j))
            img = table.get(key, {})
            # [H, E_j] is a multiple of E_j only when the pair is nonzero
            assert set(img) <= {j}
