"""
test_C_generators.py — Unit tests for C_generators.py.

Tests cover:
  - Oscillator algebra (PBW reduction, swap rules)
  - Generator dimensions and parities
  - Known bracket values
  - Graded antisymmetry
  - Jacobi identity (sample triples)
  - Structure constant list properties
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

import unittest
from fractions import Fraction
from C_generators import (
    pbw_reduce_word,
    poly_multiply,
    graded_bracket,
    build_generators,
    express_in_generators,
    compute_structure_constants,
    build_schema1,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def F(x) -> Fraction:
    return Fraction(x)


def zero_poly():
    return {}


def poly_from_gen(label, gens):
    return dict(gens[label])


# ---------------------------------------------------------------------------
# 1. Oscillator algebra: PBW reduction
# ---------------------------------------------------------------------------

class TestPBWReduction(unittest.TestCase):
    def test_already_normal(self):
        # (0,2) = a_1_p b_1_p — already in PBW order
        self.assertEqual(pbw_reduce_word((0, 2)), {(0, 2): F(1)})

    def test_fermionic_anticommute(self):
        # a_1_m · a_1_p = 1 - a_1_p · a_1_m
        result = pbw_reduce_word((1, 0))
        self.assertEqual(result.get((), F(0)), F(1))
        self.assertEqual(result.get((0, 1), F(0)), F(-1))

    def test_fermionic_square_zero(self):
        # (a_1_p)^2 = 0
        self.assertEqual(pbw_reduce_word((0, 0)), {})
        # (a_1_m)^2 = 0
        self.assertEqual(pbw_reduce_word((1, 1)), {})

    def test_bosonic_commute_same_pair(self):
        # b_1_m · b_1_p = 1 + b_1_p · b_1_m
        result = pbw_reduce_word((3, 2))
        self.assertEqual(result.get((), F(0)), F(1))
        self.assertEqual(result.get((2, 3), F(0)), F(1))

    def test_bosonic_square_nonzero(self):
        # (b_1_p)^2 is a valid PBW monomial
        result = pbw_reduce_word((2, 2))
        self.assertEqual(result, {(2, 2): F(1)})

    def test_boson_fermion_commute(self):
        # b_1_p · a_1_p = a_1_p · b_1_p  (free commutation)
        result = pbw_reduce_word((2, 0))
        self.assertEqual(result, {(0, 2): F(1)})

    def test_boson_fermion_commute2(self):
        # b_1_m · a_1_m = a_1_m · b_1_m
        result = pbw_reduce_word((3, 1))
        self.assertEqual(result, {(1, 3): F(1)})

    def test_different_bosons_commute(self):
        # b_2_m · b_1_p = b_1_p · b_2_m  (i.e. (5,2) -> (2,5))
        result = pbw_reduce_word((5, 2))
        self.assertEqual(result, {(2, 5): F(1)})


# ---------------------------------------------------------------------------
# 2. Generator dimensions and parities
# ---------------------------------------------------------------------------

class TestGeneratorDimensions(unittest.TestCase):
    def _check(self, n, expected_even, expected_odd):
        gens, parities, even_basis, odd_basis = build_generators(n)
        self.assertEqual(len(even_basis), expected_even,
                         f"n={n}: even count {len(even_basis)} != {expected_even}")
        self.assertEqual(len(odd_basis), expected_odd,
                         f"n={n}: odd count {len(odd_basis)} != {expected_odd}")
        self.assertEqual(len(gens), expected_even + expected_odd,
                         f"n={n}: total generator count mismatch")
        for g in even_basis:
            self.assertEqual(parities[g], 0, f"n={n}: {g} should be parity 0")
        for g in odd_basis:
            self.assertEqual(parities[g], 1, f"n={n}: {g} should be parity 1")

    def test_C2(self):
        self._check(1, 4, 4)   # C(2): dim (4|4)

    def test_C3(self):
        self._check(2, 11, 8)  # C(3): dim (11|8)

    def test_C4(self):
        self._check(3, 22, 12) # C(4): dim (22|12)

    def test_dimension_formula(self):
        for n in (1, 2, 3):
            _, _, even_basis, odd_basis = build_generators(n)
            self.assertEqual(len(even_basis), 2 * n * n + n + 1)
            self.assertEqual(len(odd_basis), 4 * n)


# ---------------------------------------------------------------------------
# 3. Known bracket values — Cartan action on odd generators
# ---------------------------------------------------------------------------

class TestKnownBrackets(unittest.TestCase):
    def _bracket(self, n, lx, ly):
        gens, parities, even_basis, odd_basis = build_generators(n)
        all_basis = odd_basis + even_basis
        br = graded_bracket(gens[lx], parities[lx], gens[ly], parities[ly])
        return express_in_generators(br, gens, all_basis)

    # --- n=1 (C(2)) ---

    def test_H1_Epp_n1(self):
        # [H_1, E_eps1_del1_pp} = 2 E_eps1_del1_pp
        result = self._bracket(1, "H_1", "E_eps1_del1_pp")
        self.assertEqual(result, {"E_eps1_del1_pp": F(2)})

    def test_H2_Epp_n1(self):
        # [H_2, E_eps1_del1_pp} = -E_eps1_del1_pp
        # H_2 = -b_1^+b_1^- - 1/2; root eigenvalue for eps1+del1 under H_{n+1} = -1
        result = self._bracket(1, "H_2", "E_eps1_del1_pp")
        self.assertEqual(result, {"E_eps1_del1_pp": F(-1)})

    def test_Epp_Emm_n1(self):
        # [E_eps1_del1_pp, E_eps1_del1_mm} = -H_1 - 2*H_2
        result = self._bracket(1, "E_eps1_del1_pp", "E_eps1_del1_mm")
        self.assertEqual(result, {"H_1": F(-1), "H_2": F(-2)})

    def test_Epp_Emp_n1(self):
        # [E_eps1_del1_pp, E_eps1_del1_mp} = E_2del1_p  (b_1^+)^2
        result = self._bracket(1, "E_eps1_del1_pp", "E_eps1_del1_mp")
        self.assertEqual(result, {"E_2del1_p": F(1)})

    def test_Epm_Emm_n1(self):
        # [E_eps1_del1_pm, E_eps1_del1_mm} = 0  (a_1^+ b_1^-)·(a_1^- b_1^-) + h.c. = 0 ?)
        # E_pm = a_1^+b_1^-, E_mm = a_1^-b_1^-
        # Both have same bosonic sign, bracket should be related to E_2del1_m
        result = self._bracket(1, "E_eps1_del1_pm", "E_eps1_del1_mm")
        self.assertEqual(result, {"E_2del1_m": F(1)})

    def test_H1_E2del1p_n1(self):
        # [H_1, E_2del1_p} = 0  (H_1 is even, E_2del1_p = (b_1^+)^2 has root 2δ_1)
        # H_1 = a_1^+a_1^- + b_1^+b_1^-; [b_1^+b_1^-, (b_1^+)^2] = 2*(b_1^+)^2
        # [a_1^+a_1^-, (b_1^+)^2] = 0  (fermion and boson commute)
        result = self._bracket(1, "H_1", "E_2del1_p")
        self.assertEqual(result, {"E_2del1_p": F(2)})

    def test_H2_E2del1p_n1(self):
        # [H_2, E_2del1_p}: H_2 = -b_1^+b_1^- - 1/2; root is 2δ_1 under H_{n+1}
        # eigenvalue = -2 (since H_{n+1} has eigenvalue -1 for δ_1, so -2 for 2δ_1)
        result = self._bracket(1, "H_2", "E_2del1_p")
        self.assertEqual(result, {"E_2del1_p": F(-2)})

    def test_Epp_Epm_n1(self):
        # [E_eps1_del1_pp, E_eps1_del1_pm}: both odd, same fermion (a_1^+)
        # a_1^+b_1^+ · a_1^+b_1^- + a_1^+b_1^- · a_1^+b_1^+ = (a_1^+)^2*(...)  = 0
        result = self._bracket(1, "E_eps1_del1_pp", "E_eps1_del1_pm")
        self.assertEqual(result, {})

    def test_E2del1p_E2del1m_n1(self):
        # [E_2del1_p, E_2del1_m}: [(b_1^+)^2, (b_1^-)^2]
        # = (b_1^+)^2(b_1^-)^2 - (b_1^-)^2(b_1^+)^2
        result = self._bracket(1, "E_2del1_p", "E_2del1_m")
        # Should be a combination of Cartans
        self.assertIsInstance(result, dict)
        # Verify result is purely in Cartan span
        for key in result:
            self.assertIn(key, ["H_1", "H_2"])

    # --- n=2 (C(3)) ---

    def test_H1_Epp_n2(self):
        # [H_1, E_eps1_del1_pp} = 2 E_eps1_del1_pp (same as n=1)
        result = self._bracket(2, "H_1", "E_eps1_del1_pp")
        self.assertEqual(result, {"E_eps1_del1_pp": F(2)})

    def test_H1_Epp_del2_n2(self):
        # [H_1, E_eps1_del2_pp}: H_1 = a_1^+a_1^- + b_1^+b_1^-
        # E_eps1_del2_pp = a_1^+b_2^+; root ε+δ_2 has H_1 eigenvalue 1 (from a_1^+a_1^-)
        result = self._bracket(2, "H_1", "E_eps1_del2_pp")
        self.assertEqual(result, {"E_eps1_del2_pp": F(1)})

    def test_Epp1_Emm1_n2(self):
        # [E_eps1_del1_pp, E_eps1_del1_mm} for n=2
        # Raw bracket same {(0,1):-1, (2,3):1, ():1} but Cartan generators differ from n=1
        # -H_1 + 2*H_2 - 2*H_3  (H_2=m_1-m_2, H_3=-m_2-1/2 in n=2)
        result = self._bracket(2, "E_eps1_del1_pp", "E_eps1_del1_mm")
        self.assertEqual(result, {"H_1": F(-1), "H_2": F(2), "H_3": F(-2)})

    def test_Epp2_Emm2_n2(self):
        # [E_eps1_del2_pp, E_eps1_del2_mm} for n=2
        # E_pp2 = a_1^+b_2^+, E_mm2 = a_1^-b_2^-
        result = self._bracket(2, "E_eps1_del2_pp", "E_eps1_del2_mm")
        self.assertIsInstance(result, dict)
        # Should involve H generators
        for key in result:
            self.assertIn(key, ["H_1", "H_2", "H_3"])

    def test_Epp1_Emp1_n2(self):
        # [E_eps1_del1_pp, E_eps1_del1_mp} = E_2del1_p (same as n=1)
        result = self._bracket(2, "E_eps1_del1_pp", "E_eps1_del1_mp")
        self.assertEqual(result, {"E_2del1_p": F(1)})

    def test_Epp1_Emp2_n2(self):
        # [E_eps1_del1_pp, E_eps1_del2_mp}: a_1^+b_1^+ · a_1^-b_2^+ + a_1^-b_2^+ · a_1^+b_1^+
        result = self._bracket(2, "E_eps1_del1_pp", "E_eps1_del2_mp")
        self.assertEqual(result, {"E_del1_del2_pp": F(1)})


# ---------------------------------------------------------------------------
# 4. Graded antisymmetry
# ---------------------------------------------------------------------------

class TestGradedAntisymmetry(unittest.TestCase):
    def _check_antisymm(self, n, lx, ly):
        gens, parities, even_basis, odd_basis = build_generators(n)
        all_basis = odd_basis + even_basis
        br_xy = graded_bracket(gens[lx], parities[lx], gens[ly], parities[ly])
        br_yx = graded_bracket(gens[ly], parities[ly], gens[lx], parities[lx])
        sign = (-1) ** (parities[lx] * parities[ly])
        # [X,Y} + (-1)^{p(X)p(Y)} [Y,X} = 0
        combined = {}
        for w, c in br_xy.items():
            combined[w] = combined.get(w, Fraction(0)) + c
        for w, c in br_yx.items():
            combined[w] = combined.get(w, Fraction(0)) + sign * c
        combined = {k: v for k, v in combined.items() if v != 0}
        self.assertEqual(combined, {},
                         f"[{lx},{ly}] antisymmetry fails for n={n}: residual={combined}")

    def test_antisymm_even_even_n1(self):
        self._check_antisymm(1, "H_1", "H_2")

    def test_antisymm_even_odd_n1(self):
        self._check_antisymm(1, "H_1", "E_eps1_del1_pp")
        self._check_antisymm(1, "H_2", "E_eps1_del1_mm")

    def test_antisymm_odd_odd_n1(self):
        self._check_antisymm(1, "E_eps1_del1_pp", "E_eps1_del1_mm")
        self._check_antisymm(1, "E_eps1_del1_pp", "E_eps1_del1_mp")

    def test_antisymm_n2(self):
        pairs = [
            ("H_1", "E_eps1_del2_pp"),
            ("E_eps1_del1_pp", "E_eps1_del2_mm"),
            ("E_eps1_del1_pm", "E_eps1_del2_mp"),
        ]
        for lx, ly in pairs:
            self._check_antisymm(2, lx, ly)

    def test_antisymm_all_pairs_n1(self):
        n = 1
        gens, parities, even_basis, odd_basis = build_generators(n)
        all_basis = odd_basis + even_basis
        for lx in all_basis:
            for ly in all_basis:
                self._check_antisymm(n, lx, ly)


# ---------------------------------------------------------------------------
# 5. Jacobi identity (sample triples)
# ---------------------------------------------------------------------------

class TestJacobiIdentity(unittest.TestCase):
    def _jacobi(self, n, lx, ly, lz):
        gens, parities, even_basis, odd_basis = build_generators(n)
        X, pX = gens[lx], parities[lx]
        Y, pY = gens[ly], parities[ly]
        Z, pZ = gens[lz], parities[lz]

        def br(A, pA, B, pB):
            return graded_bracket(A, pA, B, pB)

        # Graded Jacobi: (-1)^{pX pZ} [X,[Y,Z}} + (-1)^{pY pX} [Y,[Z,X}} + (-1)^{pZ pY} [Z,[X,Y}} = 0
        YZ = br(Y, pY, Z, pZ)
        XYZ = br(X, pX, YZ, (pY + pZ) % 2)

        ZX = br(Z, pZ, X, pX)
        YZX = br(Y, pY, ZX, (pZ + pX) % 2)

        XY = br(X, pX, Y, pY)
        ZXY = br(Z, pZ, XY, (pX + pY) % 2)

        s1 = Fraction((-1) ** (pX * pZ))
        s2 = Fraction((-1) ** (pY * pX))
        s3 = Fraction((-1) ** (pZ * pY))

        combined = {}
        for d, s in [(XYZ, s1), (YZX, s2), (ZXY, s3)]:
            for w, c in d.items():
                combined[w] = combined.get(w, Fraction(0)) + s * c
        combined = {k: v for k, v in combined.items() if v != 0}
        self.assertEqual(
            combined, {},
            f"Jacobi identity fails for ({lx},{ly},{lz}) n={n}: residual={combined}",
        )

    def test_jacobi_HHE_n1(self):
        self._jacobi(1, "H_1", "H_2", "E_eps1_del1_pp")

    def test_jacobi_HEE_n1(self):
        self._jacobi(1, "H_1", "E_eps1_del1_pp", "E_eps1_del1_mm")

    def test_jacobi_EEE_n1(self):
        self._jacobi(1, "E_eps1_del1_pp", "E_eps1_del1_mp", "E_eps1_del1_pm")

    def test_jacobi_HEE_n2(self):
        self._jacobi(2, "H_1", "E_eps1_del1_pp", "E_eps1_del2_mm")

    def test_jacobi_EEE_n2(self):
        self._jacobi(2, "E_eps1_del1_pp", "E_eps1_del1_mp", "E_eps1_del2_mm")

    def test_jacobi_HHE_n2(self):
        self._jacobi(2, "H_2", "H_3", "E_eps1_del1_pp")


# ---------------------------------------------------------------------------
# 6. Structure constant list properties
# ---------------------------------------------------------------------------

class TestStructureConstantList(unittest.TestCase):
    def _check(self, n):
        gens, parities, even_basis, odd_basis = build_generators(n)
        all_basis = odd_basis + even_basis
        sc = compute_structure_constants(n)

        # All referenced generators are in the basis
        for entry in sc:
            self.assertIn(entry["X"], all_basis, f"n={n}: X={entry['X']} not in basis")
            self.assertIn(entry["Y"], all_basis, f"n={n}: Y={entry['Y']} not in basis")
            self.assertIn(entry["Z"], all_basis, f"n={n}: Z={entry['Z']} not in basis")
            self.assertEqual(entry["sign_rule"], "graded")
            # coeff must parse as a valid fraction
            Fraction(entry["coeff"])

        # X ≤ Y in PBW order for every entry
        for entry in sc:
            ix = all_basis.index(entry["X"])
            iy = all_basis.index(entry["Y"])
            self.assertLessEqual(ix, iy,
                                 f"n={n}: X={entry['X']} after Y={entry['Y']} in PBW order")

        # Parity closure: p(Z) = p(X) + p(Y) mod 2
        for entry in sc:
            pz = parities[entry["Z"]]
            px = parities[entry["X"]]
            py = parities[entry["Y"]]
            self.assertEqual(pz, (px + py) % 2,
                             f"n={n}: parity mismatch for [{entry['X']},{entry['Y']}] -> {entry['Z']}")

    def test_sc_C2(self):
        self._check(1)

    def test_sc_C3(self):
        self._check(2)

    def test_sc_C4(self):
        self._check(3)


# ---------------------------------------------------------------------------
# 7. Schema 1 JSON structure
# ---------------------------------------------------------------------------

class TestSchema1(unittest.TestCase):
    def test_schema_keys(self):
        schema = build_schema1(1)
        required_keys = {
            "schema_version", "algebra", "oscillator_generators",
            "oscillator_relations", "central_elements", "basis",
            "parity", "generator_realization", "structure_constants", "metadata",
        }
        self.assertEqual(set(schema.keys()), required_keys)

    def test_schema_version(self):
        schema = build_schema1(1)
        self.assertEqual(schema["schema_version"], "5.0")

    def test_algebra_n1(self):
        schema = build_schema1(1)
        alg = schema["algebra"]
        self.assertEqual(alg["family"], "C")
        self.assertEqual(alg["m"], 1)
        self.assertEqual(alg["n"], 1)
        self.assertEqual(alg["dimension"]["total"], 8)
        self.assertEqual(alg["dimension"]["even"], 4)
        self.assertEqual(alg["dimension"]["odd"], 4)

    def test_algebra_n2(self):
        schema = build_schema1(2)
        alg = schema["algebra"]
        self.assertEqual(alg["dimension"]["total"], 19)
        self.assertEqual(alg["dimension"]["even"], 11)
        self.assertEqual(alg["dimension"]["odd"], 8)

    def test_algebra_n3(self):
        schema = build_schema1(3)
        alg = schema["algebra"]
        self.assertEqual(alg["dimension"]["total"], 34)
        self.assertEqual(alg["dimension"]["even"], 22)
        self.assertEqual(alg["dimension"]["odd"], 12)

    def test_standard_fermion_key(self):
        schema = build_schema1(1)
        osc = schema["oscillator_generators"]
        self.assertIn("standard_fermion", osc)
        self.assertNotIn("fermions", osc)
        self.assertNotIn("supplementary_fermion", osc)
        self.assertEqual(osc["standard_fermion"]["parity"], 1)

    def test_central_elements_present(self):
        schema = build_schema1(1)
        ce = schema["central_elements"]
        self.assertIn("kappa", ce)
        self.assertIn("K", ce)

    def test_basis_counts(self):
        for n in (1, 2, 3):
            schema = build_schema1(n)
            basis = schema["basis"]
            self.assertEqual(len(basis["even"]), 2 * n * n + n + 1)
            self.assertEqual(len(basis["odd"]), 4 * n)

    def test_parity_dict_complete(self):
        for n in (1, 2, 3):
            schema = build_schema1(n)
            parity = schema["parity"]
            basis = schema["basis"]
            all_gens = basis["even"] + basis["odd"]
            self.assertEqual(set(parity.keys()), set(all_gens))

    def test_json_serialisable(self):
        import json
        for n in (1, 2, 3):
            schema = build_schema1(n)
            s = json.dumps(schema)
            self.assertIsInstance(s, str)


if __name__ == "__main__":
    unittest.main(verbosity=2)
