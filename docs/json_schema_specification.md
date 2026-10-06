# C(n+1) = osp(2|2n) JSON Schema Specification (v5.0 extension)

Complete, standalone specification of the 4-layer JSON schema for $C(n+1)$, obtained from
the B(0,n) v5.0 schema (`docs/math/B0n_schema_v5.md`). Conventions: `handover/notation.md`.
Generators: `src/C_generators.py` (Layer 1), further layers in later sections.

| Layer | File | Contents |
|---|---|---|
| Schema 1 | `data/C_{n}_structure.json` | basis, parity, oscillator realization, structure constants |
| Schema 2 | `data/C_{n}_gamma.json` | symbolic inhomogeneous deformation γ (linear in gb) |
| Schema 3 | `data/C_{n}_evaluated.json` | γ evaluated at a numerical gb assignment |
| Schema 4 | `data/C_{n}_coboundary.json` | coboundary δf of an odd linear map f |

**File naming**: `C_{n}_structure.json` with $n$ the *bosonic rank*: C(2)=osp(2|2) → `C_1_...`,
C(3)=osp(2|4) → `C_2_...`, C(4)=osp(2|6) → `C_3_...`.

---

## Schema 1: Algebra Structure

Top-level keys (order as listed):
`schema_version`, `algebra`, `oscillator_generators`, `oscillator_relations`, `central_elements`,
`basis`, `parity`, `generator_realization`, `structure_constants`, `metadata`.

### `schema_version`
`"5.0"`.

### `algebra`
```json
{
  "family": "C", "m": 1, "n": 2, "cartan_type": "C(3)",
  "alternative_notation": {"osp": "osp(2|4)", "dimension_formula": "osp(2m|2n) with m=1"},
  "dimension": {"total": 19, "even": 11, "odd": 8}
}
```
Dimension formulas: even $=2n^2+n+1$, odd $=4n$, total $=2n^2+5n+1$.

| n | algebra | even | odd | total |
|---|---|---|---|---|
| 1 | C(2) | 4 | 4 | 8 |
| 2 | C(3) | 11 | 8 | 19 |
| 3 | C(4) | 22 | 12 | 34 |

### `oscillator_generators`
Two keys, `fermions` and `bosons` (the B(0,n) `supplementary_fermion` is removed):
```json
{
  "fermions": {"m": 1, "count": 2, "labels": ["a_1_p", "a_1_m"], "parity": 1,
               "description": "Standard fermionic pair a_1^+, a_1^- (CAR)."},
  "bosons": {"count": 4, "n": 2, "labels": ["b_1_p","b_1_m","b_2_p","b_2_m"],
             "description": "Bosonic oscillators b_i^± with i=1,...,n"}
}
```

### `oscillator_relations`
```json
{
  "standard_fermion_anticommutators": {
    "description": "CAR for the standard pair",
    "relations": {"conjugate_pair": "{a_1^-, a_1^+} = 1", "same_type": "(a_1^±)^2 = 0"}},
  "bosonic_commutators": {
    "description": "...",
    "relations": {"same_type": "[b_i^±, b_j^±] = 0 for all i, j", "conjugate_pair": "[b_i^-, b_j^+] = δ_{ij}"}},
  "mixed_commutators": {
    "boson_fermion": "[b_j^s, a_1^σ] = 0 (undeformed); deformed in Schema 2 as -gb_{σ,j,s} κ"}
}
```

### `central_elements` (top-level key)
```json
{
  "kappa": {"parity": 1, "nilpotent": true, "relation": "kappa^2 = 0", "description": "Odd central element."},
  "K": {"parity": 0, "value": "1", "description": "Even central element, identified with the scalar 1; not a basis element."}
}
```

### `basis`
PBW: `κ < [odd] < [even]` (K=1 excluded).
```json
{"even": ["H_1","H_2","H_3","E_2del1_p","E_2del2_p","E_del1_del2_pp","E_2del1_m","E_2del2_m",
          "E_del1_del2_mm","E_del1_del2_pm","E_del1_del2_mp"],
 "odd":  ["E_eps1_del1_pp","E_eps1_del2_pp","E_eps1_del1_pm","E_eps1_del2_pm",
          "E_eps1_del1_mp","E_eps1_del2_mp","E_eps1_del1_mm","E_eps1_del2_mm"],
 "ordering_convention": "PBW: κ < [odd: ...] < [even: ...]  (K = 1 is excluded)"}
```
Odd labels `E_eps1_del{k}_{ee}{dd}` have 4n members: `pp`: $\varepsilon+\delta_k$ ($a_1^+b_k^+$),
`pm`: $\varepsilon-\delta_k$ ($a_1^+b_k^-$), `mp`: $-\varepsilon+\delta_k$ ($a_1^-b_k^+$),
`mm`: $-\varepsilon-\delta_k$ ($a_1^-b_k^-$). Even labels as in `notation.md`.

### `parity`
`{label: 0|1}` for every basis element (even → 0, `E_eps1_*` → 1).

### `generator_realization`
```json
{
  "description": "...",
  "ordering": "a_1_p, a_1_m, b_1_p, b_1_m, ...",
  "realizations": {
    "H_1": {"standard_form": [{"words": ["a_1_p","a_1_m"], "coeff": "1"},
                              {"words": ["b_1_p","b_1_m"], "coeff": "1"}], "parity": 0},
    "H_3": {"standard_form": [{"words": [], "coeff": "-1/2"}, {"words": ["b_2_p","b_2_m"], "coeff": "-1"}], "parity": 0},
    "E_eps1_del1_pm": {"standard_form": [{"words": ["a_1_p","b_1_m"], "coeff": "1"}], "parity": 1}
  }
}
```
`words` are normal-ordered oscillator words (ordering above); `[]` is the constant 1.
No `a_0` appears. Cartan elements are the Weyl-symmetrised forms of `Cn1_definition.md`.

### `structure_constants`
List of the non-zero graded brackets $[X,Y\}=\sum_Z c\,Z$ for **all ordered pairs** $(X,Y)$ (both orders stored):
```json
{"X": "H_1", "Y": "E_eps1_del1_pp", "Z": "E_eps1_del1_pp", "coeff": "1", "sign_rule": "graded"}
```
`coeff` is a rational string (`"1"`, `"-1/2"`).

### `metadata`
`generated_by`, `generation_date`, `references` as in B(0,n) v5.0.

---

## Compatibility with B(m,n) v5.0

| Key | B(0,n) v5.0 | C(n+1) | Compatibility |
|---|---|---|---|
| `schema_version` | 5.0 | 5.0 | unchanged |
| `algebra` | family B, m=0 | family C, m=1, same sub-keys | same shape; consumers switch on `family` |
| `oscillator_generators` | `supplementary_fermion`, `bosons` | `fermions` (a_1_p, a_1_m), `bosons` | `bosons` identical; fermion key renamed |
| `oscillator_relations` | `supplementary_fermion_relation`, bosonic, mixed | `standard_fermion_anticommutators`, bosonic, mixed | bosonic/mixed keys identical |
| `central_elements` | κ (parity 0 in B doc), K | κ (parity 1), K (parity 0) | new top-level key; κ parity follows the unified rule |
| `basis` | odd `E_del{k}_{p,m}` (2n) | odd `E_eps1_del{k}_{pp,pm,mp,mm}` (4n) | same even-label grammar; ordering convention κ<odd<even retained |
| `parity`, `generator_realization`, `structure_constants`, `metadata` | as in B | same format | identical format; `a_0` replaced by `a_1_p/a_1_m` |

Everything outside the odd-label grammar and the fermion keys is format-identical, so B(0,n) readers need only
(i) accept the `fermions` key and (ii) read `central_elements`.

---

## Schema 2: Gamma structure (`C_{n}_gamma.json`, added in I05)

Deformation: $[b_j^s,a_1^\sigma]=-\mathrm{gb}_{\sigma,j,s}\,\kappa$, bracket
$[X,Y\}_\gamma=[X,Y\}_0+\kappa\,\gamma(X,Y)$ ($\kappa$ written on the left; $\kappa$ supercommutes with all oscillators).
$\gamma$ is **linear** in gb. $\gamma(X,Y)\in\mathfrak g\oplus\mathbb C K$: the component `Z = "K"` is the coefficient of $\kappa\cdot1$
(it is non-zero in general, see I05 response). gb are numeric scalars.

Top-level keys: `schema_version`, `algebra`, `basis`, `parity`, `central_elements` (copied from Schema 1),
`gb_matrix`, `inhomogeneous_deformation`, `metadata`.

```json
"gb_matrix": {"rows": ["a_1_p","a_1_m"], "cols": ["b_1_p","b_1_m", "..."], "shape": [2, "2n"],
              "entries": [["gb_a_1_p_b_1_p", "gb_a_1_p_b_1_m", "..."], ["gb_a_1_m_b_1_p", "..."]]}
```
Parameter names: `gb_a_1_{σ}_b_{j}_{s}` (σ, s ∈ {p, m}); $4n$ in total; row = fermion label, column = boson label.

```json
"inhomogeneous_deformation": {
  "description": "...", "relation": "[b_j^s, a_1^σ] = -gb_{σ,j,s} κ",
  "bracket": "[X,Y}_γ = [X,Y}_0 + κ γ(X,Y), κ written on the left",
  "parameters": {"count": 4, "parity": 1, "names": ["gb_a_1_p_b_1_p", "..."], "note": "..."},
  "central_direction": "Z = 'K' denotes the coefficient of κ·1 (K = 1) in γ(X,Y)",
  "gamma": [
    {"X": "E_eps1_del1_pp", "Y": "H_1", "Z": "E_eps1_del1_pp", "coeff": {"gb_a_1_p_b_1_p": "-2", "...": "..."}}
  ]
}
```
`gamma` lists all ordered pairs $(X,Y)$ and targets `Z` (a Schema 1 label or `"K"`) with non-zero $\gamma$;
`coeff` maps parameter names to rational strings: $\gamma(X,Y)_Z=\sum_p \mathrm{coeff}[p]\cdot p$.
Parity rule: $p(Z)=p(X)+p(Y)+1 \pmod 2$ (with $p(K)=0$) — the extra $+1$ is the parity of $\kappa$.
Consistency with Schema 1: same `basis`/`parity`; the $\kappa$-free part of the deformed bracket is gb-independent and equals Schema 1;
$\gamma$ satisfies the first-order super Jacobi (2-cocycle) condition, checked in `src/C_gamma.py` (`cocycle_failures`).

## Schema 3: Evaluated structure (`C_{n}_evaluated.json`, added in I06)

Schema 2 with a numerical gb substituted. The representative assignment `all_plus` (all $4n$ gb $=+1$) is `C_{n}_evaluated.json`;
other sign profiles are `C_{n}_evaluated_<profile>.json` (`all_minus`, `alternating`, `sigma_p_only`, `single_first`, `zero`;
definitions in `src/C_evaluate.py::profiles`).

Top-level keys: `schema_version`, `algebra`, `basis`, `parity`, `central_elements`, `gb_assignment`, `evaluated_structure`, `metadata`.
```json
"gb_assignment": {"profile": "all_plus", "values": {"gb_a_1_p_b_1_p": "1", "...": "1"}},
"evaluated_structure": {
  "description": "...",
  "undeformed_structure_constants": [ /* Schema 1 list, verbatim */ ],
  "gamma": [ {"X": "H_1", "Y": "E_eps1_del1_pp", "Z": "K", "coeff": "-1"} ],
  "central_direction": "Z = 'K' is the coefficient of κ·1"
}
```
`gamma[*].coeff` is a rational string equal to $\sum_p \mathrm{coeff}_{\text{Schema 2}}[p]\,\mathrm{gb}[p]$; only non-zero entries are listed.
The deformed bracket is $[X,Y\}_\gamma=\sum_Z c^{\,\text{Schema 1}}_{XYZ}Z+\kappa\sum_Z\gamma_{XYZ}Z$.

## Schema 4: Coboundary structure (`C_{n}_coboundary.json`, added in I07)

Odd linear map $f:\mathfrak g\to\mathfrak g\oplus\mathbb CK$, $f(Z_j)=\sum_i\phi_{ij}Z_i$ ($\phi_{ij}\ne0$ only if $p(Z_i)\ne p(Z_j)$, $p(K)=0$) and
$(\delta f)(X,Y)=(-1)^{p(X)}[X,f(Y)]-(-1)^{(p(X)+1)p(Y)}[Y,f(X)]-f([X,Y])$ (`docs/math/C_coboundary_definition.md`).
The map is the one induced by the fermion shift $a_1^\sigma\mapsto a_1^\sigma+\kappa\sum_{j,s}c^\sigma_{j,s}b_j^s$ ($4n$ parameters $c$).
`C_{n}_coboundary.json` uses the $c$ that corresponds to gb $=$ all $+1$ (profile `all_plus`); `C_{n}_coboundary_<profile>.json` use the $c$ of the other profiles
($c_{\sigma,j,p}=-\mathrm{gb}_{\sigma,j,m}$, $c_{\sigma,j,m}=+\mathrm{gb}_{\sigma,j,p}$).

Top-level keys: `schema_version`, `algebra`, `basis`, `parity`, `central_elements`, `odd_linear_map`, `coboundary`, `metadata`.
```json
"odd_linear_map": {"description": "...", "family": "fermion shift", "profile": "all_plus",
                   "c_parameters": {"c_a_1_p_b_1_p": "-1", "...": "..."},
                   "gb_correspondence": "...",
                   "phi": [ {"from": "E_eps1_del1_pp", "to": "E_2del1_p", "phi": "1"} ]},
"coboundary": {"formula": "...", "central_direction": "...",
               "delta_f": [ {"X": "H_1", "Y": "E_eps1_del1_pp", "Z": "K", "coeff": "1"} ]}
```
`phi` lists the non-zero $\phi_{ij}$ (`to` may be `"K"`); `delta_f` has the same entry format as the Schema 3 `gamma` list
(`Z = "K"`: coefficient of $\kappa\cdot1$), so Layers 3 and 4 are compared entry by entry.
