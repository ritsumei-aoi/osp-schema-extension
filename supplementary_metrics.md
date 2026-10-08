# Supplementary Session Metrics

**Run ID**: study/thm01-R-haiku55-b03-C
**Model**: Claude Haiku 5.5 (claude-haiku-5-5)

Source: this session's interface, not gemini-cli. The template asks for gemini-cli statistics, which this run did not use.

- **Total Execution Time (Wall clock)**: Not available. The session interface did not expose a wall-clock total.
- **Total Thinking Time**: Not available. The session interface did not expose a thinking-time total.
- **Token Usage (if known)**: Not reported as a total. The only figure visible in the session is the remaining-budget counter (about 15,000,000 tokens at the start of the task, about 14,994,000 at the end). That counter does not give per-session usage, so I am not reporting a usage number.
- **Any other session-level statistics available in your interface**:
  - Background verification runs: three executions of `scripts/verify_c_triviality.py`. The first attempt exceeded the foreground timeout and was moved to the background. It ran the earlier, buggy code and completed later; its n = 3 output was overwritten by the corrected run.
  - Committed artifacts: `artifacts/c_triviality_n1.json`, `artifacts/c_triviality_n2.json`, `artifacts/c_triviality_n3.json`, plus the report `docs/issues/mathematical_proof.md`.
  - Verification checks: super-Jacobi (undeformed and κ-linear) for n = 1, 2, 3; associativity of normal ordering for n = 1, 2 (400 random triples each). Associativity for n = 3 was not run.
