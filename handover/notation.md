# Notation and Terminology

This document defines the mathematical notation and terminology used in this repository.
It is initialized during the $C(n+1)$ schema extension project.

## Conventions

## C(n+1) = osp(2|2n)

Write the orthogonal roots as $\varepsilon,\delta_1,\ldots,\delta_n$.
The even roots are $\pm2\delta_k$ and $\pm\delta_i\pm\delta_j$ ($i<j$);
the odd roots are $\pm\varepsilon\pm\delta_k$. The even subalgebra includes
the $\mathfrak{so}(2)$ direction, so the Cartan basis is
$H_1,\ldots,H_{n+1}$.

### Generator labels

Use `E_2del{k}_p` and `E_2del{k}_m` for roots $2\delta_k$ and
$-2\delta_k$. For $i<j$, use `E_del{i}_del{j}_pp`, `_pm`, `_mp`, and
`_mm` for $\delta_i+\delta_j$, $\delta_i-\delta_j$,
$-\delta_i+\delta_j$, and $-\delta_i-\delta_j$, respectively. These
generators are even.

For the odd roots, use `E_eps1_del{k}_pp`, `_pm`, `_mp`, and `_mm` for
$\varepsilon+\delta_k$, $\varepsilon-\delta_k$, $-\varepsilon+\delta_k$,
and $-\varepsilon-\delta_k$, respectively. The suffix records the signs
of $\varepsilon$ and $\delta_k$ in that order. These generators are odd.

Oscillator labels are `a_1_p`, `a_1_m`, `b_k_p`, and `b_k_m`, for
$a_1^+$, $a_1^-$, $b_k^+$, and $b_k^-$. The fermions obey
$\{a_1^-,a_1^+\}=1$; the bosons obey $[b_i^-,b_j^+]=\delta_{ij}$.

### Basis lists

The following lists use the fixed order: Cartan generators; positive
even roots (`2δ_i`, then `δ_i+δ_j`, `δ_i-δ_j` for increasing `i,j`);
negative even roots in the corresponding order; then odd roots in the
suffix order `pp`, `pm`, `mp`, `mm` for increasing `k`.

**C(2), n=1**

- Even: `H_1`, `H_2`, `E_2del1_p`, `E_2del1_m`.
- Odd: `E_eps1_del1_pp`, `E_eps1_del1_pm`, `E_eps1_del1_mp`,
  `E_eps1_del1_mm`.

**C(3), n=2**

- Even: `H_1`, `H_2`, `H_3`, `E_2del1_p`, `E_2del2_p`,
  `E_del1_del2_pp`, `E_del1_del2_pm`, `E_2del1_m`, `E_2del2_m`,
  `E_del1_del2_mm`, `E_del1_del2_mp`.
- Odd: `E_eps1_del1_pp`, `E_eps1_del1_pm`, `E_eps1_del1_mp`,
  `E_eps1_del1_mm`, `E_eps1_del2_pp`, `E_eps1_del2_pm`,
  `E_eps1_del2_mp`, `E_eps1_del2_mm`.

**C(4), n=3**

- Even: `H_1`, `H_2`, `H_3`, `H_4`, `E_2del1_p`, `E_2del2_p`,
  `E_2del3_p`, `E_del1_del2_pp`, `E_del1_del2_pm`,
  `E_del1_del3_pp`, `E_del1_del3_pm`, `E_del2_del3_pp`,
  `E_del2_del3_pm`, `E_2del1_m`, `E_2del2_m`, `E_2del3_m`,
  `E_del1_del2_mm`, `E_del1_del2_mp`, `E_del1_del3_mm`,
  `E_del1_del3_mp`, `E_del2_del3_mm`, `E_del2_del3_mp`.
- Odd: for each `k=1,2,3` in order, `E_eps1_del{k}_pp`,
  `E_eps1_del{k}_pm`, `E_eps1_del{k}_mp`, `E_eps1_del{k}_mm`.

The list sizes are respectively $(4|4)$, $(11|8)$, and $(22|12)$,
matching even dimension $2n^2+n+1$ and odd dimension $4n$.

### PBW ordering

Two natural conventions are (1) all even generators before all odd
generators, following an even-first presentation, or (2) odd generators
before even generators, retaining the B(0,n) schema's explicit
parity-block convention. We choose
`[odd generators in the order above] < [even generators in the order above]`.
This preserves the existing schema's PBW parity-block convention while
the four odd-root labels make their root content explicit. The extension
symbol `κ`, when present in a deformation schema, precedes these blocks;
the scalar identity `K=1` is not an independent basis element.
