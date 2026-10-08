# C(n+1) JSON Schema Specification (Schema 1, v5.0 extension)

This document specifies the Schema 1 (algebra structure) JSON for $C(n+1) = \mathfrak{osp}(2|2n)$.
It extends the B(0,n) v5.0 schema (`docs/math/B0n_schema_v5.md`) and is produced by `src/C_structure.py`.

## Top-level keys

```json
{
  "schema_version": "5.0",
  "algebra": {...},
  "oscillator_generators": {...},
  "central_elements": {...},
  "basis": {...},
  "parity": {...},
  "generator_realization": {...},
  "structure_constants": {...},
  "metadata": {...}
}
```

`central_elements` is a new top-level key (it is not nested inside `oscillator_relations`, as required by the mandatory unified rules).

## `algebra`

| Field | Value for C(n+1) |
|---|---|
| `family` | `"C"` |
| `m` | `1` (the fermionic rank; $\mathfrak{osp}(2|2n)$) |
| `n` | bosonic rank $n$ |
| `cartan_type` | `"C(n+1)"` |
| `osp` | `"osp(2|2n)"` |
| `dimension.even` | $2n^2 + n + 1$ |
| `dimension.odd` | $4n$ |
| `dimension.total` | $2n^2 + 5n + 1$ |

Dimension table: $n=1$: $4/4/8$; $n=2$: $11/8/19$; $n=3$: $22/12/34$.

## `oscillator_generators`

```json
{
  "fermions": {"m": 1, "labels": ["a_1_p", "a_1_m"], "parity": 1},
  "bosons": {"rank": n, "labels": ["b_1_p", "b_1_m", "..."], "parity": 0}
}
```

- The supplementary fermion $a_0$ of B(0,n) is removed.
- The key `fermions` replaces `supplementary_fermion`.

## `oscillator_relations`

- `standard_fermion_anticommutators`: $\{a_1^-, a_1^+\} = 1$, $\{a_1^\pm, a_1^\pm\} = 0$.
- `bosonic_commutators`: as in B(0,n), $[b_i^-, b_j^+] = \delta_{ij}$, $[b_i^\pm, b_j^\pm] = 0$.
- `mixed_commutators`: $[b_i^\pm, a_1^\pm] = 0$ in the undeformed algebra. With the inhomogeneous deformation (Schema 2), $[b_j^s, a_1^\sigma] = -\mathrm{gb}[\sigma,j,s]\,\kappa$.

## `central_elements`

```json
{
  "kappa": {"parity": 1, "relation": "kappa^2 = 0"},
  "K": {"parity": 0, "identified_with": 1}
}
```

- $\kappa$ is odd and nilpotent. It is written with parity 1, as in `C_inhomogeneous_definition.md`.
- $K$ is identified with $1$ and is excluded from the basis, consistent with B(0,n). Constant terms in brackets are written in `structure_constants.constant_terms` under $Z = $ `"K"`.

## `basis`

- `ordering`: `"odd first, then even; within each parity by (i,j) index order"`.
- `odd`: the $4n$ labels `W(a1x,bky)`, `W(a1m,bky)`, etc.
- `even`: the $2n^2+n+1$ labels, including `W(a1p,a1m)` for the fermionic Cartan element.
- Labels are `W(x,y)`, the Weyl-symmetrized quadratic in oscillators $x \le y$ (see `handover/notation.md`).

## `parity`

Map from every basis label to 0 or 1. Odd elements are exactly the `W(a_1^±, b_k^±)` pairs.

## `generator_realization`

For each basis label, `standard_form` is the list of oscillator words with rational coefficients (normal-ordered, so the constant from $\{a_1^-,a_1^+\}=1$ appears explicitly). Example:

```json
"W(a1p,a1m)": {"standard_form": [{"words": ["a1p","a1m"], "coeff": "1"}, {"words": [], "coeff": "-1/2"}], "parity": 0}
```

## `structure_constants`

```json
{
  "brackets": [
    {"X": "W(a1p,b1p)", "Y": "W(a1m,b1p)", "Z": "W(b1p,b1p)",
     "coeff": "1", "kappa_coeff": "0"}
  ],
  "constant_terms": []
}
```

- Only nonzero entries are listed. Each ordered pair $(X,Y)$ is listed separately, so antisymmetry is checked explicitly in I04.
- `coeff` is the $\kappa$-free part. `kappa_coeff` is the $\kappa$-linear part, which becomes $\gamma$ in Schema 2.

## `metadata`

`generated_by`, `gb_provided` (true if a deformation was applied), `references` (Frappat et al., arXiv:hep-th/9607161).

## Compatibility with the B(m,n) schema

| Key | B(0,n) (v5.0) | C(n+1) |
|---|---|---|
| `algebra.family` | `B` | `C` |
| `algebra.m` | `0` | `1` |
| `oscillator_generators` | `supplementary_fermion` ($a_0$, $a_0^2 = \tfrac12$) | `fermions` ($a_1^\pm$, CAR) |
| `oscillator_relations` | $a_0^2 = \tfrac12$ | CAR; `central_elements` is a new top-level key |
| `basis` | `E_del{k}_p/m` (odd) | `W(a1x,bky)` (odd, $4n$) |
| `structure_constants` | sign rule `graded` | same; plus `kappa_coeff` and `constant_terms` |

The shared keys (`schema_version`, `algebra`, `basis`, `parity`, `generator_realization`, `structure_constants`, `metadata`) keep the same structure, so a B(0,n) reader can be reused with the fermion-key change.

## File naming

- Schema 1: `data/C_{n}_structure.json`, where $n$ is the bosonic rank ($n=1$ gives $C(2)$).
- Schema 2: `data/C_{n}_gamma.json`. Schema 3: `data/C_{n}_evaluated.json`. Schema 4: `data/C_{n}_coboundary.json`.
