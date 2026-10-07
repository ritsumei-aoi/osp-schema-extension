# Notation and Terminology

This document defines the mathematical notation and generator conventions used
for the $C(n+1)=\mathfrak{osp}(2|2n)$ schema extension.

## Root system and basis

Write the roots using the orthogonal vectors $\varepsilon$ and
$\delta_1,\ldots,\delta_n$. The simple roots are
\[
\alpha_1=\varepsilon-\delta_1,\qquad
\alpha_k=\delta_{k-1}-\delta_k\ (2\leq k\leq n),\qquad
\alpha_{n+1}=2\delta_n.
\]
The positive roots are
\[
\begin{aligned}
\Delta_{\bar 0}^+
 &= \{2\delta_i:1\leq i\leq n\}
    \cup\{\delta_i-\delta_j,\delta_i+\delta_j:1\leq i<j\leq n\},\\
\Delta_{\bar 1}^+
 &= \{\varepsilon-\delta_i,\varepsilon+\delta_i:1\leq i\leq n\}.
\end{aligned}
\]
Negative roots are the negatives of the corresponding positive roots. The
Cartan basis is $H_1,\ldots,H_{n+1}$; the even basis consists of this Cartan
basis and the root vectors for every even root, and the odd basis consists of
the root vectors for every odd root.

| Algebra | Even basis | Odd basis | Superdimension |
|---|---|---|---|
| $C(2)$, $n=1$ | $H_1,H_2;\ E_{\pm2\delta_1}$ | $E_{\varepsilon-\delta_1},E_{\varepsilon+\delta_1},E_{-\varepsilon+\delta_1},E_{-\varepsilon-\delta_1}$ | $4\mid4$ |
| $C(3)$, $n=2$ | $H_1,H_2,H_3;\ E_{\pm2\delta_i}\ (i=1,2);\ E_{\pm(\delta_1-\delta_2)},E_{\pm(\delta_1+\delta_2)}$ | $E_{\varepsilon\pm\delta_i},E_{-\varepsilon\pm\delta_i}\ (i=1,2)$ | $11\mid8$ |
| $C(4)$, $n=3$ | $H_1,\ldots,H_4;\ E_{\pm2\delta_i}\ (i=1,2,3);\ E_{\pm(\delta_i-\delta_j)},E_{\pm(\delta_i+\delta_j)}\ (1\leq i<j\leq3)$ | $E_{\varepsilon\pm\delta_i},E_{-\varepsilon\pm\delta_i}\ (i=1,2,3)$ | $22\mid12$ |

In general, $\dim\mathfrak g_{\bar0}=2n^2+n+1$ and
$\dim\mathfrak g_{\bar1}=4n$.

## Oscillators and generator labels

The oscillator generators are the standard fermionic pair $a_1^\pm$ and
bosonic pairs $b_i^\pm$ ($1\leq i\leq n$), with
\[
\{a_1^-,a_1^+\}=1,\qquad [b_i^-,b_j^+]=\delta_{ij}.
\]
The fermions anticommute with each other, bosons commute with each other, and
bosons commute with fermions. Suffixes `p` and `m` denote oscillator signs
$+$ and $-$, respectively.

Cartan labels are `H_1` through `H_{n+1}`. Their oscillator realizations are
\[
\begin{aligned}
H_1 &= a_1^+a_1^-+b_1^+b_1^-,\\
H_k &= b_{k-1}^+b_{k-1}^- - b_k^+b_k^- &&(2\leq k\leq n),\\
H_{n+1} &= -b_n^+b_n^- - \tfrac12.
\end{aligned}
\]

Even-root labels retain the B(0,n) convention. For $i<j$:

| Root | Label | Oscillator realization |
|---|---|---|
| $2\delta_i$, $-2\delta_i$ | `E_2del{i}_p`, `E_2del{i}_m` | $(b_i^+)^2$, $(b_i^-)^2$ |
| $\delta_i+\delta_j$, $-(\delta_i+\delta_j)$ | `E_del{i}_del{j}_pp`, `E_del{i}_del{j}_mm` | $b_i^+b_j^+$, $b_i^-b_j^-$ |
| $\delta_i-\delta_j$, $-(\delta_i-\delta_j)$ | `E_del{i}_del{j}_pm`, `E_del{i}_del{j}_mp` | $b_i^+b_j^-$, $b_i^-b_j^+$ |

Odd-root labels encode the fermion sign first and the boson sign second:

| Root | Label | Oscillator realization |
|---|---|---|
| $\varepsilon+\delta_i$ | `E_eps1_del{i}_pp` | $a_1^+b_i^+$ |
| $\varepsilon-\delta_i$ | `E_eps1_del{i}_pm` | $a_1^+b_i^-$ |
| $-\varepsilon+\delta_i$ | `E_eps1_del{i}_mp` | $a_1^-b_i^+$ |
| $-\varepsilon-\delta_i$ | `E_eps1_del{i}_mm` | $a_1^-b_i^-$ |

Thus the odd sector has four labels for each $i$. The even root labels and
pair indices use $1\leq i<j\leq n$.

## PBW ordering

Use the approved parity-block convention to preserve the existing B(0,n)
schema structure. Exclude the scalar identity $K=1$ from the basis and PBW
ordering.

1. **Odd block:** for $i=1,\ldots,n$, list `E_eps1_del{i}_pp`,
   `E_eps1_del{i}_pm`; then for $i=1,\ldots,n$, list
   `E_eps1_del{i}_mp`, `E_eps1_del{i}_mm`.
2. **Even block:** list `H_1,...,H_{n+1}`; then all positive even roots as
   `E_2del{i}_p`, `E_del{i}_del{j}_pp`, `E_del{i}_del{j}_pm`; then all
   negative even roots as `E_2del{i}_m`, `E_del{i}_del{j}_mm`,
   `E_del{i}_del{j}_mp`.

Within each indexed family, use increasing indices; for pair roots, iterate
lexicographically over $i<j$. The full convention is therefore
`[odd: epsilon-positive, epsilon-negative] < [even: Cartan, positive roots, negative roots]`.
