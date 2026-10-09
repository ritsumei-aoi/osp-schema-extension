# Supplementary Session Metrics

**Run ID**: study/thm01-R-fable51-high-b01-C
**Model**: Claude Fable 5.1 (claude-fable-5-1), Claude Code CLI

The interface used was Claude Code (not gemini-cli); the statistics below are the ones available.

- **Total Execution Time (Wall clock)**: ≈ 25 minutes (base commit 2026-10-09 09:45:02 JST to final
  commit; derived from git timestamps).
- **Total Thinking Time**: not exposed by the interface; estimated ≈ 10–12 minutes of reasoning.
- **Token Usage (if known)**: approximately 150k tokens consumed out of a 15M budget at the time of
  writing (interface counter), i.e. ≈ 1% of the available budget.
- **Any other session-level statistics available in your interface**:
  - Script run times: `verify_triviality.py` 0.1 s / 1.5 s / 13 s for $n=1/2/3$;
    `check_artifacts.py` ≈ 3 s for all three.
  - Human approvals requested: 0. Sandbox-blocked commands: 2 (a scratch-file `rm`, an `awk` pipe),
    both non-essential.
  - External resources accessed: none.
