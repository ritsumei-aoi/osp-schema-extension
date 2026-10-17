# JSON Schema Specification for C(n+1) = osp(2|2n)

This document specifies the v5.0 JSON schema used for $C(n+1) = \mathfrak{osp}(2|2n)$ structure constants and algebra definitions. It extends the $B(0,n)$ v5.0 base schema to the $C(n+1)$ family with a standard fermionic pair $a_1^\pm$, explicit central elements, and the finalized charge-stratified PBW ordering.

---

## 1. Overview: 4-Layer Schema Architecture

The JSON data for each algebra $C(n+1)$ is organized into 4 layers of increasing computational depth:

| Layer | File pattern | Contents |
|---|---|---|
| Schema 1 | `C_{n}_structure.json` | Algebra structure: basis, parity, oscillator realization, structure constants |
| Schema 2 | `C_{n}_gamma.json` | Inhomogeneous deformation ($\gamma$-structure, $4n$ deformation parameters) |
| Schema 3 | `C_{n}_evaluated_<gb>.json` | Numerically evaluated structure constants for specific $\gamma$ parameters |
| Schema 4 | `C_{n}_coboundary_<gb>.json` | Coboundary data for triviality verification |

**Index Convention**: The integer `n` in file names represents the **bosonic rank** ($n \ge 1$):
- $n=1$: $C(2) = \mathfrak{osp}(2|2) \implies$ `C_1_structure.json`
- $n=2$: $C(3) = \mathfrak{osp}(2|4) \implies$ `C_2_structure.json`
- $n=3$: $C(4) = \mathfrak{osp}(2|6) \implies$ `C_3_structure.json`

---

## 2. Schema 1: Algebra Structure Specification

### 2.1 Top-Level Keys

Schema 1 files contain exactly the following top-level keys:

```json
{
  "schema_version": "5.0",
  "algebra": { ... },
  "central_elements": { ... },
  "oscillator_generators": { ... },
  "oscillator_relations": { ... },
  "basis": { ... },
  "parity": { ... },
  "generator_realization": { ... },
  "structure_constants": [ ... ],
  "metadata": { ... }
}
```

---

### 2.2 Detailed Key Definitions

#### (1) `schema_version`
```json
"schema_version": "5.0"
```

#### (2) `algebra`
Specifies the Lie superalgebra family, ranks, classification labels, and dimension invariants.

- `family`: `"C"`
- `m`: `1` (fermionic rank)
- `n`: integer (bosonic rank)
- `cartan_type`: `"C(n+1)"`
- `alternative_notation`:
  - `osp`: `"osp(2|2n)"`
  - `dimension_formula`: `"osp(2m|2n) with m=1: even = 2n^2 + n + 1, odd = 4n, total = 2n^2 + 5n + 1"`
- `dimension`:
  - `total`: $2n^2 + 5n + 1$
  - `even`: $2n^2 + n + 1$
  - `odd`: $4n$

*Example ($n=1$, $C(2) = \mathfrak{osp}(2|2)$)*:
```json
{
  "family": "C",
  "m": 1,
  "n": 1,
  "cartan_type": "C(2)",
  "alternative_notation": {
    "osp": "osp(2|2)",
    "dimension_formula": "osp(2m|2n) with m=1: even = 2n^2 + n + 1, odd = 4n, total = 2n^2 + 5n + 1"
  },
  "dimension": {
    "total": 8,
    "even": 4,
    "odd": 4
  }
}
```

*Summary across ranks $n=1, 2, 3$*:
| $n$ | Cartan Type | $\mathfrak{osp}(2m\|2n)$ | even ($\dim \mathfrak{g}_{\bar{0}}$) | odd ($\dim \mathfrak{g}_{\bar{1}}$) | total |
|---|---|---|---|---|---|
| 1 | `C(2)` | `osp(2\|2)` | 4 | 4 | 8 |
| 2 | `C(3)` | `osp(2\|4)` | 11 | 8 | 19 |
| 3 | `C(4)` | `osp(2\|6)` | 22 | 12 | 34 |

---

#### (3) `central_elements` (Standalone Top-Level Key)
Defines the central extension elements used in the algebraic framework.
- `kappa`: Odd nilpotent element ($p=1, \kappa^2=0$) parametrizing the inhomogeneous deformation.
- `K`: Even central identity element ($p=0, K=1$), recorded for formal schema completeness but excluded from PBW monomial basis.

```json
{
  "kappa": {
    "parity": 1,
    "nilpotent_order": 2,
    "relation": "kappa^2 = 0",
    "description": "Odd central nilpotent element carrier of inhomogeneous deformation parameter"
  },
  "K": {
    "parity": 0,
    "scalar_value": 1,
    "description": "Even central identity element (identified with scalar 1; excluded from PBW basis)"
  }
}
```

---

#### (4) `oscillator_generators`
Defines the fundamental oscillator degrees of freedom using two dedicated keys: `"fermions"` and `"bosons"`.

- `"fermions"`:
  - `count`: 2
  - `m`: 1
  - `labels`: `["a_1_p", "a_1_m"]`
  - `parity`: 1
  - `description`: `"Standard fermionic CAR pair a_1^± (replaces B(0,n) supplementary fermion a_0)"`
- `"bosons"`:
  - `count`: $2n$
  - `n`: bosonic rank $n$
  - `labels`: `["b_1_p", "b_1_m", ..., "b_{n}_p", "b_{n}_m"]`
  - `parity`: 0
  - `description`: `"Bosonic CCR oscillators b_i^± with i=1,...,n"`

*Example ($n=1$)*:
```json
{
  "fermions": {
    "count": 2,
    "m": 1,
    "labels": ["a_1_p", "a_1_m"],
    "parity": 1,
    "description": "Standard fermionic CAR pair a_1^± (replaces B(0,n) supplementary fermion a_0)"
  },
  "bosons": {
    "count": 2,
    "n": 1,
    "labels": ["b_1_p", "b_1_m"],
    "parity": 0,
    "description": "Bosonic CCR oscillators b_i^± with i=1,...,n"
  }
}
```

---

#### (5) `oscillator_relations`
Defines the algebraic commutation/anticommutation relations among the oscillators:

```json
{
  "fermionic_anticommutators": {
    "description": "Canonical anticommutation relations (CAR) for standard fermionic pair",
    "relations": {
      "same_type": "{a_1^±, a_1^±} = 0 (nilpotent: (a_1^±)^2 = 0)",
      "conjugate_pair": "{a_1^-, a_1^+} = 1"
    }
  },
  "bosonic_commutators": {
    "description": "Canonical commutation relations (CCR) for bosonic oscillators",
    "relations": {
      "same_type": "[b_i^±, b_j^±] = 0 for all i, j",
      "conjugate_pair": "[b_i^-, b_j^+] = δ_{ij}"
    }
  },
  "mixed_commutators": {
    "boson_fermion": "[b_i^±, a_1^±] = 0 (in undeformed algebra)"
  }
}
```

---

#### (6) `basis`
Specifies the PBW monomial ordering convention and provides explicit ordered lists for even and odd generators.

**Ordering Rule**:
$$\kappa < [\text{odd}] < [\text{even}]$$

- **Odd Stratum (Option 1: Charge-Stratified)**:
  Ordered by sign blocks $(++, +-, -+, --)$ with respect to $(\varepsilon, \delta_k)$, and by mode index $k = 1, \ldots, n$:
  `E_eps1_del{k}_pp` ($k=1..n$) $<$ `E_eps1_del{k}_pm` ($k=1..n$) $<$ `E_eps1_del{k}_mp` ($k=1..n$) $<$ `E_eps1_del{k}_mm` ($k=1..n$).
- **Even Stratum**:
  Cartans `H_1, ..., H_{n+1}`
  $<$ Positive long roots `E_2del{k}_p` ($k=1..n$)
  $<$ Positive cross roots `E_del{i}_del{j}_pp` ($1 \le i < j \le n$)
  $<$ Negative long roots `E_2del{k}_m` ($k=1..n$)
  $<$ Negative cross roots `E_del{i}_del{j}_mm` ($1 \le i < j \le n$)
  $<$ Mixed cross roots `E_del{i}_del{j}_pm`, `E_del{i}_del{j}_mp` ($1 \le i < j \le n$).

*Basis lists for $n=1, 2, 3$*:

##### $n=1$ ($C(2) = \mathfrak{osp}(2|2)$, even: 4, odd: 4)
```json
{
  "even": [
    "H_1", "H_2",
    "E_2del1_p",
    "E_2del1_m"
  ],
  "odd": [
    "E_eps1_del1_pp",
    "E_eps1_del1_pm",
    "E_eps1_del1_mp",
    "E_eps1_del1_mm"
  ],
  "ordering_convention": "PBW: κ < [odd: ++, +-, -+, --] < [even]"
}
```

##### $n=2$ ($C(3) = \mathfrak{osp}(2|4)$, even: 11, odd: 8)
```json
{
  "even": [
    "H_1", "H_2", "H_3",
    "E_2del1_p", "E_2del2_p",
    "E_del1_del2_pp",
    "E_2del1_m", "E_2del2_m",
    "E_del1_del2_mm",
    "E_del1_del2_pm", "E_del1_del2_mp"
  ],
  "odd": [
    "E_eps1_del1_pp", "E_eps1_del2_pp",
    "E_eps1_del1_pm", "E_eps1_del2_pm",
    "E_eps1_del1_mp", "E_eps1_del2_mp",
    "E_eps1_del1_mm", "E_eps1_del2_mm"
  ],
  "ordering_convention": "PBW: κ < [odd: ++, +-, -+, --] < [even]"
}
```

##### $n=3$ ($C(4) = \mathfrak{osp}(2|6)$, even: 22, odd: 12)
```json
{
  "even": [
    "H_1", "H_2", "H_3", "H_4",
    "E_2del1_p", "E_2del2_p", "E_2del3_p",
    "E_del1_del2_pp", "E_del1_del3_pp", "E_del2_del3_pp",
    "E_2del1_m", "E_2del2_m", "E_2del3_m",
    "E_del1_del2_mm", "E_del1_del3_mm", "E_del2_del3_mm",
    "E_del1_del2_pm", "E_del1_del2_mp",
    "E_del1_del3_pm", "E_del1_del3_mp",
    "E_del2_del3_pm", "E_del2_del3_mp"
  ],
  "odd": [
    "E_eps1_del1_pp", "E_eps1_del2_pp", "E_eps1_del3_pp",
    "E_eps1_del1_pm", "E_eps1_del2_pm", "E_eps1_del3_pm",
    "E_eps1_del1_mp", "E_eps1_del2_mp", "E_eps1_del3_mp",
    "E_eps1_del1_mm", "E_eps1_del2_mm", "E_eps1_del3_mm"
  ],
  "ordering_convention": "PBW: κ < [odd: ++, +-, -+, --] < [even]"
}
```

---

#### (7) `parity`
Mapping from generator label to $\mathbb{Z}_2$-degree ($0$ for even, $1$ for odd):

```json
{
  "H_1": 0, "H_2": 0,
  "E_2del1_p": 0, "E_2del1_m": 0,
  "E_eps1_del1_pp": 1, "E_eps1_del1_pm": 1,
  "E_eps1_del1_mp": 1, "E_eps1_del1_mm": 1
}
```

---

#### (8) `generator_realization`
Stores the standard normal-ordered form of each Lie superalgebra generator in terms of oscillators. Rational coefficients are represented as strings.

- `ordering`: `"a_1_p, a_1_m, b_1_p, b_1_m, ..."`
- Cartans:
  - `H_1`: $a_1^+ a_1^- + b_1^+ b_1^-$
    ```json
    {
      "standard_form": [
        {"words": ["a_1_p", "a_1_m"], "coeff": "1"},
        {"words": ["b_1_p", "b_1_m"], "coeff": "1"}
      ],
      "frappat_form": "a_1^+ a_1^- + b_1^+ b_1^-",
      "parity": 0
    }
    ```
  - `H_k` ($2 \le k \le n$): $b_{k-1}^+ b_{k-1}^- - b_k^+ b_k^-$
    ```json
    {
      "standard_form": [
        {"words": ["b_{k-1}_p", "b_{k-1}_m"], "coeff": "1"},
        {"words": ["b_k_p", "b_k_m"], "coeff": "-1"}
      ],
      "frappat_form": "b_{k-1}^+ b_{k-1}^- - b_k^+ b_k^-",
      "parity": 0
    }
    ```
  - `H_{n+1}`: $-b_n^+ b_n^- - 1/2$
    ```json
    {
      "standard_form": [
        {"words": ["b_n_p", "b_n_m"], "coeff": "-1"},
        {"words": [], "coeff": "-1/2"}
      ],
      "frappat_form": "-b_n^+ b_n^- - 1/2",
      "parity": 0
    }
    ```
- Even Roots:
  - `E_2del{k}_p`: $(b_k^+)^2$
  - `E_2del{k}_m`: $(b_k^-)^2$
  - `E_del{i}_del{j}_pp`: $b_i^+ b_j^+$
  - `E_del{i}_del{j}_pm`: $b_i^+ b_j^-$
  - `E_del{i}_del{j}_mp`: $b_i^- b_j^+$
  - `E_del{i}_del{j}_mm`: $b_i^- b_j^-$
- Odd Roots:
  - `E_eps1_del{k}_pp`: $a_1^+ b_k^+$
  - `E_eps1_del{k}_pm`: $a_1^+ b_k^-$
  - `E_eps1_del{k}_mp`: $a_1^- b_k^+$
  - `E_eps1_del{k}_mm`: $a_1^- b_k^-$

---

#### (9) `structure_constants`
Array of all non-zero graded brackets $[X, Y\} = \sum_Z c_{XY}^Z Z$ with rational coefficients:

```json
[
  {
    "X": "H_1",
    "Y": "E_eps1_del1_pp",
    "Z": "E_eps1_del1_pp",
    "coeff": "2",
    "sign_rule": "graded"
  }
]
```

---

#### (10) `metadata`
Provenance tracking information:

```json
{
  "generated_by": "build_C_structure_constants.py",
  "generation_date": "YYYY-MM-DD",
  "references": [
    "Frappat et al. (2000), Dictionary on Lie Algebras and Superalgebras",
    "Bakalov and Sullivan (2017)"
  ]
}
```

---

## 3. Comparison and Compatibility with B(0,n) Schema

| Schema Key / Field | B(0,n) Schema (v5.0) | C(n+1) Schema (v5.0 Extension) | Architectural Rationale |
|---|---|---|---|
| `algebra.family` | `"B"` | `"C"` | Lie superalgebra family identification |
| `algebra.m` | `0` | `1` | Fermionic rank ($m=1$ for $osp(2|2n)$) |
| `algebra.cartan_type` | `"B(0,n)"` | `"C(n+1)"` | Frappat Cartan classification |
| `algebra.dimension` | even $= 2n^2+n$, odd $= 2n$ | even $= 2n^2+n+1$, odd $= 4n$ | $\mathfrak{so}(2)$ adds $+1$ even dim; CAR pair adds $2 \times 2n$ odd roots |
| `central_elements` | Implicit / schema note | **Top-level key** with `kappa` ($p=1$) and `K` ($p=0$) | Standardized explicit central extensions |
| `oscillator_generators` | `supplementary_fermion` (`a_0`, $a_0^2=1/2$) and `bosons` | `fermions` (`m=1`, `a_1_p, a_1_m`) and `bosons` | Standard fermionic creation/annihilation algebra |
| `oscillator_relations` | `supplementary_fermion_relation` | `fermionic_anticommutators` (CAR) | $\{a_1^-, a_1^+\} = 1$, $(a_1^\pm)^2 = 0$ |
| `basis.even` | $H_1, \ldots, H_n$ ($n$ Cartans) + roots | $H_1, \ldots, H_{n+1}$ ($n+1$ Cartans) + roots | Rank $n+1$; $H_1$ contains $a_1^+ a_1^- + b_1^+ b_1^-$ |
| `basis.odd` | `E_del{k}_p/m` ($2n$ generators) | `E_eps1_del{k}_pp/pm/mp/mm` ($4n$ generators) | Fully graded by $(\varepsilon, \delta_k)$ signs |
| `basis.ordering_convention` | `κ < [odd] < [even]` | `κ < [odd: ++, +-, -+, --] < [even]` | Option 1 charge-stratified convention |
| File naming | `B_n_structure.json` | `C_{n}_structure.json` | Indexed by bosonic rank $n$ |
