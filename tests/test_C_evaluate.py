import json
import os
import sys

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "src"))

from C_evaluate import PROFILES, build_schema3, check_schema3, evaluated_filename  # noqa: E402


@pytest.mark.parametrize("n", [1, 2, 3])
@pytest.mark.parametrize("profile", PROFILES)
def test_stored_files(n, profile):
    with open(os.path.join(ROOT, "data", evaluated_filename(n, profile))) as fh:
        stored = json.load(fh)
    fresh = build_schema3(n, profile, date=stored["metadata"]["generation_date"])
    assert stored == json.loads(json.dumps(fresh))
    chk = check_schema3(n, stored)
    assert chk == {"substitution": True, "undeformed_eq_schema1": True,
                   "deformed_jacobi_failures": 0, "labels": True}
    assert len(stored["gb_values"]) == 4 * n


def test_zero_profile_is_undeformed():
    s3 = build_schema3(2, "zero", date="t")
    assert s3["evaluated_deformation"]["entries"] == []


def test_sign_flip_linearity():
    a = build_schema3(1, "allplus", date="t")["evaluated_deformation"]["entries"]
    b = build_schema3(1, "allminus", date="t")["evaluated_deformation"]["entries"]
    assert [(e["X"], e["Y"], e["Z"]) for e in a] == [(e["X"], e["Y"], e["Z"]) for e in b]
    assert all(e["coeff"] == ("-" + f["coeff"]).replace("--", "") for e, f in zip(b, a))
