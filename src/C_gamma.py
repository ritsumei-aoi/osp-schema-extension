"""Schema 2: Inhomogeneous deformation (gamma structure) generator for C(n+1).

Implements:
1. gb_matrix definition (size 2 x 2n) for fermionic pair (a_1_p, a_1_m) and bosonic oscillators.
2. Computation of symbolic gamma coefficients gamma_{abc}(gb) from the deformed oscillator bracket:
   [b_j^s, a_1^sigma] = - gb_{sigma, j, s} * kappa.
3. Generation of Schema 2 JSON files: data/C_{n}_gamma.json for n=1, 2, 3.
"""

from collections import defaultdict
from fractions import Fraction
import json
from pathlib import Path
import sys

# Ensure repo root is on sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.C_generators import build_c_algebra, solve_exact_linear



def gb_label(sigma_tok, boson_tok):
    sig_str = "a1_p" if sigma_tok[0] == "a_p" else "a1_m"
    bos_str = f"b{boson_tok[1]}_p" if boson_tok[0] == "b_p" else f"b{boson_tok[1]}_m"
    return f"gb_{sig_str}_{bos_str}"


def reduce_word_deformed(word):
    """Normal-orders an oscillator word up to first order in kappa."""
    current = [(Fraction(1), list(word), None)]

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
        for coeff, w, gb in current:
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
                        next_gen.append((coeff, prefix + suffix, gb))
                        next_gen.append((-coeff, prefix + [t2, t1] + suffix, gb))
                    elif t1[0] == "b_m" and t2[0] == "b_p" and t1[1] == t2[1]:
                        next_gen.append((coeff, prefix + suffix, gb))
                        next_gen.append((-coeff, prefix + [t2, t1] + suffix, gb))
                    elif t1[0].startswith("b") and t2[0].startswith("a"):
                        # Exchange relation: [b, a] = - gb * kappa => b a = a b - gb * kappa
                        next_gen.append((coeff, prefix + [t2, t1] + suffix, gb))
                        if gb is None:
                            g_lbl = gb_label(t2, t1)
                            next_gen.append((-coeff, prefix + suffix, g_lbl))
                    else:
                        next_gen.append((coeff, prefix + [t2, t1] + suffix, gb))
                    break
            else:
                next_gen.append((coeff, w, gb))
        current = next_gen
        if not rewritten:
            break

    res = defaultdict(Fraction)
    for c, w, gb in current:
        if w.count(("a_p",)) <= 1 and w.count(("a_m",)) <= 1:
            res[(tuple(w), gb)] += c
    return {k: v for k, v in res.items() if v != 0}


def mul_expr_deformed(e1, e2):
    res = defaultdict(Fraction)
    for w1, c1 in e1.items():
        for w2, c2 in e2.items():
            r = reduce_word_deformed(list(w1) + list(w2))
            for (rw, rgb), rc in r.items():
                res[(rw, rgb)] += c1 * c2 * rc
    return {k: v for k, v in res.items() if v != 0}


def deformed_bracket(X, pX, Y, pY):
    sign = -1 if (pX * pY == 1) else 1
    xy = mul_expr_deformed(X, Y)
    yx = mul_expr_deformed(Y, X)
    res = defaultdict(Fraction)
    for k, c in xy.items():
        res[k] += c
    for k, c in yx.items():
        res[k] -= sign * c
    return {k: v for k, v in res.items() if v != 0}


def compute_gamma_structure(n):
    even_basis, odd_basis, parities, gens, realizations = build_c_algebra(n)
    all_gens = odd_basis + even_basis
    cartan_names = [f"H_{k}" for k in range(1, n + 2)]

    mono_to_root = {}
    for g, expr in gens.items():
        if not g.startswith("H_"):
            m = list(expr.keys())[0]
            mono_to_root[m] = g

    num_monos = [(("a_p",), ("a_m",))] + [(("b_p", k), ("b_m", k)) for k in range(1, n + 1)]
    M_num = [[gens[cname].get(m, Fraction(0)) for cname in cartan_names] for m in num_monos]

    def decompose_g(expr):
        coeffs = defaultdict(Fraction)
        num_vec = [Fraction(0)] * len(num_monos)
        has_num = False
        for m, c in expr.items():
            if m == ():
                continue
            if m in mono_to_root:
                coeffs[mono_to_root[m]] += c
            elif m in num_monos:
                has_num = True
                num_vec[num_monos.index(m)] = c
            else:
                raise ValueError(f"Unknown monomial {m}")
        if has_num:
            sol = solve_exact_linear(M_num, num_vec)
            for j, cname in enumerate(cartan_names):
                if sol[j] != 0:
                    coeffs[cname] += sol[j]
        return {k: v for k, v in coeffs.items() if v != 0}

    gamma_entries = []
    for g1 in all_gens:
        p1 = parities[g1]
        for g2 in all_gens:
            p2 = parities[g2]
            br = deformed_bracket(gens[g1], p1, gens[g2], p2)
            gb_groups = defaultdict(dict)
            for (w, gb), c in br.items():
                if gb is not None:
                    gb_groups[gb][w] = c

            for gb in sorted(gb_groups.keys()):
                dec = decompose_g(gb_groups[gb])
                for g3 in all_gens:
                    if g3 in dec:
                        coeff_frac = dec[g3]
                        coeff_str = str(coeff_frac.numerator) if coeff_frac.denominator == 1 else f"{coeff_frac.numerator}/{coeff_frac.denominator}"
                        gamma_entries.append({
                            "X": g1,
                            "Y": g2,
                            "Z": g3,
                            "gb": gb,
                            "coeff": coeff_str,
                        })

    return even_basis, odd_basis, parities, gamma_entries


def generate_schema2_json(n, output_path):
    even_basis, odd_basis, parities, gamma_entries = compute_gamma_structure(n)

    fermions = ["a_1_p", "a_1_m"]
    bosons = []
    for k in range(1, n + 1):
        bosons.append(f"b_{k}_p")
        bosons.append(f"b_{k}_m")

    # gb matrix 2 x 2n
    matrix_rows = []
    for f in fermions:
        row = []
        sig_str = "a1_p" if f == "a_1_p" else "a1_m"
        for b in bosons:
            b_clean = b.replace("b_", "b")
            row.append(f"gb_{sig_str}_{b_clean}")
        matrix_rows.append(row)


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
                "total": 2 * n * n + 5 * n + 1,
                "even": 2 * n * n + n + 1,
                "odd": 4 * n,
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
        "gb_matrix": {
            "dimensions": [2, 2 * n],
            "total_parameters": 4 * n,
            "fermionic_oscillators": fermions,
            "bosonic_oscillators": bosons,
            "matrix": matrix_rows,
        },
        "basis": {
            "even": even_basis,
            "odd": odd_basis,
            "ordering_convention": "PBW: kappa < [odd: E_eps1_del{k}_pp/pm/mp/mm] < [even: H_k, E_2del{k}_p/m, E_del{i}_del{j}_pp/mm/pm/mp]",
        },
        "parity": parities,
        "inhomogeneous_deformation": {
            "description": "Symbolic gamma coefficients gamma_abc(gb) for [X, Y]_gamma = [X, Y]_0 + kappa * gamma(X, Y)",
            "sign_rule": "graded",
            "total_gamma_terms": len(gamma_entries),
            "gamma_coefficients": gamma_entries,
        },
        "metadata": {
            "generated_by": "src/C_gamma.py",
            "generation_date": "2026-10-04",
            "references": [
                "docs/math/C_inhomogeneous_definition.md",
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
        out = f"data/C_{n}_gamma.json"
        print(f"Generating Schema 2 for n={n} -> {out}...")
        generate_schema2_json(n, out)
        print(f"Done generating {out}.")


if __name__ == "__main__":
    main()
