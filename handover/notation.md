# Notation and Terminology

This document defines the mathematical notation and terminology used in this repository.
It is initialized during the $C(n+1)$ schema extension project.

## C(n+1) = osp(2|2n) conventions

The root vectors are \(\varepsilon,\delta_1,\ldots,\delta_n\). The even
roots are \(\pm2\delta_k\) and \(\pm\delta_i\pm\delta_j\) for \(i<j\);
the odd roots are \(\pm\varepsilon\pm\delta_k\). The even Cartan basis is
\(H_1,\ldots,H_{n+1}\), so the even basis has \(n+1+2n^2\) elements and
the odd basis has \(4n\) elements.

### Generator labels

- Cartan generators: `H_1` through `H_{n+1}`.
- Roots \(2\delta_k,-2\delta_k\): `E_2del{k}_p`, `E_2del{k}_m`.
- For \(i<j\), roots \(\delta_i+\delta_j,\delta_i-\delta_j,
  -\delta_i+\delta_j,-\delta_i-\delta_j\): respectively
  `E_del{i}_del{j}_pp`, `_pm`, `_mp`, `_mm`.
- Odd roots \(+\varepsilon+\delta_k,+\varepsilon-\delta_k,
  -\varepsilon+\delta_k,-\varepsilon-\delta_k\): respectively
  `E_eps1_del{k}_pp`, `_pm`, `_mp`, `_mm`. The first suffix sign is the
  sign of \(\varepsilon\); the second is the sign of \(\delta_k\).

In oscillator realizations, `a_1_p` and `a_1_m` denote \(a_1^+\) and
\(a_1^-\); `b_{k}_p` and `b_{k}_m` denote \(b_k^+\) and \(b_k^-\).
Thus the four odd generators at index \(k\), in suffix order `pp`, `pm`,
`mp`, `mm`, are `a_1_p b_k_p`, `a_1_p b_k_m`, `a_1_m b_k_p`,
`a_1_m b_k_m`. The pair \(a_1^\pm\) and all \(b_k^\pm\) are odd and even,
respectively.

### Basis lists

For each \(n\), the even list consists of `H_1` through `H_{n+1}`, then
`E_2del{k}_p` for \(k=1,\ldots,n\), then `E_del{i}_del{j}_pp` for
\(i<j\), then the corresponding `E_2del{k}_m`, `E_del{i}_del{j}_mm`,
`E_del{i}_del{j}_pm`, and `E_del{i}_del{j}_mp`. Within each indexed
group, indices increase lexicographically (`i`, then `j`). The odd list
is the four labels for each increasing \(k\), in `pp`, `pm`, `mp`, `mm`
order.

| Algebra | Even basis (in the ordering just defined) | Odd basis |
|---|---|---|
| C(2), \(n=1\) | `H_1, H_2, E_2del1_p, E_2del1_m` | `E_eps1_del1_pp, E_eps1_del1_pm, E_eps1_del1_mp, E_eps1_del1_mm` |
| C(3), \(n=2\) | `H_1, H_2, H_3, E_2del1_p, E_2del2_p, E_del1_del2_pp, E_2del1_m, E_2del2_m, E_del1_del2_mm, E_del1_del2_pm, E_del1_del2_mp` | `E_eps1_del1_pp, E_eps1_del1_pm, E_eps1_del1_mp, E_eps1_del1_mm, E_eps1_del2_pp, E_eps1_del2_pm, E_eps1_del2_mp, E_eps1_del2_mm` |
| C(4), \(n=3\) | `H_1, H_2, H_3, H_4, E_2del1_p, E_2del2_p, E_2del3_p, E_del1_del2_pp, E_del1_del3_pp, E_del2_del3_pp, E_2del1_m, E_2del2_m, E_2del3_m, E_del1_del2_mm, E_del1_del3_mm, E_del2_del3_mm, E_del1_del2_pm, E_del1_del3_pm, E_del2_del3_pm, E_del1_del2_mp, E_del1_del3_mp, E_del2_del3_mp` | `E_eps1_del1_pp, E_eps1_del1_pm, E_eps1_del1_mp, E_eps1_del1_mm, E_eps1_del2_pp, E_eps1_del2_pm, E_eps1_del2_mp, E_eps1_del2_mm, E_eps1_del3_pp, E_eps1_del3_pm, E_eps1_del3_mp, E_eps1_del3_mm` |

The resulting dimensions are \(3\mid4\) for C(2), \(11\mid8\) for C(3),
and \(22\mid12\) for C(4), matching the root counts.

### PBW ordering

Two consistent block-order choices are:

1. \(\kappa < [\text{odd generators}] < [\text{even generators}]\), with
   the within-block order of the basis lists above.
2. \(\kappa < [\text{even generators}] < [\text{odd generators}]\), with
   the same within-block orders.

Use option 1, matching the B(0,n) v5.0 convention to minimize changes in
consumers and make the odd deformation sector contiguous. The even central
identity \(K=1\) is recorded as metadata, not included in the basis or
ordering. \(\kappa\) is an extension symbol, not a basis generator of
\(\mathfrak{osp}(2|2n)\).
