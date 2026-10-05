# Notation and Terminology

This document defines the mathematical notation and terminology used in this repository.
It is initialized during the $C(n+1)$ schema extension project.

## Conventions

### Oscillator Labels

| Symbol | JSON label | Parity | Relation |
|---|---|---|---|
| $a_1^+$ | `a_1_p` | 1 | $\{a_1^-, a_1^+\} = 1$ (CAR) |
| $a_1^-$ | `a_1_m` | 1 | $\{a_1^-, a_1^+\} = 1$ (CAR) |
| $b_k^+$ | `b_{k}_p` | 0 | $[b_k^-, b_l^+] = \delta_{kl}$ (CCR) |
| $b_k^-$ | `b_{k}_m` | 0 | $[b_k^-, b_l^+] = \delta_{kl}$ (CCR) |

### Generator Labels for C(n+1) = osp(2|2n)

**Even generators** ($\mathfrak{g}_{\bar{0}}$):

| Root | JSON label | Oscillator realization |
|---|---|---|
| Cartan $H_k$ ($k=1,\ldots,n+1$) | `H_k` | See below |
| $2\delta_k$ | `E_2del{k}_p` | $(b_k^+)^2$ |
| $-2\delta_k$ | `E_2del{k}_m` | $(b_k^-)^2$ |
| $\delta_i + \delta_j$ ($i<j$) | `E_del{i}_del{j}_pp` | $b_i^+ b_j^+$ |
| $\delta_i - \delta_j$ ($i<j$) | `E_del{i}_del{j}_pm` | $b_i^+ b_j^-$ |
| $-\delta_i + \delta_j$ ($i<j$) | `E_del{i}_del{j}_mp` | $b_i^- b_j^+$ |
| $-(\delta_i + \delta_j)$ ($i<j$) | `E_del{i}_del{j}_mm` | $b_i^- b_j^-$ |

Cartan generators:
- $H_1 = a_1^+ a_1^- + b_1^+ b_1^-$ (label `H_1`)
- $H_k = b_{k-1}^+ b_{k-1}^- - b_k^+ b_k^-$ for $k = 2, \ldots, n$ (label `H_k`)
- $H_{n+1} = -b_n^+ b_n^- - \tfrac{1}{2}$ (label `H_{n+1}`)

**Odd generators** ($\mathfrak{g}_{\bar{1}}$):

| Root | JSON label | Oscillator realization |
|---|---|---|
| $\varepsilon + \delta_k$ | `E_eps_del{k}_pp` | $a_1^+ b_k^+$ |
| $\varepsilon - \delta_k$ | `E_eps_del{k}_pm` | $a_1^+ b_k^-$ |
| $-\varepsilon + \delta_k$ | `E_eps_del{k}_mp` | $a_1^- b_k^+$ |
| $-\varepsilon - \delta_k$ | `E_eps_del{k}_mm` | $a_1^- b_k^-$ |

### Basis Lists

**C(2) = osp(2|2), n=1**: dim = (4 | 4) = 8
- Even (4): `H_1`, `H_2`, `E_2del1_p`, `E_2del1_m`
- Odd (4): `E_eps_del1_pp`, `E_eps_del1_pm`, `E_eps_del1_mp`, `E_eps_del1_mm`

**C(3) = osp(2|4), n=2**: dim = (11 | 8) = 19
- Even (11): `H_1`, `H_2`, `H_3`, `E_2del1_p`, `E_2del2_p`, `E_del1_del2_pp`, `E_2del1_m`, `E_2del2_m`, `E_del1_del2_mm`, `E_del1_del2_pm`, `E_del1_del2_mp`
- Odd (8): `E_eps_del1_pp`, `E_eps_del2_pp`, `E_eps_del1_pm`, `E_eps_del2_pm`, `E_eps_del1_mp`, `E_eps_del2_mp`, `E_eps_del1_mm`, `E_eps_del2_mm`

**C(4) = osp(2|6), n=3**: dim = (22 | 12) = 34
- Even (22): `H_1`, `H_2`, `H_3`, `H_4`, `E_2del1_p`, `E_2del2_p`, `E_2del3_p`, `E_del1_del2_pp`, `E_del1_del3_pp`, `E_del2_del3_pp`, `E_2del1_m`, `E_2del2_m`, `E_2del3_m`, `E_del1_del2_mm`, `E_del1_del3_mm`, `E_del2_del3_mm`, `E_del1_del2_pm`, `E_del1_del3_pm`, `E_del2_del3_pm`, `E_del1_del2_mp`, `E_del1_del3_mp`, `E_del2_del3_mp`
- Odd (12): `E_eps_del1_pp`, `E_eps_del2_pp`, `E_eps_del3_pp`, `E_eps_del1_pm`, `E_eps_del2_pm`, `E_eps_del3_pm`, `E_eps_del1_mp`, `E_eps_del2_mp`, `E_eps_del3_mp`, `E_eps_del1_mm`, `E_eps_del2_mm`, `E_eps_del3_mm`

### PBW Ordering

Two options were considered:

**Option A (ε-first)**: $\kappa < [\text{odd: } E_{\varepsilon\pm\delta}] < [\text{even: } H_k, E_{2\delta}, E_{\delta\pm\delta}]$

**Option B (Cartan-first)**: $\kappa < [\text{odd: } E_{\varepsilon\pm\delta}] < [H_k] < [\text{even roots: } E_{2\delta}, E_{\delta\pm\delta}]$

**Decision**: Option A is adopted. This is consistent with the B(0,n) convention where $\kappa$ precedes all odd generators, which precede all even generators. Within each parity sector, generators are ordered by: Cartan elements first (ascending index), then positive roots, then negative roots, then mixed-sign roots.

Full PBW ordering: $\kappa < [\text{odd}] < [\text{even}]$, where $K = 1$ is excluded from the basis.
