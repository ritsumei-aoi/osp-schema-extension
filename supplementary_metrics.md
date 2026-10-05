# Supplementary Session Metrics

**Run ID**: study/thm01-R-opus46-b11-C
**Model**: Claude Opus 4.6

- **Total Execution Time (Wall clock)**: ~45 minutes (estimated; session spanned context compaction)
- **Total Thinking Time**: Not separately metered in Claude Code
- **Token Usage (if known)**: Session consumed sufficient tokens to trigger one context compaction/summary event. Estimated ~150k-200k tokens total (input + output) across the full session.
- **Any other session-level statistics available in your interface**:
  - Context compactions: 1 (session was continued from summary)
  - Background agent invocations: Multiple (for running Python verification scripts)
  - Files created: 8 (6 verification scripts/data + 1 proof document + 1 pre-existing issue doc)
  - Files committed: 7 (in main analysis commit) + 2 (reflection/metrics, pending)
  - Major computational pivots: 3 (Fock-space -> analytical; lstsq -> trace decomposition; n=3 numerical -> structural argument)
  - Python scripts executed: ~15-20 runs (including failed/debugging runs)
  - Final verification results: n=1 dim_trivial=0 (analytical), n=2 dim_trivial=0 (numerical), general n dim_trivial=0 (structural proof)
