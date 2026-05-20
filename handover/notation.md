# Notation and Terminology

This document defines the mathematical notation and terminology used in this repository.
It is initialized during the $C(n+1)$ schema extension project.

## Conventions

### Scope

For the $C(n+1)$ extension in this repository, we use the Frappat-style root
symbols

$$
\pm 2\delta_k,\quad \pm(\delta_i \pm \delta_j),\quad \pm\varepsilon \pm \delta_k
\qquad (1 \le i < j \le n,\ 1 \le k \le n),
$$

with $C(n+1) = \mathfrak{osp}(2|2n)$.

### Oscillator labels

- Standard fermionic pair:
  - `a_1_p` for $a_1^+$
  - `a_1_m` for $a_1^-$
- Bosonic oscillators:
  - `b_k_p` for $b_k^+$
  - `b_k_m` for $b_k^-$

The first sign in an odd generator label records the fermionic oscillator, and
the second sign records the bosonic oscillator.

### Cartan generators

The Cartan basis is labeled `H_1, ..., H_{n+1}` with the oscillator
realizations

$$
H_1 = a_1^+ a_1^- + b_1^+ b_1^-,
$$
$$
H_k = b_{k-1}^+ b_{k-1}^- - b_k^+ b_k^- \qquad (2 \le k \le n),
$$
$$
H_{n+1} = -\,b_n^+ b_n^- - \tfrac{1}{2}.
$$

### Root-generator labels

#### Even generators

| Root | Label | Oscillator realization |
|---|---|---|
| $2\delta_k$ | `E_2del{k}_p` | $(b_k^+)^2$ |
| $-2\delta_k$ | `E_2del{k}_m` | $(b_k^-)^2$ |
| $\delta_i + \delta_j$ ($i<j$) | `E_del{i}_del{j}_pp` | $b_i^+ b_j^+$ |
| $\delta_i - \delta_j$ ($i<j$) | `E_del{i}_del{j}_pm` | $b_i^+ b_j^-$ |
| $-(\delta_i + \delta_j)$ ($i<j$) | `E_del{i}_del{j}_mm` | $b_i^- b_j^-$ |
| $-\delta_i + \delta_j$ ($i<j$) | `E_del{i}_del{j}_mp` | $b_i^- b_j^+$ |

#### Odd generators

| Root | Label | Oscillator realization |
|---|---|---|
| $\varepsilon + \delta_k$ | `E_eps1_del{k}_pp` | $a_1^+ b_k^+$ |
| $\varepsilon - \delta_k$ | `E_eps1_del{k}_pm` | $a_1^+ b_k^-$ |
| $-\varepsilon + \delta_k$ | `E_eps1_del{k}_mp` | $a_1^- b_k^+$ |
| $-\varepsilon - \delta_k$ | `E_eps1_del{k}_mm` | $a_1^- b_k^-$ |

### Approved PBW ordering (Issue I01-1, Option A)

The adopted PBW convention is

$$
\kappa < [\text{odd generators}] < [\text{even generators}].
$$

- `K = 1` is not treated as an independent basis element.
- `kappa` is ordered before the basis blocks but is not part of the even/odd
  basis lists below.

#### Odd block order

For each family, index `k` increases from `1` to `n`:

1. `E_eps1_del{k}_pp`
2. `E_eps1_del{k}_pm`
3. `E_eps1_del{k}_mp`
4. `E_eps1_del{k}_mm`

Equivalently, the odd block is

`E_eps1_del1_pp, ..., E_eps1_deln_pp, E_eps1_del1_pm, ..., E_eps1_deln_pm, E_eps1_del1_mp, ..., E_eps1_deln_mp, E_eps1_del1_mm, ..., E_eps1_deln_mm`.

#### Even block order

1. Cartan generators `H_1, ..., H_{n+1}`
2. `E_2del{k}_p` for `k = 1, ..., n`
3. `E_del{i}_del{j}_pp` in lexicographic `(i, j)` order
4. `E_del{i}_del{j}_pm` in lexicographic `(i, j)` order
5. `E_2del{k}_m` for `k = 1, ..., n`
6. `E_del{i}_del{j}_mm` in lexicographic `(i, j)` order
7. `E_del{i}_del{j}_mp` in lexicographic `(i, j)` order

### Ordered basis lists for low ranks

#### C(2) = osp(2|2), n = 1

- Even basis:
  - `H_1`, `H_2`, `E_2del1_p`, `E_2del1_m`
- Odd basis:
  - `E_eps1_del1_pp`, `E_eps1_del1_pm`, `E_eps1_del1_mp`, `E_eps1_del1_mm`

#### C(3) = osp(2|4), n = 2

- Even basis:
  - `H_1`, `H_2`, `H_3`
  - `E_2del1_p`, `E_2del2_p`
  - `E_del1_del2_pp`, `E_del1_del2_pm`
  - `E_2del1_m`, `E_2del2_m`
  - `E_del1_del2_mm`, `E_del1_del2_mp`
- Odd basis:
  - `E_eps1_del1_pp`, `E_eps1_del2_pp`
  - `E_eps1_del1_pm`, `E_eps1_del2_pm`
  - `E_eps1_del1_mp`, `E_eps1_del2_mp`
  - `E_eps1_del1_mm`, `E_eps1_del2_mm`

#### C(4) = osp(2|6), n = 3

- Even basis:
  - `H_1`, `H_2`, `H_3`, `H_4`
  - `E_2del1_p`, `E_2del2_p`, `E_2del3_p`
  - `E_del1_del2_pp`, `E_del1_del3_pp`, `E_del2_del3_pp`
  - `E_del1_del2_pm`, `E_del1_del3_pm`, `E_del2_del3_pm`
  - `E_2del1_m`, `E_2del2_m`, `E_2del3_m`
  - `E_del1_del2_mm`, `E_del1_del3_mm`, `E_del2_del3_mm`
  - `E_del1_del2_mp`, `E_del1_del3_mp`, `E_del2_del3_mp`
- Odd basis:
  - `E_eps1_del1_pp`, `E_eps1_del2_pp`, `E_eps1_del3_pp`
  - `E_eps1_del1_pm`, `E_eps1_del2_pm`, `E_eps1_del3_pm`
  - `E_eps1_del1_mp`, `E_eps1_del2_mp`, `E_eps1_del3_mp`
  - `E_eps1_del1_mm`, `E_eps1_del2_mm`, `E_eps1_del3_mm`
