import os
import json
from fractions import Fraction
from datetime import datetime

# Oscillator ordering key
def osc_key(symbol):
    if symbol == "a_1_p":
        return (0, 1, 1)
    if symbol == "a_1_m":
        return (0, 1, 2)
    if symbol.startswith("b_"):
        parts = symbol.split("_")
        k = int(parts[1])
        pm = 1 if parts[2] == "p" else 2
        return (1, k, pm)
    raise ValueError(f"Unknown oscillator symbol: {symbol}")

class Polynomial:
    def __init__(self, terms=None):
        # terms is a dict: tuple of sorted symbols -> Fraction coefficient
        self.terms = {}
        if terms:
            for word, coeff in terms.items():
                c = Fraction(coeff)
                if c != 0:
                    self.terms[word] = self.terms.get(word, Fraction(0)) + c
                    if self.terms[word] == 0:
                        del self.terms[word]

    def is_zero(self):
        return len(self.terms) == 0

    def add(self, other):
        res = Polynomial(self.terms)
        for word, coeff in other.terms.items():
            res.terms[word] = res.terms.get(word, Fraction(0)) + coeff
            if res.terms[word] == 0:
                del res.terms[word]
        return res

    def scale(self, scalar):
        c = Fraction(scalar)
        if c == 0:
            return Polynomial()
        res = Polynomial()
        for word, coeff in self.terms.items():
            res.terms[word] = coeff * c
        return res

    @staticmethod
    def _reduce_word(word):
        # Reduces a tuple of symbols using CAR and CCR
        # Returns dict of reduced_word -> Fraction coeff
        current = {word: Fraction(1)}
        
        while True:
            updated = False
            next_dict = {}
            for w, c in current.items():
                # Check for adjacent reduction or swap
                reduced_this_word = False
                w_list = list(w)
                for i in range(len(w_list) - 1):
                    s1, s2 = w_list[i], w_list[i+1]
                    
                    # Check duplicate fermion
                    if s1 == s2 and s1 in ("a_1_p", "a_1_m"):
                        # Term vanishes
                        reduced_this_word = True
                        updated = True
                        break
                    
                    if osc_key(s1) > osc_key(s2):
                        reduced_this_word = True
                        updated = True
                        prefix = tuple(w_list[:i])
                        suffix = tuple(w_list[i+2:])
                        
                        if s1 == "a_1_m" and s2 == "a_1_p":
                            # a1_m * a1_p = 1 - a1_p * a1_m
                            w_const = prefix + suffix
                            w_prod = prefix + ("a_1_p", "a_1_m") + suffix
                            next_dict[w_const] = next_dict.get(w_const, Fraction(0)) + c
                            next_dict[w_prod] = next_dict.get(w_prod, Fraction(0)) - c
                        elif s1.startswith("b_") and s2.startswith("b_") and s1.split("_")[1] == s2.split("_")[1] and s1.endswith("_m") and s2.endswith("_p"):
                            # bk_m * bk_p = bk_p * bk_m + 1
                            bk_p = s2
                            bk_m = s1
                            w_prod = prefix + (bk_p, bk_m) + suffix
                            w_const = prefix + suffix
                            next_dict[w_prod] = next_dict.get(w_prod, Fraction(0)) + c
                            next_dict[w_const] = next_dict.get(w_const, Fraction(0)) + c
                        else:
                            # Commuting operators, swap
                            w_swapped = prefix + (s2, s1) + suffix
                            next_dict[w_swapped] = next_dict.get(w_swapped, Fraction(0)) + c
                        break
                
                if not reduced_this_word:
                    next_dict[w] = next_dict.get(w, Fraction(0)) + c
            
            current = {w: c for w, c in next_dict.items() if c != 0}
            if not updated:
                break
                
        return current

    def multiply(self, other):
        res = Polynomial()
        for w1, c1 in self.terms.items():
            for w2, c2 in other.terms.items():
                raw_word = w1 + w2
                c_prod = c1 * c2
                reduced = Polynomial._reduce_word(raw_word)
                for rw, rc in reduced.items():
                    res.terms[rw] = res.terms.get(rw, Fraction(0)) + c_prod * rc
                    if res.terms[rw] == 0:
                        del res.terms[rw]
        return res

def get_basis_and_realizations(n):
    even = []
    odd = []
    parity = {}
    realizations = {} # name -> Polynomial
    realizations_json = {} # name -> dict format for schema

    # 1. Cartans: H_1 ... H_{n+1}
    # H_1 = a1_p * a1_m + b1_p * b1_m
    # H_k = b_{k-1}_p * b_{k-1}_m - b_k_p * b_k_m (2 <= k <= n)
    # H_{n+1} = - b_n_p * b_n_m - 1/2
    for k in range(1, n + 2):
        h_name = f"H_{k}"
        even.append(h_name)
        parity[h_name] = 0
        if k == 1:
            poly = Polynomial({("a_1_p", "a_1_m"): 1, ("b_1_p", "b_1_m"): 1})
            f_form = "a_1^+ a_1^- + b_1^+ b_1^-"
            std_form = [
                {"words": ["a_1_p", "a_1_m"], "coeff": "1"},
                {"words": ["b_1_p", "b_1_m"], "coeff": "1"}
            ]
        elif 2 <= k <= n:
            poly = Polynomial({(f"b_{k-1}_p", f"b_{k-1}_m"): 1, (f"b_{k}_p", f"b_{k}_m"): -1})
            f_form = f"b_{k-1}^+ b_{k-1}^- - b_{k}^+ b_{k}^-"
            std_form = [
                {"words": [f"b_{k-1}_p", f"b_{k-1}_m"], "coeff": "1"},
                {"words": [f"b_{k}_p", f"b_{k}_m"], "coeff": "-1"}
            ]
        else: # k == n + 1
            poly = Polynomial({(f"b_{n}_p", f"b_{n}_m"): -1, (): Fraction(-1, 2)})
            f_form = f"-b_{n}^+ b_{n}^- - 1/2"
            std_form = [
                {"words": [f"b_{n}_p", f"b_{n}_m"], "coeff": "-1"},
                {"words": [], "coeff": "-1/2"}
            ]
        realizations[h_name] = poly
        realizations_json[h_name] = {
            "standard_form": std_form,
            "frappat_form": f_form,
            "parity": 0
        }

    # 2. Positive 2del_k: E_2del{k}_p = (b_k_p)^2
    for k in range(1, n + 1):
        name = f"E_2del{k}_p"
        even.append(name)
        parity[name] = 0
        poly = Polynomial({(f"b_{k}_p", f"b_{k}_p"): 1})
        realizations[name] = poly
        realizations_json[name] = {
            "standard_form": [{"words": [f"b_{k}_p", f"b_{k}_p"], "coeff": "1"}],
            "frappat_form": f"(b_{k}^+)^2",
            "parity": 0
        }

    # 3. Positive mixed deltas: E_del{i}_del{j}_pp = b_i_p * b_j_p (1 <= i < j <= n)
    for i in range(1, n + 1):
        for j in range(i + 1, n + 1):
            name = f"E_del{i}_del{j}_pp"
            even.append(name)
            parity[name] = 0
            poly = Polynomial({(f"b_{i}_p", f"b_{j}_p"): 1})
            realizations[name] = poly
            realizations_json[name] = {
                "standard_form": [{"words": [f"b_{i}_p", f"b_{j}_p"], "coeff": "1"}],
                "frappat_form": f"b_{i}^+ b_{j}^+",
                "parity": 0
            }

    # 4. Negative 2del_k: E_2del{k}_m = (b_k_m)^2
    for k in range(1, n + 1):
        name = f"E_2del{k}_m"
        even.append(name)
        parity[name] = 0
        poly = Polynomial({(f"b_{k}_m", f"b_{k}_m"): 1})
        realizations[name] = poly
        realizations_json[name] = {
            "standard_form": [{"words": [f"b_{k}_m", f"b_{k}_m"], "coeff": "1"}],
            "frappat_form": f"(b_{k}^-)^2",
            "parity": 0
        }

    # 5. Negative mixed deltas: E_del{i}_del{j}_mm = b_i_m * b_j_m (1 <= i < j <= n)
    for i in range(1, n + 1):
        for j in range(i + 1, n + 1):
            name = f"E_del{i}_del{j}_mm"
            even.append(name)
            parity[name] = 0
            poly = Polynomial({(f"b_{i}_m", f"b_{j}_m"): 1})
            realizations[name] = poly
            realizations_json[name] = {
                "standard_form": [{"words": [f"b_{i}_m", f"b_{j}_m"], "coeff": "1"}],
                "frappat_form": f"b_{i}^- b_{j}^-",
                "parity": 0
            }

    # 6. Mixed sign deltas: E_del{i}_del{j}_pm, E_del{i}_del{j}_mp (1 <= i < j <= n)
    for i in range(1, n + 1):
        for j in range(i + 1, n + 1):
            name_pm = f"E_del{i}_del{j}_pm"
            even.append(name_pm)
            parity[name_pm] = 0
            poly_pm = Polynomial({(f"b_{i}_p", f"b_{j}_m"): 1})
            realizations[name_pm] = poly_pm
            realizations_json[name_pm] = {
                "standard_form": [{"words": [f"b_{i}_p", f"b_{j}_m"], "coeff": "1"}],
                "frappat_form": f"b_{i}^+ b_{j}^-",
                "parity": 0
            }

            name_mp = f"E_del{i}_del{j}_mp"
            even.append(name_mp)
            parity[name_mp] = 0
            # Note: b_i_m * b_j_p = b_j_p * b_i_m (since i < j, b_j_p comes after b_i_p, but osc_key for b_i_m is (1, i, 2) and b_j_p is (1, j, 1). Since i < j, i < j so (1, i, 2) < (1, j, 1))
            poly_mp = Polynomial({(f"b_{i}_m", f"b_{j}_p"): 1})
            realizations[name_mp] = poly_mp
            realizations_json[name_mp] = {
                "standard_form": [{"words": [f"b_{i}_m", f"b_{j}_p"], "coeff": "1"}],
                "frappat_form": f"b_{i}^- b_{j}^+",
                "parity": 0
            }

    # 7. Odd generators: E_eps1_del{k}_pp, pm, mp, mm (1 <= k <= n)
    for k in range(1, n + 1):
        specs = [
            ("pp", "a_1_p", f"b_{k}_p", "+", "+"),
            ("pm", "a_1_p", f"b_{k}_m", "+", "-"),
            ("mp", "a_1_m", f"b_{k}_p", "-", "+"),
            ("mm", "a_1_m", f"b_{k}_m", "-", "-")
        ]
        for tag, f_sym, b_sym, f_sign, b_sign in specs:
            name = f"E_eps1_del{k}_{tag}"
            odd.append(name)
            parity[name] = 1
            poly = Polynomial({(f_sym, b_sym): 1})
            realizations[name] = poly
            realizations_json[name] = {
                "standard_form": [{"words": [f_sym, b_sym], "coeff": "1"}],
                "frappat_form": f"a_1^{f_sign} b_{k}^{b_sign}",
                "parity": 1
            }

    return even, odd, parity, realizations, realizations_json

def solve_linear_combination(bracket_poly, basis_realizations, all_basis_names):
    # Solve bracket_poly = sum_Z coeff_Z * basis_realizations[Z]
    # We strip out Cartans vs non-Cartans. Non-Cartans have unique 1-word terms.
    rem = Polynomial(bracket_poly.terms)
    solution = {}

    # 1. Match non-Cartan basis generators
    for name in all_basis_names:
        if name.startswith("H_") or name == "K":
            continue
        poly = basis_realizations[name]
        # non-Cartan poly has a single term (w: 1)
        w = list(poly.terms.keys())[0]
        if w in rem.terms:
            c = rem.terms[w]
            solution[name] = c
            # subtract c * poly
            rem = rem.add(poly.scale(-c))

    # 2. Match Cartan & central generators if rem is non-zero
    if not rem.is_zero():
        cartan_names = [name for name in all_basis_names if name.startswith("H_") or name == "K"]
        # Gather all words present in cartan realizations
        cartan_words = list(set(w for name in cartan_names for w in basis_realizations[name].terms.keys()))
        
        # Build matrix
        # Columns correspond to cartan_names, rows to cartan_words
        # We solve M * c = b
        import numpy as np
        row_map = {w: idx for idx, w in enumerate(cartan_words)}
        M = np.zeros((len(cartan_words), len(cartan_names)), dtype=float)
        b = np.zeros(len(cartan_words), dtype=float)

        for col_idx, cname in enumerate(cartan_names):
            for w, val in basis_realizations[cname].terms.items():
                M[row_map[w], col_idx] = float(val)

        for w, val in rem.terms.items():
            if w in row_map:
                b[row_map[w]] = float(val)

        # Solve least squares / exact linear solve
        c_vals, residuals, rank, s = np.linalg.lstsq(M, b, rcond=None)
        
        for col_idx, cname in enumerate(cartan_names):
            val_frac = Fraction(c_vals[col_idx]).limit_denominator(1000)
            if val_frac != 0:
                solution[cname] = val_frac
                rem = rem.add(basis_realizations[cname].scale(-val_frac))

    if not rem.is_zero():
        raise RuntimeError(f"Could not fully resolve bracket polynomial: {bracket_poly.terms}, remaining: {rem.terms}")

    return solution

def generate_c_structure(n):
    even, odd, parity, realizations, realizations_json = get_basis_and_realizations(n)
    all_basis = odd + even # PBW: odd < even

    structure_constants = []

    for i in range(len(all_basis)):
        for j in range(i, len(all_basis)):
            name_X = all_basis[i]
            name_Y = all_basis[j]
            poly_X = realizations[name_X]
            poly_Y = realizations[name_Y]
            p_X = parity[name_X]
            p_Y = parity[name_Y]

            # Graded bracket: [X, Y} = X Y - (-1)^(p_X p_Y) Y X
            sign = -1 if (p_X == 1 and p_Y == 1) else 1
            term1 = poly_X.multiply(poly_Y)
            term2 = poly_Y.multiply(poly_X).scale(-sign)
            bracket_poly = term1.add(term2)

            if not bracket_poly.is_zero():
                sol = solve_linear_combination(bracket_poly, realizations, all_basis)
                for name_Z, coeff in sol.items():
                    c_str = str(coeff.numerator) if coeff.denominator == 1 else f"{coeff.numerator}/{coeff.denominator}"
                    structure_constants.append({
                        "X": name_X,
                        "Y": name_Y,
                        "Z": name_Z,
                        "coeff": c_str,
                        "sign_rule": "graded"
                    })

    # Prepare complete Schema 1 JSON
    cartan_type = f"C({n+1})"
    osp_name = f"osp(2|{2*n})"
    total_dim = 2*n*n + 5*n + 1
    even_dim = 2*n*n + n + 1
    odd_dim = 4*n

    boson_labels = []
    for k in range(1, n + 1):
        boson_labels.extend([f"b_{k}_p", f"b_{k}_m"])

    schema_data = {
        "schema_version": "5.0",
        "algebra": {
            "family": "C",
            "m": 1,
            "n": n,
            "cartan_type": cartan_type,
            "alternative_notation": {
                "osp": osp_name,
                "dimension_formula": "osp(2m|2n) with m=1"
            },
            "dimension": {
                "total": total_dim,
                "even": even_dim,
                "odd": odd_dim
            }
        },
        "oscillator_generators": {
            "fermions": {
                "count": 2,
                "m": 1,
                "labels": ["a_1_p", "a_1_m"],
                "description": "Standard CAR fermionic pair a_1^±"
            },
            "bosons": {
                "count": 2*n,
                "n": n,
                "labels": boson_labels,
                "description": "Bosonic oscillators b_i^± with i=1,...,n"
            }
        },
        "oscillator_relations": {
            "standard_fermion_anticommutators": {
                "description": "{a_1^-, a_1^+} = 1",
                "relation": "a_1_m * a_1_p + a_1_p * a_1_m = 1"
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
                "relation": "kappa^2 = 0",
                "description": "Odd nilpotent central extension element"
            },
            "K": {
                "parity": 0,
                "relation": "central scalar unit",
                "description": "Even central unit element"
            }
        },
        "basis": {
            "even": even,
            "odd": odd,
            "ordering_convention": "PBW: kappa < [odd] < [even]"
        },
        "parity": parity,
        "generator_realization": {
            "description": "Standard form with PBW ordering",
            "ordering": "a_1_p, a_1_m, " + ", ".join(boson_labels),
            "realizations": realizations_json
        },
        "structure_constants": structure_constants,
        "metadata": {
            "generated_by": "src/C_generators.py",
            "generation_date": datetime.now().strftime("%Y-%m-%d"),
            "references": [
                "Frappat et al. (2000), Dictionary on Lie Algebras and Superalgebras",
                "Bakalov and Sullivan (2017)"
            ]
        }
    }

    return schema_data

def main():
    os.makedirs("data", exist_ok=True)
    for n in (1, 2, 3):
        data = generate_c_structure(n)
        filename = f"data/C_{n}_structure.json"
        with open(filename, "w") as f:
            json.dump(data, f, indent=2)
        print(f"Generated {filename}: total_dim={data['algebra']['dimension']['total']}, structure_constants={len(data['structure_constants'])}")

if __name__ == "__main__":
    main()
