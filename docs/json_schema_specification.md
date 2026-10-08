# C(n+1) JSON Schema Specification

This is the complete Schema 1 specification for
\(C(n+1)=\mathfrak{osp}(2|2n)\), extending the B(0,n) v5.0 data format.
Here \(n\) is the bosonic rank: C(2) is stored as `C_1_structure.json`.
The basis labels and PBW ordering follow `handover/notation.md`.

## Four-layer file map

| Layer | File pattern | Contents |
|---|---|---|
| Schema 1 | `C_{n}_structure.json` | Algebra, oscillator realization, basis, and undeformed brackets |
| Schema 2 | `C_{n}_gamma.json` | Symbolic inhomogeneous-deformation coefficients |
| Schema 3 | `C_{n}_evaluated.json` | Evaluated deformation for a recorded gb assignment |
| Schema 4 | `C_{n}_coboundary.json` | Odd-map coboundary data for triviality comparison |

The `{n}` component is the positive integer bosonic rank (1, 2, or 3 for the
initial datasets). All files are UTF-8 JSON. The scalar identity `K` is not a
basis element.

## Schema 1: algebra structure

Every structure file contains these top-level keys:

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

### `algebra`

```json
{
  "family": "C",
  "m": 1,
  "n": 1,
  "cartan_type": "C(2)",
  "alternative_notation": {
    "osp": "osp(2|2)",
    "dimension_formula": "osp(2m|2n)"
  },
  "dimension": {
    "total": 8,
    "even": 4,
    "odd": 4
  }
}
```

`m` is always 1. The dimensions are even \(2n^2+n+1\), odd \(4n\), total
\(2n^2+5n+1\).

| `n` | `cartan_type` | even | odd | total |
|---:|---|---:|---:|---:|
| 1 | `C(2)` | 4 | 4 | 8 |
| 2 | `C(3)` | 11 | 8 | 19 |
| 3 | `C(4)` | 22 | 12 | 34 |

### `oscillator_generators`

Exactly two generator groups are serialized:

```json
{
  "fermions": {
    "m": 1,
    "count": 2,
    "labels": ["a_1_p", "a_1_m"],
    "parity": 1,
    "description": "One standard fermionic pair a_1^+, a_1^-"
  },
  "bosons": {
    "rank": 1,
    "count": 2,
    "labels": ["b_1_p", "b_1_m"],
    "parity": 0,
    "description": "Bosonic oscillator pairs b_k^+, b_k^- for k=1,...,n"
  }
}
```

The fermion labels are fixed for every rank; boson labels are ordered by
increasing index, with `p` before `m`.

### `oscillator_relations`

```json
{
  "fermion_anticommutators": {
    "description": "Canonical anticommutation relations",
    "relations": {
      "pair": "{a_1_m, a_1_p} = 1",
      "same_type": "{a_1_p, a_1_p} = {a_1_m, a_1_m} = 0"
    }
  },
  "boson_commutators": {
    "description": "Canonical commutation relations",
    "relations": {
      "same_type": "[b_i^s, b_j^s] = 0 for s in {+,-}",
      "conjugate_pair": "[b_i^-, b_j^+] = delta_ij"
    }
  },
  "mixed_commutators": {
    "boson_fermion": "[b_i^s, a_1^t] = 0 in the undeformed algebra"
  }
}
```

### `central_elements`

This is a top-level key, not a member of `oscillator_relations`.
`kappa` is the odd formal deformation parameter; `K` denotes the even scalar
identity. Neither is an independent member of `basis`.

```json
{
  "kappa": {
    "parity": 1,
    "central": true,
    "nilpotent": true,
    "relation": "kappa^2 = 0"
  },
  "K": {
    "parity": 0,
    "central": true,
    "identified_with_scalar": 1
  }
}
```

### `basis` and `parity`

`basis.even` contains, in order, `H_eps`, `H_1` through `H_n`, positive
`E_2del{k}_p`, mixed-root generators sorted by `(i,j)` and sign code `pp`,
`pm`, `mp`, `mm`, then negative `E_2del{k}_m`. `basis.odd` contains, for
each increasing `k`, `E_eps1_del{k}_pp`, `_pm`, `_mp`, `_mm`. These ordering
rules are specified fully in `handover/notation.md`. `ordering_convention`
records the PBW ordering, and the parity map has an entry for every basis
generator (`0` for even, `1` for odd).

For example, when `n=1`, the basis lists are:

```json
{
  "even": ["H_eps", "H_1", "E_2del1_p", "E_2del1_m"],
  "odd": [
    "E_eps1_del1_pp", "E_eps1_del1_pm",
    "E_eps1_del1_mp", "E_eps1_del1_mm"
  ],
  "ordering_convention": "PBW: kappa, then odd block, then even block; K=1 excluded"
}
```

### `generator_realization`

Store each basis generator in `realizations`, with its parity and an ordered
sum of oscillator words:

```json
{
  "description": "Normal-ordered oscillator realization",
  "ordering": ["a_1_p", "a_1_m", "b_1_p", "b_1_m"],
  "realizations": {
    "E_eps1_del1_pp": {
      "standard_form": [
        {"words": ["a_1_p", "b_1_p"], "coeff": "1"}
      ],
      "parity": 1
    }
  }
}
```

`words` are ordered monomials, and rational `coeff` values are strings.
Realizations must account for every name in `basis`; Cartan and root
normalization must be consistent with the root convention and the
`structure_constants`.

### `structure_constants`

This is a list of nonzero undeformed graded brackets:

```json
[
  {
    "X": "H_1",
    "Y": "E_2del1_p",
    "Z": "E_2del1_p",
    "coeff": "2",
    "sign_rule": "graded"
  }
]
```

Each entry represents \([X,Y\}= \mathrm{coeff}\,Z\), with
\([X,Y\}=XY-(-1)^{p(X)p(Y)}YX\). Entries refer only to basis generators;
zero brackets are omitted. Coefficients are exact rational strings.

### `metadata`

`metadata` records `generated_by`, `generation_date` in ISO `YYYY-MM-DD`
format, and a `references` array. A generator must not claim verification or
normalization that has not been checked.

## Compatibility with B(m,n) v5.0

The common keys `schema_version`, `algebra`, `oscillator_generators`,
`oscillator_relations`, `basis`, `parity`, `generator_realization`,
`structure_constants`, and `metadata` retain their purposes and types.
Consumers must branch on `algebra.family`. C data sets `family: "C"` and
`m: 1`, replaces B's `supplementary_fermion` group with the mandatory
`fermions` and `bosons` groups, uses CAR rather than the supplementary
fermion relation, and has \(4n\) odd root generators. It adds the
top-level `central_elements` object; this addition is nonbreaking for
consumers that ignore unknown keys but must be handled by strict validators.
No B basis labels or B dimension formulas may be assumed for family C.

## Later-layer field contract

Schema 2 retains the Schema 1 fields and adds
`inhomogeneous_deformation`, containing `gb_matrix` (two fermion rows and
`2n` boson columns), parameter parity, and sparse `gamma_coefficients`
entries `{X,Y,Z,coeff}`. Schema 3 retains the symbolic deformation and records
the concrete `gb_assignment` and evaluated coefficients. Schema 4 records the
odd map `f` as sparse basis-to-basis coefficients and its sparse
`coboundary_coefficients`; it must identify the coboundary formula used.
Each later layer also records its input Schema 1 file and rank so consistency
can be checked without guessing.
