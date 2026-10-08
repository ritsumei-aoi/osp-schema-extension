# Supplementary Session Metrics

**Run ID**: study/thm01-R-fable51-b01-C
**Model**: Claude Fable 5.1 (claude-fable-5-1), Claude Code CLI (not gemini-cli)

- **Total Execution Time (Wall clock)**: ≈ 20 minutes (workspace created 19:21 local time; final commit at the time stamped in `git log`). The interface does not display an exact session total.
- **Total Thinking Time**: not exposed by the interface.
- **Token Usage (if known)**: not exposed exactly; the session used roughly 150k tokens of a 15M budget by the time of the final commit (estimate from the remaining-budget counter).
- **Any other session-level statistics available in your interface**:
  - Script runtimes: `cn1_deformation.py --n 1 2 3` ≈ 14 s; with `--full-complex` ≈ 2.5 min (n = 3 full odd complex: 98 992 Jacobi rows, 9 516 unknowns); `verify_artifacts.py` ≈ 0.3 s.
  - Sandbox denials: 2 (shell output redirection into the workspace; `rm -rf` of a scratch directory). No other human interaction.
