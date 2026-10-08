# C(n+1) JSON Schema Specification (draft, v5.0 layout)

This document specifies the JSON files for $C(n+1)=\mathfrak{osp}(2|2n)$. It is the C(n+1)
counterpart of `docs/math/B0n_schema_v5.md`, produced by applying the changes listed there
and in `docs/math/Cn1_definition.md`. Notation is fixed in `handover/notation.md`.

The schema is **complete and standalone**: every key is populated for $C(n+1)$, not just the changed keys.

## 0. File layout and naming

| Schema | File pattern | Contents |
|---|---|---|
| 1 | `C_{n}_structure.json` | Algebra structure: basis, parity, oscillator realization, structure constants |
| 2 | `C_{n}_gamma.json` | Inhomogeneous deformation $\gamma$ (linear in gb) |
| 3 | `C_{n}_evaluated.json` | $\gamma$ evaluated at a representative gb |
| 4 | `C_{n}_coboundary.json` | Coboundary $\delta f$ of elementary odd maps |

$n$ is the bosonic rank: $C(2)=\mathfrak{osp}(2|2)$ is `C_1_*`, $C(3)$ is `C_2_*`, $C(4)$ is `C_3_*`.

All scalars are exact rationals written as strings, e.g. `"1/2"`, `"-1"`. Coefficients are never floats.

## 1. Schema 1: algebra structure

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

`central_elements` is a **top-level** key (mandatory rule for C(n+1)).

### `algebra`

```json
{
  "family": "C",
  "m": 1,
  "n": 1,
  "cartan_type": "C(n+1)",
  "alternative_notation": {
    "osp": "osp(2|2n)",
    "dimension_formula": "osp(2m|2n) with m=1"
  },
  "dimension": {
    "total": 8,
    "even": 4,
    "odd": 4,
    "formulas": {"even": "2n^2 + n + 1", "odd": "4n", "total": "2n^2 + 5n + 1"}
  }
}
```

Values of `dimension` by $n$: $n=1$: even 4, odd 4, total 8; $n=2$: 11, 8, 19; $n=3$: 22, 12, 34.

### `oscillator_generators`

```json
{
  "fermions": {
    "m": 1,
    "labels": ["a_1_p", "a_1_m"],
    "parity": 1,
    "relation": "{a_1_m, a_1_p} = 1, (a_1_p)^2 = (a_1_m)^2 = 0",
    "description": "Standard fermionic pair (CAR); replaces B(m,n)'s supplementary fermion a_0."
  },
  "bosons": {
    "n": 1,
    "count": 2,
    "labels": ["b_1_p", "b_1_m"],
    "description": "Bosonic oscillators b_i^± with i=1,...,n"
  }
}
```

Mandatory: exactly two keys, `fermions` (with `m: 1`, labels `a_1_p`, `a_1_m`) and `bosons` (with rank `n`).
There is no `supplementary_fermion` key.

### `oscillator_relations`

```json
{
  "standard_fermion_anticommutators": {
    "relation": "{a_1_m, a_1_p} = 1",
    "nilpotency": "(a_1_p)^2 = (a_1_m)^2 = 0"
  },
  "bosonic_commutators": {
    "same_type": "[b_i^±, b_j^±] = 0",
    "conjugate_pair": "[b_i^-, b_j^+] = δ_{ij}"
  },
  "mixed_commutators": {
    "boson_fermion": "[b_j^s, a_1^sigma] = 0 undeformed; deformed: [b_j^s, a_1^sigma] = -gb_{sigma,j,s} * kappa"
  }
}
```

`central_elements` (top-level):

```json
{
  "kappa": {"parity": 1, "relation": "central, kappa^2 = 0", "role": "formal nilpotent parameter of the deformation"},
  "K": {"parity": 0, "relation": "central, identified with the scalar 1", "role": "not a basis element; its components are recorded in Schema 2/3"}
}
```

### `basis`

PBW (C(n+1) convention, decision A in `handover/notation.md` §4):

```json
{
  "even": ["H_1", "H_2", "H_3", "E_2del1_p", "E_2del2_p", "E_del1_del2_pp", "E_2del1_m", "E_2del2_m", "E_del1_del2_mm", "E_del1_del2_pm", "E_del1_del2_mp"],
  "odd": ["E_eps1_del1_pp", "E_eps1_del1_pm", "E_eps1_del1_mp", "E_eps1_del1_mm", "E_eps1_del2_pp", "..."],
  "ordering_convention": "PBW: kappa < [odd] < [even], K excluded. Odd: k-major, then pp, pm, mp, mm. Even: B(0,n) order."
}
```

(The example above is the $n=2$ list. Each file lists its own $n$.)

Labels: `H_k`, `E_2del{k}_{p|m}`, `E_del{i}_del{j}_{pp|pm|mp|mm}` as in the B(0,n) schema; odd labels
`E_eps1_del{k}_{xy}`, where $x$ is the sign of $\varepsilon$ and $y$ the sign of $\delta_k$.

### `parity`

A dict label → 0 (even) or 1 (odd). All `E_eps1_*` labels have value 1, all others 0.

### `generator_realization`

```json
{
  "description": "Oscillator words, normal ordered (fermions left, a_1_p before a_1_m, b_k_p before b_k_m, bosons sorted by k)",
  "ordering": "a_1_p, a_1_m, b_1_p, b_1_m, ...",
  "realizations": {
    "H_1": {
      "standard_form": [
        {"words": ["a_1_p", "a_1_m"], "coeff": "1"},
        {"words": ["b_1_p", "b_1_m"], "coeff": "1"}
      ],
      "parity": 0
    },
    "H_2": {
      "standard_form": [
        {"words": ["b_1_p", "b_1_m"], "coeff": "-1"},
        {"words": [], "coeff": "-1/2"}
      ],
      "parity": 0,
      "note": "Terminal Cartan; the constant -1/2 comes from the bosonic normal ordering"
    },
    "E_eps1_del1_pp": {
      "standard_form": [{"words": ["a_1_p", "b_1_p"], "coeff": "1"}],
      "parity": 1
    }
  }
}
```

Only the realizations for the given $n$ are written; the example shows $n=1$ entries.

### `structure_constants`

```json
[
  {"X": "H_1", "Y": "E_eps1_del1_pp", "Z": "E_eps1_del1_pp", "coeff": "1", "sign_rule": "graded"}
]
```

Each entry is the coefficient of $Z$ in the graded bracket $[X,Y]$ (kappa-free). Every ordered pair with
a non-zero bracket appears once; $[Y,X]$ is listed separately.

### `metadata`

```json
{
  "generated_by": "src/C_generators.py",
  "generation_date": "YYYY-MM-DD",
  "references": [
    "Frappat, Sciarrino, Sorba (2000), Dictionary on Lie Algebras and Superalgebras, arXiv:hep-th/9607161",
    "Bakalov and Sullivan (2017), arXiv:1612.09400"
  ]
}
```

## 2. Compatibility with B(m,n) (B(0,n) = Schema v5.0)

| Key | B(0,n) | C(n+1) |
|---|---|---|
| `algebra.family`, `algebra.m` | `"B"`, `0` | `"C"`, `1` |
| `algebra.dimension` | even $2n^2+n$, odd $2n$ | even $2n^2+n+1$, odd $4n$ |
| `oscillator_generators` | `supplementary_fermion` ($a_0$, $a_0^2=\tfrac12$) and `bosons` | `fermions` ($a_1^\pm$, CAR) and `bosons` |
| `oscillator_relations` | $a_0^2=\tfrac12$ | CAR $\{a_1^-,a_1^+\}=1$; `central_elements` moved to top level |
| `central_elements` | in relations | top-level key with `kappa` (parity 1) and `K` (parity 0) |
| Odd basis | `E_del{k}_p/m` ($2n$) | `E_eps1_del{k}_{pp,pm,mp,mm}` ($4n$) |
| Odd realization | $a_0 b_k^\pm$ | $a_1^{\pm} b_k^{\pm}$ |
| PBW rule | $\kappa<[\text{odd}]<[\text{even}]$ | same rule |
| Structure constants | $a_0$ relations | recomputed with CAR and the deformed mixed relation |

The key set and nesting are the same, so a reader of the B(0,n) file can read the C(n+1) file key by key.

## 3. Schema 2: inhomogeneous deformation $\gamma$

```json
{
  "schema_version": "5.0",
  "algebra_ref": "C_1_structure.json",
  "gb_matrix": {
    "shape": [2, "2n"],
    "rows": ["+", "-"],
    "columns": ["b_1_p", "b_1_m", "..."],
    "labels": ["gb_a1p_b1p", "gb_a1p_b1m", "gb_a1m_b1p", "gb_a1m_b1m", "..."],
    "parity": 0,
    "note": "Commuting scalars (decision A1 in notation.md §8)"
  },
  "inhomogeneous_deformation": {
    "kappa_parity": 1,
    "linear_in_gb": true,
    "entries": [{"X": "...", "Y": "...", "Z": "...", "gb": "gb_a1p_b1p", "coeff": "1"}],
    "K_components": [{"X": "...", "Y": "...", "gb": "gb_a1p_b1p", "coeff": "1/2"}]
  },
  "metadata": {"generated_by": "src/C_gamma.py"}
}
```

`entries` gives the g-valued $\gamma$: the coefficient of $\kappa\cdot\mathrm{gb}\cdot Z$ in $[X,Y]_\gamma$.
`K_components` gives the coefficient of $\kappa\cdot\mathrm{gb}\cdot K$ (K = identity).

## 4. Schema 3: evaluated structure

```json
{
  "schema_version": "5.0",
  "algebra_ref": "C_1_structure.json",
  "gb_values": {"gb_a1p_b1p": "1", "...": "..."},
  "representative_rule": "all gb = 1",
  "structure_constants": [
    {"X": "...", "Y": "...", "Z": "...", "coeff_kappa0": "...", "coeff_kappa1": "..."}
  ],
  "K_components": [{"X": "...", "Y": "...", "coeff_kappa1": "..."}],
  "metadata": {"generated_by": "src/C_evaluated.py"}
}
```

## 5. Schema 4: coboundary data

For each elementary odd map $f_{ij}$ ($f_{ij}(X_j)=X_i$, all other basis vectors to $0$, parity-reversing pairs only):

```json
{
  "schema_version": "5.0",
  "algebra_ref": "C_1_structure.json",
  "map_convention": "f(X_j) = X_i, other basis elements to 0; p(X_i) != p(X_j)",
  "delta_convention": "(delta f)(X,Y) = (-1)^{p(X)} [X,f(Y)] - (-1)^{(p(X)+1)p(Y)} [Y,f(X)] - f([X,Y])",
  "maps": [
    {"i": "E_eps1_del1_pp", "j": "H_1", "coboundary": [{"X": "...", "Y": "...", "Z": "...", "coeff": "..."}]}
  ],
  "metadata": {"generated_by": "src/C_coboundary.py"}
}
```

The general odd map is $f=\sum\phi_{ij}f_{ij}$, so the coboundary is $\sum\phi_{ij}\,\delta f_{ij}$.
