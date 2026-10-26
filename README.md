# Artifacts for "Mitigating Epistemic Risks in LLM-Assisted Research" (JIP 27-J002e, revision 1)

This branch (`ipsj-r1-artifacts`, tag `ipsj-artifact-2026-10`) holds the records of Study 2 and the re-audit of Study 1 reported in the revised paper.
The Worker repositories of the runs are on separate branches of this repository; the Study 1 artifacts are under the tag `ipsj-artifact-2026-05`.

## Contents

| Path | Contents |
|---|---|
| `inventory.csv` | Every run (235): branch, final commit, status (counted / excluded with reason / not run), final verdict, verdict before the frozen prediction was revealed, condition, Worker model and harness, Manager model and harness, notes (e.g. isolation breaches). |
| `design/` | The dated design log, in Japanese. Decisions and their dates are as recorded; quota values, subscription plan names, and home paths were removed for publication. |
| `kit/` | What every run received: definition files, issue files, handover files, prompts (A, G−, F−, C), the Manager kit, and the scripts that built each workspace. |
| `runs/<run>/` | Gated runs: run log, relay records (every text sent to the Worker and to the Manager), Human memos, Manager drafts and memos, commit lists, scribe checks, Worker session records (Claude Code / Copilot CLI). |
| `transcripts/<run>/` | Antigravity CLI conversations of the Manager and of Gemini Workers, extracted from the harness state. |
| `fix/` | The correction experiment: protocol, results, and for each trial the log, the relayed texts, Worker turns, patches, and Manager memos. |
| `judging/` | Judging records: the author's verdicts (decoded), the frozen rule-based prediction (`predict.py`, rules-v1) and its comparison with the verdicts, extracted facts, independent checks of the structure constants, the Manager-claim check, post-verdict tables, and the scripts that produced them. See `judging/README.md`. |

## Language

Many records written by the scribe and the author are in Japanese; texts sent to the models are in English. `design/INDEX_en.md` indexes the design log in English (with the decisions the paper relies on), and `GLOSSARY.md` translates frequent terms. The Japanese records are the original records and are not translated.

## Branches

- `study/thm01-R-<run>`: the Worker repository of each Study 2 run (gated and automated). The final commit of each run is listed in `inventory.csv`.
- `study/thm01-R-<run>-shadow`: the five F− runs (condition without the issue files), whose Worker workspace had no Git. The scribe committed a snapshot after each step to a shadow repository; this branch is that repository, and its last commit is the final commit in `inventory.csv`. For four of them (luna-F, luna-r2-F, sonnet46-F, sonnet46-r2-F), `study/thm01-R-<run>` was published earlier with the same history without `__pycache__` files (see the run note in `inventory.csv`).
- `study/thm01-R-<run>-fix`: the corrected versions in the correction experiment.
- `study/thm01-0x`, `study/thm01-X-0x`: Study 1 (tag `ipsj-artifact-2026-05`).

## Editing for publication

- Home paths are replaced by `<home>` (the folder structure after it is kept); personal e-mail addresses in session records are replaced by `<redacted-email>`; the user name in shell output is replaced by `<user>` and the host name by `<host>`.
- Harness home directories (login data) and internal working notes are not included.
- The Worker branches are published as they are (contents and commit metadata, including home paths written by the models), so that commit hashes match the paper and the records.

## License

The repository is under the MIT License (see `main`). Model outputs are included as research records.
