import os
import sys
import json
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.C_evaluated_generators import generate_c_evaluated

@pytest.mark.parametrize("n", [1, 2, 3])
def test_evaluated_schema_consistency(n):
    gamma_path = f"data/C_{n}_gamma.json"
    eval_path = f"data/C_{n}_evaluated.json"

    assert os.path.exists(gamma_path)
    assert os.path.exists(eval_path)

    with open(gamma_path, "r") as f:
        s2 = json.load(f)
    with open(eval_path, "r") as f:
        s3 = json.load(f)

    # 1. Algebra structure match
    assert s2["algebra"] == s3["algebra"]

    # 2. Check assignment covers all gb parameters
    gb_params = set(s2["gb_matrix"]["parameters"].keys())
    assigned_params = set(s3["gb_assignment"].keys())
    assert gb_params == assigned_params
