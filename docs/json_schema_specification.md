# C(n+1) = osp(2|2n) JSON Schema Specification (v5.0 extension)

Complete, standalone specification of the C(n+1) schema, derived from
`docs/math/B0n_schema_v5.md` and `docs/math/Cn1_definition.md`.
Conventions (labels, PBW ordering) are those of `handover/notation.md`.
Schemas 2-4 are appended below as they are implemented (I05-I07).

## Overview

| Layer | File | Contents |
|---|---|---|
| Schema 1 | `data/C_{n}_structure.json` | Algebra structure: basis, parity, oscillator realization, structure constants |
| Schema 2 | `data/C_{n}_gamma.json` | Symbolic inhomogeneous deformation (γ-structure, linear in gb) |
| Schema 3 | `data/C_{n}_evaluated.json` | γ evaluated at a concrete gb assignment |
| Schema 4 | `data/C_{n}_coboundary.json` | Coboundary δf of an odd linear map f |

`n` is the **bosonic rank**: C(2)=osp(2|2) is `n=1`, C(3) is `n=2`, C(4) is `n=3`.

---

## Schema 1: Algebra Structure

Top-level keys (in order):
`schema_version, algebra, oscillator_generators, oscillator_relations, central_elements, basis, parity, generator_realization, structure_constants, metadata`.

### `schema_version`
`"5.0"` (unchanged from B(0,n); C(n+1) is an extension, new/changed keys listed below).

### `algebra`
```json
{
  "family": "C", "m": 1, "n": 2, "cartan_type": "C(3)",
  "alternative_notation": {"osp": "osp(2|4)", "dimension_formula": "osp(2m|2n) with m=1"},
  "dimension": {"total": 19, "even": 11, "odd": 8}
}
```
Dimension formulas: even = 2n²+n+1, odd = 4n, total = 2n²+5n+1.

| n | algebra | even | odd | total |
|---|---|---|---|---|
| 1 | C(2) | 4 | 4 | 8 |
| 2 | C(3) | 11 | 8 | 19 |
| 3 | C(4) | 22 | 12 | 34 |

### `oscillator_generators`
Two keys: `fermions` (no `supplementary_fermion`) and `bosons`.
```json
{
  "fermions": {"m": 1, "count": 2, "labels": ["a_1_p", "a_1_m"], "parity": 1, "description": "..."},
  "bosons": {"count": 4, "n": 2, "labels": ["b_1_p","b_1_m","b_2_p","b_2_m"], "description": "..."}
}
```

### `oscillator_relations`
```json
{
  "standard_fermion_anticommutators": {"relations": {"conjugate_pair": "{a_1^-, a_1^+} = 1", "same_type": "(a_1^+)^2 = (a_1^-)^2 = 0"}},
  "bosonic_commutators": {"relations": {"same_type": "[b_i^±, b_j^±] = 0", "conjugate_pair": "[b_i^-, b_j^+] = δ_{ij}"}},
  "mixed_commutators": {"boson_fermion": "[b_i^±, a_1^±] = 0 (undeformed Schema 1)"}
}
```
Replaces `supplementary_fermion_relation` of B(0,n).
In Schema 2 the mixed commutator becomes `[b_j^s, a_1^σ] = -gb_{σ,j,s} κ`.

### `central_elements` (top-level key)
```json
{
  "kappa": {"parity": 1, "nilpotent": true, "relation": "kappa^2 = 0", "description": "..."},
  "K":     {"parity": 0, "identification": "scalar 1", "description": "..."}
}
```
κ has parity 1 (as in `C_inhomogeneous_definition.md`). **Note**: in the B(0,n) base document κ was listed with parity 0 in the JSON; for C(n+1) the unified rule is κ odd, K even. K is identified with 1 and is not a basis element; κ appears in Schema 1 only formally (Schema 1 brackets are undeformed).

### `basis`
```json
{"even": ["H_1", "H_2", "H_3", "E_2del1_p", ...], "odd": ["E_eps1_del1_pp", ...],
 "ordering_convention": "PBW: κ < [odd] < [even]  (K = 1 is excluded)"}
```
Odd generators `E_eps1_del{k}_{pp|pm|mp|mm}` replace `E_del{k}_p/m` (4n instead of 2n). Even list has the additional Cartan generator (so(2) part), `H_1..H_{n+1}`.

### `parity`
Map name → 0/1 for every basis element (odd generators `E_eps1_del*` have parity 1).

### `generator_realization`
`ordering` is `"a_1_p, a_1_m, b_1_p, b_1_m, ..."`. Each entry of `realizations`:
```json
"E_eps1_del1_pm": {"standard_form": [{"words": ["a_1_p", "b_1_m"], "coeff": "1"}],
                   "frappat_form": "1*a_1^+ b_1^-", "parity": 1}
```
`words` are normal-ordered oscillator words (letters from `ordering`); empty `words` = scalar (K=1).
`H_1 = a_1_p a_1_m + b_1_p b_1_m`; `H_{n+1} = -b_n_p b_n_m - 1/2`.
Normalization: `E_{±2δ_k} = (b_k^±)^2` (no 1/2).

### `structure_constants`
List of **all** non-zero graded brackets for **every ordered pair** (X, Y) (both (X,Y) and (Y,X) are stored so antisymmetry is independently checkable):
```json
{"X": "H_1", "Y": "E_eps1_del1_pp", "Z": "E_eps1_del1_pp", "coeff": "1", "sign_rule": "graded"}
```
Meaning `[X,Y} = Σ coeff · Z` with `[X,Y} = XY - (-1)^{p(X)p(Y)} YX`. `coeff` is an exact rational string (`"1"`, `"-1/2"`). Absent triples are zero.

### `metadata`
`generated_by`, `generation_date`, `convention`, `references`.

---

## Compatibility with the B(m,n) / B(0,n) v5.0 schema

| Aspect | Status |
|---|---|
| Top-level key set | Superset: all B(0,n) keys retained; `central_elements` is new and top-level |
| `schema_version` | unchanged `"5.0"`; `algebra.family == "C"` discriminates |
| `algebra` | Same fields; `m` = 1; new dimension formulas |
| `oscillator_generators` | `supplementary_fermion` → `fermions` (breaking for B(0,n) readers that require the former; readers must dispatch on `family`); `bosons` identical |
| `oscillator_relations` | `supplementary_fermion_relation` → `standard_fermion_anticommutators`; `bosonic_commutators` identical |
| `basis`, `parity`, `generator_realization`, `structure_constants` | Same layout; labels `E_eps1_del{k}_{ee}` added; Cartan `H_{n+1}` realization differs |
| File naming | `C_{n}_structure.json` parallel to `B_{n}_structure.json` |
| Structure-constant entries | Same record layout `{X,Y,Z,coeff,sign_rule}` |

A reader that dispatches on `algebra.family` and ignores unknown keys can load both families.

## File naming
`C_1_structure.json` (C(2)), `C_2_structure.json` (C(3)), `C_3_structure.json` (C(4)); likewise `_gamma`, `_evaluated`, `_coboundary`.
