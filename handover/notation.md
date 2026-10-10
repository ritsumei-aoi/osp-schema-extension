# Notation and Terminology

This document defines the notation and terminology used for the
$C(n+1)=\mathfrak{osp}(2|2n)$ schema extension.

## Oscillator labels and relations

- Fermions: `a_1_p` and `a_1_m`, denoting $a_1^+$ and $a_1^-$, with
  parity 1 and CAR $\{a_1^-,a_1^+\}=1$.
- Bosons: `b_k_p` and `b_k_m`, denoting $b_k^+$ and $b_k^-$ for
  $1\leq k\leq n$, with parity 0 and CCR $[b_k^-,b_l^+]=\delta_{kl}$.
- Bosonic and fermionic oscillators commute in the undeformed algebra.

In formulas below, `_p` and `_m` mean plus and minus, respectively.

## Basis and dimensions

The even basis consists of the Cartan generators $H_1,\ldots,H_{n+1}$ and
one generator for each even root $\pm2\delta_k$ and
$\pm(\delta_i\pm\delta_j)$ with $i<j$. The odd basis consists of one
generator for each odd root $\pm\varepsilon\pm\delta_k$.

| Algebra | Even basis | Odd basis | Total |
|---|---:|---:|---:|
| C(2), $n=1$ | 4 | 4 | 8 |
| C(3), $n=2$ | 11 | 8 | 19 |
| C(4), $n=3$ | 22 | 12 | 34 |

Explicit basis lists:

- **C(2)** — even: `H_1`, `H_2`, `E_2del1_p`, `E_2del1_m`.
  Odd: `E_eps1_del1_pp`, `E_eps1_del1_pm`, `E_eps1_del1_mp`,
  `E_eps1_del1_mm`.
- **C(3)** — even: `H_1`, `H_2`, `H_3`; `E_2del1_p`,
  `E_2del2_p`; `E_del1_del2_pp`, `E_del1_del2_pm`;
  `E_2del1_m`, `E_2del2_m`; `E_del1_del2_mp`,
  `E_del1_del2_mm`. Odd: for each `k=1,2`, `E_eps1_del{k}_pp`,
  `E_eps1_del{k}_pm`, `E_eps1_del{k}_mp`, `E_eps1_del{k}_mm`.
- **C(4)** — even: `H_1`, `H_2`, `H_3`, `H_4`; `E_2del{k}_p`
  for `k=1,2,3`; for each pair `(i,j)=(1,2),(1,3),(2,3)`,
  `E_del{i}_del{j}_pp` and `E_del{i}_del{j}_pm`; `E_2del{k}_m`
  for `k=1,2,3`; and for each such pair, `E_del{i}_del{j}_mm`
  and `E_del{i}_del{j}_mp`. Odd: for each `k=1,2,3`,
  `E_eps1_del{k}_pp`, `E_eps1_del{k}_pm`, `E_eps1_del{k}_mp`,
  `E_eps1_del{k}_mm`.

The dimension formulas are $\dim\mathfrak{g}_{\bar 0}=2n^2+n+1$ and
$\dim\mathfrak{g}_{\bar 1}=4n$.

## Generator labels and realizations

The digits after `del` index $\delta_k$; `eps1` denotes $\varepsilon$.
For an odd label, the first suffix sign is the $\varepsilon$ sign and the
second is the $\delta_k$ sign. Even and odd root generators are realized as:

| Label | Root | Oscillator realization | Parity |
|---|---|---|---:|
| `E_2del{k}_p` | $2\delta_k$ | $(b_k^+)^2$ | 0 |
| `E_2del{k}_m` | $-2\delta_k$ | $(b_k^-)^2$ | 0 |
| `E_del{i}_del{j}_pp` | $\delta_i+\delta_j$ | $b_i^+b_j^+$ | 0 |
| `E_del{i}_del{j}_pm` | $\delta_i-\delta_j$ | $b_i^+b_j^-$ | 0 |
| `E_del{i}_del{j}_mp` | $-\delta_i+\delta_j$ | $b_i^-b_j^+$ | 0 |
| `E_del{i}_del{j}_mm` | $-\delta_i-\delta_j$ | $b_i^-b_j^-$ | 0 |
| `E_eps1_del{k}_pp` | $\varepsilon+\delta_k$ | $a_1^+b_k^+$ | 1 |
| `E_eps1_del{k}_pm` | $\varepsilon-\delta_k$ | $a_1^+b_k^-$ | 1 |
| `E_eps1_del{k}_mp` | $-\varepsilon+\delta_k$ | $a_1^-b_k^+$ | 1 |
| `E_eps1_del{k}_mm` | $-\varepsilon-\delta_k$ | $a_1^-b_k^-$ | 1 |

The Cartan generators follow the supplied oscillator convention:

$$
\begin{aligned}
H_1 &= a_1^+a_1^-+b_1^+b_1^-,\\
H_k &= b_{k-1}^+b_{k-1}^- - b_k^+b_k^- \quad (2\leq k\leq n),\\
H_{n+1} &= -b_n^+b_n^- - \tfrac12.
\end{aligned}
$$

For the full root-generator labels, $E_{\pm2\delta_k}=(b_k^\pm)^2$ is the
adopted normalization. The separate simple-generator formula in
`docs/math/Cn1_definition.md` writes a factor of $\tfrac12$ for the terminal
simple root; schema labels here use the full-root normalization above.

## PBW ordering (approved Option A)

Use the parity-block convention compatible with B(0,n):

`κ < [all odd generators] < [all even generators]`

Within the odd block, order `k` ascending and, for each `k`, suffixes
`pp`, `pm`, `mp`, `mm`. Within the even block, order:

1. `H_1`, ..., `H_{n+1}`.
2. `E_2del{k}_p` in ascending `k`.
3. `E_del{i}_del{j}_pp` in lexicographic `(i,j)` order, `i<j`.
4. `E_del{i}_del{j}_pm` in lexicographic `(i,j)` order.
5. `E_2del{k}_m` in ascending `k`.
6. `E_del{i}_del{j}_mm` in lexicographic `(i,j)` order.
7. `E_del{i}_del{j}_mp` in lexicographic `(i,j)` order.

Here $\kappa$ is included first only when ordering the central extension.
The even central element `K` is identified with the scalar identity and is
excluded from the basis and PBW ordering.
