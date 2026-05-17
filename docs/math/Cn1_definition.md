# Mathematical Definition of C(n+1) = osp(2|2n)

This document provides the self-contained mathematical definition of
$C(n+1) = \mathfrak{osp}(2|2n)$ and its differences from $B(0,n)$.

**Reference**: Frappat, Sciarrino, Sorba, *Dictionary on Lie Algebras and Superalgebras* (2000),
Chapter on $C(n+1)$; arXiv:hep-th/9607161.

---

## 1. Root System

The root system of $C(n+1) = \mathfrak{osp}(2|2n)$ is expressed in terms of
orthogonal vectors $\varepsilon$ (fermionic) and $\delta_1, \ldots, \delta_n$ (bosonic) as:

$$
\Delta = \left\{ \pm\delta_k \pm \delta_l,\ \pm 2\delta_k,\ \pm\varepsilon \pm \delta_k \right\}
\quad (1 \leq k < l \leq n).
$$

**Decomposition by parity**:
$$
\Delta_{\bar{0}} = \{\pm 2\delta_k\} \cup \{\pm(\delta_i \pm \delta_j) \mid i < j\},
$$
$$
\Delta_{\bar{1}} = \{\pm\varepsilon \pm \delta_k \mid k = 1, \ldots, n\}.
$$

The even subalgebra is $\mathfrak{so}(2) \times \mathfrak{sp}(2n)$ (not $\mathfrak{sp}(2n)$ alone),
with dimension $2n^2 + n + 1$.

**Superdimension**: $\dim(\mathfrak{g}) = (2n^2 + n + 1) \mid 4n$, total $= 2n^2 + 5n + 1$.

| $n$ | even | odd | total | Algebra |
|---|---|---|---|---|
| 1 | 4 | 4 | 8 | C(2) = osp(2\|2) |
| 2 | 11 | 8 | 19 | C(3) = osp(2\|4) |
| 3 | 22 | 12 | 34 | C(4) = osp(2\|6) |

---

## 2. Oscillator Realization

$C(n+1)$ is realized using:
- **Standard fermionic pair** $a_1^\pm$: CAR, $\{a_1^-, a_1^+\} = 1$, parity $p(a_1^\pm) = 1$.
- **Bosonic oscillators** $b_k^\pm$ ($k = 1, \ldots, n$): CCR, $[b_k^-, b_l^+] = \delta_{kl}$.

> **Key difference from B(0,n)**: C(n+1) uses a **standard fermionic pair** $(a_1^+, a_1^-)$
> satisfying canonical anticommutation relations, instead of B(0,n)'s
> **supplementary fermion** $a_0$ with $a_0^2 = \tfrac{1}{2}$.

### Simple generators ($2 \leq k \leq n$)

$$
\begin{aligned}
H_1 &= a_1^+ a_1^- + b_1^+ b_1^-, &
E_{\varepsilon - \delta_1} &= a_1^+ b_1^-, &
E_{\delta_1 - \varepsilon} &= b_1^+ a_1^-, \\
H_k &= b_{k-1}^+ b_{k-1}^- - b_k^+ b_k^-, &
E_{\delta_{k-1} - \delta_k} &= b_{k-1}^+ b_k^-, &
E_{\delta_k - \delta_{k-1}} &= b_k^+ b_{k-1}^-, \\
H_{n+1} &= -b_n^+ b_n^- - \tfrac{1}{2}, &
E_{2\delta_n} &= \tfrac{1}{2}(b_n^+)^2, &
E_{-2\delta_n} &= \tfrac{1}{2}(b_n^-)^2.
\end{aligned}
$$

### All root generators ($1 \leq k, l \leq n$)

$$
E_{\pm\delta_k \pm \delta_l} = b_k^\pm b_l^\pm, \quad
E_{\pm 2\delta_k} = (b_k^\pm)^2, \quad
E_{\varepsilon \pm \delta_l} = a_1^+ b_l^\pm, \quad
E_{-\varepsilon \pm \delta_l} = a_1^- b_l^\pm.
$$

> **Note on conventions**: The Frappat formula for $E_{\pm 2\delta_k}$ includes a
> factor of $\tfrac{1}{2}$. In the JSON schema implementation following Issue I01,
> this factor may be absorbed into the normalization. Confirm the convention used
> in `handover/notation.md` before generating structure constants.

### Generator label convention (JSON schema)

**Even generators**:

| Root | Generator label | Oscillator realization |
|---|---|---|
| $2\delta_k$ | `E_2del{k}_p` | $(b_k^+)^2$ |
| $-2\delta_k$ | `E_2del{k}_m` | $(b_k^-)^2$ |
| $\delta_i + \delta_j$ ($i<j$) | `E_del{i}_del{j}_pp` | $b_i^+ b_j^+$ |
| $-(\delta_i+\delta_j)$ ($i<j$) | `E_del{i}_del{j}_mm` | $b_i^- b_j^-$ |
| $\delta_i - \delta_j$ ($i<j$) | `E_del{i}_del{j}_pm` | $b_i^+ b_j^-$ |
| $-\delta_i + \delta_j$ ($i<j$) | `E_del{i}_del{j}_mp` | $b_i^- b_j^+$ |
| Cartan ($k = 1$) | `H_{1}` | $a_1^+ a_1^- + b_1^+ b_1^-$ |
| Cartan ($k = 2,\ldots,n$) | `H_{k}` | $b_{k-1}^+ b_{k-1}^- - b_k^+ b_k^-$ |
| Cartan ($k = n+1$) | `H_{n+1}` | $-b_n^+ b_n^- - \tfrac{1}{2}$ |

**Odd generators** ($k = 1, \ldots, n$):

| Root | Generator label | Oscillator realization |
|---|---|---|
| $\varepsilon + \delta_k$ | `E_eps1_del{k}_pp` | $a_1^+ b_k^+$ |
| $\varepsilon - \delta_k$ | `E_eps1_del{k}_pm` | $a_1^+ b_k^-$ |
| $-\varepsilon + \delta_k$ | `E_eps1_del{k}_mp` | $a_1^- b_k^+$ |
| $-\varepsilon - \delta_k$ | `E_eps1_del{k}_mm` | $a_1^- b_k^-$ |

---

## 3. Differences from B(0,n)

| Property | B(0,n) = osp(1\|2n) | C(n+1) = osp(2\|2n) |
|---|---|---|
| Fermionic oscillators | Supplementary fermion $a_0$, $a_0^2 = \tfrac{1}{2}$ | Standard pair $a_1^\pm$, $\{a_1^-, a_1^+\} = 1$ |
| Odd roots | $\pm\delta_k$ (2n total) | $\pm\varepsilon \pm \delta_k$ (4n total) |
| Even subalgebra | $\mathfrak{sp}(2n)$, dim $= 2n^2+n$ | $\mathfrak{so}(2) \times \mathfrak{sp}(2n)$, dim $= 2n^2+n+1$ |
| Odd generators | `E_del{k}_p`, `E_del{k}_m` | `E_eps1_del{k}_pp/pm/mp/mm` |
| Deformation | $a_0^2 \mapsto \tfrac{1}{2} + \kappa\sum \mathrm{gb}\cdot b_j^s$ | Analogous; to be determined in schema extension |
| JSON family | `"B"`, $m=0$ | `"C"`, $m=1$ |

---

## 4. PBW Ordering Convention (decided in Issue I01)

The basis ordering follows the Fermionic-first convention (Option A),
consistent with B(0,n) v5.0:

$$
\kappa < [\text{odd generators}] < [\text{even generators}].
$$

Within the odd block: $E_{\varepsilon+\delta_k}\ (k=1..n)$, then $E_{\varepsilon-\delta_k}$,
then $E_{-\varepsilon+\delta_k}$, then $E_{-\varepsilon-\delta_k}$.

Within the even block: Cartan generators $H_1, \ldots, H_{n+1}$, then positive roots, then negative roots.

> **Note on $K$**: The element $K$ (even central element, $K = 1$) appears in the
> framework of Bakalov--Sullivan (arXiv:1612.09400) as a formal central element
> identified with the scalar identity. Since $K = 1$ in all current applications,
> it does not appear as an independent basis element and is excluded from the
> PBW ordering and basis lists. It is recorded in `central_elements` of the JSON
> schema for completeness but does not contribute to structure constant computations.

See `handover/notation.md` for the definitive convention used in this project.
