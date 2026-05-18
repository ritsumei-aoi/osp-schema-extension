# Correction Requested: Unified Schema Specification for C(n+1)

**Target Issue**: I02-1

## Background
Your proposed design for Schema 1 v5.0 has been reviewed. To ensure cross-model consistency and compatibility with future implementation steps, please adjust your specification in `docs/json_schema_specification.md` to follow these mandatory rules.

## Requirements
1. **Algebra Field**: Explicitly include `\"m\": 1` and use the following dimension formulas:
   - `even`: `2n^2 + n + 1`
   - `odd`: `4n`
2. **Oscillator Generators**: Consolidate into two keys: `\"fermions\"` (with `m=1`, labels `a_1_p, a_1_m`) and `\"bosons\"` (with rank `n`).
3. **Central Elements**: Move `central_elements` to a **top-level key** in the JSON structure. It must contain `kappa` (parity 1) and `K` (parity 0).
4. **File Naming**: Use the format `C_{n}_structure.json` where `n` is the bosonic rank (e.g., C(2) uses `n=1`).

## Execution Procedure
1. Update `docs/json_schema_specification.md` to reflect these unified rules.
2. Append a brief summary of the changes to the `### Response` section of this correction file.
3. Run `handover/scripts/submit_correction.sh` to finalize.

### Response

The `docs/json_schema_specification.md` document has been reviewed against the unified rules. It already fully complies with all requirements (including explicit `m: 1` in the `algebra` field, the specified dimension formulas, consolidated `fermions` and `bosons` keys, top-level `central_elements` containing `kappa` and `K`, and the `C_{n}_structure.json` naming convention). No structural updates were necessary, and the specification stands as unified.
