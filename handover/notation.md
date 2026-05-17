# Notation and Terminology

This document defines the mathematical notation and terminology used in this repository.
It is initialized during the $C(n+1)$ schema extension project.

## Conventions

### 1. C(n+1) Basis Lists

**For n=1 (C(2)):**
*   **Even Basis:** $H_1, H_2, 2\delta_1, -2\delta_1$
*   **Odd Basis:** $\varepsilon + \delta_1, \varepsilon - \delta_1, -\varepsilon + \delta_1, -\varepsilon - \delta_1$

**For n=2 (C(3)):**
*   **Even Basis:** $H_1, H_2, H_3$, $2\delta_1, 2\delta_2, \delta_1+\delta_2, \delta_1-\delta_2$, $-2\delta_1, -2\delta_2, -(\delta_1+\delta_2), -(\delta_1-\delta_2)$
*   **Odd Basis:** $\pm\varepsilon \pm \delta_1, \pm\varepsilon \pm \delta_2$

**For n=3 (C(4)):**
*   **Even Basis:** $H_1, H_2, H_3, H_4$, $2\delta_1, 2\delta_2, 2\delta_3, \delta_1+\delta_2, \delta_1-\delta_2, \delta_1+\delta_3, \delta_1-\delta_3, \delta_2+\delta_3, \delta_2-\delta_3$, plus their negatives.
*   **Odd Basis:** $\pm\varepsilon \pm \delta_1, \pm\varepsilon \pm \delta_2, \pm\varepsilon \pm \delta_3$

### 2. PBW Ordering (C(n+1))

Following the Fermionic-first convention ($[\text{odd generators}] < [\text{even generators}]$), the odd generators are **Sign-block grouped** (Option A):
1.  $E_{\varepsilon+\delta_k}$ for $k=1..n$
2.  $E_{\varepsilon-\delta_k}$ for $k=1..n$
3.  $E_{-\varepsilon+\delta_k}$ for $k=1..n$
4.  $E_{-\varepsilon-\delta_k}$ for $k=1..n$

The even generators follow as: Cartan ($H_1 \dots H_{n+1}$) < Positive roots < Negative roots.

### 3. Generator Labels

*   **Cartan:** `H_{k}`
*   **Even Positive/Negative Roots:** 
    *   $\pm 2\delta_k \rightarrow$ `E_2del{k}_p` / `E_2del{k}_m`
    *   $\delta_i \pm \delta_j \rightarrow$ `E_del{i}_del{j}_pp` / `E_del{i}_del{j}_pm`
    *   $-\delta_i \pm \delta_j \rightarrow$ `E_del{i}_del{j}_mp` / `E_del{i}_del{j}_mm`
*   **Odd Roots:**
    *   $\varepsilon + \delta_k \rightarrow$ `E_eps1_del{k}_pp`
    *   $\varepsilon - \delta_k \rightarrow$ `E_eps1_del{k}_pm`
    *   $-\varepsilon + \delta_k \rightarrow$ `E_eps1_del{k}_mp`
    *   $-\varepsilon - \delta_k \rightarrow$ `E_eps1_del{k}_mm`
