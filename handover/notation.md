# Notation and Terminology

This document defines the mathematical notation and terminology used in this repository.
Finalized during Issue I01-1 (2026-10-11).

**Reference**: Frappat, Sciarrino, Sorba, *Dictionary on Lie Algebras and Superalgebras* (2000);
arXiv:hep-th/9607161.

---

## 1. Algebras

| Symbol | Cartan type | Alternative | Notes |
|---|---|---|---|
| B(0,n) | B(0,n) | osp(1\|2n) | Base case; see `docs/math/B0n_definition.md` |
| C(n+1) | C(n+1) | osp(2\|2n) | Extension case; see `docs/math/Cn1_definition.md` |

---

## 2. Root System Vectors

- **ε**: single fermionic orthogonal vector (C(n+1) only; parity 1)
- **δ_k** (k=1,…,n): bosonic orthogonal vectors (parity 0)

| Root type | Roots | Parity |
|---|---|---|
| Even Δ₀ | ±2δ_k, ±(δᵢ ± δⱼ) (i<j) | 0 |
| Odd Δ₁ | ±ε ± δ_k | 1 |

---

## 3. Oscillator Generators

### B(0,n)
- **Supplementary fermion**: `a_0`, parity 1, satisfying `a_0² = 1/2` (not a standard CAR pair)
- **Bosonic oscillators**: `b_k_p` = b_k⁺, `b_k_m` = b_k⁻ for k=1,…,n; CCR: [b_k⁻, b_l⁺] = δ_{kl}

### C(n+1)
- **Standard fermionic pair**: `a_1_p` = a₁⁺, `a_1_m` = a₁⁻; parity 1; CAR: {a₁⁻, a₁⁺} = 1
- **Bosonic oscillators**: `b_k_p` = b_k⁺, `b_k_m` = b_k⁻ for k=1,…,n; CCR: [b_k⁻, b_l⁺] = δ_{kl}

---

## 4. Generator Label Conventions

### 4.1 Even Generators (shared by B(0,n) and C(n+1))

| Root | JSON label | Oscillator realization |
|---|---|---|
| Cartan (simple root αₖ) | `H_{k}` (k=1,…,rank) | see §5 |
| +2δ_k | `E_2del{k}_p` | (1/2)(b_k⁺)² |
| −2δ_k | `E_2del{k}_m` | (1/2)(b_k⁻)² |
| δᵢ+δⱼ (i<j) | `E_del{i}_del{j}_pp` | b_i⁺ b_j⁺ |
| −(δᵢ+δⱼ) (i<j) | `E_del{i}_del{j}_mm` | b_i⁻ b_j⁻ |
| δᵢ−δⱼ (i<j) | `E_del{i}_del{j}_pm` | b_i⁺ b_j⁻ |
| −(δᵢ−δⱼ) (i<j) | `E_del{i}_del{j}_mp` | b_i⁻ b_j⁺ |

**Sign encoding**: the trailing `_pp/pm/mp/mm` reflects the signs of the two root components
(first sign = sign of the first vector, second sign = sign of the second vector; `p`=positive, `m`=negative).

### 4.2 Odd Generators

**B(0,n)** (2n generators, root = ±δ_k):

| Root | JSON label | Oscillator realization |
|---|---|---|
| +δ_k | `E_del{k}_p` | a_0 b_k⁺ |
| −δ_k | `E_del{k}_m` | a_0 b_k⁻ |

**C(n+1)** (4n generators, root = ±ε ± δ_k):

| Root | JSON label | Oscillator realization | Sign |
|---|---|---|---|
| ε + δ_k | `E_eps1_del{k}_pp` | a₁⁺ b_k⁺ | ε>0, δ>0 |
| ε − δ_k | `E_eps1_del{k}_pm` | a₁⁺ b_k⁻ | ε>0, δ<0 |
| −ε + δ_k | `E_eps1_del{k}_mp` | a₁⁻ b_k⁺ | ε<0, δ>0 |
| −ε − δ_k | `E_eps1_del{k}_mm` | a₁⁻ b_k⁻ | ε<0, δ<0 |

**Label anatomy**: `E_eps1_del{k}_{s_ε}{s_δ}`
- `eps1`: ε-direction, fermionic index 1 (= a₁)
- `del{k}`: δ_k direction, bosonic index k
- `{s_ε}{s_δ}`: sign pair (`p`=+, `m`=−) for (ε, δ_k) respectively

---

## 5. Cartan Generators

### B(0,n) (n Cartans: H_1,…,H_n)

| Generator | Realization |
|---|---|
| H_k (1≤k≤n−1) | b_k⁺ b_k⁻ − b_{k+1}⁺ b_{k+1}⁻ |
| H_n | b_n⁺ b_n⁻ + a_0² = b_n⁺ b_n⁻ + 1/2 |

### C(n+1) (n+1 Cartans: H_1,…,H_{n+1})

| Generator | Realization | Simple root |
|---|---|---|
| H_1 | a₁⁺ a₁⁻ + b₁⁺ b₁⁻ | α₁ = ε − δ₁ |
| H_k (2≤k≤n) | b_{k−1}⁺ b_{k−1}⁻ − b_k⁺ b_k⁻ | αₖ = δ_{k−1} − δ_k |
| H_{n+1} | −b_n⁺ b_n⁻ − 1/2 | α_{n+1} = 2δ_n |

---

## 6. PBW Ordering Convention

### Global order (both B(0,n) and C(n+1)):
```
κ  <  [odd block]  <  [even block]
```

### Even block ordering:
```
Cartans (H_1,…,H_rank)  <  positive-type (+/pp)  <  negative-type (−/mm)  <  mixed (pm, mp)
```

### Odd block ordering

**B(0,n)**: positive odd roots before negative odd roots, ordered by bosonic index:
```
E_del1_p, E_del2_p, …, E_deln_p,
E_del1_m, E_del2_m, …, E_deln_m
```

**C(n+1) — Option A (approved 2026-10-11)**: group by ε-sign (fermionic sector first),
then by bosonic sign, then by bosonic index k:
```
E_eps1_del1_pp, E_eps1_del2_pp, …, E_eps1_deln_pp,   [ε>0, δ>0]
E_eps1_del1_pm, E_eps1_del2_pm, …, E_eps1_deln_pm,   [ε>0, δ<0]
E_eps1_del1_mp, E_eps1_del2_mp, …, E_eps1_deln_mp,   [ε<0, δ>0]
E_eps1_del1_mm, E_eps1_del2_mm, …, E_eps1_deln_mm    [ε<0, δ<0]
```

**Rationale**: groups generators by which fermionic oscillator (a₁⁺ vs a₁⁻) they contain,
maintaining analogy with B(0,n)'s positive-before-negative convention.

---

## 7. Explicit Basis Lists

### C(2) = osp(2|2), n=1, dim = 4|4

**Even** (4): `H_1, H_2, E_2del1_p, E_2del1_m`

**Odd** (4): `E_eps1_del1_pp, E_eps1_del1_pm, E_eps1_del1_mp, E_eps1_del1_mm`

### C(3) = osp(2|4), n=2, dim = 11|8

**Even** (11):
```
H_1, H_2, H_3,
E_2del1_p, E_2del2_p, E_del1_del2_pp,
E_2del1_m, E_2del2_m, E_del1_del2_mm,
E_del1_del2_pm, E_del1_del2_mp
```

**Odd** (8):
```
E_eps1_del1_pp, E_eps1_del2_pp,
E_eps1_del1_pm, E_eps1_del2_pm,
E_eps1_del1_mp, E_eps1_del2_mp,
E_eps1_del1_mm, E_eps1_del2_mm
```

### C(4) = osp(2|6), n=3, dim = 22|12

**Even** (22):
```
H_1, H_2, H_3, H_4,
E_2del1_p, E_2del2_p, E_2del3_p,
E_del1_del2_pp, E_del1_del3_pp, E_del2_del3_pp,
E_2del1_m, E_2del2_m, E_2del3_m,
E_del1_del2_mm, E_del1_del3_mm, E_del2_del3_mm,
E_del1_del2_pm, E_del1_del3_pm, E_del2_del3_pm,
E_del1_del2_mp, E_del1_del3_mp, E_del2_del3_mp
```

**Odd** (12):
```
E_eps1_del1_pp, E_eps1_del2_pp, E_eps1_del3_pp,
E_eps1_del1_pm, E_eps1_del2_pm, E_eps1_del3_pm,
E_eps1_del1_mp, E_eps1_del2_mp, E_eps1_del3_mp,
E_eps1_del1_mm, E_eps1_del2_mm, E_eps1_del3_mm
```

---

## 8. Central Elements

| Symbol | JSON key | Parity | Description |
|---|---|---|---|
| K | `K` | 0 | Even central identity; identified with scalar 1 in all current applications; excluded from PBW basis |
| κ | `kappa` | 1 | Odd nilpotent central extension element (κ² = 0); smallest element in PBW ordering |

---

## 9. Dimension Formulas

| Algebra | even dim | odd dim | total |
|---|---|---|---|
| B(0,n) | 2n²+n | 2n | 2n²+3n |
| C(n+1) | 2n²+n+1 | 4n | 2n²+5n+1 |
