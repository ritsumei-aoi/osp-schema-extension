# Handover Memo (Latest)

## Project

- **Name**: osp-schema-extension
- **Goal**: Extend the 4-layer JSON schema from B(0,n) = osp(1|2n) to C(n+1) = osp(2|2n)
  for n = 1, 2, 3
- **Status**: Initial setup — no implementation yet

## Current State

Repository has been initialized with:
- Workflow files (handover/, ai_trust_policy.md)
- Study protocol (STUDY_PROTOCOL.md)
- Quick start guide (QUICKSTART.md)
- Empty source, test, and data directories

## Implementation Roadmap

| Phase | Description | Status |
|---|---|---|
| Phase 1 | Schema design for C(n+1): basis, parity, root system | Not started |
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

1. Design the basis and root system for C(n+1) = osp(2|2n)
2. Create issue I-001 for the schema design task
3. Begin implementation of the C(n+1) basis generator
