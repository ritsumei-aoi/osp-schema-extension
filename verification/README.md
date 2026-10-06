# Verification artifacts: C(n+1) inhomogeneous deformation

Run it with Python 3 (standard library only):

    python3 verification/cn1_triviality.py 1 2 3

The script writes `artifacts/cn1_n{n}_{symmetrized|cn1}.json` and `artifacts/summary.json`.
`docs/issues/mathematical_proof.md` §4 describes the JSON fields. It also explains how to re-check
`gamma = delta f` from the stored structure constants, the gamma coefficients and `closed_form_f`.
