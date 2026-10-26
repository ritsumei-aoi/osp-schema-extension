from fractions import Fraction
from typing import Dict, List, Tuple
from collections import defaultdict

# An operator is represented as a dictionary: tuple_of_oscillators -> Fraction
# Oscillator symbols:
# 'a_1_p', 'a_1_m', 'b_k_p', 'b_k_m'

# Canonical ordering of oscillators:
# a_1_p, a_1_m, b_1_p, b_1_m, b_2_p, b_2_m, ...

def parity_of(osc: str) -> int:
    return 1 if osc.startswith('a_') else 0

def normal_order_word(word: Tuple[str, ...]) -> Dict[Tuple[str, ...], Fraction]:
    # Reduce word using:
    # a_1_p * a_1_p = 0
    # a_1_m * a_1_m = 0
    # a_1_m * a_1_p = 1 - a_1_p * a_1_m
    # b_i_m * b_j_p = b_j_p * b_i_m + delta_{ij}
    # [b_i^s, a_1^\sigma] = 0 (b_i^s and a_1^\sigma commute)
    # [b_i^s, b_j^s] = 0
    # [b_i^+, b_j^-] = -delta_{ij}
    # Desired order:
    # a_1_p < a_1_m < b_1_p < b_1_m < b_2_p < b_2_m < ...
    
    # Let's define an order key for sorting
    def osc_key(osc: str):
        if osc == 'a_1_p': return (0, 0, 0)
        if osc == 'a_1_m': return (0, 1, 0)
        # b_k_s
        parts = osc.split('_')
        k = int(parts[1])
        s = 0 if parts[2] == 'p' else 1
        return (1, k, s)

    # Bubble sort / reduction
    current = {word: Fraction(1, 1)}
    
    # We loop until all words are sorted according to osc_key
    while True:
        next_dict = defaultdict(Fraction)
        all_sorted = True
        for w, coeff in current.items():
            if coeff == 0:
                continue
            # Check if w has any adjacent inversion
            found_inversion = False
            for i in range(len(w) - 1):
                o1, o2 = w[i], w[i+1]
                if o1 == o2 and parity_of(o1) == 1:
                    # (a_1_p)^2 = 0 or (a_1_m)^2 = 0
                    found_inversion = True
                    all_sorted = False
                    # vanishes, don't add to next_dict
                    break
                elif osc_key(o1) > osc_key(o2):
                    found_inversion = True
                    all_sorted = False
                    # Swap o1, o2
                    # Case 1: a_1_m * a_1_p = 1 - a_1_p * a_1_m
                    if o1 == 'a_1_m' and o2 == 'a_1_p':
                        # term 1: - a_1_p * a_1_m
                        swapped = w[:i] + (o2, o1) + w[i+2:]
                        next_dict[swapped] += -coeff
                        # term 2: + 1
                        contracted = w[:i] + w[i+2:]
                        next_dict[contracted] += coeff
                    # Case 2: b_j_m * b_k_p (where j == k) -> b_k_p * b_j_m + 1
                    elif o1.startswith('b_') and o2.startswith('b_'):
                        p1 = o1.split('_')
                        p2 = o2.split('_')
                        j, s1 = int(p1[1]), p1[2]
                        k, s2 = int(p2[1]), p2[2]
                        if s1 == 'm' and s2 == 'p' and j == k:
                            swapped = w[:i] + (o2, o1) + w[i+2:]
                            next_dict[swapped] += coeff
                            contracted = w[:i] + w[i+2:]
                            next_dict[contracted] += coeff
                        else:
                            # just commute
                            swapped = w[:i] + (o2, o1) + w[i+2:]
                            next_dict[swapped] += coeff
                    # Case 3: b and a commute: [b, a] = 0
                    elif o1.startswith('b_') and o2.startswith('a_'):
                        swapped = w[:i] + (o2, o1) + w[i+2:]
                        next_dict[swapped] += coeff
                    else:
                        raise ValueError(f"Unhandled pair: {o1}, {o2}")
                    break
            if not found_inversion:
                next_dict[w] += coeff
        if all_sorted:
            return {k: v for k, v in current.items() if v != 0}
        current = next_dict

def multiply_poly(p1: Dict[Tuple[str, ...], Fraction], p2: Dict[Tuple[str, ...], Fraction]) -> Dict[Tuple[str, ...], Fraction]:
    res = defaultdict(Fraction)
    for w1, c1 in p1.items():
        for w2, c2 in p2.items():
            c = c1 * c2
            w = w1 + w2
            ordered = normal_order_word(w)
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
    # [X, Y} = XY - (-1)^{pX pY} YX
    return add_poly(XY, YX, -sign)

print("Engine defined successfully.")

def get_generators(n: int):
    # Returns (even_basis, odd_basis, generator_realizations, parity_map)
    # Following handover/notation.md exactly
    even_basis = []
    odd_basis = []
    realizations = {}
    parity = {}

    # 1. Cartans H_1, ..., H_{n+1}
    # H_1 = a_1^+ a_1^- + b_1^+ b_1^-
    realizations['H_1'] = {
        ('a_1_p', 'a_1_m'): Fraction(1, 1),
        ('b_1_p', 'b_1_m'): Fraction(1, 1)
    }
    even_basis.append('H_1')
    parity['H_1'] = 0

    for k in range(2, n + 1):
        # H_k = b_{k-1}^+ b_{k-1}^- - b_k^+ b_k^-
        name = f"H_{k}"
        realizations[name] = {
            (f"b_{k-1}_p", f"b_{k-1}_m"): Fraction(1, 1),
            (f"b_{k}_p", f"b_{k}_m"): Fraction(-1, 1)
        }
        even_basis.append(name)
        parity[name] = 0

    # H_{n+1} = -b_n^+ b_n^- - 1/2
    name_last = f"H_{n+1}"
    realizations[name_last] = {
        (f"b_{n}_p", f"b_{n}_m"): Fraction(-1, 1),
        (): Fraction(-1, 2)
    }
    even_basis.append(name_last)
    parity[name_last] = 0

    # 2. Positive long roots E_2del{k}_p = (b_k^+)^2
    for k in range(1, n + 1):
        name = f"E_2del{k}_p"
        realizations[name] = {(f"b_{k}_p", f"b_{k}_p"): Fraction(1, 1)}
        even_basis.append(name)
        parity[name] = 0

    # 3. Positive cross roots E_del{i}_del{j}_pp = b_i^+ b_j^+ (1 <= i < j <= n)
    for i in range(1, n + 1):
        for j in range(i + 1, n + 1):
            name = f"E_del{i}_del{j}_pp"
            realizations[name] = {(f"b_{i}_p", f"b_{j}_p"): Fraction(1, 1)}
            even_basis.append(name)
            parity[name] = 0

    # 4. Negative long roots E_2del{k}_m = (b_k^-)^2
    for k in range(1, n + 1):
        name = f"E_2del{k}_m"
        realizations[name] = {(f"b_{k}_m", f"b_{k}_m"): Fraction(1, 1)}
        even_basis.append(name)
        parity[name] = 0

    # 5. Negative cross roots E_del{i}_del{j}_mm = b_i^- b_j^- (1 <= i < j <= n)
    for i in range(1, n + 1):
        for j in range(i + 1, n + 1):
            name = f"E_del{i}_del{j}_mm"
            realizations[name] = {(f"b_{i}_m", f"b_{j}_m"): Fraction(1, 1)}
            even_basis.append(name)
            parity[name] = 0

    # 6. Mixed cross roots E_del{i}_del{j}_pm, E_del{i}_del{j}_mp (1 <= i < j <= n)
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
    # ++ block
    for k in range(1, n + 1):
        name = f"E_eps1_del{k}_pp"
        realizations[name] = {('a_1_p', f"b_{k}_p"): Fraction(1, 1)}
        odd_basis.append(name)
        parity[name] = 1
    # +- block
    for k in range(1, n + 1):
        name = f"E_eps1_del{k}_pm"
        realizations[name] = {('a_1_p', f"b_{k}_m"): Fraction(1, 1)}
        odd_basis.append(name)
        parity[name] = 1
    # -+ block
    for k in range(1, n + 1):
        name = f"E_eps1_del{k}_mp"
        realizations[name] = {('a_1_m', f"b_{k}_p"): Fraction(1, 1)}
        odd_basis.append(name)
        parity[name] = 1
    # -- block
    for k in range(1, n + 1):
        name = f"E_eps1_del{k}_mm"
        realizations[name] = {('a_1_m', f"b_{k}_m"): Fraction(1, 1)}
        odd_basis.append(name)
        parity[name] = 1

    return even_basis, odd_basis, realizations, parity

for n in [1, 2, 3]:
    eb, ob, real, par = get_generators(n)
    print(f"n={n}: even={len(eb)} (expected {2*n**2+n+1}), odd={len(ob)} (expected {4*n}), total={len(eb)+len(ob)}")

def compute_structure_constants(n: int):
    even_basis, odd_basis, realizations, parity = get_generators(n)
    all_basis = even_basis + odd_basis
    dim = len(all_basis)

    # Invert the Cartan matrix to express w_0, w_1, ..., w_n in terms of H_1, ..., H_{n+1}
    # We know:
    # H_1 = w_0 + w_1
    # H_k = w_{k-1} - w_k for 2 <= k <= n
    # H_{n+1} = -w_n - 1/2
    # In general:
    # w_n = -H_{n+1} - 1/2
    # w_k = w_{k+1} + H_{k+1}
    # w_0 = H_1 - w_1

    # Let's map each basis element to its unique signature or solve linear system
    # Since each root generator is uniquely identified by its single word,
    # and Cartans span the space of (a_1_p, a_1_m), (b_k_p, b_k_m) and constant ():
    
    # Let's build a map from word to root generator
    word_to_root = {}
    for g in all_basis:
        if not g.startswith('H_'):
            words = list(realizations[g].keys())
            assert len(words) == 1
            word_to_root[words[0]] = g

    # Precompute expression of w_0, w_1, ..., w_n in terms of H_1, ..., H_{n+1}
    # w_k_coeffs[k] = {H_j: Fraction}
    # const_part[k] = Fraction
    # w_n = -H_{n+1} - 1/2
    w_coeffs = [{} for _ in range(n + 1)]
    w_const = [Fraction(0, 1) for _ in range(n + 1)]

    # k = n
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

    # Map words to Cartan index:
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
                residual_const -= coeff * w_const[idx]
            else:
                raise ValueError(f"Unrecognized word in bracket: {w}")
        
        if residual_const != 0:
            raise ValueError(f"Non-zero residual constant in bracket: {residual_const}")
        return {k: v for k, v in res.items() if v != 0}

    brackets = []
    # Structure constant tensor: (X, Y) -> {Z: coeff}
    tensor = defaultdict(dict)

    for i, X_name in enumerate(all_basis):
        X_poly = realizations[X_name]
        pX = parity[X_name]
        for j, Y_name in enumerate(all_basis):
            Y_poly = realizations[Y_name]
            pY = parity[Y_name]
            
            bracket_poly = graded_commutator(X_poly, pX, Y_poly, pY)
            decomp = decompose(bracket_poly)
            if decomp:
                tensor[(X_name, Y_name)] = decomp
                for Z_name, coeff in decomp.items():
                    brackets.append({
                        "X": X_name,
                        "Y": Y_name,
                        "Z": Z_name,
                        "coeff": str(coeff),
                        "sign_rule": "graded"
                    })

    # Validate Super-Jacobi identity
    # (-1)^{pX pZ} [X, [Y, Z}} + (-1)^{pY pX} [Y, [Z, X}} + (-1)^{pZ pY} [Z, [X, Y}} = 0
    # Let's test on all triples!
    jacobi_errors = 0
    for X in all_basis:
        pX = parity[X]
        for Y in all_basis:
            pY = parity[Y]
            for Z in all_basis:
                pZ = parity[Z]
                # term 1: (-1)^{pX pZ} [X, [Y, Z}}
                # term 2: (-1)^{pY pX} [Y, [Z, X}}
                # term 3: (-1)^{pZ pY} [Z, [X, Y}}
                sum_decomp = defaultdict(Fraction)
                
                # [Y, Z}
                for W, c_YZ_W in tensor.get((Y, Z), {}).items():
                    for V, c_XW_V in tensor.get((X, W), {}).items():
                        s = -1 if (pX * pZ) % 2 == 1 else 1
                        sum_decomp[V] += s * c_YZ_W * c_XW_V
                        
                # [Z, X}
                for W, c_ZX_W in tensor.get((Z, X), {}).items():
                    for V, c_YW_V in tensor.get((Y, W), {}).items():
                        s = -1 if (pY * pX) % 2 == 1 else 1
                        sum_decomp[V] += s * c_ZX_W * c_YW_V

                # [X, Y}
                for W, c_XY_W in tensor.get((X, Y), {}).items():
                    for V, c_ZW_V in tensor.get((Z, W), {}).items():
                        s = -1 if (pZ * pY) % 2 == 1 else 1
                        sum_decomp[V] += s * c_XY_W * c_ZW_V

                for V, val in sum_decomp.items():
                    if val != 0:
                        jacobi_errors += 1
                        print(f"Jacobi failed for ({X}, {Y}, {Z}) at {V}: {val}")
                        break
                if jacobi_errors > 5:
                    break
            if jacobi_errors > 5:
                break
        if jacobi_errors > 5:
            break

    # Graded skew-symmetry check:
    # [Y, X} = -(-1)^{pX pY} [X, Y}
    skew_errors = 0
    for X in all_basis:
        pX = parity[X]
        for Y in all_basis:
            pY = parity[Y]
            s = -Fraction(1, 1) if (pX * pY) % 2 == 1 else Fraction(1, 1)
            # expected [Y, X} = -s * [X, Y}
            b_XY = tensor.get((X, Y), {})
            b_YX = tensor.get((Y, X), {})
            all_Z = set(b_XY.keys()) | set(b_YX.keys())
            for Z in all_Z:
                if b_YX.get(Z, Fraction(0, 1)) != -s * b_XY.get(Z, Fraction(0, 1)):
                    skew_errors += 1

    return len(brackets), jacobi_errors, skew_errors

for n in [1, 2, 3]:
    num_br, jac_err, skew_err = compute_structure_constants(n)
    print(f"n={n}: non-zero brackets = {num_br}, Jacobi errors = {jac_err}, Skew errors = {skew_err}")
