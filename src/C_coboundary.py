"""C_coboundary.py — Schema 4 (Coboundary / triviality analysis) for C(n+1) = osp(2|2n).

Implements rank-based triviality verification of the inhomogeneous deformation γ
by checking whether γ is in the image of the coboundary operator δ on odd linear maps
f: g → g (parity-reversing).

Coboundary formula (C_coboundary_definition.md):
    (δf)(X, Y) = (-1)^{p(X)} [X, f(Y)] - (-1)^{(p(X)+1)p(Y)} [Y, f(X)] - f([X,Y])

Here [·,·] is the undeformed bracket (Schema 1).

Rank test (exact Q arithmetic via Python Fraction):
    γ is a coboundary  ⟺  rank(M) == rank([M|γ])
    where M_{(X,Y,Z),φ_{ij}} = ∂/∂φ_{ij} (δf_{ij})(X,Y) · e_Z
"""

import json
import os
from fractions import Fraction
from datetime import date
from typing import Dict, List, Tuple, Optional


# ---------------------------------------------------------------------------
# Data loading
# ---------------------------------------------------------------------------

def load_schema1(n: int):
    """Load basis, parities, structure constants from Schema 1."""
    with open(f"data/C_{n}_structure.json") as fh:
        s1 = json.load(fh)

    odd_basis  = s1["basis"]["odd"]
    even_basis = s1["basis"]["even"]
    all_basis  = odd_basis + even_basis          # PBW order: odd first, then even

    parities = {k: int(v) for k, v in s1["parity"].items()}

    # SC lookup: (X, Y) → {Z: Fraction}  (only X ≤ Y in PBW order)
    sc: Dict[Tuple[str, str], Dict[str, Fraction]] = {}
    for entry in s1["structure_constants"]:
        key = (entry["X"], entry["Y"])
        sc.setdefault(key, {})[entry["Z"]] = Fraction(entry["coeff"])

    return s1, all_basis, parities, sc


def load_gamma_gb1(n: int) -> Dict[Tuple[str, str, str], Fraction]:
    """Load the γ vector (kappa entries) from Schema 3 gb1."""
    with open(f"data/C_{n}_evaluated_gb1.json") as fh:
        s3 = json.load(fh)
    gamma = {}
    for entry in s3["evaluated_structure_constants"]:
        if entry["part"] == "kappa":
            key = (entry["X"], entry["Y"], entry["Z"])
            gamma[key] = Fraction(entry["coeff"])
    return gamma


# ---------------------------------------------------------------------------
# Bracket helper
# ---------------------------------------------------------------------------

def make_bracket(all_basis: List[str], parities: dict, sc: dict):
    """Return a bracket(A, B) → {Z: Fraction} closure."""
    idx = {label: i for i, label in enumerate(all_basis)}

    def bracket(A: str, B: str) -> Dict[str, Fraction]:
        ia, ib = idx[A], idx[B]
        if ia <= ib:
            return dict(sc.get((A, B), {}))
        # [A, B] = -(-1)^{p(A)*p(B)} * [B, A]
        raw = sc.get((B, A), {})
        sign = 1 if (parities[A] == 1 and parities[B] == 1) else -1
        return {z: Fraction(sign) * c for z, c in raw.items()}

    return bracket


# ---------------------------------------------------------------------------
# Build coboundary matrix (sparse)
# ---------------------------------------------------------------------------

def build_system(n: int):
    """
    Build the sparse coboundary operator matrix M and γ vector.

    Returns:
        row_dict  : {(X,Y,Z): {col_idx: Fraction}}  — rows of M
        f_params  : list[(i_label, j_label)]         — column index
        n_cols    : int                              — number of f parameters
        gamma_vec : {(X,Y,Z): Fraction}              — target vector
    """
    s1, all_basis, parities, sc = load_schema1(n)
    gamma_vec = load_gamma_gb1(n)
    bracket   = make_bracket(all_basis, parities, sc)

    # f parameterisation: φ_{ij} — maps Z_j → Z_i  (parity-reversing)
    f_params = [(i, j) for i in all_basis for j in all_basis
                if parities[i] != parities[j]]
    col_idx  = {p: k for k, p in enumerate(f_params)}
    n_cols   = len(f_params)

    row_dict: Dict[Tuple[str, str, str], Dict[int, Fraction]] = {}

    def add(X, Y, Z, col, val):
        if val == 0:
            return
        d = row_dict.setdefault((X, Y, Z), {})
        d[col] = d.get(col, Fraction(0)) + val

    for a, X in enumerate(all_basis):
        pX = parities[X]
        for b in range(a, len(all_basis)):
            Y = all_basis[b]
            pY = parities[Y]

            # ---- Term 1: (-1)^pX * [X, Z_i]  where Y acts as Z_j ----
            # col = (i_label, Y),  Z from [X, i_label]
            fac1 = Fraction((-1) ** pX)
            for i_label in all_basis:
                if parities[i_label] == parities[Y]:
                    continue
                c = col_idx.get((i_label, Y))
                if c is None:
                    continue
                for Z, coeff in bracket(X, i_label).items():
                    add(X, Y, Z, c, fac1 * coeff)

            # ---- Term 2: -(-1)^{(pX+1)*pY} * [Y, Z_i]  where X acts as Z_j ----
            # col = (i_label, X),  Z from [Y, i_label]
            fac2 = Fraction(-(-1) ** ((pX + 1) * pY))
            for i_label in all_basis:
                if parities[i_label] == parities[X]:
                    continue
                c = col_idx.get((i_label, X))
                if c is None:
                    continue
                for Z, coeff in bracket(Y, i_label).items():
                    add(X, Y, Z, c, fac2 * coeff)

            # ---- Term 3: -(SC(X,Y)[Z_j]) * Z_i ----
            # col = (i_label, j_label),  row = (X, Y, i_label)
            for j_label, ck in bracket(X, Y).items():
                for i_label in all_basis:
                    if parities[i_label] == parities[j_label]:
                        continue
                    c = col_idx.get((i_label, j_label))
                    if c is None:
                        continue
                    add(X, Y, i_label, c, -ck)

    # Remove zero entries
    row_dict = {k: {c: v for c, v in r.items() if v != 0}
                for k, r in row_dict.items()}
    row_dict = {k: r for k, r in row_dict.items() if r}

    return row_dict, f_params, n_cols, gamma_vec


# ---------------------------------------------------------------------------
# Gaussian elimination (RREF over Q, sparse rows as dicts)
# ---------------------------------------------------------------------------

def gauss_rref(rows: List[Dict[int, Fraction]], n_cols: int):
    """
    Full RREF on an augmented matrix represented as sparse row-dicts.
    Column n_cols is the RHS.

    Returns (rows_rref, pivot_cols) where pivot_cols[k] is the pivot column
    for the k-th pivot row (rows_rref[k]).
    """
    rows = [dict(r) for r in rows]
    n = len(rows)
    pivot_cols: List[int] = []
    current_row = 0

    for col in range(n_cols + 1):
        # Find a row with a non-zero entry in this column
        pivot_r = next((r for r in range(current_row, n)
                        if rows[r].get(col, Fraction(0)) != 0), None)
        if pivot_r is None:
            continue

        rows[current_row], rows[pivot_r] = rows[pivot_r], rows[current_row]
        piv = rows[current_row][col]

        # Normalise the pivot row
        rows[current_row] = {c: v / piv for c, v in rows[current_row].items()}

        # Eliminate this column from ALL other rows (full RREF)
        for r in range(n):
            if r == current_row:
                continue
            factor = rows[r].get(col, Fraction(0))
            if factor == 0:
                continue
            new_row = dict(rows[r])
            for c, v in rows[current_row].items():
                new_row[c] = new_row.get(c, Fraction(0)) - factor * v
            rows[r] = {c: v for c, v in new_row.items() if v != 0}

        pivot_cols.append(col)
        current_row += 1
        if current_row >= n:
            break

    return rows, pivot_cols


# ---------------------------------------------------------------------------
# Rank test and solution extraction
# ---------------------------------------------------------------------------

def rank_test(row_dict, n_cols, gamma_vec):
    """
    Test if γ ∈ col(M) over Q.

    Returns (rank_M, rank_aug, solution) where solution is a dict
    {col_idx: Fraction} (setting free variables = 0) when consistent,
    else None.
    """
    RHS = n_cols

    all_keys = set(row_dict.keys()) | set(gamma_vec.keys())

    aug_rows = []
    for key in all_keys:
        row = dict(row_dict.get(key, {}))
        rhs_val = gamma_vec.get(key, Fraction(0))
        if rhs_val != 0:
            row[RHS] = rhs_val
        if row:
            aug_rows.append(row)

    if not aug_rows:
        return 0, 0, {}

    rows_rref, pivot_cols = gauss_rref(aug_rows, n_cols)

    rank_M   = sum(1 for c in pivot_cols if c < n_cols)
    rank_aug = len(pivot_cols)

    is_consistent = (rank_M == rank_aug)

    solution = None
    if is_consistent:
        solution = {}
        # After RREF, rows_rref[k] has its leading 1 at pivot_cols[k].
        for k, pc in enumerate(pivot_cols):
            if pc < n_cols:
                # Set free variables = 0: solution[pc] = RHS value of this row
                solution[pc] = rows_rref[k].get(RHS, Fraction(0))
        for col in range(n_cols):
            if col not in solution:
                solution[col] = Fraction(0)

    return rank_M, rank_aug, solution


# ---------------------------------------------------------------------------
# Verification
# ---------------------------------------------------------------------------

def verify_solution(row_dict, gamma_vec, n_cols, solution):
    """Verify that M·φ = γ for the given solution. Returns True if exact."""
    RHS = n_cols
    all_keys = set(row_dict.keys()) | set(gamma_vec.keys())
    for key in all_keys:
        lhs = sum(row_dict.get(key, {}).get(c, Fraction(0)) * solution[c]
                  for c in range(n_cols))
        rhs = gamma_vec.get(key, Fraction(0))
        if lhs != rhs:
            return False
    return True


# ---------------------------------------------------------------------------
# Schema 4 builder
# ---------------------------------------------------------------------------

def build_schema4(n: int) -> dict:
    print(f"  Building coboundary system for n={n}...")
    row_dict, f_params, n_cols, gamma_vec = build_system(n)

    with open(f"data/C_{n}_structure.json") as fh:
        s1 = json.load(fh)

    print(f"  M: {len(row_dict)} rows × {n_cols} cols | γ: {len(gamma_vec)} entries")

    rank_M, rank_aug, solution = rank_test(row_dict, n_cols, gamma_vec)
    is_coboundary = (rank_M == rank_aug)

    alg   = s1["algebra"]
    n_val = alg["n"]

    if is_coboundary:
        conclusion = (
            f"The gb1 deformation gamma is a COBOUNDARY in H^2(g;g). "
            f"The inhomogeneous deformation of C({n_val+1}) = osp(2|{2*n_val}) "
            f"with all gb=1 is TRIVIAL (equivalent to the undeformed algebra by a "
            f"change of basis)."
        )
    else:
        conclusion = (
            f"The gb1 deformation gamma is NOT a coboundary in H^2(g;g). "
            f"The inhomogeneous deformation of C({n_val+1}) = osp(2|{2*n_val}) "
            f"with all gb=1 is NON-TRIVIAL (a genuinely new algebra)."
        )

    # Verify solution (if trivial)
    verified = False
    if is_coboundary and solution is not None:
        verified = verify_solution(row_dict, gamma_vec, n_cols, solution)
        if verified:
            print(f"  ✓ Solution verified: M·φ = γ holds exactly")
        else:
            print(f"  ✗ Solution verification FAILED")

    # Build explicit_f entry list
    explicit_f = None
    if is_coboundary and solution is not None:
        nonzero = []
        for col_idx, phi_val in sorted(solution.items()):
            if phi_val != 0:
                i_label, j_label = f_params[col_idx]
                nonzero.append({
                    "from": j_label,
                    "to":   i_label,
                    "coeff": str(phi_val),
                })
        explicit_f = {
            "description": (
                "f(Z_j) = sum_i phi_{ij} * Z_i; "
                "each entry means f(from) has a nonzero component along 'to'"
            ),
            "solution_verified": verified,
            "nonzero_count": len(nonzero),
            "entries": nonzero,
        }

    schema = {
        "schema_version": "5.0",
        "schema_layer": 4,
        "algebra": alg,
        "gb_assignment": {
            "profile": "gb1",
            "description": f"All {4*n_val} gb parameters set to 1",
        },
        "coboundary_analysis": {
            "coboundary_formula": (
                "(-1)^{p(X)} [X,f(Y)] - (-1)^{(p(X)+1)p(Y)} [Y,f(X)] - f([X,Y])"
            ),
            "f_space": "full space of parity-reversing odd linear maps g → g",
            "f_parameter_count": n_cols,
            "coboundary_operator_rows": len(row_dict),
            "rank_coboundary_operator": rank_M,
            "rank_augmented_matrix": rank_aug,
            "is_coboundary": is_coboundary,
            "conclusion": conclusion,
        },
        "metadata": {
            "generated_by": "C_coboundary.py",
            "generation_date": date.today().isoformat(),
            "issue": "I07-1",
            "source_schema1": f"C_{n}_structure.json",
            "source_schema3": f"C_{n}_evaluated_gb1.json",
            "references": ["docs/math/C_coboundary_definition.md"],
        },
    }

    if explicit_f is not None:
        schema["explicit_f"] = explicit_f

    return schema


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    os.makedirs("data", exist_ok=True)

    results = {}
    for n in (1, 2, 3):
        print(f"\n{'='*60}")
        print(f"C({n+1}) = osp(2|{2*n}),  n={n}")
        print(f"{'='*60}")
        schema = build_schema4(n)
        path   = f"data/C_{n}_coboundary_gb1.json"
        with open(path, "w") as fh:
            json.dump(schema, fh, indent=2)
        ca = schema["coboundary_analysis"]
        results[n] = {
            "algebra":     f"C({n+1}) = osp(2|{2*n})",
            "rank_M":      ca["rank_coboundary_operator"],
            "rank_aug":    ca["rank_augmented_matrix"],
            "is_coboundary": ca["is_coboundary"],
        }
        verdict = "TRIVIAL (coboundary)" if ca["is_coboundary"] else "NON-TRIVIAL"
        print(f"  rank(M) = {ca['rank_coboundary_operator']}, "
              f"rank([M|γ]) = {ca['rank_augmented_matrix']}")
        print(f"  → {verdict}")
        print(f"  → written to {path}")

    print("\n\n" + "="*60)
    print("DEFINITIVE MATHEMATICAL CONCLUSION")
    print("="*60)
    for n, r in results.items():
        verdict = "TRIVIAL" if r["is_coboundary"] else "NON-TRIVIAL"
        print(f"  {r['algebra']:30s}  {verdict:20s}  "
              f"(rank_M={r['rank_M']}, rank_aug={r['rank_aug']})")
    print("="*60)


if __name__ == "__main__":
    main()
