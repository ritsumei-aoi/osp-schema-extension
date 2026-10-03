# JSON Schema Specification for C(n+1) = osp(2|2n), v5.0

This document defines the 4-layer JSON schema for C(n+1), extending the B(0,n) v5.0 schema.
See `docs/math/B0n_schema_v5.md` for the base B(0,n) specification.

---

## File Naming Convention

| n (bosonic rank) | Algebra | Schema 1 | Schema 2 | Schema 3 | Schema 4 |
|---|---|---|---|---|---|
| 1 | C(2) = osp(2\|2) | `C_1_structure.json` | `C_1_gamma.json` | `C_1_evaluated.json` | `C_1_coboundary.json` |
| 2 | C(3) = osp(2\|4) | `C_2_structure.json` | `C_2_gamma.json` | `C_2_evaluated.json` | `C_2_coboundary.json` |
| 3 | C(4) = osp(2\|6) | `C_3_structure.json` | `C_3_gamma.json` | `C_3_evaluated.json` | `C_3_coboundary.json` |

All files are placed in `data/`.

---

## Compatibility with B(m,n) Schema

The C(n+1) schema is a strict extension of the B(0,n) v5.0 schema. Changes:

| Field | B(0,n) | C(n+1) |
|---|---|---|
| `algebra.family` | `"B"` | `"C"` |
| `algebra.m` | `0` | `1` |
| `algebra.cartan_type` | `"B(0,n)"` | `"C(n+1)"` |
| `algebra.alternative_notation.osp` | `"osp(1\|2n)"` | `"osp(2\|2n)"` |
| `algebra.dimension.even` | 2n²+n | 2n²+n+1 |
| `algebra.dimension.odd` | 2n | 4n |
| `oscillator_generators` key | `supplementary_fermion` | `fermions` (standard CAR pair) |
| `oscillator_relations` | supplementary fermion relation | CAR anticommutator |
| `basis.odd` | E_del{k}_p/m (2n generators) | E_eps1_del{k}_{pp/pm/mp/mm} (4n generators) |
| `parity` | odd generators have parity 1 | same (4n odd generators) |
| `generator_realization` | uses a_0 | uses a_1_p, a_1_m |
| `structure_constants` | computed from B(0,n) relations | recomputed from CAR relations |

New top-level key added: `central_elements` (present in C(n+1), not in B(0,n)).

---

## Schema 1: Algebra Structure (`C_n_structure.json`)

### Top-level structure

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

### `algebra` field

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
    "total": 8,
    "even": 4,
    "odd": 4,
    "even_formula": "2*n^2 + n + 1",
    "odd_formula": "4*n"
  }
}
```

### `central_elements` field (top-level key)

```json
{
  "K": {
    "label": "K",
    "parity": 0,
    "description": "Even central identity; K=1 in all realizations. Excluded from basis and PBW ordering.",
    "property": "K = 1"
  },
  "kappa": {
    "label": "kappa",
    "parity": 1,
    "description": "Odd central nilpotent element; appears in deformed bracket.",
    "property": "kappa^2 = 0"
  }
}
```

### `oscillator_generators` field

```json
{
  "fermions": {
    "m": 1,
    "labels": ["a_1_p", "a_1_m"],
    "parity": 1,
    "description": "Standard fermionic CAR pair a_1^+, a_1^-"
  },
  "bosons": {
    "count": 2,
    "n": 1,
    "labels": ["b_1_p", "b_1_m"],
    "description": "Bosonic oscillators b_k^± with k=1,...,n"
  }
}
```

(For n=2: bosons count=4, labels=["b_1_p","b_1_m","b_2_p","b_2_m"])
(For n=3: bosons count=6, labels=["b_1_p","b_1_m","b_2_p","b_2_m","b_3_p","b_3_m"])

### `oscillator_relations` field

```json
{
  "fermionic_anticommutators": {
    "description": "Canonical anticommutation relations for standard fermionic pair",
    "relations": {
      "anticommutator": "{a_1^-, a_1^+} = 1",
      "same_sign": "{a_1^s, a_1^s} = 0 for s in {+,-}"
    }
  },
  "bosonic_commutators": {
    "description": "Canonical commutation relations for bosonic oscillators",
    "relations": {
      "same_type": "[b_i^s, b_j^s] = 0 for all i,j,s",
      "conjugate_pair": "[b_i^-, b_j^+] = delta_ij"
    }
  },
  "mixed_commutators": {
    "boson_fermion": "[b_k^s, a_1^sigma] = -gb_{sigma,k,s} * kappa  (deformation; =0 in undeformed case)"
  }
}
```

### `basis` field

PBW ordering: `κ < [odd] < [even]`

```json
{
  "even": [
    "H_1", "H_2",
    "E_2del1_p",
    "E_2del1_m",
    "E_del1_del2_pp"
  ],
  "odd": [
    "E_eps1_del1_pp", "E_eps1_del1_pm",
    "E_eps1_del1_mp", "E_eps1_del1_mm"
  ],
  "ordering_convention": "PBW: kappa < [odd: E_eps1_del{k}_{pp/pm/mp/mm}] < [even: H_k, E_2del{k}_p/m, E_del{i}_del{j}_{pp/mm/pm/mp}]"
}
```

(Example for n=1; for n=2,3 the lists grow according to notation.md)

### `parity` field

Parity assignment: even generators → 0, odd generators → 1.

```json
{
  "H_1": 0, "H_2": 0,
  "E_2del1_p": 0, "E_2del1_m": 0,
  "E_eps1_del1_pp": 1, "E_eps1_del1_pm": 1,
  "E_eps1_del1_mp": 1, "E_eps1_del1_mm": 1
}
```

### `generator_realization` field

Each generator expressed as a sum of oscillator words with rational coefficients.
Ordering: a_1_p, a_1_m, b_1_p, b_1_m, [b_2_p, b_2_m, ...]

Key realizations:
- H_1: a_1^+ a_1^- + b_1^+ b_1^- = [{"words":["a_1_p","a_1_m"],"coeff":"1"},{"words":["b_1_p","b_1_m"],"coeff":"1"}]
- H_k (2≤k≤n): b_{k-1}^+ b_{k-1}^- - b_k^+ b_k^-
- H_{n+1}: -b_n^+ b_n^- - 1/2
- E_eps1_del{k}_pp: [{"words":["a_1_p","b_k_p"],"coeff":"1"}]  (a_1^+ b_k^+)
- E_eps1_del{k}_pm: [{"words":["a_1_p","b_k_m"],"coeff":"1"}]  (a_1^+ b_k^-)
- E_eps1_del{k}_mp: [{"words":["a_1_m","b_k_p"],"coeff":"1"}]  (a_1^- b_k^+)
- E_eps1_del{k}_mm: [{"words":["a_1_m","b_k_m"],"coeff":"1"}]  (a_1^- b_k^-)
- E_2del{k}_p: [{"words":["b_k_p","b_k_p"],"coeff":"1"}]  ((b_k^+)^2)
- E_2del{k}_m: [{"words":["b_k_m","b_k_m"],"coeff":"1"}]  ((b_k^-)^2)
- E_del{i}_del{j}_pp (i<j): [{"words":["b_i_p","b_j_p"],"coeff":"1"}]
- E_del{i}_del{j}_mm (i<j): [{"words":["b_i_m","b_j_m"],"coeff":"1"}]
- E_del{i}_del{j}_pm (i<j): [{"words":["b_i_p","b_j_m"],"coeff":"1"}]
- E_del{i}_del{j}_mp (i<j): [{"words":["b_i_m","b_j_p"],"coeff":"1"}]

### `structure_constants` field

Non-zero graded brackets [X,Y} stored as a list of objects:

```json
[
  {
    "X": "H_1",
    "Y": "E_eps1_del1_pp",
    "Z": "E_eps1_del1_pp",
    "coeff": "2",
    "sign_rule": "graded"
  }
]
```

Key brackets to compute (using relations):
- [H_k, E_eps1_del{l}_{ss}]: eigenvalue from Cartan action on ε±δ_l root
- [E_eps1_del{k}_pp, E_eps1_del{l}_mm]: produces even generators
- [E_eps1_del{k}_pm, E_eps1_del{l}_mp]: produces even generators
- [E_2del{k}_p, E_2del{k}_m]: produces H_k-type
- [E_del{i}_del{j}_pp, E_del{i}_del{j}_mm]: produces Cartan
- All even×even, even×odd, odd×odd brackets

### `metadata` field

```json
{
  "generated_by": "src/C_generators.py",
  "generation_date": "YYYY-MM-DD",
  "references": [
    "Frappat, Sciarrino, Sorba (2000), Dictionary on Lie Algebras and Superalgebras",
    "arXiv:hep-th/9607161"
  ]
}
```

---

## Schema 2: Inhomogeneous Deformation (`C_n_gamma.json`)

### Top-level structure

```json
{
  "schema_version": "5.0",
  "algebra": "C(n+1)",
  "n": 1,
  "gb_matrix": { ... },
  "gamma_coefficients": [ ... ],
  "metadata": { ... }
}
```

### `gb_matrix` field

The gb matrix for C(n+1) has 4n parameters (2 fermionic × 2n bosonic):

```json
{
  "size": "2 x 2n",
  "parameters": {
    "gb_p1_p1": {"sigma": "+", "k": 1, "s": "+", "parity": 1},
    "gb_p1_m1": {"sigma": "+", "k": 1, "s": "-", "parity": 1},
    "gb_m1_p1": {"sigma": "-", "k": 1, "s": "+", "parity": 1},
    "gb_m1_m1": {"sigma": "-", "k": 1, "s": "-", "parity": 1}
  },
  "description": "gb_{sigma,k,s} where sigma in {+,-} (fermionic), k in {1..n} (boson index), s in {+,-} (bosonic)"
}
```

(Label convention: `gb_{sigma}{1}_{s}{k}` where {sigma} is p/m for a_1^+/-, {s} is p/m for b_k^+/-)

### `gamma_coefficients` field

Non-zero γ_{abc} coefficients:

```json
[
  {
    "X": "E_eps1_del1_pp",
    "Y": "E_eps1_del1_mm",
    "Z": "H_1",
    "coeff_expr": "gb_p1_p1 * gb_m1_m1 - gb_p1_m1 * gb_m1_p1",
    "description": "From {a_1^+, a_1^-} = 1 and bosonic terms"
  }
]
```

---

## Schema 3: Evaluated Structure (`C_n_evaluated.json`)

Same structure as Schema 2 but with concrete numerical values substituted for gb parameters.
Representative assignment: all gb = +1.

```json
{
  "schema_version": "5.0",
  "algebra": "C(n+1)",
  "n": 1,
  "gb_assignment": {"gb_p1_p1": 1, "gb_p1_m1": 1, "gb_m1_p1": 1, "gb_m1_m1": 1},
  "evaluated_gamma": [ ... ]
}
```

---

## Schema 4: Coboundary Structure (`C_n_coboundary.json`)

```json
{
  "schema_version": "5.0",
  "algebra": "C(n+1)",
  "n": 1,
  "f_map": { ... },
  "coboundary_coefficients": [ ... ],
  "metadata": { ... }
}
```

### `f_map` field

The odd linear map f: g → g parametrized by phi_{ij}:
```json
{
  "description": "Odd linear map f: g -> g; f(Z_j) = sum_i phi_ij Z_i",
  "phi_coefficients": {
    "phi_H1_E_eps1_del1_pp": "phi_value",
    "...": "..."
  }
}
```

### `coboundary_coefficients` field

```json
[
  {
    "X": "E_eps1_del1_pp",
    "Y": "E_eps1_del1_mm",
    "Z": "H_1",
    "coeff": "value",
    "formula": "(-1)^p(X) [X, f(Y)] - (-1)^((p(X)+1)*p(Y)) [Y, f(X)] - f([X,Y])"
  }
]
```
