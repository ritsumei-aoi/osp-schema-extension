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

---

## 3. Differences from B(0,n)

| Property | B(0,n) = osp(1\|2n) | C(n+1) = osp(2\|2n) |
|---|---|---|
| Fermionic oscillators | Supplementary fermion $a_0$, $a_0^2 = \tfrac{1}{2}$ | Standard pair $a_1^\pm$, $\{a_1^-, a_1^+\} = 1$ |
| Odd roots | $\pm\delta_k$ (2n total) | $\pm\varepsilon \pm \delta_k$ (4n total) |
| Even subalgebra | $\mathfrak{sp}(2n)$, dim $= 2n^2+n$ | $\mathfrak{so}(2) \times \mathfrak{sp}(2n)$, dim $= 2n^2+n+1$ |
