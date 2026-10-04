import sys
import os
sys.path.append(os.path.abspath('.'))

import sympy as sp
import numpy as np
import json

from scratch.test_engine import multiply_monomials, normal_order, OperatorMonomial

class Cn1Algebra:
    def __init__(self, n):
        self.n = n
        self.gb_dict = {}
        self.gb_list = []
        for sigma in ['+', '-']:
            for k in range(1, n + 1):
                for s in ['+', '-']:
                    sig_str = 'p' if sigma == '+' else 'm'
                    s_str = 'p' if s == '+' else 'm'
                    sym = sp.Symbol(f"gb_{sig_str}_{k}_{s_str}")
                    self.gb_dict[(sigma, k, s)] = sym
                    self.gb_list.append(sym)

        # Build basis
        # Even basis
        self.even_basis = []
        self.even_basis.append(('Z0',))
        
        # h_k for k=1..n
        for k in range(1, n + 1):
            self.even_basis.append(('h', k))
            
        # Bosonic pairs
        bosons = []
        for k in range(1, n + 1):
            bosons.append((k, '+'))
            bosons.append((k, '-'))
            
        for i in range(len(bosons)):
            for j in range(i, len(bosons)):
                # exclude (k,+) and (k,-) because that is h_k
                b1, b2 = bosons[i], bosons[j]
                if b1[0] == b2[0] and b1[1] == '+' and b2[1] == '-':
                    continue
                self.even_basis.append(('B', b1, b2))
                
        # Odd basis
        self.odd_basis = []
        for sigma in ['+', '-']:
            for k in range(1, n + 1):
                for s in ['+', '-']:
                    self.odd_basis.append(('F', sigma, (k, s)))

        self.basis = self.even_basis + self.odd_basis
        self.dim_even = len(self.even_basis)
        self.dim_odd = len(self.odd_basis)
        self.dim_total = len(self.basis)

        self.basis_parity = [0]*self.dim_even + [1]*self.dim_odd

    def basis_name(self, idx):
        b = self.basis[idx]
        if b[0] == 'Z0':
            return 'Z0'
        elif b[0] == 'h':
            return f'h_{b[1]}'
        elif b[0] == 'B':
            (k1, s1), (k2, s2) = b[1], b[2]
            return f'B_({k1}{s1},{k2}{s2})'
        elif b[0] == 'F':
            sig, (k, s) = b[1], b[2]
            return f'F_({sig},{k}{s})'

    def generator_to_monomials(self, idx):
        """
        Returns list of (coeff, ops) in OperatorMonomials for basis[idx]
        """
        b = self.basis[idx]
        if b[0] == 'Z0':
            # Z0 = a+ a- - 1/2
            return [(1, [('a', '+'), ('a', '-')]), (-sp.Rational(1, 2), [])]
        elif b[0] == 'h':
            k = b[1]
            # h_k = b_k+ b_k- + 1/2
            return [(1, [('b', k, '+'), ('b', k, '-')]), (sp.Rational(1, 2), [])]
        elif b[0] == 'B':
            (k1, s1), (k2, s2) = b[1], b[2]
            if (k1, s1) == (k2, s2):
                # 0.5 * (b_k^s)^2
                return [(sp.Rational(1, 2), [('b', k1, s1), ('b', k2, s2)])]
            else:
                return [(1, [('b', k1, s1), ('b', k2, s2)])]
        elif b[0] == 'F':
            sig, (k, s) = b[1], b[2]
            return [(1, [('a', sig), ('b', k, s)])]


def express_in_basis(norm_terms, alg):
    """
    Given a list of OperatorMonomial (norm_terms),
    decomposes into sum_k c_k * Z_k (and checks constant term).
    Returns a dict {basis_idx: coeff} and constant_val.
    """
    vec = {}
    const_val = 0
    
    for m in norm_terms:
        coeff = m.coeff
        ops = m.ops
        
        # Strip kappa if present
        if len(ops) > 0 and ops[0][0] == 'kappa':
            ops = ops[1:]
            
        if len(ops) == 0:
            const_val += coeff
        elif len(ops) == 2 and ops[0][0] == 'a' and ops[1][0] == 'a':
            # a+ a- = Z0 + 1/2
            idx = 0 # Z0 is index 0
            vec[idx] = vec.get(idx, 0) + coeff
            const_val += coeff * sp.Rational(1, 2)
        elif len(ops) == 2 and ops[0][0] == 'a' and ops[1][0] == 'b':
            # F_(sigma, k, s)
            sig = ops[0][1]
            k, s = ops[1][1], ops[1][2]
            target_b = ('F', sig, (k, s))
            idx = alg.basis.index(target_b)
            vec[idx] = vec.get(idx, 0) + coeff
        elif len(ops) == 2 and ops[0][0] == 'b' and ops[1][0] == 'b':
            k1, s1 = ops[0][1], ops[0][2]
            k2, s2 = ops[1][1], ops[1][2]
            if k1 == k2 and s1 == '+' and s2 == '-':
                # h_k - 1/2
                idx = alg.basis.index(('h', k1))
                vec[idx] = vec.get(idx, 0) + coeff
                const_val -= coeff * sp.Rational(1, 2)
            elif k1 == k2 and s1 == s2:
                # 2 * B_{(k1,s1),(k1,s1)}
                target_b = ('B', (k1, s1), (k1, s1))
                idx = alg.basis.index(target_b)
                vec[idx] = vec.get(idx, 0) + 2 * coeff
            else:
                # B_{(k1,s1),(k2,s2)}
                # Ensure ordered key
                bosons = [ops[0][1:], ops[1][1:]]
                bosons.sort(key=lambda b: (b[0], 0 if b[1] == '+' else 1))
                target_b = ('B', (bosons[0][0], bosons[0][1]), (bosons[1][0], bosons[1][1]))
                idx = alg.basis.index(target_b)
                vec[idx] = vec.get(idx, 0) + coeff
        else:
            raise ValueError(f"Unhandled monomial with non-zero coefficient ({coeff}): {ops}")

    return vec, sp.simplify(const_val)

def simplify_monomials(monos):
    grouped = {}
    for m in monos:
        key = tuple(m.ops)
        grouped[key] = grouped.get(key, 0) + m.coeff
    res = []
    for ops_tuple, c in grouped.items():
        c_simp = sp.simplify(c)
        if c_simp != 0:
            res.append(OperatorMonomial(c_simp, list(ops_tuple)))
    return res

def compute_all_brackets(alg):
    """
    Computes structure constants C[i, j, k] and gamma[i, j, k]
    for all 0 <= i < j < dim_total.
    [Z_i, Z_j]_gamma = sum_k C[i, j, k] Z_k + kappa sum_k gamma[i, j, k] Z_k.
    Returns C_tensor (dict), gamma_tensor (dict).
    """
    dim = alg.dim_total
    C_tensor = {}
    gamma_tensor = {}
    
    for i in range(dim):
        for j in range(dim):
            if i >= j:
                continue
                
            p_i = alg.basis_parity[i]
            p_j = alg.basis_parity[j]
            sign = 1 if (p_i * p_j % 2 == 0) else -1
            
            # X = basis[i], Y = basis[j]
            # [X, Y] = X Y - sign Y X
            mono_X = alg.generator_to_monomials(i)
            mono_Y = alg.generator_to_monomials(j)
            
            # Expand X Y and Y X
            XY_monos = []
            for cX, opsX in mono_X:
                for cY, opsY in mono_Y:
                    XY_monos.append(OperatorMonomial(cX * cY, opsX + opsY))
                    
            YX_monos = []
            for cY, opsY in mono_Y:
                for cX, opsX in mono_X:
                    YX_monos.append(OperatorMonomial(cY * cX, opsY + opsX))
                    
            # Normal order XY and YX
            XY_norm = []
            for m in XY_monos:
                XY_norm.extend(normal_order(m, alg.gb_dict))
                
            YX_norm = []
            for m in YX_monos:
                YX_norm.extend(normal_order(m, alg.gb_dict))
                
            # Total superbracket = XY_norm - sign * YX_norm
            total_monos = XY_norm + [OperatorMonomial(-sign * m.coeff, m.ops) for m in YX_norm]
            total_monos = simplify_monomials(total_monos)
            
            # Separate kappa^0 and kappa^1
            k0_monos = []
            k1_monos = []
            for m in total_monos:
                if len(m.ops) > 0 and m.ops[0][0] == 'kappa':
                    k1_monos.append(m)
                else:
                    k0_monos.append(m)
                    
            vec0, const0 = express_in_basis(k0_monos, alg)
            vec1, const1 = express_in_basis(k1_monos, alg)
            
            if const0 != 0:
                print(f"WARNING: non-zero const0 for ({alg.basis_name(i)}, {alg.basis_name(j)}): {const0}")
            if const1 != 0:
                print(f"WARNING: non-zero const1 for ({alg.basis_name(i)}, {alg.basis_name(j)}): {const1}")
                
            C_tensor[(i, j)] = vec0
            gamma_tensor[(i, j)] = vec1
            
    return C_tensor, gamma_tensor

if __name__ == '__main__':
    alg1 = Cn1Algebra(1)
    print(f"Alg n=1 initialized: dim_even={alg1.dim_even}, dim_odd={alg1.dim_odd}")
    C1, G1 = compute_all_brackets(alg1)
    print("Computed all brackets for n=1 successfully!")
    print(f"Total pairs: {len(C1)}")
    
    # Print some brackets to verify
    for (i, j), vec in G1.items():
        if len(vec) > 0:
            str_vec = ", ".join([f"{alg1.basis_name(k)}: {v}" for k, v in vec.items()])
            print(f"gamma({alg1.basis_name(i)}, {alg1.basis_name(j)}) = {str_vec}")
