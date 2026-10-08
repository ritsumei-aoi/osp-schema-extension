# JSON Schema Specification for C(n+1) = osp(2|2n) (v5.0, C-extension)

This document is the complete, standalone specification of the JSON data produced for
$C(n+1) = \mathfrak{osp}(2|2n)$. It extends the B(0,n) v5.0 schema
(`docs/math/B0n_schema_v5.md`) and follows the conventions fixed in `handover/notation.md`.

Schema 1 (this issue, I02) is specified in full. Sections for Schemas 2–4 are specified in
I05–I07 and are kept in this same file so that the specification stays in one place.

---

## 0. File naming

| Layer | File | Produced by |
|---|---|---|
| Schema 1 | `data/C_{n}_structure.json` | `src/C_generators.py` |
| Schema 2 | `data/C_{n}_gamma.json` | `src/C_gamma.py` |
| Schema 3 | `data/C_{n}_evaluated.json` (representative profile) and `data/C_{n}_evaluated_<profile>.json` | `src/C_evaluate.py` |
| Schema 4 | `data/C_{n}_coboundary.json` (symbolic) and `data/C_{n}_coboundary_<profile>.json` | `src/C_coboundary.py` |

`n` is the **bosonic rank**: C(2)=osp(2|2) → `C_1_*.json`, C(3)=osp(2|4) → `C_2_*.json`,
C(4)=osp(2|6) → `C_3_*.json`. This mirrors `B_{n}_*.json`, where `n` is also the bosonic rank.

---

## 1. Schema 1 — Algebra structure (`C_{n}_structure.json`)

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

Compared with B(0,n) v5.0, `central_elements` is a **new top-level key**; every other
top-level key is kept with the same name and the same type. All rational numbers are
strings (`"1/2"`, `"-4"`) exactly as in B(0,n).

### 1.2 `schema_version`

`"5.0"`. The C-extension does not change the layer structure, so the version is kept.
Consumers distinguish B and C data by `algebra.family`.

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
  "even_subalgebra": "so(2) x sp(2)",
  "dimension": {
    "total": 8,
    "even": 4,
    "odd": 4,
    "formulas": {"even": "2n^2 + n + 1", "odd": "4n", "total": "2n^2 + 5n + 1"}
  }
}
```

* `family` = `"C"`, `m` = `1` (number of fermionic pairs), `n` = bosonic rank,
  `cartan_type` = `"C(n+1)"` with the numeric value substituted.
* Dimension table:

| n | even | odd | total | cartan_type | osp |
|---|---|---|---|---|---|
| 1 | 4 | 4 | 8 | C(2) | osp(2\|2) |
| 2 | 11 | 8 | 19 | C(3) | osp(2\|4) |
| 3 | 22 | 12 | 34 | C(4) | osp(2\|6) |

B(m,n) compatibility: same keys as B(0,n); `dimension.formulas` and `even_subalgebra` are
additive (new, optional for B readers).

### 1.4 `oscillator_generators`

```json
{
  "fermions": {
    "m": 1,
    "count": 2,
    "labels": ["a_1_p", "a_1_m"],
    "parity": 1,
    "description": "Standard fermionic pair a_1^± (CAR); replaces the supplementary fermion a_0 of B(0,n)"
  },
  "bosons": {
    "n": 1,
    "count": 2,
    "labels": ["b_1_p", "b_1_m"],
    "parity": 0,
    "description": "Bosonic oscillators b_k^± with k=1,...,n"
  }
}
```

Exactly two keys: `fermions` (with `m`) and `bosons` (with `n`). There is **no**
`supplementary_fermion` key. `bosons` is identical in shape to the B(0,n) key.

### 1.5 `oscillator_relations`

```json
{
  "standard_fermion_anticommutators": {
    "description": "Canonical anticommutation relations for the standard fermionic pair",
    "relations": {
      "same_type": "{a_1^±, a_1^±} = 0  (equivalently (a_1^±)^2 = 0)",
      "conjugate_pair": "{a_1^-, a_1^+} = 1"
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
    "boson_fermion": "[b_i^±, a_1^±] = 0 (undeformed; see Schema 2 for the κ-deformation)"
  },
  "central_elements_relations": {
    "K": "K = 1 commutes with everything",
    "kappa": "kappa^2 = 0; [kappa, b] = 0; {kappa, a_1^±} = 0 (odd super-central)"
  }
}
```

`supplementary_fermion_relation` of B(0,n) is replaced by `standard_fermion_anticommutators`.

### 1.6 `central_elements` (top-level, new)

```json
{
  "kappa": {
    "label": "kappa",
    "parity": 1,
    "relation": "kappa^2 = 0",
    "role": "Odd nilpotent central element carrying the inhomogeneous deformation (Schema 2)",
    "in_basis": false
  },
  "K": {
    "label": "K",
    "parity": 0,
    "relation": "K = 1",
    "role": "Even central element; identified with the scalar 1. Constants produced by a_1^+ a_1^- and b_k^+ b_k^- are recorded as multiples of K",
    "in_basis": false
  }
}
```

Neither element is a basis element of $\mathfrak{g}$; `structure_constants` of Schema 1 never
contain `K` or `kappa` as `Z`. (Schema 2 coefficients may have `Z = "K"`.)
Note: `B0n_definition.md` §3 lists κ with parity 0 in the B JSON; for C(n+1) the mandatory rule
of I02 is followed: **κ has parity 1, K has parity 0**.

### 1.7 `basis`

```json
{
  "even": ["H_1", "H_2", "E_2del1_p", "E_2del1_m"],
  "odd": ["E_eps1_del1_pp", "E_eps1_del1_pm", "E_eps1_del1_mp", "E_eps1_del1_mm"],
  "pbw_order": ["E_eps1_del1_pp", "E_eps1_del1_pm", "E_eps1_del1_mp", "E_eps1_del1_mm",
                "H_1", "H_2", "E_2del1_p", "E_2del1_m"],
  "ordering_convention": "PBW: kappa < [odd] < [even]  (K = 1 is excluded)",
  "roots": {"E_eps1_del1_pp": "eps1+del1", "E_2del1_p": "2del1", "H_1": "cartan", ...}
}
```

Lists follow `handover/notation.md` §3 exactly. `pbw_order` is the concatenation odd + even
(new, derived key). `roots` (new) gives the root of each generator as a string over the symbols
`eps1`, `del{k}`.

### 1.8 `parity`

Map label → 0/1 for every basis element. Odd generators are exactly `E_eps1_del{k}_{pp,pm,mp,mm}`.

### 1.9 `generator_realization`

```json
{
  "description": "Standard form: normal-ordered oscillator words with rational coefficients",
  "ordering": "kappa, a_1_p, a_1_m, b_1_p, b_1_m",
  "realizations": {
    "H_1": {
      "standard_form": [
        {"words": ["a_1_p", "a_1_m"], "coeff": "1"},
        {"words": ["b_1_p", "b_1_m"], "coeff": "1"}
      ],
      "frappat_form": "a_1^+ a_1^- + b_1^+ b_1^-",
      "parity": 0,
      "root": "cartan"
    },
    "H_2": {
      "standard_form": [
        {"words": ["b_1_p", "b_1_m"], "coeff": "-1"},
        {"words": [], "coeff": "-1/2"}
      ],
      "frappat_form": "-b_1^+ b_1^- - 1/2",
      "parity": 0,
      "root": "cartan",
      "note": "Terminal Cartan; constant written as a multiple of K = 1"
    },
    "E_eps1_del1_pm": {
      "standard_form": [{"words": ["a_1_p", "b_1_m"], "coeff": "1"}],
      "frappat_form": "a_1^+ b_1^-",
      "parity": 1,
      "root": "eps1-del1"
    }
  }
}
```

Every `a_0` word of B(0,n) is replaced by `a_1_p`/`a_1_m` words; the entry shape is unchanged.
General formulas: `H_1 = a_1_p a_1_m + b_1_p b_1_m`; `H_k = b_{k-1}_p b_{k-1}_m - b_k_p b_k_m`
(2 ≤ k ≤ n); `H_{n+1} = -b_n_p b_n_m - 1/2`; `E_2del{k}_p/m = (b_k_p/m)^2`;
`E_del{i}_del{j}_{st} = b_i_s b_j_t`; `E_eps1_del{k}_{σs} = a_1_σ b_k_s`.

### 1.10 `structure_constants`

List of non-zero graded brackets $[X,Y\} = \sum_Z c\, Z$:

```json
{"X": "E_eps1_del1_pm", "Y": "E_eps1_del1_mp", "Z": "H_1", "coeff": "1", "sign_rule": "graded"}
```

* One entry per $(X, Y, Z)$ with non-zero coefficient; **all ordered pairs** $(X,Y)$ are stored
  (both $(X,Y)$ and $(Y,X)$, and $X=Y$ when non-zero), so that the anti-symmetry check of I04 is a
  genuine check of the data rather than a tautology.
* `sign_rule` = `"graded"`: $[X,Y\} = XY - (-1)^{p(X)p(Y)} YX$.
* `Z` is always a basis label (never `K`); the generator asserts that no constant term survives.

### 1.11 `metadata`

```json
{
  "generated_by": "src/C_generators.py",
  "generation_date": "YYYY-MM-DD",
  "conventions": "handover/notation.md",
  "references": [
    "Frappat, Sciarrino, Sorba (2000), Dictionary on Lie Algebras and Superalgebras, arXiv:hep-th/9607161",
    "docs/math/Cn1_definition.md"
  ]
}
```

### 1.12 Compatibility summary with the B(m,n) v5.0 schema

| Key | B(0,n) v5.0 | C(n+1) | Compatible? |
|---|---|---|---|
| `schema_version` | "5.0" | "5.0" | yes |
| `algebra` | family B, m 0 | family C, m 1, + `formulas`, `even_subalgebra` | additive |
| `oscillator_generators` | `supplementary_fermion`, `bosons` | `fermions`, `bosons` | key renamed (B readers must branch on `family`) |
| `oscillator_relations` | `supplementary_fermion_relation` | `standard_fermion_anticommutators`, + `central_elements_relations` | key renamed |
| `central_elements` | (absent / informal) | top-level, `kappa` (1), `K` (0) | new |
| `basis` | even/odd/ordering_convention | same + `pbw_order`, `roots` | additive |
| `parity` | map | map | yes |
| `generator_realization` | words over `a_0`, `b_k_±` | words over `a_1_±`, `b_k_±` | yes (same shape) |
| `structure_constants` | list of {X,Y,Z,coeff,sign_rule} | same | yes |
| `metadata` | map | map | yes |

A reader written for B(0,n) v5.0 can load a C file after (i) reading `algebra.family`, and
(ii) mapping `oscillator_generators.fermions` / `oscillator_relations.standard_fermion_anticommutators`
in place of the supplementary-fermion keys. No field was removed except the two
supplementary-fermion keys, which have no meaning for C(n+1).

---

## 2. Schema 2 — Inhomogeneous deformation (`C_{n}_gamma.json`)

*(Specified in I05.)*

---

## 3. Schema 3 — Evaluated structure (`C_{n}_evaluated*.json`)

*(Specified in I06.)*

---

## 4. Schema 4 — Coboundary structure (`C_{n}_coboundary*.json`)

*(Specified in I07.)*
