# JSON Schema Specification v5.0 — C(n+1) = osp(2|2n) extension

This document extends the B(0,n) v5.0 specification (`docs/math/B0n_schema_v5.md`) to
$C(n+1)=\mathfrak{osp}(2|2n)$. Notation follows `handover/notation.md`.
It is a complete, standalone specification for the C(n+1) files.

## 0. Files and naming

`n` is always the **bosonic rank** (C(2) ↔ `n=1`). All files live in `data/`.

| Layer | File | Producer | Section |
|---|---|---|---|
| Schema 1 | `C_{n}_structure.json` | `src/C_generators.py` | §1 |
| Schema 2 | `C_{n}_gamma.json` | `src/C_gamma.py` | §2 |
| Schema 3 | `C_{n}_evaluated.json` | `src/C_evaluate.py` | §3 |
| Schema 4 | `C_{n}_coboundary.json` | `src/C_coboundary.py` | §4 |

Generated for `n = 1, 2, 3`. Conventions shared by all layers:
- `schema_version` is `"5.0"`; every file repeats `algebra.family`, `algebra.n`.
- Rational numbers are strings (`"1"`, `"-1/2"`); parameter-linear coefficients are objects
  `{"<param name>": "<rational>"}` (a linear form; absent keys mean 0).
- Global basis index: position in `basis.odd + basis.even` (odd first, PBW order).

## 1. Schema 1: `C_{n}_structure.json`

### Top-level keys

```json
{
  "schema_version": "5.0",
  "algebra": {...},
  "oscillator_generators": {...},
  "oscillator_relations": {...},
  "central_elements": {...},
  "basis": {...},
  "parity": {...},
  "generator_realization": {...},
  "structure_constants": [...],
  "metadata": {...}
}
```

Compared with B(0,n): same keys, plus the top-level key `central_elements`.

### `algebra` (example n = 2)

```json
{
  "family": "C",
  "m": 1,
  "n": 2,
  "cartan_type": "C(3)",
  "alternative_notation": {"osp": "osp(2|4)", "dimension_formula": "osp(2m|2n) with m=1"},
  "dimension_formulas": {"even": "2n^2 + n + 1", "odd": "4n", "total": "2n^2 + 5n + 1"},
  "dimension": {"total": 19, "even": 11, "odd": 8}
}
```
`cartan_type` is `"C({n+1})"`. Dimensions: n=1 → 4|4 (8), n=2 → 11|8 (19), n=3 → 22|12 (34).

### `oscillator_generators`

```json
{
  "fermions": {
    "count": 2, "m": 1,
    "labels": ["a_1_p", "a_1_m"],
    "parity": 1,
    "description": "Standard fermionic pair a_1^± (CAR)"
  },
  "bosons": {
    "count": 4, "n": 2,
    "labels": ["b_1_p", "b_1_m", "b_2_p", "b_2_m"],
    "parity": 0,
    "description": "Bosonic oscillators b_i^± with i=1,...,n (CCR)"
  }
}
```
There is **no** `supplementary_fermion` key.

### `oscillator_relations`

```json
{
  "standard_fermion_anticommutators": {
    "description": "Canonical anticommutation relations for the fermionic pair",
    "relations": {"conjugate_pair": "{a_1^-, a_1^+} = 1", "same_type": "{a_1^±, a_1^±} = 0"}
  },
  "bosonic_commutators": {
    "description": "Canonical commutation relations for bosonic oscillators",
    "relations": {"same_type": "[b_i^±, b_j^±] = 0 for all i, j", "conjugate_pair": "[b_i^-, b_j^+] = δ_{ij}"}
  },
  "mixed_commutators": {
    "boson_fermion": "[b_j^s, a_1^σ] = 0 (undeformed); = -gb_{σ,j,s} κ in the deformation of Schema 2"
  }
}
```

### `central_elements` (top level)

```json
{
  "kappa": {"label": "kappa", "parity": 1, "relation": "kappa^2 = 0",
            "role": "odd central element; carries the inhomogeneous deformation [X,Y]_γ = [X,Y]_0 + κ γ(X,Y)"},
  "K": {"label": "K", "parity": 0, "value": "1",
        "role": "even central element (Bakalov–Sullivan); identified with 1, excluded from basis/PBW"}
}
```
Correction relative to the B(0,n) note: κ is recorded with parity **1** (B0n_schema_v5 lists 0;
the mathematical definition requires p(κ)=1, and the I02 unified rule fixes parity 1).

### `basis`

```json
{
  "even": ["H_1", "...", "E_del{i}_del{j}_mp"],
  "odd": ["E_eps1_del1_pp", "..."],
  "ordering_convention": "PBW: κ < [odd] < [even]  (K = 1 is excluded)",
  "global_index_order": "odd + even"
}
```
Order of each block as in `handover/notation.md` §4.

### `parity`
Map label → 0/1. `H_*`, `E_2del*`, `E_del*_del*` → 0; `E_eps1_del*` → 1.

### `generator_realization`

```json
{
  "description": "Standard form with oscillator normal ordering",
  "ordering": "a_1_p, a_1_m, b_1_p, b_1_m, ..., b_n_p, b_n_m",
  "realizations": {
    "H_1": {"standard_form": [{"words": ["a_1_p","a_1_m"], "coeff": "1"},
                               {"words": ["b_1_p","b_1_m"], "coeff": "1"}],
            "frappat_form": "a_1^+ a_1^- + b_1^+ b_1^-", "parity": 0},
    "H_3": {"standard_form": [{"words": ["b_2_p","b_2_m"], "coeff": "-1"}, {"words": [], "coeff": "-1/2"}],
            "frappat_form": "-b_2^+ b_2^- - 1/2", "parity": 0, "note": "Terminal Cartan"},
    "E_eps1_del1_pm": {"standard_form": [{"words": ["a_1_p","b_1_m"], "coeff": "1"}],
                       "frappat_form": "a_1^+ b_1^-", "parity": 1}
  }
}
```
Every basis element has an entry (no `{k}` placeholders in the generated files).

### `structure_constants`
List of all non-zero coefficients of the undeformed graded bracket, **for every ordered
pair** (X, Y) (both orders stored, so graded antisymmetry is checkable):

```json
{"X": "H_2", "Y": "E_eps1_del1_pp", "Z": "E_eps1_del1_pp", "coeff": "-1", "sign_rule": "graded"}
```
(example from `C_1_structure.json`, where H_2 = -b_1^+b_1^- - 1/2)
meaning $[X,Y\} = \sum_Z \mathrm{coeff}\cdot Z$ with $[X,Y\}=XY-(-1)^{p(X)p(Y)}YX$.
No `K` component occurs (checked by the generator).

### `metadata`

```json
{"generated_by": "src/C_generators.py", "generation_date": "YYYY-MM-DD",
 "references": ["Frappat et al. (2000), Dictionary on Lie Algebras and Superalgebras",
                "Bakalov and Sullivan (2017)"],
 "conventions": "handover/notation.md"}
```

### Compatibility with B(m,n) v5.0

| Key | B(0,n) | C(n+1) | Compatible? |
|---|---|---|---|
| `schema_version` | 5.0 | 5.0 | same |
| `algebra` | family B, m=0 | family C, m=1, + `dimension_formulas` | additive |
| `oscillator_generators` | `supplementary_fermion` + `bosons` | `fermions` + `bosons` | key replaced; `bosons` identical |
| `oscillator_relations` | `supplementary_fermion_relation` | `standard_fermion_anticommutators` | key replaced; others identical |
| `central_elements` | described in notes only | top-level key | new key (B files may add it too) |
| `basis` | κ < odd < even | κ < odd < even | same convention, + `global_index_order` |
| `parity`, `generator_realization`, `structure_constants`, `metadata` | — | same layout | same |

A reader that dispatches on `algebra.family` and reads fermion data from either
`supplementary_fermion` (B) or `fermions` (C) can process both families; all other keys
have identical structure.

## 2. Schema 2: `C_{n}_gamma.json`

Deformation: $[b_j^s, a_1^\sigma] = -\mathrm{gb}_{\sigma,j,s}\,\kappa$. For basis elements,
computed in $U(A)$ and decomposed exactly:
$$[X,Y]_\gamma = [X,Y]_0 + \kappa\big(\gamma(X,Y) + \gamma_K(X,Y)\,K\big),\qquad \kappa \text{ on the left}.$$

```json
{
  "schema_version": "5.0",
  "layer": 2,
  "algebra": {...}, "central_elements": {...}, "basis": {...}, "parity": {...},   // copied from Schema 1
  "inhomogeneous_deformation": {
    "deformed_relation": "[b_j^s, a_1^σ] = -gb_{σ,j,s} κ",
    "bracket_form": "[X,Y]_γ = [X,Y]_0 + κ (γ(X,Y) + γ_K(X,Y) K), κ on the left",
    "gb_matrix": {"shape": [2, 2n], "rows": ["a_1_p","a_1_m"], "columns": ["b_1_p","b_1_m",...],
                  "symbols": [["gb_a1p_b1p","gb_a1p_b1m",...], ["gb_a1m_b1p",...]],
                  "parameter_type": "scalar (even) coefficient; the deformation term κ·gb is odd"},
    "parameters": ["gb_a1p_b1p", ...],                     // 4n names, row-major
    "gamma_parity": "p(γ(X,Y)) = p(X) + p(Y) + 1",
    "pair_coverage": "all ordered pairs (X, Y); only non-zero coefficients listed",
    "gamma_coefficients": [{"X": "...", "Y": "...", "Z": "...", "coeff": {"gb_a1p_b1p": "2"}}],
    "gamma_central":      [{"X": "...", "Y": "...", "coeff": {"gb_a1p_b1p": "-1/2"}}]
  },
  "consistency_checks": {
    "undeformed_part_equals_schema1": true, "gamma_parity_odd": true,
    "central_only_for_mixed_parity": true, "gamma_graded_antisymmetric": true,
    "cocycle_gamma_g_valued_failures": 0, "cocycle_gamma_with_central_failures": 0,
    "linear_in_gb": true
  },
  "metadata": {...}
}
```
`coeff` is a linear form in the gb parameters. `gamma_central` is the κK component; it only
occurs for pairs of opposite parity.

## 3–4. Schemas 3, 4
Specified in the following sections (added by issues I06–I07).
