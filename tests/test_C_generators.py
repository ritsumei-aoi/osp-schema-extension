import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from C_generators import generate_structure


EXPECTED_DIMENSIONS = {
    1: (4, 4, 8),
    2: (11, 8, 19),
    3: (22, 12, 34),
}


def test_basis_dimensions_parity_and_generators():
    for rank, expected in EXPECTED_DIMENSIONS.items():
        data = generate_structure(rank)
        even, odd, total = expected
        assert data["algebra"]["dimension"] == {
            "even": even,
            "odd": odd,
            "total": total,
        }
        assert len(data["basis"]["even"]) == even
        assert len(data["basis"]["odd"]) == odd
        assert len(data["parity"]) == total
        assert set(data["parity"].values()) == {0, 1}
        assert all(data["parity"][name] == 0 for name in data["basis"]["even"])
        assert all(data["parity"][name] == 1 for name in data["basis"]["odd"])
        assert data["oscillator_generators"]["fermions"]["labels"] == [
            "a_1_p",
            "a_1_m",
        ]
        assert len(data["oscillator_generators"]["bosons"]["labels"]) == 2 * rank
        assert set(data["generator_realization"]["realizations"]) == set(
            data["parity"]
        )


def test_generated_json_matches_schema_and_generator():
    for rank in EXPECTED_DIMENSIONS:
        path = ROOT / "data" / f"C_{rank}_structure.json"
        with path.open(encoding="utf-8") as source:
            data = json.load(source)
        assert data == generate_structure(rank)
        assert data["algebra"]["family"] == "C"
        assert data["algebra"]["m"] == 1
        assert set(data["central_elements"]) == {"kappa", "K"}
        assert "supplementary_fermion" not in data["oscillator_generators"]
        assert all(
            item["X"] in data["parity"]
            and item["Y"] in data["parity"]
            and item["Z"] in data["parity"]
            for item in data["structure_constants"]
        )
