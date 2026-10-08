# JSON Schema Specification: C(n+1) = osp(2|2n), v5.0 Extension

This document specifies the four-layer JSON schema for $C(n+1)$, extending the B(0,n) v5.0 schema.
File naming: `C_{n}_{layer}.json` where `n` is the bosonic rank and `layer` ∈ {`structure`, `gamma`, `evaluated`, `coboundary`}.

---

## Layer 1 — `C_{n}_structure.json`

### Top-level keys

```
schema_version, algebra, central_elements, oscillator_generators,
oscillator_relations, basis, parity, generator_realization,
structure_constants, metadata
```

### `schema_version`

```json
"schema_version": "5.0"
```

### `algebra`

```json
{
  "family": "C",
  "m": 1,
  "n": <bosonic rank>,
  "cartan_type": "C(n+1)",
  "alternative_notation": {
    "osp": "osp(2|2n)",
    "dimension_formula": "osp(2m|2n) with m=1"
  },
  "dimension": {
    "total": <2n^2+5n+1>,
    "even": <2n^2+n+1>,
    "odd": <4n>
  }
}
```

**Dimension formulas**: even $= 2n^2+n+1$, odd $= 4n$, total $= 2n^2+5n+1$.

| $n$ | even | odd | total | Algebra |
|---|---|---|---|---|
| 1 | 4 | 4 | 8 | C(2) = osp(2\|2) |
| 2 | 11 | 8 | 19 | C(3) = osp(2\|4) |
| 3 | 22 | 12 | 34 | C(4) = osp(2\|6) |

**B(m,n) compatibility**: set `family="C"`, `m=1`. The `dimension_formula` key documents the osp(2m|2n) formula. All other structural keys remain in the same positions as the B(0,n) schema.

### `central_elements` (new top-level key for C(n+1))

```json
"central_elements": {
  "K": {
    "label": "K",
    "parity": 0,
    "description": "Even central element; identified with scalar 1 in all representations.",
    "in_basis": false
  },
  "kappa": {
    "label": "kappa",
    "parity": 1,
    "description": "Odd nilpotent central element of the inhomogeneous extension; kappa^2=0.",
    "in_basis": false
  }
}
```

`in_basis: false` means K and κ are excluded from PBW basis lists but **may appear as `Z` in `structure_constants`** when the bracket produces a central contribution (e.g., coefficients of K from {E_{ε+δk}, E_{-ε-δk}}).

### `oscillator_generators`

```json
{
  "fermions": {
    "m": 1,
    "labels": ["a1p", "a1m"],
    "parity": 1,
    "description": "Standard fermionic pair a_1^+, a_1^- with CAR {a_1^-, a_1^+}=1."
  },
  "bosons": {
    "count": <2n>,
    "n": <n>,
    "labels": ["b1p","b1m",...,"bnp","bnm"],
    "description": "Bosonic oscillators b_k^± for k=1,...,n."
  }
}
```

**Difference from B(0,n)**: `supplementary_fermion` key replaced by `fermions` key with m=1 and CAR relations. The `supplementary_fermion.relation` (`a_0^2 = 1/2`) does not apply.

### `oscillator_relations`

```json
{
  "standard_fermion_anticommutators": {
    "description": "CAR for the standard fermionic pair",
    "relations": {
      "anticommutator": "{a1m, a1p} = 1",
      "nilpotency": "a1p * a1p = 0",
      "nilpotency_m": "a1m * a1m = 0"
    }
  },
  "bosonic_commutators": {
    "description": "CCR for bosonic oscillators",
    "relations": {
      "conjugate_pair": "[bkm, bkp] = 1 (same k)",
      "other": "[bkp, blp] = 0, [bkm, blm] = 0, [bkp, blm] = 0 for k != l"
    }
  },
  "mixed_commutators": {
    "boson_fermion": "[bkp, a1p] = [bkp, a1m] = [bkm, a1p] = [bkm, a1m] = 0"
  }
}
```

### `basis`

PBW ordering: $\kappa < [\text{odd}] < [\text{even}]$.

```json
{
  "even": [
    "H_1", ..., "H_{n+1}",
    "E_2del1_p", ..., "E_2del{n}_p",
    "E_del1_del2_pp", ...,
    "E_2del1_m", ..., "E_2del{n}_m",
    "E_del1_del2_mm", ...,
    "E_del1_del2_pm", "E_del1_del2_mp", ...
  ],
  "odd": [
    "E_eps1_del1_pp", "E_eps1_del1_pm", "E_eps1_del1_mp", "E_eps1_del1_mm",
    ...,
    "E_eps1_del{n}_pp", "E_eps1_del{n}_pm", "E_eps1_del{n}_mp", "E_eps1_del{n}_mm"
  ],
  "ordering_convention": "PBW: kappa < [odd] < [even]; K excluded (in_basis=false)"
}
```

### `parity`

All even generators have parity 0; all odd generators (`E_eps1_del{k}_{..}`) have parity 1. K has parity 0 but is not in the basis. κ has parity 1 but is not in the basis.

### `generator_realization`

```json
{
  "description": "Normal-ordered oscillator words; ordering: a1p, a1m, b1p, b1m, ..., bnp, bnm",
  "realizations": {
    "H_1": {"standard_form": [{"words": ["a1p","a1m"], "coeff": "1"},
                               {"words": ["b1p","b1m"], "coeff": "1"}],
             "frappat_form": "a_1^+ a_1^- + b_1^+ b_1^-", "parity": 0},
    "H_k (2<=k<=n)": {"standard_form": [{"words": ["b(k-1)p","b(k-1)m"], "coeff": "1"},
                                          {"words": ["bkp","bkm"], "coeff": "-1"}],
                        "frappat_form": "b_{k-1}^+ b_{k-1}^- - b_k^+ b_k^-", "parity": 0},
    "H_{n+1}": {"standard_form": [{"words": ["bnp","bnm"], "coeff": "-1"},
                                    {"words": [], "coeff": "-1/2"}],
                 "frappat_form": "-b_n^+ b_n^- - 1/2", "parity": 0,
                 "note": "The constant -1/2 reflects the central element K=-1/2 in the a_0 → a_1^± replacement."},
    "E_eps1_del{k}_pp": {"standard_form": [{"words": ["a1p","bkp"], "coeff": "1"}],
                          "frappat_form": "a_1^+ b_k^+", "parity": 1},
    "E_eps1_del{k}_pm": {"standard_form": [{"words": ["a1p","bkm"], "coeff": "1"}],
                          "frappat_form": "a_1^+ b_k^-", "parity": 1},
    "E_eps1_del{k}_mp": {"standard_form": [{"words": ["a1m","bkp"], "coeff": "1"}],
                          "frappat_form": "a_1^- b_k^+", "parity": 1},
    "E_eps1_del{k}_mm": {"standard_form": [{"words": ["a1m","bkm"], "coeff": "1"}],
                          "frappat_form": "a_1^- b_k^-", "parity": 1},
    "E_2del{k}_p": {"standard_form": [{"words": ["bkp","bkp"], "coeff": "1"}],
                     "frappat_form": "(b_k^+)^2", "parity": 0},
    "E_2del{k}_m": {"standard_form": [{"words": ["bkm","bkm"], "coeff": "1"}],
                     "frappat_form": "(b_k^-)^2", "parity": 0},
    "E_del{i}_del{j}_pp (i<j)": {"standard_form": [{"words": ["bip","bjp"], "coeff": "1"}],
                                    "frappat_form": "b_i^+ b_j^+", "parity": 0},
    "E_del{i}_del{j}_mm (i<j)": {"standard_form": [{"words": ["bim","bjm"], "coeff": "1"}],
                                    "frappat_form": "b_i^- b_j^-", "parity": 0},
    "E_del{i}_del{j}_pm (i<j)": {"standard_form": [{"words": ["bip","bjm"], "coeff": "1"}],
                                    "frappat_form": "b_i^+ b_j^-", "parity": 0},
    "E_del{i}_del{j}_mp (i<j)": {"standard_form": [{"words": ["bim","bjp"], "coeff": "1"}],
                                    "frappat_form": "b_i^- b_j^+", "parity": 0}
  }
}
```

### `structure_constants`

List of non-zero graded brackets $[X, Y\} = \sum_Z c_Z \cdot Z$.

Each entry:
```json
{
  "X": "<label>",
  "Y": "<label>",
  "result": [
    {"Z": "<label or K>", "coeff": "<rational string>"}
  ],
  "sign_rule": "graded"
}
```

The `result` is a list to allow multiple basis elements (e.g., when a bracket gives $c_1 H_j + c_2 K$). For simple cases with a single term, the list has one entry.

**Key structure constant families**:

1. Cartan-root: $[H_k, E_\alpha] = \lambda_k(\alpha) E_\alpha$ (eigenvalue, no K).
2. Odd-odd with K: $\{E_{\varepsilon+\delta_k}, E_{-\varepsilon-\delta_k}\} = N_{b_k} = \sum_{j=k+1}^n H_j - H_{n+1} - \frac{1}{2}K$.
3. Odd-odd without K: $\{E_{\varepsilon-\delta_k}, E_{-\varepsilon+\delta_k}\} = H_1 - H_2 - \cdots - H_k$ (pure Cartan).
4. Even-even: $[E_{2\delta_k}, E_{-2\delta_k}] = 4H_{n+1} - 4\sum_{j=k+1}^n H_j$ (no K).
5. Even-even: $[E_{\delta_i+\delta_j}, E_{-(\delta_i+\delta_j)}] = -N_{b_i} - N_{b_j} - 1$ (expressed in H_j, no K).

---

## Layer 2 — `C_{n}_gamma.json`

### Top-level structure

```json
{
  "schema_version": "5.0",
  "algebra": { ... },
  "inhomogeneous_deformation": {
    "gb_matrix": {
      "description": "4n deformation parameters indexed by fermion sign and boson index/sign",
      "parameters": [
        {"label": "gb_pp_k", "fermion": "a1p", "boson": "bkp", "parity": 1},
        {"label": "gb_pm_k", "fermion": "a1p", "boson": "bkm", "parity": 1},
        {"label": "gb_mp_k", "fermion": "a1m", "boson": "bkp", "parity": 1},
        {"label": "gb_mm_k", "fermion": "a1m", "boson": "bkm", "parity": 1}
      ]
    },
    "deformed_relation": "[bks, a1sigma] = -gb_{sigma,k,s} * kappa",
    "gamma_coefficients": [ ... ]
  }
}
```

The `gamma_coefficients` list stores entries `{"X": ..., "Y": ..., "Z": ..., "coeff_expr": "<polynomial in gb parameters>"}`.

---

## Layer 3 — `C_{n}_evaluated.json`

Substitutes concrete values for all gb parameters and evaluates gamma_coefficients to rational numbers.

```json
{
  "schema_version": "5.0",
  "algebra": { ... },
  "gb_assignment": {"gb_pp_1": "1", "gb_pm_1": "1", ...},
  "evaluated_gamma": [
    {"X": ..., "Y": ..., "Z": ..., "coeff": "<rational>"}
  ]
}
```

---

## Layer 4 — `C_{n}_coboundary.json`

```json
{
  "schema_version": "5.0",
  "algebra": { ... },
  "coboundary_map_f": {
    "description": "Odd linear map f: g -> g parameterized by phi coefficients",
    "phi_matrix": [
      {"from": "<basis_elem>", "to": "<basis_elem>", "coeff": "<value>"}
    ]
  },
  "delta_f_coefficients": [
    {"X": ..., "Y": ..., "Z": ..., "coeff": "<rational>"}
  ]
}
```

---

## Compatibility with B(0,n) v5.0

| Key | B(0,n) | C(n+1) | Change |
|---|---|---|---|
| `algebra.family` | `"B"` | `"C"` | updated |
| `algebra.m` | `0` | `1` | updated |
| `oscillator_generators` | `supplementary_fermion` + `bosons` | `fermions` + `bosons` | key renamed |
| `oscillator_relations` | `supplementary_fermion_relation` | `standard_fermion_anticommutators` | key replaced |
| `central_elements` | not present (K implicit) | top-level key, K + κ | added |
| `basis.odd` | `E_del{k}_p/m` | `E_eps1_del{k}_{pp/pm/mp/mm}` | 2n→4n generators |
| `structure_constants[].result` | single `{Z, coeff}` | list `[{Z,coeff},...]` | extended for K |
| File pattern | `B_n_structure.json` | `C_{n}_structure.json` | prefix changed |
