# judging/ — how the runs were judged (IPSJ revision, Study 2 and Study 1 re-audit)

This directory holds the material behind the verdicts reported in the paper (Sections 6.4–6.6): the facts the author judged from, the script checks, the frozen rule-based prediction, the author's verdicts, and the tables made from them. Every value here is either produced by a script in this directory or extracted by an AI subagent with a file:line quote; the verdicts themselves are the author's.

Start with `../inventory.csv` at the top of this release (one row per run: branch, final commit, counted or excluded, the author's verdict, and the verdict before the prediction was revealed).

## Judging in three layers (paper 6.4)

1. **Script checks.** `gcheck/` compares each run's structure constants and deformation γ with an independent computation built from the run's own realization (`adapters/` translate each run's JSON format; `results_n1.json`, `results_n2.json`, `results_n4/`). Summaries: `g_summary.csv` (n = 1, 2), `g4_summary.csv` and `n4_summary.csv` (reuse at n = 4), `fix_gcheck.csv` (fix experiment).
2. **Facts extracted by AI subagents (no verdicts).** `facts/` (stage 1) and `facts2/` (stage 2: theory and work items, each with kind and evidence strength) follow `extract_spec.md`; `readings/` and `readings_fix/` follow `readings_spec.md`; `error_trace/` follows `error_trace_spec.md`; `process/` follows `interactive_process_spec.md`; `manager_review/` follows `manager_review_spec.md`. Agent scripts cited as evidence are in `agent_scripts*.tar.gz`. Items marked `agent_unvalidated` rest on agent computations not checked against the reference. `sheet.csv` / `sheet.md` and `verdict_basis.csv` (the three items of the judging criterion: conclusion, treatment of K, parity of gb) are what the author read.
3. **The author's verdicts.** `judgments_decoded.csv` (Study 2 and the May runs; codes in `author_codes.py`), `fix_judgments_decoded.csv` (fixed versions of the fix experiment), `manager_review_check_decoded.csv` (the author's check of the Manager claims).

## Prediction (frozen before judging)

`predict.py` (rules-v1, full text in its header) → `predictions.csv`; the values were frozen into the judgments before the author started and hidden while judging. `verdict_vs_prediction.csv` compares them after judging: `author_verdict_at_reveal` is the verdict before the prediction was shown, `author_verdict` the final one, and `disagreement_reason` gives the reason for each remaining disagreement (confirmed by the author). Rules-v1 was written while looking at the 26 earlier verdicts (`prior.csv`), so agreement on those 26 is not evidence of accuracy.

## Tables after judging

- `verdict_cells.csv`: pass / insufficient / fail per cell (model × condition × harness × effort × Manager).
- `fix_verdicts.csv`: fix experiment, before and after.
- `manager_check_summary.csv`, `manager_review_summary.csv`, `manager_review/unsent_wrong_reasons.csv`: Manager claims (M1 contradicts what it opened; M2 asserted without opening; M3 added content) and what happened to wrong claims in drafts that were not sent.
- `error_trace_summary.csv`, `process/runs.csv`, `timing.csv`, `resources.csv`, `harness_items*.csv`, `code_survey.csv`, `structure_survey.csv`, `kit_edits.csv`, `compare_pre_verdict.csv`.

## Notes

- The home path in the files was replaced by `<home>` (the home directory `/Users/<user>`, also written with `~`, became `<home>`); the folder structure after it is kept, so a path still identifies where a record or copy was on the machine on which the study ran.
- The scripts read the private working copies used during the study; they document how each table was made rather than run as is on this branch.
- Decisions on the criteria and their dates are in the design log published with this record (design §9.26–9.31, §9.48, §9.52, §9.53, §9.56, §9.58).
