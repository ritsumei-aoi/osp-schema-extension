# Supplementary Session Metrics

**Run ID**: study/thm01-R-opus47-b01-C
**Model**: Claude Opus 4.7 (claude-opus-4-7)

The Claude Code CLI used for this session does not surface the same
`gemini-cli` statistics, so the fields below are populated with the
analogous information that was observable in-session.

- **Total Execution Time (Wall clock)**: Not instrumented in this
  interface. Rough estimate: a few minutes of wall time; the two
  symbolic executions of `artifacts/verify_C_triviality.py` (one
  per debugging pass) accounted for most of it, with the $n=3$
  rank computation dominating.
- **Total Thinking Time**: Not reported by this interface.
- **Token Usage (if known)**: The harness exposed only a running
  budget indicator (`<total_tokens>` reminders starting at
  15,000,000 and decreasing to ~14,920,000 by the end of the proof
  phase), i.e. roughly 80k tokens consumed across all turns of the
  mathematical analysis. The reflection + metrics phase adds a
  small additional amount.
- **Any other session-level statistics available in your interface**:
  - Turns in the main analysis phase: ~14 assistant turns (file
    reads, one script authoring, two sympy runs with a one-edit fix
    in between, one Markdown proof write, one issue-file append,
    one git commit).
  - Tool calls (approximate): 2 × Read, 3 × Edit, 3 × Write, 6 × Bash
    (including the git commit and one failed `cd` that was reissued
    with `git -C`), 0 × Agent / Skill / Workflow.
  - Human interventions: 0 substantive; 1 harness-level re-prompt
    (the `cd …` sandbox rejection, which I immediately replaced with
    `git -C`).
