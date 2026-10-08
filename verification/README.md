# Verification code for the gb-deformation of C(n+1) = osp(2|2n)

Pure Python 3 (standard library + `sympy` for one small matrix inverse + `numpy` for the
Jacobi residuals). All deformation-theoretic identities are checked with exact arithmetic
in Q[gb].

| file | purpose |
|---|---|
| `osc_algebra.py` | normal-ordered model of U(A_gb): a+, a-, b_j^±, odd central kappa (kappa^2 = 0), K = 1, relations `[b_j^s, a^sig] = -gb[a^sig,b_j^s] kappa` |
| `cn1.py` | basis of C(n+1) from `docs/math/Cn1_definition.md`, decomposition of quadratics as g ⊕ C, structure constants, the cochain gamma_gb, the explicit primitive f_gb, the coboundary operator delta |
| `run_verification.py` | driver for n = 1, 2, 3; writes `artifacts/C{n+1}_osp2_{2n}.json` and `artifacts/verification_summary.json` |
| `check_artifact.py` | independent re-verification of gamma = delta f using **only** the JSON artifacts |
| `test_report_formulas.py` | checks the closed-form general-n formulas quoted in `docs/issues/mathematical_proof.md` against the computed data |

```
python3 verification/run_verification.py
python3 verification/check_artifact.py
python3 verification/test_report_formulas.py
```

Conventions are documented in the module docstrings and inside each JSON artifact (`conventions` key).
