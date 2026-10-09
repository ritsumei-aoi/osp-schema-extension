# Notation and Terminology

This document defines the mathematical notation and terminology used in this repository.
It covers the C(n+1) = osp(2|2n) schema extension project.

---

## 1. Algebra Families

| Symbol | Full name | Oscillator fermions | Odd rank |
|---|---|---|---|
| B(0,n) | osp(1\|2n) | Supplementary fermion a_0, a_0^2=1/2 | n |
| C(n+1) | osp(2\|2n) | Standard pair a_1^+, a_1^-, {a_1^-,a_1^+}=1 | 4n |

---

## 2. Oscillator Labels

| Symbol | Label | Parity | Relations |
|---|---|---|---|
| a_1^+ | `a_1_p` | 1 | CAR with a_1^- |
| a_1^- | `a_1_m` | 1 | {a_1^-, a_1^+} = 1 |
| b_k^+ | `b_{k}_p` | 0 | CCR: [b_k^-, b_l^+] = δ_{kl} |
| b_k^- | `b_{k}_m` | 0 | CCR |
| κ | `kappa` | 1 | odd central, κ^2=0 |
| K | `K` | 0 | even central, identified with scalar 1 |

---

## 3. Generator Labels for C(n+1)

### Even generators (parity 0)

| Root | Generator label | Oscillator realization |
|---|---|---|
| Cartan H_k (k=1,...,n+1) | `H_{k}` | see Cn1_definition.md |
| 2δ_k | `E_2del{k}_p` | (b_k^+)^2 |
| -2δ_k | `E_2del{k}_m` | (b_k^-)^2 |
| δ_i + δ_j (i<j) | `E_del{i}_del{j}_pp` | b_i^+ b_j^+ |
| -(δ_i + δ_j) (i<j) | `E_del{i}_del{j}_mm` | b_i^- b_j^- |
| δ_i - δ_j (i<j) | `E_del{i}_del{j}_pm` | b_i^+ b_j^- |
| -(δ_i - δ_j) (i<j) | `E_del{i}_del{j}_mp` | b_i^- b_j^+ |

### Odd generators (parity 1)

| Root | Generator label | Oscillator realization |
|---|---|---|
| ε + δ_k | `E_eps1_del{k}_pp` | a_1^+ b_k^+ |
| ε - δ_k | `E_eps1_del{k}_pm` | a_1^+ b_k^- |
| -ε + δ_k | `E_eps1_del{k}_mp` | a_1^- b_k^+ |
| -ε - δ_k | `E_eps1_del{k}_mm` | a_1^- b_k^- |

---

## 4. Basis Lists by n

### n=1 (C(2) = osp(2|2)), dim = 4|4

Even basis (4 elements):
`H_1, H_2, E_2del1_p, E_2del1_m`

Odd basis (4 elements):
`E_eps1_del1_pp, E_eps1_del1_pm, E_eps1_del1_mp, E_eps1_del1_mm`

### n=2 (C(3) = osp(2|4)), dim = 11|8

Even basis (11 elements):
`H_1, H_2, H_3, E_2del1_p, E_2del2_p, E_del1_del2_pp, E_2del1_m, E_2del2_m, E_del1_del2_mm, E_del1_del2_pm, E_del1_del2_mp`

Odd basis (8 elements):
`E_eps1_del1_pp, E_eps1_del2_pp, E_eps1_del1_pm, E_eps1_del2_pm, E_eps1_del1_mp, E_eps1_del2_mp, E_eps1_del1_mm, E_eps1_del2_mm`

### n=3 (C(4) = osp(2|6)), dim = 22|12

Even basis (22 elements):
`H_1, H_2, H_3, H_4, E_2del1_p, E_2del2_p, E_2del3_p, E_del1_del2_pp, E_del1_del3_pp, E_del2_del3_pp, E_2del1_m, E_2del2_m, E_2del3_m, E_del1_del2_mm, E_del1_del3_mm, E_del2_del3_mm, E_del1_del2_pm, E_del1_del3_pm, E_del2_del3_pm, E_del1_del2_mp, E_del1_del3_mp, E_del2_del3_mp`

Odd basis (12 elements):
`E_eps1_del1_pp, E_eps1_del2_pp, E_eps1_del3_pp, E_eps1_del1_pm, E_eps1_del2_pm, E_eps1_del3_pm, E_eps1_del1_mp, E_eps1_del2_mp, E_eps1_del3_mp, E_eps1_del1_mm, E_eps1_del2_mm, E_eps1_del3_mm`

---

## 5. PBW Ordering

**Decision**: κ < [odd generators] < [even generators]

**Options considered**:
1. κ < odd < even — consistent with B(0,n) convention; κ is the "lowest" symbol.
2. odd < even < κ — would require κ to commute through all elements, less conventional.

**Chosen**: Option 1. This matches the B(0,n) schema convention and keeps κ as the lowest PBW symbol, making extension of existing scripts straightforward.

Within odd: positive ε-component first (pp, pm), then negative ε-component (mp, mm); for each, index k=1,...,n.
Within even: Cartans (H_1,...,H_{n+1}), then positive roots (short to long), then negative roots.

Full PBW order for oscillators: `a_1_p, a_1_m, b_1_p, b_1_m, ..., b_n_p, b_n_m`

---

## 6. Dimension Formulas

**C(n+1) = osp(2|2n)**:
- even dim = 2n^2 + n + 1
- odd dim = 4n
- total = 2n^2 + 5n + 1

| n | even | odd | total |
|---|---|---|---|
| 1 | 4 | 4 | 8 |
| 2 | 11 | 8 | 19 |
| 3 | 22 | 12 | 34 |

---

## 7. Deformation Parameters (gb matrix)

For C(n+1), there are 4n deformation parameters:
`gb_{a_1^+, b_j^+}`, `gb_{a_1^+, b_j^-}`, `gb_{a_1^-, b_j^+}`, `gb_{a_1^-, b_j^-}` for j=1,...,n.

JSON label format: `gb_p_j_p`, `gb_p_j_m`, `gb_m_j_p`, `gb_m_j_m` (first index = fermionic σ, second = bosonic j, third = bosonic sign s).
