# English index of the design log (`r1-3_experiment_design.md`)

The design log is written in Japanese and was kept with dates during the study (October 2026). This index gives, for each section and numbered decision, the date and a one-line English summary. The Japanese text is authoritative; this index is a guide and does not replace it. Numbered decisions are referred to as §9.N (for example, §9.31).

## Decisions the paper relies on as fixed before judging

| Paper | Decision | Date | Design log |
|---|---|---|---|
| 6.4 | Outcome criterion common to both studies (pass / insufficient / fail; two admissible readings; the rule for $K$-dependence); detailed items only for Study 2; cross-study comparison only at the outcome level | 2026-10-08 | §9.31 |
| 6.4 | Three items extracted from each run as the basis of the final judgment (conclusion, reading of "up to scalar", parity of gb) | 2026-10-12 | §9.48 |
| 6.4 | Judging is not blinded; one judge (the author) | 2026-10-04 | §9.7 |
| 6.4 | Frozen rule-based prediction (rules-v1) placed next to the verdicts; hidden from the author while judging | 2026-10-07; hiding 2026-10-16 | §9.29 |
| 6.4 | $K$ criterion specified: value errors confined to $K$ components are not counted; arguments about $K$ are | 2026-10-16 | §9.31 (last item) |
| 6.4 | Scope of AI help in recording judgments (templates and code checks only; no values) | 2026-10-16 | §9.28 (last item) |
| 6.4 | Nine verdicts revised after the prediction was revealed; agreement before and after | 2026-10-23 | §9.29 (item after it) |
| 6.5 | All runs reported except mechanical failures, which are listed and rerun under a new tag | 2026-10-06 | §9.24, §9.10 |
| 6.2 | Main models and run counts (ten automated runs per ungated condition for three main models; gated allocation) | 2026-10-06, 2026-10-08 | §9.19, §9.33 |
| 6.2, Table 3 | Gemini 4 Argon (Low) used as the Manager for two Gemini 3.8 Flash runs after Gemini 3.1 Pro was retired; reported separately | 2026-10-16 | §9.56 |
| 6.2 | Isolation breaches in two Gemini 3.8 Flash runs counted and marked | 2026-10-17 | §9.56 |
| 6.5 | Data collection closed; no further runs or reruns | 2026-10-17 | §9.56 |
| 7 | No statistical tests; repetition reported as $k/n$ | 2026-10-12 | §9.55 |
| 6.6 | Correction experiment: protocol, results, and the treatment of trials 3 and 5 | 2026-10-12, 2026-10-21 | §9.30, §9.52 |
| 6.6 | Manager claims: terms (M1 false, M2 unverified, M3 added) and the check of all candidate errors plus a fixed sample | 2026-10-12, 2026-10-21 | §9.53 |
| 7 | Public release of the records | 2026-10-14, 2026-10-24 | §9.58 |

## Sections 1–8 (2026-10-01 to 2026-10-03)

| Section | Summary |
|---|---|
| 1 | Purpose: answer Reviewer 1's third condition with a controlled comparison of workflow components and baselines. |
| 2 | Conditions A (full workflow; later split into A1 and A2), G− (no human gate), F− (no issue files; chat messages), C (one-shot). |
| 3 | Model panel and harnesses. |
| 4 | Conditions kept equal across runs and prevention of contamination between runs. |
| 5 | Evaluation measures. |
| 6 | Schedule (submission on 2026-10-28). |
| 7 | How results are reported in the paper. |
| 8 | Decisions of 2026-10-02 (setup of the runs). |
| (note) | Points to consider when comparing A and F− (author's memo, 2026-10-03). |

## Section 9: numbered decisions (2026-10-04 onward)

| § | Date | Summary |
|---|---|---|
| 9.1 | 10-04 | Every automated run is counted and annotated (fixed replies, stops on refusal, web search, external references, environment versions). |
| 9.2 | 10-04 | Five runs per model and condition first (later ten for main models). |
| 9.3 | 10-04 | Every run is judged by the author in a prepared file. |
| 9.4 | 10-04 | Tables in the paper use the automated runs; A and F− run regularly. |
| 9.5 | 10-04 | Gemini 3.1 Pro Worker at Low effort, as in earlier runs. |
| 9.6 | 10-04 | GPT-6 Luna (Copilot CLI) added to the automated C / G− runs. |
| 9.7 | 10-04 | Judging is not blinded; one judge; based on the correctness of theory and artifacts. |
| 9.8 | 10-04 | Schedule: data collection, judging, writing (later extended; see notes in the item). |
| 9.9 | 10-04 | Study 2 is an additional validation, not a replacement; earlier data are not modified. |
| 9.10 | 10-04 | Runs stopped by the harness (e.g. glob refusal) are listed as mechanical stops and rerun under a new tag. |
| 9.11 | 10-05 | Claude Opus 4.6 added to the automated runs (same model as Study 1 X-06). |
| 9.12 | 10-05 | Antigravity CLI allow-list extended (cp, mv, touch, rm) from a given time; difference noted. |
| 9.13 | 10-05 | Claude Haiku 4.5 C / G− five runs each. |
| 9.14 | 10-05 | Separate Manager directory and home directory for every gated run. |
| 9.15 | 10-05 | Extra Gemini 3.6 / 3.7 Flash runs before their announced retirement. |
| 9.16 | 10-05 | No A / F− runs for Gemini 3.6 / 3.7 Flash. |
| 9.17 | 10-06 | A1 (Worker continues in one session) and A2 (new Worker session per issue) defined as conditions. |
| 9.18 | 10-06 | After the final reflection, check whether the Worker read the records; corrections drafted by the Manager if not. |
| 9.19 | 10-06 | Allocation of gated runs: A1 three, A2 two, F− two per Worker model (Luna, Sonnet 4.6); one run at a time. |
| 9.20 | 10-06 | Reference: Claude Sonnet 5.5 C / G− five runs each. |
| 9.21 | 10-06 | Reference: Claude Opus 5.5 C / G− five runs each. |
| 9.22 | 10-06 | Supplementary condition with another Manager model (planned; not run). |
| 9.23 | 10-06 | Reference: Claude Opus 4.7 / 4.8 / 5, one run per condition. |
| 9.24 | 10-06 | Reporting scope: all runs except mechanical failures are reported. |
| 9.25 | 10-06 | Record of the Opus runs of that day. |
| 9.26 | 10-07 | Facts prepared per run before judging (scribe and subagents; judging by the author); C judged at the final commit (decided 10-16). |
| 9.27 | 10-07 | Columns of the judging sheet (readings stated; statements contradicting facts). |
| 9.28 | 10-07 | Recording rules for verdicts; scope of AI help (10-16). |
| 9.29 | 10-07 | Prior verdicts and the frozen prediction next to the verdicts; prediction hidden while judging (10-16); revisions after the reveal (10-23). |
| 9.30 | 10-07 | Practicality: ease of correction by human-specified requests (correction experiment), reuse at n = 4, structure. |
| 9.31 | 10-08 | Paper structure (Study 1 / Study 2) and the common outcome criterion; $K$ criterion specified (10-16). |
| 9.32 | 10-08 | Reference: Claude Haiku 5.5 (needs Claude Code 2.1.293). |
| 9.33 | 10-08 | Ten automated runs per ungated condition for Sonnet 4.6, Luna, Gemini 3.1 Pro. |
| 9.34 | 10-08 | Claude Fable 5.1 trial and runs. |
| 9.35 | 10-08 | Discussion points and how they are measured (human burden split into judgment / operation / tool failures). |
| 9.36 | 10-08 | Effort-only controls in the ungated conditions. |
| 9.37 | 10-09 | Harness-related evaluation items. |
| 9.38 | 10-09 | Reflections obtained after the fact for runs without one. |
| 9.39 | 10-09 | Preparing for the retirement of Gemini 3.1 Pro (Manager model). |
| 9.40 | 10-09 | Extensions from the literature survey (measured after judging from existing records). |
| 9.41 | 10-10 | Reference: Claude Fable 5, one run per condition. |
| 9.42 | 10-10 | Order of gated runs changed (required Sonnet A2 #2 first). |
| 9.43 | 10-10 | One remaining Gemini 3.1 Pro rerun. |
| 9.44 | 10-10 | Reference: Gemini 3.1 Pro (High), one run per condition. |
| 9.45 | 10-10 | If Gemini 3.1 Pro becomes unavailable: no substitute Manager; optional runs dropped. |
| 9.46 | 10-10 | Future direction (not measured): replacing relay operations by tools; relay protocol of the scribe. |
| 9.47 | 10-11 | Manuscript structure and drafting plan. |
| 9.48 | 10-12 | Three items extracted as the basis of the final judgment. |
| 9.49 | 10-12 | Definitions fixed before judging (flexible design, model interaction, etc.). |
| 9.50 | 10-12 | How counts are written in Table 3 ("10+3"). |
| 9.51 | 10-12 | Details of error and restart handling (sign of γ, parity, missing layers, restarts). |
| 9.52 | 10-12 | Correction experiment: results, recording of verdicts, ease tiers; trials 3 and 5 (10-21). |
| 9.53 | 10-12 | Manager misrecognition: terms, how counts are checked, order of the remaining judging (10-21). |
| 9.54 | 10-12 | Additional gated runs with Gemini 3.8 Flash (A1, F−) and their procedure. |
| 9.55 | 10-12 | No statistical tests. |
| 9.56 | 10-13 | No further runs except the successor-Manager F− (later A1); Gemini 4 Argon as successor (10-16); run records; data collection closed (10-17). |
| 9.57 | 10-14 | Page target (about ten pages); details in the public repository. |
| 9.58 | 10-14 | Public release of the records; release decisions (10-24). |
