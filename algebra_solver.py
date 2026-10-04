import sympy as sp
from collections import defaultdict
import json

class DeformedLieSuperalgebra:
    def __init__(self, n):
        self.n = n
        
        # Deformation parameters
        self.gb = {}
        for sigma in ['+', '-']:
            for j in range(1, n + 1):
                for s in ['+', '-']:
                    self.gb[(sigma, j, s)] = sp.Symbol(f"gb_{sigma}_{j}_{s}")
                    
        # Basis of g
        # Even:
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

    def normal_order_word(self, word):
        # word is list of tokens
        current = [(sp.Integer(1), list(word))]
        
        def sort_key(tok):
            if tok[0] == 'kappa':
                return (0, 0, 0)
            elif tok[0] == 'a':
                return (1, 0 if tok[1] == '+' else 1, 0)
            elif tok[0] == 'b':
                return (2, 0 if tok[2] == '+' else 1, tok[1])
            return (9, 0, 0)
            
        while True:
            new_current = []
            all_done = True
            for coeff, tokens in current:
                if coeff == 0:
                    continue
                kappa_count = sum(1 for t in tokens if t[0] == 'kappa')
                if kappa_count > 1:
                    continue
                
                has_zero = False
                for i in range(len(tokens) - 1):
                    if tokens[i] == tokens[i+1] and tokens[i][0] == 'a':
                        has_zero = True
                        break
                if has_zero:
                    continue
                    
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
                    
                    if t2[0] == 'kappa':
                        p1 = 1 if (t1[0] == 'a' or t1[0] == 'kappa') else 0
                        sgn = -1 if p1 == 1 else 1
                        new_current.append((coeff * sgn, prefix + [t2, t1] + suffix))
                    elif t1[0] == 'a' and t2[0] == 'a':
                        new_current.append((coeff, prefix + suffix))
                        new_current.append((-coeff, prefix + [('a', '+'), ('a', '-')] + suffix))
                    elif t1[0] == 'b' and t2[0] == 'b':
                        j1, s1 = t1[1], t1[2]
                        j2, s2 = t2[1], t2[2]
                        if s1 == s2:
                            new_current.append((coeff, prefix + [t2, t1] + suffix))
                        elif s1 == '-' and s2 == '+':
                            delta = 1 if j1 == j2 else 0
                            if delta != 0:
                                new_current.append((coeff * delta, prefix + suffix))
                            new_current.append((coeff, prefix + [t2, t1] + suffix))
                        else:
                            new_current.append((coeff, prefix + [t2, t1] + suffix))
                    elif t1[0] == 'b' and t2[0] == 'a':
                        sigma = t2[1]
                        j = t1[1]
                        s = t1[2]
                        gb_val = self.gb[(sigma, j, s)]
                        new_current.append((coeff, prefix + [t2, t1] + suffix))
                        new_current.append((-coeff * gb_val, prefix + [('kappa',)] + suffix))
            current = new_current
            if all_done:
                break
                
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
        kind = elem[0]
        if kind == 'J0':
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
            return [
                (sp.Integer(1), [('b', j, '+'), ('b', k, '-')]),
                (sp.Rational(1, 2) if j == k else sp.Integer(0), [])
            ]
        elif kind == 'F':
            sigma, j, s = elem[1], elem[2], elem[3]
            return [(sp.Integer(1), [('a', sigma), ('b', j, s)])]
        raise ValueError(f"Unknown element {elem}")

    def multiply_words(self, words1, words2):
        res = defaultdict(lambda: sp.Integer(0))
        for c1, w1 in words1:
            if c1 == 0: continue
            for c2, w2 in words2:
                if c2 == 0: continue
                prod_w = w1 + w2
                ordered = self.normal_order_word(prod_w)
                for k, v in ordered.items():
                    res[k] += c1 * c2 * v
        return {k: sp.simplify(v) for k, v in res.items() if sp.simplify(v) != 0}

    def superbracket(self, elem1, p1, elem2, p2):
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

    def decompose_modulo_scalars(self, poly_dict):
        # Poly dict is decomposed into:
        # basis of g + scalar identity 1
        # Returns: (c_k0, scalar_k0), (c_k1, scalar_k1)
        
        # Map each basis element of g and the identity 1 to normal ordered tokens
        # Basis elements:
        basis_normal = {}
        for b, p in self.basis:
            w = self.element_to_words(b)
            res = defaultdict(lambda: sp.Integer(0))
            for c, tok in w:
                res[tuple(tok)] += c
            basis_normal[b] = {k: sp.simplify(v) for k, v in res.items() if v != 0}
            
        # Also add scalar 1:
        scalar_elem = ('I',)
        basis_normal[scalar_elem] = {(): sp.Integer(1)}
        
        all_basis_keys = [b[0] for b in self.basis] + [scalar_elem]
        dim_all = len(all_basis_keys)
        
        def solve_linear(target_dict):
            all_monoms = set(target_dict.keys())
            for k in all_basis_keys:
                all_monoms.update(basis_normal[k].keys())
            all_monoms = list(all_monoms)
            
            coeffs = [sp.Symbol(f"c_{i}") for i in range(dim_all)]
            eqs = []
            for monom in all_monoms:
                lhs = sum(coeffs[i] * basis_normal[all_basis_keys[i]].get(monom, 0) for i in range(dim_all))
                rhs = target_dict.get(monom, 0)
                eqs.append(lhs - rhs)
                
            sol = sp.solve(eqs, coeffs)
            if not sol:
                if all(v == 0 for v in target_dict.values()):
                    return [sp.Integer(0)] * self.dim, sp.Integer(0)
                raise ValueError(f"Could not decompose in g + I: {target_dict}")
            c_g = [sp.simplify(sol.get(coeffs[i], 0)) for i in range(self.dim)]
            c_I = sp.simplify(sol.get(coeffs[self.dim], 0))
            return c_g, c_I

        target_k0 = {k[1]: v for k, v in poly_dict.items() if not k[0]}
        target_k1 = {k[1]: v for k, v in poly_dict.items() if k[0]}
        
        c_k0, s_k0 = solve_linear(target_k0)
        c_k1, s_k1 = solve_linear(target_k1)
        return (c_k0, s_k0), (c_k1, s_k1)

print("DeformedLieSuperalgebra defined successfully.")
