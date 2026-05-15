# AI Trust Policy — osp-schema-extension

This document defines the delegation boundary between human and AI for this project.

## Tasks Delegable to AI

- Implement structure constant generators from mathematical specifications
- Generate and execute test code (pytest)
- Create JSON schema files following the specification
- Run benchmark scripts and collect results
- Update documentation and handover memos
- Execute Git operations (branch, commit, push)
- Refactor existing code when instructed

## Tasks NOT Delegable to AI

- **Final judgment on mathematical correctness** of structure constants
- **PBW ordering decisions** (mathematical convention choice)
- **Gram matrix sign conventions** (requires domain expertise)
- **Schema design approval** (human must review and approve new schema fields)
- **Interpretation of verification failures** (human decides if failure is a bug or a design issue)
- **Paper submission decisions**

## Trust Conditions

All of the following must hold before AI output is accepted:

1. All tests pass: `pytest tests/ -v`
2. Super Jacobi identity verification passes for all generator triples
3. Output is human-readable and mathematically interpretable
4. Changes are consistent with the existing schema specification
5. No previously passing tests are broken

## Escalation Protocol

When the AI encounters a task at or beyond its trust boundary:

1. Stop execution
2. Document the situation in the current issue file under "## Trust Boundary Remand"
3. Present the options to the human with a clear recommendation
4. Wait for human decision before proceeding
