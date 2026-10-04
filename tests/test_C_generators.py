import os
import json
import pytest
from src.C_generators import (
    get_C_generators,
    generate_structure_constants,
    build_schema_1_json,
    generate_and_save_all
)


@pytest.mark.parametrize("n,expected_even,expected_odd,expected_total", [
    (1, 4, 4, 8),
    (2, 11, 8, 19),
    (3, 22, 12, 34),
])
def test_generator_counts_and_dimensions(n, expected_even, expected_odd, expected_total):
    even_basis, odd_basis, parity, realizations, frappat_forms = get_C_generators(n)
    assert len(even_basis) == expected_even
    assert len(odd_basis) == expected_odd
    assert len(even_basis) + len(odd_basis) == expected_total

    # Verify parity consistency
    for g in even_basis:
        assert parity[g] == 0
    for g in odd_basis:
        assert parity[g] == 1


@pytest.mark.parametrize("n", [1, 2, 3])
def test_graded_antisymmetry(n):
    even_basis, odd_basis, parity, realizations, _ = get_C_generators(n)
    sc = generate_structure_constants(n)

    # Convert to bracket lookup dict: (X, Y, Z) -> Fraction
    from fractions import Fraction
    sc_map = {}
    for entry in sc:
        sc_map[(entry["X"], entry["Y"], entry["Z"])] = Fraction(entry["coeff"])

    all_basis = odd_basis + even_basis
    for x in all_basis:
        px = parity[x]
        for y in all_basis:
            py = parity[y]
            sign = -1 if (px == 1 and py == 1) else 1
            for z in all_basis:
                xy_coeff = sc_map.get((x, y, z), Fraction(0))
                yx_coeff = sc_map.get((y, x, z), Fraction(0))
                # Graded antisymmetry: [X, Y} = - (-1)^{px*py} [Y, X}
                expected_yx = - Fraction(sign) * xy_coeff
                assert yx_coeff == expected_yx, f"Graded antisymmetry failed for [{x}, {y}] vs [{y}, {x}] on {z}"


@pytest.mark.parametrize("n", [1, 2, 3])
def test_graded_jacobi_identity(n):
    even_basis, odd_basis, parity, realizations, _ = get_C_generators(n)
    sc = generate_structure_constants(n)
    from fractions import Fraction
    sc_map = {}
    for entry in sc:
        sc_map[(entry["X"], entry["Y"], entry["Z"])] = Fraction(entry["coeff"])

    all_basis = odd_basis + even_basis

    def bracket(x, y):
        # returns dict Z -> Fraction
        res = {}
        for z in all_basis:
            c = sc_map.get((x, y, z), Fraction(0))
            if c != 0:
                res[z] = c
        return res

    def bracket_linear(dict_x, y, px):
        # [sum c_x X, y}
        res = {}
        for x, cx in dict_x.items():
            b = bracket(x, y)
            for z, cz in b.items():
                res[z] = res.get(z, Fraction(0)) + cx * cz
        return res

    def bracket_linear_right(x, dict_y):
        # [x, sum c_y Y}
        res = {}
        for y, cy in dict_y.items():
            b = bracket(x, y)
            for z, cz in b.items():
                res[z] = res.get(z, Fraction(0)) + cy * cz
        return res

    # Graded Jacobi: (-1)^{p(X)p(Z)} [X, [Y, Z}} + (-1)^{p(Y)p(X)} [Y, [Z, X}} + (-1)^{p(Z)p(Y)} [Z, [X, Y}} = 0
    # Test a representative sample or all for n=1, 2
    basis_to_test = all_basis if n <= 2 else all_basis[:15]
    for x in basis_to_test:
        px = parity[x]
        for y in basis_to_test:
            py = parity[y]
            for z in basis_to_test:
                pz = parity[z]

                # Term 1: (-1)^{px*pz} [X, [Y, Z}}
                yz = bracket(y, z)
                term1 = bracket_linear_right(x, yz)
                sign1 = -1 if (px * pz) % 2 == 1 else 1

                # Term 2: (-1)^{py*px} [Y, [Z, X}}
                zx = bracket(z, x)
                term2 = bracket_linear_right(y, zx)
                sign2 = -1 if (py * px) % 2 == 1 else 1

                # Term 3: (-1)^{pz*py} [Z, [X, Y}}
                xy = bracket(x, y)
                term3 = bracket_linear_right(z, xy)
                sign3 = -1 if (pz * py) % 2 == 1 else 1

                total = {}
                for k, v in term1.items():
                    total[k] = total.get(k, Fraction(0)) + sign1 * v
                for k, v in term2.items():
                    total[k] = total.get(k, Fraction(0)) + sign2 * v
                for k, v in term3.items():
                    total[k] = total.get(k, Fraction(0)) + sign3 * v

                for k, v in total.items():
                    assert v == 0, f"Graded Jacobi identity failed for ({x}, {y}, {z}) on {k}: {v}"


def test_schema_generation():
    generate_and_save_all("data")
    for n in [1, 2, 3]:
        file_path = f"data/C_{n}_structure.json"
        assert os.path.exists(file_path)
        with open(file_path, "r") as f:
            data = json.load(f)
        assert data["schema_version"] == "5.0"
        assert data["algebra"]["family"] == "C"
        assert data["algebra"]["m"] == 1
        assert data["algebra"]["n"] == n
        assert "central_elements" in data
        assert "oscillator_generators" in data
        assert "oscillator_relations" in data
        assert "basis" in data
        assert "parity" in data
        assert "generator_realization" in data
        assert "structure_constants" in data
