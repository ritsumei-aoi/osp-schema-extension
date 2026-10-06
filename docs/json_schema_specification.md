# C(n+1) JSON Schema Specification (v5.0-C)

Complete, standalone specification of the JSON schema for $C(n+1) = \mathfrak{osp}(2|2n)$,
obtained by extending the B(0,n) v5.0 schema (`docs/math/B0n_schema_v5.md`).
Conventions (labels, basis, PBW ordering) are those of `handover/notation.md`.

Layers: Schema 1 (`C_{n}_structure.json`), Schema 2 (`C_{n}_gamma.json`),
Schema 3 (`C_{n}_evaluated.json`), Schema 4 (`C_{n}_coboundary.json`).
**`n` is the bosonic rank**: C(2) = osp(2|2) ↔ `n=1`, C(3) ↔ `n=2`, C(4) ↔ `n=3`.
This document is extended with Schemas 2–4 in Issues I05–I07.

---

## Schema 1: Algebra structure — `C_{n}_structure.json`

### Top-level keys
```json
{
  "schema_version": "5.0",
  "algebra": {},
  "oscillator_generators": {},
  "oscillator_relations": {},
  "central_elements": {},
  "basis": {},
  "parity": {},
  "generator_realization": {},
  "structure_constants": [],
  "metadata": {}
}
```
`central_elements` is a **top-level** key (new relative to B(0,n)). `schema_version` stays `"5.0"`
(a reader of the B(0,n) schema can read this file unchanged apart from the documented key changes).

### `algebra`
```json
{
  "family": "C",
  "m": 1,
  "n": 2,
  "cartan_type": "C(3)",
  "alternative_notation": {"osp": "osp(2|4)", "dimension_formula": "osp(2m|2n) with m=1"},
  "dimension_formula": {"even": "2n^2 + n + 1", "odd": "4n", "total": "2n^2 + 5n + 1"},
  "dimension": {"total": 19, "even": 11, "odd": 8}
}
```
| n | cartan_type | osp | even | odd | total |
|---|---|---|---|---|---|
| 1 | C(2) | osp(2\|2) | 4 | 4 | 8 |
| 2 | C(3) | osp(2\|4) | 11 | 8 | 19 |
| 3 | C(4) | osp(2\|6) | 22 | 12 | 34 |

### `oscillator_generators`
Two keys, no `supplementary_fermion`.
```json
{
  "fermions": {
    "m": 1,
    "count": 2,
    "labels": ["a_1_p", "a_1_m"],
    "parity": 1,
    "description": "Standard fermionic pair a_1^±; CAR {a_1^-, a_1^+} = 1."
  },
  "bosons": {
    "count": 4,
    "n": 2,
    "labels": ["b_1_p", "b_1_m", "b_2_p", "b_2_m"],
    "parity": 0,
    "description": "Bosonic oscillators b_k^± with k=1..n"
  }
}
```
Bosons: `count = 2n`, `labels` ordered `b_1_p, b_1_m, …, b_n_p, b_n_m`.

### `oscillator_relations`
```json
{
  "standard_fermion_anticommutators": {
    "description": "CAR for the standard fermionic pair",
    "relations": {
      "conjugate_pair": "{a_1^-, a_1^+} = 1",
      "same_type": "{a_1^±, a_1^±} = 0, i.e. (a_1^±)^2 = 0"
    }
  },
  "bosonic_commutators": {
    "description": "CCR for bosonic oscillators",
    "relations": {"same_type": "[b_i^±, b_j^±] = 0", "conjugate_pair": "[b_i^-, b_j^+] = δ_{ij}"}
  },
  "mixed_commutators": {"boson_fermion": "[b_i^±, a_1^±] = 0"}
}
```
`mixed_commutators` is the **undeformed** relation; Schema 2 deforms it to `-gb·κ`.

### `central_elements` (top-level)
```json
{
  "kappa": {"label": "kappa", "parity": 1, "relation": "kappa^2 = 0",
            "description": "Odd nilpotent central element of the inhomogeneous extension"},
  "K": {"label": "K", "parity": 0, "value": "1",
        "description": "Even central identity element; identified with scalar 1, excluded from basis"}
}
```
(`kappa` has parity 1 here by the unified rules for this study. B(0,n)'s text lists κ with parity 0 in JSON;
the C(n+1) schema follows $p(\kappa)=1$ of `C_inhomogeneous_definition.md`.)

### `basis`
```json
{
  "even": ["H_1", "…", "H_{n+1}", "E_2del{k}_p", "E_del{i}_del{j}_pp", "E_2del{k}_m", "E_del{i}_del{j}_mm",
           "E_del{i}_del{j}_pm", "E_del{i}_del{j}_mp"],
  "odd": ["E_eps1_del{k}_pp (k=1..n)", "…_pm", "…_mp", "…_mm"],
  "ordering_convention": "PBW: kappa < [odd: E_eps1_del{k}_pp,pm,mp,mm] < [even: H, E_2del_p, E_del_del_pp, E_2del_m, E_del_del_mm, E_del_del_pm, E_del_del_mp]  (K = 1 excluded)"
}
```
Lists are fully expanded in the files (dimension-many entries each). The explicit lists for n=1,2,3 are in `handover/notation.md`.

### `parity`
Map label → 0/1: `H_*`, `E_2del*`, `E_del*_del*_*` have parity 0; `E_eps1_del*_*` have parity 1.

### `generator_realization`
```json
{
  "description": "Standard (normal-ordered, Weyl-symmetrized) form",
  "ordering": "a_1_p, a_1_m, b_1_p, b_1_m, ..., b_n_p, b_n_m",
  "realizations": {
    "H_1":  {"standard_form": [{"words": ["a_1_p","a_1_m"], "coeff": "1"}, {"words": ["b_1_p","b_1_m"], "coeff": "1"}],
             "frappat_form": "a_1^+ a_1^- + b_1^+ b_1^-", "parity": 0},
    "E_eps1_del1_pm": {"standard_form": [{"words": ["a_1_p","b_1_m"], "coeff": "1"}],
                       "frappat_form": "a_1^+ b_1^-", "parity": 1}
  }
}
```
Each generator is a list of `{words, coeff}`; `words` is the list of oscillator labels (empty list = constant),
`coeff` an exact rational string. Differences from B(0,n): `a_0` is replaced by `a_1_p/a_1_m`; `H_{n+1} = -b_n^+b_n^- - 1/2`;
the constant `1/2` of `H_{n+1}` comes from the Weyl symmetrization of $b_n$, not from a fermion relation.

### `structure_constants`
List of all **ordered pairs** $(X,Y)$ with nonzero graded bracket, one entry per $Z$:
```json
{"X": "H_1", "Y": "E_eps1_del1_pp", "Z": "E_eps1_del1_pp", "coeff": "1", "sign_rule": "graded"}
```
$[X,Y\} = XY-(-1)^{p(X)p(Y)}YX = \sum_Z \mathrm{coeff}\cdot Z$ (graded). Both $(X,Y)$ and $(Y,X)$ are stored so that
anti-symmetry $[X,Y\} = -(-1)^{p(X)p(Y)}[Y,X\}$ is independently verifiable. Entries sorted by (index of X, index of Y, index of Z) in basis order (even/odd lists concatenated in PBW order: odd, then even).

### `metadata`
```json
{"generated_by": "src/C_generators.py", "generation_date": "YYYY-MM-DD",
 "references": ["Frappat et al. (2000), Dictionary on Lie Algebras and Superalgebras", "Bakalov and Sullivan (2017)"]}
```

### File naming
`data/C_{n}_structure.json`, `n ∈ {1,2,3}` (also `C_{n}_gamma.json`, `C_{n}_evaluated.json`, `C_{n}_coboundary.json`).

---

## Compatibility with B(m,n) / B(0,n) v5.0

| Key | B(0,n) v5.0 | C(n+1) | Compatibility |
|---|---|---|---|
| `schema_version` | "5.0" | "5.0" | same |
| `algebra` | `family:"B"`, `m:0` | `family:"C"`, `m:1`, plus `dimension_formula` object | additive; `dimension.{total,even,odd}` unchanged |
| `oscillator_generators` | `supplementary_fermion`, `bosons` | `fermions`, `bosons` | `bosons` identical; fermion key renamed/extended (reader must branch on `family`) |
| `oscillator_relations` | `supplementary_fermion_relation` | `standard_fermion_anticommutators` | `bosonic_commutators` identical; `mixed_commutators` kept |
| `central_elements` | (prose only) | top-level key | new key; ignorable by B readers |
| `basis`, `parity` | odd `E_del{k}_{p,m}` | odd `E_eps1_del{k}_{pp,pm,mp,mm}` | same structure, longer odd list; PBW `κ<odd<even` preserved |
| `generator_realization` | words over `a_0` | words over `a_1_p`, `a_1_m` | same `{words, coeff}` format |
| `structure_constants` | list of `{X,Y,Z,coeff,sign_rule}` | identical format | identical |
| `metadata` | as is | as is | identical |

Even-sector entries of B(0,n) (`E_2del*`, `E_del*_del*_*`) reappear unchanged as the $\mathfrak{sp}(2n)$ part of C(n+1);
C(n+1) adds the $\mathfrak{so}(2)$ Cartan direction and the $\pm\varepsilon\pm\delta_k$ odd generators.

---

## Schema 2: Inhomogeneous deformation (gamma structure) — `C_{n}_gamma.json`

Defined by the deformed oscillator relation (`docs/math/C_inhomogeneous_definition.md`)
$[b_j^s, a_1^\sigma] = -\mathrm{gb}_{\sigma,j,s}\,\kappa$, giving
$[X,Y]_\gamma = [X,Y]_0 + \kappa\,\gamma(X,Y)$ with $\gamma$ **linear in gb**.

Top-level keys: `schema_version` ("5.0"), `schema_layer` (2), `algebra`, `central_elements`, `basis`, `parity`
(copied from Schema 1), `gb_matrix`, `inhomogeneous_deformation`, `metadata`.

### `gb_matrix`
```json
{"shape": [2, 4], "rows": ["a_1_p", "a_1_m"], "columns": ["b_1_p", "b_1_m", "b_2_p", "b_2_m"],
 "parity": 1, "relation": "[b_j^s, a_1^sigma] = -gb_{sigma,j,s} * kappa",
 "entries": [["gb_a_1_p_b_1_p", "gb_a_1_p_b_1_m", "gb_a_1_p_b_2_p", "gb_a_1_p_b_2_m"],
             ["gb_a_1_m_b_1_p", "gb_a_1_m_b_1_m", "gb_a_1_m_b_2_p", "gb_a_1_m_b_2_m"]],
 "parameter_count": 8}
```
Size $2\times 2n$, i.e. $4n$ parameters; row = fermion label, column = boson label.

### `inhomogeneous_deformation`
```json
{"description": "...", "bracket": "[X,Y]_gamma = [X,Y]_0 + kappa*gamma(X,Y)",
 "gamma_codomain": "g (+) C*K",
 "gamma_parity_rule": "p(Z) = p(X) + p(Y) + 1 (mod 2); Z='K' has parity 0",
 "parameters": ["gb_a_1_p_b_1_p", "..."],
 "gamma_structure": [
   {"X": "E_eps1_del1_pp", "Y": "H_1", "Z": "K", "coeff": {"gb_a_1_p_b_1_p": "1"}},
   {"X": "H_1", "Y": "E_eps1_del1_pp", "Z": "K", "coeff": {"gb_a_1_p_b_1_p": "-1"}}]}
```
$\gamma(X,Y) = \sum_Z \sum_{\text{param}} \mathrm{coeff}[\text{param}]\cdot \text{param}\cdot Z$, stored for all ordered pairs with
$\gamma\neq0$. `coeff` maps each gb symbol to the exact rational coefficient (omitted = 0).
**`Z = "K"`**: the constant component. Because $K=1$ is central and $\kappa K = \kappa$, this is a multiple of the central
element $\kappa$ in the bracket; it arises from Weyl-ordering constants (e.g. $b^-b^+ = b^+b^- + 1$) and is **not** in $\mathfrak g$.
So $\gamma:\mathfrak g\otimes\mathfrak g\to\mathfrak g\oplus\mathbb C K$.

### Consistency conditions with Schema 1 (verified by `src/verify_C_gamma.py`)
1. all labels are in the Schema 1 basis (or `K`) and $p(Z)=p(X)+p(Y)+1$;
2. skew-symmetry $\gamma(X,Y) = -(-1)^{p(X)p(Y)}\gamma(Y,X)$;
3. 2-cocycle identity w.r.t. the Schema 1 bracket (order-$\kappa$ part of the super Jacobi identity, using
   $[X,\kappa W]=(-1)^{p(X)}\kappa[X,W]$, $[\kappa W,Z]=\kappa[W,Z]$, $[K,\cdot]=0$);
4. the $\kappa$-free part of $[X,Y]_\gamma$ equals Schema 1 (tested).

---

## Schema 3: Evaluated structure — `C_{n}_evaluated.json`, `C_{n}_evaluated_<profile>.json`

gb replaced by concrete numbers. `C_{n}_evaluated.json` is the representative profile `all_plus` (all 4n parameters = +1);
other profiles: `zero` (control), `alternating`, `fermion_sign` (+1 for row `a_1_p`, −1 for `a_1_m`),
`boson_sign` (+1 for column `b_j_p`, −1 for `b_j_m`), `single_first` (only the first parameter = 1).

Top-level keys: `schema_version`, `schema_layer` (3), `algebra`, `central_elements`, `basis`, `parity`, `gb_assignment`,
`evaluated_structure`, `metadata`.
```json
{"gb_assignment": {"profile": "all_plus", "values": {"gb_a_1_p_b_1_p": "1", "...": "..."}},
 "evaluated_structure": {"description": "...", "entries": [
   {"X": "E_eps1_del1_pp", "Y": "H_1", "Z": "E_eps1_del1_pp", "coeff": "-2", "kappa_coeff": "0"},
   {"X": "E_eps1_del1_pp", "Y": "H_1", "Z": "K", "coeff": "0", "kappa_coeff": "1"}]}}
```
$[X,Y]_\gamma = \sum_Z (\mathrm{coeff} + \mathrm{kappa\_coeff}\cdot\kappa)\,Z$: `coeff` is the Schema 1 constant, `kappa_coeff` $=\gamma(X,Y)_Z$ at the
given gb (Schema 2 linear combination, exact rationals). Entries with both coefficients 0 are omitted; `Z="K"` entries have `coeff = "0"`.
Consistency with Schema 2 is tested by re-evaluating directly in the deformed oscillator algebra (`tests/test_C_evaluate.py`).

---

## Schema 4: Coboundary structure — `C_{n}_coboundary.json`

Top-level keys: `schema_version`, `schema_layer` (4), `algebra`, `central_elements`, `basis`, `parity`, `odd_linear_map`,
`coboundary_structure`, `gb_correspondence`, `metadata`.

### `odd_linear_map` (the map f)
$f_c$ is the odd derivation induced by $a_1^\sigma \to a_1^\sigma + \kappa\,\ell^\sigma$, $\ell^\sigma=\sum_{j,s}c_{\sigma,j,s}b_j^s$
(4n parameters `f_a_1_{p|m}_b_{j}_{p|m}`); on the basis $f(Z_j)=\sum_i\phi_{ij}Z_i$ with $\phi$ linear in $c$.
```json
{"parameters": ["f_a_1_p_b_1_p", "..."],
 "f_structure": [{"source": "E_eps1_del1_pp", "target": "H_2", "coeff": {"f_a_1_p_b_1_m": "-1"}},
                 {"source": "E_eps1_del1_pp", "target": "K",   "coeff": {"f_a_1_p_b_1_m": "1/2"}}]}
```
Parity rule $p(f(Z))=p(Z)+1$; target `K` (even) occurs only for odd sources (Weyl-ordering constants).

### `coboundary_structure`
`entries`: `{"X","Y","Z","coeff": {param: rational}}` = $(\delta f)(X,Y)_Z$ with
$(\delta f)(X,Y)=(-1)^{p(X)}[X,f(Y)]-(-1)^{(p(X)+1)p(Y)}[Y,f(X)]-f([X,Y])$; `Z="K"` is the central constant
($[K,\cdot]=0$, so $K$-parts of $f$ only enter through $-f([X,Y])$).

### `gb_correspondence`
Exact identity $\delta f_c=\gamma(\mathrm{gb})$ for $\mathrm{gb}_{\sigma,j,p}=c_{\sigma,j,m}$, $\mathrm{gb}_{\sigma,j,m}=-c_{\sigma,j,p}$
(stored as `map`: f-parameter → {gb-parameter: ±1}, i.e. $\delta f_{c_q}=\pm\gamma_{p(q)}$).
Verified for all pairs and all $Z$ including `K`.
