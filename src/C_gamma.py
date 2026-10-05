"""
C(n+1) = osp(2|2n) inhomogeneous deformation (gamma structure, Schema 2).

Computes gamma coefficients from the gb deformation parameters.
The deformation modifies the mixed oscillator commutators:
  [b_j^s, a_1^σ] = -gb_{σ,j,s} · κ

Approach: for each gb parameter, set it to 1 (others to 0), compute the
deformed bracket, subtract the undeformed bracket, and decompose the difference
into the generator basis.
"""

import json
import sys
from fractions import Fraction
from datetime import date
from itertools import combinations

sys.path.insert(0, __import__('os').path.dirname(__file__))
from C_generators import (
    build_basis, build_parity, build_realizations,
    realization_to_terms, build_decomposition_map, decompose_result,
    OscillatorAlgebra
)


def build_gb_params(n):
    params = []
    for sigma in ["p", "m"]:
        for j in range(1, n + 1):
            for s in ["p", "m"]:
                params.append(f"gb_a1{sigma}_b{j}{s}")
    return params


class DeformedOscillatorAlgebra(OscillatorAlgebra):
    """Oscillator algebra with deformed boson-fermion commutators."""

    def __init__(self, n, gb_values):
        super().__init__(n)
        self.gb_values = gb_values

    def _contraction(self, o1, o2):
        base = super()._contraction(o1, o2)
        if base is not None:
            return base
        if o1[0] == "b" and o2[0] == "f":
            key = (f"a_1_{o2[2]}", f"b_{o1[1]}_{o1[2]}")
            gb_val = self.gb_values.get(key, Fraction(0))
            if gb_val != 0:
                return -gb_val
            return None
        if o1[0] == "f" and o2[0] == "b":
            key = (f"a_1_{o1[2]}", f"b_{o2[1]}_{o2[2]}")
            gb_val = self.gb_values.get(key, Fraction(0))
            if gb_val != 0:
                return gb_val
            return None
        return None


def compute_gamma_coefficients(n, structure_data):
    """Compute gamma coefficients for all generator pairs and gb parameters."""
    basis_even = structure_data["basis"]["even"]
    basis_odd = structure_data["basis"]["odd"]
    all_gens = basis_odd + basis_even
    parity = structure_data["parity"]
    realizations = structure_data["generator_realization"]["realizations"]
    gen_vectors, monomial_list = build_decomposition_map(all_gens, realizations)

    gb_params = build_gb_params(n)
    undeformed_alg = OscillatorAlgebra(n)

    gamma_coefficients = []

    for param in gb_params:
        parts = param.split("_")
        sigma = parts[1][-1]
        j_str = parts[2]
        j = int(j_str[1:len(j_str)-1]) if len(j_str) > 2 else int(j_str[1])
        s = parts[2][-1]
        ferm_key = f"a_1_{sigma}"
        bos_key = f"b_{j}_{s}"
        gb_values = {(ferm_key, bos_key): Fraction(1)}

        deformed_alg = DeformedOscillatorAlgebra(n, gb_values)

        for i_idx, X in enumerate(all_gens):
            for j_idx, Y in enumerate(all_gens):
                if j_idx <= i_idx:
                    continue

                real_X = realization_to_terms(realizations[X])
                real_Y = realization_to_terms(realizations[Y])
                pX = parity[X]
                pY = parity[Y]

                bracket_def = deformed_alg.compute_bracket(real_X, real_Y, pX, pY)
                bracket_undef = undeformed_alg.compute_bracket(real_X, real_Y, pX, pY)

                diff = dict(bracket_def)
                for mono, coeff in bracket_undef.items():
                    diff[mono] = diff.get(mono, Fraction(0)) - coeff
                diff = {k: v for k, v in diff.items() if v != 0}

                if not diff:
                    continue

                coeffs = decompose_result(diff, all_gens, gen_vectors, list(monomial_list))

                for Z, coeff in coeffs.items():
                    if coeff != 0:
                        gamma_coefficients.append({
                            "X": X,
                            "Y": Y,
                            "Z": Z,
                            "gb_param": param,
                            "coeff": str(coeff),
                        })

    return gamma_coefficients


def generate_schema2(n):
    with open(f"data/C_{n}_structure.json") as f:
        structure_data = json.load(f)

    gb_params = build_gb_params(n)
    gamma_coeffs = compute_gamma_coefficients(n, structure_data)

    schema2 = {
        "schema_version": "5.0",
        "schema_layer": 2,
        "algebra": structure_data["algebra"],
        "gb_matrix": {
            "description": "Inhomogeneous deformation parameters for C(n+1)",
            "parameter_count": 4 * n,
            "parameters": gb_params,
            "deformation_rule": "[b_j^s, a_1^sigma] = -gb_{sigma,j,s} * kappa",
        },
        "gamma_coefficients": gamma_coeffs,
        "metadata": {
            "generated_by": "C_gamma.py",
            "generation_date": str(date.today()),
            "source_schema": f"C_{n}_structure.json",
        },
    }
    return schema2


def main():
    for n in [1, 2, 3]:
        print(f"Generating Schema 2 for C({n+1}) = osp(2|{2*n}) [n={n}]...")
        schema2 = generate_schema2(n)
        filename = f"data/C_{n}_gamma.json"
        with open(filename, "w") as f:
            json.dump(schema2, f, indent=2)
        n_gamma = len(schema2["gamma_coefficients"])
        print(f"  -> {filename}: {n_gamma} gamma coefficients")
    print("Done.")


if __name__ == "__main__":
    main()
