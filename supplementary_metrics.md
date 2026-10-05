# Supplementary Session Metrics

**Run ID**: study/thm01-R-opus46-b09-C
**Model**: Claude Opus 4.6

- **Total Execution Time (Wall clock)**: 2 context windows (compaction boundary required continuation via session summary)
- **Total Thinking Time**: Not directly measurable from agent interface
- **Token Usage (if known)**: Approximately 15M token budget per session; first session consumed most of the budget before compaction, second session used ~1M tokens
- **Any other session-level statistics available in your interface**:
  - Scripts executed: verify_triviality.py, verify_general_n.py, check_cocycle.py, test_n1.py
  - Total Python script runs: ~15 (including debugging iterations)
  - Jacobi identity max violations: 0.0 (n=1 hand-derived), 2.66e-15 (n=1 algebraic), 4.44e-15 (n=2), 5.77e-15 (n=3)
  - Triviality residuals (max over all gb basis vectors):
    - n=1: 2.56e-14
    - n=2: 5.77e-15
    - n=3: 2.06e-14
  - Rank analysis results:
    - n=1: rank(delta) = 28, rank([delta|gamma]) = 28, f-dim = 32, gb-dim = 4
    - n=2: rank(delta) = 168, rank([delta|gamma]) = 168, f-dim = 176, gb-dim = 8
    - n=3: rank(delta) = 516, rank([delta|gamma]) = 516, f-dim = 528, gb-dim = 12
  - Major code revisions: 3
    1. Fock space numerical approach -> purely algebraic bilinear computation
    2. Derivative/shift gamma method -> deformed-commutator gamma method
    3. Full lstsq projection (with scalar row) -> scalar-free projection (ignoring identity component)
  - Files produced: 7 (verify_triviality.py, verify_general_n.py, check_cocycle.py, test_n1.py, verification_artifacts.json, mathematical_proof.md, final_reflection.md)
