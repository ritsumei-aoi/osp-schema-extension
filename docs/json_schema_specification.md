# C(n+1) JSON Schema Specification (derived from B(0,n) v5.0)

This document specifies the JSON data for $C(n+1) = \mathfrak{osp}(2|2n)$. It extends the
B(0,n) v5.0 schema in `docs/math/B0n_schema_v5.md`. Schema 1 is defined in full below.
Schemas 2 to 4 are defined in outline and are fixed by Issues I05 to I07.

Conventions follow `handover/notation.md`. Labels, the basis, and the PBW ordering are fixed there.

---

## 0. File naming

| Layer | File | Contents |
|---|---|---|
| Schema 1 | `data/C_{n}_structure.json` | Algebra structure (basis, parity, oscillator realization, structure constants) |
| Schema 2 | `data/C_{n}_gamma.json` | Inhomogeneous deformation $\gamma$, symbolic in gb |
| Schema 3 | `data/C_{n}_evaluated.json` | $\gamma$ evaluated at a representative gb profile |
| Schema 4 | `data/C_{n}_coboundary.json` | Coboundary $\delta f$ for elementary odd maps $f$ |

Here $n$ is the bosonic rank. So $C(2)$ has $n=1$ and uses `C_1_structure.json`.

---

## 1. Schema 1: Algebra structure

### 1.1 Top-level keys

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

`central_elements` is a **top-level key** (not nested in `oscillator_relations`), as fixed by I02.

### 1.2 `algebra`

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
    "odd": 4
  }
}
```

Dimension formulas (C(n+1)): even $= 2n^2+n+1$, odd $= 4n$, total $= 2n^2+5n+1$.

| $n$ | Cartan type | even | odd | total |
|---|---|---|---|---|
| 1 | C(2) | 4 | 4 | 8 |
| 2 | C(3) | 11 | 8 | 19 |
| 3 | C(4) | 22 | 12 | 34 |

`m` is fixed to `1` for every C(n+1) file. The B(0,n) value of `m` is `0`.

### 1.3 `oscillator_generators`

Fermion and boson content. The B(0,n) supplementary fermion `a_0` is **removed**. It is replaced by the standard pair under the `fermions` key.

```json
{
  "fermions": {
    "count": 2,
    "labels": ["a_1_p", "a_1_m"],
    "parity": 1,
    "description": "Standard fermionic pair a_1^+ (a_1_p), a_1^- (a_1_m)"
  },
  "bosons": {
    "count": 2,
    "n": 1,
    "labels": ["b_1_p", "b_1_m"],
    "description": "Bosonic oscillators b_k^± with k=1,...,n; here n=1"
  }
}
```

Mandatory rules: `fermions` has `m=1` (one pair), labels `a_1_p` and `a_1_m`. `bosons` has rank `n`, count `2n`.

### 1.4 `oscillator_relations`

```json
{
  "standard_fermion_anticommutators": {
    "relation": "{a_1^-, a_1^+} = 1",
    "self_relations": "(a_1^±)^2 = 0"
  },
  "bosonic_commutators": {
    "same_type": "[b_i^±, b_j^±] = 0",
    "conjugate_pair": "[b_i^-, b_j^+] = δ_ij"
  },
  "mixed_commutators": {
    "boson_fermion": "[b_k^±, a_1^±] = 0 (undeformed)",
    "deformed": "[b_k^s, a_1^σ] = -gb_{σ,k,s} κ"
  }
}
```

The B(0,n) `supplementary_fermion_relation` (`a_0^2 = 1/2`) is **replaced** by the CAR above.

### 1.5 `central_elements` (top-level)

```json
{
  "kappa": {
    "parity": 1,
    "description": "Odd central element; κ^2 = 0; formal nilpotent deformation parameter"
  },
  "K": {
    "parity": 0,
    "value": 1,
    "description": "Even central element identified with the scalar 1; not a basis element"
  }
}
```

Mandatory: `kappa` has parity 1, `K` has parity 0. Both are at the top level.

### 1.6 `basis`

Ordering: the PBW ordering `κ < [odd] < [even]` chosen in I01 (see `handover/notation.md` §4).

```json
{
  "even": ["H_1", "H_2", "E_2del1_p", "E_2del1_m"],
  "odd": ["E_eps1_del1_pp", "E_eps1_del1_pm", "E_eps1_del1_mp", "E_eps1_del1_mm"],
  "ordering_convention": "PBW: κ < [odd] < [even]; K = 1 excluded from basis"
}
```

For general $n$: even has $2n^2+n+1$ elements, odd has $4n$ elements.

### 1.7 `parity`

Map from every basis label to 0 (even) or 1 (odd). Odd labels are exactly `E_eps1_del{k}_{st}`.

### 1.8 `generator_realization`

Each generator is a list of oscillator words with coefficients (standard form, with the canonical word order `a_1_p, a_1_m, b_1_p, ..., b_n_p, b_1_m, ..., b_n_m`), plus the Frappat form and the parity.

```json
{
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
    "parity": 0,
    "note": "Terminal Cartan; constant term -1/2"
  },
  "E_eps1_del1_pp": {
    "standard_form": [
      {"words": ["a_1_p", "b_1_p"], "coeff": "1"}
    ],
    "frappat_form": "a_1^+ b_1^+",
    "parity": 1
  }
}
```

An empty `words` list denotes the scalar $1$ (identified with $K$).

### 1.9 `structure_constants`

The undeformed bracket $[X,Y]_0$ on basis pairs, stored as a list of nonzero coefficients with the first index not larger than the second in basis order:

```json
[
  {
    "X": "H_1",
    "Y": "E_eps1_del1_pp",
    "Z": "E_eps1_del1_pp",
    "coeff": "1",
    "sign_rule": "super-skew: [Y,X] = -(-1)^{p(X)p(Y)} [X,Y]"
  }
]
```

If a bracket has a nonzero $K$ (constant) component, it is recorded as an extra entry with `"Z": "K"`. Any such entry is a closure failure and must be reported in the I03 Response.

### 1.10 `metadata`

```json
{
  "generated_by": "src/C_generators.py",
  "generation_date": "YYYY-MM-DD",
  "references": [
    "Frappat, Sciarrino, Sorba, Dictionary on Lie Algebras and Superalgebras (2000); arXiv:hep-th/9607161",
    "Bakalov and Sullivan (2017)"
  ]
}
```

---

## 2. Compatibility with the B(0,n) schema

| Key | B(0,n) v5.0 | C(n+1) (this spec) | Change |
|---|---|---|---|
| `schema_version` | `"5.0"` | `"5.0"` | none |
| `algebra.family` | `"B"` | `"C"` | value |
| `algebra.m` | `0` | `1` | value |
| `algebra.dimension` | $2n^2+n$, $2n$, $2n^2+3n$ | $2n^2+n+1$, $4n$, $2n^2+5n+1$ | formula |
| `oscillator_generators` | `supplementary_fermion` (`a_0`) + `bosons` | `fermions` (`a_1_p`, `a_1_m`) + `bosons` | fermion block |
| `oscillator_relations` | `a_0^2 = 1/2` | CAR `{a_1^-,a_1^+}=1` | relation |
| `central_elements` | κ listed with parity 0 (per `B0n_schema_v5.md` §3) | top-level, κ parity 1, K parity 0 | location and parity of κ |
| `basis.odd` | `E_del{k}_p/m` | `E_eps1_del{k}_{st}` | labels |
| `parity` | same rule | same rule | none |
| `generator_realization` | `a_0` in words | `a_1_p`/`a_1_m` in words | oscillator |
| `structure_constants` | same list format | same list format | recompute |
| `metadata` | same keys | same keys | none |

Keys that keep the same meaning: `schema_version`, the list format of `structure_constants`, the `parity` rule, and `metadata`. Keys that change are listed above.

---

## 3. Schemas 2 to 4 (outline)

- **Schema 2, `C_{n}_gamma.json`** (I05): the γ coefficients $\gamma_{XY}^Z$, each a linear form in the $4n$ gb parameters. The gb labels are `gb_a1{σ}_b{k}{s}`.
- **Schema 3, `C_{n}_evaluated.json`** (I06): the same γ, evaluated at a named gb profile, plus the profile itself.
- **Schema 4, `C_{n}_coboundary.json`** (I07): $\delta f$ for each elementary odd map $f$ (sending one basis element to another of opposite parity).
