# JSON Schema Specification for C(n+1) = osp(2|2n) (v5.0 extension)

This document is the complete, standalone schema specification for the
C(n+1) = osp(2|2n) data produced in this repository. It extends the B(0,n)
v5.0 schema (`docs/math/B0n_schema_v5.md`) and keeps the same 4-layer
architecture. Conventions (labels, ordering) are those of `handover/notation.md`.

Section 1 (Schema 1) was fixed in Issue I02. Sections 2–4 (Schemas 2–4) are
specified here as well and are the formats implemented in I05, I06, I07.

---

## 0. Architecture, naming, and compatibility

| Layer | File pattern (C(n+1)) | Produced by | Contents |
|---|---|---|---|
| Schema 1 | `data/C_{n}_structure.json` | `src/C_generators.py` | basis, parity, oscillator realization, structure constants |
| Schema 2 | `data/C_{n}_gamma.json` | `src/C_gamma.py` | inhomogeneous deformation γ, symbolic in the gb parameters |
| Schema 3 | `data/C_{n}_evaluated.json`, `data/C_{n}_evaluated_<profile>.json` | `src/C_evaluate.py` | γ with concrete gb values substituted |
| Schema 4 | `data/C_{n}_coboundary.json` | `src/C_coboundary.py` | odd map f and coboundary δf data |

**File naming rule (mandatory)**: `n` is the **bosonic rank**. C(2)=osp(2|2) → `C_1_*.json`,
C(3)=osp(2|4) → `C_2_*.json`, C(4)=osp(2|6) → `C_3_*.json`.

**Backward compatibility with the B(m,n) / B(0,n) v5.0 schema.** All B(0,n) top-level
keys are kept with the same meaning (`schema_version`, `algebra`, `oscillator_generators`,
`oscillator_relations`, `basis`, `parity`, `generator_realization`, `structure_constants`,
`metadata`). Differences are confined to:

| Key | B(0,n) v5.0 | C(n+1) (this spec) |
|---|---|---|
| `algebra.family` / `algebra.m` | `"B"`, `0` | `"C"`, `1` |
| `algebra.dimension_formula` | even `2n^2+n`, odd `2n` | even `2n^2+n+1`, odd `4n` |
| `oscillator_generators` | `supplementary_fermion` (a_0) + `bosons` | `fermions` (a_1_p, a_1_m; m=1) + `bosons` |
| `oscillator_relations` | `supplementary_fermion_relation` | `fermionic_anticommutators` (CAR) |
| `central_elements` | (note only) | **new top-level key**: `kappa` (parity 1), `K` (parity 0) |
| `basis.odd` | `E_del{k}_p/m` (2n) | `E_eps1_del{k}_pp/pm/mp/mm` (4n) |
| `basis.even` | `H_1..H_n` + roots | `H_1..H_{n+1}` + roots (extra so(2) Cartan) |
| `generator_realization.ordering` | `a_0, b_1_p, ...` | `a_1_p, a_1_m, b_1_p, ...` |
| coefficients | rational strings | rational strings (no √2 appears for C(n+1)) |

A B(0,n) reader that ignores unknown keys can read a C(n+1) Schema 1 file; the only
B(0,n)-specific keys it would miss are the removed `supplementary_fermion*` keys, which are
replaced rather than renamed so that their absence is detectable.

**Coefficient encoding**: every numeric coefficient is a string holding an exact rational
(`"1"`, `"-1/2"`, `"4"`), parsable by Python `fractions.Fraction`.

---

## 1. Schema 1: Algebra Structure (`C_{n}_structure.json`)

### Top-level keys

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

`schema_layer` is new (integer 1–4) and optional for readers.

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
  "dimension_formula": {
    "even": "2n^2 + n + 1",
    "odd": "4n",
    "total": "2n^2 + 5n + 1"
  },
  "dimension": { "total": 19, "even": 11, "odd": 8 },
  "even_subalgebra": "so(2) x sp(4)",
  "rank": 3
}
```

`cartan_type` is `C(n+1)`; `rank` is $n+1$ (number of Cartan generators).

| $n$ | even | odd | total | cartan_type | osp |
|---|---|---|---|---|---|
| 1 | 4 | 4 | 8 | C(2) | osp(2\|2) |
| 2 | 11 | 8 | 19 | C(3) | osp(2\|4) |
| 3 | 22 | 12 | 34 | C(4) | osp(2\|6) |

### `oscillator_generators`

```json
{
  "fermions": {
    "m": 1,
    "count": 2,
    "labels": ["a_1_p", "a_1_m"],
    "parity": 1,
    "description": "Standard fermionic pair a_1^± with CAR {a_1^-, a_1^+} = 1"
  },
  "bosons": {
    "n": 2,
    "count": 4,
    "labels": ["b_1_p", "b_1_m", "b_2_p", "b_2_m"],
    "parity": 0,
    "description": "Bosonic oscillators b_k^± with k=1,...,n"
  }
}
```

### `oscillator_relations`

```json
{
  "fermionic_anticommutators": {
    "description": "Canonical anticommutation relations for the standard fermionic pair",
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
    "boson_fermion": "[b_i^±, a_1^±] = 0  (undeformed; see Schema 2 for the deformation)"
  }
}
```

### `central_elements` (top-level, new)

```json
{
  "kappa": {
    "label": "kappa",
    "parity": 1,
    "relations": "kappa^2 = 0; kappa x = (-1)^{p(x)} x kappa for homogeneous x",
    "role": "odd central element of the extension A = V ⊕ CK ⊕ Cκ; carries the inhomogeneous deformation [X,Y]_γ = [X,Y]_0 + κ γ(X,Y)",
    "in_basis": false
  },
  "K": {
    "label": "K",
    "parity": 0,
    "relations": "K = 1 (identified with the scalar identity)",
    "role": "even central element; appears as the Z-label of scalar components of γ and f",
    "in_basis": false
  }
}
```

Neither element is a basis element of $\mathfrak g$; both are excluded from PBW
ordering of the basis exactly as in B(0,n). `kappa` has parity 1 (mandatory rule of I02).

### `basis`

```json
{
  "even": ["H_1", "H_2", "H_3",
           "E_2del1_p", "E_2del2_p", "E_del1_del2_pp",
           "E_2del1_m", "E_2del2_m", "E_del1_del2_mm",
           "E_del1_del2_pm", "E_del1_del2_mp"],
  "odd":  ["E_eps1_del1_pp", "E_eps1_del2_pp", "E_eps1_del1_pm", "E_eps1_del2_pm",
           "E_eps1_del1_mp", "E_eps1_del2_mp", "E_eps1_del1_mm", "E_eps1_del2_mm"],
  "ordering_convention": "PBW: kappa < [odd] < [even]  (K = 1 is excluded)",
  "pbw_order": ["E_eps1_del1_pp", "...", "E_del1_del2_mp"],
  "cartan": ["H_1", "H_2", "H_3"],
  "roots": { "E_2del1_p": "2δ_1", "E_eps1_del1_pm": "ε-δ_1", "...": "..." }
}
```

`pbw_order` is the concatenation `odd + even` and is the canonical index order used by all
later layers. `roots` maps each non-Cartan generator to its root (string).

### `parity`

Map from every basis label to 0 or 1 (e.g. `"H_1": 0`, `"E_eps1_del1_pp": 1`).

### `generator_realization`

```json
{
  "description": "Normally ordered form in the oscillator algebra",
  "ordering": "a_1_p, a_1_m, b_1_p, b_1_m, b_2_p, b_2_m",
  "realizations": {
    "H_1": {
      "standard_form": [
        {"words": ["a_1_p", "a_1_m"], "coeff": "1"},
        {"words": ["b_1_p", "b_1_m"], "coeff": "1"}
      ],
      "frappat_form": "a_1^+ a_1^- + b_1^+ b_1^-",
      "parity": 0
    },
    "H_3": {
      "standard_form": [
        {"words": ["b_2_p", "b_2_m"], "coeff": "-1"},
        {"words": [], "coeff": "-1/2"}
      ],
      "frappat_form": "-b_2^+ b_2^- - 1/2",
      "parity": 0,
      "note": "Terminal Cartan; constant required for closure of [E_2del2_p, E_2del2_m]"
    },
    "E_eps1_del2_pm": {
      "standard_form": [{"words": ["a_1_p", "b_2_m"], "coeff": "1"}],
      "frappat_form": "a_1^+ b_2^-",
      "parity": 1
    }
  }
}
```

### `structure_constants`

List of non-zero graded brackets $[X, Y\} = \sum_Z c\, Z$, one entry per $(X, Y, Z)$,
for **all ordered pairs** $(X,Y)$ (both $(X,Y)$ and $(Y,X)$ are stored; graded
antisymmetry is thus verifiable from the data):

```json
{ "X": "E_2del1_p", "Y": "E_2del1_m", "Z": "H_2", "coeff": "4", "sign_rule": "graded" }
```

`sign_rule: "graded"` means $[X,Y\} = XY - (-1)^{p(X)p(Y)}YX$. Brackets never have a
$K$-component in Schema 1 (closure in $\mathfrak g$ is asserted by the generator).

### `metadata`

```json
{
  "generated_by": "src/C_generators.py",
  "generation_date": "2026-10-09",
  "notation": "handover/notation.md",
  "references": [
    "Frappat, Sciarrino, Sorba (2000), Dictionary on Lie Algebras and Superalgebras",
    "Bakalov and Sullivan (2017)"
  ]
}
```

---

## 2. Schema 2: Inhomogeneous deformation (`C_{n}_gamma.json`)

```json
{
  "schema_version": "5.0",
  "schema_layer": 2,
  "algebra": { ...same as Schema 1... },
  "source_structure": "C_2_structure.json",
  "central_elements": { ...same as Schema 1... },
  "gb_matrix": {
    "description": "Deformation parameters gb_{a_1^σ, b_k^s}; rows = fermions, columns = bosons",
    "shape": [2, 4],
    "rows": ["a_1_p", "a_1_m"],
    "cols": ["b_1_p", "b_1_m", "b_2_p", "b_2_m"],
    "parity": 1,
    "entries": [
      {"label": "gb_a1p_b1p", "fermion": "a_1_p", "boson": "b_1_p", "row": 0, "col": 0}
    ]
  },
  "deformed_oscillator_relations": {
    "boson_fermion": "[b_k^s, a_1^σ] = - gb_{a_1^σ, b_k^s} kappa",
    "unchanged": ["CAR of a_1^±", "CCR of b_k^±", "kappa central, kappa^2 = 0"]
  },
  "inhomogeneous_deformation": {
    "description": "[X,Y]_γ = [X,Y]_0 + kappa * γ(X,Y); γ(X,Y) ∈ g ⊕ C K, p(γ(X,Y)) = p(X)+p(Y)+1",
    "gamma_is_linear_in_gb": true,
    "gamma": [
      {"X": "E_eps1_del1_pm", "Y": "E_2del1_p", "Z": "H_2",
       "coeff": {"gb_a1p_b1p": "-2"}, "linear_form": "-2*gb_a1p_b1p"}
    ]
  },
  "metadata": { ... }
}
```

Each `gamma` entry gives $\gamma_{XY}^{Z}$ as a linear form in the $4n$ parameters
(`coeff` maps parameter label → rational string). `Z` may be `"K"` for scalar components.
All ordered pairs are stored.

### Parity bookkeeping (recorded ambiguity)

`C_inhomogeneous_definition.md` states that gb has parity 1 and `kappa` has parity 1.
In the computation the *product* $\mathrm{gb}\cdot\kappa$ is the odd, super-central symbol
(it anticommutes with $a_1^\pm$ and commutes with $b_k^\pm$); the gb coefficients are then
extracted as commuting scalars. The resulting $\gamma$ is independent of whether the
odd grading is attributed to gb (B(0,n) JSON convention: κ parity 0) or to κ (I02 rule:
κ parity 1). `gb_matrix.parity: 1` is kept as the documented label.

---

## 3. Schema 3: Evaluated deformation (`C_{n}_evaluated[_<profile>].json`)

```json
{
  "schema_version": "5.0",
  "schema_layer": 3,
  "algebra": { ... },
  "source_gamma": "C_2_gamma.json",
  "profile": "ones",
  "gb_assignment": {"gb_a1p_b1p": "1", "gb_a1p_b1m": "1", "...": "..."},
  "evaluated_gamma": [
    {"X": "E_eps1_del1_pm", "Y": "E_2del1_p", "Z": "H_2", "coeff": "-2"}
  ],
  "deformed_structure_constants": [
    {"X": "...", "Y": "...", "Z": "...", "coeff": "...", "kappa_order": 0},
    {"X": "...", "Y": "...", "Z": "...", "coeff": "...", "kappa_order": 1}
  ],
  "metadata": { ... }
}
```

`evaluated_gamma` is Schema 2's `gamma` with the linear forms evaluated at `gb_assignment`
(zero entries dropped). `deformed_structure_constants` lists the full deformed bracket,
`kappa_order` 0 entries being Schema 1's structure constants and `kappa_order` 1 entries
the evaluated γ. The default profile (`C_{n}_evaluated.json`) is `ones` (all gb = 1).

---

## 4. Schema 4: Coboundary structure (`C_{n}_coboundary.json`)

```json
{
  "schema_version": "5.0",
  "schema_layer": 4,
  "algebra": { ... },
  "source_structure": "C_2_structure.json",
  "coboundary_formula": "(δf)(X,Y) = (-1)^{p(X)} [X,f(Y)] - (-1)^{(p(X)+1)p(Y)} [Y,f(X)] - f([X,Y])",
  "odd_map_parameterization": {
    "description": "f(Z_j) = Σ_i φ_ij Z_i, p(Z_i) = p(Z_j) + 1; Z_i may also be K (scalar) when Z_j is odd",
    "phi_labels": ["phi[H_1][E_eps1_del1_pp]", "..."],
    "count": 176
  },
  "elementary_coboundaries": {
    "description": "δ(f_ij) for the elementary odd map f_ij: Z_j -> Z_i (all other basis elements -> 0); pairs stored with index(X) <= index(Y)",
    "table": [
      {"phi": "phi[H_1][E_eps1_del1_pp]", "X": "...", "Y": "...", "Z": "...", "coeff": "..."}
    ]
  },
  "candidate_map": {
    "description": "f_shift induced by the oscillator shift b_k^s -> b_k^s - kappa Σ_τ gb_{a_1^{-τ}, b_k^s} a_1^τ; coefficients linear in gb",
    "f": [ {"source": "E_2del1_p", "target": "E_eps1_del1_pp", "coeff": {"gb_a1m_b1p": "-2"}} ],
    "delta_f": [ {"X": "...", "Y": "...", "Z": "...", "coeff": {"gb_...": "..."}} ]
  },
  "metadata": { ... }
}
```

The elementary table is the matrix of the linear map $\delta: C^1_{\mathrm{odd}}(\mathfrak g,\mathfrak g)
\to C^2(\mathfrak g,\mathfrak g)$ in the basis; triviality of a given $\gamma$ is the solvability
of $\sum_{ij}\phi_{ij}\,\delta(f_{ij}) = \gamma$. The `candidate_map` block stores one explicit
odd map together with its coboundary for direct comparison with Schema 2/3.
