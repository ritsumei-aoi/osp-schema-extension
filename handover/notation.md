# Notation and Terminology

This document defines the mathematical notation and terminology used in this repository.
It is initialized during the $C(n+1)$ schema extension project.

## Conventions

### Root coordinates for \(C(n+1)=\mathfrak{osp}(2|2n)\)

Use \(\varepsilon,\delta_1,\ldots,\delta_n\), where \(\varepsilon\) is the
fermionic coordinate and the \(\delta_i\) are the bosonic coordinates. The
simple roots are
\[
\alpha_1=\varepsilon-\delta_1,\qquad
\alpha_{i+1}=\delta_i-\delta_{i+1}\ (1\leq i<n),\qquad
\alpha_{n+1}=2\delta_n.
\]
The positive even roots are \(2\delta_i\), \(\delta_i+\delta_j\), and
\(\delta_i-\delta_j\) for \(i<j\). The positive odd roots are
\(\varepsilon+\delta_i\) and \(\varepsilon-\delta_i\). Negative roots are
the opposites of the corresponding positive roots.

The even part has Cartan generators \(H_1,\ldots,H_{n+1}\), including the
\(\mathfrak{so}(2)\) Cartan generator. The even and odd dimensions are
\(2n^2+n+1\) and \(4n\), respectively.

### Oscillator and generator labels

Use the standard fermionic pair `a_1_p`, `a_1_m` and bosonic pairs
`b_i_p`, `b_i_m` for \(1\leq i\leq n\). In labels, `p` and `m` denote the
signs \(+\) and \(-\). The first sign suffix in an odd-root label is the
\(\varepsilon\) sign; the second is the \(\delta_i\) sign.

| Root | Generator label | Oscillator realization |
|---|---|---|
| \(2\delta_i\) | `E_2del{i}_p` | \(\tfrac12(b_i^+)^2\) |
| \(-2\delta_i\) | `E_2del{i}_m` | \(\tfrac12(b_i^-)^2\) |
| \(\delta_i+\delta_j\), \(i<j\) | `E_del{i}_del{j}_pp` | `b_i_p b_j_p` |
| \(\delta_i-\delta_j\), \(i<j\) | `E_del{i}_del{j}_pm` | `b_i_p b_j_m` |
| \(-\delta_i+\delta_j\), \(i<j\) | `E_del{i}_del{j}_mp` | `b_i_m b_j_p` |
| \(-\delta_i-\delta_j\), \(i<j\) | `E_del{i}_del{j}_mm` | `b_i_m b_j_m` |
| \(\varepsilon+\delta_i\) | `E_eps1_del{i}_pp` | `a_1_p b_i_p` |
| \(\varepsilon-\delta_i\) | `E_eps1_del{i}_pm` | `a_1_p b_i_m` |
| \(-\varepsilon+\delta_i\) | `E_eps1_del{i}_mp` | `a_1_m b_i_p` |
| \(-\varepsilon-\delta_i\) | `E_eps1_del{i}_mm` | `a_1_m b_i_m` |

The long-root normalization follows the I02 approval: use the factor
\(\tfrac12\) uniformly for every \(E_{\pm2\delta_i}\).

### Basis lists

The following lists use a fixed display order. Even generators are listed as
Cartan generators, positive long roots, positive pair roots, negative long
roots, negative sum roots, then mixed-sign pair roots (`pm` before `mp`).
Odd generators are listed by increasing delta index, first the
positive-\(\varepsilon\) roots (`pp`, `pm`), then the negative-\(\varepsilon\)
roots (`mp`, `mm`).

**C(2), \(n=1\)**

- Even: `H_1, H_2, E_2del1_p, E_2del1_m`
- Odd: `E_eps1_del1_pp, E_eps1_del1_pm, E_eps1_del1_mp, E_eps1_del1_mm`
- Dimension: \(4|4\), total \(8\)

**C(3), \(n=2\)**

- Even: `H_1, H_2, H_3, E_2del1_p, E_2del2_p, E_del1_del2_pp, E_2del1_m, E_2del2_m, E_del1_del2_mm, E_del1_del2_pm, E_del1_del2_mp`
- Odd: `E_eps1_del1_pp, E_eps1_del1_pm, E_eps1_del2_pp, E_eps1_del2_pm, E_eps1_del1_mp, E_eps1_del1_mm, E_eps1_del2_mp, E_eps1_del2_mm`
- Dimension: \(11|8\), total \(19\)

**C(4), \(n=3\)**

- Even: `H_1, H_2, H_3, H_4, E_2del1_p, E_2del2_p, E_2del3_p, E_del1_del2_pp, E_del1_del3_pp, E_del2_del3_pp, E_2del1_m, E_2del2_m, E_2del3_m, E_del1_del2_mm, E_del1_del3_mm, E_del2_del3_mm, E_del1_del2_pm, E_del1_del2_mp, E_del1_del3_pm, E_del1_del3_mp, E_del2_del3_pm, E_del2_del3_mp`
- Odd: `E_eps1_del1_pp, E_eps1_del1_pm, E_eps1_del2_pp, E_eps1_del2_pm, E_eps1_del3_pp, E_eps1_del3_pm, E_eps1_del1_mp, E_eps1_del1_mm, E_eps1_del2_mp, E_eps1_del2_mm, E_eps1_del3_mp, E_eps1_del3_mm`
- Dimension: \(22|12\), total \(34\)

### PBW ordering

Use the B(0,n) parity-block convention, as approved for Issue I01-1:
\[
\kappa < [\text{odd generators}] < [\text{even generators}].
\]
Within the odd block, list `E_eps1_del{i}_pp`, `E_eps1_del{i}_pm` for
increasing \(i\), followed by `E_eps1_del{i}_mp`, `E_eps1_del{i}_mm` for
increasing \(i\). Within the even block, use the even-generator display order
specified above. The scalar identity \(K\) is not an independent basis
element and is excluded. Include \(\kappa\) first only in an extended basis
that represents the deformation element.
