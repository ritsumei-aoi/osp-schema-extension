# Notation — C(n+1) = osp(2|2n) Extension

This document defines the notation conventions for the C(n+1) = osp(2|2n) schema extension.
It extends the B(0,n) notation established in the primary case study (osp-triviality).

## Oscillator Generators

C(n+1) = osp(2|2n) uses:
- **1 fermionic pair**: a_1_p, a_1_m (no supplementary fermion a_0)
- **n bosonic pairs**: b_i_p, b_i_m (i = 1, ..., n)

| Element | Label | Parity |
|---|---|---|
| Fermionic creation | a_1_p | odd (1) |
| Fermionic annihilation | a_1_m | odd (1) |
| Bosonic creation (i-th) | b_i_p | even (0) |
| Bosonic annihilation (i-th) | b_i_m | even (0) |

### Key Difference from B(0,n)

B(0,n) uses a supplementary real fermion a_0 with {a_0, a_0} = 1.
C(n+1) uses a standard fermionic pair (a_1_p, a_1_m) with {a_1_p, a_1_m} = 1.

## Root System

C(n+1) has roots involving both ε (fermionic) and δ (bosonic) indices:

### Even Roots

The even subalgebra of C(n+1) = osp(2|2n) is **so(2) × sp(2n)** with dimension
2n² + n + 1. The even root system consists of sp(2n) roots only — ε₁ roots
appear only in combination with δ_k in the odd sector (standard Frappat
convention). Generators a_1_p² and a_1_m² are not independent even root vectors.

| Root | Generator | Oscillator Realization |
|---|---|---|
| 2δ_k | E_2del{k}_p | (b_k_p)² |
| -2δ_k | E_2del{k}_m | (b_k_m)² |
| δ_i + δ_j (i<j) | E_del{i}_del{j}_pp | b_i_p b_j_p |
| δ_i - δ_j (i<j) | E_del{i}_del{j}_pm | b_i_p b_j_m |
| -(δ_i - δ_j) (i<j) | E_del{i}_del{j}_mp | b_i_m b_j_p |
| -(δ_i + δ_j) (i<j) | E_del{i}_del{j}_mm | b_i_m b_j_m |

### Odd Roots

| Root | Generator | Oscillator Realization |
|---|---|---|
| ε_1 + δ_k | E_eps1_del{k}_pp | a_1_p b_k_p |
| ε_1 - δ_k | E_eps1_del{k}_pm | a_1_p b_k_m |
| -(ε_1 - δ_k) | E_eps1_del{k}_mp | a_1_m b_k_p |
| -(ε_1 + δ_k) | E_eps1_del{k}_mm | a_1_m b_k_m |

### Cartan Generators

| Generator | Realization | Index |
|---|---|---|
| H_k (k = 1,...,n-1) | b_k_p b_k_m - b_{k+1}_p b_{k+1}_m | bosonic |
| H_n | b_n_p b_n_m + 1/2 | bosonic |
| H_{n+1} | a_1_p a_1_m - 1/2 | fermionic |

## LaTeX Macros

| Macro | Output | Type |
|---|---|---|
| `\Edp{k}` | E_{δ_k} | B(0,n) odd |
| `\Edm{k}` | E_{-δ_k} | B(0,n) odd |
| `\Eepdp{1}{k}` | E_{ε_1+δ_k} | C(n+1) odd |
| `\Eepdm{1}{k}` | E_{ε_1-δ_k} | C(n+1) odd |
| `\Eemdp{1}{k}` | E_{-ε_1+δ_k} | C(n+1) odd |
| `\Eemdm{1}{k}` | E_{-ε_1-δ_k} | C(n+1) odd |
| `\E2dkp{k}` | E_{2δ_k} | C(n+1) even |
| `\E2dkm{k}` | E_{-2δ_k} | C(n+1) even |
| `\Edelpp{i}{j}` | E_{δ_i+δ_j} (i<j) | C(n+1) even |
| `\Edelmm{i}{j}` | E_{-δ_i-δ_j} (i<j) | C(n+1) even |
| `\Edelpm{i}{j}` | E_{δ_i-δ_j} (i<j) | C(n+1) even |
| `\Edelmp{i}{j}` | E_{-δ_i+δ_j} (i<j) | C(n+1) even |

## PBW Ordering

Decided in Issue I01-1 (2026-05-15). C(n+1) uses the same structure as B(0,n) v5.0:

```
κ < [odd generators] < [even generators] < K
```

### Odd block (fermionic)
Ordered by positive then negative:
```
E_eps1_del{k}_pp (k=1..n)         # positive: ε₁ + δ_k
E_eps1_del{k}_pm (k=1..n)         # positive: ε₁ − δ_k
E_eps1_del{k}_mp (k=1..n)         # negative: −(ε₁ − δ_k)
E_eps1_del{k}_mm (k=1..n)         # negative: −(ε₁ + δ_k)
```

### Even block (bosonic)
```
H_1, ..., H_{n-1}, H_n, H_{n+1}  # Cartan (n+1)
E_2del{k}_p (k=1..n)              # positive long roots
E_del{i}_del{j}_pp (i<j)          # positive sum roots
E_2del{k}_m (k=1..n)              # negative long roots
E_del{i}_del{j}_mm (i<j)          # negative sum roots
E_del{i}_del{j}_pm (i<j)          # mixed (δ_i − δ_j)
E_del{i}_del{j}_mp (i<j)          # mixed (−δ_i + δ_j)
```

### Dimension Summary

| n | Even | Odd | Total | osp(2\|2n) |
|---|------|-----|-------|------------|
| 1 | 4    | 4   | 8     | 8 |
| 2 | 11   | 8   | 19    | 19 |
| 3 | 22   | 12  | 34    | 34 |

## References

- Frappat et al., *Dictionary on Lie Algebras and Superalgebras* (2000), Chapter on C(n+1)
- osp-triviality notation: handover/notation.md in the primary case study
