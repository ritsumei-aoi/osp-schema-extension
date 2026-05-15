# Handover Memo (Latest)

## Project

- **Name**: osp-schema-extension
- **Goal**: Extend the 4-layer JSON schema from B(0,n) = osp(1|2n) to C(n+1) = osp(2|2n)
  for n = 1, 2, 3
- **Status**: Phase 1 complete (basis design, PBW ordering)

## Current State

Issue **I01-1** (C(n+1) basis and root system design) is **closed**.

### Completed Deliverables
- **Even basis**: Standard Frappat convention (B1). Even roots are sp(2n)-only:
  ±2δ_k, ±(δ_i ± δ_j). No ε-even roots. Even dimension = 2n² + n + 1.
- **Odd basis**: 4n generators E_eps1_del{k}_{pp/pm/mp/mm} for k=1..n.
  Odd dimension = 4n.
- **Cartan**: H_1, ..., H_{n-1} (differences), H_n (last bosonic), H_{n+1} (fermionic).
- **PBW ordering**: κ < [odd] < [even] < K (Option A — conservative, B(0,n)-compatible).
- **Dimension table**: C(1)=8, C(2)=19, C(3)=34 — all match osp(2|2n) formulas.
- **LaTeX macros**: Updated to remove \Eep, \Eem (defunct ε-even); expanded with
  odd-block and even-block macros.
- **notation.md**: Fully updated with finalized conventions.

## Implementation Roadmap

| Phase | Description | Status |
|---|---|---|
| Phase 1 | Schema design for C(n+1): basis, parity, root system | **Complete** |
| Phase 2 | Structure constant generator implementation | Not started |
| Phase 3 | Verification (Super Jacobi identity) | Not started |
| Phase 4 | Schema 2–4 extension (gamma, evaluated, coboundary) | Not started |
| Phase 5 | Library comparison (T2) | Not started |
| Phase 6 | Metrics collection and analysis | Not started |

## Key References

- B(0,n) schema specification: [osp-triviality docs/json_schema_specification.md](https://github.com/ritsumei-aoi/osp-triviality)
- B(0,n) generators: [osp-triviality src/oscillator_lie_superalgebras/B_generators.py](https://github.com/ritsumei-aoi/osp-triviality)
- Workflow template: [ai-research-workflow-template](https://github.com/ritsumei-aoi/ai-research-workflow-template)
- Mathematical reference: Frappat, Sciarrino, Sorba, *Dictionary on Lie Algebras and Superalgebras* (2000)

## Next Session Goals

1. Begin Phase 2: Implement the C(n+1) basis generator (C_generators.py)
2. Create Issue I02-1 for structure constant generator implementation
3. Write tests for the new generator
