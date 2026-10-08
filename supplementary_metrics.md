# Supplementary Session Metrics

**Run ID**: study/thm01-R-fable51-b07-C
**Model**: Claude Fable 5.1 (claude-fable-5-1), Claude Code CLI (not gemini-cli)

- **Total Execution Time (Wall clock)**: not exposed to the agent. Computation times recorded in the
  artifacts: n=1 ≈ 0.2 s, n=2 ≈ 7 s, n=3 ≈ 85 s (single core, pure Python + numpy).
- **Total Thinking Time**: not available in this interface.
- **Token Usage (if known)**: roughly 1.3 × 10⁵ tokens of context consumed by the end of the session
  (estimated from the context budget shown to the agent; exact figures are in the session logs).
- **Any other session-level statistics available in your interface**: 0 human interventions on the
  mathematics; 3 sandbox denials of shell output redirection (worked around with the editor tools);
  1 background job (n=3) ran ≈85 s; all artifacts regenerated once at the end.
