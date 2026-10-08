# Notation and Terminology

This document defines the mathematical notation and terminology used in this repository.
It is initialized during the $C(n+1)$ schema extension project.

## Conventions

### Oscillator Realization for C(n+1) = osp(2|2n)

**Generators**:
- Standard fermionic pair: $a_1^+, a_1^-$ with CAR $\{a_1^-, a_1^+\} = 1$ (parity 1)
- Bosonic oscillators: $b_k^+, b_k^-$ ($k=1,\ldots,n$) with CCR $[b_k^-, b_l^+] = \delta_{kl}$ (parity 0)

**Notation in JSON schema**:
- Creation operators: `_p` (plus) for `^+`, `_m` (minus) for `^-`
- Fermionic: `a_1_p`, `a_1_m`
- Bosonic: `b_k_p`, `b_k_m`

### PBW Basis Ordering for C(n+1)

**Chosen convention** (Option 1):
$$\kappa < \text{[odd: } E_{\varepsilon \pm \delta_k}] < \text{[even: } H_i, E_{2\delta_k}, E_{\delta_i \pm \delta_j}]$$

This places:
1. Central odd element $\kappa$ (nilpotent, $\kappa^2 = 0$)
2. All odd-parity generators ($E_{\pm\varepsilon \pm \delta_k}$)
3. Even-parity generators: Cartan elements ($H_i$), positive even roots, negative even roots

### Generator Label Convention for C(n+1)

| Mathematical Root | JSON Label | Oscillator |
|---|---|---|
| $2\delta_k$ | `E_2del{k}_p` | $(b_k^+)^2$ |
| $-2\delta_k$ | `E_2del{k}_m` | $(b_k^-)^2$ |
| $\delta_i + \delta_j$ ($i<j$) | `E_del{i}_del{j}_pp` | $b_i^+ b_j^+$ |
| $\delta_i - \delta_j$ ($i<j$) | `E_del{i}_del{j}_pm` | $b_i^+ b_j^-$ |
| $-(\delta_i - \delta_j)$ ($i<j$) | `E_del{i}_del{j}_mp` | $b_i^- b_j^+$ |
| $-(\delta_i + \delta_j)$ ($i<j$) | `E_del{i}_del{j}_mm` | $b_i^- b_j^-$ |
| $\varepsilon + \delta_k$ | `E_eps1_del{k}_pp` | $a_1^+ b_k^+$ |
| $\varepsilon - \delta_k$ | `E_eps1_del{k}_pm` | $a_1^+ b_k^-$ |
| $-\varepsilon + \delta_k$ | `E_eps1_del{k}_mp` | $a_1^- b_k^+$ |
| $-\varepsilon - \delta_k$ | `E_eps1_del{k}_mm` | $a_1^- b_k^-$ |
| Cartan: $H_i$ ($i=1,\ldots,n+1$) | `H_{i}` | Complex expression (see structure docs) |

### Basis Dimensions for C(n+1) = osp(2|2n)

**Formula**:
- Even dimension: $2n^2 + n + 1$
- Odd dimension: $4n$
- Total: $2n^2 + 5n + 1$

**Examples**:

| $n$ (bosonic rank) | Algebra | Even | Odd | Total |
|---|---|---|---|---|
| 1 | C(2) = osp(2\|2) | 4 | 4 | 8 |
| 2 | C(3) = osp(2\|4) | 11 | 8 | 19 |
| 3 | C(4) = osp(2\|6) | 22 | 12 | 34 |

### Central Elements

- **$\kappa$**: Odd central element (parity 1), nilpotent ($\kappa^2 = 0$), serves as formal symbol of deformation
- **$K$**: Even central element (parity 0), identified with scalar 1, excluded from basis lists
