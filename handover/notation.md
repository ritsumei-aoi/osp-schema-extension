# Notation and Terminology

This document defines the mathematical notation and terminology used in this repository.
It was initialized during the $C(n+1)$ schema extension project and finalized in Issue **I01**.

---

## 0. Scope

All conventions below apply to $C(n+1) = \mathfrak{osp}(2|2n)$ in its oscillator
realization, and are chosen to stay as close as possible to the existing
$B(0,n) = \mathfrak{osp}(1|2n)$ v5.0 schema (`docs/math/B0n_schema_v5.md`) so that
the two families can be processed by the same tooling.

**Rank convention.** Throughout this repository, `n` always denotes the **bosonic
rank** (the number of bosonic oscillator pairs $b_k^\pm$). The algebra
$C(n+1) = \mathfrak{osp}(2|2n)$ therefore has Cartan rank $n+1$, and
`n = 1` corresponds to $C(2) = \mathfrak{osp}(2|2)$.

---

## 1. Oscillator generators and labels

| Object | Math symbol | Label (JSON / code) | Parity |
|---|---|---|---|
| Fermionic creation | $a_1^+$ | `a_1_p` | 1 |
| Fermionic annihilation | $a_1^-$ | `a_1_m` | 1 |
| Bosonic creation | $b_k^+$ | `b_{k}_p` | 0 |
| Bosonic annihilation | $b_k^-$ | `b_{k}_m` | 0 |
| Odd central element | $\kappa$ | `kappa` | 1 |
| Even central element | $K$ | `K` | 0 |

Relations (undeformed):

$$\{a_1^-, a_1^+\} = 1,\qquad (a_1^\pm)^2 = 0,\qquad
[b_k^-, b_l^+] = \delta_{kl},\qquad [b_k^s, a_1^\sigma] = 0 .$$

$\kappa$ is **odd** and supercentral ($\kappa X = (-1)^{p(X)}X\kappa$) with $\kappa^2 = 0$;
$K$ is identified with the scalar $1$ and is **not** a PBW basis element (same
convention as the $B(0,n)$ v5.0 schema).

**Suffix grammar for labels.** A trailing `_p` / `_m` always denotes the sign
$+$ / $-$ of the corresponding oscillator, read **left to right in the same order
as the oscillator word**. E.g. `E_eps1_del2_pm` $= a_1^+ b_2^-$: the first suffix
letter is the sign of the $\varepsilon$ (fermionic) factor, the second is the sign
of the $\delta$ (bosonic) factor.

---

## 2. Root system and generator labels

Roots are written in the orthogonal basis $\{\varepsilon; \delta_1,\dots,\delta_n\}$:

$$\Delta_{\bar 0} = \{\pm 2\delta_k\} \cup \{\pm(\delta_i \pm \delta_j)\mid i<j\},
\qquad
\Delta_{\bar 1} = \{\pm\varepsilon \pm \delta_k\}.$$

### 2.1 Even generators

| Root / element | Label | Oscillator realization |
|---|---|---|
| $\varepsilon$-Cartan (so(2)) | `H_eps1` | $a_1^+a_1^- - \tfrac12$ |
| $\delta_k$-Cartan (sp(2n)) | `H_del{k}` | $b_k^+b_k^- + \tfrac12$ |
| $2\delta_k$ | `E_2del{k}_p` | $(b_k^+)^2$ |
| $-2\delta_k$ | `E_2del{k}_m` | $(b_k^-)^2$ |
| $\delta_i+\delta_j$ ($i<j$) | `E_del{i}_del{j}_pp` | $b_i^+b_j^+$ |
| $-(\delta_i+\delta_j)$ ($i<j$) | `E_del{i}_del{j}_mm` | $b_i^-b_j^-$ |
| $\delta_i-\delta_j$ ($i<j$) | `E_del{i}_del{j}_pm` | $b_i^+b_j^-$ |
| $-(\delta_i-\delta_j)$ ($i<j$) | `E_del{i}_del{j}_mp` | $b_i^-b_j^+$ |

Count: $1 + n + 2n + 4\binom{n}{2} = 2n^2 + n + 1$. &check;

> **Symmetrized Cartan convention (decision).** `H_eps1` and `H_del{k}` are the
> *symmetrized* number operators
> $\tfrac12[a_1^+,a_1^-]_{\text{(anti)}}\!=a_1^+a_1^--\tfrac12$ and
> $\tfrac12\{b_k^+,b_k^-\}=b_k^+b_k^-+\tfrac12$.
> This is the only normalization for which the even span closes **without** a
> residual multiple of $K$: e.g. $[(b_k^+)^2,(b_k^-)^2] = -4\,$`H_del{k}` exactly,
> and $\{a_1^+b_k^+,\,a_1^-b_k^-\} = $ `H_del{k}` $-$ `H_eps1` exactly.
> With the naive choice $a_1^+a_1^-$, $b_k^+b_k^-$ a spurious $\tfrac12 K$ term appears.
> The $\mp\tfrac12$ shifts agree with Frappat's $H_{n+1} = -b_n^+b_n^- - \tfrac12$
> up to sign (`docs/math/Cn1_definition.md` §2).

### 2.2 Odd generators

| Root | Label | Oscillator realization |
|---|---|---|
| $\varepsilon+\delta_k$ | `E_eps1_del{k}_pp` | $a_1^+ b_k^+$ |
| $\varepsilon-\delta_k$ | `E_eps1_del{k}_pm` | $a_1^+ b_k^-$ |
| $-\varepsilon+\delta_k$ | `E_eps1_del{k}_mp` | $a_1^- b_k^+$ |
| $-\varepsilon-\delta_k$ | `E_eps1_del{k}_mm` | $a_1^- b_k^-$ |

Count: $4n$. &check;

---

## 3. Explicit basis lists

### 3.1 $n=1$ — $C(2)=\mathfrak{osp}(2|2)$, $\dim = 4\,|\,4 = 8$

```
even (4): H_eps1, H_del1, E_2del1_p, E_2del1_m
odd  (4): E_eps1_del1_pp, E_eps1_del1_pm, E_eps1_del1_mp, E_eps1_del1_mm
```

### 3.2 $n=2$ — $C(3)=\mathfrak{osp}(2|4)$, $\dim = 11\,|\,8 = 19$

```
even (11): H_eps1, H_del1, H_del2,
           E_2del1_p, E_2del2_p, E_del1_del2_pp,
           E_2del1_m, E_2del2_m, E_del1_del2_mm,
           E_del1_del2_pm, E_del1_del2_mp
odd   (8): E_eps1_del1_pp, E_eps1_del1_pm, E_eps1_del1_mp, E_eps1_del1_mm,
           E_eps1_del2_pp, E_eps1_del2_pm, E_eps1_del2_mp, E_eps1_del2_mm
```

### 3.3 $n=3$ — $C(4)=\mathfrak{osp}(2|6)$, $\dim = 22\,|\,12 = 34$

```
even (22): H_eps1, H_del1, H_del2, H_del3,
           E_2del1_p, E_2del2_p, E_2del3_p,
           E_del1_del2_pp, E_del1_del3_pp, E_del2_del3_pp,
           E_2del1_m, E_2del2_m, E_2del3_m,
           E_del1_del2_mm, E_del1_del3_mm, E_del2_del3_mm,
           E_del1_del2_pm, E_del1_del3_pm, E_del2_del3_pm,
           E_del1_del2_mp, E_del1_del3_mp, E_del2_del3_mp
odd  (12): E_eps1_del{k}_pp, E_eps1_del{k}_pm, E_eps1_del{k}_mp, E_eps1_del{k}_mm
           for k = 1, 2, 3   (grouped by k, in that suffix order)
```

Dimension formulas: even $=2n^2+n+1$, odd $=4n$, total $=2n^2+5n+1$.

---

## 4. PBW ordering

### 4.1 Options considered

**Option A — grade-first (inherited from $B(0,n)$ v5.0):**
```
kappa  <  [all odd generators]  <  [all even generators]
```

**Option B — triangular / root-height:**
```
kappa < [negative-root vectors] < [Cartan: H_eps1, H_del*] < [positive-root vectors]
```

**Option C — sector-first (fermionic sector before bosonic sector):**
```
kappa < H_eps1 < [odd: E_eps1_del*] < [even sp(2n) part]
```

### 4.2 Decision — **Option A**

Adopted ordering, in full:

```
kappa
  < E_eps1_del{k}_pp, _pm, _mp, _mm   (k = 1..n, outer loop k, inner loop pp,pm,mp,mm)
  < H_eps1, H_del1, ..., H_deln
  < E_2del{k}_p (k=1..n), E_del{i}_del{j}_pp (i<j, lex)
  < E_2del{k}_m (k=1..n), E_del{i}_del{j}_mm (i<j, lex)
  < E_del{i}_del{j}_pm (i<j, lex), E_del{i}_del{j}_mp (i<j, lex)
```

**Justification.**
1. *Backward compatibility.* $B(0,n)$ v5.0 fixes `κ < [odd] < [even]` and lays the
   even block out as `H_*`, then `+`-type, then `−`-type, then mixed. Option A is
   the literal transcription of that layout to $C(n+1)$, so existing $B$ tooling,
   diff scripts and schema validators keep working. Options B and C would force a
   re-ordering of the $B$ files for comparability.
2. *Parity blocking.* Keeping all odd generators contiguous makes the
   parity-reversing map $f$ of Layer 4 a clean $2\times2$ block matrix
   (even$\to$odd and odd$\to$even blocks), which is exactly the structure the
   coboundary solver needs.
3. *Cost of rejecting B.* Option B is mathematically the most natural for
   highest-weight computations, but $C(n+1)$'s odd roots $\pm\varepsilon\pm\delta_k$
   straddle the positive/negative split in a way that depends on the choice of
   Borel; fixing one would add an arbitrary convention with no benefit here.
4. *Cost of rejecting C.* Option C separates `H_eps1` from the other Cartan
   elements, which complicates every Cartan-subalgebra loop in the code for no
   structural gain.

### 4.3 Oscillator-word ordering (normal ordering)

Inside oscillator words the letters are sorted by the index

```
kappa = 0 ,  a_1_p = 1 ,  a_1_m = 2 ,  b_k_p = 2k+1 ,  b_k_m = 2k+2
```

i.e. creation operators to the left of the matching annihilation operators,
fermions before bosons, $\kappa$ leftmost. This is the direct analogue of the
$B(0,n)$ ordering `a_0, b_1_p, b_1_m, ...`.

---

## 5. Deformation parameters

The inhomogeneous ($\gamma$) deformation is carried by the $4n$ parameters

$$\mathrm{gb}_{\sigma, k, s},\qquad \sigma\in\{+,-\},\ s\in\{+,-\},\ k=1,\dots,n,$$

labelled `gb_a1{P|M}_b{k}{P|M}` in JSON/code, defined by the deformed relation

$$[\,b_k^s,\ a_1^\sigma\,] = -\,\mathrm{gb}_{\sigma,k,s}\,\kappa .$$

See `docs/math/C_inhomogeneous_definition.md` and the parity discussion recorded
in the Response of Issue I05.

---

## 6. File naming

| Layer | File | Contents |
|---|---|---|
| 1 | `data/C_{n}_structure.json` | basis, parity, realization, structure constants |
| 2 | `data/C_{n}_gamma.json` | symbolic $\gamma$ (inhomogeneous deformation) |
| 3 | `data/C_{n}_evaluated_{profile}.json` | $\gamma$ with numeric gb |
| 4 | `data/C_{n}_coboundary.json` | $\delta f$ data for triviality testing |

`{n}` is the bosonic rank, so $C(2)$ &rarr; `C_1_structure.json`.
