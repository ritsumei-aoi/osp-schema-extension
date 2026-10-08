# JSON Schema Specification for C(n+1) = osp(2|2n)  (v5.0, C-extension)

This document specifies the 4-layer JSON schema for $C(n+1) = \mathfrak{osp}(2|2n)$.
It extends the $B(0,n)$ v5.0 schema (`docs/math/B0n_schema_v5.md`) and follows the
conventions fixed in `handover/notation.md` (Issue I01).

Schema 1 is specified in full here (Issue I02). Schemas 2–4 are specified in
Sections 6–8, which are filled in by Issues I05, I06 and I07 respectively.

---

## 1. Overview: 4-layer architecture and file naming

| Layer | File | Produced by | Contents |
|---|---|---|---|
| Schema 1 | `data/C_{n}_structure.json` | `src/C_generators.py` | basis, parity, oscillator realization, structure constants |
| Schema 2 | `data/C_{n}_gamma.json` | `src/C_gamma.py` | inhomogeneous deformation γ (symbolic in gb) |
| Schema 3 | `data/C_{n}_evaluated.json` (and `C_{n}_evaluated_<profile>.json`) | `src/C_evaluate.py` | γ and the deformed brackets for a concrete gb assignment |
| Schema 4 | `data/C_{n}_coboundary.json` | `src/C_coboundary.py` | coboundary δf of a general odd linear map f |

**File naming rule (fixed):** `C_{n}_<layer>.json` where `n` is the **bosonic rank**.
$C(2)=\mathfrak{osp}(2|2)$ is `C_1_*.json`, $C(3)=\mathfrak{osp}(2|4)$ is `C_2_*.json`,
$C(4)=\mathfrak{osp}(2|6)$ is `C_3_*.json`. This mirrors `B_n_*.json` for $B(0,n)$.

All rational numbers are stored as **strings** (`"1"`, `"-1/2"`) so that no precision is lost;
symbolic coefficients (Schemas 2 and 4) are stored both as a printable string and as a
structured linear form.

---

## 2. Schema 1: top-level keys

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
  "roots": { ... },
  "generator_realization": { ... },
  "structure_constants": [ ... ],
  "metadata": { ... }
}
```

Keys new relative to $B(0,n)$: `schema_layer`, `central_elements` (top level, mandatory),
`roots` (optional helper), `algebra.dimension_formulas`, `algebra.rank`, `algebra.even_subalgebra`.
All $B(0,n)$ keys are retained with the same meaning.

### 2.1 `schema_version`, `schema_layer`

`"schema_version": "5.0"`; `"schema_layer": 1` (integer 1–4, identifies the layer).

### 2.2 `algebra`

```json
{
  "family": "C",
  "m": 1,
  "n": 1,
  "cartan_type": "C(2)",
  "alternative_notation": {"osp": "osp(2|2)", "dimension_formula": "osp(2m|2n) with m=1"},
  "dimension": {"total": 8, "even": 4, "odd": 4},
  "dimension_formulas": {"even": "2n^2 + n + 1", "odd": "4n", "total": "2n^2 + 5n + 1"},
  "rank": 2,
  "even_subalgebra": "so(2) + sp(2)"
}
```

| Field | Type | Rule |
|---|---|---|
| `family` | string | `"C"` |
| `m` | int | always `1` (one fermionic pair) |
| `n` | int | bosonic rank $\ge 1$ |
| `cartan_type` | string | `"C(n+1)"` |
| `dimension.even/odd/total` | int | $2n^2+n+1$, $4n$, $2n^2+5n+1$ |
| `dimension_formulas` | strings | the three formulas above, verbatim |
| `rank` | int | $n+1$ |
| `even_subalgebra` | string | `"so(2) + sp(2n)"` |

| $n$ | even | odd | total |
|---|---|---|---|
| 1 | 4 | 4 | 8 |
| 2 | 11 | 8 | 19 |
| 3 | 22 | 12 | 34 |

### 2.3 `oscillator_generators`

Exactly two keys, `fermions` and `bosons` (no `supplementary_fermion`).

```json
{
  "fermions": {"m": 1, "count": 2, "labels": ["a_1_p", "a_1_m"], "parity": 1,
               "description": "Standard fermionic pair a_1^± (CAR); replaces the supplementary fermion a_0 of B(0,n)"},
  "bosons":   {"n": 1, "count": 2, "labels": ["b_1_p", "b_1_m"], "parity": 0,
               "description": "Bosonic oscillators b_k^± with k=1,...,n"}
}
```

`bosons.labels` is `["b_1_p","b_1_m",...,"b_n_p","b_n_m"]`, `bosons.count` $=2n$.

### 2.4 `oscillator_relations`

```json
{
  "standard_fermion_anticommutators": {
    "description": "Canonical anticommutation relations for the fermionic pair",
    "relations": {"conjugate_pair": "{a_1^-, a_1^+} = 1",
                  "same_type": "{a_1^±, a_1^±} = 0  (equivalently (a_1^±)^2 = 0)"}
  },
  "bosonic_commutators": {
    "description": "Canonical commutation relations for bosonic oscillators",
    "relations": {"same_type": "[b_i^±, b_j^±] = 0 for all i, j",
                  "conjugate_pair": "[b_i^-, b_j^+] = δ_{ij}"}
  },
  "mixed_commutators": {
    "boson_fermion": "[b_j^±, a_1^±] = 0  (undeformed; see Schema 2 for the gb deformation)"
  }
}
```

`supplementary_fermion_relation` of $B(0,n)$ is **replaced** by `standard_fermion_anticommutators`.

### 2.5 `central_elements` (top-level, mandatory)

```json
{
  "kappa": {"label": "kappa", "parity": 1,
            "relation": "kappa^2 = 0, [kappa, X} = 0 for all X",
            "description": "Odd nilpotent symbol of the inhomogeneous deformation; first in PBW order. Not a basis element of C(n+1)."},
  "K":     {"label": "K", "parity": 0,
            "relation": "K = 1 (central identity)",
            "description": "Even central identity of the pre-oscillator extension A = V + CK + C kappa. Identified with the scalar 1; excluded from the basis and from PBW ordering."}
}
```

Decision (I02): `kappa` has **parity 1** (it is the odd central element of
`C_inhomogeneous_definition.md`; the $B(0,n)$ document's "parity 0" listing is a $B$-specific
bookkeeping choice that we do not carry over). `K` has parity 0 and is identified with $1$.
Neither element appears in `basis` or `parity`; `K` may appear as a target label `"Z": "K"`
in Schemas 2–4 because the deformation cocycle takes values in $\tilde{\mathfrak g} = \mathfrak g \oplus \mathbb{C}K$.

### 2.6 `basis`

```json
{
  "even": ["H_1", "H_2", "E_2del1_p", "E_2del1_m"],
  "odd":  ["E_eps1_del1_pp", "E_eps1_del1_pm", "E_eps1_del1_mp", "E_eps1_del1_mm"],
  "ordering_convention": "PBW: kappa < [odd] < [even]  (K = 1 is excluded)",
  "odd_label_convention": "E_eps1_del{k}_{st}: s = sign of eps (fermion a_1^s), t = sign of delta_k (boson b_k^t)"
}
```

The lists are in PBW order (`handover/notation.md` §3–4). The full basis is `odd + even`.
Odd generators `E_eps1_del{k}_pp/pm/mp/mm` replace $B(0,n)$'s `E_del{k}_p/m`; the even list gains
one extra Cartan element (`H_{n+1}`, total $n+1$ Cartan elements).

### 2.7 `parity`

Map from every basis label to `0`/`1`; odd generators are exactly the `E_eps1_del{k}_*` labels.

### 2.8 `roots` (helper, new)

```json
{
  "coordinates": ["eps", "delta_1"],
  "simple_roots": ["eps - delta_1", "2 delta_1"],
  "vectors": {"E_eps1_del1_pp": [1, 1], "H_1": [0, 0], "E_2del1_p": [0, 2], ...}
}
```

Integer root vectors in the basis $(\varepsilon, \delta_1, \dots, \delta_n)$; Cartan elements have the zero vector.

### 2.9 `generator_realization`

```json
{
  "description": "Standard form with PBW ordering of oscillator words",
  "ordering": "kappa, a_1_p, a_1_m, b_1_p, b_1_m",
  "realizations": {
    "H_1": {"standard_form": [{"words": ["a_1_p","a_1_m"], "coeff": "1"},
                              {"words": ["b_1_p","b_1_m"], "coeff": "1"}],
            "frappat_form": "a_1^+ a_1^- + b_1^+ b_1^-", "parity": 0,
            "note": "Cartan element of the odd simple root eps - delta_1"},
    "H_2": {"standard_form": [{"words": ["b_1_p","b_1_m"], "coeff": "-1"},
                              {"words": [], "coeff": "-1/2"}],
            "frappat_form": "-b_1^+ b_1^- - 1/2", "parity": 0,
            "note": "Terminal Cartan element ...; the constant -1/2 is forced by [E_2del1_p, E_2del1_m] = 4 H_{n+1}"},
    "E_eps1_del1_pm": {"standard_form": [{"words": ["a_1_p","b_1_m"], "coeff": "1"}],
                       "frappat_form": "a_1^+ b_1^-", "parity": 1},
    "E_2del1_p": {"standard_form": [{"words": ["b_1_p","b_1_p"], "coeff": "1"}],
                  "frappat_form": "(b_1^+)^2", "parity": 0}
  }
}
```

Every basis element has an entry. `words` are oscillator labels in normal order
(`ordering`), `coeff` a rational string, `[]` denotes the constant word. Root vectors are a
single word with coefficient `1` (normalization decision, I01); the Cartan elements are
$H_1 = a_1^+a_1^- + b_1^+b_1^-$, $H_k = b_{k-1}^+b_{k-1}^- - b_k^+b_k^-$, $H_{n+1} = -b_n^+b_n^- - \tfrac12$.

### 2.10 `structure_constants`

List of all **ordered** pairs $(X, Y)$ with non-zero graded bracket, one entry per target $Z$:

```json
{"X": "E_eps1_del1_pp", "Y": "E_eps1_del1_mm", "Z": "H_2", "coeff": "-2", "sign_rule": "graded"}
```

$[X, Y\} = \sum_Z \text{coeff}\cdot Z$ with $[X,Y\} = XY - (-1)^{p(X)p(Y)}YX$. Both $(X,Y)$ and
$(Y,X)$ are listed, so graded antisymmetry is verifiable from the data (Issue I04). In the
undeformed algebra `Z` is always a basis label (never `"K"`); the generator asserts this.

Counts of non-zero entries: $n=1$: 40, $n=2$: 198, $n=3$: 528.

### 2.11 `metadata`

`generated_by`, `generation_date` (ISO), `structure_constants_convention`, `references`.

---

## 3. Compatibility with the B(m,n) / B(0,n) v5.0 schema

| Key | B(0,n) v5.0 | C(n+1) (this spec) | Compatibility |
|---|---|---|---|
| `schema_version` | `"5.0"` | `"5.0"` | unchanged |
| `schema_layer` | absent | `1..4` | additive; readers may ignore |
| `algebra.family/m` | `"B"`, `0` | `"C"`, `1` | same types; dispatch on `family` |
| `algebra.dimension_formulas`, `rank`, `even_subalgebra` | absent | present | additive |
| `oscillator_generators.supplementary_fermion` | present | **removed** | readers of C data must use `fermions` |
| `oscillator_generators.fermions` | absent | present (`m`, `labels`) | additive |
| `oscillator_generators.bosons` | present | present (adds `parity`) | unchanged |
| `oscillator_relations.supplementary_fermion_relation` | present | **replaced** by `standard_fermion_anticommutators` | key rename |
| `central_elements` | mentioned, nested in `oscillator_relations` | **top-level**, `kappa` (parity 1) + `K` (parity 0) | moved to top level |
| `basis.odd` | `E_del{k}_p/m` (2n) | `E_eps1_del{k}_pp/pm/mp/mm` (4n) | label pattern changes |
| `basis.even` | n Cartan | n+1 Cartan | one more `H` |
| `parity`, `generator_realization`, `structure_constants`, `metadata` | — | same shape | unchanged |
| `roots` | absent | present | additive |

A B(m,n)-style reader therefore needs only: (i) a `family` switch, (ii) reading `fermions`
instead of `supplementary_fermion`, (iii) tolerating the extra keys. A `family == "B"` file
remains valid under this specification with `m = 0`.

---

## 4. Validation rules (checked by `tests/test_C_structure.py`)

1. `len(basis.even) == dimension.even`, `len(basis.odd) == dimension.odd`, formulas hold.
2. `parity` covers exactly the basis; odd ⇔ label starts with `E_eps1_del`.
3. Every basis element has a `generator_realization` entry whose words are in normal order and
   whose parity equals the sum of the word parities.
4. Every `structure_constants` entry refers to basis labels only, `p(Z) = p(X)+p(Y) \bmod 2`, and the
   root vectors add: `roots[Z] = roots[X] + roots[Y]`.
5. Re-computing the brackets from the realizations reproduces the stored list exactly.
6. Graded antisymmetry and the super Jacobi identity hold (Issue I04, `src/verify_C_structure.py`).

---

## 5. Worked example: `data/C_1_structure.json` (C(2) = osp(2|2))

Basis (8): `E_eps1_del1_pp, E_eps1_del1_pm, E_eps1_del1_mp, E_eps1_del1_mm | H_1, H_2, E_2del1_p, E_2del1_m`.
Selected brackets:

| X | Y | [X,Y} |
|---|---|---|
| `E_eps1_del1_pp` | `E_eps1_del1_mm` | `-H_1 - 2 H_2` |
| `E_eps1_del1_pm` | `E_eps1_del1_mp` | `H_1` |
| `H_1` | `E_eps1_del1_pp` | `2 E_eps1_del1_pp` |
| `E_2del1_p` | `E_2del1_m` | `4 H_2` |
| `E_2del1_p` | `E_eps1_del1_pm` | `-2 E_eps1_del1_pp` |

---

## 6. Schema 2: inhomogeneous deformation (`C_{n}_gamma.json`)

*(Specified in Issue I05.)*

## 7. Schema 3: evaluated structure (`C_{n}_evaluated.json`)

*(Specified in Issue I06.)*

## 8. Schema 4: coboundary structure (`C_{n}_coboundary.json`)

*(Specified in Issue I07.)*
