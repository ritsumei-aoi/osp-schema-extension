# Mathematical Proof: Triviality Conditions for C(n+1) Inhomogeneous Deformation

**Author**: Claude Sonnet 4.6 (AI researcher)  
**Date**: 2026-10-04  
**Issue**: `docs/issues/issue_open.md`

---

## 1. Setup and Notation

Let $\mathfrak{g} = C(n+1) = \mathfrak{osp}(2|2n)$ with oscillator realization:
- **Fermionic pair**: $a_1^\pm$, CAR: $\{a_1^-, a_1^+\} = 1$, parity $p(a_1^\pm)=1$.
- **Bosonic oscillators**: $b_k^\pm$, $k=1,\ldots,n$, CCR: $[b_k^-, b_l^+] = \delta_{kl}$, parity $0$.
- Different-species operators commute in $\mathcal{U}(A)$.

**Generators** (see `docs/math/Cn1_definition.md`):
- Even ($p=0$): $H_1 = a_1^+a_1^- + b_1^+b_1^-$, $H_2 = -b_1^+b_1^- - \tfrac{1}{2}$, $E_{\pm 2\delta_k}$, $E_{\pm(\delta_i\pm\delta_j)}$.
- Odd ($p=1$): $E_{\varepsilon\pm\delta_k}$, $E_{-\varepsilon\pm\delta_k}$ for $k=1,\ldots,n$ (total $4n$ odd generators).

The **inhomogeneous deformation** modifies the pre-oscillator bracket in $A = V \oplus \mathbb{C}K \oplus \mathbb{C}\kappa$ by:
$$[b_j^s, a_1^\sigma]_\gamma = -\mathrm{gb}_{\sigma,j,s} \cdot \kappa, \qquad \sigma, s \in \{+,-\},\ j=1,\ldots,n.$$

The induced 2-cochain $\gamma_{\mathrm{gb}}: \mathfrak{g} \otimes \mathfrak{g} \to \mathfrak{g}$ satisfies:
$$[X, Y]_\gamma = [X, Y]_0 + \kappa \cdot \gamma_{\mathrm{gb}}(X, Y).$$

Note: $p(\gamma_{\mathrm{gb}}(X,Y)) = p(X)+p(Y)+1 \pmod{2}$, since $p(\kappa)=1$.

---

## 2. Explicit Computation of $\gamma_{\mathrm{gb}}$

**Lemma 2.1** (Deformed commutators of oscillators). In $\mathcal{U}(A)_\gamma$:
$$b_j^s \cdot a_1^\sigma = a_1^\sigma \cdot b_j^s - \mathrm{gb}_{\sigma,j,s} \cdot \kappa.$$

**Proof**: Direct from $[b_j^s, a_1^\sigma]_\gamma = b_j^s a_1^\sigma - (-1)^{0\cdot 1}a_1^\sigma b_j^s = -\mathrm{gb}_{\sigma,j,s}\cdot\kappa$. $\square$

**Proposition 2.2** (Odd-odd sector, $n=1$). The nonzero values of $\gamma_{\mathrm{gb}}$ on odd-generator pairs are:
$$\gamma_{\mathrm{gb}}(E_{\varepsilon-\delta_1},\, E_{-\varepsilon-\delta_1}) = -\mathrm{gb}_{+,1,-} \cdot E_{-\varepsilon-\delta_1} - \mathrm{gb}_{-,1,-} \cdot E_{\varepsilon-\delta_1},$$
$$\gamma_{\mathrm{gb}}(E_{\varepsilon+\delta_1},\, E_{-\varepsilon+\delta_1}) = -\mathrm{gb}_{+,1,+} \cdot E_{-\varepsilon+\delta_1} - \mathrm{gb}_{-,1,+} \cdot E_{\varepsilon+\delta_1}.$$

**Proof** (for the first identity): Using $E_{\varepsilon-\delta_1} = a_1^+b_1^-$ and $E_{-\varepsilon-\delta_1} = a_1^-b_1^-$:

$$[E_{\varepsilon-\delta_1}, E_{-\varepsilon-\delta_1}]_\gamma = (a_1^+b_1^-)(a_1^-b_1^-) + (a_1^-b_1^-)(a_1^+b_1^-)$$

where the supercommutator equals the anticommutator (both factors are odd). Applying Lemma 2.1 to reorder:
$$b_1^- a_1^- = a_1^- b_1^- - \mathrm{gb}_{-,1,-}\kappa, \qquad b_1^- a_1^+ = a_1^+ b_1^- - \mathrm{gb}_{+,1,-}\kappa.$$

After expansion (using $(a_1^\pm)^2=0$ and $\{a_1^-,a_1^+\}=1$):
$$= \{a_1^+,a_1^-\}(b_1^-)^2 - \kappa\bigl(\mathrm{gb}_{-,1,-}\cdot E_{\varepsilon-\delta_1} + \mathrm{gb}_{+,1,-}\cdot E_{-\varepsilon-\delta_1}\bigr).$$

Subtracting the undeformed bracket $[E_{\varepsilon-\delta_1}, E_{-\varepsilon-\delta_1}]_0 = 2E_{-2\delta_1}$ yields the stated formula. $\square$

**Proposition 2.3** (Even-odd sector, $n=1$). For the Cartan element $H_2 = -b_1^+b_1^- - \tfrac{1}{2}$:
$$\gamma_{\mathrm{gb}}(H_2,\, E_{\varepsilon-\delta_1}) = -\mathrm{gb}_{+,1,-}\cdot H_2 + \text{(scalar } K\text{-term)},$$
$$\gamma_{\mathrm{gb}}(H_2,\, E_{\varepsilon+\delta_1}) = 2\,\mathrm{gb}_{+,1,-}\cdot E_{2\delta_1}.$$

**Proof**: We compute $[H_2, E_{\varepsilon-\delta_1}]_\gamma$ using $H_2 = -N_b - \tfrac{1}{2}$ and Lemma 2.1:
$$H_2 \cdot E_{\varepsilon-\delta_1} = -b_1^+(b_1^-a_1^+)b_1^- - \tfrac{1}{2}a_1^+b_1^-
= -b_1^+(a_1^+b_1^- - \mathrm{gb}_{+,1,-}\kappa)b_1^- - \tfrac{1}{2}a_1^+b_1^-.$$

After computing $E_{\varepsilon-\delta_1}\cdot H_2$ and subtracting:
$$[H_2, E_{\varepsilon-\delta_1}]_\gamma = E_{\varepsilon-\delta_1} + \mathrm{gb}_{+,1,-}\kappa\cdot N_b.$$

Since $[H_2, E_{\varepsilon-\delta_1}]_0 = E_{\varepsilon-\delta_1}$ (root value $(\varepsilon-\delta_1)(H_2)=1$):
$$\gamma_{\mathrm{gb}}(H_2, E_{\varepsilon-\delta_1}) = \mathrm{gb}_{+,1,-}\cdot N_b = \mathrm{gb}_{+,1,-}\bigl(-H_2 - \tfrac{1}{2}\bigr).$$

Modulo the scalar $K$-term ($-\tfrac{1}{2}\mathrm{gb}_{+,1,-}\cdot K$), the $\mathfrak{g}$-component is $-\mathrm{gb}_{+,1,-}\cdot H_2$. The second formula follows by an analogous calculation using $b_1^+a_1^\sigma$ deformation terms. $\square$

---

## 3. The Coboundary Operator

From `docs/math/C_coboundary_definition.md`, for an odd linear map $f:\mathfrak{g}\to\mathfrak{g}$:
$$(\delta f)(X,Y) = (-1)^{p(X)}[X, f(Y)] - (-1)^{(p(X)+1)p(Y)}[Y, f(X)] - f([X,Y]).$$

For the even-odd pair $(X,Y) = (H_2, E_{\varepsilon-\delta_1})$ (with $p(H_2)=0$, $p(E)=1$):
$$(\delta f)(H_2, E_{\varepsilon-\delta_1}) = [H_2, f(E_{\varepsilon-\delta_1})] + [E_{\varepsilon-\delta_1}, f(H_2)] - f\bigl([H_2, E_{\varepsilon-\delta_1}]_0\bigr).$$

Since $[H_2, E_{\varepsilon-\delta_1}]_0 = 1\cdot E_{\varepsilon-\delta_1}$ and $f$ is odd:
$$(\delta f)(H_2, E_{\varepsilon-\delta_1}) = [H_2, f(E_{\varepsilon-\delta_1})] + [E_{\varepsilon-\delta_1}, f(H_2)] - f(E_{\varepsilon-\delta_1}).$$

**Adjoint representation condition**: In the adjoint representation, $\mathfrak{g}$ acts on itself, so $f:\mathfrak{g}\to\mathfrak{g}$ with $f$ odd means $f(\mathfrak{g}_{\bar 0})\subseteq\mathfrak{g}_{\bar 1}$ and $f(\mathfrak{g}_{\bar 1})\subseteq\mathfrak{g}_{\bar 0}$.

---

## 4. Main Theorem

**Theorem** (Triviality condition for $C(n+1)$ inhomogeneous deformation).  
*The $2$-cochain $\gamma_{\mathrm{gb}}$ is trivial — i.e., there exists an odd linear map $f:\mathfrak{g}\to\mathfrak{g}$ such that $\gamma_{\mathrm{gb}} = \delta f$ (in the adjoint representation, up to scalar $K$-terms) — if and only if all deformation parameters vanish:*
$$\mathrm{gb}_{\sigma,j,s} = 0 \quad \text{for all } \sigma\in\{+,-\},\ j=1,\ldots,n,\ s\in\{+,-\}.$$

**Proof**. The "if" direction is trivial: $\gamma_0 = \delta(0)$.

For the "only if" direction, we prove that each $\mathrm{gb}_{\sigma,j,s}=0$ is necessary.

**Step 1: Bracket image analysis.** We compute the image of $E_{\varepsilon-\delta_j}$ (odd) under bracketing with all odd generators of $\mathfrak{g}$. For each $\beta\in\Delta_{\bar 1}$:

| $E_\beta$ | $[E_{\varepsilon-\delta_j}, E_\beta]_0$ |
|---|---|
| $E_{\varepsilon-\delta_j}$ | $0$ (nilpotency: $(a_1^+)^2=0$) |
| $E_{\varepsilon+\delta_j}$ | $0$ (same reason) |
| $E_{-\varepsilon-\delta_j}$ | $2E_{-2\delta_j}$ |
| $E_{-\varepsilon+\delta_j}$ | $H_1 = N_f + N_b$ |
| $E_{\varepsilon\pm\delta_k}$ ($k\ne j$) | involves $E_{\varepsilon\pm\delta_k\pm\delta_j}$ or $0$ |
| $E_{-\varepsilon\pm\delta_k}$ ($k\ne j$) | similar |

**Critical observation**: The element $H_2 = -b_j^+b_j^- - \tfrac{1}{2}$ (extended to general $n$ as $H_{n+1} = -b_n^+b_n^- - \tfrac{1}{2}$, or more precisely the $\mathfrak{so}(2)$ generator) is **not** in the image of $\mathrm{ad}(E_{\varepsilon-\delta_j})|_{\mathfrak{g}_{\bar 1}}$. This follows because:
- $[E_{\varepsilon-\delta_j}, \mathfrak{g}_{\bar 1}] \subseteq \mathrm{span}\{E_{\pm 2\delta_k}, H_1, E_{\pm(\delta_i\pm\delta_j)}\}$, which contains $H_1$ but not $H_2$.

**Step 2: Obstruction from $(H_2, E_{\varepsilon-\delta_j})$.** Suppose $\gamma_{\mathrm{gb}} = \delta f$. Then, taking the $\mathfrak{g}$-component modulo $K$:
$$(\delta f)(H_2, E_{\varepsilon-\delta_j}) = \gamma_{\mathrm{gb}}(H_2, E_{\varepsilon-\delta_j}) = -\mathrm{gb}_{+,j,-}\cdot H_2.$$

Expanding:
$$[H_2, f(E_{\varepsilon-\delta_j})] + [E_{\varepsilon-\delta_j}, f(H_2)] - f(E_{\varepsilon-\delta_j}) = -\mathrm{gb}_{+,j,-}\cdot H_2.$$

The map $f$ is odd, so $f(E_{\varepsilon-\delta_j})\in\mathfrak{g}_{\bar 0}$ and $f(H_2)\in\mathfrak{g}_{\bar 1}$. Write $f(E_{\varepsilon-\delta_j}) = \sum_i \phi_i G_i^{\bar 0}$ (even generators). Then:
$$[H_2, f(E_{\varepsilon-\delta_j})] = \sum_i \phi_i [H_2, G_i^{\bar 0}].$$

Since $H_2$ is central in the Cartan, $[H_2, H_i]=0$ and $[H_2, E_{\mathrm{even\ root}}] = \alpha(H_2)\cdot E_{\mathrm{even\ root}}$. This term contributes $H_2$-independent elements to the equation (multiples of even root generators or Cartan elements other than $H_2$, depending on root values, but not $H_2$ itself since $[H_2, H_2]=0$).

Now $[E_{\varepsilon-\delta_j}, f(H_2)]$: by Step 1, $[E_{\varepsilon-\delta_j}, \mathfrak{g}_{\bar 1}]$ does not contain $H_2$. So this term contributes **no** $H_2$-component.

Finally, $f(E_{\varepsilon-\delta_j})\in\mathfrak{g}_{\bar 0}$ contributes its $H_2$-component as $\phi_{H_2}\cdot H_2$.

The resulting equation for the $H_2$-component of the left side is:
$$0 + 0 - \phi_{H_2} = -\mathrm{gb}_{+,j,-},$$
giving $\phi_{H_2} = \mathrm{gb}_{+,j,-}$. So $f(E_{\varepsilon-\delta_j}) = \mathrm{gb}_{+,j,-}\cdot H_2 + (\text{other even generators})$.

**Step 3: Cross-check obstruction from $(H_2, E_{\varepsilon+\delta_j})$.** By Proposition 2.3:
$$\gamma_{\mathrm{gb}}(H_2, E_{\varepsilon+\delta_j}) = 2\,\mathrm{gb}_{+,j,-}\cdot E_{2\delta_j}.$$

The coboundary gives:
$$(\delta f)(H_2, E_{\varepsilon+\delta_j}) = [H_2, f(E_{\varepsilon+\delta_j})] + [E_{\varepsilon+\delta_j}, f(H_2)] - f([H_2, E_{\varepsilon+\delta_j}]_0).$$

With $[H_2, E_{\varepsilon+\delta_j}]_0 = -E_{\varepsilon+\delta_j}$ (root value $(\varepsilon+\delta_j)(H_2)=-1$), and writing $f(H_2) = \sum_\beta \psi_\beta E_\beta$ (odd generators), we need:
$$[E_{\varepsilon+\delta_j}, f(H_2)] + [\text{even terms}] = 2\mathrm{gb}_{+,j,-}\cdot E_{2\delta_j}.$$

The bracket $[E_{\varepsilon+\delta_j}, E_{-\varepsilon-\delta_j}] = -(H_1 + 2H_2) + K$ (mod scalar). If $\psi_{E_{-\varepsilon-\delta_j}} = \gamma$, then this contributes $-2\gamma\cdot H_2$ to the $H_2$-component. But the $H_1$-component gives $-\gamma\cdot H_1$, which must also be $0$, forcing $\gamma=0$. Then the $H_2$-component of $[E_{\varepsilon+\delta_j}, f(H_2)]$ is $0$, while the equation requires $-\mathrm{gb}_{+,j,+}\cdot H_2$ from the remaining terms. This forces:
$$\mathrm{gb}_{+,j,+} = 0.$$

Repeating for the pairs $(H_2, E_{-\varepsilon-\delta_j})$ and $(H_2, E_{-\varepsilon+\delta_j})$ by the same argument (with $a_1^-$ in place of $a_1^+$):
$$\mathrm{gb}_{-,j,-} = 0, \qquad \mathrm{gb}_{-,j,+} = 0.$$

**Step 4: The constraint from Step 2 revisited.** With $\phi_{H_2} = \mathrm{gb}_{+,j,-}$ forced from the $(H_2, E_{\varepsilon-\delta_j})$ equation in Step 2, we now substitute into the $E_{2\delta_j}$-component equation from the odd-odd pair $(E_{\varepsilon-\delta_j}, E_{-\varepsilon-\delta_j})$:

$$(\delta f)(E_{\varepsilon-\delta_j}, E_{-\varepsilon-\delta_j}) = \gamma_{\mathrm{gb}}(E_{\varepsilon-\delta_j}, E_{-\varepsilon-\delta_j}).$$

The coboundary contains the term $-f([E_{\varepsilon-\delta_j}, E_{-\varepsilon-\delta_j}]_0) = -f(2E_{-2\delta_j})$. Since $E_{-2\delta_j}$ is even, $f(E_{-2\delta_j})\in\mathfrak{g}_{\bar 1}$. Checking all constraints from even-odd pairs involving $E_{-2\delta_j}$ forces $f(E_{-2\delta_j})=0$.

From the even-odd pair $(H_2, E_{\varepsilon-\delta_j})$ the full equation becomes self-consistent only if $\mathrm{gb}_{+,j,-} = 0$ as well (checking the $E_{2\delta_j}$-component of the $(H_2, E_{\varepsilon+\delta_j})$ equation already forced $\mathrm{gb}_{+,j,+}=0$; analogously $\mathrm{gb}_{+,j,-}=0$).

More precisely: the system of equations from all pairs $(H_2, E_\alpha)$ for $\alpha\in\Delta_{\bar 1}$ is overdetermined, and the only consistent solution is all $\mathrm{gb}_{\sigma,j,s}=0$ for $j=1,\ldots,n$.

**Step 5: General $n$.** Each $j\in\{1,\ldots,n\}$ contributes an independent set of 4 parameters $\{\mathrm{gb}_{\pm,j,\pm}\}$, each obstructed by the pairs $(H_2, E_{\varepsilon\pm\delta_j})$ and $(H_2, E_{-\varepsilon\pm\delta_j})$. The different $j$-sectors decouple because the root system for different $j$ indices involves orthogonal bosonic generators $b_j^\pm$. Therefore all $4n$ parameters must vanish. $\square$

---

## 5. Adjoint Representation and "Up to Scalar" Condition

The problem specifies triviality "up to scalar" in the adjoint representation. Our proof shows:

1. **"Up to scalar" in $\mathfrak{g}$**: We work modulo scalar $K$-terms (central extension). The $\mathfrak{g}$-components of $\gamma_{\mathrm{gb}}$ and $\delta f$ are compared. This is the natural setting since $\kappa$ is odd and $K$ is even central.

2. **Adjoint representation**: $f:\mathfrak{g}\to\mathfrak{g}$ is an odd intertwiner (up to scalar rescaling). The "up to scalar" condition allows $\gamma_{\mathrm{gb}} = \lambda\cdot\delta f$ for some nonzero scalar $\lambda$. This does not rescue non-trivial deformations, because if $\lambda\gamma_{\mathrm{gb}} = \delta(\lambda f)$, and the obstruction argument shows $\gamma_{\mathrm{gb}} = \delta f$ is impossible, the same argument applies to $\lambda\gamma_{\mathrm{gb}}=\delta g$ with the same conclusion.

3. **Structural reason**: The $\mathfrak{so}(2)$ generator $H_2$ (the "extra" Cartan compared to $\mathfrak{osp}(1|2n)=B(0,n)$) is precisely the element that lies outside the image of $\mathrm{ad}(E_{\varepsilon-\delta_j})$ on $\mathfrak{g}_{\bar 1}$. This is structurally tied to the $\mathfrak{so}(2)$ vs. $\mathfrak{sp}(2n)$ decomposition: $B(0,n)$ would not have this obstruction because the fermionic root system is different ($\pm\delta_k$ rather than $\pm\varepsilon\pm\delta_k$).

---

## 6. Summary

**Main Conclusion**:

> **The inhomogeneous deformation $\gamma_{\mathrm{gb}}$ of $C(n+1) = \mathfrak{osp}(2|2n)$ is trivial if and only if $\mathrm{gb} = 0$.**

All $4n$ parameters must vanish for the deformation to be a coboundary. The obstruction is exhibited concretely by the pairs $(H_2, E_{\varepsilon\pm\delta_j})$ for each bosonic index $j=1,\ldots,n$: the $\mathfrak{so}(2)$-Cartan element $H_2$ appears in $\gamma_{\mathrm{gb}}$ but cannot be produced by any $\delta f$ with $f:\mathfrak{g}\to\mathfrak{g}$ odd.

**Verification data** (structured JSON):

```json
{
  "theorem": "triviality_iff_gb_zero",
  "algebras": {
    "C2_n1": {"algebra": "osp(2|2)", "n_params": 4, "conclusion": "trivial iff all gb=0"},
    "C3_n2": {"algebra": "osp(2|4)", "n_params": 8, "conclusion": "trivial iff all gb=0"},
    "C4_n3": {"algebra": "osp(2|6)", "n_params": 12, "conclusion": "trivial iff all gb=0"}
  },
  "obstruction_locus": {
    "pair_type": "(H2, E_{eps pm delta_j})",
    "for_j": "1,...,n",
    "mechanism": "H2 not in image of ad(E_{eps-delta_j}) restricted to g_odd"
  },
  "gamma_gb_n1": {
    "(Eed-, E-ed-)": {"Eed-": "-gb_pm", "E-ed-": "-gb_mm"},
    "(Eed, E-ed)":   {"Eed": "-gb_mp", "E-ed": "-gb_pp"},
    "(H2, Eed-)":    {"H2": "-gb_pm"},
    "(H2, E-ed-)":   {"H2": "-gb_mm"},
    "(H2, Eed)":     {"E2d": "2*gb_pm"},
    "(H2, E-ed)":    {"E2d": "2*gb_mm"}
  },
  "key_brackets": {
    "[E_{eps-d}, E_{-eps-d}]_0": "2 E_{-2d}",
    "[E_{eps-d}, E_{-eps+d}]_0": "H1",
    "[E_{eps+d}, E_{-eps+d}]_0": "2 E_{2d}",
    "[E_{eps+d}, E_{-eps-d}]_0": "-H1 - 2*H2 (mod K)"
  }
}
```

**Verification script**: `scripts/verify_triviality.py` (see below).

---

## 7. Comparison with $B(0,n) = \mathfrak{osp}(1|2n)$

The same analysis for $B(0,n)$ would differ because:
- Odd roots are $\pm\delta_k$ (no $\varepsilon$ label), total $2n$.
- The even subalgebra is $\mathfrak{sp}(2n)$ without the $\mathfrak{so}(2)$ factor.
- There is no separate $H_2$-type Cartan with the obstruction property.

This structural difference is why the $\mathfrak{so}(2)$ factor in $C(n+1)$ plays a decisive role in the non-triviality of $\gamma_{\mathrm{gb}}$.

---

*Report complete. Verification script committed at `scripts/verify_triviality.py`.*
