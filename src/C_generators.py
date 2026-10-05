"""
C(n+1) = osp(2|2n) structure constant generator.

Computes basis, parity, oscillator realizations, and graded brackets
for C(n+1) following the conventions in handover/notation.md.
Outputs Schema 1 JSON files for n=1,2,3.
"""

import json
import os
from fractions import Fraction
from datetime import date


def build_basis(n):
    even = []
    odd = []

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
    for i in range(1, n + 1):
        for j in range(i + 1, n + 1):
            even.append(f"E_del{i}_del{j}_mp")

    for k in range(1, n + 1):
        odd.append(f"E_eps1_del{k}_pp")
    for k in range(1, n + 1):
        odd.append(f"E_eps1_del{k}_pm")
    for k in range(1, n + 1):
        odd.append(f"E_eps1_del{k}_mp")
    for k in range(1, n + 1):
        odd.append(f"E_eps1_del{k}_mm")

    return even, odd


def build_parity_map(even, odd):
    p = {}
    for g in even:
        p[g] = 0
    for g in odd:
        p[g] = 1
    return p


# --- Oscillator algebra ---
# Each oscillator is identified by (type, index, sign):
#   type: 'a' (fermion) or 'b' (boson)
#   index: integer
#   sign: '+' or '-'
# A generator realization is a LinComb: dict mapping basis_key -> Fraction
# basis_key is either:
#   () for scalar 1
#   ((type1, idx1, sign1), (type2, idx2, sign2)) for a bilinear

def osc_parse(label):
    if label.startswith("a_"):
        parts = label.split("_")
        return ('a', int(parts[1]), parts[2])
    elif label.startswith("b_"):
        parts = label.split("_")
        return ('b', int(parts[1]), parts[2])
    raise ValueError(f"Unknown oscillator: {label}")


def osc_label(osc):
    return f"{osc[0]}_{osc[1]}_{osc[2]}"


def osc_parity(osc):
    return 1 if osc[0] == 'a' else 0


def fundamental_bracket(A, B):
    """Compute the fundamental graded bracket [A, B} of two single oscillators.
    Returns a scalar (Fraction).
    For fermions: {a_i_s1, a_j_s2} = delta_{ij} * delta_{s1!=s2} (with sign convention)
    For bosons: [b_i_s1, b_j_s2] = delta_{ij} * (delta_{s1='-',s2='+'} - delta_{s1='+',s2='-'})
    Mixed: [b, a] = 0
    """
    pA, pB = osc_parity(A), osc_parity(B)

    if pA == 1 and pB == 1:
        # Both fermions: anticommutator {A, B}
        if A[1] == B[1]:
            # {a_1_m, a_1_p} = 1
            if A[2] == 'm' and B[2] == 'p':
                return Fraction(1)
            elif A[2] == 'p' and B[2] == 'm':
                return Fraction(1)
        return Fraction(0)

    if pA == 0 and pB == 0:
        # Both bosons: commutator [A, B]
        if A[1] == B[1]:
            if A[2] == 'm' and B[2] == 'p':
                return Fraction(1)
            elif A[2] == 'p' and B[2] == 'm':
                return Fraction(-1)
        return Fraction(0)

    # Mixed: commutator is 0
    return Fraction(0)


def gen_realization(n):
    """Return dict mapping generator label -> list of (coeff, term)
    where term is either () for scalar or (osc1, osc2) for bilinear.
    """
    a1p = ('a', 1, 'p')
    a1m = ('a', 1, 'm')

    def bp(k): return ('b', k, 'p')
    def bm(k): return ('b', k, 'm')

    gens = {}

    # H_1 = a_1^+ a_1^- + b_1^+ b_1^-
    gens["H_1"] = [(Fraction(1), (a1p, a1m)), (Fraction(1), (bp(1), bm(1)))]

    # H_k = b_{k-1}^+ b_{k-1}^- - b_k^+ b_k^- for 2 <= k <= n
    for k in range(2, n + 1):
        gens[f"H_{k}"] = [
            (Fraction(1), (bp(k - 1), bm(k - 1))),
            (Fraction(-1), (bp(k), bm(k))),
        ]

    # H_{n+1} = -b_n^+ b_n^- - 1/2
    gens[f"H_{n+1}"] = [
        (Fraction(-1), (bp(n), bm(n))),
        (Fraction(-1, 2), ()),
    ]

    for k in range(1, n + 1):
        gens[f"E_2del{k}_p"] = [(Fraction(1), (bp(k), bp(k)))]
        gens[f"E_2del{k}_m"] = [(Fraction(1), (bm(k), bm(k)))]

    for i in range(1, n + 1):
        for j in range(i + 1, n + 1):
            gens[f"E_del{i}_del{j}_pp"] = [(Fraction(1), (bp(i), bp(j)))]
            gens[f"E_del{i}_del{j}_mm"] = [(Fraction(1), (bm(i), bm(j)))]
            gens[f"E_del{i}_del{j}_pm"] = [(Fraction(1), (bp(i), bm(j)))]
            gens[f"E_del{i}_del{j}_mp"] = [(Fraction(1), (bm(i), bp(j)))]

    for k in range(1, n + 1):
        gens[f"E_eps1_del{k}_pp"] = [(Fraction(1), (a1p, bp(k)))]
        gens[f"E_eps1_del{k}_pm"] = [(Fraction(1), (a1p, bm(k)))]
        gens[f"E_eps1_del{k}_mp"] = [(Fraction(1), (a1m, bp(k)))]
        gens[f"E_eps1_del{k}_mm"] = [(Fraction(1), (a1m, bm(k)))]

    return gens


def bracket_bilinear(termX, termY, pX, pY):
    """Compute the graded bracket [X, Y} where X and Y are single oscillator terms.
    termX, termY are either () for scalar or (osc1, osc2) for bilinear.
    pX, pY are parities of the generators.
    Returns a LinComb: list of (coeff, term).

    Uses the graded Leibniz rule:
    [AB, CD} = A[B, CD} + (-1)^{p(B)(p(C)+p(D))} [A, CD}B

    And [A, CD} = [A, C}D + (-1)^{p(A)p(C)} C[A, D}
    (where [,} denotes the graded bracket: anticommutator if both odd, commutator otherwise)
    """
    if termX == () and termY == ():
        return []
    if termX == ():
        return []  # scalar commutes with everything
    if termY == ():
        return []  # scalar commutes with everything

    if len(termX) == 2 and len(termY) == 2:
        A, B = termX
        C, D = termY
        pA, pB, pC, pD = osc_parity(A), osc_parity(B), osc_parity(C), osc_parity(D)

        # [AB, CD} via Leibniz:
        # = A{B,C}D - (-1)^{pB*pC} A*C*{B,D} + {A,C}*B*D - (-1)^{pA*pC} C*{A,D}*B
        # Wait, let me be more careful.
        #
        # In the superalgebra, for the associative product:
        # [AB, C} = A(BC) - (-1)^{(pA+pB)pC} C(AB)
        #         = A(BC - (-1)^{pB*pC} CB) + (AC - (-1)^{pA*pC} CA)B  (not quite right)
        #
        # The correct graded Leibniz rule for the graded commutator in the
        # associative algebra is:
        # [AB, C] = A[B, C] + [A, C]B  (for commutator [,] = AB - BA)
        #
        # For the graded bracket:
        # [AB, C} = A[B, C} + (-1)^{pB*pC} [A, C}B
        #
        # Wait, I need to be precise. Let's use the standard identity.
        # In a Z_2-graded associative algebra, the graded commutator satisfies:
        # [a, bc} = [a, b}c + (-1)^{p(a)p(b)} b[a, c}
        #
        # So [AB, C} = A[B, C} + (-1)^{p(B)p(C)} [A, C}B  ... no.
        #
        # Let me use: [a, bc} = [a, b}c + (-1)^{p(a)p(b)} b[a, c}
        # This says: bracket of a with a product bc.
        #
        # For [AB, C}: we need [AB, C} = (AB)C - (-1)^{(pA+pB)pC} C(AB)
        #
        # Using [a, bc} = [a, b}c + (-1)^{p(a)p(b)} b[a, c}:
        # [C, AB} = [C, A}B + (-1)^{pC*pA} A[C, B}
        #
        # And [AB, C} = -(-1)^{(pA+pB)pC} [C, AB}
        #             = -(-1)^{(pA+pB)pC} ([C, A}B + (-1)^{pC*pA} A[C, B})
        #             = -(-1)^{(pA+pB)pC} [C, A}B - (-1)^{(pA+pB)pC + pC*pA} A[C, B}
        #             = (-1)^{pA*pC} [A, C}B + (-1)^{pB*pC} A[B, C}
        #
        # Wait, [AB, C} = -(-1)^{(pA+pB)*pC} [C, AB}, and
        # [C, A} = -(-1)^{pC*pA} [A, C}
        #
        # So: [AB, C} = -(-1)^{(pA+pB)*pC} ( -(-1)^{pC*pA}[A,C}B + (-1)^{pC*pA} A[C,B} )
        #             = (-1)^{(pA+pB)*pC + pC*pA}[A,C}B - (-1)^{(pA+pB)*pC + pC*pA} A[C,B}
        #             = (-1)^{pB*pC}[A,C}B - (-1)^{pB*pC} A[C,B}
        #             = (-1)^{pB*pC}[A,C}B + (-1)^{pB*pC + pC*pB} A[B,C}
        #             = (-1)^{pB*pC}[A,C}B + A[B,C}
        #
        # Good. So: [AB, C} = A[B,C} + (-1)^{pB*pC}[A,C}B
        #
        # Now [AB, CD} = [AB, C}D + (-1)^{(pA+pB)*pC} C[AB, D}
        #
        # Wait, using [a, bc} = [a,b}c + (-1)^{p(a)*p(b)} b[a,c}
        # with a=AB, b=C, c=D:
        # [AB, CD} = [AB, C}D + (-1)^{(pA+pB)*pC} C[AB, D}
        #
        # Each of [AB,C} and [AB,D} expands to 2 terms, giving 4 terms total.

        # [AB, C} = A[B,C} + (-1)^{pB*pC}[A,C}B
        BC = fundamental_bracket(B, C)
        AC = fundamental_bracket(A, C)

        # [AB, D} = A[B,D} + (-1)^{pB*pD}[A,D}B
        BD = fundamental_bracket(B, D)
        AD = fundamental_bracket(A, D)

        sign_BC = Fraction(1)
        sign_AC = Fraction((-1) ** (pB * pC))
        sign_CD_factor = Fraction((-1) ** ((pA + pB) * pC))
        sign_BD2 = Fraction(1)
        sign_AD2 = Fraction((-1) ** (pB * pD))

        result = []

        # Term 1: A[B,C}D -> BC * (A, D)
        if BC != 0:
            result.append((sign_BC * BC, (A, D)))

        # Term 2: (-1)^{pB*pC}[A,C}BD -> sign_AC * AC * (B, D)
        # But wait, B and D aren't necessarily in normal order.
        # Actually we need to be more careful: the result is in the associative
        # algebra, so (B, D) means the product B*D, not necessarily a basis element.
        # We need to normal-order B*D.
        if AC != 0:
            result.append((sign_AC * AC, (B, D)))

        # Term 3: (-1)^{(pA+pB)*pC} C * A[B,D} -> sign_CD_factor * BD * (C, A)
        if BD != 0:
            result.append((sign_CD_factor * sign_BD2 * BD, (C, A)))

        # Term 4: (-1)^{(pA+pB)*pC} * (-1)^{pB*pD} C * [A,D} * B
        #        -> sign_CD_factor * sign_AD2 * AD * (C, B)
        if AD != 0:
            result.append((sign_CD_factor * sign_AD2 * AD, (C, B)))

        return result

    return []


def normal_order_bilinear(osc1, osc2):
    """Normal-order a product of two oscillators.
    Returns list of (coeff, term) where term is () or (osc1', osc2').
    Normal order: creation before annihilation, fermion before boson.
    """
    p1, p2 = osc_parity(osc1), osc_parity(osc2)

    # If fermion * boson or same and already ordered, return as is
    if p1 == 1 and p2 == 0:
        return [(Fraction(1), (osc1, osc2))]
    if p1 == 0 and p2 == 1:
        # boson * fermion -> swap with sign (commutator is 0)
        return [(Fraction(1), (osc2, osc1))]

    if p1 == 1 and p2 == 1:
        # Both fermions
        if osc1 == osc2:
            return []  # a^2 = 0
        # {a_m, a_p} = 1, want a_p before a_m
        if osc1[2] == 'p':
            return [(Fraction(1), (osc1, osc2))]
        else:
            # a_m * a_p = 1 - a_p * a_m
            bracket = fundamental_bracket(osc1, osc2)
            result = [(Fraction(-1), (osc2, osc1))]
            if bracket != 0:
                result.append((bracket, ()))
            return result

    if p1 == 0 and p2 == 0:
        # Both bosons
        if osc1[1] < osc2[1]:
            return [(Fraction(1), (osc1, osc2))]
        if osc1[1] > osc2[1]:
            # Swap: [b_i, b_j] = 0 if i != j
            return [(Fraction(1), (osc2, osc1))]
        # Same index
        if osc1[2] == 'p' and osc2[2] == 'm':
            return [(Fraction(1), (osc1, osc2))]
        if osc1[2] == 'm' and osc2[2] == 'p':
            # b_m * b_p = b_p * b_m + 1
            return [(Fraction(1), (osc2, osc1)), (Fraction(1), ())]
        # same sign: b_p*b_p or b_m*b_m - already fine
        return [(Fraction(1), (osc1, osc2))]

    return [(Fraction(1), (osc1, osc2))]


def simplify_lincomb(terms):
    """Simplify a list of (coeff, term) by combining like terms."""
    d = {}
    for coeff, term in terms:
        if coeff == 0:
            continue
        # Normalize term: for bilinear, normal-order
        if len(term) == 2:
            no = normal_order_bilinear(term[0], term[1])
            for c2, t2 in no:
                key = t2
                d[key] = d.get(key, Fraction(0)) + coeff * c2
        else:
            d[term] = d.get(term, Fraction(0)) + coeff
    return [(c, t) for t, c in d.items() if c != 0]


def compute_graded_bracket_gen(realsX, realsY, pX, pY):
    """Compute [X, Y} for generators X, Y given their oscillator realizations."""
    result = []
    for cx, tx in realsX:
        for cy, ty in realsY:
            if cx == 0 or cy == 0:
                continue
            bracket_terms = bracket_bilinear(tx, ty, pX, pY)
            for cb, tb in bracket_terms:
                result.append((cx * cy * cb, tb))
    return simplify_lincomb(result)


def decompose_in_basis(bracket_result, gen_realizations, all_basis, parity_map):
    """Express bracket result as a linear combination of basis generators.
    bracket_result: list of (coeff, term)
    Returns list of (gen_label, coeff).
    """
    if not bracket_result:
        return []

    # Build a map from normalized term -> list of (gen, contribution_coeff)
    # For single-term generators this is straightforward.
    # For multi-term generators (Cartan), we need to solve.

    # Strategy: process single-term generators first to absorb those terms,
    # then handle Cartan elements.

    remaining = {}
    for c, t in bracket_result:
        remaining[t] = remaining.get(t, Fraction(0)) + c
    remaining = {t: c for t, c in remaining.items() if c != 0}

    result = {}

    # First pass: single-term generators (non-Cartan)
    single_term_gens = {}
    for gen in all_basis:
        terms = gen_realizations[gen]
        if len(terms) == 1:
            c_gen, t_gen = terms[0]
            # Normalize
            no = normal_order_bilinear(t_gen[0], t_gen[1]) if len(t_gen) == 2 else [(Fraction(1), t_gen)]
            for cn, tn in no:
                actual_coeff = c_gen * cn
                if tn in single_term_gens:
                    pass  # shouldn't happen for distinct generators
                else:
                    single_term_gens[tn] = (gen, actual_coeff)

    for t, c in list(remaining.items()):
        if t in single_term_gens:
            gen, gen_coeff = single_term_gens[t]
            coeff_in_gen = c / gen_coeff
            result[gen] = result.get(gen, Fraction(0)) + coeff_in_gen
            del remaining[t]

    # Second pass: Cartan elements (multi-term)
    for gen in all_basis:
        if not gen.startswith("H_"):
            continue
        terms = gen_realizations[gen]
        if len(terms) <= 1:
            continue

        # Normalize all terms of this generator
        normalized = []
        for c_gen, t_gen in terms:
            if len(t_gen) == 2:
                no = normal_order_bilinear(t_gen[0], t_gen[1])
                for cn, tn in no:
                    normalized.append((c_gen * cn, tn))
            else:
                normalized.append((c_gen, t_gen))

        # Find the coefficient by matching any remaining term
        for c_gen_norm, t_gen_norm in normalized:
            if t_gen_norm in remaining and c_gen_norm != 0:
                coeff_in_gen = remaining[t_gen_norm] / c_gen_norm
                result[gen] = result.get(gen, Fraction(0)) + coeff_in_gen
                # Remove all terms of this generator from remaining
                for cn2, tn2 in normalized:
                    if tn2 in remaining:
                        remaining[tn2] = remaining[tn2] - coeff_in_gen * cn2
                        if remaining[tn2] == 0:
                            del remaining[tn2]
                break

    return [(g, c) for g, c in result.items() if c != 0]


def compute_all_structure_constants(n):
    even, odd = build_basis(n)
    all_basis = odd + even
    parity = build_parity_map(even, odd)
    reals = gen_realization(n)

    constants = []

    for i, X in enumerate(all_basis):
        for j in range(i + 1, len(all_basis)):
            Y = all_basis[j]
            pX, pY = parity[X], parity[Y]
            bracket = compute_graded_bracket_gen(reals[X], reals[Y], pX, pY)

            if not bracket:
                continue

            decomp = decompose_in_basis(bracket, reals, all_basis, parity)
            for Z, coeff in decomp:
                constants.append({
                    "X": X,
                    "Y": Y,
                    "Z": Z,
                    "coeff": str(coeff),
                    "sign_rule": "graded",
                })

    return constants


def build_generator_realization_json(n):
    reals = gen_realization(n)
    result = {
        "description": "Standard form with PBW ordering",
        "ordering": ", ".join(
            ["a_1_p", "a_1_m"] + [f"b_{k}_{s}" for k in range(1, n + 1) for s in ["p", "m"]]
        ),
        "realizations": {},
    }
    for gen, terms in reals.items():
        words_list = []
        for coeff, term in terms:
            if len(term) == 2:
                words_list.append({
                    "words": [osc_label(term[0]), osc_label(term[1])],
                    "coeff": str(coeff),
                })
            elif len(term) == 0:
                words_list.append({
                    "words": [],
                    "coeff": str(coeff),
                })
        fr_parts = []
        for coeff, term in terms:
            if len(term) == 0:
                fr_parts.append(str(coeff))
            else:
                labels = [osc_label(o) for o in term]
                c = str(coeff)
                w = " ".join(labels)
                if c == "1":
                    fr_parts.append(w)
                elif c == "-1":
                    fr_parts.append(f"-{w}")
                else:
                    fr_parts.append(f"{c} * {w}")
        p = 0
        if gen.startswith("E_eps1"):
            p = 1
        result["realizations"][gen] = {
            "standard_form": words_list,
            "frappat_form": " + ".join(fr_parts).replace("+ -", "- "),
            "parity": p,
        }
    return result


def build_schema1_json(n):
    even, odd = build_basis(n)
    parity = build_parity_map(even, odd)
    constants = compute_all_structure_constants(n)
    gen_real = build_generator_realization_json(n)

    even_dim = 2 * n * n + n + 1
    odd_dim = 4 * n

    assert len(even) == even_dim, f"Even count mismatch: {len(even)} != {even_dim}"
    assert len(odd) == odd_dim, f"Odd count mismatch: {len(odd)} != {odd_dim}"

    schema = {
        "schema_version": "5.0",
        "algebra": {
            "family": "C",
            "m": 1,
            "n": n,
            "cartan_type": f"C({n + 1})",
            "alternative_notation": {
                "osp": f"osp(2|{2 * n})",
                "dimension_formula": "osp(2m|2n) with m=1",
            },
            "dimension": {
                "total": even_dim + odd_dim,
                "even": even_dim,
                "odd": odd_dim,
            },
        },
        "oscillator_generators": {
            "fermions": {
                "type": "standard_pair",
                "m": 1,
                "count": 2,
                "labels": ["a_1_p", "a_1_m"],
                "parity": 1,
                "description": "Standard fermionic pair a_1^+, a_1^- with CAR",
            },
            "bosons": {
                "count": 2 * n,
                "n": n,
                "labels": [f"b_{k}_{s}" for k in range(1, n + 1) for s in ["p", "m"]],
                "description": f"Bosonic oscillators b_i^± with i=1,...,{n}",
            },
        },
        "oscillator_relations": {
            "standard_fermion_anticommutators": {
                "description": "Canonical anticommutation relations for the standard fermionic pair",
                "relations": {
                    "anticommutator": "{a_1^-, a_1^+} = 1",
                    "nilpotency": "(a_1^+)^2 = 0, (a_1^-)^2 = 0",
                },
            },
            "bosonic_commutators": {
                "description": "Canonical commutation relations for bosonic oscillators",
                "relations": {
                    "same_type": "[b_i^±, b_j^±] = 0 for all i, j",
                    "conjugate_pair": "[b_i^-, b_j^+] = δ_{ij}",
                },
            },
            "mixed_commutators": {
                "boson_fermion": "[b_i^±, a_1^±] = 0 (undeformed)",
            },
        },
        "central_elements": {
            "kappa": {
                "parity": 1,
                "nilpotency": "kappa^2 = 0",
                "description": "Odd central element for abelian extension",
            },
            "K": {
                "parity": 0,
                "value": "1",
                "description": "Even central identity element; identified with scalar 1",
            },
        },
        "basis": {
            "even": even,
            "odd": odd,
            "ordering_convention": "PBW: κ < [odd] < [even]  (K = 1 is excluded)",
        },
        "parity": parity,
        "generator_realization": gen_real,
        "structure_constants": constants,
        "metadata": {
            "generated_by": "C_generators.py",
            "generation_date": str(date.today()),
            "references": [
                "Frappat et al. (2000), Dictionary on Lie Algebras and Superalgebras",
                "Bakalov and Sullivan (2017)",
            ],
        },
    }
    return schema


def generate_all(output_dir="data"):
    os.makedirs(output_dir, exist_ok=True)
    for n in [1, 2, 3]:
        schema = build_schema1_json(n)
        path = os.path.join(output_dir, f"C_{n}_structure.json")
        with open(path, "w") as f:
            json.dump(schema, f, indent=2)
        print(f"Generated {path}: {len(schema['structure_constants'])} structure constants, "
              f"dim={schema['algebra']['dimension']}")


if __name__ == "__main__":
    generate_all()
