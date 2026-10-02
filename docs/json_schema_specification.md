# C(n+1) Schema 1: Algebra Structure

This document defines the complete Schema 1 field layout for
$C(n+1)=\mathfrak{osp}(2|2n)$, extending the v5.0 structure schema documented
for B(m,n) in `docs/math/B0n_schema_v5.md`. The bosonic rank is $n\geq1$.
Schema version remains `"5.0"`; the family-specific fields below do not alter
existing B(m,n) files.

## File naming

Use `C_{n}_structure.json`, where the index is the bosonic rank:

| Algebra | File |
|---|---|
| C(2) = osp(2\|2) | `C_1_structure.json` |
| C(3) = osp(2\|4) | `C_2_structure.json` |
| C(4) = osp(2\|6) | `C_3_structure.json` |

## Top-level shape

```json
{
  "schema_version": "5.0",
  "algebra": {},
  "oscillator_generators": {},
  "oscillator_relations": {},
  "central_elements": {},
  "basis": {},
  "parity": {},
  "generator_realization": {},
  "structure_constants": [],
  "metadata": {}
}
```

The field definitions below describe the required content; arrays and
generator maps are populated for the selected rank. Generator labels and
their ordering follow `handover/notation.md`.

## `algebra`

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

The sample is C(3), with $n=2$. For every rank, `m` is 1, the even dimension
is $2n^2+n+1$, the odd dimension is $4n$, and the total dimension is
$2n^2+5n+1$. Equivalently, the even part is
$\mathfrak{so}(2)\oplus\mathfrak{sp}(2n)$.

## `oscillator_generators`

```json
{
  "fermions": {
    "m": 1,
    "labels": ["a_1_p", "a_1_m"],
    "parity": 1,
    "description": "Standard fermionic pair a_1^+, a_1^-"
  },
  "bosons": {
    "count": 4,
    "n": 2,
    "labels": ["b_1_p", "b_1_m", "b_2_p", "b_2_m"],
    "parity": 0,
    "description": "Bosonic oscillators b_k^± for k=1,...,n"
  }
}
```

The `fermions` object always has `m: 1` and the two stated labels. The
`bosons.count` is `2*n`, and its labels list `b_k_p, b_k_m` in increasing
index order. There is no `supplementary_fermion` field in this family.

## `oscillator_relations`

```json
{
  "standard_fermion_anticommutators": {
    "description": "Canonical anticommutation relations",
    "relations": {
      "conjugate_pair": "{a_1_m, a_1_p} = 1",
      "same_type": "{a_1_p, a_1_p} = {a_1_m, a_1_m} = 0"
    }
  },
  "bosonic_commutators": {
    "description": "Canonical commutation relations for bosonic oscillators",
    "relations": {
      "same_type": "[b_i^±, b_j^±] = 0 for all i,j",
      "conjugate_pair": "[b_i^-, b_j^+] = δ_ij"
    }
  },
  "mixed_commutators": {
    "description": "Bosons commute with fermions in the undeformed oscillator algebra",
    "boson_fermion": "[b_i^±, a_1^±] = 0"
  }
}
```

The mixed commutator statement applies to every choice of bosonic and
fermionic signs. Deformed mixed relations belong to Schema 2, not this
undeformed Schema 1.

## `central_elements`

This is a required top-level key:

```json
{
  "kappa": {
    "parity": 1,
    "central": true,
    "nilpotent": true,
    "relation": "kappa^2 = 0",
    "description": "Formal odd central element for the nilpotent extension"
  },
  "K": {
    "parity": 0,
    "central": true,
    "relation": "K = 1",
    "description": "Even central identity; identified with the scalar 1"
  }
}
```

`kappa` and `K` are recorded as algebraic metadata, not additional members of
the finite-dimensional $\mathfrak{g}$ basis. In particular, `K` is the
identity and is not included in `basis` or the PBW list. The odd central
extension symbol `kappa` precedes the Lie-superalgebra generators in the
ordering convention.

## `basis` and `parity`

`basis.even` contains, in the order defined in `handover/notation.md`,
`H_1,...,H_{n+1}`, all $2n$ long-root generators `E_2del{k}_p/m`, and all
$4\binom n2$ two-index even-root generators. `basis.odd` contains the $4n$
generators `E_eps1_del{k}_pp/pm/mp/mm`. For example, for C(3):

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
    "E_eps1_del1_pp", "E_eps1_del2_pp",
    "E_eps1_del1_pm", "E_eps1_del2_pm",
    "E_eps1_del1_mp", "E_eps1_del2_mp",
    "E_eps1_del1_mm", "E_eps1_del2_mm"
  ],
  "ordering_convention": "PBW: kappa < [odd roots in listed order] < [even generators in listed order]; K=1 is excluded"
}
```

`parity` is a map containing every basis generator exactly once: each member
of `basis.even` maps to `0`, and each member of `basis.odd` maps to `1`.
Neither `kappa` nor `K` is a basis-generator entry in this map.

## `generator_realization`

Store each generator in `realizations` as oscillator words in PBW order,
using string rational coefficients. Each record has `standard_form`,
`frappat_form`, and `parity`; optional notes may clarify conventions. The
following formulas specify the rank-dependent realizations:

| Generator | Oscillator realization |
|---|---|
| `H_1` | $a_1^+a_1^-+b_1^+b_1^-$ |
| `H_k` ($2\leq k\leq n$) | $b_{k-1}^+b_{k-1}^- - b_k^+b_k^-$ |
| `H_{n+1}` | $-b_n^+b_n^- - \tfrac12$ |
| `E_2del{k}_p` / `E_2del{k}_m` | $\tfrac12(b_k^+)^2$ / $\tfrac12(b_k^-)^2$ |
| `E_del{i}_del{j}_pp` / `E_del{i}_del{j}_mm` | $b_i^+b_j^+$ / $b_i^-b_j^-$ |
| `E_del{i}_del{j}_pm` / `E_del{i}_del{j}_mp` | $b_i^+b_j^-$ / $b_i^-b_j^+$ |
| `E_eps1_del{k}_pp` / `E_eps1_del{k}_pm` | $a_1^+b_k^+$ / $a_1^+b_k^-$ |
| `E_eps1_del{k}_mp` / `E_eps1_del{k}_mm` | $a_1^-b_k^+$ / $a_1^-b_k^-$ |

For instance, a term is encoded as
`{"words": ["a_1_p", "b_1_m"], "coeff": "1"}`; a scalar term is encoded
with an empty `words` array. The ordering field lists the fermions followed
by bosons, for example `"a_1_p, a_1_m, b_1_p, b_1_m, b_2_p, b_2_m"`.

## `structure_constants`

This is an array of nonzero graded brackets in the form
`{"X": "...", "Y": "...", "Z": "...", "coeff": "...", "sign_rule": "graded"}`.
Each record means $[X,Y\}= \mathrm{coeff}\,Z$. Include each independent
nonzero bracket once using the fixed basis, with coefficients evaluated under
the undeformed CAR/CCR relations; derive the complementary order from graded
skew-symmetry. Schema 1 contains no `gb`-dependent terms.

## `metadata`

```json
{
  "generated_by": "build_C_structure_constants.py",
  "generation_date": "YYYY-MM-DD",
  "references": [
    "Frappat et al. (2000), Dictionary on Lie Algebras and Superalgebras",
    "Bakalov and Sullivan (2017)"
  ]
}
```

The date is the actual generation date for a generated data file. Keep
rank-independent references and identify the C-family generator or tool.

## Schema 2: Inhomogeneous Deformation

Schema 2 files are named `C_{n}_gamma.json`, with `n` the bosonic rank. They
reference the corresponding Schema 1 file and preserve its algebra rank and
generator labels.

### `gb_matrix`

```json
{
  "rows": ["a_1_p", "a_1_m"],
  "columns": ["b_1_p", "b_1_m"],
  "shape": [2, 2],
  "parameters": [
    "gb_a_1_p_b_1_p", "gb_a_1_p_b_1_m",
    "gb_a_1_m_b_1_p", "gb_a_1_m_b_1_m"
  ],
  "parity": 1
}
```

For rank $n$, the matrix has shape $2\times2n$ and contains $4n$
parameters, row-major by fermion label and then boson label. Each parameter
names the coefficient in the mixed oscillator relation.

### `inhomogeneous_deformation`

This object contains:

- `kappa`: the odd nilpotent extension symbol and its square-zero relation;
- `relations`: one record per matrix entry, with `fermion`, `boson`,
  `parameter`, and the literal exchange relation
  `[boson, fermion] = -parameter * kappa`;
- `gamma_coefficients`: records with `X`, `Y`, `Z`, `parameter`, and rational
  `coeff`, representing that parameter's contribution to $\gamma(X,Y)$;
- `gamma_convention`: $\left[X,Y\right]_\gamma =
  \left[X,Y\right]_0+\kappa\gamma(X,Y)$.

The gamma records are obtained by normal-ordering the Schema 1 oscillator
realizations with the mixed relation, retaining first-order terms and dropping
terms with $\kappa^2$. `Z` may be a Schema 1 basis generator or `K`, the scalar
identity recorded in `central_elements`. The latter is needed when an exact
first-order correction contains a scalar component.

**Parity caveat**: the source definitions state that both `gb` and `kappa`
are odd while also specifying their product in a mixed commutator between an
even and an odd oscillator. Those statements do not determine a consistent
parity for the right-hand side. The generated coefficients follow the
exchange relation literally as formal first-order symbols; the serialization
does not claim to resolve that parity inconsistency.

## Compatibility with B(m,n)

B(m,n) files retain their existing `"family": "B"` values, supplementary
fermion representation where applicable, basis, and relations. C(n+1) uses
the same v5.0 envelope and the common `basis`, `parity`,
`generator_realization`, `structure_constants`, and `metadata` concepts, but
has its own `"family": "C"` parameterization (`m: 1`), standard `fermions`
pair, four odd-root generators per bosonic index, CAR relations, and required
top-level `central_elements`. Consumers must branch on `algebra.family`
rather than infer oscillator type from the schema version. No B(m,n) key or
meaning is changed by adding this C-specific specification.
