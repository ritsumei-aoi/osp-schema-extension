"""
C_generators.py: Build Schema 1 JSON for C(n+1) = osp(2|2n).

Complete general bracket computation using oscillator representation.
Each even generator = degree-2 boson polynomial.
Each odd generator = a_1^sigma * b_k^s.

Bosonic CCR: [b_i^-, b_j^+] = delta_{ij}, others 0.
CAR: {a_1^-, a_1^+} = 1.
"""

import json
import itertools
from fractions import Fraction
from datetime import date


# ---------------------------------------------------------------------------
# Basis construction
# ---------------------------------------------------------------------------

def build_basis(n):
    """Return (even_basis, odd_basis) lists for C(n+1) with bosonic rank n."""
    even = []
    # Cartan H_1, ..., H_{n+1}
    for k in range(1, n + 2):
        even.append(f"H_{k}")
    # Raising: E_2del{k}_p and E_del{i}_del{j}_pp
    for k in range(1, n + 1):
        even.append(f"E_2del{k}_p")
    for i, j in itertools.combinations(range(1, n + 1), 2):
        even.append(f"E_del{i}_del{j}_pp")
    # Lowering
    for k in range(1, n + 1):
        even.append(f"E_2del{k}_m")
    for i, j in itertools.combinations(range(1, n + 1), 2):
        even.append(f"E_del{i}_del{j}_mm")
    # Mixed
    for i, j in itertools.combinations(range(1, n + 1), 2):
        even.append(f"E_del{i}_del{j}_pm")
    for i, j in itertools.combinations(range(1, n + 1), 2):
        even.append(f"E_del{i}_del{j}_mp")

    odd = []
    for k in range(1, n + 1):
        for sign in ["pp", "pm", "mp", "mm"]:
            odd.append(f"E_eps1_del{k}_{sign}")
    return even, odd


def parity_of(label):
    return 1 if label.startswith("E_eps1") else 0


def build_parity_dict(even, odd):
    d = {}
    for g in even:
        d[g] = 0
    for g in odd:
        d[g] = 1
    return d


# ---------------------------------------------------------------------------
# Generator representation as oscillator monomials
# ---------------------------------------------------------------------------

def gen_as_monomials(label, n):
    """
    Return the oscillator representation of a generator as a list of
    (coeff, monomial) where monomial is a tuple of (osc_type, index, sign).
    osc_type: 'a' or 'b'
    For degree-2 bosonic monomials: (coeff, (b, i, si), (b, j, sj))
    For odd: (coeff, (a, 1, sigma), (b, k, s))
    For Cartan H_k: sum of (coeff, (b, i, 'p'), (b, i, 'm')) terms + const
    """
    pass  # Used internally below


def boson_eta(i, si, j, sj):
    """[b_i^si, b_j^sj] = delta_{ij} * (delta_{si=m}*delta_{sj=p} - delta_{si=p}*delta_{sj=m})"""
    if i != j:
        return Fraction(0)
    if si == 'm' and sj == 'p':
        return Fraction(1)
    if si == 'p' and sj == 'm':
        return Fraction(-1)
    return Fraction(0)


def fermion_eta(si, sj):
    """{a^si, a^sj}: {a^-, a^+} = 1, others 0"""
    if si == 'm' and sj == 'p':
        return Fraction(1)
    if si == 'p' and sj == 'm':
        return Fraction(1)
    return Fraction(0)


def normalize_boson_pair(i, si, j, sj):
    """
    Normalize b_i^si * b_j^sj to a generator label and coefficient.
    Convention: smaller index first; for same index, sign p before m.
    Returns (label, coeff) where coeff accounts for ordering.
    """
    # same index same sign: b_ip^2 or b_im^2
    if i == j and si == sj:
        if si == 'p':
            return f"E_2del{i}_p", Fraction(2)  # b_ip^2 = 2 * (1/2 b_ip^2) = 2*E_2del{i}_p
        else:
            return f"E_2del{i}_m", Fraction(2)
    # same index different sign: number operator N_bi
    if i == j and si != sj:
        return ('N', i), Fraction(1)  # b_ip*b_im = N_bi, b_im*b_ip = N_bi+1
    # different indices: ensure i < j
    if i < j:
        return f"E_del{i}_del{j}_{si}{sj}", Fraction(1)
    else:
        return f"E_del{j}_del{i}_{sj}{si}", Fraction(1)


def N_bk_in_H(k, n):
    """
    Return N_bk expressed as dict {H_l: coeff, 'const': c}.
    Derived from H_l = N_b{l-1} - N_bl (l=2..n) and H_{n+1} = -N_bn - 1/2:
    N_bk = H_{k+1} + H_{k+2} + ... + H_n - H_{n+1} - 1/2
    """
    result = {}
    for l in range(k + 1, n + 1):      # H_{k+1},...,H_n: coeff +1
        result[f"H_{l}"] = Fraction(1)
    result[f"H_{n+1}"] = Fraction(-1)   # H_{n+1}: coeff -1
    result['const'] = Fraction(-1, 2)
    return result


def N_a_in_H(n):
    """
    N_a = H_1 - H_2 - ... - H_n + H_{n+1} + 1/2
    Derived from H_1 = N_a + N_b1 and the N_bk formula.
    """
    result = {}
    result["H_1"] = Fraction(1)
    for l in range(2, n + 1):           # H_2,...,H_n: coeff -1
        result[f"H_{l}"] = Fraction(-1)
    result[f"H_{n+1}"] = Fraction(1)    # H_{n+1}: coeff +1
    result['const'] = Fraction(1, 2)
    return result


def add_cartan(result, N_expr, coeff):
    """Add coeff * N_expr to result dict (omitting const terms)."""
    for key, val in N_expr.items():
        if key == 'const':
            continue  # K=1 is not a basis element
        result[key] = result.get(key, Fraction(0)) + coeff * val


def compute_boson_boson_bracket(i, si, j, sj, k, uk, l, ul, n):
    """
    Compute [b_i^si * b_j^sj, b_k^uk * b_l^ul] as {generator: coeff}.
    Uses: [AB, CD] = AC[B,D] + A[B,C]D + [A,D]CB + [A,C]DB (Leibniz for bosons)
    Wait, correct formula: [AB, CD] = A[B,CD] + [A,CD]B
    = A(C[B,D] + [B,C]D) + (C[A,D] + [A,C]D)B
    = AC[B,D] + A[B,C]D + C[A,D]B + [A,C]DB
    """
    result = {}
    # 4 terms from Leibniz
    terms = [
        (boson_eta(j, sj, l, ul), i, si, k, uk),  # AC[B,D]: b_i^si * b_k^uk
        (boson_eta(j, sj, k, uk), i, si, l, ul),  # A[B,C]D: b_i^si * b_l^ul
        (boson_eta(i, si, l, ul), j, sj, k, uk),  # C[A,D]B: b_k^uk * b_j^sj (but bosons commute)
        (boson_eta(i, si, k, uk), j, sj, l, ul),  # [A,C]DB: b_l^ul * b_j^sj (bosons commute)
    ]
    # For bosons, b_k^uk * b_j^sj = b_j^sj * b_k^uk (free commutativity)
    for eta_val, a, sa, b, sb in terms:
        if eta_val == 0:
            continue
        label, ord_coeff = normalize_boson_pair(a, sa, b, sb)
        if isinstance(label, tuple) and label[0] == 'N':
            # Number operator N_bq
            q = label[1]
            N_expr = N_bk_in_H(q, n)
            add_cartan(result, N_expr, eta_val * ord_coeff)
        else:
            result[label] = result.get(label, Fraction(0)) + eta_val * ord_coeff
    return {k_: v for k_, v in result.items() if v != 0}


def gen_to_boson_terms(label, n):
    """
    Return list of (coeff, (i, si, j, sj)) for even bosonic generators,
    or None for Cartan generators.
    """
    if label.startswith("H_"):
        return None  # Cartan - handled via eigenvalue
    if label.startswith("E_2del"):
        parts = label.split("_")
        k = int(parts[1][4:])  # '2del{k}'[4:] = '{k}'
        s = parts[2]  # 'p' or 'm'
        return [(Fraction(1, 2), (k, s, k, s))]
    if label.startswith("E_del"):
        parts = label.split("_")
        i = int(parts[1][3:])  # 'del{i}'[3:] = '{i}'
        j = int(parts[2][3:])
        signs = parts[3]
        si, sj = signs[0], signs[1]
        return [(Fraction(1), (i, si, j, sj))]
    return []


def compute_cartan_eigenvalue(H_label, root_label, n):
    """
    Compute eigenvalue of H acting on root_label (non-Cartan generator).
    H_l acts on b_i^s: eigenvalue from b side.
    H_1 = N_a + N_b1: eigen(b_i^p)=delta_{i1}, eigen(b_i^m)=-delta_{i1}, eigen(a^p)=1, eigen(a^m)=-1
    H_l (2<=l<=n) = N_b{l-1} - N_bl: eigen(b_i^p)=delta_{i,l-1}-delta_{i,l}, eigen(b_i^m)=-(delta_{i,l-1}-delta_{i,l})
    H_{n+1} = -N_bn - 1/2: eigen(b_i^p)=-delta_{i,n}, eigen(b_i^m)=delta_{i,n}
    """
    l = int(H_label[2:])

    def b_eig(idx, sign):
        """Eigenvalue of H_l on b_idx^sign."""
        if sign == 'p':
            if l == 1:
                return Fraction(1 if idx == 1 else 0)
            elif l <= n:
                return Fraction((1 if idx == l - 1 else 0) - (1 if idx == l else 0))
            else:  # l = n+1
                return Fraction(-(1 if idx == n else 0))
        else:  # sign == 'm'
            return -b_eig(idx, 'p')

    def a_eig(sign):
        """Eigenvalue of H_l on a^sign."""
        if l == 1:
            return Fraction(1 if sign == 'p' else -1)
        else:
            return Fraction(0)

    if root_label.startswith("E_eps1"):
        parts = root_label.split("_")
        k = int(parts[2][3:])
        signs = parts[3]
        a_sgn, b_sgn = signs[0], signs[1]
        return a_eig(a_sgn) + b_eig(k, b_sgn)

    if root_label.startswith("E_2del"):
        parts = root_label.split("_")
        k = int(parts[1][4:])  # '2del{k}'[4:] = '{k}'
        s = parts[2]
        return 2 * b_eig(k, s)

    if root_label.startswith("E_del"):
        parts = root_label.split("_")
        i = int(parts[1][3:])
        j = int(parts[2][3:])
        signs = parts[3]
        si, sj = signs[0], signs[1]
        return b_eig(i, si) + b_eig(j, sj)

    return Fraction(0)


def compute_structure_constants(n, even, odd):
    sc = []

    def add(X, Y, Z, coeff):
        if coeff == 0:
            return
        sc.append({"X": X, "Y": Y, "Z": Z, "coeff": str(coeff), "sign_rule": "graded"})

    all_gens = odd + even

    # H × non-Cartan: [H_l, root] = eigenvalue * root
    cartan_gens = [g for g in even if g.startswith("H_")]
    root_gens = [g for g in all_gens if not g.startswith("H_")]

    for H in cartan_gens:
        for root in root_gens:
            ev = compute_cartan_eigenvalue(H, root, n)
            if ev != 0:
                add(H, root, root, ev)

    # [H, H] = 0 (Cartan commutes)

    # Even-Even (non-Cartan): compute via boson commutator formula.
    # Only iterate over (X,Y) pairs once (X<=Y in index) to avoid double-storing.
    non_cartan_even = [g for g in even if not g.startswith("H_")]
    for xi, X in enumerate(non_cartan_even):
        X_terms = gen_to_boson_terms(X, n)
        for yi, Y in enumerate(non_cartan_even):
            if yi < xi:
                continue  # skip; [Y,X] is inferred by checker via anti-symmetry
            Y_terms = gen_to_boson_terms(Y, n)
            result = {}
            for (cx, (ix, sx, jx, sx2)) in X_terms:
                for (cy, (iy, sy, jy, sy2)) in Y_terms:
                    br = compute_boson_boson_bracket(ix, sx, jx, sx2, iy, sy, jy, sy2, n)
                    for k, v in br.items():
                        result[k] = result.get(k, Fraction(0)) + cx * cy * v
            result = {k: v for k, v in result.items() if v != 0}
            for Z, coeff in result.items():
                add(X, Y, Z, coeff)

    # Odd-Odd: {E_eps1_del{k}_{a_sgn}{b_sgn}, E_eps1_del{l}_{a_sgn2}{b_sgn2}}
    # = {a^{a_sgn}*b_k^{b_sgn}, a^{a_sgn2}*b_l^{b_sgn2}}
    # Since [b, a] = 0:
    # {X, Y} = X*Y + Y*X = a^{a1}*b_k^{s1}*a^{a2}*b_l^{s2} + a^{a2}*b_l^{s2}*a^{a1}*b_k^{s1}
    #        = a^{a1}*a^{a2}*b_k^{s1}*b_l^{s2} + a^{a2}*a^{a1}*b_l^{s2}*b_k^{s1}
    #        = (a^{a1}*a^{a2} + a^{a2}*a^{a1})*b_k^{s1}*b_l^{s2}  [if s1*s2 terms commute]
    # But bosons: b_k^{s1}*b_l^{s2} = b_l^{s2}*b_k^{s1} + [b_k^{s1},b_l^{s2}]
    # So:
    # {X,Y} = {a^{a1},a^{a2}}*b_k^{s1}*b_l^{s2} + a^{a2}*a^{a1}*[b_l^{s2},b_k^{s1}]
    # = {a^{a1},a^{a2}}*b_k^{s1}*b_l^{s2} - a^{a2}*a^{a1}*[b_k^{s1},b_l^{s2}]

    for xi, X in enumerate(odd):
        px_parts = X.split("_")
        kx = int(px_parts[2][3:])
        sgns_x = px_parts[3]
        a1, s1 = sgns_x[0], sgns_x[1]

        for yi, Y in enumerate(odd):
            if yi < xi:
                continue  # skip; {Y,X}={X,Y} for odd generators, checker handles via symmetry
            py_parts = Y.split("_")
            ky = int(py_parts[2][3:])
            sgns_y = py_parts[3]
            a2, s2 = sgns_y[0], sgns_y[1]

            # {a^{a1},a^{a2}}: CAR
            anti_aa = fermion_eta(a1, a2)  # {a^{a1}, a^{a2}}

            # [b_k^{s1}, b_l^{s2}]
            bra = boson_eta(kx, s1, ky, s2)

            result = {}

            # Term 1: {a^{a1},a^{a2}} * b_k^{s1}*b_l^{s2}
            if anti_aa != 0:
                lbl, c = normalize_boson_pair(kx, s1, ky, s2)
                if isinstance(lbl, tuple) and lbl[0] == 'N':
                    q = lbl[1]
                    add_cartan(result, N_bk_in_H(q, n), anti_aa * c)
                else:
                    result[lbl] = result.get(lbl, Fraction(0)) + anti_aa * c

            # Term 2: -a^{a2}*a^{a1} * [b_k^{s1},b_l^{s2}]
            # a^{a2}*a^{a1} depends on a1,a2:
            # if a1==a2: a^{a}*a^{a} = 0 (CAR)
            # if a1!=a2: a^{p}*a^{m} = N_a, a^{m}*a^{p} = 1-N_a
            if bra != 0 and a1 != a2:
                if a2 == 'p' and a1 == 'm':
                    # a^p * a^m = N_a
                    N_expr = N_a_in_H(n)
                    add_cartan(result, N_expr, -bra)
                elif a2 == 'm' and a1 == 'p':
                    # a^m * a^p = 1 - N_a
                    N_expr = N_a_in_H(n)
                    add_cartan(result, {k: -v for k, v in N_expr.items() if k != 'const'}, -bra)
                    # constant term: bra * 1 (from the "1" in 1-N_a), but K=1 not in basis

            result = {k: v for k, v in result.items() if v != 0}
            for Z, coeff in result.items():
                add(X, Y, Z, coeff)

    # Even-Odd: [even, odd] = even_op * odd - odd * even_op (since even commutes differently)
    # For X = b_i^si * b_j^sj (even) and Y = a^{a_sgn} * b_k^s (odd):
    # [X, Y] = X*Y - Y*X (since p(X)=0, graded bracket = regular commutator)
    # = b_i^si*b_j^sj*a^{a_sgn}*b_k^s - a^{a_sgn}*b_k^s*b_i^si*b_j^sj
    # Since [b, a] = 0: b*a = a*b
    # = a^{a_sgn}*(b_i^si*b_j^sj*b_k^s - b_k^s*b_i^si*b_j^sj)
    # = a^{a_sgn} * [b_i^si*b_j^sj, b_k^s]
    # [b_i^si*b_j^sj, b_k^s] = b_i^si*[b_j^sj,b_k^s] + [b_i^si,b_k^s]*b_j^sj
    # = eta(j,sj,k,s)*b_i^si + eta(i,si,k,s)*b_j^sj

    for X in non_cartan_even:
        X_terms = gen_to_boson_terms(X, n)
        for Y in odd:
            py = Y.split("_")
            ky = int(py[2][3:])
            sgns_y = py[3]
            a_sgn, s = sgns_y[0], sgns_y[1]

            result = {}
            for (cx, (ix, sx, jx, sx2)) in X_terms:
                # [b_ix^sx * b_jx^sx2, b_ky^s]
                # = eta(jx,sx2,ky,s)*b_ix^sx + eta(ix,sx,ky,s)*b_jx^sx2
                for (eta_val, a_idx, a_sgn_b) in [
                    (boson_eta(jx, sx2, ky, s), ix, sx),
                    (boson_eta(ix, sx, ky, s), jx, sx2)
                ]:
                    if eta_val == 0:
                        continue
                    # Result: a^{a_sgn} * b_{a_idx}^{a_sgn_b}
                    new_sign = a_sgn + a_sgn_b
                    new_label = f"E_eps1_del{a_idx}_{new_sign}"
                    result[new_label] = result.get(new_label, Fraction(0)) + cx * eta_val

            result = {k: v for k, v in result.items() if v != 0}
            for Z, coeff in result.items():
                add(X, Y, Z, coeff)

    return sc


def build_schema1(n):
    even, odd = build_basis(n)
    parity = build_parity_dict(even, odd)
    sc = compute_structure_constants(n, even, odd)
    total_dim = 2 * n * n + 5 * n + 1
    even_dim = 2 * n * n + n + 1
    odd_dim = 4 * n

    fermion_labels = ["a_1_p", "a_1_m"]
    boson_labels = []
    for k in range(1, n + 1):
        boson_labels += [f"b_{k}_p", f"b_{k}_m"]

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
