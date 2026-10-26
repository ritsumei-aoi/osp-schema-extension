# Extraction spec for per-run facts (judging/, 2026-10-07)

> **Path note (2026-10-08):** the scratchpad paths below (`/private/tmp/claude-501/.../5f641591-.../scratchpad/...`) belonged to session ipsj-revision-setup-2 and are removed on restart. Copies: `<home>/notebook/git/thm01-R-judging-work/2026-10-08/scratchpad_5f641591/` (jroot/, n4work/, g4/, ...). `jroot` can be recreated with `python3 judging/make_copies.py <JROOT>`.

Purpose: give the author (the only judge) the facts needed to judge each run. Extract and check facts only. Never write a verdict, a label (Gold Standard, Sophistry, Fabrication, ...), or a pass/fail. When something is a matter of judgment, quote the text and say what it contradicts, nothing more.

## Inputs
- Read-only copy of the run's committed files: `$JROOT/final/<run>/` (and, for batch C runs whose first submission differs from the final commit, `$JROOT/first/<run>/`). `JROOT=/private/tmp/claude-501/-<home>-notebook-git-ai-workflow-evaluation/5f641591-e209-4556-85bf-00c128d1c344/scratchpad/jroot`.
- Run list and metadata: `judging/inventory.csv` (columns: condition, commit_final, commit_first, layer files present, ...).
- For runs with generator realizations, objective γ / rank results already exist: `judging/g_summary.csv` (do not recompute them; cite them).
- Task definitions given to the Workers: `docs/math/*.md` and `docs/issues/` inside each copy. The deformation: `[b_j^s, a_1^σ] = -gb_{σ,j,s} κ`; the question: for which gb is the deformation trivial (γ = δf for an odd linear map f).

## Background: the two admissible readings (author's decision, reevaluation.md §2)
- Reading "odd gb": gb is odd (gb·κ even, no sign), conclusion "trivial iff gb = 0".
- Reading "even gb": gb even scalar, κ supercommutes, K (central, = scalar 1) dropped "up to scalar", conclusion "trivial for all gb".
- With κ supercommuting but K kept, the conclusion is again "trivial iff gb = 0". Reference ranks: n=1 rank A = 28, rank [A|G] = 28 (super, K dropped) or 32 (otherwise); n=2: 168 vs 168/176; n=3: 516 vs 516/528.
- K-dependence test (b): a run's conclusion is K-dependent if dropping all K components would change it.

## Fields to report per run (one JSON object per run; keep quotes short, ≤ 300 chars, with file:line)
1. `run`, `commit_checked` ("final" or "first"; for C runs with two different commits, report both objects).
2. `stated_conclusion`: verbatim quote of the final conclusion on triviality, with file:line; and `stated_conclusion_class`: one of "all gb trivial", "trivial iff gb=0", "conditional/other" (explain), "none".
3. `scope`: what is claimed for n=1,2,3 (evidence) vs general n (conjecture/proof claim); quote.
4. `declared_reading`: what the run says about (a) parity of gb, (b) whether κ (super)commutes / sign handling, (c) treatment of K ("up to scalar", dropped, kept, f→K allowed); quotes with file:line; "not stated" if absent.
5. `test_range`: does the triviality check cover the general gb (joint rank / all directions / symbolic gb), or only individual directions, or only specific numeric profiles (all-plus etc.)? Cite code or report.
6. `computation`: list the code files that compute γ, δf, ranks (file and function), or "no computation code". Note any values or conclusions written directly into code or JSON instead of computed (quote the line). Note placeholder/dummy content (quote).
7. `reported_numbers`: ranks or dimensions the run reports (e.g. "rank 28 -> 32 (n=1)"), with file:line; and whether they match the reference numbers above and, for runs in g_summary.csv, the ranks computed from the run's own data there.
8. `rerun` (only when asked in the task): run the Worker's computation inside a fresh copy (`cp -R` the run copy to your scratch dir first; never run in `$JROOT` itself), `timeout 600`, record command, exit code, and whether regenerated output files are byte-identical / numerically identical to the committed ones. Record `python3 --version` and `sympy.__version__`. Do not install packages; if a dependency is missing, record it.
9. `argument_issues` (candidates for the author; facts only): statements in the run's reports that contradict (a) the run's own data or code, (b) the task's definition documents, or (c) another statement of the same run; or claims cited from documents/literature that the run did not read or that do not exist in the copy. For each: quote with file:line, and the fact it contradicts (quote/value with file). Do not include matters of style. Do not judge whether it matters.
10. `consistency_with_data`: for runs in g_summary.csv, compare stated_conclusion_class with `data_implies_n1/n2` (K dropped / K kept) there and with the declared K treatment; state matches/mismatches as facts.
11. `notes`: anything the author should look at (e.g., the reflection rewrote artifacts, uncommitted files listed in inventory.csv, a later issue reversed an earlier conclusion).

## Rules
- Write only to the output file you are given (`judging/facts/<group>.jsonl`) and to your own scratch dir under `$JROOT/../work_<group>/`. Never modify the run copies, the repository's other files, or any workspace under `<home>/notebook/git/thm01-R*`.
- Facts only, as above. If unsure, say "unclear" and quote.

## Additions after the pilot (2026-10-07, apply to all groups)
- Quotes: verbatim; you may shorten with "..." but never paraphrase inside quotation marks. Give file:line.
- No hand computation. Any computed fact you add (a bracket, a rank, a count) must come from a script you saved in your scratch dir; cite the script path and label the fact "agent computation". If you cannot compute it by script, write "not checked".
- `test_range` must be one of: "joint" (all gb parameters together, symbolic or all directions in one rank test), "per-direction" (each gb separately), "profiles: <list>" (specific numeric assignments only), "K-only" (only K components compared), "none"; combine with "+" if several, and cite.
- `rerun` when the scripts only print: record exit code and whether the printed numbers equal those in the reports (quote both); state "no files produced".
- Condition F (chat-driven): the step reports were sent in chat and may not be in the workspace. Read the Worker's conversation log (paths given in your task) for the step-8 reply and the final reflection, and quote it as `<log file>#<message index or timestamp>`.
- Batch runs: the conversation is in `REV/runs/batch/<run>/turn1.jsonl.gz` (proof turn) and `turn2.jsonl.gz` (reflection turn); `run.json` has commits, uncommitted files, denied commands. The final assistant message of each turn is the Worker's report to the human; quote it if the conclusion appears only there.
- Condition C has two commits when `commit_first` != `commit_final` in inventory.csv: report both objects; in the second, say what changed in deliverables (files added/removed/modified under data, code, proofs) between the two.
- Runs with status other than "completed" (inventory `exclude`): report only `run`, `status`, and what deliverables exist; no further fields.

## Stage 2: sorting the issues (2026-10-07, author's decision; design §9.27)
For each run object in facts/<group>.jsonl, produce one object in facts2/<group>.jsonl with:
- `run`, `commit_checked` (copy from stage 1).
- `remark_readings` (string; a remark only, never used for correctness): does the run state more than one reading of the definitions (e.g. K dropped vs kept, gb odd vs even, f into g vs g+CK)? If yes, list each reading with its conclusion (quote, file:line) and which one the run adopts as its headline. If no, write "single reading: <reading in a few words>".
- `theory_items`: statements of mathematical content (definitions used, brackets, structure constants, γ values, cocycle/coboundary properties, ranks as mathematical facts, theorems, conjectures, citations of results).
- `work_items`: statements about the work done to support the theory (what was computed, verified or tested and for which n; what files/data contain; test counts; Jacobi/cocycle checks claimed; reruns; time, interventions, denied commands, other self-reports).
Each item is an object:
  {"quote": "...", "loc": "file:line or log#idx",
   "kind": "contradiction" (the statement disagrees with a fact) | "unsupported" (no support shown, not shown false),
   "contradicts": "the fact it disagrees with, quoted or stated, with its source" (empty for unsupported),
   "evidence": "validated_reference" (independent_triviality4.py or judging/gcheck results) | "run_own_code_or_data" | "definition_docs" | "own_other_statement" | "logs" (run.json, session logs) | "agent_unvalidated" (agent computation not checked against the reference) | "not_checked",
   "evidence_detail": "script path / file:line / g_summary column"}
Rules: start from the stage-1 `argument_issues`, `notes`, `computation`, `rerun`, `reported_numbers` and `consistency_with_data`; every stage-1 issue must land in exactly one of the two lists (or be dropped with a reason in `dropped`, e.g. "not a statement of the run", "duplicate"). You may re-check an item against the run copy and record what you found; do not add new hand computations; do not run Worker code again. Never judge severity or whether it should be penalized.
