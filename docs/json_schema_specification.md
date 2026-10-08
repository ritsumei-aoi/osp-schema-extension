# JSON Schema Specification: Schema 1 for C(n+1) (v5.0 extension)

Scope: Schema 1 (algebra structure) for $C(n+1)=\mathfrak{osp}(2|2n)$.
Basis and PBW ordering follow `handover/notation.md` (I01).
Base case: `docs/math/B0n_schema_v5.md`.

## File naming

`C_{n}_structure.json`, where $n$ is the bosonic rank:

| Algebra | $n$ | File |
|---|---|---|
| C(2) | 1 | `data/C_1_structure.json` |
| C(3) | 2 | `data/C_2_structure.json` |
| C(4) | 3 | `data/C_3_structure.json` |

Layers 2–4 use the same $n$ suffix (`C_{n}_gamma.json`, `C_{n}_evaluated.json`, `C_{n}_coboundary.json`).

## Top-level keys

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

`central_elements` is a **top-level key** (not nested under `oscillator_relations`).

### `algebra`

```json
{
  "family": "C",
  "m": 1,
  "n": 1,
  "cartan_type": "C(2)",
  "alternative_notation": {"osp": "osp(2|2)", "dimension_formula": "osp(2m|2n) with m=1"},
  "dimension": {"total": 8, "even": 4, "odd": 4}
}
```

Dimension formulas: even $=2n^2+n+1$, odd $=4n$, total $=2n^2+5n+1$.

| $n$ | even | odd | total |
|---|---|---|---|
| 1 | 4 | 4 | 8 |
| 2 | 11 | 8 | 19 |
| 3 | 22 | 12 | 34 |

### `oscillator_generators`

```json
{
  "fermions": {
    "m": 1,
    "labels": ["a_1_p", "a_1_m"],
    "parity": 1,
    "description": "Standard fermionic pair a_1^± with CAR"
  },
  "bosons": {
    "count": 2,
    "n": 1,
    "labels": ["b_1_p", "b_1_m"],
    "description": "Bosonic oscillators b_k^± with k=1,...,n"
  }
}
```

`bosons.count` is $2n$. For C(2), $n=1$, so the list is `["b_1_p", "b_1_m"]`.

### `oscillator_relations`

```json
{
  "fermionic_anticommutators": {
    "relations": {
      "anticommutator": "{a_1^-, a_1^+} = 1",
      "same_type": "{a_1^±, a_1^±} = 0"
    }
  },
  "bosonic_commutators": {
    "relations": {
      "same_type": "[b_k^±, b_l^±] = 0",
      "conjugate_pair": "[b_k^-, b_l^+] = δ_{kl}"
    }
  },
  "mixed_commutators": {
    "boson_fermion": "[b_k^±, a_1^±] = 0 (undeformed; deformation carried by gamma, see I05)"
  }
}
```

### `central_elements` (top-level)

```json
{
  "kappa": {"parity": 1, "relation": "κ^2 = 0", "description": "Odd nilpotent central element"},
  "K": {"parity": 0, "relation": "K = 1", "description": "Even central element identified with the scalar 1; excluded from basis"}
}
```

### `basis`

```json
{
  "even": ["H_eps", "H_1", "E_2del1_p", "E_2del1_m"],
  "odd": ["E_eps1_del1_pp", "E_eps1_del1_pm", "E_eps1_del1_mp", "E_eps1_del1_mm"],
  "ordering_convention": "PBW: odd < even (κ and K excluded); within odd by k then pp<pm<mp<mm; within even: H_eps < H_k < E_2del{k}_p < E_del{i}_del{j}_{pp,pm,mp} < E_2del{k}_m < E_del{i}_del{j}_mm"
}
```

Even labels for general $n$: `H_eps`, `H_1..H_n`, `E_2del{k}_{p,m}`, `E_del{i}_del{j}_{pp,pm,mp,mm}` ($i<j$).
Odd labels: `E_eps1_del{k}_{pp,pm,mp,mm}`.

### `parity`

Even labels map to 0, odd labels to 1, one entry per basis element.

### `generator_realization`

Each generator is a sum of oscillator words, expressed with `a_1_p`, `a_1_m` replacing `a_0`:

| Label | Words | Frappat form | Parity |
|---|---|---|---|
| `H_eps` | `a_1_p a_1_m` | $a_1^+a_1^-$ | 0 |
| `H_k` | see I03 generator | $b_k^+b_k^- - b_{k+1}^+b_{k+1}^-$ (and terminal form) | 0 |
| `E_eps1_del{k}_pp` | `a_1_p b_k_p` | $a_1^+ b_k^+$ | 1 |
| `E_eps1_del{k}_pm` | `a_1_p b_k_m` | $a_1^+ b_k^-$ | 1 |
| `E_eps1_del{k}_mp` | `a_1_m b_k_p` | $a_1^- b_k^+$ | 1 |
| `E_eps1_del{k}_mm` | `a_1_m b_k_m` | $a_1^- b_k^-$ | 1 |
| `E_2del{k}_p` | `b_k_p b_k_p` | $(b_k^+)^2$ | 0 |
| `E_2del{k}_m` | `b_k_m b_k_m` | $(b_k^-)^2$ | 0 |

Exact coefficients for the Cartan and $\mathfrak{sp}$ generators are fixed in I03 and must match this table's words.

### `structure_constants`

List of non-zero graded brackets:

```json
[{"X": "H_eps", "Y": "E_eps1_del1_pp", "Z": "E_eps1_del1_pp", "coeff": "1", "sign_rule": "graded"}]
```

### `metadata`

```json
{
  "generated_by": "src/C_generators.py",
  "generation_date": "YYYY-MM-DD",
  "references": ["Frappat et al. (2000), Dictionary on Lie Algebras and Superalgebras", "arXiv:hep-th/9607161"]
}
```

## Compatibility with B(m,n)

| Key | B(0,n) (`m=0`) | C(n+1) (`m=1`) | Change type |
|---|---|---|---|
| `schema_version` | `"5.0"` | `"5.0"` | none |
| `algebra.family` | `"B"` | `"C"` | value |
| `algebra.m` | `0` | `1` | value |
| `oscillator_generators` | `supplementary_fermion` + `bosons` | `fermions` + `bosons` | structural |
| `oscillator_relations` | `supplementary_fermion_relation` | `fermionic_anticommutators` | structural |
| `central_elements` | absent (κ only in prose) | top-level, `kappa` and `K` | new key |
| `basis` | `κ < [odd] < [even]`, odd = `E_del{k}_p/m` | odd = `E_eps1_del{k}_*` (4n) | structural |
| `parity` | 2n odd labels | 4n odd labels | value set |

Backward compatibility: all keys shared with B(0,n) keep their names and types. `supplementary_fermion` and `supplementary_fermion_relation` are absent from C(n+1) files; a reader for B(m,n) detects the family via `algebra.family`/`algebra.m` before reading the fermionic keys.

## Decisions

- Two oscillator keys (`fermions`, `bosons`) per the unified rules; `central_elements` top-level.
- `m` appears explicitly in `algebra` and `fermions`.
- File names follow `C_{n}_structure.json` with $n$ the bosonic rank.
