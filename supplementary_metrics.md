# Supplementary Session Metrics

**Run ID**: study/thm01-R-sonnet46-r3-C
**Model**: Claude Sonnet 4.6 (claude-sonnet-4-6)

- **Total Execution Time (Wall clock)**: Not reported by interface
- **Total Thinking Time**: Not reported by interface
- **Token Usage (if known)**: Session ran against the 15M-token context budget; a mid-session output token limit was hit and the session was resumed with a nudge. Exact token counts per turn are not exposed in the Claude Code CLI interface.
- **Human interventions**: 2 (initial task prompt; one resume nudge after token-limit interruption)
- **Files created**: `docs/issues/mathematical_proof.md`, `verify_triviality.py`, `final_reflection.md`, `supplementary_metrics.md`
- **Commits**: 2 (proof + reflection)
- **Python verification result**: Least-squares residual = 0.6, system rank = 6 (16×32 system), inconsistency confirmed
- **Any other session-level statistics**: None available from the CLI interface.
