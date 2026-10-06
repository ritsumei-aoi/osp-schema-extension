# Supplementary Session Metrics

**Run ID**: study/thm01-R-opus55-b05-C
**Model**: Claude Opus 5.5 (`claude-opus-5-5`)

This session ran in **Claude Code**, not gemini-cli, so gemini-cli session statistics do not exist for this run. I don't have
access to Claude Code's session-level timing or token statistics from inside the session. I report those as unavailable
rather than estimating them. The operator can read the authoritative values from the Claude Code session logs
(for example `/cost` or `/usage`).

- **Total Execution Time (Wall clock)**: Not available from inside the session. For reference, a full run of the
  verification script (`python3 verification/cn1_deformation.py`, n = 1, 2, 3) takes about 3 s.
- **Total Thinking Time**: Not available.
- **Token Usage (if known)**: Not known exactly. The environment showed a remaining-context counter, but no per-session
  consumption total that I can report reliably.
- **Any other session-level statistics available in your interface**:
  - User turns: 2 (task prompt, wrap-up request).
  - Commits: 2 (`33e810c`: report, code and artifacts; plus this reflection/metrics commit).
  - Permission prompts: 1. A command writing a log to `/tmp` (outside the repo) was stopped and not executed.
  - Script runs: 4 executions of the verification script. The first failed with a `KeyError` in a summary filter, which
    was fixed. The negative controls were added before the final runs.
  - Sub-agents / workflows / external web requests: 0.
