# JSON Schema Specification v5.0 — C(n+1) = osp(2|2n) extension

This document specifies the v5.0 JSON layers for $C(n+1)=\mathfrak{osp}(2|2n)$.
It is a complete, standalone specification derived from the B(0,n) v5.0 schema
(`docs/math/B0n_schema_v5.md`). Notation and labels are those of `handover/notation.md`.

## 0. Files and naming

| Layer | File | Produced by |
|---|---|---|
| Schema 1 (structure) | `data/C_{n}_structure.json` | `src/C_generators.py` (I03) |
| Schema 2 (γ-structure) | `data/C_{n}_gamma.json` | `src/C_gamma.py` (I05) |
| Schema 3 (evaluated) | `data/C_{n}_evaluated.json` | `src/C_evaluate.py` (I06) |
| Schema 4 (coboundary) | `data/C_{n}_coboundary.json` | `src/C_coboundary.py` (I07) |

`{n}` is the **bosonic rank**: C(2)=osp(2|2) → `C_1_*`, C(3)=osp(2|4) → `C_2_*`, C(4)=osp(2|6) → `C_3_*`.
Schema 3 holds all evaluated sign profiles of one rank in one file (see §3); the per-profile
B(0,n) pattern `B_n_evaluated_<gb>.json` is replaced by a `profiles` list to keep the file count fixed.

All rational coefficients are strings (`"1"`, `"-1/2"`); symbolic coefficients are strings in SymPy syntax.

---

## 1. Schema 1: Algebra structure (`C_{n}_structure.json`)

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
`central_elements` is new (top level) relative to B(0,n); all other keys keep their B(0,n) names.

### `algebra`
```json
{
  "family": "C",
  "m": 1,
  "n": 2,
  "cartan_type": "C(3)",
  "alternative_notation": {
    "osp": "osp(2|4)",
    "dimension_formula": "osp(2m|2n) with m=1; even = 2n^2 + n + 1, odd = 4n"
  },
  "dimension": {"total": 19, "even": 11, "odd": 8}
}
```
`cartan_type` is `C(n+1)`. Dimensions: n=1 → 4|4 (8), n=2 → 11|8 (19), n=3 → 22|12 (34).

### `oscillator_generators`
```json
{
  "fermions": {
    "count": 2, "m": 1,
    "labels": ["a_1_p", "a_1_m"],
    "parity": 1,
    "description": "Standard fermionic pair a_1^± (CAR)"
  },
  "bosons": {
    "count": 4, "n": 2,
    "labels": ["b_1_p", "b_1_m", "b_2_p", "b_2_m"],
    "parity": 0,
    "description": "Bosonic oscillators b_i^± with i=1,...,n (CCR)"
  }
}
```
(No `supplementary_fermion` key.)

### `oscillator_relations`
```json
{
  "standard_fermion_anticommutators": {
    "description": "Canonical anticommutation relations for the fermionic pair",
    "relations": {"conjugate_pair": "{a_1^-, a_1^+} = 1", "same_type": "{a_1^±, a_1^±} = 0  (a_1^± a_1^± = 0)"}
  },
  "bosonic_commutators": {
    "description": "Canonical commutation relations for bosonic oscillators",
    "relations": {"same_type": "[b_i^±, b_j^±] = 0 for all i, j", "conjugate_pair": "[b_i^-, b_j^+] = δ_{ij}"}
  },
  "mixed_commutators": {
    "boson_fermion": "[b_i^±, a_1^±] = 0  (undeformed; deformed in Schema 2: [b_j^s, a_1^σ] = -gb_{σ,j,s} κ)"
  }
}
```

### `central_elements` (top level)
```json
{
  "kappa": {"label": "kappa", "parity": 1, "relation": "kappa^2 = 0",
            "role": "odd central element carrying the inhomogeneous deformation (Schema 2+)"},
  "K": {"label": "K", "parity": 0, "value": "1",
        "role": "even central element; identified with the scalar 1, excluded from basis/PBW"}
}
```
Note: `B0n_definition.md` says κ is listed "with parity 0" in B(0,n)'s `central_elements`; for C(n+1) the
mandatory rule (I02) fixes `kappa.parity = 1`, which also agrees with the mathematics ($p(\kappa)=1$).

### `basis`
```json
{
  "even": ["H_1", "H_2", "H_3", "E_2del1_p", "E_2del2_p", "E_del1_del2_pp",
           "E_2del1_m", "E_2del2_m", "E_del1_del2_mm", "E_del1_del2_pm", "E_del1_del2_mp"],
  "odd":  ["E_eps1_del1_pp", "E_eps1_del2_pp", "E_eps1_del1_pm", "E_eps1_del2_pm",
           "E_eps1_del1_mp", "E_eps1_del2_mp", "E_eps1_del1_mm", "E_eps1_del2_mm"],
  "ordered": ["E_eps1_del1_pp", "...", "E_del1_del2_mp"],
  "ordering_convention": "PBW: kappa < [odd] < [even]  (K = 1 is excluded)"
}
```
`ordered` is the full PBW-ordered basis (odd block then even block); its index is the basis index used by
Schemas 2–4.

### `parity`
Map label → 0/1: all `H_*`, `E_2del*`, `E_del*_del*` are 0; all `E_eps1_del*` are 1.

### `generator_realization`
```json
{
  "description": "Standard form with PBW ordering of oscillator words",
  "ordering": "a_1_p, a_1_m, b_1_p, b_1_m, b_2_p, b_2_m",
  "realizations": {
    "H_1": {"standard_form": [{"words": ["a_1_p","a_1_m"], "coeff": "1"},
                              {"words": ["b_1_p","b_1_m"], "coeff": "1"}],
            "frappat_form": "a_1^+ a_1^- + b_1^+ b_1^-", "parity": 0},
    "H_3": {"standard_form": [{"words": ["b_2_p","b_2_m"], "coeff": "-1"},
                              {"words": [], "coeff": "-1/2"}],
            "frappat_form": "-b_2^+ b_2^- - 1/2", "parity": 0,
            "note": "Terminal Cartan H_{n+1}; constant from super-symmetrization"},
    "E_eps1_del1_pm": {"standard_form": [{"words": ["a_1_p","b_1_m"], "coeff": "1"}],
                       "frappat_form": "a_1^+ b_1^-", "parity": 1}
  }
}
```
Every basis element has an entry (no `{k}` templates in generated files).

### `structure_constants`
List of non-zero graded brackets $[X,Y\} = \sum_Z c\,Z$, one entry per non-zero $(X,Y,Z)$:
```json
{"X": "H_1", "Y": "E_eps1_del1_pp", "Z": "E_eps1_del1_pp", "coeff": "2", "sign_rule": "graded"}
```
- **All ordered pairs** $(X,Y)$ are stored (both $(X,Y)$ and $(Y,X)$), so that super-antisymmetry can be checked from the file.
- `sign_rule: "graded"` means $[X,Y\} = XY - (-1)^{p(X)p(Y)}YX$.
- The bracket is computed in the oscillator algebra and re-expanded in the basis; a non-zero $K$ component is
  an error (the basis is closed).

### `metadata`
```json
{"generated_by": "src/C_generators.py", "generation_date": "YYYY-MM-DD",
 "references": ["Frappat et al. (2000), Dictionary on Lie Algebras and Superalgebras",
                "Bakalov and Sullivan (2017)"],
 "notation": "handover/notation.md"}
```

### Compatibility with the B(m,n) schema

| Key | B(0,n) v5.0 | C(n+1) v5.0 | Compatible? |
|---|---|---|---|
| `schema_version` | `"5.0"` | `"5.0"` | same |
| `algebra` | family B, m=0 | family C, m=1, `cartan_type` `C(n+1)` | same keys |
| `oscillator_generators` | `supplementary_fermion`, `bosons` | `fermions`, `bosons` | `bosons` identical; fermion key renamed (readers must branch on `algebra.family`) |
| `oscillator_relations` | `supplementary_fermion_relation`, ... | `standard_fermion_anticommutators`, ... | `bosonic_commutators` identical |
| `central_elements` | (described in prose) | top-level key | additive |
| `basis` | `even`, `odd`, `ordering_convention` | same + `ordered` | additive |
| `parity`, `generator_realization`, `structure_constants`, `metadata` | — | same format | same |

A reader written for B(0,n) that only uses `basis`, `parity`, `structure_constants` works unchanged for C(n+1).

---

## 2. Schema 2: γ-structure (`C_{n}_gamma.json`) — defined in I05

Top-level keys: `schema_version`, `algebra` (copy), `basis_ref` (`C_{n}_structure.json` and the `ordered` basis),
`central_elements` (copy), `inhomogeneous_deformation`, `metadata`.

`inhomogeneous_deformation`:
- `relation`: `"[b_j^s, a_1^σ] = -gb_{σ,j,s} kappa"`
- `gb_matrix`: `{"rows": ["a_1_p","a_1_m"], "cols": ["b_1_p","b_1_m",...], "symbols": [[...],[...]], "parity": 1}`, 2 × 2n
- `gamma`: list of `{"X","Y","Z","coeff"}` with `coeff` a linear SymPy expression in the gb symbols:
  $[X,Y]_\gamma = [X,Y]_0 + \kappa\sum_Z \gamma_{XY}^Z Z$; `Z = "K"` records the central ($\kappa\cdot1$) part.

## 3. Schema 3: evaluated structure (`C_{n}_evaluated.json`) — defined in I06

`profiles`: list of `{"name", "gb_values": {symbol: value}, "gamma": [{"X","Y","Z","coeff"}...]}` with rational `coeff`.

## 4. Schema 4: coboundary (`C_{n}_coboundary.json`) — defined in I07

`odd_map`: the parametrization $f(Z_j)=\sum_i \phi_{ij}Z_i$ restricted to $p(Z_i)\neq p(Z_j)$;
`coboundary`: list of `{"X","Y","Z","coeff"}` with `coeff` a linear SymPy expression in the `phi_i_j`.
