# JSON Schema Specification v5.0 — C(n+1) = osp(2|2n) Extension

This document specifies the complete v5.0 JSON schema for
C(n+1) = osp(2|2n) structure data, extending the B(0,n) v5.0 base schema
(`docs/math/B0n_schema_v5.md`). It covers all four layers; Schema 1 is
normative for Issue I02, Schemas 2–4 for Issues I05–I07.

Basis lists, PBW ordering, and generator labels follow `handover/notation.md`
(finalized in I01).

---

## File Naming Convention

| Layer | File | Contents |
|---|---|---|
| Schema 1 | `data/C_{n}_structure.json` | Algebra structure and structure constants |
| Schema 2 | `data/C_{n}_gamma.json` | Symbolic inhomogeneous deformation (γ-structure) |
| Schema 3 | `data/C_{n}_evaluated.json` | γ evaluated at a concrete gb assignment |
| Schema 4 | `data/C_{n}_coboundary.json` | Coboundary δf data for triviality analysis |

`n` is the **bosonic rank**: C(2) = osp(2|2) → `C_1_structure.json`,
C(3) = osp(2|4) → `C_2_structure.json`, C(4) = osp(2|6) → `C_3_structure.json`.

---

## Schema 1: Algebra Structure (`C_{n}_structure.json`)

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
  "structure_constants": [ ... ],
  "metadata": { ... }
}
```

Compared to B(0,n) v5.0, the single new **top-level** key is
`central_elements`; all other keys exist in both families (contents differ
as specified below).

### `algebra`

```json
{
  "family": "C",
  "m": 1,
  "n": 2,
  "cartan_type": "C(3)",
  "alternative_notation": {
    "osp": "osp(2|4)",
    "dimension_formula": "osp(2m|2n) with m=1; even = 2n^2 + n + 1, odd = 4n"
  },
  "dimension": {
    "total": 19,
    "even": 11,
    "odd": 8
  }
}
```

- `"m": 1` is mandatory and fixed for the C(n+1) family.
- Dimension formulas: even = `2n^2 + n + 1`, odd = `4n`, total = `2n^2 + 5n + 1`.

| n | cartan_type | osp | even | odd | total |
|---|---|---|---|---|---|
| 1 | C(2) | osp(2\|2) | 4 | 4 | 8 |
| 2 | C(3) | osp(2\|4) | 11 | 8 | 19 |
| 3 | C(4) | osp(2\|6) | 22 | 12 | 34 |

### `oscillator_generators`

Exactly two keys: `fermions` and `bosons`. The B(0,n) key
`supplementary_fermion` is **removed** (there is no a_0 in C(n+1)).

```json
{
  "fermions": {
    "m": 1,
    "count": 2,
    "labels": ["a_1_p", "a_1_m"],
    "parity": 1,
    "description": "Standard fermionic pair a_1^± with CAR {a_1^-, a_1^+} = 1"
  },
  "bosons": {
    "n": 2,
    "count": 4,
    "labels": ["b_1_p", "b_1_m", "b_2_p", "b_2_m"],
    "parity": 0,
    "description": "Bosonic oscillators b_k^± with k=1,...,n (CCR)"
  }
}
```

### `oscillator_relations`

The B(0,n) `supplementary_fermion_relation` is replaced by
`standard_fermion_anticommutators`:

```json
{
  "standard_fermion_anticommutators": {
    "description": "Canonical anticommutation relations for the standard fermionic pair",
    "relations": {
      "conjugate_pair": "{a_1^-, a_1^+} = 1",
      "same_type": "{a_1^+, a_1^+} = {a_1^-, a_1^-} = 0  (i.e. (a_1^±)^2 = 0)"
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
    "boson_fermion": "[b_i^±, a_1^±] = 0 (undeformed; deformation adds -gb·κ, see Schema 2)"
  }
}
```

### `central_elements` (new top-level key)

```json
{
  "kappa": {
    "label": "kappa",
    "parity": 1,
    "relation": "kappa^2 = 0",
    "description": "Odd nilpotent central element; carrier of the inhomogeneous deformation."
  },
  "K": {
    "label": "K",
    "parity": 0,
    "relation": "K = 1",
    "description": "Even central element, identified with the scalar 1; excluded from the basis and PBW ordering."
  }
}
```

### `basis`

PBW ordering (decided in I01): `κ < [odd] < [even]`, K = 1 excluded.
Example for n = 2:

```json
{
  "even": [
    "H_eps", "H_1", "H_2",
    "E_2del1_p", "E_2del2_p",
    "E_del1_del2_pp",
    "E_2del1_m", "E_2del2_m",
    "E_del1_del2_mm",
    "E_del1_del2_pm", "E_del1_del2_mp"
  ],
  "odd": [
    "E_eps_del1_pp", "E_eps_del2_pp",
    "E_eps_del1_pm", "E_eps_del2_pm",
    "E_eps_del1_mp", "E_eps_del2_mp",
    "E_eps_del1_mm", "E_eps_del2_mm"
  ],
  "ordering_convention": "PBW: kappa < [odd] < [even]  (K = 1 is excluded)"
}
```

### `parity`

Map from every basis label to 0 or 1. Odd generators are exactly the
`E_eps_del{k}_{σs}` labels; everything else is even.

### `generator_realization`

Same format as B(0,n): each generator is a list of normal-ordered oscillator
words with rational coefficients (strings). Oscillator word ordering:
`a_1_p < a_1_m < b_1_p < b_1_m < ... < b_n_p < b_n_m`.

```json
{
  "description": "Standard form with PBW-ordered oscillator words",
  "ordering": "a_1_p, a_1_m, b_1_p, b_1_m, ..., b_n_p, b_n_m",
  "realizations": {
    "H_eps": {
      "standard_form": [
        {"words": ["a_1_p", "a_1_m"], "coeff": "1"},
        {"words": [], "coeff": "-1/2"}
      ],
      "frappat_form": "a_1^+ a_1^- - 1/2",
      "parity": 0
    },
    "H_k": {
      "standard_form": [
        {"words": ["b_k_p", "b_k_m"], "coeff": "1"},
        {"words": [], "coeff": "1/2"}
      ],
      "frappat_form": "b_k^+ b_k^- + 1/2",
      "parity": 0
    },
    "E_eps_del{k}_pp": {
      "standard_form": [{"words": ["a_1_p", "b_k_p"], "coeff": "1"}],
      "frappat_form": "a_1^+ b_k^+",
      "parity": 1
    }
  }
}
```

(Realizations for all generators follow the table in `handover/notation.md` §3.)

### `structure_constants`

List of all non-zero graded brackets `[X, Y} = XY − (−1)^{p(X)p(Y)} YX`
for **ordered** pairs of basis elements:

```json
[
  {"X": "H_eps", "Y": "E_eps_del1_pp", "Z": "E_eps_del1_pp", "coeff": "1", "sign_rule": "graded"}
]
```

Multiple `Z` terms for one (X, Y) appear as separate entries. Coefficients
are exact rationals, serialized as strings.

### `metadata`

```json
{
  "generated_by": "src/C_generators.py",
  "generation_date": "YYYY-MM-DD",
  "references": [
    "Frappat et al. (2000), Dictionary on Lie Algebras and Superalgebras",
    "docs/math/Cn1_definition.md"
  ]
}
```

---

## Backward Compatibility with B(m,n) v5.0

| Key | B(0,n) | C(n+1) | Compatibility note |
|---|---|---|---|
| `schema_version` | "5.0" | "5.0" | unchanged |
| `algebra.family` | "B" | "C" | discriminator field |
| `algebra.m` | 0 | 1 | readers must branch on (family, m) |
| `oscillator_generators` | `supplementary_fermion` + `bosons` | `fermions` + `bosons` | readers should accept either fermionic key |
| `oscillator_relations` | `supplementary_fermion_relation` | `standard_fermion_anticommutators` | renamed; `bosonic_commutators`/`mixed_commutators` unchanged |
| `central_elements` | absent (κ, K described in prose) | top-level key | additive — B readers ignore it |
| `basis.odd` | `E_del{k}_p/m` (2n) | `E_eps_del{k}_{σs}` (4n) | label pattern change only |
| even basis labels | `H_k`, `E_2del…`, `E_del…del…` | same + `H_eps` | sp(2n) sector identical |
| `structure_constants` | same record format | same record format | unchanged |

A B(0,n) v5.0 reader that ignores unknown keys and treats basis labels as
opaque strings parses C(n+1) files without modification.

---

## Schema 2: Gamma Structure (`C_{n}_gamma.json`)

```json
{
  "schema_version": "5.0",
  "layer": 2,
  "algebra_ref": "C_{n}_structure.json",
  "gb_matrix": {
    "description": "4n parity-1 deformation parameters gb_{σ,j,s}: [b_j^s, a_1^σ] = -gb_{σ,j,s}·kappa",
    "shape": [2, "2n"],
    "rows": ["a_1_p", "a_1_m"],
    "columns": ["b_1_p", "b_1_m", "...", "b_n_p", "b_n_m"],
    "labels": ["gb_p_1_p", "gb_p_1_m", "gb_m_1_p", "gb_m_1_m", "..."]
  },
  "inhomogeneous_deformation": {
    "description": "[X,Y]_gamma = [X,Y]_0 + kappa·gamma(X,Y); entries list gamma(X,Y) as gb-linear combinations of basis elements (and K for scalar parts)",
    "entries": [
      {"X": "...", "Y": "...", "terms": [{"gb": "gb_p_1_m", "Z": "...", "coeff": "1"}]}
    ]
  },
  "metadata": { ... }
}
```

`Z` may be any Schema 1 basis label or `"K"` (scalar component).

## Schema 3: Evaluated Structure (`C_{n}_evaluated.json`)

```json
{
  "schema_version": "5.0",
  "layer": 3,
  "algebra_ref": "C_{n}_structure.json",
  "gamma_ref": "C_{n}_gamma.json",
  "gb_assignment": {"gb_p_1_p": "1", "gb_p_1_m": "1", "...": "..."},
  "evaluated_gamma": [
    {"X": "...", "Y": "...", "Z": "...", "coeff": "1"}
  ],
  "metadata": { ... }
}
```

## Schema 4: Coboundary Structure (`C_{n}_coboundary.json`)

```json
{
  "schema_version": "5.0",
  "layer": 4,
  "algebra_ref": "C_{n}_structure.json",
  "gb_assignment": {"gb_p_1_p": "1", "...": "..."},
  "f_map": {
    "description": "Odd linear map f: g -> g, f(Z_j) = Σ_i φ_ij Z_i",
    "entries": [{"source": "Z_j", "target": "Z_i", "coeff": "..."}]
  },
  "coboundary": [
    {"X": "...", "Y": "...", "Z": "...", "coeff": "..."}
  ],
  "convention": "(δf)(X,Y) = (-1)^{p(X)}[X,f(Y)] - (-1)^{(p(X)+1)p(Y)}[Y,f(X)] - f([X,Y])",
  "metadata": { ... }
}
```
