# Notation and Terminology

This document defines the mathematical notation and terminology used in this repository.
It records the finalized conventions for the $C(n+1)=\mathfrak{osp}(2|2n)$
schema extension.

## Conventions

### Root notation and basis

Use $\varepsilon$ for the one-dimensional $\mathfrak{so}(2)$ weight and
$\delta_1,\ldots,\delta_n$ for the $\mathfrak{sp}(2n)$ weights. The even roots
are $\pm2\delta_i$ and $\pm\delta_i\pm\delta_j$ ($i<j$); the odd roots are
$\pm\varepsilon\pm\delta_i$. The even subalgebra also contains the
$\mathfrak{so}(2)$ Cartan generator, so the Cartan basis is
$H_1,\ldots,H_{n+1}$.

For a pair of bosonic indices $i<j$, label even root generators by
`E_del{i}_del{j}_xy`, where `x` is the sign of $\delta_i$ and `y` the sign of
$\delta_j$ (`p` means $+$, `m` means $-$). Thus `pp`, `pm`, `mp`, and `mm`
represent $\delta_i+\delta_j$, $\delta_i-\delta_j$, $-\delta_i+\delta_j$,
and $-\delta_i-\delta_j$. The single-index even generators `E_2del{i}_p`
and `E_2del{i}_m` represent $2\delta_i$ and $-2\delta_i`.

Label the odd generators `E_eps1_del{i}_xy`; here `x` is the sign of
$\varepsilon$ and `y` the sign of $\delta_i$, in that order. Specifically:

| Label | Root |
|---|---|
| `E_eps1_del{i}_pp` | $\varepsilon+\delta_i$ |
| `E_eps1_del{i}_pm` | $\varepsilon-\delta_i$ |
| `E_eps1_del{i}_mp` | $-\varepsilon+\delta_i$ |
| `E_eps1_del{i}_mm` | $-\varepsilon-\delta_i$ |

The even basis consists of $H_1,\ldots,H_{n+1}$, both `E_2del{i}_p/m` for
each $i$, and all four `E_del{i}_del{j}_xy` for each $i<j$. The odd basis
consists of all four `E_eps1_del{i}_xy` for each $i$. These give
$2n^2+n+1$ even and $4n$ odd basis elements.

#### Concrete bases

- **C(2), $n=1$** — Even: `H_1`, `H_2`, `E_2del1_p`, `E_2del1_m`.
  Odd: `E_eps1_del1_pp`, `E_eps1_del1_pm`, `E_eps1_del1_mp`,
  `E_eps1_del1_mm`.
- **C(3), $n=2$** — Even: `H_1`, `H_2`, `H_3`, `E_2del1_p`,
  `E_2del1_m`, `E_2del2_p`, `E_2del2_m`, `E_del1_del2_pp`,
  `E_del1_del2_pm`, `E_del1_del2_mp`, `E_del1_del2_mm`. Odd:
  `E_eps1_del1_pp`, `E_eps1_del1_pm`, `E_eps1_del1_mp`,
  `E_eps1_del1_mm`, `E_eps1_del2_pp`, `E_eps1_del2_pm`,
  `E_eps1_del2_mp`, `E_eps1_del2_mm`.
- **C(4), $n=3$** — Even: `H_1`, `H_2`, `H_3`, `H_4`; `E_2del{i}_p/m`
  for $i=1,2,3$; and `E_del1_del2_xy`, `E_del1_del3_xy`,
  `E_del2_del3_xy` for each `xy` in `pp`, `pm`, `mp`, `mm`. Odd:
  `E_eps1_del{i}_xy` for each $i=1,2,3$ and `xy` in `pp`, `pm`, `mp`, `mm`.
  (Counts: 22 even and 12 odd.)

### Oscillator labels

Use the standard fermionic pair `a_1_p` and `a_1_m` for $a_1^+$ and $a_1^-$,
with parity 1 and $\{a_1^-,a_1^+\}=1$. Use bosonic labels `b_{i}_p` and
`b_{i}_m` for $b_i^+$ and $b_i^-$, with parity 0 and
$[b_i^-,b_j^+]=\delta_{ij}$. The pairwise oscillator realization of an odd
root generator follows the two signs in its root label: the $\varepsilon$
sign selects `a_1_p/m`, and the $\delta_i$ sign selects `b_i_p/m`.

### PBW ordering

Two valid candidate orders are:

1. **Root-grouped order (selected):** Cartan generators in index order, then
   positive even roots, positive odd roots, negative odd roots, and negative
   even roots. Within each group use increasing indices and lexicographic
   sign-label order (`pp`, `pm`, `mp`, `mm`); use `p` before `m` for
   single-index roots.
2. **B-style parity-grouped order:** all odd root generators first (in index
   and sign-label order), followed by the Cartan generators and even root
   generators (Cartan, positive even roots, negative even roots).

Use the root-grouped order for C schemas: it keeps Cartan and positive/negative
root sectors explicit and is readily checked against the root decomposition.
For this order, positive odd roots are $\varepsilon\pm\delta_i$ and negative
odd roots are $-\varepsilon\pm\delta_i$; positive even roots are
$2\delta_i$ and $\delta_i\pm\delta_j$ for $i<j$. The negative root groups
contain their opposites. The central identity $K$, when recorded in a schema,
is a scalar and is excluded from the basis and PBW ordering.
