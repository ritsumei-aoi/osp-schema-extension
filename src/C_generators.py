"""
C_generators.py
Generate Schema 1 structure-constant JSON for C(n+1) = osp(2|2n).

All structure constants are computed algebraically from the oscillator realization
using the "bring to normal form" algorithm.
"""

import json
import os
from fractions import Fraction
from collections import defaultdict


# ---------------------------------------------------------------------------
# Oscillator algebra: normal-form computation
# ---------------------------------------------------------------------------

def make_osc_data(n):
    """Return (ORDER, PARITY, osc_idx) for n bosonic modes."""
    ORDER = ['a1p', 'a1m'] + [f'b{k}{s}' for k in range(1, n+1) for s in 'pm']
    PARITY = {'a1p': 1, 'a1m': 1}
    for k in range(1, n+1):
        PARITY[f'b{k}p'] = 0
        PARITY[f'b{k}m'] = 0
    osc_idx = {o: i for i, o in enumerate(ORDER)}
    return ORDER, PARITY, osc_idx


def comm_scalar(o, o_next, n):
    """
    Return the scalar c such that o * o_next = sign(o,o_next) * o_next * o + c.
    sign(o,o_next) = (-1)^{p(o)*p(o_next)}.
    Derived from:
      {a1p, a1m} = 1  → a1p*a1m = 1 - a1m*a1p  and  a1m*a1p = 1 - a1p*a1m
      [bkm, bkp] = 1  → bkm*bkp = bkp*bkm + 1
      [bkp, bkm] = -1 → bkp*bkm = bkm*bkp - 1 (but this is already normal-ordered)
    The function is called when o > o_next in normal order (need to swap).
    """
    # Anti-commuting fermionic pair
    if {o, o_next} == {'a1p', 'a1m'}:
        return Fraction(1)
    # Bosonic conjugate pair in wrong order (annihilation before creation)
    for k in range(1, n+1):
        if o == f'b{k}m' and o_next == f'b{k}p':
            return Fraction(1)
    return Fraction(0)


def normal_form_poly(init_dict, n, PARITY, osc_idx):
    """
    Bring each monomial tuple in init_dict to normal form.
    Returns a dict {normal_tuple: Fraction}.
    Normal order: a1p, a1m, b1p, b1m, ..., bnp, bnm.
    """
    result = defaultdict(Fraction)
    stack = list(init_dict.items())  # [(tuple, coeff), ...]

    while stack:
        tpl, coeff = stack.pop()
        if coeff == 0:
            continue

        # Find first adjacent pair needing action
        found_swap = False
        for i in range(len(tpl) - 1):
            o, o_next = tpl[i], tpl[i + 1]
            p_o = PARITY[o]
            p_n = PARITY[o_next]

            # Fermionic operator squared = 0 (check before ordering)
            if o == o_next and p_o == 1:
                found_swap = True
                break  # discard this term (zero)

            idx_o = osc_idx[o]
            idx_n = osc_idx[o_next]

            if idx_o > idx_n:
                # Out of order: swap
                sign = Fraction((-1) ** (p_o * p_n))
                c = comm_scalar(o, o_next, n)

                prefix = tpl[:i]
                suffix = tpl[i + 2:]

                swapped = prefix + (o_next, o) + suffix
                stack.append((swapped, coeff * sign))

                if c != 0:
                    reduced = prefix + suffix
                    stack.append((reduced, coeff * c))

                found_swap = True
                break

        if not found_swap:
            result[tpl] += coeff

    return {k: v for k, v in result.items() if v != 0}


def multiply_polys(A, B, n, PARITY, osc_idx):
    """Multiply two polynomials (each a dict {tuple: Fraction})."""
    init = {}
    for ta, ca in A.items():
        for tb, cb in B.items():
            key = ta + tb
            init[key] = init.get(key, Fraction(0)) + ca * cb
    return normal_form_poly(init, n, PARITY, osc_idx)


def add_polys(*polys):
    result = defaultdict(Fraction)
    for p in polys:
        for k, v in p.items():
            result[k] += v
    return {k: v for k, v in result.items() if v != 0}


def scale_poly(p, s):
    return {k: v * s for k, v in p.items() if v * s != 0}


def lie_bracket(A, B, pA, pB, n, PARITY, osc_idx):
    """
    Compute the graded Lie bracket [A, B] = AB - (-1)^{pA*pB} BA.
    A, B: dicts {tuple: Fraction}.
    pA, pB: parities (int 0 or 1).
    """
    AB = multiply_polys(A, B, n, PARITY, osc_idx)
    BA = multiply_polys(B, A, n, PARITY, osc_idx)
    sign = Fraction((-1) ** (pA * pB))
    return add_polys(AB, scale_poly(BA, -sign))


# ---------------------------------------------------------------------------
# Basis and generator polynomials
# ---------------------------------------------------------------------------

def build_basis(n):
    cartans = [f"H_{k}" for k in range(1, n + 2)]
    pos_2del = [f"E_2del{k}_p" for k in range(1, n + 1)]
    pos_pp = [f"E_del{i}_del{j}_pp" for i in range(1, n+1) for j in range(i+1, n+1)]
    neg_2del = [f"E_2del{k}_m" for k in range(1, n + 1)]
    neg_mm = [f"E_del{i}_del{j}_mm" for i in range(1, n+1) for j in range(i+1, n+1)]
    mixed = [lbl for i in range(1,n+1) for j in range(i+1,n+1)
             for lbl in (f"E_del{i}_del{j}_pm", f"E_del{i}_del{j}_mp")]
    basis_even = cartans + pos_2del + pos_pp + neg_2del + neg_mm + mixed

    basis_odd = [f"E_eps1_del{k}_{s1}{s2}"
                 for k in range(1, n+1)
                 for s1 in ("p", "m") for s2 in ("p", "m")]
    return basis_even, basis_odd


def parity_of(label):
    return 1 if label.startswith("E_eps1") else 0


def gen_poly(label, n):
    """
    Return the polynomial (dict {tuple: Fraction}) for generator 'label'.
    Cartan elements H_k are represented as sums (e.g. H_1 = a1p*a1m + b1p*b1m).
    K (constant -1/2) is represented as {(): -1/2}.
    """
    if label.startswith("H_"):
        k = int(label[2:])
        if k == 1:
            # H_1 = a1p a1m + b1p b1m
            return {('a1p', 'a1m'): Fraction(1), ('b1p', 'b1m'): Fraction(1)}
        elif 2 <= k <= n:
            # H_k = b(k-1)p b(k-1)m - bkp bkm
            return {(f'b{k-1}p', f'b{k-1}m'): Fraction(1), (f'b{k}p', f'b{k}m'): Fraction(-1)}
        else:  # k == n+1
            # H_{n+1} = -bnp bnm - 1/2
            return {(f'b{n}p', f'b{n}m'): Fraction(-1), (): Fraction(-1, 2)}
    elif label == "K":
        return {(): Fraction(1)}
    elif label.startswith("E_2del"):
        k = int(label[len("E_2del"):].split("_")[0])
        s = label[-1]  # 'p' or 'm'
        o = f'b{k}{s}'
        return {(o, o): Fraction(1)}
    elif label.startswith("E_del") and "eps" not in label:
        rest = label[len("E_del"):]
        parts = rest.split("_")
        i, j = int(parts[0][3:]) if parts[0].startswith("del") else int(parts[0]), 0
        # Format: E_del{i}_del{j}_{suffix}
        # Actually: rest after "E_" is "del{i}_del{j}_{suffix}"
        tokens = rest.split("_")  # ["del{i}", "del{j}", "suffix"]? No: rest starts with digits after "E_del"
        # Let me re-parse: label = "E_del{i}_del{j}_{suffix}"
        # Remove "E_" prefix to get "del{i}_del{j}_{suffix}"
        core = label[2:]  # "del{i}_del{j}_{suffix}"
        toks = core.split("_")  # ["del{i}", "del{j}", "{suffix}"]
        i_idx = int(toks[0][3:])
        j_idx = int(toks[1][3:])
        suffix = toks[2]  # pp, mm, pm, mp
        s1, s2 = suffix[0], suffix[1]
        return {(f'b{i_idx}{s1}', f'b{j_idx}{s2}'): Fraction(1)}
    elif label.startswith("E_eps1"):
        # E_eps1_del{k}_{s1}{s2}
        parts = label.split("_")
        k = int(parts[2][3:])
        s1, s2 = parts[3][0], parts[3][1]
        return {(f'a1{s1}', f'b{k}{s2}'): Fraction(1)}
    return {}


def poly_parity(label):
    """Parity of a basis element."""
    if label.startswith("E_eps1"):
        return 1
    return 0


# ---------------------------------------------------------------------------
# Express a polynomial in terms of basis generators + K
# ---------------------------------------------------------------------------

def express_in_basis(poly, basis_all, n, PARITY, osc_idx):
    """
    Given a polynomial (dict {tuple: Fraction}), express it as
    a dict {basis_label: Fraction} where basis_label ∈ basis_all ∪ {'K'}.
    Raises ValueError if the polynomial is not in the span.
    """
    result = {}
    remaining = dict(poly)

    # Map from normal-form monomial to basis label
    mono_to_label = {}
    for lbl in basis_all:
        p = gen_poly(lbl, n)
        for mono in p:
            if mono != ():
                mono_to_label[mono] = (lbl, p[mono])

    # Also check H_{n+1} which has a constant term
    # H_{n+1} polynomial: {(bnp, bnm): -1, (): -1/2}
    # So () → K (if the scalar in remaining matches)

    # Subtract basis elements
    for mono, coeff in list(remaining.items()):
        if mono == ():
            # Scalar: this is K contribution
            result['K'] = result.get('K', Fraction(0)) + coeff
            del remaining[mono]
        elif mono in mono_to_label:
            lbl, c = mono_to_label[mono]
            factor = coeff / c
            # Subtract factor * gen_poly(lbl)
            gen = gen_poly(lbl, n)
            for m2, c2 in gen.items():
                remaining[m2] = remaining.get(m2, Fraction(0)) - factor * c2
            if remaining.get(m2, Fraction(0)) == 0:
                remaining.pop(m2, None)
            result[lbl] = result.get(lbl, Fraction(0)) + factor

    # Clean up scalar term after basis subtraction
    if () in remaining:
        result['K'] = result.get('K', Fraction(0)) + remaining.pop(())

    # Check remaining is empty
    remaining = {k: v for k, v in remaining.items() if v != 0}
    if remaining:
        raise ValueError(f"Polynomial not in basis span: {remaining}")

    return {k: v for k, v in result.items() if v != 0}


def _cartan_monomials(n):
    """Return the ordered list of Cartan sector monomials for C(n+1)."""
    return (
        [('a1p', 'a1m')]
        + [(f'b{k}p', f'b{k}m') for k in range(1, n + 1)]
        + [()]
    )


def _solve_cartan(cartan_coeffs, n):
    """
    Solve the linear system: given dict {cartan_mono: Fraction},
    return dict {gen_label: Fraction} for H_1,...,H_{n+1},K.

    Cartan monomials in order: (a1p,a1m), (b1p,b1m),...,(bnp,bnm), ().
    Generator ordering: H_1, H_2, ..., H_{n+1}, K.

    Uses the banded structure of the system for direct back-substitution.
    """
    monos = _cartan_monomials(n)
    c = [cartan_coeffs.get(m, Fraction(0)) for m in monos]
    x = [Fraction(0)] * (n + 2)

    # c[0] = (a1p,a1m) coeff, only in H_1 with coeff 1
    x[0] = c[0]  # H_1

    if n == 1:
        # H_2 = -b1p b1m - 1/2; appears in monos[1] with coeff -1
        # Eq for monos[1]: x[0]*1 + x[1]*(-1) = c[1]  → x[1] = x[0] - c[1]
        x[1] = x[0] - c[1]
        # Eq for monos[2]=(}: x[1]*(-1/2) + x[2]*1 = c[2]
        x[2] = c[2] + x[1] / 2
    else:
        # k=1: H_1 has m[1] with coeff 1, H_2 has m[1] with coeff 1
        # Eq: x[0]+x[1] = c[1]
        x[1] = c[1] - x[0]

        # k=2..n-1: H_k has m[k-1] with coeff 1, H_{k+1} has m[k-1] with -1
        #           H_{k+1} has m[k] with coeff 1, H_{k+2} has m[k] with -1
        # Eq for m[k]: -x[k-1] + x[k] = c[k]  → x[k] = c[k] + x[k-1]
        for k in range(2, n):
            x[k] = c[k] + x[k - 1]

        # k=n: H_n has m[n] with coeff -1, H_{n+1} has m[n] with coeff -1
        # Eq: -x[n-1] - x[n] = c[n]  → x[n] = -c[n] - x[n-1]
        x[n] = -c[n] - x[n - 1]

        # Scalar: H_{n+1} has () with coeff -1/2, K has () with coeff 1
        # Eq: x[n]*(-1/2) + x[n+1]*1 = c[n+1]
        x[n + 1] = c[n + 1] + x[n] / 2

    gens = [f'H_{k}' for k in range(1, n + 2)] + ['K']
    return {g: v for g, v in zip(gens, x) if v != 0}


def express_in_basis_v2(poly, basis_even, basis_odd, n, PARITY, osc_idx):
    """
    Express a polynomial in terms of basis generators + K.
    - Cartan monomials: solved via linear system (_solve_cartan).
    - Root monomials: uniquely matched to a single root generator.
    - Degree > 2 monomials: should not appear (raise ValueError).
    """
    # Separate monomials into categories
    cartan_monos = set(_cartan_monomials(n))
    root_generators = basis_even[n + 1:] + basis_odd  # exclude Cartans

    # Build monomial → (label, coeff) map for root generators
    root_mono_map = {}
    for lbl in root_generators:
        gp = gen_poly(lbl, n)
        for mono, c in gp.items():
            if mono in root_mono_map:
                raise RuntimeError(f"Monomial {mono} claimed by multiple root gens")
            root_mono_map[mono] = (lbl, c)

    cartan_coeffs = {}
    result = {}

    for mono, coeff in poly.items():
        if coeff == 0:
            continue
        if len(mono) > 2:
            raise ValueError(f"Degree-{len(mono)} monomial in result: {mono}")
        if mono in cartan_monos:
            cartan_coeffs[mono] = cartan_coeffs.get(mono, Fraction(0)) + coeff
        elif mono in root_mono_map:
            lbl, c_in_gen = root_mono_map[mono]
            result[lbl] = result.get(lbl, Fraction(0)) + coeff / c_in_gen
        else:
            raise ValueError(f"Monomial {mono} not in basis")

    # Solve Cartan sector
    if cartan_coeffs:
        for lbl, v in _solve_cartan(cartan_coeffs, n).items():
            result[lbl] = result.get(lbl, Fraction(0)) + v

    return {k: v for k, v in result.items() if v != 0}


# ---------------------------------------------------------------------------
# Build structure constants
# ---------------------------------------------------------------------------

def build_structure_constants(n, basis_even, basis_odd, PARITY, osc_idx):
    """Compute all non-zero structure constants by direct oscillator computation."""
    basis_all = basis_even + basis_odd
    sc = []
    seen = set()

    for Xi, X in enumerate(basis_all):
        pX = parity_of(X)
        polyX = gen_poly(X, n)

        for Yi in range(Xi, len(basis_all)):
            Y = basis_all[Yi]
            pY = parity_of(Y)

            # For [H, H] = 0
            if X.startswith("H_") and Y.startswith("H_"):
                continue

            polyY = gen_poly(Y, n)

            try:
                bracket_poly = lie_bracket(polyX, polyY, pX, pY, n, PARITY, osc_idx)
                if not bracket_poly:
                    continue

                res_dict = express_in_basis_v2(bracket_poly, basis_even, basis_odd, n, PARITY, osc_idx)
                if not res_dict:
                    continue

                result_list = [{"Z": Z, "coeff": rational_str(c)} for Z, c in sorted(res_dict.items())]
                sc.append({
                    "X": X, "Y": Y,
                    "result": result_list,
                    "sign_rule": "graded"
                })
            except ValueError as e:
                print(f"WARNING: {X}, {Y}: {e}")

    return sc


def rational_str(f):
    if f.denominator == 1:
        return str(f.numerator)
    return f"{f.numerator}/{f.denominator}"


# ---------------------------------------------------------------------------
# Cartan eigenvalue (for tests)
# ---------------------------------------------------------------------------

def cartan_eigenvalue(h_idx, gen_label, n):
    _, PARITY, osc_idx = make_osc_data(n)
    H = gen_poly(f"H_{h_idx}", n)
    G = gen_poly(gen_label, n)
    pH = 0
    pG = parity_of(gen_label)
    bracket_poly = lie_bracket(H, G, pH, pG, n, PARITY, osc_idx)
    if not bracket_poly:
        return Fraction(0)
    # [H, E_alpha] = lambda * E_alpha: the bracket is lambda * E_alpha polynomial
    # The lambda is the coeff of E_alpha's monomial divided by E_alpha's coeff
    gen_mono = gen_poly(gen_label, n)
    # E_alpha should be a single monomial with coeff 1
    if len(gen_mono) != 1:
        return Fraction(0)
    mono, c_gen = list(gen_mono.items())[0]
    c_bracket = bracket_poly.get(mono, Fraction(0))
    return c_bracket / c_gen


# ---------------------------------------------------------------------------
# Build full Schema 1 JSON
# ---------------------------------------------------------------------------

def build_schema1(n):
    ORDER, PARITY, osc_idx = make_osc_data(n)
    basis_even, basis_odd = build_basis(n)
    sc = build_structure_constants(n, basis_even, basis_odd, PARITY, osc_idx)

    parity = {g: 0 for g in basis_even}
    parity.update({g: 1 for g in basis_odd})

    boson_labels = [f"b{k}{s}" for k in range(1, n+1) for s in 'pm']

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
                "total": 2*n*n + 5*n + 1,
                "even": 2*n*n + n + 1,
                "odd": 4*n
            }
        },
        "central_elements": {
            "K": {"label": "K", "parity": 0,
                  "description": "Even central element; identified with scalar 1.", "in_basis": False},
            "kappa": {"label": "kappa", "parity": 1,
                      "description": "Odd nilpotent central element kappa^2=0.", "in_basis": False}
        },
        "oscillator_generators": {
            "fermions": {"m": 1, "labels": ["a1p", "a1m"], "parity": 1,
                         "description": "Standard fermionic pair {a1m, a1p}=1."},
            "bosons": {"count": 2*n, "n": n, "labels": boson_labels,
                       "description": f"Bosonic oscillators b_k^+/- for k=1,...,{n}"}
        },
        "oscillator_relations": {
            "standard_fermion_anticommutators": {
                "anticommutator": "{a1m, a1p} = 1", "nilpotency": "a1p^2 = 0, a1m^2 = 0"},
            "bosonic_commutators": {
                "conjugate_pair": "[bkm, bkp] = 1 (same k)", "cross": "all other pairs commute"},
            "mixed": "all [bkp/m, a1p/m] = 0"
        },
        "basis": {
            "even": basis_even, "odd": basis_odd,
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
    r["H_1"] = {"standard_form": [{"words": ["a1p","a1m"],"coeff":"1"},
                                    {"words": ["b1p","b1m"],"coeff":"1"}],
                 "frappat_form": "a_1^+ a_1^- + b_1^+ b_1^-", "parity": 0}
    for k in range(2, n+1):
        r[f"H_{k}"] = {"standard_form": [{"words": [f"b{k-1}p",f"b{k-1}m"],"coeff":"1"},
                                           {"words": [f"b{k}p",f"b{k}m"],"coeff":"-1"}],
                        "frappat_form": f"b_{k-1}^+ b_{k-1}^- - b_{k}^+ b_{k}^-", "parity": 0}
    r[f"H_{n+1}"] = {"standard_form": [{"words": [f"b{n}p",f"b{n}m"],"coeff":"-1"},
                                         {"words": [],"coeff":"-1/2"}],
                      "frappat_form": f"-b_{n}^+ b_{n}^- - 1/2", "parity": 0,
                      "note": "Constant -1/2 reflects central K."}
    for k in range(1, n+1):
        for s1, s2 in [("p","p"),("p","m"),("m","p"),("m","m")]:
            lbl = f"E_eps1_del{k}_{s1}{s2}"
            r[lbl] = {"standard_form": [{"words": [f"a1{s1}",f"b{k}{s2}"],"coeff":"1"}],
                       "frappat_form": f"a_1^{'+' if s1=='p' else '-'} b_{k}^{'+' if s2=='p' else '-'}",
                       "parity": 1}
        r[f"E_2del{k}_p"] = {"standard_form": [{"words": [f"b{k}p",f"b{k}p"],"coeff":"1"}],
                              "frappat_form": f"(b_{k}^+)^2", "parity": 0}
        r[f"E_2del{k}_m"] = {"standard_form": [{"words": [f"b{k}m",f"b{k}m"],"coeff":"1"}],
                              "frappat_form": f"(b_{k}^-)^2", "parity": 0}
    for i in range(1, n+1):
        for j in range(i+1, n+1):
            for s1, s2 in [("p","p"),("m","m"),("p","m"),("m","p")]:
                sfx = s1+s2
                lbl = f"E_del{i}_del{j}_{sfx}"
                r[lbl] = {"standard_form": [{"words": [f"b{i}{s1}",f"b{j}{s2}"],"coeff":"1"}],
                           "frappat_form": f"b_{i}^{'+' if s1=='p' else '-'} b_{j}^{'+' if s2=='p' else '-'}",
                           "parity": 0}
    return r


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    out_dir = os.path.join(os.path.dirname(__file__), "..", "data")
    os.makedirs(out_dir, exist_ok=True)

    for n in [1, 2, 3]:
        print(f"Building C({n+1})...", end=" ", flush=True)
        schema = build_schema1(n)
        path = os.path.join(out_dir, f"C_{n}_structure.json")
        with open(path, "w") as f:
            json.dump(schema, f, indent=2)
        print(f"done. dim={schema['algebra']['dimension']}, sc={len(schema['structure_constants'])}")


if __name__ == "__main__":
    main()
