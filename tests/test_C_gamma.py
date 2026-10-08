import json
import sys
from pathlib import Path

import sympy as sp

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from C_gamma import generate_gamma


def test_gamma_schema_and_schema1_consistency():
    for rank in (1, 2, 3):
        structure_path = ROOT / "data" / f"C_{rank}_structure.json"
        gamma_path = ROOT / "data" / f"C_{rank}_gamma.json"
        structure = json.loads(structure_path.read_text(encoding="utf-8"))
        gamma_file = json.loads(gamma_path.read_text(encoding="utf-8"))
        gamma_data = dict(gamma_file)

        deformation = gamma_data.pop("inhomogeneous_deformation")
        assert gamma_data == structure
        matrix = deformation["gb_matrix"]
        assert matrix["rows"] == ["a_1_p", "a_1_m"]
        assert len(matrix["columns"]) == 2 * rank
        assert len(matrix["values"]) == 2
        parameters = {
            value for row in matrix["values"] for value in row
        }
        assert len(parameters) == 4 * rank
        assert deformation["parameter_parity"] == 1

        allowed_outputs = set(structure["parity"]) | {"K"}
        for entry in deformation["gamma_coefficients"]:
            assert entry["X"] in structure["parity"]
            assert entry["Y"] in structure["parity"]
            assert entry["Z"] in allowed_outputs
            symbols = {
                str(symbol)
                for symbol in sp.sympify(entry["coeff"], evaluate=False).free_symbols
            }
            assert symbols <= parameters

        assert gamma_file == generate_gamma(rank, structure)
