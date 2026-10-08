# Notation and Terminology

This document defines the mathematical notation and terminology used in this repository.
It is initialized during the $C(n+1)$ schema extension project.

## Conventions

### Algebra and rank

- $C(n+1) = \mathfrak{osp}(2|2n)$, bosonic rank $n$ (so $C(2)$ has $n=1$, $C(3)$ has $n=2$, $C(4)$ has $n=3$).
- Dimensions: even $= 2n^2+n+1$, odd $= 4n$, total $= 2n^2+5n+1$.

| $n$ | algebra | even | odd | total |
|---|---|---|---|---|
| 1 | C(2) | 4 | 4 | 8 |
| 2 | C(3) | 11 | 8 | 19 |
| 3 | C(4) | 22 | 12 | 34 |

### Oscillators

- Standard fermionic pair $a_1^\pm$: $\{a_1^-, a_1^+\} = 1$, parity 1. Labels `a_1_p`, `a_1_m`.
- Bosonic oscillators $b_k^\pm$, $k=1,\dots,n$: $[b_k^-, b_l^+] = \delta_{kl}$. Labels `b_{k}_p`, `b_{k}_m`.
- Odd central element $\kappa$ (parity 1, $\kappa^2=0$) and even central element $K$ (identified with 1; excluded from the basis).

### Even basis (dimension $2n^2+n+1$)

The even part is $\mathfrak{so}(2)\oplus\mathfrak{sp}(2n)$.

| Group | Labels | Count |
|---|---|---|
| $\mathfrak{so}(2)$ | `H_eps` | 1 |
| Cartan of $\mathfrak{sp}(2n)$ | `H_1`, ..., `H_n` | $n$ |
| Positive $2\delta_k$ | `E_2del{k}_p` | $n$ |
| Negative $-2\delta_k$ | `E_2del{k}_m` | $n$ |
| $\delta_i+\delta_j$, $i<j$ | `E_del{i}_del{j}_pp` | $\binom{n}{2}$ |
| $\delta_i-\delta_j$, $i<j$ | `E_del{i}_del{j}_pm` | $\binom{n}{2}$ |
| $-(\delta_i-\delta_j)$, $i<j$ | `E_del{i}_del{j}_mp` | $\binom{n}{2}$ |
| $-(\delta_i+\delta_j)$, $i<j$ | `E_del{i}_del{j}_mm` | $\binom{n}{2}$ |

Count check: $1 + n + 2n + 4\binom{n}{2} = 1 + 3n + 2n(n-1) = 2n^2+n+1$. For $n=1$: 4; $n=2$: 11; $n=3$: 22.

Here `H_eps` is the $\mathfrak{so}(2)$ generator $N_a = a_1^+a_1^-$ (number operator of the fermion pair), so that the $\mathfrak{so}(2)$ factor acts only on the fermionic sector.

### Odd basis (dimension $4n$)

| Root | Label | Oscillator realization |
|---|---|---|
| $\varepsilon+\delta_k$ | `E_eps1_del{k}_pp` | $a_1^+ b_k^+$ |
| $\varepsilon-\delta_k$ | `E_eps1_del{k}_pm` | $a_1^+ b_k^-$ |
| $-\varepsilon+\delta_k$ | `E_eps1_del{k}_mp` | $a_1^- b_k^+$ |
| $-\varepsilon-\delta_k$ | `E_eps1_del{k}_mm` | $a_1^- b_k^-$ |

Count: $4n$ (for $n=1,2,3$: 4, 8, 12).

### Full basis lists

- $C(2)$, $n=1$: even `[H_eps, H_1, E_2del1_p, E_2del1_m]`, odd `[E_eps1_del1_pp, E_eps1_del1_pm, E_eps1_del1_mp, E_eps1_del1_mm]`.
- $C(3)$, $n=2$: even `[H_eps, H_1, H_2, E_2del1_p, E_2del2_p, E_2del1_m, E_2del2_m, E_del1_del2_pp, E_del1_del2_pm, E_del1_del2_mp, E_del1_del2_mm]`, odd = 8 labels `E_eps1_del{k}_{pp,pm,mp,mm}` for $k=1,2$.
- $C(4)$, $n=3$: even has 22 labels (1 + 3 + 6 + 3·4 = 22), odd has 12 labels.

The generated lists are the authoritative form; the human-readable tables above are the reference.

### Simple roots and Cartan (Frappat convention)

Simple roots: $\alpha_1 = \varepsilon - \delta_1$, $\alpha_k = \delta_{k-1}-\delta_k$ ($2\le k\le n$), $\alpha_{n+1} = 2\delta_n$. Cartan generators are the diagonal ones; `H_eps` is the $\mathfrak{so}(2)$ factor.

## PBW ordering (decided in I01)

### Options considered

1. **Odd-first**: $\text{odd} < \text{even}$, within even by $(\mathfrak{so}(2), \mathfrak{sp}(2n)$ Cartan, positive, mixed, negative$)$. This mirrors the B(0,n) convention `κ < [odd] < [even]` in `docs/math/B0n_schema_v5.md`.
2. **Even-first**: $\text{even} < \text{odd}$. Puts the $\mathfrak{g}_{\bar 0}$ block first, so the PBW monomials of $U(\mathfrak{g}_{\bar 0})$ are leftmost. Standard in some references, but it breaks the parallel with B(0,n).
3. **Root-height ordering** within the total algebra: ordering by height of the root with respect to $\alpha_1,\dots,\alpha_{n+1}$. This is canonical, but the fermionic roots $\pm\varepsilon\pm\delta_k$ and bosonic $\pm\delta_i\pm\delta_j$ have mixed height, which makes the ordering depend on the simple system choice and complicates comparison across $n$.

### Decision

**Option 1 (odd-first)** is chosen. Reasons:
- It matches the B(0,n) PBW convention used by the reference schema, so the B(0,n) → C(n+1) diff in `B0n_schema_v5.md` stays local to the odd block.
- The odd block is exactly the set of $\pm\varepsilon\pm\delta_k$, so the ordering within it is the lexicographic order on $(k; pp, pm, mp, mm)$, independent of $n$.
- It keeps the even block ordered by type (so(2), Cartan, $2\delta$, mixed, $-2\delta$) in the same pattern as B(0,n).

Within the odd block: by $k$ ascending, then `pp < pm < mp < mm`.
Within the even block: `H_eps < H_1 < ... < H_n < E_2del{k}_p (k asc) < E_del{i}_del{j}_{pp,pm,mp} (i<j, lex) < E_2del{k}_m (k asc) < E_del{i}_del{j}_mm (lex)`.

The ordering is a total order on the basis labels, with the even block after the odd block. It is recorded in the `basis.ordering_convention` field of the schema.

## Ambiguities and assumptions

- **Sign of $\kappa$ and $K$**: $\kappa$ is odd and central, $K$ is even and identified with 1. Neither enters the basis lists.
- **$\mathfrak{so}(2)$ generator**: the choice $H_\varepsilon = a_1^+a_1^-$ (number operator) is an assumption. Any normalization differing by a constant gives an isomorphic result.
- **Simple roots**: $\alpha_1 = \varepsilon-\delta_1$ as the leftmost simple root is an assumption, consistent with the oscillator simple generator list in `docs/math/Cn1_definition.md`.
