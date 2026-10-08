import json
from copy import deepcopy
from functools import lru_cache
from pathlib import Path

import pytest

from src.C_gamma_generator import build_gamma_schema

ROOT = Path(__file__).resolve().parents[1]


@lru_cache(maxsize=None)
def gamma_schema_for(n):
    return build_gamma_schema(n)


@pytest.mark.parametrize("n", [1, 2, 3])
def test_gamma_schema_matches_source_basis_and_generated_data(n):
    schema = gamma_schema_for(n)
    generated_path = ROOT / "data" / f"C_{n}_gamma.json"
    source_path = ROOT / "data" / f"C_{n}_structure.json"
    generated = json.loads(generated_path.read_text(encoding="utf-8"))
    source = json.loads(source_path.read_text(encoding="utf-8"))
    expected = deepcopy(schema)
    generated["metadata"].pop("generation_date")
    expected["metadata"].pop("generation_date")
    assert generated == expected

    assert schema["source_schema"] == source_path.name
    assert schema["algebra"]["n"] == source["algebra"]["n"] == n
    assert schema["consistency"]["undeformed_bracket_pairs_verified"] == (
        (len(source["basis"]["even"]) + len(source["basis"]["odd"]))
        * (len(source["basis"]["even"]) + len(source["basis"]["odd"]) + 1)
        // 2
    )
    assert schema["gb_matrix"]["shape"] == [2, 2 * n]
    assert len(schema["gb_matrix"]["parameters"]) == 4 * n
    assert len(schema["inhomogeneous_deformation"]["exchange_relations"]) == 4 * n

    valid_outputs = set(source["basis"]["even"] + source["basis"]["odd"]) | {"K"}
    valid_parameters = {item["label"] for item in schema["gb_matrix"]["parameters"]}
    order = {
        label: index
        for index, label in enumerate(source["basis"]["odd"] + source["basis"]["even"])
    }
    seen = set()
    for entry in schema["inhomogeneous_deformation"]["gamma_coefficients"]:
        assert entry["X"] in order and entry["Y"] in order
        assert order[entry["X"]] <= order[entry["Y"]]
        assert entry["Z"] in valid_outputs
        assert entry["parameter"] in valid_parameters
        assert entry["coeff"]
        key = (entry["X"], entry["Y"], entry["Z"], entry["parameter"])
        assert key not in seen
        seen.add(key)
