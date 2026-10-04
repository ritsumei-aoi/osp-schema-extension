# Notation and Terminology

This document defines the mathematical notation and terminology used in this repository.
It is initialized during the $C(n+1) = \mathfrak{osp}(2|2n)$ schema extension project.

## Conventions

### 1. Lie Superalgebra Family and Dimension
- **Algebra**: $C(n+1) = \mathfrak{osp}(2|2n)$, with $m = 1$ fermionic pair rank and $n$ bosonic rank.
  - $n = 1$: $C(2) = \mathfrak{osp}(2|2)$, dimension $4 \mid 4$ (total 8).
  - $n = 2$: $C(3) = \mathfrak{osp}(2|4)$, dimension $11 \mid 8$ (total 19).
  - $n = 3$: $C(4) = \mathfrak{osp}(2|6)$, dimension $22 \mid 12$ (total 34).
- **Dimension Formulas**:
  - Even dimension: $\dim(\mathfrak{g}_{\bar{0}}) = 2n^2 + n + 1$.
  - Odd dimension: $\dim(\mathfrak{g}_{\bar{1}}) = 4n$.
  - Total dimension: $\dim(\mathfrak{g}) = 2n^2 + 5n + 1$.

### 2. Oscillator Realization and Labels
- **Fermionic Oscillators** ($m=1$):
  - Creation: $a_1^+$ labeled as `a_1_p` (parity 1)
  - Annihilation: $a_1^-$ labeled as `a_1_m` (parity 1)
  - CAR: $\{a_1^-, a_1^+\} = 1$, $(a_1^+)^2 = (a_1^-)^2 = 0$.
- **Bosonic Oscillators** ($k = 1, \dots, n$):
  - Creation: $b_k^+$ labeled as `b_k_p` (parity 0)
  - Annihilation: $b_k^-$ labeled as `b_k_m` (parity 0)
  - CCR: $[b_j^-, b_k^+] = \delta_{jk}$, $[b_j^\pm, b_k^\pm] = 0$.
- **Central Elements**:
  - `kappa` ($\kappa$): Odd central element ($p(\kappa) = 1$, $\kappa^2 = 0$). Formal deformation parameter.
  - `K`: Even central element ($p(K) = 0$, $K = 1$). Central identity element.

### 3. Generator Labels
- **Cartan Generators**:
  - $H_1 = a_1^+ a_1^- + b_1^+ b_1^-$ (`H_1`)
  - $H_k = b_{k-1}^+ b_{k-1}^- - b_k^+ b_k^-$ for $k = 2, \dots, n$ (`H_k`)
  - $H_{n+1} = -b_n^+ b_n^- - \tfrac{1}{2}$ (`H_{n+1}`)
- **Long Bosonic Roots** ($\pm 2\delta_k$):
  - $E_{2\delta_k} = (b_k^+)^2 \longrightarrow$ `E_2del{k}_p`
  - $E_{-2\delta_k} = (b_k^-)^2 \longrightarrow$ `E_2del{k}_m`
- **Short Bosonic Roots** ($\pm\delta_i \pm \delta_j$ for $1 \le i < j \le n$):
  - $E_{\delta_i + \delta_j} = b_i^+ b_j^+ \longrightarrow$ `E_del{i}_del{j}_pp`
  - $E_{-(\delta_i + \delta_j)} = b_i^- b_j^- \longrightarrow$ `E_del{i}_del{j}_mm`
  - $E_{\delta_i - \delta_j} = b_i^+ b_j^- \longrightarrow$ `E_del{i}_del{j}_pm`
  - $E_{-(\delta_i - \delta_j)} = b_i^- b_j^+ \longrightarrow$ `E_del{i}_del{j}_mp`
- **Fermionic (Odd) Roots** ($\pm\varepsilon \pm \delta_k$ for $k = 1, \dots, n$):
  - $E_{\varepsilon + \delta_k} = a_1^+ b_k^+ \longrightarrow$ `E_eps1_del{k}_pp`
  - $E_{\varepsilon - \delta_k} = a_1^+ b_k^- \longrightarrow$ `E_eps1_del{k}_pm`
  - $E_{-\varepsilon + \delta_k} = a_1^- b_k^+ \longrightarrow$ `E_eps1_del{k}_mp`
  - $E_{-\varepsilon - \delta_k} = a_1^- b_k^- \longrightarrow$ `E_eps1_del{k}_mm`

### 4. PBW Ordering Convention
The PBW ordering follows the parity-separated block convention:
$$\kappa < [\text{odd generators}] < [\text{even generators}]$$
(Note: central element $K = 1$ is scalar and excluded from basis lists).

- **Odd Generators Ordering**:
  Ordered by index $k = 1, \dots, n$, with each block ordered as `pp`, `pm`, `mp`, `mm`:
  $$E_{\varepsilon+\delta_1}, E_{\varepsilon-\delta_1}, E_{-\varepsilon+\delta_1}, E_{-\varepsilon-\delta_1}, \dots, E_{\varepsilon+\delta_n}, E_{\varepsilon-\delta_n}, E_{-\varepsilon+\delta_n}, E_{-\varepsilon-\delta_n}.$$
- **Even Generators Ordering**:
  1. Cartan generators: $H_1, \dots, H_{n+1}$.
  2. Positive long roots: $E_{2\delta_1}, \dots, E_{2\delta_n}$ (`E_2del{k}_p`).
  3. Positive short roots: $E_{\delta_i + \delta_j}$ (`E_del{i}_del{j}_pp`, $1 \le i < j \le n$ lexicographic).
  4. Negative long roots: $E_{-2\delta_1}, \dots, E_{-2\delta_n}$ (`E_2del{k}_m`).
  5. Negative short roots: $E_{-(\delta_i + \delta_j)}$ (`E_del{i}_del{j}_mm`, $1 \le i < j \le n$ lexicographic).
  6. Mixed short roots: $E_{\delta_i - \delta_j}, E_{-(\delta_i - \delta_j)}$ (`E_del{i}_del{j}_pm`, `E_del{i}_del{j}_mp`, $1 \le i < j \le n$ lexicographic).

### 5. Explicit Basis Lists for $n=1, 2, 3$

#### $n = 1$ ($C(2) = \mathfrak{osp}(2|2)$)
- **Even** (4): `["H_1", "H_2", "E_2del1_p", "E_2del1_m"]`
- **Odd** (4): `["E_eps1_del1_pp", "E_eps1_del1_pm", "E_eps1_del1_mp", "E_eps1_del1_mm"]`

#### $n = 2$ ($C(3) = \mathfrak{osp}(2|4)$)
- **Even** (11):
  - Cartan (3): `["H_1", "H_2", "H_3"]`
  - Pos. long (2): `["E_2del1_p", "E_2del2_p"]`
  - Pos. short (1): `["E_del1_del2_pp"]`
  - Neg. long (2): `["E_2del1_m", "E_2del2_m"]`
  - Neg. short (1): `["E_del1_del2_mm"]`
  - Mixed short (2): `["E_del1_del2_pm", "E_del1_del2_mp"]`
- **Odd** (8):
  - $k=1$ (4): `["E_eps1_del1_pp", "E_eps1_del1_pm", "E_eps1_del1_mp", "E_eps1_del1_mm"]`
  - $k=2$ (4): `["E_eps1_del2_pp", "E_eps1_del2_pm", "E_eps1_del2_mp", "E_eps1_del2_mm"]`

#### $n = 3$ ($C(4) = \mathfrak{osp}(2|6)$)
- **Even** (22):
  - Cartan (4): `["H_1", "H_2", "H_3", "H_4"]`
  - Pos. long (3): `["E_2del1_p", "E_2del2_p", "E_2del3_p"]`
  - Pos. short (3): `["E_del1_del2_pp", "E_del1_del3_pp", "E_del2_del3_pp"]`
  - Neg. long (3): `["E_2del1_m", "E_2del2_m", "E_2del3_m"]`
  - Neg. short (3): `["E_del1_del2_mm", "E_del1_del3_mm", "E_del2_del3_mm"]`
  - Mixed short (6): `["E_del1_del2_pm", "E_del1_del2_mp", "E_del1_del3_pm", "E_del1_del3_mp", "E_del2_del3_pm", "E_del2_del3_mp"]`
- **Odd** (12):
  - $k=1$ (4): `["E_eps1_del1_pp", "E_eps1_del1_pm", "E_eps1_del1_mp", "E_eps1_del1_mm"]`
  - $k=2$ (4): `["E_eps1_del2_pp", "E_eps1_del2_pm", "E_eps1_del2_mp", "E_eps1_del2_mm"]`
  - $k=3$ (4): `["E_eps1_del3_pp", "E_eps1_del3_pm", "E_eps1_del3_mp", "E_eps1_del3_mm"]`
