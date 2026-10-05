# Supplementary Session Metrics

**Run ID**: study/thm01-R-opus46-b09-C
**Model**: Claude Opus 4.6

- **Total Execution Time (Wall clock)**: 2 context windows (compaction boundary required continuation)
- **Total Thinking Time**: Not directly measurable from agent interface
- **Token Usage (if known)**: Approximately 15M token budget, ~0.5M consumed in second session
- **Any other session-level statistics available in your interface**:
  - Scripts executed: verify_triviality.py, verify_general_n.py, check_cocycle.py, test_n1.py
  - Jacobi identity max violations: 0.0 (n=1 hand), 2.66e-15 (n=1 algebraic), 4.44e-15 (n=2), 5.77e-15 (n=3)
  - Triviality residuals: all < 2.1e-14
  - Major code revisions: 3 (Fock approach -> algebraic, derivative method -> deformed-commutator, scalar projection fix)
