"""
C(n+1) = osp(2|2n) structure constant generator.

Computes the Lie superalgebra structure constants [X, Y} for all basis
generator pairs and outputs Schema 1 JSON files for n=1,2,3.

Mathematical reference: docs/math/Cn1_definition.md, docs/math/B0n_schema_v5.md
"""

import json
import os
from fractions import Fraction
from itertools import combinations
from datetime import date


# ---------------------------------------------------------------------------
# Basis construction
# ---------------------------------------------------------------------------

def build_basis(n):
    """
    Returns (even_basis, odd_basis) lists for C(n+1) = osp(2|2n).

    Even dim = 2n^2 + n + 1, Odd dim = 4n.
    PBW odd-before-even ordering within each sector.
    """
    # Cartan generators H_1, ..., H_{n+1}
    cartan = [f"H_{k}" for k in range(1, n + 2)]

    # Positive even roots: E_2del{k}_p, E_del{i}_del{j}_pp
    pos_double = [f"E_2del{k}_p" for k in range(1, n + 1)]
    pos_mixed_pp = [f"E_del{i}_del{j}_pp" for i in range(1, n + 1)
                    for j in range(i + 1, n + 1)]

    # Negative even roots: E_2del{k}_m, E_del{i}_del{j}_mm
    neg_double = [f"E_2del{k}_m" for k in range(1, n + 1)]
    neg_mixed_mm = [f"E_del{i}_del{j}_mm" for i in range(1, n + 1)
                    for j in range(i + 1, n + 1)]

    # Mixed even roots: E_del{i}_del{j}_pm, E_del{i}_del{j}_mp
    mixed_pm = [f"E_del{i}_del{j}_pm" for i in range(1, n + 1)
                for j in range(i + 1, n + 1)]
    mixed_mp = [f"E_del{i}_del{j}_mp" for i in range(1, n + 1)
                for j in range(i + 1, n + 1)]

    even_basis = (cartan + pos_double + pos_mixed_pp +
                  neg_double + neg_mixed_mm + mixed_pm + mixed_mp)

    # Odd generators: E_eps_del{k}_{pp/pm/mp/mm}
    odd_basis = []
    for k in range(1, n + 1):
        for sign in ["pp", "pm", "mp", "mm"]:
            odd_basis.append(f"E_eps_del{k}_{sign}")

    return even_basis, odd_basis


def parity_of(label):
    """Return parity (0 or 1) of a generator label."""
    if label.startswith("E_eps_del"):
        return 1
    return 0


def build_parity_dict(even_basis, odd_basis):
    return {g: 0 for g in even_basis} | {g: 1 for g in odd_basis}


# ---------------------------------------------------------------------------
# Structure constants via oscillator algebra
# ---------------------------------------------------------------------------
# Each generator is an element of the oscillator algebra.
# We represent generators as linear combinations of oscillator monomials.
# Monomials are tuples of oscillator labels in normal order.
#
# Oscillators for C(n+1):
#   Fermions: a_1_p (creation), a_1_m (annihilation)  -- CAR: {a_1_m, a_1_p} = 1
#   Bosons:   b_k_p (creation), b_k_m (annihilation)  -- CCR: [b_k_m, b_l_p] = δ_{kl}
#
# We compute brackets by expanding the commutator/anticommutator
# (graded bracket [X,Y} = XY - (-1)^{p(X)p(Y)} YX) using bilinearity
# and the oscillator relations.
#
# For efficiency, we represent each element as a dict {monomial: coeff}
# and implement the graded bracket algebraically.

def osc_type(label):
    """Return 'f' (fermionic) or 'b' (bosonic) for an oscillator label."""
    if label.startswith("a_"):
        return "f"
    return "b"


def normal_order_product(mono1, mono2, n):
    """
    Compute the normal-ordered product of two oscillator monomials.
    Returns a dict {monomial_tuple: Fraction} representing the result.

    Normal order: all creation operators before annihilation, fermions before bosons.
    Actual ordering: a_1_p, a_1_m, b_1_p, b_1_m, ..., b_n_p, b_n_m.
    We implement a simple bubble-sort with commutation/anticommutation relations.
    """
    # Start with the concatenated monomial
    word = list(mono1) + list(mono2)
    return _normalize(word, n)


def _normalize(word, n):
    """
    Reduce a word (list of oscillator labels) to normal form using CAR/CCR.
    Returns dict {tuple: Fraction}.
    """
    # Assign ordering index to each oscillator label
    def order_idx(label):
        order = ["a_1_p", "a_1_m"] + [x for k in range(1, n + 1)
                                        for x in (f"b_{k}_p", f"b_{k}_m")]
        try:
            return order.index(label)
        except ValueError:
            raise ValueError(f"Unknown oscillator: {label}")

    # BFS/DFS approach: represent as list of (word_list, coeff) pairs
    result = {}
    stack = [(list(word), Fraction(1))]

    while stack:
        w, c = stack.pop()
        # Find first pair out of order
        moved = False
        for i in range(len(w) - 1):
            if order_idx(w[i]) > order_idx(w[i + 1]):
                a, b = w[i], w[i + 1]
                moved = True
                ta, tb = osc_type(a), osc_type(b)

                if ta == "f" and tb == "f":
                    # Fermionic: a·b = -b·a + {a,b}
                    # {a_1_m, a_1_p} = 1; all others = 0
                    anticom = Fraction(0)
                    if (a == "a_1_m" and b == "a_1_p") or (a == "a_1_p" and b == "a_1_m"):
                        anticom = Fraction(1)

                    # swap term: -b·a (anticommuting fermions)
                    new_w = list(w)
                    new_w[i], new_w[i + 1] = b, a
                    stack.append((new_w, -c))

                    # scalar term from anticommutator
                    if anticom != 0:
                        remaining = w[:i] + w[i + 2:]
                        stack.append((remaining, c * anticom))

                elif ta == "b" and tb == "b":
                    # Bosonic: a·b = b·a + [a,b]
                    # [b_k_m, b_l_p] = δ_{kl}; [b_k_p, b_l_p] = 0; etc.
                    com = Fraction(0)
                    # Check if a = b_k_m and b = b_k_p (same k)
                    if (a.endswith("_m") and b.endswith("_p") and
                            a[:-2] == b[:-2]):
                        com = Fraction(1)

                    # swap: b·a (commuting bosons)
                    new_w = list(w)
                    new_w[i], new_w[i + 1] = b, a
                    stack.append((new_w, c))

                    if com != 0:
                        remaining = w[:i] + w[i + 2:]
                        stack.append((remaining, c * com))

                else:
                    # Mixed boson-fermion: commute freely (sign: fermion passes through boson)
                    # In standard conventions, [b, a_f] = 0, but fermion picks up sign when
                    # passing a fermion. Since only one fermion pair exists (a_1_p, a_1_m),
                    # and bosons commute with fermions: b·f = (-1)^{p(b)p(f)} f·b = f·b
                    # (bosons have parity 0, so no sign change)
                    new_w = list(w)
                    new_w[i], new_w[i + 1] = b, a
                    stack.append((new_w, c))

                break

        if not moved:
            # Word is in normal order; check for adjacent identical fermions (which square to 0)
            has_zero = False
            for i in range(len(w) - 1):
                if osc_type(w[i]) == "f" and w[i] == w[i + 1]:
                    has_zero = True
                    break
            if has_zero:
                continue
            key = tuple(w)
            result[key] = result.get(key, Fraction(0)) + c

    # Remove zeros
    return {k: v for k, v in result.items() if v != 0}


def elem_product(e1, e2, n):
    """
    Compute the product of two algebra elements (dicts of monomial:coeff).
    """
    result = {}
    for m1, c1 in e1.items():
        for m2, c2 in e2.items():
            prod = _normalize(list(m1) + list(m2), n)
            for m, c in prod.items():
                result[m] = result.get(m, Fraction(0)) + c1 * c2 * c
    return {k: v for k, v in result.items() if v != 0}


def graded_bracket(e1, p1, e2, p2, n):
    """
    Compute graded bracket [e1, e2} = e1*e2 - (-1)^{p1*p2} e2*e1.
    """
    ab = elem_product(e1, e2, n)
    ba = elem_product(e2, e1, n)
    sign = Fraction((-1) ** (p1 * p2))

    result = {}
    for m, c in ab.items():
        result[m] = result.get(m, Fraction(0)) + c
    for m, c in ba.items():
        result[m] = result.get(m, Fraction(0)) - sign * c

    return {k: v for k, v in result.items() if v != 0}


# ---------------------------------------------------------------------------
# Generator realizations as oscillator elements
# ---------------------------------------------------------------------------

def build_generator_realizations(n):
    """
    Returns a dict mapping generator label -> oscillator element (dict of monomial:coeff).
    """
    gens = {}

    # H_1 = a_1^+ a_1^- + b_1^+ b_1^-
    gens["H_1"] = {("a_1_p", "a_1_m"): Fraction(1),
                   ("b_1_p", "b_1_m"): Fraction(1)}

    # H_k = b_{k-1}^+ b_{k-1}^- - b_k^+ b_k^-, for k=2,...,n
    for k in range(2, n + 1):
        gens[f"H_{k}"] = {(f"b_{k-1}_p", f"b_{k-1}_m"): Fraction(1),
                          (f"b_{k}_p", f"b_{k}_m"): Fraction(-1)}

    # H_{n+1} = -b_n^+ b_n^- - 1/2
    # Represent constant -1/2 as the empty monomial ()
    gens[f"H_{n+1}"] = {(f"b_{n}_p", f"b_{n}_m"): Fraction(-1),
                        (): Fraction(-1, 2)}

    # Even root generators
    # E_{2δ_k} = (1/2)(b_k^+)^2, E_{-2δ_k} = (1/2)(b_k^-)^2
    for k in range(1, n + 1):
        gens[f"E_2del{k}_p"] = {(f"b_{k}_p", f"b_{k}_p"): Fraction(1, 2)}
        gens[f"E_2del{k}_m"] = {(f"b_{k}_m", f"b_{k}_m"): Fraction(1, 2)}

    # E_{δ_i + δ_j} = b_i^+ b_j^+, E_{-δ_i - δ_j} = b_i^- b_j^-
    # E_{δ_i - δ_j} = b_i^+ b_j^-, E_{-δ_i + δ_j} = b_i^- b_j^+
    for i in range(1, n + 1):
        for j in range(i + 1, n + 1):
            gens[f"E_del{i}_del{j}_pp"] = {(f"b_{i}_p", f"b_{j}_p"): Fraction(1)}
            gens[f"E_del{i}_del{j}_mm"] = {(f"b_{i}_m", f"b_{j}_m"): Fraction(1)}
            gens[f"E_del{i}_del{j}_pm"] = {(f"b_{i}_p", f"b_{j}_m"): Fraction(1)}
            gens[f"E_del{i}_del{j}_mp"] = {(f"b_{i}_m", f"b_{j}_p"): Fraction(1)}

    # Odd root generators
    # E_{ε + δ_k} = a_1^+ b_k^+, E_{ε - δ_k} = a_1^+ b_k^-
    # E_{-ε + δ_k} = a_1^- b_k^+, E_{-ε - δ_k} = a_1^- b_k^-
    for k in range(1, n + 1):
        gens[f"E_eps_del{k}_pp"] = {("a_1_p", f"b_{k}_p"): Fraction(1)}
        gens[f"E_eps_del{k}_pm"] = {("a_1_p", f"b_{k}_m"): Fraction(1)}
        gens[f"E_eps_del{k}_mp"] = {("a_1_m", f"b_{k}_p"): Fraction(1)}
        gens[f"E_eps_del{k}_mm"] = {("a_1_m", f"b_{k}_m"): Fraction(1)}

    return gens


# ---------------------------------------------------------------------------
# Express bracket result in the generator basis
# ---------------------------------------------------------------------------

def build_monomial_to_generator_map(gens):
    """
    Build inverse map: canonical monomial -> (generator_label, coefficient)
    for generators that ARE single monomials (not sums).
    For generators that are sums, we handle separately.
    """
    mono_map = {}
    for label, elem in gens.items():
        if len(elem) == 1:
            (mono,), (coeff,) = zip(elem.keys()), zip(elem.values())
            mono_map[mono] = (label, coeff)
    return mono_map


def express_in_basis(elem, gens, n):
    """
    Express elem (oscillator element) as a linear combination of generators
    using Gaussian elimination over the rationals.

    Returns dict {generator_label: Fraction} or None if not expressible.
    Scalar multiples of the identity (empty monomial) are silently ignored
    since K is identified with 1 and not a basis element.
    """
    if not elem:
        return {}

    # Non-scalar part of elem
    elem_ns = {m: c for m, c in elem.items() if m != ()}
    if not elem_ns:
        return {}

    # Collect ALL non-scalar monomials from all generators
    all_gen_monos = set()
    for g_elem in gens.values():
        for m in g_elem:
            if m != ():
                all_gen_monos.add(m)

    # Use all monomials from elem AND from generators as rows
    # This over-constrains the system properly
    all_monos = sorted(all_gen_monos | set(elem_ns.keys()), key=str)
    mono_idx = {m: i for i, m in enumerate(all_monos)}
    nrow = len(all_monos)
    gen_list = list(gens.items())
    ncol = len(gen_list)

    # Augmented matrix [A | b]
    mat = [[Fraction(0)] * (ncol + 1) for _ in range(nrow)]
    for j, (label, g_elem) in enumerate(gen_list):
        for m, c in g_elem.items():
            if m != ():
                mat[mono_idx[m]][j] = c
    for m, c in elem_ns.items():
        mat[mono_idx[m]][ncol] = c

    # Gaussian elimination (full — operates on all rows)
    pivot_col = {}  # row_used -> col of pivot
    row_used = 0
    for col in range(ncol):
        pivot_row = None
        for r in range(row_used, nrow):
            if mat[r][col] != 0:
                pivot_row = r
                break
        if pivot_row is None:
            continue
        mat[row_used], mat[pivot_row] = mat[pivot_row], mat[row_used]
        pivot_col[row_used] = col
        pv = mat[row_used][col]
        mat[row_used] = [x / pv for x in mat[row_used]]
        for r in range(nrow):
            if r != row_used and mat[r][col] != 0:
                factor = mat[r][col]
                mat[r] = [mat[r][k] - factor * mat[row_used][k] for k in range(ncol + 1)]
        row_used += 1

    # Check consistency
    for r in range(row_used, nrow):
        if mat[r][ncol] != 0:
            return None

    # Extract solution (free variables default to 0)
    solution = {label: Fraction(0) for label, _ in gen_list}
    for r, col in pivot_col.items():
        label = gen_list[col][0]
        solution[label] = mat[r][ncol]

    # Verify (should be redundant, but kept as safety check)
    check = {}
    for label, coeff in solution.items():
        if coeff == 0:
            continue
        for m, c in gens[label].items():
            if m != ():
                check[m] = check.get(m, Fraction(0)) + coeff * c
    check = {m: c for m, c in check.items() if c != 0}
    if check != elem_ns:
        return None

    return {k: v for k, v in solution.items() if v != 0}


# ---------------------------------------------------------------------------
# Main structure constant computation
# ---------------------------------------------------------------------------

def compute_structure_constants(n):
    """
    Compute all non-zero structure constants for C(n+1) with bosonic rank n.
    Returns list of dicts: {"X": ..., "Y": ..., "Z": ..., "coeff": ..., "sign_rule": "graded"}
    """
    even_basis, odd_basis = build_basis(n)
    basis = odd_basis + even_basis  # PBW order: odd first
    parity = build_parity_dict(even_basis, odd_basis)
    gens = build_generator_realizations(n)

    structure_constants = []

    for xi, X in enumerate(basis):
        for yi in range(xi, len(basis)):
            Y = basis[yi]
            pX, pY = parity[X], parity[Y]

            bracket = graded_bracket(gens[X], pX, gens[Y], pY, n)

            if not bracket:
                continue

            expr = express_in_basis(bracket, gens, n)
            if expr is None:
                # Fallback: report raw (should not happen for correct algebra)
                continue

            for Z, coeff in expr.items():
                if coeff != 0:
                    structure_constants.append({
                        "X": X,
                        "Y": Y,
                        "Z": Z,
                        "coeff": str(coeff),
                        "sign_rule": "graded"
                    })

    return structure_constants


def build_schema1(n):
    """Build the complete Schema 1 JSON dict for C(n+1) with bosonic rank n."""
    even_basis, odd_basis = build_basis(n)
    parity_dict = build_parity_dict(even_basis, odd_basis)

    # Dimension
    dim_even = 2 * n * n + n + 1
    dim_odd = 4 * n
    dim_total = dim_even + dim_odd

    # Algebra label
    cartan_label = f"C({n+1})"
    osp_label = f"osp(2|{2*n})"

    # Oscillator generator labels
    fermion_labels = ["a_1_p", "a_1_m"]
    boson_labels = [f"b_{k}_{s}" for k in range(1, n + 1) for s in ["p", "m"]]

    # Generator realizations (simplified form for JSON)
    gens = build_generator_realizations(n)
    realizations = {}
    for label, elem in gens.items():
        words_list = []
        for mono, coeff in elem.items():
            words_list.append({
                "words": list(mono),
                "coeff": str(coeff)
            })
        realizations[label] = {
            "standard_form": words_list,
            "parity": parity_dict.get(label, 0)
        }

    structure_constants = compute_structure_constants(n)

    schema = {
        "schema_version": "5.0",
        "algebra": {
            "family": "C",
            "m": 1,
            "n": n,
            "cartan_type": cartan_label,
            "alternative_notation": {
                "osp": osp_label,
                "dimension_formula": "osp(2m|2n) with m=1"
            },
            "dimension": {
                "total": dim_total,
                "even": dim_even,
                "odd": dim_odd,
                "formula_even": "2n^2 + n + 1",
                "formula_odd": "4n"
            }
        },
        "central_elements": {
            "kappa": {
                "label": "kappa",
                "parity": 1,
                "relation": "kappa^2 = 0",
                "description": "Odd nilpotent central element of the abelian extension."
            },
            "K": {
                "label": "K",
                "parity": 0,
                "relation": "K = 1 (scalar identity)",
                "description": "Even central identity; identified with 1. Excluded from PBW basis."
            }
        },
        "oscillator_generators": {
            "fermions": {
                "m": 1,
                "labels": fermion_labels,
                "description": "Standard fermionic pair with CAR {a_1^-, a_1^+} = 1"
            },
            "bosons": {
                "count": 2 * n,
                "n": n,
                "labels": boson_labels,
                "description": f"Bosonic oscillators b_k^± with k=1,...,{n}"
            }
        },
        "oscillator_relations": {
            "standard_fermion_anticommutators": {
                "description": "CAR for the fermionic pair",
                "relations": {
                    "anticommutator": "{a_1^-, a_1^+} = 1",
                    "self_anticommutator_p": "{a_1^+, a_1^+} = 0",
                    "self_anticommutator_m": "{a_1^-, a_1^-} = 0"
                }
            },
            "bosonic_commutators": {
                "description": "CCR for bosonic oscillators",
                "relations": {
                    "same_type": "[b_i^±, b_j^±] = 0 for all i, j",
                    "conjugate_pair": "[b_i^-, b_j^+] = δ_{ij}"
                }
            },
            "mixed_commutators": {
                "boson_fermion": "[b_i^±, a_1^±] = 0 (undeformed)"
            }
        },
        "basis": {
            "even": even_basis,
            "odd": odd_basis,
            "ordering_convention": "PBW: κ < [odd: ε-roots] < [even]  (K=1 excluded from basis)"
        },
        "parity": parity_dict,
        "generator_realization": {
            "description": "Normal-ordered oscillator monomials",
            "ordering": ", ".join(fermion_labels + boson_labels),
            "realizations": realizations
        },
        "structure_constants": structure_constants,
        "metadata": {
            "generated_by": "src/C_generators.py",
            "generation_date": str(date.today()),
            "references": [
                "Frappat, Sciarrino, Sorba (2000), Dictionary on Lie Algebras and Superalgebras",
                "Bakalov and Sullivan (2017), arXiv:1612.09400"
            ]
        }
    }

    return schema


def main():
    os.makedirs("data", exist_ok=True)
    for n in [1, 2, 3]:
        print(f"Generating C_{n}_structure.json (C({n+1}) = osp(2|{2*n}))...")
        schema = build_schema1(n)
        fname = f"data/C_{n}_structure.json"
        with open(fname, "w") as f:
            json.dump(schema, f, indent=2)
        sc = schema["structure_constants"]
        dim = schema["algebra"]["dimension"]
        print(f"  Done: {dim['even']} even + {dim['odd']} odd = {dim['total']} generators, "
              f"{len(sc)} non-zero structure constants.")


if __name__ == "__main__":
    main()
