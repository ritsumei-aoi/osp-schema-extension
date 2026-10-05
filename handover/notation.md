# Notation and Terminology

This document defines the mathematical notation and terminology used in this repository for the $C(n+1) = \mathfrak{osp}(2|2n)$ schema extension.

## 1. Algebraic & Oscillator Conventions

- **Algebra**: $C(n+1) = \mathfrak{osp}(2|2n)$, with bosonic rank $n$.
  - $n=1$: $C(2) = \mathfrak{osp}(2|2)$, superdimension $4 \mid 4$ (total 8).
  - $n=2$: $C(3) = \mathfrak{osp}(2|4)$, superdimension $11 \mid 8$ (total 19).
  - $n=3$: $C(4) = \mathfrak{osp}(2|6)$, superdimension $22 \mid 12$ (total 34).
  - Superdimension formula: even $\dim = 2n^2 + n + 1$, odd $\dim = 4n$, total $= 2n^2 + 5n + 1$.

- **Oscillators**:
  - **Fermionic pair**: $a_1^+, a_1^-$ with CAR $\{a_1^-, a_1^+\} = 1$, $\{a_1^\pm, a_1^\pm\} = 0$, parity $p(a_1^\pm) = 1$.
  - **Bosonic oscillators**: $b_k^+, b_k^-$ ($1 \le k \le n$) with CCR $[b_k^-, b_l^+] = \delta_{kl}$, $[b_k^\pm, b_l^\pm] = 0$, parity $p(b_k^\pm) = 0$.

- **Central elements**:
  - $\kappa$: odd central element ($p(\kappa) = 1$, $\kappa^2 = 0$) parametrizing the 2-cocycle deformation.

## 2. Generator Label Conventions

### Even Generators ($\mathfrak{g}_{\bar{0}}$)
- **Cartan generators**: `H_1`, `H_2`, ..., `H_{n+1}`.
  - $H_1 = a_1^+ a_1^- + b_1^+ b_1^-$
  - $H_k = b_{k-1}^+ b_{k-1}^- - b_k^+ b_k^-$ ($2 \le k \le n$)
  - $H_{n+1} = -b_n^+ b_n^- - \frac{1}{2}$
- **Bosonic roots $\pm 2\delta_k$**: `E_2del{k}_p` ($(b_k^+)^2$), `E_2del{k}_m` ($(b_k^-)^2$) for $1 \le k \le n$.
- **Bosonic roots $\pm\delta_i \pm \delta_j$ ($1 \le i < j \le n$)**:
  - `E_del{i}_del{j}_pp` ($b_i^+ b_j^+$)
  - `E_del{i}_del{j}_mm` ($b_i^- b_j^-$)
  - `E_del{i}_del{j}_pm` ($b_i^+ b_j^-$)
  - `E_del{i}_del{j}_mp` ($b_i^- b_j^+$)

### Odd Generators ($\mathfrak{g}_{\bar{1}}$)
- **Fermionic-bosonic roots $\pm\varepsilon \pm \delta_k$ ($1 \le k \le n$)**:
  - `E_eps1_del{k}_pp` ($a_1^+ b_k^+$)
  - `E_eps1_del{k}_pm` ($a_1^+ b_k^-$)
  - `E_eps1_del{k}_mp` ($a_1^- b_k^+$)
  - `E_eps1_del{k}_mm` ($a_1^- b_k^-$)

## 3. PBW Ordering Convention

We adopt **Option A (Parity-Block PBW Ordering)**:
$$\kappa < [\text{odd basis}] < [\text{even basis}]$$

- **Odd sector**: ordered lexicographically by bosonic index $k$, then sign pair `pp < pm < mp < mm`.
- **Even sector**: Cartans `H_1, ..., H_{n+1}`, followed by positive roots, then negative roots.

**Justification**: Option A directly aligns with the $B(0,n)$ v5.0 schema convention (`κ < [odd] < [even]`), ensuring clean block-matrix decomposition in coboundary operator computations and max compatibility with downstream linear algebra routines.

## 4. Concrete Basis Specifications

### C(2) = osp(2|2) ($n=1$)
- **Even (4)**: `H_1`, `H_2`, `E_2del1_p`, `E_2del1_m`
- **Odd (4)**: `E_eps1_del1_pp`, `E_eps1_del1_pm`, `E_eps1_del1_mp`, `E_eps1_del1_mm`

### C(3) = osp(2|4) ($n=2$)
- **Even (11)**: `H_1`, `H_2`, `H_3`, `E_2del1_p`, `E_2del2_p`, `E_del1_del2_pp`, `E_2del1_m`, `E_2del2_m`, `E_del1_del2_mm`, `E_del1_del2_pm`, `E_del1_del2_mp`
- **Odd (8)**: `E_eps1_del1_pp`, `E_eps1_del1_pm`, `E_eps1_del1_mp`, `E_eps1_del1_mm`, `E_eps1_del2_pp`, `E_eps1_del2_pm`, `E_eps1_del2_mp`, `E_eps1_del2_mm`

### C(4) = osp(2|6) ($n=3$)
- **Even (22)**:
  - Cartans (4): `H_1`, `H_2`, `H_3`, `H_4`
  - $2\delta$ roots (6): `E_2del1_p`, `E_2del2_p`, `E_2del3_p`, `E_2del1_m`, `E_2del2_m`, `E_2del3_m`
  - $\delta_i \pm \delta_j$ roots (12): `E_del1_del2_pp`, `E_del1_del3_pp`, `E_del2_del3_pp`, `E_del1_del2_mm`, `E_del1_del3_mm`, `E_del2_del3_mm`, `E_del1_del2_pm`, `E_del1_del3_pm`, `E_del2_del3_pm`, `E_del1_del2_mp`, `E_del1_del3_mp`, `E_del2_del3_mp`
- **Odd (12)**:
  - `E_eps1_del1_pp`, `E_eps1_del1_pm`, `E_eps1_del1_mp`, `E_eps1_del1_mm`,
  - `E_eps1_del2_pp`, `E_eps1_del2_pm`, `E_eps1_del2_mp`, `E_eps1_del2_mm`,
  - `E_eps1_del3_pp`, `E_eps1_del3_pm`, `E_eps1_del3_mp`, `E_eps1_del3_mm`
