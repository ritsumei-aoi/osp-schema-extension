# Notation and Terminology

This document defines the mathematical notation and terminology used in this
repository for the $C(n+1)=\mathfrak{osp}(2|2n)$ extension.

## Root and basis conventions

Use $\varepsilon$ for the $\mathfrak{so}(2)$ direction and
$\delta_1,\ldots,\delta_n$ for the $\mathfrak{sp}(2n)$ directions. The complete
root sets are

$$
\Delta_{\bar 0}=\{\pm 2\delta_i\mid 1\leq i\leq n\}
\cup\{\pm\delta_i\pm\delta_j\mid 1\leq i<j\leq n\},
\qquad
\Delta_{\bar 1}=\{\pm\varepsilon\pm\delta_i\mid 1\leq i\leq n\}.
$$

The Cartan basis is $H_\varepsilon,H_{\delta_1},\ldots,H_{\delta_n}$.
For the following finite cases, list only positive roots in the table; every
negative root is also included in the corresponding basis.

| Algebra | Positive even roots | Positive odd roots |
|---|---|---|
| $C(2)$ ($n=1$) | $2\delta_1$ | $\varepsilon-\delta_1,\ \varepsilon+\delta_1$ |
| $C(3)$ ($n=2$) | $2\delta_1,\ 2\delta_2,\ \delta_1-\delta_2,\ \delta_1+\delta_2$ | $\varepsilon-\delta_1,\ \varepsilon+\delta_1,\ \varepsilon-\delta_2,\ \varepsilon+\delta_2$ |
| $C(4)$ ($n=3$) | $2\delta_1,\ 2\delta_2,\ 2\delta_3,\ \delta_1-\delta_2,\ \delta_1+\delta_2,\ \delta_1-\delta_3,\ \delta_1+\delta_3,\ \delta_2-\delta_3,\ \delta_2+\delta_3$ | $\varepsilon-\delta_1,\ \varepsilon+\delta_1,\ \varepsilon-\delta_2,\ \varepsilon+\delta_2,\ \varepsilon-\delta_3,\ \varepsilon+\delta_3$ |

Thus each basis consists of the Cartan basis and root vectors for the listed
positive roots and their negatives. The dimensions (even, odd) are respectively
$4|4$, $11|8$, and $22|12$.

## Positive roots and PBW order

Take the simple roots to be
$$
\alpha_1=\varepsilon-\delta_1,\quad
\alpha_k=\delta_{k-1}-\delta_k\ (2\leq k\leq n),\quad
\alpha_{n+1}=2\delta_n.
$$
The positive even roots are $2\delta_i$ and
$\delta_i\pm\delta_j$ for $i<j$; the positive odd roots are
$\varepsilon-\delta_i$ and $\varepsilon+\delta_i$ for $1\leq i\leq n$.

Two admissible total-order choices for the positive odd roots are:

1. Group by sign of $\varepsilon$: $\varepsilon-\delta_1,\ldots,
   \varepsilon-\delta_n,\varepsilon+\delta_1,\ldots,\varepsilon+\delta_n$.
2. Group by index: $\varepsilon-\delta_1,\varepsilon+\delta_1,\ldots,
   \varepsilon-\delta_n,\varepsilon+\delta_n$.

Use option 1. It keeps the two families $\varepsilon-\delta_i$ and
$\varepsilon+\delta_i$ contiguous and consistent across $n$, which makes
root-family-based schema generation straightforward.

The selected total PBW order is: negative even roots in the reverse of the
following positive-even order, then negative odd roots in the reverse of the
positive-odd order, then $H_\varepsilon,H_{\delta_1},\ldots,H_{\delta_n}$,
then positive even roots in this order, then positive odd roots in this order:

* Positive even: $2\delta_i$ by increasing $i$; then $\delta_i+\delta_j$ by
  lexicographic $(i,j)$; then $\delta_i-\delta_j$ by lexicographic $(i,j)$,
  always with $i<j$.
* Positive odd: first $\varepsilon-\delta_i$ by increasing $i$, then
  $\varepsilon+\delta_i$ by increasing $i$.

An ordered PBW monomial multiplies generators from left to right in this order.
The order is a fixed total order on a homogeneous basis; it does not change the
root-space decomposition.

## Oscillator generators and labels

Use bosonic pairs $b_i^+,b_i^-$ for $1\leq i\leq n$ and one standard
fermionic pair $a_1^+,a_1^-$. Their parities are
$p(b_i^\pm)=0$ and $p(a_1^\pm)=1$. The labels `p` and `m` denote plus and
minus oscillator signs, respectively.

Use the following label patterns:

| Root | Generator label |
|---|---|
| $2\delta_i$ / $-2\delta_i$ | `E_2del{i}_p` / `E_2del{i}_m` |
| $\delta_i+\delta_j$ / $-(\delta_i+\delta_j)$, $i<j$ | `E_del{i}_del{j}_pp` / `E_del{i}_del{j}_mm` |
| $\delta_i-\delta_j$ / $-(\delta_i-\delta_j)$, $i<j$ | `E_del{i}_del{j}_pm` / `E_del{i}_del{j}_mp` |
| $\varepsilon+\delta_i,\ \varepsilon-\delta_i,\ -\varepsilon+\delta_i,\ -\varepsilon-\delta_i$ | `E_eps_del{i}_pp`, `E_eps_del{i}_pm`, `E_eps_del{i}_mp`, `E_eps_del{i}_mm` |

The two-letter suffix records the signs of the first and second root
coordinates, respectively. Thus, for odd roots, the first letter is the sign
of $\varepsilon$ and the second is the sign of $\delta_i$. Oscillator
realizations use $b_i^\pm b_j^\pm$ for even roots and
$a_1^\pm b_i^\pm$ for odd roots, with signs matching the root coordinates.
