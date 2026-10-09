# Notation and Terminology

This document defines the mathematical notation and terminology used in this repository.
It is initialized during the $C(n+1)$ schema extension project.

## Conventions

### Algebra Family

- $C(n+1) = \mathfrak{osp}(2|2n)$, where $n$ is the bosonic rank.
- Instances: $C(2)=\mathfrak{osp}(2|2)$ ($n=1$), $C(3)=\mathfrak{osp}(2|4)$ ($n=2$), $C(4)=\mathfrak{osp}(2|6)$ ($n=3$).

### Oscillator Labels

| Symbol | JSON label | CAR/CCR |
|---|---|---|
| $a_1^+$ | `a_1_p` | CAR: $\{a_1^-, a_1^+\}=1$ |
| $a_1^-$ | `a_1_m` | CAR |
| $b_k^+$ | `b_{k}_p` | CCR: $[b_k^-, b_l^+]=\delta_{kl}$ |
| $b_k^-$ | `b_{k}_m` | CCR |

### Even Basis (Generator Labels)

| Generator | JSON label | Oscillator realization |
|---|---|---|
| $H_k$ ($k=1,\ldots,n+1$) | `H_{k}` | See Cn1_definition.md |
| $E_{2\delta_k}$ | `E_2del{k}_p` | $\tfrac{1}{2}(b_k^+)^2$ |
| $E_{-2\delta_k}$ | `E_2del{k}_m` | $\tfrac{1}{2}(b_k^-)^2$ |
| $E_{\delta_i+\delta_j}$ ($i<j$) | `E_del{i}_del{j}_pp` | $b_i^+ b_j^+$ |
| $E_{-(\delta_i+\delta_j)}$ ($i<j$) | `E_del{i}_del{j}_mm` | $b_i^- b_j^-$ |
| $E_{\delta_i-\delta_j}$ ($i<j$) | `E_del{i}_del{j}_pm` | $b_i^+ b_j^-$ |
| $E_{-(\delta_i-\delta_j)}$ ($i<j$) | `E_del{i}_del{j}_mp` | $b_i^- b_j^+$ |

### Odd Basis (Generator Labels)

| Generator | JSON label | Oscillator realization |
|---|---|---|
| $E_{\varepsilon+\delta_k}$ | `E_eps1_del{k}_pp` | $a_1^+ b_k^+$ |
| $E_{\varepsilon-\delta_k}$ | `E_eps1_del{k}_pm` | $a_1^+ b_k^-$ |
| $E_{-\varepsilon+\delta_k}$ | `E_eps1_del{k}_mp` | $a_1^- b_k^+$ |
| $E_{-\varepsilon-\delta_k}$ | `E_eps1_del{k}_mm` | $a_1^- b_k^-$ |

### Basis Lists by n

**n=1 (C(2), osp(2|2))**: even=4, odd=4, total=8
- Even: `H_1`, `H_2`, `E_2del1_p`, `E_2del1_m`
- Odd: `E_eps1_del1_pp`, `E_eps1_del1_pm`, `E_eps1_del1_mp`, `E_eps1_del1_mm`

**n=2 (C(3), osp(2|4))**: even=11, odd=8, total=19
- Even: `H_1`, `H_2`, `H_3`, `E_2del1_p`, `E_2del2_p`, `E_del1_del2_pp`, `E_2del1_m`, `E_2del2_m`, `E_del1_del2_mm`, `E_del1_del2_pm`, `E_del1_del2_mp`
- Odd: `E_eps1_del1_pp`, `E_eps1_del1_pm`, `E_eps1_del1_mp`, `E_eps1_del1_mm`, `E_eps1_del2_pp`, `E_eps1_del2_pm`, `E_eps1_del2_mp`, `E_eps1_del2_mm`

**n=3 (C(4), osp(2|6))**: even=22, odd=12, total=34
- Even: `H_1`, `H_2`, `H_3`, `H_4`, `E_2del1_p`, `E_2del2_p`, `E_2del3_p`, `E_del1_del2_pp`, `E_del1_del3_pp`, `E_del2_del3_pp`, `E_2del1_m`, `E_2del2_m`, `E_2del3_m`, `E_del1_del2_mm`, `E_del1_del3_mm`, `E_del2_del3_mm`, `E_del1_del2_pm`, `E_del1_del2_mp`, `E_del1_del3_pm`, `E_del1_del3_mp`, `E_del2_del3_pm`, `E_del2_del3_mp`
- Odd: `E_eps1_del{k}_pp/pm/mp/mm` for k=1,2,3 (12 total)

### PBW Ordering

**Option A**: κ < [odd in ε-root order] < [even: Cartan first, raising next, lowering last]

**Option B**: Interleave κ with the odd generators by root height.

**Chosen: Option A** — consistent with the B(0,n) v5.0 schema convention (κ < odd < even), which groups generators by parity and simplifies index tracking in code. Within odd generators, order by k=1,...,n then by sign variant pp < pm < mp < mm. Within even generators: Cartan (H_1,...,H_{n+1}), then raising even roots (E_2del{k}_p, E_del{i}_del{j}_pp in lex order), then lowering even roots (E_2del{k}_m, E_del{i}_del{j}_mm), then mixed (E_del{i}_del{j}_pm, E_del{i}_del{j}_mp).

Full PBW ordering convention:
```
κ < [E_eps1_del1_pp, E_eps1_del1_pm, E_eps1_del1_mp, E_eps1_del1_mm, ..., E_eps1_del{n}_mm]
  < [H_1, ..., H_{n+1}, E_2del1_p, ..., E_2del{n}_p, E_del{i}_del{j}_pp (i<j lex),
     E_2del1_m, ..., E_2del{n}_m, E_del{i}_del{j}_mm (i<j lex),
     E_del{i}_del{j}_pm (i<j lex), E_del{i}_del{j}_mp (i<j lex)]
```

### Dimension Formulas

$C(n+1) = \mathfrak{osp}(2|2n)$: even $= 2n^2+n+1$, odd $= 4n$, total $= 2n^2+5n+1$.
