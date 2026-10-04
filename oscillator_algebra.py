import sympy as sp
from collections import defaultdict
import json

class OscillatorAlgebra:
    def __init__(self, n):
        self.n = n
        # Define gb symbols
        self.gb = {}
        for sigma in ['+', '-']:
            for j in range(1, n + 1):
                for s in ['+', '-']:
                    self.gb[(sigma, j, s)] = sp.Symbol(f"gb_{sigma}_{j}_{s}")
                    
        # Basis of g
        # Even:
        # J0 = a^+ a^- - 1/2
        # B++_{j,k} = b_j^+ b_k^+ (1 <= j <= k <= n)
        # B--_{j,k} = b_j^- b_k^- (1 <= j <= k <= n)
        # B+-_{j,k} = b_j^+ b_k^- + 1/2 * delta_jk (1 <= j, k <= n)
        self.even_basis = []
        self.even_basis.append(('J0',))
        for j in range(1, n + 1):
            for k in range(j, n + 1):
                self.even_basis.append(('B++', j, k))
        for j in range(1, n + 1):
            for k in range(j, n + 1):
                self.even_basis.append(('B--', j, k))
        for j in range(1, n + 1):
            for k in range(1, n + 1):
                self.even_basis.append(('B+-', j, k))
                
        # Odd:
        # F_{sigma, j, s} = a^sigma b_j^s
        self.odd_basis = []
        for sigma in ['+', '-']:
            for j in range(1, n + 1):
                for s in ['+', '-']:
                    self.odd_basis.append(('F', sigma, j, s))
                    
        self.basis = [(x, 0) for x in self.even_basis] + [(x, 1) for x in self.odd_basis]
        self.basis_dict = {b[0]: idx for idx, b in enumerate(self.basis)}
        self.dim = len(self.basis)
        self.dim_even = len(self.even_basis)
        self.dim_odd = len(self.odd_basis)

    # A word is represented as a list of tokens:
    # ('a', '+'), ('a', '-'), ('b', j, '+'), ('b', j, '-')
    # Normal order for quadratic/quartic monomials:
    # ('a', '+')^e_a+ ('a', '-')^e_a- * prod (b_j^+)^e_bj+ * prod (b_j^-)^e_bj-
    # with kappa_power in {0, 1} stored as a coefficient.
    
    def normal_order_word(self, word):
        # word is list of tokens: ('a', '+'), ('a', '-'), ('b', j, '+'), ('b', j, '-'), ('kappa',)
        # returns dict of {normalized_word: coeff}
        # A normalized word has no kappa (kappa power is factored out as coeff * kappa),
        # and tokens in order: a^+, a^-, b_1^+, ..., b_n^+, b_1^-, ..., b_n^-
        
        # State: list of (coeff, list_of_tokens)
        # We rewrite step by step
        current = [(sp.Integer(1), list(word))]
        
        # Helper to get token sort key
        def sort_key(tok):
            if tok[0] == 'kappa':
                return (0, 0, 0)
            elif tok[0] == 'a':
                return (1, 0 if tok[1] == '+' else 1, 0)
            elif tok[0] == 'b':
                return (2, 0 if tok[2] == '+' else 1, tok[1])
            return (9, 0, 0)
            
        def is_sorted(tokens):
            for i in range(len(tokens) - 1):
                if sort_key(tokens[i]) > sort_key(tokens[i+1]):
                    return False
            return True
            
        while True:
            new_current = []
            all_done = True
            for coeff, tokens in current:
                if coeff == 0:
                    continue
                # Check for double kappa
                kappa_count = sum(1 for t in tokens if t[0] == 'kappa')
                if kappa_count > 1:
                    continue
                
                # Check for (a^+)^2 or (a^-)^2
                has_zero = False
                for i in range(len(tokens) - 1):
                    if tokens[i] == tokens[i+1] and tokens[i][0] == 'a':
                        has_zero = True
                        break
                if has_zero:
                    continue
                    
                # Find first inversion
                inversion = -1
                for i in range(len(tokens) - 1):
                    if sort_key(tokens[i]) > sort_key(tokens[i+1]):
                        inversion = i
                        break
                        
                if inversion == -1:
                    new_current.append((coeff, tokens))
                else:
                    all_done = False
                    i = inversion
                    t1, t2 = tokens[i], tokens[i+1]
                    prefix = tokens[:i]
                    suffix = tokens[i+2:]
                    
                    # Case 1: t2 is kappa
                    if t2[0] == 'kappa':
                        # t1 kappa = (-1)^p(t1) kappa t1
                        p1 = 1 if (t1[0] == 'a' or t1[0] == 'kappa') else 0
                        sgn = -1 if p1 == 1 else 1
                        new_current.append((coeff * sgn, prefix + [t2, t1] + suffix))
                        
                    # Case 2: t1 is kappa (should not happen if sort_key(kappa) is 0)
                    elif t1[0] == 'kappa':
                        pass # sorted correctly
                        
                    # Case 3: both 'a'
                    elif t1[0] == 'a' and t2[0] == 'a':
                        # t1 = a^-, t2 = a^+
                        # a^- a^+ = 1 - a^+ a^-
                        new_current.append((coeff, prefix + suffix)) # 1 term
                        new_current.append((-coeff, prefix + [('a', '+'), ('a', '-')] + suffix))
                        
                    # Case 4: both 'b'
                    elif t1[0] == 'b' and t2[0] == 'b':
                        j1, s1 = t1[1], t1[2]
                        j2, s2 = t2[1], t2[2]
                        # if same sign, they commute
                        if s1 == s2:
                            new_current.append((coeff, prefix + [t2, t1] + suffix))
                        elif s1 == '-' and s2 == '+':
                            # b_j^- b_k^+ = b_k^+ b_j^- + delta_jk
                            delta = 1 if j1 == j2 else 0
                            if delta != 0:
                                new_current.append((coeff * delta, prefix + suffix))
                            new_current.append((coeff, prefix + [t2, t1] + suffix))
                        else:
                            # shouldn't happen based on sort key
                            new_current.append((coeff, prefix + [t2, t1] + suffix))
                            
                    # Case 5: t1 is 'b' and t2 is 'a'
                    elif t1[0] == 'b' and t2[0] == 'a':
                        # b_j^s a^sigma = a^sigma b_j^s - gb_{sigma, j, s} * kappa
                        sigma = t2[1]
                        j = t1[1]
                        s = t1[2]
                        gb_val = self.gb[(sigma, j, s)]
                        # term 1: a^sigma b_j^s
                        new_current.append((coeff, prefix + [t2, t1] + suffix))
                        # term 2: - gb * kappa
                        new_current.append((-coeff * gb_val, prefix + [('kappa',)] + suffix))
                        
                    # Case 6: t1 is 'a' and t2 is 'b'
                    elif t1[0] == 'a' and t2[0] == 'b':
                        # sorted correctly (a before b)
                        pass
            current = new_current
            if all_done:
                break
                
        # Group terms by (has_kappa, tuple(tokens_without_kappa))
        res = defaultdict(lambda: sp.Integer(0))
        for coeff, tokens in current:
            has_kappa = False
            toks = []
            for t in tokens:
                if t[0] == 'kappa':
                    has_kappa = True
                else:
                    toks.append(t)
            res[(has_kappa, tuple(toks))] += coeff
            
        return {k: sp.simplify(v) for k, v in res.items() if sp.simplify(v) != 0}

    def element_to_words(self, elem):
        # elem is tuple like ('J0',), ('B++', j, k), etc.
        # returns list of (coeff, word)
        kind = elem[0]
        if kind == 'J0':
            # a^+ a^- - 1/2
            return [
                (sp.Integer(1), [('a', '+'), ('a', '-')]),
                (-sp.Rational(1, 2), [])
            ]
        elif kind == 'B++':
            j, k = elem[1], elem[2]
            return [(sp.Integer(1), [('b', j, '+'), ('b', k, '+')])]
        elif kind == 'B--':
            j, k = elem[1], elem[2]
            return [(sp.Integer(1), [('b', j, '-'), ('b', k, '-')])]
        elif kind == 'B+-':
            j, k = elem[1], elem[2]
            # b_j^+ b_k^- + 1/2 delta_jk
            words = [(sp.Integer(1), [('b', j, '+'), ('b', k, '-')])]
            if j == k:
                words.append((sp.Rational(1, 2), []))
            return words
        elif kind == 'F':
            sigma, j, s = elem[1], elem[2], elem[3]
            return [(sp.Integer(1), [('a', sigma), ('b', j, s)])]
        raise ValueError(f"Unknown element {elem}")

    def multiply_words(self, words1, words2):
        # words is list of (coeff, list_of_tokens)
        res = defaultdict(lambda: sp.Integer(0))
        for c1, w1 in words1:
            for c2, w2 in words2:
                prod_w = w1 + w2
                ordered = self.normal_order_word(prod_w)
                for k, v in ordered.items():
                    res[k] += c1 * c2 * v
        return {k: sp.simplify(v) for k, v in res.items() if sp.simplify(v) != 0}

    def superbracket(self, elem1, p1, elem2, p2):
        # [X, Y] = X Y - (-1)^{p1 p2} Y X
        w1 = self.element_to_words(elem1)
        w2 = self.element_to_words(elem2)
        
        xy = self.multiply_words(w1, w2)
        yx = self.multiply_words(w2, w1)
        
        sgn = -1 if (p1 * p2 % 2 == 1) else 1
        
        bracket = defaultdict(lambda: sp.Integer(0))
        for k, v in xy.items():
            bracket[k] += v
        for k, v in yx.items():
            bracket[k] -= sgn * v
            
        return {k: sp.simplify(v) for k, v in bracket.items() if sp.simplify(v) != 0}

    def decompose_in_basis(self, poly_dict):
        # poly_dict has keys (has_kappa, tuple(tokens))
        # We separate into kappa=False and kappa=True
        # and express each as linear combination of g basis elements!
        
        # Let's map each basis element of g to its normal-ordered form
        basis_normal = {}
        for b, p in self.basis:
            w = self.element_to_words(b)
            # Normal order w (undeformed, i.e. no kappa)
            res = defaultdict(lambda: sp.Integer(0))
            for c, tok in w:
                # normal order without gb
                # for standard basis elements, they are already normal ordered!
                # but let's check
                res[tuple(tok)] += c
            basis_normal[b] = {k: sp.simplify(v) for k, v in res.items() if v != 0}
            
        # We want to express poly (for kappa=0 and kappa=1) in basis_normal
        def solve_linear(target_dict):
            # target_dict is {tokens: coeff}
            # We want sum_i c_i basis_normal[b_i] == target_dict
            # Build linear system
            all_monoms = set(target_dict.keys())
            for b in self.basis:
                all_monoms.update(basis_normal[b[0]].keys())
            all_monoms = list(all_monoms)
            
            # Unknowns: c_0, ..., c_{dim-1}
            coeffs = [sp.Symbol(f"c_{i}") for i in range(self.dim)]
            eqs = []
            for monom in all_monoms:
                lhs = sum(coeffs[i] * basis_normal[self.basis[i][0]].get(monom, 0) for i in range(self.dim))
                rhs = target_dict.get(monom, 0)
                eqs.append(lhs - rhs)
                
            sol = sp.solve(eqs, coeffs)
            if not sol:
                # Check if target is 0
                if all(v == 0 for v in target_dict.values()):
                    return [sp.Integer(0)] * self.dim
                raise ValueError(f"Could not decompose in basis: {target_dict}")
            return [sp.simplify(sol.get(coeffs[i], 0)) for i in range(self.dim)]

        target_k0 = {k[1]: v for k, v in poly_dict.items() if not k[0]}
        target_k1 = {k[1]: v for k, v in poly_dict.items() if k[0]}
        
        c_k0 = solve_linear(target_k0)
        c_k1 = solve_linear(target_k1)
        return c_k0, c_k1

print("OscillatorAlgebra defined successfully.")
