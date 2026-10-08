import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from C_coboundary import generate_coboundary


def test_coboundary_map_and_evaluated_layer_consistency():
    for rank in (1, 2, 3):
        evaluated_path = ROOT / "data" / f"C_{rank}_evaluated.json"
        coboundary_path = ROOT / "data" / f"C_{rank}_coboundary.json"
        evaluated = json.loads(evaluated_path.read_text(encoding="utf-8"))
        coboundary = json.loads(coboundary_path.read_text(encoding="utf-8"))
        layer = coboundary.pop("coboundary")
        assert coboundary == evaluated
        assert layer["odd_map"] == [
            {
                "source": "H_eps",
                "target": "E_eps1_del1_pp",
                "coeff": "1",
            },
            {
                "source": "E_eps1_del1_pp",
                "target": "H_eps",
                "coeff": "1",
            },
        ]
        for entry in layer["odd_map"]:
            source_parity = evaluated["parity"][entry["source"]]
            target_parity = evaluated["parity"][entry["target"]]
            assert source_parity != target_parity
        assert layer["coboundary_coefficients"]
        assert all(
            entry["X"] in evaluated["parity"]
            and entry["Y"] in evaluated["parity"]
            and entry["Z"] in evaluated["parity"]
            for entry in layer["coboundary_coefficients"]
        )
        assert {
            **coboundary,
            "coboundary": layer,
        } == generate_coboundary(evaluated)
