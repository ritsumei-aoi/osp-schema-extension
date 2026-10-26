import pytest
from fractions import Fraction
from run_full_validation import get_generators, build_schema1_json, graded_commutator

@pytest.mark.parametrize("n, expected_even, expected_odd, expected_total", [
    (1, 4, 4, 8),
    (2, 11, 8, 19),
    (3, 22, 12, 34)
])
def test_generator_counts(n, expected_even, expected_odd, expected_total):
    eb, ob, real, par = get_generators(n)
    assert len(eb) == expected_even
    assert len(ob) == expected_odd
    assert len(eb) + len(ob) == expected_total

@pytest.mark.parametrize("n", [1, 2, 3])
def test_generator_parities(n):
    eb, ob, real, par = get_generators(n)
    for g in eb:
        assert par[g] == 0
    for g in ob:
        assert par[g] == 1

@pytest.mark.parametrize("n", [1, 2, 3])
def test_schema_keys(n):
    schema = build_schema1_json(n)
    expected_keys = {
        "schema_version", "algebra", "central_elements",
        "oscillator_generators", "oscillator_relations", "basis",
        "parity", "generator_realization", "structure_constants", "metadata"
    }
    assert set(schema.keys()) == expected_keys
    assert schema["schema_version"] == "5.0"
    assert schema["algebra"]["family"] == "C"
    assert schema["algebra"]["m"] == 1
    assert schema["algebra"]["n"] == n
    assert "kappa" in schema["central_elements"]
    assert "K" in schema["central_elements"]
    assert "fermions" in schema["oscillator_generators"]
    assert "bosons" in schema["oscillator_generators"]
    assert schema["oscillator_generators"]["fermions"]["labels"] == ["a_1_p", "a_1_m"]

@pytest.mark.parametrize("n", [1, 2, 3])
def test_graded_skew_symmetry(n):
    schema = build_schema1_json(n)
    parity = schema["parity"]
    brackets = schema["structure_constants"]
    
    b_map = {}
    for entry in brackets:
        b_map[(entry["X"], entry["Y"], entry["Z"])] = Fraction(entry["coeff"])

    for (X, Y, Z), coeff in b_map.items():
        pX = parity[X]
        pY = parity[Y]
        sign = -1 if (pX * pY) % 2 == 1 else 1
        opp_coeff = b_map.get((Y, X, Z), Fraction(0, 1))
        assert opp_coeff == -sign * coeff
