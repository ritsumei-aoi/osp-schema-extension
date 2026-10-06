# C(n+1) JSON Schema Specification (v5.0 extension)

This document specifies the four-layer JSON schema for C(n+1) = osp(2|2n),
extending the B(0,n) v5.0 schema (`docs/math/B0n_schema_v5.md`).
The base-case schema conventions are preserved verbatim where possible so
B(0,n) and C(n+1) can be processed by the same tooling.

## 1. File naming

| Layer | File (n = bosonic rank) |
|---|---|
| 1 Structure | `C_{n}_structure.json`     |
| 2 Gamma     | `C_{n}_gamma.json`         |
| 3 Evaluated | `C_{n}_evaluated.json`     |
| 4 Coboundary| `C_{n}_coboundary.json`    |

`n` is the bosonic rank, so C(2) uses `n=1`, C(3) uses `n=2`, C(4) uses `n=3`.
Files live in `data/`.

## 2. Schema 1 — algebra structure

### Top-level keys

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

Backward compatibility with B(0,n): `schema_version`, `basis`, `parity`,
`generator_realization`, `structure_constants`, `metadata` keep the same
shape as B(0,n) v5.0. New top-level key `central_elements` (mandatory for
C(n+1); B(0,n) stored this inline under `oscillator_generators`).

### `algebra`

```json
{
  "family": "C",
  "m": 1,
  "n": <bosonic rank>,
  "cartan_type": "C(n+1)",
  "alternative_notation": {
    "osp": "osp(2|2n)",
    "dimension_formula": "osp(2m|2n) with m=1"
  },
  "dimension": {
    "even": "2n^2 + n + 1",
    "odd":  "4n",
    "total":"2n^2 + 5n + 1"
  }
}
```

The `m=1` field is **mandatory** and distinguishes C(n+1) from B(0,n).

### `oscillator_generators`

Two keys: `fermions` and `bosons`. No `supplementary_fermion` key.

```json
{
  "fermions": {
    "m": 1,
    "count": 2,
    "labels": ["a_1_p", "a_1_m"],
    "description": "Standard fermionic pair a_1^± with CAR"
  },
  "bosons": {
    "n": <n>,
    "count": <2n>,
    "labels": ["b_1_p","b_1_m", ...],
    "description": "Bosonic oscillators b_k^±"
  }
}
```

### `oscillator_relations`

```json
{
  "standard_fermion_anticommutators": {
    "description": "CAR for the standard fermionic pair",
    "relations": {
      "pair":    "{a_1^-, a_1^+} = 1",
      "squares": "(a_1^+)^2 = 0, (a_1^-)^2 = 0"
    }
  },
  "bosonic_commutators": {
    "relations": {
      "same_type": "[b_i^s, b_j^s] = 0",
      "conjugate_pair": "[b_i^-, b_j^+] = δ_{ij}"
    }
  },
  "mixed_commutators": {
    "boson_fermion": "[b_k^s, a_1^σ] = 0 (undeformed; deformed = -gb_{σ,k,s} κ)"
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
    "role": "Formal generator of the odd central extension used for the inhomogeneous (gb) deformation"
  },
  "K": {
    "label": "K",
    "parity": 0,
    "relation": "K = 1 (identified with the scalar identity)",
    "role": "Even central identity; excluded from basis listings"
  }
}
```

### `basis`

Even and odd lists, PBW ordering as defined in `handover/notation.md` §6–7.
`κ` is listed only in `central_elements`; `K` is omitted entirely.

### `parity`

Map from each basis label to 0 or 1.  Even generators have parity 0, odd
generators have parity 1.

### `generator_realization`

Each generator maps to a `standard_form` (list of `{words, coeff}` records),
a `frappat_form` (human-readable expression) and the `parity`. Oscillator
word symbols are drawn from `{a_1_p, a_1_m, b_k_p, b_k_m}`. The ordering
used inside each word is `a_1_p < a_1_m < b_1_p < b_1_m < … < b_n_p < b_n_m`.

Cartan realizations (compatible with `docs/math/Cn1_definition.md`):
- `H_1 = a_1_p a_1_m + b_1_p b_1_m`
- `H_k = b_{k-1}_p b_{k-1}_m − b_k_p b_k_m`  (2 ≤ k ≤ n)
- `H_{n+1} = − b_n_p b_n_m − 1/2`

Root-vector realizations: see §4 of `Cn1_definition.md`.

### `structure_constants`

List of `{X, Y, Z, coeff, sign_rule}` records giving the non-zero graded
brackets `[X, Y}`. The sign rule is "graded": `[X, Y} = XY − (−1)^{p(X)p(Y)} YX`.

### `metadata`

```json
{
  "generated_by": "src/C_generators.py",
  "generation_date": "YYYY-MM-DD",
  "references": [
    "Frappat–Sciarrino–Sorba (2000), Dictionary on Lie Algebras and Superalgebras",
    "arXiv:hep-th/9607161"
  ]
}
```

## 3. Schema 2 — γ structure (inhomogeneous deformation)

Top-level additions:

```json
{
  "schema_version": "5.0",
  "schema_layer": 2,
  "algebra": { ... }, // same shape as Schema 1
  "gb_parameters": {
    "shape": "2 x 2n",
    "labels": [
      "gb_{a_1_p, b_1_p}", "gb_{a_1_p, b_1_m}",
      "gb_{a_1_m, b_1_p}", "gb_{a_1_m, b_1_m}",
      ...
    ],
    "parity": 1,
    "count": 4
  },
  "gamma_coefficients": [
    {"X": "...", "Y": "...", "Z": "...",
     "coeff": "<linear combination in gb symbols>"}
  ],
  "metadata": { ... }
}
```

Here `Z` is always `kappa` because the deformation cocycle only produces
κ-valued contributions.  `coeff` is a sympy-serialisable string in the gb
symbols.

## 4. Schema 3 — evaluated structure

Same shape as Schema 2 but every `coeff` is replaced by a rational number
after a concrete substitution of the gb parameters.  The chosen substitution
is recorded in the `evaluation` key:

```json
{
  "schema_layer": 3,
  "evaluation": {
    "profile_name": "all_plus_one",
    "gb_values": {"gb_{a_1_p, b_1_p}": "1", ...}
  },
  "evaluated_gamma": [
    {"X": "...", "Y": "...", "Z": "kappa", "coeff": "1"}
  ]
}
```

## 5. Schema 4 — coboundary structure

Shape:

```json
{
  "schema_layer": 4,
  "linear_map_f": {
    "description": "Odd linear map f: g -> g",
    "phi_matrix": {
      "<basis_j>": [{"basis_i": "...", "coeff": "..."}]
    }
  },
  "delta_f_coefficients": [
    {"X": "...", "Y": "...", "Z": "kappa", "coeff": "..."}
  ]
}
```

## 6. Compatibility with B(m,n) v5.0

- Shared keys retain names and shapes: `schema_version`, `algebra`,
  `oscillator_relations.bosonic_commutators`, `basis.ordering_convention`,
  `parity`, `generator_realization`, `structure_constants`, `metadata`.
- B(0,n) uses `supplementary_fermion` + `supplementary_fermion_relation`;
  C(n+1) replaces these with `fermions` + `standard_fermion_anticommutators`.
- C(n+1) promotes `central_elements` to a top-level key with κ and K.
- Odd basis labels differ: B(0,n) has `E_del{k}_p/m` (2n); C(n+1) has
  `E_eps1_del{k}_pp/pm/mp/mm` (4n).
- Dimension formulas: B(0,n) even = 2n²+n, odd = 2n; C(n+1) even = 2n²+n+1,
  odd = 4n.

## 7. File naming confirmation

Agreed convention: `C_<n>_<layer>.json` with `<n>` = bosonic rank and
`<layer> ∈ {structure, gamma, evaluated, coboundary}`.
