"""Tests for C(n+1) structure constant generator (Schema 1)."""
import json
import os
import sys
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
from C_generators import build_basis, build_parity_dict, build_schema1


DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")

EXPECTED_DIM = {
    1: {"even": 4, "odd": 4, "total": 8},
    2: {"even": 11, "odd": 8, "total": 19},
    3: {"even": 22, "odd": 12, "total": 34},
}


@pytest.mark.parametrize("n", [1, 2, 3])
def test_basis_counts(n):
    even, odd = build_basis(n)
    exp = EXPECTED_DIM[n]
    assert len(even) == exp["even"], f"n={n}: even count {len(even)} != {exp['even']}"
    assert len(odd) == exp["odd"], f"n={n}: odd count {len(odd)} != {exp['odd']}"
    assert len(even) + len(odd) == exp["total"]


@pytest.mark.parametrize("n", [1, 2, 3])
def test_basis_no_duplicates(n):
    even, odd = build_basis(n)
    all_gen = even + odd
    assert len(all_gen) == len(set(all_gen)), f"n={n}: duplicate generator labels"


@pytest.mark.parametrize("n", [1, 2, 3])
def test_parity_dict(n):
    even, odd = build_basis(n)
    parity = build_parity_dict(even, odd)
    for g in even:
        assert parity[g] == 0, f"{g} should be even"
    for g in odd:
        assert parity[g] == 1, f"{g} should be odd"


@pytest.mark.parametrize("n", [1, 2, 3])
def test_json_file_exists(n):
    path = os.path.join(DATA_DIR, f"C_{n}_structure.json")
    assert os.path.exists(path), f"Missing {path}"


@pytest.mark.parametrize("n", [1, 2, 3])
def test_json_schema_fields(n):
    path = os.path.join(DATA_DIR, f"C_{n}_structure.json")
    with open(path) as f:
        data = json.load(f)
    assert data["schema_version"] == "5.0"
    assert data["algebra"]["family"] == "C"
    assert data["algebra"]["m"] == 1
    assert data["algebra"]["n"] == n
    assert "central_elements" in data
    assert "kappa" in data["central_elements"]
    assert data["central_elements"]["kappa"]["parity"] == 1
    assert "K" in data["central_elements"]
    assert "fermions" in data["oscillator_generators"]
    assert "bosons" in data["oscillator_generators"]
    exp = EXPECTED_DIM[n]
    assert data["algebra"]["dimension"]["even"] == exp["even"]
    assert data["algebra"]["dimension"]["odd"] == exp["odd"]
    assert data["algebra"]["dimension"]["total"] == exp["total"]


@pytest.mark.parametrize("n", [1, 2, 3])
def test_structure_constants_parity(n):
    """Each structure constant [X,Y]=cZ must have p(X)+p(Y)=p(Z) mod 2."""
    path = os.path.join(DATA_DIR, f"C_{n}_structure.json")
    with open(path) as f:
        data = json.load(f)
    parity = data["parity"]
    for sc in data["structure_constants"]:
        X, Y, Z = sc["X"], sc["Y"], sc["Z"]
        px = parity.get(X, -1)
        py = parity.get(Y, -1)
        pz = parity.get(Z, -1)
        assert px != -1, f"Unknown generator {X}"
        assert py != -1, f"Unknown generator {Y}"
        assert pz != -1, f"Unknown generator {Z}"
        assert (px + py) % 2 == pz, (
            f"n={n}: Parity violation [{X}({px}),{Y}({py})]={Z}({pz})"
        )


@pytest.mark.parametrize("n", [1, 2, 3])
def test_structure_constants_conform_to_spec(n):
    """Each structure constant entry must have required fields."""
    path = os.path.join(DATA_DIR, f"C_{n}_structure.json")
    with open(path) as f:
        data = json.load(f)
    for sc in data["structure_constants"]:
        assert "X" in sc and "Y" in sc and "Z" in sc and "coeff" in sc
        # coeff must be parseable as fraction
        from fractions import Fraction
        Fraction(sc["coeff"])
