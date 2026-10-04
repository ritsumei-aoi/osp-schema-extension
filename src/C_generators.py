"""
C_generators.py
Generates Schema 1 JSON for C(n+1) = osp(2|2n).

Structure constants computed via Wick-contraction formula for oscillator bilinears:
  [o1*o2, o3*o4}_g = c23*(o1*o4) + (-1)^{p2*p3}*c24*(o1*o3)
                   + (-1)^{p1*(p3+p4)}*c13*(o4*o2)
                   + (-1)^{p1*(p3+p4)+p1*p3}*c14*(o3*o2)

where c_{ij} = [o_i, o_j}_super (scalar contraction from CAR/CCR).

Oscillator algebra (C(n+1)):
  {a_1^-, a_1^+} = 1  (CAR)
  [b_k^-, b_l^+] = delta_{kl}  (CCR)
  All boson-fermion pairs commute.
"""

import json
from fractions import Fraction
from datetime import date
import os


# ---------------------------------------------------------------------------
# Oscillator helpers
# ---------------------------------------------------------------------------

def osc_parity(o):
    if o in ("a_1_p", "a_1_m"):
        return 1
    return 0  # bosons


def is_boson(o):
    return o.startswith("b_")


def is_fermion(o):
    return o.startswith("a_")


def parse_boson(o):
    """b_{k}_{s} -> (k, s) where s in {'p','m'}."""
    parts = o.split("_")
    return int(parts[1]), parts[2]


def scalar_contraction(oi, oj):
    """
    Compute [oi, oj}_super as a scalar.
    For bosons (even): [oi,oj}_g = [oi,oj] (commutator).
    For fermions (odd): [oi,oj}_g = {oi,oj} (anticommutator).
    Mixed: 0.
    """
    if is_fermion(oi) and is_fermion(oj):
        # {a^-, a^+} = 1 = {a^+, a^-} (anticommutator is symmetric)
        if {oi, oj} == {"a_1_p", "a_1_m"}:
            return Fraction(1)
        return Fraction(0)
    if is_boson(oi) and is_boson(oj):
        ki, si = parse_boson(oi)
        kj, sj = parse_boson(oj)
        if ki == kj:
            if si == "m" and sj == "p":
                return Fraction(1)   # [b^-, b^+] = 1
            if si == "p" and sj == "m":
                return Fraction(-1)  # [b^+, b^-] = -1
        return Fraction(0)
    return Fraction(0)  # mixed boson-fermion


# ---------------------------------------------------------------------------
# Number-operator decomposition into Cartans
# ---------------------------------------------------------------------------

def number_op_to_cartans(k, n, is_ferm):
    """
    Return {H_label: coeff} and scalar_k for the number operator n_k or n_a.

    n_k = sum_{l=k+1}^{n} H_l - H_{n+1} - 1/2   (bosonic, k=1..n)
    n_a = H_1 - H_2 - ... - H_n + H_{n+1} + 1/2  (fermionic)
    """
    gens = {}
    scalar = Fraction(0)
    if not is_ferm:
        # n_k = sum_{l=k+1}^{n} H_l - H_{n+1} - 1/2
        for l in range(k + 1, n + 1):
            gens[f"H_{l}"] = gens.get(f"H_{l}", Fraction(0)) + Fraction(1)
        gens[f"H_{n+1}"] = gens.get(f"H_{n+1}", Fraction(0)) - Fraction(1)
        scalar = Fraction(-1, 2)
    else:
        # n_a = H_1 - H_2 - ... - H_n + H_{n+1} + 1/2
        gens["H_1"] = gens.get("H_1", Fraction(0)) + Fraction(1)
        for l in range(2, n + 1):
            gens[f"H_{l}"] = gens.get(f"H_{l}", Fraction(0)) - Fraction(1)
        gens[f"H_{n+1}"] = gens.get(f"H_{n+1}", Fraction(0)) + Fraction(1)
        scalar = Fraction(1, 2)
    # Remove zeros
    return {k: v for k, v in gens.items() if v != 0}, scalar


# ---------------------------------------------------------------------------
# Map oscillator product o_a * o_b to Lie algebra generators
# ---------------------------------------------------------------------------

def osc_product_to_gens(o_a, o_b, n):
    """
    Express the product o_a * o_b as a dict {label: coeff} of Lie algebra generators
    plus a scalar multiple of K.
    Returns (gen_dict, k_scalar).
    """
    gens = {}
    k_scalar = Fraction(0)

    if is_boson(o_a) and is_boson(o_b):
        ka, sa = parse_boson(o_a)
        kb, sb = parse_boson(o_b)
        if ka == kb:
            if sa == "p" and sb == "p":
                gens[f"E_2del{ka}_p"] = Fraction(1)
            elif sa == "m" and sb == "m":
                gens[f"E_2del{ka}_m"] = Fraction(1)
            elif sa == "p" and sb == "m":
                # b_k^+ b_k^- = n_k (normal ordered)
                cart, sc = number_op_to_cartans(ka, n, False)
                for g, c in cart.items():
                    gens[g] = gens.get(g, Fraction(0)) + c
                k_scalar += sc
            elif sa == "m" and sb == "p":
                # b_k^- b_k^+ = 1 + b_k^+ b_k^- = K + n_k
                cart, sc = number_op_to_cartans(ka, n, False)
                for g, c in cart.items():
                    gens[g] = gens.get(g, Fraction(0)) + c
                k_scalar += sc + Fraction(1)
        else:
            # b_i^s * b_j^t with i != j: commute freely, form root generator
            i, j, si, sj = ka, kb, sa, sb
            if i > j:
                i, j, si, sj = kb, ka, sb, sa  # canonical i < j
            ss = si + sj
            gens[f"E_del{i}_del{j}_{ss}"] = Fraction(1)

    elif is_fermion(o_a) and is_boson(o_b):
        sf = "p" if o_a == "a_1_p" else "m"
        kb, sb = parse_boson(o_b)
        gens[f"E_eps1_del{kb}_{sf}{sb}"] = Fraction(1)

    elif is_boson(o_a) and is_fermion(o_b):
        ka, sa = parse_boson(o_a)
        sf = "p" if o_b == "a_1_p" else "m"
        # bosons and fermions commute: b^s a^t = a^t b^s
        gens[f"E_eps1_del{ka}_{sf}{sa}"] = Fraction(1)

    elif is_fermion(o_a) and is_fermion(o_b):
        if o_a == o_b:
            pass  # a^+a^+ = 0 or a^-a^- = 0
        elif o_a == "a_1_p" and o_b == "a_1_m":
            # a_1^+ a_1^- = n_a
            cart, sc = number_op_to_cartans(None, n, True)
            for g, c in cart.items():
                gens[g] = gens.get(g, Fraction(0)) + c
            k_scalar += sc
        elif o_a == "a_1_m" and o_b == "a_1_p":
            # a_1^- a_1^+ = K - n_a
            cart, sc = number_op_to_cartans(None, n, True)
            for g, c in cart.items():
                gens[g] = gens.get(g, Fraction(0)) - c
            k_scalar += Fraction(1) - sc

    return {k: v for k, v in gens.items() if v != 0}, k_scalar


# ---------------------------------------------------------------------------
# Generator representation as oscillator bilinear
# ---------------------------------------------------------------------------

def gen_to_osc_pair(label, n):
    """
    Return ((o1, o2), coeff) where label = coeff * o1 * o2.
    o1, o2 are oscillator strings.
    """
    if label.startswith("H_"):
        return None  # Cartan generators are not simple bilinears in this sense
    if label.startswith("E_eps1_del"):
        rest = label[len("E_eps1_del"):]
        under = rest.rfind("_")
        k = int(rest[:under])
        ss = rest[under + 1:]
        o1 = "a_1_" + ss[0]
        o2 = f"b_{k}_{ss[1]}"
        return (o1, o2), Fraction(1)
    if label.startswith("E_2del"):
        if label.endswith("_p"):
            k = int(label[6:-2])
            return (f"b_{k}_p", f"b_{k}_p"), Fraction(1)
        else:
            k = int(label[6:-2])
            return (f"b_{k}_m", f"b_{k}_m"), Fraction(1)
    if label.startswith("E_del"):
        rest = label[5:]
        under1 = rest.find("_del")
        i = int(rest[:under1])
        rest2 = rest[under1 + 4:]
        under2 = rest2.rfind("_")
        j = int(rest2[:under2])
        ss = rest2[under2 + 1:]
        o1 = f"b_{i}_{ss[0]}"
        o2 = f"b_{j}_{ss[1]}"
        return (o1, o2), Fraction(1)
    return None


# ---------------------------------------------------------------------------
# Main bracket computation using Wick-contraction formula
# ---------------------------------------------------------------------------

def bracket(X_label, Y_label, n, parity):
    """
    Compute [X, Y}_g as dict {Z: coeff} using the Wick contraction formula.
    """
    px = parity[X_label]
    py = parity[Y_label]

    # Handle Cartan × anything
    if X_label.startswith("H_"):
        return _cartan_root_bracket(X_label, Y_label, n, parity)
    if Y_label.startswith("H_"):
        inner = _cartan_root_bracket(Y_label, X_label, n, parity)
        sign = (-1) ** (px * py)
        return {Z: -Fraction(sign) * c for Z, c in inner.items()}

    # Both are root generators
    x_pair = gen_to_osc_pair(X_label, n)
    y_pair = gen_to_osc_pair(Y_label, n)
    if x_pair is None or y_pair is None:
        return {}

    (o1, o2), cx = x_pair
    (o3, o4), cy = y_pair
    coeff_total = cx * cy

    p1 = osc_parity(o1)
    p2 = osc_parity(o2)
    p3 = osc_parity(o3)
    p4 = osc_parity(o4)

    result = {}

    def add_osc_product(o_a, o_b, multiplier):
        if multiplier == 0:
            return
        gens, k_sc = osc_product_to_gens(o_a, o_b, n)
        for g, c in gens.items():
            result[g] = result.get(g, Fraction(0)) + multiplier * c
        # k_sc * K: K is central, coeff goes to "K" key
        if k_sc != 0:
            result["K"] = result.get("K", Fraction(0)) + multiplier * k_sc

    # Contraction scalars
    c23 = scalar_contraction(o2, o3)
    c24 = scalar_contraction(o2, o4)
    c13 = scalar_contraction(o1, o3)
    c14 = scalar_contraction(o1, o4)

    # Term 1: c23 * (o1 * o4)
    if c23 != 0:
        add_osc_product(o1, o4, coeff_total * c23)

    # Term 2: (-1)^{p2*p3} * c24 * (o1 * o3)
    if c24 != 0:
        sign2 = (-1) ** (p2 * p3)
        add_osc_product(o1, o3, coeff_total * Fraction(sign2) * c24)

    # Term 3: (-1)^{p2*(p3+p4)} * c13 * (o4 * o2)
    # Derivation: from Leibniz [AB,CD} = A*[B,CD} + (-1)^{p(B)(p(C)+p(D))} [A,CD}*B
    if c13 != 0:
        sign3 = (-1) ** (p2 * (p3 + p4))
        add_osc_product(o4, o2, coeff_total * Fraction(sign3) * c13)

    # Term 4: (-1)^{p2*(p3+p4)+p1*p3} * c14 * (o3 * o2)
    if c14 != 0:
        sign4 = (-1) ** (p2 * (p3 + p4) + p1 * p3)
        add_osc_product(o3, o2, coeff_total * Fraction(sign4) * c14)

    return {k: v for k, v in result.items() if v != 0}


def _cartan_root_bracket(H_label, X_label, n, parity):
    """
    Compute [H_k, X} = eigenvalue(H_k, X) * X.
    Cartan generators act diagonally on root generators.
    """
    if X_label.startswith("H_"):
        return {}  # [H, H] = 0

    k = int(H_label[2:])
    ev = _cartan_eigenvalue(k, X_label, n)
    if ev == 0:
        return {}
    return {X_label: Fraction(ev)}


def _cartan_eigenvalue(k, X_label, n):
    """
    Eigenvalue of H_k acting on root generator X.
    H_1 = n_a + n_1 → acts with coefficient (eps-charge + delta_1-charge)
    H_j = n_{j-1} - n_j → acts with (delta_{j-1}-charge - delta_j-charge)  (2<=j<=n)
    H_{n+1} = -n_n - 1/2 → acts with -delta_n-charge
    The constant -1/2 does not contribute to the eigenvalue of root generators.
    """
    # Determine root charges
    if X_label.startswith("E_eps1_del"):
        rest = X_label[len("E_eps1_del"):]
        under = rest.rfind("_")
        m = int(rest[:under])
        ss = rest[under + 1:]
        eps_c = 1 if ss[0] == "p" else -1
        del_c = {m: 1 if ss[1] == "p" else -1}
    elif X_label.startswith("E_2del"):
        if X_label.endswith("_p"):
            m = int(X_label[6:-2])
            eps_c, del_c = 0, {m: 2}
        else:
            m = int(X_label[6:-2])
            eps_c, del_c = 0, {m: -2}
    elif X_label.startswith("E_del"):
        rest = X_label[5:]
        under1 = rest.find("_del")
        i = int(rest[:under1])
        rest2 = rest[under1 + 4:]
        under2 = rest2.rfind("_")
        j = int(rest2[:under2])
        ss = rest2[under2 + 1:]
        eps_c = 0
        del_c = {i: 1 if ss[0] == "p" else -1, j: 1 if ss[1] == "p" else -1}
    else:
        return 0

    # Eigenvalue of H_k
    if k == 1:
        return eps_c + del_c.get(1, 0)
    elif 2 <= k <= n:
        return del_c.get(k - 1, 0) - del_c.get(k, 0)
    else:  # k == n+1
        return -del_c.get(n, 0)


# ---------------------------------------------------------------------------
# Basis construction
# ---------------------------------------------------------------------------

def build_basis(n):
    even = []
    for k in range(1, n + 2):
        even.append(f"H_{k}")
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
            even.append(f"E_del{i}_del{j}_mp")

    odd = []
    for k in range(1, n + 1):
        odd.append(f"E_eps1_del{k}_pp")
        odd.append(f"E_eps1_del{k}_pm")
        odd.append(f"E_eps1_del{k}_mp")
        odd.append(f"E_eps1_del{k}_mm")

    return even, odd


def build_parity(even_basis, odd_basis):
    parity = {}
    for g in even_basis:
        parity[g] = 0
    for g in odd_basis:
        parity[g] = 1
    return parity


# ---------------------------------------------------------------------------
# Structure constant computation
# ---------------------------------------------------------------------------

def compute_structure_constants(n, even_basis, odd_basis, parity):
    all_basis = even_basis + odd_basis
    basis_set = set(all_basis)
    constants = []

    for i, X in enumerate(all_basis):
        for j, Y in enumerate(all_basis):
            if j <= i:
                continue
            result = bracket(X, Y, n, parity)
            for Z, coeff in result.items():
                if Z not in basis_set:
                    continue  # Skip K (central, not in basis)
                if coeff != 0:
                    constants.append({
                        "X": X,
                        "Y": Y,
                        "Z": Z,
                        "coeff": str(coeff),
                        "sign_rule": "graded"
                    })

    return constants


# ---------------------------------------------------------------------------
# Generator realization field
# ---------------------------------------------------------------------------

def build_generator_realization(n, even_basis, odd_basis):
    oscs = ["a_1_p", "a_1_m"] + [f"b_{k}_{s}" for k in range(1, n + 1) for s in ["p", "m"]]
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
        for ss, (o1, o2) in [
            ("pp", ("a_1_p", f"b_{k}_p")),
            ("pm", ("a_1_p", f"b_{k}_m")),
            ("mp", ("a_1_m", f"b_{k}_p")),
            ("mm", ("a_1_m", f"b_{k}_m")),
        ]:
            realizations[f"E_eps1_del{k}_{ss}"] = {
                "standard_form": [{"words": [o1, o2], "coeff": "1"}],
                "frappat_form": f"{o1} {o2}",
                "parity": 1
            }

    for k in range(1, n + 1):
        realizations[f"E_2del{k}_p"] = {
            "standard_form": [{"words": [f"b_{k}_p", f"b_{k}_p"], "coeff": "1"}],
            "frappat_form": f"(b_{k}^+)^2",
            "parity": 0
        }
        realizations[f"E_2del{k}_m"] = {
            "standard_form": [{"words": [f"b_{k}_m", f"b_{k}_m"], "coeff": "1"}],
            "frappat_form": f"(b_{k}^-)^2",
            "parity": 0
        }

    for i in range(1, n + 1):
        for j in range(i + 1, n + 1):
            for ss, (s1, s2) in [("pp", ("p", "p")), ("mm", ("m", "m")),
                                  ("pm", ("p", "m")), ("mp", ("m", "p"))]:
                realizations[f"E_del{i}_del{j}_{ss}"] = {
                    "standard_form": [{"words": [f"b_{i}_{s1}", f"b_{j}_{s2}"], "coeff": "1"}],
                    "frappat_form": f"b_{i}^{'+'  if s1=='p' else '-'} b_{j}^{'+' if s2=='p' else '-'}",
                    "parity": 0
                }

    return {
        "description": "PBW ordering: a_1_p, a_1_m, b_1_p, b_1_m, ...",
        "ordering": ", ".join(oscs),
        "realizations": realizations
    }


# ---------------------------------------------------------------------------
# Build complete Schema 1
# ---------------------------------------------------------------------------

def build_schema1(n):
    even_basis, odd_basis = build_basis(n)
    parity = build_parity(even_basis, odd_basis)
    all_basis = even_basis + odd_basis

    dim_even = 2 * n * n + n + 1
    dim_odd = 4 * n

    boson_labels = [f"b_{k}_{s}" for k in range(1, n + 1) for s in ["p", "m"]]

    print(f"Computing structure constants for C({n+1}) (n={n})...")
    structure_constants = compute_structure_constants(n, even_basis, odd_basis, parity)
    print(f"  Found {len(structure_constants)} non-zero structure constants.")

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
            "dimension": {"total": dim_even + dim_odd, "even": dim_even, "odd": dim_odd}
        },
        "central_elements": {
            "kappa": {"label": "kappa", "parity": 1, "description": "Odd nilpotent central element; kappa^2=0"},
            "K": {"label": "K", "parity": 0, "description": "Even central element; identified with scalar 1. Not in PBW basis."}
        },
        "oscillator_generators": {
            "fermions": {"m": 1, "labels": ["a_1_p", "a_1_m"], "parity": 1, "description": "Standard fermionic pair with CAR"},
            "bosons": {"count": 2 * n, "n": n, "labels": boson_labels, "description": f"Bosonic oscillators b_k^+/- for k=1,...,{n}"}
        },
        "oscillator_relations": {
            "standard_fermion_anticommutators": {
                "description": "CAR: {a_1^-, a_1^+} = 1",
                "relations": {"anticommutator": "{a_1_m, a_1_p} = 1", "self_anticommutators": "{a_1_p, a_1_p} = 0, {a_1_m, a_1_m} = 0"}
            },
            "bosonic_commutators": {
                "description": "CCR: [b_i^-, b_j^+] = delta_{ij}",
                "relations": {"same_type": "[b_i_p, b_j_p] = 0", "conjugate_pair": "[b_i_m, b_j_p] = delta_{ij}"}
            },
            "mixed_commutators": {"boson_fermion": "[b_k, a_1] = 0"}
        },
        "basis": {
            "even": even_basis,
            "odd": odd_basis,
            "ordering_convention": "PBW: kappa < [odd: E_eps1] < [even: H, E_roots]"
        },
        "parity": {g: parity[g] for g in all_basis},
        "generator_realization": build_generator_realization(n, even_basis, odd_basis),
        "structure_constants": structure_constants,
        "metadata": {
            "generated_by": "src/C_generators.py",
            "generation_date": str(date.today()),
            "references": [
                "Frappat, Sciarrino, Sorba (2000), Dictionary on Lie Algebras and Superalgebras",
                "arXiv:hep-th/9607161"
            ]
        }
    }


def main():
    os.makedirs("data", exist_ok=True)
    for n in [1, 2, 3]:
        schema = build_schema1(n)
        fname = f"data/C_{n}_structure.json"
        with open(fname, "w") as f:
            json.dump(schema, f, indent=2)
        print(f"Written {fname}")


if __name__ == "__main__":
    main()
