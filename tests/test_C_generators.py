"""Unit tests for C(n+1) generator script, basis dimensions, parities, and Schema 1 JSON."""

import json
import os
import pytest
from src.C_generators import (
    build_basis,
    build_generator_realizations,
    compute_structure_constants,
    generate_all_schema_1
)

@pytest.mark.parametrize("n,expected_even,expected_odd,expected_total", [
    (1, 4, 4, 8),
    (2, 11, 8, 19),
    (3, 22, 12, 34)
])
def test_generator_counts(n, expected_even, expected_odd, expected_total):
    even_basis, odd_basis = build_basis(n)
    assert len(even_basis) == expected_even
    assert len(odd_basis) == expected_odd
    assert len(even_basis) + len(odd_basis) == expected_total

@pytest.mark.parametrize("n", [1, 2, 3])
def test_generator_parities(n):
    even_basis, odd_basis = build_basis(n)
    polys, parities, realizations = build_generator_realizations(n)
    
    for gen in even_basis:
        assert parities[gen] == 0, f"Even generator {gen} has incorrect parity {parities[gen]}"
    for gen in odd_basis:
        assert parities[gen] == 1, f"Odd generator {gen} has incorrect parity {parities[gen]}"

@pytest.mark.parametrize("n", [1, 2, 3])
def test_structure_constants_parity_conservation(n):
    sc_list, schema_1 = compute_structure_constants(n)
    parities = schema_1["parity"]
    
    for entry in sc_list:
        x, y, z = entry["X"], entry["Y"], entry["Z"]
        p_x = parities[x]
        p_y = parities[y]
        p_z = parities[z]
        assert (p_x + p_y) % 2 == p_z, (
            f"Parity violation in [{x}, {y}] = ... + {entry['coeff']} * {z}: "
            f"p({x})={p_x}, p({y})={p_y}, p({z})={p_z}"
        )

@pytest.mark.parametrize("n", [1, 2, 3])
def test_graded_antisymmetry(n):
    sc_list, schema_1 = compute_structure_constants(n)
    parities = schema_1["parity"]
    
    from fractions import Fraction
    sc_dict = {}
    for entry in sc_list:
        sc_dict[(entry["X"], entry["Y"], entry["Z"])] = Fraction(entry["coeff"])
        
    basis = schema_1["basis"]["even"] + schema_1["basis"]["odd"]
    for x in basis:
        for y in basis:
            p_xy = (-1) ** (parities[x] * parities[y])
            for z in basis:
                c_xy = sc_dict.get((x, y, z), Fraction(0))
                c_yx = sc_dict.get((y, x, z), Fraction(0))
                # [X, Y} = - (-1)^{p(X)p(Y)} [Y, X}
                assert c_xy == - p_xy * c_yx, (
                    f"Graded antisymmetry violation for [{x}, {y}] vs [{y}, {x}] on {z}: "
                    f"c_xy={c_xy}, c_yx={c_yx}, p_xy={p_xy}"
                )

@pytest.mark.parametrize("n", [1, 2, 3])
def test_schema_1_file_conformance(n):
    filepath = os.path.join("data", f"C_{n}_structure.json")
    assert os.path.exists(filepath), f"Missing data file {filepath}"
    
    with open(filepath, "r") as f:
        data = json.load(f)
        
    assert data["schema_version"] == "5.0"
    assert data["algebra"]["family"] == "C"
    assert data["algebra"]["m"] == 1
    assert data["algebra"]["n"] == n
    assert data["algebra"]["cartan_type"] == f"C({n+1})"
    assert "kappa" in data["central_elements"]
    assert "K" in data["central_elements"]
    assert data["central_elements"]["kappa"]["parity"] == 1
    assert data["central_elements"]["K"]["parity"] == 0
    assert "fermions" in data["oscillator_generators"]
    assert "bosons" in data["oscillator_generators"]
    assert len(data["oscillator_generators"]["fermions"]["labels"]) == 2
    assert len(data["oscillator_generators"]["bosons"]["labels"]) == 2 * n

def test_super_jacobi_identity_all_ranks():
    from src.verify_C_structure import verify_all
    assert verify_all("data") is True

@pytest.mark.parametrize("n", [1, 2, 3])
def test_schema_2_consistency(n):
    path_s1 = os.path.join("data", f"C_{n}_structure.json")
    path_s2 = os.path.join("data", f"C_{n}_gamma.json")
    assert os.path.exists(path_s2), f"Missing {path_s2}"
    
    with open(path_s1, "r") as f1, open(path_s2, "r") as f2:
        d1 = json.load(f1)
        d2 = json.load(f2)
        
    assert d2["schema_version"] == "5.0"
    assert d2["algebra"]["family"] == "C"
    assert d2["algebra"]["n"] == n
    assert d2["basis"]["even"] == d1["basis"]["even"]
    assert d2["basis"]["odd"] == d1["basis"]["odd"]
    assert d2["parity"] == d1["parity"]
    assert d2["gb_matrix"]["dimensions"] == [2, 2 * n]
    assert len(d2["gb_matrix"]["matrix"]) == 2
    assert len(d2["gb_matrix"]["matrix"][0]) == 2 * n

@pytest.mark.parametrize("n", [1, 2, 3])
def test_gamma_graded_antisymmetry(n):
    from fractions import Fraction
    path_s2 = os.path.join("data", f"C_{n}_gamma.json")
    with open(path_s2, "r") as f:
        data = json.load(f)
        
    parities = data["parity"]
    gamma_dict = {}
    for entry in data["inhomogeneous_deformation"]["gamma_coefficients"]:
        key = (entry["X"], entry["Y"], entry["Z"], entry["gb_param"])
        gamma_dict[key] = Fraction(entry["coeff"])
        
    basis = data["basis"]["even"] + data["basis"]["odd"]
    # Verify antisymmetry for all non-zero entries
    for (x, y, z, param), c_xy in gamma_dict.items():
        p_xy = (-1) ** (parities[x] * parities[y])
        c_yx = gamma_dict.get((y, x, z, param), Fraction(0))
        assert c_xy == - p_xy * c_yx, (
            f"Gamma graded antisymmetry violated for [{x}, {y}] vs [{y}, {x}] on {z} with {param}: "
            f"c_xy={c_xy}, c_yx={c_yx}"
        )

@pytest.mark.parametrize("n", [1, 2, 3])
def test_schema_3_consistency(n):
    path_s2 = os.path.join("data", f"C_{n}_gamma.json")
    path_s3 = os.path.join("data", f"C_{n}_evaluated.json")
    assert os.path.exists(path_s3), f"Missing {path_s3}"
    
    with open(path_s2, "r") as f2, open(path_s3, "r") as f3:
        d2 = json.load(f2)
        d3 = json.load(f3)
        
    assert d3["schema_version"] == "5.0"
    assert d3["layer"] == 3
    assert d3["algebra"]["family"] == "C"
    assert d3["algebra"]["n"] == n
    assert d3["parameter_assignment"]["profile_name"] == "all_ones"
    assert len(d3["parameter_assignment"]["values"]) == 4 * n
    
    # Check that substitution of gb=1 matches evaluated_deformation
    from fractions import Fraction
    from collections import defaultdict
    expected_eval = defaultdict(Fraction)
    for entry in d2["inhomogeneous_deformation"]["gamma_coefficients"]:
        key = (entry["X"], entry["Y"], entry["Z"])
        expected_eval[key] += Fraction(entry["coeff"]) * 1
        
    actual_eval = {}
    for entry in d3["evaluated_deformation"]["gamma_coefficients"]:
        key = (entry["X"], entry["Y"], entry["Z"])
        actual_eval[key] = Fraction(entry["coeff"])
        
    for k, v in expected_eval.items():
        if v != 0:
            assert actual_eval.get(k) == v, f"Evaluated coefficient mismatch at {k}: expected {v}, got {actual_eval.get(k)}"

@pytest.mark.parametrize("n", [1, 2, 3])
def test_schema_4_consistency(n):
    path_s4 = os.path.join("data", f"C_{n}_coboundary.json")
    assert os.path.exists(path_s4), f"Missing {path_s4}"
    
    with open(path_s4, "r") as f4:
        d4 = json.load(f4)
        
    assert d4["schema_version"] == "5.0"
    assert d4["layer"] == 4
    assert d4["algebra"]["family"] == "C"
    assert d4["algebra"]["n"] == n
    
    # Check that f strictly reverses parity
    parities = d4["parity"]
    map_table = d4["odd_linear_map_f"]["map_table"]
    for src_gen, targets in map_table.items():
        p_src = parities[src_gen]
        for tgt_gen in targets.keys():
            p_tgt = parities[tgt_gen]
            assert p_tgt == 1 - p_src, f"Parity reversal failure: f({src_gen}) has component {tgt_gen}"

@pytest.mark.parametrize("n", [1, 2, 3])
def test_coboundary_graded_antisymmetry(n):
    from fractions import Fraction
    path_s4 = os.path.join("data", f"C_{n}_coboundary.json")
    with open(path_s4, "r") as f:
        data = json.load(f)
        
    parities = data["parity"]
    cb_dict = {}
    for entry in data["coboundary_operator"]["coboundary_coefficients"]:
        key = (entry["X"], entry["Y"], entry["Z"])
        cb_dict[key] = Fraction(entry["coeff"])
        
    # Verify graded antisymmetry: delta f(X, Y) = - (-1)^{px py} delta f(Y, X)
    for (x, y, z), c_xy in cb_dict.items():
        p_xy = (-1) ** (parities[x] * parities[y])
        c_yx = cb_dict.get((y, x, z), Fraction(0))
        assert c_xy == - p_xy * c_yx, (
            f"Coboundary graded antisymmetry violated for ({x}, {y}) on {z}: "
            f"c_xy={c_xy}, c_yx={c_yx}"
        )

@pytest.mark.parametrize("n", [1, 2, 3])
def test_triviality_analysis_execution(n):
    from src.analyze_triviality import analyze_cohomological_triviality
    res = analyze_cohomological_triviality(n, "data")
    assert res["intersection_dimension"] == 0
    assert res["trivial_only_if_gb_zero"] is True

