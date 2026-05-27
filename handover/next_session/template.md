# Next Session Instructions (Controller Template)

This file is the minimal controller for creating "next-session instruction files."

## Purpose

The sole purpose is:
- Create prompts for the next session in a stable order.

The actual prompt text is sourced from the following split files:
- `prompt_pack_start.md`
- `prompt_pack_finish.md`
- `prompt_pack_issue.md` (optional)

## Required Inputs

Prepare the following before creating the next-session file:
- `handover/README.md` (handover index)
- `handover/workflow_common.md`
- `handover/workflow_method_b.md` (when using AI agent) or
	`handover/workflow_method_a.md` (when using interactive dialog)
- `handover/session_protocol_method_a.md` (Method A details)
- `handover/handover_memo_format.md`
- `handover/handover_memo_latest.md`
- `log/README.md`
- <!-- CUSTOMIZE: Add project-specific reference files here -->

## Build Procedure

1. Retrieve the start prompt from `prompt_pack_start.md`.
2. Perform implementation work.
3. Retrieve the end prompt from `prompt_pack_finish.md`.
4. Use `prompt_pack_issue.md` only if needed.
5. Output the next-session file as `handover/next_session/YYYY-MM-DD-N.md`.
6. Move the old `handover/next_session/YYYY-MM-DD-N.md` to
	`_legacy/handover/next_session/`.

## Output Naming

- Format: `handover/next_session/YYYY-MM-DD-N.md`
- `YYYY-MM-DD`: session end date
- `N`: sequential number within the same day (1, 2, 3, ...)

## Replacement Checklist

When creating, make sure to fill in:
- `<session-goals>`
- `<topic>`
- Date and sequential number
- Reference log file name

## Notes

- `handover/` is for repo-specific handover use.
- `log/` is for session-wide/project-wide records.
- When nesting code blocks, use four backticks for the outer block and three for the inner block.

## Metadata

- Template Version: 2.0
- Created: 2026-03-08
- Last Updated: 2026-03-08
