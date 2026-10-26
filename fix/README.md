# fix/: the correction experiment

Eight automated runs that did not pass or had flaws were corrected by Manager-drafted requests (design log §9.30, §9.52; paper Section 6.6).

| File or folder | Contents | Language |
|---|---|---|
| `PROTOCOL.md` | Procedure and criteria of the experiment (including the ease tiers) | Japanese |
| `SUMMARY.md`, `results.tsv` | Results per trial | Japanese |
| `candidates.tsv` | How the eight runs were selected | Japanese, English |
| `kit/`, `scripts/` | Materials and scripts used | English |
| `<run>/fix_log.md` | Chronological record of each trial | Japanese |
| `<run>/relay/` | Texts sent to the Worker and to the Manager | English |
| `<run>/worker/` | Worker turns (compressed JSON lines) | English |
| `<run>/worker_patches/` | The corrections as patches | — |
| `<run>/manager_memo_copy.md` | Manager memos | English |
| `transcripts/` | Antigravity CLI conversations of the Managers and Gemini Workers | English |

The verdicts before and after correction are in `judging/fix_verdicts.csv`. The corrected Worker repositories are on the branches `study/thm01-R-<run>-fix`.

Three Worker turn files contain one line each that is not JSON: `gemini38f-b01-C/worker/turn1.jsonl.gz` line 207, `gemini36f-b13-C/worker/turn1.jsonl.gz` line 35, and `turn2.jsonl.gz` line 117. Each is a status line printed by the Antigravity CLI into the same output ("root agent idle; waiting up to 2h0m0s for … background task(s)"); it is in the original output and is kept as recorded.
