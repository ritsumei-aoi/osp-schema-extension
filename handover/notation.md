# Notation and Terminology

This document defines the mathematical notation and terminology used in this repository.
Finalized during Issue I01-1 (2026-10-10) for the C(n+1) = osp(2|2n) schema extension project.

---

## 1. Algebra: C(n+1) = osp(2|2n)

**Root system** (Frappat et al. notation):
- Fermionic direction: ε (single)
- Bosonic directions: δ₁, …, δₙ
- Even roots Δ₀̄: { ±2δₖ } ∪ { ±(δᵢ ± δⱼ) | i < j }
- Odd roots Δ₁̄: { ±ε ± δₖ | k = 1, …, n }

**Dimensions**:
| n | Algebra | even | odd | total |
|---|---|---|---|---|
| 1 | C(2) = osp(2\|2) | 4 | 4 | 8 |
| 2 | C(3) = osp(2\|4) | 11 | 8 | 19 |
| 3 | C(4) = osp(2\|6) | 22 | 12 | 34 |

Formulas: even = 2n²+n+1, odd = 4n, total = 2n²+5n+1.

---

## 2. Oscillator Generators

**Fermionic pair** (standard CAR):
- Labels: `a_1_p` (= a₁⁺), `a_1_m` (= a₁⁻)
- Relation: {a₁⁻, a₁⁺} = 1, parity p(a₁±) = 1

**Bosonic oscillators** (CCR):
- Labels: `b_{k}_p` (= bₖ⁺), `b_{k}_m` (= bₖ⁻), k = 1, …, n
- Relation: [bₖ⁻, bₗ⁺] = δₖₗ, parity p(bₖ±) = 0

**Oscillator standard form ordering** (for PBW words):
```
a_1_p  <  a_1_m  <  b_1_p  <  b_1_m  <  b_2_p  <  b_2_m  <  …  <  b_n_p  <  b_n_m
```

**Central elements**:
- K: even (p=0), identified with scalar 1 in all current applications; not an independent basis element.
- κ: odd (p=1), nilpotent κ²=0; plays the role of the odd extension element (analogous to B(0,n)).

---

## 3. Generator Labels and Oscillator Realizations

### Even generators

| Root | Label | Oscillator realization |
|---|---|---|
| (Cartan) | `H_{k}` (k=1,…,n+1) | see Cn1_definition.md |
| 2δₖ | `E_2del{k}_p` | (1/2)(bₖ⁺)² |
| −2δₖ | `E_2del{k}_m` | (1/2)(bₖ⁻)² |
| δᵢ+δⱼ (i<j) | `E_del{i}_del{j}_pp` | bᵢ⁺ bⱼ⁺ |
| δᵢ−δⱼ (i<j) | `E_del{i}_del{j}_pm` | bᵢ⁺ bⱼ⁻ |
| −δᵢ+δⱼ (i<j) | `E_del{i}_del{j}_mp` | bᵢ⁻ bⱼ⁺ |
| −(δᵢ+δⱼ) (i<j) | `E_del{i}_del{j}_mm` | bᵢ⁻ bⱼ⁻ |

### Odd generators

| Root | Label | Oscillator realization |
|---|---|---|
| ε+δₖ | `E_eps1_del{k}_pp` | a₁⁺ bₖ⁺ |
| ε−δₖ | `E_eps1_del{k}_pm` | a₁⁺ bₖ⁻ |
| −ε+δₖ | `E_eps1_del{k}_mp` | a₁⁻ bₖ⁺ |
| −ε−δₖ | `E_eps1_del{k}_mm` | a₁⁻ bₖ⁻ |

The subscript `eps1` identifies the unique ε direction; `del{k}` identifies the k-th bosonic direction.
The two-character suffix encodes the signs: first character = sign of ε (p=plus, m=minus), second = sign of δₖ.

---

## 4. PBW Ordering (Option A: ε-grouped)

**Approved**: 2026-10-10, Issue I01-1.

The full PBW order on the basis of g = C(n+1) is:

```
[odd, +ε, +δ]  <  [odd, +ε, −δ]  <  [odd, −ε, +δ]  <  [odd, −ε, −δ]  <  [even]
```

Concretely:

```
E_eps1_del1_pp < E_eps1_del2_pp < … < E_eps1_del{n}_pp
< E_eps1_del1_pm < E_eps1_del2_pm < … < E_eps1_del{n}_pm
< E_eps1_del1_mp < E_eps1_del2_mp < … < E_eps1_del{n}_mp
< E_eps1_del1_mm < E_eps1_del2_mm < … < E_eps1_del{n}_mm
< H_1 < H_2 < … < H_{n+1}
< E_2del1_p < … < E_2del{n}_p  < E_del{i}_del{j}_pp  (i<j, ascending)
< E_2del1_m < … < E_2del{n}_m  < E_del{i}_del{j}_mm  (i<j, ascending)
< E_del{i}_del{j}_pm  (i<j, ascending)
< E_del{i}_del{j}_mp  (i<j, ascending)
```

Note: κ and K are not listed as independent basis elements (κ is the formal extension symbol; K = 1 scalar).

### Concrete basis lists (JSON schema format)

#### C(2), n=1

```json
{
  "odd":  ["E_eps1_del1_pp", "E_eps1_del1_pm", "E_eps1_del1_mp", "E_eps1_del1_mm"],
  "even": ["H_1", "H_2", "E_2del1_p", "E_2del1_m"]
}
```

#### C(3), n=2

```json
{
  "odd":  [
    "E_eps1_del1_pp", "E_eps1_del2_pp",
    "E_eps1_del1_pm", "E_eps1_del2_pm",
    "E_eps1_del1_mp", "E_eps1_del2_mp",
    "E_eps1_del1_mm", "E_eps1_del2_mm"
  ],
  "even": [
    "H_1", "H_2", "H_3",
    "E_2del1_p", "E_2del2_p", "E_del1_del2_pp",
    "E_2del1_m", "E_2del2_m", "E_del1_del2_mm",
    "E_del1_del2_pm", "E_del1_del2_mp"
  ]
}
```

#### C(4), n=3

```json
{
  "odd":  [
    "E_eps1_del1_pp", "E_eps1_del2_pp", "E_eps1_del3_pp",
    "E_eps1_del1_pm", "E_eps1_del2_pm", "E_eps1_del3_pm",
    "E_eps1_del1_mp", "E_eps1_del2_mp", "E_eps1_del3_mp",
    "E_eps1_del1_mm", "E_eps1_del2_mm", "E_eps1_del3_mm"
  ],
  "even": [
    "H_1", "H_2", "H_3", "H_4",
    "E_2del1_p", "E_2del2_p", "E_2del3_p",
    "E_del1_del2_pp", "E_del1_del3_pp", "E_del2_del3_pp",
    "E_2del1_m", "E_2del2_m", "E_2del3_m",
    "E_del1_del2_mm", "E_del1_del3_mm", "E_del2_del3_mm",
    "E_del1_del2_pm", "E_del1_del3_pm", "E_del2_del3_pm",
    "E_del1_del2_mp", "E_del1_del3_mp", "E_del2_del3_mp"
  ]
}
```

---

## 5. Deformation Parameters (gb)

The inhomogeneous deformation of C(n+1) introduces 4n parity-1 parameters:
```
gb_{a_1^+, b_j^+},  gb_{a_1^+, b_j^-},  gb_{a_1^-, b_j^+},  gb_{a_1^-, b_j^-}
  for j = 1, …, n
```

These parametrize the deformed oscillator exchange relations:
```
[b_j^s, a_1^σ] = −gb_{σ,j,s} · κ
```

---

## 6. Comparison with B(0,n)

| Property | B(0,n) = osp(1\|2n) | C(n+1) = osp(2\|2n) |
|---|---|---|
| Fermionic oscillator | `a_0` (supplementary, a₀²=1/2) | `a_1_p`, `a_1_m` (standard CAR pair) |
| Odd root form | ±δₖ (2n roots) | ±ε±δₖ (4n roots) |
| Odd generator labels | `E_del{k}_p/m` | `E_eps1_del{k}_pp/pm/mp/mm` |
| Cartan rank | n | n+1 |
| Even subalgebra | sp(2n) | so(2) × sp(2n) |
| gb parameters | 2n | 4n |
