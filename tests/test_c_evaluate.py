import json
import sys
from fractions import Fraction
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from C_evaluate import evaluate_schema


def test_all_plus_evaluation_matches_schema1_and_schema2():
    data_dir = Path(__file__).resolve().parents[1] / "data"
    for n in (1, 2, 3):
        gamma = json.loads((data_dir / f"C_{n}_gamma.json").read_text())
        structure = json.loads((data_dir / f"C_{n}_structure.json").read_text())
        evaluated = json.loads((data_dir / f"C_{n}_evaluated.json").read_text())
        assignment = {name: 1 for name in gamma["gb_matrix"]["parameters"]}
        expected = evaluate_schema(gamma, structure, assignment)

        assert evaluated == expected
        assert evaluated["gb_assignment"]["profile"] == "all_plus_one"
        assert len(evaluated["gb_assignment"]["values"]) == 4 * n

        base_coefficients = {}
        for entry in structure["structure_constants"]:
            key = (entry["X"], entry["Y"], entry["Z"])
            base_coefficients[key] = Fraction(entry["coeff"])
        gamma_coefficients = {}
        for entry in gamma["inhomogeneous_deformation"]["gamma_coefficients"]:
            key = (entry["X"], entry["Y"], entry["Z"])
            gamma_coefficients[key] = (
                gamma_coefficients.get(key, Fraction())
                + Fraction(entry["coeff"]) * assignment[entry["parameter"]]
            )
        for entry in evaluated["structure_constants"]:
            key = (entry["X"], entry["Y"], entry["Z"])
            assert Fraction(entry["base_coeff"]) == base_coefficients.get(key, Fraction())
            assert Fraction(entry["kappa_coeff"]) == gamma_coefficients.get(key, Fraction())
