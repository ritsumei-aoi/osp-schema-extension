# JSON Schema Specification v5.0 — C(n+1) = osp(2|2n) extension

This document is the complete, standalone v5.0 specification for $C(n+1) = \mathfrak{osp}(2|2n)$.
It extends the B(0,n) v5.0 schema (`docs/math/B0n_schema_v5.md`). Notation: `handover/notation.md`.

## 0. File layout and naming

| Layer | File | Producer | Issue |
|---|---|---|---|
| Schema 1 | `data/C_{n}_structure.json` | `src/C_generators.py` | I03 |
| Schema 2 | `data/C_{n}_gamma.json` | `src/C_gamma.py` | I05 |
| Schema 3 | `data/C_{n}_evaluated_{profile}.json` (+ `data/C_{n}_evaluated.json` = default profile) | `src/C_evaluate.py` | I06 |
| Schema 4 | `data/C_{n}_coboundary.json` | `src/C_coboundary.py` | I07 |

`n` is the **bosonic rank**: C(2) = osp(2|2) → `C_1_*.json`, C(3) = osp(2|4) → `C_2_*.json`,
C(4) = osp(2|6) → `C_3_*.json`. Generated files: n = 1, 2, 3.

---

## 1. Schema 1: algebra structure (`C_{n}_structure.json`)

### Top-level keys

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

`central_elements` is a **new top-level key** (absent in B(0,n) v5.0 files).

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
  "dimension_formulas": {"even": "2n^2 + n + 1", "odd": "4n", "total": "2n^2 + 5n + 1"},
  "dimension": {"total": 19, "even": 11, "odd": 8}
}
```

| n | cartan_type | osp | even | odd | total |
|---|---|---|---|---|---|
| 1 | C(2) | osp(2\|2) | 4 | 4 | 8 |
| 2 | C(3) | osp(2\|4) | 11 | 8 | 19 |
| 3 | C(4) | osp(2\|6) | 22 | 12 | 34 |

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
    "description": "Bosonic oscillators b_k^± with k=1,...,n (CCR)"
  }
}
```

### `oscillator_relations`

```json
{
  "standard_fermion_anticommutators": {
    "description": "Canonical anticommutation relations for the fermionic pair",
    "relations": {
      "conjugate_pair": "{a_1^-, a_1^+} = 1",
      "same_type": "{a_1^+, a_1^+} = 0, {a_1^-, a_1^-} = 0"
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
    "boson_fermion": "[b_i^±, a_1^±] = 0 (undeformed; deformed version in Schema 2)"
  }
}
```

### `central_elements` (top level)

```json
{
  "kappa": {"label": "kappa", "parity": 1, "relation": "kappa^2 = 0",
            "role": "odd central element of A = V ⊕ CK ⊕ Cκ; carries the inhomogeneous deformation"},
  "K": {"label": "K", "parity": 0, "relation": "K = 1",
        "role": "even central element; identified with the scalar 1, excluded from basis/PBW"}
}
```

### `basis`

```json
{
  "even": ["H_1", "H_2", "H_3", "E_2del1_p", "E_2del2_p", "E_del1_del2_pp",
           "E_2del1_m", "E_2del2_m", "E_del1_del2_mm", "E_del1_del2_pm", "E_del1_del2_mp"],
  "odd": ["E_eps1_del1_pp", "E_eps1_del2_pp", "E_eps1_del1_pm", "E_eps1_del2_pm",
          "E_eps1_del1_mp", "E_eps1_del2_mp", "E_eps1_del1_mm", "E_eps1_del2_mm"],
  "ordering": ["E_eps1_del1_pp", "...", "E_del1_del2_mp"],
  "ordering_convention": "PBW: κ < [odd: pp < pm < mp < mm, each by k] < [even: H, E_2del_p, E_del_del_pp, E_2del_m, E_del_del_mm, E_del_del_pm, E_del_del_mp]  (K = 1 excluded)"
}
```

`ordering` is the full PBW-ordered basis (odd then even) and is the index order used by all layers.

### `parity`

Map label → 0/1. Even generators 0, `E_eps1_del{k}_{σs}` 1.

### `generator_realization`

```json
{
  "description": "Standard form: words in oscillator order, Weyl-ordered generators",
  "ordering": "a_1_p, a_1_m, b_1_p, b_1_m, ..., b_n_p, b_n_m",
  "realizations": {
    "H_1": {"standard_form": [{"words": ["a_1_p","a_1_m"], "coeff": "1"},
                              {"words": ["b_1_p","b_1_m"], "coeff": "1"}],
            "frappat_form": "a_1^+ a_1^- + b_1^+ b_1^-", "parity": 0},
    "H_3": {"standard_form": [{"words": ["b_2_p","b_2_m"], "coeff": "-1"},
                              {"words": [], "coeff": "-1/2"}],
            "frappat_form": "-b_2^+ b_2^- - 1/2", "parity": 0,
            "note": "Terminal Cartan; constant from Weyl ordering"},
    "E_eps1_del1_pm": {"standard_form": [{"words": ["a_1_p","b_1_m"], "coeff": "1"}],
                       "frappat_form": "a_1^+ b_1^-", "parity": 1}
  }
}
```

Every basis element has an entry. `words: []` denotes the constant (K = 1).
Words are normal ordered (`a_1_p < a_1_m < b_1_p < b_1_m < …`); different bosons commute, so e.g.
`E_del1_del2_mp` = $b_1^- b_2^+$ is stored as `["b_1_m", "b_2_p"]`.

### `structure_constants`

List of all non-zero components of the undeformed graded bracket, over **all ordered pairs** (X, Y):

```json
{"X": "H_1", "Y": "E_eps1_del1_pp", "Z": "E_eps1_del1_pp", "coeff": "1", "sign_rule": "graded"}
```

meaning $[X, Y\} = \sum_Z \mathrm{coeff}\cdot Z$. Both (X,Y) and (Y,X) are stored so super-antisymmetry
$[Y,X\} = -(-1)^{p(X)p(Y)}[X,Y\}$ can be verified from the data (I04). No `K` component occurs (checked).

### `metadata`

```json
{"generated_by": "src/C_generators.py", "generation_date": "YYYY-MM-DD",
 "conventions": "handover/notation.md",
 "references": ["Frappat et al. (2000), Dictionary on Lie Algebras and Superalgebras",
                "Bakalov and Sullivan (2017)"]}
```

---

## 2. Compatibility with B(m,n) v5.0

| Key | B(0,n) v5.0 | C(n+1) v5.0 | Compatibility |
|---|---|---|---|
| `schema_version` | "5.0" | "5.0" | identical |
| `algebra` | family "B", m=0 | family "C", m=1; extra `dimension_formulas` | additive; readers keyed on `family` |
| `oscillator_generators` | `supplementary_fermion`, `bosons` | `fermions`, `bosons` | `bosons` identical; fermion key renamed (readers must branch on family) |
| `oscillator_relations` | `supplementary_fermion_relation` | `standard_fermion_anticommutators` | `bosonic_commutators` identical; `mixed_commutators` same key |
| `central_elements` | (described in text, κ listed with parity 0) | top-level key, κ parity 1, K parity 0 | new key; κ parity corrected to 1 (odd), consistent with the math docs |
| `basis` | `even`, `odd`, `ordering_convention` | same + `ordering` | additive |
| `parity`, `generator_realization`, `structure_constants`, `metadata` | — | same structure | identical format |

A B(0,n) reader that ignores unknown keys can load Schema 1 C-files except for the fermion-specific keys.

---

## 3. Schema 2: γ-structure (`C_{n}_gamma.json`)

```json
{
  "schema_version": "5.0", "layer": 2,
  "algebra": {"family": "C", "m": 1, "n": 2, "cartan_type": "C(3)"},
  "structure_file": "C_2_structure.json",
  "gb_matrix": {"rows": ["a_1_p","a_1_m"], "columns": ["b_1_p","b_1_m","b_2_p","b_2_m"],
                "labels": [["gb_a1p_b1p", "..."], ["gb_a1m_b1p", "..."]], "count": 8},
  "deformed_relations": {"rule": "[b_j^s, a_1^σ] = - gb_{σ,j,s} κ", "...": "..."},
  "inhomogeneous_deformation": {
    "bracket": "[X,Y]_γ = [X,Y]_0 + κ γ(X,Y)",
    "value_space": "g ⊕ CK",
    "entries": [{"X": "...", "Y": "...", "Z": "E_... | K",
                 "coeff": {"gb_a1p_b1m": "1/2", "...": "..."}}]
  },
  "metadata": {}
}
```

γ is linear in gb; `coeff` maps gb labels to rationals. All ordered pairs are stored.
Additional keys in generated files: `basis_ordering` (copied from Schema 1),
`inhomogeneous_deformation.{value_space, linearity, pairs, parity_rule, num_entries, num_K_entries}`.
Invariants (checked by `src/C_gamma.py`): undeformed part of every deformed bracket equals Schema 1;
$\gamma(Y,X) = -(-1)^{p(X)p(Y)}\gamma(X,Y)$; $p(Z) = p(X)+p(Y)+1$ ($K$ even); the κ-part of the
super-Jacobiator of $L = \mathfrak{g} \oplus \kappa(\mathfrak{g} \oplus \mathbb{C}K)$ vanishes (2-cocycle condition).
Details: I05 Response.

## 4. Schema 3: evaluated structure (`C_{n}_evaluated_{profile}.json`)

Keys: `schema_version`, `layer` (=3), `algebra`, `structure_file`, `gamma_file`, `basis_ordering`,
`profile` {`name`, `description`}, `gb_values` {label: rational}, `gb_matrix_values` (2 × 2n),
`evaluated_deformation` {`entries`: `{"X","Y","Z","coeff": "<rational>"}` with `Z ∈ basis ∪ {"K"}`},
`evaluated_structure_constants` {`entries`: `{"X","Y","Z","coeff","part"}`, `part` = `"g"` (undeformed,
copied from Schema 1) or `"kappa"` (coefficient of κ·Z)}, `metadata`.
Profiles: `allplus` (default file `C_{n}_evaluated.json`), `allminus`, `checker`, `rowsign`, `single`, `zero`.
Details: I06 Response.

## 5. Schema 4: coboundary structure (`C_{n}_coboundary.json`)

General odd 1-cochain $f(Z_j) = \sum_i \phi_{ij} Z_i + \phi_{K,j} K$ and $(\delta f)(X,Y)$ as linear forms in
the unknowns. Details: I07 Response.
