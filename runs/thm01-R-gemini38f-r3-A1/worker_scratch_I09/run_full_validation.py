from fractions import Fraction
from typing import Dict, List, Tuple
from collections import defaultdict
import time

def parity_of(osc: str) -> int:
    return 1 if osc.startswith('a_') else 0

def normal_order_word(word: Tuple[str, ...]) -> Dict[Tuple[str, ...], Fraction]:
    def osc_key(osc: str):
        if osc == 'a_1_p': return (0, 0, 0)
        if osc == 'a_1_m': return (0, 1, 0)
        parts = osc.split('_')
        return (1, int(parts[1]), 0 if parts[2] == 'p' else 1)

    current = {word: Fraction(1, 1)}
    while True:
        next_dict = defaultdict(Fraction)
        all_sorted = True
        for w, coeff in current.items():
            if coeff == 0:
                continue
            found = False
            for i in range(len(w) - 1):
                o1, o2 = w[i], w[i+1]
                if o1 == o2 and parity_of(o1) == 1:
                    found = True
                    all_sorted = False
                    break
                elif osc_key(o1) > osc_key(o2):
                    found = True
                    all_sorted = False
                    if o1 == 'a_1_m' and o2 == 'a_1_p':
                        next_dict[w[:i] + (o2, o1) + w[i+2:]] += -coeff
                        next_dict[w[:i] + w[i+2:]] += coeff
                    elif o1.startswith('b_') and o2.startswith('b_'):
                        p1, p2 = o1.split('_'), o2.split('_')
                        j, s1 = int(p1[1]), p1[2]
                        k, s2 = int(p2[1]), p2[2]
                        if s1 == 'm' and s2 == 'p' and j == k:
                            next_dict[w[:i] + (o2, o1) + w[i+2:]] += coeff
                            next_dict[w[:i] + w[i+2:]] += coeff
                        else:
                            next_dict[w[:i] + (o2, o1) + w[i+2:]] += coeff
                    elif o1.startswith('b_') and o2.startswith('a_'):
                        next_dict[w[:i] + (o2, o1) + w[i+2:]] += coeff
                    else:
                        raise ValueError(f"Unhandled pair: {o1}, {o2}")
                    break
            if not found:
                next_dict[w] += coeff
        if all_sorted:
            return {k: v for k, v in current.items() if v != 0}
        current = next_dict

def multiply_poly(p1: Dict[Tuple[str, ...], Fraction], p2: Dict[Tuple[str, ...], Fraction]) -> Dict[Tuple[str, ...], Fraction]:
    res = defaultdict(Fraction)
    for w1, c1 in p1.items():
        for w2, c2 in p2.items():
            c = c1 * c2
            ordered = normal_order_word(w1 + w2)
            for ow, oc in ordered.items():
                res[ow] += c * oc
    return {k: v for k, v in res.items() if v != 0}

def add_poly(p1: Dict[Tuple[str, ...], Fraction], p2: Dict[Tuple[str, ...], Fraction], scale2: Fraction = Fraction(1, 1)) -> Dict[Tuple[str, ...], Fraction]:
    res = defaultdict(Fraction, p1)
    for w, c in p2.items():
        res[w] += c * scale2
    return {k: v for k, v in res.items() if v != 0}

def graded_commutator(X: Dict[Tuple[str, ...], Fraction], pX: int, Y: Dict[Tuple[str, ...], Fraction], pY: int) -> Dict[Tuple[str, ...], Fraction]:
    XY = multiply_poly(X, Y)
    YX = multiply_poly(Y, X)
    sign = -Fraction(1, 1) if (pX * pY) % 2 == 1 else Fraction(1, 1)
    return add_poly(XY, YX, -sign)

def get_generators(n: int):
    even_basis = []
    odd_basis = []
    realizations = {}
    parity = {}

    # 1. Cartans H_1, ..., H_{n+1}
    realizations['H_1'] = {
        ('a_1_p', 'a_1_m'): Fraction(1, 1),
        ('b_1_p', 'b_1_m'): Fraction(1, 1)
    }
    even_basis.append('H_1')
    parity['H_1'] = 0

    for k in range(2, n + 1):
        name = f"H_{k}"
        realizations[name] = {
            (f"b_{k-1}_p", f"b_{k-1}_m"): Fraction(1, 1),
            (f"b_{k}_p", f"b_{k}_m"): Fraction(-1, 1)
        }
        even_basis.append(name)
        parity[name] = 0

    name_last = f"H_{n+1}"
    realizations[name_last] = {
        (f"b_{n}_p", f"b_{n}_m"): Fraction(-1, 1),
        (): Fraction(-1, 2)
    }
    even_basis.append(name_last)
    parity[name_last] = 0

    # 2. Positive long roots
    for k in range(1, n + 1):
        name = f"E_2del{k}_p"
        realizations[name] = {(f"b_{k}_p", f"b_{k}_p"): Fraction(1, 1)}
        even_basis.append(name)
        parity[name] = 0

    # 3. Positive cross roots
    for i in range(1, n + 1):
        for j in range(i + 1, n + 1):
            name = f"E_del{i}_del{j}_pp"
            realizations[name] = {(f"b_{i}_p", f"b_{j}_p"): Fraction(1, 1)}
            even_basis.append(name)
            parity[name] = 0

    # 4. Negative long roots
    for k in range(1, n + 1):
        name = f"E_2del{k}_m"
        realizations[name] = {(f"b_{k}_m", f"b_{k}_m"): Fraction(1, 1)}
        even_basis.append(name)
        parity[name] = 0

    # 5. Negative cross roots
    for i in range(1, n + 1):
        for j in range(i + 1, n + 1):
            name = f"E_del{i}_del{j}_mm"
            realizations[name] = {(f"b_{i}_m", f"b_{j}_m"): Fraction(1, 1)}
            even_basis.append(name)
            parity[name] = 0

    # 6. Mixed cross roots
    for i in range(1, n + 1):
        for j in range(i + 1, n + 1):
            name_pm = f"E_del{i}_del{j}_pm"
            realizations[name_pm] = {(f"b_{i}_p", f"b_{j}_m"): Fraction(1, 1)}
            even_basis.append(name_pm)
            parity[name_pm] = 0

            name_mp = f"E_del{i}_del{j}_mp"
            realizations[name_mp] = {(f"b_{i}_m", f"b_{j}_p"): Fraction(1, 1)}
            even_basis.append(name_mp)
            parity[name_mp] = 0

    # 7. Odd roots (Option 1: Charge-Stratified)
    for k in range(1, n + 1):
        name = f"E_eps1_del{k}_pp"
        realizations[name] = {('a_1_p', f"b_{k}_p"): Fraction(1, 1)}
        odd_basis.append(name)
        parity[name] = 1
    for k in range(1, n + 1):
        name = f"E_eps1_del{k}_pm"
        realizations[name] = {('a_1_p', f"b_{k}_m"): Fraction(1, 1)}
        odd_basis.append(name)
        parity[name] = 1
    for k in range(1, n + 1):
        name = f"E_eps1_del{k}_mp"
        realizations[name] = {('a_1_m', f"b_{k}_p"): Fraction(1, 1)}
        odd_basis.append(name)
        parity[name] = 1
    for k in range(1, n + 1):
        name = f"E_eps1_del{k}_mm"
        realizations[name] = {('a_1_m', f"b_{k}_m"): Fraction(1, 1)}
        odd_basis.append(name)
        parity[name] = 1

    return even_basis, odd_basis, realizations, parity

def run_validation(n: int):
    t0 = time.time()
    even_basis, odd_basis, realizations, parity = get_generators(n)
    all_basis = even_basis + odd_basis

    word_to_root = {}
    for g in all_basis:
        if not g.startswith('H_'):
            words = list(realizations[g].keys())
            word_to_root[words[0]] = g

    w_coeffs = [{} for _ in range(n + 1)]
    w_const = [Fraction(0, 1) for _ in range(n + 1)]

    # w_n = -H_{n+1} - 1/2
    w_coeffs[n][f"H_{n+1}"] = Fraction(-1, 1)
    w_const[n] = Fraction(-1, 2)

    for k in range(n - 1, 0, -1):
        w_coeffs[k] = dict(w_coeffs[k + 1])
        w_coeffs[k][f"H_{k+1}"] = w_coeffs[k].get(f"H_{k+1}", Fraction(0, 1)) + Fraction(1, 1)
        w_const[k] = w_const[k + 1]

    w_coeffs[0] = {h_name: -c for h_name, c in w_coeffs[1].items()}
    w_coeffs[0]['H_1'] = w_coeffs[0].get('H_1', Fraction(0, 1)) + Fraction(1, 1)
    w_const[0] = -w_const[1]

    cartan_word_to_idx = {('a_1_p', 'a_1_m'): 0}
    for k in range(1, n + 1):
        cartan_word_to_idx[(f"b_{k}_p", f"b_{k}_m")] = k

    def decompose(poly: Dict[Tuple[str, ...], Fraction]) -> Dict[str, Fraction]:
        res = defaultdict(Fraction)
        residual_const = poly.get((), Fraction(0, 1))
        
        for w, coeff in poly.items():
            if w == ():
                continue
            if w in word_to_root:
                res[word_to_root[w]] += coeff
            elif w in cartan_word_to_idx:
                idx = cartan_word_to_idx[w]
                for h_name, h_c in w_coeffs[idx].items():
                    res[h_name] += coeff * h_c
                residual_const += coeff * w_const[idx]
            else:
                raise ValueError(f"Unrecognized word in bracket: {w}")
        
        if residual_const != 0:
            raise ValueError(f"Non-zero residual constant in bracket: {residual_const}")
        return {k: v for k, v in res.items() if v != 0}

    brackets = []
    tensor = defaultdict(dict)

    for X in all_basis:
        pX = parity[X]
        for Y in all_basis:
            pY = parity[Y]
            bracket_poly = graded_commutator(realizations[X], pX, realizations[Y], pY)
            decomp = decompose(bracket_poly)
            if decomp:
                tensor[(X, Y)] = decomp
                for Z, coeff in decomp.items():
                    brackets.append((X, Y, Z, coeff))

    # Jacobi identity check
    jac_errors = 0
    checked_triples = 0
    for X in all_basis:
        pX = parity[X]
        for Y in all_basis:
            pY = parity[Y]
            for Z in all_basis:
                pZ = parity[Z]
                checked_triples += 1
                sum_decomp = defaultdict(Fraction)
                for W, c_YZ_W in tensor.get((Y, Z), {}).items():
                    for V, c_XW_V in tensor.get((X, W), {}).items():
                        s = -1 if (pX * pZ) % 2 == 1 else 1
                        sum_decomp[V] += s * c_YZ_W * c_XW_V
                for W, c_ZX_W in tensor.get((Z, X), {}).items():
                    for V, c_YW_V in tensor.get((Y, W), {}).items():
                        s = -1 if (pY * pX) % 2 == 1 else 1
                        sum_decomp[V] += s * c_ZX_W * c_YW_V
                for W, c_XY_W in tensor.get((X, Y), {}).items():
                    for V, c_ZW_V in tensor.get((Z, W), {}).items():
                        s = -1 if (pZ * pY) % 2 == 1 else 1
                        sum_decomp[V] += s * c_XY_W * c_ZW_V
                for V, val in sum_decomp.items():
                    if val != 0:
                        jac_errors += 1
                        print(f"FAILED Jacobi: ({X}, {Y}, {Z}) at {V} = {val}")
                        break
                if jac_errors > 0: break
            if jac_errors > 0: break
        if jac_errors > 0: break

    skew_errors = 0
    for X in all_basis:
        pX = parity[X]
        for Y in all_basis:
            pY = parity[Y]
            s = -Fraction(1, 1) if (pX * pY) % 2 == 1 else Fraction(1, 1)
            b_XY = tensor.get((X, Y), {})
            b_YX = tensor.get((Y, X), {})
            for Z in set(b_XY) | set(b_YX):
                if b_YX.get(Z, 0) != -s * b_XY.get(Z, 0):
                    skew_errors += 1

    t1 = time.time()
    print(f"C({n+1}) [n={n}]: dim={len(all_basis)} (even={len(even_basis)}, odd={len(odd_basis)}) | brackets={len(brackets)} | Jacobi checked ({checked_triples} triples), errors={jac_errors} | Skew errors={skew_errors} | Time={t1-t0:.2f}s")
    return len(brackets), jac_errors, skew_errors

for n in [1, 2, 3]:
    run_validation(n)
import json

def build_schema1_json(n: int) -> dict:
    even_basis, odd_basis, realizations, parity = get_generators(n)
    all_basis = even_basis + odd_basis

    word_to_root = {}
    for g in all_basis:
        if not g.startswith('H_'):
            words = list(realizations[g].keys())
            word_to_root[words[0]] = g

    w_coeffs = [{} for _ in range(n + 1)]
    w_const = [Fraction(0, 1) for _ in range(n + 1)]
    w_coeffs[n][f"H_{n+1}"] = Fraction(-1, 1)
    w_const[n] = Fraction(-1, 2)

    for k in range(n - 1, 0, -1):
        w_coeffs[k] = dict(w_coeffs[k + 1])
        w_coeffs[k][f"H_{k+1}"] = w_coeffs[k].get(f"H_{k+1}", Fraction(0, 1)) + Fraction(1, 1)
        w_const[k] = w_const[k + 1]

    w_coeffs[0] = {h_name: -c for h_name, c in w_coeffs[1].items()}
    w_coeffs[0]['H_1'] = w_coeffs[0].get('H_1', Fraction(0, 1)) + Fraction(1, 1)
    w_const[0] = -w_const[1]

    cartan_word_to_idx = {('a_1_p', 'a_1_m'): 0}
    for k in range(1, n + 1):
        cartan_word_to_idx[(f"b_{k}_p", f"b_{k}_m")] = k

    def decompose(poly: Dict[Tuple[str, ...], Fraction]) -> Dict[str, Fraction]:
        res = defaultdict(Fraction)
        residual_const = poly.get((), Fraction(0, 1))
        for w, coeff in poly.items():
            if w == (): continue
            if w in word_to_root:
                res[word_to_root[w]] += coeff
            elif w in cartan_word_to_idx:
                idx = cartan_word_to_idx[w]
                for h_name, h_c in w_coeffs[idx].items():
                    res[h_name] += coeff * h_c
                residual_const += coeff * w_const[idx]
        return {k: v for k, v in res.items() if v != 0}

    brackets = []
    for X in all_basis:
        pX = parity[X]
        for Y in all_basis:
            pY = parity[Y]
            decomp = decompose(graded_commutator(realizations[X], pX, realizations[Y], pY))
            for Z, coeff in decomp.items():
                brackets.append({
                    "X": X,
                    "Y": Y,
                    "Z": Z,
                    "coeff": str(coeff) if coeff.denominator == 1 else f"{coeff.numerator}/{coeff.denominator}",
                    "sign_rule": "graded"
                })

    boson_labels = []
    for k in range(1, n + 1):
        boson_labels.extend([f"b_{k}_p", f"b_{k}_m"])

    realization_data = {
        "description": "Standard form with PBW ordering",
        "ordering": ", ".join(["a_1_p", "a_1_m"] + boson_labels),
        "realizations": {}
    }
    for g in all_basis:
        poly = realizations[g]
        std_form = []
        for w, coeff in poly.items():
            c_str = str(coeff) if coeff.denominator == 1 else f"{coeff.numerator}/{coeff.denominator}"
            std_form.append({"words": list(w), "coeff": c_str})
        realization_data["realizations"][g] = {
            "standard_form": std_form,
            "parity": parity[g]
        }

    schema = {
        "schema_version": "5.0",
        "algebra": {
            "family": "C",
            "m": 1,
            "n": n,
            "cartan_type": f"C({n+1})",
            "alternative_notation": {
                "osp": f"osp(2|{2*n})",
                "dimension_formula": "osp(2m|2n) with m=1: even = 2n^2 + n + 1, odd = 4n, total = 2n^2 + 5n + 1"
            },
            "dimension": {
                "total": 2*n**2 + 5*n + 1,
                "even": 2*n**2 + n + 1,
                "odd": 4*n
            }
        },
        "central_elements": {
            "kappa": {
                "parity": 1,
                "nilpotent_order": 2,
                "relation": "kappa^2 = 0",
                "description": "Odd central nilpotent element carrier of inhomogeneous deformation parameter"
            },
            "K": {
                "parity": 0,
                "scalar_value": 1,
                "description": "Even central identity element (identified with scalar 1; excluded from PBW basis)"
            }
        },
        "oscillator_generators": {
            "fermions": {
                "count": 2,
                "m": 1,
                "labels": ["a_1_p", "a_1_m"],
                "parity": 1,
                "description": "Standard fermionic CAR pair a_1^± (replaces B(0,n) supplementary fermion a_0)"
            },
            "bosons": {
                "count": 2 * n,
                "n": n,
                "labels": boson_labels,
                "parity": 0,
                "description": "Bosonic CCR oscillators b_i^± with i=1,...,n"
            }
        },
        "oscillator_relations": {
            "fermionic_anticommutators": {
                "description": "Canonical anticommutation relations (CAR) for standard fermionic pair",
                "relations": {
                    "same_type": "{a_1^±, a_1^±} = 0 (nilpotent: (a_1^±)^2 = 0)",
                    "conjugate_pair": "{a_1^-, a_1^+} = 1"
                }
            },
            "bosonic_commutators": {
                "description": "Canonical commutation relations (CCR) for bosonic oscillators",
                "relations": {
                    "same_type": "[b_i^±, b_j^±] = 0 for all i, j",
                    "conjugate_pair": "[b_i^-, b_j^+] = δ_{ij}"
                }
            },
            "mixed_commutators": {
                "boson_fermion": "[b_i^±, a_1^±] = 0 (in undeformed algebra)"
            }
        },
        "basis": {
            "even": even_basis,
            "odd": odd_basis,
            "ordering_convention": "PBW: κ < [odd: ++, +-, -+, --] < [even]"
        },
        "parity": parity,
        "generator_realization": realization_data,
        "structure_constants": brackets,
        "metadata": {
            "generated_by": "build_C_structure_constants.py",
            "generation_date": "2026-10-17",
            "references": [
                "Frappat et al. (2000), Dictionary on Lie Algebras and Superalgebras",
                "Bakalov and Sullivan (2017)"
            ]
        }
    }
    return schema

for n in [1, 2, 3]:
    s = build_schema1_json(n)
    txt = json.dumps(s)
    print(f"Schema 1 for C({n+1}) generated successfully. JSON size = {len(txt)} bytes. Brackets = {len(s['structure_constants'])}")
