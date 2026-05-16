# Handover Memo (Latest)

## Project

- **Name**: osp-schema-extension
- **Goal**: Extend the 4-layer JSON schema from B(0,n) = osp(1|2n) to C(n+1) = osp(2|2n)
  for n = 1, 2, 3
- **Status**: Phase 1 complete (basis design, PBW ordering)

## Current State

Issue **I01-1** (C(n+1) basis and root system design) is **closed**.
Issue **I02-1** (Schema 1 v5.0 extension for C(n+1)) is **closed**.

### Completed Deliverables
- **Phase 1**: Basis, PBW ordering, and notation finalized
- **Phase 2 prep**: Schema 1 v5.0 specification created at `docs/json_schema_specification.md`
  - `algebra` section with family="C", m=1, formula osp(2m|2n)
  - `oscillator_generators` with standard fermionic pair (no supplementary fermion)
  - `oscillator_relations` with CAR for a_1_p, a_1_m
  - `central_elements` as new top-level key (κ, K)
  - File naming: `C_n_structure.json` for n=1,2,3
  - Backward compatibility with B(m,n) documented
- **Signature conventions**: B1 (standard Frappat basis), Option A (conservative PBW)
- **Phase 2 implementation**: Structure constant generator completed
  - `src/C_generators.py` with `build_C_basis()` and `build_C_structure_constants()`
  - `tests/test_C_generators.py` with 29 tests (all pass for n=1,2,3)
  - `data/algebra_structures/C_{1,2,3}_structure.json` generated
  - `src/generate_C_json.py` for JSON output generation

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
| Phase 2 | Structure constant generator implementation | **Complete** |
| Phase 3 | Verification (Super Jacobi identity) | **Complete** |
| Phase 4 | Schema 2–4 extension (gamma, evaluated, coboundary) | Not started |
| Phase 5 | Library comparison (T2) | Not started |
| Phase 6 | Metrics collection and analysis | Not started |

## Key References

- B(0,n) schema specification: [osp-triviality docs/json_schema_specification.md](https://github.com/ritsumei-aoi/osp-triviality)
- B(0,n) generators: [osp-triviality src/oscillator_lie_superalgebras/B_generators.py](https://github.com/ritsumei-aoi/osp-triviality)
- Workflow template: [ai-research-workflow-template](https://github.com/ritsumei-aoi/ai-research-workflow-template)
- Mathematical reference: Frappat, Sciarrino, Sorba, *Dictionary on Lie Algebras and Superalgebras* (2000)

## Next Session Goals

1. Phase 4: Schema 2–4 extensions (gamma, evaluated, coboundary)
3. Phase 5: Library comparison (T2) with Garli or similar
4. Phase 6: Metrics collection and analysis
