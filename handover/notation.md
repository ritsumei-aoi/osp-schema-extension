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

| Root | Generator | Oscillator Realization |
|---|---|---|
| ε_1 | E_eps1_p | a_1_p² (or a_0 a_1_p depending on convention) |
| -ε_1 | E_eps1_m | a_1_m² |
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
| `\Eep{1}` | E_{ε_1} | C(n+1) even |
| `\Eem{1}` | E_{-ε_1} | C(n+1) even |
| `\Eepdp{1}{k}` | E_{ε_1+δ_k} | C(n+1) odd |
| `\Eepdm{1}{k}` | E_{ε_1-δ_k} | C(n+1) odd |

## PBW Ordering

To be decided in Issue I-001. The ordering must be compatible with the
existing B(0,n) v5.0 convention:

```
κ < [fermionic generators] < [bosonic generators] < K
```

For C(n+1), the fermionic block contains a_1_p, a_1_m instead of a_0.

## References

- Frappat et al., *Dictionary on Lie Algebras and Superalgebras* (2000), Chapter on C(n+1)
- osp-triviality notation: handover/notation.md in the primary case study
