# JSON Schema Specification for C(n+1) = osp(2|2n)  (v5.0-C)

Complete, standalone specification (extension of `docs/math/B0n_schema_v5.md`).
`n` = bosonic rank; C(2)=osp(2|2) is n=1, C(3) is n=2, C(4) is n=3.
Conventions (labels, PBW order, realizations) are in `handover/notation.md`.

## Layers and files (all in `data/`)

| Layer | File | Content |
|---|---|---|
| Schema 1 | `C_{n}_structure.json` | algebra structure, basis, realizations, structure constants |
| Schema 2 | `C_{n}_gamma.json` | symbolic γ-structure of the inhomogeneous deformation |
| Schema 3 | `C_{n}_evaluated.json` | γ evaluated at concrete gb profiles |
| Schema 4 | `C_{n}_coboundary.json` | coboundary data δf for odd linear maps f |

Naming: `C_{n}_...` with n the bosonic rank (C(2) -> `C_1_structure.json`).

## Schema 1 top-level keys
```
schema_version, algebra, oscillator_generators, oscillator_relations,
central_elements, basis, parity, generator_realization, structure_constants, metadata
```
`central_elements` is a **top-level** key (in B(0,n) it lived inside the relations discussion only).

### schema_version
`"5.0"` (same string as B(0,n); the family field disambiguates).

### algebra
```json
{
  "family": "C", "m": 1, "n": 2, "cartan_type": "C(3)",
  "alternative_notation": {"osp": "osp(2|4)", "dimension_formula": "osp(2m|2n) with m=1"},
  "dimension": {"total": 19, "even": 11, "odd": 8},
  "dimension_formula": {"even": "2n^2+n+1", "odd": "4n", "total": "2n^2+5n+1"}
}
```
| n | even | odd | total |
|---|---|---|---|
| 1 | 4 | 4 | 8 |
| 2 | 11 | 8 | 19 |
| 3 | 22 | 12 | 34 |

### oscillator_generators  (no `supplementary_fermion`)
```json
{
  "fermions": {"count": 2, "m": 1, "labels": ["a_1_p", "a_1_m"], "parity": 1,
               "description": "Standard fermionic pair a_1^±"},
  "bosons":   {"count": 4, "n": 2, "labels": ["b_1_p","b_1_m","b_2_p","b_2_m"], "parity": 0}
}
```

### oscillator_relations
```json
{
  "standard_fermion_anticommutators": {"relations": {"anticommutator": "{a_1^-, a_1^+} = 1", "nilpotent": "(a_1^+)^2 = (a_1^-)^2 = 0"}},
  "bosonic_commutators": {"relations": {"same_type": "[b_i^±, b_j^±] = 0", "conjugate_pair": "[b_i^-, b_j^+] = δ_ij"}},
  "mixed_commutators": {"boson_fermion": "[b_i^±, a_1^±] = 0"}
}
```
(`mixed_commutators` is replaced by `[b_j^s, a_1^σ] = -gb_{σ,j,s} κ` in Schema 2.)

### central_elements
```json
{
  "kappa": {"parity": 1, "relation": "kappa^2 = 0", "description": "odd central, nilpotent"},
  "K":     {"parity": 0, "description": "even central identity, identified with scalar 1; not a basis element"}
}
```
The note of B(0,n) listing κ with parity 0 is a known inconsistency of the B(0,n) text (`B0n_definition.md` says p(κ)=1 but schema text says 0);
for C(n+1) we follow `C_inhomogeneous_definition.md`: **κ has parity 1, K parity 0**.

### basis
Ordering: κ < odd < even (K excluded). Lists as in `handover/notation.md` §3–4, e.g. n=1:
```json
{"odd": ["E_eps1_del1_pp","E_eps1_del1_pm","E_eps1_del1_mp","E_eps1_del1_mm"],
 "even": ["H_1","H_2","E_2del1_p","E_2del1_m"],
 "ordering_convention": "PBW: kappa < [odd] < [even]  (K = 1 excluded)"}
```
### parity
Map label -> 0/1; the 4n `E_eps1_*` are 1, all else 0.

### generator_realization
```json
{"description": "Weyl-ordered quadratics, PBW word order a_1_p<a_1_m<b_1_p<b_1_m<...",
 "ordering": "a_1_p, a_1_m, b_1_p, b_1_m, ...",
 "realizations": {"H_1": {"standard_form": [{"words":["a_1_p","a_1_m"],"coeff":"1"},{"words":["b_1_p","b_1_m"],"coeff":"1"}],
                          "frappat_form": "a_1^+ a_1^- + b_1^+ b_1^-", "parity": 0}, ...}}
```
Each realization is a list of `{words, coeff}`; `words` is a list of oscillator labels (empty list = scalar).
Odd generators use `a_1_p`/`a_1_m` times one boson.

### structure_constants
List of all non-zero graded brackets over **ordered** pairs (both [X,Y} and [Y,X} listed, so antisymmetry is checkable):
`{"X","Y","Z","coeff","sign_rule":"graded"}` with coeff a rational string, meaning `[X,Y} = Σ coeff · Z`.

### metadata
`generated_by`, `generation_date`, `references`, `n`, `bracket_convention`.

## Compatibility with B(0,n) v5.0
| Key | B(0,n) | C(n+1) |
|---|---|---|
| algebra.family / m | "B" / 0 | "C" / 1 |
| dimension | even 2n²+n, odd 2n | even 2n²+n+1, odd 4n |
| oscillator_generators | `supplementary_fermion` a_0 + `bosons` | `fermions` (a_1_p,a_1_m) + `bosons` |
| oscillator_relations | a_0²=1/2 | CAR pair |
| central_elements | not top-level | top-level (κ odd, K even) |
| basis.odd | `E_del{k}_p/m` (2n) | `E_eps1_del{k}_{pp,pm,mp,mm}` (4n) |
| generator_realization words | `a_0`, `b_k_±` | `a_1_p`/`a_1_m`, `b_k_±` |
Key names, `sign_rule`, coefficient encoding and PBW convention are unchanged, so a B(0,n) reader that ignores the unknown
`fermions`/`central_elements` keys' contents still parses the file.

## Schemas 2–4
Specified in the sections appended by issues I05–I07 below.

---
## Schema 2: `C_{n}_gamma.json` (added in I05)
Top-level keys: `schema_version`, `layer` (=2), `algebra`, `basis`, `parity`, `central_elements` (copied from Schema 1),
`inhomogeneous_deformation`, `metadata` (`base_file` = the Schema 1 file).

`inhomogeneous_deformation`:
- `gb_matrix`: `rows` `["a_1_p","a_1_m"]`, `cols` `["b_1_p","b_1_m",...]`, `shape` `[2, 2n]`, `parity` 1,
  `parameters` = list of the 4n names `gb_a_1_{σ}_b_{j}_{s}` (row-major).
  Defining relation: `[b_j^s, a_1^σ] = -gb_{σ,j,s} κ`.
- `gamma_structure`: list of `{"X","Y","Z","gamma":[{"param","coeff"}, ...]}` meaning
  `γ(X,Y) = Σ_Z (Σ_p coeff_p · gb_p) Z`, where `[X,Y}_γ = [X,Y}_0 + κ·γ(X,Y)` (κ on the left). Only non-zero entries; all ordered pairs listed.
- γ is **linear** in gb (κ²=0); parity of γ(X,Y) is p(X)+p(Y)+1.
- Realization used: Weyl-symmetrised generators; in the deformed algebra the odd generators are `E = a_σ b_τ − ½ gb_{σ,k,τ} κ`
  (normal-ordered `a b`), which makes γ take values in g (no `κK` term).

---
## Schema 3: `C_{n}_evaluated.json` (added in I06)
Top-level: `schema_version`, `layer` (=3), `algebra`, `basis`, `parity`, `central_elements`, `gb_matrix`, `convention`, `profiles`, `metadata`.
`profiles`: list of `{"name", "gb": {param: integer}, "gamma_evaluated": [{"X","Y","Z","coeff"}]}`;
`gamma_evaluated` lists the non-zero γ(X,Y) = Σ_Z coeff·Z at that gb (convention as Schema 2). Names: `all_plus`, `all_minus`,
`alternating`, `row_a_1_{p,m}_only`, `{plus,minus}_sector_only`, `{diagonal,antidiagonal}_pm`, `unit_<param>`, and for n=1 all 16 `sign_±±±±`.
