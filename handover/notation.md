# Notation and Terminology

This document defines the mathematical notation and terminology used in this repository.
It is initialized during the $C(n+1)$ schema extension project.

## Conventions

### 1. Oscillator Generators
- Fermionic pair: `a_1_p` ($a_1^+$), `a_1_m` ($a_1^-$).
- Bosonic oscillators: `b_k_p` ($b_k^+$), `b_k_m` ($b_k^-$) for $k = 1, \dots, n$.

### 2. Algebra Generator Labels
- Cartan generators: `H_1`, `H_2`, ..., `H_{n+1}`.
- Even root generators:
  - `E_2del{k}_p` ($E_{2\delta_k}$)
  - `E_2del{k}_m` ($E_{-2\delta_k}$)
  - `E_del{i}_del{j}_pp` ($E_{\delta_i+\delta_j}$, $i < j$)
  - `E_del{i}_del{j}_pm` ($E_{\delta_i-\delta_j}$, $i < j$)
  - `E_del{i}_del{j}_mp` ($E_{-\delta_i+\delta_j}$, $i < j$)
  - `E_del{i}_del{j}_mm` ($E_{-\delta_i-\delta_j}$, $i < j$)
- Odd root generators:
  - `E_eps1_del{k}_pp` ($E_{\varepsilon+\delta_k}$)
  - `E_eps1_del{k}_pm` ($E_{\varepsilon-\delta_k}$)
  - `E_eps1_del{k}_mp` ($E_{-\varepsilon+\delta_k}$)
  - `E_eps1_del{k}_mm` ($E_{-\varepsilon-\delta_k}$)

### 3. PBW Ordering
The standard PBW ordering convention is `[odd] < [even]`. This mirrors the existing B(0,n) convention to ensure downstream compatibility. Within each block, generators are ordered lexicographically.
