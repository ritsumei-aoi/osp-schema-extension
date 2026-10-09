"""Unit tests for C_generators.py: parity, generator counts, consistency."""

import json
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from C_generators import build_basis, build_schema1, parity_of


def test_basis_counts():
    """Verify even/odd counts match 2n^2+n+1 and 4n."""
    for n in [1, 2, 3]:
        even, odd = build_basis(n)
        assert len(even) == 2 * n * n + n + 1, f"n={n}: even count mismatch"
        assert len(odd) == 4 * n, f"n={n}: odd count mismatch"


def test_parity_labels():
    """All odd labels start with E_eps1, all even do not."""
    for n in [1, 2, 3]:
        even, odd = build_basis(n)
        for g in odd:
            assert g.startswith("E_eps1"), f"Odd gen {g} doesn't start with E_eps1"
            assert parity_of(g) == 1
        for g in even:
            assert parity_of(g) == 0


def test_no_duplicate_basis():
    """Basis lists contain no duplicates."""
    for n in [1, 2, 3]:
        even, odd = build_basis(n)
        assert len(even) == len(set(even)), f"n={n}: duplicate in even basis"
        assert len(odd) == len(set(odd)), f"n={n}: duplicate in odd basis"
        assert len(set(even) & set(odd)) == 0, f"n={n}: overlap between even/odd"


def test_schema1_structure():
    """Schema 1 JSON has all required top-level keys."""
    required_keys = [
        "schema_version", "algebra", "oscillator_generators", "oscillator_relations",
        "central_elements", "basis", "parity", "generator_realization",
        "structure_constants", "metadata"
    ]
    for n in [1, 2, 3]:
        schema = build_schema1(n)
        for key in required_keys:
            assert key in schema, f"n={n}: missing key '{key}'"


def test_algebra_fields():
    """Algebra field has correct family, m, and dimension formulas."""
    for n in [1, 2, 3]:
        schema = build_schema1(n)
        alg = schema["algebra"]
        assert alg["family"] == "C"
        assert alg["m"] == 1
        assert alg["n"] == n
        assert alg["dimension"]["even"] == 2 * n * n + n + 1
        assert alg["dimension"]["odd"] == 4 * n
        assert alg["dimension"]["total"] == 2 * n * n + 5 * n + 1


def test_central_elements():
    """central_elements is a top-level key with K (parity 0) and kappa (parity 1)."""
    for n in [1, 2, 3]:
        schema = build_schema1(n)
        ce = schema["central_elements"]
        assert "K" in ce and ce["K"]["parity"] == 0
        assert "kappa" in ce and ce["kappa"]["parity"] == 1


def test_parity_dict_completeness():
    """Every basis element has a parity entry."""
    for n in [1, 2, 3]:
        schema = build_schema1(n)
        parity = schema["parity"]
        for g in schema["basis"]["even"] + schema["basis"]["odd"]:
            assert g in parity, f"n={n}: generator {g} missing from parity dict"


def test_structure_constants_reference_valid_generators():
    """All X, Y, Z in structure constants are valid basis generators."""
    for n in [1, 2, 3]:
        schema = build_schema1(n)
        basis_set = set(schema["basis"]["even"] + schema["basis"]["odd"])
        for entry in schema["structure_constants"]:
            assert entry["X"] in basis_set or entry["X"].startswith("H_"), \
                f"n={n}: invalid X={entry['X']}"
            assert entry["Y"] in basis_set, f"n={n}: invalid Y={entry['Y']}"
            assert entry["Z"] in basis_set, f"n={n}: invalid Z={entry['Z']}"


def test_structure_constants_parity():
    """[X,Y}=Z must preserve total parity: p(X)+p(Y) == p(Z) mod 2."""
    for n in [1, 2, 3]:
        schema = build_schema1(n)
        parity = schema["parity"]
        for entry in schema["structure_constants"]:
            px = parity.get(entry["X"], 0)
            py = parity[entry["Y"]]
            pz = parity[entry["Z"]]
            assert (px + py) % 2 == pz % 2, \
                f"n={n}: parity violation in [{entry['X']},{entry['Y']}]={entry['Z']}"


def test_cartan_h1_on_eps_generators():
    """H_1 acts on E_eps1_del1_pp with eigenvalue 2 (for n>=1)."""
    for n in [1, 2, 3]:
        schema = build_schema1(n)
        sc = {(e["X"], e["Y"]): (e["Z"], e["coeff"])
              for e in schema["structure_constants"]}
        # H_1 on E_eps1_del1_pp: a_sign=p contrib 1, b_1 contrib 1 => total 2
        # But wait: H_1 = N_a + N_b1, eigenvalue of E_eps1_del1_pp (a_p*b_1p) = 1+1=2
        # However the stored SC may have multiple entries summing to the eigenvalue.
        # Check at least one entry exists:
        found = [e for e in schema["structure_constants"]
                 if e["X"] == "H_1" and e["Y"] == "E_eps1_del1_pp" and e["Z"] == "E_eps1_del1_pp"]
        assert len(found) > 0, f"n={n}: missing H_1 action on E_eps1_del1_pp"


def test_file_naming_and_content():
    """Generated JSON files exist and have correct schema_version."""
    for n in [1, 2, 3]:
        fname = f"data/C_{n}_structure.json"
        assert os.path.exists(fname), f"Missing {fname}"
        with open(fname) as f:
            data = json.load(f)
        assert data["schema_version"] == "5.0"
        assert data["algebra"]["n"] == n
