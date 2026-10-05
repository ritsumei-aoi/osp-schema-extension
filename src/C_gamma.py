"""
C(n+1) = osp(2|2n) gamma structure (Schema 2) generator.

Computes the inhomogeneous deformation γ-coefficients arising from
the deformed oscillator relations [b_j^s, a_1^σ] = -gb_{σ,j,s} · κ.
"""

import json
import os
from fractions import Fraction
from datetime import date
from C_generators import (
    build_basis, build_parity_map, gen_realization,
    bracket_bilinear, simplify_lincomb, decompose_in_basis,
    osc_parity, osc_label,
)


def gb_label(sigma, j, s):
    """Label for a gb parameter: gb_{a_1_σ, b_j_s}."""
    return f"gb_a1{sigma}_b{j}{s}"


def build_gb_matrix(n):
    """Build the gb parameter matrix for C(n+1).
    Returns list of gb parameter labels and their metadata.
    The gb matrix has shape 2 x 2n = 4n parameters.
    """
    params = []
    for sigma in ['p', 'm']:
        for j in range(1, n + 1):
            for s in ['p', 'm']:
                label = gb_label(sigma, j, s)
                params.append({
                    "label": label,
                    "fermion": f"a_1_{sigma}",
                    "boson": f"b_{j}_{s}",
                    "parity": 1,
                })
    return params


def compute_deformed_bracket_term(A, B, C, D, n):
    """Compute the κ-correction to [AB, CD} from the deformed mixed commutators.

    The deformation changes [b_j^s, a_1^σ] = 0 to [b_j^s, a_1^σ] = -gb_{σ,j,s} · κ.
    Since κ is central and nilpotent (κ²=0), the correction is linear in κ.

    Using the same Leibniz expansion as for the undeformed bracket:
    [AB, CD} = A[B,C}D + (-1)^{pB·pC}[A,C}BD
             + (-1)^{(pA+pB)·pC} C·A[B,D} + (-1)^{(pA+pB)·pC+pB·pD} C·[A,D}B

    The κ-correction comes from replacing fundamental brackets with their
    deformed values when one operand is a fermion and the other is a boson.

    Returns: list of (gb_label, coeff, result_word) triples.
    """
    pA, pB, pC, pD = osc_parity(A), osc_parity(B), osc_parity(C), osc_parity(D)

    corrections = []

    def deformed_fundamental(X, Y):
        """Return (gb_label, sign) if the deformation modifies [X, Y},
        or None if this bracket is unchanged.
        [b_j^s, a_1^σ] = -gb_{σ,j,s} · κ  (deformation)
        [a_1^σ, b_j^s] = -[b_j^s, a_1^σ] = gb_{σ,j,s} · κ  (for commutator)
        """
        pX, pY = osc_parity(X), osc_parity(Y)
        if pX == 0 and pY == 1:
            # boson * fermion: [b_j^s, a_1^σ] = -gb_{σ,j,s}·κ
            j, s = X[1], X[2]
            sigma = Y[2]
            return (gb_label(sigma, j, s), Fraction(-1))
        elif pX == 1 and pY == 0:
            # fermion * boson: [a_1^σ, b_j^s] = gb_{σ,j,s}·κ
            sigma = X[2]
            j, s = Y[1], Y[2]
            return (gb_label(sigma, j, s), Fraction(1))
        return None

    sign_AC = Fraction((-1) ** (pB * pC))
    sign_CD_factor = Fraction((-1) ** ((pA + pB) * pC))
    sign_AD2 = Fraction((-1) ** (pB * pD))

    # Term 1: [B,C} correction → coeff * (A, D)
    df_BC = deformed_fundamental(B, C)
    if df_BC:
        gb, sign = df_BC
        corrections.append((gb, sign, (A, D)))

    # Term 2: [A,C} correction → sign_AC * coeff * (B, D)
    df_AC = deformed_fundamental(A, C)
    if df_AC:
        gb, sign = df_AC
        corrections.append((gb, sign_AC * sign, (B, D)))

    # Term 3: [B,D} correction → sign_CD_factor * coeff * (C, A)
    df_BD = deformed_fundamental(B, D)
    if df_BD:
        gb, sign = df_BD
        corrections.append((gb, sign_CD_factor * sign, (C, A)))

    # Term 4: [A,D} correction → sign_CD_factor * sign_AD2 * coeff * (C, B)
    df_AD = deformed_fundamental(A, D)
    if df_AD:
        gb, sign = df_AD
        corrections.append((gb, sign_CD_factor * sign_AD2 * sign, (C, B)))

    return corrections


def compute_gamma_coefficients(n):
    """Compute all γ_{X,Y,Z} coefficients for C(n+1).

    γ_{X,Y,Z} is the coefficient such that:
    [X, Y]_deformed = [X, Y]_0 + κ · Σ_Z γ_{X,Y,Z} · Z

    where the γ coefficients are linear in gb parameters.

    Returns: list of dicts with keys X, Y, Z, gb_terms.
    """
    even, odd = build_basis(n)
    all_basis = odd + even
    parity = build_parity_map(even, odd)
    reals = gen_realization(n)

    gamma_entries = []

    for i, X in enumerate(all_basis):
        for j in range(i + 1, len(all_basis)):
            Y = all_basis[j]
            pX, pY = parity[X], parity[Y]

            # Collect all κ-corrections from deformed brackets
            all_corrections = {}  # gb_label -> list of (coeff, word)

            for cx, tx in reals[X]:
                if len(tx) != 2:
                    continue
                for cy, ty in reals[Y]:
                    if len(ty) != 2:
                        continue
                    corrections = compute_deformed_bracket_term(
                        tx[0], tx[1], ty[0], ty[1], n
                    )
                    for gb, coeff, word in corrections:
                        if gb not in all_corrections:
                            all_corrections[gb] = []
                        all_corrections[gb].append((cx * cy * coeff, word))

            if not all_corrections:
                continue

            # For each gb parameter, simplify and decompose in basis
            for gb, terms in all_corrections.items():
                simplified = simplify_lincomb(terms)
                if not simplified:
                    continue
                decomp = decompose_in_basis(simplified, reals, all_basis, parity)
                for Z, coeff in decomp:
                    gamma_entries.append({
                        "X": X,
                        "Y": Y,
                        "Z": Z,
                        "gb_param": gb,
                        "coeff": str(coeff),
                    })

    return gamma_entries


def build_schema2_json(n):
    """Build Schema 2 JSON for C(n+1)."""
    even, odd = build_basis(n)
    gb_params = build_gb_matrix(n)
    gamma = compute_gamma_coefficients(n)

    schema = {
        "schema_version": "5.0",
        "schema_layer": 2,
        "algebra": {
            "family": "C",
            "m": 1,
            "n": n,
            "cartan_type": f"C({n + 1})",
        },
        "gb_matrix": {
            "description": "Inhomogeneous deformation parameters for C(n+1)",
            "parameter_count": 4 * n,
            "shape": f"2 x {2 * n}",
            "parameters": gb_params,
        },
        "deformation_rule": {
            "description": "[b_j^s, a_1^sigma] = -gb_{sigma,j,s} * kappa",
            "kappa_parity": 1,
            "kappa_nilpotency": "kappa^2 = 0",
        },
        "gamma_coefficients": gamma,
        "metadata": {
            "generated_by": "C_gamma.py",
            "generation_date": str(date.today()),
            "references": [
                "Frappat et al. (2000), Dictionary on Lie Algebras and Superalgebras",
                "C_inhomogeneous_definition.md",
            ],
        },
    }
    return schema


def generate_all(output_dir="data"):
    os.makedirs(output_dir, exist_ok=True)
    for n in [1, 2, 3]:
        schema = build_schema2_json(n)
        path = os.path.join(output_dir, f"C_{n}_gamma.json")
        with open(path, "w") as f:
            json.dump(schema, f, indent=2)
        print(f"Generated {path}: {len(schema['gamma_coefficients'])} gamma entries, "
              f"{schema['gb_matrix']['parameter_count']} gb params")


def verify_consistency(n, data_dir="data"):
    """Verify Schema 2 is consistent with Schema 1."""
    with open(os.path.join(data_dir, f"C_{n}_structure.json")) as f:
        s1 = json.load(f)
    with open(os.path.join(data_dir, f"C_{n}_gamma.json")) as f:
        s2 = json.load(f)

    basis_s1 = set(s1["basis"]["even"] + s1["basis"]["odd"])
    errors = []

    for entry in s2["gamma_coefficients"]:
        for key in ["X", "Y", "Z"]:
            if entry[key] not in basis_s1:
                errors.append(f"Generator {entry[key]} in gamma not in Schema 1 basis")

    if errors:
        print(f"  Consistency FAILURES for n={n}: {len(errors)}")
        for e in errors[:5]:
            print(f"    {e}")
    else:
        print(f"  Consistency check for n={n}: PASS")
    return len(errors) == 0


if __name__ == "__main__":
    generate_all()
    print("\nConsistency checks:")
    for n in [1, 2, 3]:
        verify_consistency(n)
