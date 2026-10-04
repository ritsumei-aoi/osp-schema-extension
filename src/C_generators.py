"""
C_generators.py
Generator for C(n+1) = osp(2|2n) structure constants (Schema 1, v5.0).

The algebra is realized via oscillators:
  - Standard fermionic pair: a_1^+, a_1^- with {a_1^-, a_1^+} = 1
  - Bosonic oscillators: b_k^+, b_k^- with [b_k^-, b_l^+] = delta_{kl}

Brackets are computed symbolically via the oscillator realization.
"""

import json
import os
from fractions import Fraction
from itertools import combinations


def build_basis(n):
    """Return (even_basis, odd_basis) lists for C(n+1) with bosonic rank n."""
    # Cartan generators: H_1 ... H_{n+1}
    cartans = [f"H_{i}" for i in range(1, n + 2)]

    # Even positive roots: E_2del{k}_p, E_del{i}_del{j}_pp
    even_pos = [f"E_2del{k}_p" for k in range(1, n + 1)]
    even_pos += [f"E_del{i}_del{j}_pp" for i in range(1, n + 1) for j in range(i + 1, n + 1)]

    # Even negative roots: E_2del{k}_m, E_del{i}_del{j}_mm
    even_neg = [f"E_2del{k}_m" for k in range(1, n + 1)]
    even_neg += [f"E_del{i}_del{j}_mm" for i in range(1, n + 1) for j in range(i + 1, n + 1)]

    # Even mixed roots: E_del{i}_del{j}_pm and E_del{i}_del{j}_mp
    even_mixed = []
    for i in range(1, n + 1):
        for j in range(i + 1, n + 1):
            even_mixed.append(f"E_del{i}_del{j}_pm")
            even_mixed.append(f"E_del{i}_del{j}_mp")

    even_basis = cartans + even_pos + even_neg + even_mixed

    # Odd generators: E_eps1_del{k}_{ss} for ss in {pp, pm, mp, mm}
    # Order: a_1^+ sector (pp,pm) then a_1^- sector (mp,mm), by k
    odd_basis = []
    for k in range(1, n + 1):
        odd_basis.append(f"E_eps1_del{k}_pp")
        odd_basis.append(f"E_eps1_del{k}_pm")
    for k in range(1, n + 1):
        odd_basis.append(f"E_eps1_del{k}_mp")
        odd_basis.append(f"E_eps1_del{k}_mm")

    return even_basis, odd_basis


def parity_of(label):
    """Return parity (0 or 1) of a generator by label."""
    if label.startswith("E_eps1"):
        return 1
    return 0


def build_parity_dict(even_basis, odd_basis):
    parity = {}
    for g in even_basis:
        parity[g] = 0
    for g in odd_basis:
        parity[g] = 1
    return parity


def compute_structure_constants(n, even_basis, odd_basis):
    """
    Compute all non-zero structure constants [X, Y} = sum_Z c_{XY}^Z Z
    using the oscillator realization.

    Returns list of dicts: {"X": ..., "Y": ..., "Z": ..., "coeff": "p/q"}
    """
    basis = odd_basis + even_basis  # full PBW-ordered basis (odd first)
    parity = build_parity_dict(even_basis, odd_basis)

    results = []
    seen = set()

    for i, X in enumerate(basis):
        for j, Y in enumerate(basis):
            bracket = graded_bracket(X, Y, n, parity)
            for Z, coeff in bracket.items():
                if coeff != 0 and Z in parity:
                    key = (X, Y, Z)
                    if key not in seen:
                        seen.add(key)
                        results.append({
                            "X": X,
                            "Y": Y,
                            "Z": Z,
                            "coeff": str(coeff),
                            "sign_rule": "graded"
                        })

    return results


def graded_bracket(X, Y, n, parity):
    """
    Compute [X, Y} in C(n+1) using the oscillator realization.
    Returns dict {Z: coeff} (Fraction coefficients).
    """
    px = parity.get(X, 0)
    py = parity.get(Y, 0)

    result = {}

    def add(Z, c):
        if Z is None or c == 0:
            return
        result[Z] = result.get(Z, Fraction(0)) + Fraction(c)

    # Dispatch to bracket rules
    _bracket_add(X, Y, n, parity, add)

    # Apply graded antisymmetry: [Y, X} = -(-1)^{p(X)p(Y)} [X, Y}
    # We compute [X,Y] directly so we don't need to subtract.
    # But we DO need to handle Y<X by symmetry externally.

    return {Z: c for Z, c in result.items() if c != 0}


def _bracket_add(X, Y, n, parity, add):
    """Dispatch bracket [X, Y} rules. Results accumulated via add(Z, coeff)."""
    px = parity.get(X, 0)
    py = parity.get(Y, 0)

    # Parse labels
    Xr = parse_label(X, n)
    Yr = parse_label(Y, n)

    if Xr is None or Yr is None:
        return

    Xt, Xdata = Xr
    Yt, Ydata = Yr

    # H, H -> 0
    if Xt == "H" and Yt == "H":
        return

    # H acts on roots by eigenvalue
    if Xt == "H" and Yt != "H":
        ev = cartan_eigenvalue(Xdata, Y, n)
        if ev != 0:
            add(Y, ev)
        return

    if Xt != "H" and Yt == "H":
        ev = cartan_eigenvalue(Ydata, X, n)
        if ev != 0:
            # [X, H} = -(-1)^{px*py} [H, X} = -[H, X} if py=0
            # For even H: [X, H} = -[H, X} = -ev * X
            add(X, -ev)
        return

    # Both roots: use oscillator algebra
    _root_bracket(Xt, Xdata, Yt, Ydata, n, parity, add)


def parse_label(label, n):
    """Parse a generator label into (type, data) tuple."""
    if label.startswith("H_"):
        idx = int(label[2:])
        return ("H", idx)
    if label.startswith("E_eps1_del"):
        # E_eps1_del{k}_{ss}
        rest = label[len("E_eps1_del"):]
        parts = rest.split("_")
        k = int(parts[0])
        ss = parts[1]
        eps_sign = 1 if ss[0] == "p" else -1
        del_sign = 1 if ss[1] == "p" else -1
        return ("eps_del", (eps_sign, k, del_sign))
    if label.startswith("E_2del"):
        rest = label[len("E_2del"):]
        parts = rest.split("_")
        k = int(parts[0])
        sign = 1 if parts[1] == "p" else -1
        return ("2del", (k, sign))
    if label.startswith("E_del"):
        # Format: E_del{i}_del{j}_{ss}
        rest = label[len("E_del"):]  # e.g. "1_del2_pp"
        # Split on "_del" to get i part and remainder
        idx = rest.find("_del")
        i = int(rest[:idx])
        rest2 = rest[idx + len("_del"):]  # e.g. "2_pp"
        parts2 = rest2.split("_")
        j = int(parts2[0])
        ss = parts2[1]
        s1 = 1 if ss[0] == "p" else -1
        s2 = 1 if ss[1] == "p" else -1
        return ("del_del", (i, j, s1, s2))
    return None


def cartan_eigenvalue(H_idx, Y_label, n):
    """
    Compute eigenvalue of H_{H_idx} acting on root generator Y_label.

    H_1 = a_1^+ a_1^- + b_1^+ b_1^-  → eigenvalue = eps_sign + del_sign*delta_{1,k}
    H_k (2<=k<=n) = b_{k-1}^+b_{k-1}^- - b_k^+b_k^-
    H_{n+1} = -b_n^+b_n^- - 1/2  → eigenvalue contribution from -b_n^+b_n^-
    """
    Yr = parse_label(Y_label, n)
    if Yr is None:
        return 0
    Yt, Ydata = Yr

    if Yt == "H":
        return 0

    if Yt == "eps_del":
        eps_sign, k, del_sign = Ydata
        # Root is eps_sign*epsilon + del_sign*delta_k
        # H_1 = a_1^+a_1^- + b_1^+b_1^-
        if H_idx == 1:
            ev = eps_sign  # from epsilon
            if k == 1:
                ev += del_sign  # from delta_1
            return ev
        # H_m (2<=m<=n): b_{m-1}^+b_{m-1}^- - b_m^+b_m^-
        if 2 <= H_idx <= n:
            m = H_idx
            ev = 0
            if k == m - 1:
                ev += del_sign
            if k == m:
                ev -= del_sign
            return ev
        # H_{n+1} = -b_n^+b_n^- - 1/2; on odd generators the 1/2 doesn't contribute to commutator
        if H_idx == n + 1:
            ev = 0
            if k == n:
                ev -= del_sign
            return ev

    if Yt == "2del":
        k, sign = Ydata
        # Root is 2*sign*delta_k
        if H_idx == 1:
            if k == 1:
                return 2 * sign
            return 0
        if 2 <= H_idx <= n:
            m = H_idx
            ev = 0
            if k == m - 1:
                ev += 2 * sign
            if k == m:
                ev -= 2 * sign
            return ev
        if H_idx == n + 1:
            if k == n:
                return -2 * sign
            return 0

    if Yt == "del_del":
        i, j, s1, s2 = Ydata
        # Root is s1*delta_i + s2*delta_j (i<j)
        if H_idx == 1:
            ev = 0
            if i == 1:
                ev += s1
            if j == 1:
                ev += s2
            return ev
        if 2 <= H_idx <= n:
            m = H_idx
            ev = 0
            if i == m - 1:
                ev += s1
            elif i == m:
                ev -= s1
            if j == m - 1:
                ev += s2
            elif j == m:
                ev -= s2
            return ev
        if H_idx == n + 1:
            ev = 0
            if i == n:
                ev -= s1
            if j == n:
                ev -= s2
            return ev

    return 0


def root_label(root_type, data, n):
    """Convert root data back to generator label, or None if not in basis."""
    if root_type == "eps_del":
        eps_sign, k, del_sign = data
        if k < 1 or k > n:
            return None
        ss = ("p" if eps_sign > 0 else "m") + ("p" if del_sign > 0 else "m")
        return f"E_eps1_del{k}_{ss}"
    if root_type == "2del":
        k, sign = data
        if k < 1 or k > n:
            return None
        return f"E_2del{k}_" + ("p" if sign > 0 else "m")
    if root_type == "del_del":
        i, j, s1, s2 = data
        if i < 1 or j > n or i >= j:
            return None
        ss = ("p" if s1 > 0 else "m") + ("p" if s2 > 0 else "m")
        return f"E_del{i}_del{j}_{ss}"
    if root_type == "H":
        idx = data
        if 1 <= idx <= n + 1:
            return f"H_{idx}"
    return None


def _root_bracket(Xt, Xdata, Yt, Ydata, n, parity, add):
    """Bracket between two root generators using oscillator algebra."""
    px = 1 if Xt == "eps_del" else 0
    py = 1 if Yt == "eps_del" else 0

    # [eps_del, eps_del}: {a_1^{es1}b_k^{ds1}, a_1^{es2}b_l^{ds2}}
    # Full formula: XY+YX = N_a*b_k^{ds1}b_l^{ds2} + (1-N_a)*b_l^{ds2}b_k^{ds1}
    # Non-zero only when es1+es2==0.
    if Xt == "eps_del" and Yt == "eps_del":
        es1, k, ds1 = Xdata
        es2, l, ds2 = Ydata
        if es1 + es2 == 0:
            if k != l:
                # Different bosonic indices: no eps_N mixing -> pure bosonic product
                _identify_boson_product(k, ds1, l, ds2, n, Fraction(1), add)
            elif ds1 == ds2:
                # Same bosonic index, same delta-sign: (b_k^{ds})^2
                sign_str = "p" if ds1 > 0 else "m"
                add(f"E_2del{k}_{sign_str}", Fraction(1))
            elif ds1 * es1 < 0:
                # ds1 opposite to es1: result = eps_N + N_{b_k} = H_1 - H_2 - ... - H_k
                add("H_1", Fraction(1))
                for m in range(2, k + 1):
                    add(f"H_{m}", Fraction(-1))
            else:
                # ds1 same as es1: result = N_{b_k}+1-eps_N
                # = -H_1 + H_2+...+H_k + 2*(H_{k+1}+...+H_n) - 2*H_{n+1}
                add("H_1", Fraction(-1))
                for m in range(2, k + 1):
                    add(f"H_{m}", Fraction(1))
                for m in range(k + 1, n + 1):
                    add(f"H_{m}", Fraction(2))
                add(f"H_{n+1}", Fraction(-2))
        return


    # [2del, 2del}: [(b_k^{s1})^2, (b_l^{s2})^2]
    # = [b_k^s1 b_k^s1, b_l^s2 b_l^s2]
    # Non-zero only if k==l and s1 != s2
    if Xt == "2del" and Yt == "2del":
        k, s1 = Xdata
        l, s2 = Ydata
        if k == l and s1 + s2 == 0:
            # [(b_k^{s1})^2, (b_k^{s2})^2] = s1*(-4N_{b_k} - 2)
            # N_{b_k} = H_{k+1}+...+H_n - H_{n+1} - 1/2 (from Cartan structure)
            # -4N_{b_k} - 2 = -4*(H_{k+1}+...+H_n) + 4*H_{n+1} (constant cancels)
            # Multiply by s1: sign = s1
            sign = s1
            for m in range(k + 1, n + 1):  # H_{k+1} through H_n
                add(f"H_{m}", Fraction(-4 * sign))
            add(f"H_{n+1}", Fraction(4 * sign))
        return

    # [del_del, del_del}: [b_i^{s1}b_j^{s2}, b_k^{t1}b_l^{t2}]
    if Xt == "del_del" and Yt == "del_del":
        i, j, s1, s2 = Xdata
        k, l, t1, t2 = Ydata
        # [b_i^{s1}b_j^{s2}, b_k^{t1}b_l^{t2}]
        # = [b_i^{s1}, b_k^{t1}]b_j^{s2}b_l^{t2} + [b_i^{s1}, b_l^{t2}]b_j^{s2}b_k^{t1}
        # + [b_j^{s2}, b_k^{t1}]b_i^{s1}b_l^{t2} + [b_j^{s2}, b_l^{t2}]b_i^{s1}b_k^{t1}
        # [b_p^{sp}, b_q^{tq}] = sp*delta_{pq}*delta_{sp+tq,0}  (with delta_{sp+tq,0} meaning opposite signs)
        # Actually [b_p^-, b_q^+] = delta_{pq}, all others 0
        # So [b_p^{sp}, b_q^{tq}] != 0 only if sp=-1, tq=+1 (or sp=+1,tq=-1 giving -delta)
        # [b_p^-, b_q^+] = delta_{pq} => [b_p^+, b_q^-] = -delta_{pq}

        def bos_commutator(p, sp, q, tq):
            """[b_p^{sp}, b_q^{tq}]"""
            if sp == -1 and tq == 1 and p == q:
                return Fraction(1)
            if sp == 1 and tq == -1 and p == q:
                return Fraction(-1)
            return Fraction(0)

        # Four terms from Leibniz
        # Term 1: [b_i^{s1}, b_k^{t1}] * b_j^{s2} b_l^{t2}
        c1 = bos_commutator(i, s1, k, t1)
        if c1 != 0:
            _identify_boson_product(j, s2, l, t2, n, c1, add)
        # Term 2: [b_i^{s1}, b_l^{t2}] * b_j^{s2} b_k^{t1}
        c2 = bos_commutator(i, s1, l, t2)
        if c2 != 0:
            _identify_boson_product(j, s2, k, t1, n, c2, add)
        # Term 3: [b_j^{s2}, b_k^{t1}] * b_i^{s1} b_l^{t2}
        c3 = bos_commutator(j, s2, k, t1)
        if c3 != 0:
            _identify_boson_product(i, s1, l, t2, n, c3, add)
        # Term 4: [b_j^{s2}, b_l^{t2}] * b_i^{s1} b_k^{t1}
        c4 = bos_commutator(j, s2, l, t2)
        if c4 != 0:
            _identify_boson_product(i, s1, k, t1, n, c4, add)
        return

    # [2del, del_del}: [(b_k^{s1})^2, b_i^{t1}b_j^{t2}]
    if Xt == "2del" and Yt == "del_del":
        k, s1 = Xdata
        i, j, t1, t2 = Ydata
        # = [b_k^{s1}, b_i^{t1}] b_k^{s1} b_j^{t2} + b_i^{t1} [b_k^{s1}, b_j^{t2}] b_k^{s1}
        # + [b_k^{s1}, b_j^{t2}] b_k^{s1} b_i^{t1} + b_j^{t2} [b_k^{s1}, b_i^{t1}] b_k^{s1}
        # Simpler: [(b_k^s1)^2, b_p^t] = [b_k^s1,b_p^t]*b_k^s1 + b_k^s1*[b_k^s1,b_p^t]
        def bos_comm(p, sp, q, tq):
            if sp == -1 and tq == 1 and p == q:
                return Fraction(1)
            if sp == 1 and tq == -1 and p == q:
                return Fraction(-1)
            return Fraction(0)

        ci1 = bos_comm(k, s1, i, t1)
        ci2 = bos_comm(k, s1, j, t2)
        # [(b_k^s1)^2, b_i^t1 b_j^t2]
        # = ci1*(b_k^s1 b_j^t2 + b_j^t2 b_k^s1) + ci2*(b_k^s1 b_i^t1 + b_i^t1 b_k^s1)
        # For bosons, everything commutes except conjugate pairs, so b_k^s1 b_p^t = b_p^t b_k^s1 + delta
        # Actually for even generators (bosons) the product IS commutative up to deltas already absorbed
        # b_k^s1 b_j^t2 + b_j^t2 b_k^s1 = 2 b_k^s1 b_j^t2 if they commute
        # They commute unless k==j and s1+t2==0, in which case b_k^s1 b_j^t2 = b_j^t2 b_k^s1 - 1
        # So b_k^s1 b_j^t2 + b_j^t2 b_k^s1 = 2b_k^s1 b_j^t2 - delta_{kj, s1t2=-}... hmm
        # Simpler: for generating function purposes,
        # [(b_k^s1)^2, b_i^t1] = 2*bos_comm(k,s1,i,t1)*b_k^s1
        # [(b_k^s1)^2, b_i^t1 b_j^t2] = [(b_k^s1)^2, b_i^t1]*b_j^t2 + b_i^t1*[(b_k^s1)^2, b_j^t2]
        # = 2*ci1*b_k^s1*b_j^t2 + 2*ci2*b_i^t1*b_k^s1
        if ci1 != 0:
            _identify_boson_product(k, s1, j, t2, n, 2 * ci1, add)
        if ci2 != 0:
            _identify_boson_product(i, t1, k, s1, n, 2 * ci2, add)
        return

    # [del_del, 2del}:
    if Xt == "del_del" and Yt == "2del":
        # [X, Y} = -[Y, X} for even generators
        _root_bracket("2del", Ydata, "del_del", Xdata, n, parity, lambda Z, c: add(Z, -c))
        return

    # [eps_del, 2del}: [a_1^{es}b_k^{ds}, (b_l^{ls})^2]
    # a_1 commutes with b, so:
    # = a_1^{es} [(b_k^{ds}), (b_l^{ls})^2]
    # [(b_k^ds), (b_l^ls)^2] = 2*[b_k^ds, b_l^ls]*b_l^ls
    if Xt == "eps_del" and Yt == "2del":
        es, k, ds = Xdata
        l, ls = Ydata
        if k == l and ds + ls == 0:
            # [b_k^ds, b_l^ls] = ds==- and ls==+: gives 1; ds==+, ls==-: gives -1
            c_comm = Fraction(-ds)  # [b^+, b^-] = -1, [b^-, b^+] = 1
            if c_comm != 0:
                # result: 2 * c_comm * a_1^{es} * b_l^{ls}
                new_ss = ("p" if es > 0 else "m") + ("p" if ls > 0 else "m")
                lbl = f"E_eps1_del{l}_{new_ss}"
                add(lbl, 2 * c_comm)
        return

    # [2del, eps_del}: graded antisymmetry: [Y,X} (even,odd) => -[X,Y}
    if Xt == "2del" and Yt == "eps_del":
        _root_bracket("eps_del", Ydata, "2del", Xdata, n, parity, lambda Z, c: add(Z, -c))
        return

    # [eps_del, del_del}: [a_1^{es}b_k^{ds}, b_i^{t1}b_j^{t2}]
    # = a_1^{es} [b_k^{ds}, b_i^{t1}b_j^{t2}]
    # [b_k^ds, b_i^t1 b_j^t2] = [b_k^ds,b_i^t1]*b_j^t2 + b_i^t1*[b_k^ds,b_j^t2]
    if Xt == "eps_del" and Yt == "del_del":
        es, k, ds = Xdata
        i, j, t1, t2 = Ydata
        def bos_c(p, sp, q, tq):
            if sp == -1 and tq == 1 and p == q:
                return Fraction(1)
            if sp == 1 and tq == -1 and p == q:
                return Fraction(-1)
            return Fraction(0)

        ci1 = bos_c(k, ds, i, t1)
        ci2 = bos_c(k, ds, j, t2)
        if ci1 != 0:
            # result: a_1^{es} b_j^{t2} -> E_eps1_del{j}_{es_sign t2_sign}
            new_ss = ("p" if es > 0 else "m") + ("p" if t2 > 0 else "m")
            lbl = f"E_eps1_del{j}_{new_ss}"
            add(lbl, ci1)
        if ci2 != 0:
            new_ss = ("p" if es > 0 else "m") + ("p" if t1 > 0 else "m")
            lbl = f"E_eps1_del{i}_{new_ss}"
            add(lbl, ci2)
        return

    # [del_del, eps_del}: antisymmetry (even, odd)
    if Xt == "del_del" and Yt == "eps_del":
        _root_bracket("eps_del", Ydata, "del_del", Xdata, n, parity, lambda Z, c: add(Z, -c))
        return


def _identify_boson_product(p, sp, q, tq, n, coeff, add):
    """
    Identify the even generator corresponding to b_p^{sp} b_q^{tq} (or scalar) and add to result.
    """
    if coeff == 0:
        return

    if p == q:
        if sp == tq:
            # (b_p^s)^2 = E_2del{p}_{s}
            sign_str = "p" if sp > 0 else "m"
            lbl = f"E_2del{p}_{sign_str}"
            add(lbl, coeff)
        else:
            # b_p^+ b_p^- or b_p^- b_p^+ -> number operator (contributes to Cartan)
            # b_p^+b_p^- = N_{b_p}, b_p^-b_p^+ = N_{b_p} + 1
            # Express N_{b_p} in terms of H generators
            if sp > 0:  # b_p^+ b_p^- = N_{b_p}
                _add_number_op(p, n, coeff, add)
            else:  # b_p^- b_p^+ = N_{b_p} + 1
                _add_number_op(p, n, coeff, add)
                add("_const_", coeff)  # constant 1 - should not appear in finite dim rep
    else:
        # p != q: order so i < j
        if p < q:
            i, j, s1, s2 = p, q, sp, tq
        else:
            i, j, s1, s2 = q, p, tq, sp
            # b_q^{tq} b_p^{sp} = b_p^{sp} b_q^{tq} (they commute for p != q)
        ss = ("p" if s1 > 0 else "m") + ("p" if s2 > 0 else "m")
        lbl = f"E_del{i}_del{j}_{ss}"
        add(lbl, coeff)


def _add_number_op(k, n, coeff, add):
    """Express N_{b_k} = b_k^+b_k^- in terms of H generators and add coeff*N_{b_k}."""
    # N_{b_k} from the Cartan structure:
    # H_1 = eps_N + N_{b_1}
    # H_m = N_{b_{m-1}} - N_{b_m} for 2<=m<=n
    # H_{n+1} = -N_{b_n} - 1/2
    #
    # Express N_{b_k}:
    # N_{b_n} = -H_{n+1} - 1/2
    # N_{b_{n-1}} = H_n + N_{b_n} = H_n - H_{n+1} - 1/2
    # N_{b_k} = H_{k+1} + H_{k+2} + ... + H_n - H_{n+1} - 1/2  for k < n
    # (since H_{k+1} = N_{b_k} - N_{b_{k+1}} => N_{b_k} = H_{k+1} + N_{b_{k+1}})
    # Verify: N_{b_1} = H_2 + H_3 + ... + H_n - H_{n+1} - 1/2
    # Note: H_1 = eps_N + N_{b_1}, so we can't easily extract eps_N from here.
    # For bracket computations, the constant -1/2 from N_{b_n} would lead to a scalar term,
    # which doesn't appear in the adjoint representation structure constants.
    # We'll ignore constants (they correspond to the central K = 1).

    for m in range(k + 1, n + 1):
        add(f"H_{m}", coeff)
    add(f"H_{n+1}", -coeff)
    # constant: -1/2 * coeff -- ignored (K=1 not in basis)


def build_schema1(n):
    """Build the complete Schema 1 dict for C(n+1) with bosonic rank n."""
    even_basis, odd_basis = build_basis(n)
    basis_all = odd_basis + even_basis
    parity = build_parity_dict(even_basis, odd_basis)

    # Boson labels
    boson_labels = [f"b_{k}_p" for k in range(1, n + 1)] + [f"b_{k}_m" for k in range(1, n + 1)]

    algebra_names = {1: "C(2)", 2: "C(3)", 3: "C(4)"}
    osp_names = {1: "osp(2|2)", 2: "osp(2|4)", 3: "osp(2|6)"}
    even_dim = 2 * n * n + n + 1
    odd_dim = 4 * n
    total_dim = even_dim + odd_dim

    schema = {
        "schema_version": "5.0",
        "algebra": {
            "family": "C",
            "m": 1,
            "n": n,
            "cartan_type": algebra_names.get(n, f"C({n+1})"),
            "alternative_notation": {
                "osp": osp_names.get(n, f"osp(2|{2*n})"),
                "dimension_formula": "osp(2m|2n) with m=1"
            },
            "dimension": {
                "total": total_dim,
                "even": even_dim,
                "odd": odd_dim
            }
        },
        "central_elements": {
            "kappa": {
                "label": "kappa",
                "parity": 1,
                "property": "kappa^2 = 0",
                "description": "Odd nilpotent central element for inhomogeneous deformation"
            },
            "K": {
                "label": "K",
                "parity": 0,
                "property": "identified with scalar 1",
                "description": "Even central identity element; excluded from PBW basis"
            }
        },
        "oscillator_generators": {
            "fermions": {
                "m": 1,
                "labels": ["a_1_p", "a_1_m"],
                "parity": 1,
                "description": "Standard fermionic pair a_1^+, a_1^-"
            },
            "bosons": {
                "count": 2 * n,
                "n": n,
                "labels": [f"b_{k}_p" for k in range(1, n + 1)] + [f"b_{k}_m" for k in range(1, n + 1)],
                "description": f"Bosonic oscillators b_i^pm with i=1,...,{n}"
            }
        },
        "oscillator_relations": {
            "standard_fermion_anticommutators": {
                "description": "CAR for a_1^+, a_1^-",
                "relations": {
                    "anticommutator": "{a_1^-, a_1^+} = 1",
                    "self": "{a_1^+,a_1^+}=0, {a_1^-,a_1^-}=0"
                }
            },
            "bosonic_commutators": {
                "description": "CCR for b_k^+/b_k^-",
                "relations": {
                    "conjugate_pair": "[b_i^-, b_j^+] = delta_{ij}",
                    "same_sign": "[b_i^pm, b_j^pm] = 0"
                }
            },
            "mixed_commutators": {
                "boson_fermion": "[b_i^pm, a_1^pm] = 0 (undeformed)"
            }
        },
        "basis": {
            "even": even_basis,
            "odd": odd_basis,
            "ordering_convention": "PBW: kappa < [odd: E_eps1_del{k}_{ss}] < [even: H_k, E_2del{k}_p/m, E_del{i}_del{j}_{ss}]"
        },
        "parity": parity,
        "generator_realization": {
            "description": "Oscillator realization of generators",
            "ordering": ["a_1_p", "a_1_m"] + boson_labels,
            "realizations": _build_realizations(n, even_basis, odd_basis)
        },
        "structure_constants": compute_structure_constants(n, even_basis, odd_basis),
        "metadata": {
            "generated_by": "C_generators.py",
            "generation_date": "2026-10-04",
            "references": [
                "Frappat et al. (2000), Dictionary on Lie Algebras and Superalgebras",
                "Bakalov and Sullivan (2017)"
            ]
        }
    }
    return schema


def _build_realizations(n, even_basis, odd_basis):
    """Build generator_realization dict."""
    real = {}
    for g in even_basis + odd_basis:
        Gr = parse_label(g, n)
        if Gr is None:
            continue
        Gt, Gdata = Gr
        if Gt == "H":
            idx = Gdata
            if idx == 1:
                form = [
                    {"words": ["a_1_p", "a_1_m"], "coeff": "1"},
                    {"words": [f"b_1_p", f"b_1_m"], "coeff": "1"}
                ]
                frappat = "a_1^+ a_1^- + b_1^+ b_1^-"
            elif 2 <= idx <= n:
                form = [
                    {"words": [f"b_{idx-1}_p", f"b_{idx-1}_m"], "coeff": "1"},
                    {"words": [f"b_{idx}_p", f"b_{idx}_m"], "coeff": "-1"}
                ]
                frappat = f"b_{idx-1}^+ b_{idx-1}^- - b_{idx}^+ b_{idx}^-"
            else:  # H_{n+1}
                form = [
                    {"words": [f"b_{n}_p", f"b_{n}_m"], "coeff": "-1"},
                    {"words": [], "coeff": "-1/2"}
                ]
                frappat = f"-b_{n}^+ b_{n}^- - 1/2"
            real[g] = {"standard_form": form, "frappat_form": frappat, "parity": 0}
        elif Gt == "eps_del":
            es, k, ds = Gdata
            a_lbl = "a_1_p" if es > 0 else "a_1_m"
            b_lbl = f"b_{k}_p" if ds > 0 else f"b_{k}_m"
            ss = ("p" if es > 0 else "m") + ("p" if ds > 0 else "m")
            real[g] = {
                "standard_form": [{"words": [a_lbl, b_lbl], "coeff": "1"}],
                "frappat_form": f"a_1^{'+'if es>0 else'-'} b_{k}^{'+'if ds>0 else'-'}",
                "parity": 1
            }
        elif Gt == "2del":
            k, sign = Gdata
            b_lbl = f"b_{k}_p" if sign > 0 else f"b_{k}_m"
            real[g] = {
                "standard_form": [{"words": [b_lbl, b_lbl], "coeff": "1"}],
                "frappat_form": f"(b_{k}^{'+'if sign>0 else'-'})^2",
                "parity": 0
            }
        elif Gt == "del_del":
            i, j, s1, s2 = Gdata
            b1 = f"b_{i}_p" if s1 > 0 else f"b_{i}_m"
            b2 = f"b_{j}_p" if s2 > 0 else f"b_{j}_m"
            real[g] = {
                "standard_form": [{"words": [b1, b2], "coeff": "1"}],
                "frappat_form": f"b_{i}^{'+'if s1>0 else'-'} b_{j}^{'+'if s2>0 else'-'}",
                "parity": 0
            }
    return real


def generate_all(output_dir="data"):
    """Generate Schema 1 JSON files for n=1, 2, 3."""
    os.makedirs(output_dir, exist_ok=True)
    for n in [1, 2, 3]:
        schema = build_schema1(n)
        # Remove any _const_ entries (scalars, should not appear in structure constants)
        schema["structure_constants"] = [
            sc for sc in schema["structure_constants"]
            if sc.get("Z") != "_const_"
        ]
        out_path = os.path.join(output_dir, f"C_{n}_structure.json")
        with open(out_path, "w") as f:
            json.dump(schema, f, indent=2)
        print(f"Written {out_path}: {len(schema['structure_constants'])} structure constants")


if __name__ == "__main__":
    generate_all()
