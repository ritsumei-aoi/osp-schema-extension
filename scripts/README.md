# Verification code and artifacts

| file | purpose |
|---|---|
| `osc_algebra.py` | exact normal-ordering engine for the deformed oscillator algebra U(A_gb)/(K-1) with odd central nilpotent kappa and symbolic gb |
| `test_engine.py` | hand-checked relations, including Lemma 1 (shifted bosons satisfy the undeformed relations) |
| `verify_triviality.py` | builds C(n+1), extracts structure constants and gamma_gb, verifies the closed-form f_gb and lambda_gb, certifies ker(delta), writes `artifacts/cn1_n{n}.json` and `artifacts/summary.json` (n = 1, 2, 3) |
| `recheck_artifacts.py` | engine-independent re-verification using only the JSON files, plus a from-scratch solvability check of delta(phi) = gamma |

Run from the repository root:

```
python3 scripts/test_engine.py
python3 scripts/verify_triviality.py
python3 scripts/recheck_artifacts.py
```

Requirements: Python 3, numpy (mod-p rank only). The artifact format is documented in
`docs/issues/mathematical_proof.md`, Section 7.2, and in the `conventions` block of each JSON file.
