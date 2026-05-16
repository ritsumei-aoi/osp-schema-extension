"""
verify_C_structure.py

Super Jacobi identity and anti-symmetry verification for C(n+1) = osp(2|2n).
Loads the generated JSON structure constants and checks:

  1. Anti-symmetry:  [Y, X] = -(-1)^{p(X)p(Y)} [X, Y]
  2. Super Jacobi:   (-1)^{p(X)p(Z)} [X, [Y, Z]] + cyclic = 0

for all generator triples.  Uses exact rational arithmetic (Fraction).
"""

import json
import sys
from fractions import Fraction
from itertools import combinations
from pathlib import Path


def load_json(n: int) -> dict:
    """Load C_n_structure.json from data/algebra_structures."""
    path = Path(__file__).parent.parent / "data" / "algebra_structures" / f"C_{n}_structure.json"
    with open(path) as f:
        return json.load(f)


def parse_coeff(s: str) -> Fraction:
    """Parse a rational coefficient string like '3', '-1/2', '0'."""
    if "/" in s:
        num, den = s.split("/")
        return Fraction(int(num), int(den))
    return Fraction(int(s), 1)


def check_antisymmetry(data: dict, verbose: bool = False) -> dict:
    """
    Verify [Y, X] = -(-1)^{p(X)p(Y)} [X, Y] for all bracket entries.
    """
    brackets = data["structure_constants"]["brackets"]
    parity = data["parity"]
    all_gens = list(parity.keys())

    # Build a lookup for reverse brackets
    errors = []
    checked = set()
    antisymmetric_pairs = 0

    for key, results in brackets.items():
        g1, g2 = key.split(",")
        if g1 not in parity or g2 not in parity:
            continue

        # Only check each unordered pair once
        pair = (g1, g2) if g1 <= g2 else (g2, g1)
        if pair in checked:
            continue
        checked.add(pair)

        rev_key = f"{g2},{g1}"
        rev_results = brackets.get(rev_key, {})

        p1 = parity[g1]
        p2 = parity[g2]
        sign = (-1) ** (p1 * p2)  # factor: [Y,X] = -(-1)^{p(X)p(Y)} [X,Y]

        # The expected relation: rev_result = -sign * result
        all_keys = set(results.keys()) | set(rev_results.keys())
        for gen in all_keys:
            c_fwd = parse_coeff(results.get(gen, "0"))
            c_rev = parse_coeff(rev_results.get(gen, "0"))
            expected_rev = -sign * c_fwd
            if c_rev != expected_rev:
                errors.append({
                    "pair": (g1, g2),
                    "generator": gen,
                    "c_fwd": str(c_fwd),
                    "c_rev": str(c_rev),
                    "expected_rev": str(expected_rev),
                    "parities": (p1, p2),
                    "sign_factor": sign,
                })

        if results:
            antisymmetric_pairs += 1

    return {
        "pass": len(errors) == 0,
        "total_pairs_checked": len(checked),
        "pairs_with_brackets": antisymmetric_pairs,
        "errors": errors[:20],  # limit output
        "total_errors": len(errors),
    }


def check_super_jacobi(data: dict, verbose: bool = False) -> dict:
    """
    Verify Super Jacobi identity for all triples of generators.

    For each triple (X, Y, Z) with X < Y < Z, compute:
        J(X,Y,Z) = (-1)^{p(X)p(Z)} [X, [Y, Z]] + cyclic(2 terms)
    
    The bracket expansion:
        [X, [Y, Z]] = sum_{u,v} c_{YZ}^u * c_{Xu}^v * v
    where c_{YZ}^u is the coefficient of u in [Y,Z].
    """
    brackets = data["structure_constants"]["brackets"]
    parity = data["parity"]
    all_gens = list(parity.keys())

    # Pre-compute sign factor s(Y,Z,X) for each pair-in-pair
    # [X, [Y, Z]] contributes factor (-1)^{p(X)p(Z)}
    # [Y, [Z, X]] contributes factor (-1)^{p(Y)p(X)}
    # [Z, [X, Y]] contributes factor (-1)^{p(Z)p(Y)}

    errors = []
    triples_checked = 0
    triples_with_nonzero = 0

    n_gens = len(all_gens)
    for i in range(n_gens):
        for j in range(i + 1, n_gens):
            for k in range(j + 1, n_gens):
                X = all_gens[i]
                Y = all_gens[j]
                Z = all_gens[k]
                triples_checked += 1

                pX = parity[X]
                pY = parity[Y]
                pZ = parity[Z]

                # ---- Compute J(X,Y,Z) ----
                # J = (-1)^{pX*pZ} * [X, [Y,Z]] + (-1)^{pY*pX} * [Y, [Z,X]] + (-1)^{pZ*pY} * [Z, [X,Y]]

                # Helper: given (A, B, C) and outer_parity_factor,
                # expand [A, [B, C]] into generator contributions.
                def expand_double_bracket(A, B, C, outer_factor):
                    """Return dict {gen: coeff} for outer_factor * [A, [B, C]]."""
                    # [B, C] → look up (B,C) and (C,B)
                    bc_key = f"{B},{C}"
                    cb_key = f"{C},{B}"
                    result = {}
                    # Get [B,C] entries
                    bc = brackets.get(bc_key, {})
                    for U, coeff_str in bc.items():
                        # [A, U] — look up (A,U) and (U,A)
                        au_key = f"{A},{U}"
                        ua_key = f"{U},{A}"
                        au = brackets.get(au_key, {})
                        for V, c_str in au.items():
                            c_inner = parse_coeff(coeff_str)
                            c_outer = parse_coeff(c_str)
                            total = outer_factor * c_inner * c_outer
                            if total != 0:
                                result[V] = result.get(V, Fraction(0, 1)) + total
                    return result

                # Three cyclic terms
                # We use the general Super Jacobi formula:
                # (-1)^{p(X)p(Z)} [X, [Y,Z]] + (-1)^{p(Y)p(X)} [Y, [Z,X]] + (-1)^{p(Z)p(Y)} [Z, [X,Y]]
                # BUT [Z,X] = -(-1)^{p(Z)p(X)} [X,Z], so we need to compute via existing keys.

                # Actually, the clean way: for each term, compute inner bracket, then outer.
                # The algebra only stores [X,Y] for X<Y in some sense (not guaranteed), so
                # we need to use the bracket dict which has both (g1,g2) and (g2,g1).

                # Term 1: (-1)^{pX*pZ} * [X, [Y,Z]]
                term1 = {}
                yz_key = f"{Y},{Z}"
                zy_key = f"{Z},{Y}"
                # [Y,Z] is the anticommutator if both odd, else commutator
                # For the inner bracket, we just read the stored value.
                yz_results = {}
                if yz_key in brackets:
                    yz_results.update(brackets[yz_key])
                # Now expand [X, U] for each U in yz_results
                # IMPORTANT: The generator stores BOTH [X,U] and [U,X] explicitly.
                # Use (X,U) if available; otherwise derive from (U,X) with sign factor.
                # Do NOT sum both to avoid double-counting.
                p_factor = (-1) ** (pX * pZ)
                for U, coeff_str in yz_results.items():
                    xu_key = f"{X},{U}"
                    ux_key = f"{U},{X}"
                    c_yz = parse_coeff(coeff_str)
                    if xu_key in brackets:
                        for V, c_str in brackets[xu_key].items():
                            total = p_factor * c_yz * parse_coeff(c_str)
                            if total != 0:
                                term1[V] = term1.get(V, Fraction(0, 1)) + total
                    elif ux_key in brackets:
                        pU = parity.get(U, 0)
                        sign_ux = -((-1) ** (pU * pX))  # [X,U] = -(-1)^{p(U)p(X)} [U,X]
                        for V, c_str in brackets[ux_key].items():
                            total = p_factor * c_yz * sign_ux * parse_coeff(c_str)
                            if total != 0:
                                term1[V] = term1.get(V, Fraction(0, 1)) + total

                # Term 2: (-1)^{pY*pX} * [Y, [Z,X]]
                term2 = {}
                zx_key = f"{Z},{X}"
                xz_key = f"{X},{Z}"
                zx_results = {}
                if zx_key in brackets:
                    zx_results.update(brackets[zx_key])
                elif xz_key in brackets:
                    pX = parity[X]
                    pZ = parity[Z]
                    for V, c_str in brackets[xz_key].items():
                        # [Z,X] = -(-1)^{p(Z)p(X)} [X,Z]
                        sign_zx = -((-1) ** (pZ * pX))
                        zx_results[V] = _format_coeff(sign_zx * parse_coeff(c_str))
                p_factor = (-1) ** (pY * pX)
                for U, coeff_str in zx_results.items():
                    yu_key = f"{Y},{U}"
                    uy_key = f"{U},{Y}"
                    c_zx = parse_coeff(coeff_str)
                    if yu_key in brackets:
                        for V, c_str in brackets[yu_key].items():
                            total = p_factor * c_zx * parse_coeff(c_str)
                            if total != 0:
                                term2[V] = term2.get(V, Fraction(0, 1)) + total
                    elif uy_key in brackets:
                        pU = parity.get(U, 0)
                        sign_uy = -((-1) ** (pU * pY))
                        for V, c_str in brackets[uy_key].items():
                            total = p_factor * c_zx * sign_uy * parse_coeff(c_str)
                            if total != 0:
                                term2[V] = term2.get(V, Fraction(0, 1)) + total

                # Term 3: (-1)^{pZ*pY} * [Z, [X,Y]]
                term3 = {}
                xy_key = f"{X},{Y}"
                yx_key = f"{Y},{X}"
                xy_results = {}
                if xy_key in brackets:
                    xy_results.update(brackets[xy_key])
                elif yx_key in brackets:
                    pX = parity[X]
                    pY = parity[Y]
                    for V, c_str in brackets[yx_key].items():
                        sign_xy = -((-1) ** (pY * pX))
                        xy_results[V] = _format_coeff(sign_xy * parse_coeff(c_str))
                p_factor = (-1) ** (pZ * pY)
                for U, coeff_str in xy_results.items():
                    zu_key = f"{Z},{U}"
                    uz_key = f"{U},{Z}"
                    c_xy = parse_coeff(coeff_str)
                    if zu_key in brackets:
                        for V, c_str in brackets[zu_key].items():
                            total = p_factor * c_xy * parse_coeff(c_str)
                            if total != 0:
                                term3[V] = term3.get(V, Fraction(0, 1)) + total
                    elif uz_key in brackets:
                        pU = parity.get(U, 0)
                        sign_uz = -((-1) ** (pU * pZ))
                        for V, c_str in brackets[uz_key].items():
                            total = p_factor * c_xy * sign_uz * parse_coeff(c_str)
                            if total != 0:
                                term3[V] = term3.get(V, Fraction(0, 1)) + total

                # Sum all terms
                jacobi = {}
                all_keys = set(term1.keys()) | set(term2.keys()) | set(term3.keys())
                for V in all_keys:
                    total = term1.get(V, Fraction(0, 1)) + term2.get(V, Fraction(0, 1)) + term3.get(V, Fraction(0, 1))
                    if total != 0:
                        jacobi[V] = total

                if jacobi:
                    triples_with_nonzero += 1
                    if verbose or len(errors) < 20:
                        errors.append({
                            "triple": (X, Y, Z),
                            "parities": (pX, pY, pZ),
                            "non_zero": {k: str(v) for k, v in jacobi.items()},
                        })

    return {
        "pass": len(errors) == 0,
        "total_triples": triples_checked,
        "triples_with_nonzero_sj": triples_with_nonzero,
        "errors": errors[:30],
        "total_errors": len(errors),
    }


def run_verification(n: int, verbose: bool = False) -> dict:
    """Run all checks for a given n."""
    data = load_json(n)
    result = {
        "n": n,
        "algebra": f"C({n + 1}) = osp(2|{2 * n})",
        "dimension": data["algebra"]["dimension"],
    }
    result["antisymmetry"] = check_antisymmetry(data, verbose)
    result["super_jacobi"] = check_super_jacobi(data, verbose)
    return result


def print_report(results: list):
    """Print a formatted verification report."""
    sep = "=" * 72

    print(sep)
    print("  Super Jacobi Identity & Anti-symmetry Verification for C(n+1)")
    print(sep)
    print()

    all_pass = True
    for r in results:
        n = r["n"]
        print(f"  C({n + 1}) = osp(2|{2 * n})")
        print(f"  Dimension: even={r['dimension']['even']}, "
              f"odd={r['dimension']['odd']}, "
              f"total={r['dimension']['total']}")
        print()

        a = r["antisymmetry"]
        a_status = "  ✅ Anti-symmetry: PASS" if a["pass"] else "  ❌ Anti-symmetry: FAIL"
        print(f"{a_status}")
        print(f"     Pairs checked: {a['total_pairs_checked']}, "
              f"pairs with brackets: {a['pairs_with_brackets']}")
        if not a["pass"]:
            all_pass = False
            print(f"     Errors: {a['total_errors']}")
            for e in a["errors"][:5]:
                print(f"       {e['pair']}: {e['generator']} "
                      f"fwd={e['c_fwd']} rev={e['c_rev']} "
                      f"expected={e['expected_rev']}")

        sj = r["super_jacobi"]
        sj_status = "  ✅ Super Jacobi: PASS" if sj["pass"] else "  ❌ Super Jacobi: FAIL"
        print(f"{sj_status}")
        print(f"     Triples checked: {sj['total_triples']}, "
              f"non-zero SJ values: {sj['triples_with_nonzero_sj']}")
        if not sj["pass"]:
            all_pass = False
            print(f"     Non-zero SJ count: {sj['total_errors']}")
            for e in sj["errors"][:5]:
                print(f"       Triple {e['triple']} (parities {e['parities']}):")
                nz = e['non_zero']
                for gen, val in sorted(nz.items()):
                    print(f"         {gen}: {val}")
        print()

    print(sep)
    if all_pass:
        print("  ✅ ALL CHECKS PASS — Structure constants verified.")
    else:
        print("  ❌ SOME CHECKS FAILED — See details above.")
    print(sep)


def main():
    verbose = "-v" in sys.argv or "--verbose" in sys.argv
    results = []
    for n in [1, 2, 3]:
        r = run_verification(n, verbose)
        results.append(r)
    print_report(results)


if __name__ == "__main__":
    main()
