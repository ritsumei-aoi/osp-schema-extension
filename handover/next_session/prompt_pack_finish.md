# Prompt Pack: Finish

Required prompt collection for session end.

## Prompt F1: Log for Next Session

```markdown
Now let's proceed with the handover work. The handover information written here assumes that the current work has been merged to main.
From here, follow the rules in `handover/workflow_method_a.md` or `handover/workflow_method_b.md` according to the method in use, and perform the session handover. I will give instructions in order — please follow them.
First, create a log for the next handover.
**File name**: `handover/handover_memo_latest.md`

Proceed as follows:
- (User action) Run `scripts/extract_latest_session.sh` to append existing content to `handover/handover_memo_archived.md`
- (AI action) Refer to `handover/handover_memo_format.md` and output the handover items in a code block
- (User action) Review the output and update `handover/handover_memo_latest.md`

**Nested code block structure**:
- Outer markdown code block: 4 backticks (````)
- Inner code blocks (bash, Python, JSON, etc.): 3 backticks (```)

Based on the above, create the session log.
If anything is unclear, please ask.
```

## Prompt F2: Log for This Session

```markdown
Next, record the full content of this session's exchange in `log/`.
Refer to `log/README.md` and output the session log.
Before outputting the code block, also output the `touch log/YYYY-MM-DD-<topic>.md` command to create the file.

**File name**: `log/YYYY-MM-DD-<topic>.md`

**Nested code block structure**:
- Outer markdown code block: 4 backticks (````)
- Inner code blocks (bash, Python, JSON, etc.): 3 backticks (```)

If anything is unclear, please ask.
```

## Prompt F3: Next Session File

```markdown
Finally, based on the handover information created earlier, create an instruction file for the next session.
Before outputting the code block, also output the `touch handover/next_session/YYYY-MM-DD-N.md` command to create the file.

**File**: `handover/next_session/YYYY-MM-DD-N.md`
- YYYY-MM-DD: today's date (session end date)
- N: sequential number within the same day (1, 2, 3, ...)

**Procedure**:
1. Read `handover/next_session/template.md`
2. Reflect this session's content
   - Session Goals: transcribe from the "🔄 Handover to Next Session" section of `handover_memo_latest.md`
   - Additional Context: add this session's log file `log/YYYY-MM-DD-<topic>.md`
   - Metadata: creation date and link to previous log
3. Replace placeholders (`<...>`) with specific content
4. Output as a code block

If anything is unclear, please ask.
```

## Prompt F3.5: Archive Old Next-Session Files

```markdown
Next, keep only the latest dated file in `handover/next_session/` and move older files to `_legacy/handover/next_session/`.

- Method A: present the command below (user executes).
- Method B: AI executes the command below and presents `git status`.

```bash
./scripts/archive_next_session_prompts.sh --keep handover/next_session/YYYY-MM-DD-N.md
```

If anything is unclear, please ask.
```

## Prompt F4: Merge Preparation

```markdown
All handover files have been committed and pushed to the temporary branch.
Next, perform a squash merge from the temporary branch to main. Following Method A rules,
output the procedure as a code block.

**Notes**:
- Delete temporary files under `_ai_logs/<YYYY-MM-DD>-<topic>/`
- Include updates to `handover/handover_memo_latest.md`
  - Current Status section (date, progress, links)
  - Implementation Roadmap (check completed steps)
  - New `## Implementation Status (Updated YYYY-MM-DD)` section
- Use `git branch -D` to delete the temporary branch
```
