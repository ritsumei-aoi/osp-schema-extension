# runs/: records of the gated runs (and of the hand-started ungated runs)

One folder per run, named as in `inventory.csv`. Not every folder has every file.

| File or folder | Contents | Language |
|---|---|---|
| `run_log.md` | Chronological record of the run kept by the scribe: start, each issue, texts relayed, interventions, problems, corrections of the record | Japanese |
| `relay/` | Every text sent to the Worker and to the Manager, byte for byte, with time stamps | English (texts), Japanese (notes) |
| `pending/` | Manager drafts that were prepared for sending, including drafts that were withheld | English |
| `manager_memo.md` | The Manager's memos (review notes) per issue | English, some Japanese |
| `manager_dir_snapshots.txt`, `manager_git_log.txt` | State of the Manager directory over the run | — |
| `worker_git_log.txt` | Commit list of the Worker repository | — |
| `scribe_checks/` | Facts checked by the scribe before showing them (commands and outputs) | Japanese, English |
| `check.json` | Automated check of the final state | — |
| `claude_session/`, `copilot_session/` | Worker session records (Claude Code / Copilot CLI) | English, some Japanese |
| `worker_scratch*`, `worker_compact*` | Worker's temporary files and compaction summaries | English |
| `retirement_evidence/` | Evidence of the Manager model's retirement (Gemini 3.1 Pro) | — |

The Antigravity CLI conversations (Managers and Gemini Workers) are under `transcripts/<run>/`.
Personal e-mail addresses are replaced by `<redacted-email>` and home paths by `<home>`.
