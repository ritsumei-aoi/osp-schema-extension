# Supplementary Session Metrics

**Run ID**: study/thm01-04
**Model**: Claude Sonnet 4.6 (claude-sonnet-4.6)

---

## Availability Note

> The `supplementary_metrics_template.md` was designed for **gemini-cli**, which prints a
> session-summary block (total wall time, thinking time, token counts) to stdout on exit.
> **GitHub Copilot CLI does not produce an equivalent summary log.** No "Total Thinking Time"
> or token-usage figure is exposed to the agent or visible in terminal output.
>
> The statistics below are the best honest reconstruction available from git commit timestamps
> and session checkpoint records.

---

## Per-Issue Wall-Clock Timeline (from git log)

All timestamps are JST (UTC+9). "Wall time" includes human review/approval pauses between
the AI proposal and the human's next message — it is **not** pure AI compute time.

| Issue | Commit timestamp | Wall time since previous commit |
|-------|-----------------|--------------------------------|
| I01-1 | 2026-05-20 12:59:39 | — (first commit in session) |
| I02-1 | 2026-05-20 14:53:25 | ~1 h 54 m |
| I03-1 | 2026-05-20 15:18:33 | ~25 m |
| I04-1 | 2026-05-20 16:13:09 | ~55 m |
| I05-1 | 2026-05-20 19:08:02 | ~2 h 55 m (includes session pause for missing `docs/math/` files) |
| I06-1 | 2026-05-20 20:11:16 | ~1 h 3 m |
| I07-1 | 2026-05-20 21:57:15 | ~1 h 46 m |
| I08-1 | 2026-05-20 22:23:24 | ~26 m |
| Final reflection | 2026-05-20 22:57:48 | ~34 m |

**Total elapsed (first issue commit → final reflection commit)**: ~10 h 0 m

**Session span (repository setup → final reflection)**: 2026-05-20 10:17 → 22:57 (~12 h 40 m)

Note: The large gap before I05 (~2h55m) reflects an interruption where the human paused
the session to synchronize missing mathematical definition files. The I07 gap (~1h46m)
reflects both the human approval wait and the context compaction checkpoint between sessions.

---

## Statistics Not Available from Copilot CLI

| Metric | Availability |
|--------|-------------|
| Total AI Thinking Time | ❌ Not reported by Copilot CLI runtime |
| Per-turn Thinking Time | ❌ Not exposed to agent |
| Total Token Usage (input) | ❌ Not reported |
| Total Token Usage (output) | ❌ Not reported |
| Session Summary Log | ❌ No exit-summary feature in Copilot CLI |

If per-session token or timing data is required for the evaluation, it may be available
from the **server-side API logs** for the GitHub Copilot organization (accessible to the
research team via GitHub's admin/billing API), which would show per-model usage at a
finer granularity than is visible from the agent side.

---

## Proxy Metrics (from git history)

These can be computed from the repository and are exact:

- **Total commits authored**: 19 (including 8 MARKER commits and 1 setup commit)
- **Issues closed**: 8 (I01-1 through I08-1)
- **Source files created**: 5 (`C_generators.py`, `C_gamma.py`, `C_evaluator.py`, `C_coboundary.py`, `C_triviality_analysis.py`)
- **Data files generated**: 15 (Schema 1×3, Schema 2×3, Schema 3×6, Schema 4×3)
- **Protocol violations**: 1 (I06-1 — proceeded to Phase 4 without explicit approval)
- **Human corrigenda applied**: 1 (I07-1 — f: g→R corrected to f: g→g)
