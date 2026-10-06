# JSON Schema Specification — C(n+1) = osp(2|2n), v5.0 extension

This is the complete, standalone v5.0 specification for $C(n+1)=\mathfrak{osp}(2|2n)$,
obtained by extending the B(0,n) v5.0 schema (`docs/math/B0n_schema_v5.md`).
Notation (labels, PBW order, realizations) is fixed in `handover/notation.md`.

## Overview: 4-layer architecture

| Layer | File | Contents | Produced by |
|---|---|---|---|
| Schema 1 | `data/C_{n}_structure.json` | algebra, oscillators, basis, parity, realizations, structure constants | `src/C_generators.py` (I03) |
| Schema 2 | `data/C_{n}_gamma.json` | inhomogeneous deformation: gb matrix, symbolic $\gamma_{abc}$ | `src/C_gamma.py` (I05) |
| Schema 3 | `data/C_{n}_evaluated.json` | $\gamma$ evaluated at concrete gb sign profiles | `src/C_evaluate.py` (I06) |
| Schema 4 | `data/C_{n}_coboundary.json` | odd map $f$ and coboundary $\delta f$ | `src/C_coboundary.py` (I07) |

`n` in file names is the **bosonic rank**: C(2) → `C_1_*`, C(3) → `C_2_*`, C(4) → `C_3_*`.

---

## Schema 1: Algebra Structure (`C_{n}_structure.json`)

### Top-level keys

```json
{
  "schema_version": "5.0",
  "algebra": {...},
  "oscillator_generators": {...},
  "oscillator_relations": {...},
  "central_elements": {...},
  "basis": {...},
  "parity": {...},
  "generator_realization": {...},
  "structure_constants": [...],
  "metadata": {...}
}
```

`central_elements` is a **new top-level key** (not present in B(0,n) v5.0, where $\kappa$/$K$
were only described in prose).

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

`cartan_type` is `C(n+1)`. Values:

| n | cartan_type | osp | even | odd | total |
|---|---|---|---|---|---|
| 1 | C(2) | osp(2\|2) | 4 | 4 | 8 |
| 2 | C(3) | osp(2\|4) | 11 | 8 | 19 |
| 3 | C(4) | osp(2\|6) | 22 | 12 | 34 |

### `oscillator_generators`

```json
{
  "fermions": {
    "count": 2,
    "m": 1,
    "labels": ["a_1_p", "a_1_m"],
    "parity": 1,
    "description": "Standard fermionic CAR pair a_1^± (replaces B(0,n)'s supplementary fermion a_0)"
  },
  "bosons": {
    "count": 2n,
    "n": n,
    "labels": ["b_1_p", "b_1_m", ..., "b_n_p", "b_n_m"],
    "parity": 0,
    "description": "Bosonic oscillators b_k^± with k=1,...,n"
  }
}
```

### `oscillator_relations`

```json
{
  "standard_fermion_anticommutators": {
    "description": "Canonical anticommutation relations (CAR) for the pair a_1^±",
    "relations": {
      "conjugate_pair": "{a_1^-, a_1^+} = 1",
      "nilpotency": "{a_1^+, a_1^+} = {a_1^-, a_1^-} = 0  (i.e. (a_1^±)^2 = 0)"
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
    "boson_fermion": "[b_i^±, a_1^±] = 0  (undeformed; deformed in Schema 2)"
  },
  "normal_order": "a_1_p < a_1_m < b_1_p < b_1_m < ... < b_n_p < b_n_m"
}
```

### `central_elements` (top-level)

```json
{
  "kappa": {"label": "kappa", "parity": 1, "relation": "kappa^2 = 0",
            "role": "odd central element carrying the inhomogeneous deformation (Schema 2+)"},
  "K": {"label": "K", "parity": 0, "relation": "K = 1",
        "role": "even central element of the pre-oscillator extension; identified with scalar 1, excluded from basis"}
}
```

### `basis`

```json
{
  "even": ["H_1", ..., "H_{n+1}", "E_2del{k}_p"..., "E_del{i}_del{j}_pp"...,
           "E_2del{k}_m"..., "E_del{i}_del{j}_mm"..., "E_del{i}_del{j}_pm"..., "E_del{i}_del{j}_mp"...],
  "odd": ["E_eps1_del{k}_pp"..., "E_eps1_del{k}_pm"..., "E_eps1_del{k}_mp"..., "E_eps1_del{k}_mm"...],
  "ordering_convention": "PBW: κ < [odd] < [even]  (K = 1 is excluded)"
}
```

Concrete lists for n=1,2,3: `handover/notation.md` §5.

### `parity`

Map label → 0/1. All `H_*`, `E_2del*`, `E_del*_del*` are 0; all `E_eps1_del*` are 1.

### `generator_realization`

```json
{
  "description": "Standard form with oscillator normal order",
  "ordering": "a_1_p, a_1_m, b_1_p, b_1_m, ..., b_n_p, b_n_m",
  "realizations": {
    "H_1": {"standard_form": [{"words": ["a_1_p","a_1_m"], "coeff": "1"},
                               {"words": ["b_1_p","b_1_m"], "coeff": "1"}],
            "frappat_form": "a_1^+ a_1^- + b_1^+ b_1^-", "parity": 0},
    "H_{n+1}": {"standard_form": [{"words": ["b_n_p","b_n_m"], "coeff": "-1"},
                                   {"words": [], "coeff": "-1/2"}],
                "frappat_form": "-b_n^+ b_n^- - 1/2", "parity": 0},
    "E_2del{k}_p": {"standard_form": [{"words": ["b_k_p","b_k_p"], "coeff": "1/2"}], "parity": 0},
    "E_eps1_del{k}_pm": {"standard_form": [{"words": ["a_1_p","b_k_m"], "coeff": "1"}],
                         "frappat_form": "a_1^+ b_k^-", "parity": 1}
  }
}
```

`words` is a normally ordered oscillator monomial; `[]` is the identity ($K=1$).
`coeff` is an exact rational written as a string.

### `structure_constants`

List of all non-zero graded brackets $[X,Y\} = \sum_Z c^Z_{XY} Z$ over **ordered** pairs
$(X,Y)$ (both $(X,Y)$ and $(Y,X)$ are stored so that anti-symmetry is checkable):

```json
[{"X": "E_eps1_del1_pm", "Y": "E_eps1_del1_mp", "Z": "H_1", "coeff": "1", "sign_rule": "graded"}]
```

`sign_rule: "graded"` means $[X,Y\} = XY - (-1)^{p(X)p(Y)}YX$, evaluated in the oscillator algebra
and decomposed in the basis. Since the Cartan elements are super-symmetrized, no
$K$ (constant) component ever occurs; generators MUST raise an error if one does.

### `metadata`

```json
{"generated_by": "src/C_generators.py", "generation_date": "YYYY-MM-DD",
 "references": ["Frappat et al. (2000), Dictionary on Lie Algebras and Superalgebras",
                "Bakalov and Sullivan (2017)"],
 "notation": "handover/notation.md"}
```

---

## Compatibility with the B(m,n) v5.0 schema

| Key | B(0,n) v5.0 | C(n+1) | Compatible? |
|---|---|---|---|
| `schema_version` | `"5.0"` | `"5.0"` | identical |
| `algebra` | family B, m=0 | family C, **m=1**; adds `dimension_formulas` | superset (additive key) |
| `oscillator_generators` | `supplementary_fermion` + `bosons` | `fermions` + `bosons` | `bosons` identical; fermion key renamed by design (readers must branch on `algebra.family`) |
| `oscillator_relations` | `supplementary_fermion_relation` | `standard_fermion_anticommutators` | `bosonic_commutators` identical; `mixed_commutators` same shape |
| `central_elements` | (prose only) | top-level key | additive; B(0,n) files can add it without breaking readers |
| `basis` / `parity` | `even`, `odd`, `ordering_convention` | same keys, same `κ < odd < even` convention | identical shape |
| `generator_realization` | words over `a_0, b_k_*` | words over `a_1_*, b_k_*` | identical shape |
| `structure_constants` | `{X,Y,Z,coeff,sign_rule}` | same | identical shape |
| `metadata` | | adds `notation` | additive |

A reader written for B(0,n) that reads `basis`, `parity`, and `structure_constants` works
unchanged on C(n+1) files. Only code that inspects the fermionic oscillator sector must branch
on `algebra.family`.

## File naming

`C_{n}_structure.json`, `C_{n}_gamma.json`, `C_{n}_evaluated.json`, `C_{n}_coboundary.json`
in `data/`, with $n\in\{1,2,3\}$ the bosonic rank. (The v5.0 per-gb suffix `_<gb>` of
Schemas 3/4 is replaced by storing all evaluated profiles inside one file, keyed by profile name.)

---

## Schema 2: Inhomogeneous deformation (`C_{n}_gamma.json`) — added in I05

```json
{
  "schema_version": "5.0", "layer": 2,
  "algebra": {"family": "C", "m": 1, "n": n, "cartan_type": "C(n+1)", "structure_file": "C_{n}_structure.json"},
  "gb_matrix": {
    "shape": [2, 2n], "rows": ["a_1_p", "a_1_m"], "cols": ["b_1_p", "b_1_m", ..., "b_n_m"],
    "entries": [["gb_p_1_p", "gb_p_1_m", ...], ["gb_m_1_p", "gb_m_1_m", ...]],
    "parameter_count": 4n, "parameter_parity": 1, "parity_note": "...",
    "relation": "[b_j^s, a_1^sigma] = - gb_{sigma}_{j}_{s} * kappa"
  },
  "inhomogeneous_deformation": {
    "convention": "[X,Y]_gamma = [X,Y]_0 + kappa * gamma(X,Y), kappa written on the left",
    "gamma": [{"X": "E_eps1_del1_pp", "Y": "E_eps1_del1_pp", "Z": "E_eps1_del1_pp", "coeff": {"gb_p_1_p": "2"}}],
    "central_component": [{"X": "E_eps1_del1_pp", "Y": "H_1", "Z": "K", "coeff": {"gb_p_1_p": "1"}}]
  },
  "metadata": {...}
}
```
`coeff` is a linear form in the gb parameters: $\gamma_{XY}^{Z} = \sum_{g} \mathrm{coeff}[g]\cdot g$.
`central_component` holds the component along $K=1$ (constant term of the oscillator polynomial).

---

## Schema 3: Evaluated structure (`C_{n}_evaluated.json`) — added in I06

```json
{
  "schema_version": "5.0", "layer": 3,
  "algebra": {..., "structure_file": "C_{n}_structure.json", "gamma_file": "C_{n}_gamma.json"},
  "convention": "[X,Y]_gamma = [X,Y]_0 + kappa * gamma(X,Y) with gb substituted",
  "gb_matrix_layout": {"rows": [...], "cols": [...], "entries": [[...], [...]]},
  "profiles": {
    "all_plus": {
      "gb_values": {"gb_p_1_p": 1, ...},
      "gb_matrix_values": [[1, 1, ...], [1, 1, ...]],
      "gamma": [{"X": ..., "Y": ..., "Z": ..., "coeff": "2"}],
      "central_component": [{"X": ..., "Y": ..., "Z": "K", "coeff": "1"}],
      "n_gamma_entries": 92, "n_central_entries": 20
    },
    "...": {}
  },
  "metadata": {...}
}
```
Profiles: `zero`, `all_plus`, `all_minus`, `row_sign`, `col_sign`, `checkerboard`,
`index_parity`, `single_p_1_p`, `random_signs` (definitions in `src/C_evaluate.py`).
