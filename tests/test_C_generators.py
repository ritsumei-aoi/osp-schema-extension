"""Unit tests for src/C_generators.py (I03)."""

import json
import sys
from fractions import Fraction
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

import C_generators as C  # noqa: E402


DIMS = {1: (4, 4), 2: (11, 8), 3: (22, 12)}  # n -> (even, odd)


@pytest.mark.parametrize("n", [1, 2, 3])
def test_generator_counts(n):
    labels, parity, _ = C.structure(n)
    even = [l for l in labels if parity[l] == 0]
    odd = [l for l in labels if parity[l] == 1]
    assert (len(even), len(odd)) == DIMS[n]
    assert len(set(labels)) == len(labels)


@pytest.mark.parametrize("n", [1, 2, 3])
def test_parity_of_labels(n):
    labels, parity, _ = C.structure(n)
    for l in labels:
        if l.startswith("E_eps1_"):
            assert parity[l] == 1
        else:
            assert parity[l] == 0


@pytest.mark.parametrize("n", [1, 2, 3])
def test_no_central_term(n):
    # The realization closes on the basis: brackets never produce K.
    _, _, brackets = C.structure(n)
    assert all("K" not in terms for terms in brackets.values())


@pytest.mark.parametrize("n", [1, 2, 3])
def test_brackets_respect_parity(n):
    # [even, even] lands in even, [even, odd] and [odd, odd] follow the grading.
    labels, parity, brackets = C.structure(n)
    for (X, Y), terms in brackets.items():
        for Z in terms:
            expected = (parity[X] + parity[Y]) % 2
            assert parity[Z] == expected, (X, Y, Z)


def test_n1_known_values():
    _, _, brackets = C.structure(1)
    assert brackets[("E_2del1_p", "E_2del1_m")] == {"H_1": Fraction(-1)}
    assert brackets[("H_1", "E_2del1_p")] == {"E_2del1_p": Fraction(2)}
    assert brackets[("E_eps1_del1_pm", "E_eps1_del1_mm")] == {"E_2del1_m": Fraction(2)}


@pytest.mark.parametrize("n", [1, 2, 3])
def test_json_output_matches_generator(n):
    data = json.loads((ROOT / "data" / f"C_{n}_structure.json").read_text())
    assert data["schema_version"] == "5.0"
    assert data["algebra"]["family"] == "C"
    assert data["algebra"]["m"] == 1
    assert len(data["basis"]["even"]) == DIMS[n][0]
    assert len(data["basis"]["odd"]) == DIMS[n][1]
    assert data == C.to_json(n)
