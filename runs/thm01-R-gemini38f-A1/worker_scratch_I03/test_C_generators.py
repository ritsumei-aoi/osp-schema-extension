import pytest
from fractions import Fraction
import sys
from pathlib import Path

# Add scratch to sys.path
sys.path.append(str(Path(__file__).parent))
import C_generators as cg

@pytest.mark.parametrize("n, expected_even, expected_odd, expected_total", [
    (1, 4, 4, 8),
    (2, 11, 8, 19),
    (3, 22, 12, 34),
])
def test_generator_counts_and_dimensions(n, expected_even, expected_odd, expected_total):
    even_basis, odd_basis = cg.get_basis(n)
    assert len(even_basis) == expected_even
    assert len(odd_basis) == expected_odd
    assert len(even_basis) + len(odd_basis) == expected_total

    gens, parities, realizations = cg.get_generator_polys_and_realizations(n)
    assert len(gens) == expected_total
    assert len(parities) == expected_total
    assert len(realizations) == expected_total

    # Verify parities
    for g in even_basis:
        assert parities[g] == 0
    for g in odd_basis:
        assert parities[g] == 1


@pytest.mark.parametrize("n", [1, 2, 3])
def test_pbw_ordering_structure(n):
    even_basis, odd_basis = cg.get_basis(n)
    # Check odd sector ordering: pp, pm, mp, mm
    pp_list = [f"E_eps1_del{k}_pp" for k in range(1, n + 1)]
    pm_list = [f"E_eps1_del{k}_pm" for k in range(1, n + 1)]
    mp_list = [f"E_eps1_del{k}_mp" for k in range(1, n + 1)]
    mm_list = [f"E_eps1_del{k}_mm" for k in range(1, n + 1)]
    assert odd_basis == pp_list + pm_list + mp_list + mm_list

    # Check even sector ordering starts with Cartan
    cartan = [f"H_{k}" for k in range(1, n + 2)]
    assert even_basis[:len(cartan)] == cartan


@pytest.mark.parametrize("n, expected_bracket_count", [
    (1, 40),
    (2, 198),
    (3, 528),
])
def test_structure_constants_and_antisymmetry(n, expected_bracket_count):
    schema = cg.build_schema1_json(n)
    sc = schema["structure_constants"]
    par = schema["parity"]

    assert len(sc) == expected_bracket_count

    sc_dict = {}
    for entry in sc:
        sc_dict[(entry["X"], entry["Y"], entry["Z"])] = Fraction(entry["coeff"])

    # Graded antisymmetry
    for (x, y, z), coeff in sc_dict.items():
        px, py = par[x], par[y]
        expected_other = - (-1)**(px * py) * coeff
        actual_other = sc_dict.get((y, x, z), Fraction(0))
        assert actual_other == expected_other, f"Antisymmetry failed for [{x}, {y}] -> {z}"


@pytest.mark.parametrize("n", [1, 2])
def test_graded_jacobi_identities(n):
    schema = cg.build_schema1_json(n)
    sc = schema["structure_constants"]
    par = schema["parity"]
    basis = schema["basis"]["odd"] + schema["basis"]["even"]
    dim = len(basis)

    sc_dict = {}
    for entry in sc:
        sc_dict[(entry["X"], entry["Y"], entry["Z"])] = Fraction(entry["coeff"])

    for i in range(dim):
        x = basis[i]
        px = par[x]
        for j in range(dim):
            y = basis[j]
            py = par[y]
            for k in range(dim):
                z = basis[k]
                pz = par[z]

                s_x = (-1)**(px * pz)
                s_y = (-1)**(py * px)
                s_z = (-1)**(pz * py)

                for l in range(dim):
                    w = basis[l]
                    val = Fraction(0)
                    for m in range(dim):
                        u = basis[m]
                        c_yz_u = sc_dict.get((y, z, u), Fraction(0))
                        if c_yz_u != 0:
                            c_xu_w = sc_dict.get((x, u, w), Fraction(0))
                            if c_xu_w != 0:
                                val += s_x * c_yz_u * c_xu_w

                        c_zx_u = sc_dict.get((z, x, u), Fraction(0))
                        if c_zx_u != 0:
                            c_yu_w = sc_dict.get((y, u, w), Fraction(0))
                            if c_yu_w != 0:
                                val += s_y * c_zx_u * c_yu_w

                        c_xy_u = sc_dict.get((x, y, u), Fraction(0))
                        if c_xy_u != 0:
                            c_zu_w = sc_dict.get((z, u, w), Fraction(0))
                            if c_zu_w != 0:
                                val += s_z * c_xy_u * c_zu_w

                    assert val == 0, f"Jacobi identity failed for triple ({x}, {y}, {z}) on {w}"


@pytest.mark.parametrize("n", [1, 2, 3])
def test_schema1_top_level_keys(n):
    schema = cg.build_schema1_json(n)
    expected_keys = {
        "schema_version",
        "algebra",
        "oscillator_generators",
        "oscillator_relations",
        "central_elements",
        "basis",
        "parity",
        "generator_realization",
        "structure_constants",
        "metadata",
    }
    assert set(schema.keys()) == expected_keys
    assert schema["schema_version"] == "5.0"
    assert schema["algebra"]["family"] == "C"
    assert schema["algebra"]["m"] == 1
    assert schema["algebra"]["n"] == n
    assert "central_elements" in schema
    assert "kappa" in schema["central_elements"]
    assert "K" in schema["central_elements"]
    assert "fermions" in schema["oscillator_generators"]
    assert "bosons" in schema["oscillator_generators"]
