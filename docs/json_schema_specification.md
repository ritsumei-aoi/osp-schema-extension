# C(n+1) JSON Schema Specification

This document specifies the C(n+1) = osp(2|2n) extension of the v5.0
B(m,n) structure schema. It describes Schema 1, the algebra structure
file. The field layout follows the established B(m,n) schema wherever
possible; C-specific oscillator and central-extension data are explicit.

## File naming

Use `C_{n}_structure.json`, with `n` denoting bosonic rank: C(2) =
osp(2|2) uses `C_1_structure.json`, C(3) uses `C_2_structure.json`, etc.

## Top-level object

Each Schema 1 file has these required top-level keys:

| Key | Contents |
|---|---|
| `schema_version` | String `"5.0"` |
| `algebra` | Family, rank, notation, and dimensions |
| `oscillator_generators` | The standard fermion pair and bosons |
| `oscillator_relations` | CAR, CCR, and mixed relations |
| `central_elements` | Formal extension symbols `kappa` and `K` |
| `basis` | Even and odd Lie-superalgebra basis generators and ordering |
| `parity` | Parity of every basis generator |
| `generator_realization` | Oscillator-word realization of every basis generator |
| `structure_constants` | List of nonzero graded brackets |
| `metadata` | Generation and reference information |

## Field definitions

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
    "odd": 8,
    "even_formula": "2n^2 + n + 1",
    "odd_formula": "4n",
    "total_formula": "2n^2 + 5n + 1"
  }
}
```

The mandatory `m` value is 1. Compute dimensions from the formulas for
the selected `n`; the example is the n=2 instance.

### `oscillator_generators`

This object has exactly the `fermions` and `bosons` generator groups.

```json
{
  "fermions": {
    "m": 1,
    "labels": ["a_1_p", "a_1_m"],
    "parity": 1,
    "description": "Standard fermionic pair a_1^+, a_1^-"
  },
  "bosons": {
    "rank": 2,
    "count": 4,
    "labels": ["b_1_p", "b_1_m", "b_2_p", "b_2_m"],
    "parity": 0,
    "description": "Bosonic oscillators b_k^+, b_k^- for k=1,...,n"
  }
}
```

The fermion labels encode $a_1^+$ and $a_1^-$, respectively. Boson labels
encode $b_k^+$ and $b_k^-$.

### `oscillator_relations`

```json
{
  "standard_fermion_anticommutators": {
    "description": "Canonical anticommutation relation",
    "relations": {
      "conjugate_pair": "{a_1_m, a_1_p} = 1",
      "same_type": "{a_1_p, a_1_p} = {a_1_m, a_1_m} = 0"
    }
  },
  "bosonic_commutators": {
    "description": "Canonical commutation relations",
    "relations": {
      "same_type": "[b_i^±, b_j^±] = 0",
      "conjugate_pair": "[b_i^-, b_j^+] = δ_ij"
    }
  },
  "mixed_commutators": {
    "fermion_boson": "[a_1^±, b_j^±] = 0"
  }
}
```

In a deformed Schema 2 instance the mixed relation may be augmented by
the specified inhomogeneous term; Schema 1 records the undeformed CCR/CAR.

### `central_elements`

`central_elements` is a required top-level object, not a member of
`oscillator_relations`.

```json
{
  "kappa": {
    "parity": 1,
    "central": true,
    "nilpotent": true,
    "relation": "kappa^2 = 0",
    "description": "Formal odd central symbol for the inhomogeneous extension"
  },
  "K": {
    "parity": 0,
    "central": true,
    "relation": "K = 1",
    "description": "Even central identity; scalar identity, not an independent basis element"
  }
}
```

Neither symbol is included in the `basis.even` or `basis.odd` Lie
superalgebra lists. `kappa` is extension metadata and may occur in
deformation data; `K` is identified with the scalar identity.

### `basis`

The basis contains every noncentral Lie-superalgebra generator exactly
once. Use the conventions in `handover/notation.md`: Cartan generators
are `H_1` through `H_{n+1}`; even root generators use the `E_2del...`
and `E_del...` labels; odd root generators use all four
`E_eps1_del{k}_{pp,pm,mp,mm}` labels for each `k`.

```json
{
  "even": [
    "H_1", "H_2", "H_3",
    "E_2del1_p", "E_2del2_p",
    "E_del1_del2_pp", "E_del1_del2_pm",
    "E_2del1_m", "E_2del2_m",
    "E_del1_del2_mm", "E_del1_del2_mp"
  ],
  "odd": [
    "E_eps1_del1_pp", "E_eps1_del1_pm",
    "E_eps1_del1_mp", "E_eps1_del1_mm",
    "E_eps1_del2_pp", "E_eps1_del2_pm",
    "E_eps1_del2_mp", "E_eps1_del2_mm"
  ],
  "ordering_convention": "PBW: odd generators in listed order < even generators in listed order; kappa precedes both blocks when used; K=1 excluded"
}
```

The example is C(3), with dimensions 11 even and 8 odd. For other ranks,
populate the root generators using the same index and suffix rules.
Counts must be $2n^2+n+1$ even and $4n$ odd.

### `parity`

This is an object mapping every identifier in `basis.even` and
`basis.odd` to 0 and 1, respectively. No central-element or oscillator
identifier belongs in this map. For example:

```json
{
  "H_1": 0,
  "E_2del1_p": 0,
  "E_del1_del2_pm": 0,
  "E_eps1_del1_pp": 1,
  "E_eps1_del1_mm": 1
}
```

### `generator_realization`

`ordering` records the oscillator PBW word order, beginning with
`a_1_p`, `a_1_m`, then `b_1_p`, `b_1_m` through `b_n_p`, `b_n_m`.
`realizations` maps every basis identifier to an object with a
`standard_form` array of `{ "words": [...], "coeff": "..." }` terms,
its display `frappat_form`, and its parity. Coefficients are strings
representing exact rational numbers.

Use these realizations (with empty `words` for scalar terms):

| Generators | Standard realization |
|---|---|
| `H_1` | `a_1_p a_1_m + b_1_p b_1_m` |
| `H_k`, `2 <= k <= n` | `b_{k-1}_p b_{k-1}_m - b_k_p b_k_m` |
| `H_{n+1}` | `-b_n_p b_n_m - 1/2` |
| `E_2del{k}_p/m` | `(b_k_p)^2` / `(b_k_m)^2` |
| `E_del{i}_del{j}_pp/pm/mp/mm` | `b_i^+ b_j^+`, `b_i^+ b_j^-`, `b_i^- b_j^+`, `b_i^- b_j^-` |
| `E_eps1_del{k}_pp/pm/mp/mm` | `a_1^+b_k^+`, `a_1^+b_k^-`, `a_1^-b_k^+`, `a_1^-b_k^-` |

Use oscillator labels in `standard_form` word arrays. The all-root
normalization above follows the all-root formulas in
`docs/math/Cn1_definition.md`; the simple-root terminal generators in
that reference may use a factor of $1/2$ and must not silently replace
the stated schema-wide normalization.

### `structure_constants`

Store each nonzero graded bracket as an object:

```json
{
  "X": "H_1",
  "Y": "E_eps1_del1_pp",
  "Z": "E_eps1_del1_pp",
  "coeff": "2",
  "sign_rule": "graded"
}
```

The array contains the complete nonzero brackets for the selected rank,
computed from the listed oscillator realizations and undeformed CAR/CCR.
Use exact coefficient strings and the bracket convention
$[X,Y\}=XY-(-1)^{p(X)p(Y)}YX$. Do not insert zero brackets or infer
unlisted nonzero brackets from a B(m,n) instance. Store one representative
for each unordered basis pair, with `X` no later than `Y` in the
`basis.odd`-then-`basis.even` PBW block order. The reverse orientation is
determined by graded skew-symmetry:
$[Y,X\}=-(-1)^{p(X)p(Y)}[X,Y\}$.

### `metadata`

```json
{
  "generated_by": "build_C_structure_constants.py",
  "generation_date": "YYYY-MM-DD",
  "references": [
    "Frappat et al. (2000), Dictionary on Lie Algebras and Superalgebras",
    "docs/math/Cn1_definition.md",
    "docs/math/B0n_schema_v5.md"
  ]
}
```

## Compatibility with B(m,n)

The v5.0 `schema_version` and the common keys `algebra`, `basis`,
`parity`, `generator_realization`, `structure_constants`, and `metadata`
retain their roles, allowing readers to reuse the common structural
parsers. A C(n+1) consumer must additionally handle
`oscillator_generators.fermions`, the standard fermion CAR,
`central_elements`, the $n+1$ Cartan elements, and the four odd roots per
bosonic index. The B(0,n)-specific `supplementary_fermion` and
`supplementary_fermion_relation` keys are not used. Do not interpret the
C family as B(m,n) with a changed display name: its dimensions, roots,
and odd generators differ.

## Schema 2: Inhomogeneous Deformation

Schema 2 files are named `C_{n}_gamma.json` and refer to their
corresponding Schema 1 file through `source_schema`. They retain
`schema_version` and `algebra`, and contain:

| Key | Contents |
|---|---|
| `source_schema` | Matching `C_{n}_structure.json` filename |
| `consistency` | Source filename and count of verified undeformed basis pairs |
| `gb_matrix` | 2-by-2n parameter indexing |
| `inhomogeneous_deformation` | Exchange relations, parity, central element, and gamma terms |
| `metadata` | Generator, date, and references |

`gb_matrix.rows` is ordered `a_1_p`, `a_1_m`; `columns` is ordered
`b_1_p`, `b_1_m`, through `b_n_p`, `b_n_m`. The row-major parameter list
contains `gb_a1_{p|m}_b{k}_{p|m}` exactly once per matrix cell, each with
parity 1. The exchange-relation list specifies
`[b_k_s, a_1_sigma] = -gb_a1_sigma_bk_s * kappa` for every cell.

Each `gamma_coefficients` entry has `X`, `Y`, `Z`, `parameter`, and exact
rational `coeff` fields. It contributes `coeff * parameter * Z` to the
gamma value for that canonical unordered pair `(X,Y)`; the full deformed
bracket adds this contribution with the formal central `kappa`. Reversed
pairs follow graded skew-symmetry. `Z` is a Schema 1 basis label or `K`
when the oscillator calculation yields a scalar identity term; `K=1`
remains excluded from the independent Lie-algebra basis. Each listed
coefficient must have parity consistent with the odd parameter.

Schema 2 generation checks every canonical basis pair against the
undeformed structure constants in its source Schema 1 file and fails if
the bases or brackets differ.
