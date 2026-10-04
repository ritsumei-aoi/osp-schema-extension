from fractions import Fraction
import json
import os
import pytest
from src.C_generators import get_C_generators, generate_structure_constants
from src.C_gamma import (
    get_deformation_parameters,
    generate_schema_2_json,
    generate_and_save_all_gamma
)


@pytest.mark.parametrize("n,expected_params", [
    (1, 4),
    (2, 8),
    (3, 12),
])
def test_deformation_parameter_counts(n, expected_params):
    params = get_deformation_parameters(n)
    assert len(params) == expected_params


@pytest.mark.parametrize("n", [1, 2, 3])
def test_gamma_antisymmetry_and_parity(n):
    even_basis, odd_basis, parity, _, _ = get_C_generators(n)
    data = generate_schema_2_json(n)
    params = data["deformation_parameters"]
    all_basis = odd_basis + even_basis

    # Build gamma lookup table: (X, Y, Z, param) -> Fraction
    gamma_map = {}
    for entry in data["gamma_structure_constants"]:
        x, y, z = entry["X"], entry["Y"], entry["Z"]
        px = parity[x]
        py = parity[y]
        pz = parity[z]
        # Graded parity rule for odd deformation cocycle:
        # [X, Y]_\gamma = [X, Y]_0 + \kappa \gamma(X, Y)
        # Since p(\kappa) = 1, p(\gamma(X, Y)) = (p(X) + p(Y) + 1) mod 2
        assert pz == (px + py + 1) % 2, f"Parity mismatch for gamma({x}, {y}) = {z}"

        for item in entry["linear_combination"]:
            p = item["param"]
            c = Fraction(item["coeff"])
            gamma_map[(x, y, z, p)] = c

    # Antisymmetry check: gamma(X, Y) = - (-1)^{px * py} gamma(Y, X)
    for x in all_basis:
        px = parity[x]
        for y in all_basis:
            py = parity[y]
            sign = -1 if (px == 1 and py == 1) else 1
            for z in all_basis:
                for p in params:
                    c_xy = gamma_map.get((x, y, z, p), Fraction(0))
                    c_yx = gamma_map.get((y, x, z, p), Fraction(0))
                    expected_yx = - Fraction(sign) * c_xy
                    assert c_yx == expected_yx, f"Gamma antisymmetry failed for ({x}, {y}) on {z}, param {p}"


@pytest.mark.parametrize("n", [1, 2, 3])
def test_gamma_2cocycle_identity(n):
    even_basis, odd_basis, parity, _, _ = get_C_generators(n)
    sc = generate_structure_constants(n)
    data = generate_schema_2_json(n)
    params = data["deformation_parameters"]
    all_basis = odd_basis + even_basis

    sc_map = {}
    for entry in sc:
        sc_map[(entry["X"], entry["Y"], entry["Z"])] = Fraction(entry["coeff"])

    def bracket(x, y):
        res = {}
        for z in all_basis:
            c = sc_map.get((x, y, z), Fraction(0))
            if c != 0:
                res[z] = c
        return res

    def bracket_right(x, dict_y):
        res = {}
        for y, cy in dict_y.items():
            b = bracket(x, y)
            for z, cz in b.items():
                res[z] = res.get(z, Fraction(0)) + cy * cz
        return {k: v for k, v in res.items() if v != 0}

    gamma_by_p = {p: {} for p in params}
    for entry in data["gamma_structure_constants"]:
        x, y, z = entry["X"], entry["Y"], entry["Z"]
        for item in entry["linear_combination"]:
            p = item["param"]
            c = Fraction(item["coeff"])
            if (x, y) not in gamma_by_p[p]:
                gamma_by_p[p][(x, y)] = {}
            gamma_by_p[p][(x, y)][z] = c

    def gamma_eval(p, x, y):
        return gamma_by_p[p].get((x, y), {})

    def gamma_eval_right(p, x, dict_y):
        res = {}
        for y, cy in dict_y.items():
            g = gamma_eval(p, x, y)
            for z, cz in g.items():
                res[z] = res.get(z, Fraction(0)) + cy * cz
        return {k: v for k, v in res.items() if v != 0}

    # 2-Cocycle Super Jacobi condition:
    # sum_cyclic (-1)^{p(X)p(Z)} [ (-1)^{p(X)} [X, gamma(Y, Z)]_0 + gamma(X, [Y, Z]_0) ] = 0
    test_basis = all_basis if n <= 2 else all_basis[:12]

    for p in params:
        for x in test_basis:
            px = parity[x]
            for y in test_basis:
                py = parity[y]
                for z in test_basis:
                    pz = parity[z]

                    # Term 1: (-1)^{px*pz} [ (-1)^{px} [X, gamma(Y,Z)] + gamma(X, [Y,Z]) ]
                    g_yz = gamma_eval(p, y, z)
                    b_x_gyz = bracket_right(x, g_yz)
                    s_x = -1 if px == 1 else 1
                    b_yz = bracket(y, z)
                    g_x_byz = gamma_eval_right(p, x, b_yz)
                    s1 = -1 if (px * pz) % 2 == 1 else 1

                    # Term 2: (-1)^{py*px} [ (-1)^{py} [Y, gamma(Z,X)] + gamma(Y, [Z,X]) ]
                    g_zx = gamma_eval(p, z, x)
                    b_y_gzx = bracket_right(y, g_zx)
                    s_y = -1 if py == 1 else 1
                    b_zx = bracket(z, x)
                    g_y_bzx = gamma_eval_right(p, y, b_zx)
                    s2 = -1 if (py * px) % 2 == 1 else 1

                    # Term 3: (-1)^{pz*py} [ (-1)^{pz} [Z, gamma(X,Y)] + gamma(Z, [X,Y]) ]
                    g_xy = gamma_eval(p, x, y)
                    b_z_gxy = bracket_right(z, g_xy)
                    s_z = -1 if pz == 1 else 1
                    b_xy = bracket(x, y)
                    g_z_bxy = gamma_eval_right(p, z, b_xy)
                    s3 = -1 if (pz * py) % 2 == 1 else 1

                    total = {}
                    for d, s in [
                        (b_x_gyz, s1 * s_x), (g_x_byz, s1),
                        (b_y_gzx, s2 * s_y), (g_y_bzx, s2),
                        (b_z_gxy, s3 * s_z), (g_z_bxy, s3)
                    ]:
                        for k_gen, val in d.items():
                            total[k_gen] = total.get(k_gen, Fraction(0)) + s * val

                    for k_gen, val in total.items():
                        assert val == 0, f"Cocycle identity failed for param {p}, triple ({x}, {y}, {z}) on {k_gen}: {val}"


def test_save_gamma_files():
    generate_and_save_all_gamma("data")
    for n in [1, 2, 3]:
        p = f"data/C_{n}_gamma.json"
        assert os.path.exists(p)
        with open(p) as f:
            d = json.load(f)
        assert d["schema_version"] == "5.0"
        assert len(d["deformation_parameters"]) == 4 * n
        assert len(d["gamma_structure_constants"]) > 0
