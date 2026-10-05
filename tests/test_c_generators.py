import os
import json
import pytest
from fractions import Fraction
from src.C_generators import (
    get_basis,
    get_parity,
    get_generator_realizations,
    compute_structure_constants,
    generate_structure_json,
    save_structure_json
)


@pytest.mark.parametrize("n, expected_even, expected_odd, expected_total", [
    (1, 4, 4, 8),
    (2, 11, 8, 19),
    (3, 22, 12, 34),
])
def test_basis_dimensions(n, expected_even, expected_odd, expected_total):
    basis = get_basis(n)
    even_gens = basis["even"]
    odd_gens = basis["odd"]
    
    assert len(even_gens) == expected_even
    assert len(odd_gens) == expected_odd
    assert len(even_gens) + len(odd_gens) == expected_total
    # Ensure no duplicates
    assert len(set(even_gens)) == expected_even
    assert len(set(odd_gens)) == expected_odd
    assert len(set(even_gens).intersection(set(odd_gens))) == 0


@pytest.mark.parametrize("n", [1, 2, 3])
def test_parity_consistency(n):
    basis = get_basis(n)
    parity = get_parity(n)
    for g in basis["even"]:
        assert parity[g] == 0
    for g in basis["odd"]:
        assert parity[g] == 1


@pytest.mark.parametrize("n", [1, 2])
def test_graded_antisymmetry(n):
    constants = compute_structure_constants(n)
    parity = get_parity(n)
    
    bracket_dict = {}
    for entry in constants:
        x, y, z = entry["X"], entry["Y"], entry["Z"]
        bracket_dict[(x, y, z)] = Fraction(entry["coeff"])
        
    basis = get_basis(n)
    all_gens = basis["even"] + basis["odd"]
    
    for x in all_gens:
        px = parity[x]
        for y in all_gens:
            py = parity[y]
            sign = -1 if (px * py) % 2 == 1 else 1
            for z in all_gens:
                c_xy_z = bracket_dict.get((x, y, z), Fraction(0))
                c_yx_z = bracket_dict.get((y, x, z), Fraction(0))
                # [X, Y} = - (-1)^{px py} [Y, X}
                assert c_xy_z == -sign * c_yx_z


@pytest.mark.parametrize("n", [1, 2])
def test_graded_jacobi_identity_n1(n):
    """
    Test Jacobi superidentity on C(2):
    [X, [Y, Z}} = [[X, Y}, Z} + (-1)^(px py) [Y, [X, Z}}
    """
    constants = compute_structure_constants(n)
    parity = get_parity(n)
    
    bracket_map = {}
    for entry in constants:
        x, y, z = entry["X"], entry["Y"], entry["Z"]
        if (x, y) not in bracket_map:
            bracket_map[(x, y)] = {}
        bracket_map[(x, y)][z] = Fraction(entry["coeff"])
        
    def br(u, v):
        return bracket_map.get((u, v), {})
        
    def br_lin(lin_u, v):
        # [sum c_i u_i, v]
        res = {}
        for u_i, c_i in lin_u.items():
            for w, coeff in br(u_i, v).items():
                res[w] = res.get(w, Fraction(0)) + c_i * coeff
        return {k: v_c for k, v_c in res.items() if v_c != 0}

    def br_lin_right(u, lin_v):
        # [u, sum c_j v_j]
        res = {}
        for v_j, c_j in lin_v.items():
            for w, coeff in br(u, v_j).items():
                res[w] = res.get(w, Fraction(0)) + c_j * coeff
        return {k: v_c for k, v_c in res.items() if v_c != 0}

    basis = get_basis(n)
    all_gens = basis["even"] + basis["odd"]
    
    for x in all_gens:
        px = parity[x]
        for y in all_gens:
            py = parity[y]
            sign_xy = -1 if (px * py) % 2 == 1 else 1
            for z in all_gens:
                # Term 1: [X, [Y, Z}}
                term1 = br_lin_right(x, br(y, z))
                # Term 2: [[X, Y}, Z}
                term2 = br_lin(br(x, y), z)
                # Term 3: (-1)^(px py) [Y, [X, Z}}
                term3_raw = br_lin_right(y, br(x, z))
                term3 = {k: sign_xy * v for k, v in term3_raw.items()}
                
                # Check term1 == term2 + term3
                rhs = dict(term2)
                for k, v in term3.items():
                    rhs[k] = rhs.get(k, Fraction(0)) + v
                rhs = {k: v for k, v in rhs.items() if v != 0}
                
                assert term1 == rhs, f"Jacobi failed for ({x}, {y}, {z}): LHS={term1}, RHS={rhs}"


def test_schema_json_generation_and_conformance(tmp_path):
    data_dir = tmp_path / "data"
    for n in [1, 2, 3]:
        filepath = save_structure_json(n, output_dir=str(data_dir))
        assert os.path.exists(filepath)
        
        with open(filepath, "r") as f:
            data = json.load(f)
            
        assert data["schema_version"] == "5.0"
        assert data["algebra"]["family"] == "C"
        assert data["algebra"]["m"] == 1
        assert data["algebra"]["n"] == n
        assert data["algebra"]["dimension"]["even"] == 2 * n**2 + n + 1
        assert data["algebra"]["dimension"]["odd"] == 4 * n
        assert "central_elements" in data
        assert "kappa" in data["central_elements"]
        assert "K" in data["central_elements"]
        assert len(data["basis"]["even"]) == 2 * n**2 + n + 1
        assert len(data["basis"]["odd"]) == 4 * n
        assert len(data["structure_constants"]) > 0
