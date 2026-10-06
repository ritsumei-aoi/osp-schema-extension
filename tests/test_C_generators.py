import json
import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
from C_generators import CAlgebra, basis_labels, schema1  # noqa: E402

DIMS = {1: (4, 4), 2: (11, 8), 3: (22, 12)}


@pytest.mark.parametrize("n", [1, 2, 3])
def test_counts_and_parity(n):
    even, odd = basis_labels(n)
    assert (len(even), len(odd)) == DIMS[n]
    assert len(even) == 2 * n * n + n + 1 and len(odd) == 4 * n
    assert len(set(even + odd)) == len(even) + len(odd)
    alg = CAlgebra(n)
    assert all(alg.parity[l] == 1 for l in odd) and all(alg.parity[l] == 0 for l in even)


@pytest.mark.parametrize("n", [1, 2, 3])
def test_closure_and_parity_of_brackets(n):
    alg = CAlgebra(n)
    for X in alg.labels:
        for Y in alg.labels:
            res = alg.bracket(X, Y)  # raises if not closed on the basis
            for Z in res:
                assert alg.parity[Z] == (alg.parity[X] + alg.parity[Y]) % 2


@pytest.mark.parametrize("n", [1, 2, 3])
def test_schema_fields(n):
    d = schema1(n)
    assert d["algebra"]["family"] == "C" and d["algebra"]["m"] == 1
    assert d["central_elements"]["kappa"]["parity"] == 1
    assert d["central_elements"]["K"]["parity"] == 0
    assert set(d["oscillator_generators"]) == {"fermions", "bosons"}
    assert d["oscillator_generators"]["fermions"]["labels"] == ["a_1_p", "a_1_m"]
    assert d["algebra"]["dimension"]["total"] == 2 * n * n + 5 * n + 1


def test_known_brackets_n1():
    alg = CAlgebra(1)
    # {a+ b+, a- b-} = N_b + 1 - N_a = -H_1 - 2 H_2 (hand computation)
    assert alg.bracket("E_eps1_del1_pp", "E_eps1_del1_mm") == {"H_1": -1, "H_2": -2}
    assert alg.bracket("E_eps1_del1_pp", "E_eps1_del1_pp") == {}
    assert alg.bracket("E_2del1_p", "E_2del1_m") == {"H_2": 4}
    assert alg.bracket("H_1", "E_eps1_del1_pp") == {"E_eps1_del1_pp": 2}
    assert alg.bracket("H_2", "E_2del1_p") == {"E_2del1_p": -2}


@pytest.mark.parametrize("n", [1, 2, 3])
def test_data_files_match_generator(n):
    p = os.path.join(os.path.dirname(__file__), "..", "data", f"C_{n}_structure.json")
    assert json.load(open(p)) == json.loads(json.dumps(schema1(n)))
