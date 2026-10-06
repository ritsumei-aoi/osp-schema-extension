# Notation and Terminology

Conventions for the C(n+1) = osp(2|2n) schema extension (finalized in I01).
Throughout, `n` is the bosonic rank: C(2)=osp(2|2) is n=1, C(3) is n=2, C(4) is n=3.

## 1. Oscillators
- Fermionic pair `a_1_p`, `a_1_m` (a_1^+, a_1^-), odd, CAR `{a_1^-, a_1^+} = 1`, `(a_1^±)^2 = 0`.
- Bosons `b_k_p`, `b_k_m` (k=1..n), even, CCR `[b_k^-, b_l^+] = δ_kl`.
- Fermions commute with bosons in the undeformed algebra.
- Central elements: `K` (even, identified with scalar 1, not a basis element) and `kappa` (odd, κ^2=0).
- Generators are Weyl-(symmetric-)ordered quadratics, so the bracket closes on the basis with no central term.

## 2. Generator labels and realization (N_x = x^+ x^-)
| Label | Root | Realization |
|---|---|---|
| `H_1` | | a_1^+a_1^- + b_1^+b_1^-  (= N_a + N_1) |
| `H_k` (2≤k≤n) | | b_{k-1}^+b_{k-1}^- - b_k^+b_k^- |
| `H_{n+1}` | | -b_n^+b_n^- - 1/2 |
| `E_2del{k}_p` / `_m` | ±2δ_k | (b_k^+)^2 / (b_k^-)^2 |
| `E_del{i}_del{j}_{pp,pm,mp,mm}` (i<j) | ±δ_i±δ_j | b_i^s b_j^t (first sign s on i, second t on j) |
| `E_eps1_del{k}_{pp,pm,mp,mm}` | σε+τδ_k | a_1^σ b_k^τ (first sign σ, second τ) |

Resolved ambiguity: `Cn1_definition.md` writes E_{±2δ_n} = ½(b_n^±)^2 for the simple generator but (b_k^±)^2 for
"all root generators"; we use (b_k^±)^2 for every k (uniform labels).

## 3. Bases
Even (2n²+n+1): n+1 Cartan + 2n² roots. Odd: 4n.

- C(2), n=1 (4|4): even `H_1,H_2,E_2del1_p,E_2del1_m`; odd `E_eps1_del1_pp,E_eps1_del1_pm,E_eps1_del1_mp,E_eps1_del1_mm`.
- C(3), n=2 (11|8): even `H_1,H_2,H_3,E_2del1_p,E_2del2_p,E_del1_del2_pp,E_2del1_m,E_2del2_m,E_del1_del2_mm,E_del1_del2_pm,E_del1_del2_mp`;
  odd `E_eps1_del{1,2}_pp, E_eps1_del{1,2}_pm, E_eps1_del{1,2}_mp, E_eps1_del{1,2}_mm`.
- C(4), n=3 (22|12): even `H_1..H_4`, `E_2del{1,2,3}_p`, `E_del{12,13,23}_pp`, `E_2del{1,2,3}_m`, `E_del{12,13,23}_mm`, `E_del{12,13,23}_pm`, `E_del{12,13,23}_mp`
  (`E_del12_pp` abbreviates `E_del1_del2_pp`); odd `E_eps1_del{1,2,3}_{pp,pm,mp,mm}`.

## 4. PBW ordering
Options considered:
- A: κ < odd < even (the B(0,n) v5.0 convention), odd grouped sign-pair-major then k.
- B: κ < even < odd.
- C: root-height ordering (negative roots < Cartan < positive roots, ε-roots interleaved by height).

**Chosen: A.** Reasons: (i) identical to the B(0,n) v5.0 `ordering_convention`, preserving compatibility;
(ii) κ is odd and comes first, so the normal form κ·Z matches the schema; (iii) C depends on a choice of
positive system for ε, while A is purely combinatorial.

Order within groups:
- odd: sign pairs in order pp, pm, mp, mm; within a pair k = 1..n.
- even: H_1..H_{n+1}, E_2del_p (k asc), E_del_del_pp (lex), E_2del_m, E_del_del_mm, E_del_del_pm, E_del_del_mp (as in the B schema).
- oscillator words: `kappa < a_1_p < a_1_m < b_1_p < b_1_m < b_2_p < ...`.

## 5. Bracket convention
Graded commutator in the oscillator algebra: [X,Y} = XY - (-1)^{p(X)p(Y)} YX.
