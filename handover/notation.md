# Notation and Terminology

This document defines the mathematical notation and terminology used in this repository.
It is initialized during the $C(n+1)$ schema extension project (Issue I01-1).

## 1. Lie Superalgebra $C(n+1) = \mathfrak{osp}(2|2n)$

### 1.1 Oscillators and Realization
$C(n+1)$ is realized using:
- **Standard fermionic oscillator pair**: $a_1^+, a_1^-$ with CAR relations:
  $$ \{a_1^-, a_1^+\} = 1, \quad \{a_1^\pm, a_1^\pm\} = 0, \quad p(a_1^\pm) = 1 $$
- **Bosonic oscillators**: $b_k^+, b_k^-$ ($k = 1, \ldots, n$) with CCR relations:
  $$ [b_j^-, b_k^+] = \delta_{jk}, \quad [b_j^\pm, b_k^\pm] = 0, \quad p(b_k^\pm) = 0 $$
- **Cross relations**: All mixed commutators vanish:
  $$ [b_k^\pm, a_1^\sigma] = 0 \quad (\sigma \in \{+,-\}) $$

### 1.2 Root System and Superdimension
The roots are expressed in terms of fermionic vector $\varepsilon$ and bosonic orthogonal vectors $\delta_1, \ldots, \delta_n$:
$$ \Delta = \{\pm 2\delta_k\} \cup \{\pm(\delta_i \pm \delta_j) \mid 1 \le i < j \le n\} \cup \{\pm\varepsilon \pm \delta_k \mid 1 \le k \le n\} $$
- **Even roots** $\Delta_{\bar{0}}$: $\pm 2\delta_k$, $\pm(\delta_i \pm \delta_j)$ ($2n^2$ roots)
- **Odd roots** $\Delta_{\bar{1}}$: $\pm\varepsilon \pm \delta_k$ ($4n$ roots)
- **Cartan subalgebra**: dimension $n+1$, spanned by $H_1, \ldots, H_{n+1}$
- **Even subalgebra**: $\mathfrak{so}(2) \oplus \mathfrak{sp}(2n)$, dimension $2n^2 + n + 1$
- **Odd subspace**: dimension $4n$
- **Total dimension**: $2n^2 + 5n + 1$

| $n$ | Algebra | Even dim | Odd dim | Total dim |
|---|---|---|---|---|
| 1 | $C(2) = \mathfrak{osp}(2\|2)$ | 4 | 4 | 8 |
| 2 | $C(3) = \mathfrak{osp}(2\|4)$ | 11 | 8 | 19 |
| 3 | $C(4) = \mathfrak{osp}(2\|6)$ | 22 | 12 | 34 |

### 1.3 Cartan Generators and Oscillator Realizations
- Simple/Cartan generators:
  $$
  \begin{aligned}
  H_1 &= a_1^+ a_1^- + b_1^+ b_1^- \\
  H_k &= b_{k-1}^+ b_{k-1}^- - b_k^+ b_k^- \quad (2 \le k \le n) \\
  H_{n+1} &= -b_n^+ b_n^- - \tfrac{1}{2}
  \end{aligned}
  $$

---

## 2. Generator Label Conventions

The generator labels follow the schema conventions:

| Root | Parity | Generator Label | Oscillator Realization | Count |
|---|---|---|---|---|
| Cartan | 0 (even) | `H_1`, ..., `H_{n+1}` | See above | $n+1$ |
| $2\delta_k$ ($1 \le k \le n$) | 0 (even) | `E_2del{k}_p` | $(b_k^+)^2$ | $n$ |
| $-2\delta_k$ ($1 \le k \le n$) | 0 (even) | `E_2del{k}_m` | $(b_k^-)^2$ | $n$ |
| $\delta_i + \delta_j$ ($1 \le i < j \le n$) | 0 (even) | `E_del{i}_del{j}_pp` | $b_i^+ b_j^+$ | $\binom{n}{2}$ |
| $-(\delta_i + \delta_j)$ ($1 \le i < j \le n$) | 0 (even) | `E_del{i}_del{j}_mm` | $b_i^- b_j^-$ | $\binom{n}{2}$ |
| $\delta_i - \delta_j$ ($1 \le i < j \le n$) | 0 (even) | `E_del{i}_del{j}_pm` | $b_i^+ b_j^-$ | $\binom{n}{2}$ |
| $-(\delta_i - \delta_j) = \delta_j - \delta_i$ ($1 \le i < j \le n$) | 0 (even) | `E_del{i}_del{j}_mp` | $b_i^- b_j^+$ | $\binom{n}{2}$ |
| $\varepsilon + \delta_k$ ($1 \le k \le n$) | 1 (odd) | `E_eps_del{k}_pp` | $a_1^+ b_k^+$ | $n$ |
| $\varepsilon - \delta_k$ ($1 \le k \le n$) | 1 (odd) | `E_eps_del{k}_pm` | $a_1^+ b_k^-$ | $n$ |
| $-\varepsilon + \delta_k$ ($1 \le k \le n$) | 1 (odd) | `E_eps_del{k}_mp` | $a_1^- b_k^+$ | $n$ |
| $-\varepsilon - \delta_k$ ($1 \le k \le n$) | 1 (odd) | `E_eps_del{k}_mm` | $a_1^- b_k^-$ | $n$ |

---

## 3. PBW Ordering Convention (Option A: Parity-first Graded Ordering)

The PBW ordering for $C(n+1)$ maintains parity stratification ($\kappa < \text{odd} < \text{even}$), extending the convention from $B(0,n)$:

$$ \kappa < [\text{odd roots grouped by sign of } \varepsilon] < [\text{even Cartan } H_k] < [\text{even root vectors}] $$

1. **Central element**: $\kappa$ (central odd element, $p(\kappa)=1$)
2. **Odd generators** ($\Delta_{\bar{1}}$):
   - $\varepsilon > 0$:
     - `E_eps_del1_pp`, ..., `E_eps_del{n}_pp`
     - `E_eps_del1_pm`, ..., `E_eps_del{n}_pm`
   - $\varepsilon < 0$:
     - `E_eps_del1_mp`, ..., `E_eps_del{n}_mp`
     - `E_eps_del1_mm`, ..., `E_eps_del{n}_mm`
3. **Even generators** ($\Delta_{\bar{0}}$):
   - Cartan: `H_1`, ..., `H_{n+1}`
   - Positive/creation roots: `E_2del{k}_p` ($k=1..n$), `E_del{i}_del{j}_pp` ($1 \le i < j \le n$)
   - Negative/annihilation roots: `E_2del{k}_m` ($k=1..n$), `E_del{i}_del{j}_mm` ($1 \le i < j \le n$)
   - Mixed roots: `E_del{i}_del{j}_pm` ($1 \le i < j \le n$), `E_del{i}_del{j}_mp` ($1 \le i < j \le n$)

---

## 4. Explicit Basis Lists for $n=1, 2, 3$

### 4.1 $n=1: C(2) = \mathfrak{osp}(2|2)$ (Dimension: 4 even, 4 odd, total 8)
- **Even basis**:
  ```json
  ["H_1", "H_2", "E_2del1_p", "E_2del1_m"]
  ```
- **Odd basis**:
  ```json
  ["E_eps_del1_pp", "E_eps_del1_pm", "E_eps_del1_mp", "E_eps_del1_mm"]
  ```

### 4.2 $n=2: C(3) = \mathfrak{osp}(2|4)$ (Dimension: 11 even, 8 odd, total 19)
- **Even basis**:
  ```json
  [
    "H_1", "H_2", "H_3",
    "E_2del1_p", "E_2del2_p",
    "E_del1_del2_pp",
    "E_2del1_m", "E_2del2_m",
    "E_del1_del2_mm",
    "E_del1_del2_pm", "E_del1_del2_mp"
  ]
  ```
- **Odd basis**:
  ```json
  [
    "E_eps_del1_pp", "E_eps_del2_pp",
    "E_eps_del1_pm", "E_eps_del2_pm",
    "E_eps_del1_mp", "E_eps_del2_mp",
    "E_eps_del1_mm", "E_eps_del2_mm"
  ]
  ```

### 4.3 $n=3: C(4) = \mathfrak{osp}(2|6)$ (Dimension: 22 even, 12 odd, total 34)
- **Even basis**:
  ```json
  [
    "H_1", "H_2", "H_3", "H_4",
    "E_2del1_p", "E_2del2_p", "E_2del3_p",
    "E_del1_del2_pp", "E_del1_del3_pp", "E_del2_del3_pp",
    "E_2del1_m", "E_2del2_m", "E_2del3_m",
    "E_del1_del2_mm", "E_del1_del3_mm", "E_del2_del3_mm",
    "E_del1_del2_pm", "E_del1_del3_pm", "E_del2_del3_pm",
    "E_del1_del2_mp", "E_del1_del3_mp", "E_del2_del3_mp"
  ]
  ```
- **Odd basis**:
  ```json
  [
    "E_eps_del1_pp", "E_eps_del2_pp", "E_eps_del3_pp",
    "E_eps_del1_pm", "E_eps_del2_pm", "E_eps_del3_pm",
    "E_eps_del1_mp", "E_eps_del2_mp", "E_eps_del3_mp",
    "E_eps_del1_mm", "E_eps_del2_mm", "E_eps_del3_mm"
  ]
  ```
