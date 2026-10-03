# Notation and Terminology

This document defines the mathematical notation and terminology used in this repository
for the C(n+1) = osp(2|2n) schema extension project.

## 1. Algebras

| Symbol | Name | Oscillators |
|---|---|---|
| B(0,n) | osp(1\|2n) | Supplementary fermion a_0, bosons b_k^± |
| C(n+1) | osp(2\|2n) | Standard fermionic pair a_1^±, bosons b_k^± |

## 2. Oscillator Labels

### Fermionic oscillators
| Math symbol | JSON label | Parity | Relation |
|---|---|---|---|
| a_1^+ | `a_1_p` | 1 | {a_1^-, a_1^+} = 1 |
| a_1^- | `a_1_m` | 1 | CAR pair |

### Bosonic oscillators (k = 1, ..., n)
| Math symbol | JSON label | Parity | Relation |
|---|---|---|---|
| b_k^+ | `b_{k}_p` | 0 | [b_i^-, b_j^+] = δ_{ij} |
| b_k^- | `b_{k}_m` | 0 | CCR pair |

## 3. Generator Labels for C(n+1)

### Even generators
| Root / element | JSON label | Oscillator realization |
|---|---|---|
| H_k (k=1..n+1) | `H_{k}` | see Section 5 |
| 2δ_k | `E_2del{k}_p` | (b_k^+)^2 |
| -2δ_k | `E_2del{k}_m` | (b_k^-)^2 |
| δ_i + δ_j (i<j) | `E_del{i}_del{j}_pp` | b_i^+ b_j^+ |
| -(δ_i + δ_j) (i<j) | `E_del{i}_del{j}_mm` | b_i^- b_j^- |
| δ_i - δ_j (i<j) | `E_del{i}_del{j}_pm` | b_i^+ b_j^- |
| -(δ_i - δ_j) (i<j) | `E_del{i}_del{j}_mp` | b_i^- b_j^+ |

### Odd generators (ε-roots)
| Root | JSON label | Oscillator realization |
|---|---|---|
| ε + δ_k | `E_eps1_del{k}_pp` | a_1^+ b_k^+ |
| ε - δ_k | `E_eps1_del{k}_pm` | a_1^+ b_k^- |
| -ε + δ_k | `E_eps1_del{k}_mp` | a_1^- b_k^+ |
| -ε - δ_k | `E_eps1_del{k}_mm` | a_1^- b_k^- |

### Central elements
| Symbol | JSON label | Parity | Property |
|---|---|---|---|
| K | `K` | 0 (even) | Identity; K=1 in all realizations; excluded from basis |
| κ | `kappa` | 1 (odd) | Nilpotent: κ^2 = 0; appears in deformed bracket |

## 4. PBW Ordering

Two options considered:

**Option A**: κ < a_1_p < a_1_m < [odd generators] < [even generators]
- Pro: places raw oscillators before derived generators
- Con: raw fermionic oscillators are not Lie algebra basis elements; mixing levels

**Option B**: κ < [odd generators, ordered by root type then k] < [even generators, Cartan first]
- Pro: clean separation of algebra basis from oscillator algebra; consistent with B(0,n) convention
- Con: slightly less direct connection to oscillator ordering

**Decision**: Option B is adopted, matching the B(0,n) convention `κ < [odd] < [even]`.

Within odd generators, the ordering is:
```
E_eps1_del{1}_pp, ..., E_eps1_del{n}_pp,
E_eps1_del{1}_pm, ..., E_eps1_del{n}_pm,
E_eps1_del{1}_mp, ..., E_eps1_del{n}_mp,
E_eps1_del{1}_mm, ..., E_eps1_del{n}_mm
```

Within even generators, the ordering is:
```
H_1, ..., H_{n+1},
E_2del{1}_p, ..., E_2del{n}_p,
E_del{i}_del{j}_pp  (i<j, lexicographic),
E_2del{1}_m, ..., E_2del{n}_m,
E_del{i}_del{j}_mm  (i<j, lexicographic),
E_del{i}_del{j}_pm  (i<j, lexicographic),
E_del{i}_del{j}_mp  (i<j, lexicographic)
```

## 5. Basis Lists by n

### C(2) = osp(2|2), n=1 (dim = 4|4, total 8)

**Even basis** (4 generators):
`H_1, H_2, E_2del1_p, E_2del1_m`

**Odd basis** (4 generators):
`E_eps1_del1_pp, E_eps1_del1_pm, E_eps1_del1_mp, E_eps1_del1_mm`

### C(3) = osp(2|4), n=2 (dim = 11|8, total 19)

**Even basis** (11 generators):
`H_1, H_2, H_3, E_2del1_p, E_2del2_p, E_del1_del2_pp, E_2del1_m, E_2del2_m, E_del1_del2_mm, E_del1_del2_pm, E_del1_del2_mp`

**Odd basis** (8 generators):
`E_eps1_del1_pp, E_eps1_del2_pp, E_eps1_del1_pm, E_eps1_del2_pm, E_eps1_del1_mp, E_eps1_del2_mp, E_eps1_del1_mm, E_eps1_del2_mm`

### C(4) = osp(2|6), n=3 (dim = 22|12, total 34)

**Even basis** (22 generators):
`H_1, H_2, H_3, H_4, E_2del1_p, E_2del2_p, E_2del3_p, E_del1_del2_pp, E_del1_del3_pp, E_del2_del3_pp, E_2del1_m, E_2del2_m, E_2del3_m, E_del1_del2_mm, E_del1_del3_mm, E_del2_del3_mm, E_del1_del2_pm, E_del1_del3_pm, E_del2_del3_pm, E_del1_del2_mp, E_del1_del3_mp, E_del2_del3_mp`

**Odd basis** (12 generators):
`E_eps1_del1_pp, E_eps1_del2_pp, E_eps1_del3_pp, E_eps1_del1_pm, E_eps1_del2_pm, E_eps1_del3_pm, E_eps1_del1_mp, E_eps1_del2_mp, E_eps1_del3_mp, E_eps1_del1_mm, E_eps1_del2_mm, E_eps1_del3_mm`

## 6. Dimension Formulas for C(n+1)

| n | even (2n²+n+1) | odd (4n) | total (2n²+5n+1) |
|---|---|---|---|
| 1 | 4 | 4 | 8 |
| 2 | 11 | 8 | 19 |
| 3 | 22 | 12 | 34 |

## 7. Simple Generator Realizations for C(n+1)

| Generator | Oscillator realization |
|---|---|
| H_1 | a_1^+ a_1^- + b_1^+ b_1^- |
| H_k (2≤k≤n) | b_{k-1}^+ b_{k-1}^- - b_k^+ b_k^- |
| H_{n+1} | -b_n^+ b_n^- - 1/2 |
| E_{ε-δ_1} | a_1^+ b_1^- |
| E_{δ_1-ε} | b_1^+ a_1^- |
| E_{δ_{k-1}-δ_k} (2≤k≤n) | b_{k-1}^+ b_k^- |
| E_{δ_k-δ_{k-1}} (2≤k≤n) | b_k^+ b_{k-1}^- |
| E_{2δ_n} | (1/2)(b_n^+)^2 |
| E_{-2δ_n} | (1/2)(b_n^-)^2 |

Note: In the oscillator realization used here, E_{2δ_k} = (b_k^+)^2 for all k (not just the terminal node).
The factor 1/2 in the simple generator H_{n+1} arises from the terminal Dynkin node convention.
