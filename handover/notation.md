# Notation and Terminology

This document defines the mathematical notation and terminology used in this repository.
It is initialized during the $C(n+1)$ schema extension project.

## Conventions

### Oscillator Generators

**Fermionic oscillators**:
- $a_1^+$, $a_1^-$: Standard fermionic pair for C(n+1), satisfying CAR $\{a_1^-, a_1^+\} = 1$
- Subscript convention: `a_1_p` (plus) and `a_1_m` (minus) in labels

**Bosonic oscillators**:
- $b_k^+$, $b_k^-$ ($k = 1, \ldots, n$): Standard bosonic pair, satisfying CCR $[b_j^-, b_k^+] = \delta_{jk}$
- Subscript convention: `b_k_p` (plus) and `b_k_m` (minus) in labels

**Notation symbols**:
- $\varepsilon$: Fermionic root element (weight of fermionic sector)
- $\delta_k$: Bosonic root element ($k = 1, \ldots, n$)

### Root System and Basis Labeling for C(n+1)

**Root elements**:
- Odd roots: $\pm\varepsilon \pm \delta_k$ for $k = 1, \ldots, n$
- Even roots: $\pm 2\delta_k$ and $\pm(\delta_i \pm \delta_j)$ for $1 \leq i < j \leq n$

**Generator labels** (PBW ordering: Fermionic-First):

*Even roots*:
- $2\delta_k$: `E_2del{k}_p` (positive), `E_2del{k}_m` (negative)
- $\delta_i + \delta_j$ ($i < j$): `E_del{i}_del{j}_pp`
- $\delta_i - \delta_j$ ($i < j$): `E_del{i}_del{j}_pm`
- $-(\delta_i - \delta_j)$ ($i < j$): `E_del{i}_del{j}_mp`
- $-(\delta_i + \delta_j)$ ($i < j$): `E_del{i}_del{j}_mm`

*Odd roots*:
- $\varepsilon + \delta_k$: `E_eps_del{k}_pp`
- $\varepsilon - \delta_k$: `E_eps_del{k}_pm`
- $-\varepsilon + \delta_k$: `E_eps_del{k}_mp`
- $-\varepsilon - \delta_k$: `E_eps_del{k}_mm`

**PBW Ordering Convention**:
Basis ordered as: (central elements) < Cartan < (positive odd) < (positive even) < (negative even) < (negative odd)

Within each root type:
1. Cartan: $H_1, H_2, \ldots, H_{n+1}$
2. Positive odd: $E_{\varepsilon+\delta_1}, \ldots, E_{\varepsilon+\delta_n}, E_{\varepsilon-\delta_1}, \ldots, E_{\varepsilon-\delta_n}$
3. Positive even: $E_{2\delta_1}, \ldots, E_{2\delta_n}, E_{\delta_i-\delta_j}, E_{\delta_i+\delta_j}$ (sorted by indices)
4. Negative roots: Reverse of positive roots

### Central Elements

- $K$: Even central element (parity 0), identified with scalar 1 in applications
- $\kappa$: Odd central element (parity 1), nilpotent with $\kappa^2 = 0$, used in deformation parametrization

### Deformation Parameters

**Inhomogeneous deformation (gb-parameters)**:
- $\mathrm{gb}_{\sigma, j, s}$ for $\sigma \in \{+, -\}$ and $s \in \{+, -\}$ denotes deformation parameter indexed by fermionic and bosonic oscillator labels
- Total count for C(n+1): $4n$ parameters (parity 1 each)
- Exchange relation: $[b_j^s, a_1^\sigma] = -\mathrm{gb}_{\sigma, j, s} \cdot \kappa$
