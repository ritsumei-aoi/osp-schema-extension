"""
Unit tests for Schema 3 evaluated structure generator.
"""

import os
import json
import pytest
from src.C_evaluated_generators import build_C_evaluated_structure

def test_evaluated_json_files_exist():
    for n in [1, 2, 3]:
        filepath = f"data/C_{n}_evaluated.json"
        assert os.path.exists(filepath)
        with open(filepath) as f:
            data = json.load(f)
            assert data["schema_version"] == "5.0"
            assert data["algebra"]["n"] == n
            assert len(data["evaluation_parameters"]) == 4 * n


def test_evaluated_data_consistency():
    for n in [1, 2, 3]:
        with open(f"data/C_{n}_structure.json") as f:
            struct_data = json.load(f)
        with open(f"data/C_{n}_evaluated.json") as f:
            eval_data = json.load(f)

        base_count = len(struct_data["structure_constants"])
        eval_base_count = sum(1 for e in eval_data["evaluated_structure_constants"] if not e["is_deformed"])

        assert base_count == eval_base_count, f"Base structure constants count mismatch for n={n}"
