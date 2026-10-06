# JSON Schema Specification — C(n+1) = osp(2|2n) Extension (Schema 1)

This document specifies the **v5.0 JSON schema** fields for $C(n+1)=\mathfrak{osp}(2|2n)$,
extending the $B(0,n)$ base schema (`docs/math/B0n_schema_v5.md`). It is produced for **Issue I02**
and governs the generator output of Issues I03–I07.

The schema keeps the 4-layer architecture:

| Layer | File pattern | Contents |
|---|---|---|
| Schema 1 | `C_{n}_structure.json` | Algebra structure, basis, parity, realization, structure constants |
| Schema 2 | `C_{n}_gamma.json` | Inhomogeneous deformation (γ-structure) |
| Schema 3 | `C_{n}_evaluated.json` | Numerically evaluated deformation for a chosen gb profile |
| Schema 4 | `C_{n}_coboundary.json` | Coboundary data $\delta f$ for triviality verification |

**File naming (mandatory):** `C_{n}_*.json`, where `n` is the **bosonic rank** (C(2) → `C_1`,
C(3) → `C_2`, C(4) → `C_3`).

---

## Top-level keys (Schema 1)

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

The only **new top-level key** relative to $B(0,n)$ is `central_elements` (promoted to top level
per the I02 unified rule).

### `schema_version`
`"5.0"` — unchanged from $B(0,n)$; the C(n+1) data is schema-compatible.

### `algebra`  (mandatory fields)

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
  "dimension": {
    "formula": { "even": "2n^2 + n + 1", "odd": "4n", "total": "2n^2 + 5n + 1" },
    "total": 19,
    "even": 11,
    "odd": 4
  }
}
```

- `family = "C"`, `m = 1` (explicit), `n` = bosonic rank.
- `cartan_type = "C(n+1)"`.
- Dimension formulas explicitly recorded: `even = 2n^2 + n + 1`, `odd = 4n`, `total = 2n^2 + 5n + 1`.

| C(n+1) | n | even | odd | total |
|---|---|---|---|---|
| C(2) | 1 | 4 | 4 | 8 |
| C(3) | 2 | 11 | 8 | 19 |
| C(4) | 3 | 22 | 12 | 34 |

### `oscillator_generators`  (two keys: `fermions`, `bosons`)

```json
{
  "fermions": {
    "m": 1,
    "count": 2,
    "labels": ["a_1_p", "a_1_m"],
    "description": "Standard fermionic CAR pair a_1^±; {a_1^-, a_1^+} = 1, (a_1^±)^2 = 0."
  },
  "bosons": {
    "n": 2,
    "count": 4,
    "labels": ["b_1_p", "b_1_m", "b_2_p", "b_2_m"],
    "description": "Bosonic oscillators b_k^± (k=1..n), [b_k^-, b_l^+] = δ_{kl}."
  }
}
```

The $B(0,n)$ `supplementary_fermion` key (the auxiliary $a_0$ with $a_0^2=\tfrac12$) is **removed**
and replaced by `fermions` (a genuine CAR pair with `m=1`).

### `oscillator_relations`  (CAR instead of supplementary relation)

```json
{
  "fermionic_anticommutators": {
    "description": "Standard CAR pair",
    "relations": {
      "car_pair": "{a_1^-, a_1^+} = 1",
      "nilpotency": "(a_1^+)^2 = 0, (a_1^-)^2 = 0"
    }
  },
  "bosonic_commutators": {
    "description": "Canonical commutation relations",
    "relations": {
      "same_type": "[b_i^±, b_j^±] = 0 for all i, j",
      "conjugate_pair": "[b_i^-, b_j^+] = δ_{ij}"
    }
  },
  "mixed_commutators": {
    "boson_fermion": "[b_k^±, a_1^σ] = 0   (undeformed; deformed in Schema 2)"
  }
}
```

### `central_elements`  (TOP-LEVEL key, mandatory)

```json
{
  "kappa": {
    "label": "kappa",
    "parity": 1,
    "nilpotency": "kappa^2 = 0",
    "description": "Odd central element; carrier of the inhomogeneous deformation (Schema 2)."
  },
  "K": {
    "label": "K",
    "parity": 0,
    "value": "1",
    "description": "Even central identity, identified with scalar 1; excluded from PBW basis."
  }
}
```

### `basis`

```json
{
  "even": ["H_1", "H_2", "H_3", "E_2del1_p", "E_2del2_p", "E_del1_del2_pp",
           "E_2del1_m", "E_2del2_m", "E_del1_del2_mm",
           "E_del1_del2_pm", "E_del1_del2_mp"],
  "odd":  ["E_eps1_del1_pp", "E_eps1_del2_pp", "E_eps1_del1_pm", "E_eps1_del2_pm",
           "E_eps1_del1_mp", "E_eps1_del2_mp", "E_eps1_del1_mm", "E_eps1_del2_mm"],
  "ordering_convention": "PBW: kappa < [odd] < [even]  (K = 1 excluded)"
}
```

PBW ordering is **Option A** from Issue I01: `kappa < [odd] < [even]`. Within even: Cartan
$H_1..H_{n+1}$, then `_p`/`_pp` raising block, then `_m`/`_mm` lowering block, then `_pm`/`_mp`
mixed block. Within odd: sign blocks `pp, pm, mp, mm`, each over $k=1..n$.

### `parity`

Map from every basis label to $\{0,1\}$: all `H_i`, `E_2del*`, `E_del*_del*_*` are even (`0`);
all `E_eps1_del*_**` are odd (`1`).

### `generator_realization`

Each generator is a list of oscillator words with rational coefficients (PBW normal-ordered).
Oscillator word ordering key: `a_1_p < b_1_p < b_2_p < ... < a_1_m < b_1_m < b_2_m < ...`
(creations before annihilations; fermion before bosons within each sign group).

```json
{
  "H_1": {"standard_form": [{"words": ["a_1_p","a_1_m"], "coeff": "1"},
                            {"words": ["b_1_p","b_1_m"], "coeff": "1"}],
          "frappat_form": "a_1^+ a_1^- + b_1^+ b_1^-", "parity": 0},
  "H_2": {"standard_form": [{"words": ["b_1_p","b_1_m"], "coeff": "1"},
                            {"words": ["b_2_p","b_2_m"], "coeff": "-1"}],
          "frappat_form": "b_1^+ b_1^- - b_2^+ b_2^-", "parity": 0},
  "H_3": {"standard_form": [{"words": ["b_2_p","b_2_m"], "coeff": "-1"},
                            {"words": [], "coeff": "-1/2"}],
          "frappat_form": "-b_2^+ b_2^- - 1/2", "parity": 0,
          "note": "Terminal Cartan H_{n+1}; carries normal-ordering constant -1/2."},
  "E_2del1_p":  {"standard_form": [{"words": ["b_1_p","b_1_p"], "coeff": "1"}],
                 "frappat_form": "(b_1^+)^2", "parity": 0},
  "E_eps1_del1_pp": {"standard_form": [{"words": ["a_1_p","b_1_p"], "coeff": "1"}],
                     "frappat_form": "a_1^+ b_1^+", "parity": 1}
}
```

(The example shows C(3); the realization for every label follows the table in `notation.md` §3.)

### `structure_constants`

List of non-zero graded brackets $[X,Y\} = \sum_Z c\, Z$ (one record per non-zero target $Z$):

```json
[
  { "X": "H_1", "Y": "E_eps1_del1_pp", "Z": "E_eps1_del1_pp",
    "coeff": "1", "sign_rule": "graded" }
]
```

- The bracket is the **graded commutator** $[X,Y\}=XY-(-1)^{p(X)p(Y)}YX$ evaluated in the
  oscillator (Weyl–Clifford) algebra; `sign_rule: "graded"`.
- A central contribution (multiple of identity) is recorded with `Z = "K"`.
- Only records with `X ≤ Y` in PBW order are stored; the opposite order follows from graded
  antisymmetry $[Y,X\}=-(-1)^{p(X)p(Y)}[X,Y\}$.

### `metadata`

```json
{
  "generated_by": "src/C_generators.py",
  "generation_date": "YYYY-MM-DD",
  "algebra": "C(n+1) = osp(2|2n)",
  "references": [
    "Frappat, Sciarrino, Sorba (2000), Dictionary on Lie Algebras and Superalgebras",
    "Bakalov and Sullivan (2017)"
  ]
}
```

---

## Compatibility with the B(m,n) schema

| Aspect | B(0,n) base | C(n+1) extension | Compatible? |
|---|---|---|---|
| `schema_version` | `"5.0"` | `"5.0"` | Yes (same version) |
| Top-level key set | no `central_elements` top-level | adds `central_elements` | **Additive** — B readers ignore the extra key |
| `algebra.family` | `"B"` | `"C"` | Yes (discriminator field) |
| `algebra.m` | `0` | `1` | Yes |
| Fermion key | `supplementary_fermion` ($a_0$) | `fermions` ($a_1^\pm$ CAR) | Mutually exclusive by `family` |
| Odd basis labels | `E_del{k}_p/m` | `E_eps1_del{k}_pp/pm/mp/mm` | Namespaced, no collision |
| Even basis labels | `H_i, E_2del*, E_del*_del*_*` | identical names | Yes |
| `structure_constants` record shape | `{X,Y,Z,coeff,sign_rule}` | identical | Yes |

**Compatibility rule:** the `family` + `m` fields are the discriminator. A consumer selects the
fermionic sector (`supplementary_fermion` for B, `fermions` for C) from `family`. All even-sector
labels and the record shapes are shared, so a generic Schema-1 reader works on both with only the
fermion branch switched. The new `central_elements` top-level key is additive and backward
compatible (B(0,n) consumers simply did not read it; it may be back-ported to B with `K` only).

## File naming convention (confirmed)

`C_{n}_structure.json`, `C_{n}_gamma.json`, `C_{n}_evaluated.json`, `C_{n}_coboundary.json`,
with `n` = bosonic rank. Concretely: C(2) → `C_1_*`, C(3) → `C_2_*`, C(4) → `C_3_*`.
