# JSON Schema Specification — C(n+1) = osp(2|2n) extension of v5.0

This document is the complete, standalone specification of the JSON layers for
$C(n+1)=\mathfrak{osp}(2|2n)$. It extends the B(0,n) v5.0 specification
(`docs/math/B0n_schema_v5.md`). Notation: `handover/notation.md`.

Status: Schema 1 — Issue I02; Schema 2 — Issue I05; Schema 3 — Issue I06; Schema 4 — Issue I07.

---

## 0. Layers and file naming

`n` in file names is always the **bosonic rank** (C(2) = osp(2|2) → `n=1`).

| Layer | File | Contents | Producer |
|---|---|---|---|
| Schema 1 | `data/C_{n}_structure.json` | basis, parity, realization, undeformed structure constants | `src/C_generators.py` |
| Schema 2 | `data/C_{n}_gamma.json` | symbolic inhomogeneous deformation γ (linear in gb) | `src/C_gamma.py` |
| Schema 3 | `data/C_{n}_evaluated.json` | γ evaluated at representative gb sign profiles | `src/C_evaluate.py` |
| Schema 4 | `data/C_{n}_coboundary.json` | coboundary δf of a generic odd map f (linear in φ) | `src/C_coboundary.py` |

Files are produced for n = 1, 2, 3. (The B(0,n) spec suggests per-gb file names
`*_evaluated_<gb>.json`; for C(n+1) the issues prescribe `C_{n}_evaluated.json` and
`C_{n}_coboundary.json`, so all gb profiles are stored inside one file — see Schemas 3/4.)

---

## 1. Schema 1: Algebra Structure (`C_{n}_structure.json`)

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

`central_elements` is a **top-level** key (new compared with the B(0,n) top-level list).

### 1.2 `schema_version`
`"5.0"`. The C(n+1) extension is additive (one new top-level key, new sub-keys); the
family is discriminated by `algebra.family`.

### 1.3 `algebra` (example n = 1)

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
  "dimension_formulas": {
    "even": "2n^2 + n + 1",
    "odd": "4n",
    "total": "2n^2 + 5n + 1"
  },
  "dimension": { "total": 8, "even": 4, "odd": 4 }
}
```

| n | cartan_type | osp | even | odd | total |
|---|---|---|---|---|---|
| 1 | C(2) | osp(2\|2) | 4 | 4 | 8 |
| 2 | C(3) | osp(2\|4) | 11 | 8 | 19 |
| 3 | C(4) | osp(2\|6) | 22 | 12 | 34 |

### 1.4 `oscillator_generators`

```json
{
  "fermions": {
    "m": 1,
    "count": 2,
    "labels": ["a_1_p", "a_1_m"],
    "parity": 1,
    "description": "Standard fermionic pair a_1^± (CAR); replaces the B(0,n) supplementary fermion a_0."
  },
  "bosons": {
    "n": 1,
    "count": 2,
    "labels": ["b_1_p", "b_1_m"],
    "parity": 0,
    "description": "Bosonic oscillators b_k^± with k=1,...,n (CCR)."
  }
}
```
`bosons.labels` = `b_1_p, b_1_m, ..., b_n_p, b_n_m`, `bosons.count = 2n`.

### 1.5 `oscillator_relations`

```json
{
  "standard_fermion_anticommutators": {
    "description": "Canonical anticommutation relations for the fermionic pair",
    "relations": {
      "conjugate_pair": "{a_1^-, a_1^+} = K = 1",
      "same_type": "{a_1^±, a_1^±} = 0, i.e. (a_1^±)^2 = 0"
    }
  },
  "bosonic_commutators": {
    "description": "Canonical commutation relations for bosonic oscillators",
    "relations": {
      "same_type": "[b_i^±, b_j^±] = 0 for all i, j",
      "conjugate_pair": "[b_i^-, b_j^+] = δ_{ij} K = δ_{ij}"
    }
  },
  "mixed_commutators": {
    "boson_fermion": "[b_j^s, a_1^σ] = 0 (undeformed). The inhomogeneous deformation (Schema 2) sets [b_j^s, a_1^σ] = -gb_{σ,j,s} κ."
  }
}
```

### 1.6 `central_elements` (top level)

```json
{
  "kappa": {
    "label": "kappa",
    "parity": 1,
    "relations": ["kappa is central (supercommutes with everything)", "kappa^2 = 0"],
    "role": "Odd central element carrying the inhomogeneous deformation: [X,Y]_γ = [X,Y]_0 + κ γ(X,Y)."
  },
  "K": {
    "label": "K",
    "parity": 0,
    "value": "1",
    "role": "Even central element of the pre-oscillator algebra (value of [b^-,b^+] and {a^-,a^+}); identified with 1, excluded from basis and PBW ordering."
  }
}
```
Note: for C(n+1) `kappa` has parity **1** (the B(0,n) spec text listing κ with parity 0 is not
followed; parity 1 is mandated by Issue I02 and by `B0n_definition.md` §3).

### 1.7 `basis`

```json
{
  "even": ["H_1", "H_2", "E_2del1_p", "E_2del1_m"],
  "odd": ["E_eps1_del1_pp", "E_eps1_del1_pm", "E_eps1_del1_mp", "E_eps1_del1_mm"],
  "ordering_convention": "PBW: κ < [odd] < [even]  (K = 1 is excluded)",
  "global_order": ["E_eps1_del1_pp", "E_eps1_del1_pm", "E_eps1_del1_mp", "E_eps1_del1_mm",
                   "H_1", "H_2", "E_2del1_p", "E_2del1_m"]
}
```
Rules (n general):
- `odd` = `E_eps1_del{k}_pp` (k=1..n), then `_pm`, `_mp`, `_mm`.
- `even` = `H_1..H_{n+1}`, `E_2del{k}_p`, `E_del{i}_del{j}_pp`, `E_2del{k}_m`,
  `E_del{i}_del{j}_mm`, `E_del{i}_del{j}_pm`, `E_del{i}_del{j}_mp` ($i<j$ lexicographic).
- `global_order` = `odd + even` (the PBW order and the index order used by Schemas 2–4).

### 1.8 `parity`
Map label → 0/1: every `E_eps1_*` is 1, every `H_*`, `E_2del*`, `E_del*_del*` is 0.

### 1.9 `generator_realization`

```json
{
  "description": "Standard form (normal-ordered oscillator words) with K = 1",
  "ordering": "a_1_p, a_1_m, b_1_p, b_1_m, ..., b_n_p, b_n_m",
  "realizations": {
    "H_1": {
      "standard_form": [
        {"words": ["a_1_p", "a_1_m"], "coeff": "1"},
        {"words": ["b_1_p", "b_1_m"], "coeff": "1"}
      ],
      "frappat_form": "a_1^+ a_1^- + b_1^+ b_1^-",
      "root": "0",
      "parity": 0
    },
    "H_2": {
      "standard_form": [
        {"words": ["b_1_p", "b_1_m"], "coeff": "-1"},
        {"words": [], "coeff": "-1/2"}
      ],
      "frappat_form": "-b_1^+ b_1^- - 1/2",
      "root": "0",
      "parity": 0,
      "note": "Terminal Cartan H_{n+1}; constant term from symmetric ordering"
    },
    "E_eps1_del1_pm": {
      "standard_form": [{"words": ["a_1_p", "b_1_m"], "coeff": "1"}],
      "frappat_form": "a_1^+ b_1^-",
      "root": "eps1-del1",
      "parity": 1
    }
  }
}
```
Every basis element has an entry (no `{k}` templates in data files). Words are normal-ordered
w.r.t. `ordering`; the empty word is the constant term.

### 1.10 `structure_constants`

List of non-zero coefficients of the undeformed graded bracket
$[X,Y] = XY - (-1)^{p(X)p(Y)}YX = \sum_Z c_{XY}^Z Z$:

```json
[
  {"X": "H_1", "Y": "E_eps1_del1_pp", "Z": "E_eps1_del1_pp", "coeff": "2", "sign_rule": "graded"}
]
```
- **All ordered pairs** (X, Y) are stored (both $[X,Y]$ and $[Y,X]$), so graded antisymmetry
  $c_{YX}^Z = -(-1)^{p(X)p(Y)}c_{XY}^Z$ can be checked from data.
- `Z` is always a basis label: the generator asserts that the constant ($K$) part of every
  undeformed bracket vanishes.
- Entries are sorted by (index X, index Y, index Z) in `global_order`.

### 1.11 `metadata`

```json
{
  "generated_by": "src/C_generators.py",
  "generation_date": "YYYY-MM-DD",
  "conventions": "handover/notation.md",
  "references": [
    "Frappat, Sciarrino, Sorba (2000), Dictionary on Lie Algebras and Superalgebras",
    "Bakalov and Sullivan (2017)"
  ]
}
```

### 1.12 Compatibility with B(m,n) v5.0

| Key | B(0,n) v5.0 | C(n+1) | Compatible? |
|---|---|---|---|
| `schema_version` | `"5.0"` | `"5.0"` | same |
| `algebra` | family B, m=0 | family C, m=1, + `dimension_formulas` | superset (new optional key) |
| `oscillator_generators` | `supplementary_fermion`, `bosons` | `fermions`, `bosons` | `bosons` identical; fermion key renamed (readers must branch on `family`) |
| `oscillator_relations` | `supplementary_fermion_relation` | `standard_fermion_anticommutators` | `bosonic_commutators` identical; `mixed_commutators` same key |
| `central_elements` | mentioned only in notes | top-level, κ (parity 1), K (parity 0) | new key; B readers ignore it |
| `basis` | even/odd/ordering_convention | same + `global_order` | superset |
| `parity` | label→int | label→int | same |
| `generator_realization` | `a_0` words | `a_1_p/a_1_m` words, + `root` | same structure |
| `structure_constants` | X/Y/Z/coeff/sign_rule | identical record format | same |
| `metadata` | | + `conventions` | superset |

A B(0,n) reader that only uses `basis`, `parity`, `structure_constants` works unchanged on
C(n+1) files.

### 1.13 Validation rules (checked by tests)
1. `len(basis.even) == 2n^2+n+1`, `len(basis.odd) == 4n`, equal to `algebra.dimension`.
2. `parity` keys = basis; odd labels ↔ parity 1.
3. Every structure constant has $p(Z) = p(X)+p(Y) \bmod 2$.
4. Re-expanding $\sum_Z c^Z_{XY}\,\mathrm{real}(Z)$ reproduces the oscillator bracket exactly.
5. Graded antisymmetry and super Jacobi hold (Issue I04).

---

## 2. Schema 2: Inhomogeneous deformation (`C_{n}_gamma.json`)

Defined in Issue I05. Mathematical source: `docs/math/C_inhomogeneous_definition.md`.

```json
{
  "schema_version": "5.0",
  "layer": 2,
  "algebra": {"family": "C", "m": 1, "n": 1, "cartan_type": "C(2)", "osp": "osp(2|2)"},
  "structure_ref": "C_1_structure.json",
  "basis_order": ["E_eps1_del1_pp", "...", "E_2del1_m"],
  "parity": {"E_eps1_del1_pp": 1, "...": 0},
  "inhomogeneous_deformation": {
    "description": "...",
    "bracket_convention": "[X,Y]_γ = [X,Y]_0 + κ γ(X,Y), κ written on the left; [X,Y] graded commutator",
    "gb_matrix": {
      "rows": ["a_1_p", "a_1_m"],
      "columns": ["b_1_p", "b_1_m"],
      "symbols": [["gb_p_1_p", "gb_p_1_m"], ["gb_m_1_p", "gb_m_1_m"]],
      "count": 4, "shape": [2, 2],
      "defining_relation": "[b_j^s, a_1^σ] = -gb_{σ,j,s} κ   (σ = row, (j,s) = column)",
      "parameter_parity": 1,
      "parity_note": "..."
    },
    "gamma_target_space": "g ⊕ C K; an entry with Z = 'K' is the central part",
    "gamma_parity_rule": "p(Z) = p(X) + p(Y) + 1 mod 2",
    "symmetry": "γ(Y,X) = -(-1)^{p(X)p(Y)} γ(X,Y); all ordered pairs are stored",
    "linearity": "γ is exactly linear in gb",
    "gamma": [
      {"X": "E_eps1_del1_pp", "Y": "E_eps1_del1_pp", "Z": "E_eps1_del1_pp",
       "coeff": {"gb_p_1_p": "2"}, "expr": "2*gb_p_1_p"}
    ],
    "statistics": {"entries": 112, "central_entries": 20, "nonzero_pairs": 54, "parameters": 4}
  },
  "metadata": {"generated_by": "src/C_gamma.py", "generation_date": "YYYY-MM-DD", "...": "..."}
}
```
- `gamma[i].coeff` maps gb symbols to rational strings; γ^Z_{XY} = Σ_g coeff[g]·g.
- `Z = "K"` records the central part (the coefficient of κK = κ). It is kept for completeness;
  triviality in I07/I08 is tested modulo this part ("up to scalar") and, separately, with it.
- gb symbols: `gb_{σ}_{j}_{s}`, σ, s ∈ {p, m}.
