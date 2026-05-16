"""
C_generators.py

Frappat-notation basis and structure constants for C(n+1) = osp(2|2n).
Conventions follow Issue I01-1 (B1 standard Frappat basis, Option A PBW ordering)
and the Schema 1 v5.0 specification in docs/json_schema_specification.md.

Generator realization (implementation convention):
  H_k       = b_k^+ b_k^- - b_{k+1}^+ b_{k+1}^-   (1 <= k < n)
  H_n       = b_n^+ b_n^- + 1/2
  H_{n+1}   = a_1^+ a_1^- - 1/2
  E_{2δ_k}^±      = (b_k^±)^2
  E_{±δ_i±δ_j}^±  = b_i^± b_j^±               (i < j)
  E_{δ_i-δ_j}     = b_i^+ b_j^-               (i < j)
  E_{-δ_i+δ_j}    = b_i^- b_j^+               (i < j)
  E_{ε₁+δ_k}      = a_1^+ b_k^+  (E_eps1_del{k}_pp)
  E_{ε₁-δ_k}      = a_1^+ b_k^-  (E_eps1_del{k}_pm)
  E_{-(ε₁-δ_k)}   = a_1^- b_k^+  (E_eps1_del{k}_mp)
  E_{-(ε₁+δ_k)}   = a_1^- b_k^-  (E_eps1_del{k}_mm)

Key difference from B(0,n): no supplementary fermion a_0; instead uses
standard fermionic pair (a_1^+, a_1^-) with {a_1^-, a_1^+} = 1.
No sqrt(2) factors appear in structure constants.

Structure constants are computed directly from oscillator realizations
using exact rational arithmetic (Python Fraction).
"""

from typing import Dict, List, Tuple
from fractions import Fraction


# ---------------------------------------------------------------------------
# Basis
# ---------------------------------------------------------------------------

def build_C_basis(n: int) -> Tuple[List[str], List[str], Dict[str, int]]:
    """
    Build Frappat-notation basis for C(n+1) in PBW ordering (Option A).

    Ordering (PBW: κ < odd < even < K):
      Odd block:
        E_eps1_del{k}_pp (k=1..n)         # positive: ε₁ + δ_k
        E_eps1_del{k}_pm (k=1..n)         # positive: ε₁ - δ_k
        E_eps1_del{k}_mp (k=1..n)         # negative: -(ε₁ - δ_k)
        E_eps1_del{k}_mm (k=1..n)         # negative: -(ε₁ + δ_k)

      Even block:
        Cartan: H_1, ..., H_{n-1}, H_n, H_{n+1}
        Positive long: E_2del{k}_p (k=1..n)
        Positive short sum: E_del{i}_del{j}_pp (i<j)
        Negative long: E_2del{k}_m (k=1..n)
        Negative short sum: E_del{i}_del{j}_mm (i<j)
        Mixed: E_del{i}_del{j}_pm (i<j)
               E_del{i}_del{j}_mp (i<j)

    Returns:
        even_basis, odd_basis, parity dict
    """
    even_basis: List[str] = []
    odd_basis: List[str] = []
    parity: Dict[str, int] = {}

    # --- Odd block (fermionic) ---
    # E_eps1_del{k}_pp (ε₁ + δ_k)
    for k in range(1, n + 1):
        name = f"E_eps1_del{k}_pp"
        odd_basis.append(name)
        parity[name] = 1
    # E_eps1_del{k}_pm (ε₁ - δ_k)
    for k in range(1, n + 1):
        name = f"E_eps1_del{k}_pm"
        odd_basis.append(name)
        parity[name] = 1
    # E_eps1_del{k}_mp (-(ε₁ - δ_k))
    for k in range(1, n + 1):
        name = f"E_eps1_del{k}_mp"
        odd_basis.append(name)
        parity[name] = 1
    # E_eps1_del{k}_mm (-(ε₁ + δ_k))
    for k in range(1, n + 1):
        name = f"E_eps1_del{k}_mm"
        odd_basis.append(name)
        parity[name] = 1

    # --- Even block (bosonic) ---

    # Cartan: H_1..H_{n-1}, H_n, H_{n+1}
    for k in range(1, n + 1):
        name = f"H_{k}"
        even_basis.append(name)
        parity[name] = 0
    name = "H_{n+1}"
    even_basis.append(name)
    parity[name] = 0

    # Positive long roots: E_2del{k}_p
    for k in range(1, n + 1):
        name = f"E_2del{k}_p"
        even_basis.append(name)
        parity[name] = 0

    # Positive short sum roots: E_del{i}_del{j}_pp (i<j)
    for i in range(1, n + 1):
        for j in range(i + 1, n + 1):
            name = f"E_del{i}_del{j}_pp"
            even_basis.append(name)
            parity[name] = 0

    # Negative long roots: E_2del{k}_m
    for k in range(1, n + 1):
        name = f"E_2del{k}_m"
        even_basis.append(name)
        parity[name] = 0

    # Negative short sum roots: E_del{i}_del{j}_mm (i<j)
    for i in range(1, n + 1):
        for j in range(i + 1, n + 1):
            name = f"E_del{i}_del{j}_mm"
            even_basis.append(name)
            parity[name] = 0

    # Mixed roots: E_del{i}_del{j}_pm and E_del{i}_del{j}_mp (i<j)
    for i in range(1, n + 1):
        for j in range(i + 1, n + 1):
            name_pm = f"E_del{i}_del{j}_pm"
            name_mp = f"E_del{i}_del{j}_mp"
            even_basis.append(name_pm)
            even_basis.append(name_mp)
            parity[name_pm] = 0
            parity[name_mp] = 0

    return even_basis, odd_basis, parity


# ---------------------------------------------------------------------------
# Structure constants
# ---------------------------------------------------------------------------

def build_C_structure_constants(
    n: int,
) -> Dict[Tuple[str, str], Dict[str, str]]:
    """
    Compute structure constants for C(n+1) = osp(2|2n).

    Generator realisations (implementation convention):
      H_k   = b_k^+ b_k^- - b_{k+1}^+ b_{k+1}^-   (1 <= k < n)
      H_n   = b_n^+ b_n^- + 1/2
      H_{n+1} = a_1^+ a_1^- - 1/2

      E_{2δ_k}^±       = (b_k^±)^2
      E_{δ_i+δ_j}      = b_i^+ b_j^+   (i<j)  [E_del{i}_del{j}_pp]
      E_{-(δ_i+δ_j)}   = b_i^- b_j^-   (i<j)  [E_del{i}_del{j}_mm]
      E_{δ_i-δ_j}      = b_i^+ b_j^-   (i<j)  [E_del{i}_del{j}_pm]
      E_{-(δ_i-δ_j)}   = b_i^- b_j^+   (i<j)  [E_del{i}_del{j}_mp]

      E_{ε₁+δ_k}   = a_1^+ b_k^+   [E_eps1_del{k}_pp]
      E_{ε₁-δ_k}   = a_1^+ b_k^-   [E_eps1_del{k}_pm]
      E_{-(ε₁-δ_k)} = a_1^- b_k^+  [E_eps1_del{k}_mp]
      E_{-(ε₁+δ_k)} = a_1^- b_k^-  [E_eps1_del{k}_mm]

    Oscillator relations:
      [b_i^-, b_j^+] = δ_{ij}     (CCR)
      {a_1^-, a_1^+} = 1          (CAR)
      [b_i^±, a_1^±] = 0          (boson-fermion commute)

    Structure constants are given as exact rational strings.
    Brackets are indexed by (gen1, gen2) tuples.
    For odd-odd pairs the bracket is the anticommutator; otherwise commutator.
    """
    br: Dict[Tuple[str, str], Dict[str, str]] = {}

    # ---- Coefficient helpers (rational only, no sqrt(2)) ----

    def _parse_coeff(s: str) -> Fraction:
        """Parse rational coefficient string to Fraction."""
        if s == "0":
            return Fraction(0)
        return Fraction(s)

    def _format_coeff(f: Fraction) -> str:
        """Format Fraction to coefficient string."""
        if f.denominator == 1:
            return str(f.numerator)
        return f"{f.numerator}/{f.denominator}"

    def add(g1: str, g2: str, result: str, coeff: str) -> None:
        """Accumulate a coefficient into the bracket dict."""
        key = (g1, g2)
        if key not in br:
            br[key] = {}
        existing = _parse_coeff(br[key].get(result, "0"))
        new_coeff = _parse_coeff(coeff)
        total = existing + new_coeff
        if total == 0:
            br[key].pop(result, None)
        else:
            br[key][result] = _format_coeff(total)

    # ---- Cartan eigenvalue helpers ----

    def cartan_bose_eigenvalue(k: int, l: int, sign: int) -> int:
        """
        Eigenvalue of H_k (k=1..n) acting on b_l^{sign} where sign=+1 or -1.
        [H_k, b_l^+] = ev * b_l^+,  [H_k, b_l^-] = -ev * b_l^-
        """
        if k < n:
            ev = (1 if l == k else 0) - (1 if l == k + 1 else 0)
        else:  # k == n
            ev = (1 if l == n else 0)
        return sign * ev

    def cartan_fermi_eigenvalue(sign: int) -> int:
        """
        Eigenvalue of H_{n+1} = a_1^+ a_1^- - 1/2 acting on a_1^{sign}.
        [a_1^+ a_1^-, a_1^+] = a_1^+,  [a_1^+ a_1^-, a_1^-] = -a_1^-
        So [H_{n+1}, a_1^+] = +a_1^+,  [H_{n+1}, a_1^-] = -a_1^-
        """
        return sign

    # ---- Boson number operator in H-basis ----
    # b_k^+b_k^- = sum_{j=k}^n H_j - 1/2
    # The -1/2 constant term is a central element (κ or K).
    # We store it separately; caller uses add_H_terms and add_constant.

    def bose_number_H_terms(k: int) -> List[Tuple[str, str]]:
        """Return list of (H_j, '1') for the expansion of b_k^+b_k^-."""
        return [(f"H_{j}", "1") for j in range(k, n + 1)]

    # ===================================================================
    # Section 1: [H_k, E_eps1_del{l}_{*} ]   Cartan × odd
    # ===================================================================
    # For k = 1..n: H_k acts only on the bosonic factor b_l^{sign_beta}:
    #   [H_k, a_1^α b_l^β] = [H_k, b_l^β] a_1^α  (since [H_k, a_1^α] = 0)
    #                      = ev * a_1^α b_l^β
    #
    # For k = n+1: H_{n+1} acts only on the fermionic factor a_1^α:
    #   [H_{n+1}, a_1^α b_l^β] = [H_{n+1}, a_1^α] b_l^β  (since [H_{n+1}, b_l^β] = 0)
    #                          = +a_1^+ b_l^β if α=+, -a_1^- b_l^β if α=-
    #                          = sign_α * a_1^α b_l^β

    # Convention: suffix -> sign mapping
    # _pp: α=+ (p=+1), β=+ (p=+1)
    # _pm: α=+ (p=+1), β=- (m=-1)
    # _mp: α=- (m=-1), β=+ (p=+1)
    # _mm: α=- (m=-1), β=- (m=-1)

    for k in range(1, n + 1):  # bosonic Cartan H_1..H_n
        for l in range(1, n + 1):
            hk = f"H_{k}"
            # Four odd generators for index l
            odd_types = [
                (f"E_eps1_del{l}_pp", +1),
                (f"E_eps1_del{l}_pm", -1),
                (f"E_eps1_del{l}_mp", +1),
                (f"E_eps1_del{l}_mm", -1),
            ]
            for gen_name, beta_sign in odd_types:
                ev = cartan_bose_eigenvalue(k, l, beta_sign)
                if ev != 0:
                    add(hk, gen_name, gen_name, str(ev))
                    add(gen_name, hk, gen_name, str(-ev))

    # H_{n+1} acts on fermionic index
    h_np1 = "H_{n+1}"
    for l in range(1, n + 1):
        # α=+ (pp, pm): [H_{n+1}, a_1^+] = +a_1^+
        add(h_np1, f"E_eps1_del{l}_pp", f"E_eps1_del{l}_pp", "1")
        add(f"E_eps1_del{l}_pp", h_np1, f"E_eps1_del{l}_pp", "-1")
        add(h_np1, f"E_eps1_del{l}_pm", f"E_eps1_del{l}_pm", "1")
        add(f"E_eps1_del{l}_pm", h_np1, f"E_eps1_del{l}_pm", "-1")
        # α=- (mp, mm): [H_{n+1}, a_1^-] = -a_1^-
        add(h_np1, f"E_eps1_del{l}_mp", f"E_eps1_del{l}_mp", "-1")
        add(f"E_eps1_del{l}_mp", h_np1, f"E_eps1_del{l}_mp", "1")
        add(h_np1, f"E_eps1_del{l}_mm", f"E_eps1_del{l}_mm", "-1")
        add(f"E_eps1_del{l}_mm", h_np1, f"E_eps1_del{l}_mm", "1")

    # ===================================================================
    # Section 2: Odd-odd anticommutators
    #   {E_eps1_del{k}_αβ, E_eps1_del{l}_γδ}
    #   = {a_1^α, a_1^γ} * b_k^β b_l^δ
    #   where α,β,γ,δ ∈ {p=+1, m=-1}
    #
    #   {a_1^α, a_1^γ} ≠ 0 only when α ≠ γ, and then = 1.
    #
    #   So only cross-pair (α=p, γ=m) and (α=m, γ=p) are non-zero,
    #   and they give b_k^β b_l^δ as the result.
    # ===================================================================

    # The four odd suffixes
    odd_suffixes = ["pp", "pm", "mp", "mm"]

    def _add_bose_bilinear(g1, g2, r, s, coeff_str):
        """Add c * b_r^+ b_s^- to bracket (g1,g2)."""
        c = _parse_coeff(coeff_str)
        if c == 0:
            return
        if r == s:
            for t in range(r, n + 1):
                add(g1, g2, f"H_{t}", _format_coeff(c))
            add(g1, g2, "K", _format_coeff(-c / 2))
        elif r < s:
            add(g1, g2, f"E_del{r}_del{s}_pm", coeff_str)
        else:
            # r > s: b_r^+ b_s^- = b_s^- b_r^+ = E_del{s}_del{r}_mp (bosons commute)
            add(g1, g2, f"E_del{s}_del{r}_mp", _format_coeff(c))

    def _add_pp_bilinear(g1, g2, r, s, coeff_str):
        """Add c * b_r^+ b_s^+ to bracket (g1,g2)."""
        c = _parse_coeff(coeff_str)
        if c == 0:
            return
        if r == s:
            add(g1, g2, f"E_2del{r}_p", _format_coeff(c))
        elif r < s:
            add(g1, g2, f"E_del{r}_del{s}_pp", _format_coeff(c))
        else:
            add(g1, g2, f"E_del{s}_del{r}_pp", _format_coeff(c))

    def _add_mm_bilinear(g1, g2, r, s, coeff_str):
        """Add c * b_r^- b_s^- to bracket (g1,g2)."""
        c = _parse_coeff(coeff_str)
        if c == 0:
            return
        if r == s:
            add(g1, g2, f"E_2del{r}_m", _format_coeff(c))
        elif r < s:
            add(g1, g2, f"E_del{r}_del{s}_mm", _format_coeff(c))
        else:
            add(g1, g2, f"E_del{s}_del{r}_mm", _format_coeff(c))

    def _add_mp_bilinear(g1, g2, r, s, coeff_str):
        """Add c * b_r^- b_s^+ to bracket (g1,g2)."""
        c = _parse_coeff(coeff_str)
        if c == 0:
            return
        if r == s:
            for t in range(r, n + 1):
                add(g1, g2, f"H_{t}", _format_coeff(c))
            add(g1, g2, "K", _format_coeff(c / 2))
        elif r < s:
            add(g1, g2, f"E_del{r}_del{s}_mp", _format_coeff(c))
        else:
            # r > s: b_r^- b_s^+ = b_s^+ b_r^- = E_del{s}_del{r}_pm (bosons commute)
            add(g1, g2, f"E_del{s}_del{r}_pm", _format_coeff(c))

    def _odd_odd_partial(g1, g2, a_alpha, a_gamma, k_bos, l_bos, beta, delta):
        """
        Compute {a_1^alpha b_k^beta, a_1^gamma b_l^delta} and add to bracket.

        General formula:
          {a^alpha b_k^beta, a^gamma b_l^delta}
          = a^alpha a^gamma b_k^beta b_l^delta + a^gamma a^alpha b_l^delta b_k^beta

        When k!=l: bosons commute → = {a^alpha, a^gamma} * b_k^beta b_l^delta
        When k=l, beta=delta: → = {a^alpha, a^gamma} * b_k^beta b_k^beta
        When k=l, beta!=delta: need full expansion with a^gamma a^alpha term
        """
        if a_alpha == a_gamma:
            return  # {a^alpha, a^gamma} = 0

        # Determine a^gamma a^alpha term for full expansion
        if a_alpha == 'p' and a_gamma == 'm':
            # a^gamma a^alpha = a^-a^+ = 1 - a^+a^-
            fermi_swap_is_id = False
        else:  # (alpha,gamma) = (m,p): a^gamma a^alpha = a^+a^-
            fermi_swap_is_id = True

        if k_bos != l_bos:
            # Bosons commute: b_k^beta b_l^delta = b_l^delta b_k^beta
            # = anticommutator * b_k^beta b_l^delta = b_k^beta b_l^delta
            if beta == 'p' and delta == 'p':
                _add_pp_bilinear(g1, g2, k_bos, l_bos, "1")
            elif beta == 'm' and delta == 'm':
                _add_mm_bilinear(g1, g2, k_bos, l_bos, "1")
            elif beta == 'p' and delta == 'm':
                _add_bose_bilinear(g1, g2, k_bos, l_bos, "1")
            else:  # beta='m', delta='p'
                _add_mp_bilinear(g1, g2, k_bos, l_bos, "1")
        else:
            # k == l
            if beta == delta:
                # b_k^beta b_k^beta
                if beta == 'p':
                    _add_pp_bilinear(g1, g2, k_bos, k_bos, "1")
                else:
                    _add_mm_bilinear(g1, g2, k_bos, k_bos, "1")
            else:
                # k == l, beta != delta
                # b_k^delta b_k^beta = b_k^beta b_k^delta + s  where
                # s = +1 if (beta,delta) = (p,m), s = -1 if (beta,delta) = (m,p)
                # (from [b^-, b^+] = 1 rearranged)
                # = {a^alpha, a^gamma} b_k^beta b_k^delta + s * a^gamma a^alpha
                if beta == 'p' and delta == 'm':
                    _add_bose_bilinear(g1, g2, k_bos, k_bos, "1")
                else:  # beta='m', delta='p'
                    _add_mp_bilinear(g1, g2, k_bos, k_bos, "1")

                # + s * a^gamma a^alpha term
                # s = +1 if (beta,delta) = (p,m), else -1
                # a^+a^- = H_{n+1} + 1/2
                # a^-a^+ = 1 - (H_{n+1} + 1/2) = -H_{n+1} + 1/2
                s_sign = 1 if (beta == 'p' and delta == 'm') else -1
                if fermi_swap_is_id:
                    # a^gamma a^alpha = a^+a^-
                    add(g1, g2, "H_{n+1}", _format_coeff(Fraction(s_sign, 1)))
                    add(g1, g2, "K", _format_coeff(Fraction(s_sign, 2)))
                else:
                    # a^gamma a^alpha = a^-a^+ = 1 - a^+a^-
                    add(g1, g2, "H_{n+1}", _format_coeff(Fraction(-s_sign, 1)))
                    add(g1, g2, "K", _format_coeff(Fraction(s_sign, 2)))

    for k in range(1, n + 1):
        for l in range(1, n + 1):
            for s1 in odd_suffixes:
                a1 = s1[0]  # alpha
                b1 = s1[1]  # beta
                gen1 = f"E_eps1_del{k}_{s1}"
                for s2 in odd_suffixes:
                    a2 = s2[0]  # gamma
                    b2 = s2[1]  # delta
                    gen2 = f"E_eps1_del{l}_{s2}"
                    _odd_odd_partial(gen1, gen2, a1, a2, k, l, b1, b2)

    # ===================================================================
    # Section 3: [H_k, E_{±2δ_l}] = ±2*(δ_{kl} - δ_{k+1,l}) E_{2δ_l}^±
    #            (Same as B(0,n), H_{n+1} commutes with all even bosonic)
    # ===================================================================
    for k in range(1, n + 1):
        for l in range(1, n + 1):
            hk = f"H_{k}"
            ep = f"E_2del{l}_p"
            em = f"E_2del{l}_m"
            ev = cartan_bose_eigenvalue(k, l, +1)
            coeff_p = 2 * ev
            if coeff_p != 0:
                add(hk, ep, ep, str(coeff_p))
                add(ep, hk, ep, str(-coeff_p))
            ev_m = cartan_bose_eigenvalue(k, l, -1)
            coeff_m = 2 * ev_m
            if coeff_m != 0:
                add(hk, em, em, str(coeff_m))
                add(em, hk, em, str(-coeff_m))
    # [H_{n+1}, even_bosonic] = 0, so no entries needed.

    # ===================================================================
    # Section 4: [H_k, E_{±(δ_l+δ_p)}]  (l < p)
    # ===================================================================
    for k in range(1, n + 1):
        for l in range(1, n + 1):
            for p in range(l + 1, n + 1):
                hk = f"H_{k}"
                ep = f"E_del{l}_del{p}_pp"
                em = f"E_del{l}_del{p}_mm"
                ev = cartan_bose_eigenvalue(k, l, +1) + cartan_bose_eigenvalue(k, p, +1)
                if ev != 0:
                    add(hk, ep, ep, str(ev))
                    add(ep, hk, ep, str(-ev))
                ev_m = cartan_bose_eigenvalue(k, l, -1) + cartan_bose_eigenvalue(k, p, -1)
                if ev_m != 0:
                    add(hk, em, em, str(ev_m))
                    add(em, hk, em, str(-ev_m))

    # ===================================================================
    # Section 5: [H_k, E_{δ_l-δ_p}]  (l < p)
    # ===================================================================
    for k in range(1, n + 1):
        for l in range(1, n + 1):
            for p in range(l + 1, n + 1):
                hk = f"H_{k}"
                pm = f"E_del{l}_del{p}_pm"
                mp = f"E_del{l}_del{p}_mp"
                ev_pm = cartan_bose_eigenvalue(k, l, +1) + cartan_bose_eigenvalue(k, p, -1)
                ev_mp = cartan_bose_eigenvalue(k, l, -1) + cartan_bose_eigenvalue(k, p, +1)
                if ev_pm != 0:
                    add(hk, pm, pm, str(ev_pm))
                    add(pm, hk, pm, str(-ev_pm))
                if ev_mp != 0:
                    add(hk, mp, mp, str(ev_mp))
                    add(mp, hk, mp, str(-ev_mp))

    # ===================================================================
    # Section 6: [E_{2δ_k}, E_{-2δ_k}] = -4 * sum_{j=k}^n H_j
    #            (Same telescoping as B(0,n); no H_{n+1} term)
    # ===================================================================
    for k in range(1, n + 1):
        ep = f"E_2del{k}_p"
        em = f"E_2del{k}_m"
        for j in range(k, n + 1):
            add(ep, em, f"H_{j}", "-4")
            add(em, ep, f"H_{j}", "4")

    # ===================================================================
    # Section 7: [E_{2δ_k}^+, E_{-(δ_l+δ_p)}]  and  [E_{2δ_k}^-, E_{+(δ_l+δ_p)}]
    #            Same as B(0,n) section 7.
    # ===================================================================
    for k in range(1, n + 1):
        for l in range(1, n + 1):
            for p in range(l + 1, n + 1):
                ep_k  = f"E_2del{k}_p"
                em_k  = f"E_2del{k}_m"
                em_lp = f"E_del{l}_del{p}_mm"
                ep_lp = f"E_del{l}_del{p}_pp"

                # [(b_k^+)^2, b_l^- b_p^-]:
                if k == l:
                    res = f"E_del{k}_del{p}_pm"
                    add(ep_k, em_lp, res, "-2")
                    add(em_lp, ep_k, res, "2")
                if k == p:
                    res = f"E_del{l}_del{k}_mp"
                    add(ep_k, em_lp, res, "-2")
                    add(em_lp, ep_k, res, "2")

                # [(b_k^-)^2, b_l^+ b_p^+]:
                if k == l:
                    res = f"E_del{k}_del{p}_mp"
                    add(em_k, ep_lp, res, "2")
                    add(ep_lp, em_k, res, "-2")
                if k == p:
                    res = f"E_del{l}_del{k}_pm"
                    add(em_k, ep_lp, res, "2")
                    add(ep_lp, em_k, res, "-2")

    # ===================================================================
    # Section 7b: [E_{2δ_k}^+, E_{±(δ_l-δ_p)}]  and  [E_{2δ_k}^-, E_{±(δ_l-δ_p)}]
    # ===================================================================
    for k in range(1, n + 1):
        for l in range(1, n + 1):
            for p in range(l + 1, n + 1):
                ep_k = f"E_2del{k}_p"
                em_k = f"E_2del{k}_m"
                gen_mp = f"E_del{l}_del{p}_mp"  # b_l^- b_p^+
                gen_pm = f"E_del{l}_del{p}_pm"  # b_l^+ b_p^-

                # [(b_k^+)^2, b_l^-b_p^+] = -2δ_{kl} b_k^+b_p^+
                if k == l:
                    r, s = (k, p) if k < p else (p, k)
                    res = f"E_del{r}_del{s}_pp"
                    add(ep_k, gen_mp, res, "-2")
                    add(gen_mp, ep_k, res, "2")

                # [(b_k^+)^2, b_l^+b_p^-] = -2δ_{kp} b_k^+b_l^+
                if k == p:
                    r, s = (k, l) if k < l else (l, k)
                    res = f"E_del{r}_del{s}_pp"
                    add(ep_k, gen_pm, res, "-2")
                    add(gen_pm, ep_k, res, "2")

                # [(b_k^-)^2, b_l^-b_p^+] = +2δ_{kp} b_k^-b_l^-
                if k == p:
                    r, s = (k, l) if k < l else (l, k)
                    res = f"E_del{r}_del{s}_mm"
                    add(em_k, gen_mp, res, "2")
                    add(gen_mp, em_k, res, "-2")

                # [(b_k^-)^2, b_l^+b_p^-] = +2δ_{kl} b_k^-b_p^-
                if k == l:
                    r, s = (k, p) if k < p else (p, k)
                    res = f"E_del{r}_del{s}_mm"
                    add(em_k, gen_pm, res, "2")
                    add(gen_pm, em_k, res, "-2")

    # ===================================================================
    # Section 8: [E_{2δ_k}^±, E_eps1_del{l}_*]   Even × odd
    #
    #   [E_{2δ_k}^+, E_eps1_del{l}_{αβ}] = [b_k^+ b_k^+, a_1^α b_l^β]
    #     = a_1^α [b_k^+ b_k^+, b_l^β]  (since bosons commute with fermions)
    #     = a_1^α * (b_k^+[b_k^+,b_l^β] + [b_k^+,b_l^β]b_k^+)
    #
    #   For β = +: [b_k^+, b_l^+] = 0 → bracket is 0.
    #   For β = -: [b_k^+, b_l^-] = -δ_{kl} (since [b_l^-, b_k^+] = δ_{kl})
    #     = a_1^α * (-δ_{kl}*b_k^+ + b_k^+*(-δ_{kl}))
    #     = -2δ_{kl} * a_1^α b_k^+
    #     = -2δ_{kl} * (odd generator with α and +)  
    #     If α=p: E_eps1_del{k}_pp, if α=m: E_eps1_del{k}_mp
    #
    #   For [E_{2δ_k}^-, E_eps1_del{l}_{αβ}]:
    #     = a_1^α [b_k^- b_k^-, b_l^β]
    #   For β = -: [b_k^-, b_l^-] = 0 → bracket is 0.
    #   For β = +: [b_k^-, b_l^+] = δ_{kl}
    #     = a_1^α * (δ_{kl}*b_k^- + b_k^-*δ_{kl}) = 2δ_{kl} * a_1^α b_k^-
    #     = 2δ_{kl} * (odd generator with α and -)
    #     If α=p: E_eps1_del{k}_pm, if α=m: E_eps1_del{k}_mm
    # ===================================================================
    for k in range(1, n + 1):
        for l in range(1, n + 1):
            if k != l:
                continue
            ep_k = f"E_2del{k}_p"
            em_k = f"E_2del{k}_m"

            # [E_{2δ_k}^+, E_eps1_del{k}_pm] = -2 * E_eps1_del{k}_pp
            # [E_{2δ_k}^+, E_eps1_del{k}_mm] = -2 * E_eps1_del{k}_mp
            add(ep_k, f"E_eps1_del{k}_pm", f"E_eps1_del{k}_pp", "-2")
            add(f"E_eps1_del{k}_pm", ep_k, f"E_eps1_del{k}_pp", "2")
            add(ep_k, f"E_eps1_del{k}_mm", f"E_eps1_del{k}_mp", "-2")
            add(f"E_eps1_del{k}_mm", ep_k, f"E_eps1_del{k}_mp", "2")

            # [E_{2δ_k}^-, E_eps1_del{k}_pp] = 2 * E_eps1_del{k}_pm
            # [E_{2δ_k}^-, E_eps1_del{k}_mp] = 2 * E_eps1_del{k}_mm
            add(em_k, f"E_eps1_del{k}_pp", f"E_eps1_del{k}_pm", "2")
            add(f"E_eps1_del{k}_pp", em_k, f"E_eps1_del{k}_pm", "-2")
            add(em_k, f"E_eps1_del{k}_mp", f"E_eps1_del{k}_mm", "2")
            add(f"E_eps1_del{k}_mp", em_k, f"E_eps1_del{k}_mm", "-2")

    # ===================================================================
    # Section 9: Same-index cross brackets [E_del{k}_del{l}_{pp,mm,pm,mp}]
    #            NOTE: [pp, pm] and [pp, mp] are handled by Section 13
    #            (general formula [b_i^+b_j^+, b_k^+b_l^-] and [b_i^+b_j^+, b_k^-b_l^+]).
    #            Section 9 only covers cases NOT in Section 13:
    #            [mm, pm], [mm, mp], and [mp, pm].
    # ===================================================================
    for k in range(1, n + 1):
        for l in range(k + 1, n + 1):
            mm = f"E_del{k}_del{l}_mm"
            pm = f"E_del{k}_del{l}_pm"
            mp = f"E_del{k}_del{l}_mp"
            e2k_m = f"E_2del{k}_m"
            e2l_m = f"E_2del{l}_m"

            # [b_k^-b_l^-, b_k^+b_l^-] = (b_l^-)^2
            add(mm, pm, e2l_m, "1")
            add(pm, mm, e2l_m, "-1")

            # [b_k^-b_l^-, b_k^-b_l^+] = (b_k^-)^2
            add(mm, mp, e2k_m, "1")
            add(mp, mm, e2k_m, "-1")

            # [b_k^-b_l^+, b_k^+b_l^-] = -sum_{j=k}^{l-1} H_j
            for j in range(k, l):
                add(mp, pm, f"H_{j}", "-1")
                add(pm, mp, f"H_{j}", "1")

    # ===================================================================
    # Section 10: [E_del{i}_del{j}_pp, E_eps1_del{k}_{*}]  Even short × odd
    #             [b_i^+ b_j^+, a_1^α b_k^β]
    #             = a_1^α [b_i^+ b_j^+, b_k^β]
    #
    #   For β = +: [b_i^+ b_j^+, b_k^+] = 0 (all creation)
    #   For β = -: [b_i^+ b_j^+, b_k^-]
    #     = b_i^+[b_j^+,b_k^-] + [b_i^+,b_k^-]b_j^+
    #     = -δ_{jk}*b_i^+ - δ_{ik}*b_j^+  (since [b^+,b^-] = -δ)
    #
    #   Result: -δ_{jk} * a_1^α b_i^+ - δ_{ik} * a_1^α b_j^+
    #   = -δ_{jk} * E_eps1_del{i}_{αp} - δ_{ik} * E_eps1_del{j}_{αp}
    #
    #   [E_del{i}_del{j}_mm, E_eps1_del{k}_{αβ}]
    #   = a_1^α [b_i^- b_j^-, b_k^β]
    #
    #   For β = -: [b_i^- b_j^-, b_k^-] = 0 (all annihilation)
    #   For β = +: [b_i^- b_j^-, b_k^+]
    #     = b_i^-[b_j^-,b_k^+] + [b_i^-,b_k^+]b_j^-
    #     = δ_{jk}*b_i^- + δ_{ik}*b_j^-
    #
    #   Result: δ_{jk} * a_1^α b_i^- + δ_{ik} * a_1^α b_j^-
    #   = δ_{jk} * E_eps1_del{i}_{αm} + δ_{ik} * E_eps1_del{j}_{αm}
    # ===================================================================
    for i in range(1, n + 1):
        for j in range(i + 1, n + 1):
            pp = f"E_del{i}_del{j}_pp"
            mm = f"E_del{i}_del{j}_mm"
            for k in range(1, n + 1):
                # [E_del{i}_del{j}_pp, E_eps1_del{k}_{αm}] for β=- (m suffix)
                for alpha, a_suffix in [('p', 'p'), ('m', 'm')]:
                    gen_odd_m = f"E_eps1_del{k}_{a_suffix}m"
                    if j == k:
                        res_i = f"E_eps1_del{i}_{a_suffix}p"
                        add(pp, gen_odd_m, res_i, "-1")
                        add(gen_odd_m, pp, res_i, "1")
                    if i == k:
                        res_j = f"E_eps1_del{j}_{a_suffix}p"
                        add(pp, gen_odd_m, res_j, "-1")
                        add(gen_odd_m, pp, res_j, "1")

                # [E_del{i}_del{j}_mm, E_eps1_del{k}_{αp}] for β=+ (p suffix)
                for alpha, a_suffix in [('p', 'p'), ('m', 'm')]:
                    gen_odd_p = f"E_eps1_del{k}_{a_suffix}p"
                    if j == k:
                        res_i = f"E_eps1_del{i}_{a_suffix}m"
                        add(mm, gen_odd_p, res_i, "1")
                        add(gen_odd_p, mm, res_i, "-1")
                    if i == k:
                        res_j = f"E_eps1_del{j}_{a_suffix}m"
                        add(mm, gen_odd_p, res_j, "1")
                        add(gen_odd_p, mm, res_j, "-1")

    # ===================================================================
    # Section 11: [E_del{i}_del{j}_pm, E_eps1_del{k}_{*}]  Mixed even × odd
    #
    #   [b_i^+ b_j^-, a_1^α b_k^β]
    #   = a_1^α [b_i^+ b_j^-, b_k^β]
    #
    #   For β = +: [b_i^+ b_j^-, b_k^+] = b_i^+[b_j^-,b_k^+] + [b_i^+,b_k^+]b_j^-
    #     = δ_{jk} * b_i^+  (since [b_i^+,b_k^+] = 0)
    #   Result: δ_{jk} * a_1^α b_i^+ = δ_{jk} * E_eps1_del{i}_{αp}
    #
    #   For β = -: [b_i^+ b_j^-, b_k^-] = b_i^+[b_j^-,b_k^-] + [b_i^+,b_k^-]b_j^-
    #     = -δ_{ik} * b_j^-  (since [b_i^+,b_k^-] = -δ_{ik})
    #   Result: -δ_{ik} * a_1^α b_j^- = -δ_{ik} * E_eps1_del{j}_{αm}
    #
    #   [b_i^- b_j^+, a_1^α b_k^β]
    #   For β = +: [b_i^- b_j^+, b_k^+] = b_i^-[b_j^+,b_k^+] + [b_i^-,b_k^+]b_j^+
    #     = δ_{ik} * b_j^+
    #   Result: δ_{ik} * a_1^α b_j^+ = δ_{ik} * E_eps1_del{j}_{αp}
    #
    #   For β = -: [b_i^- b_j^+, b_k^-] = b_i^-[b_j^+,b_k^-] + [b_i^-,b_k^-]b_j^+
    #     = -δ_{jk} * b_i^-
    #   Result: -δ_{jk} * a_1^α b_i^- = -δ_{jk} * E_eps1_del{i}_{αm}
    # ===================================================================
    for i in range(1, n + 1):
        for j in range(i + 1, n + 1):
            pm = f"E_del{i}_del{j}_pm"
            mp = f"E_del{i}_del{j}_mp"
            for k in range(1, n + 1):
                for alpha, a_suffix in [('p', 'p'), ('m', 'm')]:
                    # [pm, β=+]: β=p suffix
                    gen_odd_p = f"E_eps1_del{k}_{a_suffix}p"
                    gen_odd_m = f"E_eps1_del{k}_{a_suffix}m"

                    # δ_{jk} * E_eps1_del{i}_{αp}
                    if j == k:
                        res = f"E_eps1_del{i}_{a_suffix}p"
                        add(pm, gen_odd_p, res, "1")
                        add(gen_odd_p, pm, res, "-1")

                    # -δ_{ik} * E_eps1_del{j}_{αm}
                    if i == k:
                        res = f"E_eps1_del{j}_{a_suffix}m"
                        add(pm, gen_odd_m, res, "-1")
                        add(gen_odd_m, pm, res, "1")

                    # [mp, β=+]: δ_{ik} * E_eps1_del{j}_{αp}
                    if i == k:
                        res = f"E_eps1_del{j}_{a_suffix}p"
                        add(mp, gen_odd_p, res, "1")
                        add(gen_odd_p, mp, res, "-1")

                    # [mp, β=-]: -δ_{jk} * E_eps1_del{i}_{αm}
                    if j == k:
                        res = f"E_eps1_del{i}_{a_suffix}m"
                        add(mp, gen_odd_m, res, "-1")
                        add(gen_odd_m, mp, res, "1")

    # ===================================================================
    # Section 12: [E_del{i}_del{j}_pp, E_del{k}_del{l}_mm]  Short × short
    #             Same as B(0,n) section 13.
    #
    #   [b_i^+ b_j^+, b_k^- b_l^-] (i<j, k<l)
    #   = -δ_{ik} b_j^+ b_l^- - δ_{il} b_j^+ b_k^- 
    #     - δ_{jk} b_i^+ b_l^- - δ_{jl} b_i^+ b_k^-
    #     - δ_{jl}δ_{ik} - δ_{il}δ_{jk}
    #
    #   where [b_i^+, b_k^-] = -δ_{ik}. Derived from [AB, CD] expansion.
    # ===================================================================
    for i in range(1, n + 1):
        for j in range(i + 1, n + 1):
            for k in range(1, n + 1):
                for l in range(k + 1, n + 1):
                    pp_ij = f"E_del{i}_del{j}_pp"
                    mm_kl = f"E_del{k}_del{l}_mm"

                    def _neg(coeff_str: str) -> str:
                        """Negate a coefficient string via Fraction."""
                        return _format_coeff(-_parse_coeff(coeff_str))

                    def _add_bilinear(g1, g2, r: int, s: int, coeff_str: str) -> None:
                        """Add c * b_r^+ b_s^- to bracket (g1,g2)."""
                        if coeff_str == "0":
                            return
                        neg_str = _neg(coeff_str)
                        if r == s:
                            # b_r^+ b_r^- = sum_{t=r}^n H_t - 1/2
                            for t in range(r, n + 1):
                                add(g1, g2, f"H_{t}", coeff_str)
                                add(g2, g1, f"H_{t}", neg_str)
                            # constant term (anti-symmetric: reverse direction is negated)
                            c = _parse_coeff(coeff_str)
                            const_str = _format_coeff(-c / 2)
                            neg_const_str = _neg(const_str)
                            add(g1, g2, "K", const_str)
                            add(g2, g1, "K", neg_const_str)
                        else:
                            # b_r^+ b_s^- → mixed generator
                            if r < s:
                                add(g1, g2, f"E_del{r}_del{s}_pm", coeff_str)
                                add(g2, g1, f"E_del{r}_del{s}_pm", neg_str)
                            else:  # r > s
                                # b_r^+ b_s^- = b_s^- b_r^+ (bosons commute) = E_del{s}_del{r}_mp
                                # Coefficient is c for (g1,g2), -c for (g2,g1)
                                add(g1, g2, f"E_del{s}_del{r}_mp", coeff_str)
                                add(g2, g1, f"E_del{s}_del{r}_mp", neg_str)

                    # -δ_{ik} * b_j^+ b_l^-
                    if i == k:
                        _add_bilinear(pp_ij, mm_kl, j, l, "-1")

                    # -δ_{il} * b_j^+ b_k^-
                    if i == l:
                        _add_bilinear(pp_ij, mm_kl, j, k, "-1")

                    # -δ_{jk} * b_i^+ b_l^-
                    if j == k:
                        _add_bilinear(pp_ij, mm_kl, i, l, "-1")

                    # -δ_{jl} * b_i^+ b_k^-
                    if j == l:
                        _add_bilinear(pp_ij, mm_kl, i, k, "-1")

                    # -δ_{jl}δ_{ik} constant term (same-generator case: i==k and j==l)
                    if i == k and j == l:
                        add(pp_ij, mm_kl, "K", "-1")
                        add(mm_kl, pp_ij, "K", "1")

    # ===================================================================
    # Section 13: [b_i^+ b_j^+, b_k^+ b_l^-] and [b_i^+ b_j^+, b_k^- b_l^+]
    #
    #   [b_i^+ b_j^+, b_k^+ b_l^-] = -δ_{jl} * b_k^+ b_i^+ - δ_{il} * b_k^+ b_j^+  (i<j, k<l)
    #   [b_i^+ b_j^+, b_k^- b_l^+] = -δ_{jk} * b_i^+ b_l^+ - δ_{ik} * b_j^+ b_l^+
    # ===================================================================
    for i in range(1, n + 1):
        for j in range(i + 1, n + 1):
            pp_ij = f"E_del{i}_del{j}_pp"
            for k in range(1, n + 1):
                for l in range(k + 1, n + 1):
                    pm_kl = f"E_del{k}_del{l}_pm"
                    mp_kl = f"E_del{k}_del{l}_mp"

                    # [b_i^+ b_j^+, b_k^+ b_l^-] = -δ_{jl} * b_k^+ b_i^+ - δ_{il} * b_k^+ b_j^+
                    if j == l:
                        # -δ_{jl} * b_k^+ b_i^+  (normal order: b_k^+ b_i^+)
                        if i == k:
                            add(pp_ij, pm_kl, f"E_2del{i}_p", "-1")
                            add(pm_kl, pp_ij, f"E_2del{i}_p", "1")
                        elif i < k:
                            add(pp_ij, pm_kl, f"E_del{i}_del{k}_pp", "-1")
                            add(pm_kl, pp_ij, f"E_del{i}_del{k}_pp", "1")
                        else:  # i > k
                            add(pp_ij, pm_kl, f"E_del{k}_del{i}_pp", "-1")
                            add(pm_kl, pp_ij, f"E_del{k}_del{i}_pp", "1")

                    if i == l:
                        # -δ_{il} * b_k^+ b_j^+  (normal order: b_k^+ b_j^+)
                        if k == j:
                            add(pp_ij, pm_kl, f"E_2del{j}_p", "-1")
                            add(pm_kl, pp_ij, f"E_2del{j}_p", "1")
                        elif k < j:
                            add(pp_ij, pm_kl, f"E_del{k}_del{j}_pp", "-1")
                            add(pm_kl, pp_ij, f"E_del{k}_del{j}_pp", "1")
                        else:  # k > j
                            add(pp_ij, pm_kl, f"E_del{j}_del{k}_pp", "-1")
                            add(pm_kl, pp_ij, f"E_del{j}_del{k}_pp", "1")

                    # [b_i^+ b_j^+, b_k^- b_l^+] = -δ_{jk} * b_i^+ b_l^+ - δ_{ik} * b_j^+ b_l^+
                    if j == k:
                        # -δ_{jk} * b_i^+ b_l^+  (normal order: b_i^+ b_l^+)
                        if i == l:
                            add(pp_ij, mp_kl, f"E_2del{i}_p", "-1")
                            add(mp_kl, pp_ij, f"E_2del{i}_p", "1")
                        elif i < l:
                            add(pp_ij, mp_kl, f"E_del{i}_del{l}_pp", "-1")
                            add(mp_kl, pp_ij, f"E_del{i}_del{l}_pp", "1")
                        else:  # i > l
                            add(pp_ij, mp_kl, f"E_del{l}_del{i}_pp", "-1")
                            add(mp_kl, pp_ij, f"E_del{l}_del{i}_pp", "1")

                    if i == k:
                        # -δ_{ik} * b_j^+ b_l^+  (normal order: b_j^+ b_l^+)
                        if j == l:
                            add(pp_ij, mp_kl, f"E_2del{j}_p", "-1")
                            add(mp_kl, pp_ij, f"E_2del{j}_p", "1")
                        elif j < l:
                            add(pp_ij, mp_kl, f"E_del{j}_del{l}_pp", "-1")
                            add(mp_kl, pp_ij, f"E_del{j}_del{l}_pp", "1")
                        else:  # j > l
                            add(pp_ij, mp_kl, f"E_del{l}_del{j}_pp", "-1")
                            add(mp_kl, pp_ij, f"E_del{l}_del{j}_pp", "1")

    # ===================================================================
    # Section 14: [E_{2δ_k}^+, E_del{i}_del{j}_pp] = 0 (all creation, commute)
    #             [E_{2δ_k}^-, E_del{i}_del{j}_mm] = 0 (all annihilation, commute)
    #             These are zero by default.

    # ===================================================================
    # Section 15: [E_{2δ_k}^+, E_del{i}_del{j}_mm]  Long × short negative
    #             Same as B(0,n) section 7 (already handled above).

    # ===================================================================
    # Section 18: [E_del{i}_del{j}_mp, E_del{k}_del{l}_pm]  Mixed × mixed (different indices)
    #             [b_i^- b_j^+, b_k^+ b_l^-] (i<j, k<l)
    #             = δ_{ik} * b_j^+ b_l^- - δ_{jl} * b_k^+ b_i^-
    #
    #             Derivation: [AB,CD] = A[B,C]D + [A,C]BD + CA[B,D] + C[A,D]B
    #             A=b_i^-, B=b_j^+, C=b_k^+, D=b_l^-
    #             [B,C]=0, [A,C]=δ_{ik}, [B,D]=-δ_{jl}, [A,D]=0
    #             → δ_{ik} * b_j^+ b_l^- - δ_{jl} * b_k^+ b_i^-
    #
    #             NOTE: Same-index case (i,j)=(k,l) is handled by Section 9.
    #             Here we handle the cross-index cases.
    # ===================================================================
    for i in range(1, n + 1):
        for j in range(i + 1, n + 1):
            mp_ij = f"E_del{i}_del{j}_mp"
            for k in range(1, n + 1):
                for l in range(k + 1, n + 1):
                    if i == k and j == l:
                        continue  # handled by Section 9
                    pm_kl = f"E_del{k}_del{l}_pm"

                    # δ_{ik} * b_j^+ b_l^-
                    if i == k:
                        if j == l:
                            # r=s=j → H_t and K
                            for t in range(j, n + 1):
                                add(mp_ij, pm_kl, f"H_{t}", "1")
                                add(pm_kl, mp_ij, f"H_{t}", "-1")
                            add(mp_ij, pm_kl, "K", "-1/2")
                            add(pm_kl, mp_ij, "K", "1/2")
                        elif j < l:
                            add(mp_ij, pm_kl, f"E_del{j}_del{l}_pm", "1")
                            add(pm_kl, mp_ij, f"E_del{j}_del{l}_pm", "-1")
                        else:  # j > l
                            add(mp_ij, pm_kl, f"E_del{l}_del{j}_mp", "1")
                            add(pm_kl, mp_ij, f"E_del{l}_del{j}_mp", "-1")

                    # -δ_{jl} * b_k^+ b_i^-  (mixed generator, not pp)
                    if j == l:
                        if k == i:
                            # b_i^+ b_i^- = sum_{m=i}^n H_m - 1/2
                            for t in range(i, n + 1):
                                add(mp_ij, pm_kl, f"H_{t}", "-1")
                                add(pm_kl, mp_ij, f"H_{t}", "1")
                            add(mp_ij, pm_kl, "K", "1/2")
                            add(pm_kl, mp_ij, "K", "-1/2")
                        elif k < i:
                            # b_k^+ b_i^- = E_del{k}_del{i}_pm
                            add(mp_ij, pm_kl, f"E_del{k}_del{i}_pm", "-1")
                            add(pm_kl, mp_ij, f"E_del{k}_del{i}_pm", "1")
                        else:  # k > i
                            # b_k^+ b_i^- = b_i^- b_k^+ = E_del{i}_del{k}_mp
                            add(mp_ij, pm_kl, f"E_del{i}_del{k}_mp", "-1")
                            add(pm_kl, mp_ij, f"E_del{i}_del{k}_mp", "1")

    # ===================================================================
    # Section 19: Cross-index even-even brackets (share exactly one index)
    #             Process each unordered pair (ij, kl) only once.
    #             These are ALL cross-index (i,j)≠(k,l) cases for six types:
    #
    #   Type C: [b_i^-b_j^-, b_k^+b_l^-] = δ_{jk}*b_i^-b_l^- + δ_{ik}*b_j^-b_l^-
    #                                                                   (mm×pm)
    #   Type D: [b_i^-b_j^-, b_k^-b_l^+] = δ_{jl}*b_k^-b_i^- + δ_{il}*b_k^-b_j^-
    #                                                                   (mm×mp)
    #   Type E: [b_i^-b_j^+, b_k^-b_l^+] = δ_{il}*b_k^-b_j^+ - δ_{jk}*b_i^-b_l^+
    #                                                                   (mp×mp)
    #   Type F: [b_i^+b_j^-, b_k^+b_l^-] = δ_{jk}*b_i^+b_l^- - δ_{il}*b_k^+b_j^-
    #                                                                   (pm×pm)
    #
    #   Types A and B (pp×pm, pp×mp) are already handled by Section 13.
    #   Section 12 already handles all pp×mm cases.
    #   Section 18 already handles all mp×pm cases (cross-index).
    #   Section 9 handles same-index mm×pm, mm×mp, mp×pm.
    #
    #   NOTE: Types E and F only process when (i,j) < (k,l) to avoid
    #         double-counting symmetric cases. Types C and D use the
    #         asymmetric formula [mm, pm] and [mm, mp] respectively,
    #         so they naturally produce each unordered pair once.
    # ===================================================================
    for i in range(1, n + 1):
        for j in range(i + 1, n + 1):
            for k in range(1, n + 1):
                for l in range(k + 1, n + 1):
                    if i == k and j == l:
                        continue  # same-index, handled elsewhere

                    mm_ij = f"E_del{i}_del{j}_mm"
                    mp_ij = f"E_del{i}_del{j}_mp"
                    pm_ij = f"E_del{i}_del{j}_pm"

                    # --- Type C: [mm_ij, pm_kl] = δ_{jk}*b_i^-b_l^- + δ_{ik}*b_j^-b_l^-
                    if j == k:
                        if i == l:
                            add(mm_ij, f"E_del{k}_del{l}_pm", f"E_2del{i}_m", "1")
                            add(f"E_del{k}_del{l}_pm", mm_ij, f"E_2del{i}_m", "-1")
                        elif i < l:
                            add(mm_ij, f"E_del{k}_del{l}_pm", f"E_del{i}_del{l}_mm", "1")
                            add(f"E_del{k}_del{l}_pm", mm_ij, f"E_del{i}_del{l}_mm", "-1")
                        else:  # i > l
                            add(mm_ij, f"E_del{k}_del{l}_pm", f"E_del{l}_del{i}_mm", "1")
                            add(f"E_del{k}_del{l}_pm", mm_ij, f"E_del{l}_del{i}_mm", "-1")
                    if i == k:
                        if j == l:
                            add(mm_ij, f"E_del{k}_del{l}_pm", f"E_2del{j}_m", "1")
                            add(f"E_del{k}_del{l}_pm", mm_ij, f"E_2del{j}_m", "-1")
                        elif j < l:
                            add(mm_ij, f"E_del{k}_del{l}_pm", f"E_del{j}_del{l}_mm", "1")
                            add(f"E_del{k}_del{l}_pm", mm_ij, f"E_del{j}_del{l}_mm", "-1")
                        else:  # j > l
                            add(mm_ij, f"E_del{k}_del{l}_pm", f"E_del{l}_del{j}_mm", "1")
                            add(f"E_del{k}_del{l}_pm", mm_ij, f"E_del{l}_del{j}_mm", "-1")

                    # --- Type D: [mm_ij, mp_kl] = δ_{jl}*b_k^-b_i^- + δ_{il}*b_k^-b_j^-
                    if j == l:
                        if i == k:
                            add(mm_ij, f"E_del{k}_del{l}_mp", f"E_2del{i}_m", "1")
                            add(f"E_del{k}_del{l}_mp", mm_ij, f"E_2del{i}_m", "-1")
                        elif i < k:
                            add(mm_ij, f"E_del{k}_del{l}_mp", f"E_del{i}_del{k}_mm", "1")
                            add(f"E_del{k}_del{l}_mp", mm_ij, f"E_del{i}_del{k}_mm", "-1")
                        else:  # i > k
                            add(mm_ij, f"E_del{k}_del{l}_mp", f"E_del{k}_del{i}_mm", "1")
                            add(f"E_del{k}_del{l}_mp", mm_ij, f"E_del{k}_del{i}_mm", "-1")
                    if i == l:
                        if j == k:
                            add(mm_ij, f"E_del{k}_del{l}_mp", f"E_2del{j}_m", "1")
                            add(f"E_del{k}_del{l}_mp", mm_ij, f"E_2del{j}_m", "-1")
                        elif j < k:
                            add(mm_ij, f"E_del{k}_del{l}_mp", f"E_del{j}_del{k}_mm", "1")
                            add(f"E_del{k}_del{l}_mp", mm_ij, f"E_del{j}_del{k}_mm", "-1")
                        else:  # j > k
                            add(mm_ij, f"E_del{k}_del{l}_mp", f"E_del{k}_del{j}_mm", "1")
                            add(f"E_del{k}_del{l}_mp", mm_ij, f"E_del{k}_del{j}_mm", "-1")

                    # --- Types E and F: only process when (i,j) < (k,l) ---
                    if (i, j) >= (k, l):
                        continue

                    mp_kl = f"E_del{k}_del{l}_mp"
                    pm_kl = f"E_del{k}_del{l}_pm"

                    # --- Type E: [mp_ij, mp_kl] = δ_{il}*b_k^-b_j^+ - δ_{jk}*b_i^-b_l^+
                    if i == l:
                        if k == j:
                            for t in range(j, n + 1):
                                add(mp_ij, mp_kl, f"H_{t}", "1")
                                add(mp_kl, mp_ij, f"H_{t}", "-1")
                            add(mp_ij, mp_kl, "K", "-1/2")
                            add(mp_kl, mp_ij, "K", "1/2")
                        elif k < j:
                            add(mp_ij, mp_kl, f"E_del{k}_del{j}_mp", "1")
                            add(mp_kl, mp_ij, f"E_del{k}_del{j}_mp", "-1")
                        else:  # k > j
                            add(mp_ij, mp_kl, f"E_del{j}_del{k}_pm", "1")
                            add(mp_kl, mp_ij, f"E_del{j}_del{k}_pm", "-1")
                    if j == k:
                        if i == l:
                            for t in range(i, n + 1):
                                add(mp_ij, mp_kl, f"H_{t}", "-1")
                                add(mp_kl, mp_ij, f"H_{t}", "1")
                            add(mp_ij, mp_kl, "K", "1/2")
                            add(mp_kl, mp_ij, "K", "-1/2")
                        elif i < l:
                            add(mp_ij, mp_kl, f"E_del{i}_del{l}_mp", "-1")
                            add(mp_kl, mp_ij, f"E_del{i}_del{l}_mp", "1")
                        else:  # i > l
                            add(mp_ij, mp_kl, f"E_del{l}_del{i}_pm", "-1")
                            add(mp_kl, mp_ij, f"E_del{l}_del{i}_pm", "1")

                    # --- Type F: [pm_ij, pm_kl] = δ_{jk}*b_i^+b_l^- - δ_{il}*b_k^+b_j^-
                    if j == k:
                        if i == l:
                            for t in range(i, n + 1):
                                add(pm_ij, pm_kl, f"H_{t}", "1")
                                add(pm_kl, pm_ij, f"H_{t}", "-1")
                            add(pm_ij, pm_kl, "K", "-1/2")
                            add(pm_kl, pm_ij, "K", "1/2")
                        elif i < l:
                            add(pm_ij, pm_kl, f"E_del{i}_del{l}_pm", "1")
                            add(pm_kl, pm_ij, f"E_del{i}_del{l}_pm", "-1")
                        else:  # i > l
                            add(pm_ij, pm_kl, f"E_del{l}_del{i}_mp", "1")
                            add(pm_kl, pm_ij, f"E_del{l}_del{i}_mp", "-1")
                    if i == l:
                        if k == j:
                            for t in range(j, n + 1):
                                add(pm_ij, pm_kl, f"H_{t}", "-1")
                                add(pm_kl, pm_ij, f"H_{t}", "1")
                            add(pm_ij, pm_kl, "K", "1/2")
                            add(pm_kl, pm_ij, "K", "-1/2")
                        elif k < j:
                            add(pm_ij, pm_kl, f"E_del{k}_del{j}_pm", "-1")
                            add(pm_kl, pm_ij, f"E_del{k}_del{j}_pm", "1")
                        else:  # k > j
                            add(pm_ij, pm_kl, f"E_del{j}_del{k}_mp", "-1")
                            add(pm_kl, pm_ij, f"E_del{j}_del{k}_mp", "1")

    # ===================================================================
    # Section 16: [H_{n+1}, odd] — already handled in Section 1.
    #             [H_{n+1}, even] = 0 for all even generators (since H_{n+1}
    #             involves only a_1^± which commutes with all bosonic generators).

    # ===================================================================
    # Section 17: Even-even: long × long (different indices) — mostly zero.
    #             [(b_k^+)^2, (b_l^+)^2] = 0 for k≠l (commuting bosons).
    #             [(b_k^+)^2, (b_l^-)^2] for k≠l:
    #               = sum_{r} [b_k^+b_k^+, b_l^-b_l^-]
    #               = [b_k^+, b_l^-]b_k^+b_l^- + b_k^+[b_k^+, b_l^-]b_l^- 
    #                 + b_l^-[b_k^+, b_l^-]b_k^+ + ... 
    #               All terms vanish since [b_k^+, b_l^-] = 0 for k≠l.
    #             So these are zero by default for k≠l.

    # Remove empty entries
    br = {k: v for k, v in br.items() if v}
    return br
