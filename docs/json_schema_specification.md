# JSON Schema v5.0 for C(n+1) = osp(2|2n)

This document specifies the JSON Schema v5.0 for C(n+1) = osp(2|2n), extending the B(0,n) base schema.

**Reference implementations**: 
- Base case: B(0,n) in `docs/math/B0n_schema_v5.md`
- C(n+1) mathematical definitions: `docs/math/Cn1_definition.md`, `docs/math/C_inhomogeneous_definition.md`
- Notation conventions: `handover/notation.md`

---

## Overview: Schema Architecture for C(n+1)

C(n+1) follows the same 4-layer architecture as B(m,n):

| Layer | File pattern | Contents |
|---|---|---|
| Schema 1 | `C_n_structure.json` | Algebra structure: basis, parity, oscillator realization, structure constants |
| Schema 2 | `C_n_gamma.json` | Inhomogeneous deformation (γ-structure with gb parameters) |
| Schema 3 | `C_n_evaluated_<gb>.json` | Numerically evaluated structure constants for specific γ parameters |
| Schema 4 | `C_n_coboundary_<gb>.json` | Coboundary data for triviality verification |

**File naming convention**: For $C(n+1) = \text{osp}(2|2n)$, use `C_n_structure.json` where $n$ is the **bosonic rank** (not the superalgebra index).
- C(2) = osp(2|2): $n=1$ → `C_1_structure.json`
- C(3) = osp(2|4): $n=2$ → `C_2_structure.json`
- C(4) = osp(2|6): $n=3$ → `C_3_structure.json`

---

## Schema 1: Algebra Structure Specification

### Top-Level JSON Structure

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
  "structure_constants": { ... },
  "metadata": { ... }
}
```

### `schema_version`

```json
"schema_version": "5.0"
```

### `algebra`

**Complete definition for C(n+1)**:

```json
{
  "family": "C",
  "m": 1,
  "n": n_value,
  "cartan_type": "C(n+1)",
  "alternative_notation": {
    "osp": "osp(2|2n)",
    "dimension_formula": "osp(2m|2n) with m=1"
  },
  "dimension": {
    "total": 2*n_value^2 + 5*n_value + 1,
    "even": 2*n_value^2 + n_value + 1,
    "odd": 4*n_value
  }
}
```

**Dimension values for standard cases**:

| n | Algebra | even | odd | total |
|---|---------|------|-----|-------|
| 1 | C(2) | 4 | 4 | 8 |
| 2 | C(3) | 11 | 8 | 19 |
| 3 | C(4) | 22 | 12 | 34 |

**Key differences from B(0,n)**:
- `"family": "C"` (not "B")
- `"m": 1` (fixed; identifies fermionic pair count)
- `"n"` value is always the bosonic rank
- Dimension formulas differ

### `oscillator_generators`

**Complete definition for C(n+1)**:

```json
{
  "fermions": {
    "m": 1,
    "count": 2,
    "labels": ["a_1_p", "a_1_m"],
    "description": "Standard fermionic pair (a_1^+, a_1^-) with CAR: {a_1^-, a_1^+} = 1"
  },
  "bosons": {
    "count": 2*n_value,
    "n": n_value,
    "labels": ["b_1_p", "b_1_m", "b_2_p", "b_2_m", ..., "b_n_p", "b_n_m"],
    "description": "Bosonic oscillators b_k^± with k=1,...,n; CCR [b_k^-, b_l^+] = δ_{kl}"
  }
}
```

**Example for C(3) (n=2)**:
```json
{
  "fermions": {
    "m": 1,
    "count": 2,
    "labels": ["a_1_p", "a_1_m"],
    "description": "Standard fermionic pair"
  },
  "bosons": {
    "count": 4,
    "n": 2,
    "labels": ["b_1_p", "b_1_m", "b_2_p", "b_2_m"],
    "description": "Bosonic oscillators b_k^± with k=1,2"
  }
}
```

**Key differences from B(0,n)**:
- Replace `"supplementary_fermion"` with `"fermions"` (key name change)
- Include `"m": 1` to indicate fermionic pair count
- CAR relation instead of $a_0^2 = 1/2$

### `oscillator_relations`

**Complete definition for C(n+1)**:

```json
{
  "standard_fermion_anticommutators": {
    "description": "Canonical anticommutation relations for standard fermionic pair",
    "relations": {
      "hermitian_conjugate": "{a_1^-, a_1^+} = 1",
      "self_anticommutator_minus": "{a_1^-, a_1^-} = 0",
      "self_anticommutator_plus": "{a_1^+, a_1^+} = 0"
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
    "boson_fermion": "[b_k^±, a_1^±] = 0 for all k (deformation by gb parameters in Schema 2)"
  }
}
```

**Key differences from B(0,n)**:
- Replace `"supplementary_fermion_relation"` with `"standard_fermion_anticommutators"`
- Explicitly list all three CAR relations (hermitian conjugate, self-anticommutators)
- Note that boson-fermion commutators are deformed in Schema 2

### `central_elements`

**New top-level key for C(n+1)** (also applies to B(m,n) but documented here):

```json
{
  "kappa": {
    "label": "κ",
    "parity": 1,
    "nilpotency": 2,
    "relation": "κ^2 = 0",
    "description": "Odd central element; parametrizes inhomogeneous deformations"
  },
  "K": {
    "label": "K",
    "parity": 0,
    "definition": "scalar 1",
    "description": "Even central identity element; identified with scalar 1 in all applications (Bakalov-Sullivan)"
  }
}
```

**Notes**:
- `κ` is odd ($p(\kappa) = 1$) and nilpotent ($\kappa^2 = 0$)
- $K$ is even ($p(K) = 0$) and identified with scalar 1; does not appear in basis lists
- Both are recorded for schema completeness and formal completeness

### `basis`

**Even basis** (ordered by PBW convention, total $2n^2+n+1$ elements):
- Cartan generators: $H_1, \ldots, H_{n+1}$
- Doubled boson roots: $E_{2\delta_k}^p, E_{2\delta_k}^m$ for $k=1,\ldots,n$
- Off-diagonal boson roots: $E_{\delta_i\delta_j}^{ss}$ for $i<j$, all sign patterns $ss \in \{pp,pm,mp,mm\}$

**Odd basis** (ordered by PBW convention, total $4n$ elements):
- Fermionic-bosonic roots: $E_{\varepsilon 1 \delta_k}^{ss}$ for $k=1,\ldots,n$, all sign patterns $ss \in \{pp,pm,mp,mm\}$

**Example for C(2) (n=1)**:
```json
{
  "even": [
    "H_1", "H_2",
    "E_2del1_p", "E_2del1_m"
  ],
  "odd": [
    "E_eps1_del1_pp", "E_eps1_del1_pm",
    "E_eps1_del1_mp", "E_eps1_del1_mm"
  ],
  "ordering_convention": "PBW: κ < [odd] < [even] (K = 1 excluded; see note in central_elements)"
}
```

**Example for C(3) (n=2)**:
```json
{
  "even": [
    "H_1", "H_2", "H_3",
    "E_2del1_p", "E_2del1_m", "E_2del2_p", "E_2del2_m",
    "E_del1_del2_pp", "E_del1_del2_pm", "E_del1_del2_mp", "E_del1_del2_mm"
  ],
  "odd": [
    "E_eps1_del1_pp", "E_eps1_del1_pm", "E_eps1_del1_mp", "E_eps1_del1_mm",
    "E_eps1_del2_pp", "E_eps1_del2_pm", "E_eps1_del2_mp", "E_eps1_del2_mm"
  ],
  "ordering_convention": "PBW: κ < [odd] < [even]"
}
```

### `parity`

Mapping from each basis element to its parity (0 = even, 1 = odd).

**Example for C(2) (n=1)**:
```json
{
  "H_1": 0, "H_2": 0,
  "E_2del1_p": 0, "E_2del1_m": 0,
  "E_eps1_del1_pp": 1, "E_eps1_del1_pm": 1,
  "E_eps1_del1_mp": 1, "E_eps1_del1_mm": 1
}
```

### `generator_realization`

Each generator expressed as a sum of oscillator words with rational coefficients.

**Oscillator ordering** for C(n):
```
a_1_p, a_1_m, b_1_p, b_1_m, b_2_p, b_2_m, ..., b_n_p, b_n_m
```

**Example Cartan generator H_1 for C(n)**:
```json
{
  "H_1": {
    "standard_form": [
      {"words": ["a_1_p", "a_1_m"], "coeff": "1"},
      {"words": ["b_1_p", "b_1_m"], "coeff": "1"}
    ],
    "frappat_form": "a_1^+ a_1^- + b_1^+ b_1^-",
    "parity": 0
  }
}
```

**Example odd generators for C(n)**:
```json
{
  "E_eps1_del1_pp": {
    "standard_form": [
      {"words": ["a_1_p", "b_1_p"], "coeff": "1"}
    ],
    "frappat_form": "a_1^+ b_1^+",
    "parity": 1
  },
  "E_eps1_del1_pm": {
    "standard_form": [
      {"words": ["a_1_p", "b_1_m"], "coeff": "1"}
    ],
    "frappat_form": "a_1^+ b_1^-",
    "parity": 1
  }
}
```

### `structure_constants`

Graded Lie brackets computed under the CAR and CCR relations of C(n+1).

Each bracket stored as:
```json
{
  "X": "generator_label_1",
  "Y": "generator_label_2",
  "Z": "generator_label_3",
  "coeff": "rational_or_expression",
  "sign_rule": "graded"
}
```

Where $[X, Y\}_{\text{graded}} = \text{coeff} \cdot Z$.

**Example bracket for C(n)**:
```json
{
  "X": "H_1",
  "Y": "E_eps1_del1_pp",
  "Z": "E_eps1_del1_pp",
  "coeff": "2",
  "sign_rule": "graded"
}
```

### `metadata`

```json
{
  "generated_by": "build_C_structure_constants.py",
  "generation_date": "YYYY-MM-DD",
  "schema_version": "5.0",
  "algebra_family": "C",
  "extension_from": "B(0,n)",
  "references": [
    "Frappat et al. (2000), Dictionary on Lie Algebras and Superalgebras",
    "Bakalov and Sullivan (2017), arXiv:1612.09400",
    "Aoi (2026), thm01-R-haiku45"
  ]
}
```

---

## Backward Compatibility & Schema Relationship

### C(n+1) to B(0,n) Mapping

| C(n+1) field | B(0,n) field | Note |
|---|---|---|
| `algebra.family` | "C" | "B" for B(0,n) |
| `algebra.m` | 1 | 0 for B(0,n) |
| `oscillator_generators.fermions` | `oscillator_generators.supplementary_fermion` | Different fermion type |
| `oscillator_relations.standard_fermion_anticommutators` | `oscillator_relations.supplementary_fermion_relation` | CAR vs. $a_0^2$ relation |
| `central_elements` | not present | new top-level key in C(n+1) |
| `basis.odd` | odd generators | 2n vs. 4n elements |
| All other keys | structurally identical | dimension formulas differ |

### File Naming

Consistent across families:
- B(0,n): `B_n_structure.json`
- C(n+1): `C_n_structure.json`
- M(m,n): `M_m_n_structure.json` (if extended later)

Where the first parameter indicates the fermionic index (0 for B, 1 for C, etc.) and n/m indicate bosonic rank(s).

---

## Implementation Notes

1. **Central element K**: The element $K$ is identified with scalar 1 in oscillator algebra applications (Bakalov-Sullivan convention). It does not appear in PBW basis lists but is recorded in `central_elements` for formal completeness and schema consistency.

2. **Deformation parameters (Schema 2+)**: The gb parameters (4n for C(n+1)) parametrize the exchange relations between fermionic and bosonic oscillators. They are introduced in Schema 2 (`C_n_gamma.json`) and do not appear in Schema 1.

3. **Numerical evaluation (Schema 3)**: Structure constants in Schema 1 are symbolic (using rational coefficients). Schema 3 evaluates them for specific numerical gb-parameter values.

4. **Triviality (Schema 4)**: Coboundary analysis determines whether a deformation is trivial (equivalent to the standard bracket via a linear map).

---

## Summary Table: Key Changes from B(0,n)

| Aspect | B(0,n) | C(n+1) |
|--------|--------|--------|
| Fermionic oscillators | $a_0$ (supplementary) | $a_1^\pm$ (standard pair, CAR) |
| Odd generators | $2n$ | $4n$ |
| Odd roots | $\pm\delta_k$ | $\pm\varepsilon \pm \delta_k$ |
| Even dimension | $2n^2 + n$ | $2n^2 + n + 1$ |
| Central elements | implicit | explicit (κ, K) |
| Dimension formula | osp(1\|2n) | osp(2\|2n) |
