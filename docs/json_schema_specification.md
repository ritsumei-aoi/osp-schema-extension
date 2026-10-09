# JSON Schema Specification for C(n+1) = osp(2|2n), v5.0

This document defines the JSON schema fields for C(n+1) as an extension of
the B(m,n) v5.0 schema. It is the canonical reference for all four schema layers.

---

## Schema Layer Overview

| Layer | File pattern | Contents |
|---|---|---|
| 1 | `C_{n}_structure.json` | Algebra structure: basis, parity, oscillator realization, structure constants |
| 2 | `C_{n}_gamma.json` | Inhomogeneous deformation (γ-structure / gb matrix) |
| 3 | `C_{n}_evaluated.json` | Numerically evaluated structure for specific gb parameters |
| 4 | `C_{n}_coboundary.json` | Coboundary data for triviality verification |

File naming: `n` = bosonic rank (e.g., C(2)=osp(2|2) → n=1, file `C_1_structure.json`).

---

## Schema 1: Algebra Structure (`C_{n}_structure.json`)

### Top-Level Keys

```json
{
  "schema_version": "5.0",
  "algebra": { ... },
  "central_elements": { ... },
  "oscillator_generators": { ... },
  "oscillator_relations": { ... },
  "basis": { ... },
  "parity": { ... },
  "generator_realization": { ... },
  "structure_constants": [ ... ],
  "metadata": { ... }
}
```

### `schema_version`

```json
"schema_version": "5.0"
```

### `algebra`

```json
{
  "family": "C",
  "m": 1,
  "n": 1,
  "cartan_type": "C(2)",
  "alternative_notation": {
    "osp": "osp(2|2)",
    "dimension_formula": "osp(2m|2n) with m=1"
  },
  "dimension": {
    "even": "2*n^2 + n + 1",
    "odd": "4*n",
    "total": "2*n^2 + 5*n + 1"
  }
}
```

**Dimension table**:

| n | even | odd | total |
|---|---|---|---|
| 1 | 4 | 4 | 8 |
| 2 | 11 | 8 | 19 |
| 3 | 22 | 12 | 34 |

**Compatibility with B(m,n)**: The `family` field changes from `"B"` to `"C"`, `m` changes from 0 to 1. All other structural keys follow the same patterns with modifications noted below.

### `central_elements` (top-level key)

```json
"central_elements": {
  "kappa": {
    "label": "kappa",
    "parity": 1,
    "description": "Odd nilpotent central element; kappa^2 = 0. Appears in deformed bracket [X,Y]_gamma = [X,Y]_0 + kappa * gamma(X,Y)."
  },
  "K": {
    "label": "K",
    "parity": 0,
    "description": "Even central identity element. Identified with scalar 1 in all current applications; excluded from basis and PBW ordering."
  }
}
```

### `oscillator_generators`

```json
{
  "fermions": {
    "m": 1,
    "labels": ["a_1_p", "a_1_m"],
    "parity": 1,
    "description": "Standard fermionic pair a_1^+, a_1^- with CAR relations."
  },
  "bosons": {
    "count": "2*n",
    "n": 1,
    "labels": ["b_1_p", "b_1_m"],
    "description": "Bosonic oscillators b_k^± with k=1,...,n"
  }
}
```

For general n, `bosons.labels` = `["b_1_p","b_1_m",...,"b_n_p","b_n_m"]`.

### `oscillator_relations`

```json
{
  "standard_fermion_anticommutators": {
    "description": "Canonical anticommutation relations for standard fermionic pair",
    "relations": {
      "same_type": "{a_1^+, a_1^+} = 0, {a_1^-, a_1^-} = 0",
      "conjugate_pair": "{a_1^-, a_1^+} = 1"
    }
  },
  "bosonic_commutators": {
    "description": "Canonical commutation relations for bosonic oscillators",
    "relations": {
      "same_type": "[b_i^±, b_j^±] = 0 for all i, j",
      "conjugate_pair": "[b_i^-, b_j^+] = delta_{ij}"
    }
  },
  "mixed_commutators": {
    "fermion_boson": "[b_i^±, a_1^±] = 0 (undeformed)"
  }
}
```

### `basis`

PBW ordering: κ < [odd: E_eps1_del{k}_{pp/pm/mp/mm}] < [even: H_k, E_2del{k}_{p/m}, E_del{i}_del{j}_{pp/mm/pm/mp}]

Example for n=1:
```json
{
  "even": ["H_1", "H_2", "E_2del1_p", "E_2del1_m"],
  "odd": ["E_eps1_del1_pp", "E_eps1_del1_pm", "E_eps1_del1_mp", "E_eps1_del1_mm"],
  "ordering_convention": "PBW: kappa < [odd] < [even]  (K = 1 is excluded)"
}
```

Example for n=2:
```json
{
  "even": ["H_1","H_2","H_3","E_2del1_p","E_2del2_p","E_del1_del2_pp","E_2del1_m","E_2del2_m","E_del1_del2_mm","E_del1_del2_pm","E_del1_del2_mp"],
  "odd": ["E_eps1_del1_pp","E_eps1_del2_pp","E_eps1_del1_pm","E_eps1_del2_pm","E_eps1_del1_mp","E_eps1_del2_mp","E_eps1_del1_mm","E_eps1_del2_mm"],
  "ordering_convention": "PBW: kappa < [odd] < [even]"
}
```

### `parity`

All even generators → 0; all odd generators → 1.

Example for n=1:
```json
{
  "H_1": 0, "H_2": 0, "E_2del1_p": 0, "E_2del1_m": 0,
  "E_eps1_del1_pp": 1, "E_eps1_del1_pm": 1,
  "E_eps1_del1_mp": 1, "E_eps1_del1_mm": 1
}
```

### `generator_realization`

Each generator expressed as a sum of oscillator monomials with rational coefficients.

PBW ordering for oscillators: `a_1_p, a_1_m, b_1_p, b_1_m, ..., b_n_p, b_n_m`

Key realizations:
- `H_1 = a_1^+ a_1^- + b_1^+ b_1^-`
- `H_k = b_{k-1}^+ b_{k-1}^- - b_k^+ b_k^-` (k=2,...,n)
- `H_{n+1} = -b_n^+ b_n^- - 1/2`
- `E_eps1_del{k}_pp = a_1^+ b_k^+`  (word: `["a_1_p", "b_k_p"]`)
- `E_eps1_del{k}_pm = a_1^+ b_k^-`  (word: `["a_1_p", "b_k_m"]`)
- `E_eps1_del{k}_mp = a_1^- b_k^+`  (word: `["a_1_m", "b_k_p"]`)
- `E_eps1_del{k}_mm = a_1^- b_k^-`  (word: `["a_1_m", "b_k_m"]`)
- `E_2del{k}_p = (b_k^+)^2`          (word: `["b_k_p","b_k_p"]`)
- `E_2del{k}_m = (b_k^-)^2`          (word: `["b_k_m","b_k_m"]`)
- `E_del{i}_del{j}_pp = b_i^+ b_j^+`
- `E_del{i}_del{j}_pm = b_i^+ b_j^-`
- `E_del{i}_del{j}_mp = b_i^- b_j^+`
- `E_del{i}_del{j}_mm = b_i^- b_j^-`

JSON realization format:
```json
{
  "E_eps1_del1_pp": {
    "standard_form": [{"words": ["a_1_p","b_1_p"], "coeff": "1"}],
    "frappat_form": "a_1^+ b_1^+",
    "parity": 1
  }
}
```

### `structure_constants`

Non-zero graded brackets [X,Y} stored as:
```json
[{"X": "X_label", "Y": "Y_label", "Z": "Z_label", "coeff": "rational", "sign_rule": "graded"}]
```

The sign rule: [X,Y} = -(-1)^{p(X)p(Y)} [Y,X}.

### `metadata`

```json
{
  "generated_by": "build_C_structure_constants.py",
  "generation_date": "YYYY-MM-DD",
  "references": [
    "Frappat, Sciarrino, Sorba (2000), Dictionary on Lie Algebras and Superalgebras",
    "Bakalov and Sullivan (2017)"
  ]
}
```

---

## Schema 2: Gamma Structure (`C_{n}_gamma.json`)

### Top-Level Keys

```json
{
  "schema_version": "5.0",
  "algebra": { ... },
  "gb_matrix": { ... },
  "gamma_coefficients": [ ... ],
  "metadata": { ... }
}
```

### `gb_matrix`

For C(n+1), the gb matrix has 4n entries: gb_{σ,j,s} for σ∈{+,-}, j=1,...,n, s∈{+,-}.

Deformation relation: [b_j^s, a_1^σ] = -gb_{σ,j,s} · κ

```json
{
  "size": "4*n",
  "parameters": {
    "gb_p_1_p": {"sigma": "+", "j": 1, "s": "+", "parity": 1},
    "gb_p_1_m": {"sigma": "+", "j": 1, "s": "-", "parity": 1},
    "gb_m_1_p": {"sigma": "-", "j": 1, "s": "+", "parity": 1},
    "gb_m_1_m": {"sigma": "-", "j": 1, "s": "-", "parity": 1}
  },
  "description": "gb_{sigma,j,s}: parity-1 deformation parameters. Indexed by fermionic oscillator (sigma in {+,-}), bosonic index j, bosonic sign s."
}
```

### `gamma_coefficients`

Symbolic entries γ_{abc} (coefficients in [X,Y]_γ = [X,Y]_0 + κ·γ(X,Y)):

```json
[{"X": "...", "Y": "...", "Z": "...", "coeff_expr": "gb_p_j_p + gb_m_j_m", "coeff_numeric": null}]
```

---

## Schema 3: Evaluated Structure (`C_{n}_evaluated.json`)

Same as Schema 2 but with concrete numeric values substituted for all gb parameters.
Add a top-level `"gb_assignment"` key recording the substitution used.

```json
{
  "gb_assignment": {
    "gb_p_1_p": 1, "gb_p_1_m": 1, "gb_m_1_p": 1, "gb_m_1_m": 1
  },
  "gamma_coefficients": [{"X": "...", "Y": "...", "Z": "...", "coeff_numeric": 2}]
}
```

---

## Schema 4: Coboundary Structure (`C_{n}_coboundary.json`)

Stores the coboundary (δf)_{abc} for a chosen odd linear map f: g → g.

```json
{
  "schema_version": "5.0",
  "algebra": { ... },
  "odd_map_f": {
    "description": "Odd linear map f: g -> g parameterized by phi_{ij}",
    "phi_coefficients": {"H_1->E_eps1_del1_pp": "phi_val", ...}
  },
  "coboundary_coefficients": [
    {"X": "...", "Y": "...", "Z": "...", "coeff": "expr_in_phi"}
  ],
  "metadata": { ... }
}
```

The coboundary formula: (δf)(X,Y) = (-1)^{p(X)}[X,f(Y)] - (-1)^{(p(X)+1)p(Y)}[Y,f(X)] - f([X,Y])

---

## Compatibility with B(m,n) Schema

| Field | B(0,n) value | C(n+1) value |
|---|---|---|
| algebra.family | "B" | "C" |
| algebra.m | 0 | 1 |
| oscillator_generators.supplementary_fermion | present | absent |
| oscillator_generators.fermions | absent | present (m=1, labels a_1_p/m) |
| oscillator_relations | supplementary_fermion_relation | standard_fermion_anticommutators |
| central_elements | present (kappa p=1, K p=0) | same |
| basis.odd | E_del{k}_p/m | E_eps1_del{k}_{pp/pm/mp/mm} |
| dim(odd) | 2n | 4n |
| dim(even) | 2n²+n | 2n²+n+1 |
