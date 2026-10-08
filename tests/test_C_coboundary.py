import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from C_coboundary import build_coboundary


@pytest.mark.parametrize(("n", "even_count", "odd_count"), [(1, 4, 4), (2, 11, 8), (3, 22, 12)])
def test_odd_map_and_coboundary_use_only_schema1_basis(n, even_count, odd_count):
    data_dir = Path(__file__).resolve().parents[1] / "data"
    schema1_path = data_dir / f"C_{n}_structure.json"
    result = build_coboundary(schema1_path)
    schema1 = json.loads(schema1_path.read_text())
    basis = set(schema1["basis"]["even"] + schema1["basis"]["odd"])
    even = set(schema1["basis"]["even"])
    odd = set(schema1["basis"]["odd"])
    f_parameters = result["odd_linear_map"]["parameters"]
    terms = result["coboundary"]["coefficients"]

    assert len(even) == even_count
    assert len(odd) == odd_count
    assert len(f_parameters) == even_count * odd_count * 2
    assert all(
        (item["input"] in even and item["output"] in odd)
        or (item["input"] in odd and item["output"] in even)
        for item in f_parameters
    )
    assert terms
    assert all(item["X"] in basis and item["Y"] in basis and item["Z"] in basis for item in terms)
    assert all(item["parameter"] in {p["parameter"] for p in f_parameters} for item in terms)


def test_invalid_schema_path_fails_explicitly(tmp_path):
    with pytest.raises(FileNotFoundError):
        build_coboundary(tmp_path / "missing.json")
