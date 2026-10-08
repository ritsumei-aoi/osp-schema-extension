import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from C_triviality import analyze_rank


@pytest.mark.parametrize(("n", "obstructions"), [(1, 20), (2, 84), (3, 180)])
def test_identity_obstructions_force_all_deformation_parameters_to_zero(n, obstructions):
    data_dir = Path(__file__).resolve().parents[1] / "data"
    result = analyze_rank(data_dir, n)

    assert result["identity_obstruction_terms"] == obstructions
    assert result["all_positive_identity_obstructions"] == obstructions
    assert result["all_parameters_forced_zero"]
    assert len(result["single_parameter_witnesses"]) >= 4 * n
    assert result["zero_assignment_is_coboundary"]
    assert not result["all_positive_is_coboundary"]
    assert not result["layer4_has_identity_output"]
