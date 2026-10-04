# Notation and Terminology

This document defines the notation used for the $C(n+1)=\mathfrak{osp}(2|2n)$
oscillator basis and its schema.

## Root and oscillator labels

Use $\varepsilon$ for the $\mathfrak{so}(2)$ root coordinate and
$\delta_1,\ldots,\delta_n$ for the $\mathfrak{sp}(2n)$ coordinates. Oscillators
are $a_1^+,a_1^-$ (odd, with $\{a_1^-,a_1^+\}=1$) and $b_k^+,b_k^-$
(even, with $[b_k^-,b_l^+]=\delta_{kl}$). The two oscillator sectors commute.
In schema labels, `p` and `m` mean $+$ and $-$ respectively.

Use the Cartan generators $H_1,\ldots,H_{n+1}$ as in
`docs/math/Cn1_definition.md`. For $1\leq i<j\leq n$, the even root labels are:

| Root | Label | Oscillator word |
|---|---|---|
| $2\delta_k$ | `E_2del{k}_p` | $(b_k^+)^2$ |
| $-2\delta_k$ | `E_2del{k}_m` | $(b_k^-)^2$ |
| $\delta_i+\delta_j$ | `E_del{i}_del{j}_pp` | $b_i^+b_j^+$ |
| $\delta_i-\delta_j$ | `E_del{i}_del{j}_pm` | $b_i^+b_j^-$ |
| $-\delta_i+\delta_j$ | `E_del{i}_del{j}_mp` | $b_i^-b_j^+$ |
| $-\delta_i-\delta_j$ | `E_del{i}_del{j}_mm` | $b_i^-b_j^-$ |

The four odd-root labels for each $k$ are:

| Root | Label | Oscillator word |
|---|---|---|
| $\varepsilon+\delta_k$ | `E_eps1_del{k}_pp` | $a_1^+b_k^+$ |
| $\varepsilon-\delta_k$ | `E_eps1_del{k}_pm` | $a_1^+b_k^-$ |
| $-\varepsilon+\delta_k$ | `E_eps1_del{k}_mp` | $a_1^-b_k^+$ |
| $-\varepsilon-\delta_k$ | `E_eps1_del{k}_mm` | $a_1^-b_k^-$ |

Thus the even basis is
$$
\{H_r:1\leq r\leq n+1\}
\cup\{E_{\pm2\delta_k}:1\leq k\leq n\}
\cup\{E_{\pm\delta_i\pm\delta_j}:1\leq i<j\leq n\},
$$
and the odd basis is
$$
\{E_{\pm\varepsilon\pm\delta_k}:1\leq k\leq n\}.
$$
Their dimensions are $2n^2+n+1$ and $4n$, respectively.

## Explicit basis lists

The following lists use the generator labels above; each comma-separated
entry is a distinct basis element.

### C(2), $n=1$

- Even: `H_1`, `H_2`, `E_2del1_p`, `E_2del1_m`.
- Odd: `E_eps1_del1_pp`, `E_eps1_del1_pm`, `E_eps1_del1_mp`, `E_eps1_del1_mm`.

### C(3), $n=2$

- Even: `H_1`, `H_2`, `H_3`, `E_2del1_p`, `E_2del2_p`,
  `E_del1_del2_pp`, `E_del1_del2_pm`, `E_2del1_m`, `E_2del2_m`,
  `E_del1_del2_mm`, `E_del1_del2_mp`.
- Odd: `E_eps1_del1_pp`, `E_eps1_del1_pm`, `E_eps1_del1_mp`,
  `E_eps1_del1_mm`, `E_eps1_del2_pp`, `E_eps1_del2_pm`,
  `E_eps1_del2_mp`, `E_eps1_del2_mm`.

### C(4), $n=3$

- Even: `H_1`, `H_2`, `H_3`, `H_4`, `E_2del1_p`, `E_2del2_p`,
  `E_2del3_p`, `E_del1_del2_pp`, `E_del1_del2_pm`, `E_del1_del3_pp`,
  `E_del1_del3_pm`, `E_del2_del3_pp`, `E_del2_del3_pm`, `E_2del1_m`,
  `E_2del2_m`, `E_2del3_m`, `E_del1_del2_mm`, `E_del1_del2_mp`,
  `E_del1_del3_mm`, `E_del1_del3_mp`, `E_del2_del3_mm`,
  `E_del2_del3_mp`.
- Odd: for each `k` in `1, 2, 3`, in order:
  `E_eps1_del{k}_pp`, `E_eps1_del{k}_pm`, `E_eps1_del{k}_mp`,
  `E_eps1_del{k}_mm`.

## PBW ordering

Two compatible total-order choices are:

1. The schema grouping order: $\kappa$ (when the odd central extension is
   present), all odd-root generators ordered by increasing $k$ and then
   `pp`, `pm`, `mp`, `mm`; Cartan generators in increasing index; positive
   even-root generators; then negative even-root generators. Positive even
   roots are $2\delta_k$ and $\delta_i\pm\delta_j$ for $i<j$; their negatives
   follow in matching root-label order.
2. A root-coordinate lexicographic order, sorting all roots by the
   coefficient tuple of $(\varepsilon,\delta_1,\ldots,\delta_n)$ and placing
   Cartan generators between the negative- and positive-root blocks.

Use choice 1 in this repository. It is explicit in the schema, extends the
existing B(0,n) grouping convention, and keeps the four odd-root types
contiguous for each bosonic index. Here $\kappa$ is only an ordering prefix
for the extended algebra and is not part of the $C(n+1)$ basis; $K=1$ is
likewise excluded from the basis.
