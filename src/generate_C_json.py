"""
generate_C_json.py

Generate Schema 1 JSON files for C(n+1) = osp(2|2n) for n=1,2,3.
Outputs to data/algebra_structures/C_1_structure.json etc.
"""

import json
import os
from C_generators import build_C_basis, build_C_structure_constants

# Output directory
OUT_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)),
                        "data", "algebra_structures")
os.makedirs(OUT_DIR, exist_ok=True)


def generate_json(n: int) -> dict:
    """Generate Schema 1 JSON for C(n+1) = osp(2|2n)."""
    even_basis, odd_basis, parity = build_C_basis(n)
    br = build_C_structure_constants(n)

    # Dimensions
    even_dim = len(even_basis)
    odd_dim = len(odd_basis)
    total_dim = even_dim + odd_dim
    m = 1
    cartan_type = f"C({n + 1})"
    osp_name = f"osp({2 * m}|{2 * n})"

    # Oscillator labels
    boson_labels = [f"b_{i}_p" for i in range(1, n + 1)] + \
                   [f"b_{i}_m" for i in range(1, n + 1)]

    # Build basis ordering string
    ordering = (
        "PBW ordering (Option A): (1) Central element κ; "
        "(2) Odd generators: E_eps1_del{k}_pp, E_eps1_del{k}_pm, "
        "E_eps1_del{k}_mp, E_eps1_del{k}_mm (k=1..n); "
        "(3) Even generators: Cartan H_1..H_{n+1}, positive long "
        "E_2del{k}_p, positive short sum E_del{i}_del{j}_pp (i<j), "
        "negative long E_2del{k}_m, negative short sum "
        "E_del{i}_del{j}_mm (i<j), mixed E_del{i}_del{j}_pm (i<j), "
        "E_del{i}_del{j}_mp (i<j); (4) Central element K."
    )

    # Convert bracket dict to string-keyed format
    brackets = {}
    for (g1, g2), results in br.items():
        key = f"{g1},{g2}"
        brackets[key] = results

    # Build generator_realization using basis ordering
    # Generator name patterns (no curly braces in names):
    #   H_1, H_2, ..., H_{n+1}
    #   E_2del1_p, E_2del2_m  (long even: index + sign)
    #   E_del1_del2_pp, E_del1_del2_mm, E_del1_del2_pm, E_del1_del2_mp
    #   E_eps1_del1_pp, E_eps1_del1_pm, E_eps1_del1_mp, E_eps1_del1_mm
    import re

    realizations = {}
    # Order: κ, odd, even, K
    all_gens = ["κ"] + odd_basis + even_basis + ["K"]
    for gen in all_gens:
        if gen == "κ":
            realizations[gen] = {
                "standard_form": [{"words": [], "coeff": "1"}],
                "frappat_form": "κ",
                "parity": 0,
                "note": "Central element κ (constant term center)."
            }
            continue
        if gen == "K":
            realizations[gen] = {
                "standard_form": [{"words": [], "coeff": "1"}],
                "frappat_form": "K",
                "parity": 0,
                "note": (
                    "Central element K. Arises from normal-ordering "
                    "constant -1/2 in b_k^+b_k^- expansion."
                )
            }
            continue

        p = parity.get(gen, 0)

        if gen.startswith("H_"):
            idx_raw = gen[2:]
            if idx_raw == "{n+1}":
                frappat = "a_1^+ a_1^- - 1/2"
                words = [{"words": ["a_1_p", "a_1_m"], "coeff": "1"},
                         {"words": [], "coeff": "-1/2"}]
                note = "Fermionic Cartan generator H_{n+1} = a_1^+ a_1^- - 1/2."
            else:
                idx = int(idx_raw)
                if idx == n:
                    frappat = f"b_{idx}^+ b_{idx}^- + 1/2"
                    words = [
                        {"words": [f"b_{idx}_p", f"b_{idx}_m"], "coeff": "1"},
                        {"words": [], "coeff": "1/2"}
                    ]
                    note = f"Terminal bosonic Cartan H_{idx} = b_{idx}^+ b_{idx}^- + 1/2."
                else:
                    idx_n = idx + 1
                    frappat = f"b_{idx}^+ b_{idx}^- - b_{idx_n}^+ b_{idx_n}^-"
                    words = [
                        {"words": [f"b_{idx}_p", f"b_{idx}_m"], "coeff": "1"},
                        {"words": [f"b_{idx_n}_p", f"b_{idx_n}_m"], "coeff": "-1"}
                    ]
                    note = f"Bosonic Cartan H_{idx} = b_{idx}^+ b_{idx}^- - b_{idx_n}^+ b_{idx_n}^-."

        elif gen[:6] == "E_2del":
            pat = re.match(r"^E_2del(\d+)_(p|m)$", gen)
            k, sign = pat.group(1), pat.group(2)
            if sign == "p":
                frappat = f"(b_{k}^+)^2"
                words = [{"words": [f"b_{k}_p", f"b_{k}_p"], "coeff": "1"}]
                note = f"Long even root +2δ_{k}. Frappat: E_{{±2δ_k}} = (b_k^±)^2."
            else:
                frappat = f"(b_{k}^-)^2"
                words = [{"words": [f"b_{k}_m", f"b_{k}_m"], "coeff": "1"}]
                note = f"Long even root -2δ_{k}. Frappat: E_{{±2δ_k}} = (b_k^±)^2."

        elif gen[:5] == "E_del":
            pat = re.match(r"^E_del(\d+)_del(\d+)_(pp|mm|pm|mp)$", gen)
            i, j, suffix = pat.group(1), pat.group(2), pat.group(3)
            i_int, j_int = int(i), int(j)
            if suffix == "pp":
                frappat = f"b_{i}^+ b_{j}^+"
                words = [{"words": [f"b_{i}_p", f"b_{j}_p"], "coeff": "1"}]
                note = f"Short even root +δ_{i}+δ_{j}. Frappat: E_{{δ_i+δ_j}} = b_i^+ b_j^+."
            elif suffix == "mm":
                frappat = f"b_{i}^- b_{j}^-"
                words = [{"words": [f"b_{i}_m", f"b_{j}_m"], "coeff": "1"}]
                note = f"Short even root -(δ_{i}+δ_{j}). Frappat: E_{{-(δ_i+δ_j)}} = b_i^- b_j^-."
            elif suffix == "pm":
                if i_int < j_int:
                    frappat = f"b_{i}^+ b_{j}^-"
                    words = [{"words": [f"b_{i}_p", f"b_{j}_m"], "coeff": "1"}]
                    note = f"Mixed even root δ_{i}-δ_{j}. Frappat: E_{{δ_i-δ_j}} = b_i^+ b_j^-."
                else:
                    frappat = f"b_{i}^- b_{j}^+"
                    words = [{"words": [f"b_{i}_m", f"b_{j}_p"], "coeff": "1"}]
                    note = f"Mixed even root -(δ_{i}-δ_{j}). Frappat: E_{{-(δ_i-δ_j)}} = b_i^- b_j^+."
            else:  # mp
                if i_int < j_int:
                    frappat = f"b_{i}^- b_{j}^+"
                    words = [{"words": [f"b_{i}_m", f"b_{j}_p"], "coeff": "1"}]
                    note = f"Mixed even root -(δ_{i}-δ_{j}). Frappat: E_{{-(δ_i-δ_j)}} = b_i^- b_j^+."
                else:
                    frappat = f"b_{i}^+ b_{j}^-"
                    words = [{"words": [f"b_{i}_p", f"b_{j}_m"], "coeff": "1"}]
                    note = f"Mixed even root δ_{i}-δ_{j}. Frappat: E_{{δ_i-δ_j}} = b_i^+ b_j^-."

        elif gen[:10] == "E_eps1_del":
            pat = re.match(r"^E_eps1_del(\d+)_(pp|pm|mp|mm)$", gen)
            k, suffix = pat.group(1), pat.group(2)
            alpha = "+" if suffix[0] == "p" else "-"
            beta = "+" if suffix[1] == "p" else "-"
            frappat = f"a_1^{{{alpha}}} b_{k}^{{{beta}}}"
            words = [{"words": [f"a_1_{suffix[0]}", f"b_{k}_{suffix[1]}"], "coeff": "1"}]
            if suffix == "pp":
                note = f"Odd root ε₁+δ_{k}. Frappat: E_{{ε₁+δ_k}} = a_1^+ b_k^+."
            elif suffix == "pm":
                note = f"Odd root ε₁-δ_{k}. Frappat: E_{{ε₁-δ_k}} = a_1^+ b_k^-."
            elif suffix == "mp":
                note = f"Odd root -(ε₁-δ_{k}). Frappat: E_{{-(ε₁-δ_k)}} = a_1^- b_k^+."
            else:
                note = f"Odd root -(ε₁+δ_{k}). Frappat: E_{{-(ε₁+δ_k)}} = a_1^- b_k^-."

        realizations[gen] = {
            "standard_form": words,
            "frappat_form": frappat,
            "parity": p,
            "note": note
        }
    # Clean up any leaked variables from the loop
    del pat

    # Assemble JSON
    data = {
        "schema_version": "5.0",
        "algebra": {
            "family": "C",
            "m": m,
            "n": n,
            "cartan_type": cartan_type,
            "alternative_notation": {
                "osp": osp_name,
                "dimension_formula": "osp(2m|2n)"
            },
            "dimension": {
                "total": total_dim,
                "even": even_dim,
                "odd": odd_dim
            }
        },
        "oscillator_generators": {
            "fermions": {
                "count": 2,
                "m": m,
                "labels": ["a_1_p", "a_1_m"],
                "description": (
                    "Standard fermionic oscillators a_1^± "
                    "(single pair, CAR). No supplementary fermion a_0."
                )
            },
            "bosons": {
                "count": 2 * n,
                "n": n,
                "labels": boson_labels,
                "description": (
                    f"Bosonic oscillators b_i^± with i=1,...,{n}"
                )
            }
        },
        "oscillator_relations": {
            "standard_fermion_anticommutators": {
                "description": (
                    "Canonical anticommutation relations "
                    "for standard fermionic pair"
                ),
                "relations": {
                    "same_type": "{a_1^±, a_1^±} = 0",
                    "conjugate_pair": "{a_1^-, a_1^+} = 1"
                },
                "canonical_pairs": [
                    {
                        "index": 1,
                        "annihilation": "a_1_m",
                        "creation": "a_1_p",
                        "anticommutator": 1
                    }
                ]
            },
            "bosonic_commutators": {
                "description": (
                    "Canonical commutation relations "
                    "for bosonic oscillators"
                ),
                "relations": {
                    "same_type": "[b_i^±, b_j^±] = 0 for all i, j",
                    "conjugate_pair": "[b_i^-, b_j^+] = δ_{ij}"
                },
                "canonical_pairs": [
                    {
                        "index": i,
                        "annihilation": f"b_{i}_m",
                        "creation": f"b_{i}_p",
                        "commutator": 1
                    }
                    for i in range(1, n + 1)
                ]
            },
            "mixed_commutators": {
                "description": (
                    "Commutation relations between "
                    "different oscillator types"
                ),
                "boson_fermion": {
                    "relation": "[b_i^±, a_1^±] = 0",
                    "description": (
                        "Bosonic and fermionic oscillators commute"
                    )
                }
            }
        },
        "central_elements": {
            "kappa": {
                "label": "κ",
                "description": (
                    "Central element for the odd-odd anticommutator. "
                    "Arises from normal-ordering constant -1/2 "
                    "in the expansion of b_k^+b_k^- = sum_{t=k}^n H_t - 1/2. "
                    "Stored as K in the bracket output."
                ),
                "parity": 0,
                "note": "In the implementation, κ is stored as generator 'K'."
            },
            "K": {
                "label": "K",
                "description": (
                    "Central element representing the constant term "
                    "-1/2 from boson number operator expansion. "
                    "Together with κ, spans the 2-dimensional center "
                    "of C(n+1)."
                ),
                "parity": 0,
                "note": "K is the constant term generator in bracket output."
            }
        },
        "basis": {
            "even": even_basis,
            "odd": odd_basis,
            "ordering_convention": ordering
        },
        "parity": {gen: parity[gen] for gen in even_basis + odd_basis},
        "generator_realization": {
            "description": (
                "Standard form expressions with oscillator "
                "realizations. No supplementary fermion a_0. "
                "Odd generators are E_{ε₁±δ_k} = a_1^± b_k^±. "
                "No sqrt(2) factors in coefficients."
            ),
            "ordering": (
                "a_1_p, a_1_m, "
                + ", ".join(f"b_{i}_p, b_{i}_m" for i in range(1, n + 1))
            ),
            "realizations": realizations
        },
        "structure_constants": {
            "description": (
                "Non-zero brackets [X, Y] = sum_Z c_Z Z. "
                "For odd-odd pairs: anticommutator {X,Y}. "
                "Otherwise: commutator [X,Y]. "
                "Coefficients are exact rational numbers "
                "(no sqrt(2)). "
                "Computed via direct Frappat formula "
                "(C_generators.py)."
            ),
            "brackets": brackets
        },
        "metadata": {
            "reference": (
                "Frappat et al., Dictionary on Lie Algebras "
                "and Superalgebras (2000), p.219-220. "
                "C(n+1) = osp(2|2n) oscillator realization."
            ),
            "generated_by": (
                "src/C_generators.py and "
                "src/generate_C_json.py"
            ),
            "computation_method": (
                "Direct Frappat formula with exact rational "
                "arithmetic (Python Fraction). "
                "Sections: Cartan×odd, odd-odd, Cartan×even, "
                "even×even, even×odd, short×short."
            ),
            "basis_convention": {
                "signature": "B1",
                "pbw_ordering": "Option A",
                "description": (
                    "Standard Frappat basis with even roots "
                    "from sp(2n) only (no ε-even roots). "
                    "PBW: κ < odd < even < K."
                )
            }
        }
    }

    return data


def main():
    for n in [1, 2, 3]:
        data = generate_json(n)
        filename = f"C_{n}_structure.json"
        filepath = os.path.join(OUT_DIR, filename)
        with open(filepath, "w") as f:
            json.dump(data, f, indent=2)
        print(f"  ✓ {filename} written ({os.path.getsize(filepath)} bytes)")

    # Write all filenames
    print(f"\nOutput directory: {OUT_DIR}")


if __name__ == "__main__":
    main()
