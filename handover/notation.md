# Notation and Terminology

This document defines the mathematical notation and terminology used in this repository.
It is initialized during the $C(n+1)$ schema extension project.

## Conventions

## C(n+1) = osp(2|2n)

Use \(\varepsilon\) for the one-dimensional orthogonal direction and
\(\delta_1,\ldots,\delta_n\) for the symplectic directions. A `p` suffix means
the positive oscillator and an `m` suffix means the negative oscillator.
`eps1` denotes \(\varepsilon\); the first sign suffix belongs to
\(\varepsilon\), and the second to \(\delta_k\).

### Basis and labels

The even basis consists of \(n+1\) Cartan elements, the \(2n\) roots
\(\pm2\delta_k\), and the four roots \(\pm\delta_i\pm\delta_j\) for every
\(i<j\). The odd basis consists of the \(4n\) roots
\(\pm\varepsilon\pm\delta_k\). The labels are:

| Element | Label pattern | Parity |
|---|---|---:|
| Cartan in the \(\varepsilon\) direction | `H_eps` | 0 |
| Cartan in the \(k\)-th \(\delta\) direction | `H_k` | 0 |
| \(\pm2\delta_k\) | `E_2del{k}_p`, `E_2del{k}_m` | 0 |
| \(\pm\delta_i\pm\delta_j\), \(i<j\) | `E_del{i}_del{j}_pp`, `..._pm`, `..._mp`, `..._mm` | 0 |
| \(\pm\varepsilon\pm\delta_k\) | `E_eps1_del{k}_pp`, `..._pm`, `..._mp`, `..._mm` | 1 |

In pair labels, `pp`, `pm`, `mp`, `mm` encode the two signs in the displayed
order. Thus the odd labels mean respectively
\(\varepsilon+\delta_k,\varepsilon-\delta_k,-\varepsilon+\delta_k,
-\varepsilon-\delta_k\). The four oscillator generator labels are `a_1_p`,
`a_1_m`, `b_{k}_p`, and `b_{k}_m`; their parities are 1 and 0 respectively.
The standard oscillator realization uses \(a_1^+b_k^\pm\) and
\(a_1^-b_k^\pm\) for the odd roots, and the usual quadratic boson monomials
and number operators for the even basis. The fermions satisfy
\(\{a_1^-,a_1^+\}=1\); the bosons satisfy
\([b_i^-,b_j^+]=\delta_{ij}\); fermions and bosons commute.

The bases for the requested ranks, in PBW sequence, are:

* **C(2), \(n=1\)** — even:
  `H_eps, H_1, E_2del1_p, E_2del1_m`; odd:
  `E_eps1_del1_pp, E_eps1_del1_pm, E_eps1_del1_mp, E_eps1_del1_mm`.
* **C(3), \(n=2\)** — even:
  `H_eps, H_1, H_2, E_2del1_p, E_2del2_p,
  E_del1_del2_pp, E_del1_del2_pm, E_del1_del2_mp, E_del1_del2_mm,
  E_2del1_m, E_2del2_m`; odd:
  `E_eps1_del1_pp, E_eps1_del1_pm, E_eps1_del1_mp, E_eps1_del1_mm,
  E_eps1_del2_pp, E_eps1_del2_pm, E_eps1_del2_mp, E_eps1_del2_mm`.
* **C(4), \(n=3\)** — even:
  `H_eps, H_1, H_2, H_3, E_2del1_p, E_2del2_p, E_2del3_p,
  E_del1_del2_pp, E_del1_del2_pm, E_del1_del2_mp, E_del1_del2_mm,
  E_del1_del3_pp, E_del1_del3_pm, E_del1_del3_mp, E_del1_del3_mm,
  E_del2_del3_pp, E_del2_del3_pm, E_del2_del3_mp, E_del2_del3_mm,
  E_2del1_m, E_2del2_m, E_2del3_m`; odd:
  `E_eps1_del1_pp, E_eps1_del1_pm, E_eps1_del1_mp, E_eps1_del1_mm,
  E_eps1_del2_pp, E_eps1_del2_pm, E_eps1_del2_mp, E_eps1_del2_mm,
  E_eps1_del3_pp, E_eps1_del3_pm, E_eps1_del3_mp, E_eps1_del3_mm`.

### PBW ordering

Two deterministic choices were considered: (1) sort all root vectors by a
chosen positive-root system, with negative roots, Cartan, then positive roots;
(2) retain the existing project convention of listing all odd root vectors
before the even basis. Choice (2) is used for the serialized basis to remain
compatible with the B(0,n) files and make parity blocks contiguous. Within the
odd block, order by increasing \(k\), then `pp`, `pm`, `mp`, `mm`. Within the
even block, list `H_eps`, then `H_k` by increasing \(k\), positive long roots
by increasing \(k\), mixed roots by increasing \((i,j)\) and sign code, then
negative long roots by increasing \(k\). The scalar central identity \(K=1\)
is not a basis vector; the odd central symbol \(\kappa\), when present in an
extension, precedes the algebra basis. This is an explicit PBW monomial
ordering convention, not a claim that it is the unique root-theoretic order.

The resulting dimensions are even \(2n^2+n+1\) and odd \(4n\).
