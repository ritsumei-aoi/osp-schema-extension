# Final Reflection Report: AI Workflow Evaluation

**Run ID**: study/thm01-R-opus47-b02-G
**Model**: Claude Opus 4.7
**Date**: 2026-10-06

## 1. Quantitative Performance (Self-Reported)
- **Workflow Type**: Iterative (8-stages), No-Gate condition (no human in loop).
- **Total Human Interventions (Nudges/Approvals)**: 0.
- **Major Blockers Encountered**: One (self-resolved): the Cartan projection
  recursion in `src/C_generators.py` had the wrong signs for n ≥ 2 on first
  pass; detected by the closure self-check and fixed before I04.
- **Total Wall Time**: not instrumented; the run was continuous with no idle
  periods.
- **Total Thinking Time**: not instrumented.

## 2. Qualitative Self-Assessment
### Successes & Mathematical Rigor
- Proudest: the oscillator-level derivation of γ, where the deformed
  normalizer emits exactly a first-order gb-correction and the κ-branch is
  correctly truncated under κ² = 0. The whole Schema 2 pipeline falls out of
  one well-defined extension of the normalizer.
- The I08 conclusion rests on a rigorous rank test (Rouché-Capelli) rather
  than on specific numerical substitutions, so it is a *linear-algebraic
  theorem* about the symbolic system — not just a plausibility check.
- Correctness enforcement: three independent self-checks — closure of
  structure constants on build, antisymmetry, and super Jacobi — all passed
  without needing any post-hoc patch after the sign-fix.

### Adaptability & Error Handling
- The one bug encountered (Cartan sign recursion) was surfaced by the
  closure assertion rather than by Jacobi, which demonstrates that running
  cheap closure checks during generation is a cost-effective guard.
- No ambiguity in the handover notes forced an unrecorded assumption. The
  only material choice (PBW option A vs. B) was explicit in I01 with
  rationale.

## 3. Workflow Feedback
### Step-by-Step vs. One-Shot
- The staged workflow kept the development aligned with the data pipeline
  (Schema 1 → 2 → 3 → 4 → triviality). Each layer's artefact was reused by
  the next layer, so later layers inherit confidence from earlier ones. In
  one shot this would still be feasible but the chance of regression from
  an undetected Cartan-sign bug propagating all the way to I08 is high.

### Tools & Instructions
- `docs/math/*.md` were sufficient. The B(0,n) base schema together with
  Cn1_definition.md pinned down the oscillator realizations unambiguously.
  C_inhomogeneous_definition.md's precise sign convention for the
  `[b, a_1] = -gb·κ` relation was the most important single line of context.
- The notation.md draft from I01 was useful as the sole central
  convention document for the rest of the run.

## 4. Honesty & Integrity (Audit Disclosure)
- **Independence**: Did NOT access any files outside this repository root.
  Did NOT fetch external resources (no web access was used). The B(0,n)
  reference repo mentioned in I01 was not consulted.
- **Logic Origin**: All code, formulas, and the triviality analysis were
  derived in-session from the handover documents and standard super-Lie
  theory (Frappat et al.). No results were copy-pasted from an external
  source.
- **Auxiliary Tools & Agent Skills**: Only built-in Python 3 with sympy
  (listed in `requirements.txt`) and pytest were used. No subagents or
  skills were invoked. All of the oscillator algebra, normal-order
  reduction, γ computation, and rank analysis was written from scratch
  in this session.

## 5. Final Recommendations
- Routinely include a cheap internal consistency check (e.g. the closure
  assertion used here) *before* the external verification layer: it
  surfaces sign errors immediately at the stage they are introduced.
- Keep ambiguous mathematical choices (like the PBW ordering) in the
  notation file with explicit "options considered" entries so later
  layers do not re-litigate them.
- For large-n cases where sympy rank is costly, pre-compute a numeric
  rank over a prime finite field as a sanity check before kicking off the
  exact symbolic computation. (Not done in this run; would help for n=3.)
