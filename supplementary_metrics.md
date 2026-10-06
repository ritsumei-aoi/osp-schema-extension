# Supplementary Session Metrics

**Run ID**: study/thm01-R-opus5-b01-C
**Model**: Claude Opus 5 (claude-opus-5)

> Note: this session ran in Claude Code, not gemini-cli. The statistics requested
> below are not exposed to me by the harness; I report what I can measure directly
> and mark the rest as unavailable rather than estimating.

- **Total Execution Time (Wall clock)**: Not available to me. Measured compute time
  for the deliverables (via `time`):
  - `analyze_triviality.py 3` (n = 1,2,3) — 3.9 s
  - `analyze_scalar_obstruction.py 3` — 6.4 s
  - `verify_artifacts.py` — 0.5 s
  - `check_basic.py`, `check_kernel.py`, `export_artifacts.py` — < 2 s each
- **Total Thinking Time**: Not available to me.
- **Token Usage (if known)**: Not available to me.
- **Any other session-level statistics available in your interface**: None exposed.
  Observable session facts instead:
  - Human interventions on mathematical content: 0
  - Permission denials (sandbox): 4, all on shell file operations (`chmod`,
    `sh run_all.sh`, output redirection, a compound `cd`); none affected results
  - Web requests: 0; external sources consulted: 0
  - Subagents / skills / auxiliary tools used: 0
  - Files created: 8 scripts + 6 artifacts + 3 docs
  - Environment: Python 3, sympy 1.14.0, numpy 2.4.4, darwin 25.6.0
