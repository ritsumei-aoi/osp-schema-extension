# Notation and Terminology

This document defines the mathematical notation and terminology used in this repository.
It is initialized during the $C(n+1)$ schema extension project and finalized in Issue I01.

## 1. Algebra and dimensions

$C(n+1) = \mathfrak{osp}(2|2n)$, rank $n+1$, $n \ge 1$. Even part $\mathfrak{so}(2)\oplus\mathfrak{sp}(2n)$.

| $n$ | algebra | even $(2n^2+n+1)$ | odd $(4n)$ | total $(2n^2+5n+1)$ |
|---|---|---|---|---|
| 1 | $C(2)$ | 4 | 4 | 8 |
| 2 | $C(3)$ | 11 | 8 | 19 |
| 3 | $C(4)$ | 22 | 12 | 34 |

File naming: $C_{n}$ with $n$ the bosonic rank (so $C(2)$ is `C_1_*`).

## 2. Oscillators (associative algebra used for all computations)

- Standard fermion pair $a^{+}=a_1^{+}$, $a^{-}=a_1^{-}$, parity 1:
  $\{a^{-},a^{+}\}=1$, and $(a^{\pm})^2=0$ (the CAR includes $\{a^\pm,a^\pm\}=0$).
- Bosons $b_k^{\pm}$, $k=1,\dots,n$, parity 0: $[b_k^{-},b_l^{+}]=\delta_{kl}$, $[b_k^\pm,b_l^\pm]=0$.
- $a^{\pm}$ and $b_k^{\pm}$ commute.
- Deformation (`C_inhomogeneous_definition.md`): $[b_j^{s},a^{\sigma}]=-\mathrm{gb}_{\sigma,j,s}\,\kappa$, with $\kappa$ odd, $\kappa^2=0$.
  Equivalently $b_j^{s}a^{\sigma}=a^{\sigma}b_j^{s}-\mathrm{gb}_{\sigma,j,s}\kappa$.
  $\kappa$ is **super-central**: it commutes with bosons and anticommutes with $a^{\pm}$ (decision A5).
  $\kappa$ is written at the right end of each monomial.

**Normal ordering (PBW convention of oscillator words):** fermions to the left of bosons,
$a^{+}$ before $a^{-}$, $b^{+}$ before $b^{-}$, bosons sorted by index.
Thus the odd basis elements are written $a^{\sigma}b_k^{s}$ (fermion first).

**Labels of oscillator letters (JSON):** $a^{+}\to$ `a_1_p`, $a^{-}\to$ `a_1_m`, $b_k^{\pm}\to$ `b_k_p`, `b_k_m`.

## 3. Basis and generator labels

Odd generators (parity 1), $4n$ of them. Label `E_eps1_del{k}_{xy}`: $x$ is the sign of $\varepsilon$,
$y$ the sign of $\delta_k$.

| label | root | oscillator form |
|---|---|---|
| `E_eps1_del{k}_pp` | $\varepsilon+\delta_k$ | $a^{+}b_k^{+}$ |
| `E_eps1_del{k}_pm` | $\varepsilon-\delta_k$ | $a^{+}b_k^{-}$ |
| `E_eps1_del{k}_mp` | $-\varepsilon+\delta_k$ | $a^{-}b_k^{+}$ |
| `E_eps1_del{k}_mm` | $-\varepsilon-\delta_k$ | $a^{-}b_k^{-}$ |

Even generators (parity 0), $2n^2+n+1$ of them:

| label | element |
|---|---|
| `H_1` | $a^{+}a^{-}+b_1^{+}b_1^{-}$ |
| `H_k`, $2\le k\le n$ | $b_{k-1}^{+}b_{k-1}^{-}-b_k^{+}b_k^{-}$ |
| `H_{n+1}` | $-b_n^{+}b_n^{-}-\tfrac12$ |
| `E_2del{k}_p` | $\tfrac12 (b_k^{+})^2$ |
| `E_2del{k}_m` | $\tfrac12 (b_k^{-})^2$ |
| `E_del{i}_del{j}_pp` ($i<j$) | $b_i^{+}b_j^{+}$ |
| `E_del{i}_del{j}_pm` | $b_i^{+}b_j^{-}$ |
| `E_del{i}_del{j}_mp` | $b_i^{-}b_j^{+}$ |
| `E_del{i}_del{j}_mm` | $b_i^{-}b_j^{-}$ |

Explicit lists (PBW order, see §4):

- $n=1$ ($C(2)$): odd `E_eps1_del1_{pp,pm,mp,mm}`; even `H_1, H_2, E_2del1_p, E_2del1_m`.
- $n=2$ ($C(3)$): odd `E_eps1_del{1,2}_{pp,pm,mp,mm}` (8); even `H_1, H_2, H_3, E_2del1_p, E_2del2_p, E_del1_del2_pp, E_2del1_m, E_2del2_m, E_del1_del2_mm, E_del1_del2_pm, E_del1_del2_mp` (11).
- $n=3$ ($C(4)$): odd `E_eps1_del{1,2,3}_{pp,pm,mp,mm}` (12); even `H_1..H_4, E_2del{1,2,3}_p, E_del1_del2_pp, E_del1_del3_pp, E_del2_del3_pp, E_2del{1,2,3}_m, E_del1_del2_mm, E_del1_del3_mm, E_del2_del3_mm, E_del1_del2_pm, E_del1_del3_pm, E_del2_del3_pm, E_del1_del2_mp, E_del1_del3_mp, E_del2_del3_mp` (22).

Normalisation choice: $E_{\pm 2\delta_k}=\tfrac12(b_k^{\pm})^2$ for **all** $k$ (the simple-root line of
`Cn1_definition.md` uses this factor; the root list there omits it). With this factor
$[E_{2\delta_n},E_{-2\delta_n}]=H_{n+1}$ exactly.

Parity table: the odd labels have parity 1, all other labels parity 0.

## 4. PBW ordering (decision)

Options considered:

- **(A) Odd-first, B-schema even order** — $\kappa < [\text{odd}] < [\text{even}]$, the even part in the
  order $H$, $E_{2\delta_k}^{+}$, $E^{++}$, $E_{2\delta_k}^{-}$, $E^{--}$, $E^{+-}$, $E^{-+}$ (the order used in
  `B0n_schema_v5.md`). Odd part ordered by $k$, then $pp, pm, mp, mm$.
- (B) Even-first: $H$ first, then odd, then root vectors. Same algebra, different list order.
- (C) Height ordering by the $\varepsilon$-grading: $\varepsilon$-positive odd roots before $\varepsilon$-negative,
  then even. Would reorder the odd block but needs the same normal-ordering rule.

**Chosen: (A).** Reasons: (i) it is the only option that keeps the B(0,n) schema ordering rule
($\kappa<[\text{odd}]<[\text{even}]$) so the B and C schemas can be compared position by position;
(ii) the structure constants are independent of this choice (it only permutes the basis), so the choice
affects labelling and presentation only; (iii) it matches the normal-ordering rule above, so the
oscillator words in Schema 1 are already in PBW form.

## 5. Central element $K$ and the $\kappa$-components

Non-trivial fact found when computing brackets: normal ordering of $b_k^- b_k^+ = b_k^+ b_k^- + 1$ and the
deformation rule produce a $\kappa\cdot K$ term, $K=1$ the scalar identity. Such terms occur in
brackets of an odd element with an even element (parity $p(X)+p(Y)+1=0$, consistent with $K$ even).
Convention: $\gamma(X,Y)$ is the **$\mathfrak g$-valued** part; the $K$-component is recorded separately
as `gamma_K`. $K$ is not a basis element (as in the B(0,n) schema).

## 6. Deformation parameters

- `gb_matrix` has rows $\sigma\in\{+,-\}$ (fermion $a_1^\sigma$) and columns $(j,s)$, $j=1..n$,
  $s\in\{+,-\}$ (boson $b_j^s$). Size $2\times 2n$, i.e. $4n$ parameters.
- Labels: `gb_a1p_b{j}p` means $\mathrm{gb}_{a_1^+,b_j^+}$, and similarly `gb_a1p_b{j}m`, `gb_a1m_b{j}p`,
  `gb_a1m_b{j}m`.
- Parity of $\mathrm{gb}$: see Ambiguity A1.

## 7. Bracket and sign conventions

- Graded commutator: $[X,Y]=XY-(-1)^{p(X)p(Y)}YX$.
- Structure constants: $[X_a,X_b]=\sum_c C_{ab}^{c}X_c$ (kappa-free), and
  $[X_a,X_b]_\gamma=[X_a,X_b]_0+\kappa\sum_{\mathrm{gb}}\mathrm{gb}\cdot\gamma_{ab}^{c}X_c$ plus the $K$-part.
- Coboundary (`C_coboundary_definition.md`): $(\delta f)(X,Y)=(-1)^{p(X)}[X,f(Y)]-(-1)^{(p(X)+1)p(Y)}[Y,f(X)]-f([X,Y])$.
  This is super-antisymmetric (checked in I07).
- Triviality: $\gamma\in\operatorname{Im}\delta$ on odd $f$; the set of trivial $\mathrm{gb}$ is a linear subspace.

## 8. Ambiguities and decisions

- **A1 (parity of gb).** `C_inhomogeneous_definition.md` states $p(\mathrm{gb})=1$, but the relation
  $[b,a]=-\mathrm{gb}\,\kappa$ has odd left side and $\kappa$ is odd, so $\mathrm{gb}$ must be even for consistency.
  Decision: treat $\mathrm{gb}$ as commuting scalars (parity 0). This is the convention used for all
  signs. The JSON records parity 0 for gb. Consequence: $\gamma(X,Y)$ has parity $p(X)+p(Y)+1$ regardless.
- **A2 (normalisation of $E_{\pm2\delta_k}$).** Use $\tfrac12(b_k^{\pm})^2$ for all $k$ (see §3).
- **A3 (ordering of odd elements).** The root list uses $a^{\sigma}b^{s}$. The simple-root line uses
  $b_1^{+}a^{-}$ for $E_{\delta_1-\varepsilon}$. Decision: $a^{\sigma}b^{s}$ throughout. Reordering
  differs from the original element by a multiple of $\kappa K$ (central), so only the $K$-component of
  $\gamma$ can change. The $\mathfrak g$-valued $\gamma$ and its triviality are unchanged.
- **A4 (K-component).** Recorded separately, see §5.
- **A5 (super-centrality of $\kappa$).** $\kappa$ is odd, so "central" must mean super-central: it anticommutes
  with the odd oscillators $a^{\pm}$. A first version treated $\kappa$ as commuting with everything. The engine was then
  non-associative (104 of 512 triple products failed for $n=1$). The Leibniz rule on $\{a^-,a^+\}=1$ requires
  $[b,a^-a^+ + a^+a^-]=0$, which holds only if $\kappa a^\pm=-a^\pm\kappa$. This is the fix, verified by
  associativity (0 failures) and by the super-Jacobi identity in the algebra (0 failures).
- **A7 (side of $\kappa$ in $\gamma$).** The doc writes $[X,Y]_\gamma=[X,Y]_0+\kappa\,\gamma(X,Y)$, with $\kappa$ on the left.
  Internally the engine writes $\kappa$ at the right end, which changes $\gamma$ by $(-1)^{p(X)+p(Y)+1}$. The exported $\gamma$ is the
  left convention. Check: in that convention the cocycle condition holds with 0 failures. In the right convention it fails
  (462 for $n=1$), which confirms the choice.
- **A6 (cocycle check).** The sign rules for passing the odd $\kappa$ through elements are error-prone. The cocycle
  condition is therefore checked directly as the super-Jacobi defect in the associative algebra, not from a hand formula.
