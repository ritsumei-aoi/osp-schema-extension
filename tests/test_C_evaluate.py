import json
import sys
from pathlib import Path

import sympy as sp

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from C_evaluate import evaluate_gamma


def test_evaluated_layer_matches_symbolic_gamma():
    for rank in (1, 2, 3):
        gamma_path = ROOT / "data" / f"C_{rank}_gamma.json"
        evaluated_path = ROOT / "data" / f"C_{rank}_evaluated.json"
        gamma_data = json.loads(gamma_path.read_text(encoding="utf-8"))
        evaluated_data = json.loads(evaluated_path.read_text(encoding="utf-8"))
        layer = evaluated_data.pop("evaluated_deformation")
        assert evaluated_data == gamma_data

        symbolic = gamma_data["inhomogeneous_deformation"]["gamma_coefficients"]
        assignment = layer["gb_assignment"]
        assert len(assignment) == 4 * rank
        assert set(assignment.values()) == {1}
        expected = []
        symbols = {sp.Symbol(parameter): value for parameter, value in assignment.items()}
        for entry in symbolic:
            coefficient = sp.simplify(sp.sympify(entry["coeff"]).subs(symbols))
            if coefficient:
                expected.append({**entry, "coeff": str(coefficient)})
        assert layer["evaluated_coefficients"] == expected
        assert {
            **evaluated_data,
            "evaluated_deformation": layer,
        } == evaluate_gamma(gamma_data, assignment)
