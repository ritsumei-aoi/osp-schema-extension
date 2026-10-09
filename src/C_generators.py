"""
C_generators.py: Build Schema 1 JSON for C(n+1) = osp(2|2n).

Generator labels follow handover/notation.md conventions.
Structure constants are computed from the oscillator realization using
CAR (a_1^+, a_1^-) and CCR (b_k^+, b_k^-) relations.
"""

import json
import itertools
from fractions import Fraction
from datetime import date


def build_basis(n):
    """Return (even_basis, odd_basis) lists for C(n+1) with bosonic rank n."""
    even = []
    odd = []

    # Cartan generators H_1, ..., H_{n+1}
    for k in range(1, n + 2):
        even.append(f"H_{k}")

    # Raising even: E_2del{k}_p, E_del{i}_del{j}_pp (i<j)
    for k in range(1, n + 1):
        even.append(f"E_2del{k}_p")
    for i, j in itertools.combinations(range(1, n + 1), 2):
        even.append(f"E_del{i}_del{j}_pp")

    # Lowering even: E_2del{k}_m, E_del{i}_del{j}_mm
    for k in range(1, n + 1):
        even.append(f"E_2del{k}_m")
    for i, j in itertools.combinations(range(1, n + 1), 2):
        even.append(f"E_del{i}_del{j}_mm")

    # Mixed even: E_del{i}_del{j}_pm, E_del{i}_del{j}_mp (i<j)
    for i, j in itertools.combinations(range(1, n + 1), 2):
        even.append(f"E_del{i}_del{j}_pm")
    for i, j in itertools.combinations(range(1, n + 1), 2):
        even.append(f"E_del{i}_del{j}_mp")

    # Odd generators: E_eps1_del{k}_{pp,pm,mp,mm}
    for k in range(1, n + 1):
        for sign in ["pp", "pm", "mp", "mm"]:
            odd.append(f"E_eps1_del{k}_{sign}")

    return even, odd


def parity_of(label):
    """Return parity (0=even, 1=odd) of a generator label."""
    if label.startswith("E_eps1"):
        return 1
    return 0


def build_parity_dict(even, odd):
    d = {}
    for g in even:
        d[g] = 0
    for g in odd:
        d[g] = 1
    return d


def compute_structure_constants(n, even, odd):
    """
    Compute all nonzero graded brackets [X, Y} for C(n+1).

    Uses the oscillator realization from Cn1_definition.md:
    - H_1 = a1p*a1m + b1p*b1m
    - H_k (2<=k<=n) = b_{k-1}p*b_{k-1}m - b_kp*b_km
    - H_{n+1} = -b_np*b_nm - 1/2
    - E_eps1_del{k}_pp = a1p*b_kp,  E_eps1_del{k}_pm = a1p*b_km
    - E_eps1_del{k}_mp = a1m*b_kp,  E_eps1_del{k}_mm = a1m*b_km
    - E_2del{k}_p = (1/2)*(b_kp)^2, E_2del{k}_m = (1/2)*(b_km)^2
    - E_del{i}_del{j}_pp = b_ip*b_jp, E_del{i}_del{j}_mm = b_im*b_jm
    - E_del{i}_del{j}_pm = b_ip*b_jm, E_del{i}_del{j}_mp = b_im*b_jp

    We compute brackets analytically using the rules:
    - [N_a, a] = -a, [N_a, a†] = a† where N_a = a†a
    - [N_b, b_k] = -b_k delta, [N_b, b_k†] = b_k† delta  (CCR)
    - {a1m, a1p} = 1 (CAR)
    - [b_im, b_jp] = delta_ij (CCR)
    """
    basis = odd + even
    parity = build_parity_dict(even, odd)
    sc = []

    def add(X, Y, Z, coeff):
        if coeff == 0:
            return
        sc.append({
            "X": X, "Y": Y, "Z": Z,
            "coeff": str(coeff),
            "sign_rule": "graded"
        })

    # --- Cartan action on odd generators ---
    # H_1 = a1p*a1m + b1p*b1m
    # [H_1, E_eps1_del{k}_pp] = [a1p*a1m + b1p*b1m, a1p*b_kp]
    # Using: [a1p*a1m, a1p] = a1p (a1p raises a1 number)
    #        [b1p*b1m, b_kp] = delta_{1k} b_kp
    # So [H_1, E_eps1_del{k}_pp] = (1 + delta_{1k}) E_eps1_del{k}_pp

    for k in range(1, n + 1):
        # H_1 action on eps generators
        coeff_pp = Fraction(1 + (1 if k == 1 else 0))
        coeff_pm = Fraction(1 - (1 if k == 1 else 0))
        coeff_mp = Fraction(-1 + (1 if k == 1 else 0))
        coeff_mm = Fraction(-1 - (1 if k == 1 else 0))

        add("H_1", f"E_eps1_del{k}_pp", f"E_eps1_del{k}_pp", coeff_pp)
        if coeff_pm != 0:
            add("H_1", f"E_eps1_del{k}_pm", f"E_eps1_del{k}_pm", coeff_pm)
        if coeff_mp != 0:
            add("H_1", f"E_eps1_del{k}_mp", f"E_eps1_del{k}_mp", coeff_mp)
        add("H_1", f"E_eps1_del{k}_mm", f"E_eps1_del{k}_mm", coeff_mm)

    # H_l (2 <= l <= n) = b_{l-1}p*b_{l-1}m - b_lp*b_lm
    # [H_l, E_eps1_del{k}_{sign}]:
    # eigenvalue = (delta_{k,l-1} - delta_{k,l}) * (sign_bk)
    # where sign_bk = +1 if b_kp appears, -1 if b_km appears
    for l in range(2, n + 1):
        for k in range(1, n + 1):
            bk_contrib = Fraction((1 if k == l - 1 else 0) - (1 if k == l else 0))
            # a1 contribution: H_l has no a1, so eigen value from a1 is 0
            # eigenvalue for pp: +bk_contrib (b_kp)
            ev_pp = bk_contrib
            ev_pm = -bk_contrib  # b_km
            ev_mp = bk_contrib   # b_kp
            ev_mm = -bk_contrib  # b_km
            # a1 eigenvalue from H_l is 0 (H_l doesn't involve a1)

            for (sign, ev) in [("pp", ev_pp), ("pm", ev_pm), ("mp", ev_mp), ("mm", ev_mm)]:
                if ev != 0:
                    add(f"H_{l}", f"E_eps1_del{k}_{sign}", f"E_eps1_del{k}_{sign}", ev)

    # H_{n+1} = -b_np*b_nm - 1/2
    # [H_{n+1}, E_eps1_del{k}_{sign}]:
    # eigenvalue = -delta_{k,n} * (sign_bk)
    for k in range(1, n + 1):
        bn_contrib = Fraction(-(1 if k == n else 0))
        ev_pp = bn_contrib    # b_kp
        ev_pm = -bn_contrib   # b_km
        ev_mp = bn_contrib    # b_kp
        ev_mm = -bn_contrib   # b_km
        # a1: H_{n+1} doesn't involve a1, so contribution is 0
        for (sign, ev) in [("pp", ev_pp), ("pm", ev_pm), ("mp", ev_mp), ("mm", ev_mm)]:
            if ev != 0:
                add(f"H_{n+1}", f"E_eps1_del{k}_{sign}", f"E_eps1_del{k}_{sign}", ev)

    # --- Cartan action on even root generators ---
    # H_1 action on E_2del{k}_p: eigenvalue = 0 (no a1 in E_2del{k}_p)
    # E_2del{k}_p = (1/2)b_kp^2: [H_1, E_2del{k}_p] = [b1p*b1m, (1/2)b_kp^2]
    # = delta_{1k} * b_kp^2 = 2*delta_{1k} * E_2del{k}_p
    for k in range(1, n + 1):
        ev = Fraction(2 * (1 if k == 1 else 0))
        if ev != 0:
            add("H_1", f"E_2del{k}_p", f"E_2del{k}_p", ev)
        ev_m = Fraction(-2 * (1 if k == 1 else 0))
        if ev_m != 0:
            add("H_1", f"E_2del{k}_m", f"E_2del{k}_m", ev_m)

    # H_l on E_2del{k}_p/m
    for l in range(2, n + 1):
        for k in range(1, n + 1):
            bk_contrib = Fraction((1 if k == l - 1 else 0) - (1 if k == l else 0))
            ev_p = 2 * bk_contrib
            ev_m = -2 * bk_contrib
            if ev_p != 0:
                add(f"H_{l}", f"E_2del{k}_p", f"E_2del{k}_p", ev_p)
            if ev_m != 0:
                add(f"H_{l}", f"E_2del{k}_m", f"E_2del{k}_m", ev_m)

    # H_{n+1} on E_2del{k}_p/m
    for k in range(1, n + 1):
        bn_contrib = Fraction(-(1 if k == n else 0))
        ev_p = 2 * bn_contrib
        ev_m = -2 * bn_contrib
        if ev_p != 0:
            add(f"H_{n+1}", f"E_2del{k}_p", f"E_2del{k}_p", ev_p)
        if ev_m != 0:
            add(f"H_{n+1}", f"E_2del{k}_m", f"E_2del{k}_m", ev_m)

    # H_l on E_del{i}_del{j}_{sign} (i<j)
    # eigenvalue = (delta_{i,contrib} + delta_{j,contrib}) * sign_factors
    for i, j in itertools.combinations(range(1, n + 1), 2):
        for l_idx, l in enumerate(range(1, n + 2)):
            if l == 1:
                li = Fraction(0)  # b_ip contribution from H_1: H_1 has b1, so delta_{i,1}
                lj = Fraction(0)  # same
                # H_1 = a1p*a1m + b1p*b1m
                li = Fraction(1 if i == 1 else 0)
                lj = Fraction(1 if j == 1 else 0)
            elif l <= n:
                li = Fraction((1 if i == l - 1 else 0) - (1 if i == l else 0))
                lj = Fraction((1 if j == l - 1 else 0) - (1 if j == l else 0))
            else:  # l = n+1
                li = Fraction(-(1 if i == n else 0))
                lj = Fraction(-(1 if j == n else 0))

            ev_pp = li + lj
            ev_mm = -(li + lj)
            ev_pm = li - lj
            ev_mp = -(li - lj)

            for (sign, ev) in [("pp", ev_pp), ("mm", ev_mm), ("pm", ev_pm), ("mp", ev_mp)]:
                if ev != 0:
                    add(f"H_{l}", f"E_del{i}_del{j}_{sign}", f"E_del{i}_del{j}_{sign}", ev)

    # --- Brackets between odd generators ---
    # {E_eps1_del{k}_pp, E_eps1_del{l}_mm} = {a1p*b_kp, a1m*b_lm}
    # = a1p*a1m * [b_kp, b_lm] + b_kp*b_lm * {a1p, a1m} - ...
    # More carefully: using graded bracket rules and CAR/CCR:
    # {a1p*b_kp, a1m*b_lm} = a1p*b_kp*a1m*b_lm + a1m*b_lm*a1p*b_kp
    # = a1p*(a1m*b_kp + b_kp*a1m)*b_lm (using {a1m,b_kp}=0, [b_kp,a1m]=0)
    # Wait, let me use the systematic approach:
    # For odd generators X=a_sigma*b_k^s and Y=a_tau*b_l^t:
    # {X,Y} = a_sigma*b_k^s*a_tau*b_l^t + a_tau*b_l^t*a_sigma*b_k^s
    #
    # Using [b,a]=0 (commute), and {a1p,a1m}=1, {a1p,a1p}=0, {a1m,a1m}=0:
    # {a_sigma*b_k^s, a_tau*b_l^t}
    # = a_sigma*a_tau*b_k^s*b_l^t + a_tau*a_sigma*b_l^t*b_k^s
    #   (since b commutes with a)
    # = (a_sigma*a_tau + a_tau*a_sigma)*b_k^s*b_l^t  (if k!=l or s!=t for bosons)
    # = {a_sigma, a_tau} * b_k^s*b_l^t  (for distinct boson modes)
    #
    # But for bosons we need to be careful: b_k^s*b_l^t = b_l^t*b_k^s (they commute)
    # unless k=l and s=-t, giving [b_km, b_kp] = -1.
    #
    # Systematic computation:
    # {E_eps1_del{k}_{s1s2}, E_eps1_del{l}_{t1t2}}
    # where s1=sign of a, s2=sign of b_k, t1=sign of a, t2=sign of b_l
    #
    # = {a_{s1}*b_k^{s2}, a_{t1}*b_l^{t2}}
    # = {a_{s1}, a_{t1}} * b_k^{s2}*b_l^{t2} + [b_k^{s2}, b_l^{t2}]_corrections
    #
    # Since [b, a]=0:
    # {a_{s1}*b_k^{s2}, a_{t1}*b_l^{t2}}
    # = a_{s1}*(a_{t1}*b_k^{s2} - (-1)^0 b_k^{s2}*a_{t1})*b_l^{t2}
    #   + b_k^{s2}*a_{t1}*a_{s1}*b_l^{t2}  ... hmm this is getting complicated
    #
    # Let me use the cleaner approach: generators are polynomials in osc, use supercommutator.
    # For X = a_{s1}*b_k^{s2} (parity 1), Y = a_{t1}*b_l^{t2} (parity 1):
    # {X,Y} = X*Y + Y*X (since both odd, graded comm = anticommutator)
    #
    # X*Y = a_{s1}*b_k^{s2}*a_{t1}*b_l^{t2}
    # Since b commutes with a: = a_{s1}*a_{t1}*b_k^{s2}*b_l^{t2}
    #
    # Y*X = a_{t1}*b_l^{t2}*a_{s1}*b_k^{s2}
    #     = a_{t1}*a_{s1}*b_l^{t2}*b_k^{s2}
    #
    # {X,Y} = a_{s1}*a_{t1}*b_k^{s2}*b_l^{t2} + a_{t1}*a_{s1}*b_l^{t2}*b_k^{s2}
    #
    # Case 1: s1 = t1 (same fermion direction)
    # a_{s1}*a_{s1} = 0 (since {a,a}=0 for CAR), so both terms = 0 => {X,Y}=0
    #
    # Case 2: s1 != t1 (one is p, one is m)
    # WLOG s1=p, t1=m:
    # {X,Y} = a_p*a_m*b_k^{s2}*b_l^{t2} + a_m*a_p*b_l^{t2}*b_k^{s2}
    # Using {a_m, a_p}=1 => a_m*a_p = 1 - a_p*a_m:
    # = a_p*a_m*b_k^{s2}*b_l^{t2} + (1 - a_p*a_m)*b_l^{t2}*b_k^{s2}
    # = b_l^{t2}*b_k^{s2} + a_p*a_m*(b_k^{s2}*b_l^{t2} - b_l^{t2}*b_k^{s2})
    # = b_l^{t2}*b_k^{s2} + a_p*a_m*[b_k^{s2}, b_l^{t2}]
    #
    # [b_k^{s2}, b_l^{t2}]:
    # - If k!=l or s2==t2: commute => 0
    # - If k==l and s2!=t2: [b_km, b_kp] = -1 (from [b_km, b_kp] = -delta => [b_k^-, b_k^+] = 1, so if ordering is b_km*b_kp then [b_km, b_kp]=1, but b_k^{s2}*b_l^{t2} for s2=p,t2=m means [b_kp, b_km]=-1)
    #
    # Let me define: [b_k^+, b_k^-] = -1, [b_k^-, b_k^+] = 1
    # So [b_k^{s2}, b_k^{t2}] = delta_{s2,p}*delta_{t2,m}*(-1) + delta_{s2,m}*delta_{t2,p}*(1)
    #
    # Also b_l^{t2}*b_k^{s2}: bosons commute unless same k and opposite sign.
    # b_l^{t2}*b_k^{s2} = b_k^{s2}*b_l^{t2} + [b_l^{t2}, b_k^{s2}]
    #                    = b_k^{s2}*b_l^{t2} - [b_k^{s2}, b_l^{t2}]
    #
    # So {X,Y} (s1=p, t1=m):
    # = b_k^{s2}*b_l^{t2} - [b_k^{s2},b_l^{t2}] + a_p*a_m*[b_k^{s2},b_l^{t2}]
    # = b_k^{s2}*b_l^{t2} + [b_k^{s2},b_l^{t2}]*(a_p*a_m - 1)
    #
    # Now in the algebra, a_p*a_m = N_a (number operator for a), and
    # the algebra element b_k^{s2}*b_l^{t2} corresponds to:
    #   k!=l (or s2=t2): E_del{k}_del{l}_{s2t2} (properly ordered)
    #   k==l, s2!=t2: gives N_bk or -N_bk + constant
    #
    # Let's work out the cases:
    #
    # CASE A: s1=p, t1=m, k!=l (or k=l but s2=t2)
    # => {E_eps1_del{k}_p{s2}, E_eps1_del{l}_m{t2}}
    #    = b_k^{s2}*b_l^{t2} (up to ordering issues for bosons since [b_k^s,b_l^t]=0 here)
    #    maps to even generators E_del{k}_del{l}_{s2t2} (if k<l) or E_del{l}_del{k}_{t2s2} (if k>l)
    # => coeff = 1 (or adjusted for ordering)
    #
    # CASE B: s1=p, t1=m, k==l, s2!=t2
    # For s2=p, t2=m: b_kp*b_km = N_bk, [b_kp,b_km]=-1
    # {E_eps1_del{k}_pp, E_eps1_del{k}_mm}
    # = b_kp*b_km + (-1)*(a_p*a_m - 1)
    # = N_bk + 1 - N_a
    #
    # Now N_bk and N_a appear in Cartan generators:
    # H_1 = N_a + N_b1
    # H_k = N_b{k-1} - N_bk for k=2..n
    # H_{n+1} = -N_bn - 1/2
    #
    # So N_bk = ? Let's invert:
    # N_b1 = H_1 - N_a (but N_a is part of H_1 too...)
    # Actually in the algebra generated by generators, we need to express
    # anticommutators in terms of basis generators.
    #
    # {E_eps1_del{k}_pp, E_eps1_del{k}_mm} = N_bk - N_a + 1
    # We need to express this in terms of H_k generators.
    #
    # From H generators: N_a = H_1 - N_b1
    # N_bk for k=1..n can be read off from H generators.
    #
    # For the special case of simple generators (k=1):
    # H_1 = N_a + N_b1 => N_b1 = H_1 - N_a
    # H_2 = N_b1 - N_b2 => N_b2 = N_b1 - H_2 = H_1 - N_a - H_2
    # ...
    # H_k = N_b{k-1} - N_bk for k=2..n => N_bk = N_b{k-1} - H_k
    # H_{n+1} = -N_bn - 1/2 => N_bn = -H_{n+1} - 1/2
    #
    # From these: N_bk = -H_{k+1} - H_{k+2} - ... - H_{n+1} - 1/2 for k=1..n
    # And N_a = H_1 - N_b1 = H_1 + H_2 + ... + H_{n+1} + 1/2
    #
    # {E_eps1_del{k}_pp, E_eps1_del{k}_mm} = N_bk - N_a + 1
    # = (-H_{k+1}-...-H_{n+1}-1/2) - (H_1+H_2+...+H_{n+1}+1/2) + 1
    # = -H_1 - H_2 - ... - H_k - 2*(H_{k+1}+...+H_{n+1}) - 1 + 1 - 1
    # Wait let me redo:
    # N_bk - N_a + 1
    # N_bk = -(H_{k+1}+...+H_{n+1}) - 1/2  [for k=1..n]
    # N_a = H_1 + H_2 + ... + H_{n+1} + 1/2
    #
    # N_bk - N_a = -(H_{k+1}+...+H_{n+1}) - 1/2 - H_1 - H_2 - ... - H_{n+1} - 1/2
    #            = -H_1 - ... - H_k - 2(H_{k+1}+...+H_{n+1}) - 1
    #
    # {E_eps1_del{k}_pp, E_eps1_del{k}_mm} = N_bk - N_a + 1
    # = -H_1 - ... - H_k - 2(H_{k+1}+...+H_{n+1})
    #
    # This is a linear combination of Cartan generators. Let's verify for k=1, n=1:
    # N_b1 - N_a + 1 = -(H_2) - 1/2 - (H_1 + H_2 + 1/2) + 1
    # = -H_1 - 2*H_2 - 1/2 - 1/2 + 1 = -H_1 - 2*H_2
    # => {E_eps1_del1_pp, E_eps1_del1_mm} = -H_1 - 2*H_2
    #
    # For s2=m, t2=p (other case): b_km*b_kp = N_bk + 1 (from CCR: [b_km,b_kp]=1)
    # Wait: [b_k^-, b_k^+] = 1 => b_km*b_kp = b_kp*b_km + 1 = N_bk + 1
    # {E_eps1_del{k}_pm, E_eps1_del{k}_mp}
    # s1=p, t1=m, k=k, s2=m, t2=p
    # = b_km*b_kp + [b_km,b_kp]*(N_a - 1)   [sign flip due to [b_km,b_kp]=+1]
    # Actually let me redo case B carefully for s2=m, t2=p:
    # {E_eps1_del{k}_pm, E_eps1_del{k}_mp}:
    # s1=p, t1=m, s2=m (b component of first), t2=p (b component of second)
    # = b_km*b_kp + [b_km,b_kp]*(N_a - 1)
    # = (N_bk + 1) + 1*(N_a - 1)
    # = N_bk + N_a
    # = -(H_{k+1}+...+H_{n+1}) - 1/2 + H_1 + H_2 + ... + H_{n+1} + 1/2
    # = H_1 + H_2 + ... + H_k + 0*(H_{k+1}+...+H_{n+1}) - 1/2 + 1/2
    # Wait: N_bk = -(H_{k+1}+...+H_{n+1}) - 1/2
    # N_a = H_1+H_2+...+H_{n+1}+1/2
    # N_bk + N_a = H_1+H_2+...+H_k + (H_{k+1}+...+H_{n+1}) - (H_{k+1}+...+H_{n+1}) - 1/2 + 1/2
    # Wait no:
    # N_bk + N_a = [-(H_{k+1}+...+H_{n+1}) - 1/2] + [H_1+...+H_{n+1}+1/2]
    #            = H_1 + ... + H_k + 0 = H_1 + H_2 + ... + H_k
    #
    # So {E_eps1_del{k}_pm, E_eps1_del{k}_mp} = H_1 + H_2 + ... + H_k
    #
    # Let me implement this systematically:

    # N_bk in terms of H: N_bk = -sum_{l=k+1}^{n+1} H_l - 1/2
    # N_a = H_1 + sum_{l=2}^{n+1} H_l + 1/2 = sum_{l=1}^{n+1} H_l + 1/2
    # (Actually from H_1=N_a+N_b1: N_a = H_1 - N_b1 = H_1 - (-(H_2+...+H_{n+1})-1/2)
    #  = H_1 + H_2 + ... + H_{n+1} + 1/2)

    # {E_eps1_del{k}_pp, E_eps1_del{k}_mm}
    # = N_bk - N_a + 1 = [-(H_{k+1}+...+H_{n+1})-1/2] - [H_1+...+H_{n+1}+1/2] + 1
    # = -H_1-...-H_k - 2*(H_{k+1}+...+H_{n+1}) - 1 + 1
    # = -H_1-...-H_k - 2*(H_{k+1}+...+H_{n+1})

    # {E_eps1_del{k}_pm, E_eps1_del{k}_mp}
    # = N_bk + N_a = H_1+...+H_k

    # CASE A: k != l OR (k==l and s2==t2) but s1 != t1
    # {E_eps1_del{k}_p{s2}, E_eps1_del{l}_m{t2}} = b_k^{s2}*b_l^{t2}
    # (bosons commute when (k!=l) or s2=t2 so [b,b]=0)
    # => this is E_del{min(k,l)}_del{max(k,l)}_{sign} if k!=l
    #    or E_2del{k}_{s2t2 combined} if k==l and s2==t2

    # Actually if s2=t2=p and k==l: b_kp*b_kp = (b_kp)^2 = 2*E_2del{k}_p
    # if s2=t2=m and k==l: b_km*b_km = 2*E_2del{k}_m

    # Let me now code all anticommutators between odd generators:
    odd_gens = odd  # list like E_eps1_del{k}_{sign}

    def parse_odd(label):
        # returns (a_sign, k, b_sign)
        # E_eps1_del{k}_{s1s2}: s1 = a_sign, s2 = b_sign
        # label format: E_eps1_del{k}_{s1s2}
        parts = label.split("_")
        # parts: ['E', 'eps1', 'del{k}', '{s1s2}']
        k = int(parts[2][3:])  # 'del{k}' -> k
        signs = parts[3]  # 'pp', 'pm', 'mp', 'mm'
        a_sign = signs[0]  # 'p' or 'm'
        b_sign = signs[1]  # 'p' or 'm'
        return a_sign, k, b_sign

    def boson_product_label(k, s2, l, t2):
        """Return the even generator label for b_k^{s2}*b_l^{t2}, or None if 0."""
        if k == l and s2 == t2:
            # (b_kp)^2 = 2*E_2del{k}_p etc.
            return f"E_2del{k}_{s2}", Fraction(2)
        elif k == l and s2 != t2:
            # b_kp*b_km or b_km*b_kp: these contribute to number operators
            return None, None  # handled separately via Cartan
        else:
            # k != l: bosons commute, b_k^{s2}*b_l^{t2}
            # use convention: smaller index first
            if k < l:
                sign_combo = s2 + t2
                return f"E_del{k}_del{l}_{sign_combo}", Fraction(1)
            else:
                sign_combo = t2 + s2
                return f"E_del{l}_del{k}_{sign_combo}", Fraction(1)

    # Compute all odd-odd anticommutators
    for i_idx, X in enumerate(odd):
        a1, k, s2 = parse_odd(X)
        for j_idx, Y in enumerate(odd):
            if j_idx < i_idx:
                continue  # use symmetry
            a2, l, t2 = parse_odd(Y)

            # {X, Y} where X,Y are odd:
            if a1 == a2:
                # {a_{s}, a_{s}} = 0 => all zero
                continue

            # a1 != a2; WLOG we compute for a1=p, a2=m (or vice versa)
            # The sign factor: if X=E_eps1_del{k}_p{s2}, Y=E_eps1_del{l}_m{t2}
            # {X,Y} = b_k^{s2}*b_l^{t2} + [b_k^{s2},b_l^{t2}]*(N_a - 1)
            #
            # But when a1=m, a2=p: {X,Y} is same due to anticommutativity symmetry (both odd):
            # {X,Y}={Y,X} since parity(X)+parity(Y)=even

            # Order: ensure X has a_p, Y has a_m for computation
            if a1 == 'p' and a2 == 'm':
                ka, sa, la, ta = k, s2, l, t2
            else:  # a1='m', a2='p' => swap
                ka, sa, la, ta = l, t2, k, s2

            # Compute b_{ka}^{sa} * b_{la}^{ta} contribution
            commutator_val = Fraction(0)
            if ka == la:
                if sa == ta:
                    # [b_kp,b_kp]=0 or [b_km,b_km]=0
                    commutator_val = Fraction(0)
                elif sa == 'p' and ta == 'm':
                    # [b_kp, b_km] = -1
                    commutator_val = Fraction(-1)
                else:  # sa='m', ta='p'
                    # [b_km, b_kp] = +1
                    commutator_val = Fraction(1)
            # commutator_val = [b_{ka}^{sa}, b_{la}^{ta}]

            # Full formula: {X,Y} = b_{ka}^{sa}*b_{la}^{ta} + commutator_val*(N_a - 1)
            # where N_a = sum_{l=1}^{n+1} H_l + 1/2

            # Contribution from boson product term:
            if ka != la or sa == ta:
                # Bosons commute in this case => b_{ka}^{sa}*b_{la}^{ta} is an even generator
                gen_label, gen_coeff = boson_product_label(ka, sa, la, ta)
                if gen_label is not None and gen_coeff != 0:
                    add(X, Y, gen_label, gen_coeff)
            else:
                # ka==la and sa!=ta: b_{ka}^{sa}*b_{la}^{ta} is a number-like term
                # expressed as Cartan generators
                # b_kp*b_km = N_bk = -(H_{k+1}+...+H_{n+1}) - 1/2  [if sa=p, ta=m]
                # b_km*b_kp = N_bk + 1 = -(H_{k+1}+...+H_{n+1}) + 1/2 [if sa=m, ta=p]
                kk = ka
                if sa == 'p' and ta == 'm':
                    # N_bk = -(H_{k+1}+...+H_{n+1}) - 1/2
                    for l in range(kk + 1, n + 2):
                        add(X, Y, f"H_{l}", Fraction(-1))
                    # constant -1/2 has no basis generator, skip (it's absorbed into the structure)
                    # Actually we can't represent it as a basis element. Constant terms
                    # represent elements proportional to K (identity), which is 1.
                    # In the algebra, K is identified with 1, and the schema records
                    # structure constants as Z=generator. The constant 1/2 multiplied by K
                    # can be recorded if needed, but K is not in the basis.
                    # We record the -1/2 term as K if it's nonzero.
                    # For now, skip (K is scalar 1, not in basis).
                    pass
                else:  # sa='m', ta='p'
                    # N_bk + 1 = -(H_{k+1}+...+H_{n+1}) - 1/2 + 1 = -(H_{k+1}+...+H_{n+1}) + 1/2
                    for l in range(kk + 1, n + 2):
                        add(X, Y, f"H_{l}", Fraction(-1))
                    # +1/2 constant absorbed into K, skip

            # Contribution from commutator_val * (N_a - 1):
            if commutator_val != 0:
                # N_a - 1 = sum_{l=1}^{n+1} H_l + 1/2 - 1 = sum H_l - 1/2
                # (constant -1/2 is K-term, skip)
                for l in range(1, n + 2):
                    add(X, Y, f"H_{l}", commutator_val)

    # Anticommutator {E_eps1_del{k}_pp, E_eps1_del{k}_mm}: computed above,
    # let me verify and add the full Cartan results:
    # These are the "diagonal" odd-odd brackets that give Cartan elements.
    # The above loop handles them; the K-constant terms are dropped (K=1 not in basis).

    # --- Even-Even brackets (simple cases) ---
    # [E_2del{k}_p, E_2del{k}_m] = -H_{k} contribution
    # Using: [E_2del{k}_p, E_2del{k}_m] = [(1/2)(b_kp)^2, (1/2)(b_km)^2]
    # = (1/4)*[b_kp^2, b_km^2]
    # [b_kp^2, b_km^2] = b_kp*[b_kp,b_km^2] + [b_kp,b_km^2]*b_kp
    # [b_kp, b_km^2] = b_km*[b_kp,b_km] + [b_kp,b_km]*b_km = -2*b_km
    # [b_kp^2, b_km^2] = b_kp*(-2*b_km) + (-2*b_km)*b_kp
    # = -2*(b_kp*b_km + b_km*b_kp) = -2*(2*N_bk + 1)  [using b_kp*b_km = N_bk, b_km*b_kp = N_bk+1]
    # = -4*N_bk - 2
    # So [E_2del{k}_p, E_2del{k}_m] = (1/4)*(-4*N_bk - 2) = -N_bk - 1/2
    # = -[-(H_{k+1}+...+H_{n+1}) - 1/2] - 1/2 = H_{k+1}+...+H_{n+1} + 1/2 - 1/2
    # = H_{k+1}+...+H_{n+1}
    # Wait, but from the root system, [E_{2δ_k}, E_{-2δ_k}] = H_{2δ_k} (the coroot)
    # Let me check: the coroot of 2δ_k is the element in the Cartan subalgebra.
    #
    # Actually in the Cartan formalism, [E_α, E_{-α}] = H_α where H_α acts on E_β as β(H_α)*E_β.
    # The root 2δ_k: β(H_{2δ_k}) = <β, 2δ_k^∨> where 2δ_k^∨ = δ_k^∨ = δ_k/(δ_k,δ_k)
    # In the sp(2n) part, [E_{2δ_k}, E_{-2δ_k}] = H_k' where H_k' = b_kp*b_km + 1/2 in some conventions.
    #
    # From the H generator definitions:
    # H_{n+1} = -b_np*b_nm - 1/2 => b_np*b_nm = -H_{n+1} - 1/2 = N_bn
    # For k<n:
    # H_k = b_{k-1}p*b_{k-1}m - b_kp*b_km for k=2..n
    # => N_bk = N_b{k-1} - H_k
    #
    # [E_2del{k}_p, E_2del{k}_m] = -N_bk - 1/2
    # = -(-(H_{k+1}+...+H_{n+1})-1/2) - 1/2 = H_{k+1}+...+H_{n+1}
    #
    # So [E_2del{k}_p, E_2del{k}_m] = H_{k+1}+...+H_{n+1}

    for k in range(1, n + 1):
        for l in range(k + 1, n + 2):
            add(f"E_2del{k}_p", f"E_2del{k}_m", f"H_{l}", Fraction(1))

    # [E_del{i}_del{j}_pp, E_del{i}_del{j}_mm] = ?
    # = [b_ip*b_jp, b_im*b_jm]
    # = b_ip*[b_jp, b_im*b_jm] + [b_ip, b_im*b_jm]*b_jp
    # [b_jp, b_jm] = -1 (since [b_jp,b_jm]=-delta), actually [b_j^-,b_j^+]=1 so [b_j^+,b_j^-]=-1
    # [b_jp, b_im*b_jm] = b_im*[b_jp,b_jm] + [b_jp,b_im]*b_jm = b_im*(-1) + 0 = -b_im
    # [b_ip, b_im*b_jm] = [b_ip,b_im]*b_jm = (-1)*b_jm = -b_jm
    # So: [b_ip*b_jp, b_im*b_jm] = b_ip*(-b_im) + (-b_jm)*b_jp
    # = -(b_ip*b_im + b_jm*b_jp) = -(N_bi + N_bj + 1)
    # Wait: b_ip*b_im = N_bi, b_jm*b_jp = N_bj + 1 (from b_jm*b_jp = N_bj + [b_jm,b_jp]=N_bj+1)
    # = -(N_bi + N_bj + 1)
    # In terms of H: = (H_{i+1}+...+H_{n+1}) + (H_{j+1}+...+H_{n+1}) + 1/2 + 1/2 - 1
    # = H_{i+1}+...+H_{n+1} + H_{j+1}+...+H_{n+1}  (the +1/2+1/2-1=0)
    #
    # Hmm: -N_bi = H_{i+1}+...+H_{n+1}+1/2, -N_bj = H_{j+1}+...+H_{n+1}+1/2
    # -(N_bi+N_bj+1) = (H_{i+1}+...+H_{n+1}+1/2)+(H_{j+1}+...+H_{n+1}+1/2)-1
    #                = H_{i+1}+...+H_{n+1} + H_{j+1}+...+H_{n+1}
    #
    # [E_del{i}_del{j}_pp, E_del{i}_del{j}_mm] = -(N_bi+N_bj+1)
    # = H_{i+1}+...+H_{n+1} + H_{j+1}+...+H_{n+1}
    # (with i<j, so H_{j+1}..H_{n+1} is a subset)

    for i, j in itertools.combinations(range(1, n + 1), 2):
        for l in range(i + 1, n + 2):
            add(f"E_del{i}_del{j}_pp", f"E_del{i}_del{j}_mm", f"H_{l}", Fraction(1))
        for l in range(j + 1, n + 2):
            add(f"E_del{i}_del{j}_pp", f"E_del{i}_del{j}_mm", f"H_{l}", Fraction(1))

    # [E_del{i}_del{j}_pm, E_del{i}_del{j}_mp] = [b_ip*b_jm, b_im*b_jp]
    # = b_ip*[b_jm,b_im*b_jp] + [b_ip,b_im*b_jp]*b_jm
    # [b_jm, b_im*b_jp] = b_im*[b_jm,b_jp] = b_im*1 = b_im (since [b_jm,b_jp]=delta_{jj}=1)
    # [b_ip, b_im*b_jp] = [b_ip,b_im]*b_jp = (-1)*b_jp
    # = b_ip*b_im + (-b_jp)*b_jm = N_bi - b_jp*b_jm + [b_jp,b_jm] ... wait
    # = b_ip*b_im - b_jp*b_jm = N_bi - N_bj
    # = [-(H_{i+1}+...+H_{n+1})-1/2] - [-(H_{j+1}+...+H_{n+1})-1/2]
    # = -(H_{i+1}+...+H_j) + (H_{j+1}+...+H_{n+1}) - (H_{j+1}+...+H_{n+1})
    # = -(H_{i+1}+...+H_j) ... let me be more careful:
    # N_bi = -(H_{i+1}+...+H_{n+1}) - 1/2
    # N_bj = -(H_{j+1}+...+H_{n+1}) - 1/2  (i<j, so j+1>i+1)
    # N_bi - N_bj = [-(H_{i+1}+...+H_{n+1})-1/2] - [-(H_{j+1}+...+H_{n+1})-1/2]
    #             = -(H_{i+1}+...+H_j) - (H_{j+1}+...+H_{n+1}) + (H_{j+1}+...+H_{n+1})
    #             = -(H_{i+1}+...+H_j)
    #
    # Wait: -(H_{i+1}+...+H_{n+1}) = -(H_{i+1}+...+H_j) - (H_{j+1}+...+H_{n+1})
    # N_bi - N_bj = -(H_{i+1}+...+H_j) - (H_{j+1}+...+H_{n+1}) + (H_{j+1}+...+H_{n+1})
    #             = -(H_{i+1}+...+H_j)

    for i, j in itertools.combinations(range(1, n + 1), 2):
        for l in range(i + 1, j + 1):
            add(f"E_del{i}_del{j}_pm", f"E_del{i}_del{j}_mp", f"H_{l}", Fraction(-1))

    # [E_del{i}_del{j}_pp, E_del{i'}_del{j'}_mm] for different (i,j)!=(i',j'):
    # These are more complex; let me handle the main non-diagonal even-even brackets.
    # [E_del{i}_del{j}_pp, E_del{k}_del{l}_mm] where {i,j}!={k,l}:
    # = [b_ip*b_jp, b_km*b_lm]
    # Non-zero only when {i,j} and {k,l} share exactly one index.
    # Case: i=k, j!=l:
    # = [b_ip*b_jp, b_im*b_lm] = b_jp*[b_ip,b_im]*b_lm = -b_jp*b_lm = -E_del{min(j,l)}_del{max(j,l)}_...
    # Wait: [b_ip,b_im]=-1, so = (-1)*b_jp*b_lm
    # If j<l: = -E_del{j}_del{l}_pm (since b_jp*b_lm with j<l has sign 'pm')
    # If j>l: = -b_jp*b_lm = -E_del{l}_del{j}_mp (since b_lm*b_jp with l<j is 'mp')

    # This gets complex. Let me add a general approach for all even-even brackets.
    # I'll enumerate explicitly for small n and check correctness.

    # [E_del{i}_del{j}_pp, E_del{k}_del{l}_mm] with (i,j)!=(k,l), all combos:
    for (i, j) in itertools.combinations(range(1, n + 1), 2):
        for (k, l) in itertools.combinations(range(1, n + 1), 2):
            if (i, j) == (k, l):
                continue
            # [b_ip*b_jp, b_km*b_lm]
            # Non-zero if {i,j} and {k,l} share exactly one element
            shared = set([i, j]) & set([k, l])
            if len(shared) != 1:
                continue
            s = list(shared)[0]
            # The "other" indices
            other_ij = i if j == s else j
            other_kl = k if l == s else l
            # [b_sp*b_{other_ij}p, b_sm*b_{other_kl}m]
            # = b_{other_ij}p * [b_sp, b_sm] * b_{other_kl}m
            # = b_{other_ij}p * (-1) * b_{other_kl}m = -b_{other_ij}p*b_{other_kl}m
            a_idx = other_ij
            b_idx = other_kl
            a_sign = 'p'
            b_sign = 'm'
            coeff = Fraction(-1)
            if a_idx < b_idx:
                label = f"E_del{a_idx}_del{b_idx}_{a_sign}{b_sign}"
            elif a_idx > b_idx:
                label = f"E_del{b_idx}_del{a_idx}_{b_sign}{a_sign}"
            else:
                # a_idx == b_idx, different signs => number-type
                # b_ap * b_am = N_ba
                for ll in range(a_idx + 1, n + 2):
                    add(f"E_del{i}_del{j}_pp", f"E_del{k}_del{l}_mm", f"H_{ll}", Fraction(-1))
                continue
            add(f"E_del{i}_del{j}_pp", f"E_del{k}_del{l}_mm", label, coeff)

    # [E_del{i}_del{j}_pm, E_del{k}_del{l}_mp] similar analysis
    for (i, j) in itertools.combinations(range(1, n + 1), 2):
        for (k, l) in itertools.combinations(range(1, n + 1), 2):
            # [b_ip*b_jm, b_km*b_lp]
            # = b_ip*[b_jm, b_km*b_lp] + [b_ip, b_km*b_lp]*b_jm
            # [b_jm, b_km*b_lp] = b_km*[b_jm, b_lp] = delta_{jl}*b_km
            # [b_ip, b_km*b_lp] = [b_ip, b_km]*b_lp = 0 + b_km*[b_ip,b_lp] = 0
            # Wait: [b_ip, b_km] = 0 (different type or index), [b_ip, b_lp] = 0
            # So [b_ip, b_km*b_lp] = 0
            # => [E_del{i}_del{j}_pm, E_del{k}_del{l}_mp] = b_ip * delta_{jl} * b_km
            # = delta_{jl} * b_ip * b_km
            # If i < k: = delta_{jl} * E_del{i}_del{k}_pm
            # If i > k: = delta_{jl} * E_del{k}_del{i}_mp
            # If i == k: number-type
            if j != l:
                continue
            # j == l
            a_idx, b_idx = i, k
            coeff = Fraction(1)
            if a_idx < b_idx:
                label = f"E_del{a_idx}_del{b_idx}_pm"
                add(f"E_del{i}_del{j}_pm", f"E_del{k}_del{l}_mp", label, coeff)
            elif a_idx > b_idx:
                label = f"E_del{b_idx}_del{a_idx}_mp"
                add(f"E_del{i}_del{j}_pm", f"E_del{k}_del{l}_mp", label, coeff)
            else:
                # i == k: b_ip*b_km = b_ip*b_im = N_bi
                for ll in range(i + 1, n + 2):
                    add(f"E_del{i}_del{j}_pm", f"E_del{k}_del{l}_mp", f"H_{ll}", Fraction(-1))

    # Raise-Raise brackets: [E_del{i}_del{j}_pp, E_del{k}_del{l}_pp] etc.
    # For the even-even positive-positive: these commute with each other
    # (all same sign, so all bosonic - using [b_ip*b_jp, b_kp*b_lp]=0)
    # Because b's all commute: b_ip*b_jp*b_kp*b_lp = b_kp*b_lp*b_ip*b_jp => []=0. OK.

    # [E_2del{k}_p, E_del{i}_del{j}_mm]: i<j
    # = [(1/2)b_kp^2, b_im*b_jm]
    # = (1/2)*[b_kp^2, b_im*b_jm]
    # [b_kp^2, b_im*b_jm] = b_kp*[b_kp,b_im*b_jm] + [b_kp,b_im*b_jm]*b_kp
    # [b_kp, b_im*b_jm] = [b_kp,b_im]*b_jm + b_im*[b_kp,b_jm]
    # = delta_{ki}*(-1)*b_jm + b_im*delta_{kj}*(-1)
    # = -delta_{ki}*b_jm - delta_{kj}*b_im
    # [b_kp^2, b_im*b_jm] = b_kp*(-delta_{ki}*b_jm - delta_{kj}*b_im)
    #                      + (-delta_{ki}*b_jm - delta_{kj}*b_im)*b_kp
    # = -delta_{ki}*(b_kp*b_jm + b_jm*b_kp) - delta_{kj}*(b_kp*b_im + b_im*b_kp)
    # = -delta_{ki}*2*b_kp*b_jm - delta_{kj}*2*b_kp*b_im (bosons commute)
    # = -2*delta_{ki}*b_kp*b_jm - 2*delta_{kj}*b_kp*b_im
    # So [E_2del{k}_p, E_del{i}_del{j}_mm] = (1/2)*(-2*delta_{ki}*b_kp*b_jm - 2*delta_{kj}*b_kp*b_im)
    # = -delta_{ki}*b_kp*b_jm - delta_{kj}*b_kp*b_im

    for k in range(1, n + 1):
        for i, j in itertools.combinations(range(1, n + 1), 2):
            # contribution from delta_{ki}: -b_kp*b_jm
            if k == i:
                # b_kp * b_jm: k<j? or k>j?
                a, b = k, j
                if a < b:
                    add(f"E_2del{k}_p", f"E_del{i}_del{j}_mm", f"E_del{a}_del{b}_pm", Fraction(-1))
                elif a > b:
                    add(f"E_2del{k}_p", f"E_del{i}_del{j}_mm", f"E_del{b}_del{a}_mp", Fraction(-1))
            # contribution from delta_{kj}: -b_kp*b_im
            if k == j:
                a, b = i, k
                if a < b:
                    add(f"E_2del{k}_p", f"E_del{i}_del{j}_mm", f"E_del{a}_del{b}_pm", Fraction(-1))
                elif a > b:
                    add(f"E_2del{k}_p", f"E_del{i}_del{j}_mm", f"E_del{b}_del{a}_mp", Fraction(-1))

    # [E_2del{k}_m, E_del{i}_del{j}_pp]: analogous
    for k in range(1, n + 1):
        for i, j in itertools.combinations(range(1, n + 1), 2):
            if k == i:
                a, b = k, j
                if a < b:
                    add(f"E_2del{k}_m", f"E_del{i}_del{j}_pp", f"E_del{a}_del{b}_mp", Fraction(1))
                elif a > b:
                    add(f"E_2del{k}_m", f"E_del{i}_del{j}_pp", f"E_del{b}_del{a}_pm", Fraction(1))
            if k == j:
                a, b = i, k
                if a < b:
                    add(f"E_2del{k}_m", f"E_del{i}_del{j}_pp", f"E_del{a}_del{b}_mp", Fraction(1))
                elif a > b:
                    add(f"E_2del{k}_m", f"E_del{i}_del{j}_pp", f"E_del{b}_del{a}_pm", Fraction(1))

    # [E_2del{k}_p, E_del{i}_del{j}_pm]: only if k==i or k==j
    for k in range(1, n + 1):
        for i, j in itertools.combinations(range(1, n + 1), 2):
            # [b_kp^2/2, b_ip*b_jm]
            # = (1/2)*[b_kp^2, b_ip*b_jm]
            # [b_kp^2, b_ip*b_jm] = b_kp*[b_kp,b_ip*b_jm]+[b_kp,b_ip*b_jm]*b_kp
            # [b_kp, b_ip*b_jm] = [b_kp,b_ip]*b_jm + b_ip*[b_kp,b_jm] = 0 (all + signs commute)
            # => [E_2del{k}_p, E_del{i}_del{j}_pm] = 0
            pass  # All zero since raising operators commute

    # [E_2del{k}_p, E_del{i}_del{j}_mp]: similar, 0 (all + on b_k side)

    # [E_2del{k}_p, E_2del{l}_m] already done above when k==l.
    # For k!=l: [E_2del{k}_p, E_2del{l}_m] = [(1/2)b_kp^2, (1/2)b_lm^2] = 0 (k!=l, bosons commute)

    # Even-Odd brackets:
    # [E_del{i}_del{j}_pp, E_eps1_del{k}_{sign}]: even commutes with odd via adjoint
    # [b_ip*b_jp, a_1s*b_k^t] = a_1s * [b_ip*b_jp, b_k^t]  (since [b,a]=0)
    # = a_1s * (b_ip*[b_jp,b_k^t] + [b_ip,b_k^t]*b_jp)
    # For t=p: [b_lp, b_kp]=0, so = 0
    # For t=m: [b_lp, b_km] = -delta_{lk}
    # => [b_ip*b_jp, b_km] = -delta_{ik}*b_jp - delta_{jk}*b_ip  ... wait:
    # [b_ip*b_jp, b_km] = b_ip*[b_jp,b_km] + [b_ip,b_km]*b_jp = -delta_{jk}*b_ip + (-delta_{ik})*b_jp

    for i, j in itertools.combinations(range(1, n + 1), 2):
        for k in range(1, n + 1):
            # [E_del{i}_del{j}_pp, E_eps1_del{k}_{sign}]
            # = a_1^{sign_a} * [b_ip*b_jp, b_k^{sign_b}]
            for a_sgn in ['p', 'm']:
                for b_sgn in ['p', 'm']:
                    sign = a_sgn + b_sgn
                    Yg = f"E_eps1_del{k}_{sign}"
                    if b_sgn == 'p':
                        # [b_lp, b_kp]=0 for all l
                        pass
                    else:
                        # b_sgn == 'm'
                        # [b_ip*b_jp, b_km] = -delta_{ik}*b_jp - delta_{jk}*b_ip
                        # result: a_{a_sgn} * (-delta_{ik}*b_jp - delta_{jk}*b_ip)
                        if k == i:
                            # -a_{a_sgn}*b_jp
                            new_sign = a_sgn + 'p'
                            add(f"E_del{i}_del{j}_pp", Yg, f"E_eps1_del{j}_{new_sign}", Fraction(-1))
                        if k == j:
                            # -a_{a_sgn}*b_ip
                            new_sign = a_sgn + 'p'
                            add(f"E_del{i}_del{j}_pp", Yg, f"E_eps1_del{i}_{new_sign}", Fraction(-1))

    # [E_del{i}_del{j}_mm, E_eps1_del{k}_{sign}]:
    # = a_{a_sgn} * [b_im*b_jm, b_k^{b_sgn}]
    # [b_im*b_jm, b_kp] = b_im*[b_jm,b_kp] + [b_im,b_kp]*b_jm = delta_{jk}*b_im + delta_{ik}*b_jm
    # [b_im*b_jm, b_km] = 0

    for i, j in itertools.combinations(range(1, n + 1), 2):
        for k in range(1, n + 1):
            for a_sgn in ['p', 'm']:
                for b_sgn in ['p', 'm']:
                    sign = a_sgn + b_sgn
                    Yg = f"E_eps1_del{k}_{sign}"
                    if b_sgn == 'p':
                        # [b_im*b_jm, b_kp] = delta_{jk}*b_im + delta_{ik}*b_jm
                        if k == j:
                            new_sign = a_sgn + 'm'
                            add(f"E_del{i}_del{j}_mm", Yg, f"E_eps1_del{i}_{new_sign}", Fraction(1))
                        if k == i:
                            new_sign = a_sgn + 'm'
                            add(f"E_del{i}_del{j}_mm", Yg, f"E_eps1_del{j}_{new_sign}", Fraction(1))
                    else:
                        pass  # [b_im*b_jm, b_km] = 0

    # [E_del{i}_del{j}_pm, E_eps1_del{k}_{sign}]:
    # = a_{a_sgn} * [b_ip*b_jm, b_k^{b_sgn}]
    # [b_ip*b_jm, b_kp] = b_ip*[b_jm,b_kp] + [b_ip,b_kp]*b_jm = delta_{jk}*b_ip + 0 = delta_{jk}*b_ip
    # [b_ip*b_jm, b_km] = b_ip*[b_jm,b_km] + [b_ip,b_km]*b_jm = 0 + (-delta_{ik})*b_jm = -delta_{ik}*b_jm

    for i, j in itertools.combinations(range(1, n + 1), 2):
        for k in range(1, n + 1):
            for a_sgn in ['p', 'm']:
                for b_sgn in ['p', 'm']:
                    sign = a_sgn + b_sgn
                    Yg = f"E_eps1_del{k}_{sign}"
                    if b_sgn == 'p':
                        if k == j:
                            new_sign = a_sgn + 'p'
                            add(f"E_del{i}_del{j}_pm", Yg, f"E_eps1_del{i}_{new_sign}", Fraction(1))
                    else:
                        if k == i:
                            new_sign = a_sgn + 'm'
                            add(f"E_del{i}_del{j}_pm", Yg, f"E_eps1_del{j}_{new_sign}", Fraction(-1))

    # [E_del{i}_del{j}_mp, E_eps1_del{k}_{sign}]:
    # = a_{a_sgn} * [b_im*b_jp, b_k^{b_sgn}]
    # [b_im*b_jp, b_kp] = b_im*[b_jp,b_kp] + [b_im,b_kp]*b_jp = 0 + delta_{ik}*b_jp = delta_{ik}*b_jp
    # [b_im*b_jp, b_km] = b_im*[b_jp,b_km] + [b_im,b_km]*b_jp = -delta_{jk}*b_im + 0 = -delta_{jk}*b_im

    for i, j in itertools.combinations(range(1, n + 1), 2):
        for k in range(1, n + 1):
            for a_sgn in ['p', 'm']:
                for b_sgn in ['p', 'm']:
                    sign = a_sgn + b_sgn
                    Yg = f"E_eps1_del{k}_{sign}"
                    if b_sgn == 'p':
                        if k == i:
                            new_sign = a_sgn + 'p'
                            add(f"E_del{i}_del{j}_mp", Yg, f"E_eps1_del{j}_{new_sign}", Fraction(1))
                    else:
                        if k == j:
                            new_sign = a_sgn + 'm'
                            add(f"E_del{i}_del{j}_mp", Yg, f"E_eps1_del{i}_{new_sign}", Fraction(-1))

    # [E_2del{k}_p, E_eps1_del{l}_{sign}]:
    # = a_{a_sgn} * [(1/2)b_kp^2, b_l^{b_sgn}]
    # [(1/2)b_kp^2, b_lm] = (1/2)*[b_kp^2, b_lm] = (1/2)*(-2*delta_{kl}*b_kp) = -delta_{kl}*b_kp
    # [(1/2)b_kp^2, b_lp] = 0

    for k in range(1, n + 1):
        for l in range(1, n + 1):
            for a_sgn in ['p', 'm']:
                for b_sgn in ['p', 'm']:
                    sign = a_sgn + b_sgn
                    Yg = f"E_eps1_del{l}_{sign}"
                    if b_sgn == 'm' and k == l:
                        new_sign = a_sgn + 'p'
                        add(f"E_2del{k}_p", Yg, f"E_eps1_del{k}_{new_sign}", Fraction(-1))

    # [E_2del{k}_m, E_eps1_del{l}_{sign}]:
    # [(1/2)b_km^2, b_lp] = (1/2)*[b_km^2, b_lp] = (1/2)*(2*delta_{kl}*b_km) = delta_{kl}*b_km
    # [(1/2)b_km^2, b_lm] = 0

    for k in range(1, n + 1):
        for l in range(1, n + 1):
            for a_sgn in ['p', 'm']:
                for b_sgn in ['p', 'm']:
                    sign = a_sgn + b_sgn
                    Yg = f"E_eps1_del{l}_{sign}"
                    if b_sgn == 'p' and k == l:
                        new_sign = a_sgn + 'm'
                        add(f"E_2del{k}_m", Yg, f"E_eps1_del{k}_{new_sign}", Fraction(1))

    return sc


def build_schema1(n):
    even, odd = build_basis(n)
    basis_all = odd + even
    parity = build_parity_dict(even, odd)
    sc = compute_structure_constants(n, even, odd)
    total_dim = 2 * n * n + 5 * n + 1
    even_dim = 2 * n * n + n + 1
    odd_dim = 4 * n

    # Fermion and boson labels
    fermion_labels = ["a_1_p", "a_1_m"]
    boson_labels = []
    for k in range(1, n + 1):
        boson_labels += [f"b_{k}_p", f"b_{k}_m"]

    # Realization descriptions
    realizations = {}
    realizations["H_1"] = {
        "standard_form": [
            {"words": ["a_1_p", "a_1_m"], "coeff": "1"},
            {"words": ["b_1_p", "b_1_m"], "coeff": "1"}
        ],
        "frappat_form": "a_1^+ a_1^- + b_1^+ b_1^-",
        "parity": 0
    }
    for k in range(2, n + 1):
        realizations[f"H_{k}"] = {
            "standard_form": [
                {"words": [f"b_{k-1}_p", f"b_{k-1}_m"], "coeff": "1"},
                {"words": [f"b_{k}_p", f"b_{k}_m"], "coeff": "-1"}
            ],
            "frappat_form": f"b_{k-1}^+ b_{k-1}^- - b_{k}^+ b_{k}^-",
            "parity": 0
        }
    realizations[f"H_{n+1}"] = {
        "standard_form": [
            {"words": [f"b_{n}_p", f"b_{n}_m"], "coeff": "-1"},
            {"words": [], "coeff": "-1/2"}
        ],
        "frappat_form": f"-b_{n}^+ b_{n}^- - 1/2",
        "parity": 0,
        "note": "Terminal Cartan"
    }
    for k in range(1, n + 1):
        for sign, a, b in [("pp", "a_1_p", f"b_{k}_p"), ("pm", "a_1_p", f"b_{k}_m"),
                            ("mp", "a_1_m", f"b_{k}_p"), ("mm", "a_1_m", f"b_{k}_m")]:
            realizations[f"E_eps1_del{k}_{sign}"] = {
                "standard_form": [{"words": [a, b], "coeff": "1"}],
                "frappat_form": f"{a}*{b}",
                "parity": 1
            }
    for k in range(1, n + 1):
        realizations[f"E_2del{k}_p"] = {
            "standard_form": [{"words": [f"b_{k}_p", f"b_{k}_p"], "coeff": "1/2"}],
            "frappat_form": f"(1/2)*(b_{k}^+)^2",
            "parity": 0
        }
        realizations[f"E_2del{k}_m"] = {
            "standard_form": [{"words": [f"b_{k}_m", f"b_{k}_m"], "coeff": "1/2"}],
            "frappat_form": f"(1/2)*(b_{k}^-)^2",
            "parity": 0
        }
    for i, j in itertools.combinations(range(1, n + 1), 2):
        for sign, a, b in [("pp", f"b_{i}_p", f"b_{j}_p"), ("mm", f"b_{i}_m", f"b_{j}_m"),
                            ("pm", f"b_{i}_p", f"b_{j}_m"), ("mp", f"b_{i}_m", f"b_{j}_p")]:
            realizations[f"E_del{i}_del{j}_{sign}"] = {
                "standard_form": [{"words": [a, b], "coeff": "1"}],
                "frappat_form": f"{a}*{b}",
                "parity": 0
            }

    schema = {
        "schema_version": "5.0",
        "algebra": {
            "family": "C",
            "m": 1,
            "n": n,
            "cartan_type": f"C({n+1})",
            "alternative_notation": {
                "osp": f"osp(2|{2*n})",
                "dimension_formula": "osp(2m|2n) with m=1"
            },
            "dimension": {
                "total": total_dim,
                "even": even_dim,
                "odd": odd_dim,
                "even_formula": "2n^2 + n + 1",
                "odd_formula": "4n"
            }
        },
        "oscillator_generators": {
            "fermions": {
                "m": 1,
                "labels": fermion_labels,
                "parity": 1,
                "description": "Standard CAR pair: {a_1^-, a_1^+} = 1"
            },
            "bosons": {
                "count": 2 * n,
                "n": n,
                "labels": boson_labels,
                "description": "Bosonic oscillators b_i^+/- with CCR [b_i^-, b_j^+] = delta_{ij}"
            }
        },
        "oscillator_relations": {
            "standard_fermion_anticommutators": {
                "description": "CAR: {a_1^-, a_1^+} = 1",
                "relations": {
                    "anticommutator": "{a_1_m, a_1_p} = 1",
                    "same_sign_p": "{a_1_p, a_1_p} = 0",
                    "same_sign_m": "{a_1_m, a_1_m} = 0"
                }
            },
            "bosonic_commutators": {
                "description": "CCR",
                "relations": {
                    "same_sign": "[b_i^pm, b_j^pm] = 0",
                    "conjugate_pair": "[b_i^-, b_j^+] = delta_{ij}"
                }
            },
            "mixed_commutators": {
                "boson_fermion": "[b_i^pm, a_1^pm] = 0 (undeformed)"
            }
        },
        "central_elements": {
            "K": {
                "parity": 0,
                "description": "Even central identity; identified with 1 in applications.",
                "note": "Not an independent basis element."
            },
            "kappa": {
                "parity": 1,
                "description": "Odd nilpotent central element; kappa^2=0.",
                "nilpotency": "kappa^2 = 0"
            }
        },
        "basis": {
            "even": even,
            "odd": odd,
            "ordering_convention": "PBW: kappa < [odd: E_eps1_del{k}_{pp,pm,mp,mm}] < [even: H, raising, lowering, mixed]"
        },
        "parity": parity,
        "generator_realization": {
            "description": "PBW-ordered oscillator words",
            "ordering": ", ".join(fermion_labels + boson_labels),
            "realizations": realizations
        },
        "structure_constants": sc,
        "metadata": {
            "generated_by": "src/C_generators.py",
            "generation_date": str(date.today()),
            "references": [
                "Frappat, Sciarrino, Sorba (2000)",
                "arXiv:hep-th/9607161"
            ]
        }
    }
    return schema


def main():
    import os
    os.makedirs("data", exist_ok=True)
    for n in [1, 2, 3]:
        schema = build_schema1(n)
        fname = f"data/C_{n}_structure.json"
        with open(fname, "w") as f:
            json.dump(schema, f, indent=2)
        even_count = len(schema["basis"]["even"])
        odd_count = len(schema["basis"]["odd"])
        sc_count = len(schema["structure_constants"])
        print(f"C_{n}: even={even_count}, odd={odd_count}, structure_constants={sc_count} -> {fname}")


if __name__ == "__main__":
    main()
