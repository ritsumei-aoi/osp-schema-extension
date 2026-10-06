"""
C(n+1) = osp(2|2n) generator definitions, basis, and structure-constant generator.

Builds, for a given bosonic rank n:
  * the even/odd basis label lists (PBW order from handover/notation.md, Issue I01),
  * the oscillator realization of every generator (as osc_algebra polynomials),
  * the parity map,
  * a decomposition routine mapping any bracket result back onto the basis (+ central K),
  * the full Schema-1 structure constants, written as C_{n}_structure.json.

Run:  python3 src/C_generators.py           # generates data/C_1,2,3_structure.json
"""

from __future__ import annotations
import json
import os
import sys
from datetime import date
import sympy as sp

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import osc_algebra as oa

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")


# --------------------------------------------------------------------------
# Basis construction
# --------------------------------------------------------------------------

def even_labels(n):
    """Even basis in PBW order (Option A): Cartan, then _p/_pp, _m/_mm, _pm, _mp blocks."""
    labels = [f"H_{i}" for i in range(1, n + 2)]          # H_1 .. H_{n+1}
    labels += [f"E_2del{k}_p" for k in range(1, n + 1)]
    labels += [f"E_del{i}_del{j}_pp" for i in range(1, n + 1) for j in range(i + 1, n + 1)]
    labels += [f"E_2del{k}_m" for k in range(1, n + 1)]
    labels += [f"E_del{i}_del{j}_mm" for i in range(1, n + 1) for j in range(i + 1, n + 1)]
    labels += [f"E_del{i}_del{j}_pm" for i in range(1, n + 1) for j in range(i + 1, n + 1)]
    labels += [f"E_del{i}_del{j}_mp" for i in range(1, n + 1) for j in range(i + 1, n + 1)]
    return labels


def odd_labels(n):
    """Odd basis in PBW order: sign blocks pp, pm, mp, mm, each over k=1..n."""
    labels = []
    for block in ("pp", "pm", "mp", "mm"):
        labels += [f"E_eps1_del{k}_{block}" for k in range(1, n + 1)]
    return labels


def realizations(n):
    """Return {label: osc_algebra poly} for every basis generator."""
    R = {}
    # Cartan
    H1 = oa.poly_zero()
    oa.poly_add(H1, oa.mono([oa.a_p(), oa.a_m()], 1))
    oa.poly_add(H1, oa.mono([oa.b_p(1), oa.b_m(1)], 1))
    R["H_1"] = H1
    for k in range(2, n + 1):
        Hk = oa.poly_zero()
        oa.poly_add(Hk, oa.mono([oa.b_p(k - 1), oa.b_m(k - 1)], 1))
        oa.poly_add(Hk, oa.mono([oa.b_p(k), oa.b_m(k)], -1))
        R[f"H_{k}"] = Hk
    Hn1 = oa.poly_zero()
    oa.poly_add(Hn1, oa.mono([oa.b_p(n), oa.b_m(n)], -1))
    oa.poly_add(Hn1, oa.mono([], sp.Rational(-1, 2)))  # constant -1/2
    R[f"H_{n + 1}"] = Hn1
    # sp(2n) root vectors
    for k in range(1, n + 1):
        R[f"E_2del{k}_p"] = oa.mono([oa.b_p(k), oa.b_p(k)], 1)
        R[f"E_2del{k}_m"] = oa.mono([oa.b_m(k), oa.b_m(k)], 1)
    for i in range(1, n + 1):
        for j in range(i + 1, n + 1):
            R[f"E_del{i}_del{j}_pp"] = oa.mono([oa.b_p(i), oa.b_p(j)], 1)
            R[f"E_del{i}_del{j}_mm"] = oa.mono([oa.b_m(i), oa.b_m(j)], 1)
            R[f"E_del{i}_del{j}_pm"] = oa.mono([oa.b_p(i), oa.b_m(j)], 1)
            R[f"E_del{i}_del{j}_mp"] = oa.mono([oa.b_m(i), oa.b_p(j)], 1)
    # odd generators
    for k in range(1, n + 1):
        R[f"E_eps1_del{k}_pp"] = oa.mono([oa.a_p(), oa.b_p(k)], 1)
        R[f"E_eps1_del{k}_pm"] = oa.mono([oa.a_p(), oa.b_m(k)], 1)
        R[f"E_eps1_del{k}_mp"] = oa.mono([oa.a_m(), oa.b_p(k)], 1)
        R[f"E_eps1_del{k}_mm"] = oa.mono([oa.a_m(), oa.b_m(k)], 1)
    return R


def parity_map(n):
    P = {}
    for lab in even_labels(n):
        P[lab] = 0
    for lab in odd_labels(n):
        P[lab] = 1
    return P


# --------------------------------------------------------------------------
# Decomposition of a bracket result back onto the basis (+ central K)
# --------------------------------------------------------------------------

def _monomial_index(n):
    """Map the unique normal-ordered word of each root generator -> label."""
    R = realizations(n)
    idx = {}
    cartan = {f"H_{i}" for i in range(1, n + 2)}
    for lab, poly in R.items():
        if lab in cartan:
            continue
        assert len(poly) == 1, f"{lab} not single-monomial"
        (kf, word), coeff = next(iter(poly.items()))
        assert kf == 0 and coeff == 1, f"{lab} unexpected realization"
        idx[word] = lab
    return idx


def _cartan_matrix(n):
    """Columns = operator-parts of H_1..H_{n+1} in basis (Na, N1..Nn)."""
    dim = n + 1
    M = sp.zeros(dim, dim)   # rows: Na,N1..Nn ; cols: H_1..H_{n+1}
    # row 0 = Na, rows 1..n = N1..Nn
    # H_1 = Na + N1
    M[0, 0] = 1
    M[1, 0] = 1
    # H_k (k=2..n) = N_{k-1} - N_k   -> column index k-1
    for k in range(2, n + 1):
        M[k - 1, k - 1] = 1
        M[k, k - 1] = -1
    # H_{n+1} = -N_n  -> column index n
    M[n, n] = -1
    return M


def decompose(poly, n, allow_kappa=False):
    """
    Decompose a normal-ordered osc_algebra poly onto the C(n+1) basis.

    Returns dict {label_or_K: sympy coeff}.  If allow_kappa is False, any kappa-flagged term
    raises; if True, kappa terms are ignored here (handled separately by the gamma builder).
    Raises ValueError if a term does not correspond to any basis generator (non-closure).
    """
    mono_idx = _monomial_index(n)
    # accumulate number-operator coefficients and constant
    na = sp.Integer(0)
    nk = [sp.Integer(0)] * (n + 1)   # nk[1..n]
    const = sp.Integer(0)
    out = {}
    a_num_word = (oa.a_p(), oa.a_m())
    for (kf, word), coeff in poly.items():
        if kf == 1:
            if allow_kappa:
                continue
            raise ValueError("unexpected kappa term in structure-constant decomposition")
        if len(word) == 0:
            const += coeff
        elif word == a_num_word:
            na += coeff
        elif len(word) == 2 and word[0][0] == 'b' and word[1][0] == 'b' \
                and word[0][2] == +1 and word[1][2] == -1 and word[0][1] == word[1][1]:
            nk[word[0][1]] += coeff
        elif word in mono_idx:
            lab = mono_idx[word]
            out[lab] = out.get(lab, sp.Integer(0)) + coeff
        else:
            raise ValueError(f"non-closure: term {oa.poly_str({(kf, word): coeff})} "
                             f"not a basis generator")
    # solve Cartan part
    if na != 0 or any(nk[1:]):
        M = _cartan_matrix(n)
        t = sp.zeros(n + 1, 1)
        t[0] = na
        for k in range(1, n + 1):
            t[k] = nk[k]
        lam = M.LUsolve(t)
        for i in range(1, n + 2):
            li = sp.nsimplify(lam[i - 1])
            if li != 0:
                out[f"H_{i}"] = out.get(f"H_{i}", sp.Integer(0)) + li
        # constant contributed by H_{n+1} is -1/2 * lambda_{n+1}
        const = const - lam[n] * sp.Rational(-1, 2)
    if const != 0:
        out["K"] = out.get("K", sp.Integer(0)) + const
    # drop zeros
    return {k: v for k, v in out.items() if v != 0}


# --------------------------------------------------------------------------
# Structure constants
# --------------------------------------------------------------------------

def pbw_order(n):
    """Full PBW order (kappa <) odd < even, used to canonicalize X <= Y."""
    return odd_labels(n) + even_labels(n)


def structure_constants(n):
    R = realizations(n)
    P = parity_map(n)
    order = pbw_order(n)
    pos = {lab: i for i, lab in enumerate(order)}
    records = []
    for a in range(len(order)):
        for b in range(a, len(order)):
            X, Y = order[a], order[b]
            br = oa.graded_commutator(R[X], P[X], R[Y], P[Y])
            comps = decompose(br, n)
            for Z, coeff in sorted(comps.items(), key=lambda kv: pos.get(kv[0], 10 ** 9)):
                records.append({
                    "X": X, "Y": Y, "Z": Z,
                    "coeff": str(coeff),
                    "sign_rule": "graded",
                })
    return records


# --------------------------------------------------------------------------
# JSON assembly
# --------------------------------------------------------------------------

def _word_to_labels(word):
    out = []
    for (kind, index, sign) in word:
        s = "p" if sign == +1 else "m"
        out.append(f"a_1_{s}" if kind == 'a' else f"b_{index}_{s}")
    return out


def realization_json(n):
    R = realizations(n)
    P = parity_map(n)
    out = {}
    for lab in even_labels(n) + odd_labels(n):
        terms = []
        for (kf, word), coeff in sorted(R[lab].items(), key=lambda kv: len(kv[0][1])):
            terms.append({"words": _word_to_labels(word), "coeff": str(coeff)})
        out[lab] = {"standard_form": terms, "parity": P[lab]}
    return out


def build_schema1(n):
    ev, od = even_labels(n), odd_labels(n)
    even_dim, odd_dim = len(ev), len(od)
    assert even_dim == 2 * n ** 2 + n + 1, (n, even_dim)
    assert odd_dim == 4 * n, (n, odd_dim)
    P = parity_map(n)
    return {
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
                "formula": {"even": "2n^2 + n + 1", "odd": "4n", "total": "2n^2 + 5n + 1"},
                "total": even_dim + odd_dim,
                "even": even_dim,
                "odd": odd_dim,
            },
        },
        "oscillator_generators": {
            "fermions": {"m": 1, "count": 2, "labels": ["a_1_p", "a_1_m"],
                         "description": "Standard fermionic CAR pair a_1^±; {a_1^-,a_1^+}=1, (a_1^±)^2=0."},
            "bosons": {"n": n, "count": 2 * n,
                       "labels": [f"b_{k}_{s}" for k in range(1, n + 1) for s in ("p", "m")],
                       "description": "Bosonic oscillators b_k^± (k=1..n), [b_k^-,b_l^+]=δ_kl."},
        },
        "oscillator_relations": {
            "fermionic_anticommutators": {
                "description": "Standard CAR pair",
                "relations": {"car_pair": "{a_1^-, a_1^+} = 1",
                              "nilpotency": "(a_1^+)^2 = 0, (a_1^-)^2 = 0"},
            },
            "bosonic_commutators": {
                "description": "Canonical commutation relations",
                "relations": {"same_type": "[b_i^±, b_j^±] = 0",
                              "conjugate_pair": "[b_i^-, b_j^+] = δ_ij"},
            },
            "mixed_commutators": {"boson_fermion": "[b_k^±, a_1^σ] = 0 (undeformed; deformed in Schema 2)"},
        },
        "central_elements": {
            "kappa": {"label": "kappa", "parity": 1, "nilpotency": "kappa^2 = 0",
                      "description": "Odd central element; carrier of the inhomogeneous deformation."},
            "K": {"label": "K", "parity": 0, "value": "1",
                  "description": "Even central identity = scalar 1; excluded from PBW basis."},
        },
        "basis": {"even": ev, "odd": od,
                  "ordering_convention": "PBW: kappa < [odd] < [even]  (K = 1 excluded)"},
        "parity": P,
        "generator_realization": {
            "description": "Oscillator realization, PBW normal-ordered",
            "ordering": "a_1_p < b_1_p < ... < a_1_m < b_1_m < ...",
            "realizations": realization_json(n),
        },
        "structure_constants": structure_constants(n),
        "metadata": {
            "generated_by": "src/C_generators.py",
            "generation_date": date.today().isoformat(),
            "algebra": "C(n+1) = osp(2|2n)",
            "references": [
                "Frappat, Sciarrino, Sorba (2000), Dictionary on Lie Algebras and Superalgebras",
                "Bakalov and Sullivan (2017)",
            ],
        },
    }


def generate_all():
    os.makedirs(DATA_DIR, exist_ok=True)
    for n in (1, 2, 3):
        data = build_schema1(n)
        path = os.path.join(DATA_DIR, f"C_{n}_structure.json")
        with open(path, "w") as f:
            json.dump(data, f, indent=2)
        print(f"wrote {path}  (even={data['algebra']['dimension']['even']}, "
              f"odd={data['algebra']['dimension']['odd']}, "
              f"#structure_constants={len(data['structure_constants'])})")


if __name__ == "__main__":
    generate_all()
