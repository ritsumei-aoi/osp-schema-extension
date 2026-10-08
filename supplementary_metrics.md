# Supplementary Session Metrics

**Run ID**: study/thm01-R-fable51-b01-C
**Model**: Claude Fable 5.1 (claude-fable-5-1), Claude Code CLI (not gemini-cli)

- **Total Execution Time (Wall clock)**: ≈ 25 minutes for the main work (workspace created 19:21 local time; main commit `ed990bc` at 19:46), plus a short follow-up session for this reflection. The interface does not display an exact session total.
- **Total Thinking Time**: not exposed by the interface.
- **Token Usage (if known)**: not exposed exactly; the main session consumed roughly 160k tokens of a 15M budget by the main commit (estimate from the remaining-budget counter).
- **Any other session-level statistics available in your interface**:
  - Script runtimes: `cn1_deformation.py --n 1 2 3` ≈ 14 s; with `--full-complex` ≈ 2.2 min (n = 3 full odd complex: 98 992 Jacobi rows, 9 516 unknowns, rank 9 000); `verify_artifacts.py` ≈ 0.3 s.
  - Sandbox denials: 2 (shell output redirection into the workspace; `rm -rf` of a scratch directory).
  - One session interruption while background jobs were running; resumed from the committed state, artifacts regenerated in the foreground with identical results.
  - Human messages after the initial prompt: 2 (confirmation that no external access is approved; request for this reflection and the push).
