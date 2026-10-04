# Notation and Terminology

This document defines the mathematical notation and terminology used in this repository for the $C(n+1) = \mathfrak{osp}(2|2n)$ Lie superalgebra schema extension study.

## 1. Algebra Specifications

- **Algebra family**: $C(n+1) = \mathfrak{osp}(2|2n)$, with $m=1$ fermionic rank and $n$ bosonic rank.
- **Superdimension**: $\dim(\mathfrak{g}) = (2n^2 + n + 1) \mid 4n$, total dimension $2n^2 + 5n + 1$.
  - $n=1$ ($C(2) = \mathfrak{osp}(2|2)$): even = 4, odd = 4, total = 8.
  - $n=2$ ($C(3) = \mathfrak{osp}(2|4)$): even = 11, odd = 8, total = 19.
  - $n=3$ ($C(4) = \mathfrak{osp}(2|6)$): even = 22, odd = 12, total = 34.

## 2. Oscillator Generators & Parity

- **Fermionic oscillators**: Standard CAR pair $(a_1^+, a_1^-)$ with parity $p(a_1^\pm) = 1$, satisfying $\{a_1^-, a_1^+\} = 1$, $(a_1^\pm)^2 = 0$.
- **Bosonic oscillators**: Standard CCR pairs $(b_k^+, b_k^-)$ for $k = 1, \dots, n$ with parity $p(b_k^\pm) = 0$, satisfying $[b_k^-, b_l^+] = \delta_{kl}$, $[b_k^\pm, b_l^\pm] = 0$.
- **Central elements**:
  - $\kappa$: odd nilpotent central extension element ($p(\kappa) = 1$, $\kappa^2 = 0$).
  - $K$: even identity element ($p(K) = 0$).

## 3. Generator Labels & Oscillator Realizations

### 3.1 Even Generators ($\mathfrak{g}_{\bar{0}}$)
- **Cartan generators** ($n+1$ total):
  - $H_1 = a_1^+ a_1^- + b_1^+ b_1^-$
  - $H_k = b_{k-1}^+ b_{k-1}^- - b_k^+ b_k^-$ ($2 \le k \le n$)
  - $H_{n+1} = -b_n^+ b_n^- - \frac{1}{2}$
- **Bosonic root generators**:
  - $2\delta_k$: `E_2del{k}_p` $= \frac{1}{2}(b_k^+)^2$
  - $-2\delta_k$: `E_2del{k}_m` $= \frac{1}{2}(b_k^-)^2$
  - $\delta_i + \delta_j$ ($i < j$): `E_del{i}_del{j}_pp` $= b_i^+ b_j^+$
  - $-\delta_i - \delta_j$ ($i < j$): `E_del{i}_del{j}_mm` $= b_i^- b_j^-$
  - $\delta_i - \delta_j$ ($i < j$): `E_del{i}_del{j}_pm` $= b_i^+ b_j^-$
  - $-\delta_i + \delta_j$ ($i < j$): `E_del{i}_del{j}_mp` $= b_i^- b_j^+$

### 3.2 Odd Generators ($\mathfrak{g}_{\bar{1}}$)
For $k = 1, \dots, n$:
- $\varepsilon + \delta_k$: `E_eps1_del{k}_pp` $= a_1^+ b_k^+$
- $\varepsilon - \delta_k$: `E_eps1_del{k}_pm` $= a_1^+ b_k^-$
- $-\varepsilon + \delta_k$: `E_eps1_del{k}_mp` $= a_1^- b_k^+$
- $-\varepsilon - \delta_k$: `E_eps1_del{k}_mm` $= a_1^- b_k^-$

## 4. Basis Lists for $n=1, 2, 3$

### $C(2)$ ($n=1$)
- **Even** (4): `["H_1", "H_2", "E_2del1_p", "E_2del1_m"]`
- **Odd** (4): `["E_eps1_del1_pp", "E_eps1_del1_pm", "E_eps1_del1_mp", "E_eps1_del1_mm"]`

### $C(3)$ ($n=2$)
- **Even** (11): `["H_1", "H_2", "H_3", "E_2del1_p", "E_2del2_p", "E_del1_del2_pp", "E_2del1_m", "E_2del2_m", "E_del1_del2_mm", "E_del1_del2_pm", "E_del1_del2_mp"]`
- **Odd** (8): `["E_eps1_del1_pp", "E_eps1_del1_pm", "E_eps1_del1_mp", "E_eps1_del1_mm", "E_eps1_del2_pp", "E_eps1_del2_pm", "E_eps1_del2_mp", "E_eps1_del2_mm"]`

### $C(4)$ ($n=3$)
- **Even** (22): `["H_1", "H_2", "H_3", "H_4", "E_2del1_p", "E_2del2_p", "E_2del3_p", "E_del1_del2_pp", "E_del1_del3_pp", "E_del2_del3_pp", "E_2del1_m", "E_2del2_m", "E_2del3_m", "E_del1_del2_mm", "E_del1_del3_mm", "E_del2_del3_mm", "E_del1_del2_pm", "E_del1_del2_mp", "E_del1_del3_pm", "E_del1_del3_mp", "E_del2_del3_pm", "E_del2_del3_mp"]`
- **Odd** (12): `["E_eps1_del1_pp", "E_eps1_del1_pm", "E_eps1_del1_mp", "E_eps1_del1_mm", "E_eps1_del2_pp", "E_eps1_del2_pm", "E_eps1_del2_mp", "E_eps1_del2_mm", "E_eps1_del3_pp", "E_eps1_del3_pm", "E_eps1_del3_mp", "E_eps1_del3_mm"]`

## 5. PBW Ordering Convention

We adopt **Parity-Grouped PBW Ordering** (Option A):
```
κ < [odd generators] < [even generators]
```
Specifically:
1. `κ` (odd central element)
2. `[odd generators]` ordered by index $k=1,\dots,n$, then by sign suffix (`pp`, `pm`, `mp`, `mm`).
3. `[even generators]` ordered by Cartans (`H_1, ..., H_{n+1}`), then positive roots, then negative roots, then mixed roots.

### Ordering Comparison & Justification
- **Option A (Parity-Grouped: `κ < [odd] < [even]`)**: Selected. Maintains 1-to-1 structure alignment with the $B(0,n)$ v5.0 schema convention, keeping odd and even submodules cleanly separated.
- **Option B (Root-Height / Weight Ordering: `κ < [negative] < [Cartan] < [positive]`)**: Considered but rejected because mixing parities across root height increases complexity in matrix block decompositions for coboundary solvers.
