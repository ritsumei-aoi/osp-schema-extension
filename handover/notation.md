# Notation and Terminology

This document defines the mathematical notation and terminology used in this repository.

## Conventions for C(n+1) = osp(2|2n)

### 1. Basis Definition
Parity is decomposed as $\Delta = \Delta_{\bar{0}} \cup \Delta_{\bar{1}}$.

*   **Odd Basis $\mathcal{B}_{\bar{1}}$**: $\{E_{\varepsilon \pm \delta_k, \text{sign}_a, \text{sign}_b}\}$.
*   **Even Basis $\mathcal{B}_{\bar{0}}$**: $\{H_1, \ldots, H_{n+1}, E_{\pm 2\delta_k}, E_{\pm(\delta_i \pm \delta_j)}\}$.

### 2. PBW Ordering (Option A)
Order: `Odd Generators` < `Cartan Generators` < `Positive Even Generators` < `Negative Even Generators`.

### 3. Generator Labels (JSON Schema)
*   Even: `H_{k}`, `E_2del{k}_{p/m}`, `E_del{i}_del{j}_{pp/mm/pm/mp}`
*   Odd: `E_eps1_del{k}_{pp/pm/mp/mm}`
