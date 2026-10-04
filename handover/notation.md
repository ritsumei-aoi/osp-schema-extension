# Notation and Terminology

This document defines the mathematical notation and terminology used in this repository.
It is initialized during the $C(n+1)$ schema extension project.

## Conventions

### 1. Basis Definitions for C(n+1)
For $C(n+1) = \mathfrak{osp}(2|2n)$, the generators are split into even and odd parts:
- **Cartan generators (even):** $H_1, \dots, H_{n+1}$
- **Even roots:** $E_{\pm 2\delta_k}$ ($1 \le k \le n$), $E_{\pm(\delta_i \pm \delta_j)}$ ($1 \le i < j \le n$)
- **Odd roots:** $E_{\pm \varepsilon \pm \delta_k}$ ($1 \le k \le n$)

### 2. PBW Ordering
We define the root ordering such that $\varepsilon > \delta_1 > \delta_2 > \dots > \delta_n > 0$.
The PBW ordering for generators follows the standard convention:
Negative Root Generators < Cartan Generators < Positive Root Generators.
Within roots, they are ordered lexicographically based on the root ordering above.

### 3. Generator Labels (JSON Schema)
The generator string labels follow this convention:
- Cartan: $H_k \rightarrow$ `H_{k}`
- Even roots:
  - $2\delta_k \rightarrow$ `E_2del{k}_p`
  - $-2\delta_k \rightarrow$ `E_2del{k}_m`
  - $\delta_i + \delta_j \rightarrow$ `E_del{i}_del{j}_pp`
  - $\delta_i - \delta_j \rightarrow$ `E_del{i}_del{j}_pm`
  - $-\delta_i + \delta_j \rightarrow$ `E_del{i}_del{j}_mp`
  - $-\delta_i - \delta_j \rightarrow$ `E_del{i}_del{j}_mm`
- Odd roots:
  - $\varepsilon + \delta_k \rightarrow$ `E_eps_del{k}_pp`
  - $\varepsilon - \delta_k \rightarrow$ `E_eps_del{k}_pm`
  - $-\varepsilon + \delta_k \rightarrow$ `E_eps_del{k}_mp`
  - $-\varepsilon - \delta_k \rightarrow$ `E_eps_del{k}_mm`
