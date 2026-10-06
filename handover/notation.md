# C(n+1) Notation and Convention Reference

**Algebra**: C(n+1) = osp(2|2n)  
**Status**: Approved (I01-1)  
**Reference**: Frappat, Sciarrino, Sorba, *Dictionary on Lie Algebras and Superalgebras* (2000); arXiv:hep-th/9607161

---

## 1. Oscillator Generators

| Symbol | JSON label | Parity | Relation |
|--------|-----------|--------|---------|
| a_1^+ | `a_1_p` | 1 | CAR: {a_1^−, a_1^+} = 1 |
| a_1^− | `a_1_m` | 1 | CAR: {a_1^−, a_1^+} = 1 |
| b_k^+ | `b_{k}_p` | 0 | CCR: [b_k^−, b_l^+] = δ_{kl} |
| b_k^− | `b_{k}_m` | 0 | CCR: [b_k^−, b_l^+] = δ_{kl} |

PBW word ordering for oscillators: `a_1_p < a_1_m < b_1_p < b_1_m < b_2_p < b_2_m < ...`

---

## 2. Generator Label Conventions

### Even generators

| Root | Label | Oscillator realization |
|------|-------|----------------------|
| Cartan (simple root k, k=1,...,n+1) | `H_{k}` | see Cn1_definition.md §2 |
| 2δ_k | `E_2del{k}_p` | (b_k^+)^2 |
| −2δ_k | `E_2del{k}_m` | (b_k^−)^2 |
| δ_i + δ_j (i < j) | `E_del{i}_del{j}_pp` | b_i^+ b_j^+ |
| δ_i − δ_j (i < j) | `E_del{i}_del{j}_pm` | b_i^+ b_j^− |
| −δ_i + δ_j (i < j) | `E_del{i}_del{j}_mp` | b_i^− b_j^+ |
| −δ_i − δ_j (i < j) | `E_del{i}_del{j}_mm` | b_i^− b_j^− |

### Odd generators

| Root | Label | Oscillator realization |
|------|-------|----------------------|
| ε + δ_k | `E_eps1_del{k}_pp` | a_1^+ b_k^+ |
| ε − δ_k | `E_eps1_del{k}_pm` | a_1^+ b_k^− |
| −ε + δ_k | `E_eps1_del{k}_mp` | a_1^− b_k^+ |
| −ε − δ_k | `E_eps1_del{k}_mm` | a_1^− b_k^− |

---

## 3. PBW Ordering (Approved: Option A, ε-sign-first)

```
κ  <  [ε+ odd: E_eps1_del1_pp, E_eps1_del1_pm, ..., E_eps1_del{n}_pp, E_eps1_del{n}_pm]
    < [ε− odd: E_eps1_del1_mp, E_eps1_del1_mm, ..., E_eps1_del{n}_mp, E_eps1_del{n}_mm]
    < [even: H_1, ..., H_{n+1},
             E_2del1_p, ..., E_2del{n}_p,
             E_del{i}_del{j}_pp (i<j, ordered lexicographically),
             E_2del1_m, ..., E_2del{n}_m,
             E_del{i}_del{j}_mm (i<j),
             E_del{i}_del{j}_pm, E_del{i}_del{j}_mp (i<j)]
```

Within each ε-sign group, odd generators are ordered by bosonic index k ascending, then δ-sign (+ before −).

---

## 4. Basis Lists by Algebra

### C(2) = osp(2|2), n=1 — dim (4|4), total 8

**Even (4)**:
```
H_1, H_2,
E_2del1_p, E_2del1_m
```

**Odd (4)** — PBW order:
```
E_eps1_del1_pp, E_eps1_del1_pm,   [ε+]
E_eps1_del1_mp, E_eps1_del1_mm    [ε−]
```

---

### C(3) = osp(2|4), n=2 — dim (11|8), total 19

**Even (11)**:
```
H_1, H_2, H_3,
E_2del1_p, E_2del2_p,
E_del1_del2_pp,
E_2del1_m, E_2del2_m,
E_del1_del2_mm,
E_del1_del2_pm, E_del1_del2_mp
```

**Odd (8)** — PBW order:
```
E_eps1_del1_pp, E_eps1_del1_pm, E_eps1_del2_pp, E_eps1_del2_pm,   [ε+]
E_eps1_del1_mp, E_eps1_del1_mm, E_eps1_del2_mp, E_eps1_del2_mm    [ε−]
```

---

### C(4) = osp(2|6), n=3 — dim (22|12), total 34

**Even (22)**:
```
H_1, H_2, H_3, H_4,
E_2del1_p, E_2del2_p, E_2del3_p,
E_del1_del2_pp, E_del1_del3_pp, E_del2_del3_pp,
E_2del1_m, E_2del2_m, E_2del3_m,
E_del1_del2_mm, E_del1_del3_mm, E_del2_del3_mm,
E_del1_del2_pm, E_del1_del2_mp,
E_del1_del3_pm, E_del1_del3_mp,
E_del2_del3_pm, E_del2_del3_mp
```

**Odd (12)** — PBW order:
```
E_eps1_del1_pp, E_eps1_del1_pm,
E_eps1_del2_pp, E_eps1_del2_pm,
E_eps1_del3_pp, E_eps1_del3_pm,   [ε+]
E_eps1_del1_mp, E_eps1_del1_mm,
E_eps1_del2_mp, E_eps1_del2_mm,
E_eps1_del3_mp, E_eps1_del3_mm    [ε−]
```

---

## 5. Dimension Formulas

| n | even | odd | total | Algebra |
|---|------|-----|-------|---------|
| 1 | 4 | 4 | 8 | C(2) = osp(2\|2) |
| 2 | 11 | 8 | 19 | C(3) = osp(2\|4) |
| 3 | 22 | 12 | 34 | C(4) = osp(2\|6) |

Formulas: even = 2n²+n+1, odd = 4n, total = 2n²+5n+1.
