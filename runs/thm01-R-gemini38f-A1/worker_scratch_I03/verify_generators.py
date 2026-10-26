import sys
from collections import defaultdict
from fractions import Fraction

# An oscillator polynomial is a mapping: normal_ordered_key -> Fraction
# normal_ordered_key: (f_pair, tuple of (p_1, m_1, ..., p_n, m_n))
# f_pair in { '1', 'a+', 'a-', 'a+a-' }
# bosonic powers: tuple of ints of length 2n

class Poly:
    def __init__(self, terms=None):
        self.terms = defaultdict(Fraction)
        if terms:
            for k, v in terms.items():
                if v != 0:
                    self.terms[k] = Fraction(v)

    def __add__(self, other):
        res = Poly(self.terms)
        for k, v in other.terms.items():
            res.terms[k] += v
            if res.terms[k] == 0:
                del res.terms[k]
        return res

    def __sub__(self, other):
        res = Poly(self.terms)
        for k, v in other.terms.items():
            res.terms[k] -= v
            if res.terms[k] == 0:
                del res.terms[k]
        return res

    def __mul__(self, other):
        # We define multiplication of polynomials by reducing term by term
        res = Poly()
        for k1, v1 in self.terms.items():
            for k2, v2 in other.terms.items():
                prod = multiply_keys(k1, k2)
                for k, v in prod.terms.items():
                    res.terms[k] += v1 * v2 * v
                    if res.terms[k] == 0:
                        del res.terms[k]
        return res

    def scale(self, c):
        res = Poly()
        for k, v in self.terms.items():
            res.terms[k] = v * Fraction(c)
            if res.terms[k] == 0:
                del res.terms[k]
        return res

    def is_zero(self):
        return len(self.terms) == 0

def make_fermion_mult(f1, f2):
    # f in {'1', 'a+', 'a-', 'a+a-'}
    # a+ * a+ = 0
    # a- * a- = 0
    # a- * a+ = 1 - a+a-
    # returns dict: f -> Fraction
    if f1 == '1':
        return {f2: Fraction(1)}
    if f2 == '1':
        return {f1: Fraction(1)}
    if f1 == 'a+':
        if f2 == 'a+':
            return {}
        elif f2 == 'a-':
            return {'a+a-': Fraction(1)}
        elif f2 == 'a+a-': # a+ * (a+a-) = 0
            return {}
    elif f1 == 'a-':
        if f2 == 'a+':
            return {'1': Fraction(1), 'a+a-': Fraction(-1)}
        elif f2 == 'a-':
            return {}
        elif f2 == 'a+a-': # a- * a+ * a- = (1 - a+a-)a- = a-
            return {'a-': Fraction(1)}
    elif f1 == 'a+a-':
        if f2 == 'a+': # a+a-a+ = a+(1 - a+a-) = a+
            return {'a+': Fraction(1)}
        elif f2 == 'a-': # a+a-a- = 0
            return {}
        elif f2 == 'a+a-': # a+a-a+a- = a+(1-a+a-)a- = a+a-
            return {'a+a-': Fraction(1)}
    raise ValueError(f"Unknown pair {f1}, {f2}")

def reduce_single_boson(m1, p2):
    # (b^-)^m1 * (b^+)^p2
    # returns dict of (p, m) -> Fraction
    # Using formula: (b^-)^m (b^+)^p = sum_{k=0}^{min(m,p)} k! * binom(m,k) * binom(p,k) (b^+)^{p-k} (b^-)^{m-k}
    import math
    res = {}
    for k in range(min(m1, p2) + 1):
        coeff = math.factorial(k) * math.comb(m1, k) * math.comb(p2, k)
        res[(p2 - k, m1 - k)] = Fraction(coeff)
    return res

def multiply_keys(k1, k2):
    f1, b1 = k1
    f2, b2 = k2
    f_res = make_fermion_mult(f1, f2)
    if not f_res:
        return Poly()
    
    # b1 and b2 are tuples of (p_k, m_k) for k=1..n
    n = len(b1) // 2
    # For each mode k:
    # b1 has (p_k1, m_k1), b2 has (p_k2, m_k2)
    # in product: (b^+)^p_k1 (b^-)^m_k1 (b^+)^p_k2 (b^-)^m_k2
    # = (b^+)^p_k1 [ (b^-)^m_k1 (b^+)^p_k2 ] (b^-)^m_k2
    mode_results = []
    for k in range(n):
        pk1, mk1 = b1[2*k], b1[2*k+1]
        pk2, mk2 = b2[2*k], b2[2*k+1]
        mid = reduce_single_boson(mk1, pk2)
        # mid gives (p_mid, m_mid) -> coeff
        # total powers for mode k: pk1 + p_mid, mk2 + m_mid
        mode_k = {}
        for (pm, mm), coeff in mid.items():
            mode_k[(pk1 + pm, mk2 + mm)] = coeff
        mode_results.append(mode_k)
    
    # Take Cartesian product across all modes
    # start with one empty tuple
    current = {(): Fraction(1)}
    for k in range(n):
        nxt = {}
        for cur_b, cur_coeff in current.items():
            for (p, m), coeff in mode_results[k].items():
                nxt[cur_b + (p, m)] = cur_coeff * coeff
        current = nxt
    
    # Now combine with f_res
    res = Poly()
    for f, f_coeff in f_res.items():
        for b, b_coeff in current.items():
            res.terms[(f, b)] += f_coeff * b_coeff
            if res.terms[(f, b)] == 0:
                del res.terms[(f, b)]
    return res

print("Poly reducer initialized successfully.")

def zero_boson(n):
    return tuple([0] * (2 * n))

def boson_unit(n, mode, pm):
    # mode is 1..n, pm is 'p' or 'm'
    lst = [0] * (2 * n)
    idx = 2 * (mode - 1) + (0 if pm == 'p' else 1)
    lst[idx] = 1
    return tuple(lst)

def boson_pair(n, m1, pm1, m2, pm2):
    lst = [0] * (2 * n)
    idx1 = 2 * (m1 - 1) + (0 if pm1 == 'p' else 1)
    idx2 = 2 * (m2 - 1) + (0 if pm2 == 'p' else 1)
    lst[idx1] += 1
    lst[idx2] += 1
    return tuple(lst)

def build_generators(n):
    gens = {}
    parities = {}
    
    # H_1 = a1+ a1- + b1+ b1-
    H1_terms = {
        ('a+a-', zero_boson(n)): Fraction(1),
        ('1', boson_pair(n, 1, 'p', 1, 'm')): Fraction(1)
    }
    gens['H_1'] = Poly(H1_terms)
    parities['H_1'] = 0
    
    # H_k = b_{k-1}+ b_{k-1}- - b_k+ b_k- (2 <= k <= n)
    for k in range(2, n + 1):
        Hk_terms = {
            ('1', boson_pair(n, k - 1, 'p', k - 1, 'm')): Fraction(1),
            ('1', boson_pair(n, k, 'p', k, 'm')): Fraction(-1)
        }
        gens[f'H_{k}'] = Poly(Hk_terms)
        parities[f'H_{k}'] = 0
        
    # H_{n+1} = -b_n+ b_n- - 1/2
    Hnp1_terms = {
        ('1', boson_pair(n, n, 'p', n, 'm')): Fraction(-1),
        ('1', zero_boson(n)): Fraction(-1, 2)
    }
    gens[f'H_{n+1}'] = Poly(Hnp1_terms)
    parities[f'H_{n+1}'] = 0
    
    # Long roots: E_2del{k}_p = (b_k^+)^2, E_2del{k}_m = (b_k^-)^2
    for k in range(1, n + 1):
        gens[f'E_2del{k}_p'] = Poly({('1', boson_pair(n, k, 'p', k, 'p')): Fraction(1)})
        parities[f'E_2del{k}_p'] = 0
        gens[f'E_2del{k}_m'] = Poly({('1', boson_pair(n, k, 'm', k, 'm')): Fraction(1)})
        parities[f'E_2del{k}_m'] = 0
        
    # Short roots: 1 <= i < j <= n
    for i in range(1, n + 1):
        for j in range(i + 1, n + 1):
            gens[f'E_del{i}_del{j}_pp'] = Poly({('1', boson_pair(n, i, 'p', j, 'p')): Fraction(1)})
            parities[f'E_del{i}_del{j}_pp'] = 0
            gens[f'E_del{i}_del{j}_mm'] = Poly({('1', boson_pair(n, i, 'm', j, 'm')): Fraction(1)})
            parities[f'E_del{i}_del{j}_mm'] = 0
            gens[f'E_del{i}_del{j}_pm'] = Poly({('1', boson_pair(n, i, 'p', j, 'm')): Fraction(1)})
            parities[f'E_del{i}_del{j}_pm'] = 0
            gens[f'E_del{i}_del{j}_mp'] = Poly({('1', boson_pair(n, i, 'm', j, 'p')): Fraction(1)})
            parities[f'E_del{i}_del{j}_mp'] = 0
            
    # Odd generators:
    # E_eps1_del{k}_pp = a1+ b_k+
    # E_eps1_del{k}_pm = a1+ b_k-
    # E_eps1_del{k}_mp = a1- b_k+
    # E_eps1_del{k}_mm = a1- b_k-
    for k in range(1, n + 1):
        gens[f'E_eps1_del{k}_pp'] = Poly({('a+', boson_unit(n, k, 'p')): Fraction(1)})
        parities[f'E_eps1_del{k}_pp'] = 1
        gens[f'E_eps1_del{k}_pm'] = Poly({('a+', boson_unit(n, k, 'm')): Fraction(1)})
        parities[f'E_eps1_del{k}_pm'] = 1
        gens[f'E_eps1_del{k}_mp'] = Poly({('a-', boson_unit(n, k, 'p')): Fraction(1)})
        parities[f'E_eps1_del{k}_mp'] = 1
        gens[f'E_eps1_del{k}_mm'] = Poly({('a-', boson_unit(n, k, 'm')): Fraction(1)})
        parities[f'E_eps1_del{k}_mm'] = 1

    return gens, parities

def graded_bracket(X, Y, px, py):
    # [X, Y} = X Y - (-1)^{px py} Y X
    sign = -1 if (px * py % 2 == 1) else 1
    return (X * Y) - (Y * X).scale(sign)

def test_algebra(n):
    gens, parities = build_generators(n)
    print(f"\n--- Testing C({n+1}) with n={n} ---")
    print(f"Total generators: {len(gens)}")
    
    # Check linear independence and form matrix to decompose any element
    basis_keys = list(gens.keys())
    # Collect all monomial keys appearing in basis elements
    all_monomials = set()
    for g in gens.values():
        all_monomials.update(g.terms.keys())
    all_monomials = sorted(list(all_monomials))
    
    # Build basis matrix
    # rows: monomials, cols: basis elements
    import sympy as sp
    M = sp.zeros(len(all_monomials), len(basis_keys))
    for j, bname in enumerate(basis_keys):
        g = gens[bname]
        for i, mkey in enumerate(all_monomials):
            if mkey in g.terms:
                M[i, j] = sp.Rational(g.terms[mkey].numerator, g.terms[mkey].denominator)
                
    rank = M.rank()
    print(f"Matrix rank: {rank} / {len(basis_keys)} basis generators (full rank: {rank == len(basis_keys)})")
    
    # Now compute all graded brackets [X, Y} for all pairs
    structure_constants = []
    failed_brackets = 0
    total_brackets = 0
    non_zero_brackets = 0
    
    for i, name1 in enumerate(basis_keys):
        for j, name2 in enumerate(basis_keys):
            p1 = parities[name1]
            p2 = parities[name2]
            br = graded_bracket(gens[name1], gens[name2], p1, p2)
            total_brackets += 1
            if br.is_zero():
                continue
            
            # Decompose br into basis
            # Vector v
            v = sp.zeros(len(all_monomials), 1)
            is_in_monomials = True
            for mkey, coeff in br.terms.items():
                if mkey not in all_monomials:
                    is_in_monomials = False
                    break
                idx = all_monomials.index(mkey)
                v[idx, 0] = sp.Rational(coeff.numerator, coeff.denominator)
                
            if not is_in_monomials:
                print(f"Bracket [{name1}, {name2}}} has terms outside basis monomials: {br.terms}")
                failed_brackets += 1
                continue
                
            sol, params = M.gauss_jordan_solve(v)
            # check if sol exists
            # verify M * sol == v
            if (M * sol - v).is_zero:
                non_zero_brackets += 1
                for k, bname in enumerate(basis_keys):
                    if sol[k, 0] != 0:
                        structure_constants.append((name1, name2, bname, sol[k, 0]))
            else:
                print(f"Bracket [{name1}, {name2}}} could not be expressed in basis!")
                failed_brackets += 1
                
    print(f"Total brackets computed: {total_brackets}")
    print(f"Non-zero brackets: {non_zero_brackets}")
    print(f"Failed brackets: {failed_brackets}")
    return failed_brackets == 0

