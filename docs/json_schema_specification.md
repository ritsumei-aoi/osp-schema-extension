# JSON Schema Specification for C(n+1) (Schema 1, v5.0 extension)

This document defines the Schema 1 (algebra structure) fields for $C(n+1)=\mathfrak{osp}(2|2n)$.
It extends the B(m,n) v5.0 schema described in `docs/math/B0n_schema_v5.md`.
Basis and PBW conventions are fixed in `handover/notation.md` (Issue I01).

## 1. File Naming

- File: `C_{n}_structure.json`, where `n` is the bosonic rank.
- Examples: `C_1_structure.json` (C(2)), `C_2_structure.json` (C(3)), `C_3_structure.json` (C(4)).

## 2. Top-Level Keys

```json
{
  "schema_version": "5.0",
  "algebra": { ... },
  "oscillator_generators": { ... },
  "oscillator_relations": { ... },
  "central_elements": { ... },
  "basis": { ... },
  "parity": { ... },
  "generator_realization": { ... },
  "structure_constants": [ ... ],
  "metadata": { ... }
}
```

`central_elements` is a **top-level key** (not nested under `oscillator_relations`).

## 3. Field Definitions

### 3.1 `algebra`

```json
"algebra": {
  "family": "C",
  "m": 1,
  "n": 2,
  "cartan_type": "C(3)",
  "alternative_notation": {
    "osp": "osp(2|4)",
    "dimension_formula": "osp(2m|2n) with m=1"
  },
  "dimension": { "total": 19, "even": 11, "odd": 8 }
}
```

Dimension formulas: even = $2n^2+n+1$, odd = $4n$, total = $2n^2+5n+1$.

| $n$ | Algebra | even | odd | total |
|---|---|---|---|---|
| 1 | C(2) = osp(2\|2) | 4 | 4 | 8 |
| 2 | C(3) = osp(2\|4) | 11 | 8 | 19 |
| 3 | C(4) = osp(2\|6) | 22 | 12 | 34 |

### 3.2 `oscillator_generators`

Two keys, `fermions` and `bosons`. No supplementary fermion.

```json
"oscillator_generators": {
  "fermions": {
    "m": 1,
    "labels": ["a_1_p", "a_1_m"],
    "parity": 1,
    "description": "Standard fermion pair a_1^+, a_1^-"
  },
  "bosons": {
    "n": 2,
    "count": 4,
    "labels": ["b_1_p", "b_1_m", "b_2_p", "b_2_m"],
    "parity": 0,
    "description": "Bosonic oscillators b_k^+, b_k^- with k=1,...,n"
  }
}
```

### 3.3 `oscillator_relations`

```json
"oscillator_relations": {
  "fermionic_anticommutator": {
    "relation": "{a_1_m, a_1_p} = 1",
    "others": "{a_1_p, a_1_p} = {a_1_m, a_1_m} = 0"
  },
  "bosonic_commutators": {
    "same_type": "[b_i^s, b_j^s] = 0",
    "conjugate_pair": "[b_i^m, b_j^p] = delta_{ij}"
  },
  "mixed_commutators": {
    "boson_fermion": "[b_i^s, a_1^sigma] = 0 (undeformed; deformation lives in gb, see Schema 2)"
  }
}
```

### 3.4 `central_elements` (top-level)

```json
"central_elements": {
  "kappa": { "parity": 1, "relation": "kappa^2 = 0", "role": "odd nilpotent central extension" },
  "K": { "parity": 0, "value": 1, "role": "even central element; identified with the scalar 1, excluded from basis" }
}
```

### 3.5 `basis`

```json
"basis": {
  "even": ["H_1", "H_2", "H_3", "E_2del1_p", "E_2del1_m", "E_2del2_p", "E_2del2_m", "E_del1_del2_pp", "E_del1_del2_mm", "E_del1_del2_pm", "E_del1_del2_mp"],
  "odd": ["E_eps1_del1_pp", "E_eps1_del1_pm", "E_eps1_del1_mp", "E_eps1_del1_mm", "E_eps1_del2_pp", "E_eps1_del2_pm", "E_eps1_del2_mp", "E_eps1_del2_mm"],
  "ordering_convention": "PBW: kappa < [odd] < [even]; K excluded"
}
```

### 3.6 `parity`

Map from every basis label to 0 (even) or 1 (odd). Odd labels are exactly the `E_eps1_*` entries.

### 3.7 `generator_realization`

Each generator is a list of oscillator words with coefficients, in the ordering `a_1_p, a_1_m, b_1_p, b_1_m, ...` (the standard-form ordering). Realizations follow `handover/notation.md` §5. Example:

```json
"E_eps1_del1_pm": { "standard_form": [ { "words": ["a_1_p", "b_1_m"], "coeff": "1" } ], "parity": 1 }
```

### 3.8 `structure_constants`

List of non-zero graded brackets `{ "X", "Y", "Z", "coeff", "sign_rule" }`, as in B(0,n).

### 3.9 `metadata`

`generated_by`, `generation_date`, `references`.

## 4. Compatibility with B(m,n) (v5.0)

| Key | B(0,n) | C(n+1) | Change |
|---|---|---|---|
| `schema_version` | "5.0" | "5.0" | none |
| `algebra.family` | "B" | "C" | value |
| `algebra.m` | 0 | 1 | value |
| `oscillator_generators` | `supplementary_fermion` + `bosons` | `fermions` + `bosons` | key renamed |
| `oscillator_relations` | `a_0^2 = 1/2` | `{a_1_m,a_1_p}=1` | replaced |
| `central_elements` | in `oscillator_relations` note only | top-level key | moved |
| `basis.odd` | `E_del{k}_p/m` (2n) | `E_eps1_del{k}_*` (4n) | expanded |
| `basis.even` | `H_k`, `E_2del`, `E_del_del` | adds `H_{n+1}` | one Cartan added |
| `parity` | odd = `E_del*` | odd = `E_eps1_*` | value |
| `generator_realization` | uses `a_0` | uses `a_1_p`, `a_1_m` | replaced |
| `structure_constants` | B(0,n) brackets | recomputed | regenerated |

The top-level keys and their nesting are preserved, so a consumer written for v5.0 needs only the field-level changes above.

## 5. Status

Draft for I02. The generator (I03) populates these fields for n=1,2,3.
