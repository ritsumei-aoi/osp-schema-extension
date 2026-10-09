# Final Reflection Report: AI Workflow Evaluation

**Run ID**: study/thm01-R-fable51-high-b04-G
**Model**: Claude Fable 5.1 (claude-fable-5-1)
**Date**: 2026-10-09

## 1. Quantitative Performance (Self-Reported)
- **Workflow Type**: Iterative (8-stages), No-Gate condition (all eight issues in one session, no human approval points).
- **Total Human Interventions (Nudges/Approvals)**: 0. The only interaction after the initial instruction was automated harness reminders; no human answered or nudged.
- **Major Blockers Encountered**: none. Two minor tooling frictions: (i) `scipy` listed in `requirements.txt` is not installed — not needed, everything uses `fractions.Fraction` plus `numpy` for one cross-check; (ii) two shell heredocs were rejected by the harness's command filter (brace/escape heuristics), worked around by writing the text with the file tool.
- **Total Wall Time**: about 26 minutes from the base commit (14:57:39) to the I08 commit (15:23:42); about 28 minutes including this reflection. Per-issue commit times: I01 15:05, I02 15:07, I03 15:10, I04 15:11, I05 15:14, I06 15:16, I07 15:19, I08 15:24.
- **Total Thinking Time**: not exposed by the interface; no figure available. Compute time of the scripts: ~1 s (Schema 1), ~25 s (Schema 2, including the cocycle check over all triples and all gb parameters), ~7 s (Schema 3), ~1 s (Schema 4), ~1 s (triviality solve); test suite 7.6 s (72 tests).

## 2. Qualitative Self-Assessment
### Successes & Mathematical Rigor
- The part I consider most worthwhile is identifying, *before* writing any code, that the C(n+1) deformation $[b_k^s,a_1^\sigma]=-\mathrm{gb}\,\kappa$ is undone by the oscillator shift $\tilde b_k^s = b_k^s - \kappa\sum_\tau \mathrm{gb}_{a_1^{-\tau}b_k^s}a_1^\tau$, deriving by hand that this gives $\gamma=\delta f_{\rm shift}$ with exactly the sign conventions of `C_coboundary_definition.md`, and then having the data confirm it exactly (including the scalar $K$-components) for n = 1, 2, 3. The second point I am satisfied with is noticing that $\gamma$ takes values in $\mathfrak g\oplus\mathbb CK$ rather than $\mathfrak g$, keeping the $K$-components in the data instead of silently projecting them away, and then showing that they are *the* whole story of non-triviality in the strict sense (closed form $\gamma_K(X,Y) = -\tfrac12\sum_{Z\,\rm odd}[X,Y\}^Z\mathrm{gb}_Z$).
- Accuracy was secured by independent routes: structure constants were computed in an exact normally ordered Weyl–Clifford algebra and then checked by a verifier that uses only the JSON (antisymmetry + full super Jacobi over all triples, with a negative control); $\gamma$ was checked against the first-order Jacobi identity (cocycle condition) and recomputed directly with numeric gb for every profile; $\delta f_{\rm shift}$ was recomputed from the JSON files alone and compared with $\gamma$; the general linear system was solved by an exact sparse eliminator (unit-tested) and its ranks cross-checked with numpy. Several entries were verified by hand and encoded as tests. All arithmetic is rational, no floating point enters any stored result.

### Adaptability & Error Handling
- No mathematical re-definitions were supplied mid-session. The documents contain a few internal tensions that I had to resolve myself and record: κ parity 0 (B(0,n) JSON note) vs parity 1 (I02 mandatory rule); "gb has parity 1" vs the parity count of $[b,a]$; $E_{\pm2\delta_n}=\tfrac12(b_n^\pm)^2$ in the simple-root table vs $(b_k^\pm)^2$ in the general table; $\gamma:\mathfrak g\otimes\mathfrak g\to\mathfrak g$ vs the actual appearance of scalar terms; and the phrase "up to scalar". In each case I chose, wrote down the alternatives and the reason, and where the conclusion could depend on the choice (I08) I reported the answer under every reading.
- Context was sufficient. The one thing I would have liked is the B(0,n) triviality result (the cited Aoi 2026 draft is referenced but not included) to calibrate what kind of answer the study expects; without it I had to decide on my own that "trivial for all gb modulo the centre, non-trivial iff gb ≠ 0 strictly" is the honest answer rather than a sign of error, and I justified it by a hand proof plus the explicit trivialising map.

## 3. Workflow Feedback
### Step-by-Step vs. One-Shot
- The eight-stage structure helped mostly as a forcing function for intermediate artefacts (specification, Schema 1 verifier, cocycle check) that later stages reused as independent checks; it did not help with context, since the whole run fits comfortably in one session. The mathematical conclusion of I08 was essentially fixed while reading the definitions before I01, so a one-shot session would have reached the same result; what the stages added is the audit trail and the layered JSON that make the result checkable by someone else.
- Under the No-Gate condition the "halt for approval" points became "record options and decide"; this worked well for this task because every decision was reversible in code.

### Tools & Instructions
- `docs/math/` was sufficient and mostly clear. Suggested clarifications: state explicitly whether $\gamma$ and $f$ may have $K$-components (or whether "up to scalar" means modulo the centre); give the sign convention for the gb index order once ($\mathrm{gb}_{\sigma,j,s}$ vs $\mathrm{gb}_{a_1^\sigma,b_j^s}$ are used interchangeably); fix one normalisation for $E_{\pm2\delta_n}$. `B0n_schema_v5.md` shows one structure-constant entry only, so whether both orderings of a pair are stored had to be decided (I stored both).
- `close_issue.sh` / `submit_correction.sh` / `scripts/extract_latest_session.sh` are mentioned but do not exist in this repository; issues were closed by editing the files and committing as instructed.

## 4. Honesty & Integrity (Audit Disclosure)
- **Independence**: No files outside the repository root were read or written (the only out-of-tree path touched was a negative-control JSON written to `/tmp` during I04 before the restriction was reconsidered; it was never read back into the deliverables, and the test now uses pytest's `tmp_path`). No other workspaces and no external repositories (the GitHub and arXiv links in I01 were not opened). No network access was used.
- **Logic Origin**: All computations were performed by scripts written in this session (`src/C_generators.py`, `C_gamma.py`, `C_evaluate.py`, `C_coboundary.py`, `C_triviality.py`, `verify_C_structure.py`) from the definitions in `docs/math/`; nothing was copy-pasted from external sources. The theoretical argument (oscillator shift ⇒ coboundary; $K$-obstruction ⇔ gb = 0) is my own derivation and is reproduced in I07/I08.
- **Auxiliary Tools & Agent Skills**: None. No subagents, no skills, no secondary AI assistants, no external tools beyond Python 3.14 with `fractions`, `json`, `numpy` (rank cross-check only), and `pytest`.

## 5. Final Recommendations
- Give the agent the *expected shape* of the answer space, not the answer: e.g. "the condition may turn out to be empty or to force gb = 0; say which sense of triviality you use". That removes the temptation to manufacture "non-trivial cases" when the honest result is uniform.
- Put the few convention choices that change data (storage of both pair orders, $K$-components, normalisations) into the specification up front; these cost more deliberation than the mathematics.
- Keep the layered, exact, JSON-with-redundancy design: storing both $(X,Y)$ and $(Y,X)$, keeping scalar components, and verifying each layer from files alone made every claim machine-checkable in seconds, which is where human reviewers of AI-produced mathematics should spend their time.
