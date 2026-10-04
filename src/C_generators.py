"""C(n+1) = osp(2|2n) Lie superalgebra generator and structure constants builder.

Implements Schema 1 structure for n=1, 2, 3 following:
- handover/notation.md
- docs/json_schema_specification.md
- docs/math/Cn1_definition.md
"""

import json
from collections import defaultdict
from fractions import Fraction
from pathlib import Path


def solve_exact_linear(M, b):
    """Solve M x = b exactly using Gaussian elimination over Fraction."""
    nrows = len(M)
    ncols = len(M[0])
    A = [list(row) + [b[i]] for i, row in enumerate(M)]
    row = 0
    pivots = []
    for col in range(ncols):
        p = None
        for r in range(row, nrows):
            if A[r][col] != 0:
                p = r
                break
        if p is None:
            continue
        A[row], A[p] = A[p], A[row]
        pivot_val = A[row][col]
        for c in range(col, ncols + 1):
            A[row][c] /= pivot_val
        for r in range(nrows):
            if r != row and A[r][col] != 0:
                factor = A[r][col]
                for c in range(col, ncols + 1):
                    A[r][c] -= factor * A[row][c]
        pivots.append((row, col))
        row += 1
    for r in range(row, nrows):
        if A[r][-1] != 0:
            raise ValueError(f"Inconsistent linear system for row {r}: {A[r][-1]}")
    x = [Fraction(0)] * ncols
    for r, c in pivots:
        x[c] = A[r][-1]
    return x


def reduce_word(word):
    """Normal-orders an oscillator word using CAR and CCR.
    
    Fermionic CAR: {a_1^-, a_1^+} = 1, (a_1^+)^2 = (a_1^-)^2 = 0.
    Bosonic CCR: [b_k^-, b_k^+] = 1, all other commutators = 0.
    Normal order: a_1^+, a_1^-, then b_k^+, b_k^- for k=1..n.
    """
    current = [(Fraction(1), list(word))]

    def rank(tok):
        if tok[0] == "a_p":
            return (0, 0)
        if tok[0] == "a_m":
            return (0, 1)
        if tok[0] == "b_p":
            return (1, tok[1], 0)
        if tok[0] == "b_m":
            return (1, tok[1], 1)
        raise ValueError(f"Unknown token: {tok}")

    while True:
        rewritten = False
        next_gen = []
        for coeff, w in current:
            # Check adjacent fermion nilpotency
            killed = False
            for i in range(len(w) - 1):
                if w[i] == w[i + 1] and w[i][0] in ("a_p", "a_m"):
                    killed = True
                    break
            if killed:
                continue

            for i in range(len(w) - 1):
                t1, t2 = w[i], w[i + 1]
                if rank(t1) > rank(t2):
                    rewritten = True
                    prefix = w[:i]
                    suffix = w[i + 2:]
                    if t1 == ("a_m",) and t2 == ("a_p",):
                        next_gen.append((coeff, prefix + suffix))
                        next_gen.append((-coeff, prefix + [t2, t1] + suffix))
                    elif t1[0] == "b_m" and t2[0] == "b_p" and t1[1] == t2[1]:
                        next_gen.append((coeff, prefix + suffix))
                        next_gen.append((coeff, prefix + [t2, t1] + suffix))
                    else:
                        next_gen.append((coeff, prefix + [t2, t1] + suffix))
                    break
            else:
                next_gen.append((coeff, w))
        current = next_gen
        if not rewritten:
            break

    res = defaultdict(Fraction)
    for c, w in current:
        if w.count(("a_p",)) <= 1 and w.count(("a_m",)) <= 1:
            res[tuple(w)] += c
    return {k: v for k, v in res.items() if v != 0}


def mul_expr(e1, e2):
    """Multiplies two oscillator expressions and normal orders the result."""
    res = defaultdict(Fraction)
    for w1, c1 in e1.items():
        for w2, c2 in e2.items():
            r = reduce_word(list(w1) + list(w2))
            for rw, rc in r.items():
                res[rw] += c1 * c2 * rc
    return {k: v for k, v in res.items() if v != 0}


def bracket(X, pX, Y, pY):
    """Computes the graded Lie bracket [X, Y} = XY - (-1)^(pX pY) YX."""
    sign = -1 if (pX * pY == 1) else 1
    xy = mul_expr(X, Y)
    yx = mul_expr(Y, X)
    res = defaultdict(Fraction)
    for w, c in xy.items():
        res[w] += c
    for w, c in yx.items():
        res[w] -= sign * c
    return {k: v for k, v in res.items() if v != 0}


def build_c_algebra(n):
    """Builds the complete C(n+1) basis, parities, and generator realizations."""
    # Basis lists according to Option 1 PBW ordering in notation.md
    even_basis = [f"H_{k}" for k in range(1, n + 2)]
    # Positive long roots
    even_basis += [f"E_2del{k}_p" for k in range(1, n + 1)]
    # Positive cross roots
    for i in range(1, n + 1):
        for j in range(i + 1, n + 1):
            even_basis.append(f"E_del{i}_del{j}_pp")
    # Negative long roots
    even_basis += [f"E_2del{k}_m" for k in range(1, n + 1)]
    # Negative cross roots
    for i in range(1, n + 1):
        for j in range(i + 1, n + 1):
            even_basis.append(f"E_del{i}_del{j}_mm")
    # Mixed cross roots
    for i in range(1, n + 1):
        for j in range(i + 1, n + 1):
            even_basis.append(f"E_del{i}_del{j}_pm")
            even_basis.append(f"E_del{i}_del{j}_mp")

    # Odd basis: pp, pm, mp, mm
    odd_basis = []
    for k in range(1, n + 1):
        odd_basis.append(f"E_eps1_del{k}_pp")
    for k in range(1, n + 1):
        odd_basis.append(f"E_eps1_del{k}_pm")
    for k in range(1, n + 1):
        odd_basis.append(f"E_eps1_del{k}_mp")
    for k in range(1, n + 1):
        odd_basis.append(f"E_eps1_del{k}_mm")

    parities = {}
    for g in even_basis:
        parities[g] = 0
    for g in odd_basis:
        parities[g] = 1

    gens = {}
    realizations = {}

    # H_1 = a_1^+ a_1^- + b_1^+ b_1^-
    gens["H_1"] = {(("a_p",), ("a_m",)): Fraction(1), (("b_p", 1), ("b_m", 1)): Fraction(1)}
    realizations["H_1"] = {
        "standard_form": [
            {"words": ["a_1_p", "a_1_m"], "coeff": "1"},
            {"words": ["b_1_p", "b_1_m"], "coeff": "1"},
        ],
        "frappat_form": "a_1^+ a_1^- + b_1^+ b_1^-",
        "parity": 0,
    }

    # H_k = b_{k-1}^+ b_{k-1}^- - b_k^+ b_k^- (2 <= k <= n)
    for k in range(2, n + 1):
        gens[f"H_{k}"] = {(("b_p", k - 1), ("b_m", k - 1)): Fraction(1), (("b_p", k), ("b_m", k)): Fraction(-1)}
        realizations[f"H_{k}"] = {
            "standard_form": [
                {"words": [f"b_{k-1}_p", f"b_{k-1}_m"], "coeff": "1"},
                {"words": [f"b_{k}_p", f"b_{k}_m"], "coeff": "-1"},
            ],
            "frappat_form": f"b_{k-1}^+ b_{k-1}^- - b_{k}^+ b_{k}^-",
            "parity": 0,
        }

    # H_{n+1} = -b_n^+ b_n^- - 1/2
    gens[f"H_{n+1}"] = {(("b_p", n), ("b_m", n)): Fraction(-1), (): Fraction(-1, 2)}
    realizations[f"H_{n+1}"] = {
        "standard_form": [
            {"words": [f"b_{n}_p", f"b_{n}_m"], "coeff": "-1"},
            {"words": [], "coeff": "-1/2"},
        ],
        "frappat_form": f"-b_{n}^+ b_{n}^- - 1/2",
        "parity": 0,
    }

    # Long roots
    for k in range(1, n + 1):
        gens[f"E_2del{k}_p"] = {(("b_p", k), ("b_p", k)): Fraction(1)}
        realizations[f"E_2del{k}_p"] = {
            "standard_form": [{"words": [f"b_{k}_p", f"b_{k}_p"], "coeff": "1"}],
            "frappat_form": f"(b_{k}^+)^2",
            "parity": 0,
        }
        gens[f"E_2del{k}_m"] = {(("b_m", k), ("b_m", k)): Fraction(1)}
        realizations[f"E_2del{k}_m"] = {
            "standard_form": [{"words": [f"b_{k}_m", f"b_{k}_m"], "coeff": "1"}],
            "frappat_form": f"(b_{k}^-)^2",
            "parity": 0,
        }

    # Cross roots
    for i in range(1, n + 1):
        for j in range(i + 1, n + 1):
            gens[f"E_del{i}_del{j}_pp"] = {(("b_p", i), ("b_p", j)): Fraction(1)}
            realizations[f"E_del{i}_del{j}_pp"] = {
                "standard_form": [{"words": [f"b_{i}_p", f"b_{j}_p"], "coeff": "1"}],
                "frappat_form": f"b_{i}^+ b_{j}^+",
                "parity": 0,
            }
            gens[f"E_del{i}_del{j}_mm"] = {(("b_m", i), ("b_m", j)): Fraction(1)}
            realizations[f"E_del{i}_del{j}_mm"] = {
                "standard_form": [{"words": [f"b_{i}_m", f"b_{j}_m"], "coeff": "1"}],
                "frappat_form": f"b_{i}^- b_{j}^-",
                "parity": 0,
            }
            gens[f"E_del{i}_del{j}_pm"] = {(("b_p", i), ("b_m", j)): Fraction(1)}
            realizations[f"E_del{i}_del{j}_pm"] = {
                "standard_form": [{"words": [f"b_{i}_p", f"b_{j}_m"], "coeff": "1"}],
                "frappat_form": f"b_{i}^+ b_{j}^-",
                "parity": 0,
            }
            gens[f"E_del{i}_del{j}_mp"] = {(("b_m", i), ("b_p", j)): Fraction(1)}
            realizations[f"E_del{i}_del{j}_mp"] = {
                "standard_form": [{"words": [f"b_{i}_m", f"b_{j}_p"], "coeff": "1"}],
                "frappat_form": f"b_{i}^- b_{j}^+",
                "parity": 0,
            }

    # Odd roots
    for k in range(1, n + 1):
        gens[f"E_eps1_del{k}_pp"] = {(("a_p",), ("b_p", k)): Fraction(1)}
        realizations[f"E_eps1_del{k}_pp"] = {
            "standard_form": [{"words": ["a_1_p", f"b_{k}_p"], "coeff": "1"}],
            "frappat_form": f"a_1^+ b_{k}^+",
            "parity": 1,
        }
        gens[f"E_eps1_del{k}_pm"] = {(("a_p",), ("b_m", k)): Fraction(1)}
        realizations[f"E_eps1_del{k}_pm"] = {
            "standard_form": [{"words": ["a_1_p", f"b_{k}_m"], "coeff": "1"}],
            "frappat_form": f"a_1^+ b_{k}^-",
            "parity": 1,
        }
        gens[f"E_eps1_del{k}_mp"] = {(("a_m",), ("b_p", k)): Fraction(1)}
        realizations[f"E_eps1_del{k}_mp"] = {
            "standard_form": [{"words": ["a_1_m", f"b_{k}_p"], "coeff": "1"}],
            "frappat_form": f"a_1^- b_{k}^+",
            "parity": 1,
        }
        gens[f"E_eps1_del{k}_mm"] = {(("a_m",), ("b_m", k)): Fraction(1)}
        realizations[f"E_eps1_del{k}_mm"] = {
            "standard_form": [{"words": ["a_1_m", f"b_{k}_m"], "coeff": "1"}],
            "frappat_form": f"a_1^- b_{k}^-",
            "parity": 1,
        }

    return even_basis, odd_basis, parities, gens, realizations


def compute_structure_constants(n):
    """Computes all non-zero graded structure constants for C(n+1)."""
    even_basis, odd_basis, parities, gens, realizations = build_c_algebra(n)
    all_gens = odd_basis + even_basis  # PBW: kappa < odd < even
    gen_index = {g: idx for idx, g in enumerate(all_gens)}

    cartan_names = [f"H_{k}" for k in range(1, n + 2)]
    mono_to_root = {}
    for g, expr in gens.items():
        if not g.startswith("H_"):
            m = list(expr.keys())[0]
            mono_to_root[m] = g

    diag_monos = sorted(list(set(m for c in cartan_names for m in gens[c].keys())))
    M = []
    for m in diag_monos:
        row = [gens[cname].get(m, Fraction(0)) for cname in cartan_names]
        M.append(row)

    def decompose(expr):
        coeffs = defaultdict(Fraction)
        diag_vec = [Fraction(0)] * len(diag_monos)
        has_diag = False
        for m, c in expr.items():
            if m in mono_to_root:
                coeffs[mono_to_root[m]] += c
            elif m in diag_monos:
                has_diag = True
                diag_vec[diag_monos.index(m)] = c
            else:
                raise ValueError(f"Unknown monomial {m} encountered in bracket")
        if has_diag:
            sol = solve_exact_linear(M, diag_vec)
            for j, cname in enumerate(cartan_names):
                if sol[j] != 0:
                    coeffs[cname] += sol[j]
        return {k: v for k, v in coeffs.items() if v != 0}

    structure_constants = []
    for g1 in all_gens:
        for g2 in all_gens:
            br = bracket(gens[g1], parities[g1], gens[g2], parities[g2])
            dec = decompose(br)
            for g3 in all_gens:
                if g3 in dec:
                    coeff_frac = dec[g3]
                    coeff_str = str(coeff_frac.numerator) if coeff_frac.denominator == 1 else f"{coeff_frac.numerator}/{coeff_frac.denominator}"
                    structure_constants.append({
                        "X": g1,
                        "Y": g2,
                        "Z": g3,
                        "coeff": coeff_str,
                        "sign_rule": "graded",
                    })

    return even_basis, odd_basis, parities, realizations, structure_constants


def generate_schema1_json(n, output_path):
    """Generates Schema 1 JSON file for C(n+1)."""
    even_basis, odd_basis, parities, realizations, structure_constants = compute_structure_constants(n)

    dim_even = 2 * n * n + n + 1
    dim_odd = 4 * n
    dim_total = 2 * n * n + 5 * n + 1

    boson_labels = []
    for k in range(1, n + 1):
        boson_labels.append(f"b_{k}_p")
        boson_labels.append(f"b_{k}_m")

    ordering_str = "a_1_p, a_1_m, " + ", ".join(boson_labels)

    data = {
        "schema_version": "5.0",
        "algebra": {
            "family": "C",
            "m": 1,
            "n": n,
            "cartan_type": f"C({n+1})",
            "alternative_notation": {
                "osp": f"osp(2|{2*n})",
                "dimension_formula": "osp(2m|2n) with m=1",
            },
            "dimension": {
                "total": dim_total,
                "even": dim_even,
                "odd": dim_odd,
                "formulas": {
                    "even": "2n^2 + n + 1",
                    "odd": "4n",
                    "total": "2n^2 + 5n + 1",
                },
            },
        },
        "central_elements": {
            "kappa": {
                "label": "kappa",
                "parity": 1,
                "nilpotency": "kappa^2 = 0",
                "description": "Odd central extension element parameterizing inhomogeneous deformation",
            },
            "K": {
                "label": "K",
                "parity": 0,
                "description": "Even central element identified with scalar identity 1",
            },
        },
        "oscillator_generators": {
            "fermions": {
                "m": 1,
                "count": 2,
                "labels": ["a_1_p", "a_1_m"],
                "description": "Standard fermionic CAR pair a_1^±",
            },
            "bosons": {
                "n": n,
                "count": 2 * n,
                "labels": boson_labels,
                "description": "Bosonic oscillators b_i^± with i=1,...,n",
            },
        },
        "oscillator_relations": {
            "standard_fermion_anticommutators": {
                "description": "Canonical anticommutation relations (CAR) for fermionic pair",
                "relations": {
                    "anticommutator": "{a_1^-, a_1^+} = 1",
                    "nilpotency": "(a_1^+)^2 = (a_1^-)^2 = 0",
                },
            },
            "bosonic_commutators": {
                "description": "Canonical commutation relations (CCR) for bosonic oscillators",
                "relations": {
                    "same_type": "[b_i^±, b_j^±] = 0 for all i, j",
                    "conjugate_pair": "[b_i^-, b_j^+] = delta_{ij}",
                },
            },
            "mixed_commutators": {
                "boson_fermion": "[b_i^±, a_1^±] = 0 (undeformed)",
            },
        },
        "basis": {
            "even": even_basis,
            "odd": odd_basis,
            "ordering_convention": "PBW: kappa < [odd: E_eps1_del{k}_pp/pm/mp/mm] < [even: H_k, E_2del{k}_p/m, E_del{i}_del{j}_pp/mm/pm/mp]",
        },
        "parity": parities,
        "generator_realization": {
            "description": "Standard form with PBW ordering",
            "ordering": ordering_str,
            "realizations": realizations,
        },
        "structure_constants": structure_constants,
        "metadata": {
            "generated_by": "src/C_generators.py",
            "generation_date": "2026-10-04",
            "references": [
                "Frappat et al. (2000), Dictionary on Lie Algebras and Superalgebras",
                "docs/math/Cn1_definition.md",
            ],
        },
    }

    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

    return data


def main():
    for n in [1, 2, 3]:
        out = f"data/C_{n}_structure.json"
        print(f"Generating {out}...")
        generate_schema1_json(n, out)
        print(f"Generated {out} successfully.")


if __name__ == "__main__":
    main()
