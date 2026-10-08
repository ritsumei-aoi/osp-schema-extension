# Notation and Terminology

This document defines the mathematical notation and terminology used in this repository.
It is initialized during the $C(n+1)$ schema extension project.

## Conventions

### 1. Oscillator Generators
- **Fermions**: $a_1^+, a_1^-$ (code labels: `a1+`, `a1-`).
- **Bosons**: $b_k^+, b_k^-$ for $k=1, \dots, n$ (code labels: `bk+`, `bk-`).

### 2. Lie Superalgebra Generators
- **Cartan Subalgebra**: $H_k$ for $k=1, \dots, n+1$ (code labels: `H_k`).
- **Root Generators**: $E_{\alpha}$. Root labels use `eps` for $\varepsilon$ and `dk` for $\delta_k$.
  - Examples: `E_eps+d1`, `E_-eps-d1`, `E_2d1`, `E_-2d1`, `E_d1-d2`.

### 3. PBW Ordering
- We adopt **Standard Highest Weight Ordering**: $\mathfrak{n}^- < \mathfrak{h} < \mathfrak{n}^+$ (Negative Roots < Cartan < Positive Roots).
- Within each subspace, roots are ordered lexicographically assuming $\varepsilon > \delta_1 > \delta_2 > \dots > \delta_n > 0$.
