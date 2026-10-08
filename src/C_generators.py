"""
C_generators.py
Generate Schema 1 structure-constant JSON for C(n+1) = osp(2|2n).

Mathematical basis: Frappat, Sciarrino, Sorba (2000); docs/math/Cn1_definition.md.
All structure constants are derived from the oscillator realization:
  a1p, a1m: standard fermionic pair, {a1m, a1p} = 1, (a1p)^2 = (a1m)^2 = 0.
  bkp, bkm: bosonic, [bkm, bkp] = 1 (same k), cross-commutators zero.
  Boson-fermion: all commute.
"""

import json
import os
from fractions import Fraction
from itertools import combinations


# ---------------------------------------------------------------------------
# Basis construction
# ---------------------------------------------------------------------------

def build_basis(n):
    """Return (basis_even, basis_odd) lists for C(n+1)."""
    cartans = [f"H_{k}" for k in range(1, n + 2)]

    pos_2del = [f"E_2del{k}_p" for k in range(1, n + 1)]
    pos_2del_del = [f"E_del{i}_del{j}_pp"
                    for i in range(1, n + 1) for j in range(i + 1, n + 1)]

    neg_2del = [f"E_2del{k}_m" for k in range(1, n + 1)]
    neg_2del_del = [f"E_del{i}_del{j}_mm"
                    for i in range(1, n + 1) for j in range(i + 1, n + 1)]

    mixed = [lbl
             for i in range(1, n + 1) for j in range(i + 1, n + 1)
             for lbl in (f"E_del{i}_del{j}_pm", f"E_del{i}_del{j}_mp")]

    basis_even = cartans + pos_2del + pos_2del_del + neg_2del + neg_2del_del + mixed

    basis_odd = [f"E_eps1_del{k}_{s1}{s2}"
                 for k in range(1, n + 1)
                 for s1 in ("p", "m") for s2 in ("p", "m")]

    return basis_even, basis_odd


def parity_of(label):
    return 1 if label.startswith("E_eps1") else 0


# ---------------------------------------------------------------------------
# Eigenvalue computation: [H_k, E_alpha] = lambda_k(alpha) * E_alpha
# ---------------------------------------------------------------------------

def cartan_eigenvalue(h_idx, gen_label, n):
    """
    Eigenvalue of gen_label under H_{h_idx} (1-indexed).
    H_1 = N_f + N_b1
    H_k = N_b{k-1} - N_bk  for k=2..n
    H_{n+1} = -N_bn  (the -1/2 constant commutes trivially)
    """
    lbl = gen_label

    def nf_charge():
        if "eps1" not in lbl:
            return 0
        # label format: E_eps1_del{k}_{s1}{s2}
        parts = lbl.split("_")  # ["E","eps1","del{k}","{s1}{s2}"]
        s1 = parts[3][0]  # first char of suffix
        return 1 if s1 == "p" else -1

    def nbk_charge(k):
        if lbl.startswith("H_"):
            return 0
        if lbl.startswith("E_2del"):
            rest = lbl[len("E_2del"):]
            num = int(rest.split("_")[0])
            sgn = 1 if rest.endswith("_p") else -1
            return 2 * sgn if num == k else 0
        if lbl.startswith("E_del") and "eps" not in lbl:
            # format: E_del{i}_del{j}_{suffix}
            rest = lbl[len("E_"):]  # "del{i}_del{j}_{suffix}"
            tokens = rest.split("_")  # ["del{i}", "del{j}", "{suffix}"]
            i = int(tokens[0][3:])
            j = int(tokens[1][3:])
            suffix = tokens[2]  # pp, pm, mp, mm
            si = 1 if suffix[0] == "p" else -1
            sj = 1 if suffix[1] == "p" else -1
            charge = 0
            if i == k:
                charge += si
            if j == k:
                charge += sj
            return charge
        if "eps1" in lbl:
            parts = lbl.split("_")
            k_idx = int(parts[2][len("del"):])
            s2 = parts[3][1]  # second char of ss: 'p' or 'm'
            return (1 if s2 == "p" else -1) if k_idx == k else 0
        return 0

    if h_idx == 1:
        return Fraction(nf_charge() + nbk_charge(1))
    elif 2 <= h_idx <= n:
        return Fraction(nbk_charge(h_idx - 1) - nbk_charge(h_idx))
    else:  # h_idx == n+1
        return Fraction(-nbk_charge(n))


# ---------------------------------------------------------------------------
# Structure constants
# ---------------------------------------------------------------------------

def rational_str(f):
    if f.denominator == 1:
        return str(f.numerator)
    return f"{f.numerator}/{f.denominator}"


def build_structure_constants(n, basis_even, basis_odd):
    """
    Returns list of structure-constant entries:
    {"X": ..., "Y": ..., "result": [{"Z": ..., "coeff": ...}], "sign_rule": "graded"}

    Covers:
    (a) [H_k, E_alpha]
    (b) {odd, odd} brackets
    (c) [even root, even root] brackets (non-Cartan)
    (d) [even root, odd] brackets
    """
    sc = []

    all_basis = basis_even + basis_odd

    # Helper: express N_{bk} in terms of H_j generators
    # N_{bk} = sum_{j=k+1}^{n} H_j - H_{n+1} - (1/2) K
    def nbk_in_basis(k):
        result = []
        for j in range(k + 1, n + 1):
            result.append({"Z": f"H_{j}", "coeff": rational_str(Fraction(1))})
        result.append({"Z": f"H_{n+1}", "coeff": rational_str(Fraction(-1))})
        result.append({"Z": "K", "coeff": rational_str(Fraction(-1, 2))})
        return result

    # Helper: express N_f in terms of H_j generators
    # N_f = H_1 - sum_{j=2}^{n} H_j + H_{n+1} + (1/2) K
    #      (derived: N_f = H_1 - N_b1 and N_b1 = sum_{j=2}^{n} H_j - H_{n+1} - 1/2)
    def nf_in_basis():
        result = [{"Z": "H_1", "coeff": rational_str(Fraction(1))}]
        for j in range(2, n + 1):
            result.append({"Z": f"H_{j}", "coeff": rational_str(Fraction(-1))})
        result.append({"Z": f"H_{n+1}", "coeff": rational_str(Fraction(1))})
        result.append({"Z": "K", "coeff": rational_str(Fraction(1, 2))})
        return result

    # (a) Cartan-root brackets [H_k, E_alpha] = lambda * E_alpha
    for k in range(1, n + 2):
        hk = f"H_{k}"
        for gen in basis_even + basis_odd:
            if gen.startswith("H_"):
                continue  # [H, H] = 0
            ev = cartan_eigenvalue(k, gen, n)
            if ev != 0:
                sc.append({
                    "X": hk, "Y": gen,
                    "result": [{"Z": gen, "coeff": rational_str(ev)}],
                    "sign_rule": "graded"
                })

    # (b) Odd-odd brackets {E_eps1_delk_s1s2, E_eps1_dell_t1t2}
    # Result = bks * blt (where s=s2, t=t2 oscillator signs of the two generators)
    # We use anti-commutator since both are odd.
    # {a1p bks, a1m blt} = bks * blt  (using {a1p,a1m}=1)
    # {a1p bks, a1p blt} = 0          (using a1p^2=0)
    # {a1m bks, a1m blt} = 0          (using a1m^2=0)
    for g1 in basis_odd:
        for g2 in basis_odd:
            if g2 <= g1:
                continue  # process ordered pairs only
            # Parse: E_eps1_del{k}_{s1}{s2}
            parts1 = g1.split("_")  # ['E', 'eps1', 'del{k}', '{s1}{s2}']
            parts2 = g2.split("_")
            k1 = int(parts1[2][3:])
            k2 = int(parts2[2][3:])
            s1 = parts1[3]  # 'pp','pm','mp','mm'
            s2 = parts2[3]

            ferm1 = s1[0]  # 'p' or 'm' (a1 sign)
            bos1  = s1[1]  # 'p' or 'm' (bk sign)
            ferm2 = s2[0]
            bos2  = s2[1]

            # {a1^ferm1 bk1^bos1, a1^ferm2 bk2^bos2}
            if ferm1 == ferm2:
                # Both use a1p or both a1m → zero
                continue

            # Opposite fermion signs: result = bk1^bos1 * bk2^bos2
            # Figure out which Z this corresponds to
            if k1 == k2:
                k = k1
                if bos1 == "p" and bos2 == "p":
                    z_label = f"E_2del{k}_p"
                    res = [{"Z": z_label, "coeff": "1"}]
                elif bos1 == "m" and bos2 == "m":
                    z_label = f"E_2del{k}_m"
                    res = [{"Z": z_label, "coeff": "1"}]
                elif bos1 == "p" and bos2 == "m":
                    # bkp bkm = N_{bk}: involves H_j + K
                    # Ensure ferm1='p' is paired with ferm2='m'
                    res = nbk_in_basis(k)
                elif bos1 == "m" and bos2 == "p":
                    # bkm bkp = N_{bk} + 1: add 1*K to nbk_in_basis
                    res_base = nbk_in_basis(k)
                    res = [r.copy() for r in res_base]
                    # Add +1 to K coeff
                    k_entry = next((r for r in res if r["Z"] == "K"), None)
                    if k_entry:
                        k_entry["coeff"] = rational_str(
                            Fraction(k_entry["coeff"]) + Fraction(1))
                    else:
                        res.append({"Z": "K", "coeff": "1"})
            else:
                # k1 != k2, ensure i < j convention
                i, j = (k1, k2) if k1 < k2 else (k2, k1)
                bs_i = bos1 if k1 < k2 else bos2
                bs_j = bos2 if k1 < k2 else bos1
                suffix = bs_i + bs_j
                z_label = f"E_del{i}_del{j}_{suffix}"
                res = [{"Z": z_label, "coeff": "1"}]

            # Determine X, Y ordering: use alphabetical order for reproducibility
            # The graded bracket {X,Y} = {Y,X} for odd-odd (symmetric), so sign is +1
            sc.append({
                "X": g1, "Y": g2,
                "result": res,
                "sign_rule": "graded"
            })

    # (c) Even root-root brackets (non-Cartan)
    # [E_2deli_p, E_2deli_m] = -(4N_bi + 2) = 4H_{n+1} - 4*sum_{j=i+1}^{n} H_j
    for k in range(1, n + 1):
        res = [{"Z": f"H_{n+1}", "coeff": "4"}]
        for j in range(k + 1, n + 1):
            res.append({"Z": f"H_{j}", "coeff": "-4"})
        sc.append({
            "X": f"E_2del{k}_p", "Y": f"E_2del{k}_m",
            "result": res,
            "sign_rule": "graded"
        })

    # [E_deli_delj_pp, E_deli_delj_mm] = -(N_bi + N_bj + 1) (no K)
    # = -(N_bi + N_bj) - 1 K ... wait: -N_bi - N_bj - 1
    # = -(sum_{l=i+1}^n H_l - H_{n+1} - 1/2) - (sum_{l=j+1}^n H_l - H_{n+1} - 1/2) - 1
    # = -sum_{l=i+1}^n H_l - sum_{l=j+1}^n H_l + 2*H_{n+1} + 1 - 1
    # = -sum_{l=i+1}^n H_l - sum_{l=j+1}^n H_l + 2*H_{n+1}  (NO K term)
    for i in range(1, n + 1):
        for j in range(i + 1, n + 1):
            res = {f"H_{n+1}": Fraction(2)}
            for l in range(i + 1, n + 1):
                res[f"H_{l}"] = res.get(f"H_{l}", Fraction(0)) - 1
            for l in range(j + 1, n + 1):
                res[f"H_{l}"] = res.get(f"H_{l}", Fraction(0)) - 1
            # Remove zero entries
            result_list = [{"Z": k, "coeff": rational_str(v)}
                           for k, v in res.items() if v != 0]
            sc.append({
                "X": f"E_del{i}_del{j}_pp", "Y": f"E_del{i}_del{j}_mm",
                "result": result_list,
                "sign_rule": "graded"
            })

    # [E_deli_delj_pm, E_deli_delj_mp] = N_bi - N_bj = sum_{l=i+1}^{j} H_l
    for i in range(1, n + 1):
        for j in range(i + 1, n + 1):
            # N_{bi} - N_{bj}: since N_{bk} = sum_{l=k+1}^n H_l - H_{n+1} - 1/2
            # N_{bi} - N_{bj} = sum_{l=i+1}^j H_l  (H_{n+1} and K cancel)
            result_list = [{"Z": f"H_{l}", "coeff": "1"}
                           for l in range(i + 1, j + 1)]
            sc.append({
                "X": f"E_del{i}_del{j}_pm", "Y": f"E_del{i}_del{j}_mp",
                "result": result_list,
                "sign_rule": "graded"
            })

    # [E_deli_delj_pm, E_delj_delk_pm] = E_deli_delk_pm for i<j<k (chain)
    for i in range(1, n + 1):
        for j in range(i + 1, n + 1):
            for k in range(j + 1, n + 1):
                sc.append({
                    "X": f"E_del{i}_del{j}_pm", "Y": f"E_del{j}_del{k}_pm",
                    "result": [{"Z": f"E_del{i}_del{k}_pm", "coeff": "1"}],
                    "sign_rule": "graded"
                })

    # [E_deli_delj_mp, E_delj_delk_mp] = E_deli_delk_mp for i<j<k (chain)
    for i in range(1, n + 1):
        for j in range(i + 1, n + 1):
            for k in range(j + 1, n + 1):
                sc.append({
                    "X": f"E_del{i}_del{j}_mp", "Y": f"E_del{j}_del{k}_mp",
                    "result": [{"Z": f"E_del{i}_del{k}_mp", "coeff": "1"}],
                    "sign_rule": "graded"
                })

    # [E_deli_delj_pm, E_delj_delk_pp] = E_deli_delk_pp  (bip bjm * bjp bkp)
    # bip bjm * bjp bkp = bip (bjm bjp) bkp = bip (N_bj+1) bkp
    # minus bjp bkp * bip bjm = bjp bkp bip bjm = bip bjp bkp bjm = bip (bkp bjm) = bip bjm bkp...
    # These are even-even brackets; let me enumerate via oscillator action.
    # [bip bjm, bjp bkp] for i<j<k:
    #   = bip bjm bjp bkp - bjp bkp bip bjm
    #   = bip (N_bj+1) bkp - bip bjp bkp bjm  (using bjm bjp = N_bj+1, bkp commutes with bip)
    #   = bip bkp N_bj + bip bkp - bip bjp bjm bkp  (bkp commutes with bip, bjp; bjm->right)
    #   Hmm, this is getting complex. Let me compute in Fock space.
    # Actually: [bip bjm, bjp bkp] (k different from i, j with k>j>i):
    # bip commutes with bjp, bjm, bkp (different indices).
    # bjm bjp = N_bj+1 (CCR).
    # bip bjm bjp bkp = bip (bjm bjp) bkp = bip (N_bj+1) bkp  → acts as bip bkp on state with N_bj → this is bip bkp * (N_bj+1)
    # bjp bkp bip bjm = bip (bjp bkp) bjm  (commute bip past, bkp commutes with bjm)
    # = bip bjp bkp bjm
    # Hmm: bkp bjm commute (different indices), so = bip bjp bjm bkp... wait bjm bkp = bkp bjm for j≠k.
    # = bip bjp bkp bjm = bip bjp bjm bkp  (commute bkp and bjm) → No: bkp comes after bjm since j≠k.
    # Let me just enumerate directly based on the algebra structure.
    # It's known that for sp(2n), [E_{δi-δj}, E_{δj+δk}] = E_{δi+δk} for i<j<k.

    for i in range(1, n + 1):
        for j in range(i + 1, n + 1):
            for k in range(j + 1, n + 1):
                # [E_del{i}_del{j}_pm, E_del{j}_del{k}_pp] = E_del{i}_del{k}_pp
                sc.append({
                    "X": f"E_del{i}_del{j}_pm", "Y": f"E_del{j}_del{k}_pp",
                    "result": [{"Z": f"E_del{i}_del{k}_pp", "coeff": "1"}],
                    "sign_rule": "graded"
                })
                # [E_del{j}_del{k}_mp, E_del{i}_del{j}_mm] = E_del{i}_del{k}_mm  (dual)
                sc.append({
                    "X": f"E_del{j}_del{k}_mp", "Y": f"E_del{i}_del{j}_mm",
                    "result": [{"Z": f"E_del{i}_del{k}_mm", "coeff": "1"}],
                    "sign_rule": "graded"
                })

    # [E_2delk_p, E_deli_delk_pm] = -2 * E_deli_delk_pp  (for i<k)
    # [bkp bkp, bip bkm] = bkp bkp bip bkm - bip bkm bkp bkp
    # = bip bkp bkp bkm - bip (bkm bkp bkp)...
    # Fock space: (b^+)^2 b^- |n⟩ = n(n-1)|n-2⟩ applied to bk mode; bi is unchanged.
    # [(bkp)^2, bkm] = -2 bkp  (derived earlier)
    # So [E_2delk_p, E_deli_delk_pm] = bip [(bkp)^2, bkm] = bip (-2 bkp) = -2 bip bkp = -2 E_del{i}_del{k}_pp
    for k in range(1, n + 1):
        for i in range(1, n + 1):
            if i == k:
                continue
            min_ij, max_ij = min(i, k), max(i, k)
            # [(bkp)^2, bip bkm]:
            # = bip [(bkp)^2, bkm] = bip * (-2 bkp) = -2 bip bkp
            if i < k:
                z = f"E_del{i}_del{k}_pp"
            else:
                z = f"E_del{k}_del{i}_pp"
            sc.append({
                "X": f"E_2del{k}_p", "Y": f"E_del{min_ij}_del{max_ij}_pm" if i < k else f"E_del{min_ij}_del{max_ij}_mp",
                "result": [{"Z": z, "coeff": "-2"}],
                "sign_rule": "graded"
            })

    # [E_2delk_m, E_deli_delk_mp] = 2 * E_deli_delk_mm  (dual)
    for k in range(1, n + 1):
        for i in range(1, n + 1):
            if i == k:
                continue
            min_ij, max_ij = min(i, k), max(i, k)
            if i < k:
                z = f"E_del{i}_del{k}_mm"
                y_label = f"E_del{i}_del{k}_mp"
            else:
                z = f"E_del{k}_del{i}_mm"
                y_label = f"E_del{k}_del{i}_pm"
            sc.append({
                "X": f"E_2del{k}_m", "Y": y_label,
                "result": [{"Z": z, "coeff": "2"}],
                "sign_rule": "graded"
            })

    # [E_2deln_p, E_2deln_p] = 0 (same element), skip

    # (d) Even root acts on odd generators
    # [E_2delk_p, E_eps1_delk_pm] = -2 E_eps1_delk_pp  (derived: a1p [(bkp)^2, bkm] = -2 a1p bkp)
    # [E_2delk_p, E_eps1_delk_mm] = -2 E_eps1_delk_mp  (a1m [(bkp)^2, bkm] = -2 a1m bkp)
    # [E_2delk_m, E_eps1_delk_pp] =  2 E_eps1_delk_pm  (a1p [(bkm)^2, bkp] = 2 a1p bkm)
    # [E_2delk_m, E_eps1_delk_mp] =  2 E_eps1_delk_mm  (a1m [(bkm)^2, bkp] = 2 a1m bkm)
    for k in range(1, n + 1):
        sc.append({
            "X": f"E_2del{k}_p", "Y": f"E_eps1_del{k}_pm",
            "result": [{"Z": f"E_eps1_del{k}_pp", "coeff": "-2"}],
            "sign_rule": "graded"
        })
        sc.append({
            "X": f"E_2del{k}_p", "Y": f"E_eps1_del{k}_mm",
            "result": [{"Z": f"E_eps1_del{k}_mp", "coeff": "-2"}],
            "sign_rule": "graded"
        })
        sc.append({
            "X": f"E_2del{k}_m", "Y": f"E_eps1_del{k}_pp",
            "result": [{"Z": f"E_eps1_del{k}_pm", "coeff": "2"}],
            "sign_rule": "graded"
        })
        sc.append({
            "X": f"E_2del{k}_m", "Y": f"E_eps1_del{k}_mp",
            "result": [{"Z": f"E_eps1_del{k}_mm", "coeff": "2"}],
            "sign_rule": "graded"
        })

    # [E_deli_delj_pp, E_eps1_delj_pm] = E_eps1_deli_pp (bip bjp acts on a1p bjm)
    # [bip bjp, a1p bjm] = a1p [bip bjp, bjm] = a1p bip [bjp, bjm] = a1p bip (-1)...
    # Actually: [bjp, bjm] in the Lie bracket = -(N_bj+1-N_bj)... let me use:
    # [bip bjp, a1p bjm]: bip and bjp act on different modes from bjm (j mode is shared).
    # a1p commutes with all b's.
    # [bip bjp, a1p bjm] = a1p [bip bjp, bjm] (since a1p commutes with bip, bjp, bjm)
    # [bip bjp, bjm]: bip commutes with bjm (different mode), so = bip [bjp, bjm].
    # [bjp, bjm] = ? In the standard Lie algebra bracket: [E_{2δj}, E_{δi-δj}] type.
    # Using [(bkp)^2, bkm] = -2 bkp, so [bjp bjp, bjm] = -2 bjp.
    # But [bip bjp, bjm]:
    # = bip bjp bjm - bjm bip bjp
    # = bip (bjp bjm) - bip bjm bjp  (bip commutes with bjm since i≠j)
    # = bip (N_bj) - bip (bjm bjp)  ... but bjp bjm = N_bj and bjm bjp = N_bj + 1.
    # So [bip bjp, bjm] = bip N_bj - bip (N_bj+1) = -bip.
    # Therefore [E_deli_delj_pp, E_eps1_delj_pm] = a1p * (-bip) = -a1p bip = -E_eps1_deli_pp.

    for i in range(1, n + 1):
        for j in range(1, n + 1):
            if i == j:
                continue
            min_ij, max_ij = min(i, j), max(i, j)
            if i < j:
                x_label = f"E_del{i}_del{j}_pp"
            else:
                x_label = f"E_del{j}_del{i}_pp"
            # [E_del{i}_del{j}_pp, E_eps1_del{j}_pm] = -E_eps1_del{i}_pp
            sc.append({
                "X": x_label, "Y": f"E_eps1_del{j}_pm",
                "result": [{"Z": f"E_eps1_del{i}_pp", "coeff": "-1"}],
                "sign_rule": "graded"
            })
            # [E_del{i}_del{j}_mm, E_eps1_del{j}_mp] = E_eps1_del{i}_mm (dual)
            if i < j:
                x_label_mm = f"E_del{i}_del{j}_mm"
            else:
                x_label_mm = f"E_del{j}_del{i}_mm"
            sc.append({
                "X": x_label_mm, "Y": f"E_eps1_del{j}_mp",
                "result": [{"Z": f"E_eps1_del{i}_mm", "coeff": "1"}],
                "sign_rule": "graded"
            })

    # [E_deli_delj_pm, E_eps1_deli_pp] = E_eps1_delj_pp
    # [bip bjm, a1p bip] = a1p [bip bjm, bip] = a1p bjm [bip, bip] + a1p [bip,bip] bjm?
    # No: [bip bjm, bip] = bip bjm bip - bip bip bjm = bip (bjm bip) - 0
    # = bip bjm bip (since (bip)^2=0? No, bip is bosonic! (bip)^2 ≠ 0 for bosons.)
    # Wait: bip is a bosonic creation operator, so (bip)^2 is nonzero.
    # [bip bjm, bip] = bip bjm bip - bip bip bjm (bosonic; i<j)
    # = bip (bjm bip) - (bip)^2 bjm  [bip and bjm commute since i≠j]
    # = bip bip bjm - (bip)^2 bjm = 0!
    # Hmm, that's 0. Let me reconsider.
    # [E_deli_delj_pm, E_eps1_deli_pp]: i < j.
    # X = bip bjm, Y = a1p bip. [Even, Odd] = [bip bjm, a1p bip] = a1p [bip bjm, bip]
    # [bip bjm, bip] = bip bjm bip - bip bip bjm  (bip,bjm commute; bip^2 ≠ 0)
    # = (bip)^2 bjm - (bip)^2 bjm = 0. So this is zero!
    # Wait: bip bjm bip: since i≠j, bip and bjm commute, so bip bjm bip = bip bip bjm = (bip)^2 bjm.
    # And bip bip bjm = (bip)^2 bjm. So [bip bjm, bip] = 0. ✓

    # Let me compute [E_deli_delj_pm, E_eps1_delj_mp] = ?
    # X = bip bjm, Y = a1m bjp. [Even, Odd] = a1m [bip bjm, bjp]
    # [bip bjm, bjp]: bip commutes with bjp (i≠j). bjm bjp = N_bj+1.
    # [bip bjm, bjp] = bip bjm bjp - bjp bip bjm = bip (bjm bjp) - bip (bjp bjm)
    # = bip (N_bj+1) - bip N_bj = bip.
    # So [E_deli_delj_pm, E_eps1_delj_mp] = a1m bip = E_eps1_deli_mp.

    for i in range(1, n + 1):
        for j in range(i + 1, n + 1):
            sc.append({
                "X": f"E_del{i}_del{j}_pm", "Y": f"E_eps1_del{j}_mp",
                "result": [{"Z": f"E_eps1_del{i}_mp", "coeff": "1"}],
                "sign_rule": "graded"
            })
            # Dual: [E_deli_delj_mp, E_eps1_deli_pm] = -E_eps1_delj_pm
            # [bim bjp, a1p bim] = a1p [bim bjp, bim] = a1p bjp [bim, bim] = 0? No.
            # [bim bjp, bim] = bim bjp bim - bim bim bjp
            # = bim bim bjp - bim bim bjp = 0? (since i≠j means bim and bjp commute)
            # Actually: bim bjp bim = bim bim bjp (commuting bjp past bim: i≠j so they commute)
            # And bim bim bjp = (bim)^2 bjp. So [bim bjp, bim] = 0. OK.

            # [E_deli_delj_mp, E_eps1_delj_pm] = ?
            # X = bim bjp, Y = a1p bjm. [Even, Odd] = a1p [bim bjp, bjm]
            # [bim bjp, bjm]: bim commutes with bjp,bjm? No: bim and bjm are different signs of mode j... wait.
            # bim is b_i^- (mode i), bjm is b_j^- (mode j). i≠j, so they commute.
            # [bim bjp, bjm] = bim [bjp, bjm] = bim [b_j^+, b_j^-] = bim(-1)?
            # [bjp, bjm]: bjp bjm - bjm bjp = N_bj - (N_bj+1) = -1.
            # So [bim bjp, bjm] = bim * (-1) = -bim.
            # [E_deli_delj_mp, E_eps1_delj_pm] = a1p (-bim) = -a1p bim = -E_eps1_deli_pm.
            sc.append({
                "X": f"E_del{i}_del{j}_mp", "Y": f"E_eps1_del{j}_pm",
                "result": [{"Z": f"E_eps1_del{i}_pm", "coeff": "-1"}],
                "sign_rule": "graded"
            })

            # [E_deli_delj_pp, E_eps1_delj_mm] = ?
            # X = bip bjp, Y = a1m bjm. [Even, Odd] = a1m [bip bjp, bjm]
            # [bip bjp, bjm] = bip [bjp, bjm] = bip(-1) = -bip.
            # Result: a1m (-bip) = -a1m bip = -E_eps1_deli_mp.
            sc.append({
                "X": f"E_del{i}_del{j}_pp", "Y": f"E_eps1_del{j}_mm",
                "result": [{"Z": f"E_eps1_del{i}_mp", "coeff": "-1"}],
                "sign_rule": "graded"
            })

            # [E_deli_delj_mm, E_eps1_delj_pp] = ?
            # X = bim bjm, Y = a1p bjp. [Even, Odd] = a1p [bim bjm, bjp]
            # [bim bjm, bjp] = bim [bjm, bjp] = bim(1) = bim.  (using [bjm,bjp]=1)
            # Result: a1p bim = E_eps1_deli_pm.
            sc.append({
                "X": f"E_del{i}_del{j}_mm", "Y": f"E_eps1_del{j}_pp",
                "result": [{"Z": f"E_eps1_del{i}_pm", "coeff": "1"}],
                "sign_rule": "graded"
            })

    return sc


# ---------------------------------------------------------------------------
# Build full Schema 1 JSON
# ---------------------------------------------------------------------------

def build_schema1(n):
    basis_even, basis_odd = build_basis(n)
    sc = build_structure_constants(n, basis_even, basis_odd)

    parity = {g: 0 for g in basis_even}
    parity.update({g: 1 for g in basis_odd})

    boson_labels = [x for k in range(1, n + 1) for x in [f"b{k}p", f"b{k}m"]]

    return {
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
                "total": 2 * n * n + 5 * n + 1,
                "even": 2 * n * n + n + 1,
                "odd": 4 * n
            }
        },
        "central_elements": {
            "K": {"label": "K", "parity": 0,
                  "description": "Even central element; identified with scalar 1.",
                  "in_basis": False},
            "kappa": {"label": "kappa", "parity": 1,
                      "description": "Odd nilpotent central element kappa^2=0.",
                      "in_basis": False}
        },
        "oscillator_generators": {
            "fermions": {
                "m": 1,
                "labels": ["a1p", "a1m"],
                "parity": 1,
                "description": "Standard fermionic pair {a1m, a1p}=1."
            },
            "bosons": {
                "count": 2 * n,
                "n": n,
                "labels": boson_labels,
                "description": f"Bosonic oscillators b_k^+/- for k=1,...,{n}"
            }
        },
        "oscillator_relations": {
            "standard_fermion_anticommutators": {
                "anticommutator": "{a1m, a1p} = 1",
                "nilpotency": "a1p^2 = 0, a1m^2 = 0"
            },
            "bosonic_commutators": {
                "conjugate_pair": "[bkm, bkp] = 1 (same k)",
                "cross": "all other pairs commute"
            },
            "mixed": "all [bkp/m, a1p/m] = 0"
        },
        "basis": {
            "even": basis_even,
            "odd": basis_odd,
            "ordering_convention": "PBW: kappa < [odd] < [even]; K excluded (in_basis=false)"
        },
        "parity": parity,
        "generator_realization": _gen_realization(n),
        "structure_constants": sc,
        "metadata": {
            "generated_by": "C_generators.py",
            "generation_date": "2026-10-09",
            "references": [
                "Frappat, Sciarrino, Sorba (2000), Dictionary on Lie Algebras and Superalgebras",
                "docs/math/Cn1_definition.md"
            ]
        }
    }


def _gen_realization(n):
    r = {}
    r["H_1"] = {
        "standard_form": [{"words": ["a1p", "a1m"], "coeff": "1"},
                          {"words": ["b1p", "b1m"], "coeff": "1"}],
        "frappat_form": "a_1^+ a_1^- + b_1^+ b_1^-", "parity": 0
    }
    for k in range(2, n + 1):
        r[f"H_{k}"] = {
            "standard_form": [{"words": [f"b{k-1}p", f"b{k-1}m"], "coeff": "1"},
                              {"words": [f"b{k}p", f"b{k}m"], "coeff": "-1"}],
            "frappat_form": f"b_{k-1}^+ b_{k-1}^- - b_{k}^+ b_{k}^-", "parity": 0
        }
    r[f"H_{n+1}"] = {
        "standard_form": [{"words": [f"b{n}p", f"b{n}m"], "coeff": "-1"},
                          {"words": [], "coeff": "-1/2"}],
        "frappat_form": f"-b_{n}^+ b_{n}^- - 1/2", "parity": 0,
        "note": "Constant -1/2 reflects the K central element."
    }
    for k in range(1, n + 1):
        for s1, s2 in [("p", "p"), ("p", "m"), ("m", "p"), ("m", "m")]:
            lbl = f"E_eps1_del{k}_{s1}{s2}"
            r[lbl] = {
                "standard_form": [{"words": [f"a1{s1}", f"b{k}{s2}"], "coeff": "1"}],
                "frappat_form": f"a_1^{'+' if s1=='p' else '-'} b_{k}^{'+' if s2=='p' else '-'}",
                "parity": 1
            }
        r[f"E_2del{k}_p"] = {
            "standard_form": [{"words": [f"b{k}p", f"b{k}p"], "coeff": "1"}],
            "frappat_form": f"(b_{k}^+)^2", "parity": 0
        }
        r[f"E_2del{k}_m"] = {
            "standard_form": [{"words": [f"b{k}m", f"b{k}m"], "coeff": "1"}],
            "frappat_form": f"(b_{k}^-)^2", "parity": 0
        }
    for i in range(1, n + 1):
        for j in range(i + 1, n + 1):
            for s1, s2 in [("p", "p"), ("m", "m"), ("p", "m"), ("m", "p")]:
                sfx = s1 + s2
                lbl = f"E_del{i}_del{j}_{sfx}"
                r[lbl] = {
                    "standard_form": [{"words": [f"b{i}{s1}", f"b{j}{s2}"], "coeff": "1"}],
                    "frappat_form": f"b_{i}^{'+' if s1=='p' else '-'} b_{j}^{'+' if s2=='p' else '-'}",
                    "parity": 0
                }
    return r


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    out_dir = os.path.join(os.path.dirname(__file__), "..", "data")
    os.makedirs(out_dir, exist_ok=True)

    for n in [1, 2, 3]:
        schema = build_schema1(n)
        path = os.path.join(out_dir, f"C_{n}_structure.json")
        with open(path, "w") as f:
            json.dump(schema, f, indent=2)
        print(f"Written {path}  (dim={schema['algebra']['dimension']})")


if __name__ == "__main__":
    main()
