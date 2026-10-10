# Next Session Prompt Kit

This directory manages prompt collections for starting and ending the next session.

## Purpose

- Reliably create instruction files for the next session.
- Split long templates by responsibility to improve maintainability.

## File Structure

- `template.md`
  - Minimal controller for creating next-session files.
- `prompt_pack_start.md`
  - Prompt collection used at session start.
- `prompt_pack_finish.md`
  - Required prompt collection used at session end.
- `prompt_pack_issue.md`
  - Optional retrospective and resource check prompts.

## Recommended Execution Order

1. `prompt_pack_start.md`
2. Implementation work
3. `prompt_pack_finish.md`
4. `prompt_pack_issue.md` only if needed

## Operational Rules

- `template.md` holds only "reference order, required inputs, and output naming."
- Individual prompt text is managed solely in `prompt_pack_*.md` files.
- Only the latest dated next-session instruction file is kept in
  `handover/next_session/`.
- Older files are moved to `_legacy/handover/next_session/`.
- When adding new prompts, place them in the appropriate pack by purpose.
- Session-wide records in `log/` follow the policy in `log/README.md`.

### Moving Old Next-Session Files

- **Method A (manual)**:
  1. After creating the next-session file, run:
     - `./scripts/archive_next_session_prompts.sh --keep handover/next_session/YYYY-MM-DD-N.md`
  2. Check the result with `git status`.
- **Method B (AI agent)**:
  - The AI executes the above script and presents the `git status` output.
