# JSON Schema Specification for C(n+1) = osp(2|2n)  (schema_version 5.0, C extension)

This document is the complete, standalone specification of the JSON data produced for
$C(n+1)=\mathfrak{osp}(2|2n)$ in this repository. It extends the B(0,n) v5.0 schema
(`docs/math/B0n_schema_v5.md`). Conventions (labels, ordering, brackets) are those of
`handover/notation.md`.

Files are named by the **bosonic rank** $n$:

| Layer | File | Produced by | Issue |
|---|---|---|---|
| 1 | `data/C_{n}_structure.json` | `src/C_generators.py` | I03 |
| 2 | `data/C_{n}_gamma.json` | `src/C_gamma.py` | I05 |
| 3 | `data/C_{n}_evaluated.json` (default profile) and `data/C_{n}_evaluated_{profile}.json` | `src/C_evaluate.py` | I06 |
| 4 | `data/C_{n}_coboundary.json` (symbolic) and `data/C_{n}_coboundary_{profile}.json` | `src/C_coboundary.py` | I07 |

`n = 1, 2, 3` are generated (C(2), C(3), C(4)). All numbers are stored as **exact rational strings**
(`"1"`, `"-1/2"`), never floats.

---

## Schema 1: Algebra structure (`C_{n}_structure.json`)

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

Compared with B(0,n): one new top-level key `central_elements`; all other keys keep their
B(0,n) names and types (backward compatibility, see §"Compatibility" below).

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
  "dimension_formula": {
    "even": "2n^2 + n + 1",
    "odd": "4n",
    "total": "2n^2 + 5n + 1"
  },
  "dimension": { "total": 19, "even": 11, "odd": 8 },
  "even_subalgebra": "so(2) + sp(2n)",
  "rank": 3
}
```

| $n$ | even | odd | total | Cartan type |
|---|---|---|---|---|
| 1 | 4 | 4 | 8 | C(2) |
| 2 | 11 | 8 | 19 | C(3) |
| 3 | 22 | 12 | 34 | C(4) |

`rank` $= n+1$ (number of Cartan generators `H_1..H_{n+1}`). `cartan_type` is `C(n+1)`.

### `oscillator_generators`

```json
{
  "fermions": {
    "m": 1,
    "count": 2,
    "labels": ["a_1_p", "a_1_m"],
    "parity": 1,
    "description": "Standard fermionic pair a_1^± (CAR)"
  },
  "bosons": {
    "n": 2,
    "count": 4,
    "labels": ["b_1_p", "b_1_m", "b_2_p", "b_2_m"],
    "parity": 0,
    "description": "Bosonic oscillators b_i^± with i=1,...,n (CCR)"
  }
}
```

No `supplementary_fermion` key.

### `oscillator_relations`

```json
{
  "standard_fermion_anticommutators": {
    "description": "Canonical anticommutation relations for the fermionic pair",
    "relations": {
      "conjugate_pair": "{a_1^-, a_1^+} = 1",
      "same_type": "{a_1^±, a_1^±} = 0  (i.e. (a_1^±)^2 = 0)"
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
    "boson_fermion": "[b_i^±, a_1^±] = 0  (undeformed; deformed to -gb·kappa in Schema 2)"
  }
}
```

### `central_elements` (top-level, new)

```json
{
  "K": {
    "parity": 0,
    "relation": "K = 1 (even central identity; excluded from basis and PBW ordering)",
    "in_basis": false
  },
  "kappa": {
    "parity": 1,
    "relation": "kappa^2 = 0; kappa x = (-1)^{p(x)} x kappa (supercentral)",
    "in_basis": false,
    "pbw_position": "first (kappa < odd < even)",
    "description": "Odd nilpotent central element carrying the inhomogeneous deformation (Schema 2)"
  }
}
```

Note: for C(n+1) `kappa` carries parity **1** (the I02 mandatory rule), unlike the B(0,n) v5.0
remark that listed it with parity 0.

### `basis`

```json
{
  "even": ["H_1", "H_2", "H_3", "E_2del1_p", "E_2del2_p", "E_del1_del2_pp",
           "E_2del1_m", "E_2del2_m", "E_del1_del2_mm", "E_del1_del2_pm", "E_del1_del2_mp"],
  "odd":  ["E_eps1_del1_pp", "E_eps1_del2_pp", "E_eps1_del1_pm", "E_eps1_del2_pm",
           "E_eps1_del1_mp", "E_eps1_del2_mp", "E_eps1_del1_mm", "E_eps1_del2_mm"],
  "ordering_convention": "PBW: kappa < [odd] < [even]  (K = 1 is excluded)",
  "pbw_order": ["E_eps1_del1_pp", "...", "E_del1_del2_mp"]
}
```

`pbw_order` is the concatenation `odd + even` and is the index order used by every matrix-valued
computation (I04, I07, I08). The lists for $n=1,2,3$ are in `handover/notation.md` §3.

### `parity`

Map from every basis label to `0` or `1`. Odd labels are exactly the `E_eps1_del{k}_{..}` ones.

### `generator_realization`

```json
{
  "description": "Standard form: sum of normally ordered oscillator words with rational coefficients",
  "ordering": "a_1_p, a_1_m, b_1_p, b_1_m, b_2_p, b_2_m",
  "realizations": {
    "H_1": {
      "standard_form": [
        {"words": ["a_1_p", "a_1_m"], "coeff": "1"},
        {"words": ["b_1_p", "b_1_m"], "coeff": "1"}
      ],
      "frappat_form": "a_1^+ a_1^- + b_1^+ b_1^-",
      "root": null,
      "parity": 0
    },
    "H_3": {
      "standard_form": [
        {"words": ["b_2_p", "b_2_m"], "coeff": "-1"},
        {"words": [], "coeff": "-1/2"}
      ],
      "frappat_form": "-b_2^+ b_2^- - 1/2",
      "root": null,
      "parity": 0,
      "note": "Terminal Cartan; constant -1/2 makes it the super-symmetrised quadratic -(b_2^+b_2^- + 1/2)"
    },
    "E_eps1_del1_pm": {
      "standard_form": [{"words": ["a_1_p", "b_1_m"], "coeff": "1"}],
      "frappat_form": "a_1^+ b_1^-",
      "root": "eps1 - del1",
      "root_vector": [1, -1, 0],
      "parity": 1
    }
  }
}
```

`root_vector` is the coordinate vector in the ordered basis $(\varepsilon, \delta_1,\dots,\delta_n)$;
it is `null` for Cartan generators. Full list of realizations:

| Label | Realization |
|---|---|
| `H_1` | $a_1^+a_1^- + b_1^+b_1^-$ |
| `H_k`, $2\le k\le n$ | $b_{k-1}^+b_{k-1}^- - b_k^+b_k^-$ |
| `H_{n+1}` | $-b_n^+b_n^- - \tfrac12$ |
| `E_2del{k}_p/m` | $(b_k^\pm)^2$ |
| `E_del{i}_del{j}_{st}` | $b_i^s b_j^t$ |
| `E_eps1_del{k}_{σs}` | $a_1^\sigma b_k^s$ |

### `structure_constants`

List of all non-zero graded brackets $[X,Y\} = \sum_Z c\,Z$ for **all ordered pairs** $(X,Y)$:

```json
[
  {"X": "E_eps1_del1_pm", "Y": "E_eps1_del1_mp", "Z": "H_1", "coeff": "1", "sign_rule": "graded"},
  {"X": "E_2del1_p", "Y": "E_2del1_m", "Z": "H_2", "coeff": "4", "sign_rule": "graded"}
]
```

* `sign_rule: "graded"` means $[X,Y\} = XY - (-1)^{p(X)p(Y)}YX$ (anticommutator for two odd elements).
* Entries are ordered by `(pbw_index(X), pbw_index(Y), pbw_index(Z))`.
* The bracket of two basis elements never contains a constant ($K$) term; this is asserted by the generator.

### `metadata`

```json
{
  "generated_by": "src/C_generators.py",
  "generation_date": "YYYY-MM-DD",
  "notation": "handover/notation.md",
  "references": [
    "Frappat, Sciarrino, Sorba (2000), Dictionary on Lie Algebras and Superalgebras; arXiv:hep-th/9607161",
    "Bakalov and Sullivan (2017), arXiv:1612.09400"
  ]
}
```

---

## Schema 2: γ-structure (`C_{n}_gamma.json`)

```json
{
  "schema_version": "5.0",
  "layer": 2,
  "algebra": { "family": "C", "m": 1, "n": 2, "cartan_type": "C(3)" },
  "source_structure": "C_2_structure.json",
  "inhomogeneous_deformation": {
    "description": "[b_j^s, a_1^sigma] = -gb_{sigma,j,s} kappa ; [X,Y}_gamma = [X,Y}_0 + kappa * gamma(X,Y)",
    "kappa": {"parity": 1, "nilpotent": true, "supercentral": true, "position": "left"},
    "gb_matrix": {
      "shape": [2, 4],
      "rows": ["a_1_p", "a_1_m"],
      "columns": ["b_1_p", "b_1_m", "b_2_p", "b_2_m"],
      "entries": [["gb_a_1_p_b_1_p", "gb_a_1_p_b_1_m", "gb_a_1_p_b_2_p", "gb_a_1_p_b_2_m"],
                  ["gb_a_1_m_b_1_p", "gb_a_1_m_b_1_m", "gb_a_1_m_b_2_p", "gb_a_1_m_b_2_m"]],
      "parameter_count": 8,
      "parameter_parity_note": "scalars; the odd parity of the deformation is carried by kappa"
    },
    "deformed_oscillator_relations": [
      {"relation": "[b_1_p, a_1_p] = -gb_a_1_p_b_1_p * kappa"}
    ],
    "gamma_parity_rule": "p(gamma(X,Y)) = p(X) + p(Y) + 1 (mod 2); constant (K) terms dropped",
    "gamma": [
      {"X": "E_eps1_del1_pm", "Y": "E_2del1_p", "Z": "H_2",
       "coeff": {"gb_a_1_p_b_1_p": "-2"}, "expr": "-2*gb_a_1_p_b_1_p"}
    ]
  },
  "metadata": { ... }
}
```

`gamma[*].coeff` is a **linear form** in the gb parameters (dictionary parameter → rational string).
All ordered pairs $(X,Y)$ with non-zero $\gamma$ are listed.

---

## Schema 3: Evaluated structure (`C_{n}_evaluated.json`, `C_{n}_evaluated_{profile}.json`)

```json
{
  "schema_version": "5.0",
  "layer": 3,
  "algebra": { ... },
  "source_gamma": "C_2_gamma.json",
  "gb_profile": {
    "name": "all_plus",
    "values": {"gb_a_1_p_b_1_p": "1", "gb_a_1_p_b_1_m": "1", "...": "..."},
    "matrix": [["1","1","1","1"],["1","1","1","1"]]
  },
  "evaluated_gamma": [
    {"X": "E_eps1_del1_pm", "Y": "E_2del1_p", "Z": "H_2", "coeff": "-2"}
  ],
  "evaluated_structure_constants": [
    {"X": "...", "Y": "...", "Z": "...", "coeff": "...", "kappa_coeff": "..."}
  ],
  "metadata": { ... }
}
```

`evaluated_gamma` lists the numeric $\gamma$ coefficients; `evaluated_structure_constants` merges
Layer 1 and the evaluated $\gamma$: each triple $(X,Y,Z)$ carries the undeformed coefficient
(`coeff`) and the coefficient of $\kappa Z$ (`kappa_coeff`), either of which may be `"0"`.
The default file `C_{n}_evaluated.json` uses the profile `all_plus`.

---

## Schema 4: Coboundary structure (`C_{n}_coboundary.json`, `C_{n}_coboundary_{profile}.json`)

```json
{
  "schema_version": "5.0",
  "layer": 4,
  "algebra": { ... },
  "source_structure": "C_2_structure.json",
  "coboundary_definition": "(delta f)(X,Y) = (-1)^{p(X)}[X,f(Y)} - (-1)^{(p(X)+1)p(Y)}[Y,f(X)} - f([X,Y})",
  "odd_map_f": {
    "description": "...",
    "parity": "odd (parity-reversing)",
    "parameterization": "f(Z_j) = sum_i phi_ij Z_i",
    "phi": [
      {"j": "E_eps1_del1_pm", "i": "H_2", "coeff": {"gb_a_1_p_b_1_p": "-1"}, "expr": "-gb_a_1_p_b_1_p"}
    ]
  },
  "delta_f": [
    {"X": "...", "Y": "...", "Z": "...", "coeff": {"gb_...": "..."}, "expr": "..."}
  ],
  "metadata": { ... }
}
```

In the profile files the `coeff` fields are rational strings instead of linear forms.

---

## Compatibility with the B(m,n) schema

* Same top-level keys and value types as B(0,n) v5.0, plus the new top-level `central_elements`.
  A B(0,n) reader that ignores unknown keys can read the C files.
* `algebra.family` distinguishes the families; `algebra.m = 1` for C, `0` for B(0,n).
* `oscillator_generators.bosons` is identical in shape to B(0,n). The fermionic sector is under
  `fermions` (standard pair) instead of `supplementary_fermion`; readers must branch on which key exists.
* `oscillator_relations`: `bosonic_commutators` and `mixed_commutators` keep their B(0,n) shape;
  `standard_fermion_anticommutators` replaces `supplementary_fermion_relation`.
* `basis`, `parity`, `generator_realization`, `structure_constants`, `metadata`: identical shapes.
  `basis.pbw_order` and `generator_realization.realizations[*].root/root_vector` are additive fields.
* B(0,n) listed `kappa` with parity 0 in `central_elements` "for schema completeness"; here it has
  parity 1, matching the mathematics (`C_inhomogeneous_definition.md`) and the I02 mandatory rule.
