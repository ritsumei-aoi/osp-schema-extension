# Notation and Terminology

This document defines the mathematical notation and terminology used in this repository.
It is initialized during the $C(n+1)$ schema extension project.

## Conventions

### Root system vectors
- $\varepsilon$: fermionic root vector (labeled `eps1` in generator names)
- $\delta_k$ ($k = 1, \ldots, n$): bosonic root vectors (labeled `del{k}` in generator names)

### Generator label convention for C(n+1) = osp(2|2n)

#### Even generators (parity 0)

| Root | Label | Oscillator realization |
|---|---|---|
| Cartan $H_k$ ($k=1,\ldots,n+1$) | `H_k` | See below |
| $2\delta_k$ | `E_2del{k}_p` | $(b_k^+)^2$ |
| $-2\delta_k$ | `E_2del{k}_m` | $(b_k^-)^2$ |
| $\delta_i + \delta_j$ ($i<j$) | `E_del{i}_del{j}_pp` | $b_i^+ b_j^+$ |
| $\delta_i - \delta_j$ ($i<j$) | `E_del{i}_del{j}_pm` | $b_i^+ b_j^-$ |
| $-\delta_i + \delta_j$ ($i<j$) | `E_del{i}_del{j}_mp` | $b_i^- b_j^+$ |
| $-(\delta_i + \delta_j)$ ($i<j$) | `E_del{i}_del{j}_mm` | $b_i^- b_j^-$ |

#### Odd generators (parity 1)

| Root | Label | Oscillator realization |
|---|---|---|
| $\varepsilon + \delta_k$ | `E_eps1_del{k}_pp` | $a_1^+ b_k^+$ |
| $\varepsilon - \delta_k$ | `E_eps1_del{k}_pm` | $a_1^+ b_k^-$ |
| $-\varepsilon + \delta_k$ | `E_eps1_del{k}_mp` | $a_1^- b_k^+$ |
| $-\varepsilon - \delta_k$ | `E_eps1_del{k}_mm` | $a_1^- b_k^-$ |

#### Cartan generators

| Label | Oscillator realization | Notes |
|---|---|---|
| `H_1` | $a_1^+ a_1^- + b_1^+ b_1^-$ | Involves fermionic number operator |
| `H_k` ($2 \leq k \leq n$) | $b_{k-1}^+ b_{k-1}^- - b_k^+ b_k^-$ | Standard bosonic Cartan |
| `H_{n+1}` | $-b_n^+ b_n^- - \frac{1}{2}$ | Terminal Cartan |

### PBW Ordering for C(n+1)

**Convention chosen**: κ < [odd generators] < [even generators]

Within each parity sector, generators are ordered as follows:

**Odd sector** (ascending by root):
$$
E_{\varepsilon+\delta_1}, E_{\varepsilon+\delta_2}, \ldots, E_{\varepsilon+\delta_n},
E_{\varepsilon-\delta_n}, \ldots, E_{\varepsilon-\delta_1},
E_{-\varepsilon+\delta_1}, \ldots, E_{-\varepsilon+\delta_n},
E_{-\varepsilon-\delta_n}, \ldots, E_{-\varepsilon-\delta_1}
$$

Labels:
```
E_eps1_del{1}_pp, ..., E_eps1_del{n}_pp,
E_eps1_del{n}_pm, ..., E_eps1_del{1}_pm,
E_eps1_del{1}_mp, ..., E_eps1_del{n}_mp,
E_eps1_del{n}_mm, ..., E_eps1_del{1}_mm
```

**Even sector** (Cartan first, then positive roots, negative roots, mixed roots):
```
H_1, ..., H_{n+1},
E_2del{1}_p, ..., E_2del{n}_p,
E_del{i}_del{j}_pp (i<j),
E_2del{1}_m, ..., E_2del{n}_m,
E_del{i}_del{j}_mm (i<j),
E_del{i}_del{j}_pm (i<j),
E_del{i}_del{j}_mp (i<j)
```

### Even and Odd Basis Lists

#### C(2) = osp(2|2), n=1
- **Even** (4 generators): `H_1, H_2, E_2del1_p, E_2del1_m`
- **Odd** (4 generators): `E_eps1_del1_pp, E_eps1_del1_pm, E_eps1_del1_mp, E_eps1_del1_mm`
- **Total**: 8 = 4 + 4
- **Dimension check**: even = $2(1)^2 + 1 + 1 = 4$, odd = $4(1) = 4$, total = 8 ✓

#### C(3) = osp(2|4), n=2
- **Even** (11 generators):
  `H_1, H_2, H_3, E_2del1_p, E_2del2_p, E_del1_del2_pp, E_2del1_m, E_2del2_m, E_del1_del2_mm, E_del1_del2_pm, E_del1_del2_mp`
- **Odd** (8 generators):
  `E_eps1_del1_pp, E_eps1_del2_pp, E_eps1_del2_pm, E_eps1_del1_pm, E_eps1_del1_mp, E_eps1_del2_mp, E_eps1_del2_mm, E_eps1_del1_mm`
- **Total**: 19 = 11 + 8
- **Dimension check**: even = $2(2)^2 + 2 + 1 = 11$, odd = $4(2) = 8$, total = 19 ✓

#### C(4) = osp(2|6), n=3
- **Even** (22 generators):
  `H_1, H_2, H_3, H_4, E_2del1_p, E_2del2_p, E_2del3_p, E_del1_del2_pp, E_del1_del3_pp, E_del2_del3_pp, E_2del1_m, E_2del2_m, E_2del3_m, E_del1_del2_mm, E_del1_del3_mm, E_del2_del3_mm, E_del1_del2_pm, E_del1_del3_pm, E_del2_del3_pm, E_del1_del2_mp, E_del1_del3_mp, E_del2_del3_mp`
- **Odd** (12 generators):
  `E_eps1_del1_pp, E_eps1_del2_pp, E_eps1_del3_pp, E_eps1_del3_pm, E_eps1_del2_pm, E_eps1_del1_pm, E_eps1_del1_mp, E_eps1_del2_mp, E_eps1_del3_mp, E_eps1_del3_mm, E_eps1_del2_mm, E_eps1_del1_mm`
- **Total**: 34 = 22 + 12
- **Dimension check**: even = $2(3)^2 + 3 + 1 = 22$, odd = $4(3) = 12$, total = 34 ✓

### Oscillator generators

- **Fermions**: $a_1^+$ (`a_1_p`), $a_1^-$ (`a_1_m`), parity 1, satisfying $\{a_1^-, a_1^+\} = 1$
- **Bosons**: $b_k^+$ (`b_{k}_p`), $b_k^-$ (`b_{k}_m`), parity 0, satisfying $[b_k^-, b_l^+] = \delta_{kl}$

### Central elements

- $\kappa$: odd central element ($p(\kappa) = 1$, $\kappa^2 = 0$), used in deformation
- $K$: even central element ($p(K) = 0$), identified with scalar 1 in all applications
