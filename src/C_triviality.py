"""Compare evaluated C(n+1) gamma data with the coboundary image."""

from __future__ import annotations

import argparse
import json
from fractions import Fraction
from pathlib import Path


def _read(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def analyze_rank(data_directory: Path, n: int) -> dict:
    evaluated = _read(data_directory / f"C_{n}_evaluated.json")
    gamma = _read(data_directory / f"C_{n}_gamma.json")
    coboundary = _read(data_directory / f"C_{n}_coboundary.json")
    if (
        evaluated["algebra"] != gamma["algebra"]
        or evaluated["algebra"] != coboundary["algebra"]
    ):
        raise ValueError(f"rank-{n} Layer 3/4 algebra metadata does not match")

    parameter_labels = [
        item["label"] for item in gamma["gb_matrix"]["parameters"]
    ]
    evaluated_terms = evaluated["deformation_evaluation"]["gamma_coefficients"]
    coboundary_terms = coboundary["coboundary"]["coefficients"]
    if any(
        value != 1
        for value in evaluated["deformation_evaluation"]["parameter_assignment"].values()
    ):
        raise ValueError(f"rank-{n} Layer 3 file is not the all-plus profile")
    if not gamma["consistency"]["basis_matches_schema_1"]:
        raise ValueError(f"rank-{n} Schema 2 basis was not verified")
    coboundary_support = {
        (term["X"], term["Y"], term["Z"]) for term in coboundary_terms
    }
    central_terms = [term for term in evaluated_terms if term["Z"] == "K"]
    unsupported = [
        term
        for term in evaluated_terms
        if (term["X"], term["Y"], term["Z"]) not in coboundary_support
    ]
    if any(term["Z"] == "K" for term in coboundary_terms):
        raise ValueError("Schema 4 unexpectedly contains the identity K")

    symbolic_kappa: dict[tuple[str, str], dict[str, Fraction]] = {}
    for term in gamma["inhomogeneous_deformation"]["gamma_coefficients"]:
        if term["Z"] == "K":
            pair = (term["X"], term["Y"])
            row = symbolic_kappa.setdefault(pair, {})
            parameter = term["gb_parameter"]
            row[parameter] = row.get(parameter, Fraction()) + Fraction(term["coeff"])
    symbolic_kappa = {
        pair: {parameter: coefficient for parameter, coefficient in row.items() if coefficient}
        for pair, row in symbolic_kappa.items()
    }

    isolating_rows = []
    for j in range(1, n + 1):
        expected = (
            (
                (f"E_2del{j}_p", f"E_eps1_del{j}_pm"),
                f"gb_a_1_p_b_{j}_p",
                Fraction(-1),
            ),
            (
                (f"E_2del{j}_m", f"E_eps1_del{j}_pp"),
                f"gb_a_1_p_b_{j}_m",
                Fraction(1),
            ),
            (
                (f"E_eps1_del{j}_mm", f"E_2del{j}_p"),
                f"gb_a_1_m_b_{j}_p",
                Fraction(1),
            ),
            (
                (f"E_eps1_del{j}_mp", f"E_2del{j}_m"),
                f"gb_a_1_m_b_{j}_m",
                Fraction(-1),
            ),
        )
        for pair, parameter, coefficient in expected:
            actual = symbolic_kappa.get(pair, {})
            if actual != {parameter: coefficient}:
                raise ValueError(
                    f"rank-{n} central row {pair} is not the expected "
                    f"isolating equation: {actual}"
                )
            isolating_rows.append(
                {
                    "X": pair[0],
                    "Y": pair[1],
                    "gb_parameter": parameter,
                    "coeff": str(coefficient),
                }
            )

    if len({row["gb_parameter"] for row in isolating_rows}) != len(parameter_labels):
        raise ValueError(f"rank-{n} central equations do not isolate every gb")
    status = "non-trivial" if central_terms else "trivial"
    zero_specialization = [
        Fraction(term["coeff"]) * 0
        for term in gamma["inhomogeneous_deformation"]["gamma_coefficients"]
    ]
    zero_coboundary = [Fraction(term["coeff"]) * 0 for term in coboundary_terms]
    zero_assignment_status = (
        "trivial"
        if not any(zero_specialization) and not any(zero_coboundary)
        else "inconsistent"
    )

    return {
        "rank": n,
        "profile": evaluated["deformation_evaluation"]["profile"],
        "evaluated_gamma_term_count": len(evaluated_terms),
        "evaluated_nonzero_K_term_count": len(central_terms),
        "evaluated_terms_outside_coboundary_support": len(unsupported),
        "independent_gb_parameters": len(parameter_labels),
        "central_constraint_rank": len(isolating_rows),
        "all_plus_status": status,
        "zero_assignment_status": zero_assignment_status,
        "central_examples": central_terms[:4],
        "isolating_rows": isolating_rows,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--data-dir",
        type=Path,
        default=Path(__file__).resolve().parents[1] / "data",
    )
    args = parser.parse_args()

    overall_pass = True
    for n in (1, 2, 3):
        report = analyze_rank(args.data_dir, n)
        print(
            f"C({n + 1}): all-plus={report['all_plus_status']}; "
            f"gamma terms={report['evaluated_gamma_term_count']}; "
            f"nonzero K terms={report['evaluated_nonzero_K_term_count']}; "
            f"terms outside coboundary support="
            f"{report['evaluated_terms_outside_coboundary_support']}; "
            f"central constraint rank="
            f"{report['central_constraint_rank']}/"
            f"{report['independent_gb_parameters']}; "
            f"zero-assignment={report['zero_assignment_status']}"
        )
        for term in report["central_examples"][:2]:
            print(
                f"  witness: ({term['X']}, {term['Y']}) -> "
                f"{term['coeff']} K"
            )
        overall_pass = overall_pass and (
            report["central_constraint_rank"]
            == report["independent_gb_parameters"]
            and report["all_plus_status"] == "non-trivial"
        )
    print(f"Overall comparison: {'PASS' if overall_pass else 'FAIL'}")
    return 0 if overall_pass else 1


if __name__ == "__main__":
    raise SystemExit(main())
