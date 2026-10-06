# Notation and Terminology

This document defines the mathematical notation and terminology used in this repository.
It was initialized during the $C(n+1)$ schema extension project and finalized in Issue I01.

## Conventions

### Algebra and rank
- $C(n+1) = \mathfrak{osp}(2|2n)$; `n` is the **bosonic rank** (number of bosonic oscillator pairs).
  $C(2)$, $C(3)$, $C(4)$ correspond to $n = 1, 2, 3$ (file names use `n`, e.g. `C_1_structure.json` = $C(2)$).
- $\dim \mathfrak{g} = (2n^2+n+1) \mid 4n$.

| n | algebra | even | odd | total |
|---|---|---|---|---|
| 1 | C(2) = osp(2\|2) | 4 | 4 | 8 |
| 2 | C(3) = osp(2\|4) | 11 | 8 | 19 |
| 3 | C(4) = osp(2\|6) | 22 | 12 | 34 |

### Oscillators (labels used in JSON and code)
| Symbol | Label | Parity | Relation |
|---|---|---|---|
| $a_1^+$, $a_1^-$ | `a_1_p`, `a_1_m` | 1 | CAR $\{a_1^-, a_1^+\} = 1$, $(a_1^\pm)^2 = 0$ |
| $b_k^+$, $b_k^-$ ($1 \le k \le n$) | `b_k_p`, `b_k_m` | 0 | CCR $[b_k^-, b_l^+] = \delta_{kl}$ |
| $\kappa$ | `kappa` | 1 | central, $\kappa^2 = 0$ |
| $K$ | `K` | 0 | central, identified with the scalar 1 |

Fermions and bosons commute (undeformed): $[b_k^\pm, a_1^\pm] = 0$.
The generators are **Weyl-symmetrized** quadratics, so no constant term other than the ones written
below ever appears (this is what makes the span of the basis closed with $K$ excluded).

### Basis generators (label ↔ oscillator realization)
Sign suffix: first letter = sign of $\varepsilon$ (`a_1_p`/`a_1_m`), second letter = sign of $\delta_k$ (`b_k_p`/`b_k_m`).

**Even (dim $2n^2+n+1$):**

| Root | Label | Realization |
|---|---|---|
| Cartan | `H_1` | $a_1^+a_1^- + b_1^+b_1^-$ |
| Cartan | `H_k`, $2\le k\le n$ | $b_{k-1}^+b_{k-1}^- - b_k^+b_k^-$ |
| Cartan | `H_{n+1}` | $-b_n^+b_n^- - \tfrac12$ |
| $2\delta_k$ | `E_2del{k}_p` | $\tfrac12 (b_k^+)^2$ |
| $-2\delta_k$ | `E_2del{k}_m` | $\tfrac12 (b_k^-)^2$ |
| $\delta_i+\delta_j$ ($i<j$) | `E_del{i}_del{j}_pp` | $b_i^+b_j^+$ |
| $\delta_i-\delta_j$ ($i<j$) | `E_del{i}_del{j}_pm` | $b_i^+b_j^-$ |
| $-\delta_i+\delta_j$ ($i<j$) | `E_del{i}_del{j}_mp` | $b_i^-b_j^+$ (normal ordered $b_j^+b_i^-$) |
| $-\delta_i-\delta_j$ ($i<j$) | `E_del{i}_del{j}_mm` | $b_i^-b_j^-$ |

(The $\tfrac12$ in `E_2del` follows `Cn1_definition.md` §2 simple generators; with it
$[E_{2\delta_n},E_{-2\delta_n}] = -H_{n+1}$ closes without a free constant. Note the table of
"all root generators" in `Cn1_definition.md` omits the $\tfrac12$; this is only a rescaling.)
Weyl symmetrization: $b^+b^-$ appears only through $b^+b^- + \tfrac12$ and $a^+a^- - \tfrac12$;
$H_1,\dots,H_{n+1}$ span exactly $\{a^+a^- - \tfrac12,\ b_k^+b_k^- + \tfrac12\}$.

**Odd (dim $4n$):**

| Root | Label | Realization |
|---|---|---|
| $\varepsilon+\delta_k$ | `E_eps1_del{k}_pp` | $a_1^+ b_k^+$ |
| $\varepsilon-\delta_k$ | `E_eps1_del{k}_pm` | $a_1^+ b_k^-$ |
| $-\varepsilon+\delta_k$ | `E_eps1_del{k}_mp` | $a_1^- b_k^+$ |
| $-\varepsilon-\delta_k$ | `E_eps1_del{k}_mm` | $a_1^- b_k^-$ |

### PBW ordering (decision from I01)
Options considered:
1. **odd < even**, odd sorted sign-major ($pp$ for all $k$, then $pm$, $mp$, $mm$), even sorted
   Cartan, positive even roots, negative even roots (extends the B(0,n) v5.0 convention $\kappa<\text{odd}<\text{even}$).
2. **even < odd** (reverse of B(0,n)).
3. **k-major interleaved** odd list ($pp,pm,mp,mm$ for $k=1$, then $k=2$, …) with odd < even.

**Chosen: option 1.** Reasons: backward compatibility with the B(0,n) v5.0 schema (the odd block comes
first and $p$-signs precede $m$-signs, as in `E_del1_p, E_del2_p, E_del1_m, E_del2_m`); the $\varepsilon$-roots
are grouped by the sign of $\varepsilon$ ($+\varepsilon$ block before $-\varepsilon$ block), which matches the
oscillator normal order $a_1^+$ before $a_1^-$; and it keeps index arithmetic simple (odd index $= 4$-block offset $+\,k-1$).

Full ordering: $\kappa <$ `E_eps1_del{k}_pp` ($k=1..n$) $<$ `_pm` $<$ `_mp` $<$ `_mm` $<$ `H_1..H_{n+1}`
$<$ `E_2del{k}_p` $<$ `E_del{i}_del{j}_pp` ($i<j$, lexicographic) $<$ `E_2del{k}_m` $<$ `E_del{i}_del{j}_mm`
$<$ `E_del{i}_del{j}_pm` $<$ `E_del{i}_del{j}_mp`. $K=1$ is excluded from basis lists.
Oscillator word ordering inside a realization: `a_1_p, a_1_m, b_1_p, b_1_m, …, b_n_p, b_n_m`
(normal ordering: $+$ to the left of $-$).

### Explicit basis lists
- **C(2), n=1** — even: `H_1 H_2 E_2del1_p E_2del1_m`; odd: `E_eps1_del1_pp E_eps1_del1_pm E_eps1_del1_mp E_eps1_del1_mm`.
- **C(3), n=2** — even (11): `H_1 H_2 H_3 E_2del1_p E_2del2_p E_del1_del2_pp E_2del1_m E_2del2_m E_del1_del2_mm E_del1_del2_pm E_del1_del2_mp`;
  odd (8): `E_eps1_del{1,2}_{pp,pm,mp,mm}` in the sign-major order above.
- **C(4), n=3** — even (22): `H_1..H_4`, `E_2del{1,2,3}_p`, `E_del{12,13,23}_pp`, `E_2del{1,2,3}_m`, `E_del{12,13,23}_mm`,
  `E_del{12,13,23}_pm`, `E_del{12,13,23}_mp`; odd (12): `E_eps1_del{1,2,3}_{pp,pm,mp,mm}`.
  (Generated programmatically by `src/C_generators.py::build_basis`.)

### Deformation parameters
`gb_{σ,j,s}` (σ ∈ {a_1_p,a_1_m}, s ∈ {p,m}) enters via $[b_j^s, a_1^\sigma] = -\mathrm{gb}_{\sigma,j,s}\,\kappa$.
Symbol names in JSON: `gb_a_1_p_b_1_p`, `gb_a_1_p_b_1_m`, … ($4n$ total). They are treated as
numerical scalars multiplying the formal odd nilpotent $\kappa$ (see I05 response for the parity discussion).

### Bracket conventions
Graded bracket $[X,Y\} = XY - (-1)^{p(X)p(Y)}YX$ in the oscillator algebra. Structure constants:
$[X,Y\} = \sum_Z c_{XY}^Z Z$, stored for **all ordered pairs** $(X,Y)$ with nonzero result.
