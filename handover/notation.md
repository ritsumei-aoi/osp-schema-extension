# Notation and Terminology

This document defines the mathematical notation and terminology used in this repository.
Finalized during Issue I01 for the C(n+1) schema extension project.

## Conventions

### 1. Algebra Family

- **B(0,n) = osp(1|2n)**: supplementary fermion $a_0$ with $a_0^2 = 1/2$; odd generators $E_{\pm\delta_k}$.
- **C(n+1) = osp(2|2n)**: standard fermionic pair $a_1^\pm$ with $\{a_1^-, a_1^+\} = 1$; odd generators $E_{\pm\varepsilon \pm \delta_k}$.

### 2. Oscillator Labels

| Symbol | JSON label | Parity | Algebra |
|---|---|---|---|
| $a_0$ | `a_0` | 1 | B(0,n) only |
| $a_1^+$ | `a_1_p` | 1 | C(n+1) only |
| $a_1^-$ | `a_1_m` | 1 | C(n+1) only |
| $b_k^+$ | `b_{k}_p` | 0 | both |
| $b_k^-$ | `b_{k}_m` | 0 | both |

### 3. Basis Generator Labels for C(n+1)

#### 3a. Even generators

| Root / type | JSON label | Oscillator realization |
|---|---|---|
| Cartan $H_k$ ($k=1,\ldots,n+1$) | `H_{k}` | see §4 |
| $2\delta_k$ | `E_2del{k}_p` | $(b_k^+)^2$ |
| $-2\delta_k$ | `E_2del{k}_m` | $(b_k^-)^2$ |
| $\delta_i+\delta_j$ ($i<j$) | `E_del{i}_del{j}_pp` | $b_i^+ b_j^+$ |
| $-(\delta_i+\delta_j)$ ($i<j$) | `E_del{i}_del{j}_mm` | $b_i^- b_j^-$ |
| $\delta_i-\delta_j$ ($i<j$) | `E_del{i}_del{j}_pm` | $b_i^+ b_j^-$ |
| $-(\delta_i-\delta_j)$ ($i<j$) | `E_del{i}_del{j}_mp` | $b_i^- b_j^+$ |

#### 3b. Odd generators (ε-roots)

| Root | JSON label | Oscillator realization |
|---|---|---|
| $\varepsilon + \delta_k$ | `E_eps1_del{k}_pp` | $a_1^+ b_k^+$ |
| $\varepsilon - \delta_k$ | `E_eps1_del{k}_pm` | $a_1^+ b_k^-$ |
| $-\varepsilon + \delta_k$ | `E_eps1_del{k}_mp` | $a_1^- b_k^+$ |
| $-\varepsilon - \delta_k$ | `E_eps1_del{k}_mm` | $a_1^- b_k^-$ |

### 4. Cartan Generator Realizations for C(n+1)

From the Frappat oscillator realization (see `docs/math/Cn1_definition.md`):

$$
H_1 = a_1^+ a_1^- + b_1^+ b_1^-, \quad
H_k = b_{k-1}^+ b_{k-1}^- - b_k^+ b_k^- \ (2 \le k \le n), \quad
H_{n+1} = -b_n^+ b_n^- - \tfrac{1}{2}.
$$

### 5. PBW Ordering

**Choice: Option A** — mirrors the B(0,n) convention (κ < odd < even).

**Rationale**: Option A groups odd generators together before even generators, which directly mirrors the B(0,n) PBW ordering (`κ < [odd] < [even]`). This makes cross-algebra comparisons and code reuse straightforward. Option B (grouping by ε-raising vs ε-lowering) would fragment the natural ε⊗δ tensor structure and complicate structure constant bookkeeping.

**Oscillator PBW ordering**: $\kappa \prec a_1^+ \prec a_1^- \prec b_1^+ \prec b_1^- \prec b_2^+ \prec b_2^- \prec \cdots \prec b_n^+ \prec b_n^-$

**Basis element ordering**:
```
κ
< E_eps1_del{1}_pp, E_eps1_del{1}_pm, E_eps1_del{1}_mp, E_eps1_del{1}_mm
< E_eps1_del{2}_pp, ...
< ... (odd, ordered by k then sign-pair pp/pm/mp/mm)
< H_1, H_2, ..., H_{n+1}
< E_2del{1}_p, E_2del{1}_m, ..., E_2del{n}_p, E_2del{n}_m
< E_del{i}_del{j}_pp, E_del{i}_del{j}_mm, E_del{i}_del{j}_pm, E_del{i}_del{j}_mp
  (even, i<j ordered lexicographically)
```

### 6. Basis Lists by n

#### C(2) = osp(2|2), n=1: dim = 4|4, total = 8

**Even (4)**: `H_1`, `H_2`, `E_2del1_p`, `E_2del1_m`

**Odd (4)**: `E_eps1_del1_pp`, `E_eps1_del1_pm`, `E_eps1_del1_mp`, `E_eps1_del1_mm`

#### C(3) = osp(2|4), n=2: dim = 11|8, total = 19

**Even (11)**: `H_1`, `H_2`, `H_3`, `E_2del1_p`, `E_2del1_m`, `E_2del2_p`, `E_2del2_m`, `E_del1_del2_pp`, `E_del1_del2_mm`, `E_del1_del2_pm`, `E_del1_del2_mp`

**Odd (8)**: `E_eps1_del1_pp`, `E_eps1_del1_pm`, `E_eps1_del1_mp`, `E_eps1_del1_mm`, `E_eps1_del2_pp`, `E_eps1_del2_pm`, `E_eps1_del2_mp`, `E_eps1_del2_mm`

#### C(4) = osp(2|6), n=3: dim = 22|12, total = 34

**Even (22)**: `H_1`, `H_2`, `H_3`, `H_4`, `E_2del1_p`, `E_2del1_m`, `E_2del2_p`, `E_2del2_m`, `E_2del3_p`, `E_2del3_m`, `E_del1_del2_pp`, `E_del1_del2_mm`, `E_del1_del2_pm`, `E_del1_del2_mp`, `E_del1_del3_pp`, `E_del1_del3_mm`, `E_del1_del3_pm`, `E_del1_del3_mp`, `E_del2_del3_pp`, `E_del2_del3_mm`, `E_del2_del3_pm`, `E_del2_del3_mp`

**Odd (12)**: `E_eps1_del1_pp`, `E_eps1_del1_pm`, `E_eps1_del1_mp`, `E_eps1_del1_mm`, `E_eps1_del2_pp`, `E_eps1_del2_pm`, `E_eps1_del2_mp`, `E_eps1_del2_mm`, `E_eps1_del3_pp`, `E_eps1_del3_pm`, `E_eps1_del3_mp`, `E_eps1_del3_mm`

### 7. File Naming Convention

- `C_{n}_structure.json` — Schema 1 (algebra structure), bosonic rank n
- `C_{n}_gamma.json` — Schema 2 (inhomogeneous deformation)
- `C_{n}_evaluated.json` — Schema 3 (evaluated at specific gb values)
- `C_{n}_coboundary.json` — Schema 4 (coboundary structure)

Examples: C(2) = osp(2|2) uses n=1, files: `C_1_structure.json`, etc.

### 8. Central Elements

| Symbol | JSON label | Parity | Description |
|---|---|---|---|
| $K$ | `K` | 0 | Even central identity |
| $\kappa$ | `kappa` | 1 | Odd nilpotent central element ($\kappa^2=0$) |
