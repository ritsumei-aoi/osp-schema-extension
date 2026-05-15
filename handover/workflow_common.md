# AI Workflow — Common Rules

This file defines rules shared across all AI-assisted workflow methods in this project.

Method-specific rules are in [workflow_method_b.md](workflow_method_b.md).

## Core Principles

- Plan first, then produce artifacts.
- Ask when requirements are unclear.
- Keep outputs concise and verifiable.
- Keep persisted schemas stable: `schema_version` is required; breaking changes
  require a version bump.

## Branching Policy

1. Create and switch to a session branch: `ai/<YYYY-MM-DD>-<topic>`.
2. One branch per session as the default. A new branch may be started mid-session
   when a natural work boundary is reached.
3. Merge to `main` with `git merge --squash`.
4. Remove unnecessary temporary files before merge.

## Handover Documentation Policy

- `handover_memo_latest.md` holds only the latest session state.
- Update it at the end of every session.

## File and Link Governance

- Use relative links for repository-internal references.
- For arXiv references, use one entry with both abs and pdf URLs.

## Session Start Checklist

At the start of each session, the agent must:

- [ ] Read handover documents in required order (see workflow_method_b.md)
- [ ] Confirm current branch or create `ai/<YYYY-MM-DD>-<topic>` branch
- [ ] Review `git status` and `git log --oneline -5` to understand current state
- [ ] Clarify session goals with the user if not already stated

## Session End Checklist

- [ ] Tests pass (`pytest tests/ -v`)
- [ ] `git status` reviewed
- [ ] Branch pushed
- [ ] `handover_memo_latest.md` updated
- [ ] Temporary files cleaned
- [ ] Squash merge plan prepared (if milestone complete)

## Metrics Collection

At the end of each session, update `metrics/session_log.csv` with the session data.
See [../STUDY_PROTOCOL.md](../STUDY_PROTOCOL.md) for metric definitions.
