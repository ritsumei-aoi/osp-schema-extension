"""
C_gamma.py
Compute Schema 2 (gamma structure) for C(n+1) = osp(2|2n).

The inhomogeneous deformation modifies boson-fermion commutation:
  [bks, a1sigma] = -gb_{sigma,k,s} * kappa  (was 0 in standard)

gamma(X, Y) is defined by:
  [X, Y]_deformed = [X, Y]_standard + kappa * gamma(X, Y)

gamma coefficients are linear in gb parameters for degree-2 generators.
"""

import json
import os
from fractions import Fraction
from collections import defaultdict

from C_generators import (
    make_osc_data, gen_poly, parity_of, build_basis,
    normal_form_poly, multiply_polys, express_in_basis_v2,
    rational_str, build_schema1
)

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")


# ---------------------------------------------------------------------------
# Deformed normal form: track kappa contributions from boson-fermion swaps
# ---------------------------------------------------------------------------

def _gb_label(a1_sign, bk_idx, bk_sign):
    """Return canonical gb parameter label: gb_{a1_sign}{bk_idx}{bk_sign}."""
    return f"gb_{a1_sign}{bk_idx}{bk_sign}"


def _is_fermionic(o):
    return o in ('a1p', 'a1m')


def _fermion_sign(o):
    return 'p' if o == 'a1p' else 'm'


def _boson_mode_sign(o):
    """Return (k, s) for bks oscillator."""
    # o = 'b{k}{s}' where s in {'p','m'}
    return int(o[1:-1]), o[-1]


def deformed_normal_form(init_dict, n, PARITY, osc_idx):
    """
    Bring each monomial tuple in init_dict to normal form, tracking
    deformed boson-fermion commutation contributions.

    Returns:
      standard_part: dict {tuple: Fraction}   (same as normal_form_poly)
      gamma_part: dict {tuple: dict{gb_label: Fraction}}
                  The kappa coefficient poly: kappa * sum_{mono} (sum_gb c_gb * gb) * mono
                  where each tuple is already in standard normal form.
    """
    from C_generators import comm_scalar

    standard_acc = defaultdict(Fraction)
    # Raw gamma contributions: list of (raw_tpl, {gb_label: Fraction})
    gamma_raw = []

    # Stack entries: (tpl, std_coeff)
    # We only track STANDARD coefficients in the main stack.
    # Deformed contributions go into gamma_raw with their (not-yet-normalized) tuples.
    stack = list(init_dict.items())

    while stack:
        tpl, std_c = stack.pop()
        if std_c == 0:
            continue

        found_swap = False
        for i in range(len(tpl) - 1):
            o, o_next = tpl[i], tpl[i + 1]
            p_o = PARITY[o]
            p_n = PARITY[o_next]

            # Fermionic squared = 0
            if o == o_next and p_o == 1:
                found_swap = True
                break

            idx_o = osc_idx[o]
            idx_n = osc_idx[o_next]

            if idx_o > idx_n:
                sign = Fraction((-1) ** (p_o * p_n))
                prefix = tpl[:i]
                suffix = tpl[i + 2:]

                # Standard: swap with sign
                swapped = prefix + (o_next, o) + suffix
                stack.append((swapped, std_c * sign))

                # Standard scalar (CCR/CAR)
                c_std = comm_scalar(o, o_next, n)
                if c_std != 0:
                    reduced = prefix + suffix
                    stack.append((reduced, std_c * c_std))

                # Deformed contribution: boson before fermion swap only
                if p_o == 0 and p_n == 1:
                    k, s = _boson_mode_sign(o)
                    sigma = _fermion_sign(o_next)
                    gb_lbl = _gb_label(sigma, k, s)
                    reduced = prefix + suffix
                    # Contribution: -std_c * gb_lbl * (remaining monomial)
                    gamma_raw.append((reduced, {gb_lbl: -std_c}))

                found_swap = True
                break

        if not found_swap:
            standard_acc[tpl] += std_c

    std = {k: v for k, v in standard_acc.items() if v != 0}

    # Now normalize the gamma_raw tuples using STANDARD normal form
    gamma_acc = defaultdict(lambda: defaultdict(Fraction))
    for raw_tpl, gb_d in gamma_raw:
        # Bring raw_tpl to standard normal form
        # normal_form_poly returns {norm_tpl: Fraction}
        nf = normal_form_poly({raw_tpl: Fraction(1)}, n, PARITY, osc_idx)
        for norm_tpl, nf_coeff in nf.items():
            for gl, gc in gb_d.items():
                gamma_acc[norm_tpl][gl] += gc * nf_coeff

    gam = {k: {gl: gv for gl, gv in gd.items() if gv != 0}
           for k, gd in gamma_acc.items()}
    gam = {k: v for k, v in gam.items() if v}
    return std, gam


def _scale_gb(gb_c, factor):
    return {gl: gc * factor for gl, gc in gb_c.items()}


def _accumulate_gamma(gamma_acc, tpl, new_gb):
    for gl, gc in new_gb.items():
        if gc != 0:
            gamma_acc[tpl][gl] += gc


def deformed_multiply(A, pA, B, pB, n, PARITY, osc_idx):
    """
    Compute A * B and B * A in the deformed algebra.
    Returns (std_AB, gam_AB, std_BA, gam_BA).
    """
    init_AB = {}
    for ta, ca in A.items():
        for tb, cb in B.items():
            key = ta + tb
            init_AB[key] = init_AB.get(key, Fraction(0)) + ca * cb
    std_AB, gam_AB = deformed_normal_form(init_AB, n, PARITY, osc_idx)

    init_BA = {}
    for tb, cb in B.items():
        for ta, ca in A.items():
            key = tb + ta
            init_BA[key] = init_BA.get(key, Fraction(0)) + cb * ca
    std_BA, gam_BA = deformed_normal_form(init_BA, n, PARITY, osc_idx)

    return std_AB, gam_AB, std_BA, gam_BA


def deformed_lie_bracket(A, pA, B, pB, n, PARITY, osc_idx):
    """
    Compute [A, B]_deformed = AB - (-1)^{pA pB} BA.
    Returns (std_part, gamma_part) where:
      std_part: dict {tuple: Fraction}  (= standard lie_bracket result)
      gamma_part: dict {tuple: {gb_label: Fraction}}
    """
    sign = Fraction((-1) ** (pA * pB))
    std_AB, gam_AB, std_BA, gam_BA = deformed_multiply(A, pA, B, pB, n, PARITY, osc_idx)

    # std_part = std_AB - sign * std_BA
    std = defaultdict(Fraction)
    for k, v in std_AB.items():
        std[k] += v
    for k, v in std_BA.items():
        std[k] -= sign * v
    std = {k: v for k, v in std.items() if v != 0}

    # gamma_part = gam_AB - sign * gam_BA
    gam = defaultdict(lambda: defaultdict(Fraction))
    for tpl, gd in gam_AB.items():
        for gl, gc in gd.items():
            gam[tpl][gl] += gc
    for tpl, gd in gam_BA.items():
        for gl, gc in gd.items():
            gam[tpl][gl] -= sign * gc
    gam = {k: {gl: gv for gl, gv in gd.items() if gv != 0}
           for k, gd in gam.items()}
    gam = {k: v for k, v in gam.items() if v}

    return std, gam


# ---------------------------------------------------------------------------
# Build gamma coefficients
# ---------------------------------------------------------------------------

def gb_expr(poly_in_gb):
    """Convert {gb_label: Fraction} to a string expression."""
    if not poly_in_gb:
        return "0"
    terms = []
    for gl, gc in sorted(poly_in_gb.items()):
        if gc == Fraction(1):
            terms.append(gl)
        elif gc == Fraction(-1):
            terms.append(f"-{gl}")
        else:
            terms.append(f"{rational_str(gc)}*{gl}")
    return " + ".join(terms).replace("+ -", "- ")


def build_gamma_coefficients(n, basis_even, basis_odd, PARITY, osc_idx):
    """
    For each pair (X, Y) of basis generators, compute gamma(X, Y).
    Returns list of {"X": X, "Y": Y, "Z": Z, "coeff_expr": expr}.
    """
    basis_all = basis_even + basis_odd
    entries = []

    for Xi, X in enumerate(basis_all):
        pX = parity_of(X)
        polyX = gen_poly(X, n)

        for Yi in range(Xi, len(basis_all)):
            Y = basis_all[Yi]
            pY = parity_of(Y)

            # [H,H] = 0 even in deformed case (both even, no fermion)
            if X.startswith("H_") and Y.startswith("H_"):
                continue

            polyY = gen_poly(Y, n)

            try:
                std_part, gam_part = deformed_lie_bracket(
                    polyX, pX, polyY, pY, n, PARITY, osc_idx
                )
                if not gam_part:
                    continue

                # Express the gamma polynomial in the basis
                # gam_part: {monomial_tuple: {gb_label: Fraction}}
                # For each monomial_tuple, find which basis generator it corresponds to
                # and accumulate the coefficient (in gb symbols)

                # Collect: {Z: {gb_label: Fraction}}
                z_gb = defaultdict(lambda: defaultdict(Fraction))

                # Group monomials by basis generator
                from C_generators import _cartan_monomials, _solve_cartan

                cartan_monos = set(_cartan_monomials(n))
                root_generators = basis_even[n + 1:] + basis_odd
                root_mono_map = {}
                for lbl in root_generators:
                    gp = gen_poly(lbl, n)
                    for mono, c in gp.items():
                        root_mono_map[mono] = (lbl, c)

                # Check for degree > 2 monomials
                for mono, gb_d in gam_part.items():
                    if len(mono) > 2:
                        # Should be zero; skip
                        continue
                    if mono in cartan_monos:
                        # Will handle via Cartan solver below
                        pass
                    elif mono in root_mono_map:
                        lbl, c_in_gen = root_mono_map[mono]
                        for gl, gc in gb_d.items():
                            z_gb[lbl][gl] += gc / c_in_gen
                    else:
                        # Degree-0 (scalar): K
                        if mono == ():
                            for gl, gc in gb_d.items():
                                z_gb['K'][gl] += gc

                # Handle Cartan sector: for each gb_label, solve separately
                cartan_gb_monos = {m: gd for m, gd in gam_part.items()
                                   if m in cartan_monos and len(m) <= 2}
                if cartan_gb_monos:
                    # Collect all gb labels that appear
                    all_gb = set()
                    for gd in cartan_gb_monos.values():
                        all_gb.update(gd.keys())
                    for gl in all_gb:
                        # Solve Cartan for this gb label
                        coeffs = {m: gd.get(gl, Fraction(0))
                                  for m, gd in cartan_gb_monos.items()}
                        solved = _solve_cartan(coeffs, n)
                        for lbl, v in solved.items():
                            if v != 0:
                                z_gb[lbl][gl] += v

                for Z, gb_d in z_gb.items():
                    if not gb_d:
                        continue
                    gb_d = {gl: gv for gl, gv in gb_d.items() if gv != 0}
                    if not gb_d:
                        continue
                    entries.append({
                        "X": X, "Y": Y, "Z": Z,
                        "coeff_expr": gb_expr(gb_d)
                    })

            except Exception as e:
                print(f"WARNING gamma({X},{Y}): {e}")

    return entries


# ---------------------------------------------------------------------------
# Build Schema 2 JSON
# ---------------------------------------------------------------------------

def build_schema2(n):
    ORDER, PARITY, osc_idx = make_osc_data(n)
    basis_even, basis_odd = build_basis(n)

    gb_params = []
    for k in range(1, n + 1):
        for sigma in ('p', 'm'):
            for s in ('p', 'm'):
                gb_params.append({
                    "label": f"gb_{sigma}{k}{s}",
                    "fermion": f"a1{sigma}",
                    "boson": f"b{k}{s}",
                    "parity": 1,
                    "description": f"[b{k}{s}, a1{sigma}] = -gb_{sigma}{k}{s} * kappa"
                })

    gamma_coeffs = build_gamma_coefficients(n, basis_even, basis_odd, PARITY, osc_idx)

    # Load Schema 1 for algebra/basis fields
    s1_path = os.path.join(DATA_DIR, f"C_{n}_structure.json")
    with open(s1_path) as f:
        s1 = json.load(f)

    return {
        "schema_version": "5.0",
        "algebra": s1["algebra"],
        "basis": s1["basis"],
        "parity": s1["parity"],
        "inhomogeneous_deformation": {
            "gb_matrix": {
                "description": f"4n={4*n} deformation parameters indexed by fermion sign, boson index, boson sign",
                "parameters": gb_params
            },
            "deformed_relation": "[bks, a1sigma] = -gb_{sigma,k,s} * kappa",
            "gamma_coefficients": gamma_coeffs
        },
        "metadata": {
            "generated_by": "C_gamma.py",
            "generation_date": "2026-10-09",
            "note": "gamma coefficients are linear in gb parameters for C(n+1)"
        }
    }


def main():
    os.makedirs(DATA_DIR, exist_ok=True)
    for n in [1, 2, 3]:
        print(f"Building Schema 2 for C({n+1})...", end=" ", flush=True)
        schema = build_schema2(n)
        path = os.path.join(DATA_DIR, f"C_{n}_gamma.json")
        with open(path, "w") as f:
            json.dump(schema, f, indent=2)
        ng = len(schema["inhomogeneous_deformation"]["gamma_coefficients"])
        print(f"done. gamma entries={ng}")


if __name__ == "__main__":
    main()
