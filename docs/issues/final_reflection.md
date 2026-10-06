# Final Reflection Report: AI Workflow Evaluation

**Run ID**: study/thm01-R-opus5-b02-G (condition G, No-Gate)
**Model**: Claude Opus 5 (`claude-opus-5`), running in Claude Code
**Date**: 2026-10-06

## 1. Quantitative Performance (Self-Reported)

- **Workflow Type**: Iterative (8 stages), executed under the **No-Gate**
  condition — all eight issues completed in a single session with no human
  approval steps.
- **Total Human Interventions (Nudges/Approvals)**: **0**. The only
  human-in-the-loop event was a single permission prompt from the harness when a
  `sed` invocation tried to edit a file in the working directory; I switched to
  the `Edit` tool instead. No mathematical or design input was received.
- **Major Blockers Encountered**: none that stopped work. Three substantive
  issues were encountered and resolved in-session (details in §2):
  1. a contradiction in the source documents about the parity of the `gb`
     parameters (I05);
  2. a contradiction between `B0n_schema_v5.md` and `B0n_definition.md` about the
     parity of κ (I02);
  3. the discovery that γ takes values in $\mathfrak g\oplus\mathbb CK$ rather
     than $\mathfrak g$, which forced a design decision about the target of the
     map $f$ (I05 → I07).
  One genuine mistake of my own: a sign error in the hand derivation relating
  $\gamma$ to $\delta f$, caught immediately by the symbolic comparison (I07 §4).
- **Total Wall Time**: I do not have access to a session clock. The computational
  work is fast and fully reproducible: the complete pipeline
  (`C_generators` → `verify_C_structure` → `C_gamma` → `C_evaluate` →
  `C_coboundary` → `C_triviality`) runs in **≈ 13 s**, and the test suite
  (196 tests) in **3.5 s**, both measured with `time` and recorded in the issue
  Responses. My own elapsed time was dominated by reading and writing, not compute.
- **Total Thinking Time**: not exposed to me by the harness; I cannot report it
  honestly and will not estimate it.
- **Artefacts produced**: 6 source modules, 6 test modules (196 tests), 31 JSON
  data files, 1 schema specification, 1 rewritten notation document, 8 issue
  Responses, 8 commits.

## 2. Qualitative Self-Assessment

### Successes & Mathematical Rigor

**The design decision I was most pleased with was made in I03, and paid off four
times.** Instead of hard-coding a table of structure constants, I built a
normal-ordering engine for the oscillator algebra and computed every bracket as
a graded commutator inside $\mathcal U(A)$. Three consequences:

- Closure of the chosen 8/19/34-dimensional spans became a *runtime assertion*
  (`decompose` raises if a bracket leaves the span) rather than an assumption.
- Layer 2 (γ) required **no new bracket logic**: the inhomogeneous deformation is
  literally one extra contraction rule, $[b_k^s, a_1^\sigma] = -\mathrm{gb}\,\kappa$.
- Layer 4's map $f$ could be derived in closed form from an oscillator
  substitution, instead of being fitted numerically.

**A small decision in I01 that prevented a lot of downstream mess**: normalizing
the Cartan elements symmetrically, `H_eps1` $= a_1^+a_1^- - \tfrac12$ and
`H_del{k}` $= b_k^+b_k^- + \tfrac12$. With the naive choice, every structure
constant table carries spurious $K$ terms and the "basis" is not a subalgebra of
$\mathfrak g$. I verified empirically that zero $K$-components appear at all
three ranks — and, importantly, verified in I07/I08 that this choice does *not*
sweep the genuine $K$-components of γ under the rug.

**The challenge I was proudest to solve** was identifying *why* $C(n+1)$'s
deformation is trivial, rather than just reporting that it is. The mechanism is
that the whole deformation can be absorbed by $a_1^\sigma \mapsto a_1^\sigma +
\kappa u_\sigma$ with $u_\sigma$ a bosonic element built from the gb parameters
via the inverse of the symplectic form. That explanation is $n$-independent, it
predicts the solution space exactly ($f$ unique up to $\mathrm{ad}(\mathfrak g_{\bar 1})$,
dimension $4n$), and it generates a falsifiable prediction about the contrasting
$B(0,n)$ case (the single supplementary fermion $a_0$ admits no such shift).

**How I ensured accuracy of the final triviality conclusion.** I deliberately did
not let a single computation carry the result. The conclusion rests on:

1. **Exhaustive, exact checks at every layer.** Super Jacobi on *all* $N^3$
   triples in both the derivation and cyclic forms (92 750 triple-identities),
   graded antisymmetry on all $N^2$ pairs, computed from the oscillator engine
   independently of the stored table, then the stored table checked against the
   engine. All arithmetic exact (`Fraction` / sympy); **no floating point
   anywhere in the project**.
2. **Symbolic rather than sampled results.** The 2-cocycle condition for γ and
   the identity $\delta f = \gamma$ hold as polynomial identities in all $4n$ gb
   symbols, so the conclusion covers the whole parameter space, not 7 sample
   points. The 7 numeric profiles are corroboration, not the evidence base.
3. **Two independent routes to $f$.** An analytic construction (I07) and a blind
   exact linear solve of up to 20 825 equations in 540 unknowns over
   $\mathbb Q(\mathrm{gb})$ (I08). They agree exactly — the solver's particular
   solution *equals* the analytic $f$.
4. **Deliberate counterfactuals.** I re-ran the comparison with the $K$-target of
   $f$ removed, so I could state precisely which assumption the result depends on
   and what happens without it (12/40/84 obstructions). A result that flips under
   a plausible reading of the source document should be reported with that
   reading made explicit, not hidden behind a single verdict.
5. **Independent cross-generation at Layer 3**: data produced both by substituting
   into the symbolic table and by rebuilding the whole deformed algebra with
   numeric gb, then compared.

### Adaptability & Error Handling

**Document contradictions.** Three were found and all were handled the same way:
state the contradiction explicitly, enumerate the readings, pick one, give the
reason, and record it in the issue Response so an auditor can disagree with the
choice without re-deriving anything.

- *gb parity* (I05): `C_inhomogeneous_definition.md` §1 forces gb to be even,
  while its own Parity Note asserts odd. I adopted even, and I believe I found
  the cause rather than just picking: the Note is correct for $B(0,n)$, where gb
  multiplies the degree-one element $b_j^s$ inside $a_0^2$, and was carried over
  without re-deriving. The parity ledger $p(\gamma) = p(X)+p(Y)+1$ then closes on
  all 744 entries at $n=3$, which would fail under the other reading.
- *κ parity* (I02): the B schema doc says 0, the B definition doc says 1, the
  issue's mandatory rule says 1. I took 1 and recorded the divergence in-line in
  the specification.
- *File naming* (I06): the spec I wrote in I02 said
  `C_{n}_evaluated_{profile}.json`, the issue asked for `C_{n}_evaluated.json`.
  I emitted both, with a test asserting the alias stays identical to the primary
  profile — rather than silently preferring one document over the other.

**My own error.** My paper derivation predicted $\gamma = \delta(-f_{\rm nat})$;
the first run returned $\delta f = -\gamma$ uniformly. Because the mismatch was
*exactly* $-2\gamma$ on every one of the 36 pairs, the diagnosis was immediate: a
sign slip when converting $[f(Y),X]$ to $[X,f(Y)]$, not a structural error. I
corrected the code, recorded the correction in the I07 Response rather than
quietly fixing it, and kept the `delta_f` implementation verbatim from the source
document so the convention is auditable.

**A real bug I caught by reading my own output sceptically.** On the first run of
the restricted linear solve (I08), it reported *consistent*, which contradicted
I07's finding that removing $K$ from $f$ breaks 12 pairs. Two of my own results
disagreeing is a much stronger signal than either one alone. The cause: when I
restricted the *target* of $f$ I had also, inadvertently, dropped the $K$-component
*equations* — so the system was answering an easier question. Fixed by separating
equation targets from unknown targets. Without the earlier counterfactual in I07
I would have had nothing to contradict, and would likely have published a wrong
"always trivial even without $K$" claim.

**Where I lacked context.** Three places, none fatal:

- `docs/math/README.md` and I01 both point to the existing $B(0,n)$
  implementation (`github.com/ritsumei-aoi/osp-triviality`) and to
  `docs/drafts/aoi2026_triviality_osp1_2n.tex`. Neither is present in this
  repository and I was instructed not to use web access, so the comparison with
  $B(0,n)$ in I08 §5 is a *prediction derived from the provided definitions*,
  clearly labelled as unverified. If the point of the study is the $B\to C$
  contrast, having the $B$ data locally would have strengthened the conclusion
  considerably.
- `handover/handover_memo_latest.md` references
  `scripts/extract_latest_session.sh`, `handover_memo_format.md` and
  `handover_memo_archived.md`, none of which exist. I left the memo untouched
  rather than invent a format.
- The final reflection template asks for session statistics (wall time, thinking
  time, token usage) that the harness does not expose to me. I have reported what
  I can measure and declined to estimate the rest.

## 3. Workflow Feedback

### Step-by-Step vs. One-Shot

I ran the **Step-by-Step (8-stage)** workflow, in its No-Gate variant.

**The staging helped, and specifically in a way one-shot would not have.** The
value was not context management — the whole project fits comfortably in context
— but **forced commitment**. Each issue made me fix a decision and write down the
alternatives *before* seeing the downstream consequences. Concretely:

- I01 forced the Cartan normalization choice before I knew it would matter for
  $K$-leakage; because it was recorded with reasons, I could check in I04 whether
  it had been the right call and in I07 whether it was hiding anything.
- I04's exhaustive verification sat between the structure constants and γ, so by
  the time I reached the triviality question I was not simultaneously debugging
  the algebra and interpreting the result.
- I05's observation that γ has $K$-components was recorded as an open flag for
  I07 instead of being resolved on the spot. That gap is exactly where the I07
  design decision, the I07 counterfactual, and ultimately the I08 bug-catch came
  from.

**Could I have reached the final conclusion in one session?** I did — this *was*
one session. The honest answer is that I would have reached the same headline
result one-shot, but with materially worse rigour: the two document
contradictions would likely have been resolved silently, the $K$-component
question would have been settled by whichever convention made the code run, and
the restricted-setting analysis in I08 §4 — the only place a genuine obstruction
appears — would probably not exist at all, because nothing would have prompted me
to ask the counterfactual. The staging's real contribution is that it makes
*recording the reasoning* a deliverable rather than a courtesy.

**Cost of the No-Gate condition.** There were two or three points where a
30-second human answer would have been worth more than my careful reasoning:
"is gb even or odd?", "should $f$ target $\mathfrak g$ or $\tilde{\mathfrak g}$?".
I resolved both and I believe correctly, but I resolved them by inferring the
author's intent from internal consistency, which is a weaker form of evidence
than asking. The mitigation I adopted — report *both* readings and their
consequences, and make the dependence explicit — is what I would recommend as the
standard protocol for autonomous runs: not "decide and move on", but "decide,
quantify what changes if the decision is wrong, and continue".

### Tools & Instructions

**Were `docs/math/` sufficient and clear?** Largely yes — they were genuinely
self-contained on the root system, the oscillator realization and the coboundary
formula, which is what made an unsupervised run feasible. Specific feedback:

- `Cn1_definition.md` is the strongest document: §1 and §3 gave me the dimension
  tables and the $B\!\to\!C$ differences in exactly usable form, and the counts
  $(4|4), (11|8), (22|12)$ let me self-check immediately.
- Its §2 is the weakest point: the simple generators are given in mixed
  normalization ($H_1 = a_1^+a_1^- + b_1^+b_1^-$ but $H_{n+1} = -b_n^+b_n^- - \tfrac12$),
  which left the Cartan convention under-determined. One sentence fixing
  symmetrized vs unsymmetrized would remove the ambiguity.
- `C_coboundary_definition.md` §3 says "up to scalar", which I was unsure how to
  read (an overall scalar multiple of γ? a $K$-ambiguity?). I interpreted it as
  not needed — I obtained exact equality $\delta f = \gamma$ with no scalar — but
  the phrase is worth pinning down. It also does not say whether $\{Z_i\}$ includes
  $K$, which turned out to be the single most consequential ambiguity in the project.
- `C_inhomogeneous_definition.md`'s Parity Note should be corrected or marked as
  inherited from $B(0,n)$.
- A worked miniature example — the full $C(2)$ bracket table, say — would be an
  excellent cheap safeguard: it would catch a wrong basis or sign convention in
  minutes rather than at Layer 4.

**Scripts** (`close_issue.sh`, `submit_correction.sh`): not present in this
repository, so not applicable. Likewise `scripts/extract_latest_session.sh`
referenced by the handover memo.

**Harness.** The permission model worked sensibly. I note one asymmetry worth
knowing for future runs: shell commands that write into the working tree prompt
for approval, while the dedicated edit tools do not — under a No-Gate condition
with no human present, a shell-heavy approach would stall. Using the file tools
throughout avoided this entirely.

## 4. Honesty & Integrity (Audit Disclosure)

- **Independence**: **No.** I accessed no files outside this repository root
  (`/Users/aoi/notebook/git/thm01-R-batch/thm01-R-opus5-b02-G`). I did not open
  any `workspaces/osp-schema-extension/thm01-XX/` directory, any sibling run
  directory, or any other local path. I made **no network requests** and did not
  consult `github.com/ritsumei-aoi/osp-triviality` or arXiv, although both are
  referenced by the task documents — this is why the $B(0,n)$ comparison in I08
  is labelled a prediction rather than a result.
- **Logic Origin**: All computations are my own. Every script in `src/` was
  written from scratch in this session; nothing was copy-pasted from an external
  source. The mathematical content came from the documents in `docs/math/` plus
  my own derivations, and every quantitative claim in the issue Responses is the
  output of a script in this repository that the reader can re-run. The one place
  I used prior knowledge rather than the provided documents is standard
  background (CAR/CCR normal ordering, the graded Jacobi identity, $\mathfrak{sl}_2$
  commutation relations used as spot-checks) — and each such check was then
  confirmed against the generated data rather than asserted.
- **Auxiliary Tools & Agent Skills**: **None.** I did not invoke any subagent, any
  Agent Skill, any workflow/orchestration tool, Rubber Duck, or any secondary AI
  assistant. Tooling used: the file read/write/edit tools, `git`, and `python3`
  with `sympy` (1.14.0) and the standard library (`fractions`, `json`,
  `itertools`), plus `pytest` — all from the repository's own `requirements.txt`.
  `numpy`/`scipy` are listed there but I deliberately did not use them, to keep
  every computation exact.
- **Self-assessment of residual risk**: the result is verified exhaustively and
  symbolically for $n = 1, 2, 3$, but it is **not a proof for general $n$**; I have
  stated it as a conjecture with an $n$-independent mechanism and a proof sketch,
  which I believe is the honest classification. The headline conclusion also
  depends on one interpretive choice (the target of $f$), which I have flagged
  prominently and quantified rather than buried.

## 5. Final Recommendations

1. **Make conventions machine-checkable, not prose.** Most of my risk came from
   normalization and parity conventions stated in prose that later contradicted
   itself. A short "conventions" block that a script can assert against — a dozen
   expected bracket values for the smallest rank — would have caught any such
   error in the first minute instead of the fourth layer.
2. **Ask the AI for the counterfactual, not just the answer.** The most useful
   thing I produced in I08 is not "trivial" but "trivial *under this reading*,
   non-trivial under that one, and here are the 12 equations that distinguish
   them". For mathematics, a collaborator who reports which assumption the
   conclusion hangs on is far more useful than one who reports a verdict. I would
   make this an explicit deliverable in the issue template.
3. **Prefer symbolic parameters over sampled values wherever they are affordable.**
   Carrying the $4n$ gb symbols all the way through cost almost nothing in
   runtime and upgraded the result from "trivial at 7 sample points" to "trivial
   identically". Humans tend to ask AI for a worked example; asking for the
   general identity is often no harder and is worth much more.
4. **Design tasks so that two independent paths meet.** Every error I caught in
   this session was caught by a disagreement between two of my own results, never
   by re-reading code. The staged workflow accidentally produced this structure;
   making it deliberate — requiring each conclusion to be reached twice by
   different means — would be my single highest-value recommendation.
5. **For autonomous (No-Gate) runs, replace approval gates with explicit
   assumption ledgers.** The gate's real function is to catch a wrong premise
   early. When no human is available, the substitute is not more confidence —
   it is a written, auditable record of every judgement call with its
   alternatives and its blast radius. That is what I tried to do in each
   Response, and I would standardize it.
6. **Give the AI the comparison case when the study is about a comparison.** This
   project's scientific interest is the $B(0,n) \to C(n+1)$ contrast, but only
   the $C$ side was computable here. Shipping the $B(0,n)$ data alongside would
   have let me *test* the structural explanation instead of merely predicting it.

---

*Submitted for scientific evaluation of the workflow. All claims above are
reproducible from this repository; where I could not verify something, I have
said so.*
