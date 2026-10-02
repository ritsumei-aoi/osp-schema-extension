import json
import sys
from fractions import Fraction
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from C_coboundary import generate_coboundary_schema


def test_coboundary_schema_matches_layer1_basis_and_odd_map_dimensions():
    data_dir = Path(__file__).resolve().parents[1] / "data"
    for n in (1, 2, 3):
        path = data_dir / f"C_{n}_coboundary.json"
        result = generate_coboundary_schema(
            data_dir / f"C_{n}_gamma.json",
            data_dir / f"C_{n}_structure.json",
        )
        stored = json.loads(path.read_text())
        structure = json.loads((data_dir / f"C_{n}_structure.json").read_text())
        assert stored == result
        assert stored["basis"]["even"] == structure["basis"]["even"]
        assert stored["basis"]["odd"] == structure["basis"]["odd"]
        expected_count = 2 * len(structure["basis"]["even"]) * len(structure["basis"]["odd"])
        assert stored["linear_map"]["parameter_count"] == expected_count
        assert len(stored["linear_map"]["parameters"]) == expected_count


def test_coboundary_coefficients_use_valid_basis_and_have_odd_parity():
    data_dir = Path(__file__).resolve().parents[1] / "data"
    for n in (1, 2, 3):
        result = json.loads((data_dir / f"C_{n}_coboundary.json").read_text())
        basis = set(result["basis"]["even"] + result["basis"]["odd"])
        parity = {
            **{name: 0 for name in result["basis"]["even"]},
            **{name: 1 for name in result["basis"]["odd"]},
        }
        parameters = {
            entry["label"] for entry in result["linear_map"]["parameters"]
        }
        seen = set()
        for entry in result["coboundary"]["coboundary_coefficients"]:
            key = (entry["X"], entry["Y"], entry["Z"], entry["parameter"])
            assert key not in seen
            seen.add(key)
            assert entry["X"] in basis and entry["Y"] in basis and entry["Z"] in basis
            assert entry["parameter"] in parameters
            assert parity[entry["Z"]] == (parity[entry["X"]] + parity[entry["Y"]] + 1) % 2
            assert Fraction(entry["coeff"]) != 0


def test_coboundary_is_graded_skew_symmetric():
    data_dir = Path(__file__).resolve().parents[1] / "data"
    for n in (1, 2, 3):
        result = json.loads((data_dir / f"C_{n}_coboundary.json").read_text())
        basis = result["basis"]["even"] + result["basis"]["odd"]
        indices = {name: index for index, name in enumerate(basis)}
        parity = {
            **{name: 0 for name in result["basis"]["even"]},
            **{name: 1 for name in result["basis"]["odd"]},
        }
        constants = {}
        for entry in result["coboundary"]["coboundary_coefficients"]:
            key = (entry["X"], entry["Y"])
            constants.setdefault(key, {})[(entry["Z"], entry["parameter"])] = Fraction(
                entry["coeff"]
            )

        def coboundary(x, y):
            if indices[x] <= indices[y]:
                return constants.get((x, y), {})
            sign = -1 if parity[x] * parity[y] else 1
            return {
                term: -sign * coeff
                for term, coeff in constants.get((y, x), {}).items()
            }

        for x in basis:
            for y in basis:
                combined = dict(coboundary(x, y))
                sign = -1 if parity[x] * parity[y] else 1
                for term, coeff in coboundary(y, x).items():
                    combined[term] = combined.get(term, Fraction()) + sign * coeff
                assert not any(combined.values()), (n, x, y, combined)
