# Notation and Terminology

This document defines the mathematical notation and terminology used in this repository.
It was finalized in Issue I01 for the $C(n+1) = \mathfrak{osp}(2|2n)$ schema extension project.

## 1. Conventions

- `n` = bosonic rank (number of boson pairs $b_k^\pm$). C(2)=osp(2|2) is `n=1`, C(3)=osp(2|4) is `n=2`, C(4)=osp(2|6) is `n=3`.
- Parity: `0` even, `1` odd. The bracket is the supercommutator
  $[X,Y\} = XY - (-1)^{p(X)p(Y)} YX$ in the oscillator algebra.
- Oscillators: fermions $a_1^\pm$ (`a_1_p`, `a_1_m`), $\{a_1^-,a_1^+\}=1$, $(a_1^\pm)^2=0$;
  bosons $b_k^\pm$ (`b_k_p`, `b_k_m`), $[b_k^-,b_l^+]=\delta_{kl}$.
- Central elements: $K$ (even, identified with the scalar $1$, NOT a basis element) and $\kappa$ (odd, $\kappa^2=0$, central).
- Weyl-ordered number operators: $h_a = a_1^+a_1^- - \tfrac12$, $h_k = b_k^+b_k^- + \tfrac12$.
  Using these, $\mathfrak g$ closes under the bracket with no central term.
- Index conventions: $1\le k\le n$ for bosons; Cartan index $1\le k\le n+1$.

## 2. Basis (Frappat notation, $\varepsilon$ fermionic, $\delta_k$ bosonic)

Dimensions: even $=2n^2+n+1$, odd $=4n$, total $=2n^2+5n+1$.

### Generator labels and realizations

All realizations are written in PBW-ordered words (oscillator order: `a_1_p < a_1_m < b_1_p < b_1_m < b_2_p < ...`).

| Root | Label | Parity | Realization |
|---|---|---|---|
| Cartan, $k=1$ | `H_1` | 0 | $a_1^+a_1^- + b_1^+b_1^-$ ($=h_a+h_1$) |
| Cartan, $2\le k\le n$ | `H_k` | 0 | $b_{k-1}^+b_{k-1}^- - b_k^+b_k^-$ |
| Cartan, $k=n+1$ | `H_{n+1}` | 0 | $-b_n^+b_n^- - \tfrac12$ ($=-h_n$) |
| $2\delta_k$ | `E_2del{k}_p` | 0 | $(b_k^+)^2$ |
| $-2\delta_k$ | `E_2del{k}_m` | 0 | $(b_k^-)^2$ |
| $\delta_i+\delta_j$ ($i<j$) | `E_del{i}_del{j}_pp` | 0 | $b_i^+b_j^+$ |
| $-\delta_i-\delta_j$ | `E_del{i}_del{j}_mm` | 0 | $b_i^-b_j^-$ |
| $\delta_i-\delta_j$ | `E_del{i}_del{j}_pm` | 0 | $b_i^+b_j^-$ |
| $\delta_j-\delta_i$ | `E_del{i}_del{j}_mp` | 0 | $b_i^-b_j^+$ |
| $\varepsilon+\delta_k$ | `E_eps1_del{k}_pp` | 1 | $a_1^+b_k^+$ |
| $\varepsilon-\delta_k$ | `E_eps1_del{k}_pm` | 1 | $a_1^+b_k^-$ |
| $-\varepsilon+\delta_k$ | `E_eps1_del{k}_mp` | 1 | $a_1^-b_k^+$ |
| $-\varepsilon-\delta_k$ | `E_eps1_del{k}_mm` | 1 | $a_1^-b_k^-$ |

Label suffix `_{s1}{s2}`: for odd generators `s1` is the sign of $\varepsilon$ (fermion $a_1^{s1}$) and `s2` the sign of $\delta_k$ (boson $b_k^{s2}$);
for even two-index generators `s1`, `s2` are the signs of $\delta_i$, $\delta_j$.

Deviations from `Cn1_definition.md`: the doc writes $E_{\delta_1-\varepsilon}=b_1^+a_1^-$ and $E_{\pm2\delta_n}=\tfrac12(b_n^\pm)^2$ among the simple generators,
while its "all root generators" list uses $(b^\pm)^2$. We use the uniform forms `a b` (fermion first, PBW) and $(b^\pm)^2$.
They agree up to ordering/normalization in the undeformed algebra; the fermion-first form is the PBW normal form that remains unambiguous when $[b,a]\neq 0$ (deformation).

### Explicit basis lists

**C(2) (n=1)**: even (4) `H_1, H_2, E_2del1_p, E_2del1_m`; odd (4) `E_eps1_del1_pp, E_eps1_del1_pm, E_eps1_del1_mp, E_eps1_del1_mm`.

**C(3) (n=2)**: even (11) `H_1, H_2, H_3, E_2del1_p, E_2del2_p, E_del1_del2_pp, E_2del1_m, E_2del2_m, E_del1_del2_mm, E_del1_del2_pm, E_del1_del2_mp`; odd (8) `E_eps1_del{1,2}_{pp,pm,mp,mm}` (ordered below).

**C(4) (n=3)**: even (22) `H_1..H_4`, `E_2del{1,2,3}_p`, `E_del{12,13,23}_pp`, `E_2del{1,2,3}_m`, `E_del{12,13,23}_mm`, `E_del{12,13,23}_pm`, `E_del{12,13,23}_mp`; odd (12) `E_eps1_del{1,2,3}_{pp,pm,mp,mm}`.

(`del{ij}` abbreviates `del{i}_del{j}`.)

## 3. PBW ordering

Options considered:

1. **Parity-first (B(0,n)-compatible)**: $\kappa <$ odd $<$ even; within each parity block ordered by sign-type blocks. Keeps the B(0,n) v5.0 `basis` layout.
2. **Root-height / Chevalley**: $H <$ positive roots $<$ negative roots with $\varepsilon$-roots interleaved by height. Natural for Lie theory, but mixes parities and departs from the B(0,n) schema (breaks backward compatibility).
3. **Oscillator-word lexicographic**: order generators by their oscillator words (fermion letters first). Equivalent to option 1 up to internal order but gives no readable root structure.

**Chosen: option 1.** Reasons: (i) backward compatibility with B(0,n) v5.0 ("κ < [odd] < [even]");
(ii) odd generators $a_1^\sigma b^s$ begin with a fermion letter, so odd-before-even matches the oscillator normal order (fermions left of bosons), which makes the rewriting of $[b,a]=-\mathrm{gb}\,\kappa$ well defined;
(iii) it fixes one list order used for all JSON arrays.

Concrete order:

- $\kappa$ (formal, not in `basis`).
- odd: `E_eps1_del{k}_pp` ($k=1..n$), then `_pm`, then `_mp`, then `_mm` (blocks of $n$, mirroring B(0,n)'s "all `_p` then all `_m`").
- even: `H_1..H_{n+1}`, `E_2del{k}_p`, `E_del{i}_del{j}_pp` (lexicographic $i<j$), `E_2del{k}_m`, `E_del{i}_del{j}_mm`, `E_del{i}_del{j}_pm`, `E_del{i}_del{j}_mp`.

The JSON `basis.even`/`basis.odd` lists use exactly this order.

## 4. Oscillator generator labels

- Fermions: `a_1_p` ($a_1^+$), `a_1_m` ($a_1^-$), parity 1 (`m=1`: a single fermionic pair).
- Bosons: `b_k_p`, `b_k_m`, $k=1..n$, parity 0.
- Formal central symbols: `kappa` (parity 1), `K` (parity 0).
- Deformation parameters: `gb_a_1_{σ}_b_{k}_{s}` with $\sigma,s\in\{p,m\}$; $4n$ in total, defined by $[b_k^s,a_1^\sigma]=-\mathrm{gb}_{\sigma,k,s}\,\kappa$. The $2\times 2n$ matrix has rows `a_1_p, a_1_m` and columns `b_1_p, b_1_m, ..., b_n_p, b_n_m`.
- Coefficients are rational strings (`"1/2"`).

## 5. Schema layers and file names (data/)

| Layer | File |
|---|---|
| 1 | `C_{n}_structure.json` |
| 2 | `C_{n}_gamma.json` |
| 3 | `C_{n}_evaluated.json` (+ `C_{n}_evaluated_<profile>.json`) |
| 4 | `C_{n}_coboundary.json` (+ `C_{n}_coboundary_<profile>.json`) |
