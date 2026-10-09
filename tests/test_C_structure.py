"""Unit tests for C(n+1) Schema 1 structure constants."""

import json
import os
import sys
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")

def load(n):
    path = os.path.join(DATA_DIR, f"C_{n}_structure.json")
    with open(path) as f:
        return json.load(f)


@pytest.mark.parametrize("n", [1, 2, 3])
def test_dimension(n):
    d = load(n)
    basis = d["basis"]
    dim_even = 2 * n * n + n + 1
    dim_odd = 4 * n
    assert len(basis["even"]) == dim_even, f"n={n}: even basis count mismatch"
    assert len(basis["odd"]) == dim_odd, f"n={n}: odd basis count mismatch"
    assert d["algebra"]["dimension"]["even"] == dim_even
    assert d["algebra"]["dimension"]["odd"] == dim_odd
    assert d["algebra"]["dimension"]["total"] == dim_even + dim_odd


@pytest.mark.parametrize("n", [1, 2, 3])
def test_parity_counts(n):
    d = load(n)
    parity = d["parity"]
    even_count = sum(1 for v in parity.values() if v == 0)
    odd_count = sum(1 for v in parity.values() if v == 1)
    assert even_count == 2 * n * n + n + 1
    assert odd_count == 4 * n


@pytest.mark.parametrize("n", [1, 2, 3])
def test_generator_labels_consistent(n):
    d = load(n)
    basis_all = set(d["basis"]["even"] + d["basis"]["odd"])
    parity_keys = set(d["parity"].keys())
    realization_keys = set(d["generator_realization"]["realizations"].keys())
    # Every basis element must appear in parity
    assert basis_all == parity_keys, f"n={n}: parity keys do not match basis"
    # Realization keys must be a subset of basis (template keys excluded)
    for key in realization_keys:
        if "{" not in key:
            assert key in basis_all, f"n={n}: realization key {key} not in basis"


@pytest.mark.parametrize("n", [1, 2, 3])
def test_structure_constants_involve_basis_elements(n):
    d = load(n)
    basis_all = set(d["basis"]["even"] + d["basis"]["odd"])
    for sc in d["structure_constants"]:
        assert sc["X"] in basis_all, f"n={n}: X={sc['X']} not in basis"
        assert sc["Y"] in basis_all, f"n={n}: Y={sc['Y']} not in basis"
        assert sc["Z"] in basis_all, f"n={n}: Z={sc['Z']} not in basis"


@pytest.mark.parametrize("n", [1, 2, 3])
def test_cartan_action_nonzero(n):
    """Each Cartan H_k must act non-trivially on at least some generators."""
    d = load(n)
    sc = d["structure_constants"]
    cartans = {f"H_{k}" for k in range(1, n + 2)}
    active_cartans = {s["X"] for s in sc if s["X"] in cartans}
    assert active_cartans == cartans, f"n={n}: Cartans with no action: {cartans - active_cartans}"


@pytest.mark.parametrize("n", [1, 2, 3])
def test_odd_odd_brackets_exist(n):
    """Anticommutators of odd generators must produce even generators."""
    d = load(n)
    parity = d["parity"]
    sc = d["structure_constants"]
    odd_pairs = [s for s in sc if parity.get(s["X"], -1) == 1 and parity.get(s["Y"], -1) == 1]
    assert len(odd_pairs) > 0, f"n={n}: no odd-odd brackets found"
    for s in odd_pairs:
        assert parity[s["Z"]] == 0, (
            f"n={n}: odd-odd bracket {s['X']},{s['Y']} → {s['Z']} has odd parity"
        )


@pytest.mark.parametrize("n", [1, 2, 3])
def test_parity_conservation(n):
    """[X, Y] = Z requires p(X) + p(Y) ≡ p(Z) (mod 2)."""
    d = load(n)
    parity = d["parity"]
    for sc in d["structure_constants"]:
        px = parity[sc["X"]]
        py = parity[sc["Y"]]
        pz = parity[sc["Z"]]
        assert (px + py) % 2 == pz, (
            f"n={n}: parity violation [{sc['X']}({px}), {sc['Y']}({py})] → {sc['Z']}({pz})"
        )


@pytest.mark.parametrize("n", [1, 2, 3])
def test_schema_version(n):
    d = load(n)
    assert d["schema_version"] == "5.0"


@pytest.mark.parametrize("n", [1, 2, 3])
def test_central_elements_top_level(n):
    d = load(n)
    assert "central_elements" in d
    assert "kappa" in d["central_elements"]
    assert "K" in d["central_elements"]
    assert d["central_elements"]["kappa"]["parity"] == 1
    assert d["central_elements"]["K"]["parity"] == 0


@pytest.mark.parametrize("n", [1, 2, 3])
def test_algebra_fields(n):
    d = load(n)
    alg = d["algebra"]
    assert alg["family"] == "C"
    assert alg["m"] == 1
    assert alg["n"] == n
