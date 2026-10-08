# JSON Schema Specification for C(n+1) = osp(2|2n) (v5.0 extension)

This document specifies the complete 4-layer JSON schema for
$C(n+1) = \mathfrak{osp}(2|2n)$. It extends the B(0,n) v5.0 schema
(`docs/math/B0n_schema_v5.md`) and is the normative reference for the files in `data/`.

Conventions (labels, PBW order, basis lists) are defined in `handover/notation.md`.

| Layer | File | Produced by | Issue |
|---|---|---|---|
| Schema 1 | `data/C_{n}_structure.json` | `src/C_generators.py` | I03 |
| Schema 2 | `data/C_{n}_gamma.json` | `src/C_gamma.py` | I05 |
| Schema 3 | `data/C_{n}_evaluated.json` | `src/C_evaluate.py` | I06 |
| Schema 4 | `data/C_{n}_coboundary.json` | `src/C_coboundary.py` | I07 |

`n` is always the **bosonic rank** (C(2) = osp(2|2) is `n=1`, C(3) is `n=2`, C(4) is `n=3`).

---

## Schema 1: Algebra structure (`C_{n}_structure.json`)

### Top-level keys

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

Compared with B(0,n) v5.0 there is exactly **one new top-level key**, `central_elements`.
All other keys keep their B(0,n) names and types, so a B(0,n) v5.0 reader can load a
C(n+1) file after ignoring the unknown key.

### `schema_version`

`"5.0"` (unchanged; the C(n+1) extension is backward compatible, see "Compatibility").

### `algebra`

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
  "dimension": { "total": 8, "even": 4, "odd": 4 },
  "even_subalgebra": "so(2) + sp(2n)"
}
```

* `cartan_type` is `"C(n+1)"` with the value of n+1 substituted.
* `m` is always `1` (fixed rule).
* `dimension_formulas` is new (B(0,n) kept the formulas only in the spec text).

| n | even | odd | total |
|---|---|---|---|
| 1 | 4 | 4 | 8 |
| 2 | 11 | 8 | 19 |
| 3 | 22 | 12 | 34 |

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
    "n": 1,
    "count": 2,
    "labels": ["b_1_p", "b_1_m"],
    "parity": 0,
    "description": "Bosonic oscillators b_k^± with k=1,...,n"
  }
}
```

The B(0,n) key `supplementary_fermion` is **removed**; it is replaced by `fermions`.
`bosons` is unchanged.

### `oscillator_relations`

```json
{
  "standard_fermion_anticommutators": {
    "description": "Canonical anticommutation relations for the fermionic pair",
    "relations": {
      "conjugate_pair": "{a_1^-, a_1^+} = 1",
      "same_type": "{a_1^±, a_1^±} = 0  (i.e. (a_1^±)^2 = 0)"
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
    "boson_fermion": "[b_k^±, a_1^±] = 0  (undeformed; Schema 2 deforms this to -gb·kappa)"
  },
  "normal_order": "kappa < a_1_p < a_1_m < b_1_p < b_1_m < ... < b_n_p < b_n_m"
}
```

`supplementary_fermion_relation` is replaced by `standard_fermion_anticommutators`.

### `central_elements` (new top-level key)

```json
{
  "kappa": {
    "label": "kappa",
    "parity": 1,
    "relation": "kappa^2 = 0",
    "central": "[kappa, X} = 0 for all X (anticommutes with odd oscillators as an associative element)",
    "role": "formal odd parameter of the inhomogeneous deformation (Schema 2); absent from Schema 1 brackets",
    "in_basis": false
  },
  "K": {
    "label": "K",
    "parity": 0,
    "relation": "K = 1 (identified with the scalar identity)",
    "role": "even central element of the oscillator extension A = V + CK + C kappa; appears as a target of gamma in Schema 2",
    "in_basis": false
  }
}
```

Neither element is in `basis.even`/`basis.odd`. `K` may appear as a value of `"Z"` in
Schema 2–4 entries (see below); `kappa` never appears as a `"Z"` because it is factored out
of $\gamma$.

### `basis`

```json
{
  "even": ["H_1", "H_2", "E_2del1_p", "E_2del1_m"],
  "odd": ["E_eps1_del1_pp", "E_eps1_del1_pm", "E_eps1_del1_mp", "E_eps1_del1_mm"],
  "cartan": ["H_1", "H_2"],
  "pbw_order": ["E_eps1_del1_pp", "E_eps1_del1_pm", "E_eps1_del1_mp", "E_eps1_del1_mm",
                "H_1", "H_2", "E_2del1_p", "E_2del1_m"],
  "ordering_convention": "PBW: kappa < [odd] < [even]  (K = 1 is excluded)"
}
```

`even`, `odd`, `ordering_convention` are as in B(0,n). `cartan` and `pbw_order` are new
informational keys. The list order inside `even` and `odd` is the PBW order of
`handover/notation.md` §4.

### `parity`

Map label → 0/1 for every basis element (even: 0, odd: 1).

### `generator_realization`

```json
{
  "description": "Standard form with oscillator normal ordering",
  "ordering": "kappa, a_1_p, a_1_m, b_1_p, b_1_m",
  "realizations": {
    "H_1": {
      "standard_form": [
        {"words": ["a_1_p", "a_1_m"], "coeff": "1"},
        {"words": ["b_1_p", "b_1_m"], "coeff": "1"}
      ],
      "frappat_form": "a_1^+ a_1^- + b_1^+ b_1^-",
      "parity": 0
    },
    "H_2": {
      "standard_form": [
        {"words": ["b_1_p", "b_1_m"], "coeff": "-1"},
        {"words": [], "coeff": "-1/2"}
      ],
      "frappat_form": "-b_1^+ b_1^- - 1/2",
      "parity": 0,
      "note": "Terminal Cartan; the constant is required for closure"
    },
    "E_eps1_del1_pp": {
      "standard_form": [{"words": ["a_1_p", "b_1_p"], "coeff": "1"}],
      "frappat_form": "a_1^+ b_1^+",
      "parity": 1
    }
  }
}
```

Every basis element has an entry. `words` are in oscillator normal order; the empty word
is the scalar 1 (= K). Coefficients are rational strings.

### `structure_constants`

List of **all** non-zero graded brackets for **all ordered pairs** $(X, Y)$ of basis elements:

```json
{"X": "H_1", "Y": "E_eps1_del1_pp", "Z": "E_eps1_del1_pp", "coeff": "1", "sign_rule": "graded"}
```

meaning $[X, Y\} = \sum_Z \mathrm{coeff}\cdot Z$ with $[X,Y\} = XY - (-1)^{p(X)p(Y)}YX$.
Both $(X,Y)$ and $(Y,X)$ are stored, so graded antisymmetry can be verified from the file.
`Z` is always a basis label in Schema 1 (never `K`; this is asserted by the generator).

### `metadata`

```json
{
  "generated_by": "src/C_generators.py",
  "generation_date": "YYYY-MM-DD",
  "notation": "handover/notation.md",
  "references": [
    "Frappat, Sciarrino, Sorba (2000), Dictionary on Lie Algebras and Superalgebras, arXiv:hep-th/9607161",
    "Bakalov and Sullivan (2017)"
  ]
}
```

---

## Compatibility with the B(m,n) / B(0,n) v5.0 schema

| Key | B(0,n) v5.0 | C(n+1) | Compatibility |
|---|---|---|---|
| `schema_version` | "5.0" | "5.0" | identical |
| `algebra.family` | "B" | "C" | readers switch on this |
| `algebra.m` | 0 | 1 | same type |
| `algebra.dimension_formulas` | absent | present | additive |
| `oscillator_generators.supplementary_fermion` | present | **absent** | readers must test for `fermions` when family == "C" |
| `oscillator_generators.fermions` | absent | present | additive |
| `oscillator_relations.supplementary_fermion_relation` | present | absent | replaced by `standard_fermion_anticommutators` |
| `central_elements` | absent (B(0,n) mentions it in prose only) | top-level | additive |
| `basis.even/odd/ordering_convention` | present | present | identical types; `cartan`, `pbw_order` additive |
| `parity`, `generator_realization`, `structure_constants`, `metadata` | present | present | identical types |

Rule: everything that exists in B(0,n) v5.0 and still makes sense for C(n+1) keeps its name and
type; family-specific keys are replaced (fermion sector) and new information is only ever added.
A generic reader can therefore handle both families by branching on `algebra.family`.

---

## Schema 2: Inhomogeneous deformation (`C_{n}_gamma.json`) — defined in I05

Mathematical input (`docs/math/C_inhomogeneous_definition.md`): the mixed oscillator relation
is deformed to $[b_k^s, a_1^\sigma] = -\mathrm{gb}_{\sigma,k,s}\,\kappa$ with $\kappa$ odd, central,
$\kappa^2 = 0$. For basis elements $X, Y$ the bracket computed in $U(A)$ splits uniquely as
$[X,Y\}_\gamma = [X,Y\}_0 + \kappa\,\gamma(X,Y)$ (with $\kappa$ written leftmost), and
$\gamma(X,Y) \in \mathfrak g \oplus \mathbb C K$.

### Top-level keys

```json
{
  "schema_version": "5.0",
  "layer": 2,
  "algebra": { "family": "C", "m": 1, "n": 1, "cartan_type": "C(2)", "dimension": {...} },
  "schema1_file": "C_1_structure.json",
  "deformation": { ... },
  "gb_matrix": { ... },
  "inhomogeneous_deformation": { ... },
  "consistency": { ... },
  "metadata": { ... }
}
```

### `deformation`

```json
{
  "type": "inhomogeneous",
  "oscillator_relation": "[b_k^s, a_1^sigma] = -gb_{sigma,k,s} * kappa   (sigma, s in {+,-})",
  "bracket": "[X, Y}_gamma = [X, Y}_0 + kappa * gamma(X, Y)",
  "kappa": {"parity": 1, "relation": "kappa^2 = 0", "central": true},
  "gb_parity": 1,
  "gb_treatment": "gb parameters are treated as formal commuting scalars ...",
  "gamma_target": "g + C K  (K = even central element, scalar 1)",
  "gamma_parity_rule": "|gamma(X,Y)| = |X| + |Y| + 1 mod 2 (kappa carries parity 1)"
}
```

### `gb_matrix`

The $2 \times 2n$ matrix of deformation parameters:

```json
{
  "shape": [2, 2],
  "rows": ["a_1_p", "a_1_m"],
  "columns": ["b_1_p", "b_1_m"],
  "labels": [["gb_a1p_b1p", "gb_a1p_b1m"], ["gb_a1m_b1p", "gb_a1m_b1m"]],
  "count": 4,
  "index_convention": "gb_a1{sigma}_b{k}{s} = gb_{sigma,k,s}, rows: a_1_p (sigma=+), a_1_m (sigma=-)"
}
```

### `inhomogeneous_deformation`

```json
{
  "description": "gamma(X,Y) = sum_Z coeff * Z, coeff linear in gb; all ordered pairs with nonzero gamma",
  "coefficient_format": {"coeff": "sympy expression string", "linear_form": "{gb_label: rational string}"},
  "entries": [
    {"X": "H_2", "Y": "E_eps1_del1_pp", "Z": "H_2",       "coeff": "-gb_a1p_b1p",  "linear_form": {"gb_a1p_b1p": "-1"}},
    {"X": "H_2", "Y": "E_eps1_del1_pp", "Z": "E_2del1_p", "coeff": "gb_a1p_b1m",   "linear_form": {"gb_a1p_b1m": "1"}},
    {"X": "H_2", "Y": "E_eps1_del1_pp", "Z": "K",         "coeff": "gb_a1p_b1p/2", "linear_form": {"gb_a1p_b1p": "1/2"}}
  ]
}
```

* `Z` ranges over the basis **and** `"K"`. Every coefficient is a homogeneous linear form in the
  `gb_*` symbols; `linear_form` is the machine-readable version of `coeff`.
* Both orders $(X,Y)$ and $(Y,X)$ are stored; $\gamma(X,Y) = -(-1)^{|X||Y|}\gamma(Y,X)$.
* Parity rule: $|\gamma(X,Y)| = |X|+|Y|+1$, because $\kappa$ is odd.

### `consistency`

```json
{
  "zeroth_order_equals_schema1": true,
  "gamma_graded_antisymmetric": true,
  "entries_total": 112,
  "entries_with_Z_K": 20,
  "pairs_with_nonzero_gamma": 54
}
```

The generator refuses to write the file unless the $\kappa$-free part of every deformed bracket
equals the Schema 1 table and $\gamma$ is graded antisymmetric.

## Schema 3: Evaluated structure (`C_{n}_evaluated.json`) — defined in I06

A Schema 3 file is Schema 2 with a concrete numeric assignment substituted for the
$4n$ parameters. The representative assignment (`all_plus`, every $\mathrm{gb}=1$) is stored
without suffix as `C_{n}_evaluated.json`; other sign profiles use `C_{n}_evaluated_<profile>.json`.

Profiles provided by `src/C_evaluate.py`:

| profile | assignment |
|---|---|
| `all_plus` (representative) | all $\mathrm{gb}_{\sigma,k,s} = 1$ |
| `zero` | all $0$ (control: undeformed) |
| `single` | $\mathrm{gb}_{+,1,+} = 1$, all others $0$ |
| `alternating` | $+1$ if $\sigma = s$, $-1$ otherwise |
| `random` | deterministic pseudo-random values in $\{-2,-1,1,2\}$ (seed `20261009+n`) |

```json
{
  "schema_version": "5.0",
  "layer": 3,
  "algebra": { ... as Schema 2 ... },
  "schema1_file": "C_1_structure.json",
  "schema2_file": "C_1_gamma.json",
  "profile": "all_plus",
  "gb_assignment": {"gb_a1p_b1p": "1", "gb_a1p_b1m": "1", "gb_a1m_b1p": "1", "gb_a1m_b1m": "1"},
  "gb_matrix": {"rows": ["a_1_p", "a_1_m"], "columns": ["b_1_p", "b_1_m"], "values": [["1","1"],["1","1"]]},
  "evaluated_gamma": {
    "description": "gamma(X,Y) = sum_Z coeff * Z with gb substituted; Z in basis or K",
    "entries": [ {"X": "H_2", "Y": "E_eps1_del1_pp", "Z": "K", "coeff": "1/2"}, ... ]
  },
  "deformed_structure_constants": {
    "description": "[X,Y}_gamma = sum_Z (coeff_0 + kappa * coeff_kappa) * Z",
    "entries": [ {"X": "H_2", "Y": "E_eps1_del1_pp", "Z": "E_eps1_del1_pp", "coeff_0": "1", "coeff_kappa": "0"}, ... ]
  },
  "summary": {"gamma_entries": 112, "gamma_entries_with_Z_K": 20, "pairs_with_nonzero_gamma": 54},
  "metadata": { ... }
}
```

* `evaluated_gamma.entries` have rational-string `coeff`; terms that evaluate to 0 are dropped.
* `deformed_structure_constants.entries` merge Schema 1 (`coeff_0`) and the evaluated $\gamma$
  (`coeff_kappa`) per $(X,Y,Z)$, so a single list describes the full deformed bracket.
* Consistency rule: re-substituting `gb_assignment` into the Schema 2 `coeff` strings must
  reproduce `evaluated_gamma.entries` exactly, and `coeff_0` must equal Schema 1.

## Schema 4: Coboundary structure (`C_{n}_coboundary.json`) — defined in I07

*(filled in by Issue I07)*
