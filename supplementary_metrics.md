# Supplementary Session Metrics

**Run ID**: study/thm01-R-sonnet46-b17-C
**Model**: Claude Sonnet 4.6 (claude-sonnet-4-6)

- **Total Execution Time (Wall clock)**: Not available from session interface.
- **Total Thinking Time**: Not available from session interface (model does not expose per-turn thinking time in this interface).
- **Token Usage (if known)**: Not directly reported. Session started from 15,000,000 token budget; by end of mathematical proof turn, ~47,000 tokens had been consumed.
- **Output token limit event**: One output token limit was hit during the first substantive turn (file reading + planning), requiring a user resume prompt. This is the primary session-level anomaly.
- **Human turns**: 3 (initial task prompt; resume after token limit; final reflection request).
- **Tool calls**: ~12 total (6 file reads, 1 file write for proof, 2 git commands, 2 file writes for reflection/metrics, 1 git commit+push).
- **Any other session-level statistics**: The proof was completed in a single reasoning pass after the resume. No backtracking or re-derivation was required.
