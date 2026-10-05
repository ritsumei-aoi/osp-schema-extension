# Notation and Terminology

This document defines the mathematical notation and terminology used in this repository.
It is initialized during the $C(n+1)$ schema extension project.

## Conventions

### 1. Root System Notation

For $C(n+1) = \mathfrak{osp}(2|2n)$:
- $\varepsilon$: fermionic coordinate (parity 1)
- $\delta_k$ ($k = 1, \ldots, n$): bosonic coordinates (parity 0)
- $H_k$: Cartan elements (parity 0)

**Even roots** (parity 0): $\pm 2\delta_k$, $\pm(\delta_i \pm \delta_j)$ for $i < j$.

**Odd roots** (parity 1): $\pm \varepsilon \pm \delta_k$ for $k = 1, \ldots, n$.

### 2. Oscillator Realization

**Bosonic oscillators**: $b_k^\pm$ ($k = 1, \ldots, n$) with $[b_k^-, b_l^+] = \delta_{kl}$.

**Fermionic pair**: $a_1^\pm$ with $\{a_1^-, a_1^+\} = 1$ and parity $p(a_1^\pm) = 1$.

### 3. PBW Ordering (Fermionic Priority)

**Height definition**: Sum of absolute values of coefficients in a root.

**Ordering**:
- Height 1: $\varepsilon < \delta_1 < \delta_2 < \cdots < \delta_n$
- Height 2: $2\varepsilon, \varepsilon + \delta_1, \varepsilon - \delta_1, \ldots, \varepsilon \pm \delta_n, \delta_1 + \delta_2, \ldots, 2\delta_n$
- Higher heights: recursive application of the same rule.

**Rationale**: The fermionic coordinate $\varepsilon$ is the algebraic novelty of $C(n+1)$ compared to $B(0,n)$, justifying its priority.

### 4. Generator Label Convention (JSON Schema)

Labels follow the pattern: `E_<root>_<sign>` or `H_<index>` for Cartan elements.

| Root | Label | Oscillator Realization |
|---|---|---|
| Cartan | `H{k}` | Cartan element index |
| $2\delta_k$ | `E_2del{k}_p` | $(b_k^+)^2$ or $(1/2)(b_k^+)^2$ |
| $-2\delta_k$ | `E_2del{k}_m` | $(b_k^-)^2$ or $(1/2)(b_k^-)^2$ |
| $\delta_i + \delta_j$ ($i<j$) | `E_del{i}_del{j}_pp` | $b_i^+ b_j^+$ |
| $\delta_i - \delta_j$ ($i<j$) | `E_del{i}_del{j}_pm` | $b_i^+ b_j^-$ |
| $-\delta_i + \delta_j$ ($i<j$) | `E_del{i}_del{j}_mp` | $b_i^- b_j^+$ |
| $-\delta_i - \delta_j$ ($i<j$) | `E_del{i}_del{j}_mm` | $b_i^- b_j^-$ |
| $\varepsilon + \delta_k$ | `E_eps_del{k}_pp` | $a_1^+ b_k^+$ |
| $\varepsilon - \delta_k$ | `E_eps_del{k}_pm` | $a_1^+ b_k^-$ |
| $-\varepsilon + \delta_k$ | `E_eps_del{k}_mp` | $a_1^- b_k^+$ |
| $-\varepsilon - \delta_k$ | `E_eps_del{k}_mm` | $a_1^- b_k^-$ |

**Sign convention**:
- `_p` or `_pp`, `_pm`, `_mp`, `_mm`: First letter is sign of $\varepsilon$ (or first $\delta$ if no $\varepsilon$), second letter is sign of $\delta_k$.
- For $\delta$ pairs: first `p/m` is sign of $\delta_i$, second is sign of $\delta_j$.

### 5. Central Element

- **Symbol**: $\kappa$ (parity 1, nilpotent: $\kappa^2 = 0$)
- **Label in schema**: `K`
- **Role**: Central extension parameter for deformation
