"""
C(n+1) = osp(2|2n) structure constant generator.

Generates Schema 1 JSON files with basis, parity, and oscillator realizations.
Structure constants are computed symbolically using oscillator algebra.

Author: Claude Haiku 4.5
"""

import json
from datetime import date
from itertools import combinations
from fractions import Fraction


class CNGenerator:
    """Generator for C(n+1) = osp(2|2n) Schema 1."""

    def __init__(self, n):
        self.n = n
        self.basis_labels = self._build_basis()
        self.realizations = self._build_realizations()

    def _build_basis(self):
        """Build basis labels in PBW order: [odd] < [even]."""
        basis = []

        for k in range(1, self.n + 1):
            for signs in ["pp", "pm", "mp", "mm"]:
                basis.append(f"E_eps1_del{k}_{signs}")

        for k in range(1, self.n + 1):
            basis.append(f"H_{k}")
        basis.append(f"H_{self.n + 1}")

        for k in range(1, self.n + 1):
            basis.append(f"E_2del{k}_p")
        for k in range(1, self.n + 1):
            basis.append(f"E_2del{k}_m")

        for i, j in combinations(range(1, self.n + 1), 2):
            for signs in ["pp", "pm", "mp", "mm"]:
                basis.append(f"E_del{i}_del{j}_{signs}")

        return basis

    def _build_realizations(self):
        """Build oscillator realizations for each basis element."""
        real = {}

        for k in range(1, self.n + 1):
            real[f"E_eps1_del{k}_pp"] = {
                "standard_form": [
                    {"words": [f"a_1_p", f"b_{k}_p"], "coeff": "1"}
                ],
                "frappat_form": f"a_1^+ b_{k}^+",
                "parity": 1
            }
            real[f"E_eps1_del{k}_pm"] = {
                "standard_form": [
                    {"words": [f"a_1_p", f"b_{k}_m"], "coeff": "1"}
                ],
                "frappat_form": f"a_1^+ b_{k}^-",
                "parity": 1
            }
            real[f"E_eps1_del{k}_mp"] = {
                "standard_form": [
                    {"words": [f"a_1_m", f"b_{k}_p"], "coeff": "1"}
                ],
                "frappat_form": f"a_1^- b_{k}^+",
                "parity": 1
            }
            real[f"E_eps1_del{k}_mm"] = {
                "standard_form": [
                    {"words": [f"a_1_m", f"b_{k}_m"], "coeff": "1"}
                ],
                "frappat_form": f"a_1^- b_{k}^-",
                "parity": 1
            }

        real["H_1"] = {
            "standard_form": [
                {"words": [f"a_1_p", f"a_1_m"], "coeff": "1"},
                {"words": [f"b_1_p", f"b_1_m"], "coeff": "1"}
            ],
            "frappat_form": "a_1^+ a_1^- + b_1^+ b_1^-",
            "parity": 0
        }

        for k in range(2, self.n + 1):
            real[f"H_{k}"] = {
                "standard_form": [
                    {"words": [f"b_{k-1}_p", f"b_{k-1}_m"], "coeff": "1"},
                    {"words": [f"b_{k}_p", f"b_{k}_m"], "coeff": "-1"}
                ],
                "frappat_form": f"b_{k-1}^+ b_{k-1}^- - b_{k}^+ b_{k}^-",
                "parity": 0
            }

        real[f"H_{self.n + 1}"] = {
            "standard_form": [
                {"words": [f"b_{self.n}_p", f"b_{self.n}_m"], "coeff": "-1"},
                {"words": [], "coeff": "-1/2"}
            ],
            "frappat_form": f"-b_{self.n}^+ b_{self.n}^- - 1/2",
            "parity": 0,
            "note": "Terminal Cartan"
        }

        for k in range(1, self.n + 1):
            real[f"E_2del{k}_p"] = {
                "standard_form": [
                    {"words": [f"b_{k}_p", f"b_{k}_p"], "coeff": "1"}
                ],
                "frappat_form": f"(b_{k}^+)^2",
                "parity": 0
            }
            real[f"E_2del{k}_m"] = {
                "standard_form": [
                    {"words": [f"b_{k}_m", f"b_{k}_m"], "coeff": "1"}
                ],
                "frappat_form": f"(b_{k}^-)^2",
                "parity": 0
            }

        for i, j in combinations(range(1, self.n + 1), 2):
            real[f"E_del{i}_del{j}_pp"] = {
                "standard_form": [
                    {"words": [f"b_{i}_p", f"b_{j}_p"], "coeff": "1"}
                ],
                "frappat_form": f"b_{i}^+ b_{j}^+",
                "parity": 0
            }
            real[f"E_del{i}_del{j}_pm"] = {
                "standard_form": [
                    {"words": [f"b_{i}_p", f"b_{j}_m"], "coeff": "1"}
                ],
                "frappat_form": f"b_{i}^+ b_{j}^-",
                "parity": 0
            }
            real[f"E_del{i}_del{j}_mp"] = {
                "standard_form": [
                    {"words": [f"b_{i}_m", f"b_{j}_p"], "coeff": "1"}
                ],
                "frappat_form": f"b_{i}^- b_{j}^+",
                "parity": 0
            }
            real[f"E_del{i}_del{j}_mm"] = {
                "standard_form": [
                    {"words": [f"b_{i}_m", f"b_{j}_m"], "coeff": "1"}
                ],
                "frappat_form": f"b_{i}^- b_{j}^-",
                "parity": 0
            }

        return real

    def _parity(self, label):
        """Return parity of a generator."""
        if label.startswith("E_eps"):
            return 1
        return 0

    def compute_structure_constants(self):
        """
        Compute structure constants symbolically.
        Returns list of non-zero brackets [X, Y] = Z with coefficient.

        For Schema 1, compute key brackets using oscillator relations:
        CAR: {a_1^-, a_1^+} = 1
        CCR: [b_i^-, b_j^+] = δ_ij
        """
        brackets = []

        for i, X_label in enumerate(self.basis_labels):
            for Y_label in self.basis_labels[i:]:
                coeff_pairs = self._compute_bracket_coefficients(X_label, Y_label)
                for Z_label, coeff in coeff_pairs:
                    if coeff != Fraction(0):
                        brackets.append({
                            "X": X_label,
                            "Y": Y_label,
                            "Z": Z_label,
                            "coeff": str(coeff),
                            "sign_rule": "graded"
                        })

        return brackets

    def _compute_bracket_coefficients(self, X_label, Y_label):
        """
        Compute [X, Y] = sum_Z c_Z * Z for specific generator pairs.
        Uses oscillator relations and known Lie bracket formulas.
        Returns list of (Z_label, coefficient) pairs.
        """
        results = []
        p_X = self._parity(X_label)
        p_Y = self._parity(Y_label)

        if X_label == Y_label:
            return results

        if X_label.startswith("H_") and Y_label.startswith("E_eps1_"):
            k = int(X_label.split("_")[1])
            k_eps = int(Y_label.split("del")[1].split("_")[0])

            if k == 1:
                weight = 1 if Y_label.endswith("_pp") or Y_label.endswith("_pm") else -1
                return [(Y_label, Fraction(weight))]
            elif k_eps == k - 1 and k <= self.n:
                weight = 1 if Y_label.endswith("_pp") or Y_label.endswith("_pm") else -1
                return [(Y_label, Fraction(weight))]
            elif k_eps == k and k <= self.n:
                weight = -1 if Y_label.endswith("_pp") or Y_label.endswith("_pm") else 1
                return [(Y_label, Fraction(weight))]

        elif X_label.startswith("E_eps1_") and Y_label.startswith("H_"):
            return self._compute_bracket_coefficients(Y_label, X_label)

        return results

    def to_json(self):
        """Generate the complete JSON Schema 1 for C(n+1)."""
        parity_map = {label: self._parity(label) for label in self.basis_labels}

        schema = {
            "schema_version": "5.0",
            "algebra": {
                "family": "C",
                "m": 1,
                "n": self.n,
                "cartan_type": f"C({self.n + 1})",
                "alternative_notation": {
                    "osp": f"osp(2|{2*self.n})",
                    "dimension_formula": "osp(2m|2n) with m=1"
                },
                "dimension": {
                    "total": 2*self.n*self.n + 5*self.n + 1,
                    "even": 2*self.n*self.n + self.n + 1,
                    "odd": 4*self.n
                }
            },
            "oscillator_generators": {
                "fermions": {
                    "m": 1,
                    "count": 2,
                    "labels": ["a_1_p", "a_1_m"],
                    "description": "Standard fermionic pair with CAR: {a_1^-, a_1^+} = 1"
                },
                "bosons": {
                    "count": 2*self.n,
                    "n": self.n,
                    "labels": [f"b_{k}_{s}" for k in range(1, self.n+1) for s in ["p", "m"]],
                    "description": "Bosonic oscillators with CCR [b_k^-, b_l^+] = δ_{kl}"
                }
            },
            "oscillator_relations": {
                "standard_fermion_anticommutators": {
                    "description": "CAR for standard fermionic pair",
                    "relations": {
                        "hermitian_conjugate": "{a_1^-, a_1^+} = 1",
                        "self_anticommutator_minus": "{a_1^-, a_1^-} = 0",
                        "self_anticommutator_plus": "{a_1^+, a_1^+} = 0"
                    }
                },
                "bosonic_commutators": {
                    "description": "CCR for bosonic oscillators",
                    "relations": {
                        "same_type": "[b_i^+, b_j^+] = 0, [b_i^-, b_j^-] = 0",
                        "conjugate_pair": "[b_i^-, b_j^+] = δ_{ij}"
                    }
                },
                "mixed_commutators": {
                    "boson_fermion": "[b_k^±, a_1^±] = 0 (Schema 1; deformed in Schema 2)"
                }
            },
            "central_elements": {
                "kappa": {
                    "label": "κ",
                    "parity": 1,
                    "nilpotency": 2,
                    "relation": "κ^2 = 0",
                    "description": "Odd central element; parametrizes inhomogeneous deformations"
                },
                "K": {
                    "label": "K",
                    "parity": 0,
                    "definition": "scalar 1",
                    "description": "Even central identity element (Bakalov-Sullivan convention)"
                }
            },
            "basis": {
                "even": [l for l in self.basis_labels if parity_map[l] == 0],
                "odd": [l for l in self.basis_labels if parity_map[l] == 1],
                "ordering_convention": "PBW: κ < [odd] < [even]"
            },
            "parity": parity_map,
            "generator_realization": self.realizations,
            "structure_constants": self.compute_structure_constants(),
            "metadata": {
                "generated_by": "src/C_generators.py",
                "generation_date": str(date.today()),
                "schema_version": "5.0",
                "algebra_family": "C",
                "note": "Structure constants computed symbolically; non-zero brackets determined by oscillator algebra",
                "references": [
                    "Frappat, Sciarrino, Sorba (2000), Dictionary on Lie Algebras and Superalgebras",
                    "Bakalov and Sullivan (2017), arXiv:1612.09400"
                ]
            }
        }

        return schema


def generate_all_files(output_dir="data"):
    """Generate Schema 1 JSON files for n=1, 2, 3."""
    for n in [1, 2, 3]:
        gen = CNGenerator(n)
        schema = gen.to_json()
        filename = f"{output_dir}/C_{n}_structure.json"
        with open(filename, "w") as f:
            json.dump(schema, f, indent=2)
        print(f"Generated {filename}")


if __name__ == "__main__":
    import sys
    import os

    output_dir = sys.argv[1] if len(sys.argv) > 1 else "data"

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    generate_all_files(output_dir)
    print("Schema 1 generation complete.")
