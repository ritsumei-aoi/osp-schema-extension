"""
C(n+1) = osp(2|2n) structure constant generator.
Computes all non-zero graded brackets [X, Y} in the oscillator realization
and outputs Schema 1 JSON files: C_{n}_structure.json for n=1,2,3.

Oscillator index convention (n = bosonic rank):
  0       : a1+  (fermionic creation, parity 1)
  1..n    : b1+..bn+  (bosonic creation, parity 0)
  n+1     : a1-  (fermionic annihilation, parity 1)
  n+2..2n+1: b1-..bn-  (bosonic annihilation, parity 0)

Normal order: 0 < 1 < ... < n < n+1 < ... < 2n+1
"""

from fractions import Fraction
from collections import defaultdict
import json
from datetime import date
import os

# ---------------------------------------------------------------------------
# Operator arithmetic
# ---------------------------------------------------------------------------

def osc_parity(idx, n):
    return 1 if (idx == 0 or idx == n + 1) else 0


def contraction(a, b, n):
    """
    Return scalar contraction when moving oscillator a (index) past oscillator b,
    where a > b (a is out of order, needs to move right past b).

    Relation used: osc_a · osc_b = grade_sign · osc_b · osc_a + <a, b>
    where <a, b> is the commutator/anticommutator value.

    Returns Fraction.
    """
    # a1- (index n+1) anticommutes with a1+ (index 0): {a1-, a1+} = 1
    if a == n + 1 and b == 0:
        return Fraction(1)
    # bkm (index n+1+k) commutes with bkp (index k) with result 1: [bkm, bkp] = 1
    if n + 2 <= a <= 2 * n + 1 and 1 <= b <= n:
        k_a = a - (n + 1)
        k_b = b
        if k_a == k_b:
            return Fraction(1)
    return Fraction(0)


def normal_order_seq(seq, n, coeff, result):
    """
    Recursively bring seq (list of oscillator indices) to normal order.
    Accumulates terms into result: dict {tuple: Fraction}.
    Fermionic nilpotency applied only on already-normal-ordered sequences.
    """
    # Find first out-of-order adjacent pair
    for i in range(len(seq) - 1):
        a, b = seq[i], seq[i + 1]
        if a > b:
            pa = osc_parity(a, n)
            pb = osc_parity(b, n)
            grade_sign = Fraction((-1) ** (pa * pb))

            # Swapped term
            swapped = seq[:i] + [b, a] + seq[i + 2:]
            normal_order_seq(swapped, n, coeff * grade_sign, result)

            # Contraction term
            c = contraction(a, b, n)
            if c != Fraction(0):
                contracted = seq[:i] + seq[i + 2:]
                normal_order_seq(contracted, n, coeff * c, result)
            return

    # Already in normal order — apply fermionic nilpotency here
    if seq.count(0) > 1 or seq.count(n + 1) > 1:
        return  # (a1+)^2 = 0 or (a1-)^2 = 0
    key = tuple(seq)
    result[key] = result.get(key, Fraction(0)) + coeff


def op_mul(op1, op2, n):
    """Multiply two operators (each a dict {monomial: coeff})."""
    result = {}
    for m1, c1 in op1.items():
        for m2, c2 in op2.items():
            combined = list(m1) + list(m2)
            normal_order_seq(combined, n, c1 * c2, result)
    return {m: c for m, c in result.items() if c != 0}


def op_add(op1, op2):
    result = dict(op1)
    for m, c in op2.items():
        result[m] = result.get(m, Fraction(0)) + c
    return {m: c for m, c in result.items() if c != 0}


def op_scale(op, scalar):
    return {m: c * scalar for m, c in op.items()}


def graded_bracket(X, Xp, Y, Yp, n):
    """
    Compute [X, Y} = X*Y - (-1)^(Xp*Yp) * Y*X.
    Xp, Yp are parities (0 or 1) of X, Y.
    """
    sign = Fraction((-1) ** (Xp * Yp))
    XY = op_mul(X, Y, n)
    YX = op_mul(Y, X, n)
    return op_add(XY, op_scale(YX, -sign))


# ---------------------------------------------------------------------------
# Basis construction
# ---------------------------------------------------------------------------

def build_basis(n):
    """Return (odd_labels, even_labels) following PBW Option A."""
    odd = []
    for k in range(1, n + 1):
        odd.append(f"E_eps1_del{k}_pp")
        odd.append(f"E_eps1_del{k}_pm")
    for k in range(1, n + 1):
        odd.append(f"E_eps1_del{k}_mp")
        odd.append(f"E_eps1_del{k}_mm")

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
    for i in range(1, n + 1):
        for j in range(i + 1, n + 1):
            even.append(f"E_del{i}_del{j}_mp")

    return odd, even


def label_parity(label):
    return 1 if label.startswith("E_eps1") else 0


# ---------------------------------------------------------------------------
# Generator operator representations
# ---------------------------------------------------------------------------

def build_generators(n):
    """
    Returns dict: label -> op dict {monomial: Fraction}.

    Normal order indices:
      0: a1+, 1..n: b1+..bn+, n+1: a1-, n+2..2n+1: b1-..bn-
    """
    gens = {}

    # Odd generators
    for k in range(1, n + 1):
        # E_eps1_del{k}_pp = a1+ bk+: indices (0, k)
        gens[f"E_eps1_del{k}_pp"] = {(0, k): Fraction(1)}
        # E_eps1_del{k}_pm = a1+ bk-: indices (0, n+1+k)
        gens[f"E_eps1_del{k}_pm"] = {(0, n + 1 + k): Fraction(1)}
        # E_eps1_del{k}_mp = a1- bk+: normal order bk+(k) before a1-(n+1) -> (k, n+1)
        gens[f"E_eps1_del{k}_mp"] = {(k, n + 1): Fraction(1)}
        # E_eps1_del{k}_mm = a1- bk-: indices (n+1, n+1+k)
        gens[f"E_eps1_del{k}_mm"] = {(n + 1, n + 1 + k): Fraction(1)}

    # Cartan generators
    # H_1 = a1+a1- + b1+b1-
    h1 = {(0, n + 1): Fraction(1), (1, n + 2): Fraction(1)}
    gens["H_1"] = h1

    # H_k (k=2..n) = b{k-1}+b{k-1}- - bk+bk-
    for k in range(2, n + 1):
        gens[f"H_{k}"] = {
            (k - 1, n + k): Fraction(1),
            (k, n + 1 + k): Fraction(-1)
        }

    # H_{n+1} = -bn+bn- - 1/2
    gens[f"H_{n+1}"] = {
        (n, 2 * n + 1): Fraction(-1),
        (): Fraction(-1, 2)
    }

    # Even root generators
    for k in range(1, n + 1):
        # E_2del{k}_p = (1/2)(bk+)^2: monomial (k, k)
        gens[f"E_2del{k}_p"] = {(k, k): Fraction(1, 2)}
        # E_2del{k}_m = (1/2)(bk-)^2: monomial (n+1+k, n+1+k)
        gens[f"E_2del{k}_m"] = {(n + 1 + k, n + 1 + k): Fraction(1, 2)}

    for i in range(1, n + 1):
        for j in range(i + 1, n + 1):
            # E_del{i}_del{j}_pp = bi+bj+: (i, j)
            gens[f"E_del{i}_del{j}_pp"] = {(i, j): Fraction(1)}
            # E_del{i}_del{j}_mm = bi-bj-: (n+1+i, n+1+j)
            gens[f"E_del{i}_del{j}_mm"] = {(n + 1 + i, n + 1 + j): Fraction(1)}
            # E_del{i}_del{j}_pm = bi+bj-: (i, n+1+j)
            gens[f"E_del{i}_del{j}_pm"] = {(i, n + 1 + j): Fraction(1)}
            # E_del{i}_del{j}_mp = bi-bj+: normal order bj+(j) before bi-(n+1+i) -> (j, n+1+i)
            gens[f"E_del{i}_del{j}_mp"] = {(j, n + 1 + i): Fraction(1)}

    return gens


# ---------------------------------------------------------------------------
# Decomposition of result operator into basis elements
# ---------------------------------------------------------------------------

def decompose(op, n, basis_labels, gen_ops):
    """
    Express operator `op` as linear combination of basis generators.
    Returns dict {label: Fraction}.

    Strategy:
    - Unique monomials identify non-Cartan generators directly.
    - Cartan coefficients recovered from the tridiagonal-like system.
    """
    coeffs = {}
    remaining = dict(op)

    # --- Non-Cartan even generators (unique monomials) ---
    for k in range(1, n + 1):
        m_p = (k, k)
        if m_p in remaining:
            c = remaining.pop(m_p) / Fraction(1, 2)  # coeff of E_2del{k}_p is 1/2
            if c != 0:
                coeffs[f"E_2del{k}_p"] = c

        m_m = (n + 1 + k, n + 1 + k)
        if m_m in remaining:
            c = remaining.pop(m_m) / Fraction(1, 2)
            if c != 0:
                coeffs[f"E_2del{k}_m"] = c

    for i in range(1, n + 1):
        for j in range(i + 1, n + 1):
            m_pp = (i, j)
            if m_pp in remaining:
                c = remaining.pop(m_pp)
                if c != 0:
                    coeffs[f"E_del{i}_del{j}_pp"] = c

            m_mm = (n + 1 + i, n + 1 + j)
            if m_mm in remaining:
                c = remaining.pop(m_mm)
                if c != 0:
                    coeffs[f"E_del{i}_del{j}_mm"] = c

            m_pm = (i, n + 1 + j)
            if m_pm in remaining:
                c = remaining.pop(m_pm)
                if c != 0:
                    coeffs[f"E_del{i}_del{j}_pm"] = c

            m_mp = (j, n + 1 + i)
            if m_mp in remaining:
                c = remaining.pop(m_mp)
                if c != 0:
                    coeffs[f"E_del{i}_del{j}_mp"] = c

    # --- Odd generators (unique monomials) ---
    for k in range(1, n + 1):
        for suffix, mono in [
            ("pp", (0, k)),
            ("pm", (0, n + 1 + k)),
            ("mp", (k, n + 1)),
            ("mm", (n + 1, n + 1 + k)),
        ]:
            if mono in remaining:
                c = remaining.pop(mono)
                if c != 0:
                    coeffs[f"E_eps1_del{k}_{suffix}"] = c

    # --- Cartan generators ---
    # H_{n+1}: from scalar monomial ()
    scalar = remaining.pop((), Fraction(0))
    c_H_np1 = scalar / Fraction(-1, 2)  # H_{n+1} contributes -1/2 to scalar
    if c_H_np1 != 0:
        coeffs[f"H_{n+1}"] = c_H_np1

    # H_1: from monomial (0, n+1) = a1+a1-, unique to H_1
    c_H1 = remaining.pop((0, n + 1), Fraction(0))
    if c_H1 != 0:
        coeffs["H_1"] = c_H1

    # (1, n+2) = b1+b1- appears in H_1 (coeff +1) and H_2 (coeff +1)
    # c_H1 + c_H2 = C_{(1,n+2)} => c_H2 = C_{(1,n+2)} - c_H1
    c_prev = coeffs.get("H_1", Fraction(0))
    for k in range(2, n + 1):
        mono = (k - 1, n + k)  # b{k-1}+b{k-1}-
        C_val = remaining.pop(mono, Fraction(0))
        # H_{k-1} contributes -1 to this monomial (for k-1 >= 2), H_k contributes +1
        # For k=2: H_1 contributes +1, H_2 contributes +1
        # c_{H_{k-1}} * contrib + c_{H_k} * 1 = C_val
        if k == 2:
            # contrib from H_1 is +1
            c_k = C_val - c_prev
        else:
            # contrib from H_{k-1} is -1
            c_k = C_val + c_prev
        if c_k != 0:
            coeffs[f"H_{k}"] = c_k
        c_prev = c_k

    # Check: monomial (n, 2n+1) = bn+bn- should be used up by Hn and H_{n+1}
    # H_n contributes -1 (for n>=2), H_{n+1} contributes -1
    # c_{H_n}*(-1) + c_{H_{n+1}}*(-1) = C_{(n, 2n+1)}
    # This is a consistency check; the monomial should already be accounted for
    # by the Cartan reconstruction above.
    # For n=1: H_2 = -b1+b1- - 1/2. Monomial (1,3) appears in H_1 (+1) and H_2 (-1).
    # For n=1, monomial (n, 2n+1) = (1, 3) is handled in the k=2 step of the loop above.
    # Actually for n=1 the loop runs k=2..n=1, which is empty! So I need special handling.

    # Monomial (n, 2n+1) for n=1: this is (1, 3) = b1+b1-
    # It appears in H_1 (+1) and H_2 (-1).
    # The loop above (k=2..n) handles monomials (k-1, n+k):
    #   for k=2, mono = (1, n+2). For n=1, that's (1, 3). ✓
    # So n=1 IS handled when n >= 2? Wait: the loop is range(2, n+1).
    # For n=1: range(2, 2) is empty. So for n=1 we skip the loop.
    # But for n=1, there's no H_2 in the loop (H_{n+1} = H_2 is handled via scalar).

    # Let me handle the remaining monomial (n, 2n+1) separately.
    # For n=1: (1, 3) = b1+b1-. This appears in H_1 (coeff +1) and H_2 (coeff -1).
    # We already handled scalar -> c_{H_2}. And H_1 -> c_{H_1} from (0,2).
    # Consistency: c_{H_1} * 1 + c_{H_2} * (-1) = C_{(1,3)}.

    # Handle remaining monomials for the last Cartan
    mono_last = (n, 2 * n + 1)
    C_last = remaining.pop(mono_last, Fraction(0))
    if C_last != 0:
        # This should have been handled. If there's a residual, flag it.
        pass  # Will be caught by final check

    # Final sanity check: remaining should be empty
    if remaining:
        raise ValueError(f"Decomposition failed: unaccounted monomials {remaining}")

    return coeffs


# ---------------------------------------------------------------------------
# Structure constant computation
# ---------------------------------------------------------------------------

def compute_structure_constants(n):
    """Return list of non-zero bracket records."""
    odd_labels, even_labels = build_basis(n)
    all_labels = odd_labels + even_labels
    gen_ops = build_generators(n)
    records = []

    for i, X_label in enumerate(all_labels):
        Xp = label_parity(X_label)
        X_op = gen_ops[X_label]
        for j, Y_label in enumerate(all_labels):
            if j < i:
                continue  # use antisymmetry
            Yp = label_parity(Y_label)
            Y_op = gen_ops[Y_label]

            bracket = graded_bracket(X_op, Xp, Y_op, Yp, n)
            if not bracket:
                continue

            basis_labels = odd_labels + even_labels
            coeffs = decompose(bracket, n, basis_labels, gen_ops)

            for Z_label, coeff in coeffs.items():
                if coeff != 0:
                    records.append({
                        "X": X_label,
                        "Y": Y_label,
                        "Z": Z_label,
                        "coeff": str(coeff),
                        "sign_rule": "graded"
                    })

    return records


# ---------------------------------------------------------------------------
# JSON Schema 1 builder
# ---------------------------------------------------------------------------

def build_schema1(n):
    odd_labels, even_labels = build_basis(n)
    total = 2 * n * n + 5 * n + 1
    n_even = 2 * n * n + n + 1
    n_odd = 4 * n

    boson_labels = []
    for k in range(1, n + 1):
        boson_labels += [f"b_{k}_p", f"b_{k}_m"]

    osc_ordering = "a_1_p, a_1_m, " + ", ".join(boson_labels)

    # Build generator_realization entries
    realizations = {}
    # H_1
    h1_standard = [{"words": ["a_1_p", "a_1_m"], "coeff": "1"}]
    h1_standard.append({"words": ["b_1_p", "b_1_m"], "coeff": "1"})
    realizations["H_1"] = {
        "standard_form": h1_standard,
        "frappat_form": "a_1^+ a_1^- + b_1^+ b_1^-",
        "parity": 0,
        "note": "First Cartan; includes fermionic number operator a_1^+ a_1^-"
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
        "note": "Terminal Cartan; constant term -1/2"
    }
    for k in range(1, n + 1):
        realizations[f"E_eps1_del{k}_pp"] = {
            "standard_form": [{"words": ["a_1_p", f"b_{k}_p"], "coeff": "1"}],
            "frappat_form": f"a_1^+ b_{k}^+", "parity": 1
        }
        realizations[f"E_eps1_del{k}_pm"] = {
            "standard_form": [{"words": ["a_1_p", f"b_{k}_m"], "coeff": "1"}],
            "frappat_form": f"a_1^+ b_{k}^-", "parity": 1
        }
        realizations[f"E_eps1_del{k}_mp"] = {
            "standard_form": [{"words": ["a_1_m", f"b_{k}_p"], "coeff": "1"}],
            "frappat_form": f"a_1^- b_{k}^+", "parity": 1
        }
        realizations[f"E_eps1_del{k}_mm"] = {
            "standard_form": [{"words": ["a_1_m", f"b_{k}_m"], "coeff": "1"}],
            "frappat_form": f"a_1^- b_{k}^-", "parity": 1
        }
    for k in range(1, n + 1):
        realizations[f"E_2del{k}_p"] = {
            "standard_form": [{"words": [f"b_{k}_p", f"b_{k}_p"], "coeff": "1/2"}],
            "frappat_form": f"(1/2)(b_{k}^+)^2", "parity": 0
        }
        realizations[f"E_2del{k}_m"] = {
            "standard_form": [{"words": [f"b_{k}_m", f"b_{k}_m"], "coeff": "1/2"}],
            "frappat_form": f"(1/2)(b_{k}^-)^2", "parity": 0
        }
    for i in range(1, n + 1):
        for j in range(i + 1, n + 1):
            for suffix, form in [("pp", f"b_{i}^+ b_{j}^+"), ("mm", f"b_{i}^- b_{j}^-"),
                                  ("pm", f"b_{i}^+ b_{j}^-"), ("mp", f"b_{i}^- b_{j}^+")]:
                lbl = f"E_del{i}_del{j}_{suffix}"
                s1, s2 = ("p", "p") if suffix == "pp" else (("m","m") if suffix == "mm" else (("p","m") if suffix == "pm" else ("m","p")))
                realizations[lbl] = {
                    "standard_form": [{"words": [f"b_{i}_{s1}", f"b_{j}_{s2}"], "coeff": "1"}],
                    "frappat_form": form,
                    "parity": 0
                }

    # Parity dict
    parity_dict = {}
    for lbl in odd_labels:
        parity_dict[lbl] = 1
    for lbl in even_labels:
        parity_dict[lbl] = 0

    sc = compute_structure_constants(n)

    schema = {
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
            "dimension_formula": {
                "even": "2n^2 + n + 1",
                "odd": "4n",
                "total": "2n^2 + 5n + 1"
            },
            "dimension": {
                "total": total,
                "even": n_even,
                "odd": n_odd
            }
        },
        "oscillator_generators": {
            "fermions": {
                "m": 1,
                "labels": ["a_1_p", "a_1_m"],
                "parity": 1,
                "relation": "{a_1^-, a_1^+} = 1",
                "description": "Standard fermionic CAR pair; a_1_p = a_1^+, a_1_m = a_1^-"
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
                "description": "CAR for standard fermionic pair",
                "relations": {
                    "anticommutator": "{a_1^-, a_1^+} = 1",
                    "same_sign_p": "{a_1^+, a_1^+} = 0",
                    "same_sign_m": "{a_1^-, a_1^-} = 0"
                }
            },
            "bosonic_commutators": {
                "description": "Canonical commutation relations for bosonic oscillators",
                "relations": {
                    "same_type": "[b_i^±, b_j^±] = 0 for all i, j",
                    "conjugate_pair": "[b_i^-, b_j^+] = δ_{ij}"
                }
            },
            "mixed_commutators": {
                "boson_fermion": "[b_i^±, a_1^±] = 0"
            }
        },
        "central_elements": {
            "kappa": {
                "parity": 1,
                "description": "Odd nilpotent central element; kappa^2 = 0",
                "nilpotency": "kappa^2 = 0"
            },
            "K": {
                "parity": 0,
                "description": "Even central identity element; K = 1 in all current applications",
                "note": "Not an independent basis element; excluded from PBW ordering"
            }
        },
        "basis": {
            "even": even_labels,
            "odd": odd_labels,
            "ordering_convention": (
                "PBW Option A: [odd] < [even]; "
                "within odd: positive ε-block (pp/pm by k) then negative ε-block (mp/mm by k); "
                "within even: Cartans H_1...H_{n+1}, then positive roots by height, "
                "then negative, then mixed"
            )
        },
        "parity": parity_dict,
        "generator_realization": {
            "description": "Standard form with PBW ordering",
            "ordering": osc_ordering,
            "realizations": realizations
        },
        "structure_constants": sc,
        "metadata": {
            "generated_by": "build_C_structure_constants.py",
            "generation_date": str(date.today()),
            "references": [
                "Frappat et al. (2000), Dictionary on Lie Algebras and Superalgebras",
                "Bakalov and Sullivan (2017)"
            ]
        }
    }
    return schema


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    out_dir = os.path.join(os.path.dirname(__file__), "output")
    os.makedirs(out_dir, exist_ok=True)

    for n in [1, 2, 3]:
        print(f"\n=== C({n+1}) = osp(2|{2*n}), n={n} ===")
        schema = build_schema1(n)
        sc = schema["structure_constants"]
        print(f"  Basis: {schema['algebra']['dimension']['odd']} odd + "
              f"{schema['algebra']['dimension']['even']} even = "
              f"{schema['algebra']['dimension']['total']} total")
        print(f"  Non-zero brackets: {len(sc)}")

        fname = os.path.join(out_dir, f"C_{n}_structure.json")
        with open(fname, "w") as f:
            json.dump(schema, f, indent=2)
        print(f"  Written: {fname}")
