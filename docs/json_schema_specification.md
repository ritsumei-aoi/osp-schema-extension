# JSON Schema Specification v5.0 — C(n+1) = osp(2|2n) extension

This document extends the B(0,n) v5.0 schema (`docs/math/B0n_schema_v5.md`) to
$C(n+1) = \mathfrak{osp}(2|2n)$. Schema 1 is specified completely here (Issue I02);
Schemas 2–4 are specified in §6–§8 and are produced in Issues I05–I07.
All conventions (labels, orderings) follow `handover/notation.md`.

## 1. Layer overview and file naming

| Layer | File (bosonic rank `n`) | Producer | Contents |
|---|---|---|---|
| Schema 1 | `data/C_{n}_structure.json` | `src/C_generators.py` | basis, parity, oscillator realization, structure constants |
| Schema 2 | `data/C_{n}_gamma.json` | `src/C_gamma.py` | symbolic γ-structure of the inhomogeneous deformation |
| Schema 3 | `data/C_{n}_evaluated.json` (+ optional `_<profile>` suffix) | `src/C_evaluate.py` | γ with a numeric `gb` assignment |
| Schema 4 | `data/C_{n}_coboundary.json` (+ optional suffix) | `src/C_coboundary.py` | odd map $f$ and its coboundary $\delta f$ |

**File naming rule (fixed)**: `C_{n}_<layer>.json` where `n` is the **bosonic rank**:
C(2)=osp(2|2) → `C_1_*`, C(3)=osp(2|4) → `C_2_*`, C(4)=osp(2|6) → `C_3_*`.
The B(0,n) files keep their `B_{n}_*` names; the family letter prefix is the discriminator.

## 2. Common conventions

* Rational coefficients are strings in lowest terms (`"1"`, `"-1/2"`); never floats.
* Oscillator words are lists of oscillator labels, normal-ordered w.r.t.
  `kappa < a_1_p < a_1_m < b_1_p < b_1_m < ... < b_n_p < b_n_m`; the empty word `[]` is the
  constant 1 (= `K`).
* Basis generator order (PBW order of $\mathfrak g$): `kappa < [odd] < [even]`; the *basis
  index* of a generator is its position in `basis.odd + basis.even` (odd first), 0-based.
* Structure-constant style lists are sorted by (basis index of X, basis index of Y, basis index of Z);
  the central label `"K"` sorts last.
* `sign_rule: "graded"` means $[X,Y\} = XY - (-1)^{p(X)p(Y)}YX$.

## 3. Schema 1 — `C_{n}_structure.json`

### 3.1 Top-level keys

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
Compared with B(0,n) v5.0 there is exactly **one new top-level key**, `central_elements`
(mandatory unified rule). All other top-level keys are unchanged.

### 3.2 `algebra`

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
  "even_subalgebra": "so(2) x sp(2n)"
}
```
* `family`="C", `m`=1 (number of fermionic pairs), `n` = bosonic rank; `cartan_type` = `C(n+1)`.
* `dimension_formula` is a new sub-key (explicitly required): even $2n^2+n+1$, odd $4n$.

| n | even | odd | total | cartan_type | osp |
|---|---|---|---|---|---|
| 1 | 4 | 4 | 8 | C(2) | osp(2\|2) |
| 2 | 11 | 8 | 19 | C(3) | osp(2\|4) |
| 3 | 22 | 12 | 34 | C(4) | osp(2\|6) |

### 3.3 `oscillator_generators`

```json
{
  "fermions": {
    "m": 1,
    "count": 2,
    "labels": ["a_1_p", "a_1_m"],
    "parity": 1,
    "description": "Standard fermionic pair a_1^± (CAR); replaces the B(0,n) supplementary fermion a_0"
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
The B(0,n) key `supplementary_fermion` is **absent**. Exactly two keys: `fermions`, `bosons`.

### 3.4 `oscillator_relations`

```json
{
  "standard_fermion_anticommutators": {
    "description": "Canonical anticommutation relations for the fermionic pair",
    "relations": {
      "conjugate_pair": "{a_1^-, a_1^+} = 1",
      "same_type": "{a_1^±, a_1^±} = 0  (equivalently (a_1^±)^2 = 0)"
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
    "boson_fermion": "[b_i^±, a_1^±] = 0  (undeformed; see Schema 2 for the κ-deformation)"
  }
}
```
`supplementary_fermion_relation` is replaced by `standard_fermion_anticommutators`.

### 3.5 `central_elements` (new top-level key)

```json
{
  "kappa": {
    "label": "kappa",
    "parity": 1,
    "relation": "kappa^2 = 0; x*kappa = (-1)^{p(x)} kappa*x",
    "role": "odd central element of A = V + C K + C kappa; formal first-order parameter of the inhomogeneous deformation (Schema 2)",
    "in_basis": false
  },
  "K": {
    "label": "K",
    "parity": 0,
    "relation": "K = 1 (identified with the scalar unit)",
    "role": "even central element; may appear as target label \"K\" in Schema 2-4 records",
    "in_basis": false
  },
  "pbw_position": "kappa < [odd] < [even]; K is excluded from the PBW basis"
}
```
Note: `B0n_definition.md` lists κ with parity 0 in the B(0,n) `central_elements`; for C(n+1)
the mandatory rule fixes `kappa` parity **1** and `K` parity **0**, consistent with
`C_inhomogeneous_definition.md`.

### 3.6 `basis`

```json
{
  "even": ["H_1", "H_2", "H_3",
           "E_2del1_p", "E_2del2_p", "E_del1_del2_pp",
           "E_2del1_m", "E_2del2_m", "E_del1_del2_mm",
           "E_del1_del2_pm", "E_del1_del2_mp"],
  "odd":  ["E_eps1_del1_pp", "E_eps1_del1_pm", "E_eps1_del2_pp", "E_eps1_del2_pm",
           "E_eps1_del1_mp", "E_eps1_del1_mm", "E_eps1_del2_mp", "E_eps1_del2_mm"],
  "cartan": ["H_1", "H_2", "H_3"],
  "ordering_convention": "PBW: kappa < [odd] < [even]  (K = 1 is excluded)",
  "pbw_order": ["E_eps1_del1_pp", "...", "E_del1_del2_mp"]
}
```
* `cartan` and `pbw_order` are new informative sub-keys (`pbw_order` = `odd + even`).
* The Cartan subalgebra has rank $n+1$ (`H_1..H_{n+1}`), one more than B(0,n).
* `odd` contains the $4n$ generators `E_eps1_del{k}_{pp,pm,mp,mm}`.

### 3.7 `parity`

Map from every basis label to 0/1. All `H_*`, `E_2del*`, `E_del*_del*` → 0; all `E_eps1_*` → 1.

### 3.8 `generator_realization`

```json
{
  "description": "Standard form with PBW ordering of oscillator words",
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
      "root": null,
      "note": "Terminal Cartan H_{n+1} = [E_{2δ_n}/2, E_{-2δ_n}/2]"
    },
    "E_eps1_del2_pm": {
      "standard_form": [{"words": ["a_1_p", "b_2_m"], "coeff": "1"}],
      "frappat_form": "a_1^+ b_2^-",
      "parity": 1,
      "root": {"eps": 1, "delta": [0, -1]}
    }
  }
}
```
* `a_0` never appears; odd generators use `a_1_p`/`a_1_m`.
* `root` is a new informative sub-key: `eps` ∈ {−1,0,1}, `delta` = integer vector of length n
  (e.g. `E_2del1_p` → `{"eps":0,"delta":[2,0]}`); `null` for Cartan generators.

### 3.9 `structure_constants`

List of records for **every ordered pair** $(X,Y)$ with non-zero bracket, one record per
basis component $Z$:
```json
{"X": "E_eps1_del1_pm", "Y": "E_eps1_del1_mp", "Z": "H_1", "coeff": "1", "sign_rule": "graded"}
```
* Both $(X,Y)$ and $(Y,X)$ are stored (computed independently), so graded antisymmetry is a
  checkable property, not an input.
* `Z` is always a basis label in Schema 1 (closure of $\mathfrak g$; `"K"` must not occur).
  The generator asserts this.

### 3.10 `metadata`

```json
{
  "generated_by": "src/C_generators.py",
  "generation_date": "YYYY-MM-DD",
  "schema_specification": "docs/json_schema_specification.md",
  "notation": "handover/notation.md",
  "references": ["Frappat, Sciarrino, Sorba (2000), Dictionary on Lie Algebras and Superalgebras",
                 "docs/math/Cn1_definition.md"]
}
```

## 4. Compatibility with the B(m,n) / B(0,n) v5.0 schema

| Key | B(0,n) v5.0 | C(n+1) | Compatibility |
|---|---|---|---|
| `schema_version` | "5.0" | "5.0" | identical |
| `algebra.family/m/n` | "B", 0, n | "C", 1, n | same shape; `dimension_formula` sub-key added |
| `oscillator_generators` | `supplementary_fermion`, `bosons` | `fermions`, `bosons` | readers must dispatch on which fermion key is present |
| `oscillator_relations` | `supplementary_fermion_relation` | `standard_fermion_anticommutators` | same for `bosonic_commutators`, `mixed_commutators` |
| `central_elements` | (not top-level) | top-level, `kappa`(1), `K`(0) | additive; B readers ignore unknown keys |
| `basis` | `even`, `odd`, `ordering_convention` | + `cartan`, `pbw_order` | additive |
| `parity` | map | map | identical shape |
| `generator_realization` | words over `a_0, b_*` | words over `a_1_p, a_1_m, b_*`; + `root` | additive; `ordering` string differs |
| `structure_constants` | records X,Y,Z,coeff,sign_rule | identical record shape | identical |
| `metadata` | | | identical shape |

Rule: a B(0,n) v5.0 consumer that ignores unknown keys can load `C_{n}_structure.json`
provided it dispatches on `algebra.family`; all even-sector labels are literally the same
strings as in B(0,n), so even-sector tooling is reusable.

## 5. Validation rules for Schema 1 (checked by `tests/`)

1. `len(basis.even) = 2n^2+n+1`, `len(basis.odd) = 4n`, equal to `algebra.dimension`.
2. `parity` keys = basis labels; values agree with the even/odd lists and with the realization parity.
3. Every oscillator word uses only labels from `oscillator_generators`; words are normal-ordered.
4. Structure constants: Z ∈ basis; graded antisymmetry; super Jacobi (I04).
5. `cartan_type` = `C(n+1)`, `alternative_notation.osp` = `osp(2|2n)`.

## 6. Schema 2 — `C_{n}_gamma.json` (produced in I05)

```json
{
  "schema_version": "5.0",
  "schema_layer": 2,
  "algebra": { ...copy of Schema 1 algebra... },
  "source_structure": "C_{n}_structure.json",
  "central_elements": { ...copy of Schema 1... },
  "inhomogeneous_deformation": {
    "type": "inhomogeneous",
    "definition": "[b_k^s, a_1^sigma] = - gb[a_1^sigma][b_k^s] * kappa",
    "bracket_form": "[X,Y]_gamma = [X,Y]_0 + kappa * gamma(X,Y)",
    "gb_matrix": {
      "shape": [2, 4],
      "rows": ["a_1_p", "a_1_m"],
      "columns": ["b_1_p", "b_1_m", "b_2_p", "b_2_m"],
      "labels": [["gb_a1p_b1p", "gb_a1p_b1m", "gb_a1p_b2p", "gb_a1p_b2m"],
                 ["gb_a1m_b1p", "gb_a1m_b1m", "gb_a1m_b2p", "gb_a1m_b2m"]],
      "count": 8,
      "parameter_type": "commuting scalar"
    },
    "gamma_parity_rule": "p(gamma(X,Y)) = p(X)+p(Y)+1",
    "target_space": "g + C K"
  },
  "gamma": [
    {"X": "H_1", "Y": "E_eps1_del1_pp", "Z": "H_1",
     "terms": [{"gb": "gb_a1p_b1p", "coeff": "-1"}]}
  ],
  "metadata": { ... }
}
```
`gamma` lists every ordered pair with non-zero $\gamma(X,Y)$, one record per target $Z$
(basis label or `"K"`); `terms` is the linear form $\sum_g c_g\, g$ in the `gb` symbols.

## 7. Schema 3 — `C_{n}_evaluated.json` (produced in I06)

Same header as Schema 2 plus
```json
"gb_assignment": {"profile": "all_plus_one", "values": {"gb_a1p_b1p": "1", ...}},
"evaluated_gamma": [{"X": "...", "Y": "...", "Z": "...", "coeff": "-1"}],
"deformed_structure_constants": [
  {"X": "...", "Y": "...", "Z": "...", "coeff": "1", "kappa_order": 0},
  {"X": "...", "Y": "...", "Z": "...", "coeff": "-1", "kappa_order": 1}
]
```
`kappa_order` 0 records reproduce Schema 1; `kappa_order` 1 records are `evaluated_gamma`.

## 8. Schema 4 — `C_{n}_coboundary.json` (produced in I07)

```json
"odd_map_f": {
  "parameterization": "f(Z_j) = sum_i phi_<i>_<j> Z_i, p(Z_i) != p(Z_j); indices = basis index (odd first)",
  "phi_count": 176,
  "reference": {"name": "canonical_gb", "gb_assignment": {...},
                "definition": "f = kappa-coefficient of X(a_1 + kappa c, b) - X(a_1, b)",
                "values": {"phi_<i>_<j>": "rational", ...},
                "K_component": {"<odd label>": "rational"}},
  "f_matrix": [{"source": "Z_j", "target": "Z_i or K", "coeff": "..."}]
},
"coboundary": [{"X": "...", "Y": "...", "Z": "...", "coeff": "..."}],
"coboundary_formula": "(delta f)(X,Y) = (-1)^{p(X)}[X,f(Y)] - (-1)^{(p(X)+1)p(Y)}[Y,f(X)] - f([X,Y])"
```
