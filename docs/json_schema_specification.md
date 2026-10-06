# C(n+1) = osp(2|2n) JSON Schema Specification (v5.0-C)

Complete, standalone specification of the C(n+1) extension of the B(0,n) v5.0 schema
(`docs/math/B0n_schema_v5.md`). Notation: `handover/notation.md`.
Sections 1-2 (Schema 1) were written in I02; Schemas 2-4 were appended in I05-I07.

## 0. Overview

| Layer | File | Contents |
|---|---|---|
| Schema 1 | `data/C_{n}_structure.json` | Basis, parity, oscillator realization, structure constants of g = osp(2\|2n) |
| Schema 2 | `data/C_{n}_gamma.json` | gb matrix and symbolic gamma structure (inhomogeneous deformation) |
| Schema 3 | `data/C_{n}_evaluated*.json` | gamma with numeric gb |
| Schema 4 | `data/C_{n}_coboundary*.json` | odd map f and coboundary δf |

`n` is the bosonic rank: C(2)=osp(2|2) -> `C_1_*`, C(3)=osp(2|4) -> `C_2_*`, C(4)=osp(2|6) -> `C_3_*`.

## 1. Schema 1: Algebra Structure

### Top-level keys

```json
{
  "schema_version": "5.0",
  "algebra": {},
  "oscillator_generators": {},
  "oscillator_relations": {},
  "central_elements": {},
  "basis": {},
  "parity": {},
  "generator_realization": {},
  "structure_constants": [],
  "metadata": {}
}
```

`central_elements` is a **top-level key** (new relative to B(0,n)). All other keys exist in B(0,n) v5.0.

### `schema_version`
`"5.0"` (unchanged: the structure is a backward-compatible extension, see section 1.9).

### `algebra`
```json
{
  "family": "C",
  "m": 1,
  "n": 2,
  "cartan_type": "C(3)",
  "alternative_notation": {
    "osp": "osp(2|4)",
    "dimension_formula": "osp(2m|2n) with m=1"
  },
  "dimension_formula": {"even": "2n^2+n+1", "odd": "4n", "total": "2n^2+5n+1"},
  "dimension": {"total": 19, "even": 11, "odd": 8}
}
```

| n | algebra | even | odd | total |
|---|---|---|---|---|
| 1 | C(2)=osp(2\|2) | 4 | 4 | 8 |
| 2 | C(3)=osp(2\|4) | 11 | 8 | 19 |
| 3 | C(4)=osp(2\|6) | 22 | 12 | 34 |

`"m": 1` is the number of fermionic pairs. `cartan_type` is `"C(n+1)"`.

### `oscillator_generators`
Exactly two keys. There is **no** `supplementary_fermion`.
```json
{
  "fermions": {
    "m": 1,
    "count": 2,
    "labels": ["a_1_p", "a_1_m"],
    "parity": 1,
    "description": "Standard fermionic pair a_1^+, a_1^- (CAR)"
  },
  "bosons": {
    "count": 4,
    "n": 2,
    "labels": ["b_1_p", "b_1_m", "b_2_p", "b_2_m"],
    "parity": 0,
    "description": "Bosonic oscillators b_k^±, k=1..n"
  }
}
```
(`bosons.count = 2n`, `bosons.n = n` is the rank.)

### `oscillator_relations`
```json
{
  "standard_fermion_anticommutators": {
    "description": "CAR for the standard fermionic pair",
    "relations": {
      "conjugate_pair": "{a_1^-, a_1^+} = 1",
      "nilpotent": "(a_1^+)^2 = (a_1^-)^2 = 0"
    }
  },
  "bosonic_commutators": {
    "description": "Canonical commutation relations for bosonic oscillators",
    "relations": {
      "same_type": "[b_i^±, b_j^±] = 0 for all i, j",
      "conjugate_pair": "[b_i^-, b_j^+] = δ_{ij}"
    }
  },
  "mixed_commutators": {
    "boson_fermion": "[b_i^s, a_1^σ] = 0 (undeformed; deformed: = -gb_{σ,i,s} κ, see Schema 2)"
  }
}
```

### `central_elements` (top-level)
```json
{
  "kappa": {"parity": 1, "relation": "kappa^2 = 0", "central": true,
            "description": "Odd nilpotent central element; carries the deformation"},
  "K":     {"parity": 0, "relation": "K = 1", "central": true,
            "description": "Even central identity (Bakalov-Sullivan); the scalar 1, not a basis element"}
}
```

### `basis`
PBW ordering (see `handover/notation.md` §3): `κ < [odd] < [even]`.
```json
{
  "even": ["H_1", "...", "E_2del{k}_p", "E_del{i}_del{j}_pp", "E_2del{k}_m", "E_del{i}_del{j}_mm", "E_del{i}_del{j}_pm", "E_del{i}_del{j}_mp"],
  "odd":  ["E_eps1_del{k}_pp", "E_eps1_del{k}_pm", "E_eps1_del{k}_mp", "E_eps1_del{k}_mm"],
  "ordering_convention": "PBW: κ < [odd] < [even]  (K = 1 is excluded)"
}
```
Lists are expanded over `k` (`1..n`) and `i<j` in the order of `handover/notation.md`; Cartans are `H_1..H_{n+1}`.
Sizes: `len(even) = 2n²+n+1`, `len(odd) = 4n`.

### `parity`
Dictionary label -> 0/1. `H_*`, `E_2del*`, `E_del*_del*_*` have parity 0; `E_eps1_del*_*` have parity 1.

### `generator_realization`
```json
{
  "description": "Standard form with PBW ordering",
  "ordering": "a_1_p, a_1_m, b_1_p, b_1_m, ..., b_n_p, b_n_m",
  "realizations": {
    "H_1": {"standard_form": [{"words": ["a_1_p","a_1_m"], "coeff": "1"},
                              {"words": ["b_1_p","b_1_m"], "coeff": "1"}],
            "frappat_form": "a_1^+ a_1^- + b_1^+ b_1^-", "parity": 0},
    "E_eps1_del1_pm": {"standard_form": [{"words": ["a_1_p","b_1_m"], "coeff": "1"}],
                       "frappat_form": "a_1^+ b_1^-", "parity": 1}
  }
}
```
Every label of `basis` has an entry; `words` is the oscillator word (empty list = scalar); `coeff` is a rational string.
`H_{n+1}` has the constant term `{"words": [], "coeff": "-1/2"}`.

### `structure_constants`
Non-zero graded brackets `[X, Y} = Σ_Z coeff · Z`. **All ordered pairs** (X,Y) with non-zero bracket are listed
(so both `(X,Y)` and `(Y,X)` appear, which makes antisymmetry checkable).
```json
{"X": "H_1", "Y": "E_eps1_del1_pp", "Z": "E_eps1_del1_pp", "coeff": "1", "sign_rule": "graded"}
```
Graded rule: `[X,Y} = XY - (-1)^{p(X)p(Y)} YX`, `[X,Y} = -(-1)^{p(X)p(Y)}[Y,X}`.
Entries are sorted by (index of X, index of Y, index of Z) in the order `even + odd` of the basis list.

### `metadata`
```json
{"generated_by": "src/C_generators.py", "generation_date": "2026-10-06",
 "references": ["Frappat et al. (2000), Dictionary on Lie Algebras and Superalgebras",
                "Bakalov and Sullivan (2017)"]}
```

### 1.9 Compatibility with B(m,n) / B(0,n) v5.0

| Key | B(0,n) v5.0 | C(n+1) |
|---|---|---|
| `schema_version` | `"5.0"` | `"5.0"` (same) |
| `algebra.family`, `m` | `"B"`, `0` | `"C"`, `1` |
| `algebra.dimension` | even `2n²+n`, odd `2n` | even `2n²+n+1`, odd `4n` (added `dimension_formula`) |
| `oscillator_generators` | `supplementary_fermion`, `bosons` | `fermions` (a_1_p, a_1_m), `bosons` (unchanged shape) |
| `oscillator_relations` | `supplementary_fermion_relation`, `bosonic_commutators`, `mixed_commutators` | `standard_fermion_anticommutators`, `bosonic_commutators` (unchanged), `mixed_commutators` (unchanged) |
| `central_elements` | in B spec only mentioned in prose | explicit top-level key (kappa parity 1, K parity 0) |
| `basis.odd` | `E_del{k}_p/m` (2n) | `E_eps1_del{k}_{pp,pm,mp,mm}` (4n) |
| `basis.even` | `H_1..H_n`, root vectors | `H_1..H_{n+1}` (extra so(2) Cartan) + same sp(2n) root labels |
| `generator_realization` | words in `a_0, b` | words in `a_1_p, a_1_m, b` |
| `structure_constants`, `parity`, `metadata` | unchanged shape | unchanged shape |

A B(0,n) reader that ignores `fermions` / `central_elements` and treats unknown keys as optional can read the
even sp(2n) part unchanged. The family-specific keys are `oscillator_generators.{supplementary_fermion|fermions}`
and `oscillator_relations.{supplementary_fermion_relation|standard_fermion_anticommutators}`; readers should
dispatch on `algebra.family`.

### 1.10 File naming
`C_{n}_structure.json` with `n` = bosonic rank: `C_1_structure.json` (C(2)), `C_2_structure.json` (C(3)), `C_3_structure.json` (C(4)).

## 2. Schema 2: gamma structure (`C_{n}_gamma.json`, added in I05)

Models the inhomogeneous deformation of `docs/math/C_inhomogeneous_definition.md`:
`[b_j^s, a_1^σ] = -gb_{σ,j,s} κ`, `[X,Y]_γ = [X,Y]_0 + κ γ(X,Y)`.

```json
{
  "schema_version": "5.0",
  "layer": 2,
  "algebra": {"family": "C", "m": 1, "n": 1, "cartan_type": "C(2)", "dimension": {"even": 4, "odd": 4, "total": 8}},
  "structure_file": "C_1_structure.json",
  "gb_matrix": {
    "shape": [2, 2],
    "rows": ["a_1_p", "a_1_m"],
    "cols": ["b_1_p", "b_1_m"],
    "entries": [["gb_a_1_p_b_1_p", "gb_a_1_p_b_1_m"], ["gb_a_1_m_b_1_p", "gb_a_1_m_b_1_m"]],
    "parameters": [{"name": "gb_a_1_p_b_1_p", "row": "a_1_p", "col": "b_1_p", "parity": 1, "relation": "..."}]
  },
  "inhomogeneous_deformation": {
    "definition": "...", "parameter_count": 4, "parameter_parity": 1, "basis_order": ["..."],
    "gamma": [{"X": "H_1", "Y": "E_eps1_del1_pp", "Z": "H_1", "coeff": {"gb_a_1_p_b_1_p": "-1"}}],
    "central_component": {"entries": [{"X": "H_1", "Y": "E_eps1_del1_pp", "coeff": {"gb_a_1_p_b_1_p": "-1"}}]}
  },
  "consistency": {},
  "metadata": {}
}
```

- `gb_matrix` is `2 x 2n` (rows `a_1_p`, `a_1_m`; columns `b_1_p, b_1_m, ..., b_n_p, b_n_m`); entry `[σ][(j,s)]` is `gb_a_1_{σ}_b_{j}_{s}`; `4n` parameters.
- `gamma[*].coeff` maps each gb symbol to a rational string; γ_{XYZ} is linear in gb. Only non-zero entries are listed. γ is **odd**: `p(Z) = p(X)+p(Y)+1`.
- `central_component`: coefficient of `κ·K` (= κ) in `[X,Y]_γ`. This part lies outside g because `K=1` is not a basis element; it occurs only for pairs with `[X,Y]` odd. It is kept separate so that `gamma` stays a g-valued 2-cochain.
- The gb values are ordinary scalars (the "parity 1" of the docs labels the odd oscillator pair; see the I05 response).
- Consistency conditions (checked by `src/C_gamma.py`): same basis/algebra as Schema 1; gb = 0 recovers Schema 1; the κ-linear super Jacobi identity holds, using `[X, κZ] = (-1)^{p(X)} κ[X,Z]`, `[κZ, X] = κ[Z,X]`:
  `(-1)^{p(X)}[X,γ(Y,Z)] + γ(X,[Y,Z]) = [γ(X,Y),Z] + γ([X,Y],Z) + (-1)^{p(X)p(Y)}((-1)^{p(Y)}[Y,γ(X,Z)] + γ(Y,[X,Z]))`.

## 3. Schema 3: evaluated structure (`C_{n}_evaluated[_<profile>].json`, added in I06)

Schema 2 with every gb replaced by a number. `C_{n}_evaluated.json` is the profile `plus` (all gb = +1).

```json
{
  "schema_version": "5.0", "layer": 3,
  "algebra": {}, "structure_file": "C_1_structure.json", "gamma_file": "C_1_gamma.json",
  "profile": {"name": "plus", "gb_values": {"gb_a_1_p_b_1_p": "1", "...": "1"}},
  "evaluated_deformation": {
    "description": "...",
    "gamma": [{"X": "H_1", "Y": "E_eps1_del1_pp", "Z": "H_1", "coeff": "-1"}],
    "central_component": [{"X": "H_1", "Y": "E_eps1_del1_pp", "coeff": "-1"}],
    "counts": {"gamma_entries": 0, "central_entries": 0}
  },
  "metadata": {}
}
```
Only non-zero entries are stored. Profiles: `plus` (all +1), `minus` (all -1), `alt` (+1,-1,+1,... in the order of `gb_names`: `(j,s,σ)` with σ fastest), `zero` (undeformed; empty γ), `single` (only the first gb = 1).
