# C(n+1) Notation and Conventions

This document records the finalized notation, basis lists, and PBW ordering
for C(n+1) = osp(2|2n) as approved in Step 1 (Issue I01-1).

---

## 1. Algebras and Dimensions

| Algebra | n | even (g_0̄) | odd (g_1̄) | total |
|---|---|---|---|---|
| C(2) = osp(2\|2) | 1 | 4 | 4 | 8 |
| C(3) = osp(2\|4) | 2 | 11 | 8 | 19 |
| C(4) = osp(2\|6) | 3 | 22 | 12 | 34 |

Formulas: even = 2n²+n+1, odd = 4n, total = 2n²+5n+1.

Even subalgebra: so(2) × sp(2n).

---

## 2. Oscillator Generators

| Label | Parity | Relation | Description |
|---|---|---|---|
| `a_1_p` | 1 | CAR: {a_1^−, a_1^+} = 1 | Standard fermionic creation |
| `a_1_m` | 1 | CAR: {a_1^−, a_1^+} = 1 | Standard fermionic annihilation |
| `b_k_p` (k=1…n) | 0 | CCR: [b_k^−, b_l^+] = δ_{kl} | Bosonic creation |
| `b_k_m` (k=1…n) | 0 | CCR: [b_k^−, b_l^+] = δ_{kl} | Bosonic annihilation |

Central elements: K (even, identity; not a basis element), κ (odd, nilpotent: κ² = 0).

---

## 3. Generator Label Convention

### Odd generators (ε-roots)

| Root | Label | Oscillator word |
|---|---|---|
| ε + δ_k | `E_eps1_del{k}_pp` | a_1^+ b_k^+ |
| ε − δ_k | `E_eps1_del{k}_pm` | a_1^+ b_k^− |
| −ε + δ_k | `E_eps1_del{k}_mp` | a_1^− b_k^+ |
| −ε − δ_k | `E_eps1_del{k}_mm` | a_1^− b_k^− |

### Even generators

| Root | Label | Oscillator word |
|---|---|---|
| (Cartan, k=1) | `H_1` | a_1^+ a_1^− + b_1^+ b_1^− |
| (Cartan, k=2…n) | `H_k` | b_{k-1}^+ b_{k-1}^− − b_k^+ b_k^− |
| (Cartan, k=n+1) | `H_{n+1}` | −b_n^+ b_n^− − 1/2 |
| 2δ_k | `E_2del{k}_p` | (b_k^+)² |
| −2δ_k | `E_2del{k}_m` | (b_k^−)² |
| δ_i + δ_j (i<j) | `E_del{i}_del{j}_pp` | b_i^+ b_j^+ |
| −(δ_i + δ_j) (i<j) | `E_del{i}_del{j}_mm` | b_i^− b_j^− |
| δ_i − δ_j (i<j) | `E_del{i}_del{j}_pm` | b_i^+ b_j^− |
| −(δ_i − δ_j) (i<j) | `E_del{i}_del{j}_mp` | b_i^− b_j^+ |

---

## 4. PBW Ordering (Approved: Option 1 — Fermionic-oscillator primary)

General form:
```
κ < [a_1^+ block] < [a_1^− block] < [even generators]
```

Within the a_1^+ block (bosonic oscillator order: b_k^+, then b_k^−, for k=1…n):
```
E_eps1_del1_pp, …, E_eps1_deln_pp,
E_eps1_del1_pm, …, E_eps1_deln_pm
```

Within the a_1^− block:
```
E_eps1_del1_mp, …, E_eps1_deln_mp,
E_eps1_del1_mm, …, E_eps1_deln_mm
```

Within even generators:
```
H_1, …, H_{n+1}  <  [positive roots]  <  [negative roots]  <  [mixed roots]
```

Positive roots (E_2del{k}_p, E_del{i}_del{j}_pp in index order),
negative roots (E_2del{k}_m, E_del{i}_del{j}_mm),
mixed roots (E_del{i}_del{j}_pm, E_del{i}_del{j}_mp).

### C(2), n=1

```
κ
< E_eps1_del1_pp, E_eps1_del1_pm,
  E_eps1_del1_mp, E_eps1_del1_mm
< H_1, H_2,
  E_2del1_p,
  E_2del1_m
```

### C(3), n=2

```
κ
< E_eps1_del1_pp, E_eps1_del2_pp,
  E_eps1_del1_pm, E_eps1_del2_pm,
  E_eps1_del1_mp, E_eps1_del2_mp,
  E_eps1_del1_mm, E_eps1_del2_mm
< H_1, H_2, H_3,
  E_2del1_p, E_2del2_p, E_del1_del2_pp,
  E_2del1_m, E_2del2_m, E_del1_del2_mm,
  E_del1_del2_pm, E_del1_del2_mp
```

### C(4), n=3

```
κ
< E_eps1_del1_pp, E_eps1_del2_pp, E_eps1_del3_pp,
  E_eps1_del1_pm, E_eps1_del2_pm, E_eps1_del3_pm,
  E_eps1_del1_mp, E_eps1_del2_mp, E_eps1_del3_mp,
  E_eps1_del1_mm, E_eps1_del2_mm, E_eps1_del3_mm
< H_1, H_2, H_3, H_4,
  E_2del1_p, E_2del2_p, E_2del3_p,
  E_del1_del2_pp, E_del1_del3_pp, E_del2_del3_pp,
  E_2del1_m, E_2del2_m, E_2del3_m,
  E_del1_del2_mm, E_del1_del3_mm, E_del2_del3_mm,
  E_del1_del2_pm, E_del1_del3_pm, E_del2_del3_pm,
  E_del1_del2_mp, E_del1_del3_mp, E_del2_del3_mp
```

---

## 5. Basis Lists (JSON-ready)

### C(2), n=1

```json
{
  "even": ["H_1", "H_2", "E_2del1_p", "E_2del1_m"],
  "odd": [
    "E_eps1_del1_pp", "E_eps1_del1_pm",
    "E_eps1_del1_mp", "E_eps1_del1_mm"
  ]
}
```

### C(3), n=2

```json
{
  "even": [
    "H_1", "H_2", "H_3",
    "E_2del1_p", "E_2del2_p", "E_del1_del2_pp",
    "E_2del1_m", "E_2del2_m", "E_del1_del2_mm",
    "E_del1_del2_pm", "E_del1_del2_mp"
  ],
  "odd": [
    "E_eps1_del1_pp", "E_eps1_del2_pp",
    "E_eps1_del1_pm", "E_eps1_del2_pm",
    "E_eps1_del1_mp", "E_eps1_del2_mp",
    "E_eps1_del1_mm", "E_eps1_del2_mm"
  ]
}
```

### C(4), n=3

```json
{
  "even": [
    "H_1", "H_2", "H_3", "H_4",
    "E_2del1_p", "E_2del2_p", "E_2del3_p",
    "E_del1_del2_pp", "E_del1_del3_pp", "E_del2_del3_pp",
    "E_2del1_m", "E_2del2_m", "E_2del3_m",
    "E_del1_del2_mm", "E_del1_del3_mm", "E_del2_del3_mm",
    "E_del1_del2_pm", "E_del1_del3_pm", "E_del2_del3_pm",
    "E_del1_del2_mp", "E_del1_del3_mp", "E_del2_del3_mp"
  ],
  "odd": [
    "E_eps1_del1_pp", "E_eps1_del2_pp", "E_eps1_del3_pp",
    "E_eps1_del1_pm", "E_eps1_del2_pm", "E_eps1_del3_pm",
    "E_eps1_del1_mp", "E_eps1_del2_mp", "E_eps1_del3_mp",
    "E_eps1_del1_mm", "E_eps1_del2_mm", "E_eps1_del3_mm"
  ]
}
```

---

## 6. Change Log

| Date | Issue | Decision |
|---|---|---|
| 2026-10-09 | I01-1 | PBW ordering Option 1 (fermionic-oscillator primary) approved by human researcher |
