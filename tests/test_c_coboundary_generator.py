import json
from copy import deepcopy
from fractions import Fraction
from functools import lru_cache
from pathlib import Path

import pytest

from src.C_coboundary_generator import build_coboundary_schema

ROOT = Path(__file__).resolve().parents[1]


@lru_cache(maxsize=None)
def coboundary_for(n):
    return build_coboundary_schema(n)


@pytest.mark.parametrize("n", [1, 2, 3])
def test_coboundary_schema_matches_layer_one_basis(n):
    schema = coboundary_for(n)
    stored_path = ROOT / "data" / f"C_{n}_coboundary.json"
    stored = json.loads(stored_path.read_text(encoding="utf-8"))
    expected = deepcopy(schema)
    stored["metadata"].pop("generation_date")
    expected["metadata"].pop("generation_date")
    assert stored == expected

    source = json.loads(
        (ROOT / "data" / f"C_{n}_structure.json").read_text(encoding="utf-8")
    )
    basis = source["basis"]["odd"] + source["basis"]["even"]
    operator = schema["coboundary_operator"]
    assert schema["source_structure_schema"] == f"C_{n}_structure.json"
    assert operator["basis_order"] == basis
    expected_map_count = (
        2 * len(source["basis"]["even"]) * len(source["basis"]["odd"])
    )
    assert len(operator["f_coefficients"]) == expected_map_count

    f_symbols = set()
    for entry in operator["f_coefficients"]:
        assert entry["input"] in basis and entry["output"] in basis
        assert source["parity"][entry["input"]] != source["parity"][entry["output"]]
        f_symbols.add(entry["symbol"])

    seen = set()
    for entry in schema["coboundary_coefficients"]:
        assert entry["X"] in basis and entry["Y"] in basis and entry["Z"] in basis
        assert entry["phi"] in f_symbols
        assert Fraction(entry["coeff"])
        assert source["parity"][entry["Z"]] == (
            source["parity"][entry["X"]] + source["parity"][entry["Y"]] + 1
        ) % 2
        key = (entry["X"], entry["Y"], entry["Z"], entry["phi"])
        assert key not in seen
        seen.add(key)
