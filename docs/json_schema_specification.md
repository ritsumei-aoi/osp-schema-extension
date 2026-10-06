# C(n+1) = osp(2|2n) JSON Schema Specification (v5.0 extension)

Complete, standalone specification of the 4-layer JSON schema for $C(n+1)$, obtained from
the B(0,n) v5.0 schema (`docs/math/B0n_schema_v5.md`). Conventions: `handover/notation.md`.
Generators: `src/C_generators.py` (Layer 1), further layers in later sections.

| Layer | File | Contents |
|---|---|---|
| Schema 1 | `data/C_{n}_structure.json` | basis, parity, oscillator realization, structure constants |
| Schema 2 | `data/C_{n}_gamma.json` | symbolic inhomogeneous deformation γ (linear in gb) |
| Schema 3 | `data/C_{n}_evaluated.json` | γ evaluated at a numerical gb assignment |
| Schema 4 | `data/C_{n}_coboundary.json` | coboundary δf of an odd linear map f |

**File naming**: `C_{n}_structure.json` with $n$ the *bosonic rank*: C(2)=osp(2|2) → `C_1_...`,
C(3)=osp(2|4) → `C_2_...`, C(4)=osp(2|6) → `C_3_...`.

---

## Schema 1: Algebra Structure

Top-level keys (order as listed):
`schema_version`, `algebra`, `oscillator_generators`, `oscillator_relations`, `central_elements`,
`basis`, `parity`, `generator_realization`, `structure_constants`, `metadata`.

### `schema_version`
`"5.0"`.

### `algebra`
```json
{
  "family": "C", "m": 1, "n": 2, "cartan_type": "C(3)",
  "alternative_notation": {"osp": "osp(2|4)", "dimension_formula": "osp(2m|2n) with m=1"},
  "dimension": {"total": 19, "even": 11, "odd": 8}
}
```
Dimension formulas: even $=2n^2+n+1$, odd $=4n$, total $=2n^2+5n+1$.

| n | algebra | even | odd | total |
|---|---|---|---|---|
| 1 | C(2) | 4 | 4 | 8 |
| 2 | C(3) | 11 | 8 | 19 |
| 3 | C(4) | 22 | 12 | 34 |

### `oscillator_generators`
Two keys, `fermions` and `bosons` (the B(0,n) `supplementary_fermion` is removed):
```json
{
  "fermions": {"m": 1, "count": 2, "labels": ["a_1_p", "a_1_m"], "parity": 1,
               "description": "Standard fermionic pair a_1^+, a_1^- (CAR)."},
  "bosons": {"count": 4, "n": 2, "labels": ["b_1_p","b_1_m","b_2_p","b_2_m"],
             "description": "Bosonic oscillators b_i^± with i=1,...,n"}
}
```

### `oscillator_relations`
```json
{
  "standard_fermion_anticommutators": {
    "description": "CAR for the standard pair",
    "relations": {"conjugate_pair": "{a_1^-, a_1^+} = 1", "same_type": "(a_1^±)^2 = 0"}},
  "bosonic_commutators": {
    "description": "...",
    "relations": {"same_type": "[b_i^±, b_j^±] = 0 for all i, j", "conjugate_pair": "[b_i^-, b_j^+] = δ_{ij}"}},
  "mixed_commutators": {
    "boson_fermion": "[b_j^s, a_1^σ] = 0 (undeformed); deformed in Schema 2 as -gb_{σ,j,s} κ"}
}
```

### `central_elements` (top-level key)
```json
{
  "kappa": {"parity": 1, "nilpotent": true, "relation": "kappa^2 = 0", "description": "Odd central element."},
  "K": {"parity": 0, "value": "1", "description": "Even central element, identified with the scalar 1; not a basis element."}
}
```

### `basis`
PBW: `κ < [odd] < [even]` (K=1 excluded).
```json
{"even": ["H_1","H_2","H_3","E_2del1_p","E_2del2_p","E_del1_del2_pp","E_2del1_m","E_2del2_m",
          "E_del1_del2_mm","E_del1_del2_pm","E_del1_del2_mp"],
 "odd":  ["E_eps1_del1_pp","E_eps1_del2_pp","E_eps1_del1_pm","E_eps1_del2_pm",
          "E_eps1_del1_mp","E_eps1_del2_mp","E_eps1_del1_mm","E_eps1_del2_mm"],
 "ordering_convention": "PBW: κ < [odd: ...] < [even: ...]  (K = 1 is excluded)"}
```
Odd labels `E_eps1_del{k}_{ee}{dd}` have 4n members: `pp`: $\varepsilon+\delta_k$ ($a_1^+b_k^+$),
`pm`: $\varepsilon-\delta_k$ ($a_1^+b_k^-$), `mp`: $-\varepsilon+\delta_k$ ($a_1^-b_k^+$),
`mm`: $-\varepsilon-\delta_k$ ($a_1^-b_k^-$). Even labels as in `notation.md`.

### `parity`
`{label: 0|1}` for every basis element (even → 0, `E_eps1_*` → 1).

### `generator_realization`
```json
{
  "description": "...",
  "ordering": "a_1_p, a_1_m, b_1_p, b_1_m, ...",
  "realizations": {
    "H_1": {"standard_form": [{"words": ["a_1_p","a_1_m"], "coeff": "1"},
                              {"words": ["b_1_p","b_1_m"], "coeff": "1"}], "parity": 0},
    "H_3": {"standard_form": [{"words": [], "coeff": "-1/2"}, {"words": ["b_2_p","b_2_m"], "coeff": "-1"}], "parity": 0},
    "E_eps1_del1_pm": {"standard_form": [{"words": ["a_1_p","b_1_m"], "coeff": "1"}], "parity": 1}
  }
}
```
`words` are normal-ordered oscillator words (ordering above); `[]` is the constant 1.
No `a_0` appears. Cartan elements are the Weyl-symmetrised forms of `Cn1_definition.md`.

### `structure_constants`
List of the non-zero graded brackets $[X,Y\}=\sum_Z c\,Z$ for **all ordered pairs** $(X,Y)$ (both orders stored):
```json
{"X": "H_1", "Y": "E_eps1_del1_pp", "Z": "E_eps1_del1_pp", "coeff": "1", "sign_rule": "graded"}
```
`coeff` is a rational string (`"1"`, `"-1/2"`).

### `metadata`
`generated_by`, `generation_date`, `references` as in B(0,n) v5.0.

---

## Compatibility with B(m,n) v5.0

| Key | B(0,n) v5.0 | C(n+1) | Compatibility |
|---|---|---|---|
| `schema_version` | 5.0 | 5.0 | unchanged |
| `algebra` | family B, m=0 | family C, m=1, same sub-keys | same shape; consumers switch on `family` |
| `oscillator_generators` | `supplementary_fermion`, `bosons` | `fermions` (a_1_p, a_1_m), `bosons` | `bosons` identical; fermion key renamed |
| `oscillator_relations` | `supplementary_fermion_relation`, bosonic, mixed | `standard_fermion_anticommutators`, bosonic, mixed | bosonic/mixed keys identical |
| `central_elements` | κ (parity 0 in B doc), K | κ (parity 1), K (parity 0) | new top-level key; κ parity follows the unified rule |
| `basis` | odd `E_del{k}_{p,m}` (2n) | odd `E_eps1_del{k}_{pp,pm,mp,mm}` (4n) | same even-label grammar; ordering convention κ<odd<even retained |
| `parity`, `generator_realization`, `structure_constants`, `metadata` | as in B | same format | identical format; `a_0` replaced by `a_1_p/a_1_m` |

Everything outside the odd-label grammar and the fermion keys is format-identical, so B(0,n) readers need only
(i) accept the `fermions` key and (ii) read `central_elements`.

---

## Schema 2–4

Defined in the sections added by Issues I05–I07 (below).
