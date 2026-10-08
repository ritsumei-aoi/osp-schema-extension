# Mathematical Definition of B(0,n) = osp(1|2n)

This document provides the self-contained mathematical definition of
$B(0,n) = \mathfrak{osp}(1|2n)$ that serves as the base case for the
C(n+1) schema extension study.

**Reference**: Frappat, Sciarrino, Sorba, *Dictionary on Lie Algebras and Superalgebras* (2000);
Bakalov and Sullivan (2017); Aoi (2026), `docs/drafts/aoi2026_triviality_osp1_2n.tex`.

---

## 1. Root System

The root system of $B(0,n) = \mathfrak{osp}(1|2n)$ is expressed in terms of
orthogonal vectors $\delta_1, \ldots, \delta_n$ as follows:

$$
\Delta = \left\{ \pm \delta_k \pm \delta_l,\ \pm 2\delta_k,\ \pm \delta_k \right\}
\quad (1 \leq k < l \leq n).
$$

**Decomposition by parity**:
$$
\Delta_{\bar{0}}^+ = \{2\delta_i \mid 1 \leq i \leq n\} \cup \{\delta_i \pm \delta_j \mid 1 \leq i < j \leq n\},
\qquad |\Delta_{\bar{0}}^+| = n^2,
$$
$$
\Delta_{\bar{1}}^+ = \{\delta_i \mid 1 \leq i \leq n\},
\qquad |\Delta_{\bar{1}}^+| = n.
$$

The simple root system is
$$
\Pi = \{\alpha_k = \delta_k - \delta_{k+1} \mid k = 1, \ldots, n-1\} \cup \{\alpha_n = \delta_n\}.
$$

**Superdimension**: $\dim(\mathfrak{g}) = (2n^2 + n) \mid 2n$, total dimension $2n^2 + 3n$.

---

## 2. Oscillator Realization

$B(0,n)$ is realized using:
- **Bosonic oscillators** $b_j^\pm$ ($j = 1, \ldots, n$): CCR, $[b_j^-, b_k^+] = \delta_{jk}$.
- **Supplementary fermion** $a_0$: parity $p(a_0) = 1$, satisfying $a_0^2 = \tfrac{1}{2}$.

### Simple generators ($1 \leq k \leq n-1$)

$$
\begin{aligned}
H_k &= b_k^+ b_k^- - b_{k+1}^+ b_{k+1}^-, &
E_{\delta_k - \delta_{k+1}} &= b_k^+ b_{k+1}^-, &
E_{\delta_{k+1} - \delta_k} &= b_{k+1}^+ b_k^-, \\
H_n &= b_n^+ b_n^- + \tfrac{1}{2}, &
E_{\delta_n} &= \tfrac{1}{\sqrt{2}}\, b_n^+, &
E_{-\delta_n} &= \tfrac{1}{\sqrt{2}}\, b_n^-.
\end{aligned}
$$

> **Note**: In the oscillator algebra framework used in this project
> (following Bakalov–Sullivan), $a_0$ replaces the $\tfrac{1}{\sqrt{2}}$ factors
> and changes $H_n$ to $b_n^+ b_n^- + a_0^2$ with $a_0^2 = \tfrac{1}{2}$.
> The generator labels in the JSON schema use the $a_0$ convention.

### All root generators ($1 \leq k, l \leq n$)

$$
E_{\pm\delta_k \pm \delta_l} = b_k^\pm b_l^\pm, \quad
E_{\pm 2\delta_k} = (b_k^\pm)^2, \quad
E_{\pm\delta_k} = \frac{1}{\sqrt{2}}\, b_k^\pm.
$$

In the $a_0$ convention:
$$
E_{\delta_k} = a_0 b_k^+, \quad E_{-\delta_k} = a_0 b_k^-.
$$

### Generator label convention (JSON schema)

| Root | Generator label | Oscillator realization |
|---|---|---|
| $2\delta_k$ | `E_2del{k}_p` | $(b_k^+)^2$ |
| $-2\delta_k$ | `E_2del{k}_m` | $(b_k^-)^2$ |
| $\delta_i + \delta_j$ ($i<j$) | `E_del{i}_del{j}_pp` | $b_i^+ b_j^+$ |
| $\delta_i - \delta_j$ ($i<j$) | `E_del{i}_del{j}_pm` | $b_i^+ b_j^-$ |
| $-(\delta_i - \delta_j)$ ($i<j$) | `E_del{i}_del{j}_mp` | $b_i^- b_j^+$ |
| $-(\delta_i + \delta_j)$ ($i<j$) | `E_del{i}_del{j}_mm` | $b_i^- b_j^-$ |
| $\delta_k$ | `E_del{k}_p` | $a_0 b_k^+$ |
| $-\delta_k$ | `E_del{k}_m` | $a_0 b_k^-$ |

---

## 3. Central Extension and the Element κ

The oscillator Lie superalgebra $\mathfrak{g} = B(0,n)$ is extended by a
central element $\kappa$ to form:

$$
\tilde{\mathfrak{g}} = \mathfrak{g} \oplus \mathbb{R}\kappa,
$$

where $\kappa$ satisfies:
- **Parity**: $p(\kappa) = 1$ (odd element),
- **Nilpotency**: $\kappa^2 = 0$.

The extended bracket is defined via a 2-cocycle $\gamma: \mathfrak{g} \otimes \mathfrak{g} \to \mathfrak{g}$ as:

$$
[X, Y]_\gamma = [X, Y]_0 + \kappa \cdot \gamma(X, Y).
$$

Since $\kappa$ is odd and $\kappa^2 = 0$, the bracket preserves total parity.
In the oscillator realization, the deformation is parametrized by modifying $a_0^2$:

$$
a_0^2 \longmapsto \frac{1}{2} + \kappa \sum_{j=1}^{n} \sum_{s \in \{+,-\}}
\mathrm{gb}_{a_0, b_j^s} \cdot b_j^s,
$$

where $\mathrm{gb}_{a_0, b_j^\pm}$ are the **deformation parameters** ($2n$ in total, parity 1).

> **In the JSON schema**, the element $\kappa$ is listed as a central element
> with parity 0 in the `central_elements` key. It serves as the formal symbol
> of the nilpotent extension and appears in the schema to make the algebraic
> setting explicit. The symbol $K$ is the central identity element.

---

## 4. Dimension Summary

| $n$ | even ($\mathfrak{g}_{\bar{0}}$) | odd ($\mathfrak{g}_{\bar{1}}$) | total |
|---|---|---|---|
| 1 | 3 | 2 | 5 |
| 2 | 10 | 4 | 14 |
| 3 | 21 | 6 | 27 |

Formula: even $= 2n^2 + n$, odd $= 2n$, total $= 2n^2 + 3n$.
