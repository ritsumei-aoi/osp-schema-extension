# Notation and Terminology

This document defines the mathematical notation and terminology used in this repository.
Finalized during Issue I01-1 (2026-10-06).

---

## 1. Algebra Family: C(n+1) = osp(2|2n)

This project studies $C(n+1) = \mathfrak{osp}(2|2n)$ for $n = 1, 2, 3$
(i.e., $C(2)$, $C(3)$, $C(4)$).

**Reference**: Frappat, Sciarrino, Sorba, *Dictionary on Lie Algebras and Superalgebras* (2000);
arXiv:hep-th/9607161.

---

## 2. Oscillator Generators

| Symbol | JSON label | Parity | Relation | Description |
|---|---|---|---|---|
| $a_1^+$ | `a_1_p` | 1 | $\{a_1^-, a_1^+\} = 1$ | Fermionic creation operator |
| $a_1^-$ | `a_1_m` | 1 | $\{a_1^-, a_1^+\} = 1$ | Fermionic annihilation operator |
| $b_k^+$ | `b_{k}_p` | 0 | $[b_k^-, b_l^+] = \delta_{kl}$ | Bosonic creation operator, $k = 1, \ldots, n$ |
| $b_k^-$ | `b_{k}_m` | 0 | $[b_k^-, b_l^+] = \delta_{kl}$ | Bosonic annihilation operator, $k = 1, \ldots, n$ |

Standard form (PBW) ordering of oscillator words:
```
a_1_p < a_1_m < b_1_p < b_1_m < b_2_p < b_2_m < ... < b_n_p < b_n_m
```

---

## 3. Lie Superalgebra Basis and Generator Labels

### 3.1 Cartan Elements

Rank of $C(n+1)$ is $n+1$. Simple root labeling follows Frappat:

| Label | Oscillator realization | Simple root | Parity |
|---|---|---|---|
| `H_1` | $a_1^+ a_1^- + b_1^+ b_1^-$ | $\alpha_1 = \varepsilon - \delta_1$ | 0 |
| `H_k` ($2 \leq k \leq n$) | $b_{k-1}^+ b_{k-1}^- - b_k^+ b_k^-$ | $\alpha_k = \delta_{k-1} - \delta_k$ | 0 |
| `H_{n+1}` | $-b_n^+ b_n^- - \tfrac{1}{2}$ | $\alpha_{n+1} = 2\delta_n$ | 0 |

### 3.2 Even Root Generators

The even root system is $\Delta_{\bar{0}} = \{\pm 2\delta_k\} \cup \{\pm(\delta_i \pm \delta_j) \mid i < j\}$.

Label convention: suffix `_p` = positive root, `_m` = negative root; `_pp/_mm/_pm/_mp` encodes the sign of the oscillator pair $(b_i^\sigma, b_j^\tau)$.

| Root | Generator label | Oscillator realization |
|---|---|---|
| $2\delta_k$ | `E_2del{k}_p` | $(b_k^+)^2$ |
| $-2\delta_k$ | `E_2del{k}_m` | $(b_k^-)^2$ |
| $\delta_i + \delta_j$ ($i < j$) | `E_del{i}_del{j}_pp` | $b_i^+ b_j^+$ |
| $-(\delta_i + \delta_j)$ ($i < j$) | `E_del{i}_del{j}_mm` | $b_i^- b_j^-$ |
| $\delta_i - \delta_j$ ($i < j$) | `E_del{i}_del{j}_pm` | $b_i^+ b_j^-$ |
| $-(\delta_i - \delta_j)$ ($i < j$) | `E_del{i}_del{j}_mp` | $b_i^- b_j^+$ |

### 3.3 Odd Root Generators

The odd root system is $\Delta_{\bar{1}} = \{\pm\varepsilon \pm \delta_k \mid k = 1, \ldots, n\}$ (total $4n$ roots).

Label convention: `E_eps1_del{k}_{ss}` where the suffix `ss` is a two-character sign pair
`(s_\varepsilon, s_\delta)` with `p` = positive, `m` = negative.

| Root | Generator label | Oscillator realization |
|---|---|---|
| $\varepsilon + \delta_k$ | `E_eps1_del{k}_pp` | $a_1^+ b_k^+$ |
| $\varepsilon - \delta_k$ | `E_eps1_del{k}_pm` | $a_1^+ b_k^-$ |
| $-\varepsilon + \delta_k$ | `E_eps1_del{k}_mp` | $a_1^- b_k^+$ |
| $-\varepsilon - \delta_k$ | `E_eps1_del{k}_mm` | $a_1^- b_k^-$ |

---

## 4. Even and Odd Basis Lists

### C(2) = osp(2|2), n=1 — dim = 4|4 = 8

**Even basis** (4 generators):
```
H_1, H_2,
E_2del1_p,
E_2del1_m
```

**Odd basis** (4 generators):
```
E_eps1_del1_pp, E_eps1_del1_pm,
E_eps1_del1_mp, E_eps1_del1_mm
```

### C(3) = osp(2|4), n=2 — dim = 11|8 = 19

**Even basis** (11 generators):
```
H_1, H_2, H_3,
E_2del1_p, E_2del2_p,
E_del1_del2_pp,
E_2del1_m, E_2del2_m,
E_del1_del2_mm,
E_del1_del2_pm, E_del1_del2_mp
```

**Odd basis** (8 generators):
```
E_eps1_del1_pp, E_eps1_del2_pp,
E_eps1_del1_pm, E_eps1_del2_pm,
E_eps1_del1_mp, E_eps1_del2_mp,
E_eps1_del1_mm, E_eps1_del2_mm
```

### C(4) = osp(2|6), n=3 — dim = 22|12 = 34

**Even basis** (22 generators):
```
H_1, H_2, H_3, H_4,
E_2del1_p, E_2del2_p, E_2del3_p,
E_del1_del2_pp, E_del1_del3_pp, E_del2_del3_pp,
E_2del1_m, E_2del2_m, E_2del3_m,
E_del1_del2_mm, E_del1_del3_mm, E_del2_del3_mm,
E_del1_del2_pm, E_del1_del3_pm, E_del2_del3_pm,
E_del1_del2_mp, E_del1_del3_mp, E_del2_del3_mp
```

**Odd basis** (12 generators):
```
E_eps1_del1_pp, E_eps1_del2_pp, E_eps1_del3_pp,
E_eps1_del1_pm, E_eps1_del2_pm, E_eps1_del3_pm,
E_eps1_del1_mp, E_eps1_del2_mp, E_eps1_del3_mp,
E_eps1_del1_mm, E_eps1_del2_mm, E_eps1_del3_mm
```

---

## 5. PBW Ordering Convention (Option A — ε-priority)

The global PBW order is: $\kappa < [\text{odd}] < [\text{even}]$.

**Within the odd sector**: generators are grouped first by $\varepsilon$ sign (fermionic creation/annihilation partition), then by $\delta$ sign:

```
(ε+, δ+) < (ε+, δ-) < (ε-, δ+) < (ε-, δ-)
```

In JSON label terms, the four blocks in order are: `_pp`, `_pm`, `_mp`, `_mm`.

**Within the even sector** (following B(0,n) convention):
```
Cartans (H_1..H_{n+1})
< positive symmetric (E_2del{k}_p, E_del{i}_del{j}_pp)
< negative symmetric (E_2del{k}_m, E_del{i}_del{j}_mm)
< mixed (E_del{i}_del{j}_pm, E_del{i}_del{j}_mp)
```

Full PBW ordering string notation:
```
κ < [odd: _pp block] < [odd: _pm block] < [odd: _mp block] < [odd: _mm block]
  < [even: H's] < [even: pos-sym] < [even: neg-sym] < [even: mixed]
```

---

## 6. Central Elements

| Symbol | JSON label | Parity | Property |
|---|---|---|---|
| $K$ | `K` | 0 (even) | Central identity; identified with scalar 1 in all applications; excluded from PBW basis |
| $\kappa$ | `kappa` | 1 (odd) | Nilpotent odd central element; $\kappa^2 = 0$; lowest in PBW order |

---

## 7. Deformation Parameters (gb)

The inhomogeneous deformation of $C(n+1)$ is parametrized by $4n$ odd-parity constants:

$$\{ \mathrm{gb}_{a_1^\sigma, b_j^s} \mid \sigma \in \{+,-\},\ s \in \{+,-\},\ j = 1, \ldots, n \}$$

JSON key format: `gb_a1{σ}_b{j}{s}` where `σ, s ∈ {p, m}`.

| n | Count | Parameters |
|---|---|---|
| 1 | 4 | `gb_a1p_b1p`, `gb_a1p_b1m`, `gb_a1m_b1p`, `gb_a1m_b1m` |
| 2 | 8 | above + `gb_a1{σ}_b2{s}` for all σ, s |
| 3 | 12 | above + `gb_a1{σ}_b3{s}` for all σ, s |
