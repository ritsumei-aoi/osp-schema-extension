# C(n+1) JSON Schema Specification v5.0

This document specifies the v5.0 JSON schema for C(n+1) = osp(2|2n), extending the base B(0,n) specification.

**Reference documents**:
- `docs/math/B0n_schema_v5.md` - Base specification for B(0,n)
- `docs/math/Cn1_definition.md` - Mathematical definition of C(n+1)
- `handover/notation.md` - Notation and generator label conventions

---

## Overview: Schema Architecture for C(n+1)

The JSON schema for C(n+1) follows the same 4-layer architecture as B(0,n):

| Layer | File pattern | Contents |
|---|---|---|
| Schema 1 | `C_n_structure.json` | Algebra structure: basis, parity, oscillator realization, structure constants |
| Schema 2 | `C_n_gamma.json` | Inhomogeneous deformation (γ-structure) |
| Schema 3 | `C_n_evaluated_<gb>.json` | Numerically evaluated structure constants for specific γ parameters |
| Schema 4 | `C_n_coboundary_<gb>.json` | Coboundary data for triviality verification |

where `n` is the bosonic rank:
- C(2) = osp(2|2): `C_1_structure.json`, `C_1_gamma.json`, etc.
- C(3) = osp(2|4): `C_2_structure.json`, `C_2_gamma.json`, etc.
- C(4) = osp(2|6): `C_3_structure.json`, `C_3_gamma.json`, etc.

---

## Schema 1: Algebra Structure (`C_n_structure.json`)

### Top-Level Keys

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
  "dimension": {
    "total": 19,
    "even": 11,
    "odd": 8
  }
}
```

**Dimension formulas** (C(n+1) = osp(2|2n)):
- even = $2n^2 + n + 1$
- odd = $4n$
- total = $2n^2 + 5n + 1$

| $n$ | Algebra | even | odd | total |
|---|---|---|---|---|
| 1 | C(2) = osp(2\|2) | 4 | 4 | 8 |
| 2 | C(3) = osp(2\|4) | 11 | 8 | 19 |
| 3 | C(4) = osp(2\|6) | 22 | 12 | 34 |

### `oscillator_generators`

```json
{
  "fermions": {
    "label": "a_1",
    "m": 1,
    "parity": 1,
    "relation": "{a_1^-, a_1^+} = 1",
    "description": "Standard fermionic pair (CAR); m=1 indicates dimension of fermionic subsystem",
    "labels": ["a_1_p", "a_1_m"]
  },
  "bosons": {
    "count": 4,
    "n": 2,
    "labels": ["b_1_p", "b_1_m", "b_2_p", "b_2_m"],
    "description": "Bosonic oscillators b_i^± with i=1,...,n"
  }
}
```

**Key differences from B(0,n)**:
- B(0,n) has a `supplementary_fermion` (a_0 with $a_0^2 = 1/2$)
- C(n+1) has `fermions` with a standard CAR pair (a_1^+, a_1^-) with ${a_1^-, a_1^+} = 1$
- The parameter `m=1` indicates the dimension of the fermionic subsystem (osp(2m|2n))

### `oscillator_relations`

```json
{
  "standard_fermion_anticommutators": {
    "description": "Canonical anticommutation relations for standard fermionic pair",
    "relations": {
      "pair": "{a_1^-, a_1^+} = 1",
      "same": "{a_1^±, a_1^±} = 0"
    }
  },
  "bosonic_commutators": {
    "description": "Canonical commutation relations for bosonic oscillators",
    "relations": {
      "same_type": "[b_i^±, b_j^±] = 0 for all i, j",
      "conjugate_pair": "[b_i^-, b_j^+] = δ_{ij}"
    }
  },
  "mixed_anticommutators": {
    "fermion_boson": "{a_1^±, b_j^±} = 0"
  }
}
```

### `central_elements`

**New top-level key for C(n+1)**:

```json
{
  "kappa": {
    "label": "κ",
    "parity": 1,
    "nilpotency": "κ^2 = 0",
    "description": "Odd central element used in inhomogeneous deformation"
  },
  "K": {
    "label": "K",
    "parity": 0,
    "note": "Even central element (formal identity); identified with scalar 1 in applications"
  }
}
```

**Role**: 
- $\kappa$ is odd and nilpotent, serving as the symbol of the extension $\tilde{\mathfrak{g}} = \mathfrak{g} \oplus \mathbb{R}\kappa$
- $K$ is even and represents the formal central identity (not included in basis lists but recorded for schema completeness)
- In the deformed bracket $[X, Y]_\gamma = [X, Y]_0 + \kappa \cdot \gamma(X, Y)$, $\kappa$ parametrizes the deformation

### `basis`

PBW ordering (C(n+1) convention from I01):
```
[central elements] < [Cartan: H_1, ..., H_{n+1}] 
  < [positive odd: E_eps_del{k}_pp/pm] 
  < [positive even: E_2del_p, E_del{i}_del{j}_pp/pm]
  < [negative even] < [negative odd]
```

Example for C(3) (n=2):
```json
{
  "even": [
    "H_1", "H_2", "H_3",
    "E_2del1_p", "E_del1_del2_pp", "E_del1_del2_pm", "E_2del2_p",
    "E_2del1_m", "E_del1_del2_mp", "E_del1_del2_mm", "E_2del2_m"
  ],
  "odd": [
    "E_eps_del1_pp", "E_eps_del2_pp",
    "E_eps_del1_pm", "E_eps_del2_pm",
    "E_eps_del1_mp", "E_eps_del2_mp",
    "E_eps_del1_mm", "E_eps_del2_mm"
  ],
  "ordering_convention": "PBW: [central] < [Cartan] < [positive odd] < [positive even] < [negative even] < [negative odd]; κ excluded from basis lists (formally present)"
}
```

### `parity`

All Cartan elements H_k have parity 0.
All odd root generators E_eps_del{k}_{...} have parity 1.
All even root generators E_2del{k}_{...} and E_del{i}_del{j}_{...} have parity 0.

### `generator_realization`

Each generator is expressed as a sum of oscillator words with rational coefficients.

Example for C(2) (n=1):
```json
{
  "description": "Standard form with PBW ordering",
  "ordering": "a_1_p, a_1_m, b_1_p, b_1_m",
  "realizations": {
    "H_1": {
      "standard_form": [
        {"words": ["a_1_p", "a_1_m"], "coeff": "1"},
        {"words": ["b_1_p", "b_1_m"], "coeff": "1"}
      ],
      "frappat_form": "a_1^+ a_1^- + b_1^+ b_1^-",
      "parity": 0
    },
    "H_2": {
      "standard_form": [
        {"words": ["b_1_p", "b_1_m"], "coeff": "-1"},
        {"words": [], "coeff": "-1/2"}
      ],
      "frappat_form": "-b_1^+ b_1^- - 1/2",
      "parity": 0
    },
    "E_eps_del1_pp": {
      "standard_form": [
        {"words": ["a_1_p", "b_1_p"], "coeff": "1"}
      ],
      "frappat_form": "a_1^+ b_1^+",
      "parity": 1
    },
    "E_eps_del1_pm": {
      "standard_form": [
        {"words": ["a_1_p", "b_1_m"], "coeff": "1"}
      ],
      "frappat_form": "a_1^+ b_1^-",
      "parity": 1
    },
    "E_2del1_p": {
      "standard_form": [
        {"words": ["b_1_p", "b_1_p"], "coeff": "1/2"}
      ],
      "frappat_form": "1/2 (b_1^+)^2",
      "parity": 0
    }
  }
}
```

### `structure_constants`

Non-zero graded brackets $[X, Y\}$ stored as a list, following standard Lie superalgebra conventions.

Example:
```json
[
  {
    "X": "H_1",
    "Y": "E_eps_del1_pp",
    "Z": "E_eps_del1_pp",
    "coeff": "1",
    "sign_rule": "graded"
  },
  {
    "X": "E_eps_del1_pp",
    "Y": "E_eps_del1_pm",
    "Z": "E_2del1_p",
    "coeff": "1",
    "sign_rule": "graded",
    "note": "[a_1^+ b_1^+, a_1^+ b_1^-] = (b_1^+)^2"
  }
]
```

### `metadata`

```json
{
  "generated_by": "build_C_structure_constants.py",
  "generation_date": "YYYY-MM-DD",
  "references": [
    "Frappat, Sciarrino, Sorba (2000), Dictionary on Lie Algebras and Superalgebras",
    "Bakalov and Sullivan (2017)",
    "Issue I02 specification"
  ]
}
```

---

## Key Design Decisions for C(n+1)

### 1. Family and Dimension
- `family: "C"`, `m: 1` (fixed for all C(n+1) algebras)
- Dimension formula: even = $2n^2 + n + 1$, odd = $4n$
- These are mandated by Frappat's classification (osp(2|2n))

### 2. Oscillator Generators Structure
- **B(0,n)**: Single supplementary fermion $a_0$ with $a_0^2 = 1/2$ (not a CAR pair)
- **C(n+1)**: Standard fermionic pair $(a_1^+, a_1^-)$ satisfying CAR $\{a_1^-, a_1^+\} = 1$
- The key `"fermions"` replaces `"supplementary_fermion"`
- Include parameter `"m": 1` to document the fermionic dimension

### 3. Central Elements (New Top-Level Key)
C(n+1) introduces a new top-level `"central_elements"` key (not present in B(0,n) schema):
- **κ (kappa)**: Odd central element, $\kappa^2 = 0$, used in deformation
- **K**: Even central element, formally the identity

**Why at top level**: These elements are fundamental to the algebraic structure and the deformation theory, and must be visible in all schema layers.

### 4. Basis and Generator Labels
- Generator labels for odd roots: `E_eps_del{k}_{pp/pm/mp/mm}` (two subscripts for ε sign and δ sign)
- Generator labels for even roots: Same as B(0,n) (e.g., `E_2del{k}_p`, `E_del{i}_del{j}_pp`)

### 5. PBW Ordering
- Fermionic-first convention (decided in I01)
- Order: Cartan < positive odd < positive even < negative even < negative odd
- Central elements formally precede all basis elements (but not listed in basis)

### 6. File Naming Convention
- **Pattern**: `C_{n}_structure.json` where `n = $ bosonic rank (not n+1)
- **Examples**:
  - C(2) = osp(2|2): `C_1_structure.json`
  - C(3) = osp(2|4): `C_2_structure.json`
  - C(4) = osp(2|6): `C_3_structure.json`

This maintains consistency with existing naming: the filename reflects the mathematical algebra's subscript/parameter n.

---

## Backward Compatibility with B(m,n)

The C(n+1) schema is designed to extend the B(0,n) schema while maintaining compatibility:

| Feature | B(0,n) | C(n+1) | Compatibility |
|---------|--------|--------|---|
| `schema_version` | "5.0" | "5.0" | ✓ Same |
| `family` | "B" | "C" | Family-specific; no conflict |
| Central elements | Not top-level (or implicit) | Top-level key | Additive; B-schema may be updated retroactively |
| Oscillator generators | `supplementary_fermion` | `fermions` | Different keys; no conflict |
| Basis ordering | Odd < even | Positive odd < positive even (within positives) | Enhanced precision in C |

**Future-proofing**: The schema design allows for:
- Extension to C(n+1) without modifying B(0,n) files
- Addition of other families (A(m,n), D(m,n), etc.) using the same framework
- Parametrization by (m, n) to cover all classical Lie superalgebras of contact and Hamiltonian type
