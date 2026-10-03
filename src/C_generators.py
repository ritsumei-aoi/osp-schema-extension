"""
C_generators.py

Builds the C(n+1) = osp(2|2n) basis, oscillator realization, and structure
constants, then writes Schema 1 JSON to data/C_{n}_structure.json.

Oscillators:
  a_1_p = a1+, a_1_m = a1-  (fermionic, CAR: {a1-, a1+} = 1)
  b_k_p = bk+, b_k_m = bk-  (bosonic,  CCR: [bk-, bl+] = δ_{kl})

All monomials are stored as tuples of oscillator labels in normal order:
  a_1_p < a_1_m < b_1_p < b_1_m < b_2_p < b_2_m < ...
"""

import json
from fractions import Fraction
from datetime import date
import os


# ---------------------------------------------------------------------------
# Basis
# ---------------------------------------------------------------------------

def get_basis(n):
    """Return (even_basis, odd_basis) for C(n+1) with bosonic rank n."""
    odd = []
    for sign in ["pp", "pm", "mp", "mm"]:
        for k in range(1, n + 1):
            odd.append(f"E_eps1_del{k}_{sign}")

    even = []
    for j in range(1, n + 2):
        even.append(f"H_{j}")
    for k in range(1, n + 1):
        even.append(f"E_2del{k}_p")
    for i in range(1, n + 1):
        for j in range(i + 1, n + 1):
            even.append(f"E_del{i}_del{j}_pp")
    for k in range(1, n + 1):
        even.append(f"E_2del{k}_m")
    for i in range(1, n + 1):
        for j in range(i + 1, n + 1):
            even.append(f"E_del{i}_del{j}_mm")
    for i in range(1, n + 1):
        for j in range(i + 1, n + 1):
            even.append(f"E_del{i}_del{j}_pm")
    for i in range(1, n + 1):
        for j in range(i + 1, n + 1):
            even.append(f"E_del{i}_del{j}_mp")

    return even, odd


def get_parity(n):
    even, odd = get_basis(n)
    p = {}
    for g in even:
        p[g] = 0
    for g in odd:
        p[g] = 1
    return p


# ---------------------------------------------------------------------------
# Oscillator ordering
# ---------------------------------------------------------------------------

def osc_order_list(n):
    """Canonical ordering: a_1_p, a_1_m, b_1_p, b_1_m, ..., b_n_p, b_n_m."""
    osc = ["a_1_p", "a_1_m"]
    for k in range(1, n + 1):
        osc += [f"b_{k}_p", f"b_{k}_m"]
    return osc


def osc_parity(osc):
    return 1 if osc.startswith("a_1") else 0


# ---------------------------------------------------------------------------
# Generator monomials (gen → list of (Fraction, tuple))
# ---------------------------------------------------------------------------

def gen_monomials(label, n):
    """
    Return list of (Fraction, tuple-of-osc-strings) for the given generator.
    The tuple () represents the scalar K=1.
    """
    if label == "H_1":
        return [(Fraction(1), ("a_1_p", "a_1_m")),
                (Fraction(1), ("b_1_p", "b_1_m"))]
    if label.startswith("H_"):
        j = int(label[2:])
        if 2 <= j <= n:
            return [(Fraction(1), (f"b_{j-1}_p", f"b_{j-1}_m")),
                    (Fraction(-1), (f"b_{j}_p", f"b_{j}_m"))]
        if j == n + 1:
            return [(Fraction(-1), (f"b_{n}_p", f"b_{n}_m")),
                    (Fraction(-1, 2), ())]

    if label.startswith("E_eps1_del"):
        # E_eps1_del{k}_{s1}{s2}
        rest = label[len("E_eps1_del"):]
        s1, s2 = rest[-2], rest[-1]
        k = int(rest[:-3])
        a = "a_1_p" if s1 == "p" else "a_1_m"
        b = f"b_{k}_p" if s2 == "p" else f"b_{k}_m"
        return [(Fraction(1), (a, b))]

    if label.startswith("E_2del"):
        rest = label[len("E_2del"):]
        k = int(rest[:-2])
        s = rest[-1]
        b = f"b_{k}_p" if s == "p" else f"b_{k}_m"
        return [(Fraction(1), (b, b))]

    if label.startswith("E_del"):
        rest = label[len("E_del"):]
        parts = rest.split("_del")
        i = int(parts[0])
        rest2 = parts[1]
        s1, s2 = rest2[-2], rest2[-1]
        j = int(rest2[:-3])
        b1 = f"b_{i}_p" if s1 == "p" else f"b_{i}_m"
        b2 = f"b_{j}_p" if s2 == "p" else f"b_{j}_m"
        return [(Fraction(1), (b1, b2))]

    return []


# ---------------------------------------------------------------------------
# Build inverse map: monomial -> {gen: coeff, "K_scalar": coeff}
# ---------------------------------------------------------------------------

def build_mono_to_gen(n, all_basis):
    """
    Build the inverse mapping: each oscillator monomial m → linear combination
    of basis generators + scalar K.

    Returns dict: monomial_tuple → dict {gen_label: Fraction, "__K__": Fraction}

    Strategy:
      - For monomials that appear in exactly one generator with a unique monomial:
        direct inversion.
      - For Cartan sector (number-operator monomials and scalar K):
        Use the exact algebraic inverses derived below.
    """
    # Cartan: number operators and scalar K
    # N_k = b_k+b_k- for k=1..n
    # N_a = a1+a1-
    # These satisfy:
    #   H_1 = N_a + N_1
    #   H_k = N_{k-1} - N_k  (k=2..n)
    #   H_{n+1} = -N_n - 1/2 K
    #
    # Inverse:
    #   N_k = sum_{j=k+1}^{n} H_j - H_{n+1} - 1/2 K   (k=1..n)
    #   N_a = H_1 - sum_{j=2}^{n} H_j + H_{n+1} + 1/2 K

    mono_map = {}

    def set_mono(mono, gen_dict):
        """gen_dict: {gen_label: Fraction} or with "__K__" for scalar."""
        mono_map[mono] = {k: v for k, v in gen_dict.items() if v != 0}

    # Cartan: N_k = b_k+b_k- for k=1..n
    for k in range(1, n + 1):
        mono = (f"b_{k}_p", f"b_{k}_m")
        d = {}
        # sum_{j=k+1}^{n} H_j
        for j in range(k + 1, n + 1):
            d[f"H_{j}"] = d.get(f"H_{j}", Fraction(0)) + Fraction(1)
        # -H_{n+1}
        d[f"H_{n+1}"] = d.get(f"H_{n+1}", Fraction(0)) - Fraction(1)
        # -1/2 K
        d["__K__"] = d.get("__K__", Fraction(0)) - Fraction(1, 2)
        set_mono(mono, d)

    # Cartan: N_a = a1+a1-
    mono = ("a_1_p", "a_1_m")
    d = {f"H_1": Fraction(1)}
    # -sum_{j=2}^{n} H_j
    for j in range(2, n + 1):
        d[f"H_{j}"] = d.get(f"H_{j}", Fraction(0)) - Fraction(1)
    # +H_{n+1}
    d[f"H_{n+1}"] = d.get(f"H_{n+1}", Fraction(0)) + Fraction(1)
    # +1/2 K
    d["__K__"] = d.get("__K__", Fraction(0)) + Fraction(1, 2)
    set_mono(mono, d)

    # Scalar K: K → pure scalar
    set_mono((), {"__K__": Fraction(1)})

    # Unique monomials: odd generators and even root generators
    for gen in all_basis:
        if gen.startswith("H_"):
            continue  # handled above
        monos = gen_monomials(gen, n)
        if len(monos) == 1:
            (c, mono) = monos[0]
            # gen = c * mono  →  mono = (1/c) * gen
            set_mono(mono, {gen: Fraction(1) / c})

    return mono_map


# ---------------------------------------------------------------------------
# Normal-ordering engine
# ---------------------------------------------------------------------------

def normal_order(word, n):
    """
    Normal-order a word (list/tuple of osc strings) using CCR/CAR.
    Returns list of (Fraction, tuple) where the tuple is normal-ordered.

    Normal order: a_1_p < a_1_m < b_1_p < b_1_m < ... < b_n_p < b_n_m

    Commutation rules (for pair at adjacent positions i, i+1):
      {a_1_p, a_1_m} = 1  (fermionic: swap gives -1 * (swap) + 1 * scalar)
      {a_1_p, a_1_p} = 0, {a_1_m, a_1_m} = 0
      [b_k^-, b_k^+] = 1  →  b_k^- b_k^+ = b_k^+ b_k^- + 1
      all boson-boson mixed = 0 for different indices or same sign
    """
    osc_idx = {o: i for i, o in enumerate(osc_order_list(n))}

    results = [(Fraction(1), list(word))]

    changed = True
    while changed:
        changed = False
        new_results = []
        for (c, w) in results:
            swapped = False
            for i in range(len(w) - 1):
                xi, xj = w[i], w[i + 1]
                if osc_idx[xi] > osc_idx[xj]:
                    # Need to swap xi and xj using (anti)commutation
                    pi = osc_parity(xi)
                    pj = osc_parity(xj)
                    # xi * xj = [xi, xj}_graded + (-1)^{pi*pj} xj * xi
                    # where [xi, xj}_graded = xi*xj - (-1)^{pi*pj} xj*xi

                    # Compute the bracket value [xi, xj}:
                    bracket_val = _osc_bracket(xi, xj)

                    # Swapped term: (-1)^{pi*pj} * c * (... xj xi ...)
                    new_w = w[:i] + [xj, xi] + w[i + 2:]
                    new_results.append((c * Fraction((-1) ** (pi * pj)), new_w))
                    # Scalar term: bracket_val * c * (word without xi and xj)
                    if bracket_val != 0:
                        scalar_w = w[:i] + w[i + 2:]
                        new_results.append((c * bracket_val, scalar_w))
                    changed = True
                    swapped = True
                    break
            if not swapped:
                new_results.append((c, w))
        if changed:
            results = new_results

    # Collect like terms
    combined = {}
    for (c, w) in results:
        key = tuple(w)
        combined[key] = combined.get(key, Fraction(0)) + c

    return [(v, k) for k, v in combined.items() if v != 0]


def _osc_bracket(xi, xj):
    """
    Compute [xi, xj} = xi*xj - (-1)^{pi*pj} xj*xi for single oscillators.
    Returns a Fraction (the c-number part).
    """
    pi = osc_parity(xi)
    pj = osc_parity(xj)

    # Fermionic pairs
    if xi == "a_1_m" and xj == "a_1_p":
        # a1- a1+ = a1+ a1- + 1  →  [a1-, a1+} = a1-a1+ - (-1)^1 a1+a1- = a1-a1+ + a1+a1- = 1
        return Fraction(1)
    if xi == "a_1_p" and xj == "a_1_m":
        # [a1+, a1-} = a1+a1- - (-1)^1 a1-a1+ = a1+a1- + a1-a1+ = 1
        return Fraction(1)

    # Bosonic: [bk-, bl+} for k==l
    if xi.startswith("b_") and xj.startswith("b_"):
        xi_p = xi.split("_")
        xj_p = xj.split("_")
        ki, si = int(xi_p[1]), xi_p[2]
        kj, sj = int(xj_p[1]), xj_p[2]
        if ki == kj:
            if si == "m" and sj == "p":
                # [bk-, bk+} = bk- bk+ - bk+ bk- = 1 (using normal order osc_idx[bk-]>osc_idx[bk+])
                # Wait: b_k_p < b_k_m in our ordering, so normally bk+ comes before bk-
                # If xi=bk_m, xj=bk_p and osc_idx[bk_m] > osc_idx[bk_p], we're swapping bk-*bk+
                # [bk-, bk+} = bk-bk+ - (-1)^0 bk+bk- = bk-bk+ - bk+bk- = 1 (from CCR)
                return Fraction(1)
            if si == "p" and sj == "m":
                # [bk+, bk-} = bk+bk- - bk-bk+ = -1
                return Fraction(-1)
    return Fraction(0)


# ---------------------------------------------------------------------------
# Graded commutator of two generator monomials
# ---------------------------------------------------------------------------

def graded_commutator_monos(m1, m2, n):
    """
    Compute [m1, m2} = m1*m2 - (-1)^{p(m1)*p(m2)} m2*m1
    in normal-ordered form.
    Returns list of (Fraction, tuple).
    """
    pm1 = sum(osc_parity(o) for o in m1) % 2
    pm2 = sum(osc_parity(o) for o in m2) % 2
    sign = Fraction((-1) ** (pm1 * pm2))

    prod1 = normal_order(list(m1) + list(m2), n)
    prod2 = normal_order(list(m2) + list(m1), n)

    combined = {}
    for (c, w) in prod1:
        combined[w] = combined.get(w, Fraction(0)) + c
    for (c, w) in prod2:
        combined[w] = combined.get(w, Fraction(0)) - sign * c

    return [(v, k) for k, v in combined.items() if v != 0]


# ---------------------------------------------------------------------------
# Structure constant computation
# ---------------------------------------------------------------------------

def compute_structure_constants(n, all_basis, mono_map):
    """
    Compute all non-zero structure constants for C(n+1).
    Returns list of dicts {X, Y, Z, coeff, sign_rule}.
    """
    sc = []

    for X in all_basis:
        X_monos = gen_monomials(X, n)
        for Y in all_basis:
            Y_monos = gen_monomials(Y, n)

            # Compute sum of graded commutators of all monomial pairs
            total = {}
            for (cx, mx) in X_monos:
                for (cy, my) in Y_monos:
                    bracket = graded_commutator_monos(mx, my, n)
                    for (bcoeff, bword) in bracket:
                        total[bword] = total.get(bword, Fraction(0)) + cx * cy * bcoeff

            if not total:
                continue

            # Express result in terms of generators + scalar
            gen_coeffs = {}
            scalar_K = Fraction(0)
            for (mono, coeff) in total.items():
                if mono in mono_map:
                    for gl, gc in mono_map[mono].items():
                        if gl == "__K__":
                            scalar_K += coeff * gc
                        else:
                            gen_coeffs[gl] = gen_coeffs.get(gl, Fraction(0)) + coeff * gc
                # If mono not in map, it's an unknown monomial (shouldn't happen)

            # Add non-zero generator contributions
            for Z, c in gen_coeffs.items():
                if c != 0:
                    sc.append({
                        "X": X,
                        "Y": Y,
                        "Z": Z,
                        "coeff": str(c),
                        "sign_rule": "graded",
                    })

    return sc


# ---------------------------------------------------------------------------
# Generator realization
# ---------------------------------------------------------------------------

def get_generator_realization(n):
    real = {}

    real["H_1"] = {
        "standard_form": [
            {"words": ["a_1_p", "a_1_m"], "coeff": "1"},
            {"words": ["b_1_p", "b_1_m"], "coeff": "1"},
        ],
        "frappat_form": "a_1^+ a_1^- + b_1^+ b_1^-",
        "parity": 0,
    }
    for k in range(2, n + 1):
        real[f"H_{k}"] = {
            "standard_form": [
                {"words": [f"b_{k-1}_p", f"b_{k-1}_m"], "coeff": "1"},
                {"words": [f"b_{k}_p", f"b_{k}_m"], "coeff": "-1"},
            ],
            "frappat_form": f"b_{k-1}^+ b_{k-1}^- - b_{k}^+ b_{k}^-",
            "parity": 0,
        }
    real[f"H_{n+1}"] = {
        "standard_form": [
            {"words": [f"b_{n}_p", f"b_{n}_m"], "coeff": "-1"},
            {"words": [], "coeff": "-1/2"},
        ],
        "frappat_form": f"-b_{n}^+ b_{n}^- - 1/2",
        "parity": 0,
        "note": "Terminal Cartan; -1/2 from the sp(2n) Dynkin normalization",
    }

    for k in range(1, n + 1):
        for sign1 in ["p", "m"]:
            for sign2 in ["p", "m"]:
                label = f"E_eps1_del{k}_{sign1}{sign2}"
                a_osc = "a_1_p" if sign1 == "p" else "a_1_m"
                b_osc = f"b_{k}_p" if sign2 == "p" else f"b_{k}_m"
                fs1 = "+" if sign1 == "p" else "-"
                fs2 = "+" if sign2 == "p" else "-"
                real[label] = {
                    "standard_form": [{"words": [a_osc, b_osc], "coeff": "1"}],
                    "frappat_form": f"a_1^{fs1} b_{k}^{fs2}",
                    "parity": 1,
                }

    for k in range(1, n + 1):
        real[f"E_2del{k}_p"] = {
            "standard_form": [{"words": [f"b_{k}_p", f"b_{k}_p"], "coeff": "1"}],
            "frappat_form": f"(b_{k}^+)^2",
            "parity": 0,
        }
        real[f"E_2del{k}_m"] = {
            "standard_form": [{"words": [f"b_{k}_m", f"b_{k}_m"], "coeff": "1"}],
            "frappat_form": f"(b_{k}^-)^2",
            "parity": 0,
        }
    for i in range(1, n + 1):
        for j in range(i + 1, n + 1):
            for s1, s2 in [("pp", ("p", "p")), ("mm", ("m", "m")),
                           ("pm", ("p", "m")), ("mp", ("m", "p"))]:
                real[f"E_del{i}_del{j}_{s1}"] = {
                    "standard_form": [{"words": [f"b_{i}_{s2[0]}", f"b_{j}_{s2[1]}"], "coeff": "1"}],
                    "frappat_form": f"b_{i}^{'+' if s2[0]=='p' else '-'} b_{j}^{'+' if s2[1]=='p' else '-'}",
                    "parity": 0,
                }

    return real


# ---------------------------------------------------------------------------
# Build complete Schema 1
# ---------------------------------------------------------------------------

def build_schema(n):
    even_basis, odd_basis = get_basis(n)
    all_basis = even_basis + odd_basis
    par = get_parity(n)
    real = get_generator_realization(n)
    mono_map = build_mono_to_gen(n, all_basis)
    sc = compute_structure_constants(n, all_basis, mono_map)

    n_even = len(even_basis)
    n_odd = len(odd_basis)
    total = n_even + n_odd

    boson_labels = sum([[f"b_{k}_p", f"b_{k}_m"] for k in range(1, n + 1)], [])
    cartan_type = f"C({n+1})"
    osp_label = f"osp(2|{2*n})"

    return {
        "schema_version": "5.0",
        "algebra": {
            "family": "C",
            "m": 1,
            "n": n,
            "cartan_type": cartan_type,
            "alternative_notation": {
                "osp": osp_label,
                "dimension_formula": "osp(2m|2n) with m=1",
            },
            "dimension": {
                "total": total,
                "even": n_even,
                "odd": n_odd,
                "even_formula": "2*n^2 + n + 1",
                "odd_formula": "4*n",
            },
        },
        "central_elements": {
            "kappa": {
                "label": "kappa",
                "parity": 1,
                "nilpotency": "kappa^2 = 0",
                "description": "Odd nilpotent central element",
            },
            "K": {
                "label": "K",
                "parity": 0,
                "description": "Even central identity; K=1 in all applications",
                "note": "Not an independent basis element",
            },
        },
        "oscillator_generators": {
            "fermions": {
                "m": 1,
                "labels": ["a_1_p", "a_1_m"],
                "parity": 1,
                "description": "Standard fermionic pair a_1^+, a_1^- with CAR",
            },
            "bosons": {
                "count": 2 * n,
                "n": n,
                "labels": boson_labels,
                "description": f"Bosonic oscillators b_k^+/- for k=1..{n}",
            },
        },
        "oscillator_relations": {
            "standard_fermion_anticommutators": {
                "relations": {
                    "anticommutator": "{a_1^-, a_1^+} = 1",
                    "self_anticommutator_p": "{a_1^+, a_1^+} = 0",
                    "self_anticommutator_m": "{a_1^-, a_1^-} = 0",
                },
            },
            "bosonic_commutators": {
                "relations": {
                    "conjugate_pair": "[b_i^-, b_j^+] = delta_{ij}",
                    "other": "0",
                },
            },
            "mixed_commutators": {"fermion_boson": "[b_k^s, a_1^sigma] = 0"},
        },
        "basis": {
            "even": even_basis,
            "odd": odd_basis,
            "ordering_convention": (
                "PBW: kappa < [odd: pp<pm<mp<mm, k asc] < "
                "[even: Cartan H_1..H_{n+1}, +even, -even, mixed]"
            ),
        },
        "parity": par,
        "generator_realization": {
            "description": "Standard form; ordering a_1_p < a_1_m < b_1_p < b_1_m < ...",
            "realizations": real,
        },
        "structure_constants": sc,
        "metadata": {
            "generated_by": "C_generators.py",
            "generation_date": str(date.today()),
            "algebra": cartan_type,
            "n": n,
            "references": [
                "Frappat, Sciarrino, Sorba (2000)",
                "arXiv:hep-th/9607161",
            ],
        },
    }


def main():
    os.makedirs("data", exist_ok=True)
    for n in [1, 2, 3]:
        print(f"Building C_{n}_structure.json (C({n+1}) = osp(2|{2*n}))...")
        schema = build_schema(n)
        outfile = f"data/C_{n}_structure.json"
        with open(outfile, "w") as f:
            json.dump(schema, f, indent=2)
        sc = schema["structure_constants"]
        print(f"  Basis: {len(schema['basis']['even'])} even, "
              f"{len(schema['basis']['odd'])} odd")
        print(f"  Structure constants: {len(sc)} non-zero entries")
        print(f"  Written to {outfile}")


if __name__ == "__main__":
    main()
