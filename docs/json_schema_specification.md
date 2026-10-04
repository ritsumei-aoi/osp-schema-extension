# JSON Schema v5.0 Specification for $C(n+1) = \mathfrak{osp}(2|2n)$

This document specifies the v5.0 JSON schema used for the $C(n+1) = \mathfrak{osp}(2|2n)$ Lie superalgebra structure constants, deformation parameters, evaluated matrices, and coboundary structures.

---

## 1. File Naming Conventions

For a given bosonic rank $n$ (where $C(n+1) = \mathfrak{osp}(2|2n)$):
- **Schema 1 (Algebra Structure)**: `C_{n}_structure.json`
- **Schema 2 (Inhomogeneous Deformation / $\gamma$-structure)**: `C_{n}_gamma.json`
- **Schema 3 (Evaluated Structure Constants)**: `C_{n}_evaluated.json` (or `C_{n}_evaluated_<gb>.json`)
- **Schema 4 (Coboundary Data)**: `C_{n}_coboundary.json` (or `C_{n}_coboundary_<gb>.json`)

*Note*: For $C(2) = \mathfrak{osp}(2|2)$, $n=1$, file is `C_1_structure.json`.
For $C(3) = \mathfrak{osp}(2|4)$, $n=2$, file is `C_2_structure.json`.
For $C(4) = \mathfrak{osp}(2|6)$, $n=3$, file is `C_3_structure.json`.

---

## 2. Schema 1: Algebra Structure Specification

### 2.1 Top-Level Structure

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

### 2.2 Field Definitions

#### 1. `algebra`
- `family`: `"C"`
- `m`: `1` (fermionic rank)
- `n`: `<integer>` (bosonic rank, e.g. 1, 2, 3)
- `cartan_type`: `"C(n+1)"` (e.g. `"C(2)"`, `"C(3)"`, `"C(4)"`)
- `alternative_notation`:
  - `osp`: `"osp(2|2n)"`
  - `dimension_formula`: `"osp(2m|2n) with m=1"`
- `dimension`:
  - `total`: $2n^2 + 5n + 1$
  - `even`: $2n^2 + n + 1$
  - `odd`: $4n$

#### 2. `oscillator_generators`
- `fermions`:
  - `m`: `1`
  - `labels`: `["a_1_p", "a_1_m"]`
  - `description`: `"Standard CAR pair a_1^±"`
- `bosons`:
  - `n`: `<integer>`
  - `labels`: `["b_1_p", "b_1_m", ..., "b_n_p", "b_n_m"]`
  - `description`: `"Bosonic oscillators b_i^± with i=1,...,n"`

#### 3. `oscillator_relations`
- `standard_fermion_anticommutators`:
  - `description`: `"Canonical anticommutation relations (CAR)"`
  - `relations`: `{ "{a_1^-, a_1^+}": 1, "(a_1^±)^2": 0 }`
- `bosonic_commutators`:
  - `description`: `"Canonical commutation relations (CCR)"`
  - `relations`: `{ "[b_i^-, b_j^+]": "δ_{ij}", "[b_i^±, b_j^±]": 0 }`
- `mixed_commutators`:
  - `boson_fermion`: `"[b_i^±, a_1^±] = 0"`

#### 4. `central_elements` (Top-Level Key)
- `kappa`:
  - `label`: `"kappa"`
  - `parity`: `1`
  - `description`: `"Odd nilpotent element representing formal central extension parameter, kappa^2 = 0"`
- `K`:
  - `label`: `"K"`
  - `parity`: `0`
  - `description`: `"Even central identity element"`

#### 5. `basis`
- `even`: List of even generator names (Cartans `H_1, ..., H_{n+1}`, double roots `E_2delk_p/m`, mixed roots `E_deli_delj_pp/mm/pm/mp`).
- `odd`: List of odd generator names (`E_eps1_delk_pp/pm/mp/mm` for $k=1,\dots,n$).
- `ordering_convention`: `"PBW: κ < [odd] < [even]"`

#### 6. `parity`
Map from generator name to integer `0` (even) or `1` (odd).

#### 7. `generator_realization`
Map from generator name to oscillator representation:
```json
{
  "H_1": {
    "standard_form": [
      {"words": ["a_1_p", "a_1_m"], "coeff": "1"},
      {"words": ["b_1_p", "b_1_m"], "coeff": "1"}
    ],
    "frappat_form": "a_1^+ a_1^- + b_1^+ b_1^-",
    "parity": 0
  }
}
```

#### 8. `structure_constants`
List of non-zero graded brackets $[X, Y\} = \sum Z \text{ coeff}$:
```json
[
  {
    "X": "H_1",
    "Y": "E_eps1_del1_pp",
    "Z": "E_eps1_del1_pp",
    "coeff": "1",
    "sign_rule": "graded"
  }
]
```

#### 9. `metadata`
```json
{
  "generated_by": "src/C_generators.py",
  "generation_date": "2026-10-05",
  "references": [
    "Frappat et al. (2000), Dictionary on Lie Algebras and Superalgebras",
    "Bakalov and Sullivan (2017)"
  ]
}
```

---

## 3. Schema 2: Inhomogeneous Deformation ($\gamma$-Structure)

Top-level additions:
- `gb_matrix`: 2 x $2n$ matrix of deformation parameter labels `gb_{a_1_sigma, b_j_s}` ($\sigma \in \{p, m\}, s \in \{p, m\}, j=1,\dots,n$). Total $4n$ parameters of parity 1.
- `gamma_structure_constants`: List of deformed brackets $[X, Y]_\gamma = [X, Y]_0 + \kappa \cdot \gamma(X, Y)$, storing $\gamma(X,Y)$.

---

## 4. Schema 3: Evaluated Structure

Top-level additions:
- `gb_assignments`: Map from `gb_{a_1_sigma, b_j_s}` to concrete numeric values ($\pm 1$).
- `evaluated_structure_constants`: Total combined bracket values for assigned $gb$ values.

---

## 5. Schema 4: Coboundary Data

Top-level additions:
- `linear_map_f`: Specification of odd linear map $f: \mathfrak{g} \to \mathfrak{g}$.
- `coboundary_coefficients`: Coefficients $(\delta f)(X, Y)$ computed via:
  $$(\delta f)(X, Y) = (-1)^{p(X)} [X, f(Y)] - (-1)^{(p(X)+1)p(Y)} [Y, f(X)] - f([X, Y]).$$

---

## 6. Backward Compatibility with B(m,n) Schema

- Maintain same 4-layer JSON hierarchy.
- Replaced single supplementary fermion `a_0` with standard CAR pair `a_1_p, a_1_m` under `oscillator_generators.fermions`.
- Elevated `central_elements` to a top-level key containing `kappa` and `K`.
- Updated dimension formulas to $m=1$ case ($\text{even} = 2n^2+n+1, \text{odd} = 4n$).
