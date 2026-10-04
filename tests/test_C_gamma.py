from __future__ import annotations

import json
from fractions import Fraction
from pathlib import Path

import pytest

from src.C_gamma import build_gamma_schema


ROOT = Path(__file__).resolve().parents[1]


@pytest.mark.parametrize("rank", (1, 2, 3))
def test_gamma_schema_matches_structure_schema(rank: int) -> None:
    structure_path = ROOT / "data" / f"C_{rank}_structure.json"
    with structure_path.open(encoding="utf-8") as stream:
        structure = json.load(stream)
    gamma = build_gamma_schema(rank, structure)
    parity = structure["parity"]
    basis = set(parity)

    assert gamma["source_schema"] == structure_path.name
    assert gamma["algebra"]["n"] == structure["algebra"]["n"]
    assert gamma["algebra"]["dimension"] == structure["algebra"]["dimension"]
    assert gamma["gb_matrix"]["shape"] == [2, 2 * rank]
    assert gamma["gb_matrix"]["parameter_parity"] == 0
    assert len(gamma["inhomogeneous_deformation"]["relations"]) == 4 * rank

    parameters = {
        parameter
        for row in gamma["gb_matrix"]["entries"].values()
        for parameter in row.values()
    }
    assert len(parameters) == 4 * rank
    assert gamma["gamma_structure"]
    for entry in gamma["gamma_structure"]:
        assert entry["X"] in basis
        assert entry["Y"] in basis
        assert entry["Z"] in basis | {"K"}
        assert entry["gb"] in parameters
        assert Fraction(entry["coeff"])
        output_parity = parity.get(entry["Z"], 0)
        assert output_parity == (
            parity[entry["X"]]
            + parity[entry["Y"]]
            + gamma["gb_matrix"]["parameter_parity"]
            + gamma["inhomogeneous_deformation"]["kappa"]["parity"]
        ) % 2


@pytest.mark.parametrize("rank", (1, 2, 3))
def test_gamma_satisfies_first_order_super_jacobi(rank: int) -> None:
    structure = json.loads(
        (ROOT / "data" / f"C_{rank}_structure.json").read_text(encoding="utf-8")
    )
    gamma = build_gamma_schema(rank, structure)
    basis = list(structure["generator_realization"]["realizations"])
    index = {label: position for position, label in enumerate(basis)}
    parity = structure["parity"]
    brackets: dict[tuple[str, str], dict[str, Fraction]] = {}
    for entry in structure["structure_constants"]:
        brackets.setdefault((entry["X"], entry["Y"]), {})[entry["Z"]] = Fraction(
            entry["coeff"]
        )
    gamma_brackets: dict[tuple[str, str], dict[str, dict[str, Fraction]]] = {}
    for entry in gamma["gamma_structure"]:
        gamma_brackets.setdefault((entry["X"], entry["Y"]), {}).setdefault(
            entry["gb"], {}
        )[entry["Z"]] = Fraction(entry["coeff"])

    def bracket(left: str, right: str) -> dict[str, Fraction]:
        if index[left] <= index[right]:
            return brackets.get((left, right), {})
        sign = -1 if (parity[left] * parity[right]) % 2 == 0 else 1
        return {
            label: sign * coefficient
            for label, coefficient in brackets.get((right, left), {}).items()
        }

    def gamma_bracket(left: str, right: str) -> dict[str, dict[str, Fraction]]:
        if index[left] <= index[right]:
            return gamma_brackets.get((left, right), {})
        sign = -1 if (parity[left] * parity[right]) % 2 == 0 else 1
        return {
            parameter: {
                label: sign * coefficient
                for label, coefficient in vector.items()
            }
            for parameter, vector in gamma_brackets.get((right, left), {}).items()
        }

    def add(
        target: dict[str, dict[str, Fraction]],
        source: dict[str, dict[str, Fraction]],
        scale: Fraction | int,
    ) -> None:
        for parameter, vector in source.items():
            destination = target.setdefault(parameter, {})
            for label, coefficient in vector.items():
                destination[label] = destination.get(label, Fraction(0)) + (
                    scale * coefficient
                )
                if not destination[label]:
                    del destination[label]
            if not destination:
                del target[parameter]

    def first_order_jacobi_term(
        x: str, y: str, z: str
    ) -> dict[str, dict[str, Fraction]]:
        result: dict[str, dict[str, Fraction]] = {}
        for middle, coefficient in bracket(y, z).items():
            add(result, gamma_bracket(x, middle), coefficient)
        for parameter, vector in gamma_bracket(y, z).items():
            for middle, coefficient in vector.items():
                if middle == "K":
                    continue
                for output, outer_coefficient in bracket(x, middle).items():
                    destination = result.setdefault(parameter, {})
                    destination[output] = destination.get(output, Fraction(0)) + (
                        (-1) ** parity[x] * coefficient * outer_coefficient
                    )
                    if not destination[output]:
                        del destination[output]
                    if not destination:
                        del result[parameter]
        return result

    for x in basis:
        for y in basis:
            for z in basis:
                jacobiator: dict[str, dict[str, Fraction]] = {}
                for left, right, third, sign in (
                    (x, y, z, (-1) ** (parity[x] * parity[z])),
                    (y, z, x, (-1) ** (parity[y] * parity[x])),
                    (z, x, y, (-1) ** (parity[z] * parity[y])),
                ):
                    add(
                        jacobiator,
                        first_order_jacobi_term(left, right, third),
                        sign,
                    )
                assert not jacobiator, (x, y, z, jacobiator)
