# JSON Schema Specification — C(n+1) = osp(2|2n), v5.0

**Status**: finalized in Issue I02 (2026-10-06).
**Base**: `docs/math/B0n_schema_v5.md` (B(0,n) v5.0).
**Conventions**: `handover/notation.md` (Issue I01).

This document is the **complete, standalone** schema specification for
$C(n+1) = \mathfrak{osp}(2|2n)$. It is not a diff: every field is specified with
its C(n+1) value. Where a field is unchanged from B(0,n) this is stated
explicitly so that compatibility can be audited.

Throughout, `n` is the **bosonic rank**; $C(n+1)$ has Cartan rank $n+1$ and
`n = 1` means $C(2) = \mathfrak{osp}(2|2)$.

---

## 0. Four-layer architecture and file naming

| Layer | File | Contents |
|---|---|---|
| 1 | `data/C_{n}_structure.json` | algebra structure + structure constants |
| 2 | `data/C_{n}_gamma.json` | symbolic inhomogeneous ($\gamma$) deformation |
| 3 | `data/C_{n}_evaluated_{profile}.json` | $\gamma$ with numeric gb values |
| 4 | `data/C_{n}_coboundary.json` | coboundary $\delta f$ data |

Concretely: `C_1_structure.json`, `C_2_structure.json`, `C_3_structure.json`
for $C(2), C(3), C(4)$. **Confirmed** — this is the mandatory unified rule of
I02 and matches `B0n_schema_v5.md` ("For the C(n+1) extension, file naming uses
`C_n_structure.json` … where `n` is the bosonic rank").

---

## 1. Schema 1 — Algebra structure

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

**Difference from B(0,n) v5.0**: exactly one new top-level key,
`central_elements` (mandatory rule of I02). All other top-level keys are
retained with identical names and identical meaning, so a B(0,n) reader that
ignores unknown keys parses a C(n+1) file without modification.

### 1.2 `schema_version`

```json
"schema_version": "5.0"
```

The version is **not** bumped: the C(n+1) extension is additive at the top level
and all changes to existing keys are value-level, not shape-level. (See §4.)

### 1.3 `algebra`

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
  "dimension": { "total": 8, "even": 4, "odd": 4 },
  "dimension_formulas": {
    "even": "2n^2 + n + 1",
    "odd": "4n",
    "total": "2n^2 + 5n + 1"
  },
  "even_subalgebra": "so(2) + sp(2n)",
  "rank": 2
}
```

- `family` is `"C"` (B(0,n) uses `"B"`).
- `m` is **explicitly 1** (B(0,n) uses `m = 0`).
- `cartan_type` is `"C(n+1)"`, i.e. `C(2)`, `C(3)`, `C(4)` for `n = 1, 2, 3`.
- `rank` $= n+1$ is new (B(0,n) rank is $n$); it is additive and optional for
  B readers.
- `dimension_formulas` is new and mandatory per I02.

| `n` | cartan_type | osp | even | odd | total |
|---|---|---|---|---|---|
| 1 | C(2) | osp(2\|2) | 4 | 4 | 8 |
| 2 | C(3) | osp(2\|4) | 11 | 8 | 19 |
| 3 | C(4) | osp(2\|6) | 22 | 12 | 34 |

### 1.4 `oscillator_generators`

Exactly **two** keys, `fermions` and `bosons` (mandatory rule of I02).
The B(0,n) key `supplementary_fermion` is **removed**.

```json
{
  "fermions": {
    "count": 2,
    "m": 1,
    "labels": ["a_1_p", "a_1_m"],
    "type": "standard_CAR_pair",
    "parity": 1,
    "description": "Standard fermionic creation/annihilation pair a_1^+, a_1^- with {a_1^-, a_1^+} = 1. Replaces the B(0,n) supplementary fermion a_0."
  },
  "bosons": {
    "count": 2,
    "n": 1,
    "labels": ["b_1_p", "b_1_m"],
    "type": "standard_CCR_pairs",
    "parity": 0,
    "description": "Bosonic oscillators b_k^± with k = 1,...,n"
  }
}
```

`fermions.count` is $2m = 2$; `bosons.count` is $2n$ with
`labels = ["b_1_p","b_1_m", ..., "b_n_p","b_n_m"]`.

### 1.5 `oscillator_relations`

```json
{
  "standard_fermion_anticommutators": {
    "description": "Canonical anticommutation relations for the standard fermionic pair",
    "relations": {
      "conjugate_pair": "{a_1^-, a_1^+} = 1",
      "same_type": "{a_1^±, a_1^±} = 0, i.e. (a_1^±)^2 = 0"
    }
  },
  "bosonic_commutators": {
    "description": "Canonical commutation relations for bosonic oscillators",
    "relations": {
      "same_type": "[b_k^±, b_l^±] = 0 for all k, l",
      "conjugate_pair": "[b_k^-, b_l^+] = δ_{kl}"
    }
  },
  "mixed_commutators": {
    "boson_fermion": "[b_k^s, a_1^σ] = 0   (undeformed Schema 1; see Schema 2 for the γ-deformed relation)"
  },
  "normal_ordering": {
    "letter_order": ["kappa", "a_1_p", "a_1_m", "b_1_p", "b_1_m"],
    "description": "Index map kappa=0, a_1_p=1, a_1_m=2, b_k_p=2k+1, b_k_m=2k+2"
  }
}
```

**Difference from B(0,n)**: `supplementary_fermion_relation` (`a_0*a_0 = 1/2`)
is replaced by `standard_fermion_anticommutators`. The `bosonic_commutators`
block is byte-for-byte the same shape as B(0,n) (index letter changed $i,j\to k,l$).
`normal_ordering` is new and additive.

### 1.6 `central_elements` *(new top-level key)*

```json
{
  "kappa": {
    "label": "kappa",
    "parity": 1,
    "relations": ["kappa^2 = 0", "kappa X = (-1)^{p(X)} X kappa  (supercentral)"],
    "in_basis": false,
    "description": "Odd central element carrying the inhomogeneous deformation: [X,Y]_γ = [X,Y]_0 + kappa·γ(X,Y)."
  },
  "K": {
    "label": "K",
    "parity": 0,
    "relations": ["K = 1", "[K, X] = 0"],
    "in_basis": false,
    "description": "Even central element (Bakalov–Sullivan). Identified with the scalar 1; excluded from the PBW basis, recorded here for schema completeness."
  }
}
```

`kappa` has **parity 1** and `K` has **parity 0** (mandatory rule of I02).

> **Divergence from `B0n_schema_v5.md` §3, recorded deliberately.** The B(0,n)
> document states "the element $\kappa$ is listed as a central element with
> parity 0 in the `central_elements` key", while `B0n_definition.md` §3 states
> $p(\kappa) = 1$. These contradict each other. I02's mandatory rule fixes
> `kappa` parity 1, which is also the only value consistent with
> $[X,Y]_\gamma = [X,Y]_0 + \kappa\gamma(X,Y)$ preserving total parity. Schema 1
> for C(n+1) therefore uses parity 1 and the B-side statement is treated as an
> erratum.

Neither element appears in `basis` or `parity`; both carry `"in_basis": false`.

### 1.7 `basis`

PBW ordering (Option A of `handover/notation.md` §4):

```
kappa < [odd: E_eps1_del{k}_pp/pm/mp/mm] < [even: H_*, E_2del*_p, E_del*_pp, E_2del*_m, E_del*_mm, E_del*_pm, E_del*_mp]
```

For `n = 1`:

```json
{
  "even": ["H_eps1", "H_del1", "E_2del1_p", "E_2del1_m"],
  "odd":  ["E_eps1_del1_pp", "E_eps1_del1_pm", "E_eps1_del1_mp", "E_eps1_del1_mm"],
  "ordering_convention": "PBW: kappa < [odd] < [even]  (K = 1 is excluded)",
  "pbw_order": ["E_eps1_del1_pp", "E_eps1_del1_pm", "E_eps1_del1_mp", "E_eps1_del1_mm", "H_eps1", "H_del1", "E_2del1_p", "E_2del1_m"]
}
```

`pbw_order` is the single flat list `odd ++ even` and is the canonical index
order used by all structure-constant and matrix data in Layers 2–4.
Full lists for $n = 1,2,3$: `handover/notation.md` §3.

**Difference from B(0,n)**: `basis.odd` holds $4n$ labels
`E_eps1_del{k}_pp/pm/mp/mm` instead of the $2n$ labels `E_del{k}_p/m`;
`basis.even` gains `H_eps1` (the $\mathfrak{so}(2)$ Cartan) and renames
`H_k` $\to$ `H_del{k}` to keep the Cartan labels root-indexed.

### 1.8 `parity`

A flat map label &rarr; 0/1 over `pbw_order`. For `n = 1`:

```json
{
  "E_eps1_del1_pp": 1, "E_eps1_del1_pm": 1,
  "E_eps1_del1_mp": 1, "E_eps1_del1_mm": 1,
  "H_eps1": 0, "H_del1": 0,
  "E_2del1_p": 0, "E_2del1_m": 0
}
```

Shape is identical to B(0,n); only the label set changes.

### 1.9 `generator_realization`

```json
{
  "description": "Standard form with normal-ordered oscillator words",
  "ordering": "a_1_p, a_1_m, b_1_p, b_1_m",
  "realizations": {
    "H_eps1": {
      "standard_form": [
        {"words": ["a_1_p", "a_1_m"], "coeff": "1"},
        {"words": [], "coeff": "-1/2"}
      ],
      "frappat_form": "a_1^+ a_1^- - 1/2",
      "parity": 0,
      "root": "0 (so(2) Cartan)"
    },
    "H_del1": {
      "standard_form": [
        {"words": ["b_1_p", "b_1_m"], "coeff": "1"},
        {"words": [], "coeff": "1/2"}
      ],
      "frappat_form": "b_1^+ b_1^- + 1/2",
      "parity": 0,
      "root": "0 (sp(2n) Cartan)"
    },
    "E_eps1_del1_pp": {
      "standard_form": [{"words": ["a_1_p", "b_1_p"], "coeff": "1"}],
      "frappat_form": "a_1^+ b_1^+",
      "parity": 1,
      "root": "eps + del1"
    }
  }
}
```

Every entry carries `standard_form` (list of `{words, coeff}` with `coeff` a
string-encoded rational), `frappat_form`, `parity`, and — new for C(n+1) — `root`.
The `a_0` letter of B(0,n) never appears; odd generators are quadratic words
`a_1_{p|m}, b_k_{p|m}` rather than B(0,n)'s `a_0, b_k_{p|m}`.

### 1.10 `structure_constants`

A list of non-zero graded brackets $[X,Y\} = \sum_Z c\,Z$:

```json
[
  {"X": "H_eps1", "Y": "E_eps1_del1_pp", "Z": "E_eps1_del1_pp", "coeff": "1", "sign_rule": "graded"}
]
```

Shape is **identical** to B(0,n). Conventions:

- $[X,Y\} = XY - (-1)^{p(X)p(Y)}YX$ computed in $\mathcal U(A)$ with the
  relations of §1.5.
- Only **ordered pairs with `pbw_index(X) <= pbw_index(Y)`** are stored; the
  opposite order is recovered by graded antisymmetry
  $[Y,X\} = -(-1)^{p(X)p(Y)}[X,Y\}$. The file records this in
  `metadata.storage_convention`.
- Entries with `coeff == 0` are omitted.
- `coeff` is a string-encoded rational (`"1"`, `"-4"`, `"1/2"`).
- A `K`-component would be stored with `"Z": "K"`. With the symmetrized Cartan
  normalization of I01 **no such entry ever occurs**; this is asserted by the
  generator and checked in I04.

### 1.11 `metadata`

```json
{
  "generated_by": "src/C_generators.py",
  "generation_date": "2026-10-06",
  "storage_convention": "ordered pairs pbw_index(X) <= pbw_index(Y); graded antisymmetry implied",
  "bracket_convention": "[X,Y} = XY - (-1)^{p(X)p(Y)} YX",
  "cartan_normalization": "symmetrized: H_eps1 = a_1^+a_1^- - 1/2, H_del{k} = b_k^+b_k^- + 1/2",
  "references": [
    "Frappat et al. (2000), Dictionary on Lie Algebras and Superalgebras",
    "Bakalov and Sullivan (2017), arXiv:1612.09400"
  ]
}
```

---

## 2. Schema 2 — Inhomogeneous deformation (summary; detailed in I05)

```json
{
  "schema_version": "5.0",
  "layer": 2,
  "algebra": { ... as Schema 1 ... },
  "gb_matrix": {
    "shape": [2, 2],
    "rows": ["a_1_p", "a_1_m"],
    "cols": ["b_1_p", "b_1_m"],
    "parameters": ["gb_a1P_b1P", "gb_a1P_b1M", "gb_a1M_b1P", "gb_a1M_b1M"],
    "count": 4,
    "defining_relation": "[b_k^s, a_1^σ] = - gb_{σ,k,s} · kappa"
  },
  "inhomogeneous_deformation": {
    "description": "γ with [X,Y]_γ = [X,Y]_0 + kappa·γ(X,Y)",
    "entries": [
      {"X": "...", "Y": "...", "Z": "...", "coeff": "<linear form in gb>"}
    ]
  },
  "metadata": { ... }
}
```

`gb_matrix` has shape $2 \times 2n$ (rows = fermionic label, cols = bosonic
label), i.e. $4n$ parameters.

## 3. Schema 3 / Schema 4 (summary; detailed in I06 / I07)

- **Schema 3** `C_{n}_evaluated_{profile}.json`: same shape as Schema 2 with
  `gb_values` giving the numeric assignment and `coeff` fields reduced to
  rationals; adds `profile` (name of the sign assignment).
- **Schema 4** `C_{n}_coboundary.json`: carries `f_map` (the odd linear map,
  as `phi` coefficients over `pbw_order`) and `coboundary.entries` in the same
  `{X, Y, Z, coeff}` shape, so that Layer 3 and Layer 4 entry lists can be
  compared entry-by-entry in I08.

---

## 4. Compatibility with the B(m,n) schema

| Aspect | Status |
|---|---|
| `schema_version` | unchanged `"5.0"` |
| Top-level key set | B(0,n) keys all retained; `central_elements` **added** |
| `algebra` | same shape; `family`/`m`/`cartan_type`/`dimension` re-valued; `dimension_formulas`, `even_subalgebra`, `rank` added |
| `oscillator_generators` | `supplementary_fermion` **removed**, `fermions` **added**; `bosons` unchanged in shape |
| `oscillator_relations` | `supplementary_fermion_relation` **removed**, `standard_fermion_anticommutators` **added**; `bosonic_commutators`, `mixed_commutators` unchanged in shape |
| `basis` | same shape (`even`, `odd`, `ordering_convention`); `pbw_order` added; labels re-valued |
| `parity` | same shape (flat label &rarr; 0/1) |
| `generator_realization` | same shape (`{words, coeff}` lists); `root` added per entry |
| `structure_constants` | **same shape**, values recomputed under CAR |
| `metadata` | same shape; `storage_convention`, `bracket_convention`, `cartan_normalization` added |

**Compatibility statement.** A consumer written for B(0,n) v5.0 that (i) keys off
`algebra.family` and (ii) ignores unknown keys will read a C(n+1) file correctly:
no existing key changes its type or cardinality, no key is renamed in place, and
the two removals (`supplementary_fermion`, `supplementary_fermion_relation`) are
exactly the two B-specific objects whose mathematical content does not exist in
C(n+1). Code that hard-codes `supplementary_fermion` must branch on
`algebra.family`; this is the single required change and is documented here as
the migration note.

**Discriminator**: `algebra.family` (`"B"` vs `"C"`) together with
`algebra.m` (`0` vs `1`).
