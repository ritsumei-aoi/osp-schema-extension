# Mathematical Analysis: Triviality of Inhomogeneous Deformations for C(n+1)

**Category**: Pure Mathematics / Research
**Status**: resolved — full report in `docs/issues/mathematical_proof.md` (2026-10-08, Claude Fable 5.1)

## Context & Background
You are provided with the fundamental mathematical definitions for the Lie superalgebra $\mathfrak{g} = C(n+1) \cong \mathfrak{osp}(2|2n)$ and its deformation theory.

Refer strictly to the following provided documents:
- `docs/math/Cn1_definition.md` (Algebra structure)
- `docs/math/C_inhomogeneous_definition.md` (Inhomogeneous $gb$ deformation)
- `docs/math/C_coboundary_definition.md` (Coboundary $\delta f$ deformation)

## The Problem
Consider two types of deformations of the bracket on $\mathfrak{g}$:
1.  **Inhomogeneous Deformation**: $\gamma_{gb}$, defined by the parameters $gb_{\sigma, j, s}$.
2.  **Coboundary Deformation**: $\gamma_{\delta f} = \delta f$, defined by an odd linear map $f: \mathfrak{g} \to \mathfrak{g}$.

**Goal**: Determine the necessary and sufficient conditions on the parameters $gb_{\sigma, j, s}$ for the deformation $\gamma_{gb}$ to be **trivial**. A deformation is trivial if and only if there exists an odd linear map $f$ such that $\gamma_{gb} = \delta f$.

## Requirements
1. **Rigor**: Analyze the mathematical consistency between the two deformation structures for $n=1, 2, 3$.
2. **Connectivity**: Generate structured data (e.g., Python dictionaries or JSON) representing your structure constants and gamma structures. Your output must be in a form that a human researcher can use to computationally verify your claims.
3. **Verification**: Investigate whether any non-zero configuration of $gb$ parameters can satisfy the triviality condition $\gamma_{gb} = \delta f$.
4. **Report**: Provide a rigorous mathematical report detailing your reasoning, any intermediate calculations, and your final conclusion.

## Deliverables
- A comprehensive analytical report appended to the Response section below.
- Reusable verification code or data artifacts committed to the repository.

## Response

**Result.** For every $n\ge 1$ and every $\mathrm{gb}\in\mathbf C^{4n}$ the inhomogeneous deformation is trivial: $\gamma_{\mathrm{gb}}=\delta f_{\mathrm{gb}}$ with the explicit odd map

$$f_{\mathrm{gb}}(\mathfrak{sp}(2n))=0,\qquad
f_{\mathrm{gb}}(a^\sigma b_k^t)=-\sum_j\big(\mathrm{gb}_{\sigma,j,-}\operatorname{sym}(b_j^+,b_k^t)-\mathrm{gb}_{\sigma,j,+}\operatorname{sym}(b_j^-,b_k^t)\big),$$
$$f_{\mathrm{gb}}(N_a)=\sum_j\big(\mathrm{gb}_{-,j,-}a^+b_j^+-\mathrm{gb}_{-,j,+}a^+b_j^--\mathrm{gb}_{+,j,-}a^-b_j^++\mathrm{gb}_{+,j,+}a^-b_j^-\big),$$

where $N_a=a^+a^--\tfrac12$ and $\operatorname{sym}$ is the symmetrised product. The necessary and sufficient condition on $\mathrm{gb}$ is therefore vacuous. At the same time $\gamma_{\mathrm{gb}}\neq0$ whenever $\mathrm{gb}\neq0$ (the map $\mathrm{gb}\mapsto\gamma_{\mathrm{gb}}$ has rank $4n$), so every non-zero parameter choice gives a non-zero but cohomologically trivial deformation.

**Why.** (1) Constructively: the shift $a^\sigma\mapsto a^\sigma+\kappa d_\sigma$, $d_\sigma=\sum_j(\mathrm{gb}_{\sigma,j,-}b_j^+-\mathrm{gb}_{\sigma,j,+}b_j^-)$, is an algebra homomorphism from the undeformed to the deformed oscillator algebra; restricted to the quadratic elements it reads $Z\mapsto Z+\kappa F(Z)$ and forces $\Gamma_{\mathrm{gb}}=-\delta F$, whence $\gamma_{\mathrm{gb}}=\delta(-\pi F)$. (2) Cohomologically: $H^p(\mathfrak g;\Pi\mathfrak g)=0$ for all $p$, because cohomology is concentrated in $\operatorname{ad}N_a$-weight $0$ and the $\operatorname{ad}N_a$-weight of every element of $C(n+1)$ equals its parity mod 2, so no odd cochain has weight zero.

**"Adjoint representation / up to scalar".** The $\kappa$-coefficient of a deformed bracket lives in $\mathfrak g\oplus\mathbf C1$; "as an adjoint representation" means projecting onto $\mathfrak g$ (canonical, since $\mathfrak g=[Q,Q]$), and the discarded scalar part is $\lambda([X,Y]_0)$ — itself a coboundary of a scalar 1-cochain, so with a $Q$-valued $f=-F$ the identity even holds with scalars included. With $f$ restricted to $\mathfrak g$-values the clause is necessary and sufficient to make the statement true.

**Verification ($n=1,2,3$).** `scripts/cn1_deformation.py` builds the deformed oscillator algebra with symbolic $\mathrm{gb}$, computes $c_{ij}^k$, $\gamma_{ij}^k(\mathrm{gb})$, the scalar parts, and $f_{\mathrm{gb}}$; checks the Lie superalgebra axioms, the cocycle property, $\gamma_{\mathrm{gb}}=\delta f_{\mathrm{gb}}$ exactly, solves $\delta\phi=\gamma$ independently by exact linear algebra for all $4n$ directions, and computes $H^1=H^2=0$ on both the weight-zero and the full odd complex ($Z^2=B^2=28,168,516$). `scripts/verify_artifacts.py` re-checks everything from the JSON files alone. Data: `artifacts/cn1_n{1,2,3}.json`, `artifacts/summary.json`, schema in `artifacts/README.md`.
