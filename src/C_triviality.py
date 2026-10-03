"""
C_triviality.py

Triviality analysis for C(n+1) inhomogeneous deformations.

A deformation gamma is trivial iff there exists an odd linear map f such that
gamma = delta f (as bilinear forms on g).

Using the Schema 2 (symbolic gamma) and Schema 4 (symbolic delta f),
we set up the linear system:
  gamma_{XYZ}(gb) = (delta f)_{XYZ}(phi)

and determine when this system is consistent (has a solution in phi).

For the all-ones gb assignment (from Schema 3), we compare:
  evaluated gamma_{XYZ} vs coboundary (delta f)_{XYZ}

and try to solve for phi values that make them equal.

Outputs a triviality analysis report.
"""

import json
import os
from fractions import Fraction
import sys
sys.path.insert(0, os.path.dirname(__file__))


def load_json(path):
    with open(path) as f:
        return json.load(f)


def build_gamma_matrix(n, gb_values=None):
    """
    Build the gamma matrix: a dict {(X,Y,Z): {gb_label: Fraction}}.
    If gb_values is given, evaluate to {(X,Y,Z): Fraction}.
    """
    gamma_schema = load_json(f"data/C_{n}_gamma.json")
    gamma_list = gamma_schema["inhomogeneous_deformation"]["gamma_coefficients"]

    if gb_values is None:
        # Return symbolic
        result = {}
        for e in gamma_list:
            key = (e["X"], e["Y"], e["Z"])
            result[key] = {lbl: Fraction(c) for lbl, c in e["gamma_coeff"].items()}
        return result
    else:
        # Evaluate
        result = {}
        for e in gamma_list:
            key = (e["X"], e["Y"], e["Z"])
            total = sum(Fraction(c) * gb_values.get(lbl, Fraction(0))
                        for lbl, c in e["gamma_coeff"].items())
            if total != 0:
                result[key] = total
        return result


def build_coboundary_matrix(n):
    """
    Build the coboundary matrix: {(X,Y,Z): {phi_label: Fraction}}.
    """
    cb_schema = load_json(f"data/C_{n}_coboundary.json")
    cb_list = cb_schema["coboundary_coefficients"]
    result = {}
    for e in cb_list:
        key = (e["X"], e["Y"], e["Z"])
        result[key] = {lbl: Fraction(c) for lbl, c in e["coboundary_coeff"].items()}
    return result


def solve_triviality(n, gb_values):
    """
    Given gb values, determine if gamma(gb) is a coboundary.

    We need to solve:  sum_j phi_{i,j} * (delta e_j)(X,Y)[Z] = gamma_XYZ(gb)
    for all (X,Y,Z) simultaneously.

    This is a linear system A * phi_vec = b_vec where:
    - Rows correspond to (X,Y,Z) triples with nonzero gamma or coboundary
    - Columns correspond to phi parameters
    - A[row, col] = coefficient of phi_col in (delta f)_{row}
    - b[row] = evaluated gamma_{row}

    Returns (is_consistent, solution, null_space_dim, report_str)
    """
    gamma_eval = build_gamma_matrix(n, gb_values)
    coboundary = build_coboundary_matrix(n)

    # Collect all (X,Y,Z) that appear in either
    all_keys = set(list(gamma_eval.keys()) + list(coboundary.keys()))

    # Collect all phi parameters
    phi_params = set()
    for phi_dict in coboundary.values():
        phi_params.update(phi_dict.keys())
    phi_params = sorted(phi_params)
    phi_idx = {p: i for i, p in enumerate(phi_params)}

    n_phi = len(phi_params)

    # Build the system A * phi = b
    # For each row (X,Y,Z): A[row] = coboundary coefficients, b[row] = gamma value
    rows = []
    b_vals = []
    for key in sorted(all_keys):
        cb_row = coboundary.get(key, {})
        gamma_val = gamma_eval.get(key, Fraction(0))

        row = [Fraction(0)] * n_phi
        for lbl, c in cb_row.items():
            row[phi_idx[lbl]] = c
        rows.append(row)
        b_vals.append(gamma_val)

    # Solve using Gaussian elimination over Q
    n_rows = len(rows)

    if n_phi == 0 or n_rows == 0:
        return True, {}, 0, "Trivial case: no parameters."

    # Augmented matrix [A | b]
    M = [row[:] + [b_vals[i]] for i, row in enumerate(rows)]

    # Gaussian elimination
    pivot_cols = []
    row_ptr = 0
    for col in range(n_phi):
        # Find pivot
        pivot_row = None
        for r in range(row_ptr, n_rows):
            if M[r][col] != 0:
                pivot_row = r
                break
        if pivot_row is None:
            continue

        M[row_ptr], M[pivot_row] = M[pivot_row], M[row_ptr]
        pivot_val = M[row_ptr][col]
        M[row_ptr] = [x / pivot_val for x in M[row_ptr]]
        pivot_cols.append(col)

        for r in range(n_rows):
            if r != row_ptr and M[r][col] != 0:
                factor = M[r][col]
                M[r] = [M[r][j] - factor * M[row_ptr][j] for j in range(n_phi + 1)]

        row_ptr += 1

    # Check consistency: any row with all-zero A but nonzero b?
    inconsistent_rows = []
    for r in range(n_rows):
        if all(M[r][c] == 0 for c in range(n_phi)) and M[r][n_phi] != 0:
            inconsistent_rows.append(r)

    is_consistent = len(inconsistent_rows) == 0
    rank = len(pivot_cols)
    null_dim = n_phi - rank

    # Extract solution (set free variables to 0)
    solution = {}
    free_vars = [c for c in range(n_phi) if c not in pivot_cols]
    if is_consistent:
        for i, col in enumerate(pivot_cols):
            solution[phi_params[col]] = M[i][n_phi]

    # Find the specific inconsistent triples
    inconsistent_triples = []
    sorted_keys = sorted(all_keys)
    for r in inconsistent_rows[:10]:  # Report first 10
        key = sorted_keys[r]
        gamma_val = gamma_eval.get(key, Fraction(0))
        cb_expr = coboundary.get(key, {})
        inconsistent_triples.append({
            "triple": key,
            "gamma_value": str(gamma_val),
            "coboundary_expr": {k: str(v) for k, v in cb_expr.items()},
        })

    report = {
        "n": n,
        "gb_assignment": {k: str(v) for k, v in gb_values.items()},
        "is_trivial": is_consistent,
        "system_size": f"{n_rows} equations, {n_phi} unknowns",
        "rank": rank,
        "null_space_dim": null_dim,
        "n_inconsistent_rows": len(inconsistent_rows),
        "inconsistent_triples_sample": inconsistent_triples,
        "solution_sample": {k: str(v) for k, v in list(solution.items())[:10]},
    }

    return is_consistent, solution, null_dim, report


def analyze_triviality_conditions(n):
    """
    Perform a systematic triviality analysis for C(n+1).

    1. Test the all-ones gb assignment.
    2. Test the zero gb assignment (trivially trivial).
    3. Test specific sign patterns.
    4. Determine the necessary and sufficient conditions on gb.
    """
    results = []

    # Build gb labels
    gb_labels = []
    for sigma in ["p", "m"]:
        for j in range(1, n + 1):
            for s in ["p", "m"]:
                gb_labels.append(f"gb_{sigma}_{j}_{s}")

    # Test 1: zero gb (undeformed = trivially trivial since gamma=0=delta(0))
    gb_zero = {lbl: Fraction(0) for lbl in gb_labels}
    ok0, sol0, nd0, rep0 = solve_triviality(n, gb_zero)
    results.append(("zero_gb", ok0, rep0))

    # Test 2: all gb = +1
    gb_all_ones = {lbl: Fraction(1) for lbl in gb_labels}
    ok1, sol1, nd1, rep1 = solve_triviality(n, gb_all_ones)
    results.append(("all_ones", ok1, rep1))

    # Test 3: all gb = +1 except gb_p_1_p = 0 (for n>=1)
    gb_partial = {lbl: Fraction(1) for lbl in gb_labels}
    gb_partial[gb_labels[0]] = Fraction(0)
    ok2, sol2, nd2, rep2 = solve_triviality(n, gb_partial)
    results.append(("partial_zero", ok2, rep2))

    # Test 4: gb with sigma=+ and sigma=- components having opposite signs
    gb_antisym = {}
    for lbl in gb_labels:
        if lbl.startswith("gb_p"):
            gb_antisym[lbl] = Fraction(1)
        else:
            gb_antisym[lbl] = Fraction(-1)
    ok3, sol3, nd3, rep3 = solve_triviality(n, gb_antisym)
    results.append(("sigma_antisym", ok3, rep3))

    # Symbolic analysis: determine the space of trivial deformations
    # The deformation gamma(gb) is trivial iff gamma(gb) is in the image of delta.
    # We parametrize gamma linearly in gb and find the conditions.
    symbolic_analysis = symbolic_triviality_conditions(n, gb_labels)

    return results, symbolic_analysis


def symbolic_triviality_conditions(n, gb_labels):
    """
    Find necessary and sufficient conditions on gb for gamma(gb) to be trivial.

    gamma(gb) = sum_lbl gb_lbl * Gamma_lbl  (linear in gb)
    gamma is trivial iff gamma in Im(delta).

    For each gb label, we ask: is Gamma_lbl in Im(delta)?
    If all Gamma_lbl are in Im(delta), then any gb gives a trivial deformation.
    If some Gamma_lbl is NOT in Im(delta), then the condition on gb for triviality
    is that the projection of gamma(gb) onto the complement of Im(delta) vanishes.
    """
    coboundary = build_coboundary_matrix(n)
    gamma_sym = build_gamma_matrix(n)  # symbolic: {(X,Y,Z): {gb: Fraction}}

    # Build the coboundary image: collect all (X,Y,Z,phi_label) pairs
    # Find the image of delta as a subspace of the space of bilinear forms g x g -> g

    # Step 1: Build phi parameter list
    phi_params = set()
    for phi_dict in coboundary.values():
        phi_params.update(phi_dict.keys())
    phi_params = sorted(phi_params)
    phi_idx = {p: i for i, p in enumerate(phi_params)}
    n_phi = len(phi_params)

    # Step 2: Collect all nonzero (X,Y,Z) triples
    all_keys = set(list(gamma_sym.keys()) + list(coboundary.keys()))
    all_keys = sorted(all_keys)
    key_idx = {k: i for i, k in enumerate(all_keys)}
    n_keys = len(all_keys)

    # Step 3: Build the delta matrix D: n_keys x n_phi
    D = [[Fraction(0)] * n_phi for _ in range(n_keys)]
    for key, phi_dict in coboundary.items():
        r = key_idx[key]
        for lbl, c in phi_dict.items():
            c_idx = phi_idx[lbl]
            D[r][c_idx] = c

    # Step 4: Row reduce D to find its image
    D_aug = [row[:] for row in D]
    pivot_rows = []
    pivot_cols = []
    row_ptr = 0
    D_rref = [row[:] for row in D_aug]
    for col in range(n_phi):
        pivot_row = None
        for r in range(row_ptr, n_keys):
            if D_rref[r][col] != 0:
                pivot_row = r
                break
        if pivot_row is None:
            continue
        D_rref[row_ptr], D_rref[pivot_row] = D_rref[pivot_row], D_rref[row_ptr]
        pivot_rows.append(row_ptr)
        pivot_cols.append(col)
        pv = D_rref[row_ptr][col]
        D_rref[row_ptr] = [x / pv for x in D_rref[row_ptr]]
        for r in range(n_keys):
            if r != row_ptr and D_rref[r][col] != 0:
                factor = D_rref[r][col]
                D_rref[r] = [D_rref[r][j] - factor * D_rref[row_ptr][j]
                             for j in range(n_phi)]
        row_ptr += 1

    rank_delta = len(pivot_rows)

    # Step 5: For each gb parameter, check if Gamma_gb is in Im(delta)
    # Gamma_gb: a vector of length n_keys representing the map (X,Y,Z) -> gamma_{XYZ}[gb]
    gb_analysis = {}
    for gb_lbl in gb_labels:
        # Build the vector for this gb parameter
        v = [Fraction(0)] * n_keys
        for key, gb_dict in gamma_sym.items():
            if gb_lbl in gb_dict:
                r = key_idx[key]
                v[r] = gb_dict[gb_lbl]

        # Check if v is in Im(D):  solve D * phi = v
        # Augment and row-reduce [D | v]
        M = [D_rref[i][:] + [v[i]] for i in range(n_keys)]
        # We already have D in RREF; just check if b is in the image
        # Apply same row operations to v using the RREF
        for i, (pr, pc) in enumerate(zip(pivot_rows, pivot_cols)):
            # In the RREF, pivot at (pr, pc) = 1
            # The b-column was not part of RREF; apply row ops
            pass

        # Direct consistency check: extend D by column v and row-reduce
        M_aug = [D[i][:] + [v[i]] for i in range(n_keys)]
        row_ptr2 = 0
        pivs2 = []
        M_work = [row[:] for row in M_aug]
        for col in range(n_phi + 1):
            pr = None
            for r in range(row_ptr2, n_keys):
                if M_work[r][col] != 0:
                    pr = r
                    break
            if pr is None:
                continue
            M_work[row_ptr2], M_work[pr] = M_work[pr], M_work[row_ptr2]
            pivs2.append(col)
            pv = M_work[row_ptr2][col]
            M_work[row_ptr2] = [x / pv for x in M_work[row_ptr2]]
            for r in range(n_keys):
                if r != row_ptr2 and M_work[r][col] != 0:
                    factor = M_work[r][col]
                    M_work[r] = [M_work[r][j] - factor * M_work[row_ptr2][j]
                                 for j in range(n_phi + 1)]
            row_ptr2 += 1

        # Check: any row with zero in first n_phi cols but nonzero in last col?
        in_image = all(
            not (all(M_work[r][c] == 0 for c in range(n_phi)) and M_work[r][n_phi] != 0)
            for r in range(n_keys)
        )
        gb_analysis[gb_lbl] = {
            "in_image_of_delta": in_image,
            "nonzero_entries": sum(1 for key in all_keys
                                   if gb_lbl in gamma_sym.get(key, {})),
        }

    # Count: how many gb parameters produce deformations NOT in Im(delta)?
    obstructions = [lbl for lbl, info in gb_analysis.items()
                    if not info["in_image_of_delta"]]

    return {
        "rank_of_delta": rank_delta,
        "n_phi_params": n_phi,
        "n_gb_params": len(gb_labels),
        "gb_analysis": {lbl: {"in_image": info["in_image_of_delta"],
                               "nonzero_entries": info["nonzero_entries"]}
                        for lbl, info in gb_analysis.items()},
        "obstruction_parameters": obstructions,
        "n_obstructions": len(obstructions),
        "triviality_condition": (
            "Deformation is trivial iff gb parameters in obstruction_parameters are all zero"
            if obstructions else
            "All deformations are trivial (all Gamma_gb in Im(delta))"
        ),
    }


def main():
    os.makedirs("data", exist_ok=True)

    full_report = {}
    for n in [1, 2, 3]:
        print(f"\n{'='*60}")
        print(f"Triviality analysis for C({n+1}) = osp(2|{2*n}), n={n}")
        print(f"{'='*60}")

        # Build gb labels
        gb_labels = []
        for sigma in ["p", "m"]:
            for j in range(1, n + 1):
                for s in ["p", "m"]:
                    gb_labels.append(f"gb_{sigma}_{j}_{s}")

        results, symbolic = analyze_triviality_conditions(n)

        print(f"\nSymbolic analysis:")
        print(f"  Rank of delta: {symbolic['rank_of_delta']}")
        print(f"  Phi parameters: {symbolic['n_phi_params']}")
        print(f"  Obstruction parameters: {symbolic['obstruction_parameters']}")
        print(f"  Triviality condition: {symbolic['triviality_condition']}")

        print(f"\nNumerical tests:")
        for profile, is_trivial, rep in results:
            print(f"  {profile}: {'TRIVIAL' if is_trivial else 'NON-TRIVIAL'} "
                  f"(rank={rep['rank']}, inconsistent={rep['n_inconsistent_rows']})")
            if not is_trivial and rep['inconsistent_triples_sample']:
                sample = rep['inconsistent_triples_sample'][0]
                print(f"    Sample failure: gamma{sample['triple']} = {sample['gamma_value']}")
                print(f"    Coboundary: {sample['coboundary_expr']}")

        full_report[f"C_{n+1}"] = {
            "n": n,
            "symbolic_analysis": symbolic,
            "numerical_tests": [
                {
                    "profile": profile,
                    "is_trivial": is_trivial,
                    "rank": rep["rank"],
                    "n_inconsistent": rep["n_inconsistent_rows"],
                    "system_size": rep["system_size"],
                }
                for profile, is_trivial, rep in results
            ],
        }

    # Save full report
    outfile = "data/triviality_report.json"
    with open(outfile, "w") as f:
        json.dump(full_report, f, indent=2)
    print(f"\nFull report saved to {outfile}")
    return full_report


if __name__ == "__main__":
    main()
