# JSON Schema Specification for C(n+1) = osp(2|2n) (v5.0, C-extension)

This document is the complete, standalone specification of the JSON data produced for
$C(n+1)=\mathfrak{osp}(2|2n)$. It extends the $B(0,n)$ v5.0 schema
(`docs/math/B0n_schema_v5.md`); every key of the base schema is present with its C(n+1)
meaning, and the differences from $B(0,n)$ are listed in §6. Conventions (labels, PBW
ordering) follow `handover/notation.md`.

The data are organized in four layers:

| Layer | File | Produced by | Contents |
|---|---|---|---|
| Schema 1 | `data/C_{n}_structure.json` | `src/C_generators.py` | basis, parity, oscillator realization, structure constants |
| Schema 2 | `data/C_{n}_gamma.json` | `src/C_gamma.py` | inhomogeneous deformation: gb matrix, symbolic $\gamma_{abc}$ |
| Schema 3 | `data/C_{n}_evaluated.json` (and `C_{n}_evaluated_<profile>.json`) | `src/C_evaluate.py` | $\gamma_{abc}$ with concrete gb values |
| Schema 4 | `data/C_{n}_coboundary.json` | `src/C_coboundary.py` | odd map $f$, coboundary $(\delta f)_{abc}$ |

**File naming** (fixed rule): `C_{n}_<layer>.json` where **`n` is the bosonic rank**.
`C_1_structure.json` is $C(2)=\mathfrak{osp}(2|2)$, `C_2_*` is $C(3)=\mathfrak{osp}(2|4)$,
`C_3_*` is $C(4)=\mathfrak{osp}(2|6)$.

**Number encoding**: all coefficients are exact rationals written as strings
(`"1"`, `"-1/2"`). Symbolic coefficients (Schemas 2 and 4) are linear forms encoded as
objects `{"<symbol>": "<rational>"}` (see §2.4) together with a human-readable `expr` string.

---

## 1. Schema 1: `C_{n}_structure.json`

### 1.1 Top-level keys

```json
{
  "schema_version": "5.0",
  "schema_layer": 1,
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

`schema_layer` is new (integer 1–4) and identifies the layer; readers of the B(0,n) schema
may ignore it.

### 1.2 `algebra`

```json
"algebra": {
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
    "formulas": {
      "even": "2n^2 + n + 1",
      "odd": "4n",
      "total": "2n^2 + 5n + 1"
    }
  },
  "even_subalgebra": "so(2) + sp(2n)",
  "rank": 3
}
```

* `family` = `"C"`, `m` = 1 always, `n` = bosonic rank, `cartan_type` = `"C(n+1)"`.
* `dimension.formulas` is new and mandatory: `even: 2n^2 + n + 1`, `odd: 4n`.
* `rank` = $n+1$ (number of Cartan generators `H_1..H_{n+1}`).

| $n$ | even | odd | total | cartan_type |
|---|---|---|---|---|
| 1 | 4 | 4 | 8 | C(2) |
| 2 | 11 | 8 | 19 | C(3) |
| 3 | 22 | 12 | 34 | C(4) |

### 1.3 `oscillator_generators`

Two keys, `fermions` and `bosons` (the B(0,n) `supplementary_fermion` key is removed).

```json
"oscillator_generators": {
  "fermions": {
    "m": 1,
    "count": 2,
    "labels": ["a_1_p", "a_1_m"],
    "parity": 1,
    "description": "Standard fermionic pair a_1^± (CAR); replaces B(0,n)'s supplementary fermion a_0."
  },
  "bosons": {
    "n": 2,
    "count": 4,
    "labels": ["b_1_p", "b_1_m", "b_2_p", "b_2_m"],
    "parity": 0,
    "description": "Bosonic oscillators b_k^± (CCR), k = 1..n."
  }
}
```

### 1.4 `oscillator_relations`

```json
"oscillator_relations": {
  "standard_fermion_anticommutators": {
    "description": "Canonical anticommutation relations for the standard pair a_1^±",
    "relations": {
      "conjugate_pair": "{a_1^-, a_1^+} = 1",
      "same_type": "{a_1^±, a_1^±} = 0, i.e. (a_1^+)^2 = (a_1^-)^2 = 0"
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
    "boson_fermion": "[b_i^±, a_1^±] = 0 (undeformed algebra; deformed in Schema 2)"
  },
  "normal_ordering": "kappa < a_1_p < a_1_m < b_1_p < b_1_m < ... < b_n_p < b_n_m"
}
```

### 1.5 `central_elements` (top-level key, mandatory)

```json
"central_elements": {
  "kappa": {
    "label": "kappa",
    "parity": 1,
    "relation": "kappa^2 = 0; [kappa, X} = 0 for all X",
    "role": "odd central element of the inhomogeneous extension A = V + C K + C kappa; carries the deformation (Schema 2). Not a basis element of g; first in PBW order.",
    "in_basis": false
  },
  "K": {
    "label": "K",
    "parity": 0,
    "relation": "[K, X} = 0 for all X; identified with the scalar 1",
    "role": "even central element (constant term of oscillator words). Excluded from basis lists; appears as a bracket target label only in Schemas 2-4 when a constant term arises.",
    "in_basis": false
  }
}
```

### 1.6 `basis`

```json
"basis": {
  "even": ["H_1", "H_2", "H_3",
           "E_2del1_p", "E_2del2_p", "E_del1_del2_pp",
           "E_2del1_m", "E_2del2_m", "E_del1_del2_mm",
           "E_del1_del2_pm", "E_del1_del2_mp"],
  "odd":  ["E_eps1_del1_pp", "E_eps1_del2_pp",
           "E_eps1_del1_pm", "E_eps1_del2_pm",
           "E_eps1_del1_mp", "E_eps1_del2_mp",
           "E_eps1_del1_mm", "E_eps1_del2_mm"],
  "pbw_order": ["E_eps1_del1_pp", "...", "E_del1_del2_mp"],
  "ordering_convention": "PBW: kappa < [odd] < [even]  (K = 1 is excluded)"
}
```

`pbw_order` is the concatenation `odd + even` and is the canonical index order used by
Schemas 2–4 (`kappa` is prepended conceptually but is not an element of `g`).
Lists for n=1,2,3 are given in `handover/notation.md` §4.

### 1.7 `parity`

Map label → 0/1 for every basis element, e.g. `"H_1": 0`, `"E_eps1_del1_pp": 1`.

### 1.8 `generator_realization`

```json
"generator_realization": {
  "description": "Standard form: sum of normal-ordered oscillator words with rational coefficients",
  "ordering": "a_1_p, a_1_m, b_1_p, b_1_m, b_2_p, b_2_m",
  "realizations": {
    "H_1": {
      "standard_form": [
        {"words": ["a_1_p", "a_1_m"], "coeff": "1"},
        {"words": ["b_1_p", "b_1_m"], "coeff": "1"}
      ],
      "frappat_form": "a_1^+ a_1^- + b_1^+ b_1^-",
      "parity": 0,
      "root": null
    },
    "H_3": {
      "standard_form": [
        {"words": ["b_2_p", "b_2_m"], "coeff": "-1"},
        {"words": [], "coeff": "-1/2"}
      ],
      "frappat_form": "-b_2^+ b_2^- - 1/2",
      "parity": 0,
      "note": "Terminal Cartan; includes constant -1/2 (symmetrized number operator)"
    },
    "E_eps1_del1_pm": {
      "standard_form": [{"words": ["a_1_p", "b_1_m"], "coeff": "1"}],
      "frappat_form": "a_1^+ b_1^-",
      "parity": 1,
      "root": {"eps": 1, "del": [-1, 0]}
    }
  }
}
```

Full table of realizations: `handover/notation.md` §3. `root` gives the weight as
$(c_\varepsilon;\, c_{\delta_1},\dots,c_{\delta_n})$; it is `null` for Cartan elements.

### 1.9 `structure_constants`

List of all non-zero graded brackets for **all ordered pairs** $(X,Y)$ of basis elements:

```json
"structure_constants": [
  {"X": "H_1", "Y": "E_eps1_del1_pp", "Z": "E_eps1_del1_pp", "coeff": "2", "sign_rule": "graded"},
  ...
]
```

meaning $[X,Y\} = \sum_Z \mathrm{coeff}\cdot Z$ with $[X,Y\} = XY-(-1)^{p(X)p(Y)}YX$.
Both $(X,Y)$ and $(Y,X)$ are stored, so super-antisymmetry is a checkable property of the
file (I04). `Z` is always a basis label (never `K`): the symmetrized-quadratic realization
closes without constant terms.

Companion key `structure_constants_convention`:
```json
"structure_constants_convention": {
  "pairs": "all ordered pairs (X, Y) with non-zero bracket",
  "bracket": "[X,Y} = X Y - (-1)^{p(X)p(Y)} Y X",
  "count": 190
}
```

### 1.10 `metadata`

```json
"metadata": {
  "generated_by": "src/C_generators.py",
  "generation_date": "YYYY-MM-DD",
  "notation": "handover/notation.md",
  "references": [
    "Frappat, Sciarrino, Sorba (2000), Dictionary on Lie Algebras and Superalgebras, arXiv:hep-th/9607161",
    "Bakalov and Sullivan (2017), arXiv:1612.09400"
  ]
}
```

---

## 2. Schema 2: `C_{n}_gamma.json` (inhomogeneous deformation)

Mathematical source: `docs/math/C_inhomogeneous_definition.md`.

### 2.1 Top-level keys

```json
{
  "schema_version": "5.0",
  "schema_layer": 2,
  "algebra": { same as Schema 1 },
  "central_elements": { same as Schema 1 },
  "basis_ref": "C_{n}_structure.json",
  "inhomogeneous_deformation": { ... },
  "metadata": { ... }
}
```

### 2.2 `inhomogeneous_deformation.deformed_oscillator_relations`

```json
"deformed_oscillator_relations": {
  "boson_fermion": "[b_j^s, a_1^σ] = - gb_{σ,j,s} kappa   (σ, s ∈ {+,-}, j = 1..n)",
  "unchanged": ["{a_1^-, a_1^+} = 1", "[b_i^-, b_j^+] = δ_ij", "kappa central, kappa^2 = 0"]
}
```

### 2.3 `inhomogeneous_deformation.gb_matrix`

A $2\times 2n$ matrix: rows indexed by the fermionic oscillator ($a_1^+$, $a_1^-$), columns by
the bosonic oscillators (`b_1_p, b_1_m, ..., b_n_p, b_n_m`).

```json
"gb_matrix": {
  "shape": [2, 4],
  "rows": ["a_1_p", "a_1_m"],
  "columns": ["b_1_p", "b_1_m", "b_2_p", "b_2_m"],
  "parameters": [["gb_a1p_b1p", "gb_a1p_b1m", "gb_a1p_b2p", "gb_a1p_b2m"],
                 ["gb_a1m_b1p", "gb_a1m_b1m", "gb_a1m_b2p", "gb_a1m_b2m"]],
  "count": 8,
  "parity": 1,
  "parity_note": "The deformation term gb·kappa is odd; gb values are treated as scalar (c-number) coefficients in computations."
}
```

Parameter naming: `gb_a1{σ}_b{j}{s}` = $\mathrm{gb}_{a_1^\sigma, b_j^s}$.

### 2.4 `inhomogeneous_deformation.gamma`

The symbolic cocycle. Each entry gives $\gamma(X,Y)$'s coefficient on $Z$ as a linear
form in the gb parameters:

```json
"gamma": [
  {"X": "E_eps1_del1_pm", "Y": "H_2", "Z": "K",
   "coeff": {"gb_a1p_b1m": "1/2"}, "expr": "1/2*gb_a1p_b1m"},
  ...
]
```

* All ordered pairs $(X,Y)$ with non-zero $\gamma$ are stored.
* `Z` ranges over the Schema 1 basis **plus `K`**: the deformed bracket of two symmetrized
  quadratics is $[X,Y]_0 + \kappa\,(\gamma_{\mathfrak g}(X,Y) + \gamma_K(X,Y)\,K)$, and the
  constant part $\gamma_K$ is in general non-zero (see I05 Response). Entries with
  `"Z": "K"` are the $K$-components.
* `gamma_convention`: `{"bracket": "[X,Y]_gamma = [X,Y]_0 + kappa * gamma(X,Y)", "target": "g + C K"}`.

---

## 3. Schema 3: `C_{n}_evaluated.json` (evaluated structure)

Same layout as Schema 2 with the gb parameters replaced by concrete rationals.

```json
{
  "schema_version": "5.0",
  "schema_layer": 3,
  "algebra": { ... },
  "central_elements": { ... },
  "basis_ref": "C_{n}_structure.json",
  "gamma_ref": "C_{n}_gamma.json",
  "gb_assignment": {
    "profile": "all_plus",
    "values": {"gb_a1p_b1p": "1", "gb_a1p_b1m": "1", ...}
  },
  "evaluated_deformation": {
    "gamma": [
      {"X": "E_eps1_del1_pm", "Y": "H_2", "Z": "K", "coeff": "1/2"},
      ...
    ],
    "count": 40
  },
  "metadata": { ... }
}
```

`C_{n}_evaluated.json` is the representative profile (`all_plus`: every gb $=+1$);
additional profiles are written as `C_{n}_evaluated_<profile>.json`.

---

## 4. Schema 4: `C_{n}_coboundary.json` (coboundary structure)

Mathematical source: `docs/math/C_coboundary_definition.md`.
$f$ is an odd linear map, $f(Z_j)=\sum_i \phi_{ij} Z_i$, and
$(\delta f)(X,Y) = (-1)^{p(X)}[X,f(Y)] - (-1)^{(p(X)+1)p(Y)}[Y,f(X)] - f([X,Y])$.

```json
{
  "schema_version": "5.0",
  "schema_layer": 4,
  "algebra": { ... },
  "central_elements": { ... },
  "basis_ref": "C_{n}_structure.json",
  "coboundary_definition": "(delta f)(X,Y) = (-1)^{p(X)} [X, f(Y)] - (-1)^{(p(X)+1) p(Y)} [Y, f(X)] - f([X,Y])",
  "f_parameterization": {
    "description": "odd linear map; phi[<Z_i>][<Z_j>] is the coefficient of Z_i in f(Z_j); only parity-reversing pairs are unknowns",
    "target": "g + C K (K-components allowed only for odd Z_j)",
    "unknowns": ["phi[E_eps1_del1_pp][H_1]", ...],
    "count": 36
  },
  "coboundary_symbolic": [
    {"X": "H_1", "Y": "H_2", "Z": "E_eps1_del1_pp",
     "coeff": {"phi[E_eps1_del1_pp][H_2]": "2", ...}, "expr": "..."}
  ],
  "representative_f": {
    "description": "...",
    "gb_profile": "all_plus",
    "map": [{"source": "E_eps1_del1_pm", "target": "H_2", "coeff": "-1/2"}, ...]
  },
  "coboundary_evaluated": [
    {"X": "...", "Y": "...", "Z": "...", "coeff": "..."}
  ],
  "metadata": { ... }
}
```

`coboundary_symbolic` stores pairs with index(X) ≤ index(Y) in `pbw_order` (the rest follow
by super-antisymmetry); `coboundary_evaluated` stores all ordered pairs for direct comparison
with Schema 3.

---

## 5. Validation rules (used by `tests/` and `src/verify_C_structure.py`)

1. `len(basis.even) == 2n^2+n+1`, `len(basis.odd) == 4n`, dimension block consistent.
2. Every label in `basis` has a `parity` entry and a `generator_realization` entry, and the
   parity equals the number of fermionic factors mod 2 in every word of its realization.
3. Every `X`, `Y`, `Z` in `structure_constants` is a basis label; coefficients parse as rationals.
4. Super-antisymmetry and super-Jacobi identity hold for the stored structure constants.
5. Schema 2 `gamma` entries vanish when all gb = 0, and are linear in gb.
6. Schema 3 equals Schema 2 with the gb values substituted.
7. Schema 4 `coboundary_evaluated` equals $\delta$(`representative_f`) recomputed from Schema 1.

---

## 6. Compatibility with the B(m,n) v5.0 schema

| Key | B(0,n) v5.0 | C(n+1) (this spec) | Compatibility |
|---|---|---|---|
| `schema_version` | "5.0" | "5.0" | identical |
| `schema_layer` | absent | 1–4 | new, optional for readers |
| `algebra.family/m` | "B", 0 | "C", 1 | same keys, new values |
| `algebra.dimension.formulas` | absent (documented in prose) | present | additive |
| `oscillator_generators` | `supplementary_fermion` + `bosons` | `fermions` + `bosons` | key renamed; `bosons` unchanged |
| `oscillator_relations` | `supplementary_fermion_relation` | `standard_fermion_anticommutators` | key renamed; `bosonic_commutators` unchanged |
| `central_elements` | absent / informal | top-level, `kappa` (parity 1), `K` (parity 0) | additive |
| `basis.even` | H_1..H_n + sp(2n) roots | H_1..H_{n+1} + same sp(2n) root labels | sp(2n) labels identical |
| `basis.odd` | `E_del{k}_p/m` (2n) | `E_eps1_del{k}_pp/pm/mp/mm` (4n) | label family changed |
| `basis.ordering_convention` | κ < odd < even | κ < odd < even | identical |
| `generator_realization.ordering` | `a_0, b_1_p, ...` | `a_1_p, a_1_m, b_1_p, ...` | same format |
| `structure_constants` | list of {X,Y,Z,coeff,sign_rule} | same record format | identical |

Readers written for B(0,n) that only use `basis`, `parity`, `generator_realization` and
`structure_constants` work unchanged on C(n+1) files.
