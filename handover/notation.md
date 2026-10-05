# Notation and Terminology

This document defines the mathematical notation and terminology used in this repository.
It is initialized during the $C(n+1)$ schema extension project.

## Conventions

### Oscillator Pair Labels

For $C(n+1) = \mathfrak{osp}(2|2n)$:

**Fermionic oscillators** (single standard pair):
- `a_1_p` := $a_1^+$ (fermionic creation, CAR: $\{a_1^-, a_1^+\} = 1$)
- `a_1_m` := $a_1^-$ (fermionic annihilation)

**Bosonic oscillators** (one pair per index $k = 1, \ldots, n$):
- `b_k_p` := $b_k^+$ (bosonic creation, CCR: $[b_k^-, b_l^+] = \delta_{kl}$)
- `b_k_m` := $b_k^-$ (bosonic annihilation)

**Central elements**:
- `κ` (kappa): odd central element, $p(\kappa) = 1$, $\kappa^2 = 0$
- `K`: even central identity element (identified with scalar 1 in current applications)

### Root Generator Labels

Extended from $B(0,n)$ convention. For each root $\alpha$, the generator is labeled `E_{root_label}`.

**Odd generators** (associated with roots $\pm\varepsilon \pm \delta_k$, parity 1):
| Root | Label | Realization | Sign notation |
|---|---|---|---|
| $\varepsilon + \delta_k$ | `E_eps1_del{k}_pp` | $a_1^+ b_k^+$ | (fermionic +, bosonic +) |
| $\varepsilon - \delta_k$ | `E_eps1_del{k}_pm` | $a_1^+ b_k^-$ | (fermionic +, bosonic -) |
| $-\varepsilon + \delta_k$ | `E_eps1_del{k}_mp` | $a_1^- b_k^+$ | (fermionic -, bosonic +) |
| $-\varepsilon - \delta_k$ | `E_eps1_del{k}_mm` | $a_1^- b_k^-$ | (fermionic -, bosonic -) |

**Even generators** (associated with roots $\pm 2\delta_k$ and $\pm\delta_i \pm \delta_j$, parity 0):
| Root | Label | Realization |
|---|---|---|
| $2\delta_k$ | `E_2del{k}_p` | $(b_k^+)^2$ |
| $-2\delta_k$ | `E_2del{k}_m` | $(b_k^-)^2$ |
| $\delta_i + \delta_j$ ($i<j$) | `E_del{i}_del{j}_pp` | $b_i^+ b_j^+$ |
| $\delta_i - \delta_j$ ($i<j$) | `E_del{i}_del{j}_pm` | $b_i^+ b_j^-$ |
| $-(\delta_i - \delta_j)$ ($i<j$) | `E_del{i}_del{j}_mp` | $b_i^- b_j^+$ |
| $-(\delta_i + \delta_j)$ ($i<j$) | `E_del{i}_del{j}_mm` | $b_i^- b_j^-$ |

**Cartan generators** (parity 0):
- `H_k` for $k = 1, 2, \ldots, n+1$

### PBW Ordering

For $C(n+1)$, the Poincaré–Birkhoff–Witt ordering is:

$$\kappa < [E_{\text{odd}}] < [E_{\text{even}}]$$

**Odd generators** (ordered by $k$, then by sign pattern):
$$E_{\varepsilon 1 \delta_1}^{pp}, E_{\varepsilon 1 \delta_1}^{pm}, E_{\varepsilon 1 \delta_1}^{mp}, E_{\varepsilon 1 \delta_1}^{mm}, \ldots, E_{\varepsilon 1 \delta_n}^{mm}$$

**Even generators** (ordered by type, then by indices):
1. Cartan: $H_1, H_2, \ldots, H_{n+1}$
2. Doubled roots: $E_{2\delta_1}^p, E_{2\delta_1}^m, \ldots, E_{2\delta_n}^m$
3. Off-diagonal roots: $E_{\delta_1 \delta_2}^{pp}, E_{\delta_1 \delta_2}^{pm}, \ldots, E_{\delta_{n-1} \delta_n}^{mm}$

### Dimension Formulas

For $C(n+1) = \mathfrak{osp}(2|2n)$:
- Even dimension: $2n^2 + n + 1$
- Odd dimension: $4n$
- Total dimension: $2n^2 + 5n + 1$

| $n$ | even | odd | total | Algebra |
|---|---|---|---|---|
| 1 | 4 | 4 | 8 | C(2) |
| 2 | 11 | 8 | 19 | C(3) |
| 3 | 22 | 12 | 34 | C(4) |

### Deformation Parameters

For inhomogeneous deformation (Schema 2 and beyond), the $gb$ matrix contains parity-1 parameters:
$$\{gb_{a_1^\sigma, b_j^s} \mid \sigma, s \in \{+, -\}, j = 1, \ldots, n\}$$

Total: $4n$ deformation parameters.
