# Notation and Terminology

This document defines the mathematical notation and terminology used in this repository.
It is initialized during the $C(n+1)$ schema extension project.

## 1. Oscillator Generators

### Fermionic pair (standard CAR)
- **Labels**: `a_1_p` (creation, $a_1^+$), `a_1_m` (annihilation, $a_1^-$)
- **Parity**: 1 (odd)
- **Relations**: $\{a_1^-, a_1^+\} = 1$ (canonical anticommutation relation)

### Bosonic oscillators
- **Labels**: `b_k_p` (creation, $b_k^+$), `b_k_m` (annihilation, $b_k^-$) for $k = 1, \ldots, n$
- **Parity**: 0 (even)
- **Relations**: $[b_k^-, b_l^+] = \delta_{kl}$ (canonical commutation relations)

### Central elements
- **κ (kappa)**: odd central element, $p(\kappa) = 1$, $\kappa^2 = 0$ (nilpotent)
- **K**: even central identity element, $p(K) = 0$

---

## 2. Root System and Generators for C(n+1) = osp(2|2n)

### Root space decomposition
- **Even roots**: $\Delta_{\bar{0}} = \{\pm 2\delta_k\} \cup \{\pm(\delta_i \pm \delta_j) \mid 1 \leq i < j \leq n\}$
- **Odd roots**: $\Delta_{\bar{1}} = \{\pm\varepsilon \pm \delta_k \mid k = 1, \ldots, n\}$

### Even basis (Cartan + roots)
For each $n$, the even basis consists of:
- **Cartan elements**: $H_1, H_2, \ldots, H_{n+1}$ ($n+1$ generators)
- **Root generators**: $E_{\pm 2\delta_k}$, $E_{\pm(\delta_i \pm \delta_j)}$ for $1 \leq i < j \leq n$

**Counts**: Even dimension = $2n^2 + n + 1$ (Cartan: $n+1$, roots: $2n^2$)

### Odd basis (ε-roots only)
The odd basis consists of odd root generators:
- $E_{\varepsilon + \delta_k} = a_1^+ b_k^+$
- $E_{\varepsilon - \delta_k} = a_1^+ b_k^-$
- $E_{-\varepsilon + \delta_k} = a_1^- b_k^+$
- $E_{-\varepsilon - \delta_k} = a_1^- b_k^-$

**Counts**: Odd dimension = $4n$ (four generators per bosonic oscillator)

### Basis for specific cases
| Case | Even dimension | Odd dimension | Total |
|------|---|---|---|
| C(2) ($n=1$) | 4 | 4 | 8 |
| C(3) ($n=2$) | 11 | 8 | 19 |
| C(4) ($n=3$) | 22 | 12 | 34 |

---

## 3. Generator Labels (JSON Notation)

### Even generators

| Root | Label | Oscillator realization |
|---|---|---|
| $2\delta_k$ | `E_2del{k}_p` | $(b_k^+)^2/2$ |
| $-2\delta_k$ | `E_2del{k}_m` | $(b_k^-)^2/2$ |
| $\delta_i + \delta_j$ ($i<j$) | `E_del{i}_del{j}_pp` | $b_i^+ b_j^+$ |
| $\delta_i - \delta_j$ ($i<j$) | `E_del{i}_del{j}_pm` | $b_i^+ b_j^-$ |
| $-(\delta_i - \delta_j)$ ($i<j$) | `E_del{i}_del{j}_mp` | $b_i^- b_j^+$ |
| $-(\delta_i + \delta_j)$ ($i<j$) | `E_del{i}_del{j}_mm` | $b_i^- b_j^-$ |
| Cartan elements | `H_{k}` | $a_1^+ a_1^- + b_1^+ b_1^-$ or $b_{k}^+ b_{k}^- - b_{k+1}^+ b_{k+1}^-$ etc. |

### Odd generators (ε-roots)

| Root | Label | Oscillator realization | Parity |
|---|---|---|---|
| $\varepsilon + \delta_k$ | `E_eps_del{k}_pp` | $a_1^+ b_k^+$ | 1 |
| $\varepsilon - \delta_k$ | `E_eps_del{k}_pm` | $a_1^+ b_k^-$ | 1 |
| $-\varepsilon + \delta_k$ | `E_eps_del{k}_mp` | $a_1^- b_k^+$ | 1 |
| $-\varepsilon - \delta_k$ | `E_eps_del{k}_mm` | $a_1^- b_k^-$ | 1 |

**Label encoding**: The suffix encodes ε-sign and δ-sign as (ε-sign)(δ-sign) where `p` = plus, `m` = minus.

---

## 4. PBW Ordering for C(n+1)

### Chosen ordering (Option 1: ε-roots first)

The Poincaré–Birkhoff–Witt basis is ordered as:
$$\kappa < \text{[odd: } E_{\varepsilon \pm \delta_k}] < \text{[even: } H_k, E_{\pm 2\delta_k}, E_{\pm(\delta_i \pm \delta_j)}]$$

**Justification**: This ordering:
1. Extends naturally from the B(0,n) convention (which orders κ < [odd] < [even])
2. Places the ε-dependent odd generators before the purely δ-dependent even roots
3. Maintains consistency with oscillator PBW (creation operators before annihilation)
4. Simplifies computational handling in structure constant derivations

### Ordering within each group

**Odd generators** (in order):
- $E_{\varepsilon + \delta_1}, E_{\varepsilon + \delta_2}, \ldots, E_{\varepsilon + \delta_n}$
- $E_{\varepsilon - \delta_1}, E_{\varepsilon - \delta_2}, \ldots, E_{\varepsilon - \delta_n}$
- $E_{-\varepsilon + \delta_1}, E_{-\varepsilon + \delta_2}, \ldots, E_{-\varepsilon + \delta_n}$
- $E_{-\varepsilon - \delta_1}, E_{-\varepsilon - \delta_2}, \ldots, E_{-\varepsilon - \delta_n}$

**Even generators** (in order):
- Cartan: $H_1, H_2, \ldots, H_{n+1}$
- Positive pairs: $E_{\delta_1 + \delta_2}, E_{\delta_1 + \delta_3}, \ldots$ (lexicographic)
- Positive differences: $E_{\delta_1 - \delta_2}, E_{\delta_1 - \delta_3}, \ldots$
- Doubles: $E_{2\delta_1}, E_{2\delta_2}, \ldots, E_{2\delta_n}$
- Negative doubles: $E_{-2\delta_1}, E_{-2\delta_2}, \ldots$
- Negative differences: $E_{-(\delta_i - \delta_j)}$ (reverse order)
- Negative pairs: $E_{-(\delta_i + \delta_j)}$ (reverse order)

---

## 5. Inhomogeneous Deformation Parameters

For C(n+1), the deformation is parametrized by the **gb matrix**:
$$\{\mathrm{gb}_{a_1^\sigma, b_j^s} \mid \sigma \in \{+,-\}, s \in \{+,-\}, j = 1, \ldots, n\}$$

This gives **4n** parity-1 parameters total, encoding exchange relations:
$$[b_j^s, a_1^\sigma] = -\mathrm{gb}_{\sigma, j, s} \cdot \kappa$$

**Label convention in JSON**: `gb_{a_1_p, b_j_p}`, `gb_{a_1_p, b_j_m}`, `gb_{a_1_m, b_j_p}`, `gb_{a_1_m, b_j_m}`
