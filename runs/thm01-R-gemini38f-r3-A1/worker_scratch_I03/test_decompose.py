from fractions import Fraction
from collections import defaultdict

# Let's verify for n=1, 2, 3
from test_algebra import get_generators, graded_commutator, multiply_poly, normal_order_word

def run_test(n):
    eb, ob, real, par = get_generators(n)
    all_basis = eb + ob
    
    word_to_root = {}
    for g in all_basis:
        if not g.startswith('H_'):
            words = list(real[g].keys())
            word_to_root[words[0]] = g

    w_coeffs = [{} for _ in range(n + 1)]
    w_const = [Fraction(0, 1) for _ in range(n + 1)]

    # w_n = -H_{n+1} - 1/2
    w_coeffs[n][f"H_{n+1}"] = Fraction(-1, 1)
    w_const[n] = Fraction(-1, 2)

    for k in range(n - 1, 0, -1):
        # w_k = w_{k+1} + H_{k+1}
        w_coeffs[k] = dict(w_coeffs[k + 1])
        w_coeffs[k][f"H_{k+1}"] = w_coeffs[k].get(f"H_{k+1}", Fraction(0, 1)) + Fraction(1, 1)
        w_const[k] = w_const[k + 1]

    # w_0 = H_1 - w_1
    w_coeffs[0] = {h_name: -c for h_name, c in w_coeffs[1].items()}
    w_coeffs[0]['H_1'] = w_coeffs[0].get('H_1', Fraction(0, 1)) + Fraction(1, 1)
    w_const[0] = -w_const[1]

    cartan_word_to_idx = {('a_1_p', 'a_1_m'): 0}
    for k in range(1, n + 1):
        cartan_word_to_idx[(f"b_{k}_p", f"b_{k}_m")] = k

    def decompose(poly):
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
        pX = par[X]
        for Y in all_basis:
            pY = par[Y]
            bracket_poly = graded_commutator(real[X], pX, real[Y], pY)
            decomp = decompose(bracket_poly)
            if decomp:
                tensor[(X, Y)] = decomp
                for Z, coeff in decomp.items():
                    brackets.append((X, Y, Z, coeff))

    # Jacobi check
    jac_errors = 0
    for X in all_basis:
        pX = par[X]
        for Y in all_basis:
            pY = par[Y]
            for Z in all_basis:
                pZ = par[Z]
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
                        break
                if jac_errors > 0: break
            if jac_errors > 0: break
        if jac_errors > 0: break

    skew_errors = 0
    for X in all_basis:
        pX = par[X]
        for Y in all_basis:
            pY = par[Y]
            s = -Fraction(1, 1) if (pX * pY) % 2 == 1 else Fraction(1, 1)
            b_XY = tensor.get((X, Y), {})
            b_YX = tensor.get((Y, X), {})
            for Z in set(b_XY) | set(b_YX):
                if b_YX.get(Z, 0) != -s * b_XY.get(Z, 0):
                    skew_errors += 1

    return len(brackets), jac_errors, skew_errors

for n in [1, 2, 3]:
    nbr, jerr, serr = run_test(n)
    print(f"C({n+1}) [n={n}]: brackets={nbr}, jacobi_errors={jerr}, skew_errors={serr}")
